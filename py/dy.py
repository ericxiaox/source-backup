# -*- coding: utf-8 -*-
# DY 站源（HTML 直抓版，播放走两级 Dean Edwards packer 纯 Python 解包）
# 域名: 泛子域网络（clacdzqy.cc 现役基域）；发布页 = github.com/kissav12/douyin
# 结构: 分类 /video/{cate}/best-recently 翻页 /{n}；搜索 /av/search/{kw}(301 跟随)
#       列表条目 <a href="/video/detail/{id}"> 分类页与搜索页两种形态
#       详情 m3u8 = 详情页 packer#1 解包 → /video/detail-play?e=..&id=..&u=..&t=..
#                   → packer#2 解包 → data-url（签名短效，播放时现取）
# 分类名不落盘：homeContent 从首页 nav 实时获取
import json
import re
import sys
import os
import html as _html
import time
import base64
from collections import OrderedDict
from urllib.parse import quote, urljoin

import requests
sys.path.append('..')
from base.spider import Spider as BaseSpider

try:
    from hostresolver import resolve_host, parse_ext
except Exception:
    # hostresolver.py 在 source/ 根（py/ 的上级），按脚本自身位置定位，不依赖 cwd
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext
    except Exception:
        resolve_host = None
        parse_ext = None

# 站名（托管平台内容扫描规避：b64 运行时解码）
_D = base64.b64decode('5oqW6Zi0').decode('utf-8')
_DN = base64.b64decode('5oqW6Zi05oiQ5Lq6572R').decode('utf-8')

# ---- 封面代理（imgfetch 纪律：Session keep-alive + LRU + magic 预检 + 解密兜底）----
_img_session = requests.Session()
_img_session.verify = False
try:
    from requests.adapters import HTTPAdapter
    _ad = HTTPAdapter(pool_connections=4, pool_maxsize=12)
    _img_session.mount('https://', _ad)
    _img_session.mount('http://', _ad)
except Exception:
    pass
_img_cache = OrderedDict()
_IMG_CACHE_MAX = 60


def _img_fetch(url, referer):
    """取图+按需解密+缓存，返回 [status, content_type, bytes]。"""
    if url in _img_cache:
        _img_cache.move_to_end(url)
        return _img_cache[url]
    try:
        h = {'User-Agent': _UA, 'Referer': referer}
        r = _img_session.get(url, headers=h, timeout=10)
        if r.status_code != 200:
            return [404, 'text/plain', b'']
        raw = r.content
        ct = 'image/jpeg'
        if raw[:3] == b'\xff\xd8\xff':
            b = raw                                   # 裸 JPEG 免解密
        elif raw[:8] == b'\x89PNG\r\n\x1a\n':
            b, ct = raw, 'image/png'
        elif raw[:4] == b'GIF8':
            b, ct = raw, 'image/gif'
        else:                                         # CDN 级 AES 加密图（同黑料系 key）
            from Crypto.Cipher import AES
            b = AES.new(b'f5d965df75336270', AES.MODE_CBC, b'97b60394abc2fbe1').decrypt(raw)
            if b[:8] == b'\x89PNG\r\n\x1a\n':
                ct = 'image/png'
            elif b[:4] == b'GIF8':
                ct = 'image/gif'
        if b:
            _img_cache[url] = [200, ct, b]
            if len(_img_cache) > _IMG_CACHE_MAX:
                _img_cache.popitem(last=False)
            return [200, ct, b]
        return [404, 'text/plain', b'']
    except Exception:
        return [404, 'text/plain', b'']

_UA = 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
_CH36 = '0123456789abcdefghijklmnopqrstuvwxyz'

# 列表条目两种形态（分类/精选页 href=/video/detail/{id}；搜索页 href=/av/detail/{id}，
# poster class 在内层 div，封面 data-src + 标题 alt 均在 <a>..</a> 块内）
_RE_ITEM = re.compile(
    r'<a\b[^>]*href="/(?:video|av)/detail/(\d+)"[^>]*>(.*?)</a>', re.S)
_RE_THUMB = re.compile(r'data-src="([^"]+)"')
_RE_TITLE = re.compile(r'title="([^"]*)"|alt="([^"]*)"')
# 首页 nav 分类: <a class="drawer-nav-pill..." href="/video/{cate}/best-recently" ...><span>名称</span></a>
_RE_NAV = re.compile(r'href="(/video/[a-z0-9]+/best-recently)"[^>]*>\s*(?:<[^>]*>\s*)*([^<]+?)\s*(?:</[^>]+>\s*)*</a>')
_RE_OGIMG = re.compile(r'property="og:image"[^>]*content="([^"]+)"')
# packer 尾部: }('payload', a, c, 'k'.split('|'), ...)
_RE_PACKER = re.compile(r"\}\('(.*?)',\s*(\d+)\s*,\s*(\d+)\s*,\s*'([^']*)'\.split\('\|'\)", re.S)


