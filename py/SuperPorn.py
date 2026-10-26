# coding: utf-8
# ============================================================
# \u7ad9\u70b9\u4fe1\u606f\uff08\u6cd5\u521924\uff09
# \u7ad9\u70b9\u540d\uff1aSuperPorn
# \u4e3b\u57df\u540d\uff1ahttps://cn.superporn.ws
# \u5907\u7528\u57df\u540d\uff1ahttps://cn.superporn.me
# \u53d1\u5e03\u9875\uff1a\u65e0\u56fa\u5b9a\u53d1\u5e03\u9875\uff08\u591a\u8bed\u8a00\u5b50\u57df cn/vi/tr/ru\uff09
# \u5185\u5bb9\u7c7b\u578b\uff1a\u89c6\u9891\uff08\u6210\u4eba\u5f71\u89c6\uff09
# \u7279\u6b8a\u8bf4\u660e\uff1a
#   - \u8be6\u60c5\u9875 <source src> \u76f4\u63a5\u5185\u5d4c\u5e26 secure \u7b7e\u540d\u7684 mp4 \u76f4\u94fe\uff0c\u65e0\u9700\u4e8c\u6b21\u89e3\u6790
#   - \u5206\u7c7b\u9875/\u641c\u7d22\u9875\u5361\u7247\u7edf\u4e00 .thumb-video\uff0c\u53ef\u590d\u7528\u540c\u4e00\u89e3\u6790\u51fd\u6570
#   - \u5206\u9875\uff1a\u5206\u7c7b\u9875 /{slug}/{page}\uff0c\u9996\u9875 ?page={page}
#   - \u641c\u7d22\uff1aGET /search?q={\u5173\u952e\u8bcd}
# \u6700\u540e\u9a8c\u8bc1\uff1a2026-09-20
# \u6765\u6e90\uff1a\u7528\u6237\u63d0\u4f9b URL
# ============================================================
import json
import re
from urllib.parse import quote, urljoin

from base.spider import Spider as BaseSpider


