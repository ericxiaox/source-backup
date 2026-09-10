import sys
import requests
import re
from urllib.parse import urljoin
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def init(self, extend=""):
        self.host = 'https://xchina001.site'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        }
        print(f"使用站点: {self.host}")

    def getName(self):
        return "\u5c0f\u9ec4\u4e66"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False
    
    def _extractVideoItems(self, html_content):
        vods = []
        video_items = re.findall(r'<div[^>]*class="item video[^>]*>(.*?)</div>', html_content, re.S)
        for item in video_items:
            link_match = re.search(r'<a[^>]*href="(.*?)"[^>]*title="(.*?)"[^>]*>', item)
            if link_match:
                href = link_match.group(1)
                title = link_match.group(2)
                img = ''
                img_match = re.search(r'background-image:url\((.*?)\)', item)
                if img_match:
                    img = img_match.group(1).strip('"\'')
                    if not img.startswith(('http://', 'https://')):
                        img = urljoin(self.host, img)
                
                vods.append({
                    'vod_id': href,
                    'vod_name': title.strip(),
                    'vod_pic': img,
                    'vod_remarks': ''
                })
        
        if not vods:
            general_items = re.findall(r'<a[^>]*href="(/videos/.*?)"[^>]*title="(.*?)"[^>]*>', html_content, re.S)
            for href, title in general_items:
                full_href = urljoin(self.host, href)
                vods.append({
                    'vod_id': full_href,
                    'vod_name': title.strip(),
                    'vod_pic': '',
                    'vod_remarks': ''
                })
        
        return vods

    def homeContent(self, filter):
        result = {}
        classes = []
        video_classes = [
            {'type_name': '\u9ebb\u8c46\u4f20\u5a92', 'type_id': '/videos/series-5f904550b8fcc.html'},
            {'type_name': '\u72ec\u7acb\u521b\u4f5c\u8005', 'type_id': '/videos/series-61bf6e439fed6.html'},
            {'type_name': '\u7cd6\u5fc3Vlog', 'type_id': '/videos/series-61014080dbfde.html'},
            {'type_name': '\u871c\u6843\u4f20\u5a92', 'type_id': '/videos/series-5fe8403919165.html'},
            {'type_name': '\u661f\u7a7a\u4f20\u5a92', 'type_id': '/videos/series-6054e93356ded.html'},
            {'type_name': '\u5929\u7f8e\u4f20\u5a92', 'type_id': '/videos/series-60153c49058ce.html'},
            {'type_name': '\u679c\u51bb\u4f20\u5a92', 'type_id': '/videos/series-5fe840718d665.html'},
            {'type_name': '\u9999\u8549\u89c6\u9891', 'type_id': '/videos/series-65e5f74e4605c.html'},
            {'type_name': '\u7cbe\u4e1c\u5f71\u4e1a', 'type_id': '/videos/series-60126bcfb97fa.html'},
            {'type_name': '\u7231\u8c46\u4f20\u5a92', 'type_id': '/videos/series-63d134c7a0a15.html'},
            {'type_name': '\u674f\u5427\u539f\u7248', 'type_id': '/videos/series-6072997559b46.html'},
            {'type_name': 'IBiZa Media', 'type_id': '/videos/series-64e9cce89da21.html'},
            {'type_name': '\u6027\u89c6\u754c', 'type_id': '/videos/series-63490362dac45.html'},
            {'type_name': 'ED Mosaic', 'type_id': '/videos/series-63732f5c3d36b.html'},
            {'type_name': '\u5927\u8c61\u4f20\u5a92', 'type_id': '/videos/series-65bcaa9688514.html'},
            {'type_name': '\u6263\u6263\u4f20\u5a92', 'type_id': '/videos/series-6230974ada989.html'},
            {'type_name': '\u841d\u8389\u793e', 'type_id': '/videos/series-6360ca9706ecb.html'},
            {'type_name': 'SA\u56fd\u9645\u4f20\u5a92', 'type_id': '/videos/series-633ef3ef07d33.html'},
            {'type_name': '\u5176\u4ed6\u4e2d\u6587AV', 'type_id': '/videos/series-63986aec205d8.html'}
        ]

        classes.extend(video_classes)
        result['class'] = classes
        result['filters'] = {}
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        if tid.startswith('http'):
            url = tid
        else:
            url = urljoin(self.host, tid)
        pg = int(pg) if pg else 1
        if pg > 1:
            if '?' in url:
                url += f"&page={pg}"
            else:
                url += f"?page={pg}"
        
        try:
            res = requests.get(url, headers=self.header, timeout=10)
            res.encoding = 'utf-8'
            html_content = res.text
            # \u4f7f\u7528\u8f85\u52a9\u65b9\u6cd5\u63d0\u53d6\u89c6\u9891\u9879
            vods = self._extractVideoItems(html_content)

            result['list'] = vods
            current_page_items = len(vods)
            has_next_page = '\u4e0b\u4e00\u9875' in html_content or 'next' in html_content.lower() or f'page={pg+1}' in html_content
            if has_next_page:
                pagecount = pg + 1
                total = pagecount * current_page_items
            else:
                pagecount = pg
                total = current_page_items
            
            result['page'] = pg
            result['pagecount'] = pagecount
            result['limit'] = current_page_items
            result['total'] = total
        except Exception as e:
            print(f"categoryContent error: {e}")
            result['list'] = []
            result['page'] = pg
            result['pagecount'] = 1
            result['limit'] = 30
            result['total'] = 0
        return result

    def detailContent(self, ids):
        vid = ids[0]
        url = vid if 'http' in vid else urljoin(self.host, vid)
        vod = {
            'vod_id': vid,
            'vod_name': '\u5c0f\u9ec4\u4e66\u89c6\u9891',
            'vod_pic': '',
            'type_name': '',
            'vod_year': '',
            'vod_area': '',
            'vod_remarks': '',
            'vod_actor': '',
            'vod_director': '',
            'vod_content': ''
        }
        
        try:
            res = requests.get(url, headers=self.header, timeout=10)
            res.encoding = 'utf-8'
            html_content = res.text
            title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.S)
            if title_match:
                vod['vod_name'] = title_match.group(1).strip()
            else:
                title_match_alt = re.search(r'<title>(.*?)</title>', html_content, re.S)
                if title_match_alt:
                    full_title = title_match_alt.group(1).strip()
                    vod['vod_name'] = full_title.split(" - ")[0] if " - " in full_title else full_title
            cover_match = re.search(r'<meta property="og:image" content="(.*?)"', html_content, re.S)
            if cover_match:
                cover_img = cover_match.group(1).strip()
                if not cover_img.startswith(('http://', 'https://')):
                    cover_img = urljoin(self.host, cover_img)
                vod['vod_pic'] = cover_img
            desc_match = re.search(r'<meta name="description" content="(.*?)">', html_content, re.S)
            if desc_match:
                vod['vod_content'] = desc_match.group(1).strip()
            else:
                jsonld_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_content, re.S)
                if jsonld_match:
                    try:
                        import json
                        jsonld_data = json.loads(jsonld_match.group(1))
                        if isinstance(jsonld_data, list):
                            for item in jsonld_data:
                                if isinstance(item, dict) and 'description' in item:
                                    vod['vod_content'] = item['description']
                                    break
                    except:
                        pass

            vod['vod_play_from'] = '\u745f\u4f6c\u5728\u7ebf'
            vod['vod_play_url'] = f'开撸${url}'
        except Exception as e:
            print(f"detailContent error: {e}")
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags):
        url = id
        try:
            res = requests.get(url, headers=self.header, timeout=10)
            res.encoding = 'utf-8'
            html = res.text
            videoplayer_pattern = re.compile(r'const player = new VideoPlayer\(.*?src:\s*["\']([^"\']+?)["\']', re.S)
            videoplayer_match = videoplayer_pattern.search(html)
            if videoplayer_match:
                video_url = videoplayer_match.group(1)
                if re.search(r'\.(m3u8|mp4|ts)', video_url):
                    return {
                        'jx': 0,
                        'parse': 0,
                        'url': video_url,
                        'header': {
                            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
                            'Referer': url
                        }
                    }
            
        except Exception as e:
            print(f"playerContent解析错误: {e}")
        return {'parse': 1, 'url': url, 'header': self.header}

    def searchContent(self, key, quick):
        result = {'list': []}
        try:
            search_url = f'{self.host}/search?q={key}'
            res = requests.get(search_url, headers=self.header, timeout=10)
            res.encoding = 'utf-8'
            html_content = res.text
            vods = self._extractVideoItems(html_content)
            result['list'] = vods
        except Exception as e:
            print(f"searchContent error: {e}")
        return result
    
    def homeVideoContent(self):
        try:
            url = self.host
            res = requests.get(url, headers=self.header, timeout=10)
            res.encoding = 'utf-8'
            html_content = res.text
            vods = self._extractVideoItems(html_content)
            return {'list': vods}
        except Exception as e:
            print(f"homeVideoContent error: {e}")
            return {'list': []}
    
    def localProxy(self, params):
        return None
