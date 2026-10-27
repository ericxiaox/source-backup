# -*- coding: utf-8 -*-
"""\u793e\u533a\u89c6\u9891\uff08www.65jwfm.com\uff09\u2014 OK\u5f71\u89c6 py \u6e90

\u7ad9\u578b\uff1aUni-app H5 + \u540c\u6e90 REST API\uff08\u65e0 MacCMS\u3001\u65e0 HTML \u5217\u8868\uff09
  \u5217\u8868  GET {host}/api/movie/list?page=N&pageSize=24&tagid=<id>  \uff08\u4e5f\u53ef &keyword= \u505a\u641c\u7d22\uff09
  \u8be6\u60c5  GET {host}/api/movie/<movieid>
  \u5206\u7c7b  GET {host}/api/movie/tags
  \u914d\u7f6e  GET {host}/api/config/ini

\U0001f6a9 \u8be5\u7ad9\u63a5\u53e3\u5168\u90e8\u8fd4\u56de XOR2 \u4fe1\u5c01\uff0c\u4e0d\u662f\u660e\u6587 JSON\uff1a
  {\"enc\":3,\"alg\":\"XOR2\",\"n\":\"<nonce>\",\"d\":\"<base64url \u5bc6\u6587>\"}
  \u7b97\u6cd5\uff08\u9010\u5b57\u7167\u642c\u7ad9\u70b9 /assets/index-*.js\uff0c2026-10-26 \u5b9e\u6d4b\u89e3\u7801\u6210\u529f\uff09\uff1a
    \u79cd\u5b50  seed = FNV1a32(key + \"|\" + nonce)\uff0cseed \u4e3a 0 \u65f6\u53d6 2166136261
    state \u6bcf 4 \u5b57\u8282\u63a8\u8fdb\u4e00\u6b21\uff1axorshift32(x)= x^(x<<13); x^(x>>>17); x^(x<<5)\uff08\u5168\u7a0b 32 \u4f4d\uff09
    \u7b2c i \u5b57\u8282\u63a9\u7801 = (state >>> 8*(i%4)) & 0xFF
    key   \u9ed8\u8ba4 'Mumu2026#'\uff08\u7ad9\u70b9 config \u7684 mgrEncryptKey \u4e0b\u53d1\u7684\u5c31\u662f\u5b83\uff0c2026-10-26 \u5b9e\u6d4b\u786e\u8ba4\uff09
  \U0001f6a9 \u6362 key \u4e0d\u7b49\u4e8e\u524d\u7aef\u4e00\u8d77\u6302\uff1aApp \u542f\u52a8\u65f6\u4f1a\u8bfb config \u7684 mgrEncryptKey \u5199\u8fdb localStorage
     (apiEncKey)\uff0c\u4e4b\u540e\u7684\u89e3\u5bc6\u90fd\u7528\u5b83 \u2014\u2014 \u5373\u7ad9\u65b9**\u53ef\u4ee5\u5355\u65b9\u9762\u6362\u94a5\u800c\u524d\u7aef\u7167\u5e38\u8dd1**\uff0c\u6e90\u82e5\u53ea\u8ba4
     \u786c\u7f16\u7801\u94a5\u5c31\u4f1a\u9759\u9ed8\u5931\u6548\uff08\u4e0d\u62a5\u9519\u3001\u53ea\u8fd4\u56de\u7a7a\u5217\u8868\uff09\u3002\u6545\u672c\u6e90\u6309\u300c\u5019\u9009\u94a5\u96c6 + \u5931\u8d25\u81ea\u6108\u300d\u5904\u7406\uff1a
       \u2460 \u5019\u9009\u94a5\u96c6 self._keys\uff0c\u961f\u9996\u662f\u5f53\u524d\u94a5\uff0c\u961f\u5c3e\u6052\u7559\u786c\u7f16\u7801\u515c\u5e95\uff1b
       \u2461 \u4efb\u4e00\u4fe1\u5c01\u89e3\u4e0d\u5f00 \u2192 _refresh_key() \u91cd\u62c9 /api/config/ini \u53d6\u65b0 mgrEncryptKey\uff0c
          \u65b0\u94a5\u63d2\u961f\u9996\u540e\u91cd\u8bd5\uff08config \u672c\u8eab\u4e5f\u662f\u4fe1\u5c01\uff0c\u7528\u73b0\u6709\u5019\u9009\u94a5\u9010\u4e2a\u8bd5\u89e3\uff09\uff1b
       \u2462 _api_get \u7684\u81ea\u6108\u987a\u5e8f\uff1a\u5148\u6362\u94a5 \u2192 \u518d\u6362\u57df \u2192 \u90fd\u5931\u8d25\u624d\u629b\u3002

\U0001f6a9 \u64ad\u653e\u5730\u5740\u6709\u4e09\u7c7b\u5751\uff082026-10-26 \u5b9e\u6d4b\uff09\uff1a
  \u2460 \u8be6\u60c5\u91cc\u7684 h264m3u8url \u53ef\u80fd\u662f**\u76f8\u5bf9\u8def\u5f84** `/data/\u2026`\u3002\u672c\u7ad9 origin \u4e0a\u6ca1\u6709 /data/
     \uff08\u8fd4\u56de\u7684\u662f SPA \u9996\u9875 HTML\uff09\uff0c\u5fc5\u987b\u6302\u5230\u771f\u5b9e CDN \u57df \u2014\u2014 \u5b9e\u6d4b h1.qhkjapp.com /
     h3.xinghun1.com \u76f4\u63a5 200 \u4e14\u56de #EXTM3U\u3002
  \u2461 **\u5217\u8868\u63a5\u53e3**\u7ed9\u7684 h264mp4url \u57df\u662f\u8fc7\u671f\u7684\u4f2a\u88c5\u57df\uff08down.baidu.com\uff0cDNS \u5df2\u4e0d\u5b58\u5728\uff09\uff0c
     \u53ea\u6709**\u8be6\u60c5\u63a5\u53e3**\u7ed9\u7684\uff08down.mm7878.com\uff09\u662f\u6d3b\u7684 \u2192 \u64ad\u653e\u5730\u5740\u4e00\u5f8b\u8d70\u8be6\u60c5\u53d6\u3002
  \u2462 mp4 \u57df\u6302 m3u8 \u8def\u5f84\u4f1a 404\uff0c\u4e24\u4e2a\u6c60\u5b50\u5fc5\u987b\u4e25\u683c\u5206\u5f00\uff0c\u4e0d\u53ef\u6df7\u7528\u3002

\U0001f6a9 \u5217\u8868\u63a5\u53e3\u7684 smallpic \u57df sq.2277ww.com \u8bbe\u5907\u7aef\u8fde\u4e0d\u4e0a\uff0c\u4f46\u540c\u4e00\u5f20\u56fe\u7684\u771f\u5b9e\u5730\u5740
   \u5c31\u5728\u8be6\u60c5\u63a5\u53e3\u91cc\uff08ddd.aisheji8.com/data/cover/\u2026\uff09\uff0c\u6587\u4ef6\u540d\u5b8c\u5168\u4e00\u81f4\uff0c\u53ea\u5dee /data \u524d\u7f00\u3002

\U0001f6a9 \u5206\u9875\u8d85\u754c**\u4e0d\u8fd4\u56de\u7a7a**\uff0c\u670d\u52a1\u7aef\u628a page \u94b3\u5230\u6700\u540e\u4e00\u9875 \u2192 \u53cd\u590d\u8fd4\u56de\u540c\u4e00\u6279\u3002
   \u5fc5\u987b\u81ea\u5df1\u7528 total \u7b97 pagecount \u5e76\u5728\u8fb9\u754c\u505c\uff0c\u5426\u5219\u7528\u6237\u4e00\u76f4\u5f80\u4e0b\u6ed1\u90fd\u662f\u91cd\u590d\u5185\u5bb9\u3002

\u5206\u7c7b\uff1a\u7ad9\u5185 4 \u7ec4\u5171 31 \u4e2a tag\uff0c\u5176\u4e2d graphic \u7ec4\u7684 image_*/novel_* \u662f\u56fe\u6587/\u5c0f\u8bf4\uff08\u975e\u89c6\u9891\uff09
  \u6545\u4e0d\u6536\u5f55\uff1b\u957f\u7247 7 \uff0b \u89c6\u9891 8 \uff0b \u89c6\u9891 8 \uff1d 23 \u4e2a\u89c6\u9891\u5206\u7c7b\u5168\u90e8\u6536\u5f55\u3002
  \u5206\u7c7b\u540d\u4e00\u5f8b\u7528\u7ad9\u65b9\u539f\u540d\uff0c\u4e0d\u6539\u5199\uff08\u300c\u5c11\u5973\u841d\u8389\u300d\u7b49\u6807\u7b7e\u6309\u7ad9\u65b9\u5f15\u6d41\u9898\u6750\u539f\u6837\u4fdd\u7559\uff09\u3002
"""
import base64
import json
import re
import time
from urllib.parse import unquote

