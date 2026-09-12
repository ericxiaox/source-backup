# -*- coding: utf-8 -*-
# 91BL \u7ad9\u6e90\uff08Typecho + Mirages \u4e3b\u9898 \u00b7 HTML \u76f4\u6293\u7248\uff09
# \u53d1\u5e03\u9875: t91bl.com\uff08b64 \u58f3\u4e2d\u8f6c\u843d\u5730\u9875\uff0c\u89e3\u7801\u540e zz_line \u5217\u6cdb\u89e3\u6790\u57fa\u57df\u7ebf\u8def\uff09
# \u7ebf\u8def: {word}.quibepqh.cc / {word}.matutgbj.cc\uff08\u6cdb\u89e3\u6790\u4efb\u610f\u8bcd\u53ef\u7528\uff09+ cloudfront \u515c\u5e95
#       \uff0891bla1.com \u4e3b\u7ebf\u57df\u540d\u672c\u673a\u5b9e\u6d4b 000\uff0c\u7ebf\u8def\u8868\u4ee5\u6cdb\u89e3\u6790\u4e3a\u4e3b\uff09
# \u7ed3\u6784: \u5206\u7c7b /category/{slug}/ \u7ffb\u9875 /category/{slug}/{n}/\uff1b\u641c\u7d22 /search/{kw}/
#       \u5217\u8868\u6761\u76ee <article> \u5185 <a href="/archives/{id}/"> + \u5c01\u9762 img z-image-loader-url + alt \u6807\u9898
#       \u8be6\u60c5\u64ad\u653e dplayer data-config='{...}' JSON\uff08\/ \u8f6c\u4e49\u8fd8\u539f\uff09\uff0c\u591a\u89c6\u9891=\u591a dplayer
# \u5c01\u9762\u56fe\u5e8a pic.hdhwqx.cn \u4e3a CDN \u7ea7 AES \u52a0\u5bc6\u56fe\uff0c\u987b\u8d70 localProxy \u89e3\u5bc6
# \u5206\u7c7b\u540d\u4e0d\u843d\u76d8\u660e\u6587\uff08b64 \u515c\u5e95\u8868\uff09\uff0c\u5b9e\u65f6\u5206\u7c7b\u4ece nav \u83b7\u53d6
import json
import re
import sys
import os
import html as _html
import time
import base64
from collections import OrderedDict
from urllib.parse import quote

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
        parse_ext = None
        probe_first = None

# explorer.py\uff08source \u6839\uff09\uff1a\u6c60\u5168\u6302\u65f6\u4ece\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\u6d3b\u57df\uff08\u4e0e hostresolver \u540c\u76ee\u5f55\uff09
try:
    from explorer import explore_hosts
except Exception:
    explore_hosts = None

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

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
        r = _img_session.get(url, headers={'User-Agent': _UA, 'Referer': referer}, timeout=10)
        if r.status_code != 200:
            return [404, 'text/plain', b'']
        raw = r.content
        ct = 'image/jpeg'
        if raw[:3] == b'\xff\xd8\xff':
            b = raw                                   # JPEG \u76f4\u4f20\u514d\u89e3\u5bc6
        elif raw[:8] == b'\x89PNG\r\n\x1a\n':
            b, ct = raw, 'image/png'
        elif raw[:4] == b'GIF8':
            b, ct = raw, 'image/gif'
        else:                                         # CDN \u7ea7 AES \u52a0\u5bc6\u56fe\uff08\u9ed1\u6599\u7cfb\u540c key\uff09
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


# \u5206\u7c7b\u515c\u5e95\u8868 {slug: \u540d\u79f0}\uff08b64 of UTF-8 JSON\uff0c2026-09-08 \u9996\u9875 nav \u5b9e\u65f6\u91c7\u96c6\uff09
def _b64d(s):
    return base64.b64decode(s + '=' * (-len(s) % 4)).decode('utf-8')


