# -*- coding: utf-8 -*-
# JPTT \u7ad9\u6e90\uff08\u7981\u7247\u5929\u5802 \u00b7 Laravel \u98ce\u683c + Cloudflare\uff0c2026-09-08 \u73b0\u5f79\u955c\u50cf\u91cd\u5199\u7248\uff09
# \u57df\u540d: jptt.tv 301 -> 2026ajptttv.work\uff08.work \u53cc\u955c\u50cf\uff09\uff1b\u4ee5 jptt.tv \u4e3a\u53d1\u5e03\u94fe
# \u7ed3\u6784: \u5206\u7c7b /tag_list?tid={id}&idx={pg}\uff1b\u641c\u7d22 /search?kw={kw}
#       \u5217\u8868\u6761\u76ee oneVideo \u5361\u7247\uff08\u6807\u9898 h3|h5|img@alt \u4e09\u7ea7\u515c\u5e95\uff0c\u94fe\u63a5 /video/{slug}\uff09
#       \u64ad\u653e <source data-src="//cdn-*.jptt1.cc/hlsredirect/...m3u8">\uff08\u7b7e\u540d\u77ed\u6548\uff09
# \u7eaa\u5f8b: 2026-09-08 App \u7aef\u96f6\u6570\u636e\u6839\u56e0=\u5168\u5e93\u552f\u4e00\u7528 self.fetch() \u7684\u6e90\uff08App base \u7c7b\u8fd4\u56de
#       \u7c7b\u578b\u4e0e rsp.text \u9884\u671f\u4e0d\u7b26\u2192\u5404\u65b9\u6cd5 except \u541e\u9519\u8fd4\u7a7a\uff09\uff0c\u6539 requests \u76f4\u8fde\u4e0e\u5168\u5e93\u5bf9\u9f50
import sys
import re
import json
import requests
from lxml import etree
from base64 import b64decode
from urllib.parse import quote

sys.path.append('..')
from base.spider import Spider

try:
    from hostresolver import resolve_host, parse_ext
except Exception:
    # hostresolver.py \u5728\u5305\u6839\uff08py/ \u7684\u4e0a\u7ea7\uff09\u3002App \u7aef\uff08gitee \u52a0\u8f7d\uff09\u5b83\u4e0d\u5728\u73b0\u573a\uff0c
    # \u5bfc\u5165\u5fc5\u987b\u53ef\u964d\u7ea7\u4e3a None \u2192 \u8fd0\u884c\u65f6\u8d70 self._resolve_inline \u5185\u8054\u515c\u5e95\u3002\u6a21\u5757\u7ea7\u7981\u88f8\u5bfc\u5165\u3002
    try:
        import os as _os
        sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext
    except Exception:
        resolve_host = None
        parse_ext = None
_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'


