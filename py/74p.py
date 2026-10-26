import sys, re, json, requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from base.spider import Spider

# \u5ffd\u7565 SSL \u8bc1\u4e66\u8b66\u544a
requests.packages.urllib3.disable_warnings()

class Spider(Spider):
    def getName(self): return "74P\u798f\u5229(\u6f2b\u753b\u7248)"
    
    def init(self, extend=""):
        super().init(extend)
        self.base_url = "https://www.74p.net"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.base_url + '/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=retries)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

    def destroy(self):
        if hasattr(self, 'session'): self.session.close()

    def fetch(self, url, headers=None):
        req_headers = headers or self.headers.copy()
        try:
            return self.session.get(url, headers=req_headers, timeout=10, verify=False, allow_redirects=True)
        except:
            return None

    def homeContent(self, filter):
        cats = [
            {"type_name": "=== \u5199\u771f ===", "type_id": "ignore"},
            {"type_name": "\u79c0\u4eba\u7f51", "type_id": "xiurenwang"},
            {"type_name": "\u8bed\u753b\u754c", "type_id": "yuhuajie"},
            {"type_name": "\u82b1\u6f3e", "type_id": "huayang"},
            {"type_name": "\u661f\u989c\u793e", "type_id": "xingyanshe"},
            {"type_name": "\u55f2\u56e1\u56e1", "type_id": "feilin"},
            {"type_name": "\u7231\u871c\u793e", "type_id": "aimishe"},
            {"type_name": "\u6ce2\u841d\u793e", "type_id": "boluoshe"},
            {"type_name": "\u5c24\u7269\u9986", "type_id": "youwuguan"},
            {"type_name": "\u871c\u6843\u793e", "type_id": "miitao"},
            {"type_name": "=== \u6f2b\u753b ===", "type_id": "ignore"},
            {"type_name": "\u65e5\u672c\u6f2b\u753b", "type_id": "comic/category/jp"},
            {"type_name": "\u97e9\u56fd\u6f2b\u753b", "type_id": "comic/category/kr"},
            {"type_name": "=== \u5c0f\u8bf4 ===", "type_id": "ignore"},
            {"type_name": "\u90fd\u5e02", "type_id": "novel/category/Urban"},
            {"type_name": "\u4e71\u4f26", "type_id": "novel/category/Incestuous"},
            {"type_name": "\u7384\u5e7b", "type_id": "novel/category/Xuanhuan"},
            {"type_name": "\u6b66\u4fa0", "type_id": "novel/category/Wuxia"}
        ]
        return {'class': [c for c in cats if c['type_id'] != 'ignore']}

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        url = f"{self.base_url}/{tid}/page/{pg}"
        return self._get_post_list(url, pg)

    def _get_post_list(self, url, pg):
        resp = self.fetch(url)
        vlist = []
        if resp and resp.status_code == 200:
            resp.encoding = 'utf-8'
            html = resp.text
            
            list_block = html
            main_block = re.search(r'(?:id="index_ajax_list"|class="site-main")[^>]*>(.*?)<(?:footer|aside)', html, re.S)
            if main_block: list_block = main_block.group(1)
            
            items = re.findall(r'<li[^>]*>(.*?)</li>', list_block, re.S)
            for item in items:
                href_match = re.search(r'href=["\']([^"\']+)["\']', item)
                if not href_match: continue
                href = href_match.group(1)
                
                if any(x in href for x in ['.css', '.js', 'templates/', 'wp-includes']): continue

                img_match = re.search(r'data-original=["\']([^"\']+)["\']', item)
                if not img_match: img_match = re.search(r'src=["\']([^"\']+)["\']', item)
                pic = img_match.group(1) if img_match else ""
                
                if not pic: pic = "https://www.74p.net/static/images/cover.png"
                
                title_match = re.search(r'title=["\']([^"\']+)["\']', item)
                name = title_match.group(1) if title_match else re.sub(r'<[^>]+>', '', item).strip().split('\n')[0]
                if name.startswith('.') or '{' in name or len(name) > 100: continue
                
                if href.startswith('//'): href = 'https:' + href
                elif href.startswith('/'): href = self.base_url + href

                vlist.append({
                    'vod_id': href,
                    'vod_name': name,
                    'vod_pic': pic,
                    'vod_remarks': '\u70b9\u51fb\u67e5\u770b',
                    'style': {"type": "rect", "ratio": 1.33}
                })
        
        return {'list': vlist, 'page': pg, 'pagecount': pg + 1 if len(vlist) >= 15 else pg, 'limit': 20, 'total': 9999}

    def searchContent(self, key, quick, pg=1):
        search_path = f"/search/{key}"
        headers = self.headers.copy()
        if "\u6f2b\u753b" in key: headers['Referer'] = f"{self.base_url}/comic"
        else: headers['Referer'] = f"{self.base_url}/novel"
        if int(pg) > 1: url = f"{self.base_url}{search_path}/page/{pg}"
        else: url = f"{self.base_url}{search_path}"
        return self._get_post_list(url, int(pg))

    # ==========================
    #  \u8be6\u60c5\u9875\uff1a\u53ea\u89e3\u6790\u7ae0\u8282\u5217\u8868
    # ==========================
    def detailContent(self, ids):
        url = ids[0]
        resp = self.fetch(url)
        if not resp: return {'list': []}

        resp.encoding = 'utf-8'
        html = resp.text
        
        vod = {
            'vod_id': url,
            'vod_name': '',
            'vod_pic': '',
            'type_name': '\u6f2b\u753b',
            'vod_content': '',
            'vod_play_from': '74P\u6f2b\u753b',
            'vod_play_url': ''
        }

        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html)
        if h1: vod['vod_name'] = h1.group(1)
        
        desc_match = re.search(r'<div class="entry-content"[^>]*>(.*?)</div>', html, re.S)
        if desc_match: 
            clean_desc = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()
            vod['vod_content'] = clean_desc[:200]
        
        play_list = []
        
        # 1. \u5c1d\u8bd5\u67e5\u627e\u7ae0\u8282\u5217\u8868
        chapter_links = re.findall(r'<a[^>]+href=["\']([^"\']*/(?:comic|novel)/chapter/[^"\']+)["\'][^>]*>(.*?)</a>', html)
        
        if chapter_links:
            for href, name in chapter_links:
                if href.startswith('//'): href = 'https:' + href
                elif href.startswith('/'): href = self.base_url + href
                name = name.strip()
                play_list.append(f"{name}${href}")
        else:
            # 2. \u5982\u679c\u6ca1\u6709\u76ee\u5f55\uff0c\u76f4\u63a5\u8fd4\u56de\u5f53\u524d\u9875\u9762
            play_list.append(f"在线观看${url}")

        vod['vod_play_url'] = "#".join(play_list)
        return {'list': [vod]}

    # ==========================
    #  \u64ad\u653e\u9875\uff1a\u6293\u53d6\u56fe\u7247\u5e76\u62fc\u63a5
    # ==========================
    def playerContent(self, flag, id, vipFlags):
        # id \u662f detailContent \u4f20\u5165\u7684\u7ae0\u8282\u94fe\u63a5
        images = self._scrape_all_images(id)
        
        # \u4fee\u6539\uff1a\u4f7f\u7528 && \u62fc\u63a5\u6240\u6709\u56fe\u7247\u94fe\u63a5
        novel_data = "&&".join(images)
        
        return {
            "parse": 0,
            "playUrl": "",
            "url": f'pics://{novel_data}',
            "header": ""
        }

    # ==========================
    #  \u5de5\u5177\uff1a\u7ffb\u9875\u6293\u53d6\u6240\u6709\u56fe\u7247
    # ==========================
    def _scrape_all_images(self, url):
        images = []
        visited = set()
        current_url = url
        page = 1
        max_pages = 50 
        
        while page <= max_pages:
            if current_url in visited: break
            visited.add(current_url)
            
            resp = self.fetch(current_url)
            if not resp or resp.status_code != 200: break
            resp.encoding = 'utf-8'
            html = resp.text
            
            content_match = re.search(r'(?:id="content"|class="entry-content"|class="single-content")[^>]*>(.*?)<(?:div class="related|footer|section)', html, re.S)
            content_html = content_match.group(1) if content_match else html
            
            img_matches = re.findall(r'<img[^>]+(?:src|data-original|data-src)=["\']([^"\']+)["\']', content_html)
            for src in img_matches:
                if any(x in src.lower() for x in ['.gif', '.svg', 'logo', 'avatar', 'icon']): continue
                if src.startswith('//'): src = 'https:' + src
                elif src.startswith('/'): src = self.base_url + src
                if src not in images:
                    images.append(src)
            
            next_url = None
            next_match = re.search('<a[^>]+href=["\\\']([^"\\\']+)["\\\'][^>]*>(?:\u4e0b\u4e00\u9875|Next|\u00bb)', html, re.I)
            if not next_match:
                next_match = re.search(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*class=["\'][^"\']*next[^"\']*["\']', html, re.I)
            
            if not next_match and '/comic/chapter/' not in current_url and 'page' in current_url:
                 base = current_url.rsplit('/', 1)[0]
                 candidate = f"{base}/{page+1}"
                 next_url = candidate
            elif next_match:
                href = next_match.group(1)
                if href.startswith('//'): next_url = 'https:' + href
                elif href.startswith('/'): next_url = self.base_url + href
                else: next_url = href
            
            if not next_url: break
            current_url = next_url
            page += 1
            
        return images
