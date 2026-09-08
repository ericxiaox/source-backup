# -*- coding: utf-8 -*-
"""图片代理通用加速模块（imgfetch v1，2026-09-08）

供各 py 源 localProxy 封面通道统一复用（与 hostresolver 同级、同接入模式）：
- 模块级 requests.Session：TLS keep-alive + HTTPAdapter 连接池，免每图握手
- 抓取+解密结果 LRU 缓存（默认 60 张）：滚动回看/重复封面 0s 秒出
- magic 预检：明文图（JPEG/PNG/GIF/WEBP）自动跳过解密，坏解密不污染缓存

用法（源内）：
    from imgfetch import fetch_img
    mime, data = fetch_img(url, headers=..., decrypt=callable或None)
"""
import threading
import warnings
from collections import OrderedDict

try:
    import requests
except Exception:
    requests = None

warnings.filterwarnings('ignore')

_SESSION = None
_SLOCK = threading.Lock()
_CACHE = OrderedDict()
_CLOCK = threading.Lock()
_CACHE_MAX = 60


def is_plain_image(data):
    """明文图 magic 预检：JPEG/PNG/GIF/WEBP"""
    if not data or len(data) < 12:
        return False
    if data[:3] == b'\xff\xd8\xff' or data[:8] == b'\x89PNG\r\n\x1a\n':
        return True
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return True
    return data[:4] == b'RIFF' and data[8:12] == b'WEBP'


def session():
    """进程级共享 Session（连接池复用）"""
    global _SESSION
    if _SESSION is None:
        with _SLOCK:
            if _SESSION is None and requests is not None:
                s = requests.Session()
                try:
                    from requests.adapters import HTTPAdapter
                    ad = HTTPAdapter(pool_connections=8, pool_maxsize=16, max_retries=0)
                    s.mount('https://', ad)
                    s.mount('http://', ad)
                except Exception:
                    pass
                _SESSION = s
    return _SESSION


def clear_cache():
    with _CLOCK:
        _CACHE.clear()


def _mime_of(d):
    if d[:3] == b'\xff\xd8\xff':
        return 'image/jpeg'
    if d[:8] == b'\x89PNG\r\n\x1a\n':
        return 'image/png'
    if d[:6] in (b'GIF87a', b'GIF89a'):
        return 'image/gif'
    if d[:4] == b'RIFF' and d[8:12] == b'WEBP':
        return 'image/webp'
    return 'application/octet-stream'


def fetch_img(url, headers=None, decrypt=None, timeout=15, proxies=None, verify=False):
    """抓图（可选解密），带 LRU 缓存。返回 (mime, bytes)；失败返回 (None, b'')。

    decrypt: callable(bytes)->bytes；传入时若响应已是明文图则自动跳过解密。
    """
    if requests is None or not url:
        return None, b''
    key = str(url)
    with _CLOCK:
        if key in _CACHE:
            _CACHE.move_to_end(key)
            d = _CACHE[key]
            return _mime_of(d), d
    try:
        r = session().get(url, headers=headers, timeout=timeout, proxies=proxies,
                          verify=verify, allow_redirects=True)
        if r.status_code != 200 or not r.content:
            return None, b''
        data = r.content
    except Exception:
        return None, b''
    if data and decrypt and not is_plain_image(data):
        try:
            data = decrypt(data)
        except Exception:
            return None, b''
    if not data:
        return None, b''
    with _CLOCK:
        _CACHE[key] = data
        while len(_CACHE) > _CACHE_MAX:
            _CACHE.popitem(last=False)
    return _mime_of(data), data