class Spider(Spider):
    def getName(self):
        return "\u7981\u7247\u5929\u5802"

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
            'User-Agent': _UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9',
            'Connection': 'keep-alive',
        }
        # \u52a8\u6001\u57df\u540d\u89e3\u6790 v2\uff1a2026-09-08 \u5b9e\u6d4b jptt.tv \u6b63\u5728\u9000\u5f79\uff08302 -> 2026ajptttv.work\uff09\uff0c
        # \u4ee5 jptt.tv \u4e3a\u53d1\u5e03\u94fe\uff08\u8df3\u8f6c\u5373\u73b0\u5f79\uff09\uff0c.work \u53cc\u955c\u50cf\u4e3a\u5185\u7f6e\u5019\u9009\uff1b\u5168\u5931\u8d25\u8fd4\u56de '' \u515c\u7a7a\u3002
        ext = self._ext
        publish = ext.get('publish') or 'https://jptt.tv/'
        builtin_hosts = [
            'https://2026ajptttv.work/',      # 2026-09-08 \u5b9e\u6d4b\u73b0\u5f79\u955c\u50cf(222KB\u5b8c\u6574\u7ad9)
            'https://jptttv2026a.work/',
            'https://jptt.tv/',               # \u65e7\u4e3b\u57df\uff0c302 -> 2026ajptttv.work
        ]
        if ext.get('host'):
            self.host = ext['host'].rstrip('/')
        elif resolve_host:
            self.host = resolve_host(
                publish_page=publish,
                candidate_hosts=list(ext.get('hosts') or []) + builtin_hosts,
                headers=self.headers,
                proxies=self.proxies,
                timeout=8,
            ) or ''
        else:
            # \u26a0\u5fc5\u987b isinstance \u5224\u5b9a\uff1aApp \u58f3\u57fa\u7c7b\u53ef\u80fd\u7528 __getattr__ \u7ed9**\u4efb\u610f**\u7f3a\u5931\u5c5e\u6027\u8fd4\u56de
            # \u53ef\u8c03\u7528\u5bf9\u8c61 \u2192 `getattr(self,'host','')` \u62ff\u5230 bound function\uff08\u771f\u503c\uff01\uff09\u2192 \u8df3\u8fc7
            # \u5185\u8054\u515c\u5e95\u3001self.host \u7559\u6210\u51fd\u6570 \u2192 \u4e0b\u4e00\u884c `self.host + '/'` \u76f4\u63a5 TypeError
            # \uff082026-09-14 \u6a21\u62df App \u7aef\u5b9e\u6d4b\uff1a\u672c\u51fd\u6570 0.01s \u629b 'function' and 'str'\uff09\u3002
            if not isinstance(getattr(self, 'host', ''), str) or not self.host:
                h = self._resolve_inline(publish, builtin_hosts, lambda hh,tt: 'jptt' in (hh or '') or '\u7981\u7247' in (tt or ''))
                if h:
                    self.host = h
        # \u5168\u5931\u8d25\u515c\u5e95\uff1a\u9000\u56de\u9996\u4e2a\u5185\u7f6e\u5019\u9009\uff0c\u907f\u514d init \u56e0 self.host \u672a\u8bbe\u800c\u5d29\u6e83
        # \uff08\u7ad9\u70b9\u771f\u5168\u6b7b\u65f6 homeContent \u8d70\u515c\u5e95\u5206\u7c7b/\u8bca\u65ad\uff0c\u800c\u4e0d\u662f init \u629b AttributeError\uff09
        if not isinstance(getattr(self, 'host', ''), str) or not self.host:
            self.host = builtin_hosts[0].rstrip('/')
        self.headers.update({'Referer': self.host + '/', 'Origin': self.host})

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

    def _get(self, path):
        url = path if path.startswith('http') else self.host + path
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False)

    def homeContent(self, filter):
        cateManual = json.loads(b64decode('eyLkuK3mlociOiAiMjc4IiwgIuW3qOS5syI6ICIxNSIsICLnhp/lpbMiOiAiOTUiLCAi6aiO5LmY5L2NIjogIjc0IiwgIuWPo+S6pCI6ICIzNCIsICLnmaHlpbMiOiAiNzUiLCAi5r2u5ZC5IjogIjMyIiwgIuS8geWKg+eJhyI6ICI4NCIsICLnvo7lsLsiOiAiMTU2IiwgIuaJk+aJi+anjSI6ICI5OCIsICLmiLLliofjgIHpgKPnuozliociOiAiNTgiLCAi5Yi25pyNIjogIjE5IiwgIue+juiFvyI6ICIxNTciLCAi6IiU6a6RIjogIjEyMiIsICLnvo7kubMiOiAiMTY2IiwgIuaQreiolSI6ICIxMiIsICLlpoTmg7Pml48iOiAiMTg0IiwgIuesrOS4gOS6uueoseimlum7niI6ICIxNjciLCAi5aq95aq957O7IjogIjE5MyIsICLkurrlprvjg7vkuLvlqaYiOiAiMjYiLCAi5aSa56iu6IG35qWtIjogIjg0IiwgIue+nui+sSI6ICIxNjMiLCAi5aWz5pWZ5birIjogIjEzMSIsICLmt6voqp4iOiAiMTUxIiwgIuiCieaEnyI6ICIxMzYiLCAi5oSb576O6IeAIjogIjExMSIsICLog4zlvozkvY0iOiAiMTc4IiwgIuiqv+aVmSI6ICIzOTUiLCAi6JmV55S3IjogIjIzIiwgIuitt+WjqyI6ICIyODMiLCAi5L+u6ZW3IjogIjE0NyIsICLpnLLlhafopLIiOiAiMTY5IiwgIue1suilqiI6ICIxMTUiLCAi5oSb5beo5LmzIjogIjIwMCIsICLnnLzpj6EiOiAiMjkwIiwgIui2heS5syI6ICIyMTEiLCAi6aGP6Z2i6aiO5LmYIjogIjI2MyIsICLmg6HkvZzliociOiAiMTQ1IiwgIue+qeavjSI6ICIxNDQiLCAi5rer5LqC44O76YGO5r+A57O7IjogIjYzIiwgIuaEm+e+juiFvyI6ICIxMSIsICLniIbkubMiOiAiNDgzIiwgIuWls+S4iuWPuCI6ICIxMzciLCAi5q2j5aSqIjogIjQxNSIsICLnqb/ooaPlubnnoLIiOiAiMTc5IiwgIue3iui6q+earuihoyI6ICIzMDQiLCAi5a245ZySIjogIjQyMSIsICLnqbrlp5AiOiAiMTMyIiwgIueyiee1suaEn+isneelrSI6ICIxOTAiLCAi6IOM6Z2i6aiO5LmX5L2NIjogIjY0NiIsICLnp5jmm7giOiAiMzYzIiwgIuWls+S4u+aSrSI6ICIxMDYiLCAi5Y+N5ZCR5pCt6KiVIjogIjMwNSIsICLlgaXouqvmlZnnt7QiOiAiMjMzIiwgIumDqOS4i+ODu+WQjOWDmiI6ICIxNTAiLCAi6Iie6LmIIjogIjEzMCIsICLnt4rouqvooaPmv4Dlh7giOiAiMzIxIiwgIjNE5b2x54mHIjogIjUwOCIsICLml6nmtKkiOiAiNDAzIn0=').decode('utf-8'))
        result = {'class': [{'type_name': k, 'type_id': v} for k, v in cateManual.items()]}
        return result

    def homeVideoContent(self):
        return {}

    @staticmethod
    def _parse_cards(root):
        """oneVideo \u5361\u7247\u7edf\u4e00\u89e3\u6790\u3002
        2026-09-08 \u6539\u7248\u540e\u6bcf\u89c6\u9891\u542b 3-4 \u4e2a\u91cd\u590d oneVideo \u5757\uff08\u5b8c\u6574\u5757/\u5934\u5757/\u4f53\u5757/\u788e\u7247\uff09\uff0c
        \u6309\u94fe\u63a5\u53bb\u91cd\u53d6\u5b8c\u6574\u5757\uff1b\u5206\u7c7b\u9875\u6807\u9898 h3\u3001\u641c\u7d22\u9875 h5\u3001img alt \u4e09\u7ea7\u515c\u5e95\u3002"""
        out = []
        seen = set()
        for video in root.xpath('//div[contains(@class,"oneVideo")]'):
            try:
                links = video.xpath('.//a/@href')
                if not links:
                    continue
                link = links[0]
                if '/video/' not in link or link in seen:
                    continue
                seen.add(link)
                name = ''
                for xp in ('.//h3/text()', './/h5/text()'):
                    n = video.xpath(xp)
                    if n:
                        name = n[0].strip()
                        break
                if not name:
                    alts = video.xpath('.//img/@alt')
                    if alts:
                        name = alts[0].strip()
                if not name:
                    continue
                img = ''
                imgs = video.xpath('.//img/@src')
                if imgs and imgs[0].strip():
                    img = imgs[0]
                    if img.startswith('//'):
                        img = 'https:' + img
                    elif not img.startswith('http'):
                        img = 'https://2026ajptttv.work' + img
                desc = ''
                ds = video.xpath('.//p[contains(@class,"p_duration")]/text()')
                if ds:
                    desc = ds[0].strip()
                out.append({
                    'vod_name': name,
                    'vod_pic': img,
                    'vod_remarks': desc,
                    'vod_id': link,
                })
            except Exception as e:
                print(f'[parse card error]: {e}')
                continue
        return out

    def _pick_host(self):
        """\u91cd\u89e3\u6790\uff08init \u540c\u6e90\u903b\u8f91\u62bd\u6210\u65b9\u6cd5\uff0c\u4f9b\u5165\u53e3\u81ea\u6108\u590d\u7528\uff09"""
        ext = getattr(self, '_ext', {}) or {}
        publish = ext.get('publish') or 'https://jptt.tv/'
        builtin_hosts = [
            'https://2026ajptttv.work/',
            'https://jptttv2026a.work/',
            'https://jptt.tv/',
        ]
        if ext.get('host'):
            return ext['host'].rstrip('/')
        if resolve_host:
            try:
                h = resolve_host(publish_page=publish,
                                 candidate_hosts=list(ext.get('hosts') or []) + builtin_hosts,
                                 headers=self.headers, proxies=self.proxies, timeout=8)
                if h:
                    return h.rstrip('/')
            except Exception:
                pass
        try:
            h = self._resolve_inline(publish, builtin_hosts,
                                     lambda hh, tt: 'jptt' in (hh or '') or '\u7981\u7247' in (tt or ''))
            if h:
                return h
        except Exception:
            pass
        return ''

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
        result = {}
        url = f'{self.host}/tag_list?tid={tid}&idx={pg}'
        try:
            rsp = self._get(url)
            root = etree.HTML(rsp.text.encode() if isinstance(rsp.text, str) else rsp.content)
            result['list'] = self._parse_cards(root)
            result['page'] = pg
            result['pagecount'] = 9999
            result['limit'] = 90
            result['total'] = 999999
        except Exception as e:
            print(f'[categoryContent fetch error]: {e}')
            result['list'] = []
            result['page'] = pg
            result['pagecount'] = 0
            result['limit'] = 0
            result['total'] = 0
        return result

    def detailContent(self, array):
        tid = array[0]
        url = tid if tid.startswith('http') else f'{self.host}{tid}'
        try:
            rsp = self._get(url)
            root = etree.HTML(rsp.text.encode() if isinstance(rsp.text, str) else rsp.content)

            title_elements = root.xpath('//h1[@class="h1_title"]/text()')
            title = title_elements[0].strip() if title_elements else "\u672a\u77e5\u6807\u9898"

            pic_elements = root.xpath('//video/@poster')
            pic = pic_elements[0] if pic_elements else ""
            if pic and not pic.startswith('http'):
                pic = 'https:' + pic if pic.startswith('//') else self.host + pic

            desc_elements = root.xpath('//div[contains(@class,"info_original")]//p/text()')
            desc = desc_elements[0].strip() if desc_elements else title

            play_url = self.extractVideoUrl(rsp.text)

            vod = {
                "vod_id": tid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_content": desc,
                "vod_play_from": "\u6ce8\u610f\u8eab\u4f53",
                "vod_play_url": "\u591a\u770b\u5c11\u6253\u5361$" + play_url
            }
            return {'list': [vod]}
        except Exception as e:
            print(f"[detailContent error]: {e}")
            return {'list': []}

    def extractVideoUrl(self, html):
        try:
            # 2026-09-08: <source src= \u6539\u7248\u4e3a data-src=\uff08\u61d2\u52a0\u8f7d\uff09\uff0c\u4e24\u79cd\u90fd\u8ba4
            source_match = re.search(r'<source\s+(?:data-)?src="([^"]+)"', html)
            if source_match:
                video_url = source_match.group(1)
                if video_url.startswith('//'):
                    video_url = 'https:' + video_url
                return video_url

            hls_patterns = [
                r'//cdn-[^"\']+\.m3u8[^"\']*',
                r'https?://[^"\']+\.m3u8[^"\']*',
                r'/hlsredirect/[^"\']+\.m3u8'
            ]
            for pattern in hls_patterns:
                matches = re.findall(pattern, html)
                if matches:
                    for match in matches:
                        if match.startswith('//'):
                            return 'https:' + match
                        elif match.startswith('http'):
                            return match
                        else:
                            return self.host + match

            js_patterns = [
                r'src\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'url\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']'
            ]
            for pattern in js_patterns:
                match = re.search(pattern, html)
                if match:
                    video_url = match.group(1)
                    if video_url.startswith('//'):
                        return 'https:' + video_url
                    elif video_url.startswith('http'):
                        return video_url
                    else:
                        return self.host + video_url

            all_m3u8 = re.findall(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', html)
            if all_m3u8:
                return all_m3u8[0]
        except Exception as e:
            print(f"[extractVideoUrl error]: {e}")

        return ""

    def _searchContent(self, key, quick, pg="1"):
        result = {}
        url = f'{self.host}/search?kw={quote(key)}'
        try:
            rsp = self._get(url)
            root = etree.HTML(rsp.text.encode() if isinstance(rsp.text, str) else rsp.content)
            result['list'] = self._parse_cards(root)
        except Exception as e:
            print(f"[searchContent fetch error]: {e}")
            result['list'] = []
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    def playerContent(self, flag, id, vipFlags):
        result = {'parse': 0, 'playUrl': '', 'url': '',
                  'header': {'User-Agent': _UA, 'Referer': self.host + '/', 'Origin': self.host}}
        try:
            if id.startswith('http') and '.m3u8' in id:
                result["url"] = id
            else:
                url = id if id.startswith('http') else f'{self.host}{id}'
                rsp = self._get(url)
                play_url = self.extractVideoUrl(rsp.text)
                result["url"] = play_url
        except Exception as e:
            print(f"[playerContent error]: {e}")
        return result

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        pass

# >>> INLINE-GEN-START >>>
# -*- coding: utf-8 -*-
# \u672c\u533a\u81ea\u52a8\u751f\u6210\uff0c\u8bf7\u52ff\u624b\u6539\u3002\u771f\u6e90\uff1dlocal/hostresolver.py\uff1b\u6539\u4e86\u5b83\u8bf7\u91cd\u8dd1\uff1a
#     python tools/gen_inline_resolvers.py --write
# \u5b58\u5728\u7406\u7531\uff1ahostresolver.py \u4e0d\u662f\u4efb\u4f55\u7ad9\u7684 api\uff0cApp\uff08gitee \u5f62\u6001\uff09\u4e0d\u4f1a\u4e0b\u8f7d\u5b83
# \u2192 \u771f\u673a\u4e0a\u6e90\u5185\u5fc5\u987b\u81ea\u5e26\u6574\u5957\u53d6\u57df\u7b97\u6cd5\uff0c\u5426\u5219\u53ea\u80fd\u5403 v2.6 \u65f6\u4ee3\u7684\u624b\u6284\u7f29\u6c34\u7248\u3002
# FINGERPRINT: cca5f23da886\uff08\u672c\u5757\u5185\u5bb9\u6458\u8981\uff1b\u4e0e\u672c\u4f53\u91cd\u7b97\u4e0d\u7b26\uff1d\u5df2\u8fc7\u671f\uff09
import re
import time
import random
import base64
from urllib.parse import urljoin
try:
    import requests
except Exception:
    requests = None
try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
except Exception:
    ThreadPoolExecutor = None
    as_completed = None

try:
    import requests
except Exception:
    requests = None


try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
except Exception:
    ThreadPoolExecutor = None
    as_completed = None


# ---------------------------------------------------------------- \u7f13\u5b58
_gen_CACHE = {}

_gen_CACHE_TTL = 1800  # \u6210\u529f\u9009\u7ad9\u7f13\u5b58 30 \u5206\u949f


# \u9009\u7ad9\u8fc7\u7a0b\u8bb0\u5f55\uff08\u4f9b\u6e90\u5185\u300c\u8bca\u65ad\u300d\u680f\u76ee\u5c55\u793a\uff0cApp \u7aef\u65e0\u9700\u65e5\u5fd7\u5de5\u5177\u5373\u53ef\u770b\u5230\u5168\u94fe\u8def\uff09
_gen_TRACE = []



def _gen_tr(msg):
    """\u8ffd\u52a0\u4e00\u884c\u9009\u7ad9\u8fc7\u7a0b\u8bb0\u5f55\uff08\u4e0a\u9650 60 \u884c\uff0c\u9632\u9875\u9762\u4e0a\u5237\u5c4f\uff09"""
    try:
        if len(_gen_TRACE) < 60:
            _gen_TRACE.append(str(msg))
    except Exception:
        pass



def _gen_last_trace():
    """\u8fd4\u56de\u4e0a\u4e00\u6b21\u9009\u7ad9\u7684\u9010\u884c\u8bb0\u5f55\uff08\u526f\u672c\uff09"""
    return list(_gen_TRACE)



def _gen_clear_cache():
    """\u6e05\u7a7a\u9009\u7ad9\u7f13\u5b58\uff08\u8c03\u8bd5\u7528\uff1b\u8c03\u7528\u65b9\u4e00\u822c\u4e0d\u9700\u8981\uff09"""
    _gen_CACHE.clear()
    del _gen_TRACE[:]



# ---------------------------------------------------------------- ext \u89e3\u6790
def _gen_parse_ext(ext_str):
    """\u89e3\u6790\u5f71\u89c6.json \u7ad9\u70b9\u6761\u76ee\u7684 ext \u5b57\u6bb5\uff08\u6587\u672c\u683c\u5f0f\uff0c\u5206\u53f7\u5206\u9694 @ \u952e\u503c\uff09\u3002
    \u65e0\u6cd5\u8bc6\u522b\u7684\u7247\u6bb5\u81ea\u52a8\u5ffd\u7565\uff1b\u89e3\u6790\u5931\u8d25\u8fd4\u56de {}\uff08py \u56de\u9000\u5185\u7f6e\u9ed8\u8ba4\u503c\uff0c\u4e0d\u4f1a\u5d29\u6e90\uff09\u3002"""
    out = {}
    for part in str(ext_str or '').split(';'):
        part = part.strip()
        if not part or '@' not in part:
            continue
        k, _, v = part.partition('@')
        k = k.strip().lower()
        v = v.strip().rstrip('/')
        if not v:
            continue
        if k == 'hosts':
            items = [x.strip().rstrip('/') for x in v.split(',') if x.strip()]
            if items:
                out.setdefault('hosts', []).extend(items)
        elif k == 'publish':
            # \u591a\u53d1\u5e03\u9875\uff082026-09-13 \u7528\u6237\u5b9a\uff1a\u7f51\u5740\u578b + GitHub \u578b\u7b49\u53ef\u5e76\u5b58\uff09\uff1a
            # `publish@a,b` \u9017\u53f7\u5206\u9694\uff1b\u5199\u6210\u4e24\u6761 publish@ \u4e5f\u7d2f\u52a0\uff0c\u4e0d\u4e92\u76f8\u8986\u76d6\u3002
            # \u5bf9\u5916\u4ecd\u662f**\u4e00\u4e2a\u9017\u53f7\u4e32**\u2014\u2014\u5404\u6e90\u7167\u65e7 `ext.get('publish') or ''` \u53d6\u7528\uff0c
            # \u7531 resolve_host \u5185\u90e8\u62c6\u5206\uff0c\u6545\u6240\u6709\u5df2\u4e0a\u7ebf\u6e90\u96f6\u6539\u52a8\u3002
            items = [x.strip().rstrip('/') for x in v.split(',') if x.strip()]
            if items:
                cur = [x for x in (out.get('publish') or '').split(',') if x]
                out['publish'] = ','.join(dict.fromkeys(cur + items))
        elif k == 'mail':
            # \u90ae\u7bb1\u6e20\u9053\uff082026-09-13 \u65b0\u589e\uff09\uff1a`mail@a@x.com,b@y.com`\u3002\u6e90\u4fa7\u4e0d\u6d88\u8d39\uff0c
            # \u4f9b\u7ba1\u7406\u53f0/\u624b\u673a\u7aef\u53ef\u8bfb\u53ef\u590d\u5236\uff08\u5931\u8054\u65f6\u4eba\u5de5\u53d1\u4fe1\u53d6\u65b0\u5740\uff09\u3002
            items = [x.strip() for x in v.split(',') if x.strip()]
            if items:
                out.setdefault('mails', []).extend(items)
        elif k == 'host':
            out[k] = v
    return out



def _gen_ext_of(extend):
    """App \u4f20\u7ed9 Spider.init() \u7684 extend \u7edf\u4e00\u89e3\u6790\u5165\u53e3\u3002
    \u517c\u5bb9 None / dict(JSON) / str(\u6587\u672c\u6216JSON)\u3002\u4efb\u4f55\u5f02\u5e38\u8fd4\u56de {}\uff08\u4e0d\u5d29\u6e90\uff09\u3002"""
    import json as _json
    try:
        if not extend:
            return {}
        if isinstance(extend, dict):
            out = {}
            for k in ('publish', 'host'):
                if extend.get(k):
                    v = extend[k]
                    if k == 'publish' and isinstance(v, (list, tuple)):
                        v = ','.join(str(x).strip() for x in v if str(x).strip())
                    out[k] = str(v).strip()
            if extend.get('hosts'):
                hs = extend['hosts'] if isinstance(extend['hosts'], list) else [extend['hosts']]
                out['hosts'] = [str(h).strip() for h in hs if str(h).strip()]
            ms = extend.get('mails') or extend.get('mail')
            if ms:
                ms = ms if isinstance(ms, list) else [ms]
                out['mails'] = [str(m).strip() for m in ms if str(m).strip()]
            return out
        s = str(extend).strip()
        if not s:
            return {}
        try:
            cfg = _json.loads(s)
            if isinstance(cfg, dict):
                return _gen_ext_of(cfg)
        except Exception:
            pass
        return _gen_parse_ext(s)
    except Exception:
        return {}



# ---------------------------------------------------------------- \u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe
# \u6cdb\u89e3\u6790\u968f\u673a\u8bcd\u6c60\uff08\u4e0e\u7ad9\u65b9\u53d1\u5e03\u9875\u540c\u6e90\u53d6\u5e38\u7528\u82f1\u6587\u8bcd\uff1b\u6cdb\u89e3\u6790 DNS \u4e0b\u4efb\u610f\u8bcd\u5747\u53ef\u89e3\u6790\uff09
_gen_WILD_WORDS = (
    'abandon,ability,able,above,absence,accept,access,achieve,across,action,active,'
    'actual,adapt,address,adjust,admit,adopt,adult,advance,advice,afford,afraid,'
    'after,again,against,agency,agent,agree,ahead,airline,airport,album,alcohol,'
    'alive,allow,almost,alone,already,always,amazing,among,amount,ancient,another,'
    'answer,anxiety,anyone,anyway,apart,appear,apple,apply,approve,area,argue,'
    'around,arrange,arrive,article,artist,aspect,assault,assess,asset,assign,'
    'assist,assume,assure,athlete,attack,attempt,attend,attract,author,average,'
    'avoid,award,aware,baby,balance,ball,band,bank,barely,barrel,barrier,base,'
    'basic,basket,battle,beach,beauty,because,become,before,behind,being,belief,'
    'believe,belong,below,bench,beneath,benefit,beside,best,better,between,beyond,'
    'bible,bike,bill,billion,bind,bird,birth,bite,black,blade,blame,blanket,blind,'
    'block,blood,blow,blue,board,boat,body,bomb,bond,bone,book,boom,boot,border,'
    'born,borrow,boss,both,bottle,bottom,bowl,box,brain,branch,brand,bread,break,'
    'breath,breathe,brick,bridge,brief,bright,bring,broad,broken,brother,brown,'
    'brush,budget,build,bullet,bunch,burden,burn,bury,bus,busy,butter,buyer,'
    'cabin,cable,cake,call,camera,campus,cancer,capable,capital,captain,capture,'
    'carbon,card,career,careful,carrier,carry,case,cash,cast,catch,cause,ceiling,'
    'cell,center,central,century,certain,chain,chair'
).split(',')


# \u300c\u968f\u673a\u8bcd + '.\u6cdb\u89e3\u6790\u57fa\u57df'\u300d\u751f\u6210\u7b97\u6cd5\uff08\u5982 words.random() + '.iljzezhab.cc'\uff09
_gen_WILD_PAT = re.compile(
    r"[\w.]*random\s*\(\s*\)\s*\+\s*['\"]\.([a-z0-9-]+(?:\.[a-z0-9-]+)+)['\"]", re.I)

# \u53d1\u5e03\u9875 b64 \u58f3\uff08document.write(Base64.decode('...')) \u6574\u9875 HTML \u85cf base64\uff09
_gen_B64_SHELL_PAT = re.compile(r"Base64\.decode\(\s*['\"]([A-Za-z0-9+/=]{100,})['\"]")

# v2.3 \u7ebf\u8def\u8868\uff08\u57fa\u57df\u88ab\u85cf\u8fdb\u6a21\u677f\u5b57\u7b26\u4e32 / \u6570\u7ec4\uff0c\u4e0d\u518d\u4ee5 random()+'.\u57fa\u57df' \u5f62\u6001\u51fa\u73b0\uff09
_gen_TICK_PAT = re.compile(r'`([^`]{4,800})`', re.S)

# v2.5 \u7ebf\u8def\u8868\u7b2c\u4e09\u79cd\u5f62\u6001\uff082026-09-14 \u00b7 91\u7206\u6599\u771f\u673a\u5931\u8054\u5b9e\u6d4b\u63ea\u51fa\uff09\uff1a**\u5f15\u53f7\u4e32 + \u6362\u884c**\u2014\u2014
#   var zz_line = "gdubugsu.cc\ncekzqgmk.cc\nd3f9.cloudfront.net";
# \u65e7\u7248\u53ea\u8ba4\u53cd\u5f15\u53f7\u6a21\u677f \u2192 \u6b64\u5f62\u6001\u6574\u7ec4\u62bd 0 \u6761\uff1ab64 \u58f3\u660e\u660e\u89e3\u5f00\u4e86\uff0c\u57fa\u57df\u4ecd\u7136\u770b\u4e0d\u89c1\uff08\u6362\u4e0d\u5230\u57df\uff09\u3002
# \u26a0\u5fc5\u987b**\u951a\u5b9a**\uff08\u57df\u540d+\u6362\u884c+\u57df\u540d\uff09\u800c\u4e0d\u80fd\u7528\u300c\u901a\u7528\u5f15\u53f7\u914d\u5bf9\u300d\u626b\u5168\u9875\uff1a\u5b9e\u6d4b 91\u7206\u6599 \u89e3\u7801\u9875\u6709
#  424 \u4e2a\u5f15\u53f7\u4e32\uff0c\u901a\u7528\u914d\u5bf9\u4f1a\u88ab\u9875\u9996 attr \u8c10\u97f3\u4e32\uff08zh-CN / UTF-8 / X-UA-Compatible\uff09\u6574\u4f53\u9519\u4f4d\uff0c
#  \u771f\u6b63\u7684 zz_line \u4e32\u6c38\u8fdc\u8f6e\u4e0d\u5230 \u2014\u2014 \u8be5\u5199\u6cd5\u5f53\u5929\u5df2\u88ab\u8bc1\u4f2a\u3002
_gen_QUOTED_TABLE_PAT = re.compile(
    r"""['"`]("""
    r"""[a-z0-9][a-z0-9.-]*\.[a-z]{2,15}"""
    r"""(?:(?:\\r\\n|\\n|\r\n|\n)[a-z0-9][a-z0-9.-]*\.[a-z]{2,15})+"""
    r"""(?:\\r\\n|\\n|\r\n|\n)?"""
    r""")['"`]""",
    re.I)

_gen_DOMLINE_PAT = re.compile(r'^[a-z0-9][a-z0-9.-]*\.[a-z]{2,15}$', re.I)

# v2.5 TLD \u767d\u540d\u5355\uff1a\u7ebf\u8def\u8868\u884c\u5c3e\u5fc5\u987b\u843d\u5728**\u771f\u5b9e TLD**\u4e0a\u3002\u65e7\u7248 `[a-z]{2,15}` \u592a\u5bbd\uff0c
# \u4f1a\u628a JS \u5bf9\u8c61\u5c5e\u6027\u4e32\u5f53\u57df\u540d\u62bd\u51fa\uff08\u7389\u7f9e\u56ed \u5b9e\u6d4b\u62bd\u5230 ui.loading.render / ui.router.router /
# ui.close \u2014\u2014 \u5168\u662f JS \u547d\u540d\u7a7a\u95f4\uff0c\u767d\u5360\u63a2\u6d3b\u540d\u989d\u3001\u628a\u771f\u5019\u9009\u6324\u51fa\u53bb\uff09\u3002
_gen_TLD_OK = frozenset((
    'cc com net org cn tv io co me top xyz vip app link click info site online '
    'icu club fun store live shop work sbs cfd dev pro space website press host '
    'art name biz mobi asia wiki news blog ltd group tech cloud world today life '
    'us uk jp kr hk tw sg de fr nl ru in id my th vn ph au ca it es pl se no fi'
).split())

# \u6570\u7ec4\u5143\u7d20**\u5141\u8bb8\u5c3e\u90e8 / **\uff082026-09-13 v2.4\uff09\uff1a\u7ad9\u65b9\u5199\u4f5c urls=['mvbessfgf.cc/','huxrzdjnv.cc/']
# \u2014\u2014\u5c3e\u659c\u6760\u5f88\u5e38\u89c1\uff0c\u65e7\u6b63\u5219\u8981\u6c42\u7eaf\u57df\u540d \u2192 \u6574\u7ec4\u62bd 0 \u6761\uff08\u9ec4\u679c publish.js \u5c31\u662f\u8fd9\u5f62\u6001\uff09\u3002
# **\u7ec4\u5916\u5fc5\u987b\u5bb9\u5c3e\u7a7a\u767d**\uff082026-09-13 \u5b9e\u6d4b\u63ea\u51fa\uff09\uff1a\u771f\u5b9e\u5199\u6cd5\u662f\u591a\u884c\u6570\u7ec4\u3001\u672b\u5143\u7d20\u540e\u8fd8\u6709 `,\n]`\uff0c
# \u65e7\u5f0f `...,?)\]` \u8981\u6c42 `]` \u7d27\u8ddf\u6700\u540e\u4e00\u4e2a\u5143\u7d20 \u2192 \u8de8\u884c\u6570\u7ec4\u5168\u6570\u6f0f\u62bd\uff08\u5355\u884c\u624d\u78b0\u5de7\u80fd\u8fc7\uff09\u3002
_gen_ARR_PAT = re.compile(
    r'\[((?:\s*[\'"][a-z0-9.-]*\.[a-z]{2,15}/?[\'"]\s*,?)+)\s*\]', re.I)

# v2.4 JS \u58f3\u8ddf\u968f\uff1a\u53d1\u5e03\u9875\u628a\u5185\u5bb9\u653e\u8fdb\u5916\u94fe JS\uff08<div id="main"> + <script src="publish.js">\uff09
_gen_JS_SRC_PAT = re.compile(r'<script[^>]+src\s*=\s*["\']([^"\']+)["\']', re.I)

_gen_MAX_JS_PAGES = 3                     # \u6bcf\u4e2a\u53d1\u5e03\u9875\u6700\u591a\u8ddf\u968f\u51e0\u4e2a\u5916\u94fe JS

_gen_MAX_JS_BYTES = 2 * 1024 * 1024       # \u5355\u4e2a JS \u622a\u65ad\u4e0a\u9650\uff08\u9632\u70b8\u5185\u5b58\uff09

# \u53d1\u5e03\u9875\u91cc\u5fc5\u7136\u6df7\u5165\u7684\u7b2c\u4e09\u65b9\u5927\u5e73\u53f0/\u7edf\u8ba1/\u5e7f\u544a\u57df\u2014\u2014\u63a2\u6d4b\u5b83\u4eec\u4f1a\u628a\u5927\u9875\u9762\u8bef\u5224\u6210"\u7ad9\u70b9\u53ef\u7528"
_gen_JUNK_HOST_PAT = re.compile(
    r'(googletagmanager|google-analytics|googleads|gstatic|google\.|gitlab\.|github\.|'
    r'youtube\.|ytimg\.|twitter\.|x\.com|t\.me|telegram\.|addtoany\.|yandex\.|'
    r'browsehappy|schema\.org|w3\.org|qq\.com|apple\.com|bing\.com|baidu\.com|'
    r'magsrv\.|adsrv|ad-provider|chnsrv|stripchat|jsdelivr|unpkg|npmjs|shields\.io|'
    r'699pic|meituan|fontawesome|jquery|bootstrap)', re.I)

# v2.7 \u5c5e\u6027\u85cf\u57df\uff08\u7389\u7f9e\u56ed\u5f62\u6001\uff09\uff1a\u57df\u540d\u62c6\u8fdb HTML \u5c5e\u6027\u3001\u7531 JS \u73b0\u573a\u62fc `${\u968f\u673a\u524d\u7f00}.${base}.${houzui}`\u3002
# \u5fc5\u987b**\u540c\u6807\u7b7e\u5185**\u5339\u914d\uff08`[^>]` \u9650\u5236\uff09\u2014\u2014\u8de8\u6807\u7b7e\u4f1a\u628a\u4e0d\u76f8\u5e72\u7684\u5c5e\u6027\u914d\u6210\u5047\u57df\u3002
_gen_ATTR_BASES_PAT = (
    re.compile(r'data-(?:base|host|domain|sub|prefix)\s*=\s*["\']([A-Za-z0-9][A-Za-z0-9.\-]{1,40})["\']'
               r'[^>]{0,160}?(?:houzui|houzhui|suffix|tld)\s*=\s*["\']([A-Za-z0-9][A-Za-z0-9.\-]{0,20})["\']',
               re.I),
    re.compile(r'(?:houzui|houzhui|suffix|tld)\s*=\s*["\']([A-Za-z0-9][A-Za-z0-9.\-]{0,20})["\']'
               r'[^>]{0,160}?data-(?:base|host|domain|sub|prefix)\s*=\s*["\']([A-Za-z0-9][A-Za-z0-9.\-]{1,40})["\']',
               re.I),
)

# v2.8 \u5360\u4f4d\u7b26\u6620\u5c04\uff08\u5c04\u7a9d\u5f62\u6001\uff09\uff1a\u57df\u540d\u88ab\u88c5\u9970\u7b26\u5f53\u5360\u4f4d\u6253\u6563\uff0c\u8fd0\u884c\u65f6 `.replace` \u624d\u62fc\u56de\u3002
#   var url1 = pre1+'.shewo43\u300a\u51e1\u4eba\u6b4c\u300bcc';
#   var newUrl = "https://"+arr[Num].replace(/\u300a\u51e1\u4eba\u6b4c\u300b/g, '.')+ ...
# \u5360\u4f4d\u7b26\u4e0d\u5199\u6b7b\u5b57\u7b26\u96c6\uff08\u53ef\u80fd\u662f\u300a\u300b/\u203b/\u2606/\u4efb\u610f\u88c5\u9970\u4e32\uff09\uff0c\u53ea\u951a\u5b9a `.replace(/X/g,'Y')` \u8fd9\u4e00\u5f62\u6001\u3002
_gen_PH_MAP_PAT = re.compile(
    r"""\.replace\s*\(\s*/\s*([^/\n]{1,12}?)\s*/\s*[gimsuy]*\s*,\s*['"]([^'"\n]{1,6})['"]\s*\)""")

# v2.8 \u300c\u53d8\u91cf + \u5b57\u9762\u57fa\u57df\u300d\u62fc\u63a5\u7247\u6bb5\uff08\u5c04\u7a9d `var url1 = pre1+'.shewo43.cc';`\uff09\u2014\u2014
#   `_WILD_PAT` \u8981\u6c42 random() \u524d\u7f00\u3001`extract_line_bases` \u8981\u6c42\u7eaf\u57df\u540d\u4e32/\u6570\u7ec4\uff0c
#   \u4e24\u8005\u90fd\u62bd\u4e0d\u5230\u8be5\u5f62\u6001\uff0c\u6545\u987b\u65b0\u62bd\u53d6\u5668\u3002
# \u26a0 **\u5fc5\u987b\u8981\u6c42\u7d27\u8ddf `+` \u62fc\u63a5\u7b26**\uff082026-09-14 \u56de\u5f52\u5b9e\u6d4b\u6559\u8bad\uff09\uff1a\u5360\u4f4d\u7b26\u8fd8\u539f\u4e00\u65e6\u653e\u5bbd\u5230
#   \u300c\u5f15\u53f7\u91cc\u7684\u57df\u540d\u5f62\u6001\u4e32\u300d\uff0c\u666e\u901a\u9875\u9762\u904d\u5730\u90fd\u662f\uff08`+'.'` \u8fd8\u539f\u540e `"www.paypalobjects.com"`\u3001
#   `"//type.googleapis.com"`\uff09\u2014\u2014\u5b9e\u6d4b penzu / car.pvtlbzgj \u4e24\u9875\u56e0\u6b64\u8bef\u62bd
#   paypal / braintree\u00d73 / googleapis \u5171 5 \u4e2a\u5047\u57fa\u57df\uff0c\u6bcf\u4e2a\u8fd8\u4f1a \u00d74 \u8bcd\u751f\u6210\u5b50\u57df\u5019\u9009\uff0c
#   \u628a\u771f\u5019\u9009\u6324\u51fa\u6f14\u6d3b\u540d\u989d\u3002`+` \u65ad\u8a00\u628a\u62bd\u53d6\u9650\u5b9a\u5728\u300c\u771f\u5728\u62fc\u57df\u540d\u300d\u7684\u8bed\u5883\u3002
_gen_FRAG_DOM_PAT = re.compile(
    r"""(?:\+|\.concat\(\s*)['"](\.[a-z0-9][a-z0-9.\-]{1,60}|[a-z0-9][a-z0-9.\-]{1,60})['"]""",
    re.I)

# \u7247\u6bb5\u62bd\u53d6**\u4e13\u7528**\u7684\u7b2c\u4e09\u65b9\u57df\u9ed1\u540d\u5355\uff08\u4e0d\u52a8\u5168\u5c40 _JUNK_HOST_PAT\uff0c\u907f\u514d\u5f71\u54cd\u65e2\u6709\u6e90\u7684\u884c\u4e3a\uff09
_gen_FRAG_JUNK_PAT = re.compile(
    r'(googleapis|google\.|gstatic|googlesyndication|paypal|braintree|stripe|'
    r'cloudflare|akamai|cloudfront|doubleclick|w3\.org|schema\.org|jquery|'
    r'bootstrap|fontawesome|cdnjs|unpkg|jsdelivr)', re.I)

# v2.8 \u76f8\u5bf9\u8def\u5f84\u8df3\u8f6c\uff08\u5c04\u7a9d\u9996\u8df3\u5f62\u6001\uff09\uff1a\u76ee\u6807\u53ea\u6709\u76f8\u5bf9\u8def\u5f84\uff0c\u65e0\u534f\u8bae\u65e0\u4e3b\u673a\u3002
#   var urlList=["\u529b\u4e89\u4e0a\u6e38/index.html","\u594b\u53d1\u56fe\u5f3a/index.html",...]; window.open(urlList[...])
_gen_REL_STR_PAT = re.compile(r"""['"]([^'"\\\s]{1,80})['"]""")

# \u53ea\u5728\u300c\u8df3\u8f6c/\u6253\u5f00\u300d\u8bed\u5883\u91cc\u62bd\u76f8\u5bf9\u8def\u5f84\uff08\u9632\u6b63\u6587/\u8d44\u6e90\u6e05\u5355\u8bef\u62bd\uff09
_gen_REL_CTX_PAT = re.compile(r'window\.open|location\.(?:href|replace|assign)|redirect|onload', re.I)

_gen_REL_MAX_TEXT = 12000                 # \u76f8\u5bf9\u8def\u5f84\u62bd\u53d6\u7684\u9875\u9762\u4f53\u91cf\u4e0a\u9650

# v2.9 \u53d8\u91cf\u62fc\u63a5\uff08\u53d1\u5e03\u9875\u5f62\u6001\uff0c2026-09-14 \u6781\u4e50 `nf198.hscwang7y5m.link/jm6s8/`\uff09\uff1a
#   var sub_str = "bjo-eh1buu5li9"; var tdn_str = "hscwang8s8m1"; var html_go = "https://";
#   html_go += sub_str; html_go += "."; html_go += tdn_str; html_go += "."; html_go += 'cc';
# \u57df\u540d\u88ab\u62c6\u6210\u300c\u72ec\u7acb var \u503c + TLD \u5b57\u9762\u91cf\u300d\uff0c\u9010\u6bb5 `+=` \u624d\u62fc\u56de\u3002\u7247\u6bb5\u65e2\u4e0d\u7d27\u8ddf `+`\uff08`_FRAG_DOM_PAT`
# \u62bd\u4e0d\u5230\uff09\uff0c\u4e5f\u65e0 `.replace` \u5360\u4f4d\u7b26\uff08`_restore_placeholders` \u4e0d\u89e6\u53d1\uff09\u2192 v2.8 \u4e24\u901a\u8def\u5168\u7a7a\u624b\u3002
_gen_JS_VARDEF_PAT = re.compile(
    r"""\b(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*['"]([^'"\n]{0,120})['"]""")

_gen_JS_APPEND_PAT = re.compile(
    r"""\b([A-Za-z_$][\w$]*)\s*\+=\s*(?:['"]([^'"\n]{0,120})['"]|([A-Za-z_$][\w$]*))""")

_gen_JS_CONCAT_MAX_TEXT = 4000            # \u53ea\u5728\u53d1\u5e03\u9875/\u58f3\u9875\u91cf\u7ea7\u542f\u7528\uff08\u6b63\u6587\u5927\u9875\u4e0d\u505a\uff0c\u9632\u8bef\u62bd\uff09



def _gen_host_of(url):
    """\u53d6 URL \u7684 host\uff08\u5c0f\u5199\u3001\u65e0\u7aef\u53e3\u534f\u8bae\uff09\uff0c\u5931\u8d25\u8fd4\u56de ''"""
    m = re.match(r'https?://([^/:?#\s]+)', str(url or ''), re.I)
    return m.group(1).lower() if m else ''



def _gen_is_junk(cand):
    return bool(_gen_JUNK_HOST_PAT.search(_gen_host_of(cand) or cand or ''))



# v2.31\uff1a\u5185\u5bb9\u5f62\u6001**\u6b63\u5411**\u5224\u636e\uff082026-09-11 51\u5403\u74dc\u590d\u76d8\u65b0\u589e\uff09
# \u80cc\u666f\uff1a51\u5403\u74dc \u6709\u4e00\u4e2a 20KB \u7684\u300c\u65b0\u5730\u5740\u516c\u544a\u9875\u300d\uff08401.dzyeamwh.cc\uff09\uff0c\u6b63\u6587\u542b\u7ad9\u540d\u3001\u80fd\u88ab
# \u7ad9\u540d\u6821\u9a8c\u653e\u8fc7\uff0c\u4f46\u6ca1\u6709\u4efb\u4f55\u5185\u5bb9\u7ed3\u6784\u2014\u2014\u9009\u4e2d\u5b83 \u2192 \u5206\u7c7b\u53ea\u6709 3 \u4e2a\u3001\u5217\u8868\u5168\u7a7a\uff0c
# \u6b63\u662f\u300c\u8fde\u5206\u7c7b\u90fd\u5237\u4e0d\u51fa\u6765\u300d\u3002\u6545\u5728\u7ad9\u540d\u6821\u9a8c\u4e4b\u4e0a\u518d\u8981\u6c42\u300c\u50cf\u5185\u5bb9\u7ad9\u300d\u3002
# \u6ce8\uff1av2.3 \u521d\u7248\u8fd8\u5199\u8fc7\u4e00\u4e2a**\u5426\u5b9a\u5f0f**\u5224\u636e _looks_like_nav\uff08\u5916\u94fe\u591a=\u5bfc\u822a\u9875\uff09\uff0c
#     \u540c\u65e5\u5373\u5220\u2014\u2014\u5b83\u5bf9\u7981\u7247\u5929\u5802\uff08oneVideo \u5361\u7247\u3001\u65e0 <article> \u5b57\u9762\u6807\u8bb0\uff09\u8bef\u6740\u3002
#     \u540c\u4e00\u4ef6\u4e8b\u53ea\u7559\u4e00\u4e2a\u6b63\u5411\u5224\u636e\u3002
_gen_CONTENT_MARKS = ('<article', 'post-card', 'video-item', 'oneVideo', 'entry-title',
                  'post-title', 'vod-img', 'vod-txt', 'playlist', 'class="video')

_gen_CONTENT_LINK_PAT = re.compile(
    r'href=["\'][^"\']*/(?:archives?|video|videos|category|categories|post|vod|'
    r'watch|tag|detail|thread|topic|tag_list)[/"\']', re.I)



def _gen_looks_like_content(text):
    """\u50cf\u5185\u5bb9\u7ad9\u5417\uff1a\u6709\u5185\u5bb9\u7ed3\u6784\u6807\u8bb0 / \u6709 \u22655 \u6761\u5185\u5bb9\u578b\u5185\u94fe / \u9875\u9762\u591f\u5927\uff08>80KB\uff09\u3002
    \u5047\u95e8\u7ad9\uff08\u516c\u544a\u9875/\u5bfc\u822a\u9875\uff09\u4e09\u6761\u5168\u4e0d\u6ee1\u8db3\u3002"""
    t = text or ''
    if any(k in t for k in _gen_CONTENT_MARKS):
        return True
    if len(_gen_CONTENT_LINK_PAT.findall(t)) >= 5:
        return True
    return len(t) > 80000



def _gen_b64_try(blob):
    """base64 blob \u2192 \u6587\u672c\uff08\u987b\u542b HTML \u6807\u7b7e\u624d\u7b97\u89e3\u51fa\uff09\uff1b\u5bb9\u9519\u65e0 padding / \u542b\u7a7a\u767d\u3002
    \u5931\u8d25\u8fd4\u56de ''\u3002"""
    try:
        s = re.sub(r'\s+', '', blob or '')
        if len(s) < 100:
            return ''
        s += '=' * (-len(s) % 4)          # v2.6 \u8865 padding\uff1a\u7ad9\u65b9 blob \u5e38\u7701\u5c3e\u90e8 `=`
        d = base64.b64decode(s, validate=False).decode('utf-8', 'ignore')
        return d if ('<' in d and '>' in d) else ''
    except Exception:
        return ''



def _gen_expand_b64_shells(text):
    """\u5c55\u5f00\u53d1\u5e03\u9875\u91cc\u7684 Base64 \u58f3\uff0c\u8fd4\u56de [\u539f\u6587, \u89e3\u7801\u98751, \u89e3\u7801\u98752...]

    v2.6\uff1a\u2460 \u8865 padding \u4fee\u590d\u2014\u2014\u7ad9\u65b9 blob \u5e38\u7701\u5c3e\u90e8 `=`\uff0c\u65e7\u7248\u76f4\u63a5 `b64decode` \u629b\u9519 \u2192
    \u6574\u9875\u58f3\u89e3\u4e0d\u5f00\uff08\u90a3\u4e00\u6b65\u6b63\u662f\u9ed1\u6599\u5bb6\u65cf\u6362\u57df\u94fe\u7684\u7b2c\u4e8c\u8df3\uff09\uff1b\u2461 \u627e\u4e0d\u5230 `Base64.decode('...')`
    \u5b57\u9762\u5f62\u6001\u65f6\uff0c\u9000\u5230\u901a\u7528\u957f blob \u626b\u63cf\uff08\u8986\u76d6 `Base64.decode(x)` \u53d8\u91cf\u5f62\u6001\uff09\u3002"""
    texts = [text]
    blobs = [m.group(1) for m in _gen_B64_SHELL_PAT.finditer(text or '')]
    if not blobs:
        blobs = re.findall(r'[A-Za-z0-9+/=]{400,}', text or '')
    for b in blobs[:3]:
        d = _gen_b64_try(b)
        if d:
            texts.append(d)
    return texts



def _gen_restore_placeholders(text):
    """\u8fd8\u539f\u300c\u5360\u4f4d\u7b26\u6253\u6563\u57df\u540d\u300d\u5199\u6cd5\uff08v2.8\uff0c\u5c04\u7a9d\u5f62\u6001 2026-09-14\uff09\u3002

    \u73b0\u7f51\u5199\u6cd5\uff08shewo1.cc \u4e8c\u7ea7\u58f3\uff09\uff1a\u57df\u540d\u88ab\u88c5\u9970\u7b26\u5f53\u5360\u4f4d\u6253\u6563\uff0c\u8fd0\u884c\u65f6\u624d replace \u62fc\u56de\u2014\u2014
      var url1 = pre1+'.shewo43\u300a\u51e1\u4eba\u6b4c\u300bcc';
      var newUrl = \"https://\"+arr[Num].replace(/\u300a\u51e1\u4eba\u6b4c\u300b/g, '.')+ mulu[...]+'?fby';
    \u76ee\u6807\u57df**\u4e0d\u5728\u4efb\u4f55\u5c5e\u6027\u6216\u5b57\u9762\u91cf\u91cc**\uff08\u524d\u7f00\u8fd8\u662f noncestr(2,2) \u968f\u673a\u91cf\uff09\u2192 \u9759\u6001\u62bd\u94fe
    \uff08_WILD_PAT / extract_line_bases / _attr_bases\uff09\u5168\u90e8\u7a7a\u624b\u3002
    \u672c\u51fd\u6570\u4ece `.replace(/\u5360\u4f4d/g,'\u66ff\u6362')` \u53d6\u6620\u5c04\uff0c\u628a**\u5168\u6587**\u5360\u4f4d\u7b26\u66ff\u6362\u6389 \u2192
    \u5f97\u5230 `pre1+'.shewo43.cc'` \u2192 \u4ea4\u7ed9 `_frag_bases` \u62bd\u57fa\u57df\u3002

    \u8fd4\u56de\u8fd8\u539f\u540e\u7684\u6587\u672c\uff1b\u65e0\u53ef\u8fd8\u539f\u6620\u5c04\u65f6\u8fd4\u56de ''\uff08\u4f9b\u8c03\u7528\u65b9\u5224\u300c\u662f\u5426\u771f\u53d1\u751f\u8fc7\u8fd8\u539f\u300d\uff09\u3002"""
    t = text or ''
    maps = []
    for m in _gen_PH_MAP_PAT.finditer(t):
        ph, rep = m.group(1), m.group(2)
        if len(ph) < 2 or ph == rep or ph not in t or (ph, rep) in maps:
            continue
        maps.append((ph, rep))
    if not maps:
        return ''
    for ph, rep in maps:
        t = t.replace(ph, rep)
    return t if t != (text or '') else ''



def _gen_frag_bases(text):
    """\u4ece\u300c\u8fd8\u539f\u540e\u7684 JS \u62fc\u63a5\u4e32\u300d\u62bd\u57fa\u57df\uff08v2.8\uff0c\u5c04\u7a9d\u5f62\u6001\uff09\u3002

    \u5199\u6cd5\uff1a`var url1 = pre1+'.shewo43.cc';` \u2014\u2014 \u524d\u7f00\u662f**\u53d8\u91cf**\uff08\u8fd0\u884c\u65f6\u968f\u673a\uff09\uff0c
    \u57fa\u57df\u662f\u5b57\u9762\u91cf\u3002`_WILD_PAT` \u8981\u6c42 `random() + '.\u57fa\u57df'`\u3001`extract_line_bases`
    \u8981\u6c42\u7eaf\u57df\u540d\u4e32/\u6570\u7ec4 \u2192 \u4e24\u8005\u90fd\u62bd 0 \u6761\uff1b\u672c\u51fd\u6570\u76f4\u63a5\u626b\u300c\u5f15\u53f7\u5185\u7684\u57df\u540d\u5f62\u6001\u7247\u6bb5\u300d\u3002

    \u26a0 \u53ea\u7531 `_scan_text` \u5728**\u53d1\u751f\u8fc7\u5360\u4f4d\u7b26\u8fd8\u539f**\u65f6\u8c03\u7528\uff1a\u6ee1\u9875\u5f15\u53f7\u4e32\uff08zh-CN /
    index.html / text/html / favicon.ico\uff09\u82e5\u4e0d\u8bbe\u9650\u4f1a\u767d\u5360\u63a2\u6d3b\u540d\u989d\u3002"""
    out = []
    for m in _gen_FRAG_DOM_PAT.finditer(text or ''):
        s = (m.group(1) or '').strip().strip('.').lower()
        if not s or len(s) > 60 or s.count('.') > 3:
            continue
        if not _gen_DOMLINE_PAT.match(s):
            continue
        if s.rsplit('.', 1)[-1] not in _gen_TLD_OK:
            continue
        if _gen_is_junk(s) or _gen_FRAG_JUNK_PAT.search(s):
            continue
        out.append(s)
    return list(dict.fromkeys(out))



def _gen_js_concat_strs(text):
    """\u8fd8\u539f\u300c\u72ec\u7acb var \u503c \uff0b \u8fde\u7eed `+=`\u300d\u62fc\u51fa\u7684\u5b8c\u6574\u4e32\uff08v2.9\uff0c\u53d1\u5e03\u9875\u5f62\u6001 2026-09-14\uff09\u3002

    \u73b0\u7f51\u5199\u6cd5\uff08\u6781\u4e50\u53d1\u5e03\u9875 `nf198.hscwang7y5m.link/jm6s8/`\uff0c2084B\uff09\uff1a
      var sub_str = \"bjo-eh1buu5li9\";
      var tdn_str = \"hscwang8s8m1\";
      var html_go = \"https://\";
      html_go += sub_str; html_go += \".\"; html_go += tdn_str; html_go += \".\"; html_go += 'cc';
      \u2192 https://bjo-eh1buu5li9.hscwang8s8m1.cc/jlhs/

    \u57df\u540d\u88ab\u62c6\u6210**\u72ec\u7acb var \u8d4b\u503c**\uff08\u4e0d\u7d27\u8ddf `+`\uff0c`_FRAG_DOM_PAT` \u62bd\u4e0d\u5230\uff09+ TLD \u5b57\u9762\u91cf\uff0c
    \u9760\u4e00\u4e32 `+=` \u624d\u62fc\u56de\uff1b\u4e5f\u6ca1\u6709 `.replace` \u5360\u4f4d\u7b26\u3002\u2192 v2.8 \u4e24\u6761\u901a\u8def\u5168\u7a7a\u624b\uff0c
    \u8be5\u53d1\u5e03\u9875\u53ea\u80fd\u62bd 0 \u6761\uff08=\u6781\u4e50\u6362\u57df\u540e\u6e90\u65e0\u4ece\u81ea\u6108\uff09\u3002

    \u8fd4\u56de**\u7d2f\u52a0\u8fc7\u7a0b\u4e2d\u6bcf\u4e00\u6b65\u7684\u7ed3\u679c\u4e32**\uff08\u4f9b\u62bd\u57df\u7528\uff1b\u5b8c\u6574\u4e32\u901a\u5e38\u5728\u672b\u6b65\u51fa\u73b0\uff09\u3002
    \u4e09\u91cd\u9650\u6d41\uff1a\u2460 \u6574\u9875 \u2264 `_JS_CONCAT_MAX_TEXT`\uff08\u53d1\u5e03\u9875/\u58f3\u9875\u91cf\u7ea7\uff0c\u6b63\u6587\u5927\u9875\u4e0d\u505a\uff09\uff1b
    \u2461 \u5fc5\u987b\u542b `+=`\uff1b\u2462 \u5355\u6bb5\u4e3a\u7a7a\u5219\u8df3\u8fc7\uff08\u4e0d\u7ed9\u65e0\u5173\u53d8\u91cf\u767d\u8bb0\uff09\u3002
    \u26a0 \u53ea\u505a\u300c\u540c\u4e00\u53d8\u91cf\u81ea\u7d2f\u52a0\u300d\u7684\u6734\u7d20\u8fd8\u539f\uff0c\u4e0d\u505a\u8de8\u53d8\u91cf\u4ee3\u6570\u63a8\u6f14\u2014\u2014**\u5b81\u53ef\u5c11\u62bd\u4e0d\u53ef\u8bef\u62bd**\u3002"""
    t = text or ''
    if not t or len(t) > _gen_JS_CONCAT_MAX_TEXT or '+=' not in t:
        return []
    vals = {}
    for m in _gen_JS_VARDEF_PAT.finditer(t):
        vals[m.group(1)] = m.group(2)
    acc, out = {}, []
    for m in _gen_JS_APPEND_PAT.finditer(t):
        tgt = m.group(1)
        seg = m.group(2) if m.group(2) is not None else vals.get(m.group(3), '')
        if not seg:
            continue
        acc[tgt] = acc.get(tgt, vals.get(tgt, '')) + seg
        out.append(acc[tgt])
    return out



def _gen_rel_paths(text, base_url, max_n=4):
    """\u4ece\u58f3\u9875\u62bd**\u76f8\u5bf9\u8def\u5f84**\u8df3\u8f6c\u76ee\u6807\uff08v2.8\uff0c\u5c04\u7a9d\u9996\u8df3\u5f62\u6001\uff09\u3002

    \u73b0\u7f51\u5199\u6cd5\uff08shewo1.cc \u9996\u8df3 = \u70b9\u51fb\u5f0f\u9009\u62e9\u9875\uff09\uff1a
      <div class=\"enter_button\">\u529b\u4e89\u4e0a\u6e38</div>
      var urlList=[\"\u529b\u4e89\u4e0a\u6e38/index.html\",\"\u594b\u53d1\u56fe\u5f3a/index.html\",\"\u6301\u4e4b\u4ee5\u6052/index.html\"];
      window.open(urlList[Math.floor(...)]+wenhao);
    \u76ee\u6807**\u53ea\u6709\u76f8\u5bf9\u8def\u5f84**\uff08\u65e0\u534f\u8bae\u65e0\u4e3b\u673a\uff09\u2192 `_shell_target` \u7684\u7edd\u5bf9 URL \u5206\u652f\u5168\u7a7a\u624b \u2192 \u6574\u94fe\u65ad\u3002
    \u672c\u51fd\u6570\u5728\u300c\u8df3\u8f6c/\u6253\u5f00\u8bed\u5883\u300d\u4e0b\u626b\u5f15\u53f7\u4e32\uff0c\u53d6\u5f62\u5982 `/a/` \u6216 `a/index.html` \u7684\u76ee\u5f55\u578b\u4e32\uff0c
    \u7528 urljoin \u8865\u6210\u7edd\u5bf9 URL\u3002

    **\u4e09\u91cd\u9650\u6d41\u9632\u8bef\u62bd**\uff1a\u2460 \u9875\u9762 \u2264 _REL_MAX_TEXT\uff1b\u2461 \u5fc5\u987b\u547d\u4e2d _REL_CTX_PAT\uff08window.open /
    location / redirect / onload\uff09\uff1b\u2462 \u5c3e\u6bb5\u5e26\u70b9\u4f46\u4e0d\u662f .html/.htm/.php \u7684\u4e00\u5f8b\u5f53\u8d44\u6e90\u6587\u4ef6\u8df3\u8fc7
    \uff08favicon.ico / indexfby.css / logo.png\uff09\u3002"""
    if not base_url or not text or len(text) > _gen_REL_MAX_TEXT:
        return []
    if not _gen_REL_CTX_PAT.search(text):
        return []
    out = []
    for m in _gen_REL_STR_PAT.finditer(text):
        s = (m.group(1) or '').strip()
        if not s or len(s) > 80 or '://' in s or s.startswith(('//', '#', 'data:')):
            continue
        if not (s.startswith('/') or re.match(r'^[\w\u4e00-\u9fff]+/', s)):
            continue
        tail = s.rstrip('/').rsplit('/', 1)[-1].lower()
        if '.' in tail and not tail.endswith(('.html', '.htm', '.php')):
            continue
        u = urljoin(base_url, s).rstrip('/')
        if re.match(r'^https?://', u) and u not in out and not _gen_is_junk(u):
            out.append(u)
        if len(out) >= max_n:
            break
    return out



def _gen_shell_targets(text, base_url=''):
    """\u4ece\u300c\u8df3\u8f6c\u58f3\u300d\u9875\u62bd\u4e0b\u4e00\u8df3\u5019\u9009 URL **\u5217\u8868**\uff08\u4fdd\u5e8f\uff0c\u22644\uff09\uff1b\u7a7a\u5217\u8868 = \u4e0d\u662f\u8df3\u8f6c\u58f3\u3002

    v2.8 \u8d77\u8fd4\u56de\u5217\u8868\uff08\u65e7 `_shell_target` \u53ea\u8fd4\u5355\u4e2a\uff09\uff1a\u7ad9\u65b9\u5e38\u628a\u58f3\u9875\u5199\u6210**\u591a\u7ebf\u8def\u968f\u673a\u6311\u4e00**
    \uff08\u5c04\u7a9d window.open \u4e09\u76ee\u5f55\uff09\uff0c\u5355\u5019\u9009\u8ddf\u4e0d\u4e0b\u53bb\u5c31\u6574\u94fe\u65ad\u3002

    \u9ed1\u6599\u5bb6\u65cf 2026-09 \u73b0\u7f51\u5f62\u6001\uff08\u6bcf\u65e5\u5927\u8d5b / 51\u5403\u74dc / 51\u6697\u7f51 \u540c\u6b3e\uff0c\u2248300B\uff09\uff1a
      <a id=\"\u968f\u673aID\" href=\"https://\u76ee\u6807\u57df/\" target=\"_self\">\u52a0\u8f7d\u4e2d...</a>
      <script>(function(\u968f\u673a\u53d8\u91cf){...window.location.replace(\u968f\u673a\u53d8\u91cf.href)})
             (document.getElementById(\"\u968f\u673aID\"))</script>
    \u26a0\u8df3\u8f6c\u76ee\u6807\u5728 `<a href>` \u91cc\u3001JS \u53ea\u5f15\u7528\u53d8\u91cf \u2014\u2014 \u65e7 `_js_redirect` \u53ea\u8ba4**\u5b57\u9762\u91cf**
      `location.replace('...')` \u2192 \u8fd9\u7c7b\u9875\u9762\u6574\u9875\u62bd 0 \u6761\u3002

    \u8986\u76d6\u56db\u7c7b\u5f62\u6001\uff08\u6309\u4f18\u5148\u7ea7\uff09\uff1a\u2460 `<a href>` \u52a0\u8f7d\u4e2d/\u8df3\u8f6c\u7c7b\u6587\u6848\uff1b\u2461 \u6781\u5c0f\u9875\u552f\u4e00\u7edd\u5bf9\u5916\u94fe\uff1b
    \u2462 \u5b57\u9762\u91cf JS \u8df3\u8f6c / meta refresh\uff1b\u2463 \u76f8\u5bf9\u8def\u5f84\u76ee\u5f55\uff08v2.8 \u5c04\u7a9d\u5f62\u6001\uff0c\u987b\u4f20 base_url\uff09\u3002"""
    t = text or ''
    if len(t) > 4000:                 # \u5927\u9875\u9762\u4e0d\u662f\u58f3\uff0c\u522b\u8bef\u62bd\u6b63\u6587\u91cc\u7684\u9996\u4e2a\u5916\u94fe
        return []
    out = []
    for _pat in ('<a[^>]+href\\s*=\\s*["\\\'](https?://[^"\\\']+)["\\\'][^>]*>\\s*\u52a0\u8f7d\u4e2d',
                 '<a[^>]+href\\s*=\\s*["\\\'](https?://[^"\\\']+)["\\\'][^>]*>\\s*(?:\u6b63\u5728)?\u8df3\u8f6c',
                 '<a[^>]+href\\s*=\\s*["\\\'](https?://[^"\\\']+)["\\\'][^>]*>\\s*\u8bf7\u7a0d\u5019'):
        m = re.search(_pat, t, re.I)
        if m:
            u = m.group(1).strip().rstrip('/')
            if re.match(r'^https?://', u):
                out.append(u)
            break
    if not out and len(t) < 900:
        hrefs = re.findall(r'<a[^>]+href\s*=\s*["\'](https?://[^"\']+)["\']', t, re.I)
        if len(hrefs) == 1:           # \u6781\u5c0f\u9875 + \u552f\u4e00\u7edd\u5bf9\u5916\u94fe \u2192 \u4e5f\u5f53\u58f3\uff08\u6587\u6848\u53d8\u4e86\u65f6\u515c\u5e95\uff09
            out.append(hrefs[0].strip().rstrip('/'))
    if not out:
        jr = _gen_js_redirect(t)
        if jr:
            out.append(jr)
    if not out and base_url:
        out = _gen_rel_paths(t, base_url)  # v2.8 \u76f8\u5bf9\u8def\u5f84\uff08\u5c04\u7a9d\u5f62\u6001\uff09
    return [u for u in dict.fromkeys(out) if u and not _gen_is_junk(u)]



def _gen_shell_target(text, base_url=''):
    """\u5355\u503c\u7248\uff08\u517c\u5bb9\u65e7\u8c03\u7528\u70b9\uff09\uff1a\u53d6 `_shell_targets` \u9996\u9879\uff1b'' = \u4e0d\u662f\u8df3\u8f6c\u58f3\u3002"""
    cs = _gen_shell_targets(text, base_url)
    return cs[0] if cs else ''



def _gen_follow_shell(url, text, headers, proxies, timeout, max_hop=3, _sink=None):
    """\u4ee5**\u5df2\u6293\u5230\u7684** text \u4e3a\u8d77\u70b9\uff0c\u8fde\u7eed\u8ddf\u968f\u8df3\u8f6c\u58f3\uff08\u2264max_hop \u8df3\uff0c\u9632\u73af\uff09\u3002

    \u8fd4\u56de (\u6700\u7ec8URL, \u5404\u8df3\u6587\u672c\u5217\u8868)\u2014\u2014\u5217\u8868**\u4e0d\u542b**\u8c03\u7528\u65b9\u5df2\u6301\u6709\u7684\u9996\u8df3 text\u3002
    \u7528\u9014\uff1a\u53d1\u5e03\u9875\u505a\u6210\u300c\u52a0\u8f7d\u4e2d\u4e2d\u8f6c\u58f3\u300d\u65f6\uff0c\u771f\u5b9e\u843d\u70b9\uff08b64 \u58f3 / \u660e\u6587\u7ebf\u8def\u8868\uff09\u5728\u4e0b\u4e00\u8df3\uff1b
    \u4e0d\u8ddf\u968f \u2192 \u62bd\u94fe 0 \u6761 \u2192 \u53ea\u80fd\u5403\u5185\u7f6e\u6c60\uff0c\u5185\u7f6e\u6c60\u4e00\u8f6e\u6362\u6574\u6e90\u5373\u6302\u3002

    v2.8\uff1a\u6bcf\u8df3\u53d6**\u5019\u9009\u5217\u8868**\u4f9d\u6b21\u5c1d\u8bd5\uff08\u7ad9\u65b9\u5e38\u5199\u591a\u7ebf\u8def\u968f\u673a\u6311\u4e00\uff0c\u5c04\u7a9d window.open \u4e09\u76ee\u5f55\uff09\uff0c
    \u5e76\u7ef4\u62a4 seen \u96c6\u5408\u9632\u300c\u76f8\u5bf9\u8def\u5f84\u6307\u56de\u81ea\u5df1\u6240\u5728\u76ee\u5f55\u300d\u9020\u6210\u7684\u91cd\u590d\u6293\u53d6\u3002
    **\u76f8\u5bf9\u8def\u5f84\u8df3\u8f6c\u53ea\u5141\u8bb8\u53d1\u751f\u4e00\u6b21**\uff1a\u4e8c\u7ea7\u58f3\u7684\u300c\u7ebf\u8def\u76ee\u5f55\u6570\u7ec4\u300d\uff08`mulu=[\"/a/\",\"/b/\"]`\uff09\u4e0e
    \u9996\u8df3\u9009\u62e9\u9875\u5f62\u6001\u5b8c\u5168\u76f8\u540c\uff0c\u518d\u8ddf\u53ea\u4f1a\u628a\u540c\u4e00\u58f3\u9875\u91cd\u590d\u6293 N \u6b21\uff08\u5c04\u7a9d\u5b9e\u6d4b\u7b2c 2/3 \u8df3\u5747\u56de\u540c\u4e00\u9875\uff0c
    \u767d\u8017 4 \u6b21\u8bf7\u6c42\uff09\u2014\u2014\u771f\u5b9e\u7684\u76f8\u5bf9\u8def\u5f84\u8df3\u8f6c\u53ea\u6709\u300c\u9009\u62e9\u9875 \u2192 \u5185\u5bb9\u58f3\u300d\u8fd9\u4e00\u8df3\u3002"""
    log = _sink.append if _sink is not None else _gen_tr
    cur_u, cur_t, hops = url, text, []
    seen = set([(url or '').rstrip('/')])
    used_rel = False
    for _ in range(max_hop):
        cands = [c for c in _gen_shell_targets(cur_t, cur_u) if c.rstrip('/') not in seen]
        if not cands:
            break
        rel = _gen_rel_paths(cur_t, cur_u)
        if rel and set(cands) <= set(rel):
            if used_rel:
                break
            used_rel = True
        nt, nxt = '', ''
        for c in cands:
            seen.add(c.rstrip('/'))
            _nt = _gen_fetch_text(c, headers, proxies, timeout)
            if _nt:
                nt, nxt = _nt, c
                break
            log('    \u2717 \u8df3\u8f6c\u58f3\u7b2c%d\u8df3\u5019\u9009 %s \u53d6\u4e0d\u5230' % (len(hops) + 1, _gen_host_of(c) or c))
        if not nt:
            break
        log('    \u8df3\u8f6c\u58f3\u7b2c%d\u8df3 \u2192 %s (%dB)' % (len(hops) + 1, _gen_host_of(nxt) or nxt, len(nt)))
        hops.append(nt)
        cur_u, cur_t = nxt, nt
    return cur_u, hops



def _gen_domlines(body):
    """\u628a\u4e00\u6bb5\u300c\u7ebf\u8def\u8868\u300d\u6587\u672c\u5207\u6210\u88f8\u57df\u540d\u884c\u3002

    \u5bb9\u5fcd\uff1a\u771f\u6362\u884c / **\u5b57\u9762 `\\n`**\uff08JS \u53cc\u5f15\u53f7\u4e32\u91cc\u5199\u4f5c `\\n`\uff0cPython \u4fa7\u662f\u53cd\u659c\u6760+n \u4e24\u5b57\u7b26\uff09/
    `\\r\\n` / \u884c\u5c3e\u9017\u53f7 / \u884c\u9996\u5c3e\u5f15\u53f7 / \u884c\u5c3e\u659c\u6760\u3002
    \u8fd4\u56de\u5408\u6cd5\u57df\u540d\u884c\uff1b\u4e0d\u8db3 2 \u884c\u3001\u6216\u4efb\u4e00\u884c\u4e0d\u662f\u7eaf\u57df\u540d \u2192 []\uff08\u5b81\u7f3a\u52ff\u6ee5\uff0c\u9632\u628a\u6b63\u6587\u5f53\u7ebf\u8def\u8868\uff09\u3002"""
    s = (body or '').replace('\\r\\n', '\n').replace('\\n', '\n').replace('\r', '\n')
    lines = []
    for l in s.split('\n'):
        l = l.strip().strip(',').strip('"\'').strip().rstrip('/').strip()
        if l:
            lines.append(l)
    if len(lines) < 2 or not all(_gen_DOMLINE_PAT.match(l) for l in lines):
        return []
    return [l for l in lines if l.rsplit('.', 1)[-1].lower() in _gen_TLD_OK]



def _gen_extract_line_bases(text):
    """\u7ad9\u65b9\u300c\u7ebf\u8def\u8868\u300d\u57fa\u57df\u62bd\u53d6\uff08v2.3 \u65b0\u589e\uff0cv2.5 \u8865\u7b2c\u4e09\u5f62\u6001\uff09\u3002

    \u4e09\u7c7b\u5f62\u6001\uff08\u4e0e _WILD_PAT \u4e92\u8865\u2014\u2014_WILD_PAT \u6293\u300c\u5b57\u9762\u91cf .\u57fa\u57df\u300d\uff0c
    \u672c\u51fd\u6570\u6293\u300c\u57fa\u57df\u672c\u4f53\u88ab\u585e\u8fdb\u6a21\u677f\u4e32/\u5f15\u53f7\u4e32/\u6570\u7ec4\u3001\u524d\u7f00\u5728\u8fd0\u884c\u65f6\u624d\u62fc\u300d\uff09\uff1a
      \u2460 \u53cd\u5f15\u53f7\u6a21\u677f\u5185\u6309\u884c\u6392\u5217\u7684\u88f8\u57df\u540d\uff08\u6a21\u677f\u4e32\u91cc\u662f\u771f\u6362\u884c\uff09\uff1a
         var zz_line = `xndzecer.cc\\ndgebtuip.cc\\nd3f9.cloudfront.net`;
      \u2461 \u5f15\u53f7\u4e32 + \u5b57\u9762 `\\n`\uff08v2.5\uff0c91\u7206\u6599\u73b0\u7f51\u5199\u6cd5\uff09\uff1a
         var zz_line = \"gdubugsu.cc\\ncekzqgmk.cc\\nd3f9.cloudfront.net\";
      \u2462 JS \u6570\u7ec4\u5b57\u9762\u91cf\u91cc\u7684\u88f8\u57df\u540d\u4e32\uff1a['a.cc','b.cc']
    \u8fd4\u56de\u57fa\u57df\u5217\u8868\uff08\u65e0\u534f\u8bae\u3001\u4fdd\u5e8f\u53bb\u91cd\u3001\u5df2\u5254\u7b2c\u4e09\u65b9\u57df\u4e0e\u975e\u6cd5 TLD\uff09\u3002"""
    out, text = [], text or ''
    for m in _gen_TICK_PAT.finditer(text):
        out += _gen_domlines(m.group(1))
    for m in _gen_QUOTED_TABLE_PAT.finditer(text):
        body = m.group(1)
        # \u53ea\u5904\u7406\u5e26\u6362\u884c\u8bed\u4e49\u7684\u4e32\uff08\u5b57\u9762 \n \u6216\u771f\u6362\u884c\uff09\uff1b\u666e\u901a\u5355\u884c\u5f15\u53f7\u4e32\u76f4\u63a5\u8df3\u8fc7\uff0c
        # \u514d\u5f97\u628a\u6ee1\u9875 JS \u5b57\u7b26\u4e32\u5168\u5582\u8fdb _domlines\uff08\u6027\u80fd + \u8bef\u62bd\u53cc\u4fdd\u9669\uff09\u3002
        if '\\n' not in body and '\n' not in body:
            continue
        out += _gen_domlines(body)
    for m in _gen_ARR_PAT.finditer(text):
        # \u5143\u7d20\u53ef\u5e26\u5c3e\u659c\u6760\uff08['a.cc/', 'b.cc/']\uff09\u2014\u2014v2.4 \u8d77\u5bb9\u5fcd
        items = re.findall(r'[\'"]([a-z0-9.-]*\.[a-z]{2,15})/?[\'"]', m.group(1), re.I)
        if len(items) >= 2:
            out += items
    return [b for b in dict.fromkeys(out)
            if not _gen_JUNK_HOST_PAT.search(b) and b.rsplit('.', 1)[-1].lower() in _gen_TLD_OK]



def _gen_attr_bases(t):
    """\u4ece HTML \u5c5e\u6027\u62bd\u300c\u88ab\u62c6\u5f00\u7684\u57df\u540d\u300d\uff08v2.7\uff0c\u7389\u7f9e\u56ed\u5f62\u6001\uff09\u3002
    `<a data-base=\"yxy999p\" houzui=\"icu\">` + JS \u62fc `${3\u4f4d\u968f\u673a\u5b57\u6bcd}.${base}.${houzui}`
    \u2192 \u8fd4\u56de\u57fa\u57df `yxy999p.icu`\uff08\u6e90\u4fa7\u518d\u62fc\u968f\u673a\u524d\u7f00\uff09\u3002\u540c\u6807\u7b7e\u5185\u5339\u914d\uff1b\u540e\u7f00\u987b\u8fc7 _TLD_OK\u3002"""
    out = []
    for i, pat in enumerate(_gen_ATTR_BASES_PAT):
        for m in pat.finditer(t or ''):
            _a, _b = m.group(1), m.group(2)
            base, suf = (_a, _b) if i == 0 else (_b, _a)
            base = (base or '').strip().strip('.').lower()
            suf = (suf or '').strip().strip('.').lower()
            if not base or suf not in _gen_TLD_OK:
                continue
            dom = base + '.' + suf
            if dom.count('.') > 3 or _gen_is_junk(dom):
                continue
            out.append(dom)
    return out



def _gen_scan_text(t, static, wilds):
    """\u4ece\u4e00\u6bb5\u6587\u672c\u62bd\u5019\u9009\uff08\u9759\u6001\u955c\u50cf\u94fe\u63a5\u8fdb static\u3001\u57fa\u57df\u8fdb wilds\uff09\u3002
    HTML \u672c\u4f53 / b64 \u89e3\u7801\u9875 / \u5916\u94fe JS \u4e09\u79cd\u6765\u6e90\u5171\u7528\u540c\u4e00\u5957\u5224\u636e\u3002

    v2.8\uff1a\u6587\u672c\u82e5\u542b\u300c\u5360\u4f4d\u7b26\u6253\u6563\u57df\u540d\u300d\u5199\u6cd5\uff08`.replace(/\u300a\u51e1\u4eba\u6b4c\u300b/g,'.')`\uff09\uff0c\u5148\u8fd8\u539f\u518d\u626b\u4e00\u904d\uff0c
    \u5e76\u5bf9\u8fd8\u539f\u6587\u672c\u542f\u7528 `_frag_bases`\uff08\u300c\u53d8\u91cf+\u5b57\u9762\u57fa\u57df\u300d\u62fc\u63a5\u5f62\u6001\uff0c\u5c04\u7a9d\u540c\u6b3e\uff09\u3002"""
    t = t or ''
    _gen_scan_one(t, static, wilds)
    rt = _gen_restore_placeholders(t)
    if rt:
        _gen_scan_one(rt, static, wilds, frag=True)



def _gen_scan_one(t, static, wilds, frag=False):
    """\u5355\u8f6e\u62bd\u53d6\u3002frag=True \u65f6\u989d\u5916\u8dd1 `_frag_bases`\uff08**\u4ec5\u8fd8\u539f\u6587\u672c**\uff0c\u9632\u6ee1\u9875\u5f15\u53f7\u4e32\u8bef\u62bd\uff09\u3002"""
    t = t or ''
    for l in re.findall(r'href=["\'](https?://[^"\']+)["\']', t, re.I):
        m = re.match(r'https?://([a-z0-9.-]+\.[a-z]{2,})', l, re.I)
        if m and not _gen_JUNK_HOST_PAT.search(m.group(1)):
            static.append('https://' + m.group(1))
    for m in _gen_WILD_PAT.finditer(t):
        wilds.add(m.group(1))
    for b in _gen_attr_bases(t):                    # v2.7 \u5c5e\u6027\u85cf\u57df\uff08data-base\u00d7houzui\uff09
        wilds.add(b)
    for b in _gen_extract_line_bases(t):
        wilds.add(b)
    if frag:
        for b in _gen_frag_bases(t):                # v2.8 \u5360\u4f4d\u7b26\u8fd8\u539f\u540e\u7684\u7247\u6bb5\u62fc\u63a5\u57df
            wilds.add(b)
    for s in _gen_js_concat_strs(t):                # v2.9 \u53d8\u91cf\u62fc\u63a5\u8fd8\u539f\uff08\u53d1\u5e03\u9875\u5f62\u6001\uff09
        m = re.match(r'https?://([a-z0-9][a-z0-9.\-]*)', s, re.I)
        if not m:
            continue
        h = m.group(1).strip('.').lower()
        # \u26a0 \u7d2f\u52a0\u662f**\u9010\u6bb5**\u7684\uff0c\u4e2d\u95f4\u6001\u4e5f\u662f\u5408\u6cd5\u5b57\u7b26\u4e32\uff08`https://bjo-eh1buu5li9`\u3001
        #   `...hscwang8s8m1`\uff09\u2014\u2014\u672b\u6bb5\u975e\u5408\u6cd5 TLD \u7684\u4e00\u5f8b\u4e22\u5f03\uff0c\u5426\u5219\u6bcf\u6b21\u767d\u8017\u63a2\u6d3b\u540d\u989d\u3002
        if (len(h) > 80 or h.count('.') > 4 or h.rsplit('.', 1)[-1] not in _gen_TLD_OK
                or _gen_is_junk(h) or _gen_FRAG_JUNK_PAT.search(h)):
            continue
        if ('https://' + h) not in static:
            static.append('https://' + h)
        parts = h.split('.')
        if len(parts) >= 3:                     # \u6cdb\u89e3\u6790\u65cf\uff1a\u5265\u6700\u5de6\u6807\u7b7e\u5f97\u57fa\u57df
            base = '.'.join(parts[1:])
            if (base.rsplit('.', 1)[-1] in _gen_TLD_OK and not _gen_is_junk(base)
                    and not _gen_FRAG_JUNK_PAT.search(base)):
                wilds.add(base)



def _gen_text_of(r):
    """\u4ece\u54cd\u5e94\u53d6\u6587\u672c\uff0c\u5e76\u4fee\u590d\u300cUTF-8 \u88ab\u8bef\u6309 Latin-1 \u89e3\u7801\u300d\u7684\u4e71\u7801\uff08v2.8\uff09\u3002

    \u26a0 \u6839\u56e0\u7ea7\u5751\uff082026-09-14 \u5c04\u7a9d\u5b9e\u6d4b\u63ea\u51fa\uff09\uff1a\u7ad9\u65b9\u54cd\u5e94\u5934\u5199 `Content-Type: text/html`
    **\u4e0d\u5e26 charset** \u2192 requests \u6309 HTTP \u89c4\u8303\u9ed8\u8ba4 `ISO-8859-1` \u89e3\u7801 UTF-8 \u5b57\u8282 \u2192
    \u9875\u9762\u6240\u6709\u4e2d\u6587\u53d8 Latin-1 \u9ad8\u4f4d\u5b57\u7b26\uff08`\u529b\u4e89\u4e0a\u6e38` \u2192 `\u00e5\\x8a\\x9b\u00e4\u00ba\\x89...`\uff09\uff0c
    \u5176\u4e2d\u7684 C1 \u63a7\u5236\u5b57\u7b26\uff08U+0080\u2013U+009F\uff09**\u4e0d\u6ee1\u8db3 `\\w`** \u2192 \u542b\u4e2d\u6587\u7684\u76f8\u5bf9\u8def\u5f84\u3001
    \u5206\u7c7b\u540d\u3001\u6807\u9898\u5168\u90e8\u5339\u914d\u5931\u8d25\uff08\u5c04\u7a9d\u9996\u8df3\u7684\u4e09\u6761\u4e2d\u6587\u76ee\u5f55\u56e0\u6b64\u62bd 0 \u6761\uff0c\u6574\u94fe\u65ad\uff09\u3002
    \uff08\u6613\u8bef\u5224\uff1a\u7ec8\u7aef GBK \u663e\u793a\u4e5f\u4f1a\u82b1\u5c4f\uff0c\u770b\u8d77\u6765\"\u50cf\u7f16\u7801\u95ee\u9898\"\u5176\u5b9e\u662f**\u53cc\u91cd\u4e71\u7801**\u2014\u2014
      requests \u89e3\u7801\u9519 + \u7ec8\u7aef\u663e\u793a\u9519\u3002\u5224\u636e\uff1a`r.encoding` \u4e3a ISO-8859-1 \u800c `r.content`
      \u662f\u5408\u6cd5 UTF-8\u3002\uff09

    \u4fee\u590d\uff1a\u51fa\u73b0 Latin-1 \u9ad8\u4f4d\u5b57\u7b26\u65f6\uff0c\u6309 latin-1 \u7f16\u56de\u5b57\u8282\u518d\u6309 utf-8 \u89e3\uff08\u5931\u8d25\u5373\u8fd4\u56de\u539f\u6587\uff0c
    \u5bf9\u7eaf ASCII / \u771f GBK \u9875\u9762\u96f6\u526f\u4f5c\u7528\uff09\u3002"""
    t = getattr(r, 'text', None) or ''
    if t and re.search(r'[\u0080-\u00ff]', t):
        try:
            return t.encode('latin-1').decode('utf-8')
        except Exception:
            pass
    return t



def _gen_fetch_text(url, headers, proxies, timeout, cap=_gen_MAX_JS_BYTES):
    """GET \u53d6\u6587\u672c\uff08\u5931\u8d25/\u975e 200 \u2192 ''\uff09\uff1b\u8d85 cap \u622a\u65ad\u3002\u7528\u4e8e\u8ddf\u968f\u5916\u94fe JS\u3002"""
    if requests is None or not url:
        return ''
    try:
        r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout,
                         verify=False, allow_redirects=True)
        if r.status_code != 200:
            return ''
        t = _gen_text_of(r)
        return t if len(t) <= cap else t[:cap]
    except Exception:
        return ''



