# -*- coding: utf-8 -*-
# \u9ec4\u679c\u77ed\u5267 \u878d\u5408\u7248
# \u878d\u5408\u4f18\u52bf\uff1a
#   - \u52a8\u6001/\u591a\u57df\u540d\u5bb9\u707e + \u5b98\u65b9\u4e3b\u7ad9\u4f18\u5148
#   - \u5206\u7c7b JSON API\uff08\u6700\u7a33\uff09 + HTML \u56de\u9000
#   - \u5b8c\u6574\u5206\u7c7b\uff1a\u7cbe\u9009/\u4e0a\u65b0/AI\u56db\u7c7b/\u4e13\u9898/\u6392\u884c/\u5403\u74dc/\u4f5c\u8005\uff08\u654f\u611f\u8bcd b64 \u5b58\u50a8\uff09
#   - \u5c01\u9762 AES \u89e3\u5bc6 + \u672c\u5730\u56fe\u7247\u4ee3\u7406\uff08Referer \u9632\u76d7\u94fe\uff09
#   - \u64ad\u653e\u4f18\u5148 videoInitialData JSON \u76f4\u53d6 m3u8\uff08parse:0\uff09
#   - \u5403\u74dc\u6587\u7ae0\u591a\u6e90\u652f\u6301
#   - BeautifulSoup + \u6b63\u5219\u53cc\u89e3\u6790
# \u4f9d\u8d56\uff1arequests, beautifulsoup4, pycryptodome (\u6216 Crypto)
# \u9002\u914d TVBox / \u7c7b TVBox \u58f3

import sys
import re
import json
import base64
import random
import threading
import html as htmllib
import urllib.parse

sys.path.append('..')
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
    from base.spider import Spider
except ImportError:
    class Spider:
        pass

# explorer.py\uff08source \u6839\uff09\uff1a\u6c60\u5168\u6302\u65f6\u4ece\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\u6d3b\u57df\uff08\u4e0e imgfetch \u540c\u76ee\u5f55\uff09
try:
    from explorer import explore_hosts
except Exception:
    try:
        import os as _os2
        sys.path.append(_os2.path.dirname(_os2.path.dirname(_os2.path.abspath(__file__))))
        from explorer import explore_hosts
    except Exception:
        explore_hosts = None
# hostresolver.py\uff08source \u6839\uff09\uff1a\u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe + \u5019\u9009\u5e76\u884c\u5b9e\u6d4b\uff08\u4e0e explorer \u540c\u76ee\u5f55\uff09
try:
    from hostresolver import resolve_host, probe_first, ext_of
except ImportError:
    resolve_host = probe_first = ext_of = None
except Exception:
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import resolve_host, probe_first, ext_of
    except Exception:
        resolve_host = None
        probe_first = None
        ext_of = None

try:
    import requests as rq
    rq.packages.urllib3.disable_warnings()
except Exception:
    pass

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from Crypto.Cipher import AES
except ImportError:
    try:
        from Cryptodome.Cipher import AES
    except ImportError:
        AES = None

