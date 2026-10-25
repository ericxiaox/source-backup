# -*- coding: utf-8 -*-
# \u722c\u866b\u6e90: \u6026\u7136\u5fc3\u52a8 (prshinezenx.blog)
# \u7ad9\u70b9\u7c7b\u578b: SPA + \u670d\u52a1\u7aef\u6e32\u67d3\uff0c\u6570\u636e\u901a\u8fc7 Base64 \u7f16\u7801\u5d4c\u5165 HTML
# \u5f00\u53d1\u8005: AI Assistant
# \u65e5\u671f: 2026-07-22

import re
import json
import base64
from urllib.parse import urljoin, quote

from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    def __init__(self):
        self.host = "https://prshinezenx.blog"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": self.host + "/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        # \u5206\u7c7b\u5217\u8868\uff08\u4ece\u9996\u9875\u63d0\u53d6\uff0c\u672c\u5730\u786c\u7f16\u7801\u4fdd\u8bc1\u9996\u9875\u79d2\u51fa\uff09
        self.classes = [
            {"type_id": "43", "type_name": "\u56fd\u4ea7\u7cbe\u9009"},
            {"type_id": "31", "type_name": "\u675f\u7f1a\u73a9\u6cd5"},
            {"type_id": "35", "type_name": "\u4e2d\u5b57\u4e13\u533a"},
            {"type_id": "33", "type_name": "\u5973\u4f18\u7cbe\u9009"},
            {"type_id": "53", "type_name": "\u4f20\u5a92\u62cd\u6444"},
            {"type_id": "29", "type_name": "\u53d8\u6027\u7eaa\u5b9e"},
            {"type_id": "21", "type_name": "\u540c\u5fd7\u65e5\u5e38"},
            {"type_id": "23", "type_name": "\u767e\u5408\u60c5\u5883"},
            {"type_id": "39", "type_name": "\u6b27\u7f8e\u7cbe\u9009"},
            {"type_id": "45", "type_name": "\u865a\u62df\u6362\u8138"},
            {"type_id": "47", "type_name": "\u5c11\u5973\u5e7b\u60f3"},
            {"type_id": "49", "type_name": "\u4e3b\u64ad\u65e5\u8bb0"},
            {"type_id": "51", "type_name": "\u7ea6\u4f1a\u5b9e\u5f55"},
            {"type_id": "55", "type_name": "\u4f26\u7406\u5267\u573a"},
            {"type_id": "57", "type_name": "\u9ed1\u6599\u6863\u6848"},
            {"type_id": "63", "type_name": "\u81ea\u62cd\u5b9e\u5f55"},
        ]
        # \u65e0\u7b5b\u9009\u529f\u80fd
        self.filters = {}

    def getName(self):
        return "\u6026\u7136\u5fc3\u52a8"

    def getDependence(self):
        return []

    def init(self, extend=""):
        """\u521d\u59cb\u5316\uff0c\u96f6\u7f51\u7edc"""
        pass

    def _fetch(self, url):
        """\u8bf7\u6c42\u9875\u9762\uff0c\u8fd4\u56de HTML \u6587\u672c"""
        try:
            rsp = self.fetch(url, headers=self.headers, timeout=15000)
            if rsp and hasattr(rsp, 'text'):
                return rsp.text
            return None
        except Exception:
            return None

    def _extract_vod_data(self, html):
        """\u4ece HTML \u4e2d\u63d0\u53d6 window.__vod_data__ \u7684 Base64 \u6570\u636e\u5e76\u89e3\u7801"""
        if not html:
            return None
        pattern = r"const binaryStr = atob\('([^']+)'\)"
        match = re.search(pattern, html)
        if not match:
            return None
        base64_str = match.group(1)
        try:
            json_str = base64.b64decode(base64_str).decode('utf-8')
            return json.loads(json_str)
        except Exception:
            return None

    def _parse_list(self, items):
        """\u89e3\u6790\u89c6\u9891\u5217\u8868\u9879\uff0c\u6253\u5305\u6570\u636e\u5230 vod_id \u4ee5\u4fbf\u8be6\u60c5\u9875\u5feb\u901f\u5c55\u793a"""
        if not items:
            return []
        result = []
        for item in items:
            vod_id = str(item.get("vod_id", ""))
            if not vod_id:
                continue
            vod_name = item.get("vod_name", "\u672a\u77e5\u6807\u9898")
            vod_pic = item.get("vod_pic", "")
            if vod_pic and not vod_pic.startswith("http"):
                vod_pic = urljoin(self.host, vod_pic)
            vod_remark = item.get("vod_duration", "")
            type_id = str(item.get("type_id", ""))
            # \u6253\u5305\u6570\u636e\u5230 vod_id\uff0c\u65b9\u4fbf\u8be6\u60c5\u9875\u5feb\u901f\u8fd4\u56de
            packed_id = f"{vod_id}|$|{vod_name}|$|{vod_pic}|$|{vod_remark}|$|{type_id}"
            result.append({
                "vod_id": packed_id,
                "vod_name": vod_name,
                "vod_pic": vod_pic,
                "vod_remarks": vod_remark,
            })
        return result

    def homeContent(self, filter=False):
        """\u9996\u9875\uff1a\u8fd4\u56de\u5206\u7c7b\u5217\u8868\uff0c\u96f6\u7f51\u7edc"""
        return {
            "class": self.classes,
            "filters": self.filters if filter else {}
        }

    def getHomeContent(self, filter=False):
        return self.homeContent(filter)

    def homeVideoContent(self):
        """\u9996\u9875\u63a8\u8350\u89c6\u9891"""
        html = self._fetch(self.host + "/")
        if not html:
            return {"list": []}
        data = self._extract_vod_data(html)
        if not data:
            return {"list": []}
        items = data.get("other_request_data", {}).get("random_list", [])
        if not items:
            items = data.get("request_data", {}).get("list", [])
        return {"list": self._parse_list(items[:20])}

    def categoryContent(self, tid, pg=1, filter=False, extend=None):
        """\u5206\u7c7b\u5217\u8868\u9875"""
        page = pg or 1
        url = f"{self.host}/vodlist/type/{tid}/keyword/all/orderby/default/page/{page}.html"
        html = self._fetch(url)
        if not html:
            return {"list": [], "page": page, "pagecount": 1, "limit": 20, "total": 0}

        data = self._extract_vod_data(html)
        if not data:
            return {"list": [], "page": page, "pagecount": 1, "limit": 20, "total": 0}

        items = data.get("request_data", {}).get("list", [])
        total = data.get("request_data", {}).get("total", 0)
        limit = data.get("limit", 20)
        total_pages = (total + limit - 1) // limit if total > 0 else 1

        return {
            "list": self._parse_list(items),
            "page": page,
            "pagecount": total_pages,
            "limit": limit,
            "total": total
        }

    def detailContent(self, ids):
        """\u89c6\u9891\u8be6\u60c5 - \u4ece\u6253\u5305\u7684 vod_id \u4e2d\u89e3\u6790\u6570\u636e\uff0c\u5feb\u901f\u8fd4\u56de"""
        if not ids:
            return {"list": []}
        raw = str(ids[0])

        # \u89e3\u6790\u6253\u5305\u7684\u6570\u636e: vod_id|$|vod_name|$|vod_pic|$|vod_remark|$|type_id
        parts = raw.split("|$|")
        if len(parts) >= 5:
            vod_id = parts[0]
            vod_name = parts[1] if len(parts) > 1 else "\u672a\u77e5\u6807\u9898"
            vod_pic = parts[2] if len(parts) > 2 else ""
            vod_remark = parts[3] if len(parts) > 3 else ""
            type_id = parts[4] if len(parts) > 4 else ""
        else:
            # \u517c\u5bb9\u65e7\u683c\u5f0f\uff1a\u76f4\u63a5\u4f20\u6570\u5b57ID
            vod_id = raw
            vod_name = ""
            vod_pic = ""
            vod_remark = ""
            type_id = ""

        # \u83b7\u53d6\u64ad\u653e\u5730\u5740\uff1a\u8bf7\u6c42\u8be6\u60c5\u9875\u63d0\u53d6 vod_play_url
        if type_id:
            detail_url = f"{self.host}/voddetail/type/{type_id}/id/{vod_id}.html"
        else:
            detail_url = f"{self.host}/voddetail/type/all/id/{vod_id}.html"

        html = self._fetch(detail_url)
        play_page = ""
        if html:
            data = self._extract_vod_data(html)
            if data:
                vod_info = data.get("vod_info", {})
                play_page = vod_info.get("vod_play_url", "")
                if not vod_name:
                    vod_name = vod_info.get("vod_name", "\u672a\u77e5\u6807\u9898")
                if not vod_pic:
                    vod_pic = vod_info.get("vod_pic", "")
                if not vod_remark:
                    vod_remark = vod_info.get("vod_duration", "")

        if not play_page:
            return {
                "list": [{
                    "vod_id": vod_id,
                    "vod_name": vod_name or "\u672a\u77e5\u6807\u9898",
                    "vod_pic": vod_pic,
                    "vod_remarks": vod_remark,
                    "vod_content": "",
                    "vod_play_from": "\u64ad\u653e",
                    "vod_play_url": ""
                }]
            }

        # \u5982\u679c\u662f ao jie xi \u5305\u88c5\uff0c\u63d0\u53d6\u771f\u5b9e m3u8
        if "aojiexi.com" in play_page:
            match = re.search(r'url=([^&]+)', play_page)
            if match:
                real_url = match.group(1)
                real_url = re.sub(r'%([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), real_url)
                play_page = real_url

        # \u6784\u9020\u64ad\u653e\u6570\u636e\uff1a\u5355\u7ebf\u8def\u5355\u96c6
        # \u683c\u5f0f\u53c2\u8003 tmcrownxlift \u6210\u529f\u6848\u4f8b
        return {
            "list": [{
                "vod_id": vod_id,
                "vod_name": vod_name or "\u672a\u77e5\u6807\u9898",
                "vod_pic": vod_pic,
                "vod_remarks": vod_remark,
                "vod_content": "",
                "vod_play_from": "\u64ad\u653e",
                "vod_play_url": "\u64ad\u653e$" + play_page
            }]
        }

    def searchContent(self, key, quick=False, pg="1"):
        """\u641c\u7d22"""
        if not key:
            return {"list": []}
        page = pg or 1
        url = f"{self.host}/vodlist/type/all/keyword/{quote(key)}/orderby/default/page/{page}.html"
        html = self._fetch(url)
        if not html:
            return {"list": []}
        data = self._extract_vod_data(html)
        if not data:
            return {"list": []}
        items = data.get("request_data", {}).get("list", [])
        return {"list": self._parse_list(items)}

    def playerContent(self, flag, vid, vipFlags=None):
        """\u64ad\u653e\u5730\u5740\u89e3\u6790"""
        if not vid:
            return {"parse": 0, "url": ""}

        if vid.endswith((".m3u8", ".mp4")):
            return {"parse": 0, "url": vid, "header": self.headers}

        if "aojiexi.com" in vid:
            match = re.search(r'url=([^&]+)', vid)
            if match:
                real_url = match.group(1)
                real_url = re.sub(r'%([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), real_url)
                return {"parse": 0, "url": real_url, "header": self.headers}

        if vid.startswith("http"):
            html = self._fetch(vid)
            if html:
                match = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', html)
                if match:
                    return {"parse": 0, "url": match.group(0), "header": self.headers}

        return {"parse": 1, "url": vid}

    def isVideoFormat(self, url):
        if not url:
            return False
        return url.endswith((".m3u8", ".mp4", ".m3u8?"))

    def destroy(self):
        pass