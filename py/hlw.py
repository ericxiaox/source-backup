# -*- coding: utf-8 -*-
# HLW \u7ad9\u6e90\uff08\u9ed1\u6599\u7f51 \u00b7 Typecho \u98ce\u683c HTML \u76f4\u6293\u7248\uff09
# \u53d1\u5e03\u9875: hlwf6.com\uff08"\u9ed1\u6599\u7f51\u6700\u65b0\u5165\u53e3-\u5b9e\u65f6\u66f4\u65b0\u8bbf\u95ee\u7ebf\u8def"\uff0c2026-09-08 \u5b9e\u6d4b 200\uff0c
#         \u5217 4 \u4e2a .cc \u6cdb\u57fa\u57df\u7ebf\u8def + cloudfront \u515c\u5e95\uff0c\u57fa\u57df\u8f6e\u6362\u540e\u53d1\u5e03\u9875\u5373\u66f4\u65b0\uff09
# \u7ed3\u6784: \u5206\u7c7b /{slug}/ \u7ffb\u9875 /{slug}/page/{n}/\uff1b\u8be6\u60c5 /archives/{id}/
#       \u5217\u8868\u6761\u76ee video-item\uff08\u5c01\u9762 img \u7684 z-image-loader-url \u5c5e\u6027 + alt \u6807\u9898\uff09
#       \u64ad\u653e dplayer config='{...}' JSON\uff08\/ \u8f6c\u4e49\u987b\u8fd8\u539f\uff09\uff0c\u591a\u89c6\u9891=\u591a config \u5757
import json
import re
import sys
import os
import html as _html
import base64
from collections import OrderedDict
from urllib.parse import quote

import requests
from Crypto.Cipher import AES
sys.path.append('..')
from base.spider import Spider as BaseSpider


try:
    from hostresolver import resolve_host, parse_ext, probe_first
except Exception:
    # hostresolver.py \u5728\u5305\u6839\uff08py/ \u7684\u4e0a\u7ea7\uff09\u3002App \u7aef\uff08gitee \u52a0\u8f7d\uff09\u5b83\u4e0d\u5728\u73b0\u573a\uff0c
    # \u5bfc\u5165\u5fc5\u987b\u53ef\u964d\u7ea7\u4e3a None \u2192 \u8fd0\u884c\u65f6\u8d70 self._resolve_inline \u5185\u8054\u515c\u5e95\u3002\u6a21\u5757\u7ea7\u7981\u88f8\u5bfc\u5165\u3002
    try:
        import os as _os
        sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
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

# \u2500\u2500 \u5c01\u9762\u56fe\u5e8a\uff1apic.hdhwqx.cn \u4e3a CDN \u7ea7 AES \u52a0\u5bc6\u56fe\uff08\u4e0e\u9ed1\u6599\u4e0d\u6253\u70ca\u540c\u6b3e key\uff09\uff0c
#    App \u76f4\u63a5\u52a0\u8f7d\u662f\u5bc6\u6587=\u5c01\u9762\u5168\u7a7a\uff0c\u7edf\u4e00\u8d70 localProxy \u53d6\u56fe+\u6309\u9700\u89e3\u5bc6+LRU \u7f13\u5b58
_img_session = requests.Session()
_img_session.verify = False
_img_cache = OrderedDict()
_IMG_CACHE_MAX = 60


