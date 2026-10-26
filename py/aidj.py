# coding: utf-8
"""
\u7ad9\u70b9: Ai\u9876\u7ea7\u6da9\u56fe
\u4e3b\u57df\u540d: https://aidjst.cc/888/
\u5185\u5bb9\u7c7b\u578b: AI\u7ed8\u753b\u56fe\u7247\u7ad9 (pics://\u534f\u8bae)
\u7279\u6b8a\u8bf4\u660e: WordPress\u7ad9\uff0c\u5206\u7c7b\u9875\u9762404\uff0c\u6240\u6709\u5185\u5bb9\u5728\u9996\u9875\uff0c\u5206\u7c7b\u4ec5\u4f5c\u6807\u7b7e\u663e\u793a
\u6700\u540e\u9a8c\u8bc1\u65f6\u95f4: 2026-09-04
\u6765\u6e90: \u7528\u6237\u63d0\u4f9b
m3u8\u7ed3\u6784: \u65e0\uff0c\u7eaf\u56fe\u7247\u7ad9
"""
import re
import urllib.request
import urllib.parse
import ssl
from urllib.parse import urljoin, quote

from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
    def __init__(self):
        self.host = "https://aidjst.cc/888"
        # \u5206\u7c7b\u786c\u7f16\u7801 - \u7531\u4e8e\u5206\u7c7b\u9875\u9762404\uff0c\u6240\u6709\u5206\u7c7b\u5747\u8fd4\u56de\u9996\u9875\u5185\u5bb9
        self.classes = [
            {"type_id": "all", "type_name": "\u5168\u90e8"},
            {"type_id": "doupo", "type_name": "\u6597\u7834\u82cd\u7a79"},
            {"type_id": "douluo", "type_name": "\u6597\u7f57\u5927\u9646"},
            {"type_id": "uncategorized", "type_name": "\u672a\u5206\u7c7b"},
        ]
        self.filters = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 22127RK46C) AppleWebKit/537.36",
            "Referer": self.host + "/"
        }
        self.page_size = 10
        # \u5206\u7c7bslug\u6620\u5c04 - \u4ec5\u7528\u4e8e\u663e\u793a\uff0c\u5b9e\u9645\u4e0d\u7528\u4e8eURL
        self.category_slugs = {
            "doupo": "\u6597\u7834\u82cd\u7a79",
            "douluo": "\u6597\u7f57\u5927\u9646",
            "uncategorized": "uncategorized"
        }

    def getName(self):
        return "Ai\u9876\u7ea7\u6da9\u56fe"

    def getDependence(self):
        return []

    def init(self, extend=""):
        self.extend = extend or ""

    def _fetch_text(self, url):
        """\u83b7\u53d6\u9875\u9762\u6587\u672c - \u517c\u5bb9\u6c99\u76d2\u73af\u5883"""
        try:
            resp = self.fetch(url, headers=self.headers, timeout=15)
            return resp.text
        except Exception as e:
            pass
        try:
            context = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15, context=context) as resp:
                return resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            raise e

    def homeContent(self, filter):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def homeVideoContent(self):
        """\u9996\u9875\u63a8\u8350 - \u6293\u53d6\u9996\u9875\u6587\u7ae0\u5217\u8868"""
        return self._fetch_list(self.host)

    def categoryContent(self, tid, pg, filter, extend):
        """
        \u5206\u7c7b\u5217\u8868 - \u7531\u4e8e\u5206\u7c7b\u9875\u9762404\uff0c\u6240\u6709\u5206\u7c7b\u5747\u8fd4\u56de\u9996\u9875\u5185\u5bb9
        \u5206\u9875\u4f7f\u7528\u6b63\u786e\u7684URL\u683c\u5f0f: /index.php/page/{page}/
        """
        page = int(pg or 1)
        # \u6240\u6709\u5206\u7c7b\u90fd\u8fd4\u56de\u9996\u9875\u5217\u8868\uff0c\u5206\u9875URL\u4f7f\u7528 index.php/page/{page}/
        if page <= 1:
            url = self.host + "/"
        else:
            url = f"{self.host}/index.php/page/{page}/"

        result = self._fetch_list(url)
        items = result.get("list", [])
        total = page * self.page_size + 10
        return {
            "list": items,
            "page": page,
            "pagecount": page + 5 if items else page,
            "limit": self.page_size,
            "total": total if items else 0
        }

    def _fetch_list(self, url):
        """\u901a\u7528\u5217\u8868\u6293\u53d6\u65b9\u6cd5"""
        try:
            html = self._fetch_text(url)
        except Exception as e:
            self.log(f"fetch_list error: {e}")
            return {"list": []}

        items = []
        # \u5339\u914d\u6587\u7ae0\u5757
        pattern = r'<article[^>]*id="post-(\d+)"[^>]*>([\s\S]*?)</article>'
        for post_id, block in re.findall(pattern, html, re.S):
            # \u63d0\u53d6\u6807\u9898\u548c\u94fe\u63a5
            title_match = re.search(r'<h[23][^>]*class="[^"]*entry-title[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', block, re.S)
            if not title_match:
                continue
            link = title_match.group(1)
            title = title_match.group(2).strip()
            # \u63d0\u53d6\u5c01\u9762\u56fe
            pic_match = re.search(r'<img[^>]+src="([^"]+)"[^>]*>', block, re.S)
            pic = pic_match.group(1) if pic_match else ""
            # \u63d0\u53d6\u5206\u7c7b\u6807\u7b7e
            cat_match = re.search(r'<a[^>]*rel="category tag"[^>]*>([^<]+)</a>', block, re.S)
            remark = cat_match.group(1) if cat_match else ""
            items.append({
                "vod_id": link,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": remark[:20] if remark else "",
            })
        return {"list": items}

    def detailContent(self, ids):
        """\u8be6\u60c5\u9875 - \u63d0\u53d6\u6240\u6709\u56fe\u7247"""
        url = ids[0] if ids else ""
        if not url or not url.startswith("http"):
            return {"list": []}

        try:
            html = self._fetch_text(url)
        except Exception as e:
            self.log(f"detail error: {e}")
            return {"list": []}

        title_match = re.search(r'<h1[^>]*class="[^"]*entry-title[^"]*"[^>]*>([^<]+)</h1>', html, re.S)
        title = title_match.group(1).strip() if title_match else "\u56fe\u7247"

        content_match = re.search(r'<div[^>]*class="[^"]*entry-content[^"]*"[^>]*>([\s\S]*?)(?:</div>|</article>)', html, re.S)
        scope = content_match.group(1) if content_match else html

        imgs = re.findall(r'<img[^>]+src="([^"]+\.(?:jpg|jpeg|png|webp|gif))"', scope, re.S)
        imgs += re.findall(r'<img[^>]+data-src="([^"]+\.(?:jpg|jpeg|png|webp|gif))"', scope, re.S)

        filtered = []
        seen = set()
        bad_keywords = ['avatar', 'icon', 'logo', 'loading', 'smilies', 'qrcode', 'thumb', 'index', 'favicon', 'static']
        for img in imgs:
            img = img.strip()
            if not img or img in seen:
                continue
            img_lower = img.lower()
            if any(k in img_lower for k in bad_keywords):
                continue
            if img.startswith("//"):
                img = "https:" + img
            elif img.startswith("/"):
                img = urljoin(self.host, img)
            filtered.append(img)
            seen.add(img)

        if not filtered:
            all_imgs = re.findall(r'<img[^>]+src="([^"]+)"', html, re.S)
            for img in all_imgs:
                img = img.strip()
                if not img or img in seen:
                    continue
                if any(k in img.lower() for k in bad_keywords):
                    continue
                if img.startswith("//"):
                    img = "https:" + img
                elif img.startswith("/"):
                    img = urljoin(self.host, img)
                filtered.append(img)
                seen.add(img)

        pics_play = "&&".join([f"{img}@Referer={self.host}/" for img in filtered])

        vod = {
            "vod_id": url,
            "vod_name": title,
            "vod_pic": filtered[0] if filtered else "",
            "vod_remarks": f"共{len(filtered)}张",
            "vod_content": f"共{len(filtered)}张图片",
            "vod_play_from": "\u56fe\u7247\u6d4f\u89c8",
            "vod_play_url": f"浏览图片$pics://{pics_play}" if filtered else ""
        }
        return {"list": [vod]}

    def searchContent(self, key, quick, pg="1"):
        page = int(pg or 1)
        url = f"{self.host}/?s={quote(key)}"
        if page > 1:
            url = f"{self.host}/page/{page}/?s={quote(key)}"

        try:
            html = self._fetch_text(url)
        except Exception as e:
            self.log(f"search error: {e}")
            return {"list": []}

        items = []
        pattern = r'<article[^>]*id="post-(\d+)"[^>]*>([\s\S]*?)</article>'
        for post_id, block in re.findall(pattern, html, re.S):
            title_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', block, re.S)
            if not title_match:
                continue
            link = title_match.group(1)
            title = title_match.group(2).strip()
            pic_match = re.search(r'<img[^>]+src="([^"]+)"[^>]*>', block, re.S)
            pic = pic_match.group(1) if pic_match else ""
            items.append({
                "vod_id": link,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": "\u641c\u7d22\u7ed3\u679c"
            })
        return {"list": items}

    def playerContent(self, flag, id, vipFlags):
        if id.startswith("pics://"):
            return {"parse": 0, "url": id, "header": {"Referer": self.host + "/"}}
        if id.startswith("http"):
            detail = self.detailContent([id])
            if detail and detail.get("list"):
                vod = detail["list"][0]
                play_url = vod.get("vod_play_url", "")
                if play_url.startswith("\u6d4f\u89c8\u56fe\u7247$pics://"):
                    pics_url = play_url.replace("\u6d4f\u89c8\u56fe\u7247$", "")
                    return {"parse": 0, "url": pics_url, "header": {"Referer": self.host + "/"}}
        return {"parse": 0, "url": "", "header": {}}

    def recommendContent(self, ids, pg):
        return {"list": []}

    def destroy(self):
        pass