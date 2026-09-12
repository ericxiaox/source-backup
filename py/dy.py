# -*- coding: utf-8 -*-
# DY \u7ad9\u6e90\uff08HTML \u76f4\u6293\u7248\uff0c\u64ad\u653e\u8d70\u4e24\u7ea7 Dean Edwards packer \u7eaf Python \u89e3\u5305\uff09
# \u57df\u540d: \u6cdb\u5b50\u57df\u7f51\u7edc\uff08clacdzqy.cc \u73b0\u5f79\u57fa\u57df\uff09\uff1b\u53d1\u5e03\u9875 = github.com/kissav12/douyin
# \u7ed3\u6784: \u5206\u7c7b /video/{cate}/best-recently \u7ffb\u9875 /{n}\uff1b\u641c\u7d22 /av/search/{kw}(301 \u8ddf\u968f)
#       \u5217\u8868\u6761\u76ee <a href="/video/detail/{id}"> \u5206\u7c7b\u9875\u4e0e\u641c\u7d22\u9875\u4e24\u79cd\u5f62\u6001
#       \u8be6\u60c5 m3u8 = \u8be6\u60c5\u9875 packer#1 \u89e3\u5305 \u2192 /video/detail-play?e=..&id=..&u=..&t=..
#                   \u2192 packer#2 \u89e3\u5305 \u2192 data-url\uff08\u7b7e\u540d\u77ed\u6548\uff0c\u64ad\u653e\u65f6\u73b0\u53d6\uff09
# \u5206\u7c7b\u540d\u4e0d\u843d\u76d8\uff1ahomeContent \u4ece\u9996\u9875 nav \u5b9e\u65f6\u83b7\u53d6
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
    from hostresolver import resolve_host, parse_ext, probe_first
except Exception:
    # hostresolver.py \u5728 source/ \u6839\uff08py/ \u7684\u4e0a\u7ea7\uff09\uff0c\u6309\u811a\u672c\u81ea\u8eab\u4f4d\u7f6e\u5b9a\u4f4d\uff0c\u4e0d\u4f9d\u8d56 cwd
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext, probe_first
    except Exception:
        resolve_host = None
        probe_first = None
        parse_ext = None

# explorer.py\uff08source \u6839\uff09\uff1a\u6c60\u5168\u6302\u65f6\u4ece\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\u6d3b\u57df\uff08\u4e0e hostresolver \u540c\u76ee\u5f55\uff09
try:
    from explorer import explore_hosts
except Exception:
    explore_hosts = None

# \u7ad9\u540d\uff08\u6258\u7ba1\u5e73\u53f0\u5185\u5bb9\u626b\u63cf\u89c4\u907f\uff1ab64 \u8fd0\u884c\u65f6\u89e3\u7801\uff09
_D = base64.b64decode('5oqW6Zi0').decode('utf-8')
_DN = base64.b64decode('5oqW6Zi05oiQ5Lq6572R').decode('utf-8')

# ---- \u5c01\u9762\u4ee3\u7406\uff08imgfetch \u7eaa\u5f8b\uff1aSession keep-alive + LRU + magic \u9884\u68c0 + \u89e3\u5bc6\u515c\u5e95\uff09----
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
    """\u53d6\u56fe+\u6309\u9700\u89e3\u5bc6+\u7f13\u5b58\uff0c\u8fd4\u56de [status, content_type, bytes]\u3002"""
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
            b = raw                                   # \u88f8 JPEG \u514d\u89e3\u5bc6
        elif raw[:8] == b'\x89PNG\r\n\x1a\n':
            b, ct = raw, 'image/png'
        elif raw[:4] == b'GIF8':
            b, ct = raw, 'image/gif'
        else:                                         # CDN \u7ea7 AES \u52a0\u5bc6\u56fe\uff08\u540c\u9ed1\u6599\u7cfb key\uff09
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

# \u5217\u8868\u6761\u76ee\u4e24\u79cd\u5f62\u6001\uff08\u5206\u7c7b/\u7cbe\u9009\u9875 href=/video/detail/{id}\uff1b\u641c\u7d22\u9875 href=/av/detail/{id}\uff0c
# poster class \u5728\u5185\u5c42 div\uff0c\u5c01\u9762 data-src + \u6807\u9898 alt \u5747\u5728 <a>..</a> \u5757\u5185\uff09
_RE_ITEM = re.compile(
    r'<a\b[^>]*href="/(?:video|av)/detail/(\d+)"[^>]*>(.*?)</a>', re.S)
