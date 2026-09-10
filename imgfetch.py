# -*- coding: utf-8 -*-
"""\u56fe\u7247\u4ee3\u7406\u901a\u7528\u52a0\u901f\u6a21\u5757\uff08imgfetch v1\uff0c2026-09-08\uff09

\u4f9b\u5404 py \u6e90 localProxy \u5c01\u9762\u901a\u9053\u7edf\u4e00\u590d\u7528\uff08\u4e0e hostresolver \u540c\u7ea7\u3001\u540c\u63a5\u5165\u6a21\u5f0f\uff09\uff1a
- \u6a21\u5757\u7ea7 requests.Session\uff1aTLS keep-alive + HTTPAdapter \u8fde\u63a5\u6c60\uff0c\u514d\u6bcf\u56fe\u63e1\u624b
- \u6293\u53d6+\u89e3\u5bc6\u7ed3\u679c LRU \u7f13\u5b58\uff08\u9ed8\u8ba4 60 \u5f20\uff09\uff1a\u6eda\u52a8\u56de\u770b/\u91cd\u590d\u5c01\u9762 0s \u79d2\u51fa
- magic \u9884\u68c0\uff1a\u660e\u6587\u56fe\uff08JPEG/PNG/GIF/WEBP\uff09\u81ea\u52a8\u8df3\u8fc7\u89e3\u5bc6\uff0c\u574f\u89e3\u5bc6\u4e0d\u6c61\u67d3\u7f13\u5b58

\u7528\u6cd5\uff08\u6e90\u5185\uff09\uff1a
    from imgfetch import fetch_img
    mime, data = fetch_img(url, headers=..., decrypt=callable\u6216None)
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
    """\u660e\u6587\u56fe magic \u9884\u68c0\uff1aJPEG/PNG/GIF/WEBP"""
    if not data or len(data) < 12:
        return False
    if data[:3] == b'\xff\xd8\xff' or data[:8] == b'\x89PNG\r\n\x1a\n':
        return True
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return True
    return data[:4] == b'RIFF' and data[8:12] == b'WEBP'


def session():
    """\u8fdb\u7a0b\u7ea7\u5171\u4eab Session\uff08\u8fde\u63a5\u6c60\u590d\u7528\uff09"""
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
    """\u6293\u56fe\uff08\u53ef\u9009\u89e3\u5bc6\uff09\uff0c\u5e26 LRU \u7f13\u5b58\u3002\u8fd4\u56de (mime, bytes)\uff1b\u5931\u8d25\u8fd4\u56de (None, b'')\u3002

    decrypt: callable(bytes)->bytes\uff1b\u4f20\u5165\u65f6\u82e5\u54cd\u5e94\u5df2\u662f\u660e\u6587\u56fe\u5219\u81ea\u52a8\u8df3\u8fc7\u89e3\u5bc6\u3002
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
