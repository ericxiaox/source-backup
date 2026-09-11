# -*- coding: utf-8 -*-
# 51AW \u7ad9\u6e90\uff08WordPress \u578b pbody \u58f3 \u00b7 HTML \u76f4\u6293\u7248\uff09
# \u53d1\u5e03\u94fe: 51aw34.com \u7b49\u5165\u53e3\u57df\u4e3a b64 \u58f3\u843d\u5730\u9875\uff08Base64.decode \u6574\u9875\uff09\uff0c\u89e3\u7801\u540e
#         footer \u76f4\u94fe\u73b0\u5f79\u5185\u5bb9\u7ad9\uff082026-09-08 \u5b9e\u6d4b = awcg48.com\uff0cCloudflare\uff09
# \u7ed3\u6784: \u5206\u7c7b /category/{slug}/\uff08\u7ffb\u9875 page/{n}/ \u6216 /{n}/ \u53cc\u5f62\u6001\u81ea\u9002\u5e94\uff09
#       \u5217\u8868 <article><a href><h2>\u6807\u9898</h2>\uff1b\u641c\u7d22 /search/{kw}/
#       \u8be6\u60c5 dplayer config JSON\uff08\/ \u8f6c\u4e49\u8fd8\u539f\uff09\uff0c\u517c\u5bb9\u88f8 m3u8 \u515c\u5e95
# \u5c01\u9762: \u5217\u8868 <article> \u5185**\u6ca1\u6709 <img>**\uff0c\u5c01\u9762\u7531 post-card \u7684
#       <script>loadBannerDirect('URL', ...)</script> \u9996\u53c2\u6ce8\u5165 \u2192 \u5fc5\u987b\u62bd\u811a\u672c\u53c2\u6570\u3002
#       \u56fe\u5e8a pic.ndhixj.cn \u662f\u300c\u9ed1\u6599\u7cfb\u300dAES-CBC \u52a0\u5bc6\u56fe\uff08\u4e0e 51\u5403\u74dc/91\u7206\u6599\u540c key\uff0c
#       magic \u975e FFD8FF\uff09\uff0c\u88f8 URL \u7ed9 App \u4f1a\u89e3\u7801\u5931\u8d25\u663e\u793a\u7a7a\u56fe \u2192 \u5fc5\u987b\u8d70 localProxy \u89e3\u5bc6\u3002
# \u5206\u7c7b\u8868 b64 \u843d\u76d8\uff08\u89c4\u907f gitee 451 \u8bcd\u6c47\u626b\u63cf\uff09\uff0c\u8fd0\u884c\u65f6\u89e3\u7801
import json
import re
import sys
import os
import html as _html
import base64
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
        probe_first = None
        parse_ext = None

# imgfetch.py\uff08source \u6839\uff09\uff1a\u5c01\u9762\u4ee3\u7406\u5171\u4eab\u901a\u9053\uff08Session \u590d\u7528 + LRU + magic \u9884\u68c0 + \u89e3\u5bc6\u515c\u5e95\uff09
try:
    from imgfetch import fetch_img as _shared_fetch_img
except Exception:
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from imgfetch import fetch_img as _shared_fetch_img
    except Exception:
        _shared_fetch_img = None

# \u56fe\u5e8a\u89e3\u5bc6 key\uff08\u300c\u9ed1\u6599\u7cfb\u300d\u5171\u7528\uff1a51\u5403\u74dc aesimg / 91\u7206\u6599 _img_fetch / \u672c\u7ad9 pic.ndhixj.cn
# 2026-09-11 \u5b9e\u6d4b\u540c key \u2014\u2014 \u4e09\u4e2a\u7ad9\u5b9e\u6d4b\u89e3\u5bc6\u540e magic \u5747\u4e3a FFD8FF/89504E47/GIF8\uff09
_AES_KEY = b'f5d965df75336270'
_AES_IV = b'97b60394abc2fbe1'


