# -*- coding: utf-8 -*-
# \u9ec4\u8c46\u77ed\u5267\uff082026-09-12 \u6807\u51c6\u4ef6\u6539\u9020\u7248\uff0c\u57fa\u7ebf = xbpq/\u9ec4\u8c46.py \u5408\u5e76\u7248\uff09
# \u7ad9\u70b9\u6027\u8d28\uff1a\u77ed\u5267 App \u52a0\u5bc6 API \u540e\u7aef\uff08AES-CBC + gzip + sign\uff09\uff0c\u975e\u82f9\u679cCMS\u3001\u65e0 HTML \u9875\u9762
# \u57df\u540d\u6c60\uff082026-09-09 \u5b9e\u6d4b\u4e09\u57df\u540c\u5e93\uff09\uff1alzlukvca.cc / tideember.cc / xqjzvcvt.top
#   \u8bf7\u6c42\u5931\u8d25\u81ea\u52a8\u5207\u4e0b\u4e00\u57df\uff1b\u6c60\u5168\u6302\u65f6\u5bfc\u822a\u7ad9\u63a2\u7d22\uff08explorer\uff0cgitee \u5f62\u6001\u7f3a\u5931\u5219\u8df3\u8fc7\uff09
# \u672c\u6b21\u6539\u9020\uff082026-09-13\uff09\uff1a
#   1. ext \u6807\u51c6\u89e3\u6790\uff08host@ \u9501\u5b9a / hosts@ \u5019\u9009 / publish@ \u53d1\u5e03\u9875\uff0c\u517c\u5bb9\u65e7 site \u952e\uff09
#   2. init \u5e76\u884c\u63a2\u6d4b\u57df\u540d\u6c60\uff0c\u6d3b\u57df\u6392\u524d\uff08\u7701\u6bcf\u6b21\u8bf7\u6c42\u5168\u6c60\u8f6e\u6362\uff09
#   3. publish@ \u771f\u63a5\u5165\uff1a\u6293\u5b98\u65b9\u5165\u53e3\u9875\u62bd\u5019\u9009\u57df\u5e76\u5165\u6c60\uff08\u539f\u5148\u53ea\u5b58\u8fdb _ext \u4e0d\u6293 = \u6446\u8bbe\uff09
#   4. hostresolver \u63a5\u5165 + \u5185\u8054\u5e76\u884c\u515c\u5e95\uff08gitee \u8fdc\u7a0b\u5bfc\u5165\u5f62\u6001 explorer/hostresolver \u90fd\u7f3a\uff09
# \u5b98\u65b9\u6e20\u9053\uff1ahddj.tv\uff08\u5b98\u7f51\u5165\u53e3\uff0cPC \u672c\u673a DNS \u6c61\u67d3\uff0c\u771f\u673a\u53ef\u89e3\u6790\uff09
#   github.com/hddj636 = \u5185\u5bb9\u955c\u50cf\u8d26\u53f7\uff08\u6bcf\u4ed3 desc \u5747\u6307\u5411 hddj.tv\uff0c\u975e\u7ebf\u8def\u53d1\u5e03\u9875\uff09
#   www.hdmgdju.cn = \u5b98\u7f51\u5ba3\u4f20\u9875\uff08\u7ea6 15KB\uff0c\u4e0d\u542b\u7ebf\u8def\u57df\u540d\uff09
#   \u4e09\u57df\u540c\u5e93\u975e\u6cdb\u89e3\u6790\uff08\u968f\u673a\u5b50\u57df NXDOMAIN\uff0c2026-09-13 \u5b9e\u6d4b\uff09\u2192 \u4e0d\u9002\u7528\u6269\u8bcd\u65b9\u6848
import gzip
import hashlib
import hmac
import json
import os
import re
import sys
import time
import uuid
import requests

try:
    from base.spider import Spider as BaseSpider
except Exception:
    class BaseSpider:
        pass

try:
    from hostresolver import resolve_host, parse_ext, probe_first
except Exception:
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext, probe_first
    except Exception:
        resolve_host = None
        probe_first = None
        parse_ext = None

