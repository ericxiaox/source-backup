# coding: utf-8
# ============================================================
# \u7ad9\u70b9: JavKok (javkok.com)
# \u7c7b\u578b: Laravel + Alpine.js \u670d\u52a1\u7aef\u6e32\u67d3 HTML \u7ad9
# \u4e3b\u57df: https://javkok.com
# \u5185\u5bb9: \u65e5\u672c AV \u5f71\u89c6
# \u8def\u7531:
#   \u5206\u7c7b: /{slug}?page={n}   (new/release/uncensored-leak/chinese_subtitle/today/weekly/monthly ...)
#   \u5217\u8868\u5361\u7247: div.video-card  a[href] -> /{slug}
#   \u8be6\u60c5: /{slug}   \u5185\u5d4c data-video-id="148"
#   \u64ad\u653e: POST /api/play/{video_id}  -> {status:ok, d:base64}
#         base64 \u89e3\u540e XOR(key=jk_v2_x9Qm4pL7) -> JSON [{url,vtt}]
#   \u641c\u7d22: GET /search?keyword={kw}
# \u9006\u5411: /js/video-player.js?v=3 \u5185 fetchSources + _d() XOR
# \u6700\u540e\u9a8c\u8bc1: 2026-09-21
# ============================================================
import json
import base64
import re
from urllib.parse import quote, urljoin, unquote, urlparse

from base.spider import Spider as BaseSpider


