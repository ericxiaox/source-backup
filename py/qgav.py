# -*- coding: utf-8 -*-
# \u7ad9\u70b9\u4fe1\u606f
# \u4e3b\u57df\u540d: https://chineseav.xyz
# API\u57df\u540d: https://chavapi.freeaav.xyz
# API Token: chineseav_2026_secret
# \u5185\u5bb9\u7c7b\u578b: \u56fd\u4ea7AV\u89c6\u9891\u805a\u5408
# \u6765\u6e90: https://chineseav.xyz
# \u6700\u540e\u9a8c\u8bc1: 2026-08-31
# m3u8\u7ed3\u6784\u6458\u8981: \u89c6\u9891\u4e3amp4\u76f4\u94fe\uff0c\u65e0m3u8\u5e7f\u544a\u8fc7\u6ee4\u9700\u6c42

import json
import urllib.parse
import re
from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    def __init__(self):
        self.api_base = "https://chavapi.freeaav.xyz"
        self.api_token = "chineseav_2026_secret"
        self.site_name = "\u5f37\u570bAV"
        self.host = "https://chineseav.xyz"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-API-Token": self.api_token,
            "Accept": "application/json"
        }
        # \u786c\u7f16\u7801\u5206\u7c7b\uff08\u6765\u81ea /api/categories \u63a5\u53e3\uff09
        self.classes = [
            {"type_id": "91\u5236\u7247\u5382", "type_name": "91\u5236\u7247\u5382"},
            {"type_id": "Hong Kong Doll", "type_name": "Hong Kong Doll"},
            {"type_id": "Pussy Hunter", "type_name": "Pussy Hunter"},
            {"type_id": "SA\u56fd\u9645\u4f20\u5a92", "type_name": "SA\u56fd\u9645\u4f20\u5a92"},
            {"type_id": "\u0053\u0057\u0041\u0047 Live", "type_name": "\u0053\u0057\u0041\u0047 Live"},
            {"type_id": "\u0053\u0077\u0061\u0067 A\u7247", "type_name": "\u0053\u0077\u0061\u0067 A\u7247"},
            {"type_id": "\u4e9e\u88d4\u7d20\u4eba\u7db2\u7d05", "type_name": "\u4e9e\u88d4\u7d20\u4eba\u7db2\u7d05"},
            {"type_id": "\u5370\u5ea6\u5a4a\u5b50", "type_name": "\u5370\u5ea6\u5a4a\u5b50"},
            {"type_id": "\u5434\u68a6\u68a6\u9891\u9053", "type_name": "\u5434\u68a6\u68a6\u9891\u9053"},
            {"type_id": "\u570b\u7522AV", "type_name": "\u570b\u7522AV"},
            {"type_id": "\u5927\u8c61\u4f20\u5a92", "type_name": "\u5927\u8c61\u4f20\u5a92"},
            {"type_id": "\u5929\u7f8e\u4f20\u5a92", "type_name": "\u5929\u7f8e\u4f20\u5a92"},
            {"type_id": "\u5fae\u5bc6\u5708\u4f20\u5a92", "type_name": "\u5fae\u5bc6\u5708\u4f20\u5a92"},
            {"type_id": "\u661f\u7a7a\u65e0\u9650\u4f20\u5a92", "type_name": "\u661f\u7a7a\u65e0\u9650\u4f20\u5a92"},
            {"type_id": "\u674f\u5427\u539f\u521b", "type_name": "\u674f\u5427\u539f\u521b"},
            {"type_id": "\u679c\u51bb\u4f20\u5a92", "type_name": "\u679c\u51bb\u4f20\u5a92"},
            {"type_id": "\u6cf0\u56fd\u5a4a\u5b50", "type_name": "\u6cf0\u56fd\u5a4a\u5b50"},
            {"type_id": "\u7687\u5bb6\u534e\u4eba", "type_name": "\u7687\u5bb6\u534e\u4eba"},
            {"type_id": "\u7cbe\u4e1c\u4f20\u5a92", "type_name": "\u7cbe\u4e1c\u4f20\u5a92"},
            {"type_id": "\u8272\u63a7\u5de5\u4f5c\u5ba4", "type_name": "\u8272\u63a7\u5de5\u4f5c\u5ba4"},
            {"type_id": "\u83f2\u5f8b\u5bbe\u5a4a\u5b50", "type_name": "\u83f2\u5f8b\u5bbe\u5a4a\u5b50"},
            {"type_id": "\u871c\u6843\u4f20\u5a92", "type_name": "\u871c\u6843\u4f20\u5a92"},
            {"type_id": "\u97e9\u56fd\u5a4a\u5b50", "type_name": "\u97e9\u56fd\u5a4a\u5b50"},
            {"type_id": "\u9999\u8549\u89c6\u9891", "type_name": "\u9999\u8549\u89c6\u9891"},
            {"type_id": "\u9ebb\u8c46\u4f20\u5a92", "type_name": "\u9ebb\u8c46\u4f20\u5a92"},
        ]
        # filters - \u7b80\u5355\u7ad9\u65e0\u7b5b\u9009
        self.filters = {}

    def getName(self):
        return self.site_name

    def getDependence(self):
        return []

    def init(self, extend=""):
        self.extend = extend or ""

    def homeContent(self, filter=False):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter=False):
        return self.homeContent(filter)

    def homeVideoContent(self):
        """\u9996\u9875\u63a8\u8350 - \u83b7\u53d6\u6700\u65b0\u89c6\u9891\u5217\u8868"""
        try:
            result = self._fetch_api("/api/videos", {"page": "1", "sort": "newest"})
            if result and "data" in result:
                items = result["data"][:20]
                return {"list": self._parse_videos(items)}
            return {"list": []}
        except Exception as e:
            self.log({"action": "homeVideoContent_error", "error": str(e)})
            return {"list": []}

    def categoryContent(self, tid, pg, filter=False, extend=None):
        """\u5206\u7c7b\u5217\u8868 - \u6309\u9891\u9053/\u5206\u7c7b\u83b7\u53d6\u89c6\u9891"""
        try:
            page = str(pg) if pg else "1"
            # \u5206\u7c7b\u540d\u76f4\u63a5\u4f5c\u4e3a\u9891\u9053\u540d\u8bf7\u6c42
            url = "/api/videos/by-channels"
            params = {
                "channels": tid,
                "page": page,
                "sort": "newest"
            }
            result = self._fetch_api(url, params)
            if result and "data" in result:
                items = result["data"]
                # \u5982\u679c\u8fd4\u56de\u4e3a\u7a7a\uff0c\u8bf4\u660e\u6ca1\u6709\u66f4\u591a\u6570\u636e
                if not items:
                    return {"list": [], "page": int(page), "pagecount": int(page), "limit": 20, "total": 0}
                # \u5c1d\u8bd5\u4ece\u54cd\u5e94\u4e2d\u83b7\u53d6\u603b\u6570\uff0c\u5982\u679c\u6ca1\u6709\u5219\u4f30\u7b97
                total = result.get("total", 9999)
                # \u8ba1\u7b97\u603b\u9875\u6570\uff1a\u5982\u679c\u6bcf\u987520\u6761\uff0c\u7528total/20\uff0c\u4f46API\u53ef\u80fd\u8fd4\u56de\u5168\u90e8\u6570\u636e
                # \u5b9e\u9645\u4e0a\u8fd9\u4e2aAPI\u8fd4\u56de\u7684\u662f\u6240\u6709\u6570\u636e\uff0c\u6ca1\u6709\u5206\u9875\u4fe1\u606f\uff0c\u6211\u4eec\u7528\u8fd4\u56de\u7684\u6570\u636e\u91cf\u5224\u65ad
                pagecount = int(page) + 1  # \u81f3\u5c11\u7ed9\u4e00\u4e2a\u4e0b\u4e00\u9875\uff0c\u8ba9\u7528\u6237\u80fd\u7ee7\u7eed\u7ffb
                # \u4f46\u5982\u679c\u6570\u636e\u4e0d\u8db320\u6761\uff0c\u8bf4\u660e\u662f\u6700\u540e\u4e00\u9875
                if len(items) < 20:
                    pagecount = int(page)
                return {
                    "list": self._parse_videos(items),
                    "page": int(page),
                    "pagecount": pagecount,
                    "limit": 20,
                    "total": total if isinstance(total, int) else 9999
                }
            return {"list": [], "page": int(page), "pagecount": 1, "limit": 20, "total": 0}
        except Exception as e:
            self.log({"action": "categoryContent_error", "error": str(e)})
            return {"list": [], "page": int(pg or 1), "pagecount": 1, "limit": 20, "total": 0}
    def detailContent(self, ids):
        """\u89c6\u9891\u8be6\u60c5"""
        try:
            if not ids:
                return {"list": []}
            vid = ids[0]
            result = self._fetch_api(f"/api/video/{vid}")
            if result:
                data = result
                # \u6784\u5efa\u64ad\u653e\u5730\u5740
                video_url = data.get("video_url", "")
                title = data.get("title", "\u672a\u77e5\u6807\u9898")
                thumbnail = data.get("thumbnail", "")
                duration = data.get("duration", "")
                views = data.get("views", 0)
                categories = data.get("categories", "")
                description = data.get("description", "")

                play_from = "\u64ad\u653e"
                if video_url:
                    if video_url.endswith(".m3u8"):
                        play_url_str = f"播放${video_url}"
                    else:
                        play_url_str = f"播放${video_url}"
                else:
                    play_url_str = ""

                vod = {
                    "vod_id": str(vid),
                    "vod_name": title,
                    "vod_pic": thumbnail,
                    "vod_remarks": f"时长: {self._format_duration(duration)} | 播放: {views}",
                    "vod_content": description or categories,
                    "vod_play_from": play_from,
                    "vod_play_url": play_url_str,
                }
                return {"list": [vod]}
            return {"list": []}
        except Exception as e:
            self.log({"action": "detailContent_error", "error": str(e)})
            return {"list": []}

    def searchContent(self, key, quick=False, pg="1"):
        """\u641c\u7d22"""
        try:
            if not key:
                return {"list": [], "page": 1, "pagecount": 1, "total": 0}
            page = str(pg) if pg else "1"
            url = "/api/search"
            params = {"q": key}
            result = self._fetch_api(url, params)
            if result and "data" in result:
                items = result["data"]
                return {
                    "list": self._parse_videos(items),
                    "page": int(page),
                    "pagecount": 999,
                    "total": 9999
                }
            return {"list": [], "page": int(page), "pagecount": 1, "total": 0}
        except Exception as e:
            self.log({"action": "searchContent_error", "error": str(e)})
            return {"list": [], "page": int(pg or 1), "pagecount": 1, "total": 0}

    def playerContent(self, flag, id, vipFlags=None):
        """\u64ad\u653e"""
        if not id:
            return {"parse": 1, "url": ""}

        # \u5982\u679c\u662fm3u8\u6216mp4\u76f4\u94fe
        if id.startswith("http"):
            if ".m3u8" in id or ".mp4" in id:
                headers = {
                    "User-Agent": self.headers["User-Agent"],
                    "Referer": self.host + "/"
                }
                return {"parse": 0, "url": id, "header": headers}

        # \u5982\u679cid\u662f\u6570\u5b57\uff0c\u5c1d\u8bd5\u901a\u8fc7detail\u83b7\u53d6\u771f\u5b9e\u5730\u5740
        if id.isdigit():
            try:
                result = self._fetch_api(f"/api/video/{id}")
                if result and result.get("video_url"):
                    video_url = result["video_url"]
                    headers = {
                        "User-Agent": self.headers["User-Agent"],
                        "Referer": self.host + "/"
                    }
                    return {"parse": 0, "url": video_url, "header": headers}
            except Exception:
                pass

        # \u964d\u7ea7\u55c5\u63a2
        return {"parse": 1, "url": id, "header": {"User-Agent": self.headers["User-Agent"]}}

    def recommendContent(self, ids, pg=None):
        """\u76f8\u5173\u63a8\u8350"""
        try:
            if not ids:
                return {"list": []}
            # \u57fa\u4e8e\u5206\u7c7b\u63a8\u8350\u540c\u5206\u7c7b\u89c6\u9891
            vid = ids[0]
            result = self._fetch_api(f"/api/video/{vid}")
            if result:
                categories = result.get("categories", "")
                if categories:
                    url = "/api/videos/by-category"
                    params = {"cat": categories, "page": "1", "sort": "views"}
                    rec_result = self._fetch_api(url, params)
                    if rec_result and "data" in rec_result:
                        items = rec_result["data"][:10]
                        return {"list": self._parse_videos(items)}
            return {"list": []}
        except Exception as e:
            self.log({"action": "recommendContent_error", "error": str(e)})
            return {"list": []}

    def localProxy(self, params):
        """\u672c\u5730\u4ee3\u7406 - \u56fe\u7247/\u89c6\u9891\u900f\u4f20"""
        # \u6b64\u7ad9\u89c6\u9891\u4e3a\u76f4\u94fe\uff0c\u4e0d\u9700\u8981\u4ee3\u7406
        return [404, "text/plain", b"Not Found"]

    def destroy(self):
        """\u91ca\u653e\u8d44\u6e90"""
        pass

    # ==================== \u79c1\u6709\u65b9\u6cd5 ====================

    def _fetch_api(self, endpoint, params=None):
        """\u8c03\u7528API"""
        url = self.api_base.rstrip("/") + endpoint
        if params:
            url += "?" + urllib.parse.urlencode(params)
        try:
            resp = self.fetch(url, headers=self.headers, timeout=15)
            if resp and resp.status_code == 200:
                try:
                    return json.loads(resp.text)
                except:
                    return None
            return None
        except Exception as e:
            self.log({"action": "fetch_api_error", "url": url, "error": str(e)})
            return None

    def _parse_videos(self, items):
        """\u89e3\u6790\u89c6\u9891\u5217\u8868"""
        videos = []
        for item in items:
            vid = item.get("id") or item.get("rowid")
            title = item.get("title", "")
            thumbnail = item.get("thumbnail", "")
            duration = item.get("duration", "")
            views = item.get("views", 0)
            video_url = item.get("video_url", "")

            if not vid or not title:
                continue

            # \u6784\u5efavod_id - \u4f7f\u7528\u89c6\u9891ID
            vod_id = str(vid)

            # \u5907\u6ce8\uff1a\u65f6\u957f\u548c\u64ad\u653e\u91cf
            remarks = []
            if duration:
                remarks.append(self._format_duration(duration))
            if views:
                remarks.append(f"播放:{views}")
            vod_remarks = " | ".join(remarks) if remarks else ""

            videos.append({
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": thumbnail,
                "vod_remarks": vod_remarks,
            })
        return videos

    def _format_duration(self, seconds):
        """\u683c\u5f0f\u5316\u65f6\u957f"""
        try:
            secs = int(seconds)
            if secs < 60:
                return f"{secs}s"
            elif secs < 3600:
                mins = secs // 60
                rem = secs % 60
                return f"{mins}m{rem}s" if rem > 0 else f"{mins}m"
            else:
                hours = secs // 3600
                mins = (secs % 3600) // 60
                return f"{hours}h{mins}m"
        except:
            return str(seconds)

    def _parse_extend(self, extend):
        """\u89e3\u6790extend\u53c2\u6570\uff08\u591a\u683c\u5f0f\u517c\u5bb9\uff09"""
        if not extend:
            return {}
        if isinstance(extend, dict):
            return extend
        if isinstance(extend, str):
            try:
                return json.loads(extend)
            except:
                pass
            result = {}
            for part in extend.split(","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    result[k.strip()] = v.strip()
            return result
        return {}