import requests

try:
    from base.spider import Spider as BaseSpider
except Exception:
    class BaseSpider(object):
        pass

try:
    # \u53ea\u501f ext \u89e3\u6790\uff08hosts@ \u5019\u9009\u57df\uff09\u3002\u672c\u7ad9\u6ca1\u6709\u53d1\u5e03\u9875\uff0c\u53d6\u57df\u4e0d\u8d70 resolve_host \u7684
    # \u53d1\u5e03\u9875\u7b97\u6cd5\uff0c\u56e0\u6b64\u4e0d\u9700\u8981 INLINE-GEN \u5185\u8054\u94fe\uff08\u4e0e\u300c\u7981\u679c\u77ed\u5267.py\u300d\u540c\u6784\uff09\u3002
    from hostresolver import parse_ext
except Exception:
    parse_ext = None


_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
       '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# \u5165\u53e3\u57df\u6c60\u3002\u9996\u53d1\u57df\u4e4b\u5916\u7559\u4f4d\uff0c\u6362\u57df\u65f6\u7ba1\u7406\u53f0 ext \u52a0\u4e00\u6761 hosts@ \u5373\u53ef\uff0c\u4e0d\u5fc5\u6539\u6587\u4ef6\u3002
# \u88f8\u57df\u4e0e www \u5b9e\u6d4b\u540c\u4e00\u540e\u7aef\uff08302 \u2192 /index.htm\uff09\uff0c\u4e92\u4e3a\u5907\u7528\u3002
# \ud83d\udea9 2026-10-27 \u6362\u57df\uff1a65jwfm.com / eett33.com \u5168\u7ad9\u5df2\u964d\u7ea7\u4e3a JS \u8df3\u677f\uff08url2.push \u2192 www.83xvzr.com\uff09\uff0c
#    \u771f\u7ad9\u8fc1\u5230 83xvzr.com \u2014\u2014 sitename \u4ecd\u662f\u300c\u793e\u533a\u89c6\u9891\u300d\u3001project=sq\u3001API \u524d\u7f00/\u5b57\u6bb5/\u5bc6\u94a5\u5168\u672a\u53d8\u3002
#    eett33.com \u73b0\u4e3a\u8df3\u677f\uff0c\u6302\u6c60\u5c3e\u53ea\u5f53\u5907\u80ce\uff08\u63a2\u6d3b\u62ff\u4e0d\u5230 JSON \u4f1a\u81ea\u52a8\u8df3\u8fc7\uff0c\u82e5\u54ea\u5929\u8f6c\u6b63\u53ef\u81ea\u6108\u63a5\u56de\uff09\u3002
_SITE_HOSTS = ('www.83xvzr.com', '83xvzr.com', 'www.eett33.com')

