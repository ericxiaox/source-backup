# coding: utf-8
"""
\u7ad9\u70b9: CartoonPorno (\u5361\u901a\u52a8\u6f2b\u8272\u60c5\u7ad9)
\u4e3b\u57df\u540d: https://www.cartoonporno.cc
\u5185\u5bb9\u7c7b\u578b: \u6210\u4eba\u52a8\u6f2b/3D\u5361\u901a\u77ed\u89c6\u9891 (mp4\u76f4\u94fe)
\u5907\u7528\u57df\u540d: \u65e0
\u53d1\u5e03\u9875: \u65e0
\u7279\u6b8a\u8bf4\u660e:
  - \u5217\u8868\u5361\u7247 URL = data-s + data-i + data-u + data-q (JS \u62fc\u88c5)
  - \u5206\u9875\u53c2\u6570 p (\u975e page/pg)
  - \u64ad\u653e\u6e90\u5728 embed \u9875: \u8be6\u60c5\u9875 JSON-LD embedUrl -> /embed/{vid}/?hl=zh -> <source src=\"mp4\">
  - mp4 \u76f4\u94fe\u5e26\u65f6\u6548\u7b7e\u540d (utc/e)\uff0c\u9700\u6bcf\u6b21\u5b9e\u65f6\u6293 embed \u9875
\u6700\u540e\u9a8c\u8bc1\u65f6\u95f4: 2026-09-20
\u6765\u6e90: \u81ea\u4e3b\u5206\u6790
"""
import json
import re
from urllib.parse import quote, urljoin, unquote

