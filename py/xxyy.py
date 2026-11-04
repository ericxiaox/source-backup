# -*- coding: utf-8 -*-
import sys
import re
import requests
from urllib.parse import quote
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def init(self, extend=""):
        self.host = "https://xxyy5.cfd"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
            "Referer": self.host + "/",
            "Origin": self.host
        }

    def getName(self):
        return "\u5c0f\u5fc3\u5fa1\u6b32"

    def isVideoFormat(self, url):
        return bool(re.search(r'\.(m3u8|mp4|flv|avi|mkv|mov|ts)(\?|$)', url or "", re.I))

    def manualVideoCheck(self):
        return False

    def homeContent(self, filter):
        return {
            "class": [
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
                {"type_id": "48", "type_name": "VR\u89c6\u89d2"}
            ]
        }

    def homeVideoContent(self):
        return {"list": self.parseList(self.get(self.host + "/"))}

    def categoryContent(self, tid, pg, filter, extend):
        ext = extend or {}
        url = self.host + "/search.php?searchtype=5&tid=" + str(tid) + "&page=" + str(pg)
        for k in ["area", "year", "yuyan", "order"]:
            if ext.get(k):
                url += "&" + k + "=" + quote(str(ext.get(k)))
        html = self.get(url)
        return {
            "page": int(pg),
            "pagecount": 999,
            "limit": 24,
            "total": 999999,
            "list": self.parseList(html)
        }

    def detailContent(self, ids):
        vid = ids[0]
        html = self.get(self.host + "/movie/index" + vid + ".html")
        name = self.clean(self.match(html, r'<h3[^>]*class=["\'][^"\']*title[^"\']*["\'][^>]*>(.*?)</h3>') or self.match(html, r'<h1[^>]*>(.*?)</h1>') or self.match(html, r'<meta property="og:title" content="(.*?)"'))
        pic = self.fix(self.match(html, r'<meta property="og:image" content="(.*?)"') or self.match(html, r'<a[^>]+class=["\'][^"\']*stui-vodlist__thumb[^"\']*["\'][^>]+(?:data-original|data-src|src)=["\']([^"\']+)') or self.match(html, r'<img[^>]+(?:data-original|data-src|src)=["\']([^"\']+)'))
        desc = self.clean(self.match(html, r'<span[^>]*class=["\'][^"\']*detail-content[^"\']*["\'][^>]*>(.*?)</span>') or self.match(html, r'<meta property="og:description" content="(.*?)"') or name)
        play_from = []
        play_url = []
        blocks = re.findall(r'<ul[^>]+class=["\'][^"\']*stui-content__playlist[^"\']*["\'][^>]*>[\s\S]*?</ul>', html or "", re.S)
        for i, p in enumerate(blocks):
            eps = []
            for m in re.finditer(r'<a[^>]+href=["\']([^"\']*?/play/' + re.escape(vid) + r'-[^"\']+)["\'][^>]*>(.*?)</a>', p, re.S):
                t = self.clean(m.group(2)) or self.clean(self.match(m.group(0), r'title=["\']([^"\']+)')) or "\u64ad\u653e"
                u = self.fix(m.group(1))
                if t and u:
                    eps.append(t + "$" + u)
            if eps:
                play_from.append("\u9ed8\u8ba4" if i == 0 else "\u7ebf\u8def" + str(i + 1))
                play_url.append("#".join(eps))
        if not play_url:
            eps = []
            for m in re.finditer(r'<a[^>]+href=["\']([^"\']*?/play/' + re.escape(vid) + r'-[^"\']+)["\'][^>]*>(.*?)</a>', html or "", re.S):
                t = self.clean(m.group(2)) or self.clean(self.match(m.group(0), r'title=["\']([^"\']+)')) or "\u64ad\u653e"
                u = self.fix(m.group(1))
                if t and u:
                    eps.append(t + "$" + u)
            if eps:
                play_from.append("\u9ed8\u8ba4")
                play_url.append("#".join(eps))
        return {
            "list": [{
                "vod_id": vid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_content": desc,
                "vod_play_from": "$$$".join(play_from),
                "vod_play_url": "$$$".join(play_url)
            }]
        }

    def searchContent(self, key, quick, pg="1"):
        html = ""
        try:
            r = requests.post(self.host + "/search.php", headers=self.headers, data={"searchword": key}, timeout=12, verify=False)
            r.encoding = r.apparent_encoding or "utf-8"
            html = r.text
        except Exception:
            html = ""
        if not html or "/movie/index" not in html:
            html = self.get(self.host + "/search.php?searchword=" + quote(key) + "&page=" + str(pg))
        return {"list": self.parseList(html), "page": int(pg)}

    def playerContent(self, flag, id, vipFlags):
        url = id if str(id).startswith("http") else self.fix(id)
        if self.isVideoFormat(url):
            return {"parse": 0, "url": url, "header": self.headers}
        html = self.get(url)
        play = self.match(html, r'var\s+now\s*=\s*["\']([^"\']+)["\']') or self.match(html, r'(https?://[^\s"\']+\.(?:m3u8|mp4|flv)[^\s"\']*)')
        if play:
            play = self.fix(play)
            return {"parse": 0 if self.isVideoFormat(play) else 1, "url": play, "header": self.headers}
        return {"parse": 1, "url": url, "header": self.headers}

    def localProxy(self, param):
        return [404, "text/plain", "", ""]

    def destroy(self):
        return "\u6b63\u5728Destroy"

    def get(self, url):
        try:
            r = requests.get(url, headers=self.headers, timeout=12, verify=False)
            r.encoding = r.apparent_encoding or "utf-8"
            return r.text
        except Exception:
            return ""

    def match(self, text, rule):
        m = re.search(rule, text or "", re.S)
        return m.group(1) if m else ""

    def clean(self, text):
        return re.sub(r"\s+", " ", re.sub(r"<.*?>", "", text or "")).strip()

    def fix(self, url):
        if not url:
            return ""
        if url.startswith("//"):
            return "https:" + url
        if url.startswith("/"):
            return self.host + url
        return url

    def parseList(self, html):
        res = []
        seen = set()
        html = html or ""
        # \u6807\u9898\u515c\u5e95\u8868\uff1adetail \u533a <h3 class="title"><a href="/movie/index{id}.html">\u6807\u9898</a>
        name_map = {}
        for vid0, t0 in re.findall(
                r'<h3[^>]*class=["\'][^"\']*title[^"\']*["\'][^>]*>\s*<a[^>]+href=["\']/movie/index(\d+)\.html["\'][^>]*>(.*?)</a>',
                html, re.S):
            name_map[vid0] = self.clean(re.sub(r'<[^>]+>', '', t0))
        # \ud83d\udea9 2026-11-04 \u4e24\u4e2a\u5751\u4e00\u8d77\u4fee\uff1a
        #   \u2460 \u539f\u6b63\u5219\u628a class \u5199\u6b7b\u5728 href \u4e4b\u524d\uff08`class="stui-vodlist__thumb" \u2026 href=\u2026`\uff09\uff0c
        #      \u7ad9\u70b9\u4e00\u8c03\u5c5e\u6027\u987a\u5e8f\u5c31\u6574\u9875 0 \u6761\uff1b
        #   \u2461 \u540c\u4e00\u90e8\u7247\u6709**\u4e24\u4e2a** `<a href="/movie/index{id}.html">`\uff1a\u7f29\u7565\u56fe\u90a3\u4e2a\uff08\u5e26
        #      data-original \u5c01\u9762\uff09\u548c detail \u533a h3 \u91cc\u7684\u7eaf\u6587\u5b57\u6807\u9898\u94fe\u63a5\u3002\u53ea\u6309 href \u5339\u914d\u4f1a\u5148
        #      \u547d\u4e2d\u6807\u9898\u94fe\u63a5\uff0c`seen` \u53bb\u91cd\u540e\u628a\u5e26\u56fe\u7684\u94fe\u63a5\u5168\u90e8\u8df3\u8fc7 \u2192 \u6709\u6807\u9898\u6ca1\u5c01\u9762\u3002
        #   \u6539\u4e3a\u300c\u904d\u5386 <a> \u5757 \u2192 \u53ea\u91c7\u7eb3\u5e26\u5c01\u9762\u5c5e\u6027\u7684\u5757\u300d\uff0c\u6807\u9898\u7528 detail \u533a\u6620\u5c04\u515c\u5e95\u3002
        for m in re.finditer(r'<a\b([^>]*)>(.*?)</a>', html, re.S):
            attrs, body = m.group(1), m.group(2)
            if not re.search(r'stui-vodlist__thumb|data-original|data-src', attrs):
                continue
            # \ud83d\udea9 \u7f29\u7565\u56fe\u94fe\u63a5\u662f `/play/{id}-0-0.html`\uff0c\u8be6\u60c5\u94fe\u63a5\u624d\u662f `/movie/index{id}.html`
            #   \u2014\u2014 \u539f\u6b63\u5219\u53ea\u8ba4\u540e\u8005\uff0c\u7f29\u7565\u56fe\u5757\u5168\u88ab\u8df3\u8fc7\u3002\u4e24\u79cd\u90fd\u6536\uff0cvid \u7edf\u4e00\u53d6\u7eaf\u6570\u5b57
            #   \uff08detailContent \u6309 `/movie/index{vid}.html` \u62fc\u8be6\u60c5\u9875\uff09\u3002
            hm = (re.search(r'href=["\']/play/(\d+)-\d+-\d+\.html', attrs)
                  or re.search(r'href=["\']/movie/index(\d+)\.html', attrs))
            if not hm:
                continue
            vid = hm.group(1)
            if not vid or vid in seen:
                continue
            seen.add(vid)
            name = self.clean(self.match(attrs, r'title=["\']([^"\']+)') or name_map.get(vid, ''))
            pic = self.fix(self.match(attrs, r'(?:data-original|data-src|src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp|gif)[^"\']*)'))
            if not pic:
                pic = self.fix(self.match(body, r'(?:data-original|data-src|src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp|gif)[^"\']*)'))
            remarks = self.clean(self.match(body, r'<span[^>]+class=["\'][^"\']*pic-text[^"\']*["\'][^>]*>(.*?)</span>'))
            if name:
                res.append({
                    "vod_id": vid,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_remarks": remarks
                })
        return res