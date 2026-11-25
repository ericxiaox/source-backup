# coding=utf-8
"""
51\u77ed\u5267 AI \u7248 \u2014\u2014 2026-11-14 \u6309\u7ad9\u65b9 2026-11-12 \u5927\u6539\u7248\u6574\u5957\u91cd\u5199\u3002

\u65e7\u7248\uff08Nuxt SSR\uff09\u5df2\u5168\u90e8\u4f5c\u5e9f\uff1a
  - \u65e7\u8def\u5f84 rank-drama/week/\u3001explore-drama/\u3001drama-detail/\u3001play/\u3001search-drama/ \u5168 404\uff1b
  - \u65e7\u6570\u636e\u8f7d\u4f53 <script id=\"__NUXT_DATA__\"> \u5df2\u4e0d\u5b58\u5728 \u21d2 \u539f\u89e3\u6790\u5668\u6052 0 \u6761\uff08\u4f53\u68c0\u5b9e\u6d4b\uff09\u3002
  - \u8fde\u5e26\u5e9f\u5f03\uff1aAES \u56fe\u5e8a\u89e3\u5bc6\u3001\u52a0\u5bc6 API\u3001\u5f39\u5e55 XML\u3001\u672c\u5730\u56fe\u7247\u6620\u5c04\u6587\u4ef6\u3002

\u65b0\u7248\uff08\u670d\u52a1\u7aef\u6e32\u67d3 HTML\uff09\uff1a
  - \u680f\u76ee /recommend/{pg}/\u3001/newest/{pg}/\u3001/ai-duanju/{pg}/\u3001/ai-manju/{pg}/ \u2026
    /tag/{slug}/ \u7684\u5206\u9875\u5374\u662f /tag/{slug}/page/{pg}/\uff08\u4e0e\u680f\u76ee\u4e0d\u540c\uff0c\u522b\u7167\u6284\uff09\u3002
  - \u5217\u8868\u5361\u7247 .hg-card-grid .hg-drama-card\uff08\u6bcf\u9875 20 \u6761\uff09\u3002\u641c\u7d22\u5efa\u8bae\u5f39\u5c42\u3001\u4fa7\u680f\u63a8\u8350\u91cc\u7684
    \u540c\u540d\u5361\u7247\u4e0d\u5728 .hg-card-grid \u5185\uff0c\u7528\u5bb9\u5668\u9650\u5b9a\u5373\u5929\u7136\u6392\u9664\uff0c\u4e0d\u80fd\u5168\u9875\u626b\u3002
    \u6392\u884c\u699c\u9875 /ranks/hot/ \u53e6\u7528 .hg-rank-item\uff0825 \u6761\uff0c\u65e0\u5206\u9875\uff09\u3002
  - \u6807\u9898 <a> \u5185\u6df7\u6709 <span class=\"sr-only\">\u5168\u96c6\u5728\u7ebf\u89c2\u770b</span>\uff0c\u53d6 a[0].text \u624d\u5e72\u51c0\u3002
  - \u8be6\u60c5\u5373\u64ad\u653e\u9875 /video/{id}/\uff0c\u7b2c N \u96c6 /video/{id}/ep-{N}/\u3002
    <script id=\"videoInitialData\" type=\"application/json\"> \u5185\u542b
      title / coverSrc / description / tags / tracking.total_episode /
      epPlaySrcs\uff08\u5f53\u524d\u96c6 \u00b11 \u7684\u6ed1\u52a8\u7a97\u53e3\uff0c\u6700\u591a 3 \u6761\uff09/ videoSrc\uff08\u5f53\u524d\u96c6\u76f4\u94fe\uff0c\u5e26\u65f6\u6548\u7968\u636e\uff09\u3002
    \u21d2 \u6bcf\u96c6\u5728\u81ea\u5df1\u7684\u96c6\u9875\u53d6 videoSrc\uff1b\u7f3a\u76f4\u94fe\u65f6\u539f\u6837\u8fd4\u56de\u96c6\u9875\u5730\u5740\u5e76\u6253\u65e5\u5fd7\uff0c
      \U0001f6a9 \u7edd\u4e0d\u515c\u5e95\u5230\u7b2c\u4e00\u96c6\uff082026-10-26 \u65e7\u7248\u8840\u6559\u8bad\uff09\u3002
  - \u641c\u7d22\u5fc5\u987b\u8d70\u9759\u6001\u8def\u5f84 /search/keyword/{\u8bcd}/{pg}/\u3002
    /search/?q= \u53ea\u662f\u8df3\u8f6c\u5165\u53e3\uff0cCloudFront \u7f13\u5b58\u5ffd\u7565 query string\uff0c\u5b9e\u6d4b\u8bf7\u6c42\u300c\u4e3d\u6625\u9662\u300d
    \u4f1a\u62ff\u5230\u300c\u6559\u5b66 \u7b2c2\u9875\u300d\u7684\u7ed3\u679c\uff1b\u4e14 301 \u76ee\u6807\u7531 cookie \u51b3\u5b9a \u21d2 \u7edd\u4e0d\u53ef\u7528\u3002
    \u547d\u4e2d\u9875\u6709\u300c\u5171 N \u4e2a\u7ed3\u679c\u300d\uff1b\u65e0\u547d\u4e2d\u9875\u6ca1\u6709\u8fd9\u884c\uff0c\u5374\u585e 7 \u5f20\u300c\u731c\u4f60\u559c\u6b22\u300d\u5361 \u21d2 \u5fc5\u987b\u5148\u5224\u7a7a\u3002

\u53d6\u57df\uff082026-11-14 \u5b9a\u6848\uff09\uff1a
  - \u53d1\u5e03\u9875 https://51dj20.com/ \u2192 \u8df3\u677f \u2192 Base64 \u89e3\u7801\u9875\u91cc\u5217\u7740\u771f\u5b9e\u56fa\u5b9a\u57df\u3002
  - \u65e7\u5b9e\u73b0\u9760 words.random() \u62fc\u300c\u968f\u673a\u524d\u7f00 + .henoceapn.cc\u300d\u57df\uff0c\u5b9e\u6d4b 8 \u4e2a\u5168\u90e8\u8fde\u4e0d\u4e0a
    \uff1d \u5047\u81ea\u6108\uff08\u6280\u80fd\u4e66 \u5171\u7528/03 \u00a7\u5341\uff09\uff1b\u73b0\u6539\u4e3a\u5148\u8bd5\u5185\u7f6e\u6d3b\u57df\uff0c\u5168\u6302\u624d\u4ece\u53d1\u5e03\u9875\u62bd\u94fe\u9010\u4e2a\u9a8c\u9996\u9875\u7279\u5f81\u3002
"""
import base64
import json
import re
import time
import urllib.parse

