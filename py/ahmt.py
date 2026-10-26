# coding=utf-8
#!/usr/bin/python
# ============================================================================
#  \u6697\u591c\u871c\u6843 \u00b7 honeypeach.cc   \u2014\u2014 TVBox / \u8702\u871c\u5f71\u89c6 \u4e13\u7528 Python \u6e90 (type 3)
# ----------------------------------------------------------------------------
#  \u8986\u76d6\u5206\u7ec4(\u7ad9\u70b9\u9996\u9875\u6709\u51e0\u4e2a\u5c31\u63a5\u51e0\u4e2a):
#     \ud83d\udd34 \u871c\u6843\u76f4\u64ad   \ud83c\udfac \u871c\u6843\u77ed\u5267   \ud83d\udc8b \u64e6\u8fb9\u77ed\u5267   \ud83d\udcfa \u871c\u6843\u89c6\u9891
#     \ud83c\udfad \u871c\u6843\u52a8\u6f2b   \ud83c\udde8\ud83c\uddf3 \u56fd\u4ea7\u7cbe\u54c1   \ud83c\udf49 \u9ed1\u6599\u5403\u74dc
#
#  \u63a5\u53e3(\u7ad9\u70b9\u524d\u7aef\u516c\u5f00\u63a5\u53e3):
#     GET /api/handshake?dev=xxx        \u2192 \u4e0b\u53d1 {sid, skey, exp},\u4e4b\u540e /api/* \u5fc5\u987b\u5e26\u7b7e\u540d
#     \u7b7e\u540d\u5934: X-Hp-Sid / X-Hp-Ts / X-Hp-Nonce / X-Hp-Sign
#     canon = method + "\n" + path + "\n" + query + "\n" + sha256(body) + "\n"
#             + ts + "\n" + nonce + "\n" + sid      (HMAC-SHA256,key = skey \u7684\u5b57\u8282)
#
#     \u9996\u9875   /api/home
#     \u5206\u7c7b   /api/cats?key=&v=3
#     \u5217\u8868   /api/module?key=&cat=&src=&sub=&page=
#     \u8be6\u60c5   /api/detail/<key>/<id>?src=
#     \u64ad\u653e   /api/play/<key>/<id>/<ep>?src=      \u2192 {src, src_proxy, type}
#     \u641c\u7d22   /api/search?key=&kw=&page=          (\u76f4\u64ad / \u9ed1\u6599\u4e0d\u5f00\u653e\u641c\u7d22)
#     \u5f39\u5e55   /api/comments/live/<\u4e3b\u64adid>
#
#  \u64ad\u653e\u7ebf\u8def:\u6bcf\u6761\u7ed9\u4e09\u8def \u2014\u2014 \u2460 \u7ad9\u5185\u76f4\u8fde \u2461 \u7ad9\u5185\u4e2d\u8f6c \u2462 \u672c\u5730\u667a\u80fd\u8f6c\u53d1\u3002
#     \u64ad\u653e\u5730\u5740\u91cc\u7684\u7968\u636e t= \u5927\u7ea6 3 \u5206\u949f\u4f5c\u5e9f,\u2462 \u6bcf\u6b21\u8bf7\u6c42\u90fd\u91cd\u65b0\u53d6\u7968,
#     \u957f\u65f6\u95f4\u6302\u7740\u770b / \u53cd\u590d\u62c9\u8fdb\u5ea6\u6761\u90fd\u4e0d\u4f1a\u5931\u6548;\u67d0\u6761\u4e0d\u7075\u5207\u4e0b\u4e00\u6761\u5373\u53ef\u3002
#
#  \u9650\u6d41\u81ea\u6108(\u91cd\u8981):
#     \u7ad9\u70b9\u5bf9\u6bcf\u4e2a\u4f1a\u8bdd(sid)\u6709\u8bf7\u6c42\u914d\u989d,\u8d85\u4e86\u63a5\u53e3\u4f1a\u56de err=rl_sid\u3002
#     \u8868\u73b0\u5c31\u662f\u5206\u7ec4\u70b9\u8fdb\u53bb\u5168\u662f\u7a7a\u767d\u3002\u672c\u6e90\u9047\u5230\u9650\u6d41\u4f1a\u81ea\u52a8\u6362\u4f1a\u8bdd\u91cd\u7b7e\u5e76\u91cd\u653e,
#     \u540c\u65f6\u5206\u7c7b\u8868 / \u9996\u9875\u6a21\u5757 / \u5217\u8868\u7ed3\u679c\u90fd\u5e26\u7f13\u5b58,\u6b63\u5e38\u60c5\u51b5\u4e0b\u70b9\u5206\u7ec4\u51e0\u4e4e\u4e0d\u6d88\u8017\u914d\u989d\u3002
#
#  \u914d\u7f6e(\u5199\u5728\u914d\u7f6e json \u7684 ext \u91cc,\u4e0d\u5199\u5c31\u7528\u9ed8\u8ba4\u503c):
#     {
#       "host": "https://honeypeach.cc",   // \u6362\u57df\u540d
#       "ua": "...",                       // \u6362 UA
#       "danmaku": true,                    // \u76f4\u64ad\u5f39\u5e55\u5f00\u5173
#       "timeout": 15,                      // \u5355\u6b21\u8bf7\u6c42\u8d85\u65f6(\u79d2)
#       "cache": true,                      // \u5173\u6389=\u4e0d\u5403\u672c\u5730\u7f13\u5b58
#       "filters": true,                    // \u5173\u6389=\u5404\u5206\u7ec4\u4e0d\u5e26\u7b5b\u9009\u4e0b\u62c9(\u6392\u969c\u7528)
#       "video_filters": true               // \u5173\u6389=\u871c\u6843\u89c6\u9891\u4e0d\u5e26 \u7c7b\u578b/\u5973\u4f18/\u53d1\u884c\u5546
#     }
# ============================================================================

import hashlib
import hmac
import json
import os
import random
import re
import string
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.append('..')

try:
    from base.spider import Spider as BaseSpider
except Exception:
    class BaseSpider(object):
        def log(self, msg):
            pass

try:
    import requests
except Exception:
    requests = None


# ------------------------------ \u5e38\u91cf ----------------------------------------

DEFAULT_HOST = "https://honeypeach.cc"

UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")

# \u5206\u7ec4\u6e05\u5355(key, \u515c\u5e95\u540d)\u3002\u7ad9\u70b9 /api/home \u62c9\u4e0d\u5230\u65f6\u4e5f\u80fd\u6b63\u5e38\u51fa\u5206\u7ec4\u3002
MODULES = [
    ("live", "\U0001f534\u871c\u6843\u76f4\u64ad"),
    ("duanju", "\U0001f3ac\u871c\u6843\u77ed\u5267"),
    ("caibian", "\U0001f48b\u64e6\u8fb9\u77ed\u5267"),
    ("video", "\U0001f4fa\u871c\u6843\u89c6\u9891"),
    ("shortv", "\U0001f3ad\u871c\u6843\u52a8\u6f2b"),
    ("guochan", "\U0001f1e8\U0001f1f3\u56fd\u4ea7\u7cbe\u54c1"),
    ("heiliao", "\U0001f349\u9ed1\u6599\u5403\u74dc"),
]
VALID_KEYS = tuple(k for k, _ in MODULES)

# \u80fd\u641c\u7d22\u7684\u5206\u7ec4(\u5176\u4f59\u540e\u7aef\u4f1a 400)
SEARCH_MODULES = ["video", "duanju", "caibian", "shortv", "guochan"]