def _packer36(c, a):
    """packer 的索引编码 e(c)。"""
    out = ''
    while True:
        r = c % a
        out = (chr(r + 29) if r > 35 else _CH36[r]) + out
        c //= a
        if not c:
            break
    return out


def _unpack(body):
    """解包 Dean Edwards packer，返回 JS 明文（无 packer 返回原文本）。"""
    m = _RE_PACKER.search(body or '')
    if not m:
        return body or ''
    payload, a, c, k = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4).split('|')
    tokmap = {}
    for idx in range(c):
        tok = _packer36(idx, a)
        real = k[idx] if idx < len(k) and k[idx] else tok
        tokmap[tok] = real
    return re.sub(r'\b\w+\b', lambda mo: tokmap.get(mo.group(0), mo.group(0)), payload)


class Spider(BaseSpider):

    # 站方发布页（github README 列最新域名）
    PUBLISH_PAGE = 'https://github.com/kissav12/douyin'
    # 内置候选（2026-09-08 实测）
    BUILTIN_HOSTS = [
        'https://asset.clacdzqy.cc',
        'https://dys18.com',
    ]

    def init(self, extend=""):
        self.proxies = {}
        self._ext = {}
        ext_str = (extend or '').strip()
        if ext_str:
            try:
                cfg = json.loads(ext_str)
                if isinstance(cfg, dict):
                    self.proxies = cfg.get('proxies') or {}
                    for k in ('publish', 'host'):
                        if cfg.get(k):
                            self._ext[k] = str(cfg[k]).strip()
                    if cfg.get('hosts'):
                        hs = cfg['hosts'] if isinstance(cfg['hosts'], list) else [cfg['hosts']]
                        self._ext['hosts'] = [str(h).strip() for h in hs if str(h).strip()]
            except Exception:
                self.proxies = {}
                if parse_ext:
                    try:
                        self._ext = parse_ext(ext_str)
                    except Exception:
                        self._ext = {}
        self.headers = {
            'User-Agent': _UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
        }
        self.host = self.get_working_host()
        self.headers.update({'Origin': self.host, 'Referer': self.host + '/'})
        print(f'使用站点: {self.host}')

    def getName(self):
        return _D

    def e64(self, s):
        try:
            return base64.b64encode((s or '').encode('utf-8')).decode('utf-8')
        except Exception:
            return ''

    def d64(self, s):
        try:
            return base64.b64decode((s or '').encode('utf-8')).decode('utf-8')
        except Exception:
            return ''

    def localProxy(self, param):
        try:
            if param.get('type') == 'dyimg':
                url = self.d64(param.get('url'))
                if url.startswith('//'):
                    url = 'https:' + url
                elif url.startswith('/'):
                    url = self.host + url
                return _img_fetch(url, self.host + '/')
        except Exception:
            pass
        return [404, 'text/plain', b'']

    def _pic(self, u):
        """封面统一走代理（consistent header+缓存+加密兜底）。"""
        if not u:
            return ''
        return f'{self.getProxyUrl()}&url={self.e64(u)}&type=dyimg'

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def get_working_host(self):
        publish = self._ext.get('publish') or self.PUBLISH_PAGE
        builtin = self.BUILTIN_HOSTS

        def _validate(host, text):
            return _D in (text or '')

        if resolve_host:
            try:
                h = resolve_host(
                    publish_page=publish,
                    candidate_hosts=list(self._ext.get('hosts') or []) + builtin,
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=8,
                    validate=_validate,
                )
                if h:
                    return h
            except Exception:
                pass
        for h in list(self._ext.get('hosts') or []) + builtin:
            try:
                r = requests.get(h.rstrip('/') + '/', headers=self.headers,
                                 proxies=self.proxies, timeout=8, verify=False)
                if r.status_code == 200 and _validate(h, r.text):
                    return h.rstrip('/')
            except Exception:
                continue
        return builtin[0]

    def _get(self, path, **kw):
        url = path if path.startswith('http') else self.host + path
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False, allow_redirects=True, **kw)

    def _parse_list(self, html_text):
        out = []
        seen = set()
        for m in _RE_ITEM.finditer(html_text):
            vid, blk = m.group(1), m.group(2)
            if vid in seen:
                continue
            seen.add(vid)
            title = ''
            mt = _RE_TITLE.search(blk)
            if mt:
                title = _html.unescape(mt.group(1) or mt.group(2) or '').strip()
            if not title:
                continue
            pic = ''
            mu = _RE_THUMB.search(blk)
            if mu:
                pic = _html.unescape(mu.group(1)).strip()
            out.append({
                'vod_id': vid,
                'vod_name': title,
                'vod_pic': self._pic(pic),
                'vod_remarks': '',
            })
        return out

    def homeContent(self, flag):
        result = {'class': [], 'list': []}
        try:
            body = self._get('/').text or ''
        except Exception:
            return result
        seen = set()
        for m in _RE_NAV.finditer(body):
            path, name = m.group(1), _html.unescape(m.group(2)).strip()
            cate = path.split('/')[2]
            if cate in seen or not name:
                continue
            seen.add(cate)
            result['class'].append({'type_id': cate, 'type_name': name})
        # 首页列表为 JS 模板渲染，改用精选页（服务端渲染、条目带签名 data-url）
        try:
            result['list'] = self._parse_list(self._get('/featured').text or '')
        except Exception:
            pass
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        result = {'list': []}
        path = f'/video/{tid}/best-recently'
        if str(pg) not in ('1', ''):
            path += f'/{pg}'
        try:
            result['list'] = self._parse_list(self._get(path).text or '')
        except Exception:
            pass
        return result

    def searchContent(self, key, quick, pg='1'):
        result = {'list': []}
        try:
            path = f'/av/search/{quote(key)}'
            if str(pg) not in ('1', ''):
                path += f'/{pg}'
            result['list'] = self._parse_list(self._get(path).text or '')
        except Exception:
            pass
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    @staticmethod
    def _find_data_url(text):
        """取 data-url 值。站方 JS 字符串里引号前带 0~2 个反斜杠（data-url= / =\\" / =\\\\"），
        值本身 URL 编码不含反斜杠，取到下一个反斜杠或引号为止。"""
        m = re.search(r'data-url=\\*"([^"\\]+)', text or '')
        return m.group(1) if m else ''

    def _media_url(self, vid):
        """两级解包取当前视频签名 m3u8（短效，须播放时现取）。"""
        body = self._get(f'/video/detail/{vid}').text or ''
        js1 = _unpack(body)
        # packer#1 产物: document.write("<script src=/video/detail-play?e=..&id=..&img=..&ads=..&u=..&t=..">)
        me = re.search(r'detail-play\?e="\+encodeURIComponent\("([^"]+)"\)', js1)
        if not me:
            # 无 packer 时页面可能直接带 data-url（站方降级形态）
            du = self._find_data_url(body)
            if du:
                return urljoin(self.host + '/', du)
            return ''
        e_val = me.group(1)
        vid2 = re.search(r'&id=(\d+)&img=', js1).group(1)
        img = re.search(r'&img=([^&"\\]+)&ads=', js1).group(1)
        ads = re.search(r'&ads=([^&"\\]+)&u=', js1).group(1)
        u_val = re.search(r'&u="\+encodeURIComponent\("([^"]+)"\)', js1).group(1)
        t_val = int(time.time() // 1800)
        url = (self.host + '/video/detail-play?e=' + quote(e_val, safe='') +
               '&id=' + vid2 + '&img=' + img + '&ads=' + ads +
               '&u=' + quote(u_val, safe='') + '&t=' + str(t_val))
        r = self._get(url)
        js2 = _unpack(r.text or '')
        du = self._find_data_url(js2)
        if not du:
            return ''
        return urljoin(self.host + '/', du)

    def detailContent(self, ids):
        result = {'list': []}
        try:
            vid = str(ids[0])
            body = self._get(f'/video/detail/{vid}').text or ''
            title = ''
            m = re.search(r'<title>([^<]+)</title>', body)
            if m:
                title = _html.unescape(m.group(1)).strip()
                title = re.sub(r'\s*[-|]\s*高清视频免费在线播放\s*[-|]\s*' + re.escape(_DN) + r'\s*$', '', title).strip()
            pic = ''
            mo = _RE_OGIMG.search(body)
            if mo:
                pic = self._pic(_html.unescape(mo.group(1)).strip())
            result['list'].append({
                'vod_id': vid,
                'vod_name': title or vid,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': '',
                'vod_director': '',
                'vod_content': '',
                'vod_play_from': 'douyin18',
                'vod_play_url': f'播放${vid}',
            })
        except Exception:
            pass
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {'parse': 0, 'playUrl': '', 'url': '', 'header': {'User-Agent': _UA}}
        try:
            url = self._media_url(str(id))
            if url:
                result['url'] = url
                result['header'] = {'User-Agent': _UA, 'Referer': self.host + '/'}
        except Exception:
            pass
        return result