HOSTS = ["https://lzlukvca.cc", "https://tideember.cc", "https://xqjzvcvt.top"]
ALIAS = "huangdou"          # explorer \u63a2\u7d22\u522b\u540d\uff08\u5bfc\u822a\u7ad9\u7ad9\u540d/\u57df\u540d\u5339\u914d\uff09
_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
       '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')


class _AESCBC:
    @staticmethod
    def encrypt(data, key, iv):
        try:
            from Crypto.Cipher import AES
            return AES.new(key, AES.MODE_CBC, iv).encrypt(_AESCBC.pad(data))
        except Exception:
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            enc = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()).encryptor()
            return enc.update(_AESCBC.pad(data)) + enc.finalize()

    @staticmethod
    def decrypt(data, key, iv):
        try:
            from Crypto.Cipher import AES
            plain = AES.new(key, AES.MODE_CBC, iv).decrypt(data)
        except Exception:
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            dec = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()).decryptor()
            plain = dec.update(data) + dec.finalize()
        return _AESCBC.unpad(plain)

    @staticmethod
    def pad(data):
        n = 16 - len(data) % 16
        return data + bytes([n]) * n

    @staticmethod
    def unpad(data):
        n = data[-1] if data else 0
        return data[:-n] if 1 <= n <= 16 else data