def _img_fetch(url, referer):
    """\u53d6\u56fe+magic \u9884\u68c0+\u6309\u9700\u89e3\u5bc6+\u7f13\u5b58\uff0c\u8fd4\u56de (status, content_type, bytes)\u3002"""
    if url in _img_cache:
        _img_cache.move_to_end(url)
        return (200,) + _img_cache[url]
    h = {'User-Agent': _UA, 'Referer': referer}
    try:
        r = _img_session.get(url, headers=h, timeout=10)
    except Exception:
        return [404, 'text/plain', b'']
    if r.status_code != 200:
        return [404, 'text/plain', b'']
    raw = r.content
    ct = 'image/jpeg'
    if raw[:3] == b'\xff\xd8\xff':
        b = raw
    elif raw[:8] == b'\x89PNG\r\n\x1a\n':
        b, ct = raw, 'image/png'
    elif raw[:4] == b'GIF8':
        b, ct = raw, 'image/gif'
    else:
        try:
            b = AES.new(b'f5d965df75336270', AES.MODE_CBC, b'97b60394abc2fbe1').decrypt(raw)
        except Exception:
            return [404, 'text/plain', b'']
        if b[:8] == b'\x89PNG\r\n\x1a\n':
            ct = 'image/png'
        elif b[:4] == b'GIF8':
            ct = 'image/gif'
    if b:
        _img_cache[url] = (ct, b)
        if len(_img_cache) > _IMG_CACHE_MAX:
            _img_cache.popitem(last=False)
    return [200, ct, b]

# \u5217\u8868\u6761\u76ee: <a class="cursor-pointer" href="/archives/{id}/"> ... z-image-loader-url="\u5c01\u9762" alt="\u6807\u9898"
_RE_CARD = re.compile(
    r'<a[^>]*href="(/archives/(\d+)/)"[^>]*>\s*<div[^>]*>.*?z-image-loader-url="([^"]+)"[^>]*alt="([^"]*)"',
    re.S)
# \u641c\u7d22\u7ed3\u679c\u6761\u76ee: <li class="tag-item"><a href="/archives/{id}/">\u6807\u9898</a>
_RE_SEARCH = re.compile(r'<a[^>]*href="(/archives/(\d+)/)"[^>]*>([^<]{2,80})</a>')
# \u64ad\u653e config JSON\uff08\u5355\u5f15\u53f7\u5305\u88f9\uff09
_RE_CONFIG = re.compile(r"config='(\{.*?\})'", re.S)
# \u5206\u7c7b\u5bfc\u822a: <a class="slider-item ..." href="/{slug}/"><div class="span">\u540d\u79f0</div>
_RE_NAV = re.compile(r'href="(/[a-z0-9\-]{2,10}/)"[^>]*>\s*<div class="span">([^<]{2,12})</div>')




