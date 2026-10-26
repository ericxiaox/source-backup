# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import random
import re
import string
import time
import urllib.parse

try:
    from base.spider import Spider
except Exception:
    # \u975e\u58f3\u73af\u5883\uff08\u672c\u673a\u81ea\u6d4b\uff09\u515c\u5e95\u57fa\u7c7b
    class Spider(object):
        pass

try:
    import requests
except Exception:
    requests = None

_BASE = "https://honeypeach.cc"
_UA = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
_TIMEOUT = 15

_MODULES = (("video", "\u871c\u6843\u89c6\u9891"), ("duanju", "\u871c\u6843\u77ed\u5267"), ("caibian", "\u64e6\u8fb9\u77ed\u5267"),
            ("shortv", "\u871c\u6843\u52a8\u6f2b"), ("guochan", "\u56fd\u4ea7\u7cbe\u54c1"), ("heiliao", "\u9ed1\u6599\u5403\u74dc"))
_SEARCHABLE = ("video", "duanju", "caibian", "shortv", "guochan")


def _hmac_sha256(key, msg):
    """\u7eaf\u6807\u51c6\u5e93 HMAC-SHA256\uff08\u58f3\u73af\u5883\u53ef\u80fd\u65e0 hmac \u6a21\u5757\uff09"""
    if not isinstance(key, bytes):
        key = key.encode()
    if not isinstance(msg, bytes):
        msg = msg.encode()
    block = 64
    if len(key) > block:
        key = hashlib.sha256(key).digest()
    key = key + b"\x00" * (block - len(key))
    o = bytes(x ^ 0x5c for x in key)
    i = bytes(x ^ 0x36 for x in key)
    return hashlib.sha256(o + hashlib.sha256(i + msg).digest()).hexdigest()


def _rnd(n=10):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def _b64e(s):
    """urlsafe base64 \u53bb =\uff0c\u907f\u514d type_id \u7ecf\u58f3 Intent \u4f20\u9012\u88ab\u7279\u6b8a\u5b57\u7b26\u622a\u65ad"""
    return base64.urlsafe_b64encode(str(s).encode("utf-8")).decode().rstrip("=")


def _b64d(s):
    try:
        key = str(s or "")
        return base64.urlsafe_b64decode((key + "=" * (-len(key) % 4)).encode()).decode("utf-8", "replace")
    except Exception:
        return str(s or "")


def _to_int(v, default=1):
    try:
        return int(str(v).strip())
    except Exception:
        return default


