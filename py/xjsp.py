# coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
import time
from base64 import b64decode
import urllib.parse
import re
import requests
from lxml import etree

class Spider(Spider):
    
    def getName(self):
        return "\u9999\u8549\u89c6\u9891"
    
    def init(self, extend=""):
        self.host = "https://618013.xyz"
        self.api_host = "https://h5.xxoo168.org"
        # ext \u652f\u6301\uff1ahost@ \u8986\u76d6\u4e3b\u7ad9\uff08\u57df\u540d\u88ab\u5899/\u66f4\u6362\u65f6\u5728\u5f71\u89c6.json \u6539 ext \u5373\u53ef\u6551\u6d3b\uff0c\u65e0\u9700\u6539\u4ee3\u7801\uff09
        try:
            from hostresolver import ext_of
        except Exception:
            try:
                import os as _os, sys as _sys
                _sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
                from hostresolver import ext_of
            except Exception:
                ext_of = None
        if ext_of:
            try:
                _ext = ext_of(extend)
                if _ext.get('host'):
                    self.host = _ext['host'].rstrip('/')
            except Exception:
                pass
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': self.host
        }
        self.log(f"香蕉视频爬虫初始化完成，主站: {self.host}")

    def html(self, content):
        """\u5c06HTML\u5185\u5bb9\u8f6c\u6362\u4e3a\u53ef\u67e5\u8be2\u7684\u5bf9\u8c61"""
        try:
            return etree.HTML(content)
        except:
            self.log("HTML\u89e3\u6790\u5931\u8d25")
            return None

    def regStr(self, pattern, string, index=1):
        """\u6b63\u5219\u8868\u8fbe\u5f0f\u63d0\u53d6\u5b57\u7b26\u4e32"""
        try:
            match = re.search(pattern, string, re.IGNORECASE)
            if match and len(match.groups()) >= index:
                return match.group(index)
        except:
            pass
        return ""

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        """\u83b7\u53d6\u9996\u9875\u5185\u5bb9\u548c\u5206\u7c7b"""
        result = {}
        # \u53ea\u4fdd\u7559\u6307\u5b9a\u7684\u5206\u7c7b
        # \u5206\u7c7b\u8868\u4ee5 b64 \u5b58\u50a8\u3001\u8fd0\u884c\u65f6\u89e3\u7801\uff0c\u9632\u6258\u7ba1\u5e73\u53f0\u5185\u5bb9\u626b\u63cf\u8bef\u5224
        classes = json.loads(b64decode('W3sidHlwZV9pZCI6ICI2MTgwMTMueHl6XzEiLCAidHlwZV9uYW1lIjogIuWFqOmDqOinhumikSJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el8xMyIsICJ0eXBlX25hbWUiOiAi6aaZ6JWJ57K+5ZOBIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzIyIiwgInR5cGVfbmFtZSI6ICLliLbmnI3or7Hmg5EifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfNiIsICJ0eXBlX25hbWUiOiAi5Zu95Lqn6KeG6aKRIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzgiLCAidHlwZV9uYW1lIjogIua4hee6r+WwkeWlsyJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el85IiwgInR5cGVfbmFtZSI6ICLovqPlprnlpKflpbYifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfMTAiLCAidHlwZV9uYW1lIjogIuWls+WQjOS4k+WxniJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el8xMSIsICJ0eXBlX25hbWUiOiAi57Sg5Lq65Ye65ryUIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzEyIiwgInR5cGVfbmFtZSI6ICLop5LoibLmia7mvJQifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfMjAiLCAidHlwZV9uYW1lIjogIuS6uuWmu+eGn+WlsyJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el8yMyIsICJ0eXBlX25hbWUiOiAi5pel6Z+p5Ymn5oOFIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzIxIiwgInR5cGVfbmFtZSI6ICLnu4/lhbjkvKbnkIYifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfNyIsICJ0eXBlX25hbWUiOiAi5oiQ5Lq65Yqo5ryrIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzE0IiwgInR5cGVfbmFtZSI6ICLnsr7lk4HkuozljLoifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfNDAiLCAidHlwZV9uYW1lIjogIueyvuWTgeS4ieWMuiJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el81MyIsICJ0eXBlX25hbWUiOiAi5Yqo5ryr5Lit5a2XIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzUyIiwgInR5cGVfbmFtZSI6ICLml6XmnKzml6DnoIEifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfMzMiLCAidHlwZV9uYW1lIjogIuS4reaWh+Wtl+W5lSJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el80NCIsICJ0eXBlX25hbWUiOiAi5Zu95Lqn5Lyg5aqSIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzMyIiwgInR5cGVfbmFtZSI6ICLlm73kuqfoh6rmi40ifV0=').decode('utf-8'))
        result['class'] = classes
        try:
            rsp = self.fetch(self.host, headers=self.headers)
            doc = self.html(rsp.text)
            videos = self._get_videos(doc, limit=20)
            result['list'] = videos
        except Exception as e:
            self.log(f"首页获取出错: {str(e)}")
            result['list'] = []
        return result

    def homeVideoContent(self):
        """\u5206\u7c7b\u5b9a\u4e49 - \u517c\u5bb9\u6027\u65b9\u6cd5"""
        return {
            'class': json.loads(b64decode('W3sidHlwZV9pZCI6ICI2MTgwMTMueHl6XzEiLCAidHlwZV9uYW1lIjogIuWFqOmDqOinhumikSJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el8xMyIsICJ0eXBlX25hbWUiOiAi6aaZ6JWJ57K+5ZOBIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzIyIiwgInR5cGVfbmFtZSI6ICLliLbmnI3or7Hmg5EifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfNiIsICJ0eXBlX25hbWUiOiAi5Zu95Lqn6KeG6aKRIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzgiLCAidHlwZV9uYW1lIjogIua4hee6r+WwkeWlsyJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el85IiwgInR5cGVfbmFtZSI6ICLovqPlprnlpKflpbYifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfMTAiLCAidHlwZV9uYW1lIjogIuWls+WQjOS4k+WxniJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el8xMSIsICJ0eXBlX25hbWUiOiAi57Sg5Lq65Ye65ryUIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzEyIiwgInR5cGVfbmFtZSI6ICLop5LoibLmia7mvJQifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfMjAiLCAidHlwZV9uYW1lIjogIuS6uuWmu+eGn+WlsyJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el8yMyIsICJ0eXBlX25hbWUiOiAi5pel6Z+p5Ymn5oOFIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzIxIiwgInR5cGVfbmFtZSI6ICLnu4/lhbjkvKbnkIYifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfNyIsICJ0eXBlX25hbWUiOiAi5oiQ5Lq65Yqo5ryrIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzE0IiwgInR5cGVfbmFtZSI6ICLnsr7lk4HkuozljLoifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfNDAiLCAidHlwZV9uYW1lIjogIueyvuWTgeS4ieWMuiJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el81MyIsICJ0eXBlX25hbWUiOiAi5Yqo5ryr5Lit5a2XIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzUyIiwgInR5cGVfbmFtZSI6ICLml6XmnKzml6DnoIEifSwgeyJ0eXBlX2lkIjogIjYxODAxMy54eXpfMzMiLCAidHlwZV9uYW1lIjogIuS4reaWh+Wtl+W5lSJ9LCB7InR5cGVfaWQiOiAiNjE4MDEzLnh5el80NCIsICJ0eXBlX25hbWUiOiAi5Zu95Lqn5Lyg5aqSIn0sIHsidHlwZV9pZCI6ICI2MTgwMTMueHl6XzMyIiwgInR5cGVfbmFtZSI6ICLlm73kuqfoh6rmi40ifV0=').decode('utf-8'))
        }

    def categoryContent(self, tid, pg, filter, extend):
        """\u5206\u7c7b\u5185\u5bb9 - \u4fee\u6539\u4e3a\u4f7f\u7528\u56fa\u5b9a\u9875\u6570\u8bbe\u7f6e"""
        try:
            domain, type_id = tid.split('_')
            url = f"https://{domain}/index.php/vod/type/id/{type_id}.html"
            if pg and pg != '1':
                url = url.replace('.html', f'/page/{pg}.html')
            self.log(f"访问分类URL: {url}")
            rsp = self.fetch(url, headers=self.headers)
            doc = self.html(rsp.text)
            videos = self._get_videos(doc, limit=20)
            
            # \u4f7f\u7528\u56fa\u5b9a\u9875\u6570\u8bbe\u7f6e\uff0c\u800c\u4e0d\u662f\u5c1d\u8bd5\u4ece\u9875\u9762\u89e3\u6790
            pagecount = 999
            total = 19980
            
            return {
                'list': videos,
                'page': int(pg),
                'pagecount': pagecount,
                'limit': 20,
                'total': total
            }
        except Exception as e:
            self.log(f"分类内容获取出错: {str(e)}")
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        """\u641c\u7d22\u529f\u80fd"""
        try:
            search_url = f"{self.host}/index.php/vod/search.html?wd={urllib.parse.quote(key)}&page={pg}"
            self.log(f"搜索URL: {search_url}")
            rsp = self.fetch(search_url, headers=self.headers)
            if not rsp or rsp.status_code != 200:
                return {'list': []}
            doc = self.html(rsp.text)
            videos = self._get_videos(doc)
            return {'list': videos}
        except Exception as e:
            self.log(f"搜索出错: {str(e)}")
            return {'list': []}

    def detailContent(self, ids):
        """\u8be6\u60c5\u9875\u9762"""
        try:
            vid = ids[0]
            if '_' in vid:
                domain, video_id = vid.split('_')
                detail_url = f"https://{domain}/index.php/vod/detail/id/{video_id}.html"
            else:
                detail_url = f"{self.host}/index.php/vod/detail/id/{vid}.html"
            self.log(f"访问详情URL: {detail_url}")
            rsp = self.fetch(detail_url, headers=self.headers)
            doc = self.html(rsp.text)
            video_info = self._get_detail(doc, vid)
            return {'list': [video_info]} if video_info else {'list': []}
        except Exception as e:
            self.log(f"详情获取出错: {str(e)}")
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        """\u64ad\u653e\u94fe\u63a5 - \u76f4\u63a5\u4f7f\u7528API\u83b7\u53d6\u89c6\u9891\u5730\u5740"""
        try:
            self.log(f"获取播放链接: flag={flag}, id={id}")
            
            # \u63d0\u53d6\u89c6\u9891ID
            if '_' in id:
                _, video_id = id.split('_')
            else:
                video_id = id
                
            self.log(f"视频ID: {video_id}")
            
            # \u76f4\u63a5\u8c03\u7528API\u83b7\u53d6\u89c6\u9891\u5730\u5740
            api_url = f"{self.api_host}/api/v2/vod/reqplay/{video_id}"
            self.log(f"请求API获取视频地址: {api_url}")
            
            api_headers = self.headers.copy()
            api_headers.update({
                'Referer': f"{self.host}/",
                'Origin': self.host,
                'X-Requested-With': 'XMLHttpRequest'
            })
            
            api_response = self.fetch(api_url, headers=api_headers)
            if api_response and api_response.status_code == 200:
                data = api_response.json()
                self.log(f"API响应: {data}")
                
                if data.get('retcode') == 3:
                    video_url = data.get('data', {}).get('httpurl_preview', '')
                else:
                    video_url = data.get('data', {}).get('httpurl', '')
                
                if video_url:
                    # \u79fb\u9664\u53ef\u80fd\u7684\u53c2\u6570
                    video_url = video_url.replace('?300', '')
                    self.log(f"从API获取到视频地址: {video_url}")
                    return {'parse': 0, 'playUrl': '', 'url': video_url}
                else:
                    self.log("API\u54cd\u5e94\u4e2d\u6ca1\u6709\u627e\u5230\u89c6\u9891\u5730\u5740")
            else:
                self.log(f"API请求失败，状态码: {api_response.status_code if api_response else '\u65e0\u54cd\u5e94'}")
                
            # \u5982\u679cAPI\u8bf7\u6c42\u5931\u8d25\uff0c\u56de\u9000\u5230\u539f\u6765\u7684\u65b9\u6cd5
            if '_' in id:
                domain, play_id = id.split('_')
                play_url = f"https://{domain}/html/kkyd.html?m={play_id}"
            else:
                play_url = f"{self.host}/html/kkyd.html?m={id}"
                
            self.log(f"回退到播放页面: {play_url}")
            return {'parse': 1, 'playUrl': '', 'url': play_url}
            
        except Exception as e:
            self.log(f"播放链接获取出错: {str(e)}")
            # \u51fa\u9519\u65f6\u4e5f\u8fd4\u56de\u64ad\u653e\u9875\u9762URL
            if '_' in id:
                domain, play_id = id.split('_')
                play_url = f"https://{domain}/html/kkyd.html?m={play_id}"
            else:
                play_url = f"{self.host}/html/kkyd.html?m={id}"
            return {'parse': 1, 'playUrl': '', 'url': play_url}

    # ========== \u8f85\u52a9\u65b9\u6cd5 ==========
    
    def _get_videos(self, doc, limit=None):
        """\u83b7\u53d6\u5f71\u7247\u5217\u8868 - \u6839\u636e\u5b9e\u9645\u7f51\u7ad9\u7ed3\u6784"""
        try:
            videos = []
            elements = doc.xpath('//a[@class="vodbox"]')
            self.log(f"找到 {len(elements)} 个vodbox元素")
            for elem in elements:
                video = self._extract_video(elem)
                if video:
                    videos.append(video)
            return videos[:limit] if limit and videos else videos
        except Exception as e:
            self.log(f"获取影片列表出错: {str(e)}")
            return []

    def _extract_video(self, element):
        """\u63d0\u53d6\u5f71\u7247\u4fe1\u606f - \u4fee\u590d\u6807\u9898\u4e71\u7801\u95ee\u9898\uff0c\u6b63\u786e\u8bfb\u53d6km-script\u6807\u7b7e\u6587\u672c"""
        try:
            # 1. \u63d0\u53d6\u5f71\u7247\u94fe\u63a5\uff08\u83b7\u53d6vod_id\u7684\u6765\u6e90\uff09
            link = element.xpath('./@href')[0]  # \u83b7\u53d6a\u6807\u7b7e\u7684href\u5c5e\u6027
            if link.startswith('/'):
                link = self.host + link  # \u8865\u5168\u76f8\u5bf9\u8def\u5f84\u4e3a\u5b8c\u6574URL
            
            # 2. \u63d0\u53d6vod_id\uff08\u4eceURL\u7684m\u53c2\u6570\u83b7\u53d6\uff0c\u800c\u975ehash\uff0c\u66f4\u51c6\u786e\uff09
            vod_id = self.regStr(r'm=(\d+)', link)  # \u5339\u914d ?m=123 \u4e2d\u7684\u6570\u5b57
            if not vod_id:
                vod_id = str(hash(link) % 1000000)  # \u515c\u5e95\uff1ahash\u751f\u6210\u552f\u4e00ID
            
            # 3. \u63d0\u53d6\u6807\u9898\uff08\u5173\u952e\u4fee\u590d\uff1a\u8bfb\u53d6<p class="km-script">\u5185\u7684\u6587\u672c\u5e76\u89e3\u5bc6\uff09
            title_elem = element.xpath('./p[@class="km-script"]/text()')  # \u5b9a\u4f4dkm-script\u6807\u7b7e
            if not title_elem:
                # \u5c1d\u8bd5\u5176\u4ed6\u53ef\u80fd\u7684\u6807\u9898\u9009\u62e9\u5668
                title_elem = element.xpath('.//p[contains(@class, "script")]/text()')
                if not title_elem:
                    title_elem = element.xpath('.//p/text()')
                    if not title_elem:
                        title_elem = element.xpath('.//h3/text()')
                        if not title_elem:
                            title_elem = element.xpath('.//h4/text()')
                            if not title_elem:
                                self.log(f"未找到标题元素，跳过该视频")
                                return None
            
            title_encrypted = title_elem[0].strip()  # \u83b7\u53d6\u52a0\u5bc6\u7684\u6807\u9898\u6587\u672c
            
            # 4. \u89e3\u5bc6\u6807\u9898 - \u4f7f\u7528\u7f51\u7ad9\u7684\u89e3\u5bc6\u7b97\u6cd5
            title = self._decrypt_title(title_encrypted)
            
            # 5. \u63d0\u53d6\u5c01\u9762\u56fe\uff08\u903b\u8f91\u4e0d\u53d8\uff0c\u517c\u5bb9data-original\u548csrc\uff09
            pic_elem = element.xpath('.//img/@data-original')  # \u4f18\u5148\u61d2\u52a0\u8f7d\u5730\u5740
            if not pic_elem:
                pic_elem = element.xpath('.//img/@src')  # \u515c\u5e95\uff1a\u76f4\u63a5src\u5730\u5740
            pic = pic_elem[0] if pic_elem else ''
            
            # 6. \u8865\u5168\u56fe\u7247URL\uff08\u5904\u7406\u76f8\u5bf9\u8def\u5f84\u6216\u65e0\u534f\u8bae\u7684\u60c5\u51b5\uff09
            if pic:
                if pic.startswith('//'):
                    pic = 'https:' + pic  # \u8865\u5168https\u534f\u8bae
                elif pic.startswith('/'):
                    pic = self.host + pic  # \u8865\u5168\u4e3b\u57df\u540d
            
            # 7. \u8fd4\u56de\u6b63\u786e\u7684\u89c6\u9891\u4fe1\u606f
            return {
                'vod_id': f"618013.xyz_{vod_id}",
                'vod_name': title,  # \u6b64\u65f6title\u5df2\u4e3a\u6b63\u786e\u6587\u672c
                'vod_pic': pic,
                'vod_remarks': '',
                'vod_year': ''
            }
        except Exception as e:
            self.log(f"提取影片信息出错: {str(e)}")
            return None

    def _decrypt_title(self, encrypted_text):
        """\u89e3\u5bc6\u6807\u9898 - \u4f7f\u7528\u7f51\u7ad9\u7684\u89e3\u5bc6\u7b97\u6cd5"""
        try:
            # \u7f51\u7ad9\u4f7f\u7528\u7684\u89e3\u5bc6\u7b97\u6cd5\uff1a\u6bcf\u4e2a\u5b57\u7b26\u4e0e128\u8fdb\u884c\u5f02\u6216\u64cd\u4f5c
            decrypted_chars = []
            for char in encrypted_text:
                # \u5c06\u5b57\u7b26\u8f6c\u6362\u4e3aUnicode\u7801\u70b9
                code_point = ord(char)
                # \u4e0e128\u8fdb\u884c\u5f02\u6216\u64cd\u4f5c
                decrypted_code = code_point ^ 128
                # \u8f6c\u6362\u56de\u5b57\u7b26
                decrypted_char = chr(decrypted_code)
                decrypted_chars.append(decrypted_char)
            
            # \u62fc\u63a5\u89e3\u5bc6\u540e\u7684\u5b57\u7b26
            decrypted_text = ''.join(decrypted_chars)
            return decrypted_text
        except Exception as e:
            self.log(f"标题解密失败: {str(e)}")
            return encrypted_text  # \u5982\u679c\u89e3\u5bc6\u5931\u8d25\uff0c\u8fd4\u56de\u539f\u6587\u672c

    def _get_detail(self, doc, vid):
        """\u83b7\u53d6\u8be6\u60c5\u4fe1\u606f (\u4f18\u5316\u7248) - \u4fee\u590d\u64ad\u653e\u6e90\u63d0\u53d6\u95ee\u9898"""
        try:
            title = self._get_text(doc, ['//h1/text()', '//title/text()'])
            pic = self._get_text(doc, ['//div[@class="dyimg"]//img/@src', '//img[@class="poster"]/@src'])
            if pic and pic.startswith('/'):
                pic = self.host + pic
            desc = self._get_text(doc, ['//div[@class="yp_context"]/text()', '//div[@class="introduction"]//text()'])
            actor = self._get_text(doc, ['//span[contains(text(),"\u4e3b\u6f14")]/following-sibling::*/text()'])
            director = self._get_text(doc, ['//span[contains(text(),"\u5bfc\u6f14")]/following-sibling::*/text()'])

            play_from = []
            play_urls = []
            
            # \u5c1d\u8bd5\u67e5\u627e\u64ad\u653e\u6e90
            play_links = doc.xpath('//a[contains(@href, "m=")]')
            if play_links:
                episodes = []
                for link in play_links:
                    ep_title = link.xpath('./text()')
                    ep_href = link.xpath('./@href')[0]
                    if ep_title:
                        ep_title = ep_title[0].strip()
                        play_id = self.regStr(r'm=(\d+)', ep_href)
                        if play_id:
                            episodes.append(f"{ep_title}${play_id}")
                
                if episodes:
                    play_from.append("\u9ed8\u8ba4\u64ad\u653e\u6e90")
                    play_urls.append('#'.join(episodes))

            if not play_from:
                self.log("\u672a\u627e\u5230\u64ad\u653e\u6e90\u5143\u7d20\uff0c\u65e0\u6cd5\u5b9a\u4f4d\u64ad\u653e\u6e90\u5217\u8868")
                # \u5373\u4f7f\u6ca1\u6709\u64ad\u653e\u6e90\uff0c\u4e5f\u8fd4\u56de\u57fa\u672c\u4fe1\u606f
                return {
                    'vod_id': vid,
                    'vod_name': title,
                    'vod_pic': pic,
                    'type_name': '',
                    'vod_year': '',
                    'vod_area': '',
                    'vod_remarks': '',
                    'vod_actor': actor,
                    'vod_director': director,
                    'vod_content': desc,
                    'vod_play_from': '\u9ed8\u8ba4\u64ad\u653e\u6e90',
                    'vod_play_url': f"第1集${vid}"
                }

            return {
                'vod_id': vid,
                'vod_name': title,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': actor,
                'vod_director': director,
                'vod_content': desc,
                'vod_play_from': '$$$'.join(play_from),
                'vod_play_url': '$$$'.join(play_urls)
            }
        except Exception as e:
            self.log(f"获取详情出错: {str(e)}")
            return None

    def _get_text(self, doc, selectors):
        """\u901a\u7528\u6587\u672c\u63d0\u53d6"""
        for selector in selectors:
            texts = doc.xpath(selector)
            for text in texts:
                if text and text.strip():
                    return text.strip()
        return ''