class Spider(BaseSpider):

    # \u7ad9\u65b9\u53d1\u5e03\u9875
    PUBLISH_PAGE = 'https://hlwf6.com/'
    # \u5185\u7f6e\u5019\u9009\uff082026-09-08 \u53d1\u5e03\u9875\u5b9e\u6d4b\uff1a\u53d1\u5e03\u9875 5 \u6761\u7ebf\u8def\u4e2d\u4ec5 3 \u6761\u662f\u771f\u7ad9\u955c\u50cf\uff0c
    # rkrnimmm=18se\u5bfc\u822a\u5e7f\u544a\u7ad9\u3001bxouulcs=68\u5b57\u8282\u7a7a\u58f3\uff0c\u5df2\u5254\u9664\uff1b\u4ee5"\u6807\u9898\u542b\u9ed1\u6599\u7f51"\u9a8c\u8eab\uff09
    BUILTIN_HOSTS = [
        'https://fzyxd.vhksymsv.cc',
        'https://d3oyu.zbzrembr.cc',
        'https://ds6r63epm75a1.cloudfront.net',
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
        return "\u9ed1\u6599\u7f51"

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
        # \u591a\u53d1\u5e03\u9875\uff082026-09-13\uff09\uff1apublish \u53ef\u80fd\u662f\u9017\u53f7\u4e32\uff08\u7f51\u5740\u578b + GitHub \u578b\u5e76\u5b58\uff09\uff0c
        # \u62c6\u6210\u591a\u6761\u5019\u9009\u5206\u522b\u5e76\u884c\u6293\uff1b\u975e\u7edd\u5bf9\u5730\u5740\uff08\u76f8\u5bf9\u8def\u5f84\uff09\u65e0\u6cd5\u72ec\u7acb\u6293\u53d6\uff0c\u4e22\u5f03\u3002
        _pages = [x for x in re.split(r'[,\s;]+', str(publish or ''))
                  if x.startswith('http')]
        candidates += _pages or ([str(publish)] if publish else [])
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
        # \u7b2c\u4e09\u65b9\u5e73\u53f0/\u7edf\u8ba1\u57df\u4e0d\u5f97\u5f53\u76f4\u63a2\u5019\u9009\uff1aGitHub \u4ed3\u5e93\u9875 100KB+ \u81ea\u5e26 <article> \u4e14\u6b63\u6587\u542b
        # \u7ad9\u540d \u2192 validate \u5047\u901a\u8fc7\uff08\u6296\u9634 \u5b9e\u6d4b\u628a github.com/kissav12/douyin \u5f53\u6210\u7ad9\u70b9 host\uff09\u3002
        # \u53e3\u5f84\u5bf9\u9f50 hostresolver._JUNK_HOST_PAT\uff1b**\u53ea\u5254\u76f4\u63a2\u5019\u9009**\uff0c_pages \u4ecd\u539f\u6837\u8fdb\u6df1\u62bd\u94fe
        # \uff08GitHub README \u91cc\u7684\u73b0\u5f79\u7ebf\u8def\u7167\u62bd\u4e0d\u8bef\uff09\u3002
        deduped = [u for u in deduped if not re.search(
            r'(github\.|gitlab\.|gstatic|google\.|jquery|bootstrap|jsdelivr|unpkg|'
            r'fontawesome|baidu\.|bing\.|schema\.org|w3\.org)', u, re.I)]
        if not deduped:
            return ''
        result = [None]
        # \u5757\u7ea7\u5b89\u5168\u522b\u540d\uff082026-09-14\uff09\uff1a\u672c\u51fd\u6570\u5185**\u4e0d\u5f97**\u88f8\u7528 _hd / _px
        # \u2014\u2014 \u90e8\u5206\u6e90\uff082048\u77ed\u5267/\u9ec4\u679c\u77ed\u5267/\u9ed1\u6599\u4e0d\u6253\u70ca\uff09\u7684 init \u4ece\u672a\u5b9a\u4e49 _hd\uff0c
        # \u88f8\u7528\u5373 AttributeError \u88ab except \u541e\u6389 \u2192 \u5185\u8054\u515c\u5e95\u6574\u4f53\u9759\u9ed8\u5931\u6548\uff08\u5b9e\u6d4b 0.01s \u7a7a\u8fd4\uff09\u3002
        # \u26a0\u5fc5\u987b isinstance \u5224\u5b9a\uff1aApp \u7aef BaseSpider \u53ef\u80fd\u7ed9\u4efb\u610f\u7f3a\u5931\u5c5e\u6027\u8fd4\u56de\u53ef\u8c03\u7528\u5bf9\u8c61
        # \uff08\u58f3\u7ea7 __getattr__\uff09\uff0c\u53ea\u5224\u771f\u503c\u4f1a\u62ff\u5230 bound function \u2192
        # requests prepare_headers \u62a5 'function' object has no attribute 'items'
        # \u2192 \u5168\u90e8\u63a2\u6d4b\u77ac\u95f4\u70b8\u6389\u3001\u5185\u8054\u515c\u5e95\u9759\u9ed8\u7a7a\u8fd4\uff082026-09-14 \u5b9e\u6d4b\u63ea\u51fa\uff09\u3002
        _hd = getattr(self, 'headers', None)
        if not isinstance(_hd, dict):
            _hd = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/120.0.0.0 Safari/537.36'}
        _px = getattr(self, 'proxies', None)
        if not isinstance(_px, dict):
            _px = {}
        content_marks = ('<article', 'post-card', 'entry-title', 'post-title',
                         'video-item', 'oneVideo', 'playlist', 'class="video')
        content_link_pat = re.compile(
            r'href=["\'] [^"\']*/(?:archives?|video|videos|category|categories|post|vod|'
            r'watch|tag|detail|thread|topic)[/"\']', re.I)
        def _looks_like_content(t):
            return bool(t and (len(t) > 80000 or any(k in t for k in content_marks)
                               or len(content_link_pat.findall(t)) >= 5))
        def _unmask_page(_u, _t):
            """\u89e3\u58f3\uff1a\u8ddf\u8df3\u8f6c\u58f3\uff08<a href>\u52a0\u8f7d\u4e2d / location.replace\uff09\u2192 \u6574\u9875 b64 \u89e3\u7801\u3002

            \u26a0\u9ed1\u6599\u5bb6\u65cf 2026-09 \u73b0\u7f51\u53d1\u5e03\u94fe\u662f**\u4e24\u5c42\u58f3**\uff1a
              \u2460 \u8df3\u8f6c\u58f3 \u2248300B\uff1a`<a id=\u968f\u673a href=\u76ee\u6807\u57df>\u52a0\u8f7d\u4e2d...</a>` +
                 `<script>(function(v){... window.location.replace(v.href)})
                  (document.getElementById(\"\u968f\u673a\"))</script>`
                 \u2014\u2014 \u76ee\u6807\u5199\u5728 `<a href>` \u91cc\uff0cJS \u53ea\u5f15\u7528**\u53d8\u91cf**\u3002\u65e7\u7248\u53ea\u8ba4\u5b57\u9762\u91cf
                 `location.replace('...')` \u2192 \u8fd9\u7c7b\u9875\u9762\u6574\u9875\u62bd 0 \u6761\u3002
              \u2461 b64 \u58f3\uff1a`<script>document.write(Base64.decode(\"...\"))</script>`
                 \uff08\u7ad9\u65b9\u81ea\u5e26 Base64 polyfill\uff09\u2192 \u89e3\u7801\u540e\u662f**\u4e2d\u8f6c\u843d\u5730\u9875**\uff0c\u7ebf\u8def\u5199\u5728
                 `lineAry` / `backupLine`\uff08`words.random()+'.\u57fa\u57df'` \u6216\u57df\u540d\u6570\u7ec4\uff09\u3002
            \u4e0d\u8ddf\u7b2c\u4e00\u8df3 \u2192 \u62ff\u5230 300B \u7a7a\u58f3\uff1b\u4e0d\u89e3\u7b2c\u4e8c\u8df3 \u2192 \u89e3\u7801\u9875\u91cc\u7684 lineAry \u770b\u4e0d\u89c1\uff1b
            \u4efb\u4e00\u73af\u65ad\u62bd\u94fe\u90fd\u662f 0 \u6761 \u2192 \u53ea\u80fd\u5403\u5185\u7f6e\u6c60\uff0c\u6c60\u4e00\u8f6e\u6362/\u88ab DNS \u6c61\u67d3\u6574\u6e90\u5373\u6302
            \uff0851\u6697\u7f51 2026-09-14 \u5168\u6302\u590d\u76d8\uff09\u3002
            \u8fd4\u56de (\u6700\u7ec8URL, \u300c\u539f\u6587\uff0b\u5404\u8df3\u6587\u672c\uff0b\u89e3\u7801\u6587\u672c\u300d\u5408\u5e76\u4e32)\uff1b\u4efb\u4f55\u5f02\u5e38\u539f\u6837\u8fd4\u56de\u3002"""
            _acc = [_t or '']
            _cur = _u
            try:
                import base64 as _b64
                for _ in range(3):                       # \u6700\u591a 3 \u8df3\uff0c\u9632\u73af
                    _txt = _acc[-1]
                    if len(_txt) > 4000:                 # \u5927\u9875\u9762\u4e0d\u662f\u58f3
                        break
                    _m = re.search(r'<a[^>]+href\s*=\s*["\'](https?://[^"\']+)["\']',
                                   _txt, re.I)
                    if not _m:
                        _m = re.search(r'(?:window\.)?location\.(?:replace|href)\s*[=(]\s*'
                                       r'[\'"](https?://[^\'"]+)', _txt, re.I)
                    if not _m:
                        break
                    _nx = _m.group(1).rstrip('/')
                    if _nx == _cur.rstrip('/'):
                        break
                    _http = globals().get('requests') or globals().get('rq')
                    if _http is None:
                        break
                    _r2 = _http.get(_nx + '/', headers=_hd,
                                    proxies=_px, timeout=5,
                                    verify=False, allow_redirects=True)
                    if _r2.status_code != 200 or not _r2.text:
                        break
                    _cur = (_r2.url or _nx).rstrip('/')
                    _acc.append(_r2.text)
                for _b in re.findall(r'[A-Za-z0-9+/=]{400,}', _acc[-1]):
                    _b = _b + '=' * (-len(_b) % 4)
                    try:
                        _d = _b64.b64decode(_b).decode('utf-8')
                    except Exception:
                        continue
                    if '<' in _d and '>' in _d:
                        _acc.append(_d)
                        break
            except Exception:
                pass
            return _cur, '\n'.join(_acc)

        def _probe_one(u):
            if result[0]:
                return
            try:
                r = requests.get(u + '/', headers=_hd, proxies=_px,
                                 timeout=5, verify=False, allow_redirects=True)
                if r.status_code != 200:
                    return
                # \u89e3\u58f3\u5019\u9009\uff1a\u58f3\u672c\u8eab\u4e0d\u662f\u7ad9\uff1b\u89e3\u5f00\u540e\u7684\u6b63\u6587\uff08\u542b\u6700\u7ec8\u8df3\u8f6c\u843d\u70b9\uff09\u624d\u53ef\u80fd\u8fc7\u6821\u9a8c\u3002
                # host \u53d6**\u6700\u7ec8\u8df3\u8f6c\u843d\u70b9**\u2014\u2014\u7ad9\u53ef\u80fd\u5728\u4e0b\u4e00\u8df3\u57df\u540d\u4e0a\uff0c\u4e0d\u80fd\u8bb0\u6210\u58f3\u7684\u5730\u5740\u3002
                _fin, _mk = _unmask_page((r.url or u).rstrip('/'), r.text or '')
                for _ct in (r.text or '', _mk):
                    if validate(_fin, _ct) and _looks_like_content(_ct):
                        if not result[0]:
                            result[0] = _fin
                        break
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
            # \u591a\u53d1\u5e03\u9875**\u5e76\u884c**\u6293\u53d6\uff082026-09-13\uff09\uff1aN \u9875\u8017\u65f6 \u2248max\uff0c\u800c\u975e\u9010\u9875\u76f8\u52a0\u3002
            # \u542b JS \u58f3\u8ddf\u968f\u2014\u2014\u53d1\u5e03\u9875\u53ea\u6709\u7a7a\u5bb9\u5668\u3001\u771f\u5b9e\u7ebf\u8def\u5728 <script src="publish.js"> \u91cc
            # \uff08\u9ec4\u679c pages.dev/github.io \u540c\u6b3e\uff09\u3002\u6293\u56de\u7684 JS \u4e00\u5e76\u5e76\u5165 _pt \u4f9b\u4e0b\u65b9\u6b63\u5219\u62bd\u53d6\u3002
            # HTTP \u5ba2\u6237\u7aef\u540d\u9010\u6e90\u4e0d\u540c\uff1a\u591a\u6570\u6e90 `import requests`\uff0c\u9ec4\u679c\u662f `import requests as rq`\u3002
            # \u7edf\u4e00\u89e3\u6790\uff0c\u907f\u514d NameError \u88ab except \u541e\u6389 \u2192 \u6df1\u62bd\u94fe\u9759\u9ed8\u5931\u6548\u3002
            _http = globals().get('requests') or globals().get('rq')
            _texts = []
            _srcs = _pages if _pages else ([str(publish)] if publish else [])

            def _grab(_u):
                try:
                    _r = _http.get(_u, headers=_hd, proxies=_px,
                                      timeout=6, verify=False, allow_redirects=True)
                except Exception:
                    return
                if _r.status_code != 200 or not _r.text:
                    return
                _texts.append(_unmask_page(_u, _r.text)[1])
                for _s in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',
                                     _r.text, re.I)[:2]:
                    _s = _s.strip()
                    if not _s or _s.startswith('data:'):
                        continue
                    if not _s.startswith('http'):
                        _s = _u.rstrip('/') + '/' + _s.lstrip('/')
                    if re.search(r'(gstatic|google|jquery|bootstrap|jsdelivr|unpkg|'
                                 r'github|gitlab|baidu|cloudflare|fontawesome)', _s, re.I):
                        continue
                    try:
                        _jr = _http.get(_s, headers=_hd,
                                           proxies=_px, timeout=6,
                                           verify=False, allow_redirects=True)
                        if _jr.status_code == 200 and _jr.text:
                            _texts.append(_jr.text)
                    except Exception:
                        pass

            _gts = [threading.Thread(target=_grab, args=(u,)) for u in _srcs]
            for _gt in _gts:
                _gt.start()
            for _gt in _gts:
                _gt.join(timeout=8)
            _pt = '\n'.join(_texts)
            if _pt:
                # \u4f18\u5148\u4ece\u542b random() \u7684 <script> \u6bb5\u62bd\uff08\u90a3\u91cc\u624d\u662f\u6cdb\u89e3\u6790\u8bcd\u8868+\u57fa\u57df\uff09\uff0c\u515c\u5e95\u5168\u9875
                _chunks = [c for c in re.findall(r'<script[^>]*>(.*?)</script>', _pt, re.S | re.I)
                           if 'random(' in c]
                _wsrc = '\n'.join(_chunks) if _chunks else _pt
                _bases = []
                for _m in re.findall(r'''['"]\.?((?:[a-z0-9-]+\.)+(?:cc|com|net|top|xyz|vip|app|link|click|org|info|site|online|icu|club|fun|store|live|me|tv))/?['"]''', _wsrc, re.I):
                    _m = _m.lower().strip('.').strip()
                    if _m and _m not in _bases and _m.count('.') <= 2:
                        _bases.append(_m)
                if not _bases:
                    for _m in re.findall(r'''['"]\.?((?:[a-z0-9-]+\.)+(?:cc|com|net|top|xyz|vip|app|link|click|org|info|site|online|icu|club|fun|store|live|me|tv))/?['"]''', _pt, re.I):
                        _m = _m.lower().strip('.').strip()
                        if _m and _m not in _bases and _m.count('.') <= 2:
                            _bases.append(_m)
                # \u5254\u7b2c\u4e09\u65b9\u57df\uff08gitlab/github/\u7edf\u8ba1/\u5b57\u4f53\u7b49\u6df7\u5728\u9875\u9762 script src \u91cc\uff0c
                # \u4f1a\u88ab\u62bd\u51fa\u5f53\u57fa\u57df \u2192 \u751f\u6210 viewport.gitlab.com \u8fd9\u7c7b\u65e0\u6548\u5019\u9009\u767d\u8017\u63a2\u6d4b\uff09
                _bases = [b for b in _bases if not re.search(
                    r'(google|gstatic|baidu|jquery|bootstrap|jsdelivr|unpkg|'
                    r'github|gitlab|cloudflare|fontawesome|w3\.org|schema\.org|'
                    r'twitter|youtube|apple|microsoft|bing)', b, re.I)]
                # \u8865\u9f50\u300c\u660e\u6587\u5916\u94fe\u7ebf\u8def\u300d\u5f62\u6001\uff082026-09-14\uff09\uff1a\u9ed1\u6599\u7f51 hlwf6.com / \u6bcf\u65e5\u5927\u4e71\u6597
                # idld66.com \u8fd9\u7c7b**\u5bfc\u822a\u578b\u53d1\u5e03\u9875**\u628a\u73b0\u5f79\u7ebf\u8def\u5199\u6210 <a href="https://\u8bcd.\u57fa\u57df">
                # \u660e\u6587\uff0c\u6ca1\u6709\u4efb\u4f55\u5f15\u53f7\u5305\u88f9 \u2192 \u4e0a\u9762\u4e24\u6761\u6b63\u5219\u62bd 0 \u6761 \u2192 \u6df1\u62bd\u94fe\u7a7a\u8f6c\u3002
                # hostresolver \u4fa7\u7531 _scan_text \u6536 href \u8fdb static \u8986\u76d6\uff0c\u5185\u8054\u4fa7\u9700\u8865\u8fd9\u4e00\u73af\u3002
                for _h in re.findall(r'https?://([a-z0-9.-]+\.[a-z]{2,15})', _pt, re.I):
                    _h = _h.lower()
                    if _h not in _bases and _h.count('.') <= 2:
                        _bases.append(_h)
                _bases = [b for b in _bases if not re.search(
                    r'(google|gstatic|baidu|jquery|bootstrap|jsdelivr|unpkg|'
                    r'github|gitlab|cloudflare|fontawesome|w3\.org|schema\.org|'
                    r'twitter|youtube|apple|microsoft|bing)', b, re.I)]
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

        # \u8eab\u4efd\u6821\u9a8c\uff1a\u53d1\u5e03\u9875\u6df7\u6709\u5e7f\u544a\u95e8\u7ad9\uff08\u5982 18se\u5bfc\u822a\uff09\uff0c\u6807\u9898/\u6b63\u6587\u4e0d\u542b\u7ad9\u540d\u7684\u4e0d\u7b97\u771f\u7ad9
        def _validate(host, text):
            return '\u9ed1\u6599\u7f51' in (text or '')

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
                    t = r.text or ''
                    # \u52a0\u5bc6\u5c01\u9762\u4e3b\u9898\u7279\u5f81 + \u7ad9\u540d\u53cc\u6761\u4ef6\uff08\u9632\u300c818\u9ed1\u6599\u7f51\u300d\u7b49\u540c\u540d\u7ad9\u6df7\u5165\uff09
                    return r.status_code == 200 and '\u9ed1\u6599\u7f51' in t and 'z-image-loader-url' in t
                hs = explore_hosts(['hlw', '\u9ed1\u6599\u7f51'], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        # \u5168\u8d25\uff1a\u663e\u5f0f\u8fd4\u56de\u7a7a\uff08\u63a5\u53e3\u5c42\u79d2\u7a7a\uff0c\u4e0d\u518d\u56de\u9000\u6b7b\u57df\u9759\u9ed8\u7a7a\u8f6c\uff09
        return ''

    def _should_pic(self, url):
        """\u52a0\u5bc6\u56fe\u5e8a\u5224\u5b9a\uff1apic.* \u57df\u540d + \u5df2\u77e5\u52a0\u5bc6\u8def\u5f84\u524d\u7f00\u3002"""
        u = (url or '').lower()
        host = u.split('/')[2] if u.startswith('http') and u.count('/') > 2 else ''
        return any(x in u for x in ['pic.hdhwqx.cn', '/upload_01/', '/hc237/']) or host.startswith('pic.')

    def e64(self, s):
        try:
            return base64.b64encode((s or '').encode()).decode()
        except Exception:
            return ''

    def d64(self, s):
        try:
            return base64.b64decode((s or '').encode()).decode()
        except Exception:
            return ''

    def _pic(self, u):
        """\u52a0\u5bc6\u56fe\u5e8a\u5c01\u9762\u7edf\u4e00\u8d70\u4ee3\u7406\uff1b\u5176\u4f59\u76f4\u8fde\u3002"""
        u = _html.unescape(u or '').strip()
        if not u:
            return ''
        if self._should_pic(u):
            return f'{self.getProxyUrl()}&url={self.e64(u)}&type=hlwimg'
        return u

    def _get(self, path):
        url = path if path.startswith('http') else self.host + path
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False)

    def _parse_cards(self, html_text):
        out = []
        seen = set()
        for m in _RE_CARD.finditer(html_text):
            vid = m.group(2)
            if vid in seen:
                continue
            seen.add(vid)
            out.append({
                'vod_id': vid,
                'vod_name': _html.unescape(m.group(4)).strip() or vid,
                'vod_pic': self._pic(m.group(3)),
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
            slug, name = m.group(1).strip('/'), _html.unescape(m.group(2)).strip()
            if slug in seen or not name:
                continue
            seen.add(slug)
            result['class'].append({'type_id': slug, 'type_name': name})
        result['list'] = self._parse_cards(body)
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
        path = f'/{tid}/page/{pg}/' if str(pg) not in ('1', '') else f'/{tid}/'
        try:
            result['list'] = self._parse_cards(self._get(path).text or '')
        except Exception:
            pass
        return result

    def _searchContent(self, key, quick, pg='1'):
        result = {'list': []}
        try:
            body = self._get(f'/index/search?search_term_string={quote(key)}').text or ''
            seen = set()
            for m in _RE_SEARCH.finditer(body):
                vid = m.group(2)
                if vid in seen:
                    continue
                seen.add(vid)
                result['list'].append({
                    'vod_id': vid,
                    'vod_name': _html.unescape(m.group(3)).strip(),
                    'vod_pic': '',
                    'vod_remarks': '',
                })
        except Exception:
            pass
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    @staticmethod
    def _videos(html_text):
        """\u4ece\u8be6\u60c5\u9875\u63d0\u53d6\u5168\u90e8\u89c6\u9891 config \u2192 [{url,pic}...]"""
        vids = []
        for m in _RE_CONFIG.finditer(html_text):
            try:
                cfg = json.loads(m.group(1).replace('\\/', '/'))
                v = cfg.get('video') or {}
                url = str(v.get('url') or '').strip()
                if url:
                    vids.append({'url': url, 'pic': str(v.get('pic') or '').strip()})
            except Exception:
                continue
        return vids

    def detailContent(self, ids):
        result = {'list': []}
        try:
            vid = str(ids[0])
            body = self._get(f'/archives/{vid}/').text or ''
            title = ''
            m = re.search(r'<title>([^<]+)</title>', body)
            if m:
                title = _html.unescape(m.group(1)).strip()
                title = re.sub('-\u9ed1\u6599\u7f51\\s*$', '', title).strip()
            pic = ''
            mi = re.search(r'z-image-loader-url="([^"]+)"', body)
            if mi:
                pic = self._pic(mi.group(1))
            vids = self._videos(body)
            if vids:
                play = '#'.join(f'第{i + 1}集${vid}-{i}' for i in range(len(vids)))
            else:
                play = f'第1集${vid}-0'
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
                'vod_play_from': 'hlw',
                'vod_play_url': play,
            })
        except Exception:
            pass
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {'parse': 0, 'playUrl': '', 'url': '', 'header': {'User-Agent': _UA}}
        try:
            vid, idx = (str(id).split('-') + ['0'])[:2]
            body = self._get(f'/archives/{vid}/').text or ''
            vids = self._videos(body)
            i = int(idx) if idx.isdigit() else 0
            if vids:
                result['url'] = vids[min(i, len(vids) - 1)]['url']
                result['header'] = {'User-Agent': _UA, 'Referer': self.host + '/'}
        except Exception:
            pass
        return result

    def localProxy(self, param):
        try:
            if param.get('type') == 'hlwimg':
                url = self.d64(param.get('url'))
                if url.startswith('//'):
                    url = 'https:' + url
                elif url.startswith('/'):
                    url = self.host + url
                return _img_fetch(url, self.host + '/')
        except Exception as e:
            print(f'[ERROR] localProxy: {e}')
        return [404, 'text/plain', b'']
