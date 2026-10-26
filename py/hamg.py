# -*- coding: utf-8 -*-
"""
\u54c8\u5bc6\u74dc\u52a8\u6f2b (hmgdm.com) \u722c\u866b - \u589e\u5f3a\u7248\uff08\u4fee\u590d\u201c\u5927\u5bb6\u5728\u770b\u201d\u65e0\u6570\u636e\uff09
- \u4fee\u590d watched \u5206\u7c7b\u6570\u636e\u63a5\u53e3\u8def\u5f84
- \u5206\u7c7b\u5217\u8868\u6bcf\u9875\u6700\u591a 40 \u6761\uff08\u5982\u679c API \u652f\u6301\uff09
- \u9996\u9875\u63a8\u8350\u6bcf\u7c7b\u53d6 15 \u6761\uff0c\u603b\u4e0a\u9650 80 \u6761
- \u5267\u96c6\u4ece\u7b2c 1 \u96c6\u5f00\u59cb\u6392\u5e8f
- \u9002\u914d TVBox / \u5f71\u89c6\u4ed3
"""

import re
import json
import logging
import urllib.parse
import os
import sys
import time
import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from base.spider import Spider as BaseSpider
except ImportError:
    BaseSpider = object

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Spider(BaseSpider):
    """\u54c8\u5bc6\u74dc\u52a8\u6f2b\u722c\u866b - \u589e\u5f3a\u7248\uff08\u4fee\u590d watched\uff09"""

    BASE_URL = "https://hmgdm.com"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; SM-S908U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://hmgdm.com/",
        "Connection": "keep-alive",
    }

    # \u5206\u7c7b\u6620\u5c04
    CATEGORY_MAP = {
        "watched": {"name": "\u5927\u5bb6\u5728\u770b", "type": "watched"},
        "rhdm":    {"name": "\u65e5\u672c\u52a8\u6f2b", "type": "rhdm"},
        "gcdm":    {"name": "\u56fd\u4ea7\u52a8\u6f2b", "type": "gcdm"},
        "omdm":    {"name": "\u6b27\u7f8e\u52a8\u6f2b", "type": "omdm"},
        "dmdy":    {"name": "\u52a8\u6f2b\u7535\u5f71", "type": "dmdy"},
        "dtmh":    {"name": "\u52a8\u6001\u6f2b\u753b", "type": "dtmh"},
    }

    def __init__(self):
        try:
            super().__init__()
        except Exception:
            pass
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.session.verify = False
        self._cache = {}
        self._cache_ttl = 300

    def init(self, extend=""):
        pass

    def getName(self):
        return "\u54c8\u5bc6\u74dc\u52a8\u6f2b"

    def _get_json(self, url, params=None):
        """\u8bf7\u6c42 JSON \u63a5\u53e3"""
        try:
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.warning(f"JSON请求失败: {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"JSON请求异常: {e}")
            return None

    def _get_html(self, url, params=None):
        """\u8bf7\u6c42 HTML \u9875\u9762\uff08\u5907\u7528\uff09"""
        try:
            resp = self.session.get(url, params=params, timeout=15)
            resp.encoding = "utf-8"
            return resp.text
        except Exception as e:
            logger.error(f"HTML请求失败: {e}")
            return None

    def _fix_pic(self, url):
        if not url:
            return ""
        if url.startswith("//"):
            return "https:" + url
        if url.startswith("/"):
            return self.BASE_URL + url
        if not url.startswith("http"):
            return self.BASE_URL + "/" + url
        return url

    def _parse_api_item(self, item):
        vod_id = str(item.get("id", ""))
        if not vod_id:
            return None
        return {
            "vod_id": vod_id,
            "vod_name": item.get("name", ""),
            "vod_pic": self._fix_pic(item.get("pic", "")),
            "vod_remarks": item.get("remarks", "\u8fde\u8f7d\u4e2d"),
        }

    # ==================== \u9996\u9875 ====================
    def homeContent(self, filter=False):
        result = {"class": [], "list": [], "filters": {}}

        # \u5206\u7c7b\u5217\u8868
        classes = []
        for cid, cinfo in self.CATEGORY_MAP.items():
            classes.append({
                "type_id": cid,
                "type_name": cinfo["name"],
            })
        result["class"] = classes

        # \u9996\u9875\u63a8\u8350\uff1a\u4ece\u591a\u4e2a\u5206\u7c7b\u5404\u53d6\u66f4\u591a\u6761\u76ee\uff08\u6bcf\u7c7b15\u6761\uff09\uff0c\u603b\u4e0a\u965080\u6761
        all_items = []
        # \u4f18\u5148\u4ece\u201c\u52a8\u6f2b\u7535\u5f71\u201d\u548c\u201c\u65e5\u672c\u52a8\u6f2b\u201d\u83b7\u53d6
        for cid in ["dmdy", "rhdm", "gcdm", "omdm"]:
            data = self._get_json(f"{self.BASE_URL}/data/type/{cid}", params={"page": 1})
            if data and isinstance(data, list):
                for item in data[:15]:
                    parsed = self._parse_api_item(item)
                    if parsed and parsed["vod_name"]:
                        if not any(x["vod_name"] == parsed["vod_name"] for x in all_items):
                            all_items.append(parsed)
                if len(all_items) >= 80:
                    break

        result["list"] = all_items[:80]
        return result

    def homeVideoContent(self):
        return self.homeContent()

    # ==================== \u5206\u7c7b ====================
    def categoryContent(self, tid, pg, filter, extend):
        try:
            page = int(pg) if pg else 1
            type_id = str(tid)

            if type_id not in self.CATEGORY_MAP:
                return {"list": [], "page": page, "pagecount": 1, "limit": 20, "total": 0}

            # \u9488\u5bf9\u4e0d\u540c\u7684\u5206\u7c7b\u4f7f\u7528\u4e0d\u540c\u7684 API \u8def\u5f84
            if type_id == "watched":
                # \u201c\u5927\u5bb6\u5728\u770b\u201d \u4f7f\u7528 /data/watched
                url = f"{self.BASE_URL}/data/watched"
            else:
                # \u5176\u4ed6\u5206\u7c7b\u4f7f\u7528 /data/type/{type_id}
                url = f"{self.BASE_URL}/data/type/{type_id}"

            params = {"page": page, "limit": 40}  # \u5c1d\u8bd5\u6bcf\u987540\u6761

            data = self._get_json(url, params=params)

            if not data or not isinstance(data, list):
                # \u5982\u679c API \u5931\u8d25\uff0c\u964d\u7ea7\u5230 HTML \u89e3\u6790\uff08\u53ea\u652f\u6301\u7b2c\u4e00\u9875\uff09
                if page == 1:
                    html_url = f"{self.BASE_URL}/type/{type_id}" if type_id != "watched" else f"{self.BASE_URL}/watched"
                    html = self._get_html(html_url)
                    if html:
                        videos = self._parse_video_list_html(html)
                        return {
                            "list": videos,
                            "page": page,
                            "pagecount": 1,
                            "limit": len(videos),
                            "total": len(videos),
                        }
                return {"list": [], "page": page, "pagecount": 1, "limit": 20, "total": 0}

            # \u89e3\u6790 JSON \u6570\u636e
            videos = []
            for item in data:
                parsed = self._parse_api_item(item)
                if parsed:
                    videos.append(parsed)

            pagecount = page + 1 if videos else page
            actual_limit = len(videos) if videos else 20

            return {
                "list": videos,
                "page": page,
                "pagecount": pagecount,
                "limit": actual_limit,
                "total": len(videos) * pagecount,
            }
        except Exception as e:
            logger.error(f"获取分类内容失败: {e}")
            return {"list": [], "page": 1, "pagecount": 1, "limit": 20, "total": 0}

    def _parse_video_list_html(self, html):
        """\u4ece HTML \u89e3\u6790\u89c6\u9891\u5217\u8868\uff08\u5907\u7528\uff09"""
        videos = []
        soup = BeautifulSoup(html, 'html.parser')
        video_links = soup.find_all('a', class_='video')
        for link in video_links:
            href = link.get('href', '')
            vid_match = re.search(r'/details/(\d+)', href)
            if not vid_match:
                continue
            vid = vid_match.group(1)
            title = ''
            title_div = link.find('div', class_='title')
            if title_div:
                p_tag = title_div.find('p')
                if p_tag:
                    title = p_tag.get_text(strip=True)
            pic = ''
            img_box = link.find('div', class_='img-box')
            if img_box:
                pic = img_box.get('data', '')
                if not pic:
                    style = img_box.get('style', '')
                    bg_match = re.search(r'background-image:\s*url\(([^)]+)\)', style)
                    if bg_match:
                        pic = bg_match.group(1).strip()
                        pic = pic.strip('"\'')
                if pic:
                    pic = self._fix_pic(pic)
            remarks = ''
            desc_div = link.find('div', class_='desc')
            if desc_div:
                desc_p = desc_div.find_all('div')
                if len(desc_p) >= 2:
                    remarks = desc_p[1].get_text(strip=True)
            if title:
                videos.append({
                    "vod_id": vid,
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": remarks or "\u8fde\u8f7d\u4e2d",
                })
        return videos

    # ==================== \u8be6\u60c5 ====================
    def detailContent(self, ids):
        try:
            vod_id = ids[0] if isinstance(ids, list) else str(ids)
            url = f"{self.BASE_URL}/details/{vod_id}"
            html = self._get_html(url)
            if not html:
                return {"list": []}

            soup = BeautifulSoup(html, 'html.parser')

            title = ''
            title_tag = soup.find('h1')
            if title_tag:
                title = title_tag.get_text(strip=True)

            poster = ''
            img_box = soup.find('div', class_='img-box')
            if img_box:
                poster = img_box.get('data', '')
                if not poster:
                    style = img_box.get('style', '')
                    bg_match = re.search(r'background-image:\s*url\(([^)]+)\)', style)
                    if bg_match:
                        poster = bg_match.group(1).strip()
                        poster = poster.strip('"\'')
                poster = self._fix_pic(poster)

            content = ''
            desc_div = soup.find('div', class_='player-desc')
            if desc_div:
                content = desc_div.get_text(strip=True)

            play_from_list, play_url_list = self._parse_episodes(html, vod_id)

            vod_item = {
                "vod_id": vod_id,
                "vod_name": title or f"动漫{vod_id}",
                "vod_pic": poster,
                "type_name": "\u52a8\u6f2b",
                "vod_year": "",
                "vod_area": "",
                "vod_remarks": "",
                "vod_actor": "",
                "vod_director": "",
                "vod_content": content or "\u6682\u65e0\u7b80\u4ecb",
                "vod_play_from": "$$$".join(play_from_list) if play_from_list else "\u9ed8\u8ba4\u7ebf\u8def",
                "vod_play_url": "$$$".join(play_url_list) if play_url_list else "",
            }

            return {"list": [vod_item]}
        except Exception as e:
            logger.error(f"获取详情失败: {e}")
            return {"list": []}

    def _parse_episodes(self, html, vod_id):
        play_from_list = []
        play_url_list = []

        # \u65b9\u6cd51: \u89e3\u6790 episodesData
        pattern = r'const\s+episodesData\s*=\s*({[^;]+});'
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                json_str = match.group(1)
                json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
                json_str = re.sub(r'(\w+):', r'"\1":', json_str)
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                episodes_data = json.loads(json_str)

                for line_name, episodes in episodes_data.items():
                    if not episodes:
                        continue
                    urls = []
                    for ep in episodes:
                        path = ep.get('path', '')
                        name = ep.get('name', '')
                        if path:
                            full_url = self.BASE_URL + path
                            urls.append(f"{name}${full_url}")
                    if urls:
                        urls.sort(key=lambda x: self._extract_episode_num(x))
                        play_from_list.append(line_name)
                        play_url_list.append("#".join(urls))
            except Exception as e:
                logger.error(f"解析episodesData失败: {e}")

        # \u65b9\u6cd52: DOM \u63d0\u53d6
        if not play_from_list:
            soup = BeautifulSoup(html, 'html.parser')
            playlist_div = soup.find('div', id='playlist')
            if playlist_div:
                links = playlist_div.find_all('a')
                if links:
                    urls = []
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        if href and text:
                            full_url = self.BASE_URL + href if href.startswith('/') else href
                            urls.append(f"{text}${full_url}")
                    if urls:
                        urls.sort(key=lambda x: self._extract_episode_num(x))
                        play_from_list.append("\u9ed8\u8ba4\u7ebf\u8def")
                        play_url_list.append("#".join(urls))

        # \u65b9\u6cd53: \u6b63\u5219\u63d0\u53d6
        if not play_from_list:
            pattern = r'href=["\'](/player/' + vod_id + r'/\d+)["\'][^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html)
            if matches:
                urls = []
                seen = set()
                for path, name in matches:
                    if path not in seen:
                        seen.add(path)
                        full_url = self.BASE_URL + path
                        urls.append(f"{name}${full_url}")
                if urls:
                    urls.sort(key=lambda x: self._extract_episode_num(x))
                    play_from_list.append("\u9ed8\u8ba4\u7ebf\u8def")
                    play_url_list.append("#".join(urls))

        return play_from_list, play_url_list

    def _extract_episode_num(self, url_str):
        match = re.search('\u7b2c(\\d+)\u96c6', url_str)
        if match:
            return int(match.group(1))
        match = re.search(r'/(\d+)\$', url_str)
        if match:
            return int(match.group(1))
        match = re.search(r'^(\d+)\$', url_str)
        if match:
            return int(match.group(1))
        return 0

    # ==================== \u64ad\u653e ====================
    def playerContent(self, flag, id, vipFlags):
        try:
            play_url = urllib.parse.unquote(id) if id else ''

            if '/player/' in play_url or '/play/' in play_url:
                resp = self.session.get(play_url, timeout=15)
                if resp and resp.status_code == 200:
                    html = resp.text

                    pattern = r'initDplayer\s*\(\s*["\']([^"\']+\.m3u8[^"\']*)["\']'
                    match = re.search(pattern, html)
                    if match:
                        video_url = match.group(1)
                        return {
                            "parse": 0,
                            "playUrl": "",
                            "url": video_url,
                            "header": json.dumps({
                                "User-Agent": self.HEADERS["User-Agent"],
                                "Referer": self.BASE_URL + "/",
                            }),
                        }

                    m3u8_match = re.search(r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)', html)
                    if m3u8_match:
                        return {
                            "parse": 0,
                            "playUrl": "",
                            "url": m3u8_match.group(1),
                            "header": json.dumps({
                                "User-Agent": self.HEADERS["User-Agent"],
                                "Referer": self.BASE_URL + "/",
                            }),
                        }

                    iframe_match = re.search(r'<iframe[^>]*src=["\']([^"\']+)["\']', html)
                    if iframe_match:
                        iframe_url = iframe_match.group(1)
                        if iframe_url.startswith('//'):
                            iframe_url = 'https:' + iframe_url
                        return {
                            "parse": 1,
                            "playUrl": "",
                            "url": iframe_url,
                            "header": json.dumps({
                                "User-Agent": self.HEADERS["User-Agent"],
                                "Referer": self.BASE_URL + "/",
                            }),
                        }

            return {
                "parse": 0,
                "playUrl": "",
                "url": play_url,
                "header": json.dumps({
                    "User-Agent": self.HEADERS["User-Agent"],
                    "Referer": self.BASE_URL + "/",
                }),
            }
        except Exception as e:
            logger.error(f"解析播放失败: {e}")
            return {"parse": 0, "playUrl": "", "url": ""}

    # ==================== \u641c\u7d22 ====================
    def searchContent(self, key, quick, pg="1"):
        try:
            page = int(pg) if pg else 1
            encoded_key = urllib.parse.quote(key)

            url = f"{self.BASE_URL}/data/search"
            data = self._get_json(url, params={"kw": key, "page": page})

            if data and isinstance(data, list):
                videos = []
                for item in data:
                    parsed = self._parse_api_item(item)
                    if parsed:
                        videos.append(parsed)
                return {
                    "list": videos,
                    "page": page,
                    "pagecount": 1,
                    "limit": len(videos),
                    "total": len(videos),
                }

            # \u964d\u7ea7\u5230 HTML
            html_url = f"{self.BASE_URL}/search?kw={encoded_key}&page={page}"
            html = self._get_html(html_url)
            if html:
                videos = self._parse_video_list_html(html)
                return {
                    "list": videos,
                    "page": page,
                    "pagecount": 1,
                    "limit": len(videos),
                    "total": len(videos),
                }
            return {"list": [], "page": page, "pagecount": 1, "limit": 20, "total": 0}
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return {"list": [], "page": 1, "pagecount": 1, "limit": 20, "total": 0}

    def isVideoFormat(self, url):
        video_formats = ['.m3u8', '.mp4', '.ts', '.flv', '.avi', '.mkv']
        return any(url.lower().endswith(fmt) for fmt in video_formats)

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def localProxy(self, params):
        pass


if __name__ == "__main__":
    spider = Spider()
    print("\u6d4b\u8bd5\u201c\u5927\u5bb6\u5728\u770b\u201d\u5206\u7c7b:")
    watched = spider.categoryContent("watched", 1, {}, {})
    print(f"获取到 {len(watched.get('list', []))} 条数据")
    for item in watched['list'][:5]:
        print(f"  - {item['vod_name']} ({item['vod_remarks']})")