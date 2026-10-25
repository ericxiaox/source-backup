# coding=utf-8
import sys
import json
import re
import requests
import base64
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin

try:
    from base.spider import Spider as BaseSpider
except ImportError:
    class BaseSpider():
        def fetch(self, url, headers=None, timeout=10):
            try:
                res = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
                res.encoding = 'utf-8'
                return res
            except Exception as e:
                print(f"fetch error: {e}")
                return None

class Spider(BaseSpider):
    def getName(self):
        return "\u64b8\u4e00\u5929"

    def init(self, extend=""):
        self.host = "https://luyitian.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })

    def homeVideoContent(self):
        return {"list": []}

    def localProxy(self, params):
        return [200, "video/MP2T", ""]

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def fetch(self, url, headers=None, timeout=5):
        try:
            req_headers = headers or self.session.headers
            res = self.session.get(url, headers=req_headers, timeout=timeout, allow_redirects=True)
            res.encoding = 'utf-8'
            return res
        except Exception as e:
            print(f"fetch error: {e}")
            return None

    def _get_topic_filters(self):
        """
        \u4ece /topic/ \u9875\u9762\u63d0\u53d6\u6240\u6709\u4e13\u9898\u5165\u53e3\uff0c\u751f\u6210\u5b50\u5206\u7c7b\u5217\u8868\u3002
        \u9002\u914d\u771f\u5b9e URL\uff1a/topicdetail-7/
        """
        url = f"{self.host}/topic/"
        res = self.fetch(url, timeout=5)
        if not res:
            return []
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # \u4e13\u95e8\u5339\u914d /topicdetail- \u94fe\u63a5
        topic_links = soup.select('a[href*="/topicdetail-"]')
        if not topic_links:
            # \u515c\u5e95\uff1a\u53ef\u80fd\u5199\u6210 /topicdetail/ \u683c\u5f0f
            topic_links = soup.select('a[href*="/topicdetail"]')
        
        filters = []
        seen = set()
        for a in topic_links:
            href = a.get('href', '')
            # \u63d0\u53d6\u6570\u5b57 ID\uff08\u4f8b\u5982 /topicdetail-7/\uff09
            match = re.search(r'/topicdetail-(\d+)', href)
            if not match:
                match = re.search(r'/topicdetail/(\d+)', href)
            if not match:
                continue
            tid = match.group(1)
            name = a.get_text(strip=True) or a.get('title', '') or f"专题{tid}"
            if len(name) < 2:
                continue
            if tid not in seen:
                seen.add(tid)
                filters.append({"n": name, "v": tid})
        return filters

    def homeContent(self, filter):
        classes = [
            {"type_name": "\u6700\u8fd1\u66f4\u65b0", "type_id": "new"},
            {"type_name": "\u70ed\u95e8\u5f71\u7247", "type_id": "hot"},
            {"type_name": "\u5f71\u7247\u4e13\u9898", "type_id": "topic"},
            {"type_name": "\u4e2d\u6587\u5b57\u5e55", "type_id": "28"},
            {"type_name": "\u56fd\u4ea7", "type_id": "20"},
            {"type_name": "\u65e5\u672c\u6709\u7801", "type_id": "21"},
            {"type_name": "\u65e5\u672c\u65e0\u7801", "type_id": "22"},
            {"type_name": "\u6b27\u7f8e", "type_id": "23"},
            {"type_name": "\u52a8\u6f2b", "type_id": "24"},
            {"type_name": "\u4f26\u7406", "type_id": "25"},
            {"type_name": "\u97e9\u56fd", "type_id": "36"},
            {"type_name": "\u53e6\u7c7b", "type_id": "41"}
        ]

        filters = {
            "28": [{"key": "tid", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": "28"},
                {"n": "\u65e5\u672c\u4e2d\u5b57", "v": "51"}
            ]}],
            "20": [{"key": "tid", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": "20"},
                {"n": "\u56fd\u4ea7\u7cbe\u54c1", "v": "26"},
                {"n": "\u56fd\u4ea7\u5267\u60c5", "v": "27"},
                {"n": "\u56fd\u4ea7\u81ea\u62cd", "v": "29"},
                {"n": "\u56fd\u4ea7\u4e3b\u64ad", "v": "35"},
                {"n": "\u56fd\u6a21\u79c1\u62cd", "v": "85"},
                {"n": "\u7f51\u7ea2\u660e\u661f", "v": "91"},
                {"n": "\u56fd\u4ea7SM", "v": "105"},
                {"n": "\u53f0\u6e7e\u8fa3\u59b9", "v": "107"},
                {"n": "\u9999\u6e2f\u6b63\u59b9", "v": "108"}
            ]}],
            "21": [{"key": "tid", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": "21"},
                {"n": "\u4eba\u59bb", "v": "31"},
                {"n": "\u7d20\u4eba", "v": "44"},
                {"n": "\u53e3\u7206\u989c\u5c04", "v": "46"},
                {"n": "\u841d\u8389\u5c11\u5973", "v": "47"},
                {"n": "\u7f8e\u4e73\u5de8\u4e73", "v": "48"},
                {"n": "\u5236\u670d\u8bf1\u60d1", "v": "52"},
                {"n": "\u8c03\u6559", "v": "57"},
                {"n": "\u51fa\u8f68", "v": "58"},
                {"n": "\u6709\u7801\u7cbe\u54c1", "v": "101"}
            ]}],
            "22": [{"key": "tid", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": "22"},
                {"n": "\u65e0\u7801\u7cbe\u54c1", "v": "102"}
            ]}],
            "23": [{"key": "tid", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": "23"},
                {"n": "\u6b27\u7f8e\u7cbe\u54c1", "v": "104"}
            ]}],
            "24": [{"key": "tid", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": "24"},
                {"n": "\u52a8\u6f2b\u7cbe\u54c1", "v": "103"}
            ]}],
            "25": [{"key": "tid", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": "25"},
                {"n": "\u7efc\u5408\u4e09\u7ea7", "v": "39"}
            ]}],
            "36": [{"key": "tid", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": "36"},
                {"n": "\u97e9\u56fd\u4e3b\u64ad", "v": "37"}
            ]}],
            "41": [{"key": "tid", "name": "\u5b50\u5206\u7c7b", "value": [
                {"n": "\u5168\u90e8", "v": "41"},
                {"n": "Cosplay", "v": "106"}
            ]}]
        }

        # \u52a8\u6001\u6ce8\u5165\u4e13\u9898\u5b50\u5206\u7c7b\uff08\u4f8b\u5982\uff1a2018\u5fc5\u770b\u30012019\u5fc5\u770b...\uff09
        topic_values = self._get_topic_filters()
        if topic_values:
            filters["topic"] = [{
                "key": "tid",
                "name": "\u4e13\u9898",
                "value": topic_values
            }]

        return {'class': classes, 'filters': filters}

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {"list": [], "page": pg, "pagecount": 999, "limit": 20, "total": 9999}

        real_tid = extend.get('tid', tid)
        soup = None

        # ---------- \u5f71\u7247\u4e13\u9898\u4e0b\u7684\u5177\u4f53\u4e13\u9898\uff08/topicdetail-7/\uff09 ----------
        if real_tid.isdigit() and tid == "topic":
            urls_to_try = [
                f"{self.host}/topicdetail-{real_tid}/",
                f"{self.host}/topicdetail-{real_tid}.html",
                f"{self.host}/topicdetail/{real_tid}/",
                f"{self.host}/topicdetail/{real_tid}.html",
                f"{self.host}/topicdetail-{real_tid}-{pg}/",
                f"{self.host}/topicdetail/{real_tid}-{pg}/"
            ]
            for url in urls_to_try:
                res = self.fetch(url, headers={'Referer': self.host})
                if res and res.status_code == 200 and ('video-img-box' in res.text or 'vodlist' in res.text or 'vodplay' in res.text):
                    soup = BeautifulSoup(res.text, 'html.parser')
                    break
            if not soup:
                return result

        # ---------- new / hot / topic \u603b\u5165\u53e3 ----------
        elif real_tid in ["new", "hot", "topic"]:
            if real_tid == "topic":
                return result
            if pg > 1:
                url = f"{self.host}/label/{real_tid}/page/{pg}/"
            else:
                url = f"{self.host}/label/{real_tid}/"
            res = self.fetch(url, headers={'Referer': self.host})
            if not res:
                url = f"{self.host}/label/{real_tid}/"
                res = self.fetch(url, headers={'Referer': self.host})
            if not res:
                return result
            soup = BeautifulSoup(res.text, 'html.parser')

        # ---------- \u666e\u901a\u5206\u7c7b ----------
        else:
            urls_to_try = [
                f"{self.host}/vodtype/{real_tid}-{pg}.html",
                f"{self.host}/vodtype/{real_tid}-{pg}/",
                f"{self.host}/type/{real_tid}-{pg}.html",
                f"{self.host}/type/{real_tid}-{pg}/",
                f"{self.host}/vodtype/{real_tid}/",
                f"{self.host}/vodtype/{real_tid}.html"
            ]
            res = None
            for url in urls_to_try:
                res = self.fetch(url, headers={'Referer': self.host})
                if res and res.status_code == 200:
                    if 'video-img-box' in res.text or 'vodlist' in res.text or 'item' in res.text:
                        break
                res = None
            if not res:
                return result
            soup = BeautifulSoup(res.text, 'html.parser')

        # ---------- \u7edf\u4e00\u89e3\u6790\u89c6\u9891\u5217\u8868 ----------
        vod_list = []
        items = soup.select('.video-img-box') or soup.select('.video-film-list .video-item') or soup.select('.vodlist_item') or soup.select('.item')

        for item in items:
            a = item.select_one('a')
            if not a:
                continue
            href = a.get('href', '')
            vid_match = re.search(r'/vodplay/(\d+)', href) or \
                        re.search(r'/voddetail/(\d+)', href) or \
                        re.search(r'/vod/(\d+)', href) or \
                        re.search(r'/play/(\d+)', href)
            vid = vid_match.group(1) if vid_match else href

            name = ""
            img = item.select_one('img')
            if img and img.get('alt'):
                name = img['alt']
            if not name and a.get('title'):
                name = a['title']
            if not name:
                title_elem = item.select_one('.title a') or item.select_one('.detail .title a')
                if title_elem:
                    name = title_elem.get_text(strip=True)
            if not name:
                name = a.get_text(strip=True)
            if not name:
                name = "\u672a\u77e5\u6807\u9898"

            pic = ""
            if img:
                pic = img.get('data-src') or img.get('src', '')
                if pic and not pic.startswith('http'):
                    pic = urljoin(self.host, pic)

            remark = ""
            remark_elem = item.select_one('.sub-title') or item.select_one('.remarks') or item.select_one('.video-remarks')
            if remark_elem:
                remark = remark_elem.get_text(strip=True)
                if len(remark) > 20:
                    remark = remark[:20]
            else:
                text = item.get_text(strip=True)
                parts = [p.strip() for p in text.split('\n') if p.strip()]
                if parts:
                    remark = parts[-1][:20]

            vod_list.append({
                "vod_id": vid,
                "vod_name": name.strip(),
                "vod_pic": pic,
                "vod_remarks": remark
            })

        result['list'] = vod_list

        # ---------- \u5206\u9875\u4fe1\u606f ----------
        page_elem = soup.select_one('.pagination a:last-child') or soup.select_one('.page a:last-child')
        if page_elem and page_elem.get('href'):
            try:
                nums = re.findall(r'(\d+)', page_elem['href'])
                if nums:
                    result['pagecount'] = max(int(nums[-1]), 1)
            except:
                pass

        return result

    def detailContent(self, ids):
        vid = ids[0]
        url = f"{self.host}/vodplay/{vid}-1-1/"
        res = self.fetch(url, headers={'Referer': self.host})
        if not res:
            return {"list": []}

        soup = BeautifulSoup(res.text, 'html.parser')
        raw_title = soup.title.text.split('|')[0].replace('\u5728\u7ebf\u64ad\u653e\u5728\u7ebf\u89c2\u770b','').replace('\u300a','').replace('\u300b','').strip()

        vod = {
            "vod_id": vid,
            "vod_name": raw_title,
            "vod_type": "\u89c6\u9891",
            "vod_content": "\u8d44\u6e90\u6765\u81ea\u4e8e\u7f51\u7edc",
            "vod_play_from": "Luyitian",
            "vod_play_url": f"播放${vid}-1-1"
        }
        return {"list": [vod]}

    def searchContent(self, key, quick, pg=1):
        url = f"{self.host}/vodsearch/{key}----------{pg}---/"
        res = self.fetch(url, headers={'Referer': self.host})
        if not res:
            return {"list": []}

        soup = BeautifulSoup(res.text, 'html.parser')
        vod_list = []
        items = soup.select('.video-img-box') or soup.select('.video-film-list .video-item')

        for item in items:
            a = item.select_one('a')
            if not a:
                continue
            href = a.get('href', '')
            vid_match = re.search(r'/vodplay/(\d+)', href) or re.search(r'/voddetail/(\d+)', href)
            vid = vid_match.group(1) if vid_match else href

            name = ""
            img = item.select_one('img')
            if img and img.get('alt'):
                name = img['alt']
            if not name and a.get('title'):
                name = a['title']
            if not name:
                title_elem = item.select_one('.title a')
                if title_elem:
                    name = title_elem.get_text(strip=True)
            if not name:
                name = a.get_text(strip=True)
            if not name:
                name = "\u641c\u7d22\u7ed3\u679c"

            pic = ""
            if img:
                pic = img.get('data-src') or img.get('src', '')

            vod_list.append({
                "vod_id": vid,
                "vod_name": name.strip(),
                "vod_pic": pic,
                "vod_remarks": ""
            })
        return {"list": vod_list}

    def _js_decode(self, js_str):
        b64_match = re.search(r'atob\s*\(\s*["\']([^"\']+)["\']\s*\)', js_str)
        if b64_match:
            try:
                decoded = base64.b64decode(b64_match.group(1)).decode('utf-8')
                return decoded
            except:
                pass
        unescape_match = re.search(r'unescape\s*\(\s*["\']([^"\']+)["\']\s*\)', js_str)
        if unescape_match:
            try:
                decoded = unquote(unescape_match.group(1))
                return decoded
            except:
                pass
        url_match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', js_str, re.I)
        if url_match:
            return url_match.group(1)
        return None

    def _sniff_xhr(self, html, page_url):
        patterns = [
            r'fetch\s*\(\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'XMLHttpRequest.*?\.open\s*\(\s*["\']GET["\']\s*,\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'\.get\s*\(\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'url\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'src\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
        ]
        for pat in patterns:
            match = re.search(pat, html, re.I)
            if match:
                url = match.group(1)
                if not url.startswith('http'):
                    url = urljoin(page_url, url)
                return url
                
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.I | re.S)
        for script_content in scripts:
            if script_content.strip():
                found = self._js_decode(script_content)
                if found and '.m3u8' in found:
                    return found
        return None

    def playerContent(self, flag, id, vipFlags=None):
        play_url = f"{self.host}/vodplay/{id}/"
        res = self.fetch(play_url, headers={'Referer': self.host}, timeout=5)
        if not res:
            return {"parse": 1, "url": play_url}

        html = res.text
        m3u8_url = None

        match = re.search(r'var\s+player_aaaa\s*=\s*(\{.*?\});', html, re.DOTALL)
        if match:
            try:
                json_str = match.group(1).strip()
                if json_str.endswith(','):
                    json_str = json_str[:-1]
                config = json.loads(json_str)
                m3u8_url = config.get('url', '')
            except:
                pass

        if not m3u8_url:
            m3u8_url = self._js_decode(html)

        if not m3u8_url:
            m3u8_url = self._sniff_xhr(html, play_url)

        if not m3u8_url:
            return {"parse": 1, "url": play_url}

        m3u8_url = unquote(m3u8_url)
        if m3u8_url.startswith('//'):
            m3u8_url = 'https:' + m3u8_url
        elif not m3u8_url.startswith('http'):
            m3u8_url = urljoin(self.host, m3u8_url)

        return {
            "parse": 0,
            "playUrl": "",
            "url": m3u8_url,
            "header": {
                "User-Agent": self.session.headers['User-Agent'],
                "Referer": play_url,
                "Origin": self.host
            }
        }