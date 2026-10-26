# coding: utf-8
"""
\u4e50\u556a\u798f\u5229 TVBox \u722c\u866b
\u7ad9\u70b9\uff1ahttps://lpfl12.cfd/
\u7c7b\u578b\uff1aMacCMS HTML \u5f71\u89c6\u7ad9
"""
import re
import json
import posixpath
from urllib.parse import urljoin, quote, unquote, urlparse

from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    def __init__(self):
        self.host = "https://lpfl12.cfd"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 22127RK46C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36",
            "Referer": self.host + "/"
        }
        # \u5206\u7c7b\u5217\u8868\uff1atid \u8303\u56f4 28-48
        self.classes = [
            {"type_id": "28", "type_name": "\u56fd\u4ea7\u81ea\u62cd"},
            {"type_id": "29", "type_name": "\u4e3b\u64ad\u8bf1\u60d1"},
            {"type_id": "30", "type_name": "\u63a2\u82b1\u7ea6\u70ae"},
            {"type_id": "31", "type_name": "\u5077\u62cd\u5077\u7aa5"},
            {"type_id": "32", "type_name": "\u7f51\u66dd\u5403\u74dc"},
            {"type_id": "33", "type_name": "\u6296\u9634\u77ed\u7247"},
            {"type_id": "34", "type_name": "\u4f20\u5a92\u5267\u60c5"},
            {"type_id": "35", "type_name": "\u65e5\u97e9\u4e3b\u64ad"},
            {"type_id": "36", "type_name": "\u65e5\u97e9\u65e0\u7801"},
            {"type_id": "37", "type_name": "\u4e2d\u6587\u5b57\u5e55"},
            {"type_id": "38", "type_name": "AV\u89e3\u8bf4"},
            {"type_id": "39", "type_name": "\u6362\u8138\u660e\u661f"},
            {"type_id": "40", "type_name": "\u5f3a\u5978\u4e71\u4f26"},
            {"type_id": "41", "type_name": "\u5973\u4f18\u660e\u661f"},
            {"type_id": "42", "type_name": "\u6b27\u7f8e\u6fc0\u60c5"},
            {"type_id": "43", "type_name": "\u91cd\u53e3\u6fc0\u60c5"},
            {"type_id": "44", "type_name": "\u4e09\u7ea7\u4f26\u7406"},
            {"type_id": "45", "type_name": "\u5267\u60c5\u52a8\u6f2b"},
            {"type_id": "46", "type_name": "SM\u8c03\u6559"},
            {"type_id": "47", "type_name": "\u5973\u540c\u6027\u604b"},
            {"type_id": "48", "type_name": "VR\u89c6\u89d2"},
        ]
        self.filters = {str(i): [] for i in range(28, 49)}

    def getName(self):
        return "\u4e50\u556a\u798f\u5229"

    def getDependence(self):
        return []

    def init(self, extend=""):
        self.extend = extend

    def getProxyUrl(self):
        return "http://127.0.0.1:9978/proxy"

    def homeContent(self, filter):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def homeVideoContent(self):
        return self.categoryContent("28", "1", False, {})

    def categoryContent(self, tid, pg, filter, extend):
        page = str(pg) if pg else "1"
        url = f"{self.host}/frim/index{tid}-{page}.html"
        if page == "1":
            url = f"{self.host}/frim/index{tid}.html"

        try:
            res = self.fetch(url, headers=self.headers)
            if not res:
                return {"list": [], "page": int(page), "pagecount": 1, "limit": 20, "total": 0}

            html = res.text
            items = self._parse_vod_list(html)
            pagecount, total = self._parse_pagination(html)

            if pagecount <= 1:
                pagecount = self._parse_last_page(html)

            return {
                "list": items,
                "page": int(page),
                "pagecount": pagecount or 1,
                "limit": 20,
                "total": total or 0
            }
        except Exception as e:
            self.log(f"categoryContent error: {str(e)}")
            return {"list": [], "page": int(page), "pagecount": 1, "limit": 20, "total": 0}

    def detailContent(self, ids):
        vod_id = str(ids[0])
        url = f"{self.host}/movie/index{vod_id}.html"

        try:
            res = self.fetch(url, headers=self.headers)
            if not res:
                return {"list": []}

            html = res.text
            vod = self._parse_detail(html, vod_id)
            return {"list": [vod]} if vod else {"list": []}
        except Exception as e:
            self.log(f"detailContent error: {str(e)}")
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/search.php"
        data = {"searchword": key}
        try:
            res = self.post(url, data=data, headers=self.headers)
            if not res:
                return {"list": [], "page": 1}

            html = res.text
            items = self._parse_search_results(html)
            return {"list": items, "page": int(pg) if pg else 1}
        except Exception as e:
            self.log(f"searchContent error: {str(e)}")
            return {"list": [], "page": 1}

    def playerContent(self, flag, id, vipFlags):
        if id and id.endswith((".m3u8", ".mp4")):
            if id.endswith(".m3u8"):
                return {"parse": 0, "url": self._m3u8_proxy_url(id), "header": {}}
            return {"parse": 0, "url": id, "header": {"User-Agent": self.headers["User-Agent"]}}

        url = id if id.startswith("http") else f"{self.host}/play/{id}.html"
        try:
            res = self.fetch(url, headers=self.headers)
            if not res:
                return {"parse": 1, "url": id, "header": self.headers}

            html = res.text
            m3u8_url = self._extract_m3u8(html)

            if m3u8_url:
                return {"parse": 0, "url": self._m3u8_proxy_url(m3u8_url), "header": {}}
            else:
                return {"parse": 1, "url": id, "header": self.headers}
        except Exception as e:
            self.log(f"playerContent error: {str(e)}")
            return {"parse": 1, "url": id, "header": self.headers}

    def _m3u8_proxy_url(self, url):
        return self.getProxyUrl() + "?do=py&url=" + quote(str(url or ""), safe="")

    def localProxy(self, param):
        """m3u8 \u4ee3\u7406 + \u5e7f\u544a\u8fc7\u6ee4"""
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

            res = self.fetch(target, headers=self.headers, timeout=15)
            if not res:
                return [502, "text/plain", b"fetch failed"]

            content = getattr(res, "content", b"") or b""
            if not content and hasattr(res, "text") and res.text:
                content = res.text.encode("utf-8", errors="ignore")

            if not content:
                return [502, "text/plain", b"empty content"]

            text = content.decode("utf-8", errors="ignore")
            if "#EXTM3U" not in text:
                return [502, "text/plain", b"invalid m3u8"]

            cleaned = self._clean_m3u8(text, target)
            return [200, "application/vnd.apple.mpegurl", cleaned.encode("utf-8")]

        except Exception as e:
            error_msg = f"localProxy error: {str(e)}".encode("utf-8", errors="ignore")
            return [500, "text/plain", error_msg]

    def _clean_m3u8(self, text, source_url):
        """\u6e05\u6d17 m3u8\uff1a\u8fc7\u6ee4\u5e7f\u544a\u5206\u7247"""
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

        # \u4ece #EXT-X-KEY \u63d0\u53d6\u6b63\u7247\u76ee\u5f55\uff08\u66f4\u51c6\u786e\uff09
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

                # \u8fc7\u6ee4\u903b\u8f91\uff1a\u5224\u65ad\u5206\u7247\u8def\u5f84\u662f\u5426\u4ee5\u6b63\u7247\u76ee\u5f55\u5f00\u5934
                is_ad = not media_parsed.path.startswith(main_dir)

                if not is_ad:
                    segments.extend(pending)
                    segments.append(media_url)
                pending = []
                continue

            if not line.startswith("#"):
                segments.append(urljoin(source_url, line))
            else:
                segments.append(line)

        # \u4e8c\u6b21\u6e05\u6d17\uff1a\u53bb\u9664\u5b64\u7acb\u7684 DISCONTINUITY \u548c KEY:METHOD=NONE
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

    def _rewrite_m3u8_tag(self, line, source_url):
        """\u91cd\u5199 m3u8 \u6807\u7b7e\u4e2d\u7684 URI"""
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

    def _parse_vod_list(self, html):
        items = []
        pattern = r'<li class="col-md-[56]\s+col-sm-4\s+col-xs-3">(.*?)</li>'
        matches = re.findall(pattern, html, re.DOTALL)

        for block in matches:
            link_match = re.search(r'href="(/movie/index(\d+)\.html)"', block)
            if not link_match:
                continue
            vod_id = link_match.group(2)

            title_match = re.search(r'title="([^"]+)"', block)
            title = title_match.group(1) if title_match else ""

            pic_match = re.search(r'data-original="([^"]+)"', block)
            pic = pic_match.group(1) if pic_match else ""

            remark_match = re.search(r'<span class="pic-text text-right">([^<]+)</span>', block)
            remark = remark_match.group(1) if remark_match else ""

            if vod_id and title:
                items.append({
                    "vod_id": vod_id,
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": remark
                })

        return items

    def _parse_search_results(self, html):
        items = []
        pattern = r'<li class="active top-line-dot clearfix">(.*?)</li>'
        matches = re.findall(pattern, html, re.DOTALL)

        for block in matches:
            link_match = re.search(r'href="(/movie/index(\d+)\.html)"', block)
            if not link_match:
                continue
            vod_id = link_match.group(2)

            title_match = re.search(r'<h3 class="title"><a href="[^"]*">([^<]+)</a></h3>', block)
            title = title_match.group(1) if title_match else ""

            pic_match = re.search(r'data-original="([^"]+)"', block)
            pic = pic_match.group(1) if pic_match else ""

            remark_match = re.search(r'<span class="pic-text text-right">([^<]+)</span>', block)
            remark = remark_match.group(1) if remark_match else ""

            if vod_id and title:
                items.append({
                    "vod_id": vod_id,
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": remark or ""
                })

        return items

    def _parse_detail(self, html, vod_id):
        title_match = re.search(r'<h3 class="title">([^<]+)</h3>', html)
        title = title_match.group(1).strip() if title_match else ""

        pic_match = re.search(r'data-original="([^"]+)"', html)
        pic = pic_match.group(1) if pic_match else ""

        desc_match = re.search(r'<span class="detail-content" style="display: none;">(.*?)</span>', html, re.DOTALL)
        content = ""
        if desc_match:
            content = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()
        if not content:
            desc_match2 = re.search(r'<span class="detail-sketch">([^<]+)</span>', html)
            content = desc_match2.group(1) if desc_match2 else ""

        vod = {
            "vod_id": str(vod_id),
            "vod_name": title or "\u672a\u77e5\u6807\u9898",
            "vod_pic": pic,
            "vod_remarks": "\u66f4\u65b0\u81f3\u7b2c1\u96c6",
            "vod_content": content,
            "vod_actor": "\u5185\u8be6",
            "vod_director": "\u5185\u8be6",
            "vod_play_from": "\u64ad\u653e",
            "vod_play_url": f"第1集${vod_id}-0-0"
        }

        return vod

    def _parse_pagination(self, html):
        pagecount = 1
        total = 0

        num_match = re.search(r'(\d+)/(\d+)', html)
        if num_match:
            pagecount = int(num_match.group(2))

        total_match = re.search('\u5171\u6709(\\d+)\u90e8\u5f71\u7247', html)
        if total_match:
            total = int(total_match.group(1))

        return pagecount, total

    def _parse_last_page(self, html):
        match = re.search('<a[^>]*href="[^"]*/index\\d+-(\\d+)\\.html"[^>]*>\u5c3e\u9875</a>', html)
        if match:
            return int(match.group(1))
        matches = re.findall(r'<a[^>]*href="[^"]*/index\d+-(\d+)\.html"[^>]*>', html)
        if matches:
            pages = [int(x) for x in matches if x.isdigit()]
            if pages:
                return max(pages)
        return 1

    def _extract_m3u8(self, html):
        match = re.search(r'var now\s*=\s*"([^"]+\.m3u8)"', html)
        if match:
            return match.group(1).replace("\\/", "/")

        match = re.search(r'now\s*=\s*"([^"]+\.m3u8)"', html)
        if match:
            return match.group(1).replace("\\/", "/")

        match = re.search(r'url\s*:\s*"([^"]+\.m3u8)"', html)
        if match:
            return match.group(1).replace("\\/", "/")

        return None

    def destroy(self):
        pass