def _aesimg(raw):
    """\u52a0\u5bc6\u56fe \u2192 \u660e\u6587\u56fe\uff1b\u5931\u8d25\u539f\u6837\u8fd4\u56de\uff08\u7531\u8c03\u7528\u65b9\u6309 magic \u5224\u5b9a\uff09"""
    try:
        from Crypto.Cipher import AES
        return AES.new(_AES_KEY, AES.MODE_CBC, _AES_IV).decrypt(raw)
    except Exception:
        return raw


# explorer.py\uff08source \u6839\uff09\uff1a\u6c60\u5168\u6302\u65f6\u4ece\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\u6d3b\u57df\uff08\u4e0e hostresolver \u540c\u76ee\u5f55\uff09
try:
    from explorer import explore_hosts
except Exception:
    explore_hosts = None

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# \u5206\u7c7b\u8868 {slug: \u540d\u79f0}\uff08b64 of UTF-8 JSON\uff0c\u6765\u6e90\uff1a\u6e90\u6ce8\u91ca sortUrl\uff0c2026-09-08 \u91c7\u96c6\uff09
def _b64d(s):
    return base64.b64decode(s + '=' * (-len(s) % 4)).decode('utf-8')


# \u771f\u5b9e\u5206\u7c7b\u8868\uff08json: {"slug":"\u540d\u79f0", ...}\uff09
_CATS = json.loads(_b64d(
    'eyJob21lIjoi6aaW6aG1IiwianJyZyI6IuS7iuaXpeWQg+eTnCIsInF3cnMiOiLlhajnvZHng63m'
    'kJwiLCJhd2NnIjoi5pqX572R54iG5paZIiwiZHl3aCI6Iuaal+e9kee9kee6oiIsIm1yZHMiOiLm'
    'r4/ml6XlpKfotZsiLCJhaWRqIjoiQUnnn63liaciLCJmY2xsIjoi5pqX572R5Y+N5beuIiwieHlj'
    'ZyI6Iuaal+e9keagoeWbrSIsImFud2FuZ2x1YW5sdW4iOiLmmpfnvZHkubHkvKYiLCJzeHpxIjoi'
    '5pqX572R6KeG6aKRIiwiaHdhdyI6Iua1t+WkluWkp+eJhyIsImF3ZHoiOiLmmpfnvZFBVuino+iv'
    'tCIsImF3bHEiOiLmmpfnvZHnjI7lpYciLCJ0YW5odWEiOiLmjqLoirHlgbfmi40iLCJtZWlyaS10'
    'b3AiOiLmr4/ml6V0b3AiLCJjdW56aGkiOiLlr7jmraLmjJHmiJgiLCJkbXR0Ijoi5Yqo5ryr5aSp'
    '5aCCIiwiZGFyay1oaXN0b3J5Ijoi5pqX5Y+y5qGj5qGIIiwic2piIjoi5LiW55WM5p2vIn0='
))

# \u5217\u8868\u6761\u76ee: <article ...><a href="...">...<h2>\u6807\u9898</h2>...
_RE_ARTICLE = re.compile(r'<article[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</article>', re.S)
_RE_H2 = re.compile(r'<h2[^>]*>(.*?)</h2>', re.S)
# \u56fe\u5e8a\uff082026-09-11 \u5b9e\u6d4b\uff09\uff1a\u7ad9\u65b9\u9875\u9762\u4e0a\u7684\u56fe\u7247 URL host \u65f6\u5e38\u5199\u9519
#   \u2014\u2014 \u5217\u8868 loadBannerDirect \u7528\u7684\u662f\u7edd\u5bf9\u5730\u5740 pic.ndhixj.cn\uff08\u53ef\u7528\uff09\uff1b
#   \u2014\u2014 \u8be6\u60c5\u9875\u6b63\u6587\u5374\u662f https://www.cgddz.cc//upload_01/...\uff08\u5df2\u6b7b\uff09\u6216 /upload_01/...\uff08\u76f8\u5bf9\uff09\u3002
# \u5b9e\u6d4b\u540c\u4e00 /upload_01/ \u8def\u5f84\u5728 pic.ndhixj.cn \u4e0a\u90fd\u80fd 200\uff0c\u6545\u7edf\u4e00\u6309 path \u5f52\u4e00\u5230\u56fe\u5e8a\u3002
_PIC_BED = 'https://pic.ndhixj.cn'
_BED_PATHS = ('/upload_01/', '/hc237/')

