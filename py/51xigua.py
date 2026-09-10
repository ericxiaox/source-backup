# -*- coding: utf-8 -*-
# \ud83c\udf08 Love 
import json
import random
import re
import sys
import threading
import time
from base64 import b64decode, b64encode
from urllib.parse import urlparse

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider
try:
    from imgfetch import fetch_img as _shared_fetch_img
except Exception:
    try:
        import os as _os
        sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        from imgfetch import fetch_img as _shared_fetch_img
    except Exception:
        _shared_fetch_img = None
try:
    from hostresolver import resolve_host, parse_ext
except Exception:
    resolve_host = None
    parse_ext = None
# explorer.py\uff08source \u6839\uff09\uff1a\u6c60\u5168\u6302\u65f6\u4ece\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\u6d3b\u57df\uff08\u4e0e hostresolver \u540c\u76ee\u5f55\uff09
try:
    from explorer import explore_hosts
except Exception:
    explore_hosts = None


class Spider(Spider):

    def init(self, extend=""):
        self.proxies = {}
        self._ext = {}
        ext_str = (extend or '').strip()
        if ext_str:
            try:
                cfg = json.loads(ext_str)
                if isinstance(cfg, dict):
                    self.proxies = cfg.get('proxies') or {}
                    for k in ('publish', 'host'):
                        if cfg.get(k):
                            self._ext[k] = str(cfg[k]).strip()
                    if cfg.get('hosts'):
                        hs = cfg['hosts'] if isinstance(cfg['hosts'], list) else [cfg['hosts']]
                        self._ext['hosts'] = [str(h).strip() for h in hs if str(h).strip()]
            except Exception:
                if parse_ext:
                    try:
                        self._ext = parse_ext(ext_str)
                    except Exception:
                        self._ext = {}
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
        return "\u901a\u7528\u5438\u74dc"

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
            
            # Try to get categories from different possible locations
            category_selectors = [
                '.category-list ul li',
                '.nav-menu li',
                '.menu li',
                'nav ul li'
            ]
            
            for selector in category_selectors:
                for k in data(selector).items():
                    link = k('a')
                    href = (link.attr('href') or '').strip()
                    name = (link.text() or '').strip()
                    # Skip placeholder or invalid entries
                    if not href or href == '#' or not name:
                        continue
                    classes.append({
                        'type_name': name,
                        'type_id': href
                    })
                if classes:
                    break
            
            # If no categories found, create some default ones
            if not classes:
                classes = [
                    {'type_name': '\u9996\u9875', 'type_id': '/'},
                    {'type_name': '\u6700\u65b0', 'type_id': '/latest/'},
                    {'type_name': '\u70ed\u95e8', 'type_id': '/hot/'}
                ]
            
            result['class'] = classes
            result['list'] = self.getlist(data('#index article a'))
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
            if '@folder' in tid:
                id = tid.replace('@folder', '')
                videos = self.getfod(id)
            else:
                # Build URL properly
                if tid.startswith('/'):
                    if pg and pg != '1':
                        url = f"{self.host}{tid}page/{pg}/"
                    else:
                        url = f"{self.host}{tid}"
                else:
                    url = f"{self.host}/{tid}"
                    
                response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
                if response.status_code != 200:
                    return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}
                    
                data = self.getpq(response.text)
                videos = self.getlist(data('#archive article a, #index article a'), tid)
                
            result = {}
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = 1 if '@folder' in tid else 99999
            result['limit'] = 90
            result['total'] = 999999
            return result
            
        except Exception as e:
            print(f"categoryContent error: {e}")
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}

    def detailContent(self, ids):
        try:
            url = f"{self.host}{ids[0]}" if not ids[0].startswith('http') else ids[0]
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            if response.status_code != 200:
                return {'list': [{'vod_play_from': '\u901a\u7528\u5438\u74dc', 'vod_play_url': f'页面加载失败${url}'}]}
                
            data = self.getpq(response.text)
            vod = {'vod_play_from': '\u901a\u7528\u5438\u74dc'}
            
            # Get content/description
            try:
                clist = []
                if data('.tags .keywords a'):
                    for k in data('.tags .keywords a').items():
                        title = k.text()
                        href = k.attr('href')
                        if title and href:
                            clist.append('[a=cr:' + json.dumps({'id': href, 'name': title}) + '/]' + title + '[/a]')
                vod['vod_content'] = ' '.join(clist) if clist else data('.post-title').text()
            except:
                vod['vod_content'] = data('.post-title').text() or '\u901a\u7528\u5438\u74dc\u89c6\u9891'
            
            # Get video URLs (build episode list when multiple players exist)
            try:
                plist = []
                used_names = set()
                if data('.dplayer'):
                    for c, k in enumerate(data('.dplayer').items(), start=1):
                        config_attr = k.attr('data-config')
                        if config_attr:
                            try:
                                config = json.loads(config_attr)
                                video_url = config.get('video', {}).get('url', '')
                                # Determine a readable episode name from nearby headings if present
                                ep_name = ''
                                try:
                                    parent = k.parents().eq(0)
                                    # search up to a few ancestors for a heading text
                                    for _ in range(3):
                                        if not parent: break
                                        heading = parent.find('h2, h3, h4').eq(0).text() or ''
                                        heading = heading.strip()
                                        if heading:
                                            ep_name = heading
                                            break
                                        parent = parent.parents().eq(0)
                                except Exception:
                                    ep_name = ''
                                base_name = ep_name if ep_name else f"视频{c}"
                                name = base_name
                                count = 2
                                # Ensure the name is unique
                                while name in used_names:
                                    name = f"{base_name} {count}"
                                    count += 1
                                used_names.add(name)
                                if video_url:
                                    self.log(f"解析到视频: {name} -> {video_url}")
                                    print(f"解析到视频: {name} -> {video_url}")
                                    plist.append(f"{name}${video_url}")
                            except:
                                continue
                
                if plist:
                    self.log(f"拼装播放列表，共{len(plist)}个")
                    print(f"拼装播放列表，共{len(plist)}个")
                    vod['vod_play_url'] = '#'.join(plist)
                else:
                    vod['vod_play_url'] = f"未找到视频源${url}"
                    
            except Exception as e:
                vod['vod_play_url'] = f"视频解析失败${url}"
                
            return {'list': [vod]}
            
        except Exception as e:
            print(f"detailContent error: {e}")
            return {'list': [{'vod_play_from': '\u901a\u7528\u5438\u74dc', 'vod_play_url': f'详情页加载失败${ids[0] if ids else ""}'}]}

    def searchContent(self, key, quick, pg="1"):
        try:
            url = f"{self.host}/search/{key}/{pg}" if pg != "1" else f"{self.host}/search/{key}/"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            if response.status_code != 200:
                return {'list': [], 'page': pg}
                
            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article a, #index article a'))
            return {'list': videos, 'page': pg}
            
        except Exception as e:
            print(f"searchContent error: {e}")
            return {'list': [], 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        url = id
        p = 1
        if self.isVideoFormat(url):
            # m3u8/mp4 direct play; when using proxy setting, wrap to proxy for m3u8
            if '.m3u8' in url:
                url = self.proxy(url)
            p = 0
        self.log(f"播放请求: parse={p}, url={url}")
        print(f"播放请求: parse={p}, url={url}")
        return {'parse': p, 'url': url, 'header': self.headers}

    def localProxy(self, param):
        if param.get('type') == 'img':
            # \u5171\u4eab\u52a0\u901f\u901a\u9053\uff1aSession \u8fde\u63a5\u590d\u7528 + \u89e3\u5bc6 LRU \u7f13\u5b58\uff082026-09-08 \u5217\u8868\u63d0\u901f\uff09
            if _shared_fetch_img is not None:
                mime, data = _shared_fetch_img(param['url'], headers=self.headers,
                                               decrypt=self.aesimg, timeout=15,
                                               proxies=self.proxies or None)
                if data:
                    return [200, mime, data]
                return [404, 'text/plain', b'']
            res=requests.get(param['url'], headers=self.headers, proxies=self.proxies, timeout=10)
            return [200,res.headers.get('Content-Type'),self.aesimg(res.content)]
        elif param.get('type') == 'm3u8':return self.m3Proxy(param['url'])
        else:return self.tsProxy(param['url'])

    def proxy(self, data, type='m3u8'):
        if data and len(self.proxies):return f"{self.getProxyUrl()}&url={self.e64(data)}&type={type}"
        else:return data

    def m3Proxy(self, url):
        url=self.d64(url)
        ydata = requests.get(url, headers=self.headers, proxies=self.proxies, allow_redirects=False)
        data = ydata.content.decode('utf-8')
        if ydata.headers.get('Location'):
            url = ydata.headers['Location']
            data = requests.get(url, headers=self.headers, proxies=self.proxies).content.decode('utf-8')
        lines = data.strip().split('\n')
        last_r = url[:url.rfind('/')]
        parsed_url = urlparse(url)
        durl = parsed_url.scheme + "://" + parsed_url.netloc
        iskey=True
        for index, string in enumerate(lines):
            if iskey and 'URI' in string:
                pattern = r'URI="([^"]*)"'
                match = re.search(pattern, string)
                if match:
                    lines[index] = re.sub(pattern, f'URI="{self.proxy(match.group(1), "mkey")}"', string)
                    iskey=False
                    continue
            if '#EXT' not in string:
                if 'http' not in string:
                    domain = last_r if string.count('/') < 2 else durl
                    string = domain + ('' if string.startswith('/') else '/') + string
                lines[index] = self.proxy(string, string.split('.')[-1].split('?')[0])
        data = '\n'.join(lines)
        return [200, "application/vnd.apple.mpegur", data]

    def tsProxy(self, url):
        url = self.d64(url)
        data = requests.get(url, headers=self.headers, proxies=self.proxies, stream=True)
        return [200, data.headers['Content-Type'], data.content]

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
        """\u52a8\u6001\u57df\u540d\u89e3\u6790 v2\uff08hostresolver\uff09\uff1aext \u9501\u5b9a \u2192 \u65e7\u57df302\u8ddf\u968f + \u6cdb\u89e3\u6790\u5019\u9009\u5e76\u884c\u5b9e\u6d4b
        \u2192 \u6210\u529f\u7f13\u5b5830\u5206\u949f\u3002\u5168\u90e8\u5931\u8d25\u8fd4\u56de ''\uff08\u63a5\u53e3\u5c42\u515c\u7a7a\uff0c\u574f\u5f97\u660e\u660e\u767d\u767d\uff09\u3002
        2026-09-08 \u5b9e\u6d4b\uff1anlwkmsv \u57fa\u57df\u5df2\u8f6e\u6362\u4e3a ucorfqmp.cc\uff0c\u65e7\u57df 302 \u8df3\u8f6c\u4ecd\u6d3b\uff1b
        \u6cdb\u89e3\u6790\u7279\u5f81\u786e\u8ba4\uff08\u4efb\u610f\u8bcd\u5b50\u57df\u5747\u51fa\u5168\u7ad9\uff09\uff0cresolver \u6cdb\u751f\u6210\u5019\u9009\u9002\u7528\u3002"""
        ext = getattr(self, '_ext', {}) or {}
        if ext.get('host'):
            return ext['host'].rstrip('/')
        publish = ext.get('publish') or 'https://advise.nlwkmsv.cc/'
        builtin_hosts = [
            'https://advise.ucorfqmp.cc/',    # 2026-09-08 \u5b9e\u6d4b\u73b0\u5f79\u955c\u50cf(266KB\u5b8c\u6574\u7ad9)
            'https://advise.nlwkmsv.cc/',     # \u65e7\u57fa\u57df\uff0c302 -> ucorfqmp.cc
        ]
        if resolve_host:
            h = resolve_host(
                publish_page=publish,
                candidate_hosts=list(ext.get('hosts') or []) + builtin_hosts,
                headers=self.headers,
                proxies=self.proxies,
                timeout=8,
            )
            if h:
                return h
        # \u7ec8\u6781\u515c\u5e95\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\uff08\u8df3\u8f6c\u58f3/\u95e8\u6237/\u6cdb\u89e3\u6790\u8ddf\u968f + \u7ad9\u540d\u8eab\u4efd\u9a8c\u8bc1\uff09
        if explore_hosts:
            try:
                def _probe(u):
                    r = requests.get(u.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=8, verify=False)
                    return r.status_code == 200 and '51\u5403\u74dc' in (r.text or '')
                hs = explore_hosts(['51cg', '51\u5403\u74dc'], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        return (ext.get('hosts') or builtin_hosts)[0].rstrip('/')


    def getlist(self, data, tid=''):
        videos = []
        l = '/mrdg' in tid
        for k in data.items():
            a = k.attr('href')
            b = k('h2').text()
            # Some pages might not include datePublished; use a fallback
            c = k('span[itemprop="datePublished"]').text() or k('.post-meta, .entry-meta, time').text()
            if a and b:
                videos.append({
                    'vod_id': f"{a}{'@folder' if l else ''}",
                    'vod_name': b.replace('\n', ' '),
                    'vod_pic': self.getimg(k('script').text()),
                    'vod_remarks': c or '',
                    'vod_tag': 'folder' if l else '',
                    'style': {"type": "rect", "ratio": 1.33}
                })
        return videos

    def getfod(self, id):
        url = f"{self.host}{id}"
        data = self.getpq(requests.get(url, headers=self.headers, proxies=self.proxies).text)
        vdata=data('.post-content[itemprop="articleBody"]')
        r=['.txt-apps','.line','blockquote','.tags','.content-tabs']
        for i in r:vdata.remove(i)
        p=vdata('p')
        videos=[]
        for i,x in enumerate(vdata('h2').items()):
            c=i*2
            videos.append({
                'vod_id': p.eq(c)('a').attr('href'),
                'vod_name': p.eq(c).text(),
                'vod_pic': f"{self.getProxyUrl()}&url={p.eq(c+1)('img').attr('data-xkrkllgl')}&type=img",
                'vod_remarks':x.text()
                })
        return videos

    def getimg(self, text):
        match = re.search(r"loadBannerDirect\('([^']+)'", text)
        if match:
            url = match.group(1)
            return f"{self.getProxyUrl()}&url={url}&type=img"
        else:
            return ''

    def aesimg(self, word):
        key = b'f5d965df75336270'
        iv = b'97b60394abc2fbe1'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(word), AES.block_size)
        return decrypted

    def getpq(self, data):
        try:
            return pq(data)
        except Exception as e:
            print(f"{str(e)}")
            return pq(data.encode('utf-8'))
