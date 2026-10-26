# coding: utf-8
# \u5929\u7f8eav - 91xiancn.cfd
# MacCMS \u5f71\u89c6\u7ad9\uff0cplayer_aaaa encrypt:0 \u76f4\u94fe
# \u652f\u6301 m3u8 \u5e7f\u544a\u8fc7\u6ee4\uff08localProxy\uff09
# \u4f5c\u8005: AI Assistant
# \u65e5\u671f: 2026-07-27

import re
import json
import urllib.request
import urllib.error
import urllib.parse
from urllib.parse import urljoin, quote, unquote, urlparse

try:
    from base.spider import Spider as BaseSpider
except ImportError:
    class BaseSpider:
        def __init__(self):
            pass
        def fetch(self, url, headers=None, timeout=15):
            import requests
            resp = requests.get(url, headers=headers or {}, timeout=timeout)
            return resp
        def post(self, url, data=None, json=None, headers=None):
            import requests
            if json:
                resp = requests.post(url, json=json, headers=headers or {})
            else:
                resp = requests.post(url, data=data, headers=headers or {})
            return resp
        def log(self, msg):
            print(msg)
        def getProxyUrl(self):
            return "/proxy?do=local&url="


class Spider(BaseSpider):
    def __init__(self):
        self.host = "https://91xiancn.cfd"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": self.host + "/"
        }
        self.classes = [
            {"type_id": "1", "type_name": "\u56fd\u4ea7\u89c6\u9891"},
            {"type_id": "6", "type_name": "\u5236\u670d\u8bf1\u60d1"},
            {"type_id": "2", "type_name": "\u4e2d\u6587\u5b57\u5e55"},
            {"type_id": "7", "type_name": "\u7f51\u66dd\u9ed1\u6599"},
            {"type_id": "3", "type_name": "\u56fd\u4ea7\u4e3b\u64ad"},
            {"type_id": "8", "type_name": "\u65e5\u672c\u65e0\u7801"},
            {"type_id": "4", "type_name": "\u6fc0\u60c5\u52a8\u6f2b"},
            {"type_id": "5", "type_name": "\u4f26\u7406\u4e09\u7ea7"},
            {"type_id": "13", "type_name": "\u56fd\u4ea7\u4f20\u5a92"},
            {"type_id": "14", "type_name": "\u6296\u9634\u89c6\u9891"},
            {"type_id": "15", "type_name": "\u5f3a\u5978\u4e71\u4f26"},
            {"type_id": "9", "type_name": "\u6b27\u7f8e\u65e0\u7801"},
            {"type_id": "16", "type_name": "\u97e9\u56fd\u4e3b\u64ad"},
            {"type_id": "10", "type_name": "\u5c11\u5973\u841d\u8389"},
            {"type_id": "11", "type_name": "SM\u8c03\u6559"},
            {"type_id": "12", "type_name": "\u7f51\u7ea2\u5934\u6761"},
        ]
        self.filters = {}

    def getName(self):
        return "\u5929\u7f8eav"

    def getDependence(self):
        return []

    def init(self, extend=""):
        pass

    def homeContent(self, filter=False):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter=False):
        return self.homeContent(filter)

    def homeVideoContent(self):
        url = self.host + "/"
        try:
            html = self._fetch_html(url)
            items = self._parse_video_list(html)
            return {"list": items[:20]}
        except Exception as e:
            self.log(f"homeVideoContent error: {e}")
            return {"list": []}

    def categoryContent(self, tid, pg, filter=False, extend=None):
        page = int(pg) if pg and str(pg).isdigit() else 1
        if page == 1:
            url = f"{self.host}/index.php/vod/show/id/{tid}.html"
        else:
            url = f"{self.host}/index.php/vod/show/id/{tid}/page/{page}.html"
        
        try:
            html = self._fetch_html(url)
            items = self._parse_video_list(html)
            total_pages = self._parse_total_pages(html)
            return {
                "list": items,
                "page": page,
                "pagecount": total_pages or 50,
                "limit": 20,
                "total": total_pages * 20 if total_pages else 999
            }
        except Exception as e:
            self.log(f"categoryContent error: {e}")
            return {"list": [], "page": page, "pagecount": 1, "limit": 20, "total": 0}

    def detailContent(self, ids):
        raw = str(ids[0]) if ids else ""
        ps = raw.split('|$|')
        vod_id = ps[0]
        vod_name = ps[1] if len(ps) > 1 else "\u89c6\u9891"
        vod_pic = ps[2] if len(ps) > 2 else ""
        vod_remark = ps[3] if len(ps) > 3 else ""
        
        vod = {
            "vod_id": raw,
            "vod_name": vod_name,
            "vod_pic": vod_pic,
            "vod_remarks": vod_remark,
            "vod_content": vod_remark,
            "vod_play_from": "\u64ad\u653e",
            "vod_play_url": f"播放${vod_id}"
        }
        return {"list": [vod]}

    def searchContent(self, key, quick=False, pg="1"):
        url = f"{self.host}/index.php/vod/search.html"
        data = {"wd": key}
        try:
            html = self._post_html(url, data)
            items = self._parse_search_results(html)
            return {"list": items, "page": int(pg)}
        except Exception as e:
            self.log(f"searchContent error: {e}")
            return {"list": []}

    def playerContent(self, flag, id, vipFlags=None):
        if id.startswith("http"):
            play_url = id
        else:
            play_url = f"{self.host}/index.php/vod/play/id/{id}/sid/1/nid/1.html"
        
        try:
            html = self._fetch_html(play_url)
            match = re.search(r'player_aaaa\s*=\s*({[^;]+})', html, re.S)
            if not match:
                return {"parse": 1, "url": id, "header": self.headers}
            
            data = json.loads(match.group(1))
            encrypt = data.get("encrypt", 0)
            m3u8_url = data.get("url", "")
            
            if not m3u8_url:
                return {"parse": 1, "url": id, "header": self.headers}
            
            if encrypt == 0:
                if m3u8_url.endswith(".m3u8"):
                    return {"parse": 0, "url": self._m3u8_proxy_url(m3u8_url), "header": {}}
                return {"parse": 0, "url": m3u8_url, "header": self.headers}
            else:
                return {"parse": 1, "url": id, "header": self.headers}
                
        except Exception as e:
            self.log(f"playerContent error: {e}")
            return {"parse": 1, "url": id, "header": self.headers}

    def localProxy(self, param):
        target = unquote(str((param or {}).get("url", "") or ""))
        if not re.match(r"^https?://", target, re.I):
            return [400, "text/plain", b"invalid url"]
        try:
            text = self._fetch_raw(target)
            if not text:
                return [502, "text/plain", b"m3u8 fetch failed"]
            if "#EXTM3U" not in text:
                return [502, "text/plain", b"invalid m3u8"]
            cleaned = self._clean_m3u8(text, target)
            return [200, "application/vnd.apple.mpegurl", cleaned.encode("utf-8")]
        except Exception as e:
            self.log(f"m3u8广告过滤失败: {e}")
            return [500, "text/plain", b"m3u8 proxy error"]

    def _m3u8_proxy_url(self, url):
        return self.getProxyUrl() + "&url=" + quote(str(url or ""), safe="")

    def _clean_m3u8(self, text, source_url):
        lines = [line.strip() for line in str(text or "").replace("\r", "").split("\n") if line.strip()]
        if not lines:
            return "#EXTM3U\n"

        if any(line.startswith("#EXT-X-STREAM-INF") for line in lines):
            out = []
            for line in lines:
                if line.startswith("#"):
                    out.append(line)
                else:
                    child = urljoin(source_url, line)
                    out.append(self._m3u8_proxy_url(child) if ".m3u8" in child.lower() else child)
            return "\n".join(out) + "\n"

        source_path = urlparse(source_url).path
        source_parts = [p for p in source_path.split("/") if p]
        content_root = "/" + "/".join(source_parts[:2]) + "/" if len(source_parts) >= 2 else ""
        segments = []
        pending = []
        removed = 0
        
        for line in lines:
            if line.startswith("#EXTINF"):
                pending = [line]
                continue
            if pending and line.startswith("#"):
                pending.append(line)
                continue
            if pending:
                media = urljoin(source_url, line)
                if content_root and content_root not in urlparse(media).path:
                    removed += 1
                else:
                    segments.extend(pending)
                    segments.append(media)
                pending = []
                continue
            segments.append(self._rewrite_m3u8_tag(line, source_url))

        out = []
        for line in segments:
            line = self._rewrite_m3u8_tag(line, source_url)
            if line == "#EXT-X-KEY:METHOD=NONE" or line == "#EXT-X-DISCONTINUITY":
                if not out or out[-1] in ("#EXT-X-DISCONTINUITY", "#EXT-X-KEY:METHOD=NONE"):
                    continue
            out.append(line)
        while len(out) > 1 and out[-2] in ("#EXT-X-DISCONTINUITY", "#EXT-X-KEY:METHOD=NONE"):
            out.pop(-2)
        if removed:
            self.log(f"m3u8已过滤广告分片: {removed}")
        return "\n".join(out) + "\n"

    def _rewrite_m3u8_tag(self, line, source_url):
        if line.startswith("#EXT-X-KEY") or line.startswith("#EXT-X-MAP"):
            def repl(match):
                return 'URI="' + urljoin(source_url, match.group(1)) + '"'
            return re.sub(r'URI="([^"]+)"', repl, line)
        if line and not line.startswith("#"):
            return urljoin(source_url, line)
        return line

    # ============ \u8f85\u52a9\u65b9\u6cd5 ============

    def _fetch_html(self, url):
        """\u6293\u53d6HTML - \u4f7f\u7528\u57fa\u7c7bfetch"""
        resp = self.fetch(url, headers=self.headers, timeout=15)
        if hasattr(resp, 'text'):
            return resp.text
        if hasattr(resp, 'content'):
            return resp.content.decode('utf-8', errors='ignore')
        return str(resp)

    def _post_html(self, url, data):
        """POST\u8bf7\u6c42 - \u4f7f\u7528\u57fa\u7c7bpost"""
        resp = self.post(url, data=data, headers=self.headers)
        if hasattr(resp, 'text'):
            return resp.text
        if hasattr(resp, 'content'):
            return resp.content.decode('utf-8', errors='ignore')
        return str(resp)

    def _fetch_raw(self, url, headers=None):
        """\u83b7\u53d6\u539f\u59cb\u5185\u5bb9"""
        resp = self.fetch(url, headers=headers or self.headers, timeout=15)
        if hasattr(resp, 'content'):
            return resp.content.decode('utf-8', errors='ignore')
        if hasattr(resp, 'text'):
            return resp.text
        return str(resp)

    def _parse_video_list(self, html):
        items = []
        pattern = r'<li[^>]*class="[^"]*col-md-2[^"]*"[^>]*>.*?<a[^>]*class="[^"]*video-pic[^"]*"[^>]*data-original="([^"]*)"[^>]*href="([^"]*)"[^>]*title="([^"]*)"[^>]*>.*?</a>.*?<div[^>]*class="[^"]*subtitle[^"]*"[^>]*>([^<]*)</div>'
        matches = re.findall(pattern, html, re.S)
        
        for pic, href, title, remark in matches:
            vid = self._extract_vid_from_url(href)
            if vid:
                items.append({
                    "vod_id": f"{vid}|$|{title}|$|{pic}|$|{remark}",
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": remark
                })
        return items

    def _extract_vid_from_url(self, url):
        match = re.search(r'/detail/id/(\d+)\.html', url)
        if match:
            return match.group(1)
        match = re.search(r'/show/id/(\d+)\.html', url)
        if match:
            return match.group(1)
        match = re.search(r'/id/(\d+)\.html', url)
        if match:
            return match.group(1)
        return None

    def _parse_total_pages(self, html):
        match = re.search('\u5171(\\d+)\u9875', html)
        if match:
            return int(match.group(1))
        return None

    def _parse_search_results(self, html):
        items = []
        pattern = r'<a[^>]*class="[^"]*video-pic[^"]*"[^>]*data-original="([^"]*)"[^>]*href="([^"]*)"[^>]*title="([^"]*)"[^>]*>'
        matches = re.findall(pattern, html, re.S)
        for pic, href, title in matches:
            vid = self._extract_vid_from_url(href)
            if vid:
                items.append({
                    "vod_id": f"{vid}|$|{title}|$|{pic}",
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": ""
                })
        return items