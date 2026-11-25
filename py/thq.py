# coding: utf-8
# \u63a2\u82b1\u7fa4 \u5f71\u89c6\u722c\u866b - \u6807\u51c6HTML\u7ad9
# \u7ad9\u70b9: \u8df3\u677f https://132608.tanhq.top/ \uff5c \u771f\u7ad9 https://{\u65e5}{\u5e74}{\u6708}.tanhq.top/index.html
#
# 2026-11-25 \u53d6\u57df\u91cd\u5199\uff08\u65e7\u7248\u5199\u6b7b 132608.tanhq.top \u2192 \u5206\u7c7b\u9875\u6052 0 \u6761\uff09\uff1a
#   \u65e7\u94fe\u8def `https://132608.tanhq.top/` \u73b0\u5728**\u4e0d\u518d\u76f4\u51fa\u5185\u5bb9**\uff0c\u53ea\u8fd4\u56de 852B \u8df3\u677f\u9875\uff1a
#     <meta http-equiv="refresh" content="0;url=https://axc.tanhq.top/index.html">
#     <script>
#       function getCurrentDate(){ ... return day + year + month; }   // 6 \u4f4d '252611'
#       window.location.replace(`https://${dateSub}.tanhq.top/index.html?${dateSub}`);
#     </script>
#   \u21d2 \u771f\u7ad9\u662f**\u65e5\u671f\u5b50\u57df\u955c\u50cf**\uff1a`{dd}{yy}{mm}.tanhq.top/index.html`\uff08\u4eca\u65e5 2026-11-25 \u2192 252611\uff09\u3002
#   \u5b9e\u6d4b -6~+6 \u5929\u5171 13 \u4e2a\u65e5\u671f\u57df\uff0c\u9664 3 \u4e2a\u5076\u53d1 DNS/\u8fde\u63a5\u4e2d\u65ad\u5916**\u5168\u90e8 200 \u4e14\u5185\u5bb9\u540c\u4e00\u4efd**
#   \uff08\u5747 21870B / 21 \u4e2a hot-item\uff09\u21d2 \u65e5\u671f\u53ea\u5f53\u300c\u955c\u50cf\u7f16\u53f7\u300d\u7528\uff0c**\u4e0d\u5fc5**\u4e25\u683c\u7b49\u4e8e\u5f53\u5929\u3002
#   \u6545\u53d6\u57df\uff1d\u6309 \u4eca\u5929\u2192\u6628\u5929\u2192\u660e\u5929\u2192\u524d\u5929\u2192\u540e\u5929\u2026 \u5e76\u53d1\u63a2 `/index.html`\uff0c\u547d\u4e2d\u5373\u7528\uff0c\u4e0d\u505a\u683c\u5f0f\u786c\u7b97\u3002
#   \u26a0 \u6839\u8def\u5f84 `/` \u6c38\u8fdc\u662f\u8df3\u677f\uff08984B\uff09\uff0c\u9996\u9875\u5fc5\u987b\u8d70 `/index.html`\u3002
#   \u26a0 \u65e7\u7248\u6761\u76ee\u94fe\u662f `/v/{id}`\uff0c\u73b0\u5df2\u6539 `/player/{\u5e74}/{\u6708}/{\u65e5}/{id}.html?{mm.dd}`\uff08\u76f8\u5bf9\u8def\u5f84\uff0c
#     `hot-item`/`data-original`/`hot-title` \u4e09\u4e2a\u951a\u70b9\u672a\u53d8 \u2192 \u5217\u8868\u6b63\u5219\u6cbf\u7528\uff0c\u65e0\u9700\u6539\uff09\u3002

import datetime
import re
import json
import threading
import time
import urllib.parse
import posixpath
from urllib.parse import quote, urlencode

from base.spider import Spider as BaseSpider