import requests
from base.spider import Spider
from pyquery import PyQuery as pq

PUBLISH = "https://51dj20.com/"
# 2026-11-14 \u5b9e\u6d4b\u53ef\u8fbe\u3001\u4e14\u8fd4\u56de\u65b0\u7248 HTML \u7684\u56fa\u5b9a\u57df\uff08\u53d1\u5e03\u9875\u89e3\u7801\u5185\u5bb9\u91cc\u4e5f\u6709\u5176\u4e00\uff09
FALLBACK_HOSTS = [
    "https://873f8.dikclehn.cc/",
    "https://ceiling.sysrycady.com/",
]
_LAST_GOOD = ["", 0.0]      # [host, expire_ts]
_HOST_TTL = 600
_EP_CACHE = {}              # {sid: {ep: (ts, m3u8)}}
_EP_TTL = 300               # \u76f4\u94fe\u5e26 auth_key \u65f6\u6548\u7968\u636e\uff0c\u7f13\u5b58 5 \u5206\u949f\u540e\u91cd\u53d6

CLASSES = [
    {"type_id": "recommend",    "type_name": "\u63a8\u8350"},
    {"type_id": "newest",       "type_name": "\u6700\u65b0"},
    {"type_id": "rank_hot",     "type_name": "\u6392\u884c\u699c"},
    {"type_id": "ai_duanju",    "type_name": "AI\u77ed\u5267"},
    {"type_id": "ai_manju",     "type_name": "AI\u6f2b\u5267"},
    {"type_id": "ai_huanlian",  "type_name": "AI\u6362\u8138"},
    {"type_id": "ai_mogai",     "type_name": "AI\u9b54\u6539"},
    # 2026-11-25\uff1a\u539f tag_chengren(\u6210\u4eba) / tag_lunli(\u4f26\u7406) \u53cc\u53cc\u5931\u6548\u2014\u2014
    #   /tag/chengren/ \u662f**\u793e\u533a\u5e16\u5b50\u805a\u5408\u9875**\uff08h1\u300c#\u6210\u4eba\u300d\uff0c\u5361\u7247 0\uff09\uff0c\u4e0d\u662f\u77ed\u5267\u5217\u8868\uff1b
    #   /tag/lunli/ \u7ad9\u65b9\u6839\u672c\u6ca1\u8fd9\u4e2a slug\uff08404 \u9875\u4f1a\u585e 8 \u5f20\u63a8\u8350\u5361\uff0c\u770b\u7740\u50cf\u6709\u5185\u5bb9\uff09\u3002
    #   \u5df2\u6362\u6210\u7ad9\u65b9\u771f\u5b9e\u77ed\u5267\u6807\u7b7e yinluan / luanlun\uff0832 \u4e2a tag \u89c1\u9996\u9875\u6807\u7b7e\u533a\uff09\uff0c\u5747 27 \u5361\u3002
    {"type_id": "tag_yinluan",  "type_name": "\u6deb\u4e71\u6807\u7b7e"},
    {"type_id": "tag_luanlun",  "type_name": "\u4e71\u4f26\u6807\u7b7e"},
    {"type_id": "tag_doushi",   "type_name": "\u90fd\u5e02\u6807\u7b7e"},
]
CAT_PATH = {
    "recommend": "recommend",
    "newest": "newest",
    "rank_hot": "ranks/hot",
    "ai_duanju": "ai-duanju",
    "ai_manju": "ai-manju",
    "ai_huanlian": "ai-huanlian",
    "ai_mogai": "ai-mogai",
}