_CATS = json.loads(_b64d(
    'eyJqcmNnMSI6IuS7iuaXpeWQg+eTnCIsIm1yZHMiOiLmr4/ml6XlpKfotZsiLCJhaWR1YW5qdSI6'
    'IkFJ55+t5YmnIiwibGxqayI6IuiQneiOiWprIiwieWxneCI6Iue9kem7hOi1hOa6kCIsInJnangi'
    'OiLng63pl6jlpKfnk5wiLCJsbHpxIjoi5rW36KeS5Lym55CGIiwiZmNzaiI6IuWPjeW3rueIhuaW'
    'mSIsInN0enpiIjoic3Tnq5nnm7Tmkq3lm57mlL4iLCJ4eXJnIjoi5qCh5Zut54iG5paZIiwibHB6'
    'cSI6IuaOouiKseWBt+aLjSIsImdjcXMiOiJBVuWKqOa8qyIsInF3ZnEiOiLlhajnvZHnlq/msYIi'
    'LCJ3aGJnIjoi5piO5pif54iG5paZIiwicXd5cyI6IuWlh+mXu+W8guS6iyIsInR5Y2ciOiLkvZPo'
    'grLnm7Tmkq0ifQ=='
))

# \u5217\u8868\u6761\u76ee\uff08<article> \u5757\u5185: /archives/{id}/ \u94fe\u63a5 + z-image-loader-url \u5c01\u9762 + alt \u6807\u9898\uff09
_RE_ITEM = re.compile(r'<article[^>]*>(.*?)</article>', re.S)
_RE_LINK = re.compile(r'href="((?:https?://[^"]*?)?/archives/(\d+)/)"')
_RE_COVER = re.compile(r'z-image-loader-url="([^"]+)"', re.I)
_RE_TITLE = re.compile(r'alt="([^"]*)"')
# \u5206\u7c7b nav: <a href="/category/{slug}/">\u540d\u79f0</a>
_RE_NAV = re.compile(r'href="(/category/[a-z0-9]+/)"[^>]*>([^<]{2,14})<')
# \u8be6\u60c5\u64ad\u653e: dplayer data-config='{...}'\uff08\u65e7\u7248 config= \u517c\u5bb9\uff09
_RE_CONFIG = re.compile(r"data-config='(\{.*?\})'|config='(\{.*?\})'", re.S)
_RE_VIDURL = re.compile(r'"url"\s*:\s*"([^"]+)"')
_RE_NEXT = re.compile(r'class="next"[^>]*><a href="([^"]+)"')
_AD_CAT_RE = re.compile('(?i)app|\u4e0b\u8f7d|qq|\u5fae\u4fe1|\u63a8\u7279|tg\u7fa4|\u5bfc\u822a|\u8054\u7cfb|\u5408\u4f5c|\u90ae\u7bb1|\u5173\u4e8e|\u5b58\u6863|\u6536\u85cf|\u767b\u9646|\u767b\u5f55')




