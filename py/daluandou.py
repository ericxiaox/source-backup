import json
import re
import sys
import hashlib
from base64 import b64decode, b64encode
from urllib.parse import urlparse

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider as BaseSpider
try:
    from imgfetch import fetch_img as _shared_fetch_img
except Exception:
    try:
        import os as _os
        sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        from imgfetch import fetch_img as _shared_fetch_img
    except Exception:
        _shared_fetch_img = None

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

img_cache = {}



class Spider(BaseSpider):

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
                if parse_ext:
                    try:
                        self._ext = parse_ext(ext_str)
                    except Exception:
                        self._ext = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        }
        self.host = self.get_working_host()
        self.headers.update({'Origin': self.host, 'Referer': f"{self.host}/"})
        print(f"使用站点: {self.host}")

    def getName(self):
        return "\U0001f308 \u6bcf\u65e5\u5927\u4e71\u6597|\u7ec8\u6781\u5b8c\u7f8e\u7248"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        global img_cache
        img_cache.clear()

    def _resolve_inline(self, publish, builtin, validate):
        """hostresolver \u672a\u52a0\u8f7d\u65f6\u7684\u5185\u8054\u5e76\u884c\u63a2\u6d4b\uff1a\u907f\u514d\u4e32\u884c 8s\u00d7N \u5bfc\u81f4 App \u7aef\u7a7a\u8f6c\u51e0\u5341\u79d2\u3002
        \u5e26\u6781\u7b80\u5185\u5bb9\u5f62\u6001\u5224\uff0c\u9632\u6b62\u547d\u4e2d\u53d1\u5e03\u9875/\u95e8\u6237\u516c\u544a\u9875\uff08\u6709\u7ad9\u540d\u4f46\u65e0\u5185\u5bb9\uff09\u3002"""
        import threading
        import re
        ext = getattr(self, '_ext', {}) or {}
        candidates = []
        # \u591a\u53d1\u5e03\u9875\uff082026-09-13\uff09\uff1apublish \u53ef\u80fd\u662f\u9017\u53f7\u4e32\uff08\u7f51\u5740\u578b + GitHub \u578b\u5e76\u5b58\uff09\uff0c
        # \u62c6\u6210\u591a\u6761\u5019\u9009\u5206\u522b\u5e76\u884c\u6293\uff1b\u975e\u7edd\u5bf9\u5730\u5740\uff08\u76f8\u5bf9\u8def\u5f84\uff09\u65e0\u6cd5\u72ec\u7acb\u6293\u53d6\uff0c\u4e22\u5f03\u3002
        _pages = [x for x in re.split(r'[,\s;]+', str(publish or ''))
                  if x.startswith('http')]
        candidates += _pages or ([str(publish)] if publish else [])
        candidates += list(ext.get('hosts') or [])
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
            r'href=["\'][^"\']*/(?:archives?|video|videos|category|categories|post|vod|'
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
        """\u52a8\u6001\u57df\u540d\u89e3\u6790 v2\uff08hostresolver\uff09\uff1aext \u9501\u5b9a \u2192 \u53d1\u5e03\u9875\u9759\u6001\u955c\u50cf\u5e76\u884c\u5b9e\u6d4b
        \u2192 \u65e7\u57df302\u8ddf\u968f\u515c\u5e95 \u2192 \u6210\u529f\u7f13\u5b5830\u5206\u949f\u3002\u5168\u5931\u8d25\u8fd4\u56de ''\uff08\u63a5\u53e3\u5c42\u515c\u7a7a\uff09\u3002
        2026-09-08 \u5b9e\u6d4b\uff1abshzjjgq \u57fa\u57df\u5df2\u8f6e\u6362\u4e3a loewkgyyv.cc\uff08border 302 \u4ecd\u6d3b\uff09\uff1b
        \u7ad9\u65b9\u53d1\u5e03\u95e8\u6237 idld65.com \u9759\u6001\u5217\u51fa capture/carrier/center.loewkgyyv.cc \u73b0\u5f79\u955c\u50cf\u3002"""
        ext = getattr(self, '_ext', {}) or {}
        if ext.get('host'):
            return ext['host'].rstrip('/')
        publish = ext.get('publish') or 'https://gitlab.com/group305134/mrdld/-/raw/main/README.md'
        builtin_hosts = [
            'https://border.ekszkcyce.cc/',   # 2026-09-11 \u5f53\u524d\u6d3b\u955c\u50cf
            'https://capture.ekszkcyce.cc/',
            'https://border.loewkgyyv.cc/',   # 2026-09-08 \u5b9e\u6d4b\u73b0\u5f79\u955c\u50cf(190KB\u5b8c\u6574\u7ad9)
            'https://capture.loewkgyyv.cc/',
            'https://fe7.loewkgyyv.cc/',
            'https://border.bshzjjgq.cc/',    # \u65e7\u57fa\u57df\uff0c302 -> loewkgyyv.cc
        ]

        def _validate(host, text):
            return '\u6bcf\u65e5\u5927\u4e71\u6597' in (text or '')

        if resolve_host:
            h = resolve_host(
                publish_page=publish,
                candidate_hosts=list(ext.get('hosts') or []) + builtin_hosts,
                headers=self.headers,
                proxies=self.proxies,
                timeout=8,
                validate=_validate,
                site_key='\u6bcf\u65e5\u5927\u4e71\u6597',
            )
            if h:
                return h
        # \u515c\u5e95\uff1ahostresolver \u5df2\u52a0\u8f7d\u5219\u7528 probe_first\uff1b\u672a\u52a0\u8f7d\u5219\u5185\u8054\u5e76\u884c\u63a2\u6d4b
        cands = list(ext.get('hosts') or []) + builtin_hosts
        if probe_first:
            try:
                h = probe_first(cands, headers=self.headers, proxies=self.proxies,
                                timeout=5, validate=_validate, tag='\u515c\u5e95')
                if h:
                    return h
            except Exception:
                pass
        else:
            h = self._resolve_inline(publish, builtin_hosts, _validate)
            if h:
                return h
        # \u7ec8\u6781\u515c\u5e95\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\uff08\u8df3\u8f6c\u58f3/\u95e8\u6237/\u6cdb\u89e3\u6790\u8ddf\u968f + \u7ad9\u540d\u8eab\u4efd\u9a8c\u8bc1\uff09
        if explore_hosts:
            try:
                def _probe(u):
                    r = requests.get(u.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=5, verify=False)
                    return r.status_code == 200 and '\u6bcf\u65e5\u5927\u4e71\u6597' in (r.text or '')
                hs = explore_hosts(['dldd', '\u5927\u4e71\u6597'], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        return ''

    def homeContent(self, filter):

        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200: return {'class': [], 'list': []}
            data = self.getpq(response.text)
            
            classes = []
            category_selectors = ['.category-list ul li', '.nav-menu li', '.menu li', 'nav ul li']
            for selector in category_selectors:
                for k in data(selector).items():
                    link = k('a')
                    href = (link.attr('href') or '').strip()
                    name = (link.text() or '').strip()
                    if not href or href == '#' or not name: continue
                    classes.append({'type_name': name, 'type_id': href})
                if classes: break
            
            if not classes:
                classes = [{'type_name': '\u6700\u65b0', 'type_id': '/latest/'}, {'type_name': '\u70ed\u95e8', 'type_id': '/hot/'}]
            
            return {'class': classes, 'list': self.getlist(data('#index article, article'))}
        except Exception as e:
            return {'class': [], 'list': []}

    def homeVideoContent(self):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200: return {'list': []}
            data = self.getpq(response.text)
            return {'list': self.getlist(data('#index article, article'))}
        except Exception as e:
            return {'list': []}

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
        try:
            if '@folder' in tid:
                v = self.getfod(tid.replace('@folder', ''))
                return {'list': v, 'page': 1, 'pagecount': 1, 'limit': 90, 'total': len(v)}
            
            pg = int(pg) if pg else 1
            
            if tid.startswith('http'):
                base_url = tid.rstrip('/')
            else:
                path = tid if tid.startswith('/') else f"/{tid}"
                base_url = f"{self.host}{path}".rstrip('/')
            
            if pg == 1:
                url = f"{base_url}/"
            else:
                url = f"{base_url}/{pg}/"
                
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200: return {'list': [], 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 0}
                
            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article, #index article, article'), tid)
            
            return {'list': videos, 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 999999}
        except Exception as e:
            return {'list': [], 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 0}

    def detailContent(self, ids):
        try:
            url = ids[0] if ids[0].startswith('http') else f"{self.host}{ids[0]}"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            data = self.getpq(response.text)
            
            plist = []
            used_names = set()
            if data('.dplayer'):
                for c, k in enumerate(data('.dplayer').items(), start=1):
                    try:
                        config_attr = k.attr('data-config')
                        if config_attr:
                            config = json.loads(config_attr)
                            video_url = config.get('video', {}).get('url', '')
                            
                            if video_url:
                                ep_name = ''
                                parent = k.parents().eq(0)
                                for _ in range(4):
                                    if not parent: break
                                    heading = parent.find('h2, h3, h4').eq(0).text().strip()
                                    if heading:
                                        ep_name = heading
                                        break
                                    parent = parent.parents().eq(0)
                                
                                base_name = ep_name if ep_name else f"视频{c}"
                                name = base_name
                                count = 2
                                while name in used_names:
                                    name = f"{base_name} {count}"
                                    count += 1
                                used_names.add(name)
                                
                                plist.append(f"{name}${video_url}")
                    except: continue
            
            if not plist:
                content_area = data('.post-content, article')
                for i, link in enumerate(content_area('a').items(), start=1):
                    link_text = link.text().strip()
                    link_href = link.attr('href')
                    
                    if link_href and any(kw in link_text for kw in ['\u70b9\u51fb\u89c2\u770b', '\u89c2\u770b', '\u64ad\u653e', '\u89c6\u9891', '\u7b2c\u4e00\u5f39', '\u7b2c\u4e8c\u5f39', '\u7b2c\u4e09\u5f39', '\u7b2c\u56db\u5f39', '\u7b2c\u4e94\u5f39', '\u7b2c\u516d\u5f39', '\u7b2c\u4e03\u5f39', '\u7b2c\u516b\u5f39', '\u7b2c\u4e5d\u5f39', '\u7b2c\u5341\u5f39']):
                        ep_name = link_text.replace('\u70b9\u51fb\u89c2\u770b\uff1a', '').replace('\u70b9\u51fb\u89c2\u770b', '').strip()
                        if not ep_name: ep_name = f"视频{i}"
                        
                        if not link_href.startswith('http'):
                            link_href = f"{self.host}{link_href}" if link_href.startswith('/') else f"{self.host}/{link_href}"
                        
                        plist.append(f"{ep_name}${link_href}")
            
            play_url = '#'.join(plist) if plist else f"未找到视频源${url}"
            
            vod_content = ''
            try:
                tags = []
                seen_names = set()
                seen_ids = set()
                
                tag_links = data('.tags a, .keywords a, .post-tags a')
                
                candidates = []
                for k in tag_links.items():
                    title = k.text().strip()
                    href = k.attr('href')
                    if title and href:
                        candidates.append({'name': title, 'id': href})
                
                candidates.sort(key=lambda x: len(x['name']), reverse=True)
                
                for item in candidates:
                    name = item['name']
                    id_ = item['id']
                    
                    if id_ in seen_ids: continue
                    
                    is_duplicate = False
                    for seen in seen_names:
                        if name in seen:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        target = json.dumps({'id': id_, 'name': name})
                        tags.append(f'[a=cr:{target}/]{name}[/a]')
                        seen_names.add(name)
                        seen_ids.add(id_)
                
                if tags:
                    vod_content = ' '.join(tags)
                else:
                    vod_content = data('.post-title').text()
            except Exception:
                vod_content = '\u83b7\u53d6\u6807\u7b7e\u5931\u8d25'

            if not vod_content:
                vod_content = data('h1').text() or '\u6bcf\u65e5\u5927\u4e71\u6597'

            return {'list': [{'vod_play_from': '\u6bcf\u65e5\u5927\u4e71\u6597', 'vod_play_url': play_url, 'vod_content': vod_content}]}
        except:
            return {'list': [{'vod_play_from': '\u6bcf\u65e5\u5927\u4e71\u6597', 'vod_play_url': '\u83b7\u53d6\u5931\u8d25'}]}

    def _searchContent(self, key, quick, pg="1"):
        try:
            pg = int(pg) if pg else 1
            
            if pg == 1:
                url = f"{self.host}/search/{key}/"
            else:
                url = f"{self.host}/search/{key}/{pg}/"
            
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            return {'list': self.getlist(self.getpq(response.text)('article')), 'page': pg, 'pagecount': 9999}
        except:
            return {'list': [], 'page': pg, 'pagecount': 9999}

    def playerContent(self, flag, id, vipFlags):
        parse = 0 if self.isVideoFormat(id) else 1
        url = self.proxy(id) if '.m3u8' in id else id
        return {'parse': parse, 'url': url, 'header': self.headers}

    def localProxy(self, param):
        try:
            type_ = param.get('type')
            url = param.get('url')
            if type_ == 'cache':
                key = param.get('key')
                if content := img_cache.get(key):
                    return [200, 'image/jpeg', content]
                return [404, 'text/plain', b'Expired']
            elif type_ == 'img':
                real_url = self.d64(url) if not url.startswith('http') else url
                # \u5171\u4eab\u52a0\u901f\u901a\u9053\uff1aSession \u8fde\u63a5\u590d\u7528 + \u89e3\u5bc6 LRU \u7f13\u5b58\uff082026-09-08 \u5217\u8868\u63d0\u901f\uff09
                if _shared_fetch_img is not None:
                    mime, data = _shared_fetch_img(real_url, headers=self.headers,
                                                   decrypt=self.aesimg, timeout=15,
                                                   proxies=self.proxies or None)
                    if data:
                        return [200, mime, data]
                    return [404, 'text/plain', b'']
                res = requests.get(real_url, headers=self.headers, proxies=self.proxies, timeout=10)
                content = self.aesimg(res.content)
                return [200, 'image/jpeg', content]
            elif type_ == 'm3u8':
                return self.m3Proxy(url)
            else:
                return self.tsProxy(url)
        except:
            return [404, 'text/plain', b'']

    def proxy(self, data, type='m3u8'):
        if data and self.proxies: return f"{self.getProxyUrl()}&url={self.e64(data)}&type={type}"
        return data

    def m3Proxy(self, url):
        url = self.d64(url)
        res = requests.get(url, headers=self.headers, proxies=self.proxies)
        data = res.text
        base = res.url.rsplit('/', 1)[0]
        lines = []
        for line in data.split('\n'):
            if '#EXT' not in line and line.strip():
                if not line.startswith('http'):
                    line = f"{base}/{line}"
                lines.append(self.proxy(line, 'ts'))
            else:
                lines.append(line)
        return [200, "application/vnd.apple.mpegurl", '\n'.join(lines)]

    def tsProxy(self, url):
        return [200, 'video/mp2t', requests.get(self.d64(url), headers=self.headers, proxies=self.proxies).content]

    def e64(self, text):
        return b64encode(str(text).encode()).decode()

    def d64(self, text):
        return b64decode(str(text).encode()).decode()

    def aesimg(self, data):
        if len(data) < 16: return data
        keys = [(b'f5d965df75336270', b'97b60394abc2fbe1'), (b'75336270f5d965df', b'abc2fbe197b60394')]
        for k, v in keys:
            try:
                dec = unpad(AES.new(k, AES.MODE_CBC, v).decrypt(data), 16)
                if dec.startswith(b'\xff\xd8') or dec.startswith(b'\x89PNG'): return dec
            except: pass
            try:
                dec = unpad(AES.new(k, AES.MODE_ECB).decrypt(data), 16)
                if dec.startswith(b'\xff\xd8'): return dec
            except: pass
        return data

    def getlist(self, data, tid=''):
        videos = []
        is_folder = '/mrdg' in (tid or '')
        for k in data.items():
            card_html = k.outer_html() if hasattr(k, 'outer_html') else str(k)
            a = k if k.is_('a') else k('a').eq(0)
            href = a.attr('href')
            title = k('h2').text() or k('.entry-title').text() or k('.post-title').text()
            if not title and k.is_('a'): title = k.text()
            
            if href and title:
                img = self.getimg(k('script').text(), k, card_html)
                videos.append({
                    'vod_id': f"{href}{'@folder' if is_folder else ''}",
                    'vod_name': title.strip(),
                    'vod_pic': img,
                    'vod_remarks': k('time').text() or '',
                    'vod_tag': 'folder' if is_folder else '',
                    'style': {"type": "rect", "ratio": 1.33}
                })
        return videos

    def getfod(self, id):
        url = f"{self.host}{id}"
        data = self.getpq(requests.get(url, headers=self.headers, proxies=self.proxies).text)
        videos = []
        for i, h2 in enumerate(data('.post-content h2').items()):
            p_txt = data('.post-content p').eq(i * 2)
            p_img = data('.post-content p').eq(i * 2 + 1)
            p_html = p_img.outer_html() if hasattr(p_img, 'outer_html') else str(p_img)
            videos.append({
                'vod_id': p_txt('a').attr('href'),
                'vod_name': p_txt.text().strip(),
                'vod_pic': self.getimg('', p_img, p_html),
                'vod_remarks': h2.text().strip()
            })
        return videos

    def getimg(self, text, elem=None, html_content=None):
        if m := re.search(r"loadBannerDirect\('([^']+)'", text or ''):
            return self._proc_url(m.group(1))
        
        if html_content is None and elem is not None:
             html_content = elem.outer_html() if hasattr(elem, 'outer_html') else str(elem)
        if not html_content: return ''

        html_content = html_content.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')

        if 'data:image' in html_content:
            m = re.search(r'(data:image/[a-zA-Z0-9+/=;,]+)', html_content)
            if m: return self._proc_url(m.group(1))

        m = re.search(r'(https?://[^"\'\s)]+\.(?:jpg|png|jpeg|webp))', html_content, re.I)
        if m: return self._proc_url(m.group(1))
            
        if 'url(' in html_content:
            m = re.search(r'url\s*\(\s*[\'"]?([^"\'\)]+)[\'"]?\s*\)', html_content, re.I)
            if m: return self._proc_url(m.group(1))
            
        return ''

    def _proc_url(self, url):
        if not url: return ''
        url = url.strip('\'" ')
        if url.startswith('data:'):
            try:
                _, b64_str = url.split(',', 1)
                raw = b64decode(b64_str)
                if not (raw.startswith(b'\xff\xd8') or raw.startswith(b'\x89PNG') or raw.startswith(b'GIF8')):
                    raw = self.aesimg(raw)
                key = hashlib.md5(raw).hexdigest()
                img_cache[key] = raw
                return f"{self.getProxyUrl()}&type=cache&key={key}"
            except: return ""
        if not url.startswith('http'):
            url = f"{self.host}{url}" if url.startswith('/') else f"{self.host}/{url}"
        return f"{self.getProxyUrl()}&url={self.e64(url)}&type=img"

    def getpq(self, data):
        try: return pq(data)
        except: return pq(data.encode('utf-8'))