from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    def __init__(self):
        self.extend = ""
        self.host = "https://www.cartoonporno.cc"
        self.hl = "zh"
        self.classes = [
            {"type_id": "217/3d", "type_name": "3D\u6027\u611f"},
            {"type_id": "231/anime", "type_name": "\u52a8\u6f2b\u8bf1\u60d1"},
            {"type_id": "447/hentai", "type_name": "\u52a8\u6f2b\u8272\u60c5"},
            {"type_id": "218/3d-cartoon", "type_name": "3D\u5361\u901a\u8bf1\u60d1"},
            {"type_id": "445/hardcore", "type_name": "\u6fc0\u70c8\u786c\u6838"},
            {"type_id": "494/lesbian", "type_name": "\u5973\u540c\u6027\u604b"},
            {"type_id": "276/blowjob", "type_name": "\u53e3\u4ea4\u5feb\u611f"},
            {"type_id": "338/creampie", "type_name": "\u4f53\u5185\u5c04\u7cbe"},
            {"type_id": "180/demons", "type_name": "Demons"},
            {"type_id": "376/erotic", "type_name": "\u8272\u60c5\u8bf1\u60d1"},
            {"type_id": "725/uncensored", "type_name": "\u65e0\u7801\u76f4\u51fb"},
            {"type_id": "234/ass", "type_name": "\u7fd8\u81c0\u8bf1\u60d1"},
            {"type_id": "184/big-tits", "type_name": "\u5de8\u4e73\u8bf1\u60d1"},
            {"type_id": "327/comic", "type_name": "\u6f2b\u753b\u98ce"},
        ]
        self.filters = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Referer": self.host + "/"
        }
    def getName(self):
        return "CartoonPorno"

    def getDependence(self):
        return []

    def init(self, extend=""):
        # \u96f6\u7f51\u7edc
        self.extend = extend or ""

    def homeContent(self, filter):
        # \u96f6\u7f51\u7edc
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def _fetch(self, url, headers=None):
        h = dict(self.headers)
        if headers:
            h.update(headers)
        try:
            r = self.fetch(url, headers=h, timeout=15)
            if not r or r.status_code != 200:
                self.log({"fetch_fail": url, "status": r.status_code if r else None})
                return ""
            return r.text or ""
        except Exception as e:
            self.log({"fetch_exc": url, "error": str(e)})
            return ""

    # ---------- \u5217\u8868\u89e3\u6790 ----------
    def _build_url(self, ds, di, du, dq):
        """\u6309\u7ad9\u70b9 JS: data-s + data-i + data-u + data-q \u62fc\u8be6\u60c5 URL"""
        return (ds or "") + str(di or "") + (du or "") + (dq or "")

    def _parse_cards(self, html):
        out = []
        if not html:
            return out
        # \u6bcf\u5f20\u5361\u7247\u4ee5 <div class="item"> \u5f00\u5934\uff0c\u5185\u542b <a class='...lnk' data-s=.. data-i=.. data-u=.. data-q=..>
        blocks = re.split(r'<div class="item">', html)
        for blk in blocks[1:]:
            am = re.search(
                r"<a[^>]*class=['\"][^'\"]*lnk[^'\"]*['\"][^>]*data-s=['\"]([^'\"]*)['\"][^>]*data-i=['\"]([^'\"]*)['\"][^>]*data-u=['\"]([^'\"]*)['\"][^>]*data-q=['\"]([^'\"]*)['\"][^>]*title=['\"]([^'\"]*)['\"]",
                blk, re.S)
            if not am:
                continue
            ds, di, du, dq, title = am.group(1), am.group(2), am.group(3), am.group(4), am.group(5)
            link = self._build_url(ds, di, du, dq)
            # \u5c01\u9762: data-src
            pm = re.search(r'data-src=["\']([^"\']+)["\']', blk)
            pic = pm.group(1) if pm else ""
            if pic.startswith("//"):
                pic = "https:" + pic
            # \u65f6\u957f
            tm = re.search(r'<span class="item-time">([^<]+)</span>', blk)
            remark = tm.group(1).strip() if tm else ""
            out.append({
                "vod_id": di,
                "vod_name": self._unescape(title),
                "vod_pic": pic,
                "vod_remarks": remark,
                "vod_link": link,
            })
        return out

    @staticmethod
    def _unescape(s):
        if not s:
            return ""
        return (s.replace("&amp;", "&").replace("&quot;", '"')
                 .replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">"))

    def _to_list(self, cards):
        res = []
        for c in cards:
            vid = str(c.get("vod_id") or "")
            name = str(c.get("vod_name") or "").replace("|$|", " ").replace("$", " ")
            pic = str(c.get("vod_pic") or "")
            remark = str(c.get("vod_remarks") or "").replace("|$|", " ").replace("$", " ")
            packed = "|$|".join([vid, name, pic, remark])
            res.append({
                "vod_id": packed,
                "vod_name": c.get("vod_name") or "",
                "vod_pic": pic,
                "vod_remarks": remark,
            })
        return res
    def homeVideoContent(self):
        html = self._fetch(f"{self.host}/?hl={self.hl}")
        cards = self._parse_cards(html)
        return {"list": self._to_list(cards)}

    # ---------- \u5206\u7c7b\u5217\u8868 ----------
    def categoryContent(self, tid, pg, filter, extend):
        page = str(pg or "1")
        tid = str(tid or "")
        if tid == "videos_hot":
            url = f"{self.host}/videos?hl={self.hl}&p={page}"
        elif tid == "videos_new":
            url = f"{self.host}/videos?hl={self.hl}&s=n&p={page}"
        else:
            # tid \u5f62\u5982 217/3d
            url = f"{self.host}/categories/{tid}?hl={self.hl}&p={page}"
        html = self._fetch(url)
        cards = self._parse_cards(html)
        return {
            "list": self._to_list(cards),
            "page": int(page),
            "pagecount": 9999,
            "limit": 20,
            "total": 9999,
        }

    # ---------- \u641c\u7d22 ----------
    def searchContent(self, key, quick, pg="1"):
        page = str(pg or "1")
        kw = quote(str(key or ""))
        url = f"{self.host}/toon?q={kw}&hl={self.hl}&p={page}"
        html = self._fetch(url)
        cards = self._parse_cards(html)
        return {"list": self._to_list(cards), "page": int(page)}

    # ---------- \u8be6\u60c5 ----------
    @staticmethod
    def _norm_ids(ids):
        if ids is None:
            return ""
        if isinstance(ids, (list, tuple)):
            if not ids:
                return ""
            ids = ids[0]
        if isinstance(ids, bytes):
            ids = ids.decode("utf-8", errors="ignore")
        return str(ids).strip()

    def _skeleton(self, vid, title="", pic="", remarks="\u89e3\u6790\u4e2d"):
        pid = str(vid).split("|$|")[0].replace("$", "|")
        return {"list": [{
            "vod_id": vid, "vod_name": title or "\u672a\u77e5\u6807\u9898", "vod_pic": pic or "",
            "vod_remarks": remarks, "vod_content": "",
            "vod_play_from": "\u64ad\u653e", "vod_play_url": "\u64ad\u653e$" + pid,
        }]}

    def detailContent(self, ids):
        raw = self._norm_ids(ids)
        if not raw:
            return {"list": []}
        try:
            ps = raw.split("|$|")
            vid = ps[0]
            old_name = ps[1] if len(ps) > 1 else ""
            old_pic = ps[2] if len(ps) > 2 else ""
            old_remark = ps[3] if len(ps) > 3 else ""
            # \u62fc\u8be6\u60c5\u9875 URL\uff08\u7528\u4e8e\u53d6 embedUrl\uff09
            detail_url = self._detail_url(vid)
            html = self._fetch(detail_url) if detail_url else ""
            name, pic, content = old_name, old_pic, old_remark
            if html:
                # JSON-LD
                jm = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
                if jm:
                    try:
                        jd = json.loads(jm.group(1))
                        name = jd.get("name") or name
                        pic = jd.get("thumbnailUrl") or pic
                        content = jd.get("description") or content
                        if pic.startswith("//"):
                            pic = "https:" + pic
                    except Exception:
                        pass
                if not name:
                    tm = re.search(r'<meta property="og:title" content="([^"]*)"', html)
                    if tm:
                        name = tm.group(1)
            if not vid:
                return self._skeleton(raw, name, pic)
            vod = {
                "vod_id": raw,
                "vod_name": name or "\u89c6\u9891",
                "vod_pic": pic,
                "vod_remarks": old_remark,
                "vod_content": content or old_remark,
                "vod_play_from": "\u64ad\u653e",
                "vod_play_url": "\u64ad\u653e$" + vid,
            }
            return {"list": [vod]}
        except Exception as e:
            self.log({"detail_exc": raw, "error": str(e)})
            return self._skeleton(raw)

    def _detail_url(self, vid):
        """vid \u5f62\u5982 131319\uff0c\u4f46\u8be6\u60c5 URL \u9700\u8981 slug\u3002
        \u6211\u4eec\u4ece\u641c\u7d22/\u5217\u8868\u9636\u6bb5\u53ea\u5b58\u4e86 id\uff0c\u8be6\u60c5\u9875\u53ef\u5c1d\u8bd5 /v-niche/{id}/ \u76f4\u63a5\u8df3 embed\u3002
        \u771f\u6b63\u53d6\u64ad\u653e\u5730\u5740\u53ea\u4f9d\u8d56 /embed/{id}/\uff0c\u6545\u8be6\u60c5 URL \u53ef\u7701\u7565 slug\u3002"""
        return f"{self.host}/v-niche/{vid}/?hl={self.hl}"

    # ---------- \u64ad\u653e ----------
    def playerContent(self, flag, id, vipFlags):
        pid = str(id or "")
        if "$" in pid:
            pid = pid.split("$", 1)[1]
        pid = pid.strip()
        # \u7eaf\u6570\u5b57 id
        m = re.search(r"(\d+)", pid)
        if not m:
            return {"parse": 1, "url": pid, "header": self.headers}
        vid = m.group(1)
        # \u6293 embed \u9875\u53d6 mp4 \u76f4\u94fe
        embed_url = f"{self.host}/embed/{vid}/?hl={self.hl}"
        html = self._fetch(embed_url, headers={"Referer": f"{self.host}/v-niche/{vid}/?hl={self.hl}"})
        real = ""
        if html:
            sm = re.search(r'<source[^>]+src=["\']([^"\']+)["\']', html)
            if sm:
                real = sm.group(1)
            if not real:
                vm = re.search(r'(https?://[^"\'\s]+\.mp4[^"\'\s]*)', html)
                if vm:
                    real = vm.group(1)
        if real:
            if real.startswith("//"):
                real = "https:" + real
            return {
                "parse": 0,
                "url": real,
                "header": {
                    "User-Agent": self.headers["User-Agent"],
                    "Referer": f"{self.host}/",
                },
            }
        # \u515c\u5e95\uff1a\u964d\u7ea7\u5230\u8be6\u60c5\u9875\u55c5\u63a2
        return {
            "parse": 1,
            "url": f"{self.host}/v-niche/{vid}/?hl={self.hl}",
            "header": self.headers,
        }

    def recommendContent(self, ids, pg):
        return {"list": []}

    def destroy(self):
        pass