# ---------- \u5e38\u91cf ----------
HOSTS = [
    "https://huangguoai.com",
    "https://ttvoij.ediayikma.cc",
    "https://thu.ediayikma.cc",
    "https://pku.ediayikma.cc",
    "https://fdu.ediayikma.cc",
    "https://thu.agdkczeyx.cc",
]
# \u5b98\u65b9\u5730\u5740\u53d1\u5e03\u9875\uff082026-09-13 \u5b9e\u6d4b\uff09\uff1ahuangguo5.com / huangguo3.com / huangguoai.ai \u4e09\u9875
# \u540c\u6e90\uff0846KB\uff0c\u6807\u9898\u300c\u5b98\u65b9\u6700\u65b0\u5730\u5740\u53d1\u5e03\u9875\u00b7\u9ec4\u679c\u77ed\u5267\u300d\uff09\uff0c\u7ebf\u8def\u4ee5 <a href="https://\u8bcd.\u57fa\u57df.cc">
# \u5f62\u5f0f\u5217\u51fa\u3001**\u6bcf\u6b21\u6253\u5f00\u968f\u673a\u8f6e\u6362**\uff08\u5f53\u524d\u57fa\u57df mvbessfgf.cc\uff0c\u6cdb\u89e3\u6790\uff09\uff0c\u6545\u53ea\u80fd\u9760\u53d1\u5e03\u9875\u73b0\u62bd\u73b0\u7528\u3002
# \u6ce8\u610f\uff1a\u53d1\u5e03\u9875\u542b <article class="route-card">\uff0c\u4f1a\u88ab hostresolver \u7684\u300c\u5185\u5bb9\u5f62\u6001\u5224\u300d\u8bef\u653e\u884c
# \u2192 \u5fc5\u987b\u9760 _validate \u7684\u5185\u5bb9\u7ed3\u6784\u8981\u6c42\u628a\u5b83\u6321\u6389\uff0c\u5426\u5219\u4f1a\u88ab\u5f53\u6210 host\uff08\u5168\u5206\u7c7b\u7a7a\uff09\u3002
# ext \u7684 publish@ \u4f18\u5148\uff0c\u6b64\u5904\u4e3a\u5185\u7f6e\u515c\u5e95\uff08ext \u7f3a\u5931/\u672a\u4e0b\u53d1\u65f6\u4ecd\u80fd\u6362\u57df\uff09\u3002
PUBLISH_PAGE = "https://huangguo5.com/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
TIMEOUT = 18
PAGE_SIZE = 24
# AES \u5c01\u9762\u89e3\u5bc6\uff08\u7ad9\u70b9 CDN \u52a0\u5bc6\uff09
_AES_KEY = b'f5d965df75336270'
_AES_IV = b'97b60394abc2fbe1'
_PLACEHOLDER_GIF = base64.b64decode(
    'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
_PROXY_PORT = [0]
_TAG_RE = re.compile(r'<[^>]+>')


def _clean(s):
    if not s:
        return ""
    s = htmllib.unescape(str(s))
    s = _TAG_RE.sub(' ', s)
    return re.sub(r'\s+', ' ', s).strip()


# ---------- \u672c\u5730\u56fe\u7247\u4ee3\u7406\u670d\u52a1\u5668 ----------
try:
    from http.server import BaseHTTPRequestHandler, HTTPServer

    def _fetch_img_raw(u, referer):
        headers = {"User-Agent": UA, "Referer": referer,
                   "Accept": "image/*"}
        # \u5171\u4eab\u52a0\u901f\u901a\u9053\uff1aSession \u8fde\u63a5\u590d\u7528 + LRU \u7f13\u5b58\uff082026-09-08 \u5217\u8868\u63d0\u901f\uff09
        if _shared_fetch_img is not None:
            try:
                mime, data = _shared_fetch_img(u, headers=headers, timeout=15)
                if data and len(data) > 50:
                    return data
                return b''
            except Exception:
                pass
        try:
            rr = rq.get(u, headers=headers, timeout=15, verify=False,
                        allow_redirects=True)
            if rr.status_code == 200 and rr.content and len(rr.content) > 50:
                return rr.content
        except Exception:
            pass
        return b''

    def _decrypt_img(data):
        if not data or AES is None:
            return data
        # \u5df2\u662f\u6b63\u5e38\u56fe\u7247\u5219\u76f4\u63a5\u8fd4\u56de
        if data[:3] == b'\xff\xd8\xff' or data[:8] == b'\x89PNG\r\n\x1a\n' \
                or data[:6] in (b'GIF87a', b'GIF89a') \
                or (data[:4] == b'RIFF' and data[8:12] == b'WEBP'):
            return data
        try:
            dec = AES.new(_AES_KEY, AES.MODE_CBC, _AES_IV).decrypt(data)
            # \u53bb PKCS7 / \u5c3e\u90e8 null
            pad = dec[-1]
            if 1 <= pad <= 16 and all(b == pad for b in dec[-pad:]):
                dec = dec[:-pad]
            else:
                dec = dec.rstrip(b'\x00')
            if dec[:3] == b'\xff\xd8\xff' or dec[:8] == b'\x89PNG\r\n\x1a\n':
                return dec
            return dec  # \u4ecd\u8fd4\u56de\u5c1d\u8bd5\u7ed3\u679c
        except Exception:
            return data

    def _detect_mime(data):
        if data[:3] == b'\xff\xd8\xff':
            return 'image/jpeg'
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return 'image/png'
        if data[:6] in (b'GIF87a', b'GIF89a'):
            return 'image/gif'
        if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            return 'image/webp'
        return 'image/jpeg'

    class _ImgHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                pr = urllib.parse.urlparse(self.path)
                if pr.path not in ('/img', '/proxy'):
                    self.send_response(404)
                    self.end_headers()
                    return
                q = urllib.parse.parse_qs(pr.query)
                u = q.get('u', q.get('url', ['']))[0]
                u = urllib.parse.unquote(u)
                if not u.startswith('http'):
                    self.send_response(400)
                    self.end_headers()
                    return
                raw = _fetch_img_raw(u, HOSTS[0] + "/")
                data = _decrypt_img(raw) if raw else b''
                if not data or len(data) < 50:
                    data, ctype = _PLACEHOLDER_GIF, 'image/gif'
                else:
                    ctype = _detect_mime(data)
                self.send_response(200)
                self.send_header('Content-Type', ctype)
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Cache-Control', 'max-age=86400')
                self.end_headers()
                self.wfile.write(data)
            except Exception:
                pass

        def log_message(self, *args):
            pass

    def _start_proxy_server():
        if _PROXY_PORT[0]:
            return _PROXY_PORT[0]
        for port in [9978] + list(range(9979, 10020)) + list(range(30261, 30281)):
            try:
                srv = HTTPServer(('127.0.0.1', port), _ImgHandler)
                _PROXY_PORT[0] = port
                threading.Thread(target=srv.serve_forever, daemon=True).start()
                return port
            except Exception:
                continue
        return 0
except Exception:
    def _start_proxy_server():
        return 0
    def _decrypt_img(data):
        return data
    def _detect_mime(data):
        return 'image/jpeg'




class Spider(Spider):

    def getName(self):
        return "\u9ec4\u679c\u77ed\u5267"

    def init(self, extend=""):
        # \u5148\u7ed9\u9ed8\u8ba4\u503c\uff0c\u9632\u6b62\u90e8\u5206\u58f3\u4e0d\u8c03\u7528 init \u6216\u8c03\u7528\u5931\u8d25\u5bfc\u81f4 AttributeError
        self.host = HOSTS[0].rstrip('/')
        # ext \u652f\u6301\uff082026-09-11 \u8865\uff09\uff1apublish@\u53d1\u5e03\u9875 / hosts@\u5019\u9009 / host@\u9501\u5b9a\uff0c
        # \u7ba1\u7406\u53f0\u300c\u914d\u7f6e \u2192 \u57df\u540d\u300d\u53ef\u76f4\u63a5\u6539\uff0c\u4e0d\u5fc5\u518d\u52a8\u6e90\u6587\u4ef6
        self._ext = {}
        self.proxies = {}
        try:
            if ext_of:
                self._ext = ext_of(extend) or {}
        except Exception:
            self._ext = {}
        try:
            self.host = self._pick_host()
        except Exception:
            pass
        try:
            self.s = rq.Session()
            self.s.verify = False
            self.s.headers.update({
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Referer": self.host + "/",
            })
        except Exception:
            self.s = None
        try:
            _start_proxy_server()
        except Exception:
            pass

    def _pick_host(self):
        """\u53d6\u57df v2.4\uff082026-09-13\uff09\uff1aext \u9501\u5b9a \u2192 \u5019\u9009**\u5e76\u884c**\u5b9e\u6d4b\uff08\u5e26\u8eab\u4efd\u6821\u9a8c\uff09
        \u2192 \u53d1\u5e03\u9875\u62bd\u94fe \u2192 \u5bfc\u822a\u7ad9\u63a2\u7d22\u3002\u539f\u4e3a 6\u00d75s \u4e32\u884c\uff0c\u7ad9\u70b9\u6302\u65f6\u8981\u8f6c\u5708 30 \u79d2\u3002
        v2.4 \u53d8\u66f4\uff1a\u63a5\u5165\u5b98\u65b9\u53d1\u5e03\u9875\uff08ext publish@ \u4f18\u5148\uff0cPUBLISH_PAGE \u515c\u5e95\uff09\u2014\u2014
        \u7ad9\u65b9 2026-09 \u5df2\u6362\u65cf\uff08ediayikma.cc/agdkczeyx.cc \u2192 mvbessfgf.cc\uff09\uff0c
        \u5185\u7f6e\u6c60\u4f1a\u6ede\u540e\uff1b\u53d1\u5e03\u9875\u6bcf\u6b21\u6253\u5f00\u5373\u7ed9\u51fa\u5f53\u524d\u53ef\u7528\u7ebf\u8def\u3002"""
        ext = getattr(self, '_ext', {}) or {}
        if ext.get('host'):
            return str(ext['host']).rstrip('/')

        pub = (ext.get('publish') or '').strip() or PUBLISH_PAGE

        def _validate(host, text):
            # v2.4 \u6536\u7d27\uff1a\u5fc5\u987b\u300c\u7ad9\u540d + \u7ad9\u5185\u5185\u5bb9\u7ed3\u6784\u300d\u53cc\u6ee1\u8db3\u3002
            # \u539f\u5224\u636e\u53ea\u8ba4\u7ad9\u540d\uff0c\u800c\u5b98\u65b9\u53d1\u5e03\u9875\uff0846KB\uff0c\u542b <article class="route-card">\uff09
            # \u540c\u6837\u542b\u300c\u9ec4\u679c\u300d\u4e8c\u5b57\uff0c\u4f1a\u88ab\u9009\u4e2d\u5f53 host \u2192 \u5206\u7c7b\u5168\u7a7a\u3002
            t = text or ''
            if not (('\u9ec4\u679c' in t) or ('huangguo' in t.lower())):
                return False
            return ('hg-drama-card' in t) or ('videoInitialData' in t)

        cands = list(ext.get('hosts') or []) + HOSTS
        if resolve_host:
            try:
                h = resolve_host(publish_page=pub,
                                 candidate_hosts=cands,
                                 headers={'User-Agent': UA},
                                 proxies=getattr(self, 'proxies', {}) or {},
                                 timeout=8, validate=_validate, site_key='\u9ec4\u679c')
                if h:
                    return h
            except Exception:
                pass
        if probe_first:
            try:
                h = probe_first(cands, headers={'User-Agent': UA},
                                proxies=getattr(self, 'proxies', {}) or {},
                                timeout=6, validate=_validate, tag='\u515c\u5e95')
                if h:
                    return h
            except Exception:
                pass
        # \u7ec8\u6781\u515c\u5e95\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\uff08\u8df3\u8f6c\u58f3/\u95e8\u6237/\u6cdb\u89e3\u6790\u8ddf\u968f + \u7ad9\u540d\u8eab\u4efd\u9a8c\u8bc1\uff09
        if explore_hosts:
            try:
                def _probe(u):
                    r = rq.get(u.rstrip('/') + '/', headers={"User-Agent": UA}, timeout=8, verify=False)
                    return r.status_code == 200 and '\u9ec4\u679c' in (r.text or '')
                hs = explore_hosts(['huangguo', '\u9ec4\u679c'], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        # \u5168\u8d25\uff1a\u663e\u5f0f\u8fd4\u56de\u7a7a
        return self._resolve_inline(pub, HOSTS, _validate)

    def _resolve_inline(self, publish, builtin, validate):
        """hostresolver \u672a\u52a0\u8f7d\u65f6\u7684\u5185\u8054\u5e76\u884c\u63a2\u6d4b\uff1a\u907f\u514d\u4e32\u884c\u8d85\u65f6\u5bfc\u81f4 App \u7aef\u7a7a\u8f6c\u51e0\u5341\u79d2\u3002
        \u5e26\u5185\u5bb9\u5f62\u6001\u5224\uff0c\u9632\u6b62\u547d\u4e2d\u53d1\u5e03\u9875/\u95e8\u6237\u516c\u544a\u9875\uff1b\u53d1\u5e03\u9875\u975e\u6d3b\u955c\u50cf\u65f6\u505a\u6df1\u5ea6\u62bd\u94fe
        \uff08\u5bf9\u6807 hostresolver.extract_publish_domains\uff0cgitee \u5f62\u6001\u4e0e\u672c\u5730\u5305\u540c\u7b49\u80fd\u529b\uff09\u3002"""
        import threading
        candidates = []
        # \u591a\u53d1\u5e03\u9875\uff082026-09-13\uff09\uff1apublish \u53ef\u80fd\u662f\u9017\u53f7\u4e32\uff08\u7f51\u5740\u578b + GitHub \u578b\u5e76\u5b58\uff09\uff0c
        # \u62c6\u6210\u591a\u6761\u5019\u9009\u5206\u522b\u5e76\u884c\u6293\uff1b\u975e\u7edd\u5bf9\u5730\u5740\uff08\u76f8\u5bf9\u8def\u5f84\uff09\u65e0\u6cd5\u72ec\u7acb\u6293\u53d6\uff0c\u4e22\u5f03\u3002
        _pages = [x for x in re.split(r'[,\s;]+', str(publish or ''))
                  if x.startswith('http')]
        candidates += _pages or ([str(publish)] if publish else [])
        candidates += list(getattr(self, '_ext', {}).get('hosts') or [])
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
                r = rq.get(u + '/', headers={"User-Agent": UA}, timeout=5,
                           verify=False, allow_redirects=True)
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
                    _r = _http.get(_u, headers=self.headers, proxies=self.proxies,
                                      timeout=6, verify=False, allow_redirects=True)
                except Exception:
                    return
                if _r.status_code != 200 or not _r.text:
                    return
                _texts.append(_r.text)
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
                        _jr = _http.get(_s, headers=self.headers,
                                           proxies=self.proxies, timeout=6,
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
    def _safe_host(self):
        """\u4efb\u4f55\u65f6\u5019\u90fd\u80fd\u62ff\u5230\u4e00\u4e2a\u53ef\u7528 host"""
        h = getattr(self, 'host', None)
        if h and isinstance(h, str) and h.startswith('http'):
            return h.rstrip('/')
        return HOSTS[0].rstrip('/')

    def _wrap_pic(self, url):
        """\u5c01\u9762\u8d70\u672c\u5730\u4ee3\u7406\uff08\u5e26 Referer + AES \u89e3\u5bc6\uff09"""
        if not url or not str(url).startswith('http'):
            return url or ""
        if not _PROXY_PORT[0]:
            _start_proxy_server()
        if _PROXY_PORT[0]:
            return ("http://127.0.0.1:%d/proxy?url=%s"
                    % (_PROXY_PORT[0], urllib.parse.quote(url, safe='')))
        # \u65e0\u4ee3\u7406\u65f6\u9000\u56de TVBox localProxy \u683c\u5f0f
        try:
            b = base64.b64encode(url.encode('utf-8')).decode('ascii')
            return f"proxy://type=pic&url={b}"
        except Exception:
            return url

    def _get(self, path, ref="/"):
        host = self._safe_host()
        url = host + path if path.startswith('/') else path
        try:
            headers = {"User-Agent": UA, "Referer": host + (ref if ref.startswith('/') else '/' + ref)}
            if getattr(self, 's', None) is not None:
                r = self.s.get(url, timeout=TIMEOUT, allow_redirects=True, headers=headers)
            else:
                r = rq.get(url, timeout=TIMEOUT, verify=False, headers=headers)
            if r.status_code == 200 and r.text:
                r.encoding = 'utf-8'
                return r.text
        except Exception:
            pass
        return ""

    def isVideoFormat(self, url):
        return any(x in (url or '') for x in ['.m3u8', '.mp4', '.flv', '.mkv', '.avi'])

    def manualVideoCheck(self):
        return False

    # ---------- \u9996\u9875 ----------

    def homeContent(self, filter=False):

        result = {
            "class": [
                {"type_id": "recommend", "type_name": "\u7cbe\u9009\u63a8\u8350"},
                {"type_id": "newest", "type_name": "\u6700\u8fd1\u4e0a\u65b0"},
                {"type_id": "ai-duanju", "type_name": base64.b64decode('QUnmiJDkurrnn63liac=').decode('utf-8')},
                {"type_id": "ai-manju", "type_name": base64.b64decode('QUnmiJDkurrmvKvliac=').decode('utf-8')},
                {"type_id": "ai-huanlian", "type_name": "AI\u6362\u8138"},
                {"type_id": "ai-mogai", "type_name": "AI\u9b54\u6539"},
                {"type_id": "topic", "type_name": "\U0001f4cc\u4e13\u9898"},
                {"type_id": "ranks", "type_name": "\u6392\u884c\u699c"},
                {"type_id": "chigua", "type_name": "\u9ec4\u679c\u5403\u74dc"},
                {"type_id": "author", "type_name": "\u9ec4\u679c\u5b98\u65b9"},
            ],
            "list": [],
            "filters": {
                "ranks": [{"key": "\u7c7b\u578b", "name": "\u7c7b\u578b", "value": [
                    {"n": "\u70ed\u64ad\u699c", "v": "hot"},
                    {"n": "\u63a8\u8350\u699c", "v": "recommend"},
                    {"n": "\u6f5c\u529b\u699c", "v": "potential"},
                ]}],
                "chigua": [{"key": "\u7c7b\u578b", "name": "\u7c7b\u578b", "value": [
                    {"n": "\u5168\u90e8", "v": "page"},
                    {"n": "\u70ed\u95e8\u5403\u74dc", "v": "remen"},
                    {"n": "AI\u539f\u521b", "v": "yuanchuang"},
                ]}],
                "author": [{"key": "\u7c7b\u578b", "name": "\u7c7b\u578b", "value": [
                    {"n": "\u9ec4\u679c\u5b98\u65b9", "v": "156291"},
                    {"n": "\u9ec4\u679cai\u5927\u5e08", "v": "156305"},
                ]}],
            }
        }
        if filter:
            pass
        try:
            html = self._get("/")
            if html:
                result["list"] = self._parse_list(html)
        except Exception:
            pass
        return result

    def homeVideoContent(self):
        try:
            html = self._get("/recommend/1/")
            if not html:
                html = self._get("/")
            return {"list": self._parse_list(html)}
        except Exception:
            return {"list": []}

    # ---------- \u5206\u7c7b ----------
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

    def _categoryContent(self, tid, pg=1, filter=False, extend=""):
        try:
            pg = int(str(pg or 1))
        except Exception:
            pg = 1
        if pg < 1:
            pg = 1
        cid = str(tid or "").strip().strip("/")
        ext = extend if isinstance(extend, dict) else {}
        rc = ext.get("\u7c7b\u578b", cid)

        videos, pages, total = [], 9999, 0

        try:
            # \u4e13\u9898\u6587\u4ef6\u5939
            if cid.startswith("dir_topic_"):
                slug = cid.replace("dir_topic_", "")
                html = self._get(f"/topics/{slug}/?page={pg}")
                videos = self._parse_list(html, mode="drama")
                return self._result(videos, pg, 9999)

            # AI \u56db\u5206\u7c7b\u4f18\u5148 JSON API
            if cid in ("ai-duanju", "ai-manju", "ai-huanlian", "ai-mogai"):
                videos, pages, total = self._category_api(cid, pg)
                if not videos:
                    path = f"/{cid}/" if pg <= 1 else f"/{cid}/{pg}/"
                    html = self._get(path)
                    videos = self._parse_list(html)
                    ps = [int(x) for x in re.findall(
                        r'/' + re.escape(cid) + r'/(\d+)/', html or "")]
                    if ps:
                        pages = max(ps)
                if len(videos) > PAGE_SIZE:
                    videos = videos[:PAGE_SIZE]
                return self._result(videos, pg, pages or 9999, total)

            # \u5176\u5b83\u56fa\u5b9a\u8def\u5f84
            if cid == "recommend":
                html = self._get(f"/recommend/{pg}/")
                videos = self._parse_list(html)
            elif cid == "newest":
                html = self._get(f"/newest/{pg}/")
                videos = self._parse_list(html)
            elif cid == "topic":
                html = self._get("/topics/")
                videos = self._parse_list(html, mode="topic")
                pages = 1
            elif cid == "ranks":
                rtype = rc if rc in ("hot", "recommend", "potential") else "hot"
                html = self._get(f"/ranks/{rtype}/")
                videos = self._parse_list(html, mode="rank")
                pages = 1
            elif cid == "chigua":
                ctype = rc if rc in ("page", "remen", "yuanchuang") else "page"
                html = self._get(f"/chigua/{ctype}/{pg}/")
                videos = self._parse_list(html, mode="post")
            elif cid == "author":
                aid = rc if str(rc).isdigit() else "156291"
                html = self._get(f"/author/{aid}/video/{pg}/")
                videos = self._parse_list(html)
            else:
                # \u515c\u5e95\u5f53\u666e\u901a\u5206\u7c7b
                path = f"/{cid}/" if pg <= 1 else f"/{cid}/{pg}/"
                html = self._get(path)
                videos = self._parse_list(html)

        except Exception:
            videos = []

        return self._result(videos, pg, pages, total)

    def _category_api(self, slug, pg):
        url = (f"/api/videos/category/{urllib.parse.quote(slug)}"
               f"?sort=hot&page={pg}&size={PAGE_SIZE}")
        text = self._get(url, ref="/" + slug + "/")
        if not text:
            return [], 0, 0
        try:
            data = json.loads(text)
        except Exception:
            return [], 0, 0
        d = data.get("data") or {}
        items = d.get("items") or []
        pag = d.get("pagination") or {}
        videos = []
        for it in items:
            v = self._api_item(it)
            if v:
                videos.append(v)
        pages = total = 0
        try:
            pages = int(pag.get("pages") or 0)
        except Exception:
            pass
        try:
            total = int(pag.get("total") or 0)
        except Exception:
            pass
        return videos, pages, total

    def _api_item(self, it):
        vid = it.get("id")
        if vid is None:
            return None
        title = _clean(it.get("title"))
        if not title:
            return None
        pic = (it.get("cover") or "").strip()
        epc = it.get("episode_count")
        finished = it.get("is_finished")
        if finished:
            remark = "\u5168%d\u96c6" % epc if epc else "\u5168\u5267"
        else:
            remark = "\u66f4\u65b0\u81f3%d\u96c6" % epc if epc else "\u8fde\u8f7d\u4e2d"
        score = it.get("score")
        if score:
            remark = f"{score}分 " + remark
        return {
            "vod_id": str(vid),
            "vod_name": title,
            "vod_pic": self._wrap_pic(pic),
            "vod_remarks": remark or "\u5728\u7ebf\u89c2\u770b",
        }

    def _result(self, videos, pg, pagecount=9999, total=0):
        n = len(videos)
        if total < 1:
            total = pagecount * max(n, 1) if pagecount > 1 else n
        return {
            "list": videos,
            "page": pg,
            "pagecount": pagecount,
            "limit": PAGE_SIZE,
            "total": total,
        }

    # ---------- \u641c\u7d22 ----------
    def _searchContent(self, key, quick=False, pg="1"):
        return self.searchContentPage(key, quick, pg)

    def searchContentPage(self, key, quick, page):
        kw = urllib.parse.quote(str(key or "").strip())
        if not kw:
            return {"list": [], "page": 1, "pagecount": 1, "limit": 20, "total": 0}
        try:
            pg = int(page) if page else 1
        except Exception:
            pg = 1
        html = self._get(f"/search/video/{kw}/{pg}/")
        videos = self._parse_list(html, mode="search")
        has_more = len(videos) >= 18
        return {
            "page": pg,
            "pagecount": pg + 1 if has_more else pg,
            "limit": 20,
            "total": 0,
            "list": videos,
        }

    # ---------- \u8be6\u60c5 ----------
    def detailContent(self, ids):
        try:
            raw = ids[0] if isinstance(ids, (list, tuple)) else ids
            did = str(raw).strip()
        except Exception:
            return {"list": []}
        if not did:
            return {"list": []}

        # \u5403\u74dc\u6587\u7ae0
        if "/archives/" in did or did.startswith("http") and "archives" in did:
            return self._detail_chigua(did)

        # \u7edf\u4e00\u6210\u7eaf\u6570\u5b57 id
        m = re.search(r'(?:detail/|/)?(\d+)/?$', did)
        vid = m.group(1) if m else (did if did.isdigit() else None)
        if not vid:
            # \u53ef\u80fd\u662f\u5b8c\u6574\u8def\u5f84
            html = self._get(did if did.startswith("/") else "/" + did)
        else:
            html = self._get(f"/detail/{vid}/")

        if not html:
            return {"list": []}

        title = ""
        m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        if m:
            title = _clean(m.group(1))
        if not title:
            m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
            if m:
                title = _clean(m.group(1))
        if not title:
            m = re.search(r'<title>(.*?)</title>', html)
            if m:
                title = _clean(m.group(1).split('|')[0])
        if not title:
            return {"list": []}

        pic = ""
        m = re.search(r'<img[^>]*data-src="([^"]+)"[^>]*>', html)
        if m:
            pic = htmllib.unescape(m.group(1)).strip()
        if not pic:
            m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
            if m:
                pic = htmllib.unescape(m.group(1)).strip()

        desc = ""
        m = re.search(r'<p class="[^"]*hg-web-detail__desc[^"]*"[^>]*>(.*?)</p>', html, re.S)
        if m:
            desc = _clean(m.group(1))
        if not desc:
            m = re.search(r'<meta name="description" content="([^"]+)"', html)
            if m:
                desc = _clean(m.group(1))

        meta = ""
        m = re.search(r'class="[^"]*hg-web-detail__meta[^"]*"[^>]*>(.*?)</div>', html, re.S)
        if m:
            meta = _clean(m.group(1))
        tags = []
        for m in re.finditer(r'class="hg-tag"[^>]*href="(/tag/[^"]+)"[^>]*>([^<]+)<', html):
            tags.append(_clean(m.group(2)))
        remark = meta or "\u5728\u7ebf\u89c2\u770b"

        # \u5267\u96c6\u5217\u8868\uff08\u517c\u5bb9\u5e26 <img> \u7684\u7acb\u5373\u64ad\u653e\u6309\u94ae\u3001\u5355\u96c6\u3001\u591a\u96c6\uff09
        eps = []
        seen = set()
        if vid:
            # 1) \u5bbd\u677e\u5339\u914d\u6240\u6709 /video/{vid}/ \u548c /video/{vid}/ep-n/
            for m in re.finditer(
                    r'href="(/video/' + re.escape(vid) + r'(?:/ep-(\d+))?/)"', html):
                path = m.group(1)
                if path in seen:
                    continue
                seen.add(path)
                epn = m.group(2)
                label = f"{int(epn):02d}" if epn else "01"
                eps.append((label, path))

            # 2) \u5e26\u6587\u5b57\u7684\u94fe\u63a5\uff08\u6709\u7684\u9875\u9762\u6709\uff09
            for m in re.finditer(
                    r'href="(/video/' + re.escape(vid) + r'(?:/ep-\d+)?/)"[^>]*>(.*?)</a>',
                    html, re.S):
                path = m.group(1)
                label = _clean(m.group(2)) or None
                if path in seen:
                    # \u5c1d\u8bd5\u7528\u66f4\u597d\u7684\u6587\u5b57\u66f4\u65b0 label
                    if label and label not in ("\u7acb\u5373\u64ad\u653e", "\u64ad\u653e"):
                        for i, (lb, p) in enumerate(eps):
                            if p == path and (lb.isdigit() or lb == "01"):
                                eps[i] = (label, p)
                                break
                    continue
                seen.add(path)
                if not label or label in ("\u7acb\u5373\u64ad\u653e", "\u64ad\u653e"):
                    em = re.search(r'/ep-(\d+)/', path)
                    label = f"{int(em.group(1)):02d}" if em else "01"
                eps.append((label, path))

            # 3) \u8be6\u60c5\u9875\u6ca1\u6709\u96c6\u6570\u65f6\uff0c\u53bb\u64ad\u653e\u9875\u518d\u6293\u4e00\u6b21
            if not eps:
                vhtml = self._get(f"/video/{vid}/")
                if vhtml:
                    for m in re.finditer(
                            r'href="(/video/' + re.escape(vid) + r'(?:/ep-(\d+))?/)"',
                            vhtml):
                        path = m.group(1)
                        if path in seen:
                            continue
                        seen.add(path)
                        epn = m.group(2)
                        label = f"{int(epn):02d}" if epn else "01"
                        eps.append((label, path))
                    for m in re.finditer(
                            r'<a class="hg-play__ep-item[^"]*" href="([^"]*)"[^>]*data-ep-id="([^"]*)"[^>]*>([^<]*)</a>',
                            vhtml):
                        path = m.group(1)
                        if not path.startswith("/"):
                            path = "/" + path
                        if path in seen:
                            continue
                        seen.add(path)
                        label = _clean(m.group(3)) or f"第{m.group(2)}集"
                        eps.append((label, path))

        eps = sorted(eps, key=lambda x: self._ep_sort(x[1]))
        if not eps and vid:
            eps = [("01", f"/video/{vid}/")]

        play_from = ["\u6b63\u7247"]
        play_url = ["#".join(f"{l}${p}" for l, p in eps)]

        vod = {
            "vod_id": vid or did,
            "vod_name": title,
            "vod_pic": self._wrap_pic(pic),
            "type_name": ",".join(tags) or "\u9ec4\u679c\u77ed\u5267",
            "vod_remarks": remark,
            "vod_content": desc,
            "vod_play_from": "$$$".join(play_from),
            "vod_play_url": "$$$".join(play_url),
            "vod_year": "",
            "vod_area": "",
            "vod_actor": "",
            "vod_director": "",
        }
        return {"list": [vod]}

    def _detail_chigua(self, url):
        if not url.startswith("http"):
            url = self.host.rstrip('/') + (url if url.startswith('/') else '/' + url)
        try:
            html = self._get(url.replace(self.host, "")) if url.startswith(self.host) else ""
            if not html:
                r = rq.get(url, headers={"User-Agent": UA, "Referer": self.host + "/"},
                           timeout=TIMEOUT, verify=False)
                html = r.text if r.status_code == 200 else ""
        except Exception:
            return {"list": []}
        if not html:
            return {"list": []}

        title = ""
        m = re.search(r'<title>(.*?)</title>', html)
        if m:
            title = _clean(m.group(1).split('|')[0])

        players = re.findall(
            r'<div class="post-video-player"[^>]*data-player-key="([^"]*)"[^>]*data-src="([^"]*)"', html)
        if not players:
            players = re.findall(r'data-src="(https?://[^"]+\.m3u8[^"]*)"', html)
            players = [(f"线路{i+1}", u) for i, u in enumerate(players)]

        play = "#".join([f"{k}${v.replace('&amp;', '&')}" for k, v in players]) if players else ""

        video = {
            "vod_id": url,
            "vod_name": title or "\u5403\u74dc",
            "vod_pic": "",
            "vod_remarks": "",
            "vod_content": title,
            "type_name": "\u9ec4\u679c\u5403\u74dc",
            "vod_play_from": "\u9ec4\u679c\u5403\u74dc",
            "vod_play_url": play or f"正片${url}",
            "vod_year": "", "vod_area": "", "vod_actor": "", "vod_director": "",
        }
        return {"list": [video]}

    @staticmethod
    def _ep_sort(path):
        m = re.search(r'/ep-(\d+)/', path or "")
        return int(m.group(1)) if m else 0

    # ---------- \u64ad\u653e ----------
    def playerContent(self, flag, id, vipFlags=None, vipIds=None):
        """\u5bf9\u9f50\u7cbe\u7b80\u7248 + \u517c\u5bb9\u7eaf\u6570\u5b57 id / \u5355\u96c6 AI\u9b54\u6539\u3002"""
        key = str(id or "").strip()
        if not key:
            return {"url": ""}

        # \u5df2\u7ecf\u662f\u76f4\u94fe
        if key.startswith("http"):
            url = key.replace("&amp;", "&").replace("\\u0026", "&")
            return {"parse": 0, "url": url, "header": {"User-Agent": UA}}

        # \u7eaf\u6570\u5b57 \u2192 \u5f53\u6210\u89c6\u9891 id\uff0c\u8d70 /video/{id}/
        if key.isdigit():
            key = f"/video/{key}/"
        elif not key.startswith("/"):
            key = "/" + key
        # \u6709\u4eba\u4f20 video/123 \u6216 video/123/ep-1 \u6ca1\u6709\u524d\u5bfc /
        if key.startswith("video/"):
            key = "/" + key

        html = self._get(key, ref="/")
        # \u4e3b\u7ad9\u5931\u8d25\u65f6\u6362\u955c\u50cf
        if not html or "videoInitialData" not in html:
            for h in HOSTS:
                try:
                    u = h.rstrip('/') + key
                    r = rq.get(u, headers={"User-Agent": UA, "Referer": h.rstrip('/') + "/"},
                               timeout=TIMEOUT, verify=False, allow_redirects=True)
                    if r.status_code == 200 and r.text and "videoInitialData" in r.text:
                        html = r.text
                        break
                except Exception:
                    continue

        if not html:
            return {"url": ""}

        # \u63d0\u53d6 videoInitialData
        m = re.search(
            r'<script id="videoInitialData" type="application/json">(.*?)</script>',
            html, re.S)
        if not m:
            m2 = re.search(r'data-play-src="(https?://[^"]+)"', html)
            if m2:
                return {"parse": 0, "url": m2.group(1).replace("&amp;", "&"),
                        "header": {"User-Agent": UA}}
            return {"url": ""}

        try:
            data = json.loads(m.group(1))
        except Exception:
            return {"url": ""}

        url = data.get("videoSrc") or ""
        if not url:
            eps = data.get("epPlaySrcs") or {}
            # \u4ece\u5f53\u524d\u8def\u5f84\u63a8\u65ad\u96c6\u6570
            ep_from_path = None
            pm = re.search(r'/ep-(\d+)/', key)
            if pm:
                ep_from_path = pm.group(1)
            ep = data.get("ep")
            if ep_from_path and str(ep_from_path) in eps:
                url = eps[str(ep_from_path)]
            elif ep is not None and str(ep) in eps:
                url = eps[str(ep)]
            else:
                for v in eps.values():
                    if v:
                        url = v
                        break

        url = str(url or "").replace("\\u0026", "&").replace("&amp;", "&").strip()
        if url.startswith("http"):
            return {"parse": 0, "url": url, "header": {"User-Agent": UA}}
        return {"url": ""}

    # ---------- \u672c\u5730\u4ee3\u7406\uff08TVBox \u8c03\u7528\uff09 ----------
    def localProxy(self, param):
        try:
            if isinstance(param, dict):
                if param.get("type") == "pic":
                    return self._proxy_pic(param)
                url = param.get("url") or param.get("u") or ""
            else:
                url = self._resolve_img_param(param)
            if not url:
                return None
            host = self._safe_host()
            headers = {"User-Agent": UA, "Referer": host + "/", "Accept": "image/*"}
            # \u5171\u4eab\u52a0\u901f\u901a\u9053\uff1aSession \u590d\u7528 + \u7f13\u5b58 + \u89e3\u5bc6\uff08\u660e\u6587\u56fe\u81ea\u52a8\u8df3\u8fc7\uff09
            if _shared_fetch_img is not None:
                try:
                    mime, data = _shared_fetch_img(url, headers=headers,
                                                   decrypt=_decrypt_img, timeout=15)
                    if data and len(data) > 50:
                        return [200, mime, data]
                    return None
                except Exception:
                    pass
            rr = rq.get(url, headers=headers, timeout=15, verify=False, allow_redirects=True)
            if rr.status_code == 200 and rr.content and len(rr.content) > 50:
                data = _decrypt_img(rr.content)
                ctype = _detect_mime(data)
                return [200, ctype, data]
        except Exception:
            pass
        return None

    def _proxy_pic(self, params):
        try:
            raw = params.get("url") or ""
            if not raw.startswith("http"):
                try:
                    raw = base64.b64decode(raw + "==").decode("utf-8", "ignore")
                except Exception:
                    pass
            if not raw.startswith("http"):
                return None
            host = self._safe_host()
            headers = {"User-Agent": UA, "Referer": host + "/"}
            if _shared_fetch_img is not None:
                try:
                    mime, data = _shared_fetch_img(raw, headers=headers,
                                                   decrypt=_decrypt_img, timeout=15)
                    if data and len(data) > 50:
                        return [200, mime, data]
                    return None
                except Exception:
                    pass
            data = rq.get(raw, headers=headers, timeout=15, verify=False).content
            data = _decrypt_img(data)
            mime = _detect_mime(data)
            return [200, mime, data]
        except Exception:
            return None

    @staticmethod
    def _resolve_img_param(param):
        if not param:
            return ""
        p = str(param).strip()
        p = re.sub(r'^https?://127\.0\.0\.1:\d+/proxy\?', '', p)
        p = re.sub(r'^proxy\?', '', p)
        if "url=" in p:
            q = urllib.parse.parse_qs(p)
            cand = q.get("url", [""])[0]
            if cand:
                p = cand
        try:
            p = urllib.parse.unquote(p)
        except Exception:
            pass
        if not p.startswith("http"):
            try:
                dec = base64.b64decode(p + "==").decode("utf-8", "ignore")
                if dec.startswith("http"):
                    p = dec
            except Exception:
                pass
        return p if p.startswith("http") else ""

    # ---------- \u5217\u8868\u89e3\u6790 ----------
    def _parse_list(self, html, mode="drama"):
        if not html or len(html) < 150:
            return []
        if BeautifulSoup is not None:
            try:
                return self._parse_bs4(html, mode)
            except Exception:
                pass
        return self._parse_regex(html)

    def _parse_bs4(self, html, mode):
        videos, seen = [], set()
        doc = BeautifulSoup(html, "lxml") if "lxml" in str(BeautifulSoup) else BeautifulSoup(html, "html.parser")

        if mode == "drama" or mode == "search":
            # \u901a\u7528\u5361\u7247
            for card in doc.select("div.hg-drama-card"):
                a = card.find("a", href=True)
                if not a:
                    continue
                href = a.get("href", "")
                m = re.search(r"/detail/(\d+)", href)
                if not m:
                    continue
                vid = m.group(1)
                if vid in seen:
                    continue
                seen.add(vid)
                img = card.find("img")
                pic = ""
                if img:
                    pic = img.get("data-src") or img.get("src") or ""
                title = ""
                if img:
                    title = img.get("alt") or ""
                if not title:
                    t = card.select_one(".hg-drama-card__title a, .hg-drama-card__title, h2, h3")
                    title = t.get_text(strip=True) if t else ""
                if not title:
                    title = card.get("data-track-title") or ""
                parts = []
                for sel in [".hg-drama-card__score", ".hg-drama-card__episode",
                            ".hg-drama-card__badge"]:
                    el = card.select_one(sel)
                    if el:
                        parts.append(el.get_text(strip=True))
                remark = " ".join(parts).strip() or "\u5728\u7ebf\u89c2\u770b"
                if title:
                    videos.append({
                        "vod_id": vid,
                        "vod_name": _clean(title),
                        "vod_pic": self._wrap_pic(pic),
                        "vod_remarks": remark,
                    })

            # search \u8865\u5145
            if mode == "search" and not videos:
                for a in doc.find_all("a", href=re.compile(r"/detail/\d+")):
                    m = re.search(r"/detail/(\d+)", a.get("href", ""))
                    if not m or m.group(1) in seen:
                        continue
                    seen.add(m.group(1))
                    img = a.find("img")
                    if not img:
                        continue
                    pic = img.get("data-src") or img.get("src") or ""
                    title = img.get("alt") or img.get("title") or a.get("title") or ""
                    if not title:
                        t = a.find(class_=re.compile("title"))
                        title = t.get_text(strip=True) if t else ""
                    remark = ""
                    for cls in ["episode", "score"]:
                        s = a.find(class_=re.compile(cls))
                        if s:
                            remark = s.get_text(strip=True)
                            break
                    if title:
                        videos.append({
                            "vod_id": m.group(1),
                            "vod_name": _clean(title),
                            "vod_pic": self._wrap_pic(pic),
                            "vod_remarks": remark or "\u5728\u7ebf\u89c2\u770b",
                        })

        elif mode == "rank":
            for item in doc.select("div.hg-rank-item"):
                a = item.find("a", href=True, class_=re.compile("cover")) or item.find("a", href=True)
                if not a:
                    continue
                href = a.get("href", "")
                m = re.search(r"/detail/(\d+)", href)
                vid = m.group(1) if m else href
                if vid in seen:
                    continue
                seen.add(vid)
                img = item.find("img")
                pic = (img.get("data-src") or img.get("src") or "") if img else ""
                title = item.get("data-track-title") or (img.get("alt") if img else "") or ""
                if not title:
                    t = item.select_one(".hg-rank-item__title, h2")
                    title = t.get_text(strip=True) if t else ""
                heat = item.select_one(".hg-rank-item__heat-value")
                remark = ("\U0001f525" + heat.get_text(strip=True)) if heat else ""
                if title:
                    videos.append({
                        "vod_id": vid,
                        "vod_name": _clean(title),
                        "vod_pic": self._wrap_pic(pic),
                        "vod_remarks": remark,
                    })

        elif mode == "topic":
            for card in doc.select("a.hg-topic-card"):
                href = card.get("href", "")
                slug = href.strip("/").split("/")[-1]
                img = card.find("img")
                pic = (img.get("data-src") or img.get("src") or "") if img else ""
                t = card.select_one(".hg-topic-card__title, h2")
                title = t.get_text(strip=True) if t else (img.get("alt") if img else "")
                meta = card.select_one(".hg-topic-card__meta")
                remark = meta.get_text(strip=True) if meta else ""
                if title:
                    videos.append({
                        "vod_id": "dir_topic_" + slug,
                        "vod_name": _clean(title),
                        "vod_pic": self._wrap_pic(pic),
                        "vod_remarks": remark,
                        "vod_tag": "folder",
                    })

        elif mode == "post":
            for card in doc.select("a.hg-post-card"):
                href = card.get("href", "")
                if not href:
                    continue
                img = card.find("img")
                pic = (img.get("data-src") or img.get("src") or "") if img else ""
                h3 = card.find("h3")
                title = h3.get_text(strip=True) if h3 else ""
                date = card.select_one(".hg-post-card__date")
                cat = card.select_one(".hg-post-card__cat")
                parts = [s.get_text(strip=True) for s in (date, cat) if s]
                videos.append({
                    "vod_id": href if href.startswith("http") else self.host + href,
                    "vod_name": _clean(title),
                    "vod_pic": self._wrap_pic(pic),
                    "vod_remarks": " | ".join(parts),
                })

        return videos

    def _parse_regex(self, html):
        """\u65e0 BS4 \u65f6\u7684\u6b63\u5219\u515c\u5e95\uff08\u4e0e\u7b2c\u4e00\u7248\u517c\u5bb9\uff09"""
        result, seen = [], set()
        for block in re.split(r'<div class="hg-drama-card"', html)[1:]:
            m = re.search(r'href="(/detail/(\d+)/)"', block)
            if not m:
                continue
            vid = m.group(2)
            if vid in seen:
                continue
            pic = ""
            pm = re.search(r'data-src="([^"]+)"', block)
            if pm:
                pic = htmllib.unescape(pm.group(1)).strip()
            if not pic:
                pm = re.search(r'<img[^>]*src="([^"]+)"', block)
                if pm:
                    pic = htmllib.unescape(pm.group(1)).strip()
            title = ""
            tm = re.search(
                r'class="[^"]*hg-drama-card__title[^"]*"[^>]*>\s*<a[^>]*>(.*?)</a>',
                block, re.S)
            if tm:
                title = _clean(tm.group(1))
            if not title:
                tm = re.search(r'<img[^>]*alt="([^"]+)"', block)
                if tm:
                    title = _clean(tm.group(1))
            parts = []
            sm = re.search(r'class="hg-drama-card__score">([^<]+)<', block)
            if sm:
                parts.append(_clean(sm.group(1)))
            em = re.search(r'class="hg-drama-card__episode">([^<]+)<', block)
            if em:
                parts.append(_clean(em.group(1)))
            remark = " ".join(parts).strip() or "\u5728\u7ebf\u89c2\u770b"
            if not title:
                continue
            seen.add(vid)
            result.append({
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": self._wrap_pic(pic),
                "vod_remarks": remark,
            })
        return result
