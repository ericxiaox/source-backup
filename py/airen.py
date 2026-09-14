# -*- coding: utf-8 -*-
import requests
import re
import sys
import base64
import json
import urllib.parse
from base.spider import Spider
from urllib.parse import urljoin

sys.path.append('..')
from base.spider import Spider
from urllib.parse import urljoin

try:
    from hostresolver import ext_of
except Exception:
    # hostresolver.py \u5728\u5305\u6839\uff08py/ \u7684\u4e0a\u7ea7\uff09\u3002App \u7aef\uff08gitee \u52a0\u8f7d\uff09\u5b83\u4e0d\u5728\u73b0\u573a\uff0c
    # \u5bfc\u5165\u5fc5\u987b\u53ef\u964d\u7ea7\u4e3a None \u2192 \u8fd0\u884c\u65f6\u8d70 self._resolve_inline \u5185\u8054\u515c\u5e95\u3002\u6a21\u5757\u7ea7\u7981\u88f8\u5bfc\u5165\u3002
    try:
        import os as _os
        sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        from hostresolver import ext_of
    except Exception:
        ext_of = None
class Spider(Spider):
    # \u6c60 mdcmai*.xyz \u4e0e madouai.xyz \u8fd4\u540c\u4e00\u9875\u9762\u2014\u2014**Vue SPA \u5916\u58f3**\uff08<div id="app"> +
    # /assets/index-*.js\uff0c\u9875\u9762\u672c\u8eab 2970B \u65e0\u5185\u5bb9\uff0c\u5224\u6d3b\u770b\u540e\u7aef /api/v1/*\uff09\u3002
    # 2026-09-14 \u5b9e\u6d4b 6 \u57df\u5168\u90e8 200 code=200 cats=28 \u2192 \u6c60\u5e76\u672a\u5931\u6548\uff08\u66fe\u8bef\u5224\u300c\u6c60\u5df2\u5e9f\u300d\uff09\u3002
    # madouai.xyz \uff1d SPA \u81ea\u8eab `canonical` \u58f0\u660e\u7684\u5b98\u65b9\u4e3b\u57df\uff0c\u8865\u8fdb\u5019\u9009\u3002
    CANDIDATE_DOMAINS = [
        "https://mdcmai4.xyz",
        "https://mdcmai5.xyz",
        "https://mdcmai3.xyz",
        "https://mdcmai2.xyz",
        "https://madouai.xyz",
    ]
    decode_mode = 0

    # \u7f51\u7ad9 menu \u7ed3\u6784 (menuId -> \u83dc\u5355\u540d)
    MENU_NAMES = {
        1: base64.b64decode('6bq76LGG5Y6f5Yib').decode('utf-8'),
        2: base64.b64decode('5Zu95LqnQVY=').decode('utf-8'),
        3: base64.b64decode('5bKb5Zu9QVY=').decode('utf-8'),
        4: "\u9ed1\u6599\u5403\u74dc",
    }

    def __init__(self):
        super().__init__()
        self._xurl = None
        self._headers = None
        self._cache_cats = None  # \u7f13\u5b58\u5206\u7c7b\u5217\u8868

    def getName(self):
        return base64.b64decode('6bq76LGG5Lyg5aqSQUk=').decode('utf-8')

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

    def init(self, extend=""):
        # ext \u652f\u6301\uff1ahost@ \u9501\u5b9a / hosts@ \u8ffd\u52a0\u5019\u9009 / publish@ \u9884\u7559\uff08\u7ad9\u65b9\u6682\u65e0\u7a33\u5b9a\u53d1\u5e03\u9875\uff09
        self._ext = ext_of(extend) if ext_of else {}
        self._detect_domain()

    def _detect_domain(self):
        """\u5019\u9009\u57df\u5e76\u884c\u5b9e\u6d4b\uff08hostresolver \u7f3a\u5931\u65f6\u4ecd\u53ef\u7528\uff09\uff1aext host \u9501\u5b9a > ext hosts > \u5185\u7f6e\u5019\u9009\u3002
        \u539f\u4e32\u884c 3s\u00d7N \u6539\u4e3a\u5e76\u884c\uff0c\u907f\u514d App \u7aef\u7a7a\u8f6c\u3002\u7b2c\u4e00\u4e2a\u6210\u529f\u5373\u91c7\u7528\u3002"""
        import threading
        ext = getattr(self, '_ext', {}) or {}
        hosts = []
        if ext.get('host'):
            hosts.append(ext['host'].rstrip('/'))
        hosts += [h.rstrip('/') for h in (ext.get('hosts') or [])]
        hosts += [d.rstrip('/') for d in self.CANDIDATE_DOMAINS]
        result = [None]
        UAMOB = 'Mozilla/5.0 (Linux; Android 13; M2102J2SC Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.31 Mobile Safari/537.36'

        def _try(d):
            if result[0]:
                return
            try:
                h = {'User-Agent': UAMOB, 'Referer': d}
                r = requests.get(f"{d}/api/v1/categories", headers=h, timeout=3)
                if r.status_code == 200:
                    data = r.json()
                    if data.get('code') == 200 and not result[0]:
                        result[0] = (d, h)
            except Exception:
                pass
        threads = [threading.Thread(target=_try, args=(d,)) for d in hosts]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=4)
        if result[0]:
            self._xurl, self._headers = result[0]
        else:
            self._xurl = self.CANDIDATE_DOMAINS[0]
            self._headers = {'User-Agent': UAMOB, 'Referer': self._xurl}

    def _domain(self):
        if self._xurl is None:
            self._detect_domain()
        return self._xurl

    def _req_headers(self):
        if self._headers is None:
            self._detect_domain()
        return self._headers

    def _fetch_api(self, path, params=None):
        url = f"{self._domain()}/api/v1{path}"
        resp = requests.get(url, headers=self._req_headers(), params=params, timeout=15)
        resp.encoding = resp.apparent_encoding or 'utf-8'
        return json.loads(resp.text)

    def _get_categories(self):
        """\u83b7\u53d6\u5e76\u7f13\u5b58\u6240\u6709\u5206\u7c7b"""
        if self._cache_cats is None:
            try:
                data = self._fetch_api('/categories')
                self._cache_cats = data.get('data', [])
            except Exception:
                self._cache_cats = []
        return self._cache_cats

    def _build_image_url(self, cover_url):
        if not cover_url:
            return ''
        if cover_url.startswith('http'):
            return cover_url
        if '/api/v1/image/proxy' in cover_url:
            return urljoin(self._domain(), cover_url)
        if cover_url.startswith('/uploads/'):
            return urljoin(self._domain(), cover_url)
        encoded = urllib.parse.quote(cover_url, safe='')
        return f"{self._domain()}/api/v1/image/proxy?path={encoded}"

    def _build_m3u8_proxy_url(self, video_url):
        if not video_url:
            return ''
        if video_url.startswith('http'):
            parsed = urllib.parse.urlparse(video_url)
            path = parsed.path.lstrip('/')
        else:
            path = video_url.lstrip('/')
        encoded = urllib.parse.quote(path, safe='')
        return f"{self._domain()}/api/v1/m3u8/proxy?path={encoded}"

    def _parse_video_items(self, items):
        videos = []
        for item in items:
            vid = str(item.get('id', ''))
            if not vid:
                continue
            title = item.get('title', '').strip()
            if not title:
                continue
            pic = self._build_image_url(item.get('coverUrl', ''))
            remark = ''
            dur = item.get('durationSec', 0)
            if dur and dur > 0:
                mins = dur // 60
                secs = dur % 60
                remark = f'{mins:02d}:{secs:02d}'
            videos.append({
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": remark
            })
        return videos

    def _parse_short_drama_items(self, items):
        videos = []
        for item in items:
            vid = str(item.get('id', ''))
            if not vid:
                continue
            title = item.get('title', '').strip()
            if not title:
                continue
            pic = self._build_image_url(item.get('coverUrl', ''))
            ep_count = item.get('episodeCount', 0)
            if ep_count:
                remark = f'{ep_count}集'
            else:
                remark = ''
            videos.append({
                "vod_id": f'sd_{vid}',
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": remark
            })
        return videos

    def _parse_post_items(self, items):
        """\u5e16\u5b50/\u9ed1\u6599\u7c7b\u5185\u5bb9"""
        videos = []
        for item in items:
            pid = str(item.get('id', ''))
            if not pid:
                continue
            title = (item.get('title') or item.get('name') or '').strip()
            if not title:
                continue
            pic = self._build_image_url(item.get('coverUrl') or item.get('cover') or '')
            published = item.get('publishedAt', '')
            if published:
                m = re.match(r'(\d{4})-(\d{2})-(\d{2})', published)
                if m:
                    title += f' [{m.group(1)}-{m.group(2)}-{m.group(3)}]'
            videos.append({
                "vod_id": f'post_{pid}',
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": item.get('categoryName', '')
            })
        return videos

    # ============ \u9996\u9875\u5206\u7c7b\uff1a4 \u4e2a\u83dc\u5355 folder + AI\u77ed\u5267 ============
    def homeContent(self, filter):
        class_items = []
        filters = {}

        # 4 \u4e2a\u4e00\u7ea7\u83dc\u5355\uff08\u6309 menuId \u5206\u7ec4\uff09\u4f5c\u4e3a folder
        for mid in [1, 2, 3, 4]:
            name = self.MENU_NAMES.get(mid, f"菜单{mid}")
            class_items.append({
                "type_id": f"menu_{mid}",
                "type_name": name
            })
            # \u6392\u5e8f\u7b5b\u9009\uff08\u83dc\u5355 1/2/3 \u89c6\u9891\u7528\uff09
            if mid in (1, 2, 3):
                filters[f"menu_{mid}"] = [self._video_sort_filter(), self._time_filter(), self._duration_filter()]
            else:
                # \u9ed1\u6599\u5403\u74dc(\u5e16\u5b50)\u53ea\u9700\u65f6\u95f4
                filters[f"menu_{mid}"] = [self._time_filter()]

        # AI\u77ed\u5267\uff08\u72ec\u7acb\u4e00\u7ea7\uff09
        class_items.append({"type_id": "short-dramas", "type_name": "AI\u77ed\u5267"})
        filters["short-dramas"] = [self._time_filter()]

        return {"class": class_items, "filters": filters}

    def _video_sort_filter(self):
        return {
            "key": "sortBy",
            "name": "\u6392\u5e8f",
            "value": [
                {"n": "\u6700\u70ed", "v": "heat"},
                {"n": "\u6700\u65b0", "v": "newest"},
                {"n": "\u6700\u65e9", "v": "oldest"},
                {"n": "\u64ad\u653e\u6700\u591a", "v": "views"},
                {"n": "\u70b9\u8d5e\u6700\u591a", "v": "likes"},
            ]
        }

    def _time_filter(self):
        return {
            "key": "timeRange",
            "name": "\u66f4\u65b0\u65f6\u95f4",
            "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "\u8fd17\u5929", "v": "7d"},
                {"n": "\u8fd11\u6708", "v": "1m"},
                {"n": "\u8fd13\u6708", "v": "3m"},
            ]
        }

    def _duration_filter(self):
        return {
            "key": "minDuration",
            "name": "\u89c6\u9891\u65f6\u957f",
            "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "10\u5206\u949f\u4ee5\u4e0a", "v": "10"},
                {"n": "20\u5206\u949f\u4ee5\u4e0a", "v": "20"},
            ]
        }

    def homeVideoContent(self):
        """\u63a8\u8350\u9875 = \u6bcf\u65e5\u66f4\u65b0 (menuId=1 \u6392\u5e8f)"""
        try:
            data = self._fetch_api('/videos', params={'page': 1, 'size': 20, 'sortBy': 'heat'})
            items = data.get('data', {}).get('items', [])
            return {'list': self._parse_video_items(items)}
        except:
            return {'list': []}

    # ============ \u5206\u7c7b\u5185\u5bb9 ============
    # \u2500\u2500 \u5165\u53e3\u81ea\u6108\uff082026-09-12 \u63a8\u5e7f\uff0c\u7279\u5316\uff1a\u672c\u6e90\u7684 host \u8f7d\u4f53\u662f _xurl\uff09\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    # \u80cc\u666f\uff1a_detect_domain \u53ea\u5728 init \u8dd1\u4e00\u6b21\uff0c\u5168\u8d25\u5373\u9501\u9759\u6001\u9996\u57df \u2192 \u771f\u673a\u300c\u6709\u5206\u7c7b\u65e0\u89c6\u9891\u300d\u3002
    def _ensure_host(self, force=False):
        if force or not getattr(self, '_xurl', None):
            try:
                self._detect_domain()
            except Exception:
                pass
        return getattr(self, '_xurl', '') or ''

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

    def _categoryContent(self, cid, pg, filter, ext):
        page = int(pg) if pg else 1
        cid = str(cid)

        # \u4e8c\u7ea7\u76ee\u5f55\uff1a\u8fdb\u5165\u83dc\u5355 \u2192 \u5217\u5b50\u5206\u7c7b
        if cid.startswith('menu_'):
            return self._category_menu(cid, page, filter, ext)

        # AI\u77ed\u5267
        if cid == 'short-dramas':
            return self._category_short_dramas(page, ext)

        # \u89c6\u9891\u5206\u7c7b
        if cid.isdigit():
            return self._category_videos(int(cid), page, ext)

        # \u5e16\u5b50\u5206\u7c7b
        if cid.startswith('post_cat_'):
            return self._category_posts(int(cid[9:]), page, ext)

        return {'list': [], 'page': page, 'pagecount': 1, 'limit': 20, 'total': 0}

    def _category_menu(self, cid, page, filter, ext):
        """\u8fdb\u5165\u83dc\u5355\uff0c\u5217\u51fa\u5b50\u5206\u7c7b\u4f5c\u4e3a folder \u9879"""
        menu_id = int(cid.split('_')[1])
        all_cats = self._get_categories()
        sub_cats = [c for c in all_cats
                    if c.get('menuId') == menu_id
                    and c.get('enabled')
                    and c.get('type') in ('video', 'post', 'shortdrama')]
        sub_cats.sort(key=lambda x: x.get('sortOrder', 0))

        videos = []
        for c in sub_cats:
            c_id = c.get('id')
            c_type = c.get('type', 'video')
            # video/post \u7528\u5206\u7c7b ID\uff0c\u77ed\u5267\u7528 short-dramas
            if c_type == 'post':
                vod_id = f'post_cat_{c_id}'
            elif c_type == 'video':
                vod_id = str(c_id)
            else:
                continue
            videos.append({
                "vod_id": vod_id,
                "vod_name": c.get('name', ''),
                "vod_pic": '',
                "vod_remarks": '',
                "vod_tag": "folder"
            })
        return {'list': videos, 'page': 1, 'pagecount': 1, 'limit': 100, 'total': len(videos)}

    def _category_short_dramas(self, page, ext):
        size = 12
        params = {'productId': 1, 'sortBy': 'heat', 'page': page, 'size': size}
        if isinstance(ext, dict):
            tr = ext.get('timeRange', '')
            if tr:
                params['timeRange'] = tr
        try:
            data = self._fetch_api('/short-dramas', params=params)
            d = data.get('data', {})
            items = d.get('items', [])
            total = d.get('total', 0)
            pagecount = d.get('totalPages', (total + size - 1) // size if total > 0 else 1)
            return {
                'list': self._parse_short_drama_items(items),
                'page': page, 'pagecount': pagecount, 'limit': size, 'total': total
            }
        except:
            return {'list': [], 'page': page, 'pagecount': 1, 'limit': size, 'total': 0}

    def _category_videos(self, cat_id, page, ext):
        size = 20
        params = {'page': page, 'size': size, 'categoryId': cat_id}
        if isinstance(ext, dict):
            for k, param in [('sortBy', 'sortBy'), ('timeRange', 'timeRange'), ('minDuration', 'minDuration')]:
                v = ext.get(k, '')
                if v:
                    params[param] = v
        try:
            data = self._fetch_api('/videos', params=params)
            d = data.get('data', {})
            items = d.get('items', [])
            total = d.get('total', 0)
            pagecount = (total + size - 1) // size if total > 0 else 1
            return {
                'list': self._parse_video_items(items),
                'page': page, 'pagecount': pagecount, 'limit': size, 'total': total
            }
        except:
            return {'list': [], 'page': page, 'pagecount': 1, 'limit': size, 'total': 0}

    def _category_posts(self, cat_id, page, ext):
        size = 20
        params = {'page': page, 'size': size, 'categoryId': cat_id}
        if isinstance(ext, dict):
            tr = ext.get('timeRange', '')
            if tr:
                params['timeRange'] = tr
        try:
            data = self._fetch_api('/posts', params=params)
            d = data.get('data', {})
            items = d.get('items', [])
            total = d.get('total', 0)
            pagecount = (total + size - 1) // size if total > 0 else 1
            return {
                'list': self._parse_post_items(items),
                'page': page, 'pagecount': pagecount, 'limit': size, 'total': total
            }
        except:
            return {'list': [], 'page': page, 'pagecount': 1, 'limit': size, 'total': 0}

    # ============ \u8be6\u60c5 ============
    def detailContent(self, ids):
        vid = ids[0]
        if vid.startswith('sd_'):
            return self._detail_short_drama(vid)
        if vid.startswith('post_'):
            return self._detail_post(vid)
        try:
            data = self._fetch_api(f'/videos/{vid}')
            item = data.get('data', {})
        except:
            return {'list': []}

        vod = {}
        vod["vod_id"] = vid
        vod["vod_name"] = item.get('title', '')
        vod["vod_pic"] = self._build_image_url(item.get('coverUrl', ''))
        published = item.get('publishedAt', '')
        if published:
            ym = re.match(r'(\d{4})', published)
            if ym:
                vod["vod_year"] = ym.group(1)
        vod["type_name"] = item.get('categoryName', '')
        author = item.get('authorName', '')
        if author:
            vod["vod_actor"] = author
        desc = item.get('description', '')
        if desc:
            vod["vod_content"] = desc
        dur = item.get('durationSec', 0)
        if dur and dur > 0:
            mins = dur // 60
            secs = dur % 60
            vod["vod_remarks"] = f'{mins:02d}:{secs:02d}'
        video_url = item.get('videoUrl', '')
        if video_url:
            m3u8_url = self._build_m3u8_proxy_url(video_url)
            if m3u8_url:
                vod["vod_play_from"] = base64.b64decode('6bq76LGG').decode('utf-8')
                vod["vod_play_url"] = f'正片${m3u8_url}'
        return {'list': [vod]}

    def _detail_short_drama(self, vid):
        sd_id = vid[3:]
        try:
            data = self._fetch_api(f'/short-dramas/{sd_id}', params={'productId': 1})
            item = data.get('data', {})
        except:
            return {'list': []}
        vod = {}
        vod["vod_id"] = vid
        vod["vod_name"] = item.get('title', '')
        vod["vod_pic"] = self._build_image_url(item.get('coverUrl', ''))
        published = item.get('publishedAt', '')
        if published:
            ym = re.match(r'(\d{4})', published)
            if ym:
                vod["vod_year"] = ym.group(1)
        vod["type_name"] = 'AI\u77ed\u5267'
        desc = item.get('description', '')
        if desc:
            vod["vod_content"] = desc
        ep_count = item.get('episodeCount', 0)
        if ep_count:
            vod["vod_remarks"] = f'{ep_count}集'
        episodes = item.get('episodes', [])
        play_list = []
        for ep in episodes:
            ep_title = ep.get('titleOverride') or ep.get('title') or f"第{ep.get('episodeNo', '')}集"
            ep_url = self._build_m3u8_proxy_url(ep.get('videoUrl', ''))
            if ep_url:
                play_list.append(f'{ep_title}${ep_url}')
        if play_list:
            vod["vod_play_from"] = base64.b64decode('6bq76LGG').decode('utf-8')
            vod["vod_play_url"] = '#'.join(play_list)
        return {'list': [vod]}

    def _detail_post(self, vid):
        post_id = vid[5:]
        try:
            data = self._fetch_api(f'/posts/{post_id}')
            item = data.get('data', {})
        except:
            return {'list': []}
        vod = {}
        vod["vod_id"] = vid
        vod["vod_name"] = item.get('title', '')
        vod["vod_pic"] = self._build_image_url(item.get('coverUrl') or item.get('cover') or '')
        published = item.get('publishedAt', '')
        if published:
            ym = re.match(r'(\d{4})', published)
            if ym:
                vod["vod_year"] = ym.group(1)
        vod["type_name"] = item.get('categoryName', '\u9ed1\u6599\u5403\u74dc')
        # \u63cf\u8ff0
        desc = item.get('content') or item.get('description') or ''
        if desc:
            vod["vod_content"] = str(desc)[:1000]
        # \u89c6\u9891\uff08\u9876\u5c42 videoUrl \u5b57\u6bb5\uff09
        video_url = item.get('videoUrl', '')
        if video_url:
            m3u8_url = self._build_m3u8_proxy_url(video_url)
            if m3u8_url:
                vod["vod_play_from"] = base64.b64decode('6bq76LGG').decode('utf-8')
                vod["vod_play_url"] = f'正片${m3u8_url}'
        # \u56fe\u7247\u5217\u8868\u62fc\u5230\u5185\u5bb9\uff08\u9ed1\u6599\u591a\u56fe\u6587\uff09
        images = item.get('images') or []
        img_urls = []
        for img in images:
            if isinstance(img, dict):
                url = img.get('url') or img.get('path') or img.get('imageUrl')
            else:
                url = img
            if url:
                img_urls.append(self._build_image_url(url))
        if img_urls:
            vod["vod_content"] = (vod.get("vod_content", "") + '\n\n' + '\n'.join(img_urls))
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags):
        try:
            if id.startswith('http') and '/m3u8/proxy' in id:
                return {"parse": 0, "playUrl": "", "url": id, "header": json.dumps(self._req_headers())}
            if not id.startswith('http'):
                proxy_url = self._build_m3u8_proxy_url(id)
                if proxy_url:
                    return {"parse": 0, "playUrl": "", "url": proxy_url, "header": json.dumps(self._req_headers())}
            play_url = id if id.startswith(('http://', 'https://')) else urljoin(self._domain(), id)
            return {"parse": 1, "playUrl": "", "url": play_url, "header": json.dumps(self._req_headers())}
        except Exception as e:
            print(f"player error: {e}")
            return {"parse": 1, "playUrl": "", "url": id, "header": json.dumps(self._req_headers())}

    def _searchContent(self, key, quick, page='1'):
        page = int(page) if page else 1
        size = 20
        params = {'page': page, 'size': size, 'keyword': key}
        try:
            data = self._fetch_api('/videos', params=params)
            d = data.get('data', {})
            items = d.get('items', [])
            total = d.get('total', 0)
            pagecount = (total + size - 1) // size if total > 0 else 1
            return {
                'list': self._parse_video_items(items),
                'page': page, 'pagecount': pagecount, 'limit': size, 'total': total
            }
        except:
            return {'list': [], 'page': page, 'pagecount': 1, 'limit': size, 'total': 0}