# \u5c01\u9762\uff08\u6309\u4f18\u5148\u7ea7\uff09\uff1a
#   \u2460 post-card \u5185\u8054\u811a\u672c loadBannerDirect('URL', ...) \u2014\u2014 \u672c\u7ad9\u5217\u8868\u5c01\u9762**\u53ea**\u6709\u8fd9\u4e00\u5904\uff1b
#   \u2461 \u61d2\u52a0\u8f7d data-src\uff08\u8be6\u60c5\u9875/\u5176\u5b83\u6a21\u677f\uff09\uff1b\u2462 <img src> \u515c\u5e95\u3002
#   \u4e09\u8005\u90fd\u5254\u9664\u7edf\u8ba1\u811a\u672c / \u4e3b\u9898\u56fe\u6807 / \u5e7f\u544a\u4f4d\u56fe\uff08\u5e7f\u544a\u56fe\u5f53\u5c01\u9762\u4f1a\u663e\u793a\u300c\u540c\u57ce\u7ea6\u70ae\u300d\u4e4b\u7c7b\uff09
_RE_BANNER = re.compile(r"loadBannerDirect\(\s*'([^']+)'", re.I)
_RE_IMG_LAZY = re.compile(r'data-src="([^"]+)"', re.I)
_RE_IMG_ANY = re.compile(r'<img[^>]*?src="([^"]+)"', re.I)
_RE_IMG_TAG = re.compile(r'<img[^>]*>', re.I)
_IMG_SKIP = ('mc.yandex', '/usr/themes/', '/usr/plugins/', 'data:image')
_AD_MARK = re.compile(r'(?i)data-ad_|rel="sponsored|sponsored nofollow|/usr/plugins/tbxw/')
# dplayer config JSON\uff08\u5355\u5f15\u53f7\u5305\u88f9\uff09\u4e0e\u88f8 m3u8 \u515c\u5e95
_RE_CONFIG = re.compile(r"config='(\{.*?\})'", re.S)
_RE_M3U8 = re.compile(r'https?://[^"\'\\\s]+\.m3u8[^"\'\\\s]*')
_RE_NEXT = re.compile('class="page-navigator".*?href="([^"]+)"[^>]*>[^<]*\u4e0b\u4e00\u9875', re.S)


# \u2500\u2500 \u81ea\u8bca\u65ad\uff08\u4e34\u65f6\u6392\u969c\u7528\uff0c2026-09-11\uff09\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# \u76ee\u7684\uff1aApp \u7aef\u53d6\u4e0d\u5230\u65e5\u5fd7\uff0c\u628a\u300c\u53d6\u57df\u5168\u8fc7\u7a0b\u300d\u76f4\u63a5\u644a\u6210 App \u91cc\u80fd\u770b\u89c1\u7684\u6587\u5b57\u3002
# \u8bbe\u8ba1\uff1a\u5b8c\u5168\u81ea\u5305\u542b\u2014\u2014\u6700\u9700\u8981\u6392\u67e5\u7684\u573a\u666f\u6070\u6070\u662f\u300c\u540c\u7ea7\u6a21\u5757 hostresolver/explorer \u6ca1\u52a0\u8f7d\u5230\u300d\uff0c
#      \u6240\u4ee5\u672c\u51fd\u6570\u4e0d\u4f9d\u8d56\u5b83\u4eec\uff0cimport \u5931\u8d25\u4e5f\u7167\u6837\u8f93\u51fa\u3002
DIAG_TID = '__diag__'