_API = '/api'
_PAGE_SIZE = 24
_ENC_KEY = 'Mumu2026#'

# \u76f8\u5bf9\u8def\u5f84\u515c\u5e95\u6c60\uff08\u8be6\u60c5\u8fd4\u56de\u7edd\u5bf9 URL \u65f6\u4f1a\u81ea\u52a8\u628a\u771f\u5b9e\u57df\u5b66\u5230\u6c60\u9996\uff0c\u8fd9\u91cc\u662f\u51b7\u542f\u52a8\u515c\u5e95\uff09
_M3U8_HOSTS = ('https://h1.qhkjapp.com', 'https://h3.xinghun1.com')
_MP4_HOSTS = ('https://down.mm7878.com',)

# \u5217\u8868\u5c01\u9762\u57df \u2192 \u8be6\u60c5\u63a5\u53e3\u91cc\u540c\u56fe\u7684\u771f\u5b9e\u57df\uff08\u8def\u5f84\u53ea\u5dee /data \u524d\u7f00\uff09
_PIC_FIX = re.compile(r'^https?://sq\.2277ww\.com/cover/(.+)$', re.I)
_PIC_ALT = 'https://ddd.aisheji8.com/data/cover/'

# JS \u8df3\u677f\u9875\uff08\u7ad9\u7fa4\u901a\u7528 Jump3url \u6a21\u677f\uff09\uff1aurl2.push("\u65b0\u57df")\u3002\u771f\u5b9e\u9875\u9762\u5e38\u628a\u6574\u53e5\u585e\u8fdb
# eval(decodeURIComponent('url2%2Epush%28%2283xvzr%2Ecom%22%29\u2026'))\uff0c\u8fde\u57df\u540d\u7684\u70b9\u90fd\u7f16\u7801\u6210
# %2E\uff0c\u6545\u5148\u89e3\u4e00\u6b21\u767e\u5206\u53f7\u518d\u8dd1\u540c\u4e00\u5957\u660e\u6587\u6b63\u5219\u3002
_JUMP_RE = re.compile(r'url2\s*\.\s*push\s*\(\s*["\']([a-z0-9][a-z0-9.\-]{2,60})["\']', re.I)