# \u77ed\u5267\u7c7b\u5206\u7ec4\u7684\u9ed8\u8ba4\u4e0a\u6e38(\u8be6\u60c5 / \u64ad\u653e\u5fc5\u987b\u5e26\u5bf9,\u5426\u5219\u62ff\u4e0d\u5230\u96c6\u6570\u548c\u5730\u5740)
DEFAULT_SRC = {
    "duanju": "huangguo",
    "caibian": "huangdou",
    "heiliao": "huangdou",
}

# /cover/<x>? \u91cc\u80fd\u51fa\u73b0\u7684\u4e0a\u6e38\u540d,\u53ef\u7528\u6765\u53cd\u63a8\u771f\u5b9e src
SRC_NAMES = ("huangguo", "huangdou", "\u006d\u0069\u0073\u0073\u0061\u0076", "dongman", "guochan", "video")

# \u5206\u7ec4\u9ed8\u8ba4\u5206\u7c7b(\u62ff\u4e0d\u5230 /api/cats \u65f6\u515c\u5e95)
DEFAULT_CAT = {
    "live": "girls",
    "duanju": "tuijian",
    "caibian": "0",
    "video": "new",
    "shortv": "all",
    "guochan": "",
    "heiliao": "0",
}


# ------------------------------ \u5c0f\u5de5\u5177 --------------------------------------

def _s(v):
    """\u4efb\u4f55\u503c \u2192 \u5e72\u51c0\u5b57\u7b26\u4e32\u3002"""
    if v is None:
        return ''
    if isinstance(v, (dict, list, tuple)):
        return ''
    return str(v).strip()


def _as_dict(v):
    """extend \u53c2\u6570\u5f52\u4e00\u5316:None / \u7a7a\u4e32 / JSON \u5b57\u7b26\u4e32 / URL \u7f16\u7801 JSON / dict / list \u5168\u5403\u3002"""
    if isinstance(v, dict):
        return v
    if isinstance(v, (list, tuple)):
        # \u5c11\u6570\u5185\u6838\u4f1a\u4f20 [{key,value}] \u8fd9\u79cd\u7ed3\u6784
        out = {}
        for it in v:
            if isinstance(it, dict):
                k = it.get('key') or it.get('k')
                val = it.get('value', it.get('v'))
                if k:
                    out[str(k)] = val
        return out
    if isinstance(v, str):
        t = v.strip()
        if not t:
            return {}
        for cand in (t, urllib.parse.unquote(t)):
            if cand[:1] in '{[':
                try:
                    d = json.loads(cand)
                    if isinstance(d, dict):
                        return d
                except Exception:
                    pass
        return {}
    return {}


def _to_int(v, dft=0, low=None, high=None):
    try:
        n = int(float(str(v).strip()))
    except Exception:
        n = dft
    if low is not None and n < low:
        n = low
    if high is not None and n > high:
        n = high
    return n


def _looks_like_garbage(v):
    """\u5224\u65ad\u4e00\u4e2a\u7b5b\u9009\u503c\u662f\u4e0d\u662f JSON \u4e32\u88ab\u5f53\u5b57\u7b26\u4e32\u7528\u5269\u4e0b\u7684\u5783\u573e\u3002"""
    t = _s(v)
    if not t:
        return False
    if any(c in t for c in '{}\'"') and ':' in t:
        return True
    if ' ' in t and (',' in t or ':' in t):
        return True
    return len(t) > 60


# ------------------------------ \u4e3b\u4f53 ----------------------------------------