def _diag_lines(sp, key=''):
    """\u628a\u53d6\u57df\u94fe\u8def\u644a\u6210\u53ef\u8bfb\u6587\u672c\u884c\uff08\u5728\u300c\u26a0\u8bca\u65ad\u300d\u5206\u7c7b\u91cc\u9010\u6761\u663e\u793a\uff09"""
    out = []
    g = globals()

    def add(k, v):
        out.append('%s: %s' % (k, v))

    add('\u6700\u7ec8\u9009\u5b9a host', getattr(sp, 'host', '') or '(\u7a7a\u2605\u5730\u5740\u6ca1\u89e3\u6790\u51fa\u6765)')
    add('hostresolver \u6a21\u5757', '\u5df2\u52a0\u8f7d' if g.get('resolve_host') else '\u2605\u672a\u52a0\u8f7d(\u540c\u7ea7\u6a21\u5757\u6ca1\u8fdb\u8bbe\u5907)')
    add('explorer \u6a21\u5757', '\u5df2\u52a0\u8f7d' if g.get('explore_hosts') else '\u672a\u52a0\u8f7d')
    ext = getattr(sp, '_ext', {}) or {}
    add('ext.publish', ext.get('publish') or '(\u7a7a\uff0c\u7528\u5185\u7f6e)')
    add('ext.hosts', ','.join(ext.get('hosts') or []) or '(\u7a7a)')
    if not key:
        try:
            key = sp.getName()
        except Exception:
            key = ''
    add('\u672c\u6587\u4ef6\u58f0\u660e\u7684\u7ad9\u540d', key or '(\u672a\u77e5)')
    _rq = g.get('requests') or g.get('rq')
    u = getattr(sp, 'host', '') or ''
    if u and _rq is not None:
        hh = dict(getattr(sp, 'headers', None) or {})
        if not hh.get('User-Agent'):
            hh['User-Agent'] = g.get('_UA') or g.get('UA') or 'Mozilla/5.0'
        try:
            r = _rq.get(u.rstrip('/') + '/', headers=hh,
                        proxies=getattr(sp, 'proxies', {}) or {}, timeout=6, verify=False)
            t = r.text or ''
            add('\u5b9e\u6d4b\u8be5 host', 'HTTP %s / %dB / \u542b\u7ad9\u540d:%s'
                % (r.status_code, len(t), ('\u662f' if key in t else '\u5426\u2605') if key else '\u672a\u5224\u5b9a'))
        except Exception as e:
            add('\u5b9e\u6d4b\u8be5 host', '\u2605\u8fde\u4e0d\u4e0a: %s' % str(e)[:60])
    else:
        add('\u5b9e\u6d4b\u8be5 host', '(\u8df3\u8fc7\uff1ahost \u4e3a\u7a7a\u6216 requests \u4e0d\u53ef\u7528)')
    try:
        import hostresolver as _hr
        tr = _hr.last_trace()
        if tr:
            out.append('\u2500\u2500 \u9009\u7ad9\u8fc7\u7a0b \u2500\u2500')
            out += tr[:30]
    except Exception as e:
        out.append('\u2605 \u8bfb\u9009\u7ad9\u8fc7\u7a0b\u5931\u8d25: %s' % str(e)[:60])
    return out