class Spider(BaseSpider):

    def __init__(self):
        # \u96f6\u7f51\u7edc\u4f9d\u8d56\uff1a\u53ea\u505a\u672c\u5730\u521d\u59cb\u5316
        self.host = "https://cn.superporn.ws"
        self.hosts = ["https://cn.superporn.ws", "https://cn.superporn.me"]
        self.api = "https://api.superporn.ws"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 22127RK46C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Referer": self.host + "/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        # \u9759\u6001\u5206\u7c7b\uff08\u6cd5\u521916/17\uff1a\u5206\u7c7b\u96f6\u7f51\u7edc\u3001\u9759\u6001\u786c\u7f16\u7801\uff09
        self.classes = [
            {"type_id": "lesbian", "type_name": "\u5973\u540c"},
            {"type_id": "ebony", "type_name": "\u9ed1\u4eba"},
            {"type_id": "big-ass", "type_name": "\u4e30\u81c0"},
            {"type_id": "hentai", "type_name": "\u6210\u4eba\u52a8\u6f2b"},
            {"type_id": "milf", "type_name": "MILF"},
            {"type_id": "latina", "type_name": "\u62c9\u4e01\u88d4"},
            {"type_id": "japanese", "type_name": "\u65e5\u672c\u4eba"},
            {"type_id": "anal", "type_name": "\u809b\u4ea4"},
            {"type_id": "threesome", "type_name": "3P"},
            {"type_id": "creampie", "type_name": "\u5185\u5c04"},
            {"type_id": "bbw", "type_name": "BBW"},
            {"type_id": "teen", "type_name": "\u9752\u5c11\u5e74"},
            {"type_id": "big-tits", "type_name": "Big tits"},
            {"type_id": "interracial", "type_name": "\u5f02\u65cf"},
            {"type_id": "asian", "type_name": "\u4e9a\u6d32\u4eba"},
            {"type_id": "gangbang", "type_name": "\u7fa4\u4ea4"},
            {"type_id": "pov", "type_name": "POV"},
            {"type_id": "squirting", "type_name": "\u55b7\u5c04"},
            {"type_id": "redhead", "type_name": "\u7ea2\u53d1"},
            {"type_id": "shemale", "type_name": "\u53d8\u6027\u4eba"},
            {"type_id": "mature", "type_name": "\u6210\u719f"},
            {"type_id": "orgasm", "type_name": "\u6027\u9ad8\u6f6e"},
            {"type_id": "brunette", "type_name": "\u6df1\u8272\u5934\u53d1"},
            {"type_id": "amateur", "type_name": "\u4e1a\u4f59"},
            {"type_id": "maid", "type_name": "\u5973\u4ec6"},
            {"type_id": "fetish", "type_name": "\u604b\u7269\u7656"},
            {"type_id": "cosplay", "type_name": "\u89d2\u8272\u626e\u6f14"},
            {"type_id": "cheating", "type_name": "\u5077\u60c5"},
        ]
        self.filters = {c["type_id"]: [] for c in self.classes}

        # \u591a\u7ea7\u515c\u5e95\uff08\u6cd5\u521914\uff09
        self.CARD_SEL = [".thumb-video", "li.thumb-video", "[class*='thumb-video']"]
        self.TITLE_SEL = [
            ".thumb-video__description",
            "a.thumb-video__description",
            "[class*='thumb-video__description']",
            ".thumb-video__meta h3 a",
        ]
        self.PIC_SEL = [
            ".thumb-duracion img",
            "img.lazy",
            "[class*='thumb-duracion'] img",
        ]

    # ==================== \u57fa\u7840\u65b9\u6cd5 ====================

    def getName(self):
        return "SuperPorn"

    def getDependence(self):
        return []

    def init(self, extend=""):
        # \u96f6\u7f51\u7edc\uff1b\u52a8\u6001\u57df\u540d\u63a2\u6d4b\u653e\u5230 _pick_host\uff08\u975e\u9996\u9875\u65b9\u6cd5\u5185\u8c03\u7528\uff09
        self.extend = extend or ""

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        return bool(url and re.search(r"\.(m3u8|mp4|flv)(\?|$)", url, re.I))

    def manualVideoCheck(self):
        return False

    # ==================== \u57df\u540d\u5bb9\u707e ====================

    def _pick_host(self):
        """\u61d2\u52a0\u8f7d\u57df\u540d\u63a2\u6d4b\uff08\u6cd5\u521916\uff1a\u4e0d\u5728 homeContent \u8c03\u7528\uff09"""
        if getattr(self, "_cached_host", ""):
            return self._cached_host
        for h in self.hosts:
            try:
                r = self.fetch(h + "/", headers=self.headers, timeout=8, verify=False)
                if r and r.status_code == 200:
                    self._cached_host = h
                    self.headers["Referer"] = h + "/"
                    return h
            except Exception:
                continue
        self._cached_host = self.host
        return self.host

    # ==================== \u9996\u9875\uff08\u96f6\u7f51\u7edc\uff09 ====================

    def homeContent(self, filter):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def homeVideoContent(self):
        """\u9996\u9875\u63a8\u8350\uff1a\u6293\u9996\u9875\u7b2c\u4e00\u9875"""
        host = self._pick_host()
        r = self.fetch(host + "/", headers=self.headers, timeout=15, verify=False)
        if not r or r.status_code != 200:
            self.log({"home": "fetch_failed"})
            return {"list": []}
        return {"list": self._parse_list(r.text, host)}

    # ==================== \u5206\u7c7b\u5217\u8868 ====================

    def _parse_extend(self, extend):
        if not extend:
            return {}
        if isinstance(extend, dict):
            return extend
        if isinstance(extend, str):
            try:
                return json.loads(extend)
            except Exception:
                pass
            result = {}
            for part in extend.split(","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    result[k.strip()] = v.strip()
            return result
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        host = self._pick_host()
        page = int(pg or 1)
        tid = str(tid or "").strip()
        if not tid:
            return {"list": [], "page": 1, "pagecount": 1, "limit": 20, "total": 0}

        if page <= 1:
            url = "%s/%s" % (host, tid)
        else:
            url = "%s/%s/%d" % (host, tid, page)

        r = self.fetch(url, headers=self.headers, timeout=15, verify=False)
        if not r or r.status_code != 200:
            self.log({"category": "fetch_failed", "url": url})
            return {"list": [], "page": page, "pagecount": 9999, "limit": 20, "total": 0}

        vlist = self._parse_list(r.text, host)
        return {
            "list": vlist,
            "page": page,
            "pagecount": 9999,
            "limit": 20,
            "total": 999999,
        }

    # ==================== \u5217\u8868\u89e3\u6790\uff08\u590d\u7528\u51fd\u6570\uff09 ====================

    def _parse_list(self, html, host):
        """\u7edf\u4e00\u5217\u8868\u89e3\u6790\uff1a\u5206\u7c7b\u9875/\u641c\u7d22\u9875/\u9996\u9875\u5361\u7247\u7ed3\u6784\u4e00\u81f4"""
        if not html:
            return []
        items = []
        seen = set()
        # \u6309\u5361\u7247\u8d77\u59cb\u5207\u5206\uff0c\u907f\u514d\u975e\u8d2a\u5a6a\u6b63\u5219\u8fc7\u65e9\u95ed\u5408
        blocks = re.split(r'<div class="thumb-video\s*">', html)
        for block in blocks[1:]:
            # \u8be6\u60c5\u94fe\u63a5\uff08\u53d6\u7b2c\u4e00\u4e2a /video/ \u94fe\u63a5\uff09
            m_link = re.search(r'href="(https?://[^"]*/video/[^"]+)"', block)
            if not m_link:
                m_link = re.search(r'href="(/video/[^"]+)"', block)
            if not m_link:
                continue
            link = m_link.group(1)
            if link.startswith("/"):
                link = host + link
            if link in seen:
                continue
            seen.add(link)

            # \u6807\u9898\uff08\u591a\u7ea7\u515c\u5e95\uff0c\u53bb\u5185\u8054\u6807\u7b7e\uff09
            title = ""
            for sel in [
                r'class="thumb-video__description"[^>]*>(.*?)</a>',
                r'<h3>\s*<a[^>]*>(.*?)</a>',
            ]:
                m_t = re.search(sel, block, re.S)
                if m_t:
                    title = re.sub(r"<[^>]+>", "", m_t.group(1)).strip()
                    if title:
                        break
            if not title:
                continue
            title = self._unescape(title)

            # \u5c01\u9762\uff08data-src \u4f18\u5148\uff09
            pic = ""
            m_p = re.search(r'data-src="(https?://[^"]+)"', block)
            if not m_p:
                m_p = re.search(r'<img[^>]+src="(https?://[^"]+)"', block)
            if m_p:
                pic = m_p.group(1)

            # \u65f6\u957f\u89d2\u6807
            remark = ""
            m_r = re.search(r'class="duracion">\s*([\d:]+)\s*</span>', block)
            if m_r:
                remark = m_r.group(1).strip()

            # \u63d0\u53d6\u89c6\u9891 ID\uff08\u7528\u4e8e\u53bb\u91cd/\u9aa8\u67b6\u515c\u5e95\uff09
            vid = self._extract_vid(link)
            items.append({
                "vod_id": link,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": remark,
            })
        return items

    @staticmethod
    def _extract_vid(link):
        m = re.search(r"/video/([^/?#]+)", link)
        return m.group(1) if m else link

    @staticmethod
    def _unescape(s):
        if not s:
            return ""
        s = s.replace("&#039;", "'").replace("&quot;", '"')
        s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        s = s.replace("&#39;", "'").replace("&apos;", "'")
        return s.strip()

    @staticmethod
    def _norm_ids(ids):
        """\u6cd5\u521935\uff1aids \u517c\u5bb9 list/str/int/bytes"""
        if ids is None:
            return ""
        if isinstance(ids, (list, tuple)):
            if not ids:
                return ""
            ids = ids[0]
        if isinstance(ids, bytes):
            ids = ids.decode("utf-8", errors="ignore")
        return str(ids).strip()

    # ==================== \u8be6\u60c5 ====================

    def detailContent(self, ids):
        raw = self._norm_ids(ids)
        if not raw:
            return {"list": []}
        host = self._pick_host()
        page_url = raw if raw.startswith("http") else urljoin(host + "/", raw.lstrip("/"))

        vod = {
            "vod_id": raw,
            "vod_name": "",
            "vod_pic": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": "",
            "vod_play_from": "\u64ad\u653e",
            "vod_play_url": "",
        }
        try:
            r = self.fetch(page_url, headers=self.headers, timeout=15, verify=False)
            if not r or r.status_code != 200 or len(r.text or "") < 500:
                return self._skeleton(raw, vod)

            html = r.text

            # \u6807\u9898\uff1ah1 > og:title > title
            m = re.search(r"<h1>(.*?)</h1>", html, re.S)
            if m:
                vod["vod_name"] = self._unescape(re.sub(r"<[^>]+>", "", m.group(1)).strip())
            if not vod["vod_name"]:
                m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                if m:
                    vod["vod_name"] = self._unescape(m.group(1))
            if not vod["vod_name"]:
                m = re.search(r"<title>(.*?)</title>", html, re.S)
                if m:
                    vod["vod_name"] = self._unescape(m.group(1).replace("- SuperPorn", "").strip())

            # \u5c01\u9762\uff1aog:image
            m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
            if m:
                vod["vod_pic"] = m.group(1)

            # \u7b80\u4ecb\uff1a#resume
            m = re.search(r'id="resume"[^>]*>(.*?)</span>', html, re.S)
            if m:
                vod["vod_content"] = self._unescape(re.sub(r"<[^>]+>", "", m.group(1)).strip())

            # \u5206\u7c7b\u6807\u7b7e
            tags = re.findall(r'class="chip-link"[^>]*>.*?<span>(.*?)</span>', html, re.S)
            if tags:
                vod["vod_remarks"] = ",".join([self._unescape(t.strip()) for t in tags[:6]])

            # \u64ad\u653e\u76f4\u94fe\uff1a<source src="..."> \uff08\u4f18\u5148\uff09\uff0c\u515c\u5e95\u6b63\u5219\u6293 mp4/m3u8
            play_url = ""
            m = re.search(r'<source\s+src="([^"]+)"', html)
            if m:
                play_url = self._unescape(m.group(1))
            if not play_url:
                m = re.search(r'"(https?://[^"]+\.(?:mp4|m3u8)[^"]*)"', html)
                if m:
                    play_url = self._unescape(m.group(1))

            if play_url:
                vod["vod_play_from"] = "\u64ad\u653e"
                vod["vod_play_url"] = "\u64ad\u653e$" + play_url
            else:
                # \u9aa8\u67b6\u515c\u5e95\uff08\u6cd5\u521935\uff09
                return self._skeleton(raw, vod)

            return {"list": [vod]}
        except Exception as e:
            self.log({"detail": "exception", "error": str(e)})
            return self._skeleton(raw, vod)

    def _skeleton(self, vid, vod):
        """\u6cd5\u521935\uff1a\u9aa8\u67b6\u515c\u5e95\uff0c\u7981\u6b62\u8fd4\u56de\u7a7a list"""
        vod = dict(vod or {})
        vod["vod_id"] = vid
        vod["vod_name"] = vod.get("vod_name") or "\u672a\u77e5\u6807\u9898"
        vod["vod_play_from"] = "\u64ad\u653e"
        vod["vod_play_url"] = "\u64ad\u653e$" + str(vid)
        return {"list": [vod]}

    # ==================== \u641c\u7d22 ====================

    def searchContent(self, key, quick, pg="1"):
        host = self._pick_host()
        page = int(pg or 1)
        url = "%s/search?q=%s" % (host, quote(str(key or ""), safe=""))
        if page > 1:
            url += "&page=%d" % page
        r = self.fetch(url, headers=self.headers, timeout=15, verify=False)
        if not r or r.status_code != 200:
            self.log({"search": "fetch_failed", "url": url})
            return {"list": [], "page": page}
        return {"list": self._parse_list(r.text, host), "page": page}

    # ==================== \u64ad\u653e ====================

    def playerContent(self, flag, id, vipFlags):
        play_url = str(id) if id else ""
        # id \u53ef\u80fd\u4e3a "\u540d\u79f0$\u5730\u5740" \u683c\u5f0f
        if "$" in play_url:
            parts = play_url.split("$", 1)
            if len(parts) == 2 and parts[1].strip():
                play_url = parts[1]
        # \u8865\u5168\u534f\u8bae
        if play_url and not play_url.startswith("http"):
            play_url = "https://" + play_url.lstrip("/")

        if not play_url:
            return {"parse": 1, "url": "", "header": self.headers}

        # \u76f4\u94fe\uff08mp4/m3u8\uff09\u76f4\u63a5\u8fd4\u56de\uff0cparse:0
        if self.isVideoFormat(play_url) or play_url.startswith("http"):
            return {
                "parse": 0,
                "url": play_url,
                "header": {
                    "User-Agent": self.headers["User-Agent"],
                    "Referer": self.host + "/",
                },
            }
        return {"parse": 1, "url": play_url, "header": self.headers}

    # ==================== \u63a8\u8350 ====================

    def recommendContent(self, ids, pg):
        raw = self._norm_ids(ids)
        if not raw:
            return {"list": []}
        host = self._pick_host()
        try:
            # related \u63a5\u53e3\u9700\u6570\u5b57\u89c6\u9891 ID\uff1b\u5148\u4ece\u8be6\u60c5\u9875\u53d6 data-stats-video-id
            vid = ""
            page_url = raw if raw.startswith("http") else urljoin(host + "/", raw.lstrip("/"))
            r0 = self.fetch(page_url, headers=self.headers, timeout=12, verify=False)
            if r0 and r0.status_code == 200:
                m = re.search(r'data-stats-video-id="(\d+)"', r0.text)
                if m:
                    vid = m.group(1)
            if not vid:
                # \u515c\u5e95\uff1a\u7528 related \u63a5\u53e3\u7684 slug \u7248\u4e0d\u53ef\u7528\uff0c\u76f4\u63a5\u8fd4\u56de\u7a7a
                return {"list": []}

            url = "%s/video/%s/related" % (self.api, vid)
            r = self.fetch(url, headers=self.headers, timeout=12, verify=False)
            if r and r.status_code == 200:
                data = r.json()
                items = data.get("videos") or []
                out = []
                for it in items:
                    if not isinstance(it, dict):
                        continue
                    link = it.get("url") or ""
                    if link and not str(link).startswith("http"):
                        link = host + "/" + str(link).lstrip("/")
                    title = it.get("title") or ""
                    if not link or not title:
                        continue
                    out.append({
                        "vod_id": link,
                        "vod_name": title,
                        "vod_pic": it.get("thumb") or "",
                        "vod_remarks": it.get("duration") or "",
                    })
                if out:
                    return {"list": out}
        except Exception as e:
            self.log({"recommend": "exception", "error": str(e)})
        return {"list": []}
