# -*- coding: utf-8 -*-
"""
2048\u6838\u57fa\u5730 py\u6e90 \u91cd\u5199\u7248
\u6309\u7f51\u7ad9\u5bfc\u822a\u7ed3\u6784\u91cd\u5199\u5206\u7c7b\u4f53\u7cfb\uff0c\u56fe\u7247\u533a+\u5c0f\u8bf4\u533a\u52a0\u4e0a
- \u89c6\u9891\u533a 9 \u4e2a\u4e00\u7ea7\u5206\u7c7b\uff08\u5b50\u5206\u7c7b\u5c11\u7684\u7528\u7b5b\u9009\u9762\u677f\uff0c\u591a\u7684\u4e5f\u7528\u7b5b\u9009\u56e0\u4e3a\u4e0d\u8d85\u8fc7 8 \u4e2a\uff09
- \u56fe\u7247\u533a 2 \u4e2a\u4e00\u7ea7\u5206\u7c7b\uff08folder \u6807\u7b7e\u4e8c\u7ea7\u76ee\u5f55\uff09
- \u5c0f\u8bf4\u533a 2 \u4e2a\u4e00\u7ea7\u5206\u7c7b\uff08folder \u6807\u7b7e\u4e8c\u7ea7\u76ee\u5f55\uff09
- m3u8 \u5e7f\u544a\u6e05\u6d17\u4ee3\u7406\u4fdd\u7559
- \u591a\u57df\u540d\u81ea\u52a8\u66f4\u65b0\u4fdd\u7559
"""
import sys
import re
import json
import html as html_mod
import requests
import urllib3
import time
import random
from urllib.parse import quote, urljoin, unquote, urlparse

