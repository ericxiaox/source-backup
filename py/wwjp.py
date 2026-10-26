# coding: utf-8
"""
\u7ad9\u70b9: \u5916\u56f4\u7cbe\u54c1
\u4e3b\u57df\u540d: https://o8cjc.wwjpp.shop/
\u5907\u7528\u57df\u540d: wwjpp.buzz
CMS: MacCMS
\u7c7b\u578b: \u6210\u4eba\u89c6\u9891
\u7ef4\u62a4\u4fe1\u606f: 2026-08-06
"""
import json
import re
from urllib.parse import quote, urljoin, unquote, urlparse

from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
    def __init__(self):
        self.host = "https://o8cjc.wwjpp.shop"
        self.backup_host = "https://wwjpp.buzz"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 22127RK46C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
            "Referer": self.host + "/"
        }
        self.classes = [
            {"type_id": "20", "type_name": "\u56fd\u4ea7\u5927\u5236\u4f5c"},
            {"type_id": "21", "type_name": "\u5077\u62cd\u81ea\u62cd"},
            {"type_id": "22", "type_name": "\u4e71\u4f26\u6bc1\u4e09\u89c2"},
            {"type_id": "23", "type_name": "\u4e3b\u64ad\u5973\u7f51\u7ea2"},
            {"type_id": "24", "type_name": "\u9ed1\u6599\u7f51\u66dd"},
            {"type_id": "25", "type_name": "\u9ad8\u6e05\u65e0\u7801"},
            {"type_id": "26", "type_name": "\u4e2d\u6587\u5b57\u5e55"},
            {"type_id": "27", "type_name": "\u6b27\u7f8e\u7cbe\u54c1"},
            {"type_id": "28", "type_name": "\u6deb\u4e71\u5b66\u751f\u59b9"},
            {"type_id": "29", "type_name": "\u52a8\u6f2b\u7cbe\u9009"},
            {"type_id": "30", "type_name": "\u9ad8\u6e05\u6709\u7801"},
            {"type_id": "31", "type_name": "\u65e5\u672c\u7d20\u4eba"},
            {"type_id": "32", "type_name": "\u65e0\u7801\u6d41\u51fa"},
            {"type_id": "33", "type_name": "FC2"},
            {"type_id": "34", "type_name": "\u4f1a\u6240\u6280\u5e08"},
            {"type_id": "35", "type_name": "\u56fd\u4ea7\u63a8\u8350"},
            {"type_id": "36", "type_name": "\u63a2\u82b1\u7ea6\u70ae"},
            {"type_id": "37", "type_name": "\u97e9\u56fd\u76f4\u64ad"},
            {"type_id": "38", "type_name": "\u56fd\u4ea7\u76f4\u64ad"},
            {"type_id": "39", "type_name": "\u6deb\u59bb\u7eff\u5e3d"},
            {"type_id": "40", "type_name": "\u5236\u670d\u8bf1\u60d1"},
            {"type_id": "41", "type_name": "\u91cd\u53e3\u730e\u5947"},
            {"type_id": "42", "type_name": "\u4e1c\u4eac\u70ed"},
            {"type_id": "43", "type_name": "\u4e00\u672c\u9053"},
            {"type_id": "44", "type_name": "\u6b27\u7f8e\u7cbe\u54c1"}
        ]
        self.filters = {}
        for c in self.classes:
            self.filters[c["type_id"]] = []

    def getName(self):
        return "\u5916\u56f4\u7cbe\u54c1"

    def getDependence(self):
        return []

    def init(self, extend=""):
        self.extend = extend

    def _get_host(self):
        return self.host

    def _fetch_html(self, url):
        try:
            resp = self.fetch(url, headers=self.headers, timeout=15)
            if resp and hasattr(resp, "content"):
                return resp.content.decode("utf-8", errors="ignore")
        except Exception as e:
            self.log({"action": "fetch_error", "url": url, "error": str(e)})
        return None

    def _parse_video_list(self, html):
        if not html:
            return []
        items = []
        article_pattern = r'<article>.*?<a[^>]*href="([^"]+)"[^>]*>.*?<img[^>]*data-src="([^"]+)"[^>]*>.*?<cite>([^<]+)</cite>.*?</article>'
        matches = re.findall(article_pattern, html, re.DOTALL)
        for match in matches:
            link, pic, title = match
            vod_id = re.search(r'/id/(\d+)\.html', link)
            if vod_id:
                items.append({
                    "vod_id": vod_id.group(1),
                    "vod_name": title.strip(),
                    "vod_pic": pic,
                    "vod_remarks": ""
                })
        return items

    def homeContent(self, filter):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def homeVideoContent(self):
        url = f"{self._get_host()}/index.php/vod/type/id/20.html"
        html = self._fetch_html(url)
        items = self._parse_video_list(html)
        return {"list": items[:20]}

    def categoryContent(self, tid, pg, filter, extend):
        page = pg or "1"
        if page == "1":
            url = f"{self._get_host()}/index.php/vod/type/id/{tid}.html"
        else:
            url = f"{self._get_host()}/index.php/vod/type/id/{tid}/page/{page}.html"
        html = self._fetch_html(url)
        items = self._parse_video_list(html)
        total = 0
        pagecount = 1
        if html:
            total_match = re.search(r'<em[^>]*class="mac_total"[^>]*>(\d+)</em>', html)
            if total_match:
                total = int(total_match.group(1))
            page_matches = re.findall(r'<a[^>]*href="[^"]*page/(\d+)\.html"[^>]*>(\d+)</a>', html)
            if page_matches:
                max_page = max([int(p[0]) for p in page_matches])
                pagecount = max_page
            last_match = re.search('<a[^>]*href="[^"]*page/(\\d+)\\.html"[^>]*>\u5c3e\u9875</a>', html)
            if last_match:
                pagecount = int(last_match.group(1))
        return {
            "list": items,
            "page": int(page),
            "pagecount": pagecount,
            "limit": 20,
            "total": total
        }

    def detailContent(self, ids):
        if not ids:
            return {"list": []}
        if isinstance(ids, (int, str)):
            vod_id = str(ids)
        elif isinstance(ids, list) and len(ids) > 0:
            vod_id = str(ids[0])
        else:
            return {"list": []}
        url = f"{self._get_host()}/index.php/vod/detail/id/{vod_id}.html"
        html = self._fetch_html(url)
        if not html:
            return {"list": []}
        title_match = re.search('<h2[^>]*>\u7247\u540d[\uff1a:]\\s*([^<]+)</h2>', html)
        title = title_match.group(1).strip() if title_match else ""
        pic_match = re.search(r'<div[^>]*class="video-poster"[^>]*>.*?<img[^>]*src="([^"]+)"', html, re.DOTALL)
        pic = pic_match.group(1) if pic_match else ""
        play_btn_pattern = r'<button[^>]*class="play-btn"[^>]*onclick="window\.location\.href=\'([^\']+)\'"[^>]*>([^<]+)</button>'
        play_matches = re.findall(play_btn_pattern, html)
        play_froms = []
        play_urls = []
        for idx, (play_link, play_name) in enumerate(play_matches):
            play_froms.append(play_name.strip())
            sid_match = re.search(r'/sid/(\d+)/nid/(\d+)', play_link)
            if sid_match:
                sid, nid = sid_match.group(1), sid_match.group(2)
                play_urls.append(f"第1集${vod_id}|{sid}|{nid}")
            else:
                play_urls.append(f"第1集${vod_id}|1|1")
        if not play_matches:
            play_link_match = re.search('<a[^>]*href="([^"]*play[^"]*)"[^>]*>\u70b9\u6b64\u7acb\u5373\u89c2\u770b', html)
            if play_link_match:
                play_link = play_link_match.group(1)
                play_froms.append("\u64ad\u653e")
                sid_match = re.search(r'/sid/(\d+)/nid/(\d+)', play_link)
                if sid_match:
                    sid, nid = sid_match.group(1), sid_match.group(2)
                    play_urls.append(f"第1集${vod_id}|{sid}|{nid}")
                else:
                    play_urls.append(f"第1集${vod_id}|1|1")
        vod = {
            "vod_id": vod_id,
            "vod_name": title or "\u89c6\u9891",
            "vod_pic": pic,
            "vod_remarks": "",
            "vod_content": "",
            "vod_play_from": "$$$".join(play_froms) if play_froms else "",
            "vod_play_url": "$$$".join(play_urls) if play_urls else ""
        }
        return {"list": [vod]}

    def searchContent(self, key, quick, pg="1"):
        if not key:
            return {"list": [], "page": 1}
        url = f"{self._get_host()}/index.php/vod/search.html?wd={quote(key)}"
        html = self._fetch_html(url)
        items = self._parse_video_list(html)
        return {"list": items, "page": int(pg)}

    def playerContent(self, flag, id, vipFlags):
        parts = id.split("|")
        if len(parts) >= 3:
            vod_id, sid, nid = parts[0], parts[1], parts[2]
        else:
            vod_id = id
            sid, nid = "1", "1"
        url = f"{self._get_host()}/index.php/vod/play/id/{vod_id}/sid/{sid}/nid/{nid}.html"
        html = self._fetch_html(url)
        if not html:
            return {"parse": 1, "url": url, "header": self.headers}
        player_match = re.search(r'var\s+player_aaaa\s*=\s*({[^}]+})', html)
        if player_match:
            try:
                player_data = json.loads(player_match.group(1))
                play_url = player_data.get("url", "")
                encrypt = player_data.get("encrypt", 0)
                if play_url and encrypt == 0:
                    if play_url.endswith(".m3u8"):
                        return {"parse": 0, "url": self._m3u8_proxy_url(play_url), "header": self.headers}
                    return {"parse": 0, "url": play_url, "header": self.headers}
            except Exception as e:
                self.log({"action": "parse_player_fail", "error": str(e)})
        iframe_match = re.search(r'<iframe[^>]*src="([^"]+)"[^>]*>', html)
        if iframe_match:
            iframe_src = iframe_match.group(1)
            if iframe_src.startswith("http"):
                return {"parse": 1, "url": iframe_src, "header": self.headers}
        return {"parse": 1, "url": url, "header": self.headers}

    def _m3u8_proxy_url(self, url):
        return self.getProxyUrl() + "&url=" + quote(str(url or ""), safe="")

    def localProxy(self, param):
        target = unquote(str((param or {}).get("url", "") or ""))
        if not re.match(r"^https?://", target, re.I):
            return [400, "text/plain", b"invalid url"]
        try:
            res = self.fetch(target, headers=self.headers, timeout=15, verify=False)
            if not res or getattr(res, "status_code", 0) != 200:
                return [502, "text/plain", b"m3u8 fetch failed"]
            raw = getattr(res, "content", b"") or b""
            text = raw.decode("utf-8", errors="ignore")
            if "#EXTM3U" not in text:
                return [502, "text/plain", b"invalid m3u8"]
            cleaned = self._clean_m3u8(text, target)
            return [200, "application/vnd.apple.mpegurl", cleaned.encode("utf-8")]
        except Exception as e:
            self.log("m3u8\u4ee3\u7406\u5931\u8d25: " + str(e))
            return [500, "text/plain", b"m3u8 proxy error"]

    def _clean_m3u8(self, text, source_url):
        """\u6e05\u6d17 m3u8\uff1a\u8fc7\u6ee4\u5e7f\u544a\u5206\u7247\uff0c\u4fdd\u7559\u6b63\u7247"""
        if not text:
            return "#EXTM3U\n"
        lines = [line.strip() for line in text.replace("\r", "").split("\n")]
        if not lines:
            return "#EXTM3U\n"

        # \u5982\u679c\u662f\u591a\u7801\u7387 m3u8\uff08\u6709 #EXT-X-STREAM-INF\uff09\uff0c\u9012\u5f52\u5904\u7406\u5b50 m3u8
        if any(line.startswith("#EXT-X-STREAM-INF") for line in lines):
            out = []
            for line in lines:
                if line.startswith("#"):
                    out.append(line)
                elif line and not line.startswith("#"):
                    child = urljoin(source_url, line)
                    out.append(self._m3u8_proxy_url(child) if ".m3u8" in child.lower() else child)
            return "\n".join(out) + "\n"

        # \u5355\u7801\u7387 m3u8\uff1a\u8fc7\u6ee4\u5e7f\u544a\u5206\u7247
        # \u5e7f\u544a\u5206\u7247\u7279\u5f81\uff1a\u8def\u5f84\u5305\u542b ad/\u3001\u77ed\u65f6\u957f\u3001\u7279\u5b9a\u57df\u540d
        ad_patterns = [
            r'/ad[s]?/',
            r'/advert/',
            r'/banner/',
            r'/promo/',
            r'/sponsor/',
            r'[/_]ad[/_]',
            r'\.ad\.',
            r'advertisement',
            r'guanggao',
            r'gg[0-9]+',
            r'pre[-_]?roll',
            r'post[-_]?roll',
            r'mid[-_]?roll',
            r'seg_00000\.',  # \u7b2c\u4e00\u4e2a\u5206\u7247\u901a\u5e38\u662f\u5e7f\u544a
            r'seg_00001\.',
            r'seg_00002\.',
            r'[0-9a-f]{8}\.jpg$',  # \u77ed\u54c8\u5e0c\u540d\u7684 jpg \u53ef\u80fd\u662f\u5e7f\u544a
        ]

        source_path = urlparse(source_url).path
        source_parts = [p for p in source_path.split("/") if p]
        # \u53d6\u524d\u4e09\u7ea7\u4f5c\u4e3a\u5185\u5bb9\u6839\u8def\u5f84
        content_root = "/" + "/".join(source_parts[:3]) + "/" if len(source_parts) >= 3 else ""
        if not content_root and len(source_parts) >= 2:
            content_root = "/" + "/".join(source_parts[:2]) + "/"

        segments = []
        pending = []
        removed = 0

        # \u68c0\u6d4b\u662f\u5426\u6709 KEY \u6807\u7b7e\uff0c\u6807\u8bb0\u4e3a\u52a0\u5bc6\u89c6\u9891
        has_key = any(line.startswith("#EXT-X-KEY") and "URI" in line for line in lines)

        i = 0
        while i < len(lines):
            line = lines[i]
            if not line:
                i += 1
                continue

            # \u6536\u96c6 EXTINF \u5757
            if line.startswith("#EXTINF"):
                pending = [line]
                i += 1
                # \u6536\u96c6\u540e\u7eed\u7684\u6ce8\u91ca\u884c
                while i < len(lines) and lines[i].startswith("#") and not lines[i].startswith("#EXTINF"):
                    pending.append(lines[i])
                    i += 1
                # \u6536\u96c6\u5a92\u4f53 URL
                if i < len(lines) and lines[i] and not lines[i].startswith("#"):
                    media = lines[i]
                    media_url = media if media.startswith("http") else urljoin(source_url, media)
                    should_remove = False

                    # 1. \u68c0\u67e5\u5e7f\u544a\u7279\u5f81
                    media_lower = media_url.lower()
                    for pattern in ad_patterns:
                        if re.search(pattern, media_lower, re.I):
                            should_remove = True
                            break

                    # 2. \u68c0\u67e5\u65f6\u957f\uff1a\u77ed\u4e8e 2 \u79d2\u7684\u5e7f\u544a
                    if not should_remove:
                        for p in pending:
                            if p.startswith("#EXTINF"):
                                dur_match = re.search(r'#EXTINF:([\d.]+)', p)
                                if dur_match:
                                    try:
                                        dur = float(dur_match.group(1))
                                        if dur < 2.0 and dur > 0:
                                            should_remove = True
                                            break
                                    except:
                                        pass

                    # 3. \u5bf9\u4e8e\u52a0\u5bc6\u89c6\u9891\uff0c\u68c0\u67e5\u5206\u7247\u5e8f\u53f7
                    if not should_remove and has_key:
                        # \u68c0\u67e5\u5206\u7247\u8def\u5f84\u662f\u5426\u5305\u542b\u65e5\u671f\u548c\u89c6\u9891ID
                        # \u6b63\u7247\u8def\u5f84\u683c\u5f0f: /20260805/7251a1c7cef11f7f/xxx.jpg
                        # \u5e7f\u544a\u8def\u5f84\u4e0d\u540c
                        if content_root and content_root not in media_url:
                            # \u4f46\u5982\u679c\u662f\u540c\u57df\u540d\u7684\u5176\u4ed6\u8def\u5f84\uff0c\u4fdd\u7559
                            if urlparse(media_url).netloc != urlparse(source_url).netloc:
                                should_remove = True

                    # 4. \u989d\u5916\uff1a\u68c0\u67e5\u662f\u5426\u5305\u542b "seg_00000" \u6216 "seg_00001" \u5f00\u5934\uff08\u5e7f\u544a\uff09
                    if not should_remove:
                        seg_match = re.search(r'seg_(\d+)\.', media_url)
                        if seg_match:
                            seg_num = int(seg_match.group(1))
                            if seg_num <= 3:
                                should_remove = True

                    if should_remove:
                        removed += 1
                    else:
                        # \u5bf9\u4e8e\u52a0\u5bc6\u89c6\u9891\uff0c\u9700\u8981\u8865\u5168 KEY \u7684\u7edd\u5bf9\u8def\u5f84
                        if has_key:
                            for j, p in enumerate(pending):
                                if p.startswith("#EXT-X-KEY") and "URI=" in p:
                                    key_match = re.search(r'URI="([^"]+)"', p)
                                    if key_match:
                                        key_url = key_match.group(1)
                                        if not key_url.startswith("http"):
                                            key_url = urljoin(source_url, key_url)
                                        pending[j] = p.replace(key_match.group(0), f'URI="{key_url}"')
                        segments.extend(pending)
                        segments.append(media_url)
                    i += 1
                else:
                    # \u6ca1\u6709\u5a92\u4f53 URL\uff0c\u4fdd\u7559 pending
                    segments.extend(pending)
                    i += 1
                continue

            # \u5904\u7406\u5355\u72ec\u7684\u6807\u7b7e\u884c
            if line.startswith("#"):
                # \u5904\u7406 KEY \u6807\u7b7e\uff0c\u8865\u5168 URI
                if line.startswith("#EXT-X-KEY") and "URI=" in line:
                    key_match = re.search(r'URI="([^"]+)"', line)
                    if key_match:
                        key_url = key_match.group(1)
                        if not key_url.startswith("http"):
                            key_url = urljoin(source_url, key_url)
                        line = line.replace(key_match.group(0), f'URI="{key_url}"')
                segments.append(line)
            else:
                # \u76f4\u63a5\u7684\u5a92\u4f53 URL
                media_url = line if line.startswith("http") else urljoin(source_url, line)
                should_remove = False
                media_lower = media_url.lower()
                for pattern in ad_patterns:
                    if re.search(pattern, media_lower, re.I):
                        should_remove = True
                        break
                if should_remove:
                    removed += 1
                else:
                    segments.append(media_url)
            i += 1

        # \u6e05\u7406\u5c3e\u90e8\u65e0\u6548\u6807\u7b7e
        while len(segments) > 1 and segments[-1] in ("#EXT-X-DISCONTINUITY", "#EXT-X-KEY:METHOD=NONE"):
            segments.pop(-1)

        if removed:
            self.log({"action": "m3u8_ad_filtered", "removed": removed})

        if segments and not segments[0].startswith("#EXTM3U"):
            segments.insert(0, "#EXTM3U")

        return "\n".join(segments) + "\n"
