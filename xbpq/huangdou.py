# -*- coding: utf-8 -*-
# \u9ec4\u8c46\u77ed\u5267 \u2014\u2014 \u5408\u5e76\u7248\uff08\u539f hd_dj.py / hd_dj.py.bak / hd_.py \u4e09\u6587\u4ef6\u5408\u4e00\uff0c\u65e7\u540d\u5df2\u5f03\u7528\uff09
# \u540c\u4e00 App \u540e\u7aef\uff08platform_key \u4e00\u81f4\uff09\uff0c\u4e09\u4e2a\u8f6e\u6362\u57df\u540d\u540c\u6570\u636e\uff1a
#   lzlukvca.cc / tideember.cc / xqjzvcvt.top   \uff082026-09-09 \u5b9e\u6d4b\u4e09\u57df\u5168\u6d3b\u3001\u8fd4\u56de\u540c\u5e93\uff09
# \u673a\u5236\uff1a\u8bf7\u6c42\u5931\u8d25\u81ea\u52a8\u5207\u4e0b\u4e00\u57df\u540d\uff1bext \u53ef\u8986\u76d6 site/platform_key/version/device_type
# \u515c\u5e95\u63a2\u7d22\uff1a\u5185\u7f6e\u6c60\u5168\u6302\u65f6\u8c03 explorer.py\uff08\u591a\u5bfc\u822a\u7ad9\u6293\u53d6 -> \u534f\u8bae\u9a8c\u8bc1\uff09\u81ea\u52a8\u627e\u6d3b\u57df\u63d2\u6c60
# \u5b98\u65b9\u6e20\u9053\uff08\u65e0\u4f20\u7edf\u53d1\u5e03\u9875\uff0c\u4ec5\u5907\u5fd8\uff09\uff1a
#   hddj.tv\uff08\u5b98\u65b9\u7ad9\uff0c\u672c\u673a DNS \u88ab\u6c61\u67d3\u5230 104.244.46.85\uff09
#   github.com/hddj636\uff08\u5b98\u65b9\u6bcf\u65e5\u5267\u96c6\u4ed3\u5e93\u7fa4\uff0cREADME \u53ea\u6307\u5411 hddj.tv\uff09
#   www.hdmgdju.cn\uff08\u4e0b\u8f7d\u4ecb\u7ecd\u9875\uff0c\u65e0 API\uff09
import gzip
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
import requests

try:
    from base.spider import Spider as BaseSpider
except Exception:
    class BaseSpider:
        pass

HOSTS = ["https://lzlukvca.cc", "https://tideember.cc", "https://xqjzvcvt.top"]
ALIAS = "huangdou"          # explorer \u63a2\u7d22\u522b\u540d\uff08\u5bfc\u822a\u7ad9\u7ad9\u540d/\u57df\u540d\u5339\u914d\uff09

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
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Accept": "*/*", "Origin": self.host, "Referer": self.host + "/home", "Content-Type": "application/octet-stream", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "zh-CN,zh;q=0.9"}
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

    def init(self, extend=""):
        if extend:
            try:
                cfg = json.loads(extend)
                site = (cfg.get("site") or cfg.get("base_url") or "").rstrip("/")
                if site:
                    # ext \u6307\u5b9a\u7ad9\u70b9\uff1a\u63d2\u5230\u6c60\u5b50\u6700\u524d\uff0c\u5931\u6548\u4ecd\u53ef\u56de\u843d\u5230\u5185\u7f6e\u6c60
                    if site not in self.hosts:
                        self.hosts.insert(0, site)
                    self._hi = self.hosts.index(site)
                    self._apply_host(site)
                self.token = cfg.get("token", self.token)
                self.platform_key = cfg.get("platform_key", self.platform_key)
                self.version = cfg.get("version", self.version)
                self.device_type = cfg.get("device_type", self.device_type)
            except Exception:
                pass

    def getName(self):
        return self.name

    def homeContent(self, filter):
        data = self._api("/drama/list", {"page": "1", "page_size": "18"})
        classes = self._classes()
        return {"class": classes, "filters": self._filters(classes), "list": [self._vod(x) for x in self._list(data)], "parse": 0, "jx": 0}

    def categoryContent(self, tid, pg, filter, extend):
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

    def playerContent(self, flag, id, vipFlags):
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

    def _check_host(self, host):
        """explorer \u9a8c\u8bc1\u56de\u8c03\uff1a\u5019\u9009\u57df\u7528\u672c\u6e90\u534f\u8bae\u5b9e\u6d4b\uff08\u80fd\u51fa\u5217\u8868\u6570\u636e\u624d\u7b97\u6d3b\u57df\uff09"""
        try:
            t = Spider()
            t.hosts = [host.rstrip("/")]
            t._apply_host(host)
            t._explore_ts = time.time() + 10 ** 9   # \u7981\u6b62\u4e34\u65f6\u5b9e\u4f8b\u518d\u89e6\u53d1\u63a2\u7d22\uff08\u9632\u9012\u5f52\uff09
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
            return False
        try:
            found = discover([ALIAS, "\u9ec4\u8c46"], validate=self._check_host) or []
        except Exception:
            found = []
        for h in found:
            if h not in self.hosts:
                self.hosts.append(h)
        if found:
            self._hi = self.hosts.index(found[0])
            self._apply_host(found[0])
            try:
                remember(ALIAS, found)
            except Exception:
                pass
        return bool(found)

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
