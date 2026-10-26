# coding: utf-8
"""
\u7ad9\u70b9\uff1a\u63a2\u871c\u7a7a\u95f4\u00b7\u82b1\u5f71\u793e (hlfuli.com)
\u7c7b\u578b\uff1aHTML \u89c6\u9891\u7ad9\uff08\u975e MacCMS\uff0cCloudflare \u540e\u7aef\uff09
\u4e3b\u57df\u540d\uff1ahttps://hlfuli.com
\u5185\u5bb9\u7c7b\u578b\uff1a\u6210\u4eba\u89c6\u9891
\u7279\u6b8a\u8bf4\u660e\uff1a
  - \u5206\u7c7b\u8def\u7531 /category/{slug}/\uff0c\u5206\u9875 ?page={page}&c=1
  - \u8be6\u60c5\u9875 /video/{slug}-{id}/\uff0c\u64ad\u653e\u76f4\u94fe\u5185\u5d4c\u5728 #url-data \u7684 data-val \u5c5e\u6027
  - m3u8 \u53d6\u8bc1\uff1a\u65e0\u5e7f\u544a\u3001\u65e0\u591a\u7801\u7387\u3001\u65e0 KEY\u3001\u975e\u56fe\u7247\u6d41\u3001\u5206\u7247\u53ef\u8fbe \u2192 \u76f4\u63a5\u8fd4\u56de\u539f\u59cb\u76f4\u94fe\uff0c\u4e0d\u8d70\u4ee3\u7406
  - data-free=\"True\" \u4e3a\u514d\u8d39\u89c6\u9891\uff1bdata-vip=\"1\" \u4e3a\u4f1a\u5458\u4e13\u5c5e\uff0c\u64ad\u653e\u76f4\u94fe\u4ecd\u53ef\u80fd\u5185\u5d4c
\u6700\u540e\u9a8c\u8bc1\uff1a2026-09-13
"""
import re
import json
from urllib.parse import quote, urljoin

from base.spider import Spider as BaseSpider

try:
    from lxml import etree
except ImportError:
    etree = None


