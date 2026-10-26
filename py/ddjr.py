# coding: utf-8
# ============================================================
# \u7ad9\u70b9: \u5927\u5c4cv\u5de8\u4e73 (MacCMS)
# \u4e3b\u57df\u540d: https://pfgzyhx2z.817020.xyz
# \u53d1\u5e03\u9875: 817010.xyz
# \u5185\u5bb9\u7c7b\u578b: \u6210\u4eba\u5f71\u89c6\uff08\u89c6\u9891\uff09
# \u7279\u6b8a\u8bf4\u660e: \u5168\u7ad9\u9875\u9762\u4e3a base64(atob) + \u6570\u5b57\u6570\u7ec4\u53cc\u91cd\u7f16\u7801\uff0c\u987b\u5728\u811a\u672c\u5185\u89e3\u7801
# \u6765\u6e90: \u624b\u52a8\u9006\u5411 + m3u8_analyzer \u53d6\u8bc1
# \u6700\u540e\u9a8c\u8bc1: 2026-09-12
# ============================================================
import json
import base64
import ast
import re
from urllib.parse import quote, urljoin, unquote, urlparse
import posixpath

from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    def __init__(self):
        # __init__ \u53ea\u505a\u672c\u5730\u521d\u59cb\u5316\uff0c\u96f6\u7f51\u7edc
        self.extend = ""
        self.host = "https://pfgzyhx2z.817020.xyz"
        self.classes = [
            {"type_id": "3", "type_name": "\u56fd\u4ea7\u89c6\u9891"},
            {"type_id": "7", "type_name": "\u65e5\u672c\u6709\u7801"},
            {"type_id": "8", "type_name": "\u5176\u4ed6\u53e3\u5473"},
            {"type_id": "1", "type_name": "\u65e5\u672c\u65e0\u7801"},
            {"type_id": "2", "type_name": "\u6b27\u7f8e\u89c6\u9891"},
            {"type_id": "4", "type_name": "\u52a8\u6f2b\u8089\u756a"},
            {"type_id": "5", "type_name": "\u4f26\u7406\u4e09\u7ea7"},
        ]
        # \u7ad9\u70b9\u65e0\u771f\u5b9e\u7b5b\u9009 DOM/API\uff0c\u4e0d\u4f2a\u9020\u7b5b\u9009
        self.filters = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
            "Referer": self.host + "/",
        }
        # m3u8_analyzer \u53d6\u8bc1\u7ed3\u8bba\uff1a\u5b58\u5728\u5e7f\u544a\u76ee\u5f55 /20260830/... \uff0c\u9700\u6e05\u6d17
        self.NEED_CLEAN = True
        self.ANCHOR = "/20260910/uVXsfAuw/2000kb/hls/"
        self.AD_DIRS = ["/20260830/i2vAQKIt/1000kb/hls/"]

    def getName(self):
        return "\u5927\u5c4cv\u5de8\u4e73"

    def getDependence(self):
        return []

    def init(self, extend=""):
        self.extend = extend or ""

    # ---------------- \u7f16\u7801\u89e3\u7801 ----------------
    def _decode_page(self, raw):
        """\u5168\u7ad9\u53cc\u91cd\u7f16\u7801: base64(atob) -> \u6570\u5b57\u6570\u7ec4 -> bytes -> html"""
        if not raw:
            return ""
        try:
            m = re.search(r'atob\("([^"]+)"\)', raw)
            if not m:
                return raw
            stage1 = base64.b64decode(m.group(1)).decode("utf-8", errors="ignore")
            try:
                arr = ast.literal_eval(stage1.strip())
                return bytes(arr).decode("utf-8", errors="ignore")
            except Exception:
                return stage1
        except Exception as e:
            self.log({"action": "decode_fail", "error": str(e)})
            return raw

    def _fetch_html(self, url, post_data=None):
        try:
            if post_data is not None:
                r = self.post(url, data=post_data, headers=self.headers, timeout=20)
            else:
                r = self.fetch(url, headers=self.headers, timeout=20)
            if not r or r.status_code != 200:
                return ""
            raw = r.text if hasattr(r, "text") else ""
            return self._decode_page(raw)
        except Exception as e:
            self.log({"action": "fetch_fail", "url": url, "error": str(e)})
            return ""

    # ---------------- \u9996\u9875 ----------------
    def homeContent(self, filter):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def homeVideoContent(self):
        html = self._fetch_html(self.host + "/")
        return {"list": self._parse_list(html)}

    # ---------------- \u5206\u7c7b ----------------
    def categoryContent(self, tid, pg, filter, extend):
        page = str(pg or "1")
        if page == "1":
            url = f"{self.host}/vodtype/{tid}.html"
        else:
            url = f"{self.host}/vodtype/{tid}-{page}.html"
        html = self._fetch_html(url)
        vlist = self._parse_list(html)
        # \u5c3e\u9875\u5b9e\u6d4b 18160 \u9875\uff0c\u53d6\u4e00\u4e2a\u4fdd\u5b88\u7684\u8f83\u5927\u503c
        return {
            "list": vlist,
            "page": int(page) if page.isdigit() else 1,
            "pagecount": 18160,
            "limit": 20,
            "total": 999999,
        }

    # ---------------- \u641c\u7d22 ----------------
    def searchContent(self, key, quick, pg="1"):
        # POST /vod/search.html  wd=\u5173\u952e\u8bcd
        data = "wd=" + quote(key or "")
        html = self._fetch_html(self.host + "/vod/search.html", post_data=data)
        # \u65e0\u7ed3\u679c\u9875\u8fc7\u6ee4
        if html and re.search("\u6ca1\u6709\u627e\u5230|\u6682\u65e0\u6570\u636e|\u6ca1\u6709\u627e\u5230\u60a8\u60f3\u8981\u7684\u7ed3\u679c", html):
            return {"list": [], "page": int(pg) if str(pg).isdigit() else 1}
        return {"list": self._parse_list(html), "page": int(pg) if str(pg).isdigit() else 1}

    # ---------------- \u8be6\u60c5 ----------------
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
            "vod_id": vid, "vod_name": title or "\u672a\u77e5\u6807\u9898", "vod_pic": pic or "",
            "vod_remarks": remarks, "vod_content": "",
            "vod_play_from": "\u64ad\u653e", "vod_play_url": "\u64ad\u653e$" + pid,
        }]}

    def detailContent(self, ids):
        raw = self._norm_ids(ids)
        if not raw:
            return {"list": []}
        vid = raw.split("|$|")[0]
        try:
            html = self._fetch_html(f"{self.host}/voddetail/{vid}.html")
            if not html or len(html) < 500:
                return self._skeleton(vid, remarks="\u8be6\u60c5\u52a0\u8f7d\u5931\u8d25")

            title = ""
            m = re.search(r'<h1[^>]*class="movie-title"[^>]*>(.*?)</h1>', html, re.S)
            if m:
                title = self._clean_text(m.group(1))
            if not title:
                m = re.search(r"<title>(.*?)</title>", html, re.S)
                if m:
                    title = self._clean_text(m.group(1)).split("--")[-1]
            if not title:
                m = re.search(r'property="og:title"[^>]*content="([^"]*)"', html)
                if m:
                    title = self._clean_text(m.group(1))

            pic = ""
            m = re.search(r'<img[^>]+src="([^"]+)"[^>]*class="vod-cover"', html)
            if not m:
                m = re.search(r'class="vod-cover"[^>]*src="([^"]+)"', html)
            if not m:
                m = re.search(r'property="og:image"[^>]*content="([^"]*)"', html)
            if m:
                pic = m.group(1)

            # \u64ad\u653e\u9875\u5165\u53e3: /vodplay/{vid}-1-1.html
            play_page = ""
            m = re.search(r'href="(/vodplay/%s[^"]*)"' % re.escape(vid), html)
            if m:
                play_page = m.group(1)
            if not play_page:
                m = re.search(r'href="(/vodplay/[^"]+)"', html)
                if m:
                    play_page = m.group(1)

            vod = {
                "vod_id": raw,
                "vod_name": title or "\u89c6\u9891",
                "vod_pic": pic,
                "vod_remarks": "",
                "vod_content": title or "",
                "vod_play_from": "\u64ad\u653e",
                "vod_play_url": "\u64ad\u653e$" + (play_page or f"/vodplay/{vid}-1-1.html"),
            }
            return {"list": [vod]}
        except Exception as e:
            self.log({"detail": "exception", "error": str(e)})
            return self._skeleton(vid)

    @staticmethod
    def _clean_text(s):
        s = re.sub(r"<[^>]+>", "", s or "")
        s = s.replace("&nbsp;", " ").replace("&amp;", "&").strip()
        return s

    # ---------------- \u64ad\u653e ----------------
    def playerContent(self, flag, id, vipFlags):
        play_url = str(id or "").strip()
        if play_url and "$" in play_url:
            play_url = play_url.split("$", 1)[-1]
        if play_url.startswith("http") and ".m3u8" in play_url.lower():
            if self.NEED_CLEAN:
                return {"parse": 0, "url": self._m3u8_proxy_url(play_url),
                        "header": {"User-Agent": self.headers["User-Agent"]}}
            return {"parse": 0, "url": play_url,
                    "header": {"User-Agent": self.headers["User-Agent"]}}

        # \u7ad9\u5185\u64ad\u653e\u9875\uff1a\u89e3\u6790 mark#bfz data-user-name="\u7b2c1\u96c6$http.../index.m3u8"
        page_url = play_url
        if page_url and not page_url.startswith("http"):
            page_url = urljoin(self.host + "/", page_url.lstrip("/"))
        m3u8 = ""
        if page_url:
            html = self._fetch_html(page_url)
            if html:
                m = re.search(r'data-user-name="[^"$]*\$(https?://[^"]+\.m3u8[^"]*)"', html)
                if not m:
                    m = re.search(r'(https?://[^"\'\s]+\.m3u8[^"\'\s]*)', html)
                if m:
                    m3u8 = m.group(1)

        if m3u8:
            if self.NEED_CLEAN:
                return {"parse": 0, "url": self._m3u8_proxy_url(m3u8),
                        "header": {"User-Agent": self.headers["User-Agent"]}}
            return {"parse": 0, "url": m3u8,
                    "header": {"User-Agent": self.headers["User-Agent"]}}

        # \u964d\u7ea7\uff1aurl \u7981\u6b62\u4e3a\u7a7a
        return {"parse": 1, "url": page_url or self.host,
                "header": {"User-Agent": self.headers["User-Agent"], "Referer": self.host + "/"}}

    def _m3u8_proxy_url(self, url):
        if url:
            url = url.replace("\\/", "/")
        base = self.getProxyUrl()
        # getProxyUrl() \u901a\u5e38\u5df2\u542b "?do=py"\uff0c\u53ea\u9700\u8ffd\u52a0 url \u53c2\u6570
        sep = "&" if "?" in base else "?do=py&"
        if base.rstrip().endswith("do=py"):
            return base + "&url=" + quote(str(url or ""), safe="")
        if "?" in base:
            return base + "&url=" + quote(str(url or ""), safe="")
        return base + "?do=py&url=" + quote(str(url or ""), safe="")
    IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")
    VIDEO_EXT = (".ts", ".m4s", ".mp4", ".aac", ".m4a")

    def _is_fake_image_stream(self, text):
        has_video = False
        has_image = False
        for line in str(text or "").split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            path = line.split("?")[0].split("#")[0].lower()
            if path.endswith(self.VIDEO_EXT):
                has_video = True
            elif path.endswith(self.IMAGE_EXT):
                has_image = True
        return has_image and not has_video

    def _rewrite_m3u8_tag(self, line, source_url):
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

    def _resolve_main_dir(self, lines, source_url, is_image_stream=False):
        base_dir = posixpath.dirname(urlparse(source_url).path)
        if not base_dir.endswith("/"):
            base_dir += "/"
        if is_image_stream:
            counter = {}
            for line in lines:
                if not line or line.startswith("#"):
                    continue
                p = urlparse(urljoin(source_url, line)).path
                d = posixpath.dirname(p)
                if d and d != "/":
                    counter[d + "/"] = counter.get(d + "/", 0) + 1
            if counter:
                return max(counter.items(), key=lambda kv: kv[1])[0]
            return base_dir
        for line in lines:
            if not line.startswith("#EXT-X-KEY") or "URI=" not in line:
                continue
            m = re.search(r'URI="([^"]+)"', line)
            if not m:
                continue
            key_uri = m.group(1)
            key_path = urlparse(key_uri if key_uri.startswith("http")
                                else urljoin(source_url, key_uri)).path
            key_dir = posixpath.dirname(key_path)
            if key_dir and key_dir != "/":
                return key_dir + "/"
        return base_dir

    def _filter_segments(self, lines, source_url, main_dir):
        segments, pending = [], []
        removed = kept = 0
        for line in lines:
            if line.startswith("#EXTINF"):
                pending = [line]
                continue
            if pending and line.startswith("#"):
                pending.append(line)
                continue
            if pending:
                media_url = urljoin(source_url, line)
                media_path = urlparse(media_url).path
                if media_path.startswith(main_dir):
                    segments.extend(pending)
                    segments.append(media_url)
                    kept += 1
                else:
                    removed += 1
                pending = []
                continue
            if line.startswith("#"):
                segments.append(line)
            else:
                segments.append(urljoin(source_url, line))
        return segments, removed, kept

    def _dedup_tags(self, segments, source_url):
        NOISE = ("#EXT-X-DISCONTINUITY", "#EXT-X-KEY:METHOD=NONE")
        out = []
        for line in segments:
            line = self._rewrite_m3u8_tag(line, source_url)
            if line in NOISE:
                if not out or out[-1] in NOISE:
                    continue
            out.append(line)
        while len(out) > 1 and out[-1] in NOISE:
            out.pop()
        return out

    def _clean_m3u8_multi(self, lines, source_url):
        out = []
        for line in lines:
            if line.startswith("#"):
                out.append(line)
                continue
            child = urljoin(source_url, line)
            if ".m3u8" in child.lower():
                out.append(self._m3u8_proxy_url(child))
            else:
                out.append(child)
        return "\n".join(out) + "\n"

    def _clean_m3u8(self, text, source_url):
        lines = [l.strip() for l in str(text or "").replace("\r", "").split("\n") if l.strip()]
        if not lines:
            return "#EXTM3U\n"
        is_img = self._is_fake_image_stream(text)
        if is_img:
            self.log({"stage": "clean", "fake_image_stream": True})
        # \u7b2c2\u5c42\uff1a\u591a\u7801\u7387
        if any(l.startswith("#EXT-X-STREAM-INF") for l in lines):
            return self._clean_m3u8_multi(lines, source_url)
        # \u7b2c3\u5c42\uff1a\u951a\u70b9
        main_dir = self._resolve_main_dir(lines, source_url, is_image_stream=is_img)
        # \u7b2c4\u5c42\uff1a\u8fc7\u6ee4
        segments, removed, kept = self._filter_segments(lines, source_url, main_dir)
        # \u7b2c5\u5c42\uff1a\u5168\u6ee4\u515c\u5e95
        if removed > 0 and (kept == 0 or removed > kept):
            self.log({"stage": "clean", "fallback": "no_filter",
                      "removed": removed, "kept": kept, "anchor": main_dir})
            out = [self._rewrite_m3u8_tag(l, source_url) for l in lines]
            return "\n".join(out) + "\n"
        if removed:
            self.log({"stage": "clean", "removed": removed,
                      "kept": kept, "anchor": main_dir})
        out = self._dedup_tags(segments, source_url)
        return "\n".join(out) + "\n"

    def localProxy(self, param):
        try:
            if isinstance(param, dict):
                target = param.get("url", "") or param.get("source", "")
            else:
                target = str(param or "")
            if target.startswith("url="):
                target = target[4:]
            elif "url=" in target:
                qs = urlparse(target).query
                import urllib.parse as _up
                q = _up.parse_qs(qs)
                if "url" in q:
                    target = q["url"][0]
            target = unquote(str(target or ""))
            if not target or not re.match(r"^https?://", target, re.I):
                return [400, "text/plain", b"invalid url"]

            resp = self.fetch(target, headers={"User-Agent": self.headers["User-Agent"]}, timeout=20)
            if not resp or resp.status_code != 200:
                return [502, "text/plain", b"fetch failed"]
            content = getattr(resp, "content", b"") or b""
            if not content and getattr(resp, "text", ""):
                content = resp.text.encode("utf-8", errors="ignore")
            if not content:
                return [502, "text/plain", b"empty content"]
            if b"#EXTM3U" in content[:256]:
                cleaned = self._clean_m3u8(content.decode("utf-8", errors="ignore"), target)
                return [200, "application/vnd.apple.mpegurl", cleaned.encode("utf-8")]
            return [200, "application/octet-stream", content]
        except Exception as e:
            return [500, "text/plain", ("localProxy error: " + str(e)).encode("utf-8", errors="ignore")]

    # ---------------- \u89e3\u6790\u5217\u8868 ----------------
    def _parse_list(self, html):
        items = []
        if not html:
            return items
        # \u4ee5 box-item \u4e3a\u5757\u5207\u5206
        blocks = re.findall(r'<div class="box-item">(.*?)</div>\s*</div>', html, re.S)
        if not blocks:
            blocks = re.split(r'<div class="box-item">', html)[1:]
        seen = set()
        for b in blocks:
            m = re.search(r'href="(/voddetail/(\d+)\.html)"', b)
            if not m:
                continue
            vid = m.group(2)
            if vid in seen:
                continue
            seen.add(vid)
            nm = re.search(r'title="([^"]*)"', b)
            name = nm.group(1) if nm else ""
            if not name:
                nm = re.search(r'class="movie-name"[^>]*>([^<]*)<', b)
                name = nm.group(1) if nm else ""
            pic = ""
            pm = re.search(r'<img[^>]+src="([^"]+)"', b)
            if pm:
                pic = pm.group(1)
            remark = ""
            rm = re.search(r'<span>([^<]*)</span>', b)
            if rm:
                remark = rm.group(1)
            items.append({
                "vod_id": vid,
                "vod_name": self._clean_text(name),
                "vod_pic": pic,
                "vod_remarks": remark,
            })
        return items

    # ---------------- \u63a8\u8350 ----------------
    def recommendContent(self, ids, pg):
        """\u76f8\u5173\u63a8\u8350\uff08\u5b98\u65b9\u6a21\u5f0f3\uff1a\u5206\u7c7b/\u5173\u952e\u8bcd\u641c\u7d22 + \u70ed\u95e8\u515c\u5e95\uff09"""
        try:
            raw = self._norm_ids(ids)
            m0 = re.search(r"(\d{3,})", raw)
            vid = m0.group(1) if m0 else ""
            self.log({"recommend": "input", "raw": raw, "vid": vid})
            if not vid:
                return {"list": []}
            page = str(max(1, int(pg or 1)))
            # 1. \u8be6\u60c5\u9875\u53d6\u6807\u9898
            html = self._fetch_html(f"{self.host}/voddetail/{vid}.html")
            title = ""
            if html:
                m = re.search(r'<h1[^>]*class="movie-title"[^>]*>(.*?)</h1>', html, re.S)
                if m:
                    title = self._clean_text(m.group(1))
            self.log({"recommend": "title", "title": title})
            videos = []
            seen = set()
            # 2. \u5173\u952e\u8bcd\uff1a\u756a\u53f7\u4f18\u5148\uff0c\u5426\u5219\u524d4\u5b57
            kw = ""
            if title:
                m = re.search(r"([A-Za-z]+-\d+)", title)
                if m:
                    kw = m.group(1)
                if not kw:
                    kw = re.sub(r"[^\w\u4e00-\u9fff]", "", title)[:4]
            # 3. \u5173\u952e\u5b57\u641c\u7d22
            if kw:
                data = "wd=" + quote(kw)
                shtml = self._fetch_html(self.host + "/vod/search.html", post_data=data)
                for x in self._parse_list(shtml):
                    if x["vod_id"] != vid and x["vod_id"] not in seen:
                        seen.add(x["vod_id"]); videos.append(x)
            # 4. \u515c\u5e95\uff1a\u6700\u65b0\u5217\u8868\uff08\u9996\u9875\uff09\u8865\u4f4d
            if len(videos) < 12:
                hhtml = self._fetch_html(self.host + "/")
                for x in self._parse_list(hhtml):
                    if x["vod_id"] != vid and x["vod_id"] not in seen:
                        seen.add(x["vod_id"]); videos.append(x)
                        if len(videos) >= 12:
                            break
            self.log({"recommend": "result", "count": len(videos), "kw": kw})
            return {"list": videos[:12]}
        except Exception as e:
            self.log({"recommend": "exception", "error": str(e)})
            return {"list": []}
    def destroy(self):
        pass