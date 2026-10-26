# coding: utf-8
# \u8272\u732b\u89c6\u9891 - TVBox\u722c\u866b
# \u7ad9\u70b9: https://semao212.xyz/

import re
import json
import urllib.parse
from urllib.parse import quote

from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    def __init__(self):
        self.host = "https://semao212.xyz"
        self.site_name = "\u8272\u732b\u89c6\u9891"
        
        self.classes = [
            {"type_id": "96", "type_name": "\u56fd\u4ea7\u89c6\u9891"},
            {"type_id": "97", "type_name": "\u7f51\u66dd\u9ed1\u6599"},
            {"type_id": "103", "type_name": "\u771f\u5b9e\u4e71\u4f26"},
            {"type_id": "135", "type_name": "\u76f4\u64ad\u88f8\u804a"},
            {"type_id": "106", "type_name": "\u56fd\u4ea7\u4f20\u5a92"},
            {"type_id": "132", "type_name": "\u7cd6\u5fc3vlog"},
            {"type_id": "142", "type_name": "\u5c11\u5973\u841d\u8389"},
            {"type_id": "143", "type_name": "\u719f\u5973\u5c11\u5987"},
            {"type_id": "123", "type_name": "\u56fd\u4ea7\u81ea\u62cd"},
            {"type_id": "139", "type_name": "\u7fa4P\u6362\u59bb"},
            {"type_id": "144", "type_name": "\u9152\u5e97\u63a2\u82b1"},
            {"type_id": "141", "type_name": "\u5077\u62cd\u76d7\u6444"},
            {"type_id": "136", "type_name": "\u7efc\u5408\u5f3a\u7247"},
            {"type_id": "140", "type_name": "\u9189\u9152\u5f3a\u5978"},
            {"type_id": "138", "type_name": "\u6237\u5916\u91ce\u6218"},
            {"type_id": "137", "type_name": "\u5de8\u4e73\u8bf1\u60d1"},
            {"type_id": "131", "type_name": "\u660e\u661f\u6362\u8138"},
            {"type_id": "114", "type_name": "\u65e5\u97e9\u4e2d\u5b57"},
            {"type_id": "113", "type_name": "\u65e5\u97e9\u65e0\u7801"},
            {"type_id": "133", "type_name": "\u65e0\u7801\u7d20\u4eba"},
            {"type_id": "130", "type_name": "\u65e0\u7801\u7834\u89e3"},
            {"type_id": "121", "type_name": "\u6b27\u7f8e\u89c6\u9891"},
        ]
        
        self.filters = {str(c["type_id"]): [] for c in self.classes}
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": self.host + "/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    def getName(self):
        return "\u8272\u732b\u89c6\u9891"

    def getDependence(self):
        return []

    def init(self, extend=""):
        self.extend = extend or ""

    def homeContent(self, filter):
        return {"class": self.classes, "filters": self.filters if filter else {}}

    def getHomeContent(self, filter):
        return self.homeContent(filter)

    def homeVideoContent(self):
        html = self._fetch_html(self.host + "/")
        items = self._parse_video_list(html)
        return {"list": items[:15]}

    def categoryContent(self, tid, pg, filter, extend):
        pg = str(pg) if pg else "1"
        if pg == "1":
            url = f"{self.host}/index.php/vod/type/id/{tid}.html"
        else:
            url = f"{self.host}/index.php/vod/type/id/{tid}/page/{pg}.html"
        
        html = self._fetch_html(url)
        items = self._parse_video_list(html)
        page_count = self._parse_page_count(html)
        
        return {
            "list": items,
            "page": int(pg),
            "pagecount": page_count if page_count > 0 else 999,
            "limit": 20,
            "total": page_count * 20 if page_count > 0 else 9999,
        }

    def detailContent(self, ids):
        if not ids:
            return {"list": []}
        
        if isinstance(ids, list):
            vid = str(ids[0])
        else:
            vid = str(ids)
        
        # \u5148\u8bbf\u95ee\u8be6\u60c5\u9875\u63d0\u53d6\u6807\u9898\u548c\u56fe\u7247
        detail_url = f"{self.host}/index.php/vod/detail/id/{vid}.html"
        detail_html = self._fetch_html(detail_url)
        
        vod_name = f"视频{vid}"
        vod_pic = ""
        vod_content = ""
        vod_actor = ""
        vod_director = ""
        vod_remarks = ""
        
        if detail_html:
            # \u65b9\u6cd51: \u4ece <title> \u63d0\u53d6\u6807\u9898
            title_pattern = r'<title>([^<]+)</title>'
            title_match = re.search(title_pattern, detail_html)
            if title_match:
                title = title_match.group(1).strip()
                # \u53bb\u6389\u540e\u7f00 " - \u8272\u732b\u89c6\u9891"
                title = title.replace(' - \u8272\u732b\u89c6\u9891', '').strip()
                if title:
                    vod_name = title
            
            # \u65b9\u6cd52: \u4ece\u9875\u9762\u4e2d\u7684 h3 \u63d0\u53d6\u6807\u9898\uff08\u8be6\u60c5\u9875\u6807\u9898\u5728 h3 \u4e2d\uff09
            if vod_name == f"视频{vid}":
                title_pattern2 = r'<h3[^>]*>([^<]+)</h3>'
                title_match2 = re.search(title_pattern2, detail_html)
                if title_match2:
                    vod_name = title_match2.group(1).strip()
            
            # \u63d0\u53d6\u56fe\u7247 - \u67e5\u627e detail-cover \u4e2d\u7684 img
            pic_pattern = r'<div[^>]*class="[^"]*detail-cover[^"]*"[^>]*>.*?<img[^>]*src="([^"]+)"'
            pic_match = re.search(pic_pattern, detail_html, re.DOTALL)
            if not pic_match:
                # \u76f4\u63a5\u67e5\u627e img \u6807\u7b7e
                pic_pattern2 = r'<img[^>]*src="([^"]+)"[^>]*>'
                pic_match = re.search(pic_pattern2, detail_html)
            if pic_match:
                vod_pic = pic_match.group(1)
                vod_pic = vod_pic.replace('&quot;', '').strip('"\'')
                if vod_pic.startswith('//'):
                    vod_pic = 'https:' + vod_pic
                elif vod_pic.startswith('/'):
                    vod_pic = self.host + vod_pic
        
        # \u83b7\u53d6\u64ad\u653e\u94fe\u63a5
        play_url = f"{self.host}/index.php/vod/play/id/{vid}/sid/1/nid/1.html"
        html = self._fetch_html(play_url)
        m3u8_url = self._extract_m3u8_from_html(html)
        
        if m3u8_url:
            vod = {
                "vod_id": vid,
                "vod_name": vod_name,
                "vod_pic": vod_pic,
                "vod_remarks": vod_remarks,
                "vod_actor": vod_actor,
                "vod_director": vod_director,
                "vod_content": vod_content,
                "vod_play_from": "\u64ad\u653e",
                "vod_play_url": f"播放${m3u8_url}",
            }
        else:
            vod = {
                "vod_id": vid,
                "vod_name": vod_name,
                "vod_pic": vod_pic,
                "vod_remarks": vod_remarks,
                "vod_actor": vod_actor,
                "vod_director": vod_director,
                "vod_content": vod_content,
                "vod_play_from": "\u64ad\u653e",
                "vod_play_url": f"播放${play_url}",
            }
        
        return {"list": [vod]}
    def searchContent(self, key, quick, pg="1"):
        if not key:
            return {"list": [], "page": 1}
        
        pg = str(pg) if pg else "1"
        encoded_key = quote(key)
        url = f"{self.host}/index.php/vod/search/wd/{encoded_key}.html"
        if pg != "1":
            url = f"{self.host}/index.php/vod/search/page/{pg}/wd/{encoded_key}.html"
        
        html = self._fetch_html(url)
        items = self._parse_video_list(html)
        return {"list": items, "page": int(pg)}

    def playerContent(self, flag, id, vipFlags):
        if not id:
            return {"parse": 1, "url": "", "header": self.headers}
        
        # \u5982\u679c\u5df2\u7ecf\u662f m3u8 \u94fe\u63a5\uff0c\u76f4\u63a5\u8fd4\u56de
        if id.startswith("http") and ".m3u8" in id:
            return {
                "parse": 0,
                "url": id,
                "header": {
                    "User-Agent": self.headers.get("User-Agent", ""),
                    "Referer": self.host + "/",
                }
            }
        
        # \u5982\u679c\u662f\u64ad\u653e\u9875URL\uff0c\u6293\u53d6\u9875\u9762\u63d0\u53d6m3u8
        if id.startswith("http"):
            html = self._fetch_html(id)
            m3u8_url = self._extract_m3u8_from_html(html)
            if m3u8_url:
                return {
                    "parse": 0,
                    "url": m3u8_url,
                    "header": {
                        "User-Agent": self.headers.get("User-Agent", ""),
                        "Referer": self.host + "/",
                    }
                }
            return {"parse": 1, "url": id, "header": self.headers}
        
        # \u5982\u679c\u662f vod_id\uff0c\u6784\u9020\u64ad\u653e\u9875URL
        play_url = f"{self.host}/index.php/vod/play/id/{id}/sid/1/nid/1.html"
        html = self._fetch_html(play_url)
        m3u8_url = self._extract_m3u8_from_html(html)
        if m3u8_url:
            return {
                "parse": 0,
                "url": m3u8_url,
                "header": {
                    "User-Agent": self.headers.get("User-Agent", ""),
                    "Referer": self.host + "/",
                }
            }
        
        return {"parse": 1, "url": play_url, "header": self.headers}

    def recommendContent(self, ids, pg):
        """
        \u76f8\u5173\u63a8\u8350\u63a5\u53e3 - \u6839\u636e\u5f53\u524d\u89c6\u9891ID\u83b7\u53d6\u540c\u7c7b\u63a8\u8350
        """
        try:
            if not ids:
                return {"list": []}
            vid = str(ids[0]) if isinstance(ids, list) else str(ids)
            
            # \u83b7\u53d6\u5f53\u524d\u89c6\u9891\u8be6\u60c5
            detail_result = self.detailContent([vid])
            detail_list = detail_result.get("list", [])
            if not detail_list:
                return {"list": []}
            
            vod_name = detail_list[0].get("vod_name", "")
            
            page = max(1, int(pg or 1))
            limit = 18
            seen = set()
            videos = []
            
            # \u76f4\u63a5\u7528\u89c6\u9891\u6807\u9898\u641c\u7d22\uff08\u53d6\u524d6\u4e2a\u5b57\u7b26\uff09
            keyword = vod_name[:6].strip()
            if keyword and len(keyword) > 2:
                search_result = self.searchContent(keyword, 0, str(page))
                search_list = search_result.get("list", [])
                for item in search_list:
                    item_id = item.get("vod_id", "")
                    if item_id and item_id != vid and item_id not in seen:
                        seen.add(item_id)
                        videos.append(item)
                        if len(videos) >= limit:
                            break
            
            # \u5982\u679c\u641c\u7d22\u7ed3\u679c\u4e0d\u8db3\uff0c\u7528\u5206\u7c7b\u63a8\u8350
            if len(videos) < 6:
                # \u5c1d\u8bd5\u83b7\u53d6\u5206\u7c7bID
                tid = "96"  # \u9ed8\u8ba4\u56fd\u4ea7\u89c6\u9891
                category_result = self.categoryContent(tid, str(page), {}, {})
                category_list = category_result.get("list", [])
                for item in category_list:
                    item_id = item.get("vod_id", "")
                    if item_id and item_id != vid and item_id not in seen:
                        seen.add(item_id)
                        videos.append(item)
                        if len(videos) >= limit:
                            break
            
            # \u515c\u5e95\uff1a\u9996\u9875\u63a8\u8350
            if len(videos) < 4:
                home_result = self.homeVideoContent()
                home_list = home_result.get("list", [])
                for item in home_list:
                    item_id = item.get("vod_id", "")
                    if item_id and item_id != vid and item_id not in seen:
                        seen.add(item_id)
                        videos.append(item)
                        if len(videos) >= limit:
                            break
            
            return {"list": videos[:limit]}
            
        except Exception as e:
            if hasattr(self, 'log'):
                self.log('[recommendContent] \u5f02\u5e38: %s' % e)
            return {"list": []}
    def destroy(self):
        pass

    def _fetch_html(self, url):
        try:
            resp = self.fetch(url, headers=self.headers, timeout=15)
            if resp and hasattr(resp, "status_code") and resp.status_code == 200:
                return resp.text
            if resp and hasattr(resp, "text"):
                return resp.text
        except Exception as e:
            self.log(f"fetch error: {e}")
        return ""

    def _parse_video_list(self, html):
        items = []
        if not html:
            return items
        
        # \u5339\u914d\u89c6\u9891\u5361\u7247\u7ed3\u6784
        pattern = r'<li[^>]*class="[^"]*content-item[^"]*"[^>]*>.*?<a[^>]*href="[^"]*detail/id/(\d+)\.html[^"]*"[^>]*style="background-image:\s*url\([\'"]?([^\'"]+)[\'"]?\)"[^>]*>.*?<span[^>]*class="note[^"]*"[^>]*>(.*?)</span>.*?<h5[^>]*class="[^"]*video-title[^"]*"[^>]*>.*?<a[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html, re.DOTALL)
        
        seen = set()
        for vid, pic, date, title in matches:
            if vid in seen:
                continue
            title = title.strip()
            if re.match(r'^\d{4}-\d{2}-\d{2}$', title):
                continue
            if not title or len(title) < 2:
                continue
            seen.add(vid)
            # \u6e05\u7406\u56fe\u7247URL
            pic = pic.replace('&quot;', '').strip('"\'')
            if pic.startswith('//'):
                pic = 'https:' + pic
            elif pic.startswith('/'):
                pic = self.host + pic
            items.append({
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": date,
            })
        
        # \u56de\u9000\u65b9\u6cd5\uff1a\u76f4\u63a5\u63d0\u53d6\u56fe\u7247\u548c\u6807\u9898
        if not items:
            # \u63d0\u53d6\u89c6\u9891\u9879
            li_pattern = r'<li[^>]*class="[^"]*content-item[^"]*"[^>]*>(.*?)</li>'
            li_matches = re.findall(li_pattern, html, re.DOTALL)
            for li_html in li_matches:
                # \u63d0\u53d6ID
                id_match = re.search(r'detail/id/(\d+)\.html', li_html)
                if not id_match:
                    continue
                vid = id_match.group(1)
                if vid in seen:
                    continue
                # \u63d0\u53d6\u56fe\u7247
                pic_match = re.search(r'background-image:\s*url\([\'"]?([^\'"]+)[\'"]?\)', li_html)
                pic = ""
                if pic_match:
                    pic = pic_match.group(1).replace('&quot;', '').strip('"\'')
                if pic.startswith('//'):
                    pic = 'https:' + pic
                elif pic.startswith('/'):
                    pic = self.host + pic
                # \u63d0\u53d6\u6807\u9898
                title_match = re.search(r'<h5[^>]*>.*?<a[^>]*>([^<]+)</a>', li_html, re.DOTALL)
                title = title_match.group(1).strip() if title_match else f"视频{vid}"
                # \u63d0\u53d6\u65e5\u671f
                date_match = re.search(r'<span[^>]*class="note[^"]*"[^>]*>(.*?)</span>', li_html)
                date = date_match.group(1).strip() if date_match else ""
                seen.add(vid)
                items.append({
                    "vod_id": vid,
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": date,
                })
        
        return items
    def _parse_page_count(self, html):
        if not html:
            return 1
        
        # \u4ece\u9875\u9762\u4e2d\u63d0\u53d6\u603b\u9875\u6570
        pattern = '<a[^>]*>(\\d+)</a>[^<]*<a[^>]*>.*?\u4e0b\u4e00\u9875'
        matches = re.findall(pattern, html)
        if matches:
            try:
                return int(matches[-1])
            except:
                pass
        
        # \u4ece"\u5c3e\u9875"\u94fe\u63a5\u63d0\u53d6
        pattern2 = '<a[^>]*href="[^"]*/page/(\\d+)\\.html"[^>]*>\u5c3e\u9875</a>'
        match = re.search(pattern2, html)
        if match:
            try:
                return int(match.group(1))
            except:
                pass
        
        return 999

    def _extract_m3u8_from_html(self, html):
        if not html:
            return None
        
        # \u65b9\u6cd51: \u4ece player_aaaa \u5bf9\u8c61\u4e2d\u63d0\u53d6 (\u53c2\u8003\u738b\u5ba4\u65e5\u62a5)
        pattern = r'var\s+player_aaaa\s*=\s*(\{[^;]+\});'
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                url = data.get("url", "")
                if url and url.startswith("http") and (".m3u8" in url or ".mp4" in url):
                    return url
            except:
                pass
        
        # \u65b9\u6cd52: \u76f4\u63a5\u63d0\u53d6url\u5b57\u6bb5
        pattern2 = r'"url"\s*:\s*"([^"]+\.m3u8[^"]*)"'
        match2 = re.search(pattern2, html)
        if match2:
            url = match2.group(1)
            if url and url.startswith("http"):
                return url
        
        # \u65b9\u6cd53: \u67e5\u627e\u4efb\u4f55m3u8\u94fe\u63a5
        pattern3 = r'https?://[^"\']+\.m3u8[^"\']*'
        match3 = re.search(pattern3, html)
        if match3:
            return match3.group(0)
        
        return None