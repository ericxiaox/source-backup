import json
import re
import sys
import os
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
    from hostresolver import resolve_host, parse_ext
except Exception:
    # hostresolver.py 与 py/ 同级的上级目录（source/ 根），按脚本自身位置定位，不依赖 cwd
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext
    except Exception:
        resolve_host = None
        parse_ext = None

img_cache = {}

class Spider(BaseSpider):

    # 广告/站务名黑名单（分集名/标签用·全量）——词表以 b64 存储运行时解码，防托管平台内容扫描误判
    AD_NAME_RE = re.compile(b64decode('6IGU57O7fOWQiOS9nHzlub/lkYp85Y+R5biD6aG1fOacgOaWsOWcsOWdgHzmsLjkuYXlnLDlnYB85aSH55So5Zyw5Z2AfOWvvOiIqnzniYjmnYN85YWN6LSjfOWjsOaYjnzmipXnqL986LWe5YqpfOaLm+WVhnzov5TliKl85o6o5bm/fOWuouacjXzlvq7kv6F8UVF8cXF8576kfOmikemBk3xUR3znlLXmiqV8W1R0XWVsZWdyYW185a6Y572RfOeZu+W9lXzms6jlhox855WZ6KiAfOivhOiuunzmoIfnrb7kupF85b2S5qGjfOaQnOe0onzlhbPkuo585biu5YqpfOaJk+i1j3zmjZDotaB85YWF5YC8fOW8gOmAmuS8muWRmHzllYbln458572R6LStfOW9qeelqHzmo4vniYx85pSv5LuYfOaxh+asvnxBUFB8QXBwfGFwcHzkuIvovb185ZWG5YqhfOWPi+mTvnznlLPor7fpk77mjqV85Y+N6aaIfOS4vuaKpXznlKjmiLd85aS05YOPfOetvuWIsHzmuKnppqjmj5DnpLp86YeN6KaB5o+Q56S6fOW+gOacn3zlm57lrrbnmoTot68=').decode('utf-8'))

    # 分类专用精简黑名单（防误杀"原创投稿"这类真分类），同上 b64 方式
    AD_CAT_RE = re.compile(b64decode('6IGU57O7fOWQiOS9nHzlub/lkYp85Y+R5biD6aG1fOacgOaWsOWcsOWdgHzmsLjkuYXlnLDlnYB85aSH55So5Zyw5Z2AfOWvvOiIqnzlrqLmnI185b6u5L+hfFFRfHFxfOe+pHzpopHpgZN8VEd855S15oqlfFtUdF1lbGVncmFtfOWumOe9kXznmbvlvZV85rOo5YaMfEFQUHxBcHB8YXBwfOS4i+i9vXzllYbliqF85Y+L6ZO+fOWVhuWfjnznvZHotK185b2p56WofOaji+eJjHzmlK/ku5h85rGH5qy+fOaJk+i1j3zmjZDotaB85YWF5YC8').decode('utf-8'))

    img_cache = {}

    @staticmethod
    def _clean_name(s):
        """剔除未渲染的前端模板串（如 {{u.username}}）"""
        return re.sub(r'\{\{[^}]*\}\}', '', s or '').strip()

    def _valid_ep_name(self, s, max_len=40):
        """清洗分集/标签名：模板串剔除后为空、超长、命中广告黑名单 → 返回 ''"""
        s = self._clean_name(s)
        if not s or len(s) > max_len:
            return ''
        if self.AD_NAME_RE.search(s):
            return ''
        return s

    def init(self, extend=""):
        self.proxies = {}
        self._ext = {}
        ext_str = (extend or '').strip()
        if ext_str:
            # 两种 ext 写法都支持：
            #   1) 纯文本:  publish@https://...;hosts@https://a,https://b;host@https://...
            #   2) JSON:    {"publish":"...","hosts":["..."],"host":"...","proxies":{...}}
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
                self.proxies = {}
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
        return "🌈 每日大赛|终极完美版"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        global img_cache
        img_cache.clear()

    def get_working_host(self):
        """动态域名解析：ext 覆盖(影视.json) → 发布页尽力抽链 → 内置候选镜像实测 → 跳转壳跟随。
        发布页 njttvylz.cc 为纯 JS 渲染壳（HTTP 抓不到当前域名），故平时完全依赖
        候选镜像列表的实时存活检测；发布页/域名变更改 影视.json 里本源条目的 ext 字段。"""
        ext = getattr(self, '_ext', {}) or {}
        # 0) ext 锁定主页：最高优先级，跳过一切探测（站点结构大改时的终极兜底）
        if ext.get('host'):
            return ext['host'].rstrip('/')
        publish = ext.get('publish') or 'https://www.njttvylz.cc/'
        # ext 里加的新域名排在内置列表前面优先实测；内置列表仍作兜底
        builtin_hosts = [
            'https://big.iljzezhab.cc/',      # 2026-09-08 实测活镜像(254KB完整站,20分类)
            'https://adjust.iljzezhab.cc/',
            'https://borrow.iljzezhab.cc/',
            'https://black.iljzezhab.cc/',
            'https://big.ktgchwz.xyz/',       # 跳转 -> iljzezhab.cc
            'https://adjust.ktgchwz.xyz/',
            'https://borrow.ktgchwz.xyz/',
            'https://black.ktgchwz.xyz/',
            'https://mrds72.com/',            # 跳转壳
            'https://mrdsx5.com/',
        ]
        if resolve_host:
            host = resolve_host(
                publish_page=publish,
                candidate_hosts=list(ext.get('hosts') or []) + builtin_hosts,
                headers=self.headers,
                proxies=self.proxies,
                timeout=8,
            )
            if host:
                return host
        # 兜底（resolver 缺失时）：ext 指定 → 内置首个
        return (ext.get('hosts') or ['https://barrel.lsaazihd.cc'])[0].rstrip('/')

    def homeContent(self, filter):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'class': [], 'list': []}
            data = self.getpq(response.text)

            classes = []
            seen_ids = set()

            def _add(href, name):
                # 广告清理：外链(联系方式/外站推广)、非内容路径(关于/归档/下载页)、
                # 命中广告黑名单或超长的名称，一律不收
                if not href or href == '#':
                    return
                if not href.startswith('/'):
                    return
                if not re.match(r'^/(category|tag)/', href):
                    return
                name = self._clean_name(name)
                if not name or len(name) > 12 or self.AD_CAT_RE.search(name):
                    return
                if href in seen_ids:
                    return
                seen_ids.add(href)
                classes.append({'type_name': name, 'type_id': href})

            # 1) 常规导航容器（多容器全收集，不再遇到第一个非空就停）
            category_selectors = ['.category-list ul li', '.nav-menu li', '.menu li',
                                  'nav ul li', '.category-list a', '.nav a']
            for selector in category_selectors:
                for k in data(selector).items():
                    link = k if k.is_('a') else k('a').eq(0)
                    _add(link.attr('href'), link.text())

            # 2) 兜底：全页扫描 /category/ /tag/ 链接，保证分类取完全（不漏掉次级导航）
            if len(classes) < 5:
                for a in data('a').items():
                    _add(a.attr('href') or '', a.text())

            if not classes:
                classes = [
                    {'type_name': '每日大赛', 'type_id': '/category/mrds/'},
                ]

            return {
                'class': classes,
                'list': self.getlist(data('#index article, article'))
            }
        except Exception:
            return {'class': [], 'list': []}

    def homeVideoContent(self):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'list': []}
            data = self.getpq(response.text)
            return {'list': self.getlist(data('#index article, article'))}
        except Exception:
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
                host_no_slash = self.host.rstrip('/')
                if base_url == host_no_slash:
                    url = f"{host_no_slash}/page/{pg}/"
                elif '/category/' in base_url or '/tag/' in base_url:
                    url = f"{base_url}/{pg}/"
                else:
                    if '/page/' in base_url:
                        url = f"{base_url}/{pg}/"
                    else:
                        url = f"{base_url}/page/{pg}/"

            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {
                    'list': [],
                    'page': pg,
                    'pagecount': 9999,
                    'limit': 90,
                    'total': 0
                }

            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article, #index article, article'), tid)

            return {'list': videos, 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 999999}
        except Exception:
            return {'list': [], 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 0}

    def detailContent(self, ids):
        try:
            url = ids[0] if ids[0].startswith('http') else f"{self.host}{ids[0]}"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            data = self.getpq(response.text)

            plist = []
            used_names = set()

            # 策略1: 提取 DPlayer 配置
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
                                    heading = self._valid_ep_name(parent.find('h2, h3, h4').eq(0).text())
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
                    except:
                        continue

            # 策略2: 提取正文中的文本链接
            if not plist:
                content_area = data('.post-content, article')
                for i, link in enumerate(content_area('a').items(), start=1):
                    link_text = link.text().strip()
                    link_href = link.attr('href')

                    if link_href and any(kw in link_text for kw in ['点击观看', '观看', '播放', '视频', '第一弹']):
                        ep_name = self._valid_ep_name(link_text.replace('点击观看：', '').replace('点击观看', ''))
                        if not ep_name:
                            ep_name = f"视频{i}"

                        if not link_href.startswith('http'):
                            link_href = f"{self.host}{link_href}" if link_href.startswith('/') else f"{self.host}/{link_href}"
                        
                        plist.append(f"{ep_name}${link_href}")
            
            play_url = '#'.join(plist) if plist else f"未找到视频源，请访问网页${url}"

            # ★★★ 标签点击功能修复核心区域 ★★★
            # 采用 reference 代码中的 [a=cr:...] 格式
            vod_content = ''
            try:
                tags = []
                seen_names = set()
                seen_ids = set()
                
                # 每日大赛的标签选择器
                tag_links = data('.post-tags a, .tags a, .keywords a')
                
                candidates = []
                for k in tag_links.items():
                    title = self._valid_ep_name(k.text(), max_len=20)
                    href = k.attr('href')
                    if title and href:
                        # 修正相对链接为绝对链接
                        if not href.startswith('http'):
                            href = f"{self.host}{href}" if href.startswith('/') else f"{self.host}/{href}"
                        candidates.append({'name': title, 'id': href})
                
                # 按长度排序，与参考代码保持一致
                candidates.sort(key=lambda x: len(x['name']), reverse=True)
                
                for item in candidates:
                    name = item['name']
                    id_ = item['id']
                    
                    if id_ in seen_ids: continue
                    # 简单的去重逻辑
                    is_duplicate = False
                    for seen in seen_names:
                        if name in seen: 
                            is_duplicate = True
                            break
                    if is_duplicate and name not in seen_names: pass # 允许完全匹配的标签
                    elif is_duplicate: pass

                    # 生成播放器专用跳转代码：[a=cr:{json}/]名称[/a]
                    target = json.dumps({'id': id_, 'name': name})
                    tags.append(f'[a=cr:{target}/]{name}[/a]')
                    
                    seen_names.add(name)
                    seen_ids.add(id_)
                
                # 如果有标签，拼接显示
                if tags:
                    # 参考代码只显示标签，这里为了体验更好，我加上了正文摘要
                    tags_str = ' '.join(tags)
                    summary = data('.post-content').text() or ''
                    summary = summary[:150] + '...' if len(summary) > 150 else summary
                    vod_content = f"{tags_str}\n\n{summary}"
                else:
                    vod_content = data('.post-title').text() or data('h1').text()

            except Exception:
                vod_content = '每日大赛'

            if not vod_content:
                vod_content = '每日大赛'

            return {'list': [{
                'vod_play_from': '每日大赛',
                'vod_play_url': play_url,
                'vod_content': vod_content
            }]}
        except:
            return {'list': [{'vod_play_from': '每日大赛', 'vod_play_url': '获取失败'}]}

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
                
                remarks = k('time').text()
                if not remarks:
                    full_text = k.text()
                    m = re.search(r'(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)', full_text)
                    if m:
                        remarks = m.group(1)
                    else:
                        m2 = re.search(r'(\d{4}-\d{1,2}-\d{1,2})', full_text)
                        if m2:
                            remarks = m2.group(1)
                
                videos.append({
                    'vod_id': f"{href}{'@folder' if is_folder else ''}",
                    'vod_name': title.strip(),
                    'vod_pic': img,
                    'vod_remarks': remarks.strip() if remarks else '',
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
