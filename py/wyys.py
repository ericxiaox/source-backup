# -*- coding: utf-8 -*-
import sys
import os
import json
import ssl
import re
import time
import html
import urllib.request
import urllib.parse
import http.cookiejar

try:
    from base.spider import Spider
except Exception:
    class Spider(object):
        def __init__(self):
            pass

class Spider(Spider):
    def __init__(self):
        super(Spider, self).__init__()
        self.site_url = "https://xn--5us888dtla.wuye.mom"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
        self.ssl_ctx = ssl._create_unverified_context()
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=self.ssl_ctx),
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )

    def getName(self):
        return "\u8774\u8776\u5f71\u89c6"

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        return 0

    def manualVideoCheck(self):
        return 0

    def action(self, action):
        return {}

    def liveContent(self):
        return {}

    def localProxy(self, params):
        return []

    def destroy(self):
        pass

    def _fetch(self, url, retry=2):
        for attempt in range(retry + 1):
            try:
                req = urllib.request.Request(url, headers=self.headers)
                resp = self.opener.open(req, timeout=12)
                code = resp.getcode()
                raw_data = resp.read()
                charset = "utf-8"
                content_type = resp.headers.get("Content-Type", "")
                match = re.search(r"charset=([\w\-]+)", content_type, re.IGNORECASE)
                if match:
                    charset = match.group(1)
                text = raw_data.decode(charset, errors="ignore")
                if len(text) > 500:
                    return code, text
            except Exception:
                if attempt == retry:
                    break
                time.sleep(0.3)
        return 0, ""

    def homeContent(self, filter):
        classes = [
            {"type_id": "4", "type_name": "\u65b0\u7535\u5f71"},
            {"type_id": "5", "type_name": "\u7535\u89c6\u5267"},
            {"type_id": "9", "type_name": "\u70ed\u77ed\u5267"},
            {"type_id": "7", "type_name": "\u706b\u52a8\u6f2b"},
            {"type_id": "6", "type_name": "\u7efc\u827a\u7247"},
            {"type_id": "1", "type_name": "\u56fd\u4ea7\u533a"},
            {"type_id": "2", "type_name": "\u65e5\u97e9\u533a"},
            {"type_id": "3", "type_name": "\u7cbe\u54c1\u533a"},
            {"type_id": "8", "type_name": "\u4f26\u7406\u7247"},
            {"type_id": "10", "type_name": "\u4f53\u80b2\u8d5b\u4e8b"}
        ]
        filters = {
            "4": [{"key": "sub", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "\u52a8\u6f2b\u7535\u5f71", "v": "78"},
                {"n": "\u52a8\u4f5c\u7247", "v": "38"},
                {"n": "\u7231\u60c5\u7247", "v": "39"},
                {"n": "\u559c\u5267\u7247", "v": "40"},
                {"n": "\u79d1\u5e7b\u7247", "v": "41"},
                {"n": "\u6050\u6016\u7247", "v": "42"},
                {"n": "\u5267\u60c5\u7247", "v": "43"},
                {"n": "\u6218\u4e89\u7247", "v": "44"},
                {"n": "\u60ca\u609a\u7247", "v": "45"},
                {"n": "\u7eaa\u5f55\u7247", "v": "46"}
            ]}],
            "5": [{"key": "sub", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "\u56fd\u4ea7\u5267", "v": "47"},
                {"n": "\u9999\u6e2f\u5267", "v": "48"},
                {"n": "\u97e9\u5267", "v": "49"},
                {"n": "\u6b27\u7f8e\u5267", "v": "50"},
                {"n": "\u65e5\u672c\u5267", "v": "51"},
                {"n": "\u6cf0\u56fd\u5267", "v": "52"},
                {"n": "\u53f0\u6e7e\u5267", "v": "53"},
                {"n": "\u6d77\u5916\u5267", "v": "54"}
            ]}],
            "9": [{"key": "sub", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "\u91cd\u751f\u6c11\u56fd", "v": "64"},
                {"n": "\u7a7f\u8d8a\u73b0\u4ee3", "v": "65"},
                {"n": "\u53cd\u8f6c\u723d\u5267", "v": "66"},
                {"n": "\u8a00\u60c5\u603b\u88c1", "v": "67"},
                {"n": "\u73b0\u4ee3\u90fd\u5e02", "v": "68"},
                {"n": "\u53e4\u88c5\u4ed9\u4fa0", "v": "69"},
                {"n": "\u60ac\u7591\u70e7\u8111", "v": "70"}
            ]}],
            "7": [{"key": "sub", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "\u56fd\u4ea7\u52a8\u6f2b", "v": "60"},
                {"n": "\u65e5\u672c\u52a8\u6f2b", "v": "61"},
                {"n": "\u6b27\u7f8e\u52a8\u6f2b", "v": "62"},
                {"n": "\u6d77\u5916\u52a8\u6f2b", "v": "63"}
            ]}],
            "6": [{"key": "sub", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "\u5927\u9646\u7efc\u827a", "v": "55"},
                {"n": "\u65e5\u97e9\u7efc\u827a", "v": "56"},
                {"n": "\u6e2f\u53f0\u7efc\u827a", "v": "57"},
                {"n": "\u6b27\u7f8e\u7efc\u827a", "v": "58"},
                {"n": "\u6f14\u5531\u4f1a", "v": "59"}
            ]}],
            "1": [{"key": "sub", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "\u5f3a\u5978\u8ff7\u5978", "v": "11"},
                {"n": "\u7f51\u66dd\u9ed1\u6599", "v": "12"},
                {"n": "\u56fd\u4ea7\u5382\u724c", "v": "13"},
                {"n": "\u4e1d\u889c\u5236\u670d", "v": "14"},
                {"n": "\u4e3b\u64ad\u7f51\u7ea2", "v": "15"},
                {"n": "AI\u6362\u8138", "v": "16"},
                {"n": "\u5bb6\u5ead\u4e71\u4f26", "v": "17"},
                {"n": "SM\u8c03\u6559", "v": "18"},
                {"n": "\u7fa4\u4ea4\u591aP", "v": "19"}
            ]}],
            "2": [{"key": "sub", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "\u5b66\u751f\u841d\u8389", "v": "20"},
                {"n": "\u81ea\u62cd\u5077\u62cd", "v": "21"},
                {"n": "\u53e3\u4ea4\u81ea\u6170", "v": "22"},
                {"n": "\u56fd\u4ea7\u4e09\u7ea7", "v": "23"},
                {"n": "\u7d20\u4eba\u7279\u6444", "v": "24"},
                {"n": "\u65e0\u7801\u9ad8\u6e05", "v": "25"},
                {"n": "\u7ecf\u5178\u6709\u7801", "v": "26"},
                {"n": "\u4e2d\u6587\u5b57\u5e55", "v": "27"},
                {"n": "\u65e5\u97e9\u4e09\u7ea7", "v": "28"}
            ]}],
            "3": [{"key": "sub", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "\u65e5\u97e9\u7cbe\u9009", "v": "29"},
                {"n": "\u56fd\u4ea7\u7cbe\u9009", "v": "30"},
                {"n": "\u6b27\u7f8e\u7cbe\u9009", "v": "31"},
                {"n": "VR\u4e13\u533a", "v": "32"},
                {"n": "\u5382\u724c\u7ecf\u5178", "v": "33"},
                {"n": "\u91cd\u53e3\u8c03\u6559", "v": "34"},
                {"n": "\u4eba\u517d\u52a8\u7269", "v": "35"},
                {"n": "\u6fc0\u60c5H\u6f2b", "v": "36"},
                {"n": "\u5f02\u65cf\u98ce\u60c5", "v": "37"}
            ]}],
            "10": [{"key": "sub", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "\u7bee\u7403", "v": "71"},
                {"n": "\u8db3\u7403", "v": "72"},
                {"n": "\u7f51\u7403", "v": "73"},
                {"n": "\u65af\u8bfa\u514b", "v": "74"},
                {"n": "LPL", "v": "75"}
            ]}]
        }
        return {"class": classes, "filters": filters, "list": []}

    def homeVideoContent(self):
        return {"list": []}

    def categoryContent(self, tid, pg, filter, extend):
        actual_tid = str(tid)
        if extend and isinstance(extend, dict) and extend.get("sub"):
            actual_tid = str(extend.get("sub"))

        page_int = int(pg) if str(pg).isdigit() else 1
        
        if page_int <= 1:
            req_url = "%s/vodshow/%s-----------.html" % (self.site_url, actual_tid)
        else:
            req_url = "%s/vodshow/%s--------%d---.html" % (self.site_url, actual_tid, page_int)

        videos = []
        page_count = page_int
        total_records = 0

        try:
            code, raw_html = self._fetch(req_url)
            page_text = html.unescape(raw_html)
            
            card_blocks = re.findall(r'<li[^>]*class=[\'"][^\'"]*stui-vodlist__item[^\'"]*[\'"][^>]*>([\s\S]*?)</li>', page_text)
            if not card_blocks:
                card_blocks = re.findall(r'(<a[^>]*class=[\'"][^\'"]*stui-vodlist__thumb[^\'"]*[\'"][\s\S]*?</a>)', page_text)

            for block in card_blocks:
                id_match = re.search(r'href=[\'"][^\'"]*?/voddetail/(\d+)\.html[\'"]', block)
                if not id_match:
                    continue
                vod_id = id_match.group(1)

                name_match = re.search(r'title=[\'"]([^\'"]+)[\'"]', block)
                vod_name = name_match.group(1).strip() if name_match else ""

                pic_match = re.search(r'data-original=[\'"]([^\'"]+)[\'"]', block)
                if not pic_match:
                    pic_match = re.search(r'src=[\'"]([^\'"]+)[\'"]', block)
                vod_pic = pic_match.group(1) if pic_match else ""
                if vod_pic and not vod_pic.startswith("http"):
                    vod_pic = urllib.parse.urljoin(self.site_url, vod_pic)

                remarks_match = re.search(r'<span[^>]*class=[\'"][^\'"]*pic-text[^\'"]*[\'"][^>]*>([\s\S]*?)</span>', block)
                raw_remarks = remarks_match.group(1).strip() if remarks_match else ""
                clean_remarks = re.sub(r"<[^>]+>", "", raw_remarks).strip()
                
                if clean_remarks:
                    final_remarks = "\u8774\u8776\u5f71\u89c6 | %s" % clean_remarks
                else:
                    final_remarks = "\u8774\u8776\u5f71\u89c6"

                videos.append({
                    "vod_id": vod_id,
                    "vod_name": vod_name,
                    "vod_pic": vod_pic,
                    "vod_remarks": final_remarks
                })

            page_numbers = re.findall(r'/vodshow/[0-9\-]+?(\d+)---\.html', page_text)
            if page_numbers:
                page_count = max([int(x) for x in page_numbers if x.isdigit()] + [page_int])
            else:
                page_count = page_int + 1 if len(videos) >= 20 else page_int

            total_records = page_count * len(videos) if len(videos) > 0 else 0

        except Exception:
            pass

        return {
            "page": page_int,
            "pagecount": page_count,
            "limit": len(videos),
            "total": total_records,
            "list": videos
        }

    def detailContent(self, ids):
        target_id = ids[0] if isinstance(ids, list) and ids else str(ids)
        detail_url = "%s/voddetail/%s.html" % (self.site_url, target_id)
        
        detail_item = {
            "vod_id": str(target_id),
            "vod_name": "",
            "vod_pic": "",
            "type_name": "",
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": "\u8774\u8776\u5f71\u89c6",
            "vod_actor": "\U0001f98b TG\u7fa4: @tvshare23",
            "vod_director": "\U0001f98b \u8774\u8776\u5f71\u89c6",
            "vod_content": "",
            "vod_play_from": "",
            "vod_play_url": ""
        }

        try:
            code, raw_html = self._fetch(detail_url)
            page_text = html.unescape(raw_html)

            name_match = re.search(r'<h1[^>]*class=[\'"][^\'"]*title[^\'"]*[\'"][^>]*>([\s\S]*?)</h1>', page_text)
            if not name_match:
                name_match = re.search(r'<title>(.*?)</title>', page_text)
            if name_match:
                raw_name = re.sub(r"<[^>]+>", "", name_match.group(1)).strip()
                detail_item["vod_name"] = raw_name.split("-")[0].replace("\u5267\u60c5\u4ecb\u7ecd", "").strip()

            pic_match = re.search(r'<div[^>]*class=[\'"][^\'"]*stui-content__thumb[^\'"]*[\'"][\s\S]*?<img[^>]*data-original=[\'"]([^\'"]+)[\'"]', page_text)
            if not pic_match:
                pic_match = re.search(r'<div[^>]*class=[\'"][^\'"]*stui-content__thumb[^\'"]*[\'"][\s\S]*?<img[^>]*src=[\'"]([^\'"]+)[\'"]', page_text)
            if pic_match:
                pic_url = pic_match.group(1)
                if not pic_url.startswith("http"):
                    pic_url = urllib.parse.urljoin(self.site_url, pic_url)
                detail_item["vod_pic"] = pic_url

            real_desc = ""
            desc_patterns = [
                r'<span[^>]*class=[\'"][^\'"]*(?:detail-content|desc|data)[^\'"]*[\'"][^>]*>([\s\S]*?)</span>',
                r'<div[^>]*class=[\'"][^\'"]*stui-content__desc[^\'"]*[\'"][^>]*>([\s\S]*?)</div>',
                r'<p[^>]*class=[\'"][^\'"]*desc[^\'"]*[\'"][^>]*>([\s\S]*?)</p>'
            ]
            for pattern in desc_patterns:
                desc_match = re.search(pattern, page_text)
                if desc_match:
                    candidate = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()
                    if len(candidate) > len(real_desc):
                        real_desc = candidate

            official_notice = "\U0001f98b TG\u7fa4: @tvshare23\n\U0001f98b \u8774\u8776\u5f71\u89c6 \u72ec\u5bb6\u5b9a\u5236\n\n"
            if real_desc:
                detail_item["vod_content"] = official_notice + real_desc
            else:
                detail_item["vod_content"] = official_notice + "\u6682\u65e0\u5267\u60c5\u7b80\u4ecb"

            from_list = []
            url_list = []

            playlist_blocks = re.findall(r'<ul[^>]*class=[\'"][^\'"]*(?:stui-content__playlist|playlist)[^\'"]*[\'"][^>]*>([\s\S]*?)</ul>', page_text)
            if not playlist_blocks:
                playlist_blocks = re.findall(r'<ul[^>]*class=[\'"][^\'"]*clearfix[^\'"]*[\'"][^>]*>([\s\S]*?)</ul>', page_text)

            for idx, block in enumerate(playlist_blocks):
                episodes = re.findall(r'<a[^>]*href=[\'"]([^\'"]*?/vodplay/([^\'"]+)\.html)[\'"][^>]*>([\s\S]*?)</a>', block)
                if not episodes:
                    continue
                
                ep_strs = []
                for full_play_href, play_route, ep_name in episodes:
                    c_name = re.sub(r"<[^>]+>", "", ep_name).strip()
                    ep_strs.append("%s$%s" % (c_name, play_route))

                if ep_strs:
                    from_list.append("\u64ad\u653e\u7ebf\u8def %d" % (idx + 1))
                    url_list.append("#".join(ep_strs))

            if from_list:
                detail_item["vod_play_from"] = "$$$".join(from_list)
                detail_item["vod_play_url"] = "$$$".join(url_list)

        except Exception:
            pass

        return {"list": [detail_item]}

    def playerContent(self, flag, id, vipFlags):
        play_url = "%s/vodplay/%s.html" % (self.site_url, id)
        final_video_url = ""

        try:
            code, html_content = self._fetch(play_url)
            player_match = re.search(r'player_aaaa\s*=\s*(\{[\s\S]*?\})\s*</script>', html_content)
            if player_match:
                try:
                    pobj = json.loads(player_match.group(1))
                    if isinstance(pobj, dict) and pobj.get("url"):
                        raw_stream = pobj.get("url")
                        if raw_stream.startswith("http"):
                            final_video_url = raw_stream
                        else:
                            final_video_url = urllib.parse.unquote(raw_stream)
                except Exception:
                    pass

            if not final_video_url:
                streams = re.findall(r'[\'"](https?://[^\'"\s]+\.(?:m3u8|mp4)[^\'"\s]*)[\'"]', html_content)
                if streams:
                    final_video_url = streams[0]

        except Exception:
            pass

        if not final_video_url:
            final_video_url = play_url

        return {
            "parse": 0,
            "url": final_video_url,
            "header": self.headers
        }

    def searchContent(self, key, quick, pg="1"):
        page_int = int(pg) if str(pg).isdigit() else 1
        encoded_wd = urllib.parse.quote(key)
        if page_int <= 1:
            search_url = "%s/vodsearch/-------------.html?wd=%s" % (self.site_url, encoded_wd)
        else:
            search_url = "%s/vodsearch/%s----------%d---.html?wd=%s" % (self.site_url, encoded_wd, page_int, encoded_wd)

        videos = []
        try:
            code, raw_html = self._fetch(search_url)
            page_text = html.unescape(raw_html)

            card_blocks = re.findall(r'<li[^>]*class=[\'"][^\'"]*stui-vodlist__item[^\'"]*[\'"][^>]*>([\s\S]*?)</li>', page_text)
            if not card_blocks:
                card_blocks = re.findall(r'(<a[^>]*class=[\'"][^\'"]*stui-vodlist__thumb[^\'"]*[\'"][\s\S]*?</a>)', page_text)

            for block in card_blocks:
                id_match = re.search(r'href=[\'"][^\'"]*?/voddetail/(\d+)\.html[\'"]', block)
                if not id_match:
                    continue
                vod_id = id_match.group(1)

                name_match = re.search(r'title=[\'"]([^\'"]+)[\'"]', block)
                vod_name = name_match.group(1).strip() if name_match else ""

                pic_match = re.search(r'data-original=[\'"]([^\'"]+)[\'"]', block)
                if not pic_match:
                    pic_match = re.search(r'src=[\'"]([^\'"]+)[\'"]', block)
                vod_pic = pic_match.group(1) if pic_match else ""
                if vod_pic and not vod_pic.startswith("http"):
                    vod_pic = urllib.parse.urljoin(self.site_url, vod_pic)

                remarks_match = re.search(r'<span[^>]*class=[\'"][^\'"]*pic-text[^\'"]*[\'"][^>]*>([\s\S]*?)</span>', block)
                raw_remarks = remarks_match.group(1).strip() if remarks_match else ""
                clean_remarks = re.sub(r"<[^>]+>", "", raw_remarks).strip()
                
                if clean_remarks:
                    final_remarks = "\u8774\u8776\u5f71\u89c6 | %s" % clean_remarks
                else:
                    final_remarks = "\u8774\u8776\u5f71\u89c6"

                videos.append({
                    "vod_id": vod_id,
                    "vod_name": vod_name,
                    "vod_pic": vod_pic,
                    "vod_remarks": final_remarks
                })
        except Exception:
            pass

        return {
            "page": page_int,
            "pagecount": page_int + 1 if len(videos) >= 20 else page_int,
            "limit": len(videos),
            "total": len(videos),
            "list": videos
        }