def _gen_js_candidates(html, base_url):
    """\u53d1\u5e03\u9875\u91cc\u7684\u5916\u94fe JS\uff08JS \u58f3\u8ddf\u968f\u7528\uff09\u3002\u76f8\u5bf9\u8def\u5f84\u6309\u53d1\u5e03\u9875\u5730\u5740\u8865\u5168\uff1b
    \u5254\u7b2c\u4e09\u65b9 CDN/\u7edf\u8ba1\u57df\uff0c\u4fdd\u5e8f\u53bb\u91cd\uff0c\u6700\u591a _MAX_JS_PAGES \u4e2a\u3002"""
    out = []
    for m in _gen_JS_SRC_PAT.finditer(html or ''):
        raw = (m.group(1) or '').strip()
        if not raw or raw.startswith('data:'):
            continue
        u = urljoin(base_url or '', raw)
        if not re.match(r'^https?://', u):
            continue
        if _gen_is_junk(u) or u in out:
            continue
        out.append(u)
        if len(out) >= _gen_MAX_JS_PAGES:
            break
    return out



def _gen_extract_publish_domains(publish_page, headers, proxies, timeout, _sink=None):
    """\u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe\u3002\u8fd4\u56de (\u9759\u6001\u955c\u50cf\u94fe\u63a5\u5217\u8868, \u6cdb\u89e3\u6790/\u7ebf\u8def\u8868\u57fa\u57df\u5217\u8868)\u3002
    JS \u6e32\u67d3\u4f46\u65e0 b64 \u58f3\u7684\u9875\u9762\u9759\u6001\u94fe\u63a5\u4ecd\u53ef\u80fd\u4e3a\u7a7a\u2014\u2014\u57fa\u57df\u8bc6\u522b\u662f\u4e3b\u901a\u9053\uff1b
    \u82e5 HTML \u9636\u6bb5\u57fa\u57df\u4e3a 0\uff08JS \u58f3\u5f62\u6001\uff1a\u5185\u5bb9\u5728\u5916\u94fe js\uff09\uff0c\u81ea\u52a8**\u8ddf\u968f\u5916\u94fe JS** \u518d\u626b\u4e00\u904d\u3002

    _sink\uff1a\u53ef\u9009 list\uff0c\u672c\u9875\u7684 trace \u884c\u5199\u5165\u5b83\u800c\u975e\u5168\u5c40 _TRACE\u2014\u2014\u5e76\u884c\u6293\u591a\u9875\u65f6\u5404\u9875\u72ec\u7acb
    \u6536\u96c6\u3001\u7531\u8c03\u7528\u65b9\u6309\u5e8f\u5199\u56de\uff0c\u907f\u514d\u591a\u7ebf\u7a0b\u4ea4\u9519\u5bfc\u81f4\u8bca\u65ad\u8bb0\u5f55\u4e71\u5e8f\u3002"""
    log = _sink.append if _sink is not None else _gen_tr
    if requests is None or not publish_page:
        return [], []
    try:
        r = requests.get(publish_page, headers=headers, proxies=proxies,
                         timeout=timeout, verify=False, allow_redirects=True)
        html = _gen_text_of(r)
        log('[\u53d1\u5e03\u9875] %s \u2192 HTTP %s / %dB' % (_gen_host_of(publish_page) or publish_page,
                                             r.status_code, len(html)))
        if r.status_code != 200:
            log('  \u2717 \u53d1\u5e03\u9875\u975e 200\uff0c\u62bd\u94fe\u4e2d\u6b62')
            return [], []
    except Exception as e:
        log('[\u53d1\u5e03\u9875] %s \u6293\u53d6\u5f02\u5e38: %s' % (_gen_host_of(publish_page) or publish_page,
                                       str(e)[:60]))
        return [], []
    static, wilds = [], set()
    # \u24ea \u8df3\u8f6c\u58f3\u8ddf\u968f\uff08v2.6\uff0c2026-09-14\uff09\uff1a\u53d1\u5e03\u9875\u53ef\u80fd\u662f \u2248300B \u7684\u300c\u52a0\u8f7d\u4e2d\u300d\u4e2d\u8f6c\u58f3
    #    \uff08\u9ed1\u6599\u5bb6\u65cf\u73b0\u7f51\u540c\u6b3e\uff1a<a href>\u52a0\u8f7d\u4e2d</a> + location.replace(\u53d8\u91cf.href)\uff09\u3002
    #    \u771f\u5b9e\u843d\u70b9\uff08b64 \u58f3 / \u660e\u6587\u7ebf\u8def\u8868\uff09\u5728\u4e0b\u4e00\u8df3 \u2014\u2014 \u4e0d\u8ddf\u968f\u5219\u62bd\u94fe 0 \u6761\u3001\u53ea\u80fd\u5403\u5185\u7f6e\u6c60\uff0c
    #    \u5185\u7f6e\u6c60\u4e00\u65e6\u88ab DNS \u6c61\u67d3/\u8f6e\u6362\u6574\u6e90\u5373\u6302\uff0851\u6697\u7f51 \u590d\u76d8\uff09\u3002
    fin_u, hops = _gen_follow_shell(publish_page, html, headers, proxies, timeout, 3, _sink)
    texts = []
    for _t in [html] + hops:
        texts += _gen_expand_b64_shells(_t)
    # \u26a0 \u8ba1\u6570\u53e3\u5f84\u4fee\u6b63\uff08v2.8\uff09\uff1a_expand_b64_shells \u8fd4\u56de `[\u539f\u6587] + \u89e3\u51fa\u7684\u58f3`\uff0c
    #   \u6545\u300c\u89e3\u51fa\u4e2a\u6570\u300d= \u603b\u957f - \u8f93\u5165\u6587\u672c\u6570\uff0c\u800c\u975e \u603b\u957f-1\uff08\u65e7\u5199\u6cd5\u628a hops \u4e5f\u7b97\u6210 b64 \u58f3\uff0c
    #   \u5c04\u7a9d\u5b9e\u6d4b\u65e5\u5fd7\u62a5\u300c\u5c55\u5f00 b64 \u58f3 3 \u4e2a\u300d\u800c\u5b9e\u9645 0 \u4e2a\uff0c\u8bef\u5bfc\u6392\u67e5\uff09\u3002
    _n_b64 = len(texts) - (1 + len(hops))
    if _n_b64 > 0:
        log('  \u5c55\u5f00 b64 \u58f3 %d \u4e2a' % _n_b64)
    for t in texts:
        _gen_scan_text(t, static, wilds)
    if hops and fin_u and fin_u.rstrip('/') != (publish_page or '').rstrip('/'):
        static.append(fin_u)          # \u8df3\u8f6c\u843d\u70b9\u672c\u8eab\u4e5f\u662f\u5019\u9009\uff08\u7ad9\u65b9\u5e38\u628a\u843d\u70b9\u505a\u6210\u6d3b\u955c\u50cf\uff09
    # \u2461 JS \u58f3\u8ddf\u968f\uff1aHTML \u62bd\u4e0d\u5230\u57fa\u57df \u2192 \u7ebf\u8def\u5728 <script src="publish.js"> \u91cc\uff08\u9ec4\u679c\u540c\u6b3e\u5f62\u6001\uff09
    #    v2.6\uff1a\u82e5\u5df2\u8ddf\u968f\u8df3\u8f6c\u58f3\uff0c\u5219\u4ee5**\u843d\u70b9\u9875**\u4e3a\u57fa\u51c6\u8ddf\u968f\uff08\u843d\u70b9\u624d\u662f\u771f\u53d1\u5e03\u9875\uff09\u3002
    if not wilds:
        _base_html = (hops[-1] if hops else html)
        _base_url = fin_u or publish_page
        js_urls = _gen_js_candidates(_base_html, _base_url)
        if js_urls:
            log('  JS \u58f3\u8ddf\u968f %d \u4e2a: %s'
                % (len(js_urls), ', '.join(u.split('//', 1)[-1] for u in js_urls)))
            for ju in js_urls:
                jt = _gen_fetch_text(ju, headers, proxies, timeout)
                if not jt:
                    log('    \u2717 %s \u53d6\u4e0d\u5230' % _gen_host_of(ju))
                    continue
                log('    \u2713 %s %dB' % (_gen_host_of(ju), len(jt)))
                for t in _gen_expand_b64_shells(jt):
                    _gen_scan_text(t, static, wilds)
    log('  \u62bd\u94fe: \u9759\u6001\u94fe\u63a5 %d \u4e2a / \u57fa\u57df %d \u4e2a %s'
        % (len(dict.fromkeys(static)), len(wilds),
           ('\u2192 ' + ', '.join(sorted(wilds)[:6])) if wilds else ''))
    return list(dict.fromkeys(static)), list(wilds)