class Spider(BaseSpider):

    # \u5165\u53e3\u843d\u5730\u9875\uff08b64 \u58f3\uff0c\u89e3\u7801\u540e\u542b\u73b0\u5f79\u5185\u5bb9\u7ad9\u76f4\u94fe\uff1b\u968f\u54c1\u724c\u6362\u57df\u5373\u66f4\u65b0\uff09
    PUBLISH_PAGE = 'https://51aw34.com/'
    # \u5185\u7f6e\u5019\u9009\uff082026-09-08 \u5b9e\u6d4b\uff09\uff1a\u58f3\u9875 JS \u6cdb\u89e3\u6790\u5907\u7ebf {word}.haqwhuwn.cc \u4efb\u610f\u8bcd\u53ef\u7528\uff0c
    # awcg48.com \u4e3b\u7ebf\u65f6\u6d3b\u65f6\u6b7b\uff08App \u7aef\u66fe\u5168\u6302=\u96f6\u6570\u636e\uff09\uff0c\u6545\u6cdb\u89e3\u6790\u7ebf\u6392\u524d
    BUILTIN_HOSTS = [
        'https://main.haqwhuwn.cc',
        'https://apple.haqwhuwn.cc',
        'https://being.djvvxecgc.cc',
        'https://awcg48.com',
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
        try:
            self._diag = _diag_lines(self, '51\u6697\u7f51')
        except Exception:
            self._diag = []
        self.headers.update({'Origin': self.host, 'Referer': self.host + '/'})
        print(f'使用站点: {self.host}')

    def getName(self):
        return "51\u6697\u7f51"

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
            # \u5185\u5bb9\u7ad9\u8eab\u4efd\uff1aWordPress \u578b\u6587\u7ae0\u6d41\uff08article \u6807\u7b7e\uff09+ \u7ad9\u540d\u8bcd
            t = text or ''
            return ('<article' in t) and ('\u6697\u7f51' in t)

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
            for h in cands:
                try:
                    r = requests.get(h.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=8, verify=False)
                    if r.status_code == 200 and _validate(h, r.text):
                        return h.rstrip('/')
                except Exception:
                    continue
        # \u7ec8\u6781\u515c\u5e95\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\uff08\u8df3\u8f6c\u58f3/\u95e8\u6237/\u6cdb\u89e3\u6790\u8ddf\u968f + \u7ad9\u540d\u8eab\u4efd\u9a8c\u8bc1\uff09
        if explore_hosts:
            try:
                def _probe(u):
                    r = requests.get(u.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=8, verify=False)
                    t = r.text or ''
                    return r.status_code == 200 and '<article' in t and '\u6697\u7f51' in t
                hs = explore_hosts(['51aw', '\u6697\u7f51'], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        # \u5168\u8d25\uff1a\u663e\u5f0f\u8fd4\u56de\u7a7a\uff08\u63a5\u53e3\u5c42\u79d2\u7a7a\uff0c\u4e0d\u518d\u56de\u9000\u6b7b\u57df\u9759\u9ed8\u7a7a\u8f6c\uff09
        return ''

    def _get(self, path):
        url = path if path.startswith('http') else self.host + path
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False)

    # \u2500\u2500 \u5c01\u9762\u4ee3\u7406\uff08\u56fe\u5e8a\u4e3a AES \u52a0\u5bc6\u56fe\uff0c\u987b\u89e3\u5bc6\u540e\u518d\u56de\u7ed9 App\uff09\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    def e64(self, s):
        try:
            return base64.b64encode((s or '').encode('utf-8')).decode('utf-8')
        except Exception:
            return ''

    def d64(self, s):
        s = (s or '').replace(' ', '+')
        try:
            return base64.b64decode(s + '=' * (-len(s) % 4)).decode('utf-8')
        except Exception:
            return ''

    def _fetch_once(self, url):
        """\u53d6\u56fe + \u6309\u9700\u89e3\u5bc6 \u2192 (mime, bytes)\u3002\u660e\u6587\u56fe\u76f4\u63a5\u653e\u884c\uff0c\u975e\u660e\u6587\u6309\u9ed1\u6599\u7cfb key \u89e3\u5bc6\u3002"""
        if _shared_fetch_img is not None:
            return _shared_fetch_img(url, headers=self.headers, decrypt=_aesimg,
                                     timeout=15, proxies=self.proxies or None)
        try:
            r = requests.get(url, headers=self.headers, proxies=self.proxies or None,
                             timeout=10, verify=False)
            raw = r.content if r.status_code == 200 else b''
        except Exception:
            raw = b''
        if not raw:
            return None, b''
        for b in (raw, _aesimg(raw)):
            if b[:3] == b'\xff\xd8\xff':
                return 'image/jpeg', b
            if b[:8] == b'\x89PNG\r\n\x1a\n':
                return 'image/png', b
            if b[:4] == b'GIF8':
                return 'image/gif', b
            if b[:4] == b'RIFF' and b[8:12] == b'WEBP':
                return 'image/webp', b
        return None, b''

    def _img_fetch(self, url):
        """\u53d6\u56fe\uff1b\u7ad9\u65b9 host \u5199\u9519/\u5df2\u6b7b\u65f6\u6309 path \u6362\u56fe\u5e8a\u518d\u8bd5\u4e00\u6b21\u3002"""
        mime, data = self._fetch_once(url)
        if not data:
            mm = re.match(r'^https?://[^/]+(/.*)$', url)
            if mm and _PIC_BED not in url:
                mime, data = self._fetch_once(_PIC_BED + mm.group(1))
        return mime, data

    def localProxy(self, param):
        try:
            if param.get('type') == 'awimg':
                url = self._to_bed(self.d64(param.get('url')))
                if url.startswith('//'):
                    url = 'https:' + url
                if url.startswith('/'):
                    url = self.host + url
                mime, data = self._img_fetch(url)
                if data:
                    return [200, mime or 'image/jpeg', data]
        except Exception:
            pass
        return [404, 'text/plain', b'']

    @staticmethod
    def _to_bed(u):
        """\u56fe\u7247 URL \u5f52\u4e00\u5230\u56fe\u5e8a\uff1a\u7ad9\u65b9\u9875\u9762\u91cc\u7684 host \u5e38\u5199\u9519\uff08\u5df2\u6b7b\u57df/\u76f8\u5bf9\u8def\u5f84\uff09\uff0c
        \u53ea\u8981 path \u843d\u5728\u5df2\u77e5\u56fe\u5e8a\u76ee\u5f55\uff08/upload_01/\u3001/hc237/\uff09\u5c31\u6362\u6210 _PIC_BED \u7684 host\u3002"""
        if not u:
            return ''
        if u.startswith('//'):
            u = 'https:' + u
        if u.startswith('/'):
            return _PIC_BED + u if any(p in u for p in _BED_PATHS) else u
        mm = re.match(r'^https?://[^/]+(/.*)$', u)
        if mm and _PIC_BED not in u and any(p in mm.group(1) for p in _BED_PATHS):
            return _PIC_BED + mm.group(1)
        return u

    def _pic(self, u):
        """\u5c01\u9762\u7edf\u4e00\u5305\u6210\u4ee3\u7406 URL\uff08\u4ee3\u7406\u5185\u505a magic \u9884\u68c0 + \u89e3\u5bc6 + LRU \u7f13\u5b58\uff09"""
        u = self._to_bed(u)
        if not u:
            return ''
        if u.startswith('/'):
            u = self.host + u
        return f'{self.getProxyUrl()}&url={self.e64(u)}&type=awimg'

    @staticmethod
    def _pick_pic(block):
        """\u62bd\u5c01\u9762\u88f8 URL\uff08loadBannerDirect \u811a\u672c \u2192 img \u6807\u7b7e data-src/src\uff09\uff0c
        \u81ea\u52a8\u8df3\u8fc7\u4e3b\u9898\u56fe\u6807\u4e0e\u5e7f\u544a\u4f4d\u56fe\u3002\u8fd4\u56de\u88f8 URL\uff0c\u9700\u518d\u7ecf _pic() \u5305\u6210\u4ee3\u7406 URL\u3002"""
        block = block or ''
        for u in _RE_BANNER.findall(block):
            if u and not any(s in u for s in _IMG_SKIP):
                return _html.unescape(u).strip()
        # \u9010\u4e2a <img> \u5224\u5b9a\uff1a\u81ea\u8eab\u6216\u5176\u524d 260 \u5b57\u4e0a\u4e0b\u6587\u5e26\u5e7f\u544a\u6807\u8bb0 \u2192 \u8df3\u8fc7
        for m in _RE_IMG_TAG.finditer(block):
            tag = m.group(0)
            near = block[max(0, m.start() - 260):m.start()]
            if _AD_MARK.search(tag) or _AD_MARK.search(near):
                continue
            for pat in (_RE_IMG_LAZY, _RE_IMG_ANY):
                mm = pat.search(tag)
                if mm and not any(s in mm.group(1) for s in _IMG_SKIP):
                    return _html.unescape(mm.group(1)).strip()
        # \u515c\u5e95\uff1a\u4e0d\u8ba1\u5e7f\u544a\u6807\u8bb0\u7684\u5bbd\u677e\u626b\u63cf\uff08\u539f\u884c\u4e3a\uff09
        for pat in (_RE_IMG_LAZY, _RE_IMG_ANY):
            for u in pat.findall(block):
                if u and not any(s in u for s in _IMG_SKIP):
                    return _html.unescape(u).strip()
        return ''

    def _parse_articles(self, html_text):
        out = []
        seen = set()
        for m in _RE_ARTICLE.finditer(html_text):
            link, blk = m.group(1), m.group(2)
            if not link or not (link.startswith('http') or link.startswith('/')):
                continue
            if link in seen:
                continue
            seen.add(link)
            t = _RE_H2.search(blk)
            title = _html.unescape(re.sub(r'<[^>]+>', '', t.group(1))).strip() if t else ''
            if not title:
                continue
            out.append({
                'vod_id': link,
                'vod_name': title,
                'vod_pic': self._pic(self._pick_pic(blk)),
                'vod_remarks': '',
            })
        return out

    def _diag_items(self):
        """\u8bca\u65ad\u884c \u2192 App \u5217\u8868\u6761\u76ee\uff08\u70b9\u300c\u26a0\u8bca\u65ad\u300d\u5206\u7c7b\u5373\u53ef\u770b\u5230\u5168\u90e8\u53d6\u57df\u8fc7\u7a0b\uff09"""
        return [{'vod_id': 'diag%d' % i, 'vod_name': '\u26a0 ' + str(x),
                 'vod_pic': '', 'vod_remarks': ''}
                for i, x in enumerate(getattr(self, '_diag', []) or [])]
    def homeContent(self, *a, **kw):
        """\u5916\u5c42\u5305\u88c5\uff1a\u539f\u5b9e\u73b0\u7ed3\u679c + \u8ffd\u52a0\u300c\u26a0\u8bca\u65ad\u300d\u5206\u7c7b\uff08\u4e34\u65f6\u6392\u969c\uff0c\u5b9a\u4f4d App \u7aef\u65e0\u5185\u5bb9\u6839\u56e0\uff09"""
        try:
            r = self._homeContent(*a, **kw)
        except Exception:
            r = {}
        try:
            if isinstance(r, dict):
                r['class'] = list(r.get('class') or []) + \
                    [{'type_id': DIAG_TID, 'type_name': '\u26a0\u8bca\u65ad'}]
        except Exception:
            pass
        return r

    def _homeContent(self, flag):

        result = {'class': [], 'list': []}
        for slug, name in _CATS.items():
            result['class'].append({'type_id': slug, 'type_name': name})
        try:
            result['list'] = self._parse_articles(self._get('/').text or '')
        except Exception:
            pass
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        if tid == DIAG_TID:
            items = self._diag_items()
            return {'page': 1, 'pagecount': 1, 'limit': len(items),
                    'total': len(items), 'list': items}
        result = {'list': []}
        if tid == 'home' or str(pg) in ('1', ''):
            paths = ['/'] if tid == 'home' else [f'/category/{tid}/']
        else:
            paths = [f'/category/{tid}/page/{pg}/', f'/category/{tid}/{pg}/']
        for p in paths:
            try:
                lst = self._parse_articles(self._get(p).text or '')
                if lst:
                    result['list'] = lst
                    break
            except Exception:
                continue
        return result

    def searchContent(self, key, quick, pg='1'):
        result = {'list': []}
        try:
            body = self._get(f'/search/{quote(key)}/').text or ''
            result['list'] = self._parse_articles(body)
        except Exception:
            pass
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    @staticmethod
    def _videos(html_text):
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
        if not vids:
            seen = set()
            for u in _RE_M3U8.findall(html_text):
                if u not in seen:
                    seen.add(u)
                    vids.append({'url': u, 'pic': ''})
        return vids

    def detailContent(self, ids):
        result = {'list': []}
        try:
            link = str(ids[0])
            body = self._get(link).text or ''
            title = ''
            m = re.search(r'<title>([^<]+)</title>', body)
            if m:
                title = _html.unescape(m.group(1)).strip()
                title = re.sub('\\s*[-|]\\s*51\u6697\u7f51\\s*$', '', title).strip()
            pic = self._pic(self._pick_pic(body))
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
                'vod_play_from': '51aw',
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
                result['url'] = vids[min(i, len(vids) - 1)]['url']
                result['header'] = {'User-Agent': _UA, 'Referer': self.host + '/'}
        except Exception:
            pass
        return result
