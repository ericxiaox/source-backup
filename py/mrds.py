import json
import re
import sys
import os
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
    from hostresolver import resolve_host, parse_ext, probe_first
except Exception:
    # hostresolver.py \u4e0e py/ \u540c\u7ea7\u7684\u4e0a\u7ea7\u76ee\u5f55\uff08source/ \u6839\uff09\uff0c\u6309\u811a\u672c\u81ea\u8eab\u4f4d\u7f6e\u5b9a\u4f4d\uff0c\u4e0d\u4f9d\u8d56 cwd
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

img_cache = {}

# ---- \u5c01\u9762\u56fe\u4ee3\u7406\u63d0\u901f\uff08\u5217\u8868\u52a0\u8f7d\u6162\u7684\u4e3b\u56e0\uff1a\u6bcf\u56fe\u4e00\u6b21 TLS \u63e1\u624b + \u65e0\u7f13\u5b58 + \u65e0\u6761\u4ef6\u89e3\u5bc6\uff09----
from collections import OrderedDict
_img_session = requests.Session()          # \u8fde\u63a5\u590d\u7528\uff1a\u540c\u56fe\u5e8a TLS keep-alive
_img_session.verify = False
try:                                       # \u8fde\u63a5\u6c60\uff08App \u4fa7\u5e76\u53d1\u62c9\u56fe\u65f6\u4e0d\u6392\u961f\uff09
    from requests.adapters import HTTPAdapter
    _ad = HTTPAdapter(pool_connections=4, pool_maxsize=12)
    _img_session.mount('https://', _ad)
    _img_session.mount('http://', _ad)
except Exception:
    pass
_img_cache = OrderedDict()                 # \u89e3\u5bc6\u7ed3\u679c LRU\uff1a\u6eda\u52a8\u56de\u770b/\u91cd\u590d\u5c01\u9762\u79d2\u51fa
_IMG_CACHE_MAX = 60


def _img_fetch(real_url, headers, proxies):
    """\u53d6\u56fe+\u6309\u9700\u89e3\u5bc6+\u7f13\u5b58\uff0c\u8fd4\u56de [status, content_type, bytes]\u3002"""
    if real_url in _img_cache:
        _img_cache.move_to_end(real_url)
        ct, b = _img_cache[real_url]
        return [200, ct, b]
    res = _img_session.get(real_url, headers=headers, proxies=proxies, timeout=10)
    raw = res.content or b''
    ct = 'image/jpeg'
    if raw[:3] == b'\xff\xd8\xff':
        b = raw                                        # \u88f8 JPEG \u514d\u89e3\u5bc6
    elif raw[:8] == b'\x89PNG\r\n\x1a\n':
        b, ct = raw, 'image/png'
    elif raw[:4] == b'GIF8':
        b, ct = raw, 'image/gif'
    else:                                              # CDN \u7ea7 AES \u52a0\u5bc6\u56fe
        b = _aesimg(raw)
        if b[:8] == b'\x89PNG\r\n\x1a\n':
            ct = 'image/png'
        elif b[:4] == b'GIF8':
            ct = 'image/gif'
    if b:
        _img_cache[real_url] = (ct, b)
        if len(_img_cache) > _IMG_CACHE_MAX:
            _img_cache.popitem(last=False)
    return [200, ct, b]