def _gen_extract_pages(pages, headers, proxies, timeout):
    """**\u5e76\u884c**\u6293\u53d6\u591a\u4e2a\u53d1\u5e03\u9875\u5e76\u62bd\u94fe\uff08v2.4\uff0c2026-09-13\uff09\u3002

    \u8fd4\u56de (pub_domains, bases, traces)\uff1a
      - pub_domains / bases \u6309 **pages \u539f\u5e8f**\u5408\u5e76\uff08\u7ed3\u679c\u786e\u5b9a\uff0c\u4e0d\u53d7\u7ebf\u7a0b\u5b8c\u6210\u65f6\u5e8f\u5f71\u54cd\uff09
      - traces = \u9010\u9875 trace \u884c\u5217\u8868\uff0c\u8c03\u7528\u65b9\u6309\u5e8f\u5199\u56de _TRACE\uff08\u591a\u7ebf\u7a0b\u4e0d\u53ef\u76f4\u63a5\u5199\u5168\u5c40\u5217\u8868\uff09
    \u7ebf\u7a0b\u6c60\u4e0d\u53ef\u7528\u65f6\u9000\u56de\u4e32\u884c\uff0c\u884c\u4e3a\u7b49\u4ef7\u3002"""
    n = len(pages or [])
    if not n:
        return [], [], []
    results = [None] * n
    traces = [[] for _ in range(n)]
    if not (ThreadPoolExecutor and as_completed) or n == 1:
        for i, pg in enumerate(pages):
            try:
                results[i] = _gen_extract_publish_domains(pg, headers, proxies,
                                                     timeout, traces[i])
            except Exception:
                results[i] = ([], [])
    else:
        ex = ThreadPoolExecutor(max_workers=min(6, n))
        try:
            futs = {}
            for i, pg in enumerate(pages):
                futs[ex.submit(_gen_extract_publish_domains, pg, headers, proxies,
                               timeout, traces[i])] = i
            for f in as_completed(list(futs)):
                i = futs[f]
                try:
                    results[i] = f.result()
                except Exception:
                    results[i] = ([], [])
        finally:
            ex.shutdown(wait=False)
    pub_domains, bases = [], []
    for i in range(n):
        s, b = results[i] or ([], [])
        for u in s:
            if u not in pub_domains:
                pub_domains.append(u)
        for x in b:
            if x not in bases:
                bases.append(x)
    return pub_domains, bases, traces



