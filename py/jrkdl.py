# -*- coding: utf-8 -*-
# \ud83c\udf08 Love 
import json
import random
import re
import sys
import threading
import time
from base64 import b64decode, b64encode
from urllib.parse import urlparse, quote

import requests
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        try:self.proxies = json.loads(extend)
        except:self.proxies = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        }
        # Use working dynamic URLs directly
        self.host = self.get_working_host()
        self.headers.update({'Origin': self.host, 'Referer': f"{self.host}/"})
        self.log(f"使用站点: {self.host}")
        print(f"使用站点: {self.host}")
        pass

    def getName(self):
        return "\U0001f308 \u4eca\u65e5\u770b\u6599"

    def isVideoFormat(self, url):
        # Treat direct media formats as playable without parsing
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def homeContent(self, filter):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'class': [], 'list': []}
                
            data = self.getpq(response.text)
            result = {}
            classes = []
            
            # \u4f18\u5148\u4ece\u5bfc\u822a\u680f\u83b7\u53d6\u5206\u7c7b
            nav_selectors = [
                '#navbarCollapse .navbar-nav .nav-item .nav-link',
                '.navbar-nav .nav-item .nav-link',
                '#nav .menu-item a',
                '.menu .menu-item a'
            ]
            
            found_categories = False
            for selector in nav_selectors:
                for item in data(selector).items():
                    href = item.attr('href') or ''
                    name = item.text().strip()
                    
                    # \u8fc7\u6ee4\u6389\u975e\u5206\u7c7b\u94fe\u63a5
                    if (not href or not name or 
                        href == '#' or 
                        href.startswith('http') or
                        'about' in href.lower() or
                        'contact' in href.lower() or
                        'tags' in href.lower() or
                        'top' in href.lower() or
                        'start' in href.lower() or
                        'time' in href.lower()):
                        continue
                    
                    # \u786e\u4fdd\u662f\u5206\u7c7b\u94fe\u63a5\uff08\u5305\u542bcategory\u6216\u660e\u786e\u7684\u5206\u7c7b\u8def\u5f84\uff09
                    if '/category/' in href or any(cat in href for cat in ['/dy/', '/ks/', '/douyu/', '/hy/', '/hj/', '/tt/', '/wh/', '/asmr/', '/xb/', '/xsp/', '/rdgz/']):
                        # \u5904\u7406\u76f8\u5bf9\u8def\u5f84
                        if href.startswith('/'):
                            type_id = href
                        else:
                            type_id = f'/{href}'
                            
                        classes.append({
                            'type_name': name,
                            'type_id': type_id
                        })
                        found_categories = True
            
            # \u5982\u679c\u5bfc\u822a\u680f\u6ca1\u627e\u5230\uff0c\u5c1d\u8bd5\u4ece\u5206\u7c7b\u4e0b\u62c9\u83dc\u5355\u83b7\u53d6
            if not found_categories:
                category_selectors = [
                    '.category-list a',
                    '.slide-toggle + .category-list a',
                    '.menu .category-list a'
                ]
                for selector in category_selectors:
                    for item in data(selector).items():
                        href = item.attr('href') or ''
                        name = item.text().strip()
                        
                        if href and name and href != '#':
                            if href.startswith('/'):
                                type_id = href
                            else:
                                type_id = f'/{href}'
                                
                            classes.append({
                                'type_name': name,
                                'type_id': type_id
                            })
                            found_categories = True
            
            # \u53bb\u91cd
            unique_classes = []
            seen_ids = set()
            for cls in classes:
                if cls['type_id'] not in seen_ids:
                    unique_classes.append(cls)
                    seen_ids.add(cls['type_id'])
            
            # \u5982\u679c\u6ca1\u6709\u627e\u5230\u5206\u7c7b\uff0c\u521b\u5efa\u9ed8\u8ba4\u5206\u7c7b
            if not unique_classes:
                unique_classes = [
                    {'type_name': '\u70ed\u70b9\u5173\u6ce8', 'type_id': '/category/rdgz/'},
                    {'type_name': '\u6296\u97f3', 'type_id': '/category/dy/'},
                    {'type_name': '\u5feb\u624b', 'type_id': '/category/ks/'},
                    {'type_name': '\u6597\u9c7c', 'type_id': '/category/douyu/'},
                    {'type_name': '\u864e\u7259', 'type_id': '/category/hy/'},
                    {'type_name': '\u82b1\u6912', 'type_id': '/category/hj/'},
                    {'type_name': '\u63a8\u7279', 'type_id': '/category/tt/'},
                    {'type_name': '\u7f51\u7ea2', 'type_id': '/category/wh/'},
                    {'type_name': 'ASMR', 'type_id': '/category/asmr/'},
                    {'type_name': 'X\u64ad', 'type_id': '/category/xb/'},
                    {'type_name': '\u5c0f\u89c6\u9891', 'type_id': '/category/xsp/'}
                ]
            
            result['class'] = unique_classes
            result['list'] = self.getlist(data('#index article a, #archive article a'))
            return result
            
        except Exception as e:
            print(f"homeContent error: {e}")
            return {'class': [], 'list': []}

    def homeVideoContent(self):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'list': []}
            data = self.getpq(response.text)
            return {'list': self.getlist(data('#index article a, #archive article a'))}
        except Exception as e:
            print(f"homeVideoContent error: {e}")
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            # \u4fee\u590dURL\u6784\u5efa - \u53bb\u9664\u591a\u4f59\u7684\u659c\u6760
            base_url = tid.lstrip('/').rstrip('/')
            if pg and pg != '1':
                url = f"{self.host}{base_url}/{pg}/"
            else:
                url = f"{self.host}{base_url}/"
                
            print(f"分类页面URL: {url}")
            
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                print(f"分类页面请求失败: {response.status_code}")
                return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}
                
            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article a, #index article a, .post-card'), tid)
            
            # \u5982\u679c\u6ca1\u6709\u627e\u5230\u89c6\u9891\uff0c\u5c1d\u8bd5\u5176\u4ed6\u9009\u62e9\u5668
            if not videos:
                videos = self.getlist(data('article a, .post a, .entry-title a'), tid)
            
            print(f"找到 {len(videos)} 个视频")
            
            # \u6539\u8fdb\u7684\u9875\u6570\u68c0\u6d4b\u903b\u8f91
            pagecount = self.detect_page_count(data, pg)
            
            result = {}
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = pagecount
            result['limit'] = 90
            result['total'] = 999999
            return result
            
        except Exception as e:
            print(f"categoryContent error: {e}")
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}

    def tagContent(self, tid, pg, filter, extend):
        """\u6807\u7b7e\u9875\u9762\u5185\u5bb9"""
        try:
            # \u4fee\u590dURL\u6784\u5efa - \u53bb\u9664\u591a\u4f59\u7684\u659c\u6760
            base_url = tid.lstrip('/').rstrip('/')
            if pg and pg != '1':
                url = f"{self.host}{base_url}/{pg}/"
            else:
                url = f"{self.host}{base_url}/"
                
            print(f"标签页面URL: {url}")
            
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                print(f"标签页面请求失败: {response.status_code}")
                return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}
                
            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article a, #index article a, .post-card'), tid)
            
            # \u5982\u679c\u6ca1\u6709\u627e\u5230\u89c6\u9891\uff0c\u5c1d\u8bd5\u5176\u4ed6\u9009\u62e9\u5668
            if not videos:
                videos = self.getlist(data('article a, .post a, .entry-title a'), tid)
            
            print(f"找到 {len(videos)} 个标签相关视频")
            
            # \u9875\u6570\u68c0\u6d4b
            pagecount = self.detect_page_count(data, pg)
            
            result = {}
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = pagecount
            result['limit'] = 90
            result['total'] = 999999
            return result
            
        except Exception as e:
            print(f"tagContent error: {e}")
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}

    def detect_page_count(self, data, current_page):
        """\u6539\u8fdb\u7684\u9875\u6570\u68c0\u6d4b\u65b9\u6cd5"""
        pagecount = 99999  # \u9ed8\u8ba4\u5927\u6570\u5b57\uff0c\u5141\u8bb8\u65e0\u9650\u7ffb\u9875
        
        # \u65b9\u6cd51: \u68c0\u67e5\u5206\u9875\u5668\u4e2d\u7684\u6240\u6709\u9875\u7801\u94fe\u63a5
        page_numbers = []
        
        # \u67e5\u627e\u6240\u6709\u53ef\u80fd\u7684\u9875\u7801\u94fe\u63a5
        page_selectors = [
            '.page-navigator a',
            '.pagination a', 
            '.pages a',
            '.page-numbers a'
        ]
        
        for selector in page_selectors:
            for page_link in data(selector).items():
                href = page_link.attr('href') or ''
                text = page_link.text().strip()
                
                # \u4ecehref\u4e2d\u63d0\u53d6\u9875\u7801
                if href:
                    # \u5339\u914d /category/dy/2/ \u8fd9\u79cd\u683c\u5f0f
                    match = re.search(r'/(\d+)/?$', href.rstrip('/'))
                    if match:
                        page_num = int(match.group(1))
                        if page_num not in page_numbers:
                            page_numbers.append(page_num)
                
                # \u4ece\u6587\u672c\u4e2d\u63d0\u53d6\u6570\u5b57\u9875\u7801
                if text and text.isdigit():
                    page_num = int(text)
                    if page_num not in page_numbers:
                        page_numbers.append(page_num)
        
        # \u5982\u679c\u6709\u627e\u5230\u9875\u7801\uff0c\u53d6\u6700\u5927\u503c
        if page_numbers:
            max_page = max(page_numbers)
            print(f"从分页器检测到最大页码: {max_page}")
            return max_page
        
        # \u65b9\u6cd52: \u68c0\u67e5\u662f\u5426\u5b58\u5728"\u4e0b\u4e00\u9875"\u6309\u94ae
        next_selectors = [
            '.page-navigator .next',
            '.pagination .next',
            '.next-page',
            'a:contains("\u4e0b\u4e00\u9875")'
        ]
        
        for selector in next_selectors:
            if data(selector):
                print("\u68c0\u6d4b\u5230\u4e0b\u4e00\u9875\u6309\u94ae\uff0c\u5141\u8bb8\u7ee7\u7eed\u7ffb\u9875")
                return 99999
        
        # \u65b9\u6cd53: \u5982\u679c\u5f53\u524d\u9875\u89c6\u9891\u6570\u91cf\u5f88\u5c11\uff0c\u53ef\u80fd\u6ca1\u6709\u4e0b\u4e00\u9875
        if len(data('#archive article, #index article, .post-card')) < 5:
            print("\u5f53\u524d\u9875\u5185\u5bb9\u8f83\u5c11\uff0c\u53ef\u80fd\u6ca1\u6709\u4e0b\u4e00\u9875")
            return int(current_page)
        
        print("\u4f7f\u7528\u9ed8\u8ba4\u9875\u6570: 99999")
        return 99999

    def detailContent(self, ids):
        try:
            url = f"{self.host}{ids[0]}" if not ids[0].startswith('http') else ids[0]
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            if response.status_code != 200:
                return {'list': [{'vod_play_from': '\u4eca\u65e5\u770b\u6599', 'vod_play_url': f'页面加载失败${url}'}]}
                
            data = self.getpq(response.text)
            vod = {'vod_play_from': '\u4eca\u65e5\u770b\u6599'}
            
            # \u83b7\u53d6\u6807\u9898
            title_selectors = ['.post-title', 'h1.entry-title', 'h1', '.post-card-title']
            for selector in title_selectors:
                title_elem = data(selector)
                if title_elem:
                    vod['vod_name'] = title_elem.text().strip()
                    break
            
            if 'vod_name' not in vod:
                vod['vod_name'] = '\u4eca\u65e5\u770b\u6599\u89c6\u9891'
            
            # \u83b7\u53d6\u5185\u5bb9/\u63cf\u8ff0
            try:
                clist = []
                if data('.tags .keywords a'):
                    for k in data('.tags .keywords a').items():
                        title = k.text()
                        href = k.attr('href')
                        if title and href:
                            # \u4f7fhref\u76f8\u5bf9\u8def\u5f84
                            if href.startswith(self.host):
                                href = href.replace(self.host, '')
                            clist.append('[a=cr:' + json.dumps({'id': href, 'name': title}) + '/]' + title + '[/a]')
                vod['vod_content'] = ' '.join(clist) if clist else data('.post-content').text() or vod['vod_name']
            except:
                vod['vod_content'] = vod['vod_name']
            
            # \u83b7\u53d6\u89c6\u9891URLs
            try:
                plist = []
                used_names = set()
                
                # \u67e5\u627eDPlayer\u89c6\u9891
                if data('.dplayer'):
                    for c, k in enumerate(data('.dplayer').items(), start=1):
                        config_attr = k.attr('data-config')
                        if config_attr:
                            try:
                                config = json.loads(config_attr)
                                video_url = config.get('video', {}).get('url', '')
                                if video_url:
                                    name = f"视频{c}"
                                    count = 2
                                    while name in used_names:
                                        name = f"视频{c}_{count}"
                                        count += 1
                                    used_names.add(name)
                                    self.log(f"解析到视频: {name} -> {video_url}")
                                    print(f"解析到视频: {name} -> {video_url}")
                                    plist.append(f"{name}${video_url}")
                            except:
                                continue
                
                # \u67e5\u627e\u89c6\u9891\u6807\u7b7e
                if not plist:
                    video_selectors = ['video source', 'video', 'iframe[src*="video"]', 'a[href*=".m3u8"]', 'a[href*=".mp4"]']
                    for selector in video_selectors:
                        for c, elem in enumerate(data(selector).items(), start=1):
                            src = elem.attr('src') or elem.attr('href') or ''
                            if src and any(ext in src for ext in ['.m3u8', '.mp4', 'video']):
                                name = f"视频{c}"
                                count = 2
                                while name in used_names:
                                    name = f"视频{c}_{count}"
                                    count += 1
                                used_names.add(name)
                                plist.append(f"{name}${src}")
                
                if plist:
                    self.log(f"拼装播放列表，共{len(plist)}个")
                    print(f"拼装播放列表，共{len(plist)}个")
                    vod['vod_play_url'] = '#'.join(plist)
                else:
                    vod['vod_play_url'] = f"正片${url}"
                    
            except Exception as e:
                print(f"视频解析错误: {e}")
                vod['vod_play_url'] = f"正片${url}"
                
            return {'list': [vod]}
            
        except Exception as e:
            print(f"detailContent error: {e}")
            return {'list': [{'vod_play_from': '\u4eca\u65e5\u770b\u6599', 'vod_play_url': f'详情页加载失败${ids[0] if ids else ""}'}]}

    def searchContent(self, key, quick, pg="1"):
        try:
            # \u4f18\u5148\u4f7f\u7528\u6807\u7b7e\u641c\u7d22
            encoded_key = quote(key)
            url = f"{self.host}/tag/{encoded_key}/{pg}" if pg != "1" else f"{self.host}/tag/{encoded_key}/"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            if response.status_code != 200:
                # \u5c1d\u8bd5\u641c\u7d22\u9875\u9762
                url = f"{self.host}/search/{encoded_key}/{pg}" if pg != "1" else f"{self.host}/search/{encoded_key}/"
                response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            if response.status_code != 200:
                return {'list': [], 'page': pg}
                
            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article a, #index article a, .post-card'))
            
            # \u4f7f\u7528\u6539\u8fdb\u7684\u9875\u6570\u68c0\u6d4b\u65b9\u6cd5
            pagecount = self.detect_page_count(data, pg)
            
            return {'list': videos, 'page': pg, 'pagecount': pagecount}
            
        except Exception as e:
            print(f"searchContent error: {e}")
            return {'list': [], 'page': pg}

    def getTagsContent(self, pg="1"):
        """\u83b7\u53d6\u6807\u7b7e\u9875\u9762\u5185\u5bb9"""
        try:
            url = f"{self.host}/tags.html"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            if response.status_code != 200:
                return {'list': [], 'page': pg}
                
            data = self.getpq(response.text)
            tags = []
            
            # \u4ece\u6807\u7b7e\u9875\u9762\u63d0\u53d6\u6240\u6709\u6807\u7b7e - \u4f7f\u7528\u66f4\u5bbd\u677e\u7684\u9009\u62e9\u5668
            for tag_elem in data('a[href*="/tag/"]').items():
                tag_name = tag_elem.text().strip()
                tag_href = tag_elem.attr('href') or ''
                
                if tag_name and tag_href and '/tag/' in tag_href and tag_name != '\u5168\u90e8\u6807\u7b7e':  # \u6392\u9664\u6807\u9898\u94fe\u63a5
                    # \u5904\u7406\u4e3a\u76f8\u5bf9\u8def\u5f84
                    tag_id = tag_href.replace(self.host, '')
                    if not tag_id.startswith('/'):
                        tag_id = '/' + tag_id
                    
                    tags.append({
                        'vod_id': tag_id,
                        'vod_name': f"🏷️ {tag_name}",
                        'vod_pic': '',
                        'vod_remarks': '\u6807\u7b7e',
                        'vod_tag': 'tag',
                        'style': {"type": "rect", "ratio": 1.33}
                    })
            
            print(f"找到 {len(tags)} 个标签")
            
            # \u5206\u9875\u5904\u7406 - \u6807\u7b7e\u9875\u9762\u901a\u5e38\u4e0d\u9700\u8981\u5206\u9875
            result = {}
            result['list'] = tags
            result['page'] = pg
            result['pagecount'] = 1  # \u6807\u7b7e\u9875\u9762\u901a\u5e38\u53ea\u6709\u4e00\u9875
            result['limit'] = 999
            result['total'] = len(tags)
            return result
            
        except Exception as e:
            print(f"getTagsContent error: {e}")
            return {'list': [], 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        url = id
        p = 1
        if self.isVideoFormat(url):
            if '.m3u8' in url:
                url = self.proxy(url)
            p = 0
        self.log(f"播放请求: parse={p}, url={url}")
        print(f"播放请求: parse={p}, url={url}")
        return {'parse': p, 'url': url, 'header': self.headers}

    def localProxy(self, param):
        try:
            if param.get('type') == 'img':
                img_url = self.d64(param['url'])
                if not img_url.startswith(('http://', 'https://')):
                    if img_url.startswith('/'):
                        img_url = f"{self.host}{img_url}"
                    else:
                        img_url = f"{self.host}/{img_url}"
                
                res = requests.get(img_url, headers=self.headers, proxies=self.proxies, timeout=10)
                return [200, res.headers.get('Content-Type', 'image/jpeg'), res.content]
            elif param.get('type') == 'm3u8':
                return self.m3Proxy(param['url'])
            else:
                return self.tsProxy(param['url'])
        except Exception as e:
            print(f"localProxy error: {e}")
            return [500, "text/plain", f"Proxy error: {str(e)}".encode()]

    def proxy(self, data, type='m3u8'):
        if data and len(self.proxies):
            return f"{self.getProxyUrl()}&url={self.e64(data)}&type={type}"
        else:
            return data

    def m3Proxy(self, url):
        try:
            url = self.d64(url)
            ydata = requests.get(url, headers=self.headers, proxies=self.proxies, allow_redirects=False)
            data = ydata.content.decode('utf-8')
            if ydata.headers.get('Location'):
                url = ydata.headers['Location']
                data = requests.get(url, headers=self.headers, proxies=self.proxies).content.decode('utf-8')
            lines = data.strip().split('\n')
            last_r = url[:url.rfind('/')]
            parsed_url = urlparse(url)
            durl = parsed_url.scheme + "://" + parsed_url.netloc
            iskey = True
            for index, string in enumerate(lines):
                if iskey and 'URI' in string:
                    pattern = r'URI="([^"]*)"'
                    match = re.search(pattern, string)
                    if match:
                        lines[index] = re.sub(pattern, f'URI="{self.proxy(match.group(1), "mkey")}"', string)
                        iskey = False
                        continue
                if '#EXT' not in string:
                    if 'http' not in string:
                        domain = last_r if string.count('/') < 2 else durl
                        string = domain + ('' if string.startswith('/') else '/') + string
                    lines[index] = self.proxy(string, string.split('.')[-1].split('?')[0])
            data = '\n'.join(lines)
            return [200, "application/vnd.apple.mpegur", data]
        except Exception as e:
            print(f"m3Proxy error: {e}")
            return [500, "text/plain", f"m3u8 proxy error: {str(e)}".encode()]

    def tsProxy(self, url):
        try:
            url = self.d64(url)
            data = requests.get(url, headers=self.headers, proxies=self.proxies, stream=True)
            return [200, data.headers.get('Content-Type', 'video/mp2t'), data.content]
        except Exception as e:
            print(f"tsProxy error: {e}")
            return [500, "text/plain", f"ts proxy error: {str(e)}".encode()]

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64编码错误: {str(e)}")
            return ""

    def d64(self, encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64解码错误: {str(e)}")
            return ""

    def get_working_host(self):
        """Get working host from known dynamic URLs"""
        dynamic_urls = [
            'https://kanliao2.one/',
            'https://kanliao7.org/',
            'https://kanliao7.net/',
            'https://kanliao14.com/'
        ]
        
        for url in dynamic_urls:
            try:
                response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
                if response.status_code == 200:
                    data = self.getpq(response.text)
                    articles = data('#index article a, #archive article a')
                    if len(articles) > 0:
                        self.log(f"选用可用站点: {url}")
                        print(f"选用可用站点: {url}")
                        return url
            except Exception as e:
                continue
        
        self.log(f"未检测到可用站点，回退: {dynamic_urls[0]}")
        print(f"未检测到可用站点，回退: {dynamic_urls[0]}")
        return dynamic_urls[0]

    def getlist(self, data, tid=''):
        videos = []
        for k in data.items():
            a = k.attr('href')
            b = k('h2').text() or k('.post-card-title').text() or k('.entry-title').text() or k.text()
            c = k('span[itemprop="datePublished"]').text() or k('.post-meta, .entry-meta, time, .post-card-info').text()
            
            # \u8fc7\u6ee4\u5e7f\u544a\uff1a\u68c0\u67e5\u662f\u5426\u5305\u542b"\u70ed\u641cHOT"\u6807\u5fd7
            if self.is_advertisement(k):
                print(f"过滤广告: {b}")
                continue
                
            if a and b and b.strip():
                # \u5904\u7406\u76f8\u5bf9\u8def\u5f84
                if not a.startswith('http'):
                    if a.startswith('/'):
                        vod_id = a
                    else:
                        vod_id = f'/{a}'
                else:
                    vod_id = a
                    
                videos.append({
                    'vod_id': vod_id,
                    'vod_name': b.replace('\n', ' ').strip(),
                    'vod_pic': self.get_article_img(k),
                    'vod_remarks': c.strip() if c else '',
                    'vod_tag': '',
                    'style': {"type": "rect", "ratio": 1.33}
                })
        return videos

    def is_advertisement(self, article_elem):
        """\u5224\u65ad\u662f\u5426\u4e3a\u5e7f\u544a\uff08\u5305\u542b\u70ed\u641cHOT\u6807\u5fd7\uff09"""
        # \u68c0\u67e5.wraps\u5143\u7d20\u662f\u5426\u5305\u542b"\u70ed\u641cHOT"\u6587\u672c
        hot_elements = article_elem.find('.wraps')
        for elem in hot_elements.items():
            if '\u70ed\u641cHOT' in elem.text():
                return True
        
        # \u68c0\u67e5\u6807\u9898\u662f\u5426\u5305\u542b\u5e7f\u544a\u5173\u952e\u8bcd
        title = article_elem('h2').text() or article_elem('.post-card-title').text() or ''
        ad_keywords = ['\u70ed\u641cHOT', '\u624b\u673a\u94fe\u63a5', 'DNS\u8bbe\u7f6e', '\u4fee\u6539DNS', 'WIFI\u8bbe\u7f6e']
        if any(keyword in title for keyword in ad_keywords):
            return True
            
        # \u68c0\u67e5\u80cc\u666f\u989c\u8272\u662f\u5426\u4e3a\u5e7f\u544a\u7279\u6709\u7684\u6e10\u53d8\u80cc\u666f
        style = article_elem.attr('style') or ''
        if 'background:' in style and any(gradient in style for gradient in ['-webkit-linear-gradient', 'linear-gradient']):
            # \u8fdb\u4e00\u6b65\u68c0\u67e5\u662f\u5426\u5305\u542b\u7279\u5b9a\u7684\u5e7f\u544a\u989c\u8272\u7ec4\u5408
            ad_gradients = ['#ec008c,#fc6767', '#ffe259,#ffa751']
            if any(gradient in style for gradient in ad_gradients):
                return True
                
        return False

    def get_article_img(self, article_elem):
        """\u4ece\u6587\u7ae0\u5143\u7d20\u4e2d\u63d0\u53d6\u56fe\u7247\uff0c\u591a\u79cd\u65b9\u5f0f\u5c1d\u8bd5"""
        # \u65b9\u5f0f1: \u4ecescript\u6807\u7b7e\u4e2d\u63d0\u53d6loadBannerDirect
        script_text = article_elem('script').text()
        if script_text:
            match = re.search(r"loadBannerDirect\('([^']+)'", script_text)
            if match:
                url = match.group(1)
                if not url.startswith(('http://', 'https://')):
                    if url.startswith('/'):
                        url = f"{self.host}{url}"
                    else:
                        url = f"{self.host}/{url}"
                return f"{self.getProxyUrl()}&url={self.e64(url)}&type=img"
        
        # \u65b9\u5f0f2: \u4ece\u80cc\u666f\u56fe\u7247\u4e2d\u63d0\u53d6
        bg_elem = article_elem.find('.blog-background')
        if bg_elem:
            style = bg_elem.attr('style') or ''
            bg_match = re.search(r'background-image:\s*url\(["\']?([^"\'\)]+)["\']?\)', style)
            if bg_match:
                img_url = bg_match.group(1)
                if img_url and not img_url.startswith('data:'):
                    if not img_url.startswith(('http://', 'https://')):
                        if img_url.startswith('/'):
                            img_url = f"{self.host}{img_url}"
                        else:
                            img_url = f"{self.host}/{img_url}"
                    return f"{self.getProxyUrl()}&url={self.e64(img_url)}&type=img"
        
        # \u65b9\u5f0f3: \u4ece\u56fe\u7247\u6807\u7b7e\u4e2d\u63d0\u53d6
        img_elem = article_elem.find('img')
        if img_elem:
            data_src = img_elem.attr('data-src')
            if data_src:
                if not data_src.startswith(('http://', 'https://')):
                    if data_src.startswith('/'):
                        data_src = f"{self.host}{data_src}"
                    else:
                        data_src = f"{self.host}/{data_src}"
                return f"{self.getProxyUrl()}&url={self.e64(data_src)}&type=img"
            
            src = img_elem.attr('src')
            if src:
                if not src.startswith(('http://', 'https://')):
                    if src.startswith('/'):
                        src = f"{self.host}{src}"
                    else:
                        src = f"{self.host}/{src}"
                return f"{self.getProxyUrl()}&url={self.e64(src)}&type=img"
        
        return ''

    def getpq(self, data):
        try:
            return pq(data)
        except Exception as e:
            print(f"{str(e)}")
            return pq(data.encode('utf-8'))