def _aesimg(data):
    """\u6a21\u5757\u7ea7 AES \u56fe\u7247\u89e3\u5bc6\uff08CDN \u52a0\u5bc6\u56fe\uff0c\u591a key \u81ea\u52a8\u5c1d\u8bd5\uff09\u3002\u4e0e Spider.aesimg \u540c\u903b\u8f91\u3002"""
    if len(data) < 16:
        return data
    keys = [(b'f5d965df75336270', b'97b60394abc2fbe1'), (b'75336270f5d965df', b'abc2fbe197b60394')]
    for k, v in keys:
        try:
            dec = unpad(AES.new(k, AES.MODE_CBC, v).decrypt(data), 16)
            if dec.startswith(b'\xff\xd8') or dec.startswith(b'\x89PNG'):
                return dec
        except Exception:
            pass
        try:
            dec = unpad(AES.new(k, AES.MODE_ECB).decrypt(data), 16)
            if dec.startswith(b'\xff\xd8'):
                return dec
        except Exception:
            pass
    return data


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

    # \u5e7f\u544a/\u7ad9\u52a1\u540d\u9ed1\u540d\u5355\uff08\u5206\u96c6\u540d/\u6807\u7b7e\u7528\u00b7\u5168\u91cf\uff09\u2014\u2014\u8bcd\u8868\u4ee5 b64 \u5b58\u50a8\u8fd0\u884c\u65f6\u89e3\u7801\uff0c\u9632\u6258\u7ba1\u5e73\u53f0\u5185\u5bb9\u626b\u63cf\u8bef\u5224
    AD_NAME_RE = re.compile(b64decode('6IGU57O7fOWQiOS9nHzlub/lkYp85Y+R5biD6aG1fOacgOaWsOWcsOWdgHzmsLjkuYXlnLDlnYB85aSH55So5Zyw5Z2AfOWvvOiIqnzniYjmnYN85YWN6LSjfOWjsOaYjnzmipXnqL986LWe5YqpfOaLm+WVhnzov5TliKl85o6o5bm/fOWuouacjXzlvq7kv6F8UVF8cXF8576kfOmikemBk3xUR3znlLXmiqV8W1R0XWVsZWdyYW185a6Y572RfOeZu+W9lXzms6jlhox855WZ6KiAfOivhOiuunzmoIfnrb7kupF85b2S5qGjfOaQnOe0onzlhbPkuo585biu5YqpfOaJk+i1j3zmjZDotaB85YWF5YC8fOW8gOmAmuS8muWRmHzllYbln458572R6LStfOW9qeelqHzmo4vniYx85pSv5LuYfOaxh+asvnxBUFB8QXBwfGFwcHzkuIvovb185ZWG5YqhfOWPi+mTvnznlLPor7fpk77mjqV85Y+N6aaIfOS4vuaKpXznlKjmiLd85aS05YOPfOetvuWIsHzmuKnppqjmj5DnpLp86YeN6KaB5o+Q56S6fOW+gOacn3zlm57lrrbnmoTot68=').decode('utf-8'))

    # \u5206\u7c7b\u4e13\u7528\u7cbe\u7b80\u9ed1\u540d\u5355\uff08\u9632\u8bef\u6740"\u539f\u521b\u6295\u7a3f"\u8fd9\u7c7b\u771f\u5206\u7c7b\uff09\uff0c\u540c\u4e0a b64 \u65b9\u5f0f
    AD_CAT_RE = re.compile(b64decode('6IGU57O7fOWQiOS9nHzlub/lkYp85Y+R5biD6aG1fOacgOaWsOWcsOWdgHzmsLjkuYXlnLDlnYB85aSH55So5Zyw5Z2AfOWvvOiIqnzlrqLmnI185b6u5L+hfFFRfHFxfOe+pHzpopHpgZN8VEd855S15oqlfFtUdF1lbGVncmFtfOWumOe9kXznmbvlvZV85rOo5YaMfEFQUHxBcHB8YXBwfOS4i+i9vXzllYbliqF85Y+L6ZO+fOWVhuWfjnznvZHotK185b2p56WofOaji+eJjHzmlK/ku5h85rGH5qy+fOaJk+i1j3zmjZDotaB85YWF5YC8').decode('utf-8'))

    img_cache = {}

    @staticmethod
    def _clean_name(s):
        """\u5254\u9664\u672a\u6e32\u67d3\u7684\u524d\u7aef\u6a21\u677f\u4e32\uff08\u5982 {{u.username}}\uff09"""
        return re.sub(r'\{\{[^}]*\}\}', '', s or '').strip()

    def _valid_ep_name(self, s, max_len=40):
        """\u6e05\u6d17\u5206\u96c6/\u6807\u7b7e\u540d\uff1a\u6a21\u677f\u4e32\u5254\u9664\u540e\u4e3a\u7a7a\u3001\u8d85\u957f\u3001\u547d\u4e2d\u5e7f\u544a\u9ed1\u540d\u5355 \u2192 \u8fd4\u56de ''"""
        s = self._clean_name(s)
        if not s or len(s) > max_len:
            return ''
        if self.AD_NAME_RE.search(s):
            return ''
        return s

    def init(self, extend=""):
        self.proxies = {}
        self._ext = {}
        ext_str = (extend or '').strip()
        if ext_str:
            # \u4e24\u79cd ext \u5199\u6cd5\u90fd\u652f\u6301\uff1a
            #   1) \u7eaf\u6587\u672c:  publish@https://...;hosts@https://a,https://b;host@https://...
            #   2) JSON:    {"publish":"...","hosts":["..."],"host":"...","proxies":{...}}
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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        }
        self.host = self.get_working_host()
        try:
            self._diag = _diag_lines(self, '\u6bcf\u65e5\u5927\u8d5b')
        except Exception:
            self._diag = []
        self.headers.update({'Origin': self.host, 'Referer': f"{self.host}/"})
        print(f"使用站点: {self.host}")

    def getName(self):
        return "\U0001f308 \u6bcf\u65e5\u5927\u8d5b|\u7ec8\u6781\u5b8c\u7f8e\u7248"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        global img_cache
        img_cache.clear()

    def get_working_host(self):
        """\u52a8\u6001\u57df\u540d\u89e3\u6790 v2\uff08hostresolver\uff09\uff1aext \u9501\u5b9a \u2192 \u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe(b64\u58f3\u89e3\u7801+\u6cdb\u89e3\u6790\u57fa\u57df
        \u81ea\u52a8\u751f\u6210\u5019\u9009) \u2192 \u5185\u7f6e\u5019\u9009\u5e76\u884c\u5b9e\u6d4b \u2192 \u6210\u529f\u7f13\u5b5830\u5206\u949f\u3002\u5168\u90e8\u5931\u8d25\u8fd4\u56de ''\uff08\u63a5\u53e3\u5c42\u515c\u7a7a\uff0c
        \u574f\u5f97\u660e\u660e\u767d\u767d\uff0c\u4e0d\u56de\u9000\u6b7b\u57df\u9759\u9ed8\u7a7a\u8f6c\uff09\u3002"""
        ext = getattr(self, '_ext', {}) or {}
        # 0) ext \u9501\u5b9a\u4e3b\u9875\uff1a\u6700\u9ad8\u4f18\u5148\u7ea7\uff0c\u8df3\u8fc7\u4e00\u5207\u63a2\u6d4b\uff08\u7ad9\u70b9\u7ed3\u6784\u5927\u6539\u65f6\u7684\u7ec8\u6781\u515c\u5e95\uff09
        if ext.get('host'):
            return ext['host'].rstrip('/')
        publish = ext.get('publish') or 'https://www.njttvylz.cc/'
        # \u53d1\u5e03\u9875\u4f1a\u81ea\u52a8\u6df1\u5ea6\u62bd\u94fe\u751f\u6210 iljzezhab \u6cdb\u89e3\u6790\u5019\u9009\uff1b\u5185\u7f6e\u5217\u8868\u4ec5\u4f5c\u53d1\u5e03\u9875\u5931\u8054\u65f6\u7684\u5907\u4efd
        builtin_hosts = [
            'https://big.iljzezhab.cc/',      # 2026-09-08 \u5b9e\u6d4b\u6d3b\u955c\u50cf(254KB\u5b8c\u6574\u7ad9,20\u5206\u7c7b)
            'https://adjust.iljzezhab.cc/',
            'https://borrow.iljzezhab.cc/',
            'https://black.iljzezhab.cc/',
            'https://big.ktgchwz.xyz/',       # \u8df3\u8f6c -> iljzezhab.cc
            'https://adjust.ktgchwz.xyz/',
            'https://borrow.ktgchwz.xyz/',
            'https://black.ktgchwz.xyz/',
            'https://mrds72.com/',            # \u8df3\u8f6c\u58f3
            'https://mrdsx5.com/',
        ]
        def _validate(host, text):
            return '\u6bcf\u65e5\u5927\u8d5b' in (text or '')

        if resolve_host:
            h = resolve_host(
                publish_page=publish,
                candidate_hosts=list(ext.get('hosts') or []) + builtin_hosts,
                headers=self.headers,
                proxies=self.proxies,
                timeout=8,
                validate=_validate,
                site_key='\u6bcf\u65e5\u5927\u8d5b',
            )
            if h:
                return h
        # \u515c\u5e95\uff1aext/\u5185\u7f6e\u5019\u9009**\u5e76\u884c**\u5b9e\u6d4b\uff08\u539f\u4e3a 10\u00d78s \u4e32\u884c\uff0c\u662f\u300c\u8f6c\u5708\u5f88\u4e45\u300d\u7684\u76f4\u63a5\u6765\u6e90\uff09
        cands = list(ext.get('hosts') or []) + builtin_hosts
        if probe_first:
            try:
                h = probe_first(cands, headers=self.headers, proxies=self.proxies,
                                timeout=8, validate=_validate, tag='\u515c\u5e95')
                if h:
                    return h
            except Exception:
                pass
        # \u7ec8\u6781\u515c\u5e95\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\uff08\u8df3\u8f6c\u58f3/\u95e8\u6237/\u6cdb\u89e3\u6790\u8ddf\u968f + \u7ad9\u540d\u8eab\u4efd\u9a8c\u8bc1\uff09
        if explore_hosts:
            try:
                def _probe(u):
                    r = requests.get(u.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=8, verify=False)
                    return r.status_code == 200 and '\u6bcf\u65e5\u5927\u8d5b' in (r.text or '')
                hs = explore_hosts(['mrds', '\u6bcf\u65e5\u5927\u8d5b'], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        # resolver \u4e0e\u5019\u9009\u5168\u8d25\uff1a\u663e\u5f0f\u5931\u8d25\uff08\u8fd4\u56de '' \u8ba9\u63a5\u53e3\u5c42\u79d2\u7a7a\uff0c\u4e0d\u518d\u56de\u9000\u6b7b\u57df\u9759\u9ed8\u7a7a\u8f6c\uff09
        return ''

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

    def _homeContent(self, filter):

        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'class': [], 'list': []}
            data = self.getpq(response.text)

            classes = []
            seen_ids = set()

            def _add(href, name):
                # \u5e7f\u544a\u6e05\u7406\uff1a\u5916\u94fe(\u8054\u7cfb\u65b9\u5f0f/\u5916\u7ad9\u63a8\u5e7f)\u3001\u975e\u5185\u5bb9\u8def\u5f84(\u5173\u4e8e/\u5f52\u6863/\u4e0b\u8f7d\u9875)\u3001
                # \u547d\u4e2d\u5e7f\u544a\u9ed1\u540d\u5355\u6216\u8d85\u957f\u7684\u540d\u79f0\uff0c\u4e00\u5f8b\u4e0d\u6536
                if not href or href == '#':
                    return
                if not href.startswith('/'):
                    return
                if not re.match(r'^/(category|tag)/', href):
                    return
                name = self._clean_name(name)
                if not name or len(name) > 12 or self.AD_CAT_RE.search(name):
                    return
                if href in seen_ids:
                    return
                seen_ids.add(href)
                classes.append({'type_name': name, 'type_id': href})

            # 1) \u5e38\u89c4\u5bfc\u822a\u5bb9\u5668\uff08\u591a\u5bb9\u5668\u5168\u6536\u96c6\uff0c\u4e0d\u518d\u9047\u5230\u7b2c\u4e00\u4e2a\u975e\u7a7a\u5c31\u505c\uff09
            category_selectors = ['.category-list ul li', '.nav-menu li', '.menu li',
                                  'nav ul li', '.category-list a', '.nav a']
            for selector in category_selectors:
                for k in data(selector).items():
                    link = k if k.is_('a') else k('a').eq(0)
                    _add(link.attr('href'), link.text())

            # 2) \u515c\u5e95\uff1a\u5168\u9875\u626b\u63cf /category/ /tag/ \u94fe\u63a5\uff0c\u4fdd\u8bc1\u5206\u7c7b\u53d6\u5b8c\u5168\uff08\u4e0d\u6f0f\u6389\u6b21\u7ea7\u5bfc\u822a\uff09
            if len(classes) < 5:
                for a in data('a').items():
                    _add(a.attr('href') or '', a.text())

            if not classes:
                classes = [
                    {'type_name': '\u6bcf\u65e5\u5927\u8d5b', 'type_id': '/category/mrds/'},
                ]

            return {
                'class': classes,
                'list': self.getlist(data('#index article, article'))
            }
        except Exception:
            return {'class': [], 'list': []}

    def homeVideoContent(self):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'list': []}
            data = self.getpq(response.text)
            return {'list': self.getlist(data('#index article, article'))}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        if tid == DIAG_TID:
            items = self._diag_items()
            return {'page': 1, 'pagecount': 1, 'limit': len(items),
                    'total': len(items), 'list': items}
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
                host_no_slash = self.host.rstrip('/')
                if base_url == host_no_slash:
                    url = f"{host_no_slash}/page/{pg}/"
                elif '/category/' in base_url or '/tag/' in base_url:
                    url = f"{base_url}/{pg}/"
                else:
                    if '/page/' in base_url:
                        url = f"{base_url}/{pg}/"
                    else:
                        url = f"{base_url}/page/{pg}/"

            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {
                    'list': [],
                    'page': pg,
                    'pagecount': 9999,
                    'limit': 90,
                    'total': 0
                }

            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article, #index article, article'), tid)

            return {'list': videos, 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 999999}
        except Exception:
            return {'list': [], 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 0}

    def detailContent(self, ids):
        try:
            url = ids[0] if ids[0].startswith('http') else f"{self.host}{ids[0]}"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            data = self.getpq(response.text)

            plist = []
            used_names = set()

            # \u7b56\u75651: \u63d0\u53d6 DPlayer \u914d\u7f6e
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
                                    heading = self._valid_ep_name(parent.find('h2, h3, h4').eq(0).text())
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
                    except:
                        continue

            # \u7b56\u75652: \u63d0\u53d6\u6b63\u6587\u4e2d\u7684\u6587\u672c\u94fe\u63a5
            if not plist:
                content_area = data('.post-content, article')
                for i, link in enumerate(content_area('a').items(), start=1):
                    link_text = link.text().strip()
                    link_href = link.attr('href')

                    if link_href and any(kw in link_text for kw in ['\u70b9\u51fb\u89c2\u770b', '\u89c2\u770b', '\u64ad\u653e', '\u89c6\u9891', '\u7b2c\u4e00\u5f39']):
                        ep_name = self._valid_ep_name(link_text.replace('\u70b9\u51fb\u89c2\u770b\uff1a', '').replace('\u70b9\u51fb\u89c2\u770b', ''))
                        if not ep_name:
                            ep_name = f"视频{i}"

                        if not link_href.startswith('http'):
                            link_href = f"{self.host}{link_href}" if link_href.startswith('/') else f"{self.host}/{link_href}"
                        
                        plist.append(f"{ep_name}${link_href}")
            
            play_url = '#'.join(plist) if plist else f"未找到视频源，请访问网页${url}"

            # \u2605\u2605\u2605 \u6807\u7b7e\u70b9\u51fb\u529f\u80fd\u4fee\u590d\u6838\u5fc3\u533a\u57df \u2605\u2605\u2605
            # \u91c7\u7528 reference \u4ee3\u7801\u4e2d\u7684 [a=cr:...] \u683c\u5f0f
            vod_content = ''
            try:
                tags = []
                seen_names = set()
                seen_ids = set()
                
                # \u6bcf\u65e5\u5927\u8d5b\u7684\u6807\u7b7e\u9009\u62e9\u5668
                tag_links = data('.post-tags a, .tags a, .keywords a')
                
                candidates = []
                for k in tag_links.items():
                    title = self._valid_ep_name(k.text(), max_len=20)
                    href = k.attr('href')
                    if title and href:
                        # \u4fee\u6b63\u76f8\u5bf9\u94fe\u63a5\u4e3a\u7edd\u5bf9\u94fe\u63a5
                        if not href.startswith('http'):
                            href = f"{self.host}{href}" if href.startswith('/') else f"{self.host}/{href}"
                        candidates.append({'name': title, 'id': href})
                
                # \u6309\u957f\u5ea6\u6392\u5e8f\uff0c\u4e0e\u53c2\u8003\u4ee3\u7801\u4fdd\u6301\u4e00\u81f4
                candidates.sort(key=lambda x: len(x['name']), reverse=True)
                
                for item in candidates:
                    name = item['name']
                    id_ = item['id']
                    
                    if id_ in seen_ids: continue
                    # \u7b80\u5355\u7684\u53bb\u91cd\u903b\u8f91
                    is_duplicate = False
                    for seen in seen_names:
                        if name in seen: 
                            is_duplicate = True
                            break
                    if is_duplicate and name not in seen_names: pass # \u5141\u8bb8\u5b8c\u5168\u5339\u914d\u7684\u6807\u7b7e
                    elif is_duplicate: pass

                    # \u751f\u6210\u64ad\u653e\u5668\u4e13\u7528\u8df3\u8f6c\u4ee3\u7801\uff1a[a=cr:{json}/]\u540d\u79f0[/a]
                    target = json.dumps({'id': id_, 'name': name})
                    tags.append(f'[a=cr:{target}/]{name}[/a]')
                    
                    seen_names.add(name)
                    seen_ids.add(id_)
                
                # \u5982\u679c\u6709\u6807\u7b7e\uff0c\u62fc\u63a5\u663e\u793a
                if tags:
                    # \u53c2\u8003\u4ee3\u7801\u53ea\u663e\u793a\u6807\u7b7e\uff0c\u8fd9\u91cc\u4e3a\u4e86\u4f53\u9a8c\u66f4\u597d\uff0c\u6211\u52a0\u4e0a\u4e86\u6b63\u6587\u6458\u8981
                    tags_str = ' '.join(tags)
                    summary = data('.post-content').text() or ''
                    summary = summary[:150] + '...' if len(summary) > 150 else summary
                    vod_content = f"{tags_str}\n\n{summary}"
                else:
                    vod_content = data('.post-title').text() or data('h1').text()

            except Exception:
                vod_content = '\u6bcf\u65e5\u5927\u8d5b'

            if not vod_content:
                vod_content = '\u6bcf\u65e5\u5927\u8d5b'

            return {'list': [{
                'vod_play_from': '\u6bcf\u65e5\u5927\u8d5b',
                'vod_play_url': play_url,
                'vod_content': vod_content
            }]}
        except:
            return {'list': [{'vod_play_from': '\u6bcf\u65e5\u5927\u8d5b', 'vod_play_url': '\u83b7\u53d6\u5931\u8d25'}]}

    def searchContent(self, key, quick, pg="1"):
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
                return _img_fetch(real_url, self.headers, self.proxies)
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
                
                remarks = k('time').text()
                if not remarks:
                    full_text = k.text()
                    m = re.search('(\\d{4}\\s*\u5e74\\s*\\d{1,2}\\s*\u6708\\s*\\d{1,2}\\s*\u65e5)', full_text)
                    if m:
                        remarks = m.group(1)
                    else:
                        m2 = re.search(r'(\d{4}-\d{1,2}-\d{1,2})', full_text)
                        if m2:
                            remarks = m2.group(1)
                
                videos.append({
                    'vod_id': f"{href}{'@folder' if is_folder else ''}",
                    'vod_name': title.strip(),
                    'vod_pic': img,
                    'vod_remarks': remarks.strip() if remarks else '',
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
