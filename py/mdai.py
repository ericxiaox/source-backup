# coding: utf-8
# \u9ebb\u8c46AI\u4f20\u5a92 - https://www.madouai.xyz/
# \u7ad9\u70b9\u7c7b\u578b: React SPA, API\u9a71\u52a8
# \u6700\u540e\u9a8c\u8bc1: 2026-08-30

import json
import re
import time
import urllib.parse
from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
    def getName(self):
        return "\u9ebb\u8c46AI\u4f20\u5a92"

    def __init__(self):
        self.host = "https://www.madouai.xyz"
        self.api = self.host + "/api/v1"
        self.ua = "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 Chrome/126 Mobile Safari/537.36"
        self._cache = {}
        self._cache_time = 0

        # \u5206\u7c7b\u5217\u8868 - \u7b2c\u4e00\u4e2a\u662f"\u77ed\u5267"\uff08\u4f7f\u7528short-dramas\u63a5\u53e3\uff09\uff0c\u5176\u4ed6\u4f7f\u7528videos\u63a5\u53e3
        self.classes = [
            {"type_id": "short_dramas", "type_name": "AI\u77ed\u5267"},
            {"type_id": "27", "type_name": "\u6bcf\u65e5\u66f4\u65b0"},
            {"type_id": "6", "type_name": "\u9ebb\u8c46\u539f\u521bAI"},
            {"type_id": "10", "type_name": "\u9ebb\u8c46x\u6027\u5427\u8054\u5408\u539f\u521b"},
            {"type_id": "9", "type_name": "\u9ebb\u8c46\u4f20\u5a92"},
            {"type_id": "13", "type_name": "\u6e05\u7eaf\u5c11\u5973"},
            {"type_id": "14", "type_name": "\u91cd\u53e3\u8c03\u6559"},
            {"type_id": "15", "type_name": "\u76f4\u64ad\u5927\u79c0"},
            {"type_id": "16", "type_name": "\u7f51\u7ea2\u4e3b\u64ad"},
            {"type_id": "17", "type_name": "\u5a9a\u9ed1\u6bcd\u72d7"},
            {"type_id": "18", "type_name": "\u767d\u864e\u5c11\u5973"},
            {"type_id": "19", "type_name": "\u9ed1\u6599\u5403\u74dc"},
            {"type_id": "1", "type_name": "\u56fd\u4ea7\u81ea\u62cd\uff08\u6700\u65b0\u66f4\u65b0\uff09"},
            {"type_id": "2", "type_name": "AV - \u4e2d\u6587\u5b57\u5e55"},
            {"type_id": "8", "type_name": "AV - \u65e0\u7801\u6d41\u51fa"},
            {"type_id": "4", "type_name": "\u63a2\u82b1\u5927\u795e"},
            {"type_id": "7", "type_name": "91\u5927\u795e"},
            {"type_id": "20", "type_name": "\u7834\u89e3\u5077\u62cd"},
            {"type_id": "28", "type_name": "\u4e16\u754c\u676f\u4e13\u680f"},
            {"type_id": "21", "type_name": "\u53cd\u5dee\u6bcd\u72d7"},
            {"type_id": "22", "type_name": "\u767d\u864e\u5ae9\u59b9"},
            {"type_id": "23", "type_name": "\u5bb6\u5ead\u4e71\u4f26"},
            {"type_id": "24", "type_name": "\u719f\u5973\u5077\u60c5"},
            {"type_id": "25", "type_name": "\u7f51\u9ec4\u539f\u521b"},
        ]

        # \u7b5b\u9009\u5668
        self.filters = {}
        for c in self.classes:
            self.filters[c["type_id"]] = []

    def init(self, extend=""):
        self.extend = extend or ""

    def getDependence(self):
        return []

    def destroy(self):
        self._cache = {}
        self._cache_time = 0

    def homeContent(self, filter=False):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter=False):
        return self.homeContent(filter)

    def homeVideoContent(self):
        try:
            # \u4f7f\u7528 videos API \u83b7\u53d6\u6700\u65b0\u89c6\u9891\u4f5c\u4e3a\u9996\u9875\u63a8\u8350
            data = self._api_get("/videos", {"page": 1, "size": 24})
            items = data.get("items", []) if data else []
            return {"list": self._parse_video_list(items)}
        except Exception as e:
            self.log("\u9996\u9875\u63a8\u8350\u5931\u8d25: %s" % str(e))
            return {"list": []}

    def categoryContent(self, tid, pg, filter=False, extend=""):
        page = self._int(pg, 1)
        ext = self._parse_extend(extend)

        try:
            tid = str(tid or "27")
            params = {"page": page, "size": 24}

            # \u5224\u65ad\u4f7f\u7528\u54ea\u4e2a\u63a5\u53e3
            if tid == "short_dramas":
                # \u77ed\u5267\u63a5\u53e3 - \u4f7f\u7528 /api/v1/short-dramas
                short_params = {"productId": 1, "sortBy": "heat", "page": page, "size": 24}
                data = self._api_get("/short-dramas", short_params)
                if not data:
                    return {"list": [], "page": page, "pagecount": 1, "limit": 24, "total": 0}
                items = data.get("items", [])
                total = self._int(data.get("total", 0))
                total_pages = self._int(data.get("totalPages", 1))
                return {
                    "list": self._parse_list(items),
                    "page": page,
                    "pagecount": total_pages or 1,
                    "limit": 24,
                    "total": total
                }

            # \u666e\u901a\u89c6\u9891\u63a5\u53e3 - \u4f7f\u7528 /api/v1/videos\uff08\u652f\u6301\u5206\u7c7b\u8fc7\u6ee4\uff09
            if tid != "all":
                params["categoryId"] = tid

            data = self._api_get("/videos", params)
            if not data:
                return {"list": [], "page": page, "pagecount": 1, "limit": 24, "total": 0}

            items = data.get("items", [])
            total = self._int(data.get("total", 0))
            total_pages = self._int(data.get("totalPages", 1))

            return {
                "list": self._parse_video_list(items),
                "page": page,
                "pagecount": total_pages or 1,
                "limit": 24,
                "total": total
            }
        except Exception as e:
            self.log("\u5206\u7c7b\u5931\u8d25 tid=%s pg=%s err=%s" % (tid, page, str(e)))
            return {"list": [], "page": page, "pagecount": 1, "limit": 24, "total": 0}

    def detailContent(self, ids):
        try:
            vid = ids[0] if isinstance(ids, list) else ids
            vid = str(vid).strip()
            if not vid:
                return {"list": []}

            # \u5148\u5c1d\u8bd5\u4f5c\u4e3a\u77ed\u5267\u83b7\u53d6\uff08\u591a\u96c6\uff09
            data = self._api_get("/short-dramas/%s" % vid, {"productId": 1})
            if data and data.get("episodes"):
                # \u77ed\u5267 - \u591a\u96c6
                vod = {
                    "vod_id": str(data.get("id", vid)),
                    "vod_name": data.get("title", ""),
                    "vod_pic": self._pic_url(data.get("coverUrl", "")),
                    "vod_remarks": "%s\u96c6" % data.get("episodeCount", 0) if data.get("episodeCount") else "",
                    "vod_content": data.get("description", ""),
                    "vod_actor": "",
                    "vod_director": "",
                    "vod_play_from": "\u9ebb\u8c46",
                    "vod_play_url": ""
                }
                # \u89e3\u6790\u5267\u96c6
                episodes = data.get("episodes", [])
                if episodes:
                    play_urls = []
                    for ep in episodes:
                        ep_no = ep.get("episodeNo", 1)
                        title = ep.get("title", "\u7b2c%s\u96c6" % ep_no)
                        video_url = ep.get("videoUrl", "")
                        if video_url:
                            play_urls.append("%s$%s" % (title, video_url))
                    if play_urls:
                        vod["vod_play_url"] = "#".join(play_urls)
                return {"list": [vod]}

            # \u518d\u5c1d\u8bd5\u4f5c\u4e3a\u666e\u901a\u89c6\u9891\u83b7\u53d6\uff08\u5355\u96c6\uff09
            data = self._api_get("/videos/%s" % vid)
            if data:
                vod = {
                    "vod_id": str(data.get("id", vid)),
                    "vod_name": data.get("title", ""),
                    "vod_pic": self._pic_url(data.get("coverUrl", "")),
                    "vod_remarks": data.get("categoryName", ""),
                    "vod_content": data.get("description", "") or data.get("title", ""),
                    "vod_actor": data.get("authorName", "") or "",
                    "vod_director": "",
                    "vod_play_from": "\u9ebb\u8c46",
                    "vod_play_url": ""
                }
                video_url = data.get("videoUrl", "")
                if video_url:
                    vod["vod_play_url"] = "\u64ad\u653e$" + video_url
                return {"list": [vod]}

            return {"list": []}
        except Exception as e:
            self.log("\u8be6\u60c5\u5931\u8d25: %s" % str(e))
            return {"list": []}

    def searchContent(self, key, quick=False, pg="1"):
        page = self._int(pg, 1)
        try:
            # \u4f7f\u7528 videos API \u7684 keyword \u53c2\u6570\u8fdb\u884c\u641c\u7d22
            params = {"keyword": key, "page": page, "size": 24}
            data = self._api_get("/videos", params)
            if data:
                items = data.get("items", [])
                if items:
                    return {"list": self._parse_video_list(items), "page": page}
            return {"list": [], "page": page}
        except Exception as e:
            self.log("\u641c\u7d22\u5931\u8d25: %s" % str(e))
            return {"list": [], "page": page}

    def playerContent(self, flag, id, vipFlags=None):
        try:
            if not id:
                return {"parse": 0, "url": "", "header": {}}

            # \u5982\u679c\u5df2\u7ecf\u5305\u542b\u5b8c\u6574URL\uff0c\u76f4\u63a5\u8fd4\u56de
            if id.startswith("http"):
                if ".m3u8" in id:
                    return {
                        "parse": 0,
                        "url": self._m3u8_proxy_url(id),
                        "header": {"User-Agent": self.ua}
                    }
                return {"parse": 0, "url": id, "header": {"User-Agent": self.ua}}

            # \u5426\u5219\u62fc\u63a5\u4ee3\u7406URL
            encoded_path = urllib.parse.quote(id, safe="")
            m3u8_url = "%s/api/v1/m3u8/proxy?path=%s" % (self.host, encoded_path)
            return {
                "parse": 0,
                "url": self._m3u8_proxy_url(m3u8_url),
                "header": {"User-Agent": self.ua, "Referer": self.host + "/"}
            }
        except Exception as e:
            self.log("\u64ad\u653e\u5931\u8d25: %s" % str(e))
            return {"parse": 1, "url": id, "header": {"User-Agent": self.ua, "Referer": self.host + "/"}}

    def recommendContent(self, ids, pg):
        try:
            vid = ids[0] if isinstance(ids, list) else ids
            vid = str(vid).strip()
            if not vid:
                return {"list": []}

            # \u4f7f\u7528\u540c\u5206\u7c7b\u63a8\u8350
            data = self._api_get("/short-dramas", {"productId": 1, "sortBy": "heat", "page": 1, "size": 12})
            items = data.get("items", []) if data else []
            # \u8fc7\u6ee4\u6389\u5f53\u524d\u89c6\u9891
            filtered = [it for it in items if str(it.get("id", "")) != vid]
            return {"list": self._parse_list(filtered[:10])}
        except Exception as e:
            self.log("\u63a8\u8350\u5931\u8d25: %s" % str(e))
            return {"list": []}

    def localProxy(self, param):
        """m3u8 \u4ee3\u7406 - \u900f\u4f20\u5e76\u8865\u5168\u5206\u7247\u5730\u5740"""
        try:
            target = ""
            if isinstance(param, dict):
                target = param.get("url", "") or param.get("source", "")
            else:
                target = str(param or "")

            if target.startswith("url="):
                target = target[4:]
            elif "url=" in target:
                qs = urllib.parse.parse_qs(urllib.parse.urlparse(target).query)
                if "url" in qs:
                    target = qs["url"][0]

            target = urllib.parse.unquote(str(target or ""))
            if not target or not re.match(r"^https?://", target, re.I):
                return [400, "text/plain", b"invalid url"]

            resp = self.fetch(target, headers={"User-Agent": self.ua, "Referer": self.host + "/"}, timeout=20)
            if not resp:
                return [502, "text/plain", b"fetch failed"]

            content = getattr(resp, "content", b"") or b""
            if not content and getattr(resp, "text", ""):
                content = resp.text.encode("utf-8", errors="ignore")

            if not content:
                return [502, "text/plain", b"empty content"]

            # \u5982\u679c\u662f m3u8\uff0c\u8fdb\u884c\u6e05\u6d17
            if b"#EXTM3U" in content[:512]:
                cleaned = self._clean_m3u8(content.decode("utf-8", errors="ignore"), target)
                return [200, "application/vnd.apple.mpegurl", cleaned.encode("utf-8")]

            # \u975e m3u8 \u76f4\u63a5\u900f\u4f20
            return [200, "application/octet-stream", content]
        except Exception as e:
            self.log("localProxy error: %s" % str(e))
            return [500, "text/plain", str(e).encode("utf-8", errors="ignore")]

    def _clean_m3u8(self, text, source_url):
        """\u6e05\u6d17 m3u8\uff1a\u91cd\u5199\u76f8\u5bf9\u8def\u5f84\u4e3a\u7edd\u5bf9\u8def\u5f84"""
        lines = [line.strip() for line in str(text or "").replace("\r", "").split("\n") if line.strip()]
        if not lines:
            return "#EXTM3U\n"

        # \u68c0\u6d4b\u662f\u5426\u591a\u7801\u7387
        if any(line.startswith("#EXT-X-STREAM-INF") for line in lines):
            out = []
            for line in lines:
                if line.startswith("#"):
                    out.append(line)
                else:
                    # \u5b50\u6d41\u5730\u5740\u6539\u4e3a\u4ee3\u7406
                    child = urllib.parse.urljoin(source_url, line)
                    if ".m3u8" in child.lower():
                        out.append(self._m3u8_proxy_url(child))
                    else:
                        out.append(child)
            return "\n".join(out) + "\n"

        # \u5355\u7801\u7387\uff1a\u91cd\u5199\u6240\u6709\u5206\u7247\u4e3a\u7edd\u5bf9\u8def\u5f84
        out = []
        for line in lines:
            if line.startswith("#EXT-X-KEY") or line.startswith("#EXT-X-MAP"):
                # \u91cd\u5199 KEY URI
                def repl(match):
                    uri = match.group(1)
                    if uri.startswith(("http://", "https://")):
                        return 'URI="' + uri + '"'
                    return 'URI="' + urllib.parse.urljoin(source_url, uri) + '"'
                out.append(re.sub(r'URI="([^"]+)"', repl, line))
            elif line and not line.startswith("#"):
                # \u5206\u7247\u5730\u5740\u8865\u5168
                if line.startswith(("http://", "https://")):
                    out.append(line)
                else:
                    out.append(urllib.parse.urljoin(source_url, line))
            else:
                out.append(line)

        return "\n".join(out) + "\n"

    def _m3u8_proxy_url(self, url):
        """\u751f\u6210\u4ee3\u7406\u5730\u5740"""
        if not url:
            return ""
        # getProxyUrl() \u5df2\u7ecf\u5305\u542b\u4e86 ?do=py\uff0c\u76f4\u63a5\u62fc\u63a5 url \u53c2\u6570
        proxy_base = self.getProxyUrl()
        if "?" in proxy_base:
            return proxy_base + "&url=" + urllib.parse.quote(str(url), safe="")
        else:
            return proxy_base + "?url=" + urllib.parse.quote(str(url), safe="")

    def _api_get(self, path, params=None):
        """\u901a\u7528 API GET \u8bf7\u6c42"""
        try:
            url = self.api + path
            headers = {
                "User-Agent": self.ua,
                "Accept": "application/json, text/plain, */*",
                "Referer": self.host + "/",
                "Origin": self.host
            }
            resp = self.fetch(url, params=params, headers=headers, timeout=15)
            if not resp:
                return None
            data = resp.json()
            if isinstance(data, dict) and data.get("code") == 200:
                return data.get("data")
            return data
        except Exception as e:
            self.log("API\u8bf7\u6c42\u5931\u8d25 %s: %s" % (path, str(e)))
            return None

    def _parse_list(self, items):
        """\u89e3\u6790\u77ed\u5267\u5217\u8868\u9879 (short-dramas)"""
        result = []
        seen = set()
        for it in items or []:
            try:
                vid = str(it.get("id", ""))
                if not vid or vid in seen:
                    continue
                seen.add(vid)
                result.append({
                    "vod_id": vid,
                    "vod_name": it.get("title", ""),
                    "vod_pic": self._pic_url(it.get("coverUrl", "")),
                    "vod_remarks": "%s\u96c6" % it.get("episodeCount", 0) if it.get("episodeCount") else "",
                    "vod_rating": str(it.get("rating", "")),
                })
            except Exception:
                continue
        return result

    def _parse_video_list(self, items):
        """\u89e3\u6790\u89c6\u9891\u5217\u8868\u9879 (videos)"""
        result = []
        seen = set()
        for it in items or []:
            try:
                vid = str(it.get("id", ""))
                if not vid or vid in seen:
                    continue
                seen.add(vid)
                # \u65f6\u957f\u683c\u5f0f\u5316
                dur = it.get("durationSec", 0)
                if dur > 0:
                    mins = dur // 60
                    secs = dur % 60
                    remark = "%d\u5206%d\u79d2" % (mins, secs) if mins > 0 else "%d\u79d2" % secs
                else:
                    remark = ""

                # \u5c01\u9762URL\u53ef\u80fd\u662f\u76f8\u5bf9\u8def\u5f84
                cover = it.get("coverUrl", "")
                if cover and not cover.startswith("http"):
                    cover = self.host + "/" + cover.lstrip("/")

                result.append({
                    "vod_id": vid,
                    "vod_name": it.get("title", ""),
                    "vod_pic": cover,
                    "vod_remarks": remark,
                    "vod_rating": str(it.get("viewCount", 0)),
                    "categoryName": it.get("categoryName", ""),
                })
            except Exception:
                continue
        return result

    def _pic_url(self, url):
        """\u8865\u5168\u56fe\u7247URL"""
        if not url:
            return ""
        if url.startswith("http"):
            return url
        return self.host + url

    def _parse_extend(self, extend):
        """\u89e3\u6790 extend \u53c2\u6570"""
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

    def _int(self, v, default=0):
        try:
            return int(v)
        except Exception:
            return default