class Spider(Spider):
    def __init__(self):
        try:
            super().__init__()
        except TypeError:
            pass
        self.proxy = ""            # \u4ec5\u5f53\u7528\u6237\u663e\u5f0f\u914d\u7f6e\u540e\u624d\u6302\u4ee3\u7406\uff08\u76f4\u8fde\u4f18\u5148\uff09
        self._sid = None
        self._skey = None
        self._exp = 0.0
        self._dev = None

    # ---------------- \u58f3\u5951\u7ea6 ----------------
    def init(self, extend=""):
        try:
            cfg = json.loads(extend) if extend else {}
        except Exception:
            cfg = {}
        self.proxy = str(cfg.get("proxy", "") or "") if isinstance(cfg, dict) else ""

    def getDependence(self):
        return ""

    def getName(self):
        return "\u6697\u591c\u871c\u6843"

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        return bool(url) and re.search(r'(?i)\.(mp4|m3u8|flv|mkv|avi|ts|mov|mpd)(\?.*)?$', str(url)) is not None

    def isTextFormat(self, url):
        return False

    def __getattr__(self, name):
        # \u53cd\u5c04\u5230\u672a\u5b9e\u73b0\u65b9\u6cd5\u65f6\u4e0d\u5d29\uff0c\u515c\u5e95\u8fd4\u56de no-arg lambda
        return lambda *a, **k: None

    # ---------------- \u7b7e\u540d\u8bf7\u6c42 ----------------
    def _dev_id(self):
        if not self._dev:
            self._dev = _rnd(12) + format(int(time.time() * 1000), 'x')
        return self._dev

    def _handshake(self):
        q = "dev=" + urllib.parse.quote(self._dev_id())
        st, txt = self._raw_get("/api/handshake", q, signed=False)
        if st != 200:
            return False
        try:
            d = json.loads(txt)
        except Exception:
            return False
        if d and d.get("sid") and d.get("skey"):
            self._sid = d["sid"]
            self._skey = d["skey"]
            self._exp = float(d.get("exp") or 0)
            return True
        return False

    def _raw_get(self, path, query="", signed=True):
        url = _BASE + path + (("?" + query) if query else "")
        headers = {"User-Agent": _UA, "Accept": "application/json"}
        if signed and self._sid and self._skey:
            ts = str(int(time.time()))
            nonce = _rnd(8) + format(int(time.time() * 1000), 'x')
            bh = hashlib.sha256(b"").hexdigest()
            canon = "GET\n%s\n%s\n%s\n%s\n%s\n%s" % (path, query, bh, ts, nonce, self._sid)
            sig = _hmac_sha256(bytes.fromhex(self._skey), canon.encode())
            headers["X-Hp-Sid"] = self._sid
            headers["X-Hp-Ts"] = ts
            headers["X-Hp-Nonce"] = nonce
            headers["X-Hp-Sign"] = sig
        if requests is not None:
            kw = {"headers": headers, "timeout": _TIMEOUT}
            if self.proxy:
                kw["proxies"] = {"http": self.proxy, "https": self.proxy}
            r = requests.get(url, **kw)
            return r.status_code, r.text
        try:
            import urllib.request
        except Exception:
            return 0, "{}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")
        except Exception:
            return 0, "{}"

    def _api(self, path, query=""):
        try:
            if not (self._sid and self._skey and time.time() < self._exp - 60):
                self._handshake()
            st, txt = self._raw_get(path, query)
            if st == 401:
                self._handshake()
                st, txt = self._raw_get(path, query)
            return st, txt
        except Exception:
            return 0, "{}"

    # ---------------- \u5de5\u5177 ----------------
    def _full(self, u):
        if not u:
            return ""
        if str(u).startswith("http"):
            return str(u)
        return _BASE + str(u)

    def _enc_id(self, key, iid, src="", sub=""):
        return _b64e("|".join([str(key), str(iid), str(src or ""), str(sub or "")]))

    def _dec_id(self, vid):
        s = _b64d(vid)
        p = s.split("|")
        p = (p + ["", "", "", ""])[:4]
        return p[0], p[1], p[2], p[3]

    def _enc_play(self, key, iid, ep, src="", sub=""):
        """\u64ad\u653e id\uff1akey|id|ep|src|sub"""
        return _b64e("|".join([str(key), str(iid), str(ep), str(src or ""), str(sub or "")]))

    def _dec_play(self, vid):
        s = _b64d(vid)
        p = s.split("|")
        p = (p + ["", "", "", "", ""])[:5]
        return p[0], p[1], p[2], p[3], p[4]

    def _vod(self, it, key, src="", sub=""):
        iid = it.get("id")
        if iid is None:
            return None
        s = str(it.get("src") or src or "")
        return {
            "vod_id": self._enc_id(key, iid, s, sub),
            "vod_name": str(it.get("title") or ""),
            "vod_pic": self._full(it.get("cover") or ""),
            "vod_remarks": str(it.get("remark") or ""),
        }

    # ---------------- \u9996\u9875 ----------------
    def homeContent(self, filter):
        try:
            classes = []
            for key, mod_name in _MODULES:
                st, txt = self._api("/api/cats", "key=%s&v=3" % key)
                d = json.loads(txt) if txt else {}
                for c in (d.get("cats") or []):
                    kind = c.get("kind") or "vod"
                    if kind not in ("vod", "tags"):
                        continue
                    classes.append({
                        "type_id": self._enc_id(key, c.get("code", ""), c.get("src", ""), c.get("sub", "")),
                        "type_name": mod_name + "\u00b7" + str(c.get("name") or c.get("code") or ""),
                    })
            return {"class": classes, "filters": {}}
        except Exception:
            return {"class": [], "filters": {}}

    def homeVideoContent(self):
        return {"list": []}

    # ---------------- \u5206\u7c7b\u5217\u8868 ----------------
    def categoryContent(self, tid, pg, filter, extend):
        try:
            key, cat, src, sub = self._dec_id(tid)
            if not key or not cat:
                return {"list": [], "page": 1, "pagecount": 1, "limit": 20, "total": 0}
            page = _to_int(pg, 1)
            q = "key=%s&cat=%s&page=%s" % (key, urllib.parse.quote(cat), page)
            if src:
                q += "&src=" + urllib.parse.quote(src)
            if sub not in ("", None):
                q += "&sub=" + urllib.parse.quote(str(sub))
            st, txt = self._api("/api/module", q)
            d = json.loads(txt) if txt else {}
            lst = []
            for it in (d.get("list") or []):
                v = self._vod(it, key, src, sub)
                if v:
                    lst.append(v)
            pc = _to_int(d.get("pages"), 1)
            return {"list": lst, "page": page, "pagecount": pc, "limit": 20, "total": len(lst)}
        except Exception:
            return {"list": [], "page": _to_int(pg, 1), "pagecount": 1, "limit": 20, "total": 0}

    # ---------------- \u8be6\u60c5\uff08\u4e09\u8def\u517c\u5bb9 ids: list / JSON\u4e32 / \u88f8\u5b57\u7b26\u4e32\uff09 ----------------
    def detailContent(self, ids):
        try:
            if isinstance(ids, str):
                s = ids.strip()
                if s.startswith("["):
                    try:
                        id_list = [str(json.loads(s)[0])]
                    except Exception:
                        id_list = [s.split(",")[0].strip("[]\"' ")]
                else:
                    id_list = [s.split(",")[0].strip("\"' ")]
            elif isinstance(ids, (list, tuple)):
                id_list = [str(x).strip("\"' ") for x in ids]
            else:
                id_list = [str(ids).split(",")[0].strip("\"' ")]
            vid = id_list[0] if id_list else ""
            key, iid, src, sub = self._dec_id(vid)
            if not key or not iid:
                return {"list": []}
            params = []
            if src:
                params.append("src=" + urllib.parse.quote(src))
            if sub not in ("", None):
                params.append("sub=" + urllib.parse.quote(str(sub)))
            q = "&".join(params)
            st, txt = self._api("/api/detail/%s/%s" % (key, urllib.parse.quote(str(iid))), q)
            d = json.loads(txt) if txt else {}
            det = d.get("detail")
            if not det:
                return {"list": []}
            eps = det.get("episodes") or []
            if not eps:
                eps = [{"ep": 1, "name": "\u6b63\u7247"}]
            lines = []
            for e in eps:
                ep = e.get("ep", 1)
                name = str(e.get("name") or ("\u7b2c%s\u96c6" % ep))
                # \u96c6\u540d\u6e05\u6d17\uff1a\u53bb\u6389 $ # \u7b49\u58f3\u5206\u9694\u7b26
                name = re.sub(r"[$#]", " ", name).strip() or str(ep)
                pid = self._enc_play(key, iid, ep, src, sub)
                lines.append("%s$%s" % (name, pid))
            play_url = "#".join(lines)
            vod = {
                "vod_id": vid,
                "vod_name": str(det.get("title") or ""),
                "vod_pic": self._full(det.get("cover") or ""),
                "vod_year": str(det.get("date") or ""),
                "vod_remarks": ("\u5171%s\u96c6" % det.get("ep_count")) if det.get("ep_count") else "",
                "vod_content": str(det.get("desc") or ""),
                "vod_play_from": "\u871c\u6843",
                "vod_play_url": play_url,
            }
            return {"list": [vod]}
        except Exception:
            return {"list": []}

    # ---------------- \u641c\u7d22\uff08pg \u9ed8\u8ba4\u503c\u5fc5\u5e26\uff09 ----------------
    def searchContent(self, key, quick, pg="1"):
        try:
            kw = urllib.parse.quote(str(key))
            out = []
            seen = set()
            for mod in _SEARCHABLE:
                st, txt = self._api("/api/search", "key=%s&kw=%s&page=%s" % (mod, kw, _to_int(pg, 1)))
                d = json.loads(txt) if txt else {}
                for it in (d.get("list") or []):
                    v = self._vod(it, mod)
                    if v and v["vod_id"] not in seen:
                        seen.add(v["vod_id"])
                        out.append(v)
            return {"list": out, "page": _to_int(pg, 1)}
        except Exception:
            return {"list": [], "page": _to_int(pg, 1)}

    # ---------------- \u64ad\u653e\uff08\u517c\u5bb9\u5355\u96c6 id \u4e0e\u6574\u6bb5 play_url\uff09 ----------------
    def playerContent(self, flag, id, vipFlags):
        try:
            raw = str(id or "")
            # \u6574\u6bb5 vod_play_url \u4f20\u5165\u65f6\u53d6\u7b2c\u4e00\u7ebf\u8def\u7b2c\u4e00\u96c6
            seg = raw.split("$$$", 1)[0].split("#", 1)[0]
            cand = seg.rsplit("$", 1)[-1] if "$" in seg else seg
            key, iid, ep, src, sub = self._dec_play(cand)
            if not key or not iid:
                return {"parse": 0, "url": "http://", "header": {"User-Agent": _UA}}
            params = []
            if src:
                params.append("src=" + urllib.parse.quote(src))
            if sub not in ("", None):
                params.append("sub=" + urllib.parse.quote(str(sub)))
            q = "&".join(params)
            st, txt = self._api("/api/play/%s/%s/%s" % (key, urllib.parse.quote(str(iid)),
                                                       urllib.parse.quote(str(ep))), q)
            d = json.loads(txt) if txt else {}
            pl = d.get("play") or {}
            url = str(pl.get("src") or "")
            if not url or pl.get("locked"):
                return {"parse": 0, "url": "http://", "header": {"User-Agent": _UA}}
            return {"parse": 0, "url": self._full(url), "header": {"User-Agent": _UA}}
        except Exception:
            return {"parse": 0, "url": "http://", "header": {"User-Agent": _UA}}


