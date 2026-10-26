# coding: utf-8
"""
\u7ad9\u70b9: \u9ec4\u8272\u5b9d\u5e93-Hsbk.CC (bk678.cc)
\u7c7b\u578b: \u6210\u4eba\u5f71\u89c6\u7ad9 (MacCMS)
\u7279\u70b9: \u6807\u51c6MacCMS\u67b6\u6784\uff0cm3u8\u76f4\u94fe\u64ad\u653e
\u57df\u540d: https://www.bk678.cc/
\u5907\u7528: www.hsbk.cc, www.bk567.cc
\u5206\u7c7b: \u65e5\u97e9AV(1), \u56fd\u4ea7\u7cfb\u5217(2), \u6b27\u7f8e(3), \u65e0\u7801\u4e2d\u6587\u5b57\u5e55(5), \u6709\u7801\u4e2d\u6587\u5b57\u5e55(6), \u65e5\u672c\u65e0\u7801(7), \u65e5\u672c\u6709\u7801(8), \u56fd\u4ea7\u89c6\u9891(9), \u6b27\u7f8e\u9ad8\u6e05(10), \u52a8\u6f2b\u5267\u60c5(11)
"""

import re
import json
from urllib.parse import urljoin, quote, unquote

from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    def __init__(self):
        self.host = "https://www.bk678.cc/"
        self.classes = [
            {"type_id": "1", "type_name": "\u65e5\u97e9AV"},
            {"type_id": "2", "type_name": "\u56fd\u4ea7\u7cfb\u5217"},
            {"type_id": "3", "type_name": "\u6b27\u7f8e"},
            {"type_id": "5", "type_name": "\u65e0\u7801\u4e2d\u6587\u5b57\u5e55"},
            {"type_id": "6", "type_name": "\u6709\u7801\u4e2d\u6587\u5b57\u5e55"},
            {"type_id": "7", "type_name": "\u65e5\u672c\u65e0\u7801"},
            {"type_id": "8", "type_name": "\u65e5\u672c\u6709\u7801"},
            {"type_id": "9", "type_name": "\u56fd\u4ea7\u89c6\u9891"},
            {"type_id": "10", "type_name": "\u6b27\u7f8e\u9ad8\u6e05"},
            {"type_id": "11", "type_name": "\u52a8\u6f2b\u5267\u60c5"},
        ]
        self.filters = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 22127RK46C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
            "Referer": self.host,
        }

    def getName(self):
        return "\u9ec4\u8272\u5b9d\u5e93"

    def getDependence(self):
        return []

    def init(self, extend=""):
        self.extend = extend or ""

    def homeContent(self, filter=False):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter=False):
        return self.homeContent(filter)

    def homeVideoContent(self):
        """\u9996\u9875\u63a8\u8350\u89c6\u9891"""
        try:
            html = self.fetch(self.host, headers=self.headers).text
            return {"list": self._parse_video_list(html)}
        except Exception as e:
            self.log("homeVideoContent error: " + str(e))
            return {"list": []}

    def categoryContent(self, tid, pg, filter=False, extend=""):
        """\u5206\u7c7b\u5217\u8868\u9875"""
        page = pg or "1"
        url = f"{self.host}vodtype/{tid}-{page}/"

        try:
            html = self.fetch(url, headers=self.headers).text
            videos = self._parse_video_list(html)
            pagecount = self._parse_page_count(html)
            return {
                "list": videos,
                "page": int(page),
                "pagecount": pagecount,
                "limit": 20,
                "total": pagecount * 20
            }
        except Exception as e:
            self.log("categoryContent error: " + str(e))
            return {"list": [], "page": int(page), "pagecount": 1, "limit": 20, "total": 0}

    def detailContent(self, ids):
        """\u8be6\u60c5\u9875 - \u4ece\u64ad\u653e\u9875\u63d0\u53d6m3u8"""
        url = ids[0]
        if not url.startswith("http"):
            url = urljoin(self.host, url)

        try:
            res = self.fetch(url, headers=self.headers)
            raw_content = getattr(res, "content", b"") or b""
            html = raw_content.decode("utf-8", errors="ignore")
            
            # \u63d0\u53d6 m3u8
            m3u8 = ""
            m3u8_match = re.search(r'var player_aaaa\s*=\s*\{[\s\S]*?"url"\s*:\s*"([^"]+)"', html)
            if m3u8_match:
                m3u8 = m3u8_match.group(1).replace("\\/", "/")
            
            # \u63d0\u53d6\u6807\u9898
            title_match = re.search(r'<h3 class="title">([^<]+)</h3>', html)
            title = title_match.group(1).strip() if title_match else ""
            
            vod = {
                "vod_id": url,
                "vod_name": title or "\u89c6\u9891",
                "vod_pic": "",
                "vod_remarks": "",
                "vod_actor": "",
                "vod_director": "",
                "vod_content": "",
                "vod_play_from": "\u76f4\u94fe",
                "vod_play_url": f"播放${m3u8}" if m3u8 else "",
            }
            return {"list": [vod]}
        except Exception as e:
            self.log("detailContent error: " + str(e))
            return {"list": []}
    def searchContent(self, key, quick=False, pg="1"):
        """\u641c\u7d22"""
        page = pg or "1"
        # MacCMS \u641c\u7d22URL\u683c\u5f0f
        url = f"{self.host}vodsearch/-------------.html?wd={quote(key)}&page={page}"

        try:
            html = self.fetch(url, headers=self.headers).text
            videos = self._parse_search_list(html)
            pagecount = self._parse_page_count(html)
            return {
                "list": videos,
                "page": int(page),
                "pagecount": pagecount
            }
        except Exception as e:
            self.log("searchContent error: " + str(e))
            return {"list": [], "page": int(page)}

    def playerContent(self, flag, id, vipFlags=""):
        """\u64ad\u653e\u5730\u5740\u89e3\u6790"""
        # id \u53ef\u80fd\u662fm3u8\u76f4\u94fe\u6216\u64ad\u653e\u9875URL
        if id.startswith("http") and (".m3u8" in id or ".mp4" in id):
            if ".m3u8" in id:
                return {"parse": 0, "url": self._m3u8_proxy_url(id), "header": self.headers}
            return {"parse": 0, "url": id, "header": self.headers}

        # \u5982\u679c\u662f\u64ad\u653e\u9875URL\uff0c\u63d0\u53d6m3u8
        if id.startswith("http"):
            try:
                html = self.fetch(id, headers=self.headers).text
                m3u8_url = self._extract_m3u8(html)
                if m3u8_url:
                    return {"parse": 0, "url": self._m3u8_proxy_url(m3u8_url), "header": self.headers}
            except:
                pass

        return {"parse": 1, "url": id, "header": self.headers}

    def _parse_video_list(self, html):
        """\u89e3\u6790\u89c6\u9891\u5217\u8868 - \u4f18\u5316\u7248"""
        videos = []
        # \u5206\u5272\u89c6\u9891\u9879\uff0c\u4f7f\u7528\u66f4\u7b80\u5355\u7684\u5339\u914d
        items = re.findall(r'<div class="stui-vodlist__box">(.*?)</div>\s*</div>', html, re.DOTALL)
        for item in items:
            # \u63d0\u53d6\u94fe\u63a5
            href_match = re.search(r'<a[^>]*href="([^"]+)"', item)
            if not href_match:
                continue
            href = href_match.group(1)
            
            # \u63d0\u53d6\u5c01\u9762
            img_match = re.search(r'data-original="([^"]+)"', item)
            img = img_match.group(1) if img_match else ""
            
            # \u63d0\u53d6\u65f6\u957f
            duration_match = re.search(r'<span class="pic-text[^"]*">([^<]*)</span>', item)
            duration = duration_match.group(1).strip() if duration_match else ""
            
            # \u63d0\u53d6\u6807\u9898
            title_match = re.search(r'<h4 class="title">.*?<a[^>]*>([^<]+)</a>', item, re.DOTALL)
            title = title_match.group(1).strip() if title_match else ""
            
            if href and title:
                video_id = href if href.startswith("/") else "/" + href
                videos.append({
                    "vod_id": video_id,
                    "vod_name": title,
                    "vod_pic": img,
                    "vod_remarks": duration,
                })
                if len(videos) >= 20:  # \u9650\u5236\u8fd4\u56de\u6570\u91cf\uff0c\u63d0\u9ad8\u901f\u5ea6
                    break
        return videos
    def _parse_search_list(self, html):
        """\u89e3\u6790\u641c\u7d22\u5217\u8868"""
        videos = []
        # \u641c\u7d22\u9875\u9762\u7684\u89c6\u9891\u9879\u7ed3\u6784
        items = re.findall(r'<div class="stui-vodlist__box">(.*?)</div>\s*</div>', html, re.DOTALL)
        for item in items:
            # \u63d0\u53d6\u94fe\u63a5
            href_match = re.search(r'<a[^>]*href="([^"]+)"', item)
            if not href_match:
                continue
            href = href_match.group(1)
            
            # \u63d0\u53d6\u5c01\u9762
            img_match = re.search(r'data-original="([^"]+)"', item)
            img = img_match.group(1) if img_match else ""
            
            # \u63d0\u53d6\u6807\u9898
            title_match = re.search(r'<h4 class="title">.*?<a[^>]*>([^<]+)</a>', item, re.DOTALL)
            title = title_match.group(1).strip() if title_match else ""
            
            # \u63d0\u53d6\u65f6\u957f
            duration_match = re.search(r'<span class="pic-text[^"]*">([^<]*)</span>', item)
            duration = duration_match.group(1).strip() if duration_match else ""
            
            if href and title and title != "\u9996\u9875":
                video_id = href if href.startswith("/") else "/" + href
                videos.append({
                    "vod_id": video_id,
                    "vod_name": title,
                    "vod_pic": img,
                    "vod_remarks": duration,
                })
        
        # \u5982\u679c\u4e0a\u9762\u6ca1\u5339\u914d\u5230\uff0c\u5c1d\u8bd5\u76f4\u63a5\u5339\u914d\u641c\u7d22\u7ed3\u679c\u4e2d\u7684\u94fe\u63a5
        if not videos:
            pattern = r'<a class="stui-vodlist__thumb[^"]*" href="([^"]+)"[^>]*data-original="([^"]+)"[^>]*>.*?<h4 class="title">.*?<a[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.DOTALL)
            for href, img, title in matches:
                if title and title != "\u9996\u9875":
                    video_id = href if href.startswith("/") else "/" + href
                    videos.append({
                        "vod_id": video_id,
                        "vod_name": title.strip(),
                        "vod_pic": img,
                        "vod_remarks": "",
                    })
        return videos
    def _parse_page_count(self, html):
        """\u89e3\u6790\u603b\u9875\u6570"""
        # \u5339\u914d\u5206\u9875\u94fe\u63a5\uff0c\u5982 /vodtype/1-2/ \u6216 \u5c3e\u9875\u94fe\u63a5
        page_nums = re.findall(r'/vodtype/\d+-(\d+)/', html)
        if page_nums:
            return max(int(p) for p in page_nums)
        # \u68c0\u67e5\u662f\u5426\u6709 "\u5c3e\u9875" \u94fe\u63a5
        tail_match = re.search('/vodtype/\\d+-(\\d+)/"[^>]*>\u5c3e\u9875', html)
        if tail_match:
            return int(tail_match.group(1))
        # \u68c0\u67e5\u662f\u5426\u6709 "\u4e0b\u4e00\u9875" \u94fe\u63a5
        if 'class="next page-link"' in html or '\u4e0b\u4e00\u9875' in html:
            return 50
        return 1

    def _parse_detail(self, html, base_url):
        """\u89e3\u6790\u8be6\u60c5\u9875 - \u63d0\u53d6m3u8"""
        # \u6807\u9898 - \u4ece\u591a\u79cd\u53ef\u80fd\u4f4d\u7f6e\u63d0\u53d6
        title = ""
        title_match = re.search(r'<h3 class="title">([^<]+)</h3>', html)
        if title_match:
            title = title_match.group(1).strip()
        else:
            title_match = re.search(r'<title>([^<]+)</title>', html)
            if title_match:
                title = title_match.group(1).strip()
                title = re.sub(r'\s*[-|]\s*.*$', '', title)

        # \u4ece player_aaaa \u63d0\u53d6\u64ad\u653e\u5730\u5740
        m3u8_url = self._extract_m3u8(html)
        
        # \u8c03\u8bd5\u65e5\u5fd7
        self.log("m3u8_url: " + str(m3u8_url))
        self.log("title: " + str(title))

        # \u6784\u5efavod
        vod = {
            "vod_id": base_url,
            "vod_name": title or "\u89c6\u9891",
            "vod_pic": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": "",
            "vod_play_from": "\u76f4\u94fe",
            "vod_play_url": f"播放${m3u8_url}" if m3u8_url else "",
        }
        return vod
    def _extract_m3u8(self, html):
        """\u4eceHTML\u4e2d\u63d0\u53d6m3u8\u5730\u5740"""
        # \u65b9\u6cd51: player_aaaa \u53d8\u91cf (\u6700\u53ef\u9760)
        # \u4f7f\u7528\u66f4\u5bbd\u677e\u7684\u5339\u914d\uff0c\u63d0\u53d6url\u5b57\u6bb5
        pattern1 = r'var player_aaaa\s*=\s*\{[^}]*"url"\s*:\s*"([^"]+)"'
        match = re.search(pattern1, html)
        if match:
            url = match.group(1).replace("\\/", "/")
            if ".m3u8" in url:
                return url

        # \u65b9\u6cd52: \u5728script\u4e2d\u67e5\u627e\u5305\u542bm3u8\u7684\u53d8\u91cf
        pattern2 = r'url\s*:\s*["\']([^"\']+\.m3u8)["\']'
        matches = re.findall(pattern2, html)
        if matches:
            return matches[0].replace("\\/", "/")

        # \u65b9\u6cd53: videojs sources
        pattern3 = r'sources:\s*\[\s*\{\s*src:\s*["\']([^"\']+\.m3u8)["\']'
        match = re.search(pattern3, html)
        if match:
            return match.group(1).replace("\\/", "/")

        # \u65b9\u6cd54: \u76f4\u63a5\u5728html\u4e2d\u67e5\u627em3u8
        pattern4 = r'https?://[^\s"\']+\.m3u8'
        matches = re.findall(pattern4, html)
        if matches:
            for m in matches:
                if "index.m3u8" in m or "playlist" in m:
                    return m
            return matches[0]

        return None
    def _m3u8_proxy_url(self, url):
        """m3u8\u4ee3\u7406\u5730\u5740"""
        proxy_base = self.getProxyUrl()
        if "?do=py" in proxy_base:
            return proxy_base + "&url=" + quote(str(url or ""), safe="")
        return proxy_base + "?do=py&url=" + quote(str(url or ""), safe="")

    def localProxy(self, param):
        """m3u8\u672c\u5730\u4ee3\u7406 - \u7b80\u5316\u7248"""
        try:
            if isinstance(param, dict):
                target = param.get("url", "") or param.get("source", "")
            else:
                target = str(param or "")

            if target.startswith("url="):
                target = target[4:]
            target = unquote(str(target or ""))

            if not target or not re.match(r"^https?://", target, re.I):
                return [400, "text/plain", b"invalid url"]

            # \u76f4\u63a5\u8bf7\u6c42m3u8
            res = self.fetch(target, headers=self.headers, timeout=15)
            if not res or getattr(res, "status_code", 0) != 200:
                return [502, "text/plain", b"m3u8 fetch failed"]

            raw = getattr(res, "content", b"") or b""
            text = raw.decode("utf-8", errors="ignore")

            if "#EXTM3U" not in text:
                return [502, "text/plain", b"invalid m3u8"]

            # \u53ea\u505a\u8def\u5f84\u8865\u5168\uff0c\u4e0d\u505a\u5e7f\u544a\u8fc7\u6ee4
            cleaned = self._rewrite_m3u8(text, target)
            return [200, "application/vnd.apple.mpegurl", cleaned.encode("utf-8")]
        except Exception as e:
            self.log("localProxy error: " + str(e))
            return [500, "text/plain", str(e).encode("utf-8", errors="ignore")]

    def _rewrite_m3u8(self, text, source_url):
        """\u91cd\u5199m3u8\uff1a\u8865\u5168\u76f8\u5bf9\u8def\u5f84"""
        lines = [line.strip() for line in str(text or "").replace("\r", "").split("\n") if line.strip()]
        if not lines:
            return "#EXTM3U\n"

        out = []
        for line in lines:
            if line.startswith("#"):
                if line.startswith("#EXT-X-KEY") or line.startswith("#EXT-X-MAP"):
                    def repl(match):
                        return 'URI="' + urljoin(source_url, match.group(1)) + '"'
                    line = re.sub(r'URI="([^"]+)"', repl, line)
                out.append(line)
            else:
                if not line.startswith(("http://", "https://")):
                    line = urljoin(source_url, line)
                out.append(line)
        return "\n".join(out) + "\n"
    def _clean_m3u8(self, text, source_url):
        """\u6e05\u6d17m3u8\uff1a\u8fc7\u6ee4\u5e7f\u544a\u5206\u7247\uff0c\u4fdd\u7559\u6b63\u7247"""
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
                    child = urljoin(source_url, line)
                    out.append(self._m3u8_proxy_url(child) if ".m3u8" in child.lower() else child)
            return "\n".join(out) + "\n"

        parsed = urlparse(source_url)
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
                media_url = urljoin(source_url, line)
                media_parsed = urlparse(media_url)

                is_ad = not media_parsed.path.startswith(main_dir)

                if not is_ad:
                    segments.extend(pending)
                    segments.append(media_url)
                else:
                    removed += 1
                pending = []
                continue

            if not line.startswith("#"):
                segments.append(urljoin(source_url, line))
            else:
                segments.append(line)

        out = []
        for line in segments:
            line = self._rewrite_m3u8_tag(line, source_url)
            if line in ("#EXT-X-KEY:METHOD=NONE", "#EXT-X-DISCONTINUITY"):
                if not out or out[-1] in ("#EXT-X-DISCONTINUITY", "#EXT-X-KEY:METHOD=NONE"):
                    continue
            out.append(line)

        while len(out) > 1 and out[-1] in ("#EXT-X-DISCONTINUITY", "#EXT-X-KEY:METHOD=NONE"):
            out.pop()

        if removed:
            self.log("m3u8\u5df2\u8fc7\u6ee4\u5e7f\u544a\u5206\u7247: %d" % removed)
        return "\n".join(out) + "\n"

    def _rewrite_m3u8_tag(self, line, source_url):
        """\u91cd\u5199m3u8\u6807\u7b7e\u4e2d\u7684URI\uff08\u8865\u5168\u7edd\u5bf9\u5730\u5740\uff09"""
        if line.startswith("#EXT-X-KEY") or line.startswith("#EXT-X-MAP"):
            def repl(match):
                uri = match.group(1)
                if uri.startswith(("http://", "https://")):
                    return 'URI="' + uri + '"'
                return 'URI="' + urljoin(source_url, uri) + '"'
            return re.sub(r'URI="([^"]+)"', repl, line)

        if line and not line.startswith("#"):
            if line.startswith(("http://", "https://")):
                return line
            return urljoin(source_url, line)

        return line

    def siteInfo(self):
        """\u7ad9\u70b9\u4fe1\u606f"""
        return {
            "name": "\u9ec4\u8272\u5b9d\u5e93",
            "domain": "bk678.cc",
            "type": "\u6210\u4eba\u5f71\u89c6\u7ad9",
            "description": "MacCMS\u6807\u51c6\u67b6\u6784\uff0cm3u8\u76f4\u94fe\u64ad\u653e"
        }