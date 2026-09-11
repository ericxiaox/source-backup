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


# \u2500\u2500 \u81ea\u8bca\u65ad\uff08\u4e34\u65f6\u6392\u969c\u7528\uff0c2026-09-11\uff09\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# \u76ee\u7684\uff1aApp \u7aef\u6ca1\u6709\u53ef\u53d6\u7684\u65e5\u5fd7\u5de5\u5177\uff0c\u628a\u300c\u53d6\u57df\u5168\u8fc7\u7a0b\u300d\u76f4\u63a5\u644a\u6210 App \u91cc\u80fd\u770b\u89c1\u7684\u6587\u5b57\u3002
# \u8bbe\u8ba1\uff1a\u5b8c\u5168\u81ea\u5305\u542b\u2014\u2014\u6700\u9700\u8981\u6392\u67e5\u7684\u573a\u666f\u6070\u6070\u662f\u300c\u540c\u7ea7\u6a21\u5757 hostresolver/explorer \u6ca1\u52a0\u8f7d\u5230\u300d\uff0c
#      \u6240\u4ee5\u672c\u51fd\u6570\u4e0d\u4f9d\u8d56\u5b83\u4eec\uff0cimport \u5931\u8d25\u4e5f\u7167\u6837\u8f93\u51fa\u3002
DIAG_TID = '__diag__'


def _diag_lines(sp):
    """\u628a\u53d6\u57df\u94fe\u8def\u644a\u6210\u53ef\u8bfb\u6587\u672c\u884c\uff08\u5728\u7b2c\u4e00\u5c42\u5206\u7c7b\u300c\u26a0\u8bca\u65ad\u300d\u91cc\u9010\u6761\u663e\u793a\uff09"""
    out = []

    def add(k, v):
        out.append('%s: %s' % (k, v))

    add('\u6700\u7ec8\u9009\u5b9a host', getattr(sp, 'host', '') or '(\u7a7a\u2605\u5730\u5740\u6ca1\u89e3\u6790\u51fa\u6765)')
    add('hostresolver \u6a21\u5757', '\u5df2\u52a0\u8f7d' if resolve_host else '\u2605\u672a\u52a0\u8f7d(\u540c\u7ea7\u6a21\u5757\u6ca1\u8fdb\u8bbe\u5907)')
    add('explorer \u6a21\u5757', '\u5df2\u52a0\u8f7d' if explore_hosts else '\u672a\u52a0\u8f7d')
    ext = getattr(sp, '_ext', {}) or {}
    add('ext.publish', ext.get('publish') or '(\u7a7a\uff0c\u7528\u5185\u7f6e)')
    add('ext.hosts', ','.join(ext.get('hosts') or []) or '(\u7a7a)')
    add('\u5185\u7f6e\u5019\u9009\u6570', len(getattr(sp, 'BUILTIN_HOSTS', []) or []))

    # \u72ec\u7acb\u5b9e\u6d4b\u6700\u7ec8 host\uff08\u4e0d\u4f9d\u8d56 hostresolver\uff0c\u76f4\u63a5\u770b\u5b83\u5230\u5e95\u901a\u4e0d\u901a\uff09
    u = getattr(sp, 'host', '') or ''
    if u:
        try:
            r = requests.get(u.rstrip('/') + '/', headers=getattr(sp, 'headers', {}) or {},
                             proxies=getattr(sp, 'proxies', {}) or {}, timeout=6, verify=False)
            t = r.text or ''
            add('\u5b9e\u6d4b\u8be5 host', 'HTTP %s / %dB / \u542b\u7ad9\u540d:%s'
                % (r.status_code, len(t), '\u662f' if sp.getName() in t else '\u5426\u2605'))
        except Exception as e:
            add('\u5b9e\u6d4b\u8be5 host', '\u2605\u8fde\u4e0d\u4e0a: %s' % str(e)[:60])
    else:
        add('\u5b9e\u6d4b\u8be5 host', '(\u8df3\u8fc7\uff0chost \u4e3a\u7a7a)')

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
        try:
            self._diag = _diag_lines(self)
        except Exception:
            self._diag = []
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

    def _diag_items(self):
        """\u8bca\u65ad\u884c \u2192 App \u5217\u8868\u6761\u76ee\uff08\u70b9\u300c\u26a0\u8bca\u65ad\u300d\u5206\u7c7b\u5373\u53ef\u770b\u5230\u5168\u90e8\u53d6\u57df\u8fc7\u7a0b\uff09"""
        return [{'vod_id': 'diag%d' % i, 'vod_name': '\u26a0 ' + str(x),
                 'vod_pic': '', 'vod_remarks': ''}
                for i, x in enumerate(getattr(self, '_diag', []) or [])]

    def homeContent(self, *a, **kw):
        """\u5916\u5c42\u5305\u88c5\uff1a\u539f\u7ed3\u679c + \u8ffd\u52a0\u300c\u26a0\u8bca\u65ad\u300d\u5206\u7c7b\uff08\u4e34\u65f6\u6392\u969c\uff0c\u5b9a\u4f4d App \u7aef\u65e0\u5185\u5bb9\u6839\u56e0\uff09"""
        try:
            r = self._homeContent(*a, **kw)
        except Exception:
            r = {'class': [], 'list': []}
        try:
            if isinstance(r, dict):
                r['class'] = list(r.get('class') or []) + \
                    [{'type_id': DIAG_TID, 'type_name': '\u26a0\u8bca\u65ad'}]
        except Exception:
            pass
        return r

    def _homeContent(self, flag):
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

    def categoryContent(self, tid, pg, filter, extend):
        if tid == DIAG_TID:
            items = self._diag_items()
            return {'page': 1, 'pagecount': 1, 'limit': len(items),
                    'total': len(items), 'list': items}
        result = {'list': []}
        path = f'/category/{tid}/'
        if str(pg) not in ('1', ''):
            path = f'/category/{tid}/{pg}/'
        try:
            result['list'] = self._parse_list(self._get(path).text or '')
        except Exception:
            pass
        return result

    def searchContent(self, key, quick, pg='1'):
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