class Spider(Spider):
    def getName(self):
        return "51\u77ed\u5267"

    def init(self, extend=""):
        self.ua = "Mozilla/5.0 (Linux; Android 16; Pixel 8) AppleWebKit/537.36 Chrome/143.0.0.0 Mobile Safari/537.36"
        self.headers = {
            "User-Agent": self.ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        self.session = requests.Session()
        self.host = FALLBACK_HOSTS[0]
        self._resolve_domain()
        self.headers["Referer"] = self.host

    # ---------- \u53d6\u57df ----------
    def _alive(self, url):
        try:
            h = dict(self.headers)
            h["Cache-Control"] = "no-cache"
            r = self.session.get(url, headers=h, timeout=8, verify=False)
            body = r.content.decode("utf-8", "ignore")
            return r.status_code == 200 and "hg-drama-card" in body and "51\u77ed\u5267" in body[:4000]
        except Exception:
            return False

    def _from_publish(self):
        """\u53d1\u5e03\u9875 \u2192 \u8df3\u677f \u2192 Base64 \u89e3\u7801\u9875 \u2192 \u62bd\u56fa\u5b9a\u57df \u2192 \u9010\u4e2a\u9a8c\u9996\u9875\u3002\u62bd 0 \u6761\u7b97\u5931\u8d25\uff0c\u4e0d\u4f2a\u9020\u3002"""
        try:
            r = self.session.get(PUBLISH, headers=self.headers, timeout=10, verify=False)
            m = re.search(r'<a[^>]+href=["\'](https?://[^"\']+)', r.text, re.I)
            if not m:
                return ""
            jump_url = m.group(1)
            jump = self.session.get(jump_url, headers=self.headers, timeout=10, verify=False).text
            jump_host = urllib.parse.urlparse(jump_url).netloc.lower()
            m = re.search(r'Base64\.decode\(["\']([^"\']+)["\']\)', jump, re.I)
            if not m:
                return ""
            page = base64.b64decode(m.group(1)).decode("utf-8", "ignore")
            doms = re.findall(r'https?://([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.cc)', page, re.I)
            cand, seen = [], set()
            for d in doms:
                d = d.lower()
                if d in seen or d == jump_host or d.endswith("." + jump_host) or "51dj20" in d:
                    continue
                seen.add(d)
                cand.append("https://" + d + "/")
            print("[51\u77ed\u5267] \u53d1\u5e03\u9875\u62bd\u5230 %d \u4e2a\u5019\u9009\u57df" % len(cand))
            for u in cand[:8]:
                if self._alive(u):
                    return u
        except Exception as e:
            print("[51\u77ed\u5267] \u53d1\u5e03\u9875\u53d6\u57df\u5931\u8d25: %s" % e)
        return ""

    def _resolve_domain(self):
        if _LAST_GOOD[0] and _LAST_GOOD[1] > time.time():
            self.host = _LAST_GOOD[0]
            return
        host = ""
        for u in FALLBACK_HOSTS:
            if self._alive(u):
                host = u
                break
        if not host:
            host = self._from_publish()
        if not host:
            host = FALLBACK_HOSTS[0]      # \u5168\u6302\u4e5f\u4e0d\u5199\u6b7b\u7a7a\uff0c\u7559\u7ed9 _req \u62a5\u9519\u4e0e\u4e0b\u6b21\u91cd\u8bd5
            print("[51\u77ed\u5267] \u672a\u53d6\u5230\u6d3b\u57df\uff0c\u6682\u7528\u5185\u7f6e\u9996\u9009")
        self.host = host
        _LAST_GOOD[0], _LAST_GOOD[1] = host, time.time() + _HOST_TTL
        print("[51\u77ed\u5267] \u57df\u540d: %s" % host)

    def _req(self, url):
        try:
            r = self.session.get(url, headers=self.headers, timeout=15, verify=False)
            if r.status_code != 200:
                if _LAST_GOOD[0] and str(url).startswith(_LAST_GOOD[0]):
                    _LAST_GOOD[0], _LAST_GOOD[1] = "", 0.0   # \u6362\u57df\u540e\u522b\u88ab\u9489\u5728 TTL \u91cc
                return ""
            return r.content.decode("utf-8", "ignore")
        except Exception as e:
            print("[51\u77ed\u5267] \u8bf7\u6c42\u5931\u8d25: %s %s" % (url, e))
            return ""

    # ---------- \u901a\u7528\u89e3\u6790 ----------
    def _fix(self, u):
        u = str(u or "").replace("\\u002F", "/").replace("\\/", "/")
        if u.startswith("http"):
            return u
        return self.host.rstrip("/") + "/" + u.lstrip("/")

    def _initial(self, html):
        m = re.search(r'<script[^>]*id=["\']videoInitialData["\'][^>]*>(.*?)</script>', html or "", re.S | re.I)
        if not m:
            return {}
        try:
            return json.loads(m.group(1).strip()) or {}
        except Exception:
            return {}

    def _card_vod(self, c):
        a = c.find(".hg-drama-card__title a")
        if not a:
            return None
        title = (a[0].text or "").strip()          # \u53ea\u53d6\u9996\u4e2a\u6587\u672c\u8282\u70b9\uff0c\u7529\u6389 sr-only
        link = c.find(".hg-drama-card__cover-link").attr("href") or a.attr("href") or ""
        if not title or not link or "/video/" not in link:
            return None
        img = c.find(".hg-drama-card__cover-link img")
        pic = img.attr("data-src") or img.attr("src") or ""
        if "cover-placeholder" in pic:
            pic = ""
        ep = c.find(".hg-drama-card__episode").text() or ""
        m = re.search("(\u5168\\d+\u96c6|\u66f4\u65b0\u81f3\\d+\u96c6)", ep)
        return {
            "vod_id": self._fix(link),
            "vod_name": title,
            "vod_pic": self._fix(pic) if pic else "",
            "vod_remarks": m.group(1) if m else "",
            "vod_tag": "",
        }

    def _cards(self, html):
        if not html:
            return []
        out, seen = [], set()
        for c in pq(html)(".hg-card-grid .hg-drama-card").items():
            v = self._card_vod(c)
            if v and v["vod_id"] not in seen:
                seen.add(v["vod_id"])
                out.append(v)
        return out

    def _ranks(self, html):
        if not html:
            return []
        out, seen = [], set()
        for it in pq(html)(".hg-rank-item").items():
            a = it.find(".hg-rank-item__cover")
            link = a.attr("href") or ""
            title = it.find(".hg-rank-item__title a").text().strip() or it.attr("data-track-title") or ""
            if not title or "/video/" not in link:
                continue
            img = a.find("img")
            pic = img.attr("data-src") or ""
            if "cover-placeholder" in pic:
                pic = ""
            v = {"vod_id": self._fix(link), "vod_name": title,
                 "vod_pic": self._fix(pic) if pic else "",
                 "vod_remarks": "\u699c%s" % (it.attr("data-rank") or "?"), "vod_tag": ""}
            if v["vod_id"] not in seen:
                seen.add(v["vod_id"])
                out.append(v)
        return out

    def _pager(self, html, pg, count):
        """\u4ece .hg-pager a[href] \u6293\u6700\u5927\u9875\u7801\uff1b\u6ca1\u6709\u5206\u9875\u6761\u5c31\u6309\u672c\u9875\u6761\u6570\u4f30\u3002"""
        top = pg
        for a in pq(html or "")(".hg-pager a[href]").items():
            m = re.search(r"/(\d+)/?$", str(a.attr("href") or ""))
            if m:
                top = max(top, int(m.group(1)))
        if top == pg and count >= 20:
            top = pg + 1
        return top

    def _empty(self, pg):
        return {"list": [], "page": pg, "pagecount": pg, "limit": 20, "total": 0}

    # ---------- \u5165\u53e3 ----------
    def homeContent(self, filter):
        return {"class": CLASSES, "filters": {}, "list": self._cards(self._req(self.host))}

    def homeVideoContent(self):
        return self._cards(self._req(self.host))

    def _url(self, cid, pg):
        cid = str(cid)
        if cid in CAT_PATH:
            base = self.host + CAT_PATH[cid] + "/"
            if cid == "rank_hot":
                return base
            return base if pg <= 1 else base + str(pg) + "/"
        if cid.startswith("tag_"):
            slug = cid[4:]
            base = self.host + "tag/" + slug + "/"
            return base if pg <= 1 else base + "page/" + str(pg) + "/"
        # \u517c\u5bb9\u65e7\u7f13\u5b58\u91cc\u7684\u5206\u7c7b id
        if cid in ("drama", "drama_week", "drama_month", "aisd"):
            return self._url("recommend", pg)
        return self.host

    def categoryContent(self, cid, pg, filter, ext):
        try:
            pg = int(pg) if str(pg).isdigit() else 1
            pg = max(1, pg)
            html = self._req(self._url(cid, pg))
            # \u7ad9\u65b9\u5bf9\u4e0d\u5b58\u5728\u7684\u680f\u76ee/slug \u4f1a\u8fd4\u56de 200 \u7684\u9519\u9875\uff0c\u9875\u91cc\u8fd8\u585e 8 \u5f20\u300c\u63a8\u8350\u300d\u5361\u2014\u2014
            # \u4e0d\u5148\u5224\u9519\u9875\u5c31\u4f1a\u628a\u4e0d\u76f8\u5e72\u5185\u5bb9\u5f53\u6210\u8be5\u5206\u7c7b\u7ed3\u679c\uff082026-11-25 tag_lunli \u4e8b\u6545\uff09\u3002
            head = (html or "")[:8000]
            if not html or "\u9875\u9762\u672a\u627e\u5230" in head or "\u8bbf\u95ee\u7684\u9875\u9762\u51fa\u9519\u4e86" in head:
                return self._empty(pg)
            vods = self._ranks(html) if str(cid) == "rank_hot" else self._cards(html)
            if not vods:
                return self._empty(pg)
            pagecount = 1 if str(cid) == "rank_hot" else self._pager(html, pg, len(vods))
            print("[51\u77ed\u5267] \u5206\u7c7b %s \u7b2c%d\u9875: %d \u6761 / \u5171%d\u9875" % (cid, pg, len(vods), pagecount))
            return {"list": vods, "page": pg, "pagecount": pagecount,
                    "limit": 20, "total": pagecount * 20}
        except Exception as e:
            print("[51\u77ed\u5267] \u5206\u7c7b\u5931\u8d25: %s" % e)
            return self._empty(1)

    def _sid(self, vid):
        s = str(vid or "")
        m = re.search(r"/video/(\d+)", s) or re.search(r"[?&](?:id|video_id)=(\d+)", s)
        if m:
            return m.group(1)
        m = re.search(r"/(?:drama-detail|drama-play|play|actor-detail)/(\d+)", s)
        if m:
            return m.group(1)
        m = re.search(r"(\d+)", s)
        return m.group(1) if m else ""

    def _ep_url(self, sid, ep):
        return self.host + "video/" + str(sid) + "/" + (("ep-" + str(ep) + "/") if ep > 1 else "")

    def detailContent(self, ids):
        try:
            sid = self._sid(ids[0])
            if not sid:
                return {"list": []}
            html = self._req(self._ep_url(sid, 1))
            d = self._initial(html)
            if not d:
                return {"list": []}
            title = str(d.get("title") or "")
            pic = str(d.get("coverSrc") or d.get("posterSrc") or "")
            desc = str(d.get("description") or "")
            tags = [str(x) for x in (d.get("tags") or [])]
            tr = d.get("tracking") or {}
            try:
                total = int(tr.get("total_episode") or 0)
            except Exception:
                total = 0
            total = max(total, int(d.get("ep") or 1), 1)
            srcs = d.get("epPlaySrcs") or {}
            now = time.time()
            slot = _EP_CACHE.setdefault(sid, {})
            for k, v in srcs.items():
                if v:
                    slot[str(k)] = (now, str(v).replace("\\u0026", "&"))
            eps = ["\u7b2c%d\u96c6$%s" % (n, self._ep_url(sid, n)) for n in range(1, total + 1)]
            return {"list": [{
                "vod_id": self._ep_url(sid, 1),
                "vod_name": title,
                "vod_pic": self._fix(pic) if pic else "",
                "vod_content": desc,
                "vod_remarks": "\u5168%d\u96c6" % total,
                "vod_year": str(d.get("time") or "")[:4],
                "vod_tag": ",".join(tags),
                "vod_play_from": "51\u77ed\u5267",
                "vod_play_url": "#".join(eps),
            }]}
        except Exception as e:
            print("[51\u77ed\u5267] \u8be6\u60c5\u5931\u8d25: %s" % e)
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        try:
            pg = max(1, int(pg) if str(pg).isdigit() else 1)
            kw = str(key or "").strip()
            if not kw:
                return self._empty(pg)
            u = self.host + "search/keyword/" + urllib.parse.quote(kw) + "/"
            if pg > 1:
                u += str(pg) + "/"
            html = self._req(u)
            if not html:
                return self._empty(pg)
            # \u65e0\u547d\u4e2d\u9875\u585e\u7684\u662f\u300c\u731c\u4f60\u559c\u6b22\u300d\u5361\uff0c\u5fc5\u987b\u7528\u547d\u4e2d\u6570\u5224\u7a7a\uff0c\u5426\u5219\u641c\u5783\u573e\u8bcd\u4f1a\u51fa\u4e00\u5806\u4e0d\u76f8\u5e72\u6761\u76ee
            txt = pq(html)(".hg-list-page").text()
            m = re.search("\u5171\\s*(\\d+)\\s*\u4e2a\u7ed3\u679c", txt)
            if not m or int(m.group(1)) == 0:
                return self._empty(pg)
            total = int(m.group(1))
            vods = self._cards(html)
            pagecount = self._pager(html, pg, len(vods))
            print("[51\u77ed\u5267] \u641c\u7d22 %s \u7b2c%d\u9875: %d \u6761 / \u547d\u4e2d%d / \u5171%d\u9875" % (kw, pg, len(vods), total, pagecount))
            return {"list": vods, "page": pg, "pagecount": pagecount,
                    "limit": 20, "total": total}
        except Exception as e:
            print("[51\u77ed\u5267] \u641c\u7d22\u5931\u8d25: %s" % e)
            return self._empty(1)

    def isVideoFormat(self, url):
        return bool(re.search(r"\.(m3u8|mp4|m4v|ts)(\?|$)", str(url), re.I))

    def playerContent(self, flag, id, vipFlags):
        url = str(id or "").replace("\\u002F", "/").replace("\\/", "/")
        ret = {"parse": 0, "url": url, "header": json.dumps(self.headers, ensure_ascii=False)}
        try:
            if self.isVideoFormat(url):
                return ret
            sid, ep = self._sid(url), 0
            m = re.search(r"/video/\d+/ep-(\d+)", url)
            if m:
                ep = int(m.group(1))
            else:
                m = re.search(r"/play/\d+/(\d+)", url)     # \u65e7\u7248\u96c6\u9875 URL \u517c\u5bb9
                if m:
                    ep = int(m.group(1))
                elif "drama-play" in url or "episode_id=" in url:
                    # \u65e7\u7248 episode_id \u4e0e\u65b0\u7248\u96c6\u5e8f\u53f7\u662f\u4e24\u5957 id\uff0c\u65e0\u6cd5\u6620\u5c04 \u21d2 \u4e0d\u731c\u3001\u4e0d\u4e32\u96c6
                    print("[51\u77ed\u5267] \u65e7\u7248\u96c6\u5730\u5740\u65e0\u6cd5\u6620\u5c04\uff0c\u8fd4\u56de\u539f\u5730\u5740\uff0c\u8bf7\u91cd\u65b0\u4ece\u8be6\u60c5\u70b9\u9009")
                    return ret
                else:
                    ep = 1
            if not sid:
                return ret
            src = ""
            slot = _EP_CACHE.get(sid) or {}
            hit = slot.get(str(ep))
            if hit and time.time() - hit[0] < _EP_TTL:
                src = hit[1]
            if not src:
                d = self._initial(self._req(self._ep_url(sid, ep)))
                src = str(d.get("videoSrc") or (d.get("epPlaySrcs") or {}).get(str(ep)) or "")
                src = src.replace("\\u0026", "&")
                now = time.time()
                for k, v in (d.get("epPlaySrcs") or {}).items():
                    if v:
                        slot[str(k)] = (now, str(v).replace("\\u0026", "&"))
                _EP_CACHE[sid] = slot
                if src:
                    slot[str(ep)] = (now, src)
            if not src:
                print("[51\u77ed\u5267] %s \u7b2c%d\u96c6\u65e0\u76f4\u94fe\uff0c\u4e0d\u505a\u515c\u5e95\u4e32\u96c6" % (sid, ep))
                return ret
            ret["url"] = src
            return ret
        except Exception as e:
            print("[51\u77ed\u5267] \u64ad\u653e\u89e3\u6790\u5931\u8d25: %s" % e)
            return ret

    def localProxy(self, param):
        # \u65b0\u7248\u5c01\u9762\u662f\u666e\u901a\u56fe\u5e8a\u76f4\u94fe\u3001\u65e0\u52a0\u5bc6\uff1b\u5f39\u5e55\u63a5\u53e3\u5df2\u968f\u65e7\u7248\u4e00\u8d77\u4e0b\u7ebf
        return [404, "text/plain", "", {}]

    def destroy(self):
        try:
            self.session.close()
        except Exception:
            pass