def _jump_targets(text):
    """\u4ece JS \u8df3\u677f\u9875\u63d0\u53d6\u76ee\u6807\u57df\uff1b\u8fd4\u56de\u5c0f\u5199\u53bb\u91cd\u5217\u8868\uff08\u987a\u5e8f\uff1d\u9875\u9762\u51fa\u73b0\u987a\u5e8f\uff09\u3002"""
    out = []
    for src in (text or '', unquote(text or '')):
        for m in _JUMP_RE.finditer(src):
            h = m.group(1).lower().strip('.')
            if h and h not in out:
                out.append(h)
    return out

# \u7ad9\u65b9 tagid \u2192 \u5206\u7c7b\u540d\uff08\u987a\u5e8f\uff1d\u7ad9\u65b9\u5206\u7ec4\u987a\u5e8f\uff1a\u957f\u7247 7\uff5c\u89c6\u9891 8\uff5c\u89c6\u9891 8\uff09
_CATS = (
    ('26', '\u65e0\u7801\u7d20\u4eba'), ('84', '\u65e5\u672c\u65e0\u7801'), ('22', '\u65e0\u7801\u7834\u89e3'),
    ('25', '\u65e5\u97e9\u4e2d\u5b57'), ('19', '\u6b27\u7f8e\u52b2\u7206'), ('28', '\u7ecf\u5178\u4e09\u7ea7'), ('20', '3D\u52a8\u6f2b'),
    ('1', '\u56fd\u4ea7\u81ea\u62cd'), ('90', '\u7efc\u5408\u5f3a\u7247'), ('4', '\u5bb6\u5ead\u4e71\u4f26'), ('3', '\u5c11\u5973\u841d\u8389'),
    ('5', '\u719f\u5973\u5c11\u5987'), ('7', '\u9152\u5e97\u63a2\u82b1'), ('8', '\u5077\u62cd\u76d7\u6444'), ('37', '\u9189\u9152\u8ff7\u5978'),
    ('38', '\u5403\u74dc\u9ed1\u6599'), ('2', '\u76f4\u64ad\u88f8\u804a'), ('76', '\u5de8\u4e73\u8bf1\u60d1'), ('36', '\u6237\u5916\u91ce\u6218'),
    ('23', 'AI\u6362\u8138'), ('73', '\u7fa4P\u6362\u59bb'), ('57', '\u7f51\u9ec4\u535a\u4e3b'), ('56', '\u9ed1\u4eba\u5a9a\u9ed1'),
)


# ---------------------------------------------------------------- XOR2 \u89e3\u7801
def _b64u(s):
    s = str(s or '').strip().replace('-', '+').replace('_', '/')
    return base64.b64decode(s + '=' * ((4 - len(s) % 4) % 4))


def _fnv1a(text):
    h = 2166136261
    for b in str(text).encode('utf-8'):
        h = ((h ^ b) * 16777619) & 0xFFFFFFFF
    return h


def _xs32(x):
    t = x & 0xFFFFFFFF
    t = (t ^ ((t << 13) & 0xFFFFFFFF)) & 0xFFFFFFFF
    t = (t ^ (t >> 17)) & 0xFFFFFFFF
    t = (t ^ ((t << 5) & 0xFFFFFFFF)) & 0xFFFFFFFF
    return t


def _xor2(data, nonce, key):
    seed = _fnv1a('%s|%s' % (key, nonce)) or 2166136261
    out = bytearray(len(data))
    state, r = seed, 0
    for i, b in enumerate(data):
        if not (i & 3):
            state = _xs32(state)
            r = state
        out[i] = b ^ ((r >> (8 * (i & 3))) & 255)
    return bytes(out)


def _unseal(obj, key=_ENC_KEY):
    """\u89e3 ENC3 \u4fe1\u5c01\uff1b\u4e0d\u662f\u4fe1\u5c01\u7684\u503c\u539f\u6837\u9012\u5f52\u5904\u7406\u3002"""
    if isinstance(obj, dict):
        enc = obj.get('enc')
        try:
            enc = int(enc or 0)
        except Exception:
            enc = 0
        if enc == 3 and obj.get('n') and obj.get('d'):
            raw = _xor2(_b64u(obj['d']), str(obj['n']), key)
            return json.loads(raw.decode('utf-8', 'replace'))
        return dict((k, _unseal(v, key)) for k, v in obj.items())
    if isinstance(obj, list):
        return [_unseal(x, key) for x in obj]
    return obj


def _is_envelope(obj):
    """\u662f\u5426 ENC3\uff08XOR2\uff09\u4fe1\u5c01\u3002"""
    try:
        return (isinstance(obj, dict) and int(obj.get('enc') or 0) == 3
                and bool(obj.get('n')) and bool(obj.get('d')))
    except Exception:
        return False