class Spider(BaseSpider):

    # \u5b98\u65b9\u5165\u53e3/\u53d1\u5e03\u9875\uff082026-09-13\uff09\uff1aext publish@ \u4f18\u5148\uff0c\u7f3a\u7701\u7528\u5b83\u3002\u6293\u9875\u9762\u62bd\u5019\u9009\u57df\u5e76\u5165\u6c60\uff1b
    # PC \u672c\u673a DNS \u6c61\u67d3\u53d6\u4e0d\u5230 \u2192 \u9759\u9ed8\u9000\u56de\u5185\u7f6e\u4e09\u57df\uff0c\u96f6\u526f\u4f5c\u7528\u3002
    PUBLISH_PAGE = "https://hddj.tv"

    def __init__(self):
        self.hosts = list(HOSTS)
        self._hi = 0
        self.host = self.hosts[0]
        self.api = self.host + "/api"
        self.name = "\u9ec4\u8c46\u77ed\u5267"
        self.platform_key = "7961beb44246e3012ce228d6b5ced05a"
        self.version = "2.0.0"
        self.device_type = "web"
        self.session_id = uuid.uuid4().hex
        self.device_id = self.session_id
        self.token = ""
        self._ext = {}
        self.trace = []
        self.headers = {"User-Agent": _UA, "Accept": "*/*", "Origin": self.host, "Referer": self.host + "/home", "Content-Type": "application/octet-stream", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "zh-CN,zh;q=0.9"}
        self.session = requests.Session()
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            retry = Retry(total=2, backoff_factor=0.4, status_forcelist=[500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        except Exception:
            pass
        self._apply_host(self.host)
        self.class_cache = None
        self.filter_cache = {}
        self._explore_ts = 0
        self._init_done = False
        # \u5386\u53f2\u63a2\u7d22\u6210\u679c\u9884\u8f7d\uff08explorer.py \u5728\u4e0a\u7ea7\u76ee\u5f55\uff0cbest-effort\uff09
        try:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from explorer import known
            for h in known(ALIAS):
                if h not in self.hosts:
                    self.hosts.append(h)
        except Exception:
            pass

    def _apply_host(self, host):
        self.host = host.rstrip("/")
        self.api = self.host + "/api"
        self.headers["Origin"] = self.host
        self.headers["Referer"] = self.host + "/home"
        self.session.headers.update(self.headers)

    def _rotate(self):
        self._hi = (self._hi + 1) % len(self.hosts)
        self._apply_host(self.hosts[self._hi])

    # ---------- ext \u89e3\u6790\uff082026-09-12 \u6807\u51c6\u5316\uff09 ----------
    def _parse_ext(self, extend):
        """host@ \u9501\u5b9a / hosts@ \u5019\u9009 / publish@ \u5907\u5fd8\uff1b\u517c\u5bb9\u65e7 site/base_url \u952e\u3002"""
        s = (extend or '').strip()
        if not s:
            return
        try:
            cfg = json.loads(s)
            if isinstance(cfg, dict):
                for k in ('host', 'publish', 'site', 'base_url'):
                    if cfg.get(k):
                        v = str(cfg[k]).strip()
                        if k in ('host', 'site', 'base_url'):
                            self._ext['host'] = v
                        else:
                            self._ext[k] = v
                if cfg.get('hosts'):
                    hs = cfg['hosts'] if isinstance(cfg['hosts'], list) else [cfg['hosts']]
                    self._ext['hosts'] = [str(h).strip() for h in hs if str(h).strip()]
                self.token = cfg.get("token", self.token)
                self.platform_key = cfg.get("platform_key", self.platform_key)
                self.version = cfg.get("version", self.version)
                self.device_type = cfg.get("device_type", self.device_type)
                return
        except Exception:
            pass
        # \u975e\u6cd5 JSON\uff1a\u6309\u5206\u53f7\u4e32\u8d70 parse_ext\uff08host@x;hosts@a,b \u5f62\u6001\uff09
        if parse_ext:
            try:
                self._ext.update(parse_ext(s) or {})
            except Exception:
                pass

    def _publish_candidates(self, publish):
        """\u6293\u53d1\u5e03\u9875/\u5b98\u65b9\u5165\u53e3\u9875\uff0c\u62bd\u51fa\u5176\u4e2d\u51fa\u73b0\u7684\u5019\u9009\u57df\u540d\uff08\u672c\u57df + \u9875\u9762\u5185 http(s) \u57df\u540d\uff09\u3002
        \u9ec4\u8c46\u4e09\u57df\u975e\u6cdb\u89e3\u6790\uff08\u968f\u673a\u5b50\u57df NXDOMAIN\uff09\uff0c\u4e0d\u505a\u6269\u8bcd\uff1b\u9875\u9762\u4e3a JS \u5355\u9875\u6216\u53d6\u4e0d\u5230\u65f6
        \u9759\u9ed8\u8fd4\u56de []\uff0c\u9000\u56de\u5185\u7f6e\u6c60\uff0c\u96f6\u526f\u4f5c\u7528\u3002"""
        if not publish:
            return []
        out = []
        m = re.match(r'^https?://([^/]+)', str(publish), re.I)
        if m:
            out.append('https://' + m.group(1).lower())
        try:
            r = self.session.get(publish, headers={'User-Agent': _UA},
                                 timeout=8, verify=False, allow_redirects=True)
            t = r.text or ''
            cands = [getattr(r, 'url', '')] + re.findall(
                r'https?://[a-z0-9.-]+\.[a-z]{2,15}', t, re.I)
            for u in cands:
                mm = re.match(r'^https?://([a-z0-9.-]+\.[a-z]{2,15})', str(u), re.I)
                if not mm:
                    continue
                d = mm.group(1).lower()
                # \u5254\u7b2c\u4e09\u65b9\u7edf\u8ba1/\u5b57\u4f53/\u5ba2\u670d/\u4ed3\u5e93\u57df\uff0c\u53ea\u7559\u7591\u4f3c\u7ad9\u70b9\u57df
                if re.search(r'(google|gstatic|baidu|schema\.org|w3\.org|fonts\.|'
                             r'kf\.|weibo|jquery|bootstrap|github|cloudflare|'
                             r'jsdelivr|unpkg)', d):
                    continue
                out.append('https://' + d)
        except Exception:
            pass
        seen, res = set(), []
        for u in out:
            if u not in seen:
                seen.add(u)
                res.append(u)
        return res

    def init(self, extend=""):
        self._parse_ext(extend)
        locked = bool(self._ext.get('host'))
        # \u9501\u5b9a\u57df\u6700\u4f18\u5148\uff08\u88ab\u9501\u57df\u5df2\u5728\u9ed8\u8ba4\u6c60\u4e2d\u65f6 insert \u4f1a\u88ab\u8df3\u8fc7\uff0c\u987b\u663e\u5f0f\u628a _hi \u6307\u8fc7\u53bb\uff09
        if locked:
            h = self._ext['host'].rstrip('/')
            if h not in self.hosts:
                self.hosts.insert(0, h)
            self._hi = self.hosts.index(h)
            self._apply_host(h)
        # ext \u5019\u9009\u63d2\u6c60
        for h in reversed(self._ext.get('hosts') or []):
            if h not in self.hosts:
                self.hosts.insert(0, h)
        # \u53d1\u5e03\u9875\u5019\u9009\uff08\u771f\u63a5\u5165\uff1a\u6293\u9875\u9762\u62bd\u57df\uff0c\u6392\u5185\u7f6e\u6c60\u4e4b\u524d\u4e00\u8d77\u5b9e\u6d4b\uff09
        if not locked:
            pub = self._ext.get('publish') or self.PUBLISH_PAGE
            for h in reversed(self._publish_candidates(pub)):
                if h not in self.hosts:
                    self.hosts.insert(0, h)
        self._apply_host(self.hosts[self._hi])
        # \u5e76\u884c\u63a2\u6d4b\uff1a\u6d3b\u57df\u6392\u524d\uff08\u6bcf\u57df\u4e00\u6b21\u771f\u5b9e API \u8c03\u7528\uff0c8s \u8d85\u65f6\uff09
        self._probe_pool()
        self._init_done = True

    def _probe_api(self, host, result):
        """\u5355\u57df\u63a2\u6d3b\uff1a\u771f\u5b9e\u52a0\u5bc6 API \u8c03\u7528\uff0c\u80fd\u51fa\u5217\u8868\u6570\u636e\u624d\u7b97\u6d3b\u3002"""
        if result[0]:
            return
        try:
            t = Spider()
            t.hosts = [host.rstrip('/')]
            t._apply_host(host)
            t._explore_ts = time.time() + 10 ** 9
            t.trace = []
            obj = t._api('/drama/list', {'page': '1', 'page_size': '3'})
            if self._list(obj):
                self.trace.append('%s -> API OK' % host)
                if not result[0]:
                    result[0] = host.rstrip('/')
            else:
                self.trace.append('%s -> API \u65e0\u6570\u636e' % host)
        except Exception as e:
            self.trace.append('%s -> FAIL %s' % (host, str(e)[:40]))

    def _probe_pool(self):
        """\u5e76\u884c\u63a2\u6d4b\u57df\u540d\u6c60\uff0c\u6d3b\u57df\u6392\u5230\u6700\u524d\uff08\u9501\u5b9a\u57df\u4e0d\u91cd\u63a2\uff09\u3002
        \u52a0\u5bc6 API \u7ad9\u4e0d\u80fd\u7528 hostresolver \u7684 GET \u63a2\u6d3b\uff08\u5224\u65ad\u4e0d\u4e86 JSON \u6570\u636e\uff09\uff0c
        \u76f4\u63a5\u7528 _probe_api \u771f\u5b9e\u8c03\u7528\u9a8c\u8bc1\u3002"""
        import threading
        if self._ext.get('host'):
            return
        result = [None]
        threads = [threading.Thread(target=self._probe_api, args=(h, result))
                   for h in self.hosts[:8]]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if result[0]:
            self._promote(result[0])

    def _promote(self, host):
        host = host.rstrip('/')
        if host not in self.hosts:
            self.hosts.insert(0, host)
        self._hi = self.hosts.index(host)
        self._apply_host(host)
        print(f'使用站点: {self.host}')

    def _check_host(self, host):
        """explorer/hostresolver \u9a8c\u8bc1\u56de\u8c03\uff1a\u5019\u9009\u57df\u7528\u672c\u6e90\u534f\u8bae\u5b9e\u6d4b\u3002"""
        try:
            t = Spider()
            t.hosts = [host.rstrip("/")]
            t._apply_host(host)
            t._explore_ts = time.time() + 10 ** 9
            return bool(self._list(t._api("/drama/list", {"page": "1", "page_size": "6"})))
        except Exception:
            return False

    def _explore(self):
        """\u5185\u7f6e\u6c60\u5168\u6302\uff1a\u591a\u5bfc\u822a\u7ad9\u6293\u53d6\u5019\u9009\u57df -> \u534f\u8bae\u9a8c\u8bc1 -> \u6d3b\u57df\u63d2\u6c60 + \u6301\u4e45\u5316\u3002
        10 \u5206\u949f\u5185\u53ea\u63a2\u4e00\u6b21\uff1bexplorer.py \u7f3a\u5e2d\u65f6\u9759\u9ed8\u8df3\u8fc7\u3002"""
        now = time.time()
        if now - self._explore_ts < 600:
            return False
        self._explore_ts = now
        try:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from explorer import discover, remember
        except Exception:
            self.trace.append('explorer \u7f3a\u5931\uff1a\u8df3\u8fc7\u5bfc\u822a\u7ad9\u63a2\u7d22')
            return False
        try:
            found = discover([ALIAS, "\u9ec4\u8c46"], validate=self._check_host) or []
        except Exception:
            found = []
        for h in found:
            if h not in self.hosts:
                self.hosts.append(h)
        if found:
            self._promote(found[0])
            try:
                remember(ALIAS, found)
            except Exception:
                pass
        self.trace.append('\u63a2\u7d22\u7ed3\u679c: %s' % (found or '\u65e0'))
        return bool(found)

    def getName(self):
        return self.name

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def localProxy(self, params):
        return [200, "video/MP2T", ""]

    # ---------- \u63a5\u53e3 ----------
    def homeContent(self, filter):
        data = self._api("/drama/list", {"page": "1", "page_size": "18"})
        classes = self._classes()
        return {"class": classes, "filters": self._filters(classes), "list": [self._vod(x) for x in self._list(data)], "parse": 0, "jx": 0}

    def homeVideoContent(self):
        data = self._api("/drama/list", {"page": "1", "page_size": "12"})
        return {"list": [self._vod(x) for x in self._list(data)]}

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg or 1)
        extend = extend or {}
        if tid == "yuandou":
            data = self._api("/drama/navBlock", {"code": "yuandou", "tab": "recommend", "page": str(pg)})
            items = self._nav_items(data)
        else:
            req = {"page": str(pg), "page_size": "18"}
            if tid and tid not in ("all", "recommend"):
                tabs = self._nav_filter(tid)
                idx = self._int(extend.get("sub"), 0)
                sub = tabs[idx] if tabs and 0 <= idx < len(tabs) else {}
                flt = sub.get("filter", {}) if isinstance(sub, dict) else {}
                req["cat_id"] = flt.get("cat_id", "")
                if flt.get("tag_id"):
                    req["tag_id"] = flt.get("tag_id", "")
                req["order"] = flt.get("order", "") or extend.get("order", "")
            elif extend.get("order"):
                req["order"] = extend.get("order")
            if extend.get("update_status"):
                req["update_status"] = extend.get("update_status")
            data = self._api("/drama/list", req)
            items = self._list(data)
        return {"page": int(pg), "pagecount": int(pg) if len(items) < 18 else int(pg) + 1, "limit": 18, "total": 99999, "list": [self._vod(x) for x in items], "parse": 0, "jx": 0}

    def detailContent(self, ids):
        vid = str(ids[0]).replace("rp_", "")
        obj = self._api("/drama/detail", {"id": vid})
        data = obj.get("data", obj) if isinstance(obj, dict) else {}
        if not isinstance(data, dict):
            return {"list": []}
        data = self._unlock(data)
        vod_id = self._sid(data.get("id") or data.get("drama_id") or vid)
        name = data.get("name") or data.get("title") or data.get("t") or vod_id
        eps = data.get("episodes") if isinstance(data.get("episodes"), list) else []
        count = self._int(data.get("episode_count") or data.get("free_episodes"), len(eps) or 1)
        play = []
        if eps:
            for i, ep in enumerate(eps, 1):
                seq = ep.get("seq") or ep.get("episode") or ep.get("ep") or i
                play.append("%s$%s|%s" % (ep.get("name") or ep.get("title") or "\u7b2c%s\u96c6" % seq, vod_id, seq))
        else:
            play = ["\u7b2c%s\u96c6$%s|%s" % (i, vod_id, i) for i in range(1, count + 1)]
        vod = {"vod_id": vod_id, "vod_name": name, "vod_pic": self._pic(data), "type_name": data.get("category") or data.get("type") or "", "vod_year": "", "vod_area": "", "vod_remarks": data.get("update_label") or "\u5168%s\u96c6" % count, "vod_actor": "", "vod_director": "", "vod_content": data.get("description") or data.get("summary") or name, "vod_play_from": self.name, "vod_play_url": "#".join(play)}
        return {"list": [vod], "parse": 0, "jx": 0}

    def searchContent(self, key, quick, pg="1"):
        data = self._api("/drama/list", {"page": str(pg), "page_size": "18", "keywords": str(key)})
        items = self._list(data)
        return {"page": int(pg), "pagecount": int(pg) if len(items) < 18 else int(pg) + 1, "limit": 18, "total": 99999, "list": [self._vod(x) for x in items], "parse": 0, "jx": 0}

    def searchContentPage(self, key, quick, pg="1"):
        return self.searchContent(key, quick, pg)

    def playerContent(self, flag, id, vipFlags=None):
        vid, seq = self._split(id)
        obj = self._api("/drama/play", {"id": vid, "seq": str(seq)}, True)
        data = obj.get("data", {}) if isinstance(obj, dict) else {}
        url = data.get("m3u8") or data.get("url") or self._hls(vid, seq)
        return {"parse": 0, "playUrl": "", "url": url, "jx": 0, "header": {"User-Agent": self.headers["User-Agent"], "Referer": self.host + "/home", "Origin": self.host}}

    def _api(self, path, data=None, silent=False):
        path = "/" + path.lstrip("/")
        rid = str(uuid.uuid4())
        key = self._key(rid)
        iv = os.urandom(16)
        raw = json.dumps({"token": self.token or "", "deviceId": self.device_id, "data": data or {}}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        body = iv + _AESCBC.encrypt(gzip.compress(raw), key, iv)
        ts = int(time.time())
        sign = hashlib.sha256(("Dart|%s|%s|%s|%s" % (self.session_id, rid, ts, path)).encode("utf-8")).hexdigest() + "-" + str(ts)
        h = dict(self.headers)
        h.update({"version": self.version, "deviceType": self.device_type, "time": str(ts), "sign": sign, "requestId": rid, "sessionId": self.session_id, "deviceBrand": "", "deviceModel": "", "systemName": "", "systemVersion": ""})
        # \u57df\u540d\u6c60\u8f6e\u6362\uff1a\u5f02\u5e38/\u975e JSON \u5373\u5207\u4e0b\u4e00\u4e2a\u57df\u540d\uff0c\u6700\u591a\u8bd5\u5b8c\u6574\u6c60
        last = {}
        for _ in range(len(self.hosts)):
            try:
                r = self.session.post(self.api + path, data=body, headers=h, timeout=15, verify=False)
                r.raise_for_status()
                obj = self._decode(r.content, rid)
                if obj:
                    return obj
                last = {}
            except Exception:
                last = {}
            self._rotate()
        # \u6c60\u5185\u57df\u540d\u5168\u6302\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\u6362\u57df\u540e\u91cd\u8bd5\u4e00\u6b21
        if self._explore():
            try:
                r = self.session.post(self.api + path, data=body, headers=h, timeout=15, verify=False)
                r.raise_for_status()
                obj = self._decode(r.content, rid)
                if obj:
                    return obj
            except Exception:
                pass
        return last

    def _key(self, rid):
        return hmac.new(self.platform_key.encode("utf-8"), bytes.fromhex(str(rid).replace("-", "")), hashlib.sha256).digest()

    def _decode(self, blob, rid):
        if not blob or len(blob) < 32 or (len(blob) - 16) % 16 != 0:
            try:
                return json.loads(blob.decode("utf-8"))
            except Exception:
                return {}
        plain = _AESCBC.decrypt(blob[16:], self._key(rid), blob[:16])
        if plain[:2] == b"\x1f\x8b":
            plain = gzip.decompress(plain)
        return json.loads(plain.decode("utf-8"))

    def _classes(self):
        if self.class_cache:
            return self.class_cache
        arr = [{"type_id": "all", "type_name": "\u5168\u90e8\u77ed\u5267"}]
        data = self._api("/drama/navList", {})
        for item in self._list(data.get("data", data) if isinstance(data, dict) else data):
            tid = str(item.get("code") or item.get("id") or item.get("cat_id") or "")
            name = item.get("name") or item.get("title") or tid
            if tid and name:
                arr.append({"type_id": tid, "type_name": name})
        self.class_cache = arr
        return arr

    def _filters(self, classes):
        common = [{"key": "order", "name": "\u6392\u5e8f", "value": [{"n": "\u9ed8\u8ba4", "v": ""}, {"n": "\u6700\u65b0", "v": "new"}, {"n": "\u6700\u70ed", "v": "hot"}]}, {"key": "update_status", "name": "\u72b6\u6001", "value": [{"n": "\u5168\u90e8", "v": ""}, {"n": "\u8fde\u8f7d", "v": "0"}, {"n": "\u5b8c\u7ed3", "v": "1"}]}]
        fs = {}
        for c in classes:
            tid = c["type_id"]
            tabs = self._nav_filter(tid) if tid not in ("all", "yuandou") else []
            fs[tid] = ([{"key": "sub", "name": "\u5b50\u5206\u7c7b", "value": [{"n": t.get("name", "\u9ed8\u8ba4"), "v": str(i)} for i, t in enumerate(tabs)]}] if tabs else []) + common
        return fs

    def _nav_filter(self, code):
        if code not in self.filter_cache:
            data = self._api("/drama/navFilter", {"code": str(code)})
            self.filter_cache[code] = self._list(data.get("data", data) if isinstance(data, dict) else data)
        return self.filter_cache.get(code, [])

    def _list(self, data):
        if isinstance(data, list):
            return data
        if not isinstance(data, dict):
            return []
        if isinstance(data.get("list"), list):
            return data["list"]
        if isinstance(data.get("items"), list):
            return data["items"]
        if isinstance(data.get("data"), list):
            return data["data"]
        if isinstance(data.get("data"), dict):
            return self._list(data["data"])
        return []

    def _nav_items(self, data):
        blocks = self._list(data.get("data", data) if isinstance(data, dict) else data)
        items = []
        for b in blocks:
            if isinstance(b, dict) and isinstance(b.get("items"), list):
                items += b.get("items")
            elif isinstance(b, dict) and (b.get("id") or b.get("drama_id")):
                items.append(b)
        return items

    def _vod(self, item):
        item = item or {}
        vid = self._sid(item.get("id") or item.get("drama_id") or "")
        remarks = item.get("update_label") or item.get("corner") or ("\u5168%s\u96c6" % item.get("episode_count") if item.get("episode_count") else "")
        return {"vod_id": vid, "vod_name": item.get("name") or item.get("title") or item.get("t") or vid, "vod_pic": self._pic(item), "vod_remarks": remarks}

    def _pic(self, item):
        return item.get("img_y") or item.get("img_x") or item.get("img") or item.get("cover") or item.get("pic") or ""

    def _unlock(self, d):
        eps = d.get("episodes")
        if isinstance(eps, list):
            for ep in eps:
                if isinstance(ep, dict):
                    ep["is_buy"] = True
                    ep["type"] = "free"
                    ep["price"] = 0
                    ep["methods"] = []
        d.update({"pay_type": "free", "money": 0, "episode_price": 0, "points_price": 0, "can_vip_watch": True, "is_buy_whole": True, "vip_episodes": [], "coin_episodes": [], "points_episodes": []})
        return d

    def _sid(self, x):
        return str(x or "").replace("rp_", "")

    def _split(self, x):
        p = str(x).split("|", 1)
        return self._sid(p[0]), p[1] if len(p) > 1 and p[1] else "1"

    def _hls(self, vid, seq):
        return "%s/api/drama/hls/%s/%s/play.m3u8?line=free" % (self.host, self._sid(vid), seq)

    def _int(self, x, d=0):
        try:
            return int(x)
        except Exception:
            return d