# \u8df3\u677f\u57df\uff08\u53ea\u7528\u6765\u6d3e\u751f\u56fa\u5b9a\u57df\uff0c\u4e0d\u627f\u8f7d\u5185\u5bb9\uff09
_GATE_HOSTS = [
    "https://132608.tanhq.top",
    "https://axc.tanhq.top",
]
# \u65e5\u671f\u955c\u50cf\u6a21\u677f\uff1atag = \u65e5(2) + \u5e74(2) + \u6708(2)
_DATE_TPL = "https://%s.tanhq.top"
# \u63a2\u6d3b\u6df1\u94fe\uff08\u5fc5\u987b index.html\uff1b`/` \u662f\u8df3\u677f\uff09
_PROBE_PATH = "/index.html"
# \u547d\u4e2d\u8bb0\u5fc6\uff08\u79d2\uff09\uff1a\u7ad9\u70b9\u6362\u57df\u662f\u5c0f\u65f6\u7ea7\u4e8b\u4ef6\uff0c\u70ed\u542f\u4e0d\u518d\u63a2\u6d3b
_LAST_GOOD = ["", 0.0]
_LAST_GOOD_TTL = 600


class Spider(BaseSpider):
    def __init__(self):
        self.host = ""
        self.site_name = "\u63a2\u82b1\u7fa4"
        self.classes = [
            {"type_id": "1", "type_name": "\u65e5\u97e9"},
            {"type_id": "2", "type_name": "\u56fd\u4ea7"},
            {"type_id": "3", "type_name": "\u6b27\u7f8e"},
            {"type_id": "4", "type_name": "\u52a8\u6f2b"},
        ]
        self.filters = {str(c["type_id"]): [] for c in self.classes}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": self.host + "/",
        }
        self._title_cache = {}

    def getName(self):
        return "\u63a2\u82b1\u7fa4"

    def getDependence(self):
        return []

    def init(self, extend=""):
        self.extend = extend or ""
        h = self._resolve_host()
        if h:
            self._set_host(h)

    def _set_host(self, host):
        self.host = host.rstrip("/")
        self.headers.update({
            "Referer": self.host + "/",
            "Origin": self.host,
        })

    def _ensure_host(self):
        """init \u53d6\u57df\u5931\u8d25\uff08\u624b\u673a\u7f51\u7edc\u6162\uff09\u2192 \u9996\u6b21\u771f\u6b63\u8bbf\u95ee\u65f6\u518d\u8865\u4e00\u6b21\u3002"""
        if self.host:
            return
        h = self._resolve_host()
        if h:
            self._set_host(h)

    # ---------- \u53d6\u57df\uff08\u65e5\u671f\u955c\u50cf\u57df \u2192 \u8df3\u677f\u6d3e\u751f\u57df\uff09 ----------
    def _probe(self, url, slot):
        """\u63a2\u4e00\u4e2a\u5019\u9009\u57df\uff1b\u547d\u4e2d\u5199\u8fdb slot[0]\uff08\u5148\u5230\u5148\u5f97\uff09\u3002

        \u26a0 \u5fc5\u987b\u63a2 `/index.html`\uff1a\u6839\u8def\u5f84 `/` \u5728\u8be5\u7ad9\u6c38\u8fdc\u662f 852B \u8df3\u677f\u9875\uff0c\u63a2 `/` \u5fc5\u7136\u5168\u706d\u3002
        """
        try:
            u = url.rstrip("/")
            if not u.endswith(_PROBE_PATH):
                u += _PROBE_PATH
            resp = self.fetch(u, headers=self.headers, timeout=8)
            text = ""
            if resp is not None:
                content = getattr(resp, "content", b"") or b""
                text = content.decode("utf-8", errors="ignore") if content else (getattr(resp, "text", "") or "")
            # \u5224\u636e\uff1a\u771f\u5185\u5bb9\u9875\u4e00\u5b9a\u6709 hot-item \u5217\u8868\u5757\uff08\u8df3\u677f\u9875 852B\uff0c0 \u4e2a\uff09
            if text.count("hot-item") >= 4 and not slot[0]:
                slot[0] = url
        except Exception as e:
            self.log({"action": "probe_fail", "url": url, "error": str(e)[:60]})

    def _date_hosts(self):
        """\u65e5\u671f\u955c\u50cf\u5019\u9009\uff1a\u4eca\u5929 \u2192 \u6628\u5929 \u2192 \u660e\u5929 \u2192 \u524d\u5929 \u2192 \u540e\u5929 \u2192 -3/+3\u3002"""
        out = []
        today = datetime.date.today()
        for delta in (0, -1, 1, -2, 2, -3, 3):
            d = today + datetime.timedelta(days=delta)
            u = _DATE_TPL % d.strftime("%d%y%m")
            if u not in out:
                out.append(u)
        return out

    def _gate_hosts(self):
        """\u4ece\u8df3\u677f\u9875\u62bd**\u5199\u6b7b\u7684**\u56fa\u5b9a\u57df\uff08`${...}` \u6a21\u677f\u4e0d\u7b97\uff0c\u90a3\u8981\u9760\u65e5\u671f\u7b97\uff09\u3002"""
        out = []
        for g in _GATE_HOSTS:
            page = self._fetch_html(g + "/")
            if not page:
                continue
            # meta refresh \u7684\u843d\u70b9
            for m in re.findall(r'url=([^"\'>\s]+)', page, re.I):
                mm = re.match(r'^(https?://[^/]+)', m)
                if mm and ".tanhq.top" in mm.group(1):
                    out.append(mm.group(1))
            # \u9875\u9762\u91cc\u5199\u6b7b\u7684\uff08\u975e\u63d2\u503c\uff09tanhq.top \u57df
            for m in re.findall(r'https://([a-z0-9\-]+)\.tanhq\.top', page, re.I):
                if "$" not in m:
                    u = _DATE_TPL % m
                    if u not in out:
                        out.append(u)
        return out

    def _resolve_host(self):
        # 0) \u547d\u4e2d\u8bb0\u5fc6
        if _LAST_GOOD[0] and _LAST_GOOD[1] > time.time():
            return _LAST_GOOD[0]

        # \u26a0 \u5148**\u4e32\u884c**\u63a2\u4eca\u5929\uff1a\u5b9e\u6d4b\u4eca\u5929\u57df 1.1s \u547d\u4e2d\uff1b\u800c 5 \u4e2a\u5e76\u53d1\u4f1a\u88ab\u7ad9\u65b9\u9650\u901f
        #   \u2192 \u5355\u4e2a\u8bf7\u6c42\u90fd\u62d6\u5230 7s \u4ee5\u4e0a\uff0c\u5e76\u53d1\u7a97\u53e3\u5185\u5168\u706d\uff0c\u53cd\u800c\u9000\u5230\u540e\u5929\u7684\u57df\uff0810.5s\uff09\u3002
        cands = self._date_hosts()
        slot = [None]
        self._probe(cands[0], slot)
        if slot[0]:
            return self._remember(slot[0])

        # 1) \u4eca\u5929\u6ca1\u4e2d\uff08\u6362\u4e86\u955c\u50cf\u7f16\u53f7/\u6682\u65f6\u6302\uff09\u2192 \u76f8\u90bb\u65e5\u671f\u5e76\u53d1\u8865\u63a2
        rest = cands[1:]
        for group in (rest[:4], rest[4:]):
            if not group:
                continue
            result = [None]
            ts = [threading.Thread(target=self._probe, args=(u, result)) for u in group]
            for t in ts:
                t.start()
            for t in ts:
                t.join(9)
            if result[0]:
                return self._remember(result[0])

        # 2) \u8df3\u677f\u6d3e\u751f\u56fa\u5b9a\u57df\u515c\u5e95
        gate = self._gate_hosts()
        if gate:
            result = [None]
            ts = [threading.Thread(target=self._probe, args=(u, result)) for u in gate[:6]]
            for t in ts:
                t.start()
            for t in ts:
                t.join(9)
            if result[0]:
                return self._remember(result[0])

        self.log({"action": "resolve_host_fail", "cands": cands[:7]})
        return ""

    def _remember(self, url):
        m = re.match(r'^(https?://[^/]+)', url or "")
        host = m.group(1) if m else ""
        if host:
            _LAST_GOOD[0] = host
            _LAST_GOOD[1] = time.time() + _LAST_GOOD_TTL
        return host

    def homeContent(self, filter):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def homeVideoContent(self):
        self._ensure_host()
        html = self._fetch_html(self.host + _PROBE_PATH)
        items = self._parse_video_list(html)
        return {"list": items[:20]}

    def categoryContent(self, tid, pg, filter, extend):
        self._ensure_host()
        pg = str(pg) if pg else "1"
        url = f"{self.host}/list.php?cid={tid}&page={pg}"
        html = self._fetch_html(url)
        items = self._parse_video_list(html)
        page_count = self._parse_page_count(html)
        return {
            "list": items,
            "page": int(pg),
            "pagecount": page_count,
            "limit": 20,
            "total": page_count * 20,
        }

    def detailContent(self, ids):
        self._ensure_host()
        if not ids:
            return {"list": []}
        if isinstance(ids, list):
            vid = str(ids[0])
        else:
            vid = str(ids)
        
        detail_url = vid
        if not detail_url.startswith("http"):
            if detail_url.startswith("/"):
                detail_url = self.host + detail_url
            else:
                detail_url = self.host + "/" + detail_url
        
        html = self._fetch_html(detail_url)
        play_url = self._extract_m3u8_from_html(html)
        vod_name = self._extract_title_from_html(html)
        
        if play_url:
            vod = {
                "vod_id": vid,
                "vod_name": vod_name or "\u89c6\u9891",
                "vod_pic": "",
                "vod_remarks": "",
                "vod_actor": "",
                "vod_director": "",
                "vod_content": "",
                "vod_play_from": "\u64ad\u653e",
                "vod_play_url": f"播放${play_url}",
            }
        else:
            vod = {
                "vod_id": vid,
                "vod_name": vod_name or "\u89c6\u9891",
                "vod_pic": "",
                "vod_remarks": "",
                "vod_actor": "",
                "vod_director": "",
                "vod_content": "",
                "vod_play_from": "\u64ad\u653e",
                "vod_play_url": f"播放${detail_url}",
            }
        return {"list": [vod]}

    def searchContent(self, key, quick, pg="1"):
        self._ensure_host()
        pg = str(pg) if pg else "1"
        url = f"{self.host}/search.php?keyword={quote(key)}&page={pg}"
        html = self._fetch_html(url)
        items = self._parse_video_list(html)
        return {"list": items, "page": int(pg)}

    def recommendContent(self, ids, pg="1"):
        """
        \u76f8\u5173\u63a8\u8350\u63a5\u53e3 - \u591a\u7ea7\u964d\u7ea7\u7b56\u7565
        \u7b56\u75651: \u7528\u63d0\u53d6\u7684\u5173\u952e\u8bcd\u641c\u7d22
        \u7b56\u75652: \u7528\u77ed\u5173\u952e\u8bcd\u641c\u7d22
        \u7b56\u75653: \u7528\u5206\u7c7bID\u83b7\u53d6\u70ed\u95e8\u63a8\u8350
        \u7b56\u75654: \u9996\u9875\u63a8\u8350\u515c\u5e95
        """
        try:
            if not ids:
                return {"list": []}
            
            vid = ids[0] if isinstance(ids, list) else ids
            result_list = []
            
            # ===== \u7b56\u75651: \u4f7f\u7528\u5b8c\u6574\u5173\u952e\u8bcd =====
            keyword = self._extract_keyword_from_id(vid)
            if keyword and len(keyword) >= 2:
                search_result = self.searchContent(keyword, quick=False, pg=pg)
                items = search_result.get("list", [])
                filtered = [item for item in items if item.get("vod_id") != vid]
                result_list.extend(filtered)
            
            # ===== \u7b56\u75652: \u5982\u679c\u7ed3\u679c\u5c11\u4e8e3\u6761\uff0c\u4f7f\u7528\u77ed\u5173\u952e\u8bcd =====
            if len(result_list) < 3 and keyword:
                words = keyword.split()
                if len(words) >= 3:
                    short_keyword = " ".join(words[:3])
                elif len(words) >= 2:
                    short_keyword = " ".join(words[:2])
                else:
                    short_keyword = keyword[:8] if len(keyword) > 8 else keyword
                
                if short_keyword != keyword:
                    search_result2 = self.searchContent(short_keyword, quick=False, pg=pg)
                    items2 = search_result2.get("list", [])
                    existing_ids = {item.get("vod_id") for item in result_list}
                    for item in items2:
                        if item.get("vod_id") != vid and item.get("vod_id") not in existing_ids:
                            result_list.append(item)
            
            # ===== \u7b56\u75653: \u5982\u679c\u7ed3\u679c\u5c11\u4e8e3\u6761\uff0c\u4f7f\u7528\u5206\u7c7b\u70ed\u95e8 =====
            if len(result_list) < 3:
                tid = self._extract_tid_from_vid(vid)
                if tid:
                    try:
                        category_result = self.categoryContent(tid, pg="1", filter=False, extend={})
                        items3 = category_result.get("list", [])
                        existing_ids = {item.get("vod_id") for item in result_list}
                        for item in items3[:20]:
                            if item.get("vod_id") != vid and item.get("vod_id") not in existing_ids:
                                result_list.append(item)
                                if len(result_list) >= 12:
                                    break
                    except:
                        pass
            
            # ===== \u7b56\u75654: \u5982\u679c\u7ed3\u679c\u5c11\u4e8e3\u6761\uff0c\u4f7f\u7528\u9996\u9875\u63a8\u8350\u515c\u5e95 =====
            if len(result_list) < 3:
                try:
                    home_result = self.homeVideoContent()
                    items4 = home_result.get("list", [])
                    existing_ids = {item.get("vod_id") for item in result_list}
                    for item in items4[:20]:
                        if item.get("vod_id") != vid and item.get("vod_id") not in existing_ids:
                            result_list.append(item)
                            if len(result_list) >= 12:
                                break
                except:
                    pass
            
            return {"list": result_list[:12]}
            
        except Exception as e:
            self.log({"action": "recommendContent_fail", "error": str(e)})
            return {"list": []}

    def playerContent(self, flag, id, vipFlags):
        self._ensure_host()
        if id and id.startswith("http") and ".m3u8" in id:
            return {
                "parse": 0, 
                "url": self._m3u8_proxy_url(id), 
                "header": {"User-Agent": self.headers.get("User-Agent", "")}
            }
        if id and id.startswith("http"):
            html = self._fetch_html(id)
            play_url = self._extract_m3u8_from_html(html)
            if play_url:
                return {
                    "parse": 0, 
                    "url": self._m3u8_proxy_url(play_url), 
                    "header": {"User-Agent": self.headers.get("User-Agent", "")}
                }
            return {"parse": 1, "url": id, "header": self.headers}
        if id and id.startswith("/"):
            detail_url = self.host + id
            html = self._fetch_html(detail_url)
            play_url = self._extract_m3u8_from_html(html)
            if play_url:
                return {
                    "parse": 0, 
                    "url": self._m3u8_proxy_url(play_url), 
                    "header": {"User-Agent": self.headers.get("User-Agent", "")}
                }
            return {"parse": 1, "url": detail_url, "header": self.headers}
        return {"parse": 1, "url": id, "header": self.headers}

    def getProxyUrl(self):
        return "http://127.0.0.1:9978/proxy"

    def _m3u8_proxy_url(self, url):
        if url:
            url = url.replace("\\/", "/")
        return self.getProxyUrl() + "?do=py&url=" + urllib.parse.quote(str(url or ""), safe="")

    def localProxy(self, param):
        try:
            if isinstance(param, dict):
                target = param.get("url", "") or param.get("source", "")
            else:
                target = str(param or "")

            if target.startswith("url="):
                target = target[4:]
            target = urllib.parse.unquote(str(target or ""))

            if not target or not re.match(r"^https?://", target, re.I):
                return [400, "text/plain", b"invalid url"]

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
                return [502, "text/plain", b"invalid m3u8"]

            cleaned = self._clean_m3u8(text, target)
            return [200, "application/vnd.apple.mpegurl", cleaned.encode("utf-8")]

        except Exception as e:
            error_msg = f"localProxy error: {str(e)}".encode("utf-8", errors="ignore")
            return [500, "text/plain", error_msg]

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
                    child = urllib.parse.urljoin(source_url, line)
                    out.append(self._m3u8_proxy_url(child) if ".m3u8" in child.lower() else child)
            return "\n".join(out) + "\n"

        parsed = urllib.parse.urlparse(source_url)
        source_dir = posixpath.dirname(parsed.path)
        if not source_dir.endswith("/"):
            source_dir += "/"

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
                media_url = urllib.parse.urljoin(source_url, line)
                media_parsed = urllib.parse.urlparse(media_url)

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
        if line.startswith("#EXT-X-KEY") or line.startswith("#EXT-X-MAP"):
            def repl(match):
                uri = match.group(1)
                if uri.startswith(("http://", "https://")):
                    return 'URI="' + uri + '"'
                return 'URI="' + urllib.parse.urljoin(source_url, uri) + '"'
            return re.sub(r'URI="([^"]+)"', repl, line)

        if line and not line.startswith("#"):
            if line.startswith(("http://", "https://")):
                return line
            return urllib.parse.urljoin(source_url, line)

        return line

    def _fetch_html(self, url, params=None):
        full_url = url
        if params:
            if "?" in url:
                full_url = url + "&" + urlencode(params)
            else:
                full_url = url + "?" + urlencode(params)
        # 2026-11-25\uff1a\u53d6\u57df\u521a\u5e76\u53d1\u63a2\u6d3b\u8fc7\uff0c\u7ad9\u65b9\u5076\u53d1\u9650\u901f/\u7a7a\u54cd\u5e94 \u2192 \u7a7a\u7ed3\u679c\u91cd\u8bd5\u4e00\u6b21\u518d\u5224\u6b7b\u3002
        for attempt in (1, 2):
            try:
                resp = self.fetch(full_url, headers=self.headers, timeout=15)
                if resp:
                    content = getattr(resp, "content", b"") or b""
                    if not content and hasattr(resp, "text") and resp.text:
                        content = resp.text.encode("utf-8", errors="ignore")

                    if content:
                        for encoding in ["utf-8", "gbk", "gb2312", "gb18030", "latin-1"]:
                            try:
                                text = content.decode(encoding)
                                if re.search(r'[\u4e00-\u9fa5]', text) or "html" in text.lower():
                                    return text
                            except:
                                continue
                        return content.decode("utf-8", errors="ignore")
            except Exception as e:
                self.log({"action": "fetch_fail", "url": full_url, "error": str(e), "try": attempt})
            if attempt == 1:
                time.sleep(0.6)
        return ""

    def _parse_video_list(self, html):
        items = []
        if not html:
            return items
        pattern = r'<a\s+href="([^"]+)"[^>]*>.*?<div[^>]*class="[^"]*hot-item[^"]*"[^>]*>.*?<img[^>]*data-original="([^"]+)"[^>]*>.*?<div[^>]*class="[^"]*hot-title[^"]*"[^>]*>([^<]+)</div>'
        matches = re.findall(pattern, html, re.DOTALL)
        for link, pic, title in matches:
            if "player" in link:
                items.append({
                    "vod_id": link,
                    "vod_name": title.strip(),
                    "vod_pic": pic,
                    "vod_remarks": ""
                })
        return items

    def _parse_page_count(self, html):
        if not html:
            return 1
        pattern = r'<a[^>]*href="[^"]*page=(\d+)"[^>]*>(\d+)</a>'
        matches = re.findall(pattern, html)
        if matches:
            max_page = 1
            for page_num, _ in matches:
                try:
                    p = int(page_num)
                    if p > max_page:
                        max_page = p
                except:
                    pass
            return max_page
        return 1

    def _extract_m3u8_from_html(self, html):
        if not html:
            return None
        pattern = r"hls\.loadSource\('([^']+\.m3u8[^']*)'\)"
        match = re.search(pattern, html)
        if match:
            url = match.group(1)
            if url and url.startswith("http"):
                return url
        pattern2 = r'var\s+player_aaaa\s*=\s*(\{[^;]+\});'
        match2 = re.search(pattern2, html, re.DOTALL)
        if match2:
            try:
                data = json.loads(match2.group(1))
                url = data.get("url", "")
                if url and url.startswith("http"):
                    return url
            except:
                pass
        pattern3 = r'"url"\s*:\s*"([^"]+\.m3u8[^"]*)"'
        match3 = re.search(pattern3, html)
        if match3:
            url = match3.group(1)
            if url and url.startswith("http"):
                return url
        pattern4 = r'https?://[^"\']+\.m3u8[^"\']*'
        match4 = re.search(pattern4, html)
        if match4:
            return match4.group(0)
        return None

    def _extract_title_from_html(self, html):
        if not html:
            return None
        pattern = r'<title>([^<]+)</title>'
        match = re.search(pattern, html)
        if match:
            title = match.group(1)
            title = title.replace(" - \u63a2\u82b1\u7fa4", "").strip()
            return title
        return None

    def _extract_keyword_from_id(self, vid):
        if not vid:
            return None
        
        if vid in self._title_cache:
            cached_title = self._title_cache[vid]
            if cached_title:
                return self._clean_keyword(cached_title)
        
        try:
            detail_url = vid
            if not detail_url.startswith("http"):
                if detail_url.startswith("/"):
                    detail_url = self.host + detail_url
                else:
                    detail_url = self.host + "/" + detail_url
            
            html = self._fetch_html(detail_url)
            if not html:
                return None
            
            title = self._extract_title_from_html(html)
            if title:
                self._title_cache[vid] = title
                return self._clean_keyword(title)
                
            id_match = re.search(r'/(\d+)\.html', vid)
            if id_match:
                return id_match.group(1)
                
        except Exception as e:
            self.log({"action": "extract_keyword_fail", "error": str(e)})
        
        return None

    def _clean_keyword(self, title):
        if not title:
            return None
        title = re.sub('\u3010[^\u3011]*\u3011', '', title)
        title = re.sub(r'\[[^\]]*\]', '', title)
        title = re.sub('[\u3010\u3011\\[\\]\uff08\uff09()]', '', title)
        title = re.sub('[\u3001\uff0c\u3002\uff01\uff1f\\s]+$', '', title)
        
        parts = re.split('[\uff0c,\u3001\u3002.\uff01!\uff1f?\\\\s]+', title)
        words = [w.strip() for w in parts if w.strip() and len(w.strip()) > 1]
        
        chinese_words = [w for w in words if re.search(r'[\u4e00-\u9fa5]', w)]
        if chinese_words:
            clean = chinese_words[:3]
            return " ".join(clean)
        
        if words:
            clean = words[:2]
            return " ".join(clean)
        
        return None

    def _extract_tid_from_vid(self, vid):
        """\u4ece\u89c6\u9891ID\u4e2d\u63d0\u53d6\u5206\u7c7bID"""
        if not vid:
            return None
        # \u89c6\u9891\u8def\u5f84\u4e2d\u5305\u542b\u65e5\u671f\uff0c\u65e0\u6cd5\u76f4\u63a5\u63d0\u53d6\u5206\u7c7b
        # \u9ed8\u8ba4\u8fd4\u56de\u65e5\u97e9\u5206\u7c7b\uff08cid=1\uff09\u4f5c\u4e3a\u515c\u5e95
        return "1"