class Spider(BaseSpider):

    def __init__(self):
        # \u96f6\u7f51\u7edc\uff1a\u4ec5\u672c\u5730\u521d\u59cb\u5316
        self.host = "https://hlfuli.com"
        self.extend = ""
        # \u9876\u7ea7\u5206\u7c7b\uff08\u9759\u6001\u786c\u7f16\u7801\uff0c\u6cd5\u521916/17\uff09
        self.classes = [
            {"type_id": "all", "type_name": "\u5168\u90e8"},
            {"type_id": "chinese-premium", "type_name": "\u7cbe\u54c1\u56fd\u4ea7"},
            {"type_id": "welfare-cosplay", "type_name": "\u798f\u5229\u59ec"},
            {"type_id": "virgin-girl", "type_name": "\u5904\u5973&\u5c11\u5973"},
            {"type_id": "incest", "type_name": "\u4e71\u4f26"},
            {"type_id": "SM", "type_name": "\u7f51\u66b4"},
            {"type_id": "candid-selfie", "type_name": "\u5077\u62cd\u81ea\u62cd"},
            {"type_id": "seduce", "type_name": "\u5077\u60c5"},
            {"type_id": "alternative", "type_name": "\u53e6\u7c7b\u89c6\u9891"},
            {"type_id": "latest", "type_name": "\u6700\u65b0\u8d44\u6e90"},
            {"type_id": "special", "type_name": "\u7279\u8272\u8d44\u6e90"},
            {"type_id": "loli-student", "type_name": "\u841d\u8389\u5b66\u751f"},
            {"type_id": "today-expose", "type_name": "\u4eca\u65e5\u7206\u6599"},
        ]
        # \u7ad9\u70b9\u65e0\u771f\u5b9e\u7b5b\u9009 DOM\uff0c\u8fd4\u56de\u7a7a filters\uff08\u907f\u514d\u4f2a\u9020\u5047\u7b5b\u9009\uff09
        self.filters = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 22127RK46C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Referer": self.host + "/",
            "Accept-Language": "zh-Hans-CN,zh;q=0.9",
        }

    def getName(self):
        return "\u63a2\u871c\u7a7a\u95f4"

    def getDependence(self):
        return []

    def init(self, extend=""):
        # \u96f6\u7f51\u7edc
        self.extend = extend or ""

    def _full_url(self, path):
        if not path:
            return ""
        if path.startswith("http"):
            return path
        if path.startswith("//"):
            return "https:" + path
        return urljoin(self.host, path)

    # ---------- \u9996\u9875 ----------

    def homeContent(self, filter):
        # \u96f6\u7f51\u7edc
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def homeVideoContent(self):
        # \u9996\u9875\u63a8\u8350 = \u5168\u90e8\u89c6\u9891\u7b2c\u4e00\u9875
        return self.categoryContent("all", "1", False, {})

    # ---------- \u5206\u7c7b\u5217\u8868 ----------

    def _parse_extend(self, extend):
        """\u652f\u6301 dict / '{a=b}' / 'a=b' \u4e09\u79cd\u683c\u5f0f"""
        if not extend:
            return {}
        if isinstance(extend, dict):
            return extend
        if isinstance(extend, str):
            s = extend.strip()
            try:
                return json.loads(s)
            except Exception:
                pass
            result = {}
            for part in s.split(","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    result[k.strip()] = v.strip()
            return result
        return {}

    def _list_url(self, tid, pg):
        page = pg or "1"
        if tid in ("all", "", None):
            base = "%s/video" % self.host
        else:
            base = "%s/category/%s/" % (self.host, tid)
        if str(page) == "1":
            return base if tid in ("all", "", None) else base
        sep = "&" if "?" in base else "?"
        return "%s%spage=%s&c=1" % (base, sep, page)

    def categoryContent(self, tid, pg, filter, extend):
        page = str(pg or "1")
        url = self._list_url(tid, page)
        try:
            r = self.fetch(url, headers=self.headers, timeout=15)
        except Exception as e:
            self.log({"category": "fetch_exception", "error": type(e).__name__})
            r = None
        if not r or r.status_code != 200:
            self.log({"category": "fetch_failed", "status": getattr(r, "status_code", None)})
            return {"list": [], "page": int(page) if page.isdigit() else 1,
                    "pagecount": 1, "limit": 20, "total": 0}

        html = r.text or ""
        items = self._parse_list_html(html)
        # \u5206\u9875\u603b\u9875\u6570\uff1a\u4ece\u5206\u9875\u533a\u6700\u5927\u9875\u7801\u63a8\u65ad\uff0c\u515c\u5e95 10
        pagecount = self._parse_pagecount(html) or 10
        return {
            "list": items,
            "page": int(page) if page.isdigit() else 1,
            "pagecount": pagecount,
            "limit": 20,
            "total": pagecount * 20,
        }

    def _parse_pagecount(self, html):
        try:
            nums = re.findall(r'page=(\d+)', html)
            nums = [int(n) for n in nums if n.isdigit()]
            nums = [n for n in nums if 1 <= n <= 5000]
            if nums:
                return max(nums)
        except Exception:
            pass
        return 0

    def _parse_list_html(self, html):
        """\u89e3\u6790\u5217\u8868\u9879\uff1aul#data_list li"""
        items = []
        if not html:
            return items
        try:
            if etree is not None:
                doc = etree.HTML(html)
                lis = doc.xpath('//ul[@id="data_list"]/li')
                for li in lis:
                    a_list = li.xpath('.//span[@class="sTit"]/a')
                    if not a_list:
                        continue
                    a = a_list[0]
                    href = a.get("href", "")
                    name = (a.text or "").strip()
                    if not name:
                        name = (a.get("title") or "").strip()
                    pic_list = li.xpath('.//div[@class="pic"]//img')
                    pic = ""
                    if pic_list:
                        pic = pic_list[0].get("src", "") or pic_list[0].get("data-original", "")
                    des_list = li.xpath('.//span[@class="sDes"]')
                    remark = (des_list[0].text or "").strip() if des_list else ""
                    vid = self._href_to_id(href)
                    if not vid or not name:
                        continue
                    items.append({
                        "vod_id": vid,
                        "vod_name": name,
                        "vod_pic": self._full_url(pic),
                        "vod_remarks": remark,
                    })
        except Exception as e:
            self.log({"parse_list": "exception", "error": type(e).__name__})
        return items

    @staticmethod
    def _href_to_id(href):
        """/video/movie-4045/ -> https://hlfuli.com/video/movie-4045/"""
        if not href:
            return ""
        m = re.search(r'/video/([a-zA-Z0-9_\-]+)/?', href)
        if m:
            return "/video/%s/" % m.group(1)
        return ""

    # ---------- \u8be6\u60c5 ----------

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
        pid = str(vid).replace("$", "|")
        return {"list": [{
            "vod_id": vid, "vod_name": title or "\u672a\u77e5\u6807\u9898", "vod_pic": pic or "",
            "vod_remarks": remarks, "vod_content": "",
            "vod_play_from": "\u64ad\u653e", "vod_play_url": "\u64ad\u653e$" + pid,
        }]}

    def detailContent(self, ids):
        raw = self._norm_ids(ids)
        if not raw:
            return {"list": []}

        # raw \u662f /video/xxx-123/ \u5f62\u5f0f
        detail_url = self._full_url(raw)
        if not detail_url.startswith("http"):
            detail_url = self.host + "/" + raw.lstrip("/")

        title = ""
        pic = ""
        content = ""
        m3u8 = ""
        try:
            r = self.fetch(detail_url, headers=self.headers, timeout=15)
            if r and r.status_code == 200:
                html = r.text or ""
                if len(html) > 500:
                    parsed = self._parse_detail_html(html)
                    title = parsed.get("title", "")
                    pic = parsed.get("pic", "")
                    content = parsed.get("content", "")
                    m3u8 = parsed.get("m3u8", "")
        except Exception as e:
            self.log({"detail": "exception", "error": type(e).__name__})

        if not m3u8:
            # \u515c\u5e95\u9aa8\u67b6\uff1a\u4ea4\u7ed9 playerContent \u518d\u6293\u4e00\u6b21
            return self._skeleton(raw, title, pic)

        play_id = self._pack_play_id(m3u8, detail_url)
        vod = {
            "vod_id": raw,
            "vod_name": title or "\u89c6\u9891",
            "vod_pic": pic,
            "vod_remarks": content or "",
            "vod_content": content or "",
            "vod_play_from": "\u64ad\u653e",
            "vod_play_url": "\u64ad\u653e$" + play_id,
        }
        return {"list": [vod]}

    def _parse_detail_html(self, html):
        result = {"title": "", "pic": "", "content": "", "m3u8": ""}
        try:
            # \u6807\u9898\uff1a<h1> \u6216 og:title \u6216 <title>
            m = re.search(r'<title>(.*?)</title>', html, re.S)
            if m:
                t = m.group(1).strip()
                t = re.sub('\\s*[-_|].*?\u63a2\u871c\u7a7a\u95f4.*$', '', t).strip()
                result["title"] = t
            # \u64ad\u653e\u76f4\u94fe\uff1a#url-data \u7684 data-val
            m2 = re.search(r'id="url-data"[^>]*data-val="([^"]+)"', html)
            if not m2:
                m2 = re.search(r'data-val="(https?://[^"]*\.m3u8[^"]*)"', html)
            if m2:
                result["m3u8"] = m2.group(1).strip()
            # \u8be6\u60c5\u5c01\u9762
            m3 = re.search(r'class="detailPic".*?<img[^>]+src="([^"]+)"', html, re.S)
            if not m3:
                m3 = re.search(r'class="aesImgTag"[^>]*src="([^"]+)"', html)
            if m3:
                result["pic"] = self._full_url(m3.group(1).strip())
            # \u89c2\u770b\u6b21\u6570/\u8bc4\u5206\u4f5c\u4e3a content
            m4 = re.search('\u89c2\u770b\u6b21\u6570\uff1a\\s*(\\d+)', html)
            if m4:
                result["content"] = "\u89c2\u770b\u6b21\u6570\uff1a" + m4.group(1)
        except Exception:
            pass
        return result

    def _pack_play_id(self, m3u8, page_url):
        """\u64ad\u653eID \u5185\u7981\u6b62\u88f8 $\uff0c\u7528 | \u5206\u9694\uff1am3u8|\u9875\u9762URL"""
        safe = m3u8.replace("$", "%24")
        return safe + "|" + page_url

    # ---------- \u641c\u7d22 ----------

    def searchContent(self, key, quick, pg="1"):
        page = str(pg or "1")
        kw = quote(str(key or ""), safe="")
        url = "%s/video/search/?q=%s" % (self.host, kw)
        if page != "1":
            url += "&page=" + page
        try:
            r = self.fetch(url, headers=self.headers, timeout=15)
        except Exception as e:
            self.log({"search": "exception", "error": type(e).__name__})
            r = None
        if not r or r.status_code != 200:
            return {"list": [], "page": int(page) if page.isdigit() else 1}
        html = r.text or ""
        # \u65e0\u7ed3\u679c\u6c61\u67d3\u8fc7\u6ee4
        if re.search('\u6ca1\u6709\u627e\u5230|\u6682\u65e0\u6570\u636e|\u641c\u7d22\u65e0\u7ed3\u679c', html):
            return {"list": [], "page": int(page) if page.isdigit() else 1}
        items = self._parse_list_html(html)
        return {"list": items, "page": int(page) if page.isdigit() else 1}

    # ---------- \u64ad\u653e ----------

    def playerContent(self, flag, id, vipFlags):
        play_url = str(id or "").strip()
        page_url = ""

        # \u62c6\u5305\uff1am3u8|\u9875\u9762URL
        if "|" in play_url:
            parts = play_url.split("|", 1)
            play_url = parts[0]
            page_url = parts[1] if len(parts) > 1 else ""
        # \u517c\u5bb9 \u540d\u79f0$\u5730\u5740 \u5f62\u5f0f
        if "$" in play_url:
            play_url = play_url.split("$", 1)[1]

        play_url = play_url.replace("%24", "$")

        # \u5df2\u662f m3u8/mp4 \u76f4\u94fe \u2192 \u76f4\u63a5\u8fd4\u56de\uff0c\u4e0d\u8d70\u4ee3\u7406\uff08\u6cd5\u521930\uff1am3u8_analyzer \u53d6\u8bc1\u65e0\u5e7f\u544a\uff09
        if play_url and re.search(r'\.(m3u8|mp4|flv)(\?|$)', play_url, re.I):
            if not play_url.startswith("http"):
                if play_url.startswith("//"):
                    play_url = "https:" + play_url
                else:
                    play_url = "https://" + play_url
            return {"parse": 0, "url": play_url, "header": {
                "User-Agent": self.headers["User-Agent"],
                "Referer": self.host + "/",
            }}

        # \u515c\u5e95\uff1a\u6293\u8be6\u60c5\u9875\u63d0\u53d6 data-val
        if page_url:
            try:
                r = self.fetch(page_url, headers=self.headers, timeout=15)
                if r and r.status_code == 200:
                    m = re.search(r'data-val="(https?://[^"]*\.m3u8[^"]*)"', r.text or "")
                    if m:
                        return {"parse": 0, "url": m.group(1).strip(), "header": {
                            "User-Agent": self.headers["User-Agent"],
                            "Referer": self.host + "/",
                        }}
            except Exception as e:
                self.log({"player": "fallback_exception", "error": type(e).__name__})

        # \u6700\u540e\u624b\u6bb5\uff1a\u55c5\u63a2
        if page_url:
            return {"parse": 1, "url": page_url, "header": {
                "User-Agent": self.headers["User-Agent"],
                "Referer": self.host + "/",
            }}
        return {"parse": 1, "url": play_url, "header": {
            "User-Agent": self.headers["User-Agent"],
            "Referer": self.host + "/",
        }}

    # ---------- \u63a8\u8350 ----------

    def recommendContent(self, ids, pg):
        """\u57fa\u4e8e\u5f53\u524d\u5206\u7c7b\u63a8\u8350\uff1a\u8fd4\u56de\u5168\u90e8\u5217\u8868\u7b2c\u4e00\u9875"""
        try:
            return self.categoryContent("all", "1", False, {})
        except Exception:
            return {"list": []}

    # ---------- \u5176\u4ed6 ----------

    def destroy(self):
        try:
            self.extend = ""
        except Exception:
            pass

    def isVideoFormat(self, url):
        return bool(url and re.search(r'\.(m3u8|mp4|flv)', url, re.I))

    def manualVideoCheck(self):
        return False

    def liveContent(self, url):
        return ""

    def action(self, action):
        return {}