# -*- coding: utf-8 -*-
# WXTS \u7ad9\u6e90\uff08MacCMS \u6a21\u677f \u00b7 HTML \u76f4\u6293\u7248\uff09
# \u53d1\u5e03\u9875: \u7ad9\u65b9 github.io\uff08\u9759\u6001\u5217\u51fa 966~969 \u56db\u955c\u50cf\uff0c2026-09-08 \u5b9e\u6d4b\u5168\u6d3b\uff09
# \u7ed3\u6784: \u5206\u7c7b /index.php/vod/type/id/{tid}/page/{pg}.html\uff08\u5217\u8868\u76f4\u94fe\u64ad\u653e\u9875\uff09
#       \u9875\u9762\u5185\u94fe\u63a5 2026-09-14 \u8d77\u4e3a /vod/.../ \u65b0\u5f62\u6001\uff0c\u670d\u52a1\u7aef\u4ecd\u53ea\u8ba4 /index.php/vod/...\u2192 \u89e3\u6790\u53cc\u5f62\u6001\u517c\u5bb9
#       \u64ad\u653e\u9875 var player_aaaa = {...} \u5185\u542b url(m3u8)/poster/link
# \u5206\u7c7b\u540d\u4e0d\u843d\u76d8\uff0chomeContent \u4ece\u9996\u9875\u5b9e\u65f6\u83b7\u53d6\uff08\u8bcd\u8868 b64 \u4e5f\u4e0d\u9700\u8981\uff09
import json
import re
import sys
import os
import html as _html
from urllib.parse import quote

import requests
sys.path.append('..')
from base.spider import Spider as BaseSpider


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
_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# \u5217\u8868\u6761\u76ee: <a class="thumbnail" href="..."><img src=\u5c01\u9762 alt=\u6807\u9898>
# \u5206\u7c7b\u9875 href=\u64ad\u653e\u9875\uff1b\u641c\u7d22\u9875 href=\u8be6\u60c5\u9875\u3002
# \u26a0 URL \u53cc\u5f62\u6001\uff082026-09-14 \u7ad9\u65b9\u6539\u7248\uff09\uff1a\u9875\u9762\u5185\u94fe\u63a5\u5df2\u6362\u6210 /vod/.../\uff08\u65e0 index.php\u3001\u5c3e\u659c\u6760\uff09\uff0c
#   \u4f46\u670d\u52a1\u7aef\u53ea\u8ba4\u8001\u5f62\u6001 /index.php/vod/....html\uff08\u65b0\u5f62\u6001 404\uff09\u2192 \u6b63\u5219\u53cc\u5f62\u6001\u517c\u5bb9\u3001\u8bf7\u6c42\u4ecd\u7528\u8001\u5f62\u6001\u3002
_RE_ITEM = re.compile(
    r'<a[^>]*class="[^"]*thumbnail[^"]*"[^>]*href="((?:/index\.php)?/vod/(?:play/id/(\d+)/sid/(\d+)/nid/(\d+)|detail/id/(\d+))(?:\.html|/))"[^>]*>\s*<img([^>]*)>')
_RE_ATTR = re.compile(r'(src|alt)\s*=\s*"([^"]*)"')
_RE_PLAY_HREF = re.compile(r'(?:/index\.php)?/vod/play/id/(\d+)/sid/(\d+)/nid/(\d+)(?:\.html|/)')


