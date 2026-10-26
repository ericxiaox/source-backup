# coding: utf-8
# \u7ad9\u70b9: 365\u9ed1\u6599\u5f71\u9662 (mh365.cc)
# \u7c7b\u578b: \u6210\u4eba\u5f71\u89c6\u805a\u5408\u7ad9 (HTML\u89e3\u6790)
# \u57df\u540d: https://www.mh365.cc

import json
import re
import base64
from urllib.parse import urljoin, urlparse, quote, unquote

from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
    def __init__(self):
        self.host = "https://www.mh365.cc"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 22127RK46C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
            "Referer": self.host + "/"
        }
        self.classes = [
            {"type_id": "oumeiag", "type_name": "\u6b27\u7f8e\u52b2\u7206"},
            {"type_id": "guochanv", "type_name": "\u56fd\u4ea7\u4f20\u5a92"},
            {"type_id": "huanlian", "type_name": "AI\u6362\u8138"},
            {"type_id": "rihank", "type_name": "\u65e5\u97e9\u65e0\u7801"},
            {"type_id": "lunliv", "type_name": "\u4f26\u7406\u5f71\u7247"},
            {"type_id": "qiangjian", "type_name": "\u5f3a\u5978\u4e71\u4f26"},
            {"type_id": "yezhan", "type_name": "\u91ce\u6218\u8f66\u9707"},
            {"type_id": "chengren", "type_name": "\u6210\u4eba\u52a8\u6f2b"},
            {"type_id": "jiatingk", "type_name": "\u5bb6\u5ead\u4e71\u4f26"},
            {"type_id": "diaojiao", "type_name": "SM\u8c03\u6559"},
            {"type_id": "baihe", "type_name": "\u767e\u5408\u5973\u540c"},
            {"type_id": "guochanx", "type_name": "\u56fd\u4ea7\u4e3b\u64ad"},
            {"type_id": "jiudian", "type_name": "\u9152\u5e97\u63a2\u82b1"},
            {"type_id": "xuesheng", "type_name": "\u5b66\u751f\u7a7a\u59d0"},
            {"type_id": "touqing", "type_name": "\u5077\u60c5\u5c11\u5987"},
            {"type_id": "chigua", "type_name": "\u5403\u74dc\u9ed1\u6599"},
            {"type_id": "luguan", "type_name": "\u64b8\u7ba1\u5fc5\u770b"},
            {"type_id": "fancha", "type_name": "\u53cd\u5dee\u6bcd\u72d7"},
            {"type_id": "zipai", "type_name": "\u81ea\u62cd\u5077\u62cd"},
            {"type_id": "zhibo", "type_name": "\u76f4\u64ad\u88f8\u804a"}
        ]
        years = [{"n": "\u5168\u90e8", "v": ""}] + [{"n": str(y), "v": str(y)} for y in range(2026, 2010, -1)]
        self.filters = {}
        for c in self.classes:
            self.filters[c["type_id"]] = [{"key": "year", "name": "\u5e74\u4ee3", "value": years}]

    def getName(self):
        return "365\u9ed1\u6599\u5f71\u9662"

    def getDependence(self):
        return []

    def init(self, extend=""):
        self.extend = extend or ""
        pass

    def homeContent(self, filter):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def homeVideoContent(self):
        url = self.host + "/"
        res = self.fetch(url, headers=self.headers)
        if not res or res.status_code != 200:
            return {"list": []}
        html = res.text
        items = []
        # \u5339\u914d\u9996\u9875\u6240\u6709\u5361\u7247 - \u66f4\u5bbd\u677e\u7684\u6a21\u5f0f
        patterns = [
            # \u6807\u51c6\u5361\u7247
            r'<article\s+class="[^"]*wu-poster-card[^"]*"[^>]*>.*?<a\s+class="[^"]*wu-poster-card__cover[^"]*"\s+href="([^"]+)"[^>]*>.*?<img[^>]*src="([^"]+)"[^>]*>.*?<h3>.*?<a\s+href="[^"]+"[^>]*>([^<]+)</a>.*?</h3>',
            # \u5907\u7528\u6a21\u5f0f
            r'<article\s+class="[^"]*wu-poster-card[^"]*"[^>]*>.*?<a\s+href="([^"]+)"[^>]*>.*?<img[^>]*src="([^"]+)"[^>]*>.*?<h3>([^<]+)</h3>',
            # \u9996\u9875magazine\u7126\u70b9
            r'<article\s+class="[^"]*wt05-magazine__item[^"]*"[^>]*>.*?<a\s+class="[^"]*wt05-magazine__media[^"]*"\s+href="([^"]+)"[^>]*>.*?<img[^>]*src="([^"]+)"[^>]*>.*?<h2>.*?<a\s+href="[^"]+"[^>]*>([^<]+)</a>.*?</h2>',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                if len(match) >= 3:
                    vod_id = match[0]
                    vod_pic = match[1]
                    vod_name = match[2].strip()
                    if vod_id and vod_name and not vod_id.startswith("#") and not vod_id.startswith("javascript"):
                        items.append({
                            "vod_id": vod_id,
                            "vod_name": vod_name,
                            "vod_pic": urljoin(self.host, vod_pic),
                            "vod_remarks": ""
                        })
                if len(items) >= 30:
                    break
            if len(items) >= 30:
                break
        # \u5982\u679c\u4e0a\u9762\u7684\u90fd\u6ca1\u5339\u914d\u5230\uff0c\u5c1d\u8bd5\u76f4\u63a5\u641c\u7d22\u6240\u6709a\u6807\u7b7e\u4e2d\u7684\u89c6\u9891\u94fe\u63a5
        if not items:
            video_links = re.findall(r'<a\s+href="(/video/[^"]+\.html)"[^>]*>.*?<img[^>]*src="([^"]+)"[^>]*>.*?<h3[^>]*>([^<]+)</h3>', html, re.DOTALL)
            for match in video_links[:30]:
                vod_id = match[0]
                vod_pic = match[1]
                vod_name = match[2].strip()
                if vod_id and vod_name and not vod_id.startswith("#"):
                    items.append({
                        "vod_id": vod_id,
                        "vod_name": vod_name,
                        "vod_pic": urljoin(self.host, vod_pic),
                        "vod_remarks": ""
                    })
        return {"list": items[:30]}
    def categoryContent(self, tid, pg, filter, extend):
        page = pg or "1"
        base_url = f"{self.host}/video/{tid}"
        params = {}
        if page and page != "1":
            params["page"] = page
        ext = self._parse_extend(extend)
        if ext and ext.get("year"):
            params["year"] = ext["year"]
        url = base_url + ("?" + "&".join([f"{k}={v}" for k, v in params.items()]) if params else "")
        res = self.fetch(url, headers=self.headers)
        if not res or res.status_code != 200:
            return {"list": [], "page": 1, "pagecount": 1, "limit": 20, "total": 0}
        html = res.text
        items = []
        pattern = r'<article class="wu-poster-card"[^>]*>.*?<a class="wu-poster-card__cover" href="([^"]+)">.*?<img[^>]*src="([^"]+)"[^>]*>.*?<h3><a href="[^"]+">([^<]+)</a></h3>.*?<p>([^<]*)</p>.*?<small>([^<]*)</small>'
        matches = re.findall(pattern, html, re.DOTALL)
        for match in matches:
            vod_id = match[0]
            vod_pic = match[1]
            vod_name = match[2].strip()
            vod_type = match[3].strip() if match[3] else ""
            vod_year = match[4].strip() if match[4] else ""
            remark = f"{vod_type} {vod_year}".strip()
            items.append({
                "vod_id": vod_id,
                "vod_name": vod_name,
                "vod_pic": urljoin(self.host, vod_pic),
                "vod_remarks": remark
            })
        pagecount = 1
        page_links = re.findall(r'<a[^>]*href="[^"]*[?&]page=(\d+)"[^>]*>', html)
        if page_links:
            max_page = max([int(x) for x in page_links if x.isdigit()] + [1])
            pagecount = max_page
        next_match = re.search('<a[^>]*href="[^"]*[?&]page=(\\d+)"[^>]*>[^<]*\u4e0b\u4e00\u9875[^<]*</a>', html)
        if next_match and int(next_match.group(1)) > int(page):
            pagecount = max(pagecount, int(next_match.group(1)))
        if not page_links and not next_match:
            pagecount = 1
        return {
            "list": items,
            "page": int(page),
            "pagecount": pagecount,
            "limit": 20,
            "total": len(items) + (int(page) - 1) * 20
        }

    def detailContent(self, ids):
        if not ids:
            return {"list": []}
        vod_id = ids[0]
        url = self.host + vod_id if vod_id.startswith("/") else self.host + "/" + vod_id
        res = self.fetch(url, headers=self.headers)
        if not res or res.status_code != 200:
            return {"list": []}
        html = res.text
        title_match = re.search(r'<h1[^>]*itemprop="name"[^>]*>([^<]+)</h1>', html)
        vod_name = title_match.group(1).strip() if title_match else ""
        pic_match = re.search(r'<a class="wu-detail-poster"[^>]*>.*?<img[^>]*src="([^"]+)"[^>]*>', html, re.DOTALL)
        vod_pic = urljoin(self.host, pic_match.group(1)) if pic_match else ""
        meta_match = re.search(r'<p class="wu-detail-meta">([^<]+)</p>', html)
        vod_remarks = meta_match.group(1).strip() if meta_match else ""
        desc_match = re.search(r'<p class="wu-detail-summary"[^>]*itemprop="description"[^>]*>([^<]+)</p>', html)
        vod_content = desc_match.group(1).strip() if desc_match else ""
        episode_links = []
        ep_pattern = r'<div class="wu-episode-list">.*?<a[^>]*href="([^"]+)"[^>]*>.*?<b>([^<]*)</b>.*?<small>([^<]*)</small>'
        ep_matches = re.findall(ep_pattern, html, re.DOTALL)
        if not ep_matches:
            ep_pattern2 = r'<div class="wu-episode-list">.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
            ep_matches2 = re.findall(ep_pattern2, html, re.DOTALL)
            for match in ep_matches2:
                ep_link = match[0]
                ep_name = match[1].strip()
                if ep_link and ep_name:
                    episode_links.append((ep_name, ep_link))
        else:
            for match in ep_matches:
                ep_link = match[0]
                ep_name = match[1].strip() or match[2].strip()
                if ep_link and ep_name:
                    episode_links.append((ep_name, ep_link))
        if not episode_links:
            play_btn = re.search('<a[^>]*href="([^"]+)"[^>]*>[^<]*\u7acb\u5373\u64ad\u653e[^<]*</a>', html)
            if play_btn:
                play_link = play_btn.group(1)
                if play_link and not play_link.startswith("#"):
                    episode_links.append(("\u64ad\u653e", play_link))
        if episode_links:
            play_url = "$$$".join([f"{name}${link}" for name, link in episode_links])
            play_from = "$$$".join(["\u7ebf\u8def1"] * len(episode_links))
        else:
            play_url = ""
            play_from = ""
        vod = {
            "vod_id": vod_id,
            "vod_name": vod_name or "\u672a\u77e5\u5f71\u7247",
            "vod_pic": vod_pic,
            "vod_remarks": vod_remarks,
            "vod_content": vod_content or vod_name,
            "vod_play_from": play_from,
            "vod_play_url": play_url
        }
        return {"list": [vod]}

    def searchContent(self, key, quick, pg="1"):
        if not key:
            return {"list": [], "page": 1}
        url = f"{self.host}/video/search={key}"
        if pg and pg != "1":
            url += f"&page={pg}"
        res = self.fetch(url, headers=self.headers)
        if not res or res.status_code != 200:
            return {"list": [], "page": 1}
        html = res.text
        items = []
        pattern = r'<article class="wu-poster-card"[^>]*>.*?<a class="wu-poster-card__cover" href="([^"]+)">.*?<img[^>]*src="([^"]+)"[^>]*>.*?<h3><a href="[^"]+">([^<]+)</a></h3>.*?<p>([^<]*)</p>.*?<small>([^<]*)</small>'
        matches = re.findall(pattern, html, re.DOTALL)
        for match in matches:
            vod_id = match[0]
            vod_pic = match[1]
            vod_name = match[2].strip()
            vod_type = match[3].strip() if match[3] else ""
            vod_year = match[4].strip() if match[4] else ""
            remark = f"{vod_type} {vod_year}".strip()
            items.append({
                "vod_id": vod_id,
                "vod_name": vod_name,
                "vod_pic": urljoin(self.host, vod_pic),
                "vod_remarks": remark
            })
        return {"list": items, "page": int(pg) if pg else 1}

    def playerContent(self, flag, id, vipFlags):
        # \u5982\u679c\u5df2\u7ecf\u662fm3u8\u94fe\u63a5\uff0c\u901a\u8fc7\u4ee3\u7406\u8fd4\u56de\uff08\u8fc7\u6ee4\u5e7f\u544a\uff09
        if id.startswith("http") and ".m3u8" in id.lower():
            return {"parse": 0, "url": self._m3u8_proxy_url(id), "header": self.headers}
        if id.startswith("http") and ".mp4" in id.lower():
            return {"parse": 0, "url": id, "header": self.headers}
        # \u64ad\u653e\u9875\u89e3\u6790
        url = self.host + id if id.startswith("/") else self.host + "/" + id
        res = self.fetch(url, headers=self.headers)
        if not res or res.status_code != 200:
            return {"parse": 1, "url": url, "header": self.headers}
        html = res.text
        m3u8_url = None
        # \u4f18\u5148\u4ece data-player-token \u63d0\u53d6
        token_match = re.search(r'data-player-token="([^"]+)"', html)
        if token_match:
            try:
                token = token_match.group(1)
                decoded = base64.b64decode(token).decode('utf-8')
                if decoded.startswith("http"):
                    if "url=" in decoded:
                        url_param = re.search(r'[?&]url=([^&]+)', decoded)
                        if url_param:
                            m3u8_url = unquote(url_param.group(1))
                    elif ".m3u8" in decoded.lower():
                        m3u8_url = decoded
            except:
                pass
        # \u4ece iframe \u63d0\u53d6
        if not m3u8_url:
            iframe_match = re.search(r'<iframe[^>]*src="([^"]+)"[^>]*>', html)
            if iframe_match:
                src = iframe_match.group(1)
                if "url=" in src:
                    url_param = re.search(r'[?&]url=([^&]+)', src)
                    if url_param:
                        m3u8_url = unquote(url_param.group(1))
                elif ".m3u8" in src.lower():
                    m3u8_url = src
        # \u4ece data-video-token \u63d0\u53d6
        if not m3u8_url:
            video_token_match = re.search(r'data-video-token="([^"]+)"', html)
            if video_token_match:
                try:
                    token = video_token_match.group(1)
                    decoded = base64.b64decode(token).decode('utf-8')
                    if ".m3u8" in decoded.lower():
                        m3u8_url = decoded
                except:
                    pass
        # \u5982\u679c\u627e\u5230m3u8\uff0c\u8d70\u4ee3\u7406\u8fc7\u6ee4\u5e7f\u544a
        if m3u8_url and m3u8_url.endswith(".m3u8"):
            return {"parse": 0, "url": self._m3u8_proxy_url(m3u8_url), "header": self.headers}
        # \u76f4\u63a5\u64ad\u653e\u94fe\u63a5
        direct_match = re.search(r'<video[^>]*src="([^"]+)"', html)
        if direct_match:
            video_url = direct_match.group(1)
            if video_url.startswith("http"):
                if ".m3u8" in video_url.lower():
                    return {"parse": 0, "url": self._m3u8_proxy_url(video_url), "header": self.headers}
                return {"parse": 0, "url": video_url, "header": self.headers}
        # \u964d\u7ea7\u5230\u55c5\u63a2
        return {"parse": 1, "url": url, "header": self.headers}
    def localProxy(self, param):
        """m3u8 \u672c\u5730\u4ee3\u7406 + \u5e7f\u544a\u5206\u7247\u8fc7\u6ee4"""
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
        lines = [line.strip() for line in str(text or "").replace("\r", "").split("\n") if line.strip()]
        if not lines:
            return "#EXTM3U\n"
        # \u5904\u7406\u591a\u7801\u7387 m3u8
        if any(line.startswith("#EXT-X-STREAM-INF") for line in lines):
            out = []
            for line in lines:
                if line.startswith("#"):
                    out.append(line)
                else:
                    child = urljoin(source_url, line)
                    if ".m3u8" in child.lower():
                        out.append(self._m3u8_proxy_url(child))
                    else:
                        out.append(child)
            return "\n".join(out) + "\n"
        # \u5355\u7801\u7387 m3u8 - \u8fc7\u6ee4\u5e7f\u544a\u5206\u7247
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
                # \u5e7f\u544a\u8fc7\u6ee4\uff1a\u5305\u542b ad\u3001banner\u3001advert \u7b49\u5173\u952e\u8bcd\u7684\u5206\u7247
                if self._is_ad_segment(media) or (content_root and content_root not in urlparse(media).path):
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
            self.log("m3u8\u5df2\u8fc7\u6ee4\u5e7f\u544a\u5206\u7247: %d" % removed)
        return "\n".join(out) + "\n"

    def _is_ad_segment(self, url):
        """\u5224\u65ad\u662f\u5426\u4e3a\u5e7f\u544a\u5206\u7247"""
        ad_keywords = [
            "ad", "banner", "advert", "advertisement", "promo", 
            "sponsor", "campaign", "marketing", "promotion",
            "ads", "ad_", "-ad-", "_ad_", ".ad.", "-promo-",
            "guanggao", "gg_", "_gg"
        ]
        url_lower = url.lower()
        for kw in ad_keywords:
            if kw in url_lower:
                return True
        return False

    def _rewrite_m3u8_tag(self, line, source_url):
        """\u91cd\u5199 m3u8 \u6807\u7b7e\u4e2d\u7684 URI\uff08\u8865\u5168\u7edd\u5bf9\u5730\u5740\uff09"""
        if line.startswith("#EXT-X-KEY") or line.startswith("#EXT-X-MAP"):
            def repl(match):
                return 'URI="' + urljoin(source_url, match.group(1)) + '"'
            return re.sub(r'URI="([^"]+)"', repl, line)
        if line and not line.startswith("#"):
            return urljoin(source_url, line)
        return line

    def _m3u8_proxy_url(self, url):
        """\u751f\u6210 m3u8 \u4ee3\u7406\u5730\u5740"""
        return self.getProxyUrl() + "&url=" + quote(str(url or ""), safe="")

    def _parse_extend(self, extend):
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
            clean = extend.strip()
            if clean.startswith("{") and clean.endswith("}"):
                clean = clean[1:-1]
            for part in clean.split(','):
                if '=' in part:
                    k, v = part.split('=', 1)
                    result[k.strip()] = v.strip()
            return result
        return {}