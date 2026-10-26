# coding: utf-8
# AV\u8272\u754c - TVBox\u722c\u866b
# \u7ad9\u70b9: https://avsejie8.sbs

import re
import json
import urllib.parse
from urllib.parse import quote, urljoin

from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    def __init__(self):
        self.host = "https://avsejie8.sbs"
        self.path = ""
        self.site_name = "AV\u8272\u754c"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": self.host + "/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        self.classes = [
            {"type_id": "128", "type_name": "\u89c6\u9891\u4e00\u533a"},
            {"type_id": "129", "type_name": "\u7cbe\u54c1\u63a8\u8350"},
            {"type_id": "130", "type_name": "\u56fd\u4ea7\u8272\u60c5"},
            {"type_id": "132", "type_name": "91\u63a2\u82b1"},
            {"type_id": "133", "type_name": "\u7f51\u7ea2\u6d41\u51fa"},
            {"type_id": "134", "type_name": "\u91ce\u5916\u9732\u51fa"},
            {"type_id": "135", "type_name": "\u4f20\u5a92\u51fa\u54c1"},
            {"type_id": "136", "type_name": "\u56fd\u4ea7\u7cbe\u54c1"},
            {"type_id": "172", "type_name": "\u81ea\u62cd\u6cc4\u5bc6"},
            {"type_id": "146", "type_name": "\u89c6\u9891\u4e8c\u533a"},
            {"type_id": "147", "type_name": "\u5de8\u4e73\u7f8e\u4e73"},
            {"type_id": "148", "type_name": "\u4eba\u59bb\u719f\u5973"},
            {"type_id": "149", "type_name": "\u5f3a\u5978\u4e71\u4f26"},
            {"type_id": "150", "type_name": "\u4e9a\u6d32\u65e0\u7801"},
            {"type_id": "151", "type_name": "\u6b3a\u8fb1\u51cc\u8fb1"},
            {"type_id": "152", "type_name": "\u5236\u670d\u4e1d\u889c"},
            {"type_id": "153", "type_name": "\u5267\u60c5\u4ecb\u7ecd"},
            {"type_id": "154", "type_name": "\u591a\u4eba\u591aP"},
            {"type_id": "155", "type_name": "\u89c6\u9891\u4e09\u533a"},
            {"type_id": "156", "type_name": "\u7eff\u5e3d\u6362\u59bb"},
            {"type_id": "157", "type_name": "\u97e9\u56fd\u5fa1\u59d0"},
            {"type_id": "158", "type_name": "\u91ce\u5916\u642d\u8baa"},
            {"type_id": "160", "type_name": "\u7cbe\u54c1\u65e0\u7801"},
            {"type_id": "161", "type_name": "\u6210\u4eba\u52a8\u6f2b"},
            {"type_id": "162", "type_name": "\u5185\u5c04\u7279\u5199"},
            {"type_id": "163", "type_name": "\u81ea\u62cd\u6cc4\u5bc6"},
            {"type_id": "179", "type_name": "\u4e2d\u6587\u5b57\u5e55"},
        ]
        self.filters = {}

    def getName(self):
        return self.site_name

    def getDependence(self):
        return []

    def init(self, extend=""):
        self.extend = extend or ""

    def destroy(self):
        pass

    def _fix_url(self, url):
        if not url:
            return ""
        url = url.strip()
        if url.startswith("http"):
            return url
        if url.startswith("//"):
            return "https:" + url
        if url.startswith("/"):
            return self.host + url
        return self.host + "/" + url.lstrip("/")

    def _fetch_html(self, url):
        try:
            resp = self.fetch(url, headers=self.headers)
            if resp and hasattr(resp, "text"):
                return resp.text
            return None
        except Exception:
            return None

    def _parse_video_list(self, html):
        videos = []
        if not html:
            return videos

        pattern = r'<a[^>]*href="(/vodplay/\d+-\d+-\d+\.html)"[^>]*class="[^"]*group-item[^"]*"[^>]*>.*?<img[^>]*src="([^"]+)"[^>]*>.*?<p>([^<]+)</p>'
        matches = re.findall(pattern, html, re.DOTALL)

        for href, pic, title in matches:
            if not href or not title:
                continue
            vid_match = re.search(r'/vodplay/(\d+)-\d+-\d+\.html', href)
            if vid_match:
                vid = vid_match.group(1)
                videos.append({
                    "vod_id": vid,
                    "vod_name": title.strip(),
                    "vod_pic": self._fix_url(pic.strip()),
                    "vod_remarks": ""
                })

        return videos

    def _parse_page_count(self, html):
        if not html:
            return 1
        pattern = r'<a[^>]*class="[^"]*pageitem[^"]*"[^>]*href="[^"]*-(\d+)\.html"[^>]*>'
        matches = re.findall(pattern, html)
        if matches:
            return int(matches[-1]) if matches else 1
        pattern2 = '\u5171(\\d+)\u6761'
        match2 = re.search(pattern2, html)
        if match2:
            total = int(match2.group(1))
            return (total + 19) // 20
        return 1

    def _extract_m3u8_from_html(self, html):
        if not html:
            return None
        pattern = r'var\s+player_aaaa\s*=\s*(\{[^;]+\});'
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                url = data.get("url", "")
                if url and url.startswith("http"):
                    return url
            except:
                pass
        pattern2 = r'"url"\s*:\s*"([^"]+\.m3u8[^"]*)"'
        match2 = re.search(pattern2, html)
        if match2:
            url = match2.group(1)
            if url and url.startswith("http"):
                return url
        pattern3 = r'https?://[^"\']+\.m3u8[^"\']*'
        match3 = re.search(pattern3, html)
        if match3:
            return match3.group(0)
        return None

    def _extract_title_from_html(self, html):
        if not html:
            return ""
        pattern = r'<p[^>]*class="[^"]*group-title[^"]*"[^>]*>([^<]+)</p>'
        match = re.search(pattern, html)
        if match:
            return match.group(1).strip()
        pattern2 = r'<title>([^<]+)</title>'
        match2 = re.search(pattern2, html)
        if match2:
            title = match2.group(1).strip()
            if "\u8be6\u60c5\u4ecb\u7ecd" in title:
                title = title.split("\u8be6\u60c5\u4ecb\u7ecd")[0].strip()
            return title
        return ""

    def homeContent(self, filter=False):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter=False):
        return self.homeContent(filter)

    def homeVideoContent(self):
        return self.categoryContent("128", "1", False, {})

    def categoryContent(self, tid, pg, filter=False, extend=None):
        page = str(pg) if pg else "1"
        if page == "1":
            url = f"{self.host}/vodtype/{tid}.html"
        else:
            url = f"{self.host}/vodtype/{tid}-{page}.html"

        try:
            res = self.fetch(url, headers=self.headers)
            if not res:
                return {"list": [], "page": int(page), "pagecount": 1, "limit": 20, "total": 0}

            html = res.text
            videos = self._parse_video_list(html)
            pagecount = self._parse_page_count(html)

            return {
                "list": videos,
                "page": int(page),
                "pagecount": pagecount or 1,
                "limit": 20,
                "total": (pagecount or 1) * 20
            }
        except Exception as e:
            return {"list": [], "page": int(page), "pagecount": 1, "limit": 20, "total": 0}

    def detailContent(self, ids):
        if not ids:
            return {"list": []}

        vid = str(ids[0]) if isinstance(ids, list) else str(ids)
        detail_url = f"{self.host}/vodplay/{vid}-1-1.html"
        html = self._fetch_html(detail_url)

        if not html:
            return {"list": []}

        play_url = self._extract_m3u8_from_html(html)
        title = self._extract_title_from_html(html)

        vod = {
            "vod_id": vid,
            "vod_name": title or f"视频{vid}",
            "vod_pic": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": "",
            "vod_play_from": "\u64ad\u653e" if play_url else "",
            "vod_play_url": f"播放${play_url}" if play_url else "",
        }

        return {"list": [vod]}

    def searchContent(self, key, quick=False, pg="1"):
        if not key:
            return {"list": [], "page": 1, "pagecount": 1, "total": 0}

        pg = int(pg) if pg else 1
        encoded_key = quote(key)
        search_url = f"{self.host}/vodsearch/-------------.html?wd={encoded_key}"

        html = self._fetch_html(search_url)
        videos = self._parse_video_list(html) if html else []

        pagecount = 1
        if html:
            pattern = '\u5171(\\d+)\u6761'
            match = re.search(pattern, html)
            if match:
                total = int(match.group(1))
                pagecount = (total + 19) // 20 if total > 0 else 1

        return {"list": videos, "page": pg, "pagecount": pagecount, "total": pagecount * 20}

    def _m3u8_proxy_url(self, url):
        """\u751f\u6210m3u8\u4ee3\u7406\u5730\u5740"""
        if url:
            url = url.replace("\\/", "/")
        # \u786e\u4fdd\u4f7f\u7528\u6b63\u786e\u7684\u4ee3\u7406\u683c\u5f0f
        return self.getProxyUrl() + "?do=py&url=" + urllib.parse.quote(str(url or ""), safe="")
    def playerContent(self, flag, id, vipFlags=None):
        # \u5904\u7406\u8f6c\u4e49\u5b57\u7b26 - \u5173\u952e\u4fee\u590d
        if id and isinstance(id, str):
            id = id.replace("\\/", "/")
        
        # \u5982\u679cid\u662fm3u8\u94fe\u63a5\uff0c\u5305\u88c5\u6210\u4ee3\u7406URL
        if id and id.startswith("http") and ".m3u8" in id:
            return {
                "parse": 0,
                "url": self._m3u8_proxy_url(id),
                "header": {"User-Agent": self.headers.get("User-Agent", "")}
            }
        
        # \u5982\u679cid\u662f\u8be6\u60c5\u9875URL\uff0c\u5c1d\u8bd5\u63d0\u53d6m3u8
        if id and id.startswith("http") and "/vodplay/" in id:
            html = self._fetch_html(id)
            play_url = self._extract_m3u8_from_html(html)
            if play_url:
                return self.playerContent(flag, play_url, vipFlags)
            return {"parse": 1, "url": id, "header": self.headers}
        
        # \u5982\u679cid\u662fvod_id\uff0c\u5c1d\u8bd5\u83b7\u53d6m3u8
        if id and id.isdigit():
            detail_url = f"{self.host}/vodplay/{id}-1-1.html"
            html = self._fetch_html(detail_url)
            play_url = self._extract_m3u8_from_html(html)
            if play_url:
                return self.playerContent(flag, play_url, vipFlags)
            return {"parse": 1, "url": detail_url, "header": self.headers}
        
        return {"parse": 1, "url": id, "header": self.headers}
    def getProxyUrl(self):
        return "http://127.0.0.1:9978/proxy"

    def _rewrite_m3u8_tag(self, line, source_url):
        if line.startswith("#EXT-X-KEY") or line.startswith("#EXT-X-MAP"):
            def repl(match):
                return 'URI="' + urljoin(source_url, match.group(1)) + '"'
            return re.sub(r'URI="([^"]+)"', repl, line)
        if line and not line.startswith("#"):
            return urljoin(source_url, line)
        return line

    def _clean_m3u8(self, text, source_url):
        """\u6e05\u6d17m3u8 - \u8fc7\u6ee4\u5e7f\u544a\u5206\u7247\uff08\u53c2\u8003\u738b\u5ba4\u65e5\u62a5\u5b9e\u73b0\uff09"""
        import posixpath
        lines = [line.strip() for line in str(text or "").replace("\r", "").split("\n") if line.strip()]
        if not lines:
            return "#EXTM3U\n"

        # \u5904\u7406\u591a\u7801\u7387 Master Playlist
        if any(line.startswith("#EXT-X-STREAM-INF") for line in lines):
            out = []
            for line in lines:
                if line.startswith("#"):
                    out.append(line)
                else:
                    child = urllib.parse.urljoin(source_url, line)
                    out.append(self._m3u8_proxy_url(child) if ".m3u8" in child.lower() else child)
            return "\n".join(out) + "\n"

        parsed = urllib.parse.urlparse(source_url)
        source_dir = posixpath.dirname(parsed.path)
        if not source_dir.endswith("/"):
            source_dir += "/"

        # \u4ece #EXT-X-KEY \u63d0\u53d6\u6b63\u7247\u76ee\u5f55
        main_dir = source_dir
        for line in lines:
            if line.startswith("#EXT-X-KEY") and "URI=" in line:
                uri_match = re.search(r'URI="([^"]+)"', line)
                if uri_match:
                    key_path = uri_match.group(1)
                    if not key_path.startswith("http"):
                        key_dir = posixpath.dirname(key_path)
                        if key_dir and key_dir != "/":
                            main_dir = key_dir + "/"
                            break

        # \u5982\u679c\u901a\u8fc7KEY\u6ca1\u627e\u5230\uff0c\u5c1d\u8bd5\u4eceDISCONTINUITY\u540e\u7684\u7b2c\u4e00\u4e2a\u5206\u7247\u63a8\u65ad
        if main_dir == source_dir:
            discontinuity_found = False
            for line in lines:
                if line.startswith("#EXT-X-DISCONTINUITY"):
                    discontinuity_found = True
                    continue
                if discontinuity_found and not line.startswith("#"):
                    media_url = urllib.parse.urljoin(source_url, line)
                    media_parsed = urllib.parse.urlparse(media_url)
                    if media_parsed.path:
                        dir_path = posixpath.dirname(media_parsed.path)
                        if dir_path and dir_path != "/":
                            main_dir = dir_path + "/"
                            break

        segments = []
        pending = []

        for line in lines:
            if line.startswith("#EXTINF"):
                pending = [line]
                continue
            if pending and line.startswith("#"):
                pending.append(line)
                continue
            if pending:
                media_url = urllib.parse.urljoin(source_url, line)
                media_parsed = urllib.parse.urlparse(media_url)
                # \u8fc7\u6ee4\u903b\u8f91\uff1a\u5224\u65ad\u5206\u7247\u8def\u5f84\u662f\u5426\u4ee5\u6b63\u7247\u76ee\u5f55\u5f00\u5934
                is_ad = not media_parsed.path.startswith(main_dir)
                if not is_ad:
                    segments.extend(pending)
                    segments.append(media_url)
                pending = []
                continue

            if not line.startswith("#"):
                segments.append(urllib.parse.urljoin(source_url, line))
            else:
                segments.append(line)

        # \u4e8c\u6b21\u6e05\u6d17
        out = []
        for line in segments:
            line = self._rewrite_m3u8_tag(line, source_url)
            if line in ("#EXT-X-KEY:METHOD=NONE", "#EXT-X-DISCONTINUITY"):
                if not out or out[-1] in ("#EXT-X-DISCONTINUITY", "#EXT-X-KEY:METHOD=NONE"):
                    continue
            out.append(line)

        while len(out) > 1 and out[-1] in ("#EXT-X-DISCONTINUITY", "#EXT-X-KEY:METHOD=NONE"):
            out.pop()

        return "\n".join(out) + "\n"
    def localProxy(self, param):
        """
        m3u8\u672c\u5730\u4ee3\u7406 - \u5e7f\u544a\u5206\u7247\u8fc7\u6ee4
        """
        try:
            # \u517c\u5bb9 url \u548c source \u4e24\u79cd\u53c2\u6570\u540d
            if isinstance(param, dict):
                target = param.get("url", "") or param.get("source", "")
            else:
                target = str(param or "")

            # \u5265\u79bb\u524d\u7f00 url= \u5e76\u89e3\u7801
            if target.startswith("url="):
                target = target[4:]
            target = urllib.parse.unquote(str(target or ""))

            if not target or not re.match(r"^https?://", target, re.I):
                return [400, "text/plain", b"invalid url"]

            # \u53d1\u8d77HTTP\u8bf7\u6c42\u83b7\u53d6m3u8\u5185\u5bb9 - \u8bbe\u7f6e\u8d85\u65f615\u79d2
            resp = self.fetch(target, headers=self.headers, timeout=15)
            if not resp:
                return [502, "text/plain", b"fetch failed"]

            content = getattr(resp, "content", b"") or b""
            if not content and hasattr(resp, "text") and resp.text:
                content = resp.text.encode("utf-8", errors="ignore")

            if not content:
                return [502, "text/plain", b"empty content"]

            text = content.decode("utf-8", errors="ignore")
            if "#EXTM3U" not in text:
                return [200, "application/vnd.apple.mpegurl", content]

            cleaned = self._clean_m3u8(text, target)
            return [200, "application/vnd.apple.mpegurl", cleaned.encode("utf-8")]

        except Exception as e:
            # \u8d85\u65f6\u6216\u5f02\u5e38\u65f6\uff0c\u8fd4\u56de\u539f\u59cb\u5185\u5bb9\u8ba9\u58f3\u7aef\u76f4\u63a5\u64ad\u653e
            error_msg = f"localProxy error: {str(e)}".encode("utf-8", errors="ignore")
            return [500, "text/plain", error_msg]
    def recommendContent(self, ids, pg):
        try:
            if not ids:
                return {"list": []}

            vid = str(ids[0]) if isinstance(ids, list) else str(ids)

            detail_url = f"{self.host}/vodplay/{vid}-1-1.html"
            html = self._fetch_html(detail_url)

            if not html:
                return {"list": []}

            pattern = r'<a[^>]*href="(/vodplay/\d+-\d+-\d+\.html)"[^>]*class="[^"]*group-item[^"]*"[^>]*>.*?<img[^>]*src="([^"]+)"[^>]*>.*?<p>([^<]+)</p>'
            matches = re.findall(pattern, html, re.DOTALL)

            videos = []
            for href, pic, title in matches:
                vid_match = re.search(r'/vodplay/(\d+)-\d+-\d+\.html', href)
                if vid_match:
                    v = vid_match.group(1)
                    if v != vid:
                        videos.append({
                            "vod_id": v,
                            "vod_name": title.strip(),
                            "vod_pic": self._fix_url(pic.strip()),
                            "vod_remarks": ""
                        })

            if videos:
                return {"list": videos[:15]}

            return {"list": []}

        except Exception as e:
            return {"list": []}