class Spider(BaseSpider):

    # ---- \u7c7b\u7ea7\u9ed8\u8ba4\u503c:\u5373\u4f7f init() \u6ca1\u88ab\u8c03\u3001\u6216\u5b9e\u4f8b\u88ab\u5e76\u53d1\u4f7f\u7528,\u4e5f\u4e0d\u4f1a\u6709\u5c5e\u6027\u7f3a\u5931 ----
    host = DEFAULT_HOST
    ua = UA
    timeout = 15
    danmaku_on = True
    filters_on = True
    video_filters_on = True

    _ready = False
    _sid = ""
    _skey = b""
    _skexp = 0
    _dev = ""
    _sess = None
    _boot_lock = threading.RLock()

    # ---------------- \u542f\u52a8 / \u914d\u7f6e ----------------

    def _ensure(self):
        """\u5e42\u7b49\u521d\u59cb\u5316:\u6807\u5fd7\u4f4d\u6700\u540e\u624d\u7f6e\u4f4d,\u907f\u514d\u5e76\u53d1\u4e0b\u62ff\u5230\u534a\u6210\u54c1\u5b9e\u4f8b\u3002"""
        if self._ready:
            return
        with Spider._boot_lock:
            if self._ready:
                return
            self._sid = _s(getattr(self, '_sid', ''))
            self._skey = self._skey if isinstance(self._skey, bytes) else b''
            self._skexp = _to_int(getattr(self, '_skexp', 0), 0)
            self._sign_lock = threading.RLock()
            self._cat_cache = {}
            self._cat_lock = threading.RLock()
            self._home_cache = None
            self._filter_defaults = {}   # \u5206\u7ec4 \u2192 {\u7b5b\u9009\u952e: \u9ed8\u8ba4\u503c}(\u5224\u65ad\u4e0b\u62c9\u662f\u5426\u88ab\u6539\u8fc7)
            self._cat_defaults = {}      # \u5206\u7ec4 \u2192 (\u5206\u7c7b, \u4e0a\u6e38, sub)
            self._api_cache = {}         # \u63a5\u53e3\u7ed3\u679c\u7f13\u5b58(\u5e26 TTL)
            self._disk_done = False
            self._last_err = ''
            self._ready = True

    def init(self, extend="", ext=None, *args, **kwargs):
        self._ensure()
        if ext is None:
            ext = kwargs.get('extend')
        cfg = {}
        if isinstance(extend, dict):
            cfg = extend
        elif isinstance(extend, str) and extend.strip():
            cfg = _as_dict(extend)
        if isinstance(ext, dict):
            cfg = dict(cfg)
            cfg.update(ext)
        elif isinstance(ext, str) and ext.strip():
            d = _as_dict(ext)
            cfg = dict(cfg)
            cfg.update(d)

        host = _s(cfg.get('host') or cfg.get('site') or cfg.get('domain'))
        if host:
            if not host.startswith('http'):
                host = 'https://' + host
            self.host = host.rstrip('/')
        ua = _s(cfg.get('ua'))
        if ua:
            self.ua = ua
        self.timeout = _to_int(cfg.get('timeout') or 15, 15, 3, 60)
        self.danmaku_on = bool(cfg.get('danmaku', True))
        # filters=false \u65f6\u4e0d\u51fa\u7b5b\u9009\u4e0b\u62c9(\u4e2a\u522b\u5185\u6838\u7b5b\u9009\u89e3\u6790\u6709\u6bdb\u75c5\u7684\u6392\u969c\u5f00\u5173)
        self.filters_on = bool(cfg.get('filters', True))
        self.video_filters_on = bool(cfg.get('video_filters', True))
        # cache=false \u65f6\u4e0d\u5403\u672c\u5730\u7f13\u5b58(\u7ad9\u70b9\u6539\u7248\u540e\u60f3\u7acb\u523b\u770b\u5230\u65b0\u6570\u636e\u65f6\u7528)
        self.cache_on = bool(cfg.get('cache', True))
        self.log('\u6697\u591c\u871c\u6843 \u00b7 \u6e90\u5df2\u52a0\u8f7d host=%s' % self.host)

    def getName(self):
        return "\u6697\u591c\u871c\u6843"

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def destroy(self):
        try:
            if getattr(self, '_sess', None) is not None:
                self._sess.close()
        except Exception:
            pass
        return None

    # ---------------- \u7f51\u7edc\u5c42 ----------------

    def _session(self):
        s = getattr(self, '_sess', None)
        if s is not None:
            return s
        if requests is None:
            self._sess = None
            return None
        try:
            s = requests.Session()
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            rt = Retry(total=2, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
            ad = HTTPAdapter(max_retries=rt, pool_connections=10, pool_maxsize=20)
            s.mount('http://', ad)
            s.mount('https://', ad)
            self._sess = s
        except Exception:
            self._sess = None
        return self._sess

    def _req(self, url, headers=None, data=None, method=None, timeout=None):
        """\u8fd4\u56de (status, bytes);\u4efb\u4f55\u5f02\u5e38\u90fd\u541e\u6389\u8f6c\u6210 (0, b'')\u3002"""
        h = {"User-Agent": self.ua, "Accept": "application/json, text/plain, */*"}
        if headers:
            h.update(headers)
        to = timeout or self.timeout
        sess = self._session()
        if sess is not None:
            try:
                r = sess.request(method or ("POST" if data else "GET"), url,
                                 headers=h, data=data, timeout=to, allow_redirects=True)
                return r.status_code, r.content
            except Exception as e:
                self.log('\u8bf7\u6c42\u5931\u8d25 %s: %s' % (url.split('?')[0], e))
                return 0, b''
        try:
            rq = urllib.request.Request(url, headers=h, data=data, method=method)
            with urllib.request.urlopen(rq, timeout=to) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            try:
                return e.code, e.read()
            except Exception:
                return e.code, b''
        except Exception as e:
            self.log('\u8bf7\u6c42\u5931\u8d25 %s: %s' % (url.split('?')[0], e))
            return 0, b''

    def _json(self, url, headers=None, timeout=None):
        st, body = self._req(url, headers=headers, timeout=timeout)
        if not body:
            return {}
        try:
            d = json.loads(body.decode('utf-8', 'replace'))
            return d if isinstance(d, dict) else {}
        except Exception:
            return {}

    # ---------------- \u63e1\u624b / \u7b7e\u540d ----------------

    def _dev_file(self, name):
        """\u914d\u7f6e/\u7f13\u5b58\u6587\u4ef6\u843d\u70b9:\u4f18\u5148\u8ddf\u6e90\u540c\u76ee\u5f55,\u4e0d\u53ef\u5199\u5c31\u9000\u5230\u4e34\u65f6\u76ee\u5f55\u3002"""
        base = getattr(self, '_dev_dir', None)
        if base is None:
            base = ''
            cands = []
            try:
                cands.append(os.path.dirname(os.path.abspath(__file__)))
            except Exception:
                pass
            try:
                import tempfile
                cands.append(tempfile.gettempdir())
            except Exception:
                pass
            cands += [os.path.expanduser('~'), os.getcwd(), '/sdcard']
            for cand in cands:
                try:
                    if not cand or not os.path.isdir(cand):
                        continue
                    probe = os.path.join(cand, '.hani.w')
                    fh = open(probe, 'w')
                    fh.write('1')
                    fh.close()
                    os.remove(probe)
                    base = cand
                    break
                except Exception:
                    continue
            self._dev_dir = base
        return os.path.join(base, name) if base else ''

    def _dev_id(self):
        if self._dev:
            return self._dev
        path = self._dev_file('.hani.dev')
        if path:
            try:
                if os.path.exists(path):
                    d = open(path, 'r').read().strip()
                    if d:
                        self._dev = d
                        return d
            except Exception:
                pass
        d = 'zp' + ''.join(random.choice(string.ascii_lowercase + string.digits)
                           for _ in range(24))
        if path:
            try:
                fh = open(path, 'w')
                fh.write(d)
                fh.close()
            except Exception:
                pass
        self._dev = d
        return d

    # \u63e1\u624b\u7ed3\u679c\u843d\u76d8:\u67d0\u4e9b\u5185\u6838\u6bcf\u4e2a\u8bf7\u6c42\u65b0\u5efa\u5b9e\u4f8b,\u8fd9\u6837\u4e0d\u7528\u53cd\u590d\u63e1\u624b
    def _load_sign_cache(self):
        path = self._dev_file('.hani.sk')
        if not path:
            return False
        try:
            if not os.path.exists(path):
                return False
            parts = open(path, 'r').read().strip().split('|')
            if len(parts) != 4:
                return False
            dev, sid, key, exp = parts
            if dev != self._dev_id():
                return False
            if _to_int(exp, 0) - 180 < time.time():
                return False
            self._sid = sid
            self._skey = bytes.fromhex(key)
            self._skexp = _to_int(exp, 0)
            return bool(self._sid and self._skey)
        except Exception:
            return False

    def _save_sign_cache(self):
        path = self._dev_file('.hani.sk')
        if not path:
            return
        try:
            fh = open(path, 'w')
            fh.write('%s|%s|%s|%s' % (self._dev_id(), self._sid,
                                      self._skey.hex(), self._skexp))
            fh.close()
        except Exception:
            pass

    def _handshake(self, force_new_dev=False):
        """\u63e1\u624b;\u5931\u8d25\u81ea\u52a8\u91cd\u8bd5,\u4efb\u4f55\u60c5\u51b5\u90fd\u4e0d\u5f80\u5916\u629b\u5f02\u5e38\u3002"""
        if force_new_dev:
            self._dev = ''
            self._dev_id()
        last = ''
        for attempt in range(3):
            try:
                url = self.host + '/api/handshake?dev=' + urllib.parse.quote(self._dev_id())
                d = self._json(url, timeout=min(self.timeout, 12))
                if d.get('skey') and d.get('sid'):
                    self._sid = _s(d.get('sid'))
                    self._skey = bytes.fromhex(_s(d.get('skey')))
                    self._skexp = _to_int(d.get('exp'), 0)
                    self._save_sign_cache()
                    return True
                last = _s(d.get('err')) or 'skey/sid \u4e3a\u7a7a'
            except Exception as e:
                last = str(e)
            time.sleep(0.3 * (attempt + 1))
        self.log('\u63e1\u624b\u5931\u8d25: %s' % last)
        return False

    def _ensure_sign(self, force=False):
        with self._sign_lock:
            if self._skey and not force and time.time() < (self._skexp - 120):
                return True
            if not force and not self._skey and self._load_sign_cache():
                return True
            if self._handshake(force_new_dev=force):
                return True
            # \u518d\u515c\u4e00\u6b21:\u6362\u4e2a\u8bbe\u5907\u53f7\u91cd\u65b0\u63e1\u624b(\u907f\u5f00\u670d\u52a1\u7aef\u5bf9\u5355\u4e2a dev \u7684\u5076\u53d1\u62d2\u7edd)
            if not force:
                return self._handshake(force_new_dev=True)
            return False

    # \u7ad9\u70b9\u6709\u6309\u4f1a\u8bdd(sid)\u7684\u9650\u6d41:\u88ab\u9650\u65f6\u63a5\u53e3\u4f1a\u56de err=rl_sid\u3002\u6362\u4e00\u4e2a\u8bbe\u5907\u53f7\u91cd\u65b0\u63e1\u624b
    # \u7acb\u523b\u5c31\u80fd\u6062\u590d,\u6240\u4ee5\u8fd9\u91cc\u9047\u5230\u9650\u6d41\u5c31\u8f6e\u6362\u7b7e\u540d\u518d\u91cd\u653e\u3002
    RL_ERRS = ('rl_sid', 'rl_dev', 'rl_ip', 'rl', 'rate', 'limit', 'toomany', 'busy')
    # \u7f13\u5b58\u65f6\u957f(\u79d2):\u64ad\u653e\u5730\u5740\u5e26\u7968\u636e,\u7edd\u4e0d\u80fd\u7f13\u5b58;\u5217\u8868\u77ed\u7f13\u5b58;\u5206\u7c7b/\u9996\u9875\u6a21\u5757\u957f\u7f13\u5b58
    CACHE_TTL = {
        '/api/home': 21600,
        '/api/cats': 21600,
        '/api/module': 90,
        '/api/detail': 600,
        '/api/search': 120,
        '/api/comments': 3,
    }

    def _rotate_dev(self):
        """\u6362\u4e00\u4e2a\u8bbe\u5907\u53f7(\u76f8\u5f53\u4e8e\u6362\u4f1a\u8bdd,\u7ed5\u5f00\u6309 sid \u7684\u9650\u6d41)\u3002"""
        with self._sign_lock:
            self._dev = 'zp' + ''.join(random.choice(string.ascii_lowercase + string.digits)
                                       for _ in range(24))
            path = self._dev_file('.hani.dev')
            if path:
                try:
                    fh = open(path, 'w')
                    fh.write(self._dev)
                    fh.close()
                except Exception:
                    pass
            self._sid = ''
            self._skey = b''
            self._skexp = 0
        return True

    def _sign(self, path, params):
        """\u5355\u6b21\u7b7e\u540d\u8bf7\u6c42,\u8fd4\u56de (data, err)\u3002"""
        p = {}
        for k, v in (params or {}).items():
            v = _s(v)
            if v == '':
                continue
            p[k] = v
        qs = urllib.parse.urlencode(p)
        if not self._ensure_sign():
            return {}, 'nosign'
        ts = str(int(time.time()))
        nonce = ''.join(random.choice(string.ascii_lowercase + string.digits)
                        for _ in range(16))
        bh = hashlib.sha256(b'').hexdigest()
        canon = "GET\n%s\n%s\n%s\n%s\n%s\n%s" % (path, qs, bh, ts, nonce, self._sid)
        sig = hmac.new(self._skey, canon.encode('utf-8'), hashlib.sha256).hexdigest()
        url = self.host + path + (('?' + qs) if qs else '')
        st, body = self._req(url, headers={
            "X-Hp-Sid": self._sid,
            "X-Hp-Ts": ts,
            "X-Hp-Nonce": nonce,
            "X-Hp-Sign": sig,
            "Referer": self.host + '/',
        })
        d = {}
        if body:
            try:
                d = json.loads(body.decode('utf-8', 'replace'))
            except Exception:
                d = {}
        if not isinstance(d, dict):
            d = {}
        err = _s(d.get('err'))
        if not err and st == 429:
            err = 'rl_sid'
        self._last_err = err
        return d, err

    def _cache_ttl(self, path):
        for pfx, ttl in self.CACHE_TTL.items():
            if path.startswith(pfx):
                return ttl
        return 0

    def _cache_key(self, path, params):
        items = sorted((_s(k), _s(v)) for k, v in (params or {}).items() if _s(v))
        return path + '?' + '&'.join('%s=%s' % kv for kv in items)

    def _cache_get(self, key, allow_stale=False):
        c = getattr(self, '_api_cache', None) or {}
        hit = c.get(key)
        if not hit:
            return None
        ts, ttl, data = hit
        age = time.time() - ts
        if age <= ttl:
            return data
        if allow_stale and age <= 1800:      # \u88ab\u9650\u6d41\u65f6,30 \u5206\u949f\u5185\u7684\u65e7\u6570\u636e\u4e5f\u80fd\u9876\u4e00\u4e0b
            return data
        return None

    def _cache_put(self, key, data, ttl):
        if ttl <= 0 or not isinstance(data, dict) or not data:
            return
        if not (data.get('list') or data.get('cats') or data.get('modules')):
            return                            # \u7a7a\u7ed3\u679c\u4e0d\u8fdb\u7f13\u5b58
        c = getattr(self, '_api_cache', None)
        if c is None:
            c = self._api_cache = {}
        if len(c) > 400:
            c.clear()
        c[key] = (time.time(), ttl, data)
        if key.startswith('/api/cats') or key.startswith('/api/home'):
            self._disk_put(key, data)

    # \u5206\u7c7b\u8868 / \u9996\u9875\u6a21\u5757 / \u9996\u9875\u7b5b\u9009 \u843d\u76d8:\u4e0b\u6b21\u542f\u52a8\u76f4\u63a5\u590d\u7528,\u9996\u9875\u51e0\u4e4e\u4e0d\u53d1\u8bf7\u6c42
    def _disk_path(self):
        return self._dev_file('.hani.cache.json')

    def _disk_raw(self):
        path = self._disk_path()
        if not path or not os.path.exists(path):
            return {}
        try:
            raw = json.loads(open(path, 'r').read() or '{}')
            return raw if isinstance(raw, dict) else {}
        except Exception:
            return {}

    def _disk_load(self):
        if getattr(self, '_disk_done', False):
            return
        self._disk_done = True
        c = getattr(self, '_api_cache', None)
        if c is None:
            c = self._api_cache = {}
        now = time.time()
        for k, v in self._disk_raw().items():
            if k.startswith('/api/') and isinstance(v, list) and len(v) == 3:
                ts, ttl, data = v
                if isinstance(data, dict) and now - _to_int(ts, 0) <= _to_int(ttl, 0):
                    c[k] = (ts, ttl, data)

    def _disk_set(self, key, data, ttl):
        path = self._disk_path()
        if not path:
            return
        try:
            raw = self._disk_raw()
            raw[key] = [time.time(), ttl, data]
            if len(raw) > 40:
                raw = dict(list(raw.items())[-40:])
            fh = open(path, 'w')
            fh.write(json.dumps(raw, ensure_ascii=False))
            fh.close()
        except Exception:
            pass

    def _disk_get(self, key, ttl):
        v = self._disk_raw().get(key)
        if not v:
            return None
        if not (isinstance(v, list) and len(v) == 3):
            return None
        ts, t, data = v
        if time.time() - _to_int(ts, 0) > _to_int(t, ttl):
            return None
        return data

    def _disk_put(self, key, data):
        self._disk_set(key, data, self._cache_ttl(key) or 21600)

    def _api(self, path, params=None, _retry=1, _rotate=2):
        """\u5e26\u7b7e\u540d + \u7f13\u5b58 + \u9650\u6d41\u81ea\u6108\u7684 /api/* \u8bf7\u6c42\u3002\u5931\u8d25\u4e00\u5f8b\u8fd4\u56de {},\u7edd\u4e0d\u629b\u5f02\u5e38\u3002"""
        try:
            ttl = self._cache_ttl(path) if getattr(self, 'cache_on', True) else 0
            if ttl > 0:
                self._disk_load()
                ck = self._cache_key(path, params)
                hit = self._cache_get(ck)
                if hit is not None:
                    return hit
            else:
                ck = ''

            d, err = self._sign(path, params)

            if err in ('nosig', 'nosign', 'badsig', 'expired') and _retry > 0:
                self._ensure_sign(True)
                return self._api(path, params, _retry - 1, _rotate)

            if err in self.RL_ERRS and _rotate > 0:
                # \u88ab\u9650\u6d41:\u6362\u4f1a\u8bdd\u91cd\u6765(\u5b9e\u6d4b\u6362 dev \u91cd\u7b7e\u7acb\u5373\u6062\u590d)
                self.log('\u63a5\u53e3\u88ab\u9650\u6d41(%s),\u8f6e\u6362\u4f1a\u8bdd\u91cd\u8bd5' % err)
                self._rotate_dev()
                time.sleep(0.3)
                return self._api(path, params, _retry, _rotate - 1)

            if err:
                self.log('\u63a5\u53e3\u8fd4\u56de\u9519\u8bef %s: %s' % (path, err))
                if ck:
                    stale = self._cache_get(ck, allow_stale=True)
                    if stale is not None:
                        return stale
                return {}

            # \u7ad9\u70b9\u5728 IP \u7ea7\u9650\u6d41\u65f6\u4f1a"\u8fd4\u56de\u7a7a\u5217\u8868\u4f46\u4e0d\u62a5\u9519",\u8fd9\u65f6\u7528\u65e7\u7f13\u5b58\u9876\u4e0a,\u522b\u7ed9\u7528\u6237\u7a7a\u767d
            if ck and ttl > 0 and not (d.get('list') or d.get('cats') or d.get('modules')):
                stale = self._cache_get(ck, allow_stale=True)
                if stale is not None:
                    return stale

            if ck and ttl > 0:
                self._cache_put(ck, d, ttl)
            return d
        except Exception as e:
            self.log('\u63a5\u53e3\u5f02\u5e38 %s: %s' % (path, e))
            return {}

    def _api_list(self, path, params=None):
        d = self._api(path, params)
        lst = [x for x in (d.get('list') or []) if isinstance(x, dict)]
        return lst, d

    # ---------------- \u672c\u5730\u4ee3\u7406\u5730\u5740 ----------------

    def _px_base(self):
        try:
            u = self.getProxyUrl()
            if u:
                return str(u)
        except Exception:
            pass
        return 'http://127.0.0.1:9978/proxy'

    def _px(self, **kw):
        base = self._px_base()
        sep = '&' if '?' in base else '?'
        return base + sep + urllib.parse.urlencode(kw)

    # ---------------- \u5c0f\u5de5\u5177 ----------------

    def _abs(self, u):
        u = _s(u)
        if not u:
            return ''
        if u.startswith('//'):
            return 'https:' + u
        if u.startswith('/'):
            return self.host + u
        return u

    def _norm_tid(self, tid):
        """\u5206\u7ec4ID\u5f52\u4e00:key / \u4e2d\u6587\u540d / \u5e26 emoji \u7684\u540d\u5b57\u90fd\u80fd\u8ba4\u51fa\u6765\u3002"""
        t = _s(tid)
        if t in VALID_KEYS:
            return t
        for k, name in MODULES:
            if k and k in t:
                return k
        core = re.sub(r'[^0-9A-Za-z\u4e00-\u9fff]+', '', t)
        if core:
            for k, name in MODULES:
                n = re.sub(r'[^0-9A-Za-z\u4e00-\u9fff]+', '', name)
                if n and (n in core or core in n):
                    return k
        return t or 'video'

    def _pack(self, key, src, vid, ep):
        return "%s|%s|%s|%s" % (key, src or '', vid, ep if ep is not None else 1)

    def _split_vod(self, s):
        p = _s(s).split('|')
        if len(p) >= 3:
            return self._norm_tid(p[0]), p[1], p[2]
        return 'video', '', _s(s)

    def _split_play(self, s):
        p = _s(s).split('|')
        if len(p) >= 4:
            return self._norm_tid(p[0]), p[1], p[2], p[3]
        if len(p) == 3:
            return self._norm_tid(p[0]), p[1], p[2], '1'
        return 'video', '', _s(s), '1'

    def _guess_src(self, mod, item):
        """\u8be6\u60c5 / \u64ad\u653e\u5fc5\u987b\u5e26\u5bf9\u4e0a\u6e38 src;\u5217\u8868\u91cc\u6ca1\u6709\u5c31\u6309\u5c01\u9762\u8def\u5f84\u53cd\u63a8\u3002"""
        s = _s((item or {}).get('src'))
        if s:
            return s
        cov = _s((item or {}).get('cover'))
        m = re.match(r'^/cover/([^?/]+)\?', cov)
        if m:
            c = m.group(1)
            if c in ('huangguo', 'huangdou') and mod in ('duanju', 'caibian', 'heiliao'):
                return c
        return DEFAULT_SRC.get(mod, '')

    def _brief(self, mod, src, x):
        return {
            "vod_id": "%s|%s|%s" % (mod, src or '', _s(x.get('id'))),
            "vod_name": _s(x.get('title') or x.get('name')),
            "vod_pic": self._abs(x.get('cover')),
            "vod_remarks": _s(x.get('remark')),
            "vod_content": _s(x.get('desc')),
        }

    # ---------------- \u9996\u9875 / \u5206\u7c7b ----------------

    def _home_modules(self):
        if self._home_cache is not None:
            return self._home_cache
        out = {}
        try:
            d = self._api('/api/home')
            for m in (d.get('modules') or []):
                if isinstance(m, dict) and m.get('key'):
                    out[_s(m['key'])] = _s(m.get('icon')) + _s(m.get('name') or m['key'])
        except Exception as e:
            self.log('\u9996\u9875\u6a21\u5757\u62c9\u53d6\u5931\u8d25: %s' % e)
        self._home_cache = out
        return out

    def _cats_of(self, key):
        """\u5206\u7ec4\u5206\u7c7b\u8868;\u5e76\u53d1\u53ea\u62c9\u4e00\u6b21\u3002"""
        cache = getattr(self, '_cat_cache', None)
        if cache is None:
            cache = self._cat_cache = {}
        if key in cache:
            return cache[key]
        with self._cat_lock:
            if key in cache:
                return cache[key]
            cats = []
            try:
                d = self._api('/api/cats', {'key': key, 'v': 3}, )

                cats = [c for c in (d.get('cats') or []) if isinstance(c, dict)]
            except Exception as e:
                self.log('\u5206\u7c7b\u62c9\u53d6\u5931\u8d25 %s: %s' % (key, e))
            if cats:                     # \u7a7a\u7ed3\u679c(\u9650\u6d41/\u6296\u52a8)\u522b\u7f13\u5b58,\u4e0b\u6b21\u8fd8\u80fd\u91cd\u8bd5
                cache[key] = cats
            return cats

    def _default_cat(self, key):
        """\u8be5\u5206\u7ec4\u7684\u9ed8\u8ba4\u5206\u7c7b(\u7b2c\u4e00\u4e2a\u53ef\u7528\u5206\u7c7b)\u3002"""
        dft = getattr(self, '_cat_defaults', None)
        if dft is None:
            dft = self._cat_defaults = {}
        if key in dft:
            return dft[key]
        cat, src, sub = DEFAULT_CAT.get(key, ''), DEFAULT_SRC.get(key, ''), 0
        for c in self._cats_of(key):
            code = _s(c.get('code'))
            if code:
                cat = code
                src = _s(c.get('src')) or src
                sub = _to_int(c.get('sub'), 0)
                break
        dft[key] = (cat, src, sub)
        return dft[key]

    def _tag_options(self, cat_code, limit=200):
        """\u871c\u6843\u89c6\u9891\u7684\u300c\u7c7b\u578b / \u5973\u4f18 / \u53d1\u884c\u5546\u300d\u4e8c\u7ea7\u5165\u53e3\u3002"""
        out = []
        try:
            lst, _ = self._api_list('/api/module',
                                    {'key': 'video', 'cat': cat_code, 'page': 1})
            for x in lst:
                code = _s(x.get('code'))
                if not code:
                    continue
                out.append({"n": _s(x.get('name')) or code, "v": code})
                if len(out) >= limit:
                    break
        except Exception as e:
            self.log('\u4e8c\u7ea7\u5165\u53e3\u62c9\u53d6\u5931\u8d25 %s: %s' % (cat_code, e))
        return out

    def homeContent(self, filter=True):
        self._ensure()
        try:
            mods = self._home_modules()
            classes = []
            for key, fallback in MODULES:
                classes.append({"type_id": key,
                                "type_name": mods.get(key) or fallback})

            filters = {}
            if not self.filters_on:
                return {"class": classes, "filters": {}}

            # \u7b5b\u9009\u7ed3\u6784\u6574\u5757\u843d\u76d8\u7f13\u5b58:\u4e0b\u6b21\u542f\u52a8\u76f4\u63a5\u590d\u7528,\u4e0d\u518d\u6253\u90a3\u5341\u51e0\u4e2a\u8bf7\u6c42
            # (\u7ad9\u70b9\u6309\u4f1a\u8bdd\u9650\u6d41,\u9996\u9875\u8bf7\u6c42\u8d8a\u5c11\u8d8a\u7a33)
            if getattr(self, 'cache_on', True):
                cached = self._disk_get('home_filters', 21600)
                if isinstance(cached, dict) and cached:
                    for k, v in cached.items():
                        if isinstance(v, list) and v:
                            filters[k] = v
                            self._filter_defaults[k] = {
                                f.get('key'): (f.get('value') or [{}])[0].get('v')
                                for f in v if f.get('value')}
                    if len(filters) == len(MODULES):
                        return {"class": classes, "filters": filters}

            # \u5404\u5206\u7ec4\u5206\u7c7b\u8868\u5e76\u53d1\u62c9,\u907f\u514d\u9996\u5c4f\u88ab\u4e32\u884c\u8bf7\u6c42\u62d6\u8d85\u65f6
            boxes = {}

            def _work(k):
                try:
                    boxes[k] = self._cats_of(k)
                except Exception:
                    boxes[k] = []

            ts = [threading.Thread(target=_work, args=(k,)) for k, _ in MODULES]
            for t in ts:
                t.daemon = True
                t.start()
            for t in ts:
                t.join(8)

            for key, _ in MODULES:
                opts = []
                dflt = None
                for c in boxes.get(key) or []:
                    if c.get('kind') in ('tags', 'actress', 'todo'):
                        continue        # \u8fd9\u4e09\u4e2a\u662f\u4e8c\u7ea7\u5165\u53e3,\u5355\u72ec\u505a\u4e0b\u62c9
                    code = _s(c.get('code'))
                    label = _s(c.get('name')) or code or '\u5168\u90e8'
                    val = json.dumps({"c": code, "s": _s(c.get('src')),
                                      "b": _to_int(c.get('sub'), 0)},
                                     ensure_ascii=False)
                    if dflt is None:
                        dflt = val
                    opts.append({"n": label, "v": val})
                if not opts:
                    val = json.dumps({"c": DEFAULT_CAT.get(key, ''),
                                      "s": DEFAULT_SRC.get(key, ''), "b": 0},
                                     ensure_ascii=False)
                    opts = [{"n": "\u5168\u90e8", "v": val}]
                    dflt = val
                flt = [{"key": "cat", "name": "\u5206\u7c7b", "value": opts}]
                self._filter_defaults[key] = dict(self._filter_defaults.get(key) or {})
                self._filter_defaults[key]['cat'] = dflt or ''

                if key == 'video' and self.video_filters_on:
                    try:
                        for kk, nm, cc in (("tag", "\u7c7b\u578b", "genres"),
                                           ("actress", "\u5973\u4f18", "actresses-ranking"),
                                           ("maker", "\u53d1\u884c\u5546", "makers")):
                            vals = self._tag_options(cc)
                            if vals:
                                flt.append({"key": kk, "name": nm, "value": vals})
                                self._filter_defaults[key][kk] = vals[0]['v']
                    except Exception as e:
                        self.log('\u4e8c\u7ea7\u5165\u53e3\u6784\u5efa\u5931\u8d25: %s' % e)
                filters[key] = flt

            if getattr(self, 'cache_on', True) and len(filters) == len(MODULES):
                self._disk_set('home_filters', filters, 21600)
            return {"class": classes, "filters": filters}
        except Exception as e:
            self.log('homeContent \u5f02\u5e38: %s' % e)
            return {"class": [{"type_id": k, "type_name": n} for k, n in MODULES],
                    "filters": {}}

    def homeVideoContent(self):
        """\u9996\u9875\u63a8\u8350\u4f4d\u3002\u7ad9\u70b9\u6709\u6309\u4f1a\u8bdd\u9650\u6d41,\u8fd9\u91cc\u53ea\u53d1\u4e00\u6b21\u8bf7\u6c42,\u7701\u914d\u989d\u3002"""
        self._ensure()
        vlist = []
        try:
            for mod, cat in (('video', 'new'), ('duanju', 'tuijian'),
                             ('guochan', ''), ('shortv', 'all'), ('heiliao', '0')):
                lst, _ = self._api_list('/api/module',
                                        {'key': mod, 'cat': cat, 'page': 1,
                                         'src': DEFAULT_SRC.get(mod, '')})
                if lst:
                    for x in lst[:12]:
                        vlist.append(self._brief(mod, self._guess_src(mod, x), x))
                    break
                if getattr(self, '_last_err', ''):
                    break
        except Exception as e:
            self.log('\u63a8\u8350\u4f4d\u62c9\u53d6\u5931\u8d25: %s' % e)
        return {"list": vlist}

    def _parse_filter(self, key, extend):
        """\u628a\u5185\u6838\u4f20\u4e0b\u6765\u7684\u7b5b\u9009\u503c,\u89e3\u6790\u6210 (cat, src, sub)\u3002\u5404\u79cd\u4f20\u6cd5\u90fd\u5403\u5f97\u4e0b\u3002"""
        ext = _as_dict(extend)
        if not ext and isinstance(extend, str) and extend.strip():
            ext = {'cat': extend.strip()}          # \u88f8\u503c\u5f53\u5206\u7c7b\u7528

        def raw(k):
            v = ext.get(k)
            if isinstance(v, (list, tuple)):
                v = v[0] if v else ''
            return v

        tmp = {}
        for k in ('cat', 'tag', 'actress', 'maker'):
            v = raw(k)
            if isinstance(v, dict):                 # \u5185\u6838\u628a JSON \u89e3\u6790\u6210\u5bf9\u8c61\u4e86
                tmp[k] = _s(v.get('c') if v.get('c') is not None else v.get('code'))
                tmp[k + '_src'] = _s(v.get('s') or v.get('src'))
                tmp[k + '_sub'] = _to_int(v.get('b', v.get('sub')), 0)
                continue
            t = _s(v)
            if not t:
                continue
            if t[:1] in '{[' or '%7B' in t.upper():
                o = _as_dict(t)
                if o:
                    tmp[k] = _s(o.get('c') if o.get('c') is not None else o.get('code'))
                    tmp[k + '_src'] = _s(o.get('s') or o.get('src'))
                    tmp[k + '_sub'] = _to_int(o.get('b', o.get('sub')), 0)
                    continue
                m = re.search(r'["\']c["\']\s*:\s*["\']([^"\']*)["\']', t)
                if m:
                    tmp[k] = m.group(1)
                    continue
            if _looks_like_garbage(t):
                continue
            tmp[k] = t

        dflt = (getattr(self, '_filter_defaults', None) or {}).get(key) or {}
        picked, picked_k = '', ''
        # \u4e8c\u7ea7\u7b5b\u9009(\u7c7b\u578b/\u5973\u4f18/\u53d1\u884c\u5546)\u4f18\u5148\u4e8e\u666e\u901a\u5206\u7c7b,\u53ea\u8981\u5b83\u4e0d\u662f\u9ed8\u8ba4\u503c
        for k in ('tag', 'actress', 'maker'):
            v = tmp.get(k)
            if v and v != dflt.get(k):
                picked, picked_k = v, k
                break
        if not picked:
            c = tmp.get('cat')
            if c and (c != _json_cat(dflt.get('cat')) or not dflt.get('cat')):
                picked, picked_k = c, 'cat'
        if not picked:
            dc, dsrc, dsub = self._default_cat(key)
            return dc, dsrc, dsub
        src = tmp.get(picked_k + '_src') or ''
        sub = _to_int(tmp.get(picked_k + '_sub'), 0)
        if not src and picked_k == 'cat':
            src = DEFAULT_SRC.get(key, '')
        if picked_k != 'cat':
            src = ''          # \u4e8c\u7ea7\u5165\u53e3\u8d70\u5404\u81ea\u4e3b\u4e0a\u6e38
        return picked, src, sub

    def _empty_page(self, page):
        return {"list": [], "page": page, "pagecount": page,
                "limit": 30, "total": 0}

    def categoryContent(self, tid, pg="1", filter=None, extend=None, *args, **kwargs):
        try:
            self._ensure()
            key = self._norm_tid(tid)
            page = _to_int(pg, 1, 1)
            try:
                cat, src, sub = self._parse_filter(key, extend)
            except Exception as e:
                self.log('\u7b5b\u9009\u89e3\u6790\u5931\u8d25,\u6539\u7528\u9ed8\u8ba4: %s' % e)
                cat, src, sub = self._default_cat(key)

            plans = [(cat, src, sub)]
            if page == 1:
                dc, dsrc, dsub = self._default_cat(key)
                for p in ((dc, dsrc, dsub), ('', '', 0)):
                    if p not in plans:
                        plans.append(p)
            plans = plans[:3]

            first = None
            for (c, s, b) in plans:
                lst, d = self._api_list('/api/module',
                                        {'key': key, 'cat': c, 'src': s,
                                         'sub': b, 'page': page})
                if first is None:
                    first = d
                if lst:
                    vlist = [self._brief(key, _s(x.get('src')) or s, x) for x in lst]
                    pages = _to_int(d.get('pages'), 0, 0)
                    if pages > 0:
                        pagecount = pages
                    elif d.get('has_more'):
                        pagecount = page + 1
                    else:
                        pagecount = page
                    return {"list": vlist, "page": page, "pagecount": pagecount,
                            "limit": len(vlist), "total": pagecount * max(len(vlist), 1)}
                # \u88ab\u9650\u6d41 / \u7f51\u7edc\u9519\u5c31\u522b\u63a5\u7740\u5237\u4e86,\u5426\u5219\u53ea\u4f1a\u628a\u4f1a\u8bdd\u6253\u5f97\u66f4\u6b7b
                if getattr(self, '_last_err', ''):
                    self.log('\u5217\u8868\u62c9\u53d6\u53d7\u632b(%s),\u505c\u6b62\u515c\u5e95\u91cd\u8bd5' % self._last_err)
                    break

            # \u4e00\u6761\u90fd\u6ca1\u62ff\u5230:\u7b2c 1 \u9875\u7ed9\u4e2a\u7a7a\u9875\u63d0\u793a,\u7ffb\u9875\u8d8a\u754c\u5c31\u76f4\u63a5\u56de\u7a7a
            d = first or {}
            pagecount = _to_int(d.get('pages'), 0, 0) or page
            if page > 1 and pagecount >= page:
                pagecount = page
            return {"list": [], "page": page, "pagecount": pagecount,
                    "limit": 30, "total": 0}
        except Exception as e:
            self.log('categoryContent \u5f02\u5e38 %s: %s' % (tid, e))
            return self._empty_page(_to_int(pg, 1, 1))

    # ---------------- \u8be6\u60c5 ----------------

    def detailContent(self, array=None, *args, **kwargs):
        try:
            self._ensure()
            ids = ''
            if isinstance(array, (list, tuple)):
                ids = _s(array[0]) if array else ''
            else:
                ids = _s(array)
            if not ids:
                ids = _s(kwargs.get('ids') or kwargs.get('id'))
            if not ids:
                return {"list": []}

            key, src, vid = self._split_vod(ids)
            if not src:
                src = DEFAULT_SRC.get(key, '')
            params = {'src': src} if src else {}
            d = self._api('/api/detail/%s/%s' % (key, urllib.parse.quote(vid)), params)
            det = d.get('detail') or {}
            if not isinstance(det, dict) or not det:
                self.log('\u8be6\u60c5\u4e3a\u7a7a %s' % ids)
                return {"list": []}

            eps = det.get('episodes') or []
            ep_list = []
            for i, e in enumerate(eps):
                if not isinstance(e, dict):
                    continue
                ep = e.get('ep') or (i + 1)
                nm = _s(e.get('name')) or ('\u7b2c%s\u96c6' % ep)
                if e.get('lock') or e.get('vip') or e.get('price'):
                    nm = nm + '\U0001f512'
                ep_list.append("%s$%s" % (nm, self._pack(key, src, vid, ep)))
            if not ep_list:
                ep_list = ["\u64ad\u653e$%s" % self._pack(key, src, vid, 1)]

            vod = {
                "vod_id": ids,
                "vod_name": _s(det.get('title')),
                "vod_pic": self._abs(det.get('cover')),
                "vod_content": _s(det.get('desc')),
                "vod_remarks": _s(det.get('remark') or det.get('duration')),
                "vod_play_from": "\u76f4\u64ad" if key == 'live' else "\u871c\u6843",
                "vod_play_url": "#".join(ep_list),
            }
            if det.get('actor'):
                vod['vod_actor'] = _s(det.get('actor'))
            if det.get('area'):
                vod['vod_area'] = _s(det.get('area'))
            if det.get('tag'):
                vod['vod_tag'] = _s(det.get('tag'))
            if key == 'live' and det.get('viewers'):
                vod['vod_remarks'] = '\u5728\u7ebf %s \u4eba' % det.get('viewers')
            return {"list": [vod]}
        except Exception as e:
            self.log('detailContent \u5f02\u5e38: %s' % e)
            return {"list": []}

    # ---------------- \u641c\u7d22 ----------------

    def searchContent(self, key, quick=True, pg="1", *args, **kwargs):
        try:
            self._ensure()
            kw = _s(key)
            page = _to_int(pg, 1, 1)
            if not kw:
                return {"list": [], "page": page}
            out, seen = [], set()
            for mod in SEARCH_MODULES:
                lst, _ = self._api_list('/api/search', {'key': mod, 'kw': kw, 'page': page})
                for x in lst:
                    vid = _s(x.get('id'))
                    if not vid or vid in seen:
                        continue
                    seen.add(vid)
                    out.append(self._brief(mod, self._guess_src(mod, x), x))
            return {"list": out, "page": page}
        except Exception as e:
            self.log('searchContent \u5f02\u5e38: %s' % e)
            return {"list": [], "page": 1}

    # ---------------- \u64ad\u653e ----------------

    def _play_data(self, key, src, vid, ep, _retry=1):
        params = {'src': src} if src else {}
        d = self._api('/api/play/%s/%s/%s' % (key, urllib.parse.quote(vid), ep or '1'),
                      params)
        pl = d.get('play') or {}
        if not isinstance(pl, dict):
            pl = {}
        if not pl.get('src') and _retry > 0:
            time.sleep(0.5)
            return self._play_data(key, src, vid, ep, _retry - 1)
        return pl

    def playerContent(self, flag=None, id=None, vipFlags=None, *args, **kwargs):
        res = {"parse": 0}
        try:
            self._ensure()
            raw = _s(id)
            if raw and '%' in raw:
                try:
                    raw = urllib.parse.unquote(raw)
                except Exception:
                    pass
            key, src, vid, ep = self._split_play(raw)
            if not src:
                src = DEFAULT_SRC.get(key, '')
            if not ep:
                ep = '1'

            header = {"User-Agent": self.ua, "Referer": self.host + '/'}
            try:
                pl = self._play_data(key, src, vid, ep)
            except Exception as e:
                self.log('\u53d6\u64ad\u653e\u5730\u5740\u5931\u8d25 %s: %s' % (raw, e))
                pl = {}

            s = _s(pl.get('src'))
            px = _s(pl.get('src_proxy'))
            smart = self._px(type='hls', key=key, src=src, vid=vid, ep=ep)
            lines = []
            if s.startswith('/'):
                lines += ["\u7ebf\u8def\u4e00\u00b7\u76f4\u8fde", self.host + s]
                if px.startswith('/'):
                    lines += ["\u7ebf\u8def\u4e8c\u00b7\u4e2d\u8f6c", self.host + px]
                lines += ["\u7ebf\u8def\u4e09\u00b7\u667a\u80fd", smart]
            elif s:
                if px.startswith('/'):
                    lines += ["\u7ebf\u8def\u4e00\u00b7\u4e2d\u8f6c", self.host + px]
                lines += ["\u7ebf\u8def\u4e8c\u00b7\u76f4\u8fde", s]
                lines += ["\u7ebf\u8def\u4e09\u00b7\u667a\u80fd", smart]
            else:
                lines += ["\u7ebf\u8def\u4e00\u00b7\u667a\u80fd", smart]

            res["header"] = header
            if len(lines) >= 4:
                res["url"] = lines
            else:
                res["url"] = lines[1] if len(lines) > 1 else ''
            if key == 'live' and self.danmaku_on:
                res["danmaku"] = self._px(type='danmu', sid=vid)
            return res
        except Exception as e:
            self.log('playerContent \u5f02\u5e38: %s' % e)
            res["url"] = ''
            return res

    # ---------------- \u672c\u5730\u4ee3\u7406 ----------------

    def _xml_esc(self, s):
        return (_s(s).replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;').replace('"', '&quot;'))

    def _rewrite_m3u8(self, url):
        """\u628a\u64ad\u653e\u5217\u8868\u91cc\u7684\u76f8\u5bf9\u5730\u5740\u8865\u6210\u7edd\u5bf9\u5730\u5740\u3002"""
        st, body = self._req(url, headers={"Referer": self.host + '/'}, timeout=20)
        if st not in (200, 206) or not body:
            return None
        try:
            txt = body.decode('utf-8', 'replace')
        except Exception:
            return None
        if '#EXTM3U' not in txt:
            return None

        def _abs_uri(m):
            q, u = m.group(1), m.group(2)
            if u.startswith('http') or u.startswith('//'):
                return m.group(0)
            if u.startswith('/'):
                return 'URI=%s%s%s' % (q, self.host, u)
            return 'URI=%s%s/%s%s' % (q, self.host, u.lstrip('./'), q)

        txt = re.sub(r'URI=(["\'])([^"\']+)\1', _abs_uri, txt)

        out = []
        for line in txt.split('\n'):
            ln = line.strip()
            if ln and not ln.startswith('#'):
                if ln.startswith('/'):
                    ln = self.host + ln
                elif not ln.startswith('http'):
                    ln = self.host + '/' + ln.lstrip('./')
                out.append(ln)
            else:
                out.append(line)
        return '\n'.join(out)

    def _danmaku_xml(self, sid):
        head = '<?xml version="1.0" encoding="UTF-8"?>'
        try:
            d = self._api('/api/comments/live/%s' % urllib.parse.quote(_s(sid)))
            msgs = d.get('messages') or []
            rows = []
            i = 0
            for m in msgs:
                if not isinstance(m, dict):
                    continue
                u = _s(m.get('u'))
                t = _s(m.get('t'))
                if not t:
                    continue
                show = ('%s: %s' % (u, t)) if u else t
                rows.append('\t<d p="%.1f,1,25,16777215,0">%s</d>'
                            % (i * 0.8, self._xml_esc(show[:80])))
                i += 1
            if not rows:
                return [200, 'text/xml', head + '<i></i>']
            return [200, 'text/xml', '\n'.join([head, '<i>'] + rows + ['</i>'])]
        except Exception as e:
            self.log('\u5f39\u5e55\u751f\u6210\u5931\u8d25: %s' % e)
            return [200, 'text/xml', head + '<i></i>']

    def localProxy(self, param=None, *args, **kwargs):
        self._ensure()
        try:
            if not isinstance(param, dict):
                p = {}
                if isinstance(param, str) and '=' in param:
                    for k, v in urllib.parse.parse_qsl(param.lstrip('?&')):
                        p[k] = v
                param = p
            typ = _s(param.get('type'))
            # \u2460 \u667a\u80fd\u64ad\u653e\u7ebf\u8def:\u6bcf\u6b21\u8bf7\u6c42\u90fd\u91cd\u65b0\u53d6\u7968,\u7968\u636e\u4e0d\u8fc7\u671f
            if typ == 'hls':
                key = self._norm_tid(param.get('key') or 'video')
                src = _s(param.get('src'))
                vid = _s(param.get('vid'))
                ep = _s(param.get('ep')) or '1'
                pl = self._play_data(key, src, vid, ep)
                s = _s(pl.get('src'))
                if not s:
                    return [404, 'text/plain', '']
                url = s if s.startswith('http') else (self.host + s)
                txt = self._rewrite_m3u8(url)
                if txt is None and pl.get('src_proxy'):
                    txt = self._rewrite_m3u8(self._abs(pl.get('src_proxy')))
                if txt is None:
                    return [404, 'text/plain', '']
                return [200, 'application/vnd.apple.mpegurl', txt]
            # \u2461 \u76f4\u64ad\u5f39\u5e55
            if typ == 'danmu':
                return self._danmaku_xml(param.get('sid') or '')
        except Exception as e:
            self.log('\u672c\u5730\u4ee3\u7406\u5f02\u5e38: %s' % e)
        return [404, 'text/plain', '']


# \u7b5b\u9009\u4e0b\u62c9\u91cc\u90a3\u4e2a JSON \u4e32 \u2192 \u53d6\u56de\u91cc\u9762\u7684\u5206\u7c7b code(\u7528\u4e8e\u5224\u65ad\u662f\u5426\u88ab\u6539\u8fc7)
def _json_cat(v):
    t = _s(v)
    if not t:
        return ''
    if t[:1] == '{':
        try:
            o = json.loads(t)
            if isinstance(o, dict):
                return _s(o.get('c'))
        except Exception:
            pass
    return t