class Spider(BaseSpider):

    # \u7ad9\u65b9\u53d1\u5e03\u9875\uff08github.io \u9759\u6001\u9875\uff0c\u5217\u6700\u65b0\u955c\u50cf\u57df\u540d\uff09
    PUBLISH_PAGE = 'https://wuxiants.github.io/'
    # \u5185\u7f6e\u5019\u9009\uff082026-09-08 \u5b9e\u6d4b\uff0c\u53d1\u5e03\u9875\u5217\u51fa\u7684\u56db\u4e2a\u955c\u50cf\uff09
    BUILTIN_HOSTS = [
        'https://wxts.wuxiants966.com',
        'https://wxts.wuxiants967.com',
        'https://wxts.wuxiants968.com',
        'https://wxts.wuxiants969.com',
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
        return "\u65e0\u9650\u81c0\u5c71"

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
        if resolve_host:
            try:
                h = resolve_host(
                    publish_page=publish,
                    candidate_hosts=list(self._ext.get('hosts') or []) + builtin,
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=8,
                )
                if h:
                    return h
            except Exception:
                pass
        # resolver \u7f3a\u5931\u515c\u5e95\uff1aext \u6307\u5b9a \u2192 \u5185\u7f6e\u9010\u4e2a\u8bd5
        return self._resolve_inline(publish, builtin, lambda h,t: 'vod/type' in (t or ''))

    def _get(self, path):
        url = path if path.startswith('http') else self.host + path
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False)

    @staticmethod
    def _parse_items(html_text):
        out = []
        seen = set()
        for m in _RE_ITEM.finditer(html_text):
            img = m.group(6)
            pic = alt = ''
            for a in _RE_ATTR.finditer(img):
                if a.group(1) == 'src' and not pic:
                    pic = _html.unescape(a.group(2)).strip()
                elif a.group(1) == 'alt' and not alt:
                    alt = _html.unescape(a.group(2)).strip()
            if not alt:
                continue
            # vod_id \u4e24\u79cd\u5f62\u6001\uff1a\u64ad\u653e\u9875\u76f4\u94fe = vid-sid-nid\uff1b\u641c\u7d22\u8be6\u60c5\u9875 = d{vid}
            if m.group(2):
                vod_id = f'{m.group(2)}-{m.group(3)}-{m.group(4)}'
            else:
                vod_id = f'd{m.group(5)}'
            if vod_id in seen:
                continue
            seen.add(vod_id)
            out.append({
                'vod_id': vod_id,
                'vod_name': alt,
                'vod_pic': pic,
                'vod_remarks': '',
            })
        return out

    def homeContent(self, flag):
        result = {'class': [], 'list': []}
        try:
            r = self._get('/')
            body = r.text or ''
        except Exception:
            return result
        seen = set()
        for m in re.finditer(
                r'href="(?:/index\.php)?/vod/type/id/(\d+)(?:\.html|/)"[^>]*>([^<]+)<', body):
            tid, name = m.group(1), _html.unescape(m.group(2)).strip()
            if tid in seen or not name or name == '\u66f4\u591a':
                continue
            seen.add(tid)
            result['class'].append({'type_id': tid, 'type_name': name})
        result['list'] = self._parse_items(body)
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
        try:
            r = self._get(f'/index.php/vod/type/id/{tid}/page/{pg}.html')
            result['list'] = self._parse_items(r.text or '')
        except Exception:
            pass
        return result

    def _searchContent(self, key, quick, pg='1'):
        result = {'list': []}
        try:
            path = f'/index.php/vod/search.html?wd={quote(key)}'
            if str(pg) not in ('1', ''):
                path += f'&page={pg}'
            r = self._get(path)
            result['list'] = self._parse_items(r.text or '')
        except Exception:
            pass
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    def _play_page(self, vid, sid, nid):
        return self._get(f'/index.php/vod/play/id/{vid}/sid/{sid}/nid/{nid}.html')

    @staticmethod
    def _player_cfg(html_text):
        j = html_text.find('player_aaaa')
        if j < 0:
            return {}
        start = html_text.find('{', j)
        if start < 0:
            return {}
        # \u627e\u542b "url" \u952e\u7684\u5bf9\u8c61\u7ec8\u70b9\uff1a\u4ece m3u8/mp4 \u5904\u5411\u540e\u627e "sid" \u540e\u7684\u6536\u5c3e }
        end = html_text.find('</script>', start)
        seg = html_text[start:end if end > 0 else start + 8000]
        try:
            return json.loads(seg.strip().rstrip(';').replace('\\/', '/'))
        except Exception:
            # \u515c\u5e95\uff1a\u622a\u5230\u6700\u540e\u4e00\u4e2a } \u524d
            k = seg.rfind('}')
            if k > 0:
                try:
                    return json.loads(seg[:k + 1].replace('\\/', '/'))
                except Exception:
                    return {}
            return {}

    def _resolve_play(self, vod_id):
        """\u5f52\u4e00 vod_id \u2192 (vid, sid, nid)\u3002'd{vid}' \u5f62\u6001\u5148\u6293\u8be6\u60c5\u9875\u89e3\u6790\u64ad\u653e\u94fe\u63a5\u3002"""
        vod_id = str(vod_id)
        if vod_id.startswith('d'):
            body = self._get(f'/index.php/vod/detail/id/{vod_id[1:]}.html').text or ''
            m = _RE_PLAY_HREF.search(body)
            if not m:
                return None, None, None
            return m.group(1), m.group(2), m.group(3)
        parts = (vod_id.split('-') + ['1', '1'])[:3]
        return parts[0], parts[1], parts[2]

    def detailContent(self, ids):
        result = {'list': []}
        try:
            vid, sid, nid = self._resolve_play(ids[0])
            if not vid:
                return result
            body = self._play_page(vid, sid, nid).text or ''
            cfg = self._player_cfg(body)
            title = ''
            m = re.search(r'<title>([^<]+)</title>', body)
            if m:
                title = _html.unescape(m.group(1)).strip()
                title = re.sub('^\u5728\u7ebf\u89c2\u770b', '', title).replace('_\u65e0\u9650\u81c0\u5c71', '').strip()
            pic = str(cfg.get('poster') or '').strip()
            if not pic:
                m2 = re.search(r'<img[^>]*src="([^"]*(?:upload|vod)[^"]*)"', body)
                pic = _html.unescape(m2.group(1)).strip() if m2 else ''
            vod_id = f'{vid}-{sid}-{nid}'
            result['list'].append({
                'vod_id': vod_id,
                'vod_name': title or vid,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': '',
                'vod_director': '',
                'vod_content': '',
                'vod_play_from': str(cfg.get('from') or 'wxts'),
                'vod_play_url': f'播放${vod_id}',
            })
        except Exception:
            pass
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {'parse': 0, 'playUrl': '', 'url': '', 'header': {'User-Agent': _UA}}
        try:
            vid, sid, nid = self._resolve_play(id)
            if not vid:
                return result
            body = self._play_page(vid, sid, nid).text or ''
            cfg = self._player_cfg(body)
            url = str(cfg.get('url') or '').strip()
            if url:
                result['url'] = url
                result['header'] = {'User-Agent': _UA, 'Referer': self.host + '/'}
        except Exception:
            pass
        return result