def _gen_dedupe(urls):
    """\u4fdd\u5e8f\u53bb\u91cd + \u8865\u534f\u8bae\u5934\u3002"""
    seen, out = set(), []
    for u in urls:
        u2 = (u or '').strip().rstrip('/')
        if not u2:
            continue
        if not re.match(r'^https?://', u2):
            u2 = 'https://' + u2
        if u2 not in seen:
            seen.add(u2)
            out.append(u2)
    return out



def _gen_split_publish_pages(publish_page):
    """\u5f52\u4e00 publish_page \u53c2\u6570 \u2192 \u53d1\u5e03\u9875 URL \u5217\u8868\uff08\u4fdd\u5e8f\u53bb\u91cd\uff0c2026-09-13 \u591a\u53d1\u5e03\u9875\uff09\u3002

    \u63a5\u53d7\uff1aNone / '' / 'https://a' / 'https://a,https://b' / ['https://a', ...]\u3002
    \u53ea\u8ba4 http(s) \u7edd\u5bf9\u5730\u5740\uff08\u76f8\u5bf9\u8def\u5f84\u5982 `/homeway.html` \u65e0\u6cd5\u72ec\u7acb\u6293\u53d6\uff0c\u76f4\u63a5\u4e22\u5f03\uff09\uff1b
    \u9017\u53f7\u3001\u5206\u53f7\u3001\u7a7a\u767d\u90fd\u5f53\u5206\u9694\u7b26\u2014\u2014ext \u91cc\u7528\u9017\u53f7\uff0c\u624b\u5de5\u586b\u65f6\u5206\u53f7\u4e5f\u5e38\u89c1\u3002"""
    if not publish_page:
        return []
    if isinstance(publish_page, (list, tuple)):
        raw = [str(x) for x in publish_page]
    else:
        raw = re.split(r'[,\s;]+', str(publish_page))
    out = []
    for u in raw:
        u = (u or '').strip().rstrip('/')
        if u and re.match(r'^https?://\S+$', u) and u not in out:
            out.append(u)
    return out



