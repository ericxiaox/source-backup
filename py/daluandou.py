import json
import re
import sys
import hashlib
from base64 import b64decode, b64encode
from urllib.parse import urlparse

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider as BaseSpider
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
    from hostresolver import resolve_host, parse_ext, probe_first
except Exception:
    resolve_host = None
    probe_first = None
    parse_ext = None
# explorer.py\uff08source \u6839\uff09\uff1a\u6c60\u5168\u6302\u65f6\u4ece\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\u6d3b\u57df\uff08\u4e0e hostresolver \u540c\u76ee\u5f55\uff09
try:
    from explorer import explore_hosts
except Exception:
    explore_hosts = None

img_cache = {}



class Spider(BaseSpider):

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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        }
        self.host = self.get_working_host()
        self.headers.update({'Origin': self.host, 'Referer': f"{self.host}/"})
        print(f"使用站点: {self.host}")

    def getName(self):
        return "\U0001f308 \u6bcf\u65e5\u5927\u4e71\u6597|\u7ec8\u6781\u5b8c\u7f8e\u7248"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        global img_cache
        img_cache.clear()

    def _resolve_inline(self, publish, builtin, validate):
        """hostresolver \u672a\u52a0\u8f7d\u65f6\u7684\u5185\u8054\u5e76\u884c\u63a2\u6d4b\uff1a\u907f\u514d\u4e32\u884c 8s\u00d7N \u5bfc\u81f4 App \u7aef\u7a7a\u8f6c\u51e0\u5341\u79d2\u3002
        \u5e26\u6781\u7b80\u5185\u5bb9\u5f62\u6001\u5224\uff0c\u9632\u6b62\u547d\u4e2d\u53d1\u5e03\u9875/\u95e8\u6237\u516c\u544a\u9875\uff08\u6709\u7ad9\u540d\u4f46\u65e0\u5185\u5bb9\uff09\u3002"""
        import threading
        import re
        ext = getattr(self, '_ext', {}) or {}
        candidates = []
        if publish:
            candidates.append(publish)
        candidates += list(ext.get('hosts') or [])
        candidates += list(builtin or [])
        seen = set()
        deduped = []
        for u in candidates:
            u = (u or '').strip().rstrip('/')
            if not u:
                continue
            if not u.startswith('http'):
                u = 'https://' + u
            if u not in seen:
                seen.add(u)
                deduped.append(u)
        if not deduped:
            return ''
        result = [None]
        content_marks = ('<article', 'post-card', 'entry-title', 'post-title',
                         'video-item', 'oneVideo', 'playlist', 'class="video')
        content_link_pat = re.compile(
            r'href=["\'][^"\']*/(?:archives?|video|videos|category|categories|post|vod|'
            r'watch|tag|detail|thread|topic)[/"\']', re.I)

        def _looks_like_content(t):
            return bool(t and (len(t) > 80000 or any(k in t for k in content_marks)
                               or len(content_link_pat.findall(t)) >= 5))

        def _probe_one(u):
            if result[0]:
                return
            try:
                r = requests.get(u + '/', headers=self.headers, proxies=self.proxies,
                                 timeout=5, verify=False, allow_redirects=True)
                if r.status_code == 200 and validate(r.url, r.text) and _looks_like_content(r.text):
                    if not result[0]:
                        result[0] = r.url.rstrip('/')
            except Exception:
                pass
        threads = [threading.Thread(target=_probe_one, args=(u,)) for u in deduped]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
        if not result[0] and publish:
            # \u6df1\u5ea6\u62bd\u94fe\uff08\u5bf9\u6807 hostresolver.extract_publish_domains\uff09\uff1a\u53d1\u5e03\u9875\u4e0d\u662f\u6d3b\u955c\u50cf\u65f6\uff0c
            # \u4ece\u5176 JS/HTML \u6316\u57fa\u57df\u2014\u2014\u542b words.random()+'.base.cc' \u6cdb\u89e3\u6790\u5f62\u6001\u2014\u2014\u751f\u6210\u5019\u9009\u518d\u63a2\uff0c
            # \u4f7f gitee \u8fdc\u7a0b\u5bfc\u5165\u5f62\u6001\uff08\u65e0 hostresolver \u6a21\u5757\uff09\u4e0e\u672c\u5730\u5305\u540c\u7b49\u81ea\u52a8\u6362\u57df\u80fd\u529b\u3002
            try:
                _pr = requests.get(publish, headers=self.headers, proxies=self.proxies,
                                   timeout=6, verify=False, allow_redirects=True)
                _pt = _pr.text or ''
            except Exception:
                _pt = ''
            if _pt:
                # \u4f18\u5148\u4ece\u542b random() \u7684 <script> \u6bb5\u62bd\uff08\u90a3\u91cc\u624d\u662f\u6cdb\u89e3\u6790\u8bcd\u8868+\u57fa\u57df\uff09\uff0c\u515c\u5e95\u5168\u9875
                _chunks = [c for c in re.findall(r'<script[^>]*>(.*?)</script>', _pt, re.S | re.I)
                           if 'random(' in c]
                _wsrc = '\n'.join(_chunks) if _chunks else _pt
                _bases = []
                for _m in re.findall(r'''['"]\.?((?:[a-z0-9-]+\.)+(?:cc|com|net|top|xyz|vip|app|link|click|org|info|site|online|icu|club|fun|store|live|me|tv))['"]''', _wsrc, re.I):
                    _m = _m.lower().strip('.').strip()
                    if _m and _m not in _bases and _m.count('.') <= 2:
                        _bases.append(_m)
                if not _bases:
                    for _m in re.findall(r'''['"]\.?((?:[a-z0-9-]+\.)+(?:cc|com|net|top|xyz|vip|app|link|click|org|info|site|online|icu|club|fun|store|live|me|tv))['"]''', _pt, re.I):
                        _m = _m.lower().strip('.').strip()
                        if _m and _m not in _bases and _m.count('.') <= 2:
                            _bases.append(_m)
                _slds = [b for b in _bases if b.count('.') == 1]   # \u6cdb\u89e3\u6790\u57fa\u57df\uff08\u8bcd.sld.tld\uff09
                _fulls = [b for b in _bases if b.count('.') > 1]   # \u5b8c\u6574\u57df\uff08\u5982 cloudfront \u56fa\u5b9a\u7ebf\u8def\uff09
                _words = []
                for w in re.findall(r'''['"]([a-z]{3,9})['"]''', _wsrc):
                    if w.lower() not in _words:
                        _words.append(w.lower())
                if not _words:
                    _words = ['berry', 'melon', 'apple', 'kiwi', 'lemon', 'mango',
                              'peach', 'grape', 'plum', 'fig', 'papaya', 'guava']
                _gen = []
                for u in (_fulls[:3] + _slds[:3]):      # SLD/\u5b8c\u6574\u57df\u672c\u8eab\u4e5f\u76f4\u63a2\u4e00\u6b21
                    _u = 'https://' + u
                    if _u not in _gen:
                        _gen.append(_u)
                if _slds:
                    for i in range(12):                 # \u8bcd\u00d7\u57fa\u57df\u8f6e\u8f6c\uff0c\u4e0d\u8ba9\u5355\u57fa\u57df\u9738\u5360\u540d\u989d
                        if len(_gen) >= 12:
                            break
                        _b = _slds[i % len(_slds)]
                        _u = 'https://' + _words[i % len(_words)] + '.' + _b
                        if _u not in _gen:
                            _gen.append(_u)
                _t2 = [threading.Thread(target=_probe_one, args=(u,)) for u in _gen[:12]]
                for t in _t2:
                    t.start()
                for t in _t2:
                    t.join(timeout=10)
        return result[0] or ''

    def get_working_host(self):
        """\u52a8\u6001\u57df\u540d\u89e3\u6790 v2\uff08hostresolver\uff09\uff1aext \u9501\u5b9a \u2192 \u53d1\u5e03\u9875\u9759\u6001\u955c\u50cf\u5e76\u884c\u5b9e\u6d4b
        \u2192 \u65e7\u57df302\u8ddf\u968f\u515c\u5e95 \u2192 \u6210\u529f\u7f13\u5b5830\u5206\u949f\u3002\u5168\u5931\u8d25\u8fd4\u56de ''\uff08\u63a5\u53e3\u5c42\u515c\u7a7a\uff09\u3002
        2026-09-08 \u5b9e\u6d4b\uff1abshzjjgq \u57fa\u57df\u5df2\u8f6e\u6362\u4e3a loewkgyyv.cc\uff08border 302 \u4ecd\u6d3b\uff09\uff1b
        \u7ad9\u65b9\u53d1\u5e03\u95e8\u6237 idld65.com \u9759\u6001\u5217\u51fa capture/carrier/center.loewkgyyv.cc \u73b0\u5f79\u955c\u50cf\u3002"""
        ext = getattr(self, '_ext', {}) or {}
        if ext.get('host'):
            return ext['host'].rstrip('/')
        publish = ext.get('publish') or 'https://idld65.com/'
        builtin_hosts = [
            'https://border.ekszkcyce.cc/',   # 2026-09-11 \u5f53\u524d\u6d3b\u955c\u50cf
            'https://capture.ekszkcyce.cc/',
            'https://border.loewkgyyv.cc/',   # 2026-09-08 \u5b9e\u6d4b\u73b0\u5f79\u955c\u50cf(190KB\u5b8c\u6574\u7ad9)
            'https://capture.loewkgyyv.cc/',
            'https://fe7.loewkgyyv.cc/',
            'https://border.bshzjjgq.cc/',    # \u65e7\u57fa\u57df\uff0c302 -> loewkgyyv.cc
        ]

        def _validate(host, text):
            return '\u6bcf\u65e5\u5927\u4e71\u6597' in (text or '')

        if resolve_host:
            h = resolve_host(
                publish_page=publish,
                candidate_hosts=list(ext.get('hosts') or []) + builtin_hosts,
                headers=self.headers,
                proxies=self.proxies,
                timeout=8,
                validate=_validate,
                site_key='\u6bcf\u65e5\u5927\u4e71\u6597',
            )
            if h:
                return h
        # \u515c\u5e95\uff1ahostresolver \u5df2\u52a0\u8f7d\u5219\u7528 probe_first\uff1b\u672a\u52a0\u8f7d\u5219\u5185\u8054\u5e76\u884c\u63a2\u6d4b
        cands = list(ext.get('hosts') or []) + builtin_hosts
        if probe_first:
            try:
                h = probe_first(cands, headers=self.headers, proxies=self.proxies,
                                timeout=5, validate=_validate, tag='\u515c\u5e95')
                if h:
                    return h
            except Exception:
                pass
        else:
            h = self._resolve_inline(publish, builtin_hosts, _validate)
            if h:
                return h
        # \u7ec8\u6781\u515c\u5e95\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\uff08\u8df3\u8f6c\u58f3/\u95e8\u6237/\u6cdb\u89e3\u6790\u8ddf\u968f + \u7ad9\u540d\u8eab\u4efd\u9a8c\u8bc1\uff09
        if explore_hosts:
            try:
                def _probe(u):
                    r = requests.get(u.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=5, verify=False)
                    return r.status_code == 200 and '\u6bcf\u65e5\u5927\u4e71\u6597' in (r.text or '')
                hs = explore_hosts(['dldd', '\u5927\u4e71\u6597'], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        return ''

    def homeContent(self, filter):

        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200: return {'class': [], 'list': []}
            data = self.getpq(response.text)
            
            classes = []
            category_selectors = ['.category-list ul li', '.nav-menu li', '.menu li', 'nav ul li']
            for selector in category_selectors:
                for k in data(selector).items():
                    link = k('a')
                    href = (link.attr('href') or '').strip()
                    name = (link.text() or '').strip()
                    if not href or href == '#' or not name: continue
                    classes.append({'type_name': name, 'type_id': href})
                if classes: break
            
            if not classes:
                classes = [{'type_name': '\u6700\u65b0', 'type_id': '/latest/'}, {'type_name': '\u70ed\u95e8', 'type_id': '/hot/'}]
            
            return {'class': classes, 'list': self.getlist(data('#index article, article'))}
        except Exception as e:
            return {'class': [], 'list': []}

    def homeVideoContent(self):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200: return {'list': []}
            data = self.getpq(response.text)
            return {'list': self.getlist(data('#index article, article'))}
        except Exception as e:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            if '@folder' in tid:
                v = self.getfod(tid.replace('@folder', ''))
                return {'list': v, 'page': 1, 'pagecount': 1, 'limit': 90, 'total': len(v)}
            
            pg = int(pg) if pg else 1
            
            if tid.startswith('http'):
                base_url = tid.rstrip('/')
            else:
                path = tid if tid.startswith('/') else f"/{tid}"
                base_url = f"{self.host}{path}".rstrip('/')
            
            if pg == 1:
                url = f"{base_url}/"
            else:
                url = f"{base_url}/{pg}/"
                
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200: return {'list': [], 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 0}
                
            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article, #index article, article'), tid)
            
            return {'list': videos, 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 999999}
        except Exception as e:
            return {'list': [], 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 0}

    def detailContent(self, ids):
        try:
            url = ids[0] if ids[0].startswith('http') else f"{self.host}{ids[0]}"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            data = self.getpq(response.text)
            
            plist = []
            used_names = set()
            if data('.dplayer'):
                for c, k in enumerate(data('.dplayer').items(), start=1):
                    try:
                        config_attr = k.attr('data-config')
                        if config_attr:
                            config = json.loads(config_attr)
                            video_url = config.get('video', {}).get('url', '')
                            
                            if video_url:
                                ep_name = ''
                                parent = k.parents().eq(0)
                                for _ in range(4):
                                    if not parent: break
                                    heading = parent.find('h2, h3, h4').eq(0).text().strip()
                                    if heading:
                                        ep_name = heading
                                        break
                                    parent = parent.parents().eq(0)
                                
                                base_name = ep_name if ep_name else f"视频{c}"
                                name = base_name
                                count = 2
                                while name in used_names:
                                    name = f"{base_name} {count}"
                                    count += 1
                                used_names.add(name)
                                
                                plist.append(f"{name}${video_url}")
                    except: continue
            
            if not plist:
                content_area = data('.post-content, article')
                for i, link in enumerate(content_area('a').items(), start=1):
                    link_text = link.text().strip()
                    link_href = link.attr('href')
                    
                    if link_href and any(kw in link_text for kw in ['\u70b9\u51fb\u89c2\u770b', '\u89c2\u770b', '\u64ad\u653e', '\u89c6\u9891', '\u7b2c\u4e00\u5f39', '\u7b2c\u4e8c\u5f39', '\u7b2c\u4e09\u5f39', '\u7b2c\u56db\u5f39', '\u7b2c\u4e94\u5f39', '\u7b2c\u516d\u5f39', '\u7b2c\u4e03\u5f39', '\u7b2c\u516b\u5f39', '\u7b2c\u4e5d\u5f39', '\u7b2c\u5341\u5f39']):
                        ep_name = link_text.replace('\u70b9\u51fb\u89c2\u770b\uff1a', '').replace('\u70b9\u51fb\u89c2\u770b', '').strip()
                        if not ep_name: ep_name = f"视频{i}"
                        
                        if not link_href.startswith('http'):
                            link_href = f"{self.host}{link_href}" if link_href.startswith('/') else f"{self.host}/{link_href}"
                        
                        plist.append(f"{ep_name}${link_href}")
            
            play_url = '#'.join(plist) if plist else f"未找到视频源${url}"
            
            vod_content = ''
            try:
                tags = []
                seen_names = set()
                seen_ids = set()
                
                tag_links = data('.tags a, .keywords a, .post-tags a')
                
                candidates = []
                for k in tag_links.items():
                    title = k.text().strip()
                    href = k.attr('href')
                    if title and href:
                        candidates.append({'name': title, 'id': href})
                
                candidates.sort(key=lambda x: len(x['name']), reverse=True)
                
                for item in candidates:
                    name = item['name']
                    id_ = item['id']
                    
                    if id_ in seen_ids: continue
                    
                    is_duplicate = False
                    for seen in seen_names:
                        if name in seen:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        target = json.dumps({'id': id_, 'name': name})
                        tags.append(f'[a=cr:{target}/]{name}[/a]')
                        seen_names.add(name)
                        seen_ids.add(id_)
                
                if tags:
                    vod_content = ' '.join(tags)
                else:
                    vod_content = data('.post-title').text()
            except Exception:
                vod_content = '\u83b7\u53d6\u6807\u7b7e\u5931\u8d25'

            if not vod_content:
                vod_content = data('h1').text() or '\u6bcf\u65e5\u5927\u4e71\u6597'

            return {'list': [{'vod_play_from': '\u6bcf\u65e5\u5927\u4e71\u6597', 'vod_play_url': play_url, 'vod_content': vod_content}]}
        except:
            return {'list': [{'vod_play_from': '\u6bcf\u65e5\u5927\u4e71\u6597', 'vod_play_url': '\u83b7\u53d6\u5931\u8d25'}]}

    def searchContent(self, key, quick, pg="1"):
        try:
            pg = int(pg) if pg else 1
            
            if pg == 1:
                url = f"{self.host}/search/{key}/"
            else:
                url = f"{self.host}/search/{key}/{pg}/"
            
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            return {'list': self.getlist(self.getpq(response.text)('article')), 'page': pg, 'pagecount': 9999}
        except:
            return {'list': [], 'page': pg, 'pagecount': 9999}

    def playerContent(self, flag, id, vipFlags):
        parse = 0 if self.isVideoFormat(id) else 1
        url = self.proxy(id) if '.m3u8' in id else id
        return {'parse': parse, 'url': url, 'header': self.headers}

    def localProxy(self, param):
        try:
            type_ = param.get('type')
            url = param.get('url')
            if type_ == 'cache':
                key = param.get('key')
                if content := img_cache.get(key):
                    return [200, 'image/jpeg', content]
                return [404, 'text/plain', b'Expired']
            elif type_ == 'img':
                real_url = self.d64(url) if not url.startswith('http') else url
                # \u5171\u4eab\u52a0\u901f\u901a\u9053\uff1aSession \u8fde\u63a5\u590d\u7528 + \u89e3\u5bc6 LRU \u7f13\u5b58\uff082026-09-08 \u5217\u8868\u63d0\u901f\uff09
                if _shared_fetch_img is not None:
                    mime, data = _shared_fetch_img(real_url, headers=self.headers,
                                                   decrypt=self.aesimg, timeout=15,
                                                   proxies=self.proxies or None)
                    if data:
                        return [200, mime, data]
                    return [404, 'text/plain', b'']
                res = requests.get(real_url, headers=self.headers, proxies=self.proxies, timeout=10)
                content = self.aesimg(res.content)
                return [200, 'image/jpeg', content]
            elif type_ == 'm3u8':
                return self.m3Proxy(url)
            else:
                return self.tsProxy(url)
        except:
            return [404, 'text/plain', b'']

    def proxy(self, data, type='m3u8'):
        if data and self.proxies: return f"{self.getProxyUrl()}&url={self.e64(data)}&type={type}"
        return data

    def m3Proxy(self, url):
        url = self.d64(url)
        res = requests.get(url, headers=self.headers, proxies=self.proxies)
        data = res.text
        base = res.url.rsplit('/', 1)[0]
        lines = []
        for line in data.split('\n'):
            if '#EXT' not in line and line.strip():
                if not line.startswith('http'):
                    line = f"{base}/{line}"
                lines.append(self.proxy(line, 'ts'))
            else:
                lines.append(line)
        return [200, "application/vnd.apple.mpegurl", '\n'.join(lines)]

    def tsProxy(self, url):
        return [200, 'video/mp2t', requests.get(self.d64(url), headers=self.headers, proxies=self.proxies).content]

    def e64(self, text):
        return b64encode(str(text).encode()).decode()

    def d64(self, text):
        return b64decode(str(text).encode()).decode()

    def aesimg(self, data):
        if len(data) < 16: return data
        keys = [(b'f5d965df75336270', b'97b60394abc2fbe1'), (b'75336270f5d965df', b'abc2fbe197b60394')]
        for k, v in keys:
            try:
                dec = unpad(AES.new(k, AES.MODE_CBC, v).decrypt(data), 16)
                if dec.startswith(b'\xff\xd8') or dec.startswith(b'\x89PNG'): return dec
            except: pass
            try:
                dec = unpad(AES.new(k, AES.MODE_ECB).decrypt(data), 16)
                if dec.startswith(b'\xff\xd8'): return dec
            except: pass
        return data

    def getlist(self, data, tid=''):
        videos = []
        is_folder = '/mrdg' in (tid or '')
        for k in data.items():
            card_html = k.outer_html() if hasattr(k, 'outer_html') else str(k)
            a = k if k.is_('a') else k('a').eq(0)
            href = a.attr('href')
            title = k('h2').text() or k('.entry-title').text() or k('.post-title').text()
            if not title and k.is_('a'): title = k.text()
            
            if href and title:
                img = self.getimg(k('script').text(), k, card_html)
                videos.append({
                    'vod_id': f"{href}{'@folder' if is_folder else ''}",
                    'vod_name': title.strip(),
                    'vod_pic': img,
                    'vod_remarks': k('time').text() or '',
                    'vod_tag': 'folder' if is_folder else '',
                    'style': {"type": "rect", "ratio": 1.33}
                })
        return videos

    def getfod(self, id):
        url = f"{self.host}{id}"
        data = self.getpq(requests.get(url, headers=self.headers, proxies=self.proxies).text)
        videos = []
        for i, h2 in enumerate(data('.post-content h2').items()):
            p_txt = data('.post-content p').eq(i * 2)
            p_img = data('.post-content p').eq(i * 2 + 1)
            p_html = p_img.outer_html() if hasattr(p_img, 'outer_html') else str(p_img)
            videos.append({
                'vod_id': p_txt('a').attr('href'),
                'vod_name': p_txt.text().strip(),
                'vod_pic': self.getimg('', p_img, p_html),
                'vod_remarks': h2.text().strip()
            })
        return videos

    def getimg(self, text, elem=None, html_content=None):
        if m := re.search(r"loadBannerDirect\('([^']+)'", text or ''):
            return self._proc_url(m.group(1))
        
        if html_content is None and elem is not None:
             html_content = elem.outer_html() if hasattr(elem, 'outer_html') else str(elem)
        if not html_content: return ''

        html_content = html_content.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')

        if 'data:image' in html_content:
            m = re.search(r'(data:image/[a-zA-Z0-9+/=;,]+)', html_content)
            if m: return self._proc_url(m.group(1))

        m = re.search(r'(https?://[^"\'\s)]+\.(?:jpg|png|jpeg|webp))', html_content, re.I)
        if m: return self._proc_url(m.group(1))
            
        if 'url(' in html_content:
            m = re.search(r'url\s*\(\s*[\'"]?([^"\'\)]+)[\'"]?\s*\)', html_content, re.I)
            if m: return self._proc_url(m.group(1))
            
        return ''

    def _proc_url(self, url):
        if not url: return ''
        url = url.strip('\'" ')
        if url.startswith('data:'):
            try:
                _, b64_str = url.split(',', 1)
                raw = b64decode(b64_str)
                if not (raw.startswith(b'\xff\xd8') or raw.startswith(b'\x89PNG') or raw.startswith(b'GIF8')):
                    raw = self.aesimg(raw)
                key = hashlib.md5(raw).hexdigest()
                img_cache[key] = raw
                return f"{self.getProxyUrl()}&type=cache&key={key}"
            except: return ""
        if not url.startswith('http'):
            url = f"{self.host}{url}" if url.startswith('/') else f"{self.host}/{url}"
        return f"{self.getProxyUrl()}&url={self.e64(url)}&type=img"

    def getpq(self, data):
        try: return pq(data)
        except: return pq(data.encode('utf-8'))