class Spider(BaseSpider):

    # \u7ad9\u65b9\u4e2d\u8f6c\u53d1\u5e03\u9875\uff08b64 \u58f3\uff0c\u89e3\u7801\u540e JS zz_line \u5217\u7ebf\u8def\u57fa\u57df\uff09
    PUBLISH_PAGE = 'https://t91bl.com/'
    # \u5185\u7f6e\u5019\u9009\uff082026-09-08 \u5b9e\u6d4b 200/204KB\uff0c\u6cdb\u89e3\u6790\u4efb\u610f\u8bcd\u5b50\u57df\u53ef\u7528\uff1b
    # 2026-09-11 \u8ffd\u52a0 dgebtuip.cc \u5f53\u524d\u56fa\u5b9a\u7ebf\u8def\uff0c\u9632 hostresolver \u672a\u52a0\u8f7d\u65f6\u88f8\u5954\uff09
    BUILTIN_HOSTS = [
        'https://borrow.dgebtuip.cc',
        'https://bank.dgebtuip.cc',
        'https://main.quibepqh.cc',
        'https://apple.quibepqh.cc',
        'https://main.matutgbj.cc',
        'https://apple.matutgbj.cc',
        'https://dle7ftqaeg81q.cloudfront.net',
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
        return "91\u7206\u6599"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

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
            if param.get('type') == 'blimg':
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
        """\u5c01\u9762\u7edf\u4e00\u8d70\u4ee3\u7406\uff08\u56fe\u5e8a\u4e3a\u52a0\u5bc6\u56fe\uff0c\u4ee3\u7406\u5185 magic \u9884\u68c0+\u89e3\u5bc6+\u7f13\u5b58\uff09\u3002"""
        if not u:
            return ''
        return f'{self.getProxyUrl()}&url={self.e64(u)}&type=blimg'

    def _resolve_inline(self, publish, builtin, validate):
        """hostresolver \u672a\u52a0\u8f7d\u65f6\u7684\u5185\u8054\u5e76\u884c\u63a2\u6d4b\uff1a\u907f\u514d\u4e32\u884c 8s\u00d7N \u5bfc\u81f4 App \u7aef\u7a7a\u8f6c\u51e0\u5341\u79d2\u3002
        \u5e26\u6781\u7b80\u5185\u5bb9\u5f62\u6001\u5224\uff0c\u9632\u6b62\u547d\u4e2d\u53d1\u5e03\u9875/\u95e8\u6237\u516c\u544a\u9875\uff08\u6709\u7ad9\u540d\u4f46\u65e0\u5185\u5bb9\uff09\u3002"""
        import threading
        import re
        candidates = []
        if publish:
            candidates.append(publish)
        candidates += list(self._ext.get('hosts') or [])
        candidates += list(builtin or [])
        seen = set()
        deduped = []
        for u in candidates:
            u = (u or '').strip().rstrip('/')
            if not u:
                continue
            if not u.startswith('http'):
                u = 'https://' + u
            if u not in seen:
                seen.add(u)
                deduped.append(u)
        if not deduped:
            return ''
        result = [None]
        content_marks = ('<article', 'post-card', 'entry-title', 'post-title',
                         'video-item', 'oneVideo', 'playlist', 'class="video')
        content_link_pat = re.compile(
            r'href=["\'][^"\']*/(?:archives?|video|videos|category|categories|post|vod|'
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
        """\u52a8\u6001\u57df\u540d\u89e3\u6790 v2.3\uff08hostresolver\uff09\uff1aext \u9501\u5b9a \u2192 \u53d1\u5e03\u9875\u62bd\u94fe(\u542b\u53cd\u5f15\u53f7\u7ebf\u8def\u8868)\u5e76\u884c
        \u5b9e\u6d4b \u2192 ext/\u5185\u7f6e\u5019\u9009\u5e76\u884c\u515c\u5e95 \u2192 \u5bfc\u822a\u7ad9\u63a2\u7d22\u3002\u5168\u5931\u8d25\u8fd4\u56de ''\uff08\u63a5\u53e3\u5c42\u515c\u7a7a\uff1aApp \u7aef
        \u8868\u73b0\u4e3a\u300c\u660e\u786e\u5931\u8d25\u300d\u800c\u975e 50 \u79d2\u9759\u9ed8\u7a7a\u8f6c\uff09\u3002"""
        publish = self._ext.get('publish') or self.PUBLISH_PAGE
        builtin = self.BUILTIN_HOSTS

        def _validate(host, text):
            return '91\u7206\u6599' in (text or '')

        if resolve_host:
            try:
                h = resolve_host(
                    publish_page=publish,
                    candidate_hosts=list(self._ext.get('hosts') or []) + builtin,
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=8,
                    validate=_validate,
                    site_key='91\u7206\u6599',
                )
                if h:
                    return h
            except Exception:
                pass
        # \u515c\u5e95\uff1ahostresolver \u5df2\u52a0\u8f7d\u5219\u7528 probe_first\uff1b\u672a\u52a0\u8f7d/\u5931\u8d25\u5219\u5185\u8054\u5e76\u884c\u63a2\u6d4b
        cands = list(self._ext.get('hosts') or []) + builtin
        if probe_first:
            try:
                h = probe_first(cands, headers=self.headers, proxies=self.proxies,
                                timeout=5, validate=_validate, tag='\u515c\u5e95')
                if h:
                    return h
            except Exception:
                pass
        h = self._resolve_inline(publish, builtin, _validate)
        if h:
            return h
        # \u7ec8\u6781\u515c\u5e95\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\uff08\u8df3\u8f6c\u58f3/\u95e8\u6237/\u6cdb\u89e3\u6790\u8ddf\u968f + \u7ad9\u540d\u8eab\u4efd\u9a8c\u8bc1\uff09
        if explore_hosts:
            try:
                def _probe(u):
                    r = requests.get(u.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=5, verify=False)
                    return r.status_code == 200 and '91\u7206\u6599' in (r.text or '')
                hs = explore_hosts(['91bl', '\u7206\u6599'], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        return ''

    def _get(self, path):
        url = path if path.startswith('http') else self.host + path
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False, allow_redirects=True)

    def _parse_list(self, html_text):
        out = []
        seen = set()
        for m in _RE_ITEM.finditer(html_text or ''):
            blk = m.group(1)
            ml = _RE_LINK.search(blk)
            if not ml:
                continue
            link, aid = ml.group(1), ml.group(2)
            if aid in seen:
                continue
            seen.add(aid)
            mt = _RE_TITLE.search(blk)
            title = _html.unescape(mt.group(1)).strip() if mt else ''
            if not title:
                continue
            pic = ''
            mu = _RE_COVER.search(blk)
            if mu:
                pic = _html.unescape(mu.group(1)).strip()
            out.append({
                'vod_id': link,
                'vod_name': title,
                'vod_pic': self._pic(pic),
                'vod_remarks': '',
            })
        return out


    def homeContent(self, flag):
        result = {'class': [], 'list': []}
        body = ''
        try:
            body = self._get('/').text or ''
        except Exception:
            pass
        seen = set()
        for m in _RE_NAV.finditer(body):
            path, name = m.group(1), _html.unescape(m.group(2)).strip()
            slug = path.split('/')[2]
            if slug in seen or not name or _AD_CAT_RE.search(name):
                continue
            seen.add(slug)
            result['class'].append({'type_id': slug, 'type_name': name})
        if not result['class']:
            result['class'] = [{'type_id': k, 'type_name': v} for k, v in _CATS.items()]
        try:
            result['list'] = self._parse_list(body)
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
        path = f'/category/{tid}/'
        if str(pg) not in ('1', ''):
            path = f'/category/{tid}/{pg}/'
        try:
            result['list'] = self._parse_list(self._get(path).text or '')
        except Exception:
            pass
        return result

    def _searchContent(self, key, quick, pg='1'):
        result = {'list': []}
        try:
            path = f'/search/{quote(key)}/'
            if str(pg) not in ('1', ''):
                path = f'/search/{quote(key)}/page/{pg}/'
            result['list'] = self._parse_list(self._get(path).text or '')
        except Exception:
            pass
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    @staticmethod
    def _videos(html_text):
        """\u6309 dplayer data-config \u62bd\u5206\u96c6\uff08\u8d34\u7247\u5e7f\u544a\u7d20\u6750\u4e0d\u5728 dplayer \u5185\uff0c\u5929\u7136\u6392\u9664\uff09\u3002
        url = \u7ad9\u5185\u7968\u636e\u7aef\u70b9 /action/player/get_play_url?cid=..&idx=..\uff08\u64ad\u653e\u65f6\u4e24\u6b65\u53d6\u771f m3u8\uff09\u3002"""
        vids = []
        for m in _RE_CONFIG.finditer(html_text or ''):
            c = m.group(1) or m.group(2)
            if not c:
                continue
            try:
                s = c.replace('&quot;', '"').replace('&#34;', '"').replace('&amp;', '&')
                cfg = json.loads(s)
                mv = cfg.get('video') or {}
                # 91\u7206\u6599\u4e3a ArtPlayer \u6241\u5e73\u7ed3\u6784\uff08url/poster \u9876\u5c42\uff09\uff1b\u517c\u5bb9\u9ed1\u6599\u7cfb video:{} \u5d4c\u5957
                u = str(mv.get('url') or cfg.get('url') or '').replace('\\/', '/')
                poster = str(mv.get('poster') or cfg.get('poster') or '').replace('\\/', '/')
            except Exception:
                mv2 = _RE_VIDURL.search(c)
                u = mv2.group(1).replace('\\/', '/') if mv2 else ''
                poster = ''
            if u:
                vids.append({'url': u, 'poster': poster})
        return vids

    def _resolve_play(self, url):
        """\u4e24\u6b65\u7968\u636e\uff1aPOST /action/player/ticket \u53d6\u77ed\u671f\u4e00\u6b21\u6027\u7968\uff08120s\uff09\u2192 POST \u6362\u7b7e\u540d m3u8\u3002
        \u670d\u52a1\u7aef env \u9a8c\u7b7e\u5bbd\u677e\uff08\u7a7a env \u53ef\u8fc7\uff09\u3002"""
        m = re.search(r'cid=(\d+)&idx=(\d+)', url)
        if not m:
            return url
        cid, idx = m.group(1), m.group(2)
        try:
            tk_url = f'{self.host}/action/player/ticket?cid={cid}&idx={idx}&_={int(time.time()*1000)}'
            r1 = requests.post(tk_url, headers=self.headers, proxies=self.proxies, timeout=10, verify=False)
            tr = r1.json()
            if tr.get('status') != 0 or not (tr.get('data') or {}).get('ticket'):
                return ''
            ticket = tr['data']['ticket']
            r2 = requests.post(f'{self.host}/action/player/get_play_url?cid={cid}&idx={idx}',
                               headers=self.headers, proxies=self.proxies, timeout=10, verify=False,
                               data={'ticket': ticket, 'env': '{}', '_ver': 'v0'})
            pr = r2.json()
            if pr.get('status') == 0 and pr.get('data'):
                return pr['data']
        except Exception:
            pass
        return ''

    def detailContent(self, ids):
        result = {'list': []}
        try:
            link = str(ids[0])
            body = self._get(link).text or ''
            title = ''
            m = re.search(r'<title>([^<]+)</title>', body)
            if m:
                title = _html.unescape(m.group(1)).strip()
                title = re.sub('\\s*-\\s*91\u7206\u6599\\s*$', '', title).strip()
            pic = ''
            vids = self._videos(body)
            if vids and vids[0].get('poster'):
                pic = self._pic(vids[0]['poster'])
            vids = self._videos(body)
            if vids:
                play = '#'.join(f'第{i + 1}集${link}-{i}' for i in range(len(vids)))
            else:
                play = f'第1集${link}-0'
            result['list'].append({
                'vod_id': link,
                'vod_name': title or link,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': '',
                'vod_director': '',
                'vod_content': '',
                'vod_play_from': '91bl',
                'vod_play_url': play,
            })
        except Exception:
            pass
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {'parse': 0, 'playUrl': '', 'url': '', 'header': {'User-Agent': _UA}}
        try:
            link, idx = (str(id).rsplit('-', 1) + ['0'])[:2]
            body = self._get(link).text or ''
            vids = self._videos(body)
            i = int(idx) if idx.isdigit() else 0
            if vids:
                u = vids[min(i, len(vids) - 1)]['url']
                if 'get_play_url' in u:
                    u = self._resolve_play(u)
                if u and not u.startswith('http'):
                    u = self.host + u
                result['url'] = u
                result['header'] = {'User-Agent': _UA, 'Referer': self.host + '/'}
        except Exception:
            pass
        return result