# ---------------------------------------------------------------- \u63a2\u6d4b
def _gen_js_redirect(t):
    """\u4ece JS \u8df3\u8f6c\u58f3\u63d0\u53d6\u76ee\u6807 URL\uff08\u7eaf JS \u58f3\u65e0 <a href> \u65f6\u515c\u5e95\u8ddf\u968f\uff09\u3002

    \u8986\u76d6\uff1awindow.location.replace('...') / window.location.href='...' /
    location.replace('...') / location.href='...' / <meta http-equiv=refresh ... url=...>\u3002
    \u8fd4\u56de\u53bb\u5c3e\u659c\u6760\u7684\u7edd\u5bf9 http(s) URL\uff0c\u5426\u5219 ''\u3002"""
    pats = [
        r'window\.location\.replace\(\s*[\'"](https?://[^\'"]+)[\'"]',
        r'window\.location\.href\s*=\s*[\'"](https?://[^\'"]+)[\'"]',
        r'location\.replace\(\s*[\'"](https?://[^\'"]+)[\'"]',
        r'location\.href\s*=\s*[\'"](https?://[^\'"]+)[\'"]',
        r'<meta[^>]+http-equiv=["\']?refresh["\']?[^>]+content=["\']?[^\'">]*url=([^"\'>\s]+)',
    ]
    for p in pats:
        m = re.search(p, t, re.I)
        if m:
            u = m.group(1).strip().rstrip('/')
            if re.match(r'^https?://', u):
                return u
    return None