_RE_THUMB = re.compile(r'data-src="([^"]+)"')
_RE_TITLE = re.compile(r'title="([^"]*)"|alt="([^"]*)"')
# \u9996\u9875 nav \u5206\u7c7b: <a class="drawer-nav-pill..." href="/video/{cate}/best-recently" ...><span>\u540d\u79f0</span></a>
_RE_NAV = re.compile(r'href="(/video/[a-z0-9]+/best-recently)"[^>]*>\s*(?:<[^>]*>\s*)*([^<]+?)\s*(?:</[^>]+>\s*)*</a>')
_RE_OGIMG = re.compile(r'property="og:image"[^>]*content="([^"]+)"')
# packer \u5c3e\u90e8: }('payload', a, c, 'k'.split('|'), ...)
_RE_PACKER = re.compile(r"\}\('(.*?)',\s*(\d+)\s*,\s*(\d+)\s*,\s*'([^']*)'\.split\('\|'\)", re.S)


def _packer36(c, a):
    """packer \u7684\u7d22\u5f15\u7f16\u7801 e(c)\u3002"""
    out = ''
    while True:
        r = c % a
        out = (chr(r + 29) if r > 35 else _CH36[r]) + out
        c //= a
        if not c:
            break
    return out


def _unpack(body):
    """\u89e3\u5305 Dean Edwards packer\uff0c\u8fd4\u56de JS \u660e\u6587\uff08\u65e0 packer \u8fd4\u56de\u539f\u6587\u672c\uff09\u3002"""
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

    # \u7ad9\u65b9\u53d1\u5e03\u9875\uff08github README \u5217\u6700\u65b0\u57df\u540d\uff09
    PUBLISH_PAGE = 'https://github.com/kissav12/douyin'
    # \u5185\u7f6e\u5019\u9009\uff082026-09-08 \u5b9e\u6d4b\uff09
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
        """\u5c01\u9762\u7edf\u4e00\u8d70\u4ee3\u7406\uff08consistent header+\u7f13\u5b58+\u52a0\u5bc6\u515c\u5e95\uff09\u3002"""
        if not u:
            return ''
        return f'{self.getProxyUrl()}&url={self.e64(u)}&type=dyimg'

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def _resolve_inline(self, publish, builtin, validate):
        """hostresolver \u672a\u52a0\u8f7d\u65f6\u7684\u5185\u8054\u5e76\u884c\u63a2\u6d4b\uff1a\u907f\u514d\u4e32\u884c\u8d85\u65f6\u5bfc\u81f4 App \u7aef\u7a7a\u8f6c\u51e0\u5341\u79d2\u3002
        \u5e26\u5185\u5bb9\u5f62\u6001\u5224\uff0c\u9632\u6b62\u547d\u4e2d\u53d1\u5e03\u9875/\u95e8\u6237\u516c\u544a\u9875\uff08\u6709\u7ad9\u540d\u4f46\u65e0\u5185\u5bb9\uff09\u3002"""
        import threading
        candidates = []
        if publish:
            candidates.append(publish)
        candidates += list(self._ext.get('hosts') or [])
        candidates += list(builtin or [])
        seen = set(); deduped = []
        for u in candidates:
            u = (u or '').strip().rstrip('/')
            if not u:
                continue
            if not u.startswith('http'):
                u = 'https://' + u
            if u not in seen:
                seen.add(u); deduped.append(u)
        if not deduped:
            return ''
        result = [None]
        content_marks = ('<article', 'post-card', 'entry-title', 'post-title',
                         'video-item', 'oneVideo', 'playlist', 'class="video')
        content_link_pat = re.compile(
            r'href=["\'] [^"\']*/(?:archives?|video|videos|category|categories|post|vod|'
            r'watch|tag|detail|thread|topic)[/"\']', re.I)
        def _looks_like_content(t):
            return bool(t and (len(t) > 80000 or any(k in t for k in content_marks)
                               or len(content_link_pat.findall(t)) >= 5))
        def _probe_one(u):
            if result[0]:
                return
            try:
                r = requests.get(u + '/', headers=self.headers, proxies=self.proxies,
                                 timeout=5, verify=False, allow_redirects=True)
                if r.status_code == 200 and validate(r.url, r.text) and _looks_like_content(r.text):
                    if not result[0]:
                        result[0] = r.url.rstrip('/')
            except Exception:
                pass
        threads = [threading.Thread(target=_probe_one, args=(u,)) for u in deduped]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
        if not result[0] and publish:
            # \u6df1\u5ea6\u62bd\u94fe\uff08\u5bf9\u6807 hostresolver.extract_publish_domains\uff09\uff1a\u53d1\u5e03\u9875\u4e0d\u662f\u6d3b\u955c\u50cf\u65f6\uff0c
            # \u4ece\u5176 JS/HTML \u6316\u57fa\u57df\u2014\u2014\u542b words.random()+'.base.cc' \u6cdb\u89e3\u6790\u5f62\u6001\u2014\u2014\u751f\u6210\u5019\u9009\u518d\u63a2\uff0c
            # \u4f7f gitee \u8fdc\u7a0b\u5bfc\u5165\u5f62\u6001\uff08\u65e0 hostresolver \u6a21\u5757\uff09\u4e0e\u672c\u5730\u5305\u540c\u7b49\u81ea\u52a8\u6362\u57df\u80fd\u529b\u3002
            try:
                _pr = requests.get(publish, headers=self.headers, proxies=self.proxies,
                                   timeout=6, verify=False, allow_redirects=True)
                _pt = _pr.text or ''
            except Exception:
                _pt = ''
            if _pt:
                # \u4f18\u5148\u4ece\u542b random() \u7684 <script> \u6bb5\u62bd\uff08\u90a3\u91cc\u624d\u662f\u6cdb\u89e3\u6790\u8bcd\u8868+\u57fa\u57df\uff09\uff0c\u515c\u5e95\u5168\u9875
                _chunks = [c for c in re.findall(r'<script[^>]*>(.*?)</script>', _pt, re.S | re.I)
                           if 'random(' in c]
                _wsrc = '\n'.join(_chunks) if _chunks else _pt
                _bases = []
                for _m in re.findall(r'''['"]\.?((?:[a-z0-9-]+\.)+(?:cc|com|net|top|xyz|vip|app|link|click|org|info|site|online|icu|club|fun|store|live|me|tv))['"]''', _wsrc, re.I):
                    _m = _m.lower().strip('.').strip()
                    if _m and _m not in _bases and _m.count('.') <= 2:
                        _bases.append(_m)
                if not _bases:
                    for _m in re.findall(r'''['"]\.?((?:[a-z0-9-]+\.)+(?:cc|com|net|top|xyz|vip|app|link|click|org|info|site|online|icu|club|fun|store|live|me|tv))['"]''', _pt, re.I):
                        _m = _m.lower().strip('.').strip()
                        if _m and _m not in _bases and _m.count('.') <= 2:
                            _bases.append(_m)
                _slds = [b for b in _bases if b.count('.') == 1]   # \u6cdb\u89e3\u6790\u57fa\u57df\uff08\u8bcd.sld.tld\uff09
                _fulls = [b for b in _bases if b.count('.') > 1]   # \u5b8c\u6574\u57df\uff08\u5982 cloudfront \u56fa\u5b9a\u7ebf\u8def\uff09
                _words = []
                for w in re.findall(r'''['"]([a-z]{3,9})['"]''', _wsrc):
                    if w.lower() not in _words:
                        _words.append(w.lower())
                if not _words:
                    _words = ['berry', 'melon', 'apple', 'kiwi', 'lemon', 'mango',
                              'peach', 'grape', 'plum', 'fig', 'papaya', 'guava']
                _gen = []
                for u in (_fulls[:3] + _slds[:3]):      # SLD/\u5b8c\u6574\u57df\u672c\u8eab\u4e5f\u76f4\u63a2\u4e00\u6b21
                    _u = 'https://' + u
                    if _u not in _gen:
                        _gen.append(_u)
                if _slds:
                    for i in range(12):                 # \u8bcd\u00d7\u57fa\u57df\u8f6e\u8f6c\uff0c\u4e0d\u8ba9\u5355\u57fa\u57df\u9738\u5360\u540d\u989d
                        if len(_gen) >= 12:
                            break
                        _b = _slds[i % len(_slds)]
                        _u = 'https://' + _words[i % len(_words)] + '.' + _b
                        if _u not in _gen:
                            _gen.append(_u)
                _t2 = [threading.Thread(target=_probe_one, args=(u,)) for u in _gen[:12]]
                for t in _t2:
                    t.start()
                for t in _t2:
                    t.join(timeout=10)
        return result[0] or ''

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
        # \u515c\u5e95\uff1aext/\u5185\u7f6e\u5019\u9009**\u5e76\u884c**\u5b9e\u6d4b\uff08\u539f\u4e3a 5\u00d78s \u4e32\u884c\uff0c\u662f\u300c\u8f6c\u5708\u5f88\u4e45\u300d\u7684\u76f4\u63a5\u6765\u6e90\uff09
        cands = list(self._ext.get('hosts') or []) + builtin
        if probe_first:
            try:
                h = probe_first(cands, headers=self.headers, proxies=self.proxies,
                                timeout=8, validate=_validate, tag='\u515c\u5e95')
                if h:
                    return h
            except Exception:
                pass
        else:
            return self._resolve_inline(publish, builtin, _validate)
        # \u7ec8\u6781\u515c\u5e95\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\uff08\u8df3\u8f6c\u58f3/\u95e8\u6237/\u6cdb\u89e3\u6790\u8ddf\u968f + \u7ad9\u540d\u8eab\u4efd\u9a8c\u8bc1\uff09
        if explore_hosts:
            try:
                def _probe(u):
                    r = requests.get(u.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=8, verify=False)
                    return r.status_code == 200 and _D in (r.text or '')
                hs = explore_hosts(['douyin', _D], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        # \u5168\u8d25\uff1a\u663e\u5f0f\u8fd4\u56de\u7a7a\uff08\u63a5\u53e3\u5c42\u79d2\u7a7a\uff0c\u4e0d\u518d\u56de\u9000\u6b7b\u57df\u9759\u9ed8\u7a7a\u8f6c\uff09
        return ''

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
        # \u9996\u9875\u5217\u8868\u4e3a JS \u6a21\u677f\u6e32\u67d3\uff0c\u6539\u7528\u7cbe\u9009\u9875\uff08\u670d\u52a1\u7aef\u6e32\u67d3\u3001\u6761\u76ee\u5e26\u7b7e\u540d data-url\uff09
        try:
            result['list'] = self._parse_list(self._get('/featured').text or '')
        except Exception:
            pass
        return result

    def homeVideoContent(self):
        return {}

    # \u2500\u2500 \u5165\u53e3\u81ea\u6108\uff082026-09-12 \u5168\u91cf\u63a8\u5e7f\uff0c\u6a21\u677f\u540c \u9ed1\u6599\u4e0d\u6253\u70ca\uff09\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    # \u80cc\u666f\uff1ainit \u53ea\u8dd1\u4e00\u6b21\uff0cApp \u51b7\u542f\u52a8\u7f51\u7edc\u672a\u5c31\u7eea/\u77ac\u65f6\u6296\u52a8/\u7ad9\u65b9\u6362\u57df \u2192 \u53d6\u57df\u5931\u8d25\u540e host \u6c38\u4e45\u4e3a\u7a7a\uff0c
    #      \u5206\u7c7b(\u5185\u7f6e\u515c\u5e95)\u7167\u5e38\u663e\u793a\u3001\u5217\u8868\u6c38\u8fdc\u7a7a \u2014\u2014 \u771f\u673a\u75c7\u72b6\u300c\u6709\u5206\u7c7b\u65e0\u89c6\u9891\u300d\u3002
    # \u4e09\u4ef6\u5957\uff1a\u2460\u5165\u53e3\u61d2\u91cd\u89e3\u6790 \u2461\u5217\u8868\u7a7a \u2192 \u63a2\u6d3b/\u6362\u57df\u540e\u91cd\u8bd5\u4e00\u6b21 \u2462\u9996\u8f6e\u5168\u8d25\u65f6\u9759\u6001\u515c\u5e95\u3002
    def _ensure_host(self, force=False):
        old = getattr(self, 'host', '') or ''
        if old and not force:
            return old
        _rq = globals().get('requests') or globals().get('rq')
        if old and _rq is not None:
            # \u5148\u63a2\u6d3b\u5f53\u524d host\uff1a\u6d3b\u7740=\u53ea\u662f\u5076\u53d1\u6296\u52a8\uff0c\u4e0d\u52a8\uff1b\u8fde\u4e0d\u4e0a=\u7591\u4f3c\u6362\u57df\uff0c\u91cd\u89e3\u6790
            try:
                _r = _rq.get(old.rstrip('/') + '/', headers=getattr(self, 'headers', {}) or {},
                             proxies=getattr(self, 'proxies', {}) or {},
                             timeout=6, verify=False)
                if getattr(_r, 'status_code', 0) == 200:
                    return old
            except Exception:
                pass
        h = ''
        try:
            _fn = getattr(self, 'get_working_host', None) or getattr(self, '_pick_host', None)
            if _fn:
                h = (_fn() or '').rstrip('/')
        except Exception:
            h = ''
        if h:
            self.host = h
        elif not old:
            for _c in (getattr(self, 'BUILTIN_HOSTS', None), globals().get('BUILTIN_HOSTS'),
                       globals().get('HOSTS'), getattr(self, 'HOSTS', None)):
                if _c:
                    _v = _c[0] if isinstance(_c, (list, tuple)) else _c
                    if _v:
                        self.host = str(_v).rstrip('/')
                        break
        else:
            self.host = old
        try:
            self.headers.update({'Origin': self.host, 'Referer': self.host + '/'})
        except Exception:
            pass
        print(f'[ensure_host] 使用站点: {self.host}')
        return self.host

    def categoryContent(self, *a, **kw):
        """\u5165\u53e3\u81ea\u6108 + \u7a7a\u7ed3\u679c\u91cd\u8bd5\u4e00\u6b21\uff08\u539f\u5b9e\u73b0\u89c1 _categoryContent\uff09"""
        try:
            self._ensure_host()
        except Exception:
            pass
        r = self._categoryContent(*a, **kw)
        if isinstance(r, dict) and not r.get('list'):
            try:
                self._ensure_host(force=True)
                r2 = self._categoryContent(*a, **kw)
                if isinstance(r2, dict) and r2.get('list'):
                    return r2
            except Exception:
                pass
        return r

    def searchContent(self, *a, **kw):
        """\u5165\u53e3\u81ea\u6108 + \u7a7a\u7ed3\u679c\u91cd\u8bd5\u4e00\u6b21\uff08\u539f\u5b9e\u73b0\u89c1 _searchContent\uff09"""
        try:
            self._ensure_host()
        except Exception:
            pass
        r = self._searchContent(*a, **kw)
        if isinstance(r, dict) and not r.get('list'):
            try:
                self._ensure_host(force=True)
                r2 = self._searchContent(*a, **kw)
                if isinstance(r2, dict) and r2.get('list'):
                    return r2
            except Exception:
                pass
        return r

    def _categoryContent(self, tid, pg, filter, extend):
        result = {'list': []}
        path = f'/video/{tid}/best-recently'
        if str(pg) not in ('1', ''):
            path += f'/{pg}'
        try:
            result['list'] = self._parse_list(self._get(path).text or '')
        except Exception:
            pass
        return result

    def _searchContent(self, key, quick, pg='1'):
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
        """\u53d6 data-url \u503c\u3002\u7ad9\u65b9 JS \u5b57\u7b26\u4e32\u91cc\u5f15\u53f7\u524d\u5e26 0~2 \u4e2a\u53cd\u659c\u6760\uff08data-url= / =\\\" / =\\\\\"\uff09\uff0c
        \u503c\u672c\u8eab URL \u7f16\u7801\u4e0d\u542b\u53cd\u659c\u6760\uff0c\u53d6\u5230\u4e0b\u4e00\u4e2a\u53cd\u659c\u6760\u6216\u5f15\u53f7\u4e3a\u6b62\u3002"""
        m = re.search(r'data-url=\\*"([^"\\]+)', text or '')
        return m.group(1) if m else ''

    def _media_url(self, vid):
        """\u4e24\u7ea7\u89e3\u5305\u53d6\u5f53\u524d\u89c6\u9891\u7b7e\u540d m3u8\uff08\u77ed\u6548\uff0c\u987b\u64ad\u653e\u65f6\u73b0\u53d6\uff09\u3002"""
        body = self._get(f'/video/detail/{vid}').text or ''
        js1 = _unpack(body)
        # packer#1 \u4ea7\u7269: document.write("<script src=/video/detail-play?e=..&id=..&img=..&ads=..&u=..&t=..">)
        me = re.search(r'detail-play\?e="\+encodeURIComponent\("([^"]+)"\)', js1)
        if not me:
            # \u65e0 packer \u65f6\u9875\u9762\u53ef\u80fd\u76f4\u63a5\u5e26 data-url\uff08\u7ad9\u65b9\u964d\u7ea7\u5f62\u6001\uff09
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
                title = re.sub('\\s*[-|]\\s*\u9ad8\u6e05\u89c6\u9891\u514d\u8d39\u5728\u7ebf\u64ad\u653e\\s*[-|]\\s*' + re.escape(_DN) + r'\s*$', '', title).strip()
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