urllib3.disable_warnings()
sys.path.append('..')
from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    # ========== \u591a\u57df\u540d\u914d\u7f6e ==========
    hosts = ['https://s7t8u9v0.luanlunba15.cc']
    host = hosts[0]

    PUBLISH_PAGES = [
        'https://www.luanlunba.cc',
        'https://s7t8u9v0.luanlunba13.cc',
        'https://s7t8u9v0.luanlunba14.cc',
    ]

    session = requests.Session()

    def _log(self, msg):
        pass  # \u9759\u9ed8

    def getName(self):
        return '2048\u6838\u57fa\u5730'

    def isVideoFormat(self, url):
        return url and ('.m3u8' in url or '.mp4' in url or '.ts' in url)

    def manualVideoCheck(self):
        return False

    def destroy(self):
        try:
            self.session.close()
        except:
            pass

    # ===================== \u7f51\u7edc =====================
    def _headers(self, referer=None):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': referer or self.host + '/',
        }

    def _fetch(self, url, referer=None, retries=2):
        for i in range(retries):
            try:
                if i > 0:
                    time.sleep(random.uniform(0.3, 1))
                r = self.session.get(url, headers=self._headers(referer),
                                     timeout=(10, 20), verify=False)
                if not r.encoding or r.encoding.lower() in ('iso-8859-1', 'latin-1'):
                    r.encoding = r.apparent_encoding
                if r.status_code == 200:
                    return r.text
            except:
                continue
        return ''

    # ===================== \u57df\u540d\u81ea\u52a8\u66f4\u65b0 =====================
    def _update_host(self):
        for pub in self.PUBLISH_PAGES:
            try:
                r1 = self.session.get(pub + '/', headers=self._headers(), timeout=10, verify=False)
                cookie_match = re.search(r'document\.cookie\s*=\s*"([^"]+)"', r1.text)
                if cookie_match:
                    for part in cookie_match.group(1).split(';'):
                        part = part.strip()
                        if '=' in part and 'path' not in part and 'max-age' not in part:
                            k, v = part.split('=', 1)
                            self.session.cookies.set(k.strip(), v.strip())

                ajax_url = pub + '/xuexi/data.php'
                h = self._headers(pub + '/')
                h['X-Requested-With'] = 'XMLHttpRequest'
                r2 = self.session.get(ajax_url, headers=h, timeout=10, verify=False)
                if not r2.encoding or r2.encoding.lower() in ('iso-8859-1', 'latin-1'):
                    r2.encoding = r2.apparent_encoding
                try:
                    urls = r2.json().get('urls', [])
                except:
                    urls = re.findall(r'(https?://[a-z0-9]+\.luanlunba\d*\.\w+)', r2.text)

                for url in urls:
                    url = url.strip('/')
                    if not url.startswith('http'):
                        continue
                    try:
                        test = self.session.get(url + '/', headers=self._headers(), timeout=8, verify=False)
                        if test.status_code == 200 and len(test.text) > 1000:
                            if 'vodtype' in test.text or 'voddetail' in test.text:
                                self.host = url
                                self.hosts = [url] + [h for h in self.hosts if h != url]
                                return True
                    except:
                        continue
            except:
                continue

        for h in self.hosts:
            try:
                test = self.session.get(h + '/', headers=self._headers(), timeout=8, verify=False)
                if test.status_code == 200 and len(test.text) > 1000:
                    self.host = h
                    return True
            except:
                continue
        return False

    # ===================== \u5206\u7c7b\u4f53\u7cfb\uff08\u7cbe\u7b80\uff1a\u89c6\u9891+\u56fe\u7247+\u5c0f\u8bf4 \u51718\u4e2a\u4e00\u7ea7\uff09 =====================
    # \u4e00\u7ea7\u5206\u7c7b\u5c3d\u91cf\u5c11\uff1a\u89c6\u9891\u533a\u6309\u7f51\u7ad9\u5bfc\u822a6\u7ec4 + \u56fe\u7247\u533a1 + \u5c0f\u8bf4\u533a1 = 8\u4e2a
    # \u6bcf\u4e2a\u5206\u7c7b\u7684\u5b50\u5206\u7c7b\u7528\u7b5b\u9009\u9762\u677f\u5b9e\u73b0\uff08\u4e0d\u5360\u7528\u4e00\u7ea7\u5206\u7c7b\u540d\u989d\uff09
    CATEGORIES = [
        # ---- \u89c6\u9891\u533a\uff086\u4e2a\u4e00\u7ea7\uff0c\u6309\u7f51\u7ad9\u5bfc\u822a\u5206\u7ec4\uff0c\u672a\u9009\u6ee4\u9ed8\u8ba4\u663e\u793a\u7236\u5206\u7c7b\uff09----
        {'type_id': 'v_gc', 'type_name': '\u56fd\u4ea7\u4f20\u5a92', 'filters': [
            ('6', '\u9ebb\u8c46\u89c6\u9891'), ('7', '91\u5236\u7247\u5382'), ('8', '\u5929\u7f8e\u4f20\u5a92'), ('9', '\u871c\u6843\u4f20\u5a92'),
            ('10', '\u7687\u5bb6\u534e\u4eba'), ('11', '\u661f\u7a7a\u4f20\u5a92'), ('12', '\u7cbe\u4e1c\u5f71\u4e1a'), ('20', '\u4e50\u64ad\u4f20\u5a92'),
        ]},
        {'type_id': 'v_gq', 'type_name': '\u56fd\u4ea7\u5267\u60c5', 'filters': [
            ('57', '\u5154\u5b50\u5148\u751f'), ('21', '\u674f\u5427\u539f\u521b'), ('22', '\u7cd6\u5fc3Vlog'), ('24', '\u73a9\u5076\u59d0\u59d0'),
            ('25', 'mini\u4f20\u5a92'), ('26', '\u5927\u8c61\u4f20\u5a92'), ('30', '\u6210\u4eba\u5934\u6761'), ('31', '\u4e4c\u9e26\u4f20\u5a92'),
        ]},
        {'type_id': 'v_wb', 'type_name': '\u7f51\u66dd\u9ed1\u6599', 'filters': [
            ('60', '\u56fd\u4ea7\u7cbe\u54c1'), ('61', '\u534e\u8bedAV'), ('62', '\u9ed1\u6599\u5403\u74dc'), ('63', '\u5b66\u751f\u5408\u96c6'),
            ('64', '\u4e71\u4f26\u7cbe\u54c1'), ('65', '\u63a2\u82b1\u7ea6\u70ae'), ('66', '\u65e5\u672c\u65e0\u7801'), ('67', '\u4e3b\u64ad\u7f51\u7ea2'),
        ]},
        {'type_id': 'v_ts', 'type_name': '\u7279\u8272\u4ed3\u5e93', 'filters': [
            ('37', '\u56fd\u4ea7\u81ea\u62cd'), ('32', '\u5f3a\u5978\u4e71\u4f26'), ('33', '\u5973\u4f18\u660e\u661f'), ('34', '\u6b27\u7f8e\u6fc0\u60c5'),
            ('28', '\u91cd\u53e3\u6fc0\u60c5'), ('29', '\u4e09\u7ea7\u4f26\u7406'), ('35', '\u5267\u60c5\u52a8\u6f2b'), ('15', 'SM\u8c03\u6559'),
        ]},
        {'type_id': 'v_zp', 'type_name': '\u7cbe\u54c1\u8d44\u6e90', 'filters': [
            ('70', '\u5973\u540c\u6027\u604b'), ('71', '\u65e5\u97e9\u65e0\u7801'), ('72', '\u7f51\u66dd\u5403\u74dc'), ('73', '\u63a2\u82b1\u7ea6\u70ae'),
            ('74', '\u5077\u62cd\u5077\u7aa5'), ('75', '\u65e5\u97e9\u4e3b\u64ad'), ('76', '\u4e2d\u6587\u5b57\u5e55'), ('77', '\u4e3b\u64ad\u8bf1\u60d1'),
        ]},
        {'type_id': 'v_rb', 'type_name': '\u70ed\u64ad\u7247\u5e93', 'filters': [
            ('79', '\u4f20\u5a92\u5267\u60c5'), ('80', '\u6296\u9634\u77ed\u7247'), ('81', 'AV\u89e3\u8bf4'), ('82', '\u6362\u8138\u660e\u661f'),
            ('83', 'VR\u89c6\u89d2'),
        ]},
        # ---- \u56fe\u7247\u533a\uff081\u4e2a\u4e00\u7ea7\uff0c\u5b50\u5206\u7c7b\u7528\u7b5b\u9009\u9762\u677f\uff09----
        {'type_id': 'image', 'type_name': '\u56fe\u7247\u533a', 'filters': [
            ('39', '\u7f8e\u817f\u4e1d\u889c'), ('40', '\u7f51\u53cb\u81ea\u62cd'), ('41', '\u6e05\u7eaf\u552f\u7f8e'), ('42', '\u53e6\u7c7b\u56fe\u7247'),
            ('43', '\u5361\u901a\u8d34\u56fe'), ('44', '\u719f\u5973\u4e71\u4f26'), ('17', '\u4e9a\u5dde\u56fe\u7247'), ('18', '\u6b27\u7f8e\u56fe\u7247'),
        ]},
        # ---- \u5c0f\u8bf4\u533a\uff081\u4e2a\u4e00\u7ea7\uff0c\u5b50\u5206\u7c7b\u7528\u7b5b\u9009\u9762\u677f\uff09----
        {'type_id': 'novel', 'type_name': '\u5c0f\u8bf4\u533a', 'filters': [
            ('45', '\u73b0\u4ee3\u6fc0\u60c5'), ('46', '\u53e4\u5178\u6b66\u4fa0'), ('47', '\u66b4\u529b\u5f3a\u5978'), ('48', '\u6821\u56ed\u6625\u8272'),
            ('49', '\u5bb6\u5ead\u4e71\u4f26'), ('50', '\u957f\u7bc7\u8fde\u8f7d'), ('51', '\u60c5\u8272\u5e7d\u9ed8'), ('52', '\u6deb\u59bb\u4ea4\u6362'),
        ]},
    ]

    def _clean(self, text):
        if not text:
            return ''
        text = re.sub(r'<[^>]+>', '', text)
        text = html_mod.unescape(text)
        return text.strip()

    def init(self, extend=''):
        if hasattr(self, 'session') and self.session:
            try:
                self.session.close()
            except:
                pass
        self.session = requests.Session()
        if not self._update_host():
            pass  # \u7528\u9ed8\u8ba4\u57df\u540d

    # ===================== homeContent =====================
    def homeContent(self, filter_):
        classes = [{'type_id': c['type_id'], 'type_name': c['type_name']} for c in self.CATEGORIES]
        filters = {}
        for c in self.CATEGORIES:
            if 'filters' in c:
                filters[c['type_id']] = [{
                    'key': 'tid', 'name': '\u5b50\u5206\u7c7b',
                    'value': [{'n': '\u5168\u90e8', 'v': ''}] + [{'n': name, 'v': tid} for tid, name in c['filters']]
                }]
        # \u9996\u9875\u53d6\u63a8\u8350\u89c6\u9891\u5217\u8868
        list_items = self._fetch_video_list()
        return {'class': classes, 'list': list_items[:20], 'filters': filters}

    def homeVideoContent(self):
        return {'list': self._fetch_video_list()[:20]}

    # ===================== categoryContent =====================
    def categoryContent(self, tid, pg, filter_=None, extend=''):
        page = int(pg) if pg else 1

        # \u89e3\u6790\u7b5b\u9009\u503c
        ext = extend
        if isinstance(filter_, dict) and filter_.get('tid'):
            ext = filter_['tid']
        if isinstance(ext, dict):
            ext = ext.get('tid', '')

        # --- \u89c6\u9891\u533a\uff1a\u76f4\u63a5\u5206\u7c7b or \u7b5b\u9009\u5b50\u5206\u7c7b ---
        if tid.startswith('vod:') or tid.startswith('v_'):
            # \u89c6\u9891\u5206\u7ec4\u672a\u9009\u7b5b\u9009\u65f6\u7684\u9ed8\u8ba4\u7236\u5206\u7c7b id
            VOD_DEFAULTS = {
                'v_gc': '1', 'v_gq': '2', 'v_wb': '58', 'v_ts': '3',
                'v_zp': '69', 'v_rb': '78',
            }
            real_tid = tid.replace('vod:', '')
            if not real_tid.isdigit():
                real_tid = VOD_DEFAULTS.get(tid, '1')
            if ext and str(ext).isdigit():
                real_tid = str(ext)
            url = f'{self.host}/vodtype/{real_tid}-{page}.html' if page > 1 else f'{self.host}/vodtype/{real_tid}.html'
            html_content = self._fetch(url)
            items = self._parse_video_list(html_content) if html_content else []
            pagecount = self._extract_pagecount(html_content, real_tid) if html_content else page
            return {'list': items, 'page': page, 'pagecount': max(pagecount, page)}

        # --- \u56fe\u7247\u533a / \u5c0f\u8bf4\u533a\uff1aarttype\uff0c\u5b50\u5206\u7c7b\u7528\u7b5b\u9009 ---
        if tid == 'image':
            art_id = str(ext) if ext and str(ext).isdigit() else '5'  # \u9ed8\u8ba4\u6fc0\u60c5\u56fe\u533a
        elif tid == 'novel':
            art_id = str(ext) if ext and str(ext).isdigit() else '38'  # \u9ed8\u8ba4\u60c5\u8272\u5c0f\u8bf4
        else:
            return {'list': [], 'page': page, 'pagecount': 1}

        url = f'{self.host}/arttype/{art_id}-{page}.html' if page > 1 else f'{self.host}/arttype/{art_id}.html'
        html_content = self._fetch(url)
        # \u6839\u636e tid \u51b3\u5b9a vod_id \u524d\u7f00\uff1aimg_ \u6216 nov_
        prefix = 'img_' if tid == 'image' else 'nov_'
        is_image = (tid == 'image')
        items = self._parse_art_list(html_content, prefix, is_image) if html_content else []
        pagecount = self._extract_art_pagecount(html_content, art_id) if html_content else page
        return {'list': items, 'page': page, 'pagecount': max(pagecount, page), 'limit': 15}

    # ===================== detailContent =====================
    def detailContent(self, ids):
        vid = str(ids[0] if isinstance(ids, list) else ids)
        # \u89c6\u9891
        if vid.startswith('v_'):
            real_id = vid.replace('v_', '')
            html_content = self._fetch(f'{self.host}/voddetail/{real_id}.html')
            if html_content:
                return self._video_detail(real_id, html_content)
        # \u56fe\u7247\uff08img_ \u524d\u7f00\u6765\u81ea\u56fe\u7247\u533a\uff09
        if vid.startswith('img_'):
            real_id = vid.replace('img_', '')
            html_content = self._fetch(f'{self.host}/artdetail-{real_id}.html')
            if html_content:
                return self._img_detail(real_id, html_content)
        # \u5c0f\u8bf4\uff08nov_ \u524d\u7f00\u6765\u81ea\u5c0f\u8bf4\u533a\uff09
        if vid.startswith('nov_'):
            real_id = vid.replace('nov_', '')
            html_content = self._fetch(f'{self.host}/artdetail-{real_id}.html')
            if html_content:
                return self._novel_detail(real_id, html_content)
        return {'list': [{'vod_id': vid, 'vod_name': '\u52a0\u8f7d\u5931\u8d25', 'vod_play_from': '\u9519\u8bef', 'vod_play_url': ''}]}

    # ===================== \u89c6\u9891\u5217\u8868\u89e3\u6790 =====================
    def _fetch_video_list(self):
        html_content = self._fetch(self.host + '/')
        return self._parse_video_list(html_content) if html_content else []

    def _parse_video_list(self, html_content):
        items = []
        if not html_content:
            return items
        pattern = (r'<dl>\s*<dt[^>]*>.*?<a[^>]*href="/voddetail/(\d+)\.html"[^>]*>'
                   r'.*?<img[^>]*data-original="([^"]*)"[^>]*>.*?</a>.*?</dt>\s*<dd>\s*'
                   r'<a[^>]*href="/voddetail/\d+\.html"[^>]*>(.*?)</a>\s*</dd>\s*</dl>')
        for m in re.finditer(pattern, html_content, re.S):
            vid, img, title_block = m.groups()
            if not img.startswith('http'):
                img = urljoin(self.host, img)
            items.append({
                'vod_id': f'v_{vid}',
                'vod_name': self._clean(title_block) or '\u672a\u77e5\u6807\u9898',
                'vod_pic': img,
            })
        return items

    # ===================== \u56fe\u7247\u5217\u8868\u89e3\u6790\uff08arttype \u9875\uff09 =====================
    def _parse_art_list(self, html_content, prefix='art_', is_image=False):
        items = []
        if not html_content:
            return items
        # arttype \u9875\u9762 artdetail-ID.html\uff08\u6a2a\u6760\u683c\u5f0f\uff09
        for m in re.finditer(r'<a[^>]*href="/artdetail-(\d+)\.html"[^>]*>(.*?)</a>', html_content, re.S):
            aid, block = m.groups()
            raw = html_mod.unescape(self._clean(block))
            if is_image:
                # \u56fe\u7247\u533a\uff1a\u76f4\u63a5\u5220\u6389\u65e5\u671f
                date_m = re.match(r'\[\d{4}-\d{2}-\d{2}\]\s*(.*)', raw)
                title = date_m.group(1).strip() if date_m else raw
                short = title
                # \u8fc7\u6ee4\u7a7a\u58f3\u6761\u76ee
                if short and len(short) < 4 and '\u3010' not in short:
                    continue
            else:
                # \u5c0f\u8bf4\u533a\uff1a\u5220\u6389\u65e5\u671f\u548c\u3010\u4f5c\u8005\uff1axxx\u3011\u6807\u8bb0
                title = raw
                title = re.sub(r'\[\d{4}-\d{2}-\d{2}\]\s*', '', title)
                title = re.sub('\u3010\u4f5c\u8005\uff1a[^\u3011]*\u3011', '', title)
                title = re.sub('\u3010\u5b8c\u3011', '', title).strip()
                if title and len(title) < 20 and '\u3010' not in title:
                    continue
            items.append({
                'vod_id': f'{prefix}{aid}',
                'vod_name': title or f'图集{aid}',
                'vod_pic': '',
            })
        return items

    # ===================== \u89c6\u9891\u8be6\u60c5 =====================
    def _video_detail(self, vid, html_content):
        title, cover = '', ''
        m = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.S)
        if m:
            title = self._clean(m.group(1))
        if not title:
            m = re.search(r'<title>(.*?)</title>', html_content)
            if m:
                title = self._clean(m.group(1))
        m = re.search(r'<img[^>]*data-original="([^"]*)"[^>]*>', html_content)
        if m:
            cover = m.group(1)
        if not cover:
            m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html_content)
            if m:
                cover = m.group(1)
        if cover and not cover.startswith('http'):
            cover = urljoin(self.host, cover)

        buttons = re.findall(
            r'<div[^>]+class="item"[^>]*>\s*<a[^>]+href="(/vodplay/' + vid + r'[-_]\d+[-_]\d+\.html)"[^>]*>(.*?)</a>',
            html_content, re.S)
        if not buttons:
            buttons = re.findall(
                r'href="(/vodplay/' + vid + r'[^"]*)"[^>]*>(.*?)</a>', html_content, re.S)
        if not buttons:
            buttons = [(f'/vodplay/{vid}-1-1.html', '\u9ad8\u6e05')]

        line_map = {}
        cache = {}
        for href, btn_name in buttons:
            # \u64ad\u653e\u6e90\u540d\u7edf\u4e00\u4e3a"\u9ad8\u6e05"\uff0c\u4e0d\u4eceHTML\u6293
            btn_name = '\u9ad8\u6e05'

            play_url = urljoin(self.host, href)
            if href not in cache:
                play_html = self._fetch(play_url)
                m3u8_list = self._extract_m3u8(play_html) if play_html else []
                cache[href] = m3u8_list
            else:
                m3u8_list = cache[href]

            if m3u8_list:
                for i, m3u8 in enumerate(m3u8_list):
                    name = btn_name if i == 0 else f'{btn_name}_{i+1}'
                    if btn_name not in line_map:
                        line_map[btn_name] = []
                    line_map[btn_name].append((name, m3u8))
            else:
                if btn_name not in line_map:
                    line_map[btn_name] = []
                line_map[btn_name].append((btn_name, play_url))

        if not line_map:
            return {'list': [{'vod_id': f'v_{vid}', 'vod_name': title, 'vod_pic': cover,
                              'vod_play_from': '\u9519\u8bef', 'vod_play_url': '\u672a\u627e\u5230\u64ad\u653e\u5730\u5740'}]}

        from_lines, url_lines = [], []
        for line_name, episodes in line_map.items():
            from_lines.append(line_name)
            url_lines.append('#'.join([f'{ep_name}${ep_url}' for ep_name, ep_url in episodes]))

        return {'list': [{'vod_id': f'v_{vid}', 'vod_name': title, 'vod_pic': cover,
                          'vod_play_from': '#'.join(from_lines),
                          'vod_play_url': '$$$'.join(url_lines)}]}

    # ===================== \u56fe\u7247/\u5c0f\u8bf4\u8be6\u60c5 =====================
    def _img_detail(self, vid, html_content):
        """\u56fe\u7247\u96c6\u8be6\u60c5\uff1a\u63d0\u53d6\u6b63\u6587\u56fe\u7247"""
        title = ''
        m = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.S)
        if m:
            title = html_mod.unescape(self._clean(m.group(1)))
        if not title:
            m = re.search(r'<title>(.*?)</title>', html_content)
            if m:
                title = self._clean(m.group(1))

        # \u4f18\u5148\u4ece\u6b63\u6587\u5bb9\u5668 m1938ing \u63d0\u53d6\uff08\u9694\u79bb\u5e7f\u544a\uff09
        content_area = re.search(r'<div[^>]+class="m1938ing"[^>]*>(.*?)</div>', html_content, re.S)
        if content_area:
            imgs = []
            for attr in ['src', 'data-original', 'data-src', 'original', 'data-url']:
                imgs.extend(re.findall(rf"""<img[^>]*{attr}=['"]([^'"]+)['"]""", content_area.group(1), re.I))
            real_imgs = []
            seen = set()
            for img in imgs:
                if img.startswith('//'): img = 'https:' + img
                if not img.startswith('http'): img = urljoin(self.host, img)
                if img not in seen:
                    seen.add(img)
                    real_imgs.append(img)
        else:
            real_imgs = []

        if real_imgs:
            pics = '&&'.join(real_imgs)
            play_url = f'查看$pics://{pics}'
            return {'list': [{'vod_id': f'img_{vid}', 'vod_name': title,
                              'vod_pic': real_imgs[0], 'vod_play_from': '\u56fe\u7247', 'vod_play_url': play_url}]}
        return {'list': [{'vod_id': f'img_{vid}', 'vod_name': title, 'vod_play_from': '\u9519\u8bef', 'vod_play_url': '\u65e0\u56fe\u7247'}]}

    def _novel_detail(self, vid, html_content):
        """\u5c0f\u8bf4\u8be6\u60c5 - \u5b8c\u5168\u7167\u642c\u4e09\u4e09\u8a00\u60c5\u683c\u5f0f"""
        title = ''
        m = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.S)
        if m:
            title = html_mod.unescape(self._clean(m.group(1)))
        if not title:
            m = re.search(r'<title>(.*?)</title>', html_content)
            if m:
                title = self._clean(m.group(1))

        # \u4ece m1938ing \u63d0\u53d6\u6b63\u6587
        content = ''
        m1938 = re.search(r'class="m1938ing"[^>]*>(.*?)</div>', html_content, re.S)
        if m1938:
            content = re.sub(r'<br\s*/?>', '\n', m1938.group(1))
            content = re.sub(r'<[^>]+>', '', content)
            content = html_mod.unescape(content).strip()
        if not content or len(content) < 20:
            for pat in [r'<div[^>]+id="content"[^>]*>(.*?)</div>',
                        r'<div[^>]+class="[^"]*content[^"]*"[^>]*>(.*?)</div>']:
                m = re.search(pat, html_content, re.S)
                if m:
                    content = re.sub(r'<[^>]+>', '', m.group(1)).strip()
                    if len(content) > 50:
                        break

        if not content or len(content) < 20:
            return {'list': []}

        # \u6784\u9020\u7ae0\u8282 URL \u5217\u8868\uff08\u548c\u4e09\u4e09\u8a00\u60c5\u5b8c\u5168\u4e00\u6837\u7684\u683c\u5f0f\uff1a\u7ae0\u8282\u540d$\u5b8c\u6574URL\uff09
        play_list = []
        chapters = re.split('\\n\\s*(\u7b2c[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e\u5343\\d]+[\u7ae0\u96c6\u56de\u8282\u5377]\uff1a?[^\\n]*)\\n', content)
        if len(chapters) > 3:
            intro = chapters[0].strip()
            if intro and len(intro) > 20:
                play_list.append(f"内容简介${self.host}/artdetail-{vid}.html?ch=0")
            for i in range(1, len(chapters), 2):
                ch_name = chapters[i].strip()
                ch_idx = (i + 1) // 2
                if ch_name:
                    play_list.append(f"{ch_name}${self.host}/artdetail-{vid}.html?ch={ch_idx}")
        else:
            play_list.append(f"第1章${self.host}/artdetail-{vid}.html?ch=0")

        # vod_play_from \u548c vod_play_url \u5b8c\u5168\u5bf9\u9f50\u4e09\u4e09\u8a00\u60c5\u683c\u5f0f
        play_url = '#'.join(play_list)
        return {
            "list": [{
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": "",
                "vod_play_from": "\u5c0f\u8bf4",
                "vod_play_url": play_url
            }]
        }

    # ===================== \u641c\u7d22 =====================
    def searchContent(self, key, quick, pg='1'):
        try:
            page = int(pg) if pg else 1
            url = f'{self.host}/vodsearch/-------------.html?wd={quote(key)}&page={page}'
            html_content = self._fetch(url)
            items = self._parse_video_list(html_content) if html_content else []
            return {'list': items, 'page': page, 'pagecount': page + 1}
        except:
            return {'list': [], 'page': int(pg) if pg else 1, 'pagecount': 1}

    # ===================== \u64ad\u653e\u5730\u5740\u63d0\u53d6 =====================
    def _extract_m3u8(self, html_content):
        urls = []
        if not html_content:
            return urls
        player_match = re.search(r'var\s+player_aaaa\s*=\s*({.*?});', html_content, re.S)
        if player_match:
            try:
                data = json.loads(player_match.group(1))
                raw = data.get('url', '')
                if raw:
                    decoded = unquote(raw)
                    if decoded.startswith('http'):
                        urls.append(decoded)
            except:
                pass
        urls.extend(re.findall(r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)', html_content))
        if not urls:
            for scr in re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.S):
                urls.extend(re.findall(r'''['"]url['"]\s*:\s*['"]([^'"]+\.m3u8[^'"]*)['"]''', scr))
        seen = set()
        return [u for u in urls if u.startswith('http') and u not in seen and not seen.add(u)]

    def playerContent(self, flag, id, vipFlags=None):
        # \u5c0f\u8bf4\uff1aURL?ch=\u7ae0\u8282\u7d22\u5f15 \u2192 \u8bf7\u6c42 artdetail \u63d0\u53d6\u6307\u5b9a\u7ae0\u8282
        # \u517c\u5bb9 shell \u7aef URL \u7f16\u7801\uff08?\u2192%3F, =\u2192%3D\uff09
        ch_match = re.search(r'artdetail-(\d+)\.html(?:\?|%3F)ch(?:=|%3D)(\d+)', id)
        if ch_match:
            try:
                art_id = ch_match.group(1)
                ch_idx = int(ch_match.group(2))
                html_content = self._fetch(f'{self.host}/artdetail-{art_id}.html')
                if not html_content:
                    return {"parse": 0, "playUrl": "", "url": "novel://" + json.dumps({"title": "\u52a0\u8f7d\u5931\u8d25", "content": "\u65e0\u6cd5\u83b7\u53d6\u5185\u5bb9"}, ensure_ascii=False), "header": ""}
                # \u63d0\u53d6\u5168\u6587
                content = ''
                m1938 = re.search(r'class="m1938ing"[^>]*>(.*?)</div>', html_content, re.S)
                if m1938:
                    content = re.sub(r'<br\s*/?>', '\n', m1938.group(1))
                    content = re.sub(r'<[^>]+>', '', content)
                    content = html_mod.unescape(content).strip()
                if not content:
                    for pat in [r'<div[^>]+id="content"[^>]*>(.*?)</div>',
                                r'<div[^>]+class="[^"]*content[^"]*"[^>]*>(.*?)</div>']:
                        m = re.search(pat, html_content, re.S)
                        if m:
                            content = re.sub(r'<[^>]+>', '', m.group(1)).strip()
                            if len(content) > 50:
                                break
                # \u6807\u9898
                title_m = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.S)
                title = html_mod.unescape(self._clean(title_m.group(1))) if title_m else '\u5c0f\u8bf4'
                # \u7ae0\u8282\u5206\u5272
                chapters = re.split('\\n\\s*(\u7b2c[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e\u5343\\d]+[\u7ae0\u96c6\u56de\u8282\u5377]\uff1a?[^\\n]*)\\n', content)
                if len(chapters) > 3 and ch_idx > 0:
                    ch_real_idx = ch_idx * 2 - 1
                    if ch_real_idx + 1 < len(chapters):
                        ch_name = chapters[ch_real_idx].strip()
                        ch_content = chapters[ch_real_idx + 1].strip()
                        data = {"title": ch_name, "content": ch_content[:15000]}
                    elif ch_real_idx < len(chapters):
                        data = {"title": chapters[ch_real_idx].strip(), "content": chapters[ch_real_idx].strip()[:15000]}
                    else:
                        data = {"title": "\u7b80\u4ecb", "content": chapters[0].strip()[:15000]}
                else:
                    data = {"title": title, "content": content[:15000]}
                return {"parse": 0, "playUrl": "", "url": "novel://" + json.dumps(data, ensure_ascii=False), "header": ""}
            except Exception as e:
                return {"parse": 0, "playUrl": "", "url": "novel://" + json.dumps({"title": "\u9519\u8bef", "content": str(e)[:500]}, ensure_ascii=False), "header": ""}
        # \u5c0f\u8bf4\u76f4\u901a
        if id.startswith('novel://'):
            return {'parse': 0, 'playUrl': '', 'url': id, 'header': ''}
        # \u89c6\u9891\uff1am3u8/mp4
        if id.startswith('http') and ('.m3u8' in id or '.mp4' in id or '.ts' in id):
            if '.m3u8' in id:
                return {'parse': 0, 'url': self._proxy_m3u8_url(id, self.host),
                        'header': {'Referer': self.host, 'User-Agent': 'Mozilla/5.0'}}
            return {'parse': 0, 'url': id, 'header': {'Referer': self.host, 'User-Agent': 'Mozilla/5.0'}}
        return {'parse': 1, 'url': id, 'header': {'Referer': self.host, 'User-Agent': 'Mozilla/5.0'}}

    # ===================== localProxy =====================
    def localProxy(self, param):
        EMPTY_GIF = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        if 'do=m3u8' in param:
            try:
                params = dict(p.split('=', 1) for p in param.split('&') if '=' in p)
                url = unquote(params.get('url', ''))
                referer = unquote(params.get('referer', self.host))
                if not url:
                    return [404, "text/plain", "missing url"]
                raw = self._get_m3u8_content(url, referer)
                if not raw:
                    return [404, "text/plain", "m3u8 download failed"]
                cleaned = self._clean_m3u8(raw, url, referer)
                return [200, "application/vnd.apple.mpegurl", cleaned]
            except:
                return [404, "text/plain", "proxy error"]
        if not param or not param.startswith('http'):
            return [200, 'image/gif', EMPTY_GIF]
        try:
            r = self.session.get(param, headers={'User-Agent': 'Mozilla/5.0', 'Referer': self.host + '/'},
                                 timeout=(10, 15))
            r.raise_for_status()
            return [200, r.headers.get('Content-Type', 'application/octet-stream'), r.content]
        except:
            return [200, 'image/gif', EMPTY_GIF]

    # ===================== \u5206\u9875 =====================
    def _extract_pagecount(self, html_content, tid):
        if not html_content:
            return 1
        page_links = re.findall(rf'/vodtype/{tid}[-_](\d+)\.html', html_content)
        if page_links:
            return max(int(p) for p in page_links)
        return 1

    def _extract_art_pagecount(self, html_content, art_id):
        if not html_content:
            return 1
        page_links = re.findall(rf'/arttype/{art_id}-(\d+)\.html', html_content)
        if page_links:
            return max(int(p) for p in page_links)
        return 1

    # ===================== m3u8 \u5e7f\u544a\u6e05\u6d17 =====================
    def _proxy_m3u8_url(self, url, referer=''):
        try:
            base = self.getProxyUrl()
            if '?' not in base:
                base += '?do=py'
            return base + '&do=m3u8&url=' + quote(url, safe='') + '&referer=' + quote(referer or self.host, safe='')
        except:
            return url

    def _get_m3u8_content(self, url, referer):
        try:
            resp = requests.get(url, headers={'Referer': referer, 'User-Agent': 'Mozilla/5.0'}, timeout=15)
            if resp.status_code == 200:
                if not resp.encoding or resp.encoding.lower() in ('iso-8859-1', 'latin-1'):
                    resp.encoding = resp.apparent_encoding
                return resp.text
        except:
            pass
        return None

    def _clean_m3u8(self, m3u8_text, m3u8_url='', referer='', skip_seconds=25):
        text = (m3u8_text or '').replace('\r', '')
        if '#EXT-X-STREAM-INF' in text:
            out = []
            for raw in text.splitlines():
                line = raw.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    out.append(line)
                else:
                    abs_url = urljoin(m3u8_url, line)
                    if '.m3u8' in line.lower():
                        out.append(self._proxy_m3u8_url(abs_url, referer))
                    else:
                        out.append(abs_url)
            return '\n'.join(out) + '\n'

        header, segments, tail, media_sequence, target_duration = self._parse_m3u8_segments(text)
        if not segments:
            return text

        marker = self._main_path_marker(m3u8_url)
        stat = {}
        for seg in segments:
            key = self._segment_host_key(seg['uri'], m3u8_url)
            stat[key] = stat.get(key, 0.0) + float(seg.get('dur') or 0)
        main_key = max(stat.items(), key=lambda x: x[1])[0] if stat else ('', '')
        total_dur = sum(stat.values()) or 0
        main_dur = stat.get(main_key, 0)

        cleaned, removed = [], 0
        for idx, seg in enumerate(segments):
            key = self._segment_host_key(seg['uri'], m3u8_url)
            is_front = idx < 12
            abs_uri = urljoin(m3u8_url, seg.get('uri', ''))
            is_ad = self._is_ad_segment(seg['uri'], seg.get('dur'), seg.get('tags'))
            if marker and marker not in urlparse(abs_uri).path.lower():
                is_ad = True
            tags_text = '\n'.join(seg.get('tags') or []).upper()
            if is_front and 'METHOD=NONE' in tags_text and marker and marker not in urlparse(abs_uri).path.lower():
                is_ad = True
            if (not is_ad) and is_front and total_dur > 0 and main_dur >= total_dur * 0.6:
                if key != main_key and stat.get(key, 0) <= 90:
                    is_ad = True
            if is_ad:
                removed += 1
                continue
            seg['_idx'] = idx
            cleaned.append(seg)

        if removed == 0 and len(segments) > 4:
            acc, cut = 0.0, 0
            for idx, seg in enumerate(segments[:12]):
                key = self._segment_host_key(seg['uri'], m3u8_url)
                if key == main_key and acc >= 3:
                    break
                acc += float(seg.get('dur') or target_duration or 3)
                cut = idx + 1
                if acc >= skip_seconds:
                    break
            if cut > 0 and cut < len(segments):
                first_key = self._segment_host_key(segments[0]['uri'], m3u8_url)
                if first_key != main_key:
                    cleaned = segments[cut:]
                    removed = cut

        if not cleaned:
            cleaned = segments
            removed = 0

        new_lines = []
        has_m3u = False
        for line in header:
            if line.startswith('#EXTM3U'): has_m3u = True
            if line.startswith('#EXT-X-MEDIA-SEQUENCE') or line.startswith('#EXT-X-START'):
                continue
            if line.startswith('#EXT-X-KEY') and 'METHOD=NONE' in line.upper() and removed > 0:
                continue
            new_lines.append(line)
        if not has_m3u:
            new_lines.insert(0, '#EXTM3U')
        first_idx = cleaned[0].get('_idx', removed) if cleaned else removed
        new_lines.append(f'#EXT-X-MEDIA-SEQUENCE:{media_sequence + first_idx}')
        for seg in cleaned:
            for tag in seg.get('tags') or []:
                if tag.startswith('#EXT-X-KEY') or tag.startswith('#EXT-X-MAP'):
                    def _fix_uri(m):
                        return 'URI="' + urljoin(m3u8_url, m.group(1)) + '"'
                    tag = re.sub(r'URI="([^"]+)"', _fix_uri, tag)
                new_lines.append(tag)
            new_lines.append(urljoin(m3u8_url, seg.get('uri', '')))
        if tail:
            for line in tail:
                if line.startswith('#EXT-X-ENDLIST'):
                    new_lines.append(line)
        elif '#EXT-X-ENDLIST' in text:
            new_lines.append('#EXT-X-ENDLIST')
        return '\n'.join(new_lines) + '\n'

    def _parse_m3u8_segments(self, text):
        lines = [x.strip() for x in (text or '').replace('\r', '').split('\n') if x.strip()]
        header, segments, tail = [], [], []
        pending_tags = []
        media_sequence = 0
        target_duration = 0
        started = False
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('#EXT-X-MEDIA-SEQUENCE'):
                try: media_sequence = int(line.split(':', 1)[1])
                except: pass
                if not started: header.append(line)
                else: pending_tags.append(line)
            elif line.startswith('#EXT-X-TARGETDURATION'):
                try: target_duration = float(line.split(':', 1)[1])
                except: pass
                if not started: header.append(line)
                else: pending_tags.append(line)
            elif line.startswith('#EXTINF'):
                started = True
                dur = target_duration or 3.0
                m = re.search(r'#EXTINF:\s*([\d.]+)', line)
                if m:
                    try: dur = float(m.group(1))
                    except: pass
                tags = pending_tags + [line]
                pending_tags = []
                uri = ''
                j = i + 1
                while j < len(lines):
                    if lines[j].startswith('#'):
                        tags.append(lines[j]); j += 1; continue
                    uri = lines[j]; break
                if uri:
                    segments.append({'tags': tags, 'uri': uri, 'dur': dur}); i = j
                else:
                    tail.extend(tags)
            elif line.startswith('#EXT-X-ENDLIST'):
                tail.append(line)
            elif line.startswith('#'):
                if started: pending_tags.append(line)
                else: header.append(line)
            else:
                started = True
                segments.append({'tags': pending_tags, 'uri': line, 'dur': target_duration or 3.0})
                pending_tags = []
            i += 1
        return header, segments, tail, media_sequence, target_duration

    def _is_ad_segment(self, uri, dur=0, prev_tags=None):
        u = (uri or '').strip().lower()
        if not u: return False
        if any(w in u for w in ['ad', 'ads', 'advert', 'sponsor', 'pre', 'preroll', '/gg/', '_gg', 'gg_', '/adv/', '/ad/', 'banner', 'promo']):
            return True
        try:
            if 0 < float(dur) <= 1.2: return True
        except: pass
        return False

    def _segment_host_key(self, uri, base_url):
        try:
            full = urljoin(base_url, uri)
            p = urlparse(full)
            return (p.netloc.lower(), re.sub(r'/[^/]*$', '/', (p.path or '/').lower()))
        except:
            return ('', '')

    def _main_path_marker(self, m3u8_url):
        try:
            p = urlparse(m3u8_url).path
            m = re.search(r'(/\d{8}/[^/]+/\d+kb/hls/)', p)
            if m: return m.group(1).lower()
            m = re.search(r'(/\d{8}/[^/]+/)', p)
            if m: return m.group(1).lower()
        except: pass
        return ''