class Spider(BaseSpider):

    XOR_KEY = [106, 107, 95, 118, 50, 95, 120, 57, 81, 109, 52, 112, 76, 55]  # "jk_v2_x9Qm4pL7"

    def __init__(self):
        self.host = "https://javkok.com"
        self.extend = ""
        self.session_cookie = ""
        self.csrf_token = ""
        self.warmed = False

        # \u5206\u7c7b\u9759\u6001\u786c\u7f16\u7801\uff08\u6cd5\u521916/17\uff0c\u96f6\u7f51\u7edc\uff09
        self.classes = [
            {"type_id": "new", "type_name": "\u6700\u8fd1\u66f4\u65b0"},
            {"type_id": "release", "type_name": "\u65b0\u4f5c\u4e0a\u5e02"},
            {"type_id": "uncensored-leak", "type_name": "\u7121\u78bc\u6d41\u51fa"},
            {"type_id": "chinese_subtitle", "type_name": "\u4e2d\u6587\u5b57\u5e55"},
            {"type_id": "today", "type_name": "\u4eca\u65e5\u71b1\u9580"},
            {"type_id": "weekly", "type_name": "\u672c\u9031\u71b1\u9580"},
            {"type_id": "monthly", "type_name": "\u672c\u6708\u71b1\u9580"},
            {"type_id": "actresses", "type_name": "\u5973\u512a\u4e00\u89bd"},
            {"type_id": "genres", "type_name": "\u985e\u578b"},
            {"type_id": "makers", "type_name": "\u767c\u884c\u5546"},
        ]
        self.filters = {}

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        }

    # ---------------- \u57fa\u7840 ----------------

    def getName(self):
        return "JavKok"

    def getDependence(self):
        return []

    def init(self, extend=""):
        # \u96f6\u7f51\u7edc
        self.extend = extend or ""

    def destroy(self):
        pass

    def _hdrs(self, referer=None, extra=None):
        h = dict(self.headers)
        h["Referer"] = referer or (self.host + "/")
        if extra:
            h.update(extra)
        return h

    # ---------------- \u9996\u9875/\u5206\u7c7b ----------------

    def homeContent(self, filter):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def homeVideoContent(self):
        return {"list": self._fetch_list(self.host + "/new")}

    def categoryContent(self, tid, pg, filter, extend):
        pg = str(pg or "1")
        base = "%s/%s" % (self.host, tid)
        if pg and pg != "1":
            url = "%s?page=%s" % (base, pg)
        else:
            url = base
        lst = self._fetch_list(url)
        # \u603b\u9875\u6570\uff1a\u4ece\u5206\u9875\u5668\u63d0\u53d6\uff08\u7ad9\u70b9\u6309\u9875\u663e\u793a\uff09
        pagecount = self._parse_pagecount(url, pg)
        return {
            "list": lst,
            "page": int(pg) if pg.isdigit() else 1,
            "pagecount": pagecount,
            "limit": 20,
            "total": pagecount * 20,
        }

    def _parse_pagecount(self, url, pg):
        try:
            r = self.fetch(url, headers=self._hdrs(), timeout=15)
            if not r or r.status_code != 200:
                return 9999
            html = r.text or ""
            idx = html.find("site-pagination")
            if idx == -1:
                return 1
            seg = html[idx:idx + 6000]
            nums = [int(n) for n in re.findall(r'[?&]page=(\d+)', seg)]
            has_next = bool(re.search(r'data-next-url="[^"]+"', seg))
            cur = int(pg) if str(pg).isdigit() else 1
            if nums:
                mx = max(nums)
                return mx + 1 if has_next else mx
            return 9999 if has_next else cur
        except Exception:
            return 9999
    def _fetch_list(self, url):
        try:
            r = self.fetch(url, headers=self._hdrs(), timeout=15)
            if not r or r.status_code != 200:
                self.log({"action": "list_fail", "url": url, "status": getattr(r, "status_code", None)})
                return []
            return self._parse_cards(r.text or "")
        except Exception as e:
            self.log({"action": "list_exc", "url": url, "error": type(e).__name__})
            return []

    def _parse_cards(self, html):
        items = []
        seen = set()
        # \u5b9a\u4f4d\u5361\u7247\u5757
        blocks = re.split(r'class="thumbnail group video-card"', html)
        for blk in blocks[1:]:
            blk = blk[:2500]
            # \u94fe\u63a5
            m = re.search(r'<a\s+href="(https?://[^"]+)"\s+title="([^"]*)"', blk)
            if not m:
                continue
            href = m.group(1)
            code = m.group(2).strip()
            # \u53ea\u53d6\u8be6\u60c5 slug \u94fe\u63a5\uff08\u5f62\u5982 host/slug\uff0c\u65e0\u591a\u7ea7\u8def\u5f84\uff09
            try:
                p = urlparse(href).path.strip("/")
            except Exception:
                continue
            if not p or "/" in p:
                continue
            slug = p
            if slug in seen:
                continue
            seen.add(slug)
            # \u6807\u9898
            tm = re.search(r'title="[^"]*"\s*>\s*([^<]{2,})</a>', blk)
            name = ""
            if tm:
                name = self._clean(tm.group(1))
            if not name:
                im = re.search(r'alt="([^"]+)"', blk)
                if im:
                    name = self._clean(im.group(1))
            if not name:
                name = code
            # \u5c01\u9762
            pic = ""
            pm = re.search(r'<img[^>]+src="(https?://[^"]+)"', blk)
            if pm:
                pic = pm.group(1)
            # \u65f6\u957f\u89d2\u6807
            rem = ""
            rm = re.search(r'>(\d{1,2}:\d{2}:\d{2})<', blk)
            if rm:
                rem = rm.group(1)
            items.append({
                "vod_id": slug,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": rem,
            })
        return items

    @staticmethod
    def _clean(s):
        return re.sub(r"\s+", " ", str(s or "")).strip()

    # ---------------- \u641c\u7d22 ----------------

    def searchContent(self, key, quick, pg="1"):
        try:
            url = "%s/search?keyword=%s" % (self.host, quote(str(key or ""), safe=""))
            r = self.fetch(url, headers=self._hdrs(), timeout=15)
            if not r or r.status_code != 200:
                return {"list": [], "page": 1}
            return {"list": self._parse_cards(r.text or ""), "page": int(pg) if str(pg).isdigit() else 1}
        except Exception:
            return {"list": [], "page": 1}

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

    def _skeleton(self, vid, title="", pic="", remarks=""):
        return {"list": [{
            "vod_id": vid, "vod_name": title or "\u672a\u77e5\u6807\u9898", "vod_pic": pic or "",
            "vod_remarks": remarks, "vod_content": "",
            "vod_play_from": "\u64ad\u653e", "vod_play_url": "\u64ad\u653e$" + str(vid),
        }]}

    def detailContent(self, ids):
        raw = self._norm_ids(ids)
        if not raw:
            return {"list": []}
        slug = raw.split("|")[0]
        # \u5df2\u5c01\u88c5 video_id
        vid = ""
        if "|" in raw:
            vid = raw.split("|", 1)[1]
        try:
            url = "%s/%s" % (self.host, slug)
            r = self.fetch(url, headers=self._hdrs(), timeout=15)
            if not r or r.status_code != 200 or len(r.text or "") < 500:
                return self._skeleton(raw)
            html = r.text or ""

            # \u6807\u9898
            name = ""
            hm = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
            if hm:
                inner = hm.group(1)
                spans = re.findall(r'<span[^>]*>([^<]*)</span>', inner)
                name = self._clean(" ".join(spans)) if spans else self._clean(re.sub(r"<[^>]+>", "", inner))
            if not name:
                tm = re.search(r"<title>([^<]+)</title>", html)
                if tm:
                    name = self._clean(tm.group(1).split("|")[0])
            if not name:
                name = slug

            # \u5c01\u9762
            pic = ""
            pm = re.search(r'poster="(https?://[^"]+)"', html)
            if pm:
                pic = pm.group(1)
            if not pic:
                pm2 = re.search(r'<img[^>]+src="(https?://images-cdn[^"]+)"', html)
                if pm2:
                    pic = pm2.group(1)

            # video_id
            if not vid:
                vm = re.search(r'data-video-id="(\d+)"', html)
                if vm:
                    vid = vm.group(1)

            # \u7b80\u4ecb / \u6f14\u5458
            content = ""
            cm = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
            if cm:
                content = self._clean(cm.group(1))

            # \u64ad\u653eID \u5c01\u88c5 slug|video_id
            play_id = slug if not vid else "%s|%s" % (slug, vid)
            vod = {
                "vod_id": raw,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": "",
                "vod_actor": "",
                "vod_director": "",
                "vod_content": content,
                "vod_play_from": "\u64ad\u653e",
                "vod_play_url": "\u64ad\u653e$" + play_id,
            }
            return {"list": [vod]}
        except Exception as e:
            self.log({"action": "detail_exc", "ids": raw, "error": type(e).__name__})
            return self._skeleton(raw)

    # ---------------- \u64ad\u653e ----------------

    def _xor_decode(self, b64):
        raw = base64.b64decode(b64)
        k = self.XOR_KEY
        out = "".join(chr(raw[i] ^ k[i % len(k)]) for i in range(len(raw)))
        return json.loads(out)

    def _get_sources(self, video_id):
        """POST /api/play/{id} \u62ff m3u8 \u76f4\u94fe"""
        try:
            url = "%s/api/play/%s" % (self.host, str(video_id).strip())
            # Laravel \u9632\u62a4\uff1a\u9700\u540c\u4e00 session + X-CSRF-TOKEN + XHR \u5934
            self._warmup()
            h = {
                "User-Agent": self.headers["User-Agent"],
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": self.host + "/",
                "Origin": self.host,
            }
            if self.csrf_token:
                h["X-CSRF-TOKEN"] = self.csrf_token
            if self.session_cookie:
                h["Cookie"] = self.session_cookie
            r = self.post(url, headers=h, timeout=15)
            if not r or r.status_code != 200:
                return []
            data = json.loads(r.text or "{}")
            if data.get("status") != "ok" or not data.get("d"):
                return []
            src = self._xor_decode(data["d"])
            return src if isinstance(src, list) else []
        except Exception as e:
            self.log({"action": "play_api_exc", "error": type(e).__name__})
            return []

    def _warmup(self):
        """\u83b7\u53d6 session cookie + csrf\uff08\u4e00\u6b21\u5373\u53ef\uff09"""
        if self.warmed and self.session_cookie:
            return
        try:
            r = self.fetch(self.host + "/", headers=self._hdrs(), timeout=15)
            if r and r.status_code == 200:
                html = r.text or ""
                m = re.search(r'csrf-token"\s+content="([^"]+)"', html)
                if m:
                    self.csrf_token = m.group(1)
                # \u4ece\u54cd\u5e94\u5934\u62ff set-cookie
                try:
                    sc = r.headers.get("Set-Cookie") or r.headers.get("set-cookie") or ""
                    if sc:
                        self.session_cookie = sc.split(";")[0]
                except Exception:
                    pass
                self.warmed = True
        except Exception:
            pass

    def playerContent(self, flag, id, vipFlags):
        play_url = str(id) if id else ""
        if "$" in play_url:
            play_url = play_url.split("$", 1)[1]
        video_id = play_url.split("|", 1)[1] if "|" in play_url else ""
        if not video_id:
            slug = play_url.split("|")[0]
            try:
                r = self.fetch("%s/%s" % (self.host, slug), headers=self._hdrs(), timeout=15)
                if r and r.status_code == 200:
                    vm = re.search(r'data-video-id="(\d+)"', r.text or "")
                    if vm:
                        video_id = vm.group(1)
            except Exception:
                pass
        if not video_id:
            slug = play_url.split("|")[0]
            return {"parse": 1, "url": "%s/%s" % (self.host, slug),
                    "header": {"User-Agent": self.headers["User-Agent"], "Referer": self.host + "/"}}
        srcs = self._get_sources(video_id)
        if srcs:
            m3u8 = srcs[0].get("url", "")
            if m3u8:
                # \u76f4\u8fde\u65b9\u6848\uff08MPV/IJK \u517c\u5bb9\u6700\u4f73\uff0c\u52ff\u5957\u4ee3\u7406\uff09\uff1a
                # \u8fd4\u56de\u5b50\u6d41\u7edd\u5bf9\u5730\u5740 + Referer\uff0c\u64ad\u653e\u5668\u900f\u4f20 header \u76f4\u8fde CDN\u3002
                sub = self._sub_stream_url(m3u8)
                hdr = {
                    "User-Agent": self.headers["User-Agent"],
                    "Referer": self.host + "/",
                    "Accept": "*/*",
                }
                return {"parse": 0, "url": sub, "header": hdr}
        slug = play_url.split("|")[0]
        return {"parse": 1, "url": "%s/%s" % (self.host, slug),
                "header": {"User-Agent": self.headers["User-Agent"], "Referer": self.host + "/"}}
    def _sub_stream_url(self, master_url):
        """\u4ece\u4e3b\u8868\u53d6\u7b2c\u4e00\u6761\u5b50\u6d41\uff0c\u62fc\u6210\u7edd\u5bf9\u5730\u5740\uff1b\u5931\u8d25\u5219\u8fd4\u56de\u539f\u5730\u5740\u3002"""
        try:
            r = self.fetch(master_url, headers={"User-Agent": self.headers["User-Agent"],
                                                "Referer": self.host + "/"}, timeout=15)
            if r and r.status_code == 200 and "#EXTM3U" in (r.text or ""):
                base = master_url.rsplit("/", 1)[0] + "/"
                for line in (r.text or "").replace("\r", "").split("\n"):
                    s = line.strip()
                    if s and not s.startswith("#"):
                        return urljoin(base, s)
        except Exception:
            pass
        return master_url
    def localProxy(self, param):
        try:
            target = unquote(str((param or {}).get("url", "") or ""))
            if not re.match(r"^https?://", target, re.I):
                return [400, "text/plain", b"invalid url"]
            media_headers = {
                "User-Agent": self.headers["User-Agent"],
                "Referer": self.host + "/",
                "Accept": "*/*",
            }
            low = target.lower()
            if ".m3u8" in low:
                r = self.fetch(target, headers=media_headers, timeout=15)
                if not r or r.status_code != 200:
                    self.log({"proxy": "m3u8_fail", "status": getattr(r, "status_code", None)})
                    return [502, "text/plain", b"m3u8 fetch failed"]
                text = r.text or ""
                if "#EXTM3U" not in text:
                    return [502, "text/plain", b"invalid m3u8"]
                base = target.rsplit("/", 1)[0] + "/"
                out = []
                for line in text.replace("\r", "").split("\n"):
                    s = line.strip()
                    if not s:
                        out.append(line)
                        continue
                    if s.startswith("#EXT-X-KEY") or s.startswith("#EXT-X-MAP"):
                        out.append(re.sub(r'URI="([^"]+)"',
                                          lambda m: 'URI="' + self._proxy_media(urljoin(base, m.group(1))) + '"',
                                          s))
                    elif s.startswith("#"):
                        out.append(s)
                    else:
                        out.append(self._proxy_media(urljoin(base, s)))
                body = "\n".join(out).encode("utf-8")
                self.log({"proxy": "m3u8_ok", "lines": len(out), "bytes": len(body)})
                return [200, "application/vnd.apple.mpegurl", body]
            else:
                r = self.fetch(target, headers=media_headers, timeout=20)
                if not r or getattr(r, "status_code", 0) != 200:
                    self.log({"proxy": "seg_fail", "status": getattr(r, "status_code", None)})
                    return [502, "text/plain", b"media fetch failed"]
                content = getattr(r, "content", None)
                if content is None:
                    try:
                        content = r.text.encode("utf-8", errors="ignore")
                    except Exception:
                        content = b""
                self.log({"proxy": "seg_ok", "bytes": len(content), "ct": "video/mp2t"})
                if low.endswith((".ts", ".m4s")):
                    ctype = "video/mp2t"
                elif low.endswith((".jpeg", ".jpg", ".webp", ".png")):
                    ctype = "video/mp2t"
                else:
                    ctype = "application/octet-stream"
                return [200, ctype, content]
        except Exception as e:
            self.log({"action": "proxy_exc", "error": type(e).__name__})
            return [500, "text/plain", b"proxy error"]
    def _proxy_media(self, url):
        base = self.getProxyUrl()
        sep = "&" if "?" in base else "?"
        return base + sep + "url=" + quote(str(url), safe="")
    def recommendContent(self, ids, pg):
        return {"list": []}