# ---------------- \u5168\u94fe\u8def\u81ea\u6d4b\uff08\u89c4\u5219\u7b2c\u5341\u516b\u7ae0\u6a21\u677f\uff09 ----------------
if __name__ == "__main__":
    sp = Spider()
    sp.init("")
    h = sp.homeContent(False)
    print("homeContent:", len(h.get("class", [])), "\u5206\u7c7b")
    vc = [c for c in h.get("class", []) if "\u871c\u6843\u89c6\u9891" in c["type_name"]]
    c = sp.categoryContent(vc[0]["type_id"], 1, "", "")
    print("categoryContent:", len(c.get("list", [])), "\u9879; pagecount:", c.get("pagecount"))
    if not c.get("list"):
        raise SystemExit("\u5217\u8868\u4e3a\u7a7a")
    vid = c["list"][0]["vod_id"]
    d = sp.detailContent([vid])
    vod = (d.get("list") or [{}])[0]
    print("detailContent:", vod.get("vod_name", "")[:20], "| \u96c6\u6570:", len(vod.get("vod_play_url", "").split("#")))
    if vod.get("vod_play_url"):
        first = vod["vod_play_url"].split("#")[0]
        pid = first.rsplit("$", 1)[-1]
        print("playerContent(\u5355\u96c6):", sp.playerContent("\u871c\u6843", pid, [])["url"][:60])
        print("playerContent(\u6574\u6bb5):", sp.playerContent("\u871c\u6843", vod["vod_play_url"], [])["url"][:60])
    s = sp.searchContent("\u4e09\u56fd", False)
    print("searchContent:", len(s.get("list", [])), "\u9879")
    print(sp.getName(), "| getDependence =", repr(sp.getDependence()))