class Spider(BaseSpider):
    site = 'https://' + _SITE_HOSTS[0]
    api = site + _API

    def getName(self):
        return '\u793e\u533a\u89c6\u9891'

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        return True

    def manualVideoCheck(self):
        return False

    def destroy(self):
        return None

    def init(self, extend=''):
        self.host = 'https://' + _SITE_HOSTS[0]
        self._key = _ENC_KEY
        self._keys = [_ENC_KEY]  # \u5019\u9009\u94a5\u96c6\uff1a\u961f\u9996\u5f53\u524d\u94a5\uff0c\u961f\u5c3e\u6052\u7559\u786c\u7f16\u7801\u515c\u5e95
        self._hosts = list(_SITE_HOSTS)
        self._m3u8_hosts = list(_M3U8_HOSTS)
        self._mp4_hosts = list(_MP4_HOSTS)
        self._cand = {}          # movieid -> [\u64ad\u653e\u5019\u9009]
        self._key_synced = False
        try:
            self._ext_hosts(extend)
        except Exception:
            pass

    # ------------------------------------------------------------ \u57fa\u7840\u8bbe\u65bd
    def _hd(self):
        # \u94c1\u5f8b\uff1a\u4e0d\u88f8\u7528 self.headers\uff08App \u58f3\u4f1a\u7ed9\u7f3a\u5931\u5c5e\u6027\u8fd4\u56de\u53ef\u8c03\u7528\u5bf9\u8c61\uff09
        return {
            'User-Agent': _UA,
            'Referer': str(getattr(self, 'host', self.site)) + '/',
            'Accept': 'application/json, text/plain, */*',
        }

    def _ext_hosts(self, extend):
        if not parse_ext:
            return
        ext = parse_ext(extend or '') or {}
        cands = []
        for v in (ext.get('hosts') or []):
            cands.append(v)
        if ext.get('host'):
            cands.append(ext.get('host'))
        for u in cands:
            u = str(u or '').strip().rstrip('/')
            if not u:
                continue
            u = re.sub(r'^https?://', '', u).split('/')[0]
            if u and u not in self._hosts:
                self._hosts.insert(0, u)

    def _ensure_host(self):
        """\u5165\u53e3\u81ea\u6108\uff1a\u4f9d\u6b21\u63a2\u5019\u9009\u57df\uff0c\u80fd\u89e3\u51fa\u5206\u7c7b\u5c31\u5b9a\u4e3a\u5f53\u524d\u57df\u3002

        \U0001f6a9 \u8f6e\u6362\u7ad9\u7fa4\u5e38\u6001\u662f\u300c\u65e7\u57df\u53ea\u7559 JS \u8df3\u677f\u300d\uff082026-10-27\uff1a65jwfm/eett33 \u2192 83xvzr \u5373\u6b64\u5f62\u6001\uff09\uff1a
        \u63a2\u6d3b\u62ff\u5230 HTML \u800c\u975e JSON \u65f6\uff0c\u89e3\u6790 url2.push \u7684\u76ee\u6807\u57df\u8ffd\u52a0\u5165\u6c60\u7ee7\u7eed\u63a2\uff0c
        \u8fd9\u6837\u8fd0\u8425\u65b9\u4e0b\u6b21\u518d\u6362\u57df\uff0c\u6e90\u81ea\u5df1\u8ddf\u8fc7\u53bb\uff0c\u4e0d\u5fc5\u6539\u6587\u4ef6\u3002
        """
        cur = str(getattr(self, 'host', '') or '')
        i, guard = 0, 12          # guard\uff1a\u9632\u8df3\u677f\u4e92\u76f8\u6307\u5411\u9020\u6210\u6b7b\u5faa\u73af
        while i < len(self._hosts) and i < guard:
            h = self._hosts[i]
            i += 1
            base = h if h.startswith('http') else 'https://' + h
            try:
                r = requests.get(base + _API + '/movie/tags', headers={
                    'User-Agent': _UA, 'Referer': base + '/',
                    'Accept': 'application/json, text/plain, */*'}, timeout=8)
                if r.status_code != 200:
                    continue
                try:
                    obj = r.json()
                except Exception:
                    # \u4e0d\u662f JSON \u2192 \u591a\u534a\u662f\u8df3\u677f\u9875\uff0c\u628a\u65b0\u57df\u8ffd\u52a0\u8fdb\u6c60\u7ee7\u7eed\u63a2
                    for t in _jump_targets(getattr(r, 'text', '') or ''):
                        if t not in self._hosts:
                            self._hosts.append(t)
                    continue
                d = self._unseal_auto(obj)
                if d.get('code') == 0 and d.get('data'):
                    self.host = base
                    if i > 1:                    # \u547d\u4e2d\u7684\u57df\u63d0\u5230\u961f\u9996\uff0c\u4e0b\u6b21\u5c11\u8d70\u5f2f\u8def
                        try:
                            self._hosts.remove(h)
                            self._hosts.insert(0, h)
                        except Exception:
                            pass
                    return True
            except Exception:
                continue
        self.host = cur or self.site
        return False

    def _api_get(self, path, params=None):
        """GET \u5e76\u89e3\u7801\u3002\u5931\u8d25\u5148\u8bd5\u6362\u94a5 \u2192 \u518d\u8bd5\u6362\u57df \u2192 \u90fd\u5931\u8d25\u624d\u629b\u3002"""
        for attempt in (0, 1, 2):
            base = str(getattr(self, 'host', '') or self.site)
            try:
                r = requests.get(base + _API + path, headers=self._hd(),
                                 params=params or {}, timeout=12)
                if r.status_code != 200:
                    raise IOError('HTTP %s' % r.status_code)
                return self._unseal_auto(r.json())
            except Exception:
                if attempt == 0:
                    self._refresh_key()   # \u7ad9\u65b9\u53ef\u80fd\u6362\u94a5\uff08\u6e90\u53ea\u8ba4\u786c\u7f16\u7801\u94a5\u65f6\u4f1a\u9759\u9ed8\u5931\u6548\uff09
                elif attempt == 1:
                    self._ensure_host()   # \u7ad9\u65b9\u53ef\u80fd\u6362\u57df
                else:
                    raise
        return {}

    def _unseal_auto(self, obj):
        """\u6309\u5019\u9009\u94a5\u96c6\u89e3\u4fe1\u5c01\uff1b\u54ea\u628a\u89e3\u5f00\u5c31\u628a\u54ea\u628a\u63d0\u5230\u961f\u9996\u3002\u975e\u4fe1\u5c01\u539f\u6837\u8fd4\u56de\u3002

        \u94a5\u9519\u65f6 json.loads \u4f1a\u629b\uff08\u6781\u5c0f\u6982\u7387\u89e3\u51fa\u5408\u6cd5 JSON\uff0c\u6545\u518d\u6821\u4e00\u5c42\u7ed3\u6784\uff09\u3002
        """
        if not _is_envelope(obj):
            try:
                return _unseal(obj, getattr(self, '_key', _ENC_KEY))
            except Exception:
                return obj
        for k in list(getattr(self, '_keys', [_ENC_KEY])):
            try:
                d = _unseal(obj, k)
            except Exception:
                continue
            if isinstance(d, (dict, list)) and d:
                if k != getattr(self, '_key', ''):
                    self._key = k
                    self._keys.remove(k)
                    self._keys.insert(0, k)
                return d
        raise ValueError('unseal: no key matched')

    def _refresh_key(self):
        """\u91cd\u62c9 /api/config/ini \u786e\u8ba4\u6216\u66f4\u65b0 mgrEncryptKey\u3002

        \u8fd4\u56de True \u8868\u793a config \u5df2\u89e3\u51fa\uff08\u94a5\u786e\u8ba4\u6216\u5df2\u66f4\u65b0\uff09\uff1bFalse \u8868\u793a\u6839\u672c\u62ff\u4e0d\u5230 config\u3002
        config \u81ea\u8eab\u4e5f\u662f\u4fe1\u5c01 \u2014\u2014 \u7528\u73b0\u6709\u5019\u9009\u94a5\u9010\u4e2a\u8bd5\u89e3\uff0c\u65b0\u94a5\u63d2\u961f\u9996\u3002
        """
        try:
            base = str(getattr(self, 'host', '') or self.site)
            r = requests.get(base + _API + '/config/ini', headers=self._hd(), timeout=8)
            if r.status_code != 200:
                return False
            j = r.json()
        except Exception:
            return False
        cands = list(getattr(self, '_keys', [_ENC_KEY]))
        if _ENC_KEY not in cands:
            cands.append(_ENC_KEY)
        for k in cands:
            try:
                d = _unseal(j, k)
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            sysd = (d.get('data') or {}).get('system') or {}
            nk = str(sysd.get('mgrEncryptKey') or '').strip()
            # SEAL1.* \u5f62\u6001\u9700\u53e6\u89e3\uff0c\u672c\u6e90\u53ea\u8ba4\u660e\u6587\u94a5
            if nk and not nk.startswith('SEAL1.'):
                if nk not in self._keys:
                    self._keys.insert(0, nk)
                if nk != getattr(self, '_key', ''):
                    self._key = nk
            return True
        return False

    def _key_sync(self):
        """\u542f\u52a8\u65f6\u4e3b\u52a8\u540c\u6b65\u4e00\u6b21 config \u4e0b\u53d1\u7684 mgrEncryptKey\uff08\u6210\u529f\u624d\u7f6e\u4f4d\uff0c\u5931\u8d25\u7559\u7ed9 _api_get \u515c\u5e95\uff09\u3002"""
        if getattr(self, '_key_synced', False):
            return
        if self._refresh_key():
            self._key_synced = True

    # ------------------------------------------------------------ \u53d6\u6570
    def _raw_list(self, tid, pg):
        self._key_sync()
        params = {'page': int(pg), 'pageSize': _PAGE_SIZE}
        if tid and str(tid) not in ('new', 'all', ''):
            params['tagid'] = str(tid)
        return self._api_get('/movie/list', params) or {}

    def _list(self, tid, pg):
        d = self._raw_list(tid, pg)
        arr = d.get('data') or []
        try:
            total = int(d.get('total') or 0)
        except Exception:
            total = 0
        pages = max(1, int((total + _PAGE_SIZE - 1) / _PAGE_SIZE)) if total else int(pg)
        # \ud83d\udea9 \u670d\u52a1\u7aef\u8d85\u754c\u4e0d\u8fd4\u7a7a\u800c\u662f\u94b3\u5230\u6700\u540e\u4e00\u9875 \u2192 \u5fc5\u987b\u81ea\u5df1\u5728\u8fb9\u754c\u622a\u65ad
        if int(pg) > pages:
            arr = []
        return self._items(arr), total, pages

    def _dur(self, s):
        try:
            s = int(s or 0)
        except Exception:
            return ''
        if s <= 0:
            return ''
        h, m, sec = s // 3600, s % 3600 // 60, s % 60
        return '%d:%02d:%02d' % (h, m, sec) if h else '%02d:%02d' % (m, sec)

    def _pic(self, u):
        u = str(u or '').strip()
        if not u:
            return ''
        m = _PIC_FIX.match(u)
        if m:
            return _PIC_ALT + m.group(1)
        return u

    def _items(self, arr):
        out, seen = [], set()
        for x in (arr or []):
            if not isinstance(x, dict):
                continue
            mid = str(x.get('movieid') or x.get('id') or '').strip()
            name = str(x.get('Topic') or x.get('title') or '').strip()
            if not mid or not name or mid in seen:
                continue
            seen.add(mid)
            out.append({
                'vod_id': mid,
                'vod_name': name,
                'vod_pic': self._pic(x.get('smallpic')),
                'vod_remarks': str(x.get('formatted_timesize')
                                   or self._dur(x.get('timesize')) or ''),
            })
        return out

    # ------------------------------------------------------------ \u64ad\u653e\u5730\u5740
    def _learn(self, url):
        """\u4ece\u7edd\u5bf9\u64ad\u653e URL \u5b66\u5230\u771f\u5b9e CDN \u57df\uff0c\u63d2\u5230\u5bf9\u5e94\u6c60\u9996\uff08\u81ea\u6108\u6362\u57df\uff09\u3002"""
        try:
            m = re.match(r'^(https?://[^/]+)(/.*)?$', url)
            if not m:
                return
            host, path = m.group(1), (m.group(2) or '')
            pool = self._m3u8_hosts if ('m3u8' in path.lower() or path.endswith('.m3u8')) \
                else self._mp4_hosts
            if host not in pool:
                pool.insert(0, host)
        except Exception:
            pass

    def _abs(self, v, pool):
        v = str(v or '').strip()
        if not v:
            return []
        if v.startswith('//'):
            return ['https:' + v]
        if v.startswith('http'):
            self._learn(v)
            return [v]
        if not v.startswith('/'):
            v = '/' + v
        return [h + v for h in pool]

    def _detail(self, mid):
        d = self._api_get('/movie/' + str(mid)) or {}
        return d.get('data') or {}

    def _cands(self, mid):
        mid = str(mid).strip()
        hit = self._cand.get(mid)
        if hit:
            return hit
        c = self._detail(mid)
        if not c:
            return []
        out = []
        for k in ('h264m3u8url', 'h264m3u8url2', 'h265m3u8url', 'h265m3u8url2'):
            for u in self._abs(c.get(k), self._m3u8_hosts):
                if u and u not in out:
                    out.append(u)
        for k in ('h264mp4url', 'h264mp4url2'):
            for u in self._abs(c.get(k), self._mp4_hosts):
                if u and u not in out:
                    out.append(u)
        self._cand[mid] = out
        if len(self._cand) > 400:
            for k in list(self._cand.keys())[:200]:
                self._cand.pop(k, None)
        return out

    def _alive(self, url):
        """\u53ea\u53d6\u524d 300 \u5b57\u8282\u5224\u6d3b\uff0c\u4e0d\u4e0b\u8f7d\u6574\u7247\uff08mp4 \u52a8\u8f84\u4e0a\u767e MB\uff09\u3002"""
        try:
            r = requests.get(url, headers={
                'User-Agent': _UA,
                'Referer': str(getattr(self, 'host', self.site)) + '/',
            }, timeout=8, stream=True)
            try:
                if r.status_code != 200:
                    return False
                head = r.raw.read(300)
            finally:
                try:
                    r.close()
                except Exception:
                    pass
            if not head:
                return False
            if head[:7] == b'#EXTM3U':
                return True
            if head[4:8] == b'ftyp' or head[:3] == b'\xff\xd8\xff':
                return True
            return False
        except Exception:
            return False

    # ------------------------------------------------------------ \u516d\u63a5\u53e3
    def homeContent(self, filter):
        cls = [{'type_id': 'new', 'type_name': '\u6700\u65b0'}]
        cls += [{'type_id': t, 'type_name': n} for t, n in _CATS]
        lst = []
        try:
            lst, _, _ = self._list('new', 1)
        except Exception:
            try:
                self._ensure_host()
                lst, _, _ = self._list('new', 1)
            except Exception:
                lst = []
        return {'class': cls, 'list': lst}

    def homeVideoContent(self):
        try:
            lst, _, _ = self._list('new', 1)
        except Exception:
            lst = []
        return {'list': lst}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            pg = int(pg or 1)
        except Exception:
            pg = 1
        if pg < 1:
            pg = 1
        try:
            lst, total, pages = self._list(tid, pg)
        except Exception:
            try:
                self._ensure_host()
                lst, total, pages = self._list(tid, pg)
            except Exception:
                lst, total, pages = [], 0, pg
        return {'list': lst, 'page': pg, 'pagecount': pages,
                'limit': _PAGE_SIZE, 'total': total}

    def detailContent(self, ids):
        mid = str((ids or [''])[0]).strip()
        if not mid:
            return {'list': []}
        try:
            c = self._detail(mid)
        except Exception:
            c = {}
        name = str(c.get('Topic') or mid).strip()
        tag = str(c.get('tagname') or '').strip()
        self._cands(mid)      # \u9884\u70ed\u64ad\u653e\u5019\u9009\uff0c\u8be6\u60c5\u9875\u8fdb\u5165\u65f6\u4e0d\u5fc5\u518d\u7b49\u4e00\u6b21\u63a5\u53e3
        return {'list': [{
            'vod_id': mid,
            'vod_name': name,
            'vod_pic': self._pic(c.get('smallpic')),
            'type_name': tag,
            'vod_remarks': self._dur(c.get('timesize')),
            'vod_year': str(c.get('release_date') or c.get('UpdateTime') or '')[:10],
            'vod_area': '',
            'vod_actor': tag,
            'vod_director': '',
            'vod_content': name,
            'vod_play_from': '\u793e\u533a\u89c6\u9891',
            'vod_play_url': '\u6b63\u7247$' + mid,   # \u771f\u5730\u5740\u5728 playerContent \u73b0\u53d6\uff08\u9700\u63a2\u6d3b\u9009\u8def\uff09
        }]}

    def searchContent(self, key, quick, pg='1'):
        try:
            pg = int(pg or 1)
        except Exception:
            pg = 1
        self._key_sync()
        try:
            d = self._api_get('/movie/list',
                              {'page': pg, 'pageSize': _PAGE_SIZE, 'keyword': str(key or '')}) or {}
        except Exception:
            d = {}
        arr = d.get('data') or []
        try:
            total = int(d.get('total') or 0)
        except Exception:
            total = 0
        pages = max(1, int((total + _PAGE_SIZE - 1) / _PAGE_SIZE)) if total else pg
        if pg > pages:
            arr = []
        return {'list': self._items(arr), 'page': pg, 'pagecount': pages,
                'limit': _PAGE_SIZE, 'total': total}

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    def playerContent(self, flag, id, vipFlags):
        mid = str(id or '').strip()
        try:
            cands = self._cands(mid)
        except Exception:
            cands = []
        url = ''
        for u in cands:
            if self._alive(u):
                url = u
                break
        if not url and cands:
            url = cands[0]
        headers = {'User-Agent': _UA, 'Referer': str(getattr(self, 'host', self.site)) + '/'}
        if not url:
            return {'parse': 1, 'playUrl': '', 'url': mid, 'header': headers}
        return {'parse': 0, 'playUrl': '', 'url': url, 'header': headers}

    def localProxy(self, param):
        return None
