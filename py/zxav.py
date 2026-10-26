# coding: utf-8
# \u7ad9\u70b9: \u6700\u65b0AV (https://www.changwen.shop/)
# \u7c7b\u578b: MacCMS \u67b6\u6784\u5f71\u89c6\u7ad9 (\u6210\u4eba\u5185\u5bb9)
# \u6700\u540e\u9a8c\u8bc1: 2026-09-07

import json
import re
from urllib.parse import urljoin, quote, unquote, urlparse

from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
    def __init__(self):
        self.extend = ""
        self.host = "https://www.changwen.shop"
        self.classes = [
            {"type_id": "1", "type_name": "\u56fd\u4ea7"},
            {"type_id": "2", "type_name": "\u6b27\u7f8e\u65e5\u672c"},
            {"type_id": "3", "type_name": "\u4e3b\u64ad"},
            {"type_id": "4", "type_name": "\u52a8\u6f2b"},
        ]
        self.filters = {
            "1": [],
            "2": [],
            "3": [],
            "4": [],
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 22127RK46C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
            "Referer": self.host + "/",
        }
        self.timeout = 15
        self._ad_filter = None

    def getName(self):
        return "\u6700\u65b0AV"

    def getDependence(self):
        return []

    def init(self, extend=""):
        self.extend = extend or ""

    def _fetch(self, url, **kwargs):
        """\u5e26\u5224\u7a7a\u7684\u8bf7\u6c42\uff0c\u652f\u6301 SSL \u5bb9\u9519"""
        # \u5982\u679c kwargs \u4e2d\u6ca1\u6709 timeout\uff0c\u4f7f\u7528\u9ed8\u8ba4\u503c
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        try:
            r = self.fetch(url, headers=self.headers, verify=False, **kwargs)
            if r is None:
                self.log({"fetch": "returned None", "url": url})
                return None
            if r.status_code != 200:
                self.log({"fetch": "non-200", "url": url, "status": r.status_code})
                return None
            return r
        except Exception as e:
            self.log({"fetch": "exception", "url": url, "error": str(e)})
            return None

    def homeContent(self, filter):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def homeVideoContent(self):
        """\u9996\u9875\u63a8\u8350 - \u76f4\u63a5\u53d6\u5206\u7c7b\u9875\u7b2c1\u9875"""
        url = f"{self.host}/index.php/vod/type/page/1.html"
        r = self._fetch(url)
        if not r:
            return {"list": []}
        items = self._parse_list(r.text, url)
        return {"list": items[:20]}

    def _parse_list(self, html, page_url):
        """\u89e3\u6790\u89c6\u9891\u5217\u8868\uff08\u5206\u7c7b\u9875/\u641c\u7d22\u9875\u5171\u7528\uff09"""
        items = []
        # \u63d0\u53d6\u6240\u6709\u89c6\u9891\u94fe\u63a5\u548c\u6807\u9898
        link_pattern = r'<a href="(/index.php/vod/play/id/\d+/sid/1/nid/1\.html)"\s+title="([^"]+)"'
        link_matches = re.findall(link_pattern, html)
        # \u63d0\u53d6\u5c01\u9762\u56fe
        pic_pattern = r'<a href="(/index.php/vod/play/id/\d+/sid/1/nid/1\.html)".*?<img[^>]+data-original="([^"]+)"'
        pic_matches = re.findall(pic_pattern, html, re.DOTALL)
        pic_map = {link: pic for link, pic in pic_matches}
        # \u63d0\u53d6\u65f6\u957f
        dur_pattern = r'<a href="(/index.php/vod/play/id/\d+/sid/1/nid/1\.html)".*?<span class="duration">([^<]*)</span>'
        dur_matches = re.findall(dur_pattern, html, re.DOTALL)
        dur_map = {link: dur for link, dur in dur_matches}
        # \u5408\u5e76
        for link, title in link_matches:
            if not title:
                continue
            id_match = re.search(r'/id/(\d+)/', link)
            if not id_match:
                continue
            vod_id = id_match.group(1)
            pic = pic_map.get(link, "")
            pic = pic.strip() if pic and not pic.startswith("data:") else ""
            duration = dur_map.get(link, "").strip()
            items.append({
                "vod_id": vod_id,
                "vod_name": title.strip(),
                "vod_pic": pic,
                "vod_remarks": duration if duration else "HD",
            })
        # \u5982\u679c\u4e0a\u8ff0\u65b9\u6cd5\u6ca1\u6709\u5339\u914d\u5230\uff0c\u5c1d\u8bd5\u5907\u7528\u65b9\u6cd5
        if not items:
            # \u5907\u7528\uff1a\u5339\u914d\u6240\u6709 /vod/play/id/ \u94fe\u63a5
            alt_pattern = r'<a href="(/index.php/vod/play/id/\d+/sid/1/nid/1\.html)"[^>]*>(.*?)</a>'
            alt_matches = re.findall(alt_pattern, html, re.DOTALL)
            for link, text in alt_matches:
                id_match = re.search(r'/id/(\d+)/', link)
                if not id_match:
                    continue
                # \u4ece\u6587\u672c\u4e2d\u63d0\u53d6\u6807\u9898\uff08\u53bb\u9664\u65f6\u957f\u3001\u65e5\u671f\u7b49\u4fe1\u606f\uff09
                title = re.sub(r'\d+:\d+.*$', '', text).strip()
                if not title:
                    continue
                items.append({
                    "vod_id": id_match.group(1),
                    "vod_name": title,
                    "vod_pic": "",
                    "vod_remarks": "HD",
                })
        return items

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
            "vod_id": vid,
            "vod_name": title or "\u672a\u77e5\u6807\u9898",
            "vod_pic": pic or "",
            "vod_remarks": remarks,
            "vod_content": "",
            "vod_play_from": "\u64ad\u653e",
            "vod_play_url": "\u64ad\u653e$" + pid,
        }]}

    def detailContent(self, ids):
        raw = self._norm_ids(ids)
        if not raw:
            return {"list": []}
        # \u6784\u9020\u64ad\u653e\u9875URL
        play_url = f"{self.host}/index.php/vod/play/id/{raw}/sid/1/nid/1.html"
        r = self._fetch(play_url)
        title = f"视频{raw}"
        pic = ""
        if r:
            html = r.text
            # \u63d0\u53d6\u6807\u9898
            title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                # \u6e05\u6d17\u7ad9\u540d\u540e\u7f00
                title = re.sub('\\s*-\\s*\u5728\u7ebf\u64ad\u653e.*$', '', title)
                title = re.sub('\\s*\u7b2c\\d+\u96c6\\s*-\\s*.*$', '', title)
                title = re.sub('\\s*-\\s*\u6700\u65b0AV.*$', '', title)
            # \u63d0\u53d6\u5c01\u9762
            pic_match = re.search(r'<img[^>]+class="thumb"[^>]+data-original="([^"]+)"', html, re.DOTALL)
            if pic_match:
                pic = pic_match.group(1)
            # \u5982\u679c\u4e0a\u9762\u6ca1\u627e\u5230\uff0c\u5c1d\u8bd5\u5176\u4ed6\u6a21\u5f0f
            if not pic:
                pic_match2 = re.search(r'data-original="([^"]+)"', html, re.DOTALL)
                if pic_match2:
                    pic = pic_match2.group(1)
        if not title or title == "\u672a\u77e5\u6807\u9898":
            title = f"视频{raw}"
        # \u8fd4\u56de\u8be6\u60c5\u6570\u636e\uff0c\u64ad\u653e\u5730\u5740\u7531 playerContent \u5904\u7406
        return {
            "list": [{
                "vod_id": raw,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": "\u9ad8\u6e05",
                "vod_content": "",
                "vod_play_from": "\u64ad\u653e",
                "vod_play_url": f"播放${raw}",
            }]
        }

    def categoryContent(self, tid, pg, filter, extend):
        page = pg or "1"
        url = f"{self.host}/index.php/vod/type/page/{page}.html"
        # \u5982\u679c\u6709\u5206\u7c7b\u7b5b\u9009\uff0c\u5c1d\u8bd5\u52a0\u4e0a\u5206\u7c7b\u53c2\u6570
        if tid and tid != "1":
            url = f"{self.host}/index.php/vod/type/id/{tid}/page/{page}.html"
        self.log({"category": "fetching", "url": url})
        r = self._fetch(url)
        if not r:
            self.log({"category": "fetch_failed", "url": url})
            return {"list": [], "page": int(page), "pagecount": 1, "limit": 20, "total": 0}
        self.log({"category": "fetch_success", "status": r.status_code, "html_len": len(r.text)})
        items = self._parse_list(r.text, url)
        self.log({"category": "parsed_items", "count": len(items)})
        # \u4ece\u9875\u9762\u63d0\u53d6\u603b\u9875\u6570
        pagecount = 495
        total_match = re.search('\u5171(\\d+)\u9875', r.text)
        if total_match:
            pagecount = int(total_match.group(1))
        return {
            "list": items,
            "page": int(page),
            "pagecount": pagecount,
            "limit": 20,
            "total": len(items) * pagecount,
        }

    def searchContent(self, key, quick, pg="1"):
        if not key or len(key.strip()) < 2:
            return {"list": [], "page": 1}
        # \u641c\u7d22\u8bcd\u53ef\u80fd\u5305\u542b\u4e2d\u6587\uff0c\u9700\u8981 URL \u7f16\u7801
        encoded_key = quote(key.strip().encode('utf-8'))
        url = f"{self.host}/index.php/vod/search.html?wd={encoded_key}"
        r = self._fetch(url)
        if not r:
            return {"list": [], "page": 1}
        items = self._parse_list(r.text, url)
        return {"list": items, "page": int(pg)}

    def _extract_play_url(self, html):
        """\u4ece\u64ad\u653e\u9875\u63d0\u53d6 m3u8 \u5730\u5740"""
        # \u5339\u914d var player_aaaa \u4e2d\u7684 url
        pattern = r'var player_aaaa=.*?"url":"([^"]+)"'
        match = re.search(pattern, html, re.DOTALL)
        if match:
            url = match.group(1)
            # \u53cd\u8f6c\u4e49 \/
            url = url.replace('\\/', '/')
            if url.startswith("//"):
                url = "https:" + url
            if not url.startswith("http"):
                url = "https://" + url
            return url
        return None

    def _m3u8_proxy_url(self, url):
        """\u751f\u6210 m3u8 \u4ee3\u7406\u5730\u5740"""
        proxy_base = self.getProxyUrl()
        # \u79fb\u9664\u5df2\u6709\u7684\u67e5\u8be2\u53c2\u6570
        if '?' in proxy_base:
            proxy_base = proxy_base.split('?')[0]
        return proxy_base + "?do=py&url=" + quote(str(url or ""), safe="")

    def playerContent(self, flag, id, vipFlags):
        play_url = str(id) if id else ""

        # \u5982\u679c id \u662f "\u540d\u79f0$\u5730\u5740" \u683c\u5f0f\uff0c\u63d0\u53d6\u5730\u5740\u90e8\u5206
        if play_url and "$" in play_url:
            parts = play_url.split("$", 1)
            if len(parts) == 2:
                play_url = parts[1]

        # \u5982\u679c play_url \u662f\u7eaf\u6570\u5b57ID\uff0c\u8bf7\u6c42\u64ad\u653e\u9875\u63d0\u53d6m3u8
        if play_url and re.match(r'^\d+$', play_url):
            page_url = f"{self.host}/index.php/vod/play/id/{play_url}/sid/1/nid/1.html"
            r = self._fetch(page_url)
            if r:
                m3u8_url = self._extract_play_url(r.text)
                if m3u8_url:
                    # \u8fd4\u56de\u4ee3\u7406\u5730\u5740\uff08\u56e0\u4e3am3u8\u6709\u5e7f\u544a\u9700\u8981\u6e05\u6d17\uff09
                    return {"parse": 0, "url": self._m3u8_proxy_url(m3u8_url), "header": {"User-Agent": self.headers["User-Agent"]}}
            # \u964d\u7ea7\u5230\u64ad\u653e\u9875\u55c5\u63a2
            return {"parse": 1, "url": page_url, "header": self.headers}

        # \u8865\u5168\u534f\u8bae
        if play_url and not play_url.startswith("http"):
            if not play_url.startswith("//"):
                play_url = "https://" + play_url

        if not play_url:
            return {"parse": 0, "url": "", "header": {}}

        if play_url.endswith((".m3u8", ".mp4")):
            if ".m3u8" in play_url:
                return {"parse": 0, "url": self._m3u8_proxy_url(play_url), "header": {"User-Agent": self.headers["User-Agent"]}}
            return {"parse": 0, "url": play_url, "header": {"User-Agent": self.headers["User-Agent"]}}

        # \u5982\u679c\u5df2\u7ecf\u662f\u64ad\u653e\u9875URL
        if "/vod/play/" in play_url:
            r = self._fetch(play_url)
            if r:
                m3u8_url = self._extract_play_url(r.text)
                if m3u8_url:
                    return {"parse": 0, "url": self._m3u8_proxy_url(m3u8_url), "header": {"User-Agent": self.headers["User-Agent"]}}
            return {"parse": 1, "url": play_url, "header": self.headers}

        return {"parse": 0, "url": play_url, "header": {"User-Agent": self.headers["User-Agent"]}}

    def _get_ad_filter(self):
        """\u5ef6\u8fdf\u52a0\u8f7d ad_filter \u6a21\u5757"""
        if self._ad_filter is not None:
            return self._ad_filter
        try:
            from ad_filter import M3u8AdFilter
            self._ad_filter = M3u8AdFilter()
            return self._ad_filter
        except ImportError:
            self._ad_filter = False
            return None

    def localProxy(self, param):
        """m3u8 \u672c\u5730\u4ee3\u7406 + \u5e7f\u544a\u5206\u7247\u8fc7\u6ee4"""
        target = unquote(str((param or {}).get("url", "") or ""))
        if not re.match(r"^https?://", target, re.I):
            return [400, "text/plain", b"invalid url"]

        # \u5148\u5c1d\u8bd5\u4f7f\u7528 ad_filter \u6a21\u5757
        ad_filter = self._get_ad_filter()
        try:
            r = self._fetch(target, stream=True, timeout=15)
            if not r or getattr(r, "status_code", 0) != 200:
                return [502, "text/plain", b"m3u8 fetch failed"]
            raw = getattr(r, "content", b"") or b""
            if not raw:
                return [502, "text/plain", b"empty response"]
            text = raw.decode("utf-8", errors="ignore")
            if "#EXTM3U" not in text:
                return [502, "text/plain", b"invalid m3u8"]

            # \u4f7f\u7528 ad_filter \u6a21\u5757\u6e05\u6d17
            if ad_filter:
                try:
                    cleaned = ad_filter.clean(text, target)
                    if cleaned and "#EXTM3U" in cleaned:
                        return [200, "application/vnd.apple.mpegurl", cleaned.encode("utf-8")]
                except Exception as e:
                    self.log({"localProxy": "ad_filter_error", "error": str(e)})

            # \u964d\u7ea7\u6e05\u6d17
            cleaned = self._clean_m3u8_fallback(text, target)
            return [200, "application/vnd.apple.mpegurl", cleaned.encode("utf-8")]
        except Exception as e:
            self.log({"localProxy": "error", "error": str(e)})
            return [500, "text/plain", b"m3u8 proxy error"]

    def _clean_m3u8_fallback(self, text, source_url):
        """\u964d\u7ea7\u6e05\u6d17\uff1aad_filter \u4e0d\u53ef\u7528\u65f6\u4f7f\u7528"""
        lines = [line.strip() for line in str(text or "").replace("\r", "").split("\n") if line.strip()]
        if not lines:
            return "#EXTM3U\n"

        # \u591a\u7801\u7387\u4e3b\u8868\u5904\u7406
        if any(line.startswith("#EXT-X-STREAM-INF") for line in lines):
            out = []
            for line in lines:
                if line.startswith("#"):
                    out.append(line)
                else:
                    child = urljoin(source_url, line)
                    out.append(self._m3u8_proxy_url(child) if ".m3u8" in child.lower() else child)
            return "\n".join(out) + "\n"

        # \u5355\u7801\u7387\uff1a\u6309\u951a\u70b9\u8fc7\u6ee4
        source_path = urlparse(source_url).path
        source_parts = [p for p in source_path.split("/") if p]
        # \u951a\u70b9\uff1a\u53d6 m3u8_url \u76ee\u5f55
        content_root = ""
        if len(source_parts) >= 3:
            content_root = "/" + "/".join(source_parts[:3]) + "/"
        elif len(source_parts) >= 2:
            content_root = "/" + "/".join(source_parts[:2]) + "/"

        segments = []
        pending = []
        removed = 0
        kept = 0

        for line in lines:
            if line.startswith("#EXTINF"):
                pending = [line]
                continue
            if pending and line.startswith("#"):
                pending.append(line)
                continue
            if pending:
                media = urljoin(source_url, line)
                # \u68c0\u67e5\u662f\u5426\u5728\u951a\u70b9\u76ee\u5f55\u4e0b
                if content_root and content_root not in urlparse(media).path:
                    removed += 1
                else:
                    segments.extend(pending)
                    segments.append(media)
                    kept += 1
                pending = []
                continue
            segments.append(line)

        # \u8fc7\u6ee4\u540e\u5982\u679c kept == 0 \u6216 removed > kept\uff0c\u5168\u91cf\u8fd4\u56de\uff08\u5168\u6ee4\u515c\u5e95\uff09
        if kept == 0 or removed > kept:
            self.log({"m3u8": "fallback_triggered", "removed": removed, "kept": kept})
            # \u8fd4\u56de\u539f\u59cb\u5185\u5bb9\uff08\u4e0d\u505a\u8fc7\u6ee4\uff09
            return "\n".join(lines) + "\n"

        # \u91cd\u5199\u5206\u7247\u4e3a\u7edd\u5bf9\u5730\u5740
        out = []
        for line in segments:
            line = self._rewrite_m3u8_tag(line, source_url)
            if line == "#EXT-X-KEY:METHOD=NONE" or line == "#EXT-X-DISCONTINUITY":
                if not out or out[-1] in ("#EXT-X-DISCONTINUITY", "#EXT-X-KEY:METHOD=NONE"):
                    continue
            out.append(line)

        # \u6e05\u7406\u5c3e\u90e8\u5b64\u7acb\u6807\u7b7e
        while len(out) > 1 and out[-2] in ("#EXT-X-DISCONTINUITY", "#EXT-X-KEY:METHOD=NONE"):
            out.pop(-2)

        self.log({"m3u8": "cleaned", "removed": removed, "kept": kept})
        return "\n".join(out) + "\n"

    def _rewrite_m3u8_tag(self, line, source_url):
        """\u91cd\u5199 m3u8 \u6807\u7b7e\u4e2d\u7684 URI\uff08\u8865\u5168\u7edd\u5bf9\u5730\u5740\uff09"""
        if line.startswith("#EXT-X-KEY") or line.startswith("#EXT-X-MAP"):
            def repl(match):
                return 'URI="' + urljoin(source_url, match.group(1)) + '"'
            return re.sub(r'URI="([^"]+)"', repl, line)
        if line and not line.startswith("#"):
            return urljoin(source_url, line)
        return line

    def recommendContent(self, ids, *args):
        return {"list": []}

    def destroy(self):
        pass