def _gen_root_of(u):
    """\u53d6 URL \u7684 scheme://host \u6839\uff08\u53bb\u8def\u5f84/\u67e5\u8be2\uff09\u3002"""
    m = re.match(r'(https?://[^/?#]+)', str(u or ''), re.I)
    return m.group(1).rstrip('/') if m else ''



def _gen_probe(url, headers, proxies, timeout, depth=0, validate=None, probe_path=None):
    """\u6d4b\u8bd5\u5355\u57df\u540d\uff1a\u8df3\u8f6c\u58f3\u5219\u8ddf\u968f\uff08\u22643 \u5c42\uff0c`_shell_target` \u7edf\u4e00\u5224 <a href>\u52a0\u8f7d\u4e2d / \u5b57\u9762\u91cf JS /
    meta refresh / \u76f8\u5bf9\u8def\u5f84\u76ee\u5f55\uff09\uff1b\u6574\u9875 b64 \u58f3\u5219\u89e3\u7801\u540e\u6309\u5f62\u6001\u5224+\u6821\u9a8c\u8ba4\u5f53\u524d\u57df\u3002
    \u771f\u5185\u5bb9\u8fd4\u56de\u6700\u7ec8 host\uff1b\u5931\u8d25 None\u3002
    validate(final_host, text) -> bool\uff1a\u5185\u5bb9\u8eab\u4efd\u6821\u9a8c\uff08\u9632\u5e7f\u544a\u95e8\u7ad9/\u7b2c\u4e09\u65b9\u9875\u5192\u5145\uff09\u3002
    \u672a\u4f20 validate \u65f6\u9000\u5230\u300c\u5185\u5bb9\u5f62\u6001\u5224\u300d\uff1a\u5916\u94fe\u5f88\u591a\u53c8\u65e0\u5185\u5bb9\u7ed3\u6784 = \u5bfc\u822a\u9875 \u2192 \u62d2\u7edd\u3002

    probe_path\uff08v2.8\uff09\uff1a\u5019\u9009\u57df\u540d**\u6839\u8def\u5f84\u662f\u58f3\u9875 / \u9009\u62e9\u9875\u3001\u53ea\u6709\u6df1\u94fe\u624d\u662f\u771f\u5185\u5bb9**\u65f6\u4f20\u5b83
    \uff08\u5c04\u7a9d `/vodtype/55-1.html`\u3001\u6781\u4e50\u7981\u533a `/vodtype/45-1/`\uff1a\u6839 3214B \u9009\u62e9\u9875\u3001\u6df1\u94fe 64KB \u5185\u5bb9\uff09\u3002
    **\u53ea\u5728\u9996\u8df3\u62fc\u63a5**\uff08\u8df3\u8f6c\u843d\u70b9\u4e0d\u518d\u62fc\uff09\uff0c\u547d\u4e2d\u540e\u8fd4\u56de**\u7ad9\u70b9\u6839**\uff08scheme://host\uff09\u2014\u2014
    \u5426\u5219\u8c03\u7528\u65b9 `self.host + '/vodtype/...'` \u4f1a\u62fc\u51fa\u53cc\u8def\u5f84\u3002"""
    if requests is None:
        return None
    req = url
    if probe_path and depth == 0:
        req = url.rstrip('/') + '/' + str(probe_path).lstrip('/')
    try:
        r = requests.get(req, headers=headers, proxies=proxies,
                         timeout=timeout, verify=False, allow_redirects=True)
        if r.status_code != 200:
            return None
        t = _gen_text_of(r)
        final = (r.url or req).rstrip('/')
        ret = _gen_root_of(final) if probe_path else final
        if len(t) < 4000 and depth < 3:
            # \u2460 \u8df3\u8f6c\u58f3\u8ddf\u968f\uff1a<a href>\u52a0\u8f7d\u4e2d / \u53d8\u91cf.href / \u5b57\u9762\u91cf JS / meta refresh / \u76f8\u5bf9\u76ee\u5f55
            #    \u7edf\u4e00\u5224\uff08v2.6 \u9ed1\u6599\u5bb6\u65cf\u5f62\u6001\uff1bv2.8 \u8865\u76f8\u5bf9\u8def\u5f84\u76ee\u5f55\uff0c\u5c04\u7a9d\u9996\u8df3\uff09
            #    \u76f8\u5bf9\u8def\u5f84**\u53ea\u5728\u9996\u8df3**\u542f\u7528\uff08depth==0 \u624d\u4f20 base_url\uff09\u2014\u2014\u5426\u5219\u4e8c\u7ea7\u58f3\u7684\u7ebf\u8def\u76ee\u5f55
            #    \u6570\u7ec4\u4f1a\u88ab\u5f53\u4e0b\u4e00\u8df3\u3001\u628a\u540c\u4e00\u58f3\u9875\u53cd\u590d\u6293\uff08\u5c04\u7a9d\u5b9e\u6d4b\u767d\u8017 2 \u6b21\u8bf7\u6c42\uff09
            tgt = _gen_shell_target(t, final if depth == 0 else '')
            if tgt and tgt.rstrip('/') != final:
                return _gen_probe(tgt, headers, proxies, timeout, depth + 1, validate)
        # \u2460' \u6574\u9875 b64 \u58f3\uff08\u53d1\u5e03\u94fe\u7b2c\u4e8c\u8df3\uff09\uff1a\u89e3\u7801\u9875\u82e5\u300c\u50cf\u5185\u5bb9\u7ad9\u300d\u4e14\u8fc7\u8eab\u4efd\u6821\u9a8c \u2192 \u8ba4\u5f53\u524d\u57df
        #    \uff082026-09-14\uff1a\u8df3\u8f6c\u58f3\u2192b64\u58f3\u2192\u771f\u7ad9 \u662f\u9ed1\u6599\u5bb6\u65cf\u73b0\u7f51\u4e3b\u94fe\uff0c\u65e7\u7248\u5230\u7b2c\u4e8c\u8df3\u5373\u65ad\uff09
        if len(t) < 60000:
            for _d in _gen_expand_b64_shells(t)[1:]:
                if not _gen_looks_like_content(_d):
                    continue
                if validate is not None:
                    try:
                        if not validate(ret, _d):
                            continue
                    except Exception:
                        continue
                return ret
        if len(t) > 5000 or ('article' in t and 'category' in t):
            if not _gen_looks_like_content(t):
                return None                     # \u5047\u95e8\u7ad9\uff1a\u516c\u544a\u9875/\u5bfc\u822a\u9875\uff0c\u4e0d\u542b\u5185\u5bb9\u7ed3\u6784
            if validate is not None:
                try:
                    if not validate(ret, t):
                        return None
                except Exception:
                    return None
            return ret
        return None
    except Exception:
        return None



def _gen_probe_all(urls, headers, proxies, timeout, validate=None, tag='', probe_path=None):
    """\u5e76\u884c\u63a2\u6d4b\uff0c\u4efb\u4e00\u5019\u9009\u6210\u529f\u5373\u523b\u8fd4\u56de\uff08\u53d6\u6d88\u5176\u4f59\u4efb\u52a1\uff09\uff1b\u5168\u8d25\u8fd4\u56de ''\u3002
    \u603b\u8017\u65f6 \u2248 \u5355\u6b21\u8d85\u65f6\uff0c\u4e0d\u518d\u968f\u5019\u9009\u6570\u91cf\u53e0\u52a0\u3002"""
    if not urls:
        return ''
    if not (ThreadPoolExecutor and as_completed) or len(urls) == 1:
        for u in urls:
            h = _gen_probe(u, headers, proxies, timeout, 0, validate, probe_path)
            _gen_tr('  [%s] %s' % (tag or '\u4e32\u884c', ('\u2713 ' + h) if h else ('\u2717 ' + _gen_host_of(u))))
            if h:
                return h
        return ''
    ex = ThreadPoolExecutor(max_workers=min(12, len(urls)))
    try:
        futs = dict((ex.submit(_gen_probe, u, headers, proxies, timeout, 0, validate,
                               probe_path), u)
                    for u in urls)
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception:
                r = None
            if r:
                for x in futs:
                    x.cancel()
                ok_u = futs.get(f, '')
                _gen_tr('  [%s] \u2713 %s\uff08\u5019\u9009 %s \u547d\u4e2d\uff09' % (tag or '\u5e76\u884c', r, _gen_host_of(ok_u)))
                return r
        _gen_tr('  [%s] \u2717 %d \u4e2a\u5019\u9009\u5168\u90e8\u5931\u8d25' % (tag or '\u5e76\u884c', len(urls)))
        return ''
    finally:
        ex.shutdown(wait=False)



def _gen_probe_first(urls, headers=None, proxies=None, timeout=8, validate=None, tag='\u515c\u5e95',
                probe_path=None):
    """\u516c\u5f00\u7248\u5e76\u884c\u63a2\u6d4b\uff08\u4f9b\u5404\u6e90\u7684\u300c\u5185\u7f6e\u5019\u9009\u515c\u5e95\u300d\u7528\uff0c\u66ff\u4ee3 5\u00d78s \u4e32\u884c\u5faa\u73af\uff09\u3002
    \u4efb\u4e00\u6210\u529f\u5373\u8fd4\u56de\u5176 host\uff08\u53bb\u5c3e\u659c\u6760\uff09\uff0c\u5168\u8d25\u8fd4\u56de ''\u3002
    probe_path\uff1a\u6df1\u94fe\u63a2\u6d4b\u8def\u5f84\uff08v2.8\uff09\uff0c\u6839\u8def\u5f84\u662f\u58f3\u9875\u3001\u6df1\u94fe\u624d\u662f\u5185\u5bb9\u65f6\u4f20\uff08\u89c1 `_probe`\uff09\u3002"""
    return _gen_probe_all(_gen_dedupe(urls or []), headers, proxies, timeout, validate, tag,
                      probe_path)



def _gen_auto_validate(site_key):
    """\u6309\u7ad9\u540d\u751f\u6210\u8eab\u4efd\u6821\u9a8c\u51fd\u6570\uff08validate \u7f3a\u7701\u65f6\u7684\u9ed8\u8ba4\u5b9e\u73b0\uff09"""
    def _v(host, text):
        return site_key in (text or '')
    return _v



# ---------------------------------------------------------------- \u4e3b\u5165\u53e3
def _gen_resolve_host(publish_page=None, candidate_hosts=None, headers=None,
                 proxies=None, timeout=8, use_cache=True, validate=None,
                 site_key=None, probe_path=None):
    """\u8fd4\u56de\u5f53\u524d\u53ef\u7528 host\uff08\u53bb\u5c3e\u659c\u6760\uff09\u3002\u5168\u90e8\u5931\u8d25\u8fd4\u56de ''\uff08\u8c03\u7528\u65b9\u63a5\u53e3\u5c42\u81ea\u884c\u515c\u7a7a\uff09\u3002

    validate(final_host, text)->bool\uff1a\u7ad9\u70b9\u8eab\u4efd\u6821\u9a8c\u56de\u8c03\u3002
    site_key\uff1a\u7ad9\u540d\u5173\u952e\u8bcd\uff1bvalidate \u7f3a\u7701\u65f6\u81ea\u52a8\u7528\u5b83\u751f\u6210\u6821\u9a8c\uff08\u518d\u4e0d\u4f20\u5219\u9000\u5230\u5185\u5bb9\u5f62\u6001\u5224\uff09\u3002
    publish_page\uff1a\u5355\u4e2a\u53d1\u5e03\u9875 URL\uff0c\u6216\u591a\u4e2a\uff08\u5217\u8868 / \u9017\u53f7\u00b7\u5206\u53f7\u5206\u9694\u4e32\uff09\u2014\u2014**\u5e76\u884c\u6293\u3001\u6309\u5e8f\u5408\u5e76**\u3002
    probe_path\uff1a\u6df1\u94fe\u63a2\u6d4b\u8def\u5f84\uff08v2.8\uff09\u2014\u2014\u5019\u9009\u57df\u540d**\u6839\u8def\u5f84\u662f\u58f3\u9875/\u9009\u62e9\u9875\u3001\u53ea\u6709\u6df1\u94fe\u624d\u662f\u771f\u5185\u5bb9**
      \u65f6\u4f20\u5b83\uff08\u5c04\u7a9d `/vodtype/55-1.html`\u3001\u6781\u4e50\u7981\u533a `/vodtype/45-1/`\uff09\u3002\u547d\u4e2d\u540e\u8fd4\u56de**\u7ad9\u70b9\u6839**\u3002
    \u987a\u5e8f\uff1a\u53d1\u5e03\u9875\u57fa\u57df\u5019\u9009\uff08\u6700\u65b0\u9c9c\uff09> ext/\u5185\u7f6e\u5019\u9009 > \u53d1\u5e03\u9875\u9759\u6001\u94fe\u63a5\u3002
    \u5168\u8fc7\u7a0b\u5199\u5165 last_trace()\uff0c\u4f9b\u6e90\u5185\u300c\u8bca\u65ad\u300d\u680f\u76ee\u5c55\u793a\u3002"""
    del _gen_TRACE[:]
    candidate_hosts = candidate_hosts or []
    pages = _gen_split_publish_pages(publish_page)      # \u591a\u53d1\u5e03\u9875\uff082026-09-13\uff09
    _gen_tr('== \u9009\u7ad9\u5f00\u59cb (publish=%s | site_key=%s%s) =='
        % ('\u3001'.join([_gen_host_of(p) for p in pages]) or '(\u65e0)', site_key or '(\u672a\u4f20)',
           (' | probe=' + probe_path) if probe_path else ''))
    if validate is None and site_key:
        validate = _gen_auto_validate(site_key)
    key = (tuple(pages), tuple(candidate_hosts), site_key or '', probe_path or '')
    if use_cache:
        hit = _gen_CACHE.get(key)
        if hit and time.time() < hit[1]:
            _gen_tr('  \u547d\u4e2d\u9009\u7ad9\u7f13\u5b58 \u2192 %s\uff08%d \u79d2\u540e\u8fc7\u671f\uff09'
                % (hit[0], int(hit[1] - time.time())))
            return hit[0]

    # 1) \u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe\uff08\u57fa\u57df\u81ea\u52a8\u751f\u6210\u5019\u9009 + \u9759\u6001\u955c\u50cf\u94fe\u63a5\uff09
    #    \u591a\u4e2a\u53d1\u5e03\u9875\uff08\u7f51\u5740\u578b + GitHub \u578b\u7b49\uff09**\u5e76\u884c**\u6293\u53d6\u3001\u7ed3\u679c\u6309\u586b\u5199\u987a\u5e8f\u5408\u5e76\uff1a
    #    \u4e00\u9875\u6302\u4e86\u4e0d\u5f71\u54cd\u5176\u4ed6\u9875\uff0cN \u9875\u8017\u65f6\u4ece N\u00d7 \u964d\u4e3a \u2248max\uff08v2.4\uff0c2026-09-13\uff09\u3002
    pub_domains, bases, _pg_traces = _gen_extract_pages(pages, headers, proxies, timeout)
    for _lines in _pg_traces:                 # trace \u6309 pages \u539f\u5e8f\u5199\u56de\uff08\u5e76\u884c\u4e0b\u4e0d\u53ef\u4e71\u5e8f\uff09
        for _l in _lines:
            _gen_tr(_l)
    words = random.sample(_gen_WILD_WORDS, min(4, len(_gen_WILD_WORDS)))
    wild_candidates = []
    for b in bases:
        wild_candidates += ['https://%s.%s' % (w, b) for w in words]
        wild_candidates.append('https://%s' % b)      # \u7ad9\u65b9\u56fa\u5b9a\u7ebf\u8def\uff1a\u4e0d\u52a0\u524d\u7f00

    # 2) \u5206\u5c42\u5019\u9009\uff08\u5404\u5c42\u4fdd\u5e8f\u53bb\u91cd\uff09\uff1a
    #    \u53d1\u5e03\u9875\u5730\u5740**\u672c\u8eab\u5c31\u662f\u9996\u9009\u5019\u9009**\u2014\u2014\u7ad9\u65b9\u5e38\u628a\u300c\u53d1\u5e03\u9875\u300d\u76f4\u63a5\u505a\u6210\u4e3b\u57df\u7684\u6d3b\u955c\u50cf
    #    \uff0851\u5403\u74dc advise.nlwkmsv.cc \u5b9e\u6d4b 260KB \u5b8c\u6574\u7ad9 + 302 \u8df3\u65b0\u57df\uff1b\u82e5\u9884\u5148\u6392\u6389\u5b83\uff0c
    #    \u5c31\u53ea\u5269\u5047\u95e8\u7ad9\u53ef\u9009\uff09\u3002\u662f\u5426\u5408\u683c\u4ea4\u7ed9\u8eab\u4efd\u6821\u9a8c + \u5185\u5bb9\u5f62\u6001\u5224\u3002
    #    \u7b2c\u4e00\u5c42 = \u53d1\u5e03\u9875 + \u62bd\u94fe\u5019\u9009 + ext/\u5185\u7f6e\u5019\u9009\uff08\u65b0\u9c9c\u4e14\u53ef\u4fe1\uff09
    #    \u7b2c\u4e8c\u5c42 = \u53d1\u5e03\u9875\u91cc\u7684\u9759\u6001\u5916\u94fe\uff08\u591a\u4e3a\u5e7f\u544a/\u5bfc\u822a/\u5047\u95e8\u7ad9\uff0c\u4ec5\u7b2c\u4e00\u5c42\u5168\u8d25\u65f6\u624d\u8bd5\uff09
    tier1 = [u for u in _gen_dedupe(list(pages) + wild_candidates + list(candidate_hosts))
             if not _gen_is_junk(u)]
    _t1 = set(tier1)
    tier2 = [u for u in _gen_dedupe(pub_domains) if u not in _t1 and not _gen_is_junk(u)]

    if not tier1 and not tier2:
        _gen_tr('  \u65e0\u4efb\u4f55\u5019\u9009\u53ef\u6d4b\uff08\u53d1\u5e03\u9875\u62bd\u94fe\u4e3a\u7a7a\u4e14\u65e0\u5185\u7f6e\u5019\u9009\uff09\u2192 \u8fd4\u56de\u7a7a')
        return ''
    _gen_tr('  \u5019\u9009: \u7b2c\u4e00\u5c42 %d \u4e2a / \u7b2c\u4e8c\u5c42 %d \u4e2a\uff08\u7b2c\u4e00\u5c42\u9996\u9009=%s\uff09'
        % (len(tier1), len(tier2),
           '\u3001'.join([_gen_host_of(p) for p in pages]) or '-'))

    # 3) \u5206\u6ce2\u5b9e\u6d4b\uff08use_cache=False=\u5f3a\u5236\u5237\u65b0\uff0c\u4f46\u6210\u529f\u7ed3\u679c\u4ecd\u5199\u7f13\u5b58\u4f9b\u540e\u7eed init \u79d2\u5f00\uff09
    host = _gen_probe_all(tier1, headers, proxies, timeout, validate, '\u4e00\u7ea7', probe_path)
    if not host and tier2:
        host = _gen_probe_all(tier2, headers, proxies, timeout, validate, '\u4e8c\u7ea7', probe_path)
    if host:
        _gen_CACHE[key] = (host, time.time() + _gen_CACHE_TTL)
        _gen_tr('  \u2605 \u9009\u4e2d %s\uff08\u7f13\u5b58 30 \u5206\u949f\uff09' % host)
    else:
        _gen_tr('  \u2605 \u5168\u90e8\u5931\u8d25 \u2192 \u8fd4\u56de\u7a7a\uff08\u8c03\u7528\u65b9\u5e94\u7acb\u5373\u5931\u8d25\uff0c\u4e0d\u518d\u9759\u9ed8\u7a7a\u8f6c\uff09')
    return host

# <<< INLINE-GEN-END <<<

# >>> INLINE-GEN-BIND-START >>>
# \u5185\u8054\u63a5\u9a73\uff08\u81ea\u52a8\u751f\u6210\uff09\uff1a\u8ba9\u672c\u6e90\u5728\u300cApp \u5f62\u6001\uff08\u65e0 hostresolver.py\uff09\u300d\u4e0b\u4e5f\u62ff\u5230\u5168\u91cf\u7b97\u6cd5\u3002
# \u2460 \u9876\u66ff\u6a21\u5757\u7ea7\u5168\u5c40\uff1a\u6e90\u9876\u90e8 except \u5206\u652f\u628a\u540d\u5b57\u8bbe\u6210\u4e86 None\uff0c\u65b9\u6cd5\u5185 `if resolve_host:`
#    \u8bfb\u7684\u5c31\u662f\u8fd9\u4e9b\u5168\u5c40\u3002\u2461 \u6ce8\u518c\u5047\u6a21\u5757\uff1a\u51fd\u6570\u5185 `from hostresolver import ext_of` \u7531\u6b64\u547d\u4e2d\u3002
# \u2462 \u771f\u6a21\u5757\u5df2\u5728\uff08PC \u7aef / \u672c\u5730\u5305\u5f62\u6001\uff09\u2192 \u8df3\u8fc7\uff0c\u884c\u4e3a\u96f6\u53d8\u5316\u3002
try:
    import sys as _gen_sys
    import types as _gen_types
    if 'hostresolver' not in _gen_sys.modules:
        _gen_mod = _gen_types.ModuleType('hostresolver')
        _gen_mod.resolve_host = _gen_resolve_host
        _gen_mod.probe_first = _gen_probe_first
        _gen_mod.parse_ext = _gen_parse_ext
        _gen_mod.ext_of = _gen_ext_of
        _gen_mod.last_trace = _gen_last_trace
        _gen_mod.clear_cache = _gen_clear_cache
        _gen_sys.modules['hostresolver'] = _gen_mod
    for _gen_n in ('resolve_host', 'probe_first', 'parse_ext', 'ext_of', 'last_trace', 'clear_cache',):
        if globals().get(_gen_n) is None:
            globals()[_gen_n] = globals().get('_gen_' + _gen_n.lstrip('_'))
except Exception:
    pass
# <<< INLINE-GEN-BIND-END <<<
