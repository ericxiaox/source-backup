#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, re, json, base64, time, gzip, ssl

sys.path.append('..')
try:
    from base.spider import Spider as BaseSpider
except ImportError:
    class BaseSpider:
        pass

try:
    from urllib.request import Request, urlopen, build_opener, HTTPSHandler
    from urllib.parse import quote
except ImportError:
    from urllib import quote
    from urllib2 import Request, urlopen, build_opener, HTTPSHandler


class Spider(BaseSpider):
    host = 'https://baoporn.com'
    searchable = True
    filterable = True

    _CATS = [
        (1, '\u6700\u65b0\u89c6\u9891', 'video'),
        (2, '\u56fd\u4ea7', 'tag/%E5%9B%BD%E4%BA%A7'),
        (3, '\u65e5\u672c', 'tag/%E6%97%A5%E6%9C%AC'),
        (4, '\u81ea\u62cd', 'tag/%E8%87%AA%E6%8B%8D'),
        (5, '\u5267\u60c5', 'tag/%E5%89%A7%E6%83%85'),
        (6, '\u63a2\u82b1', 'tag/%E6%8E%A2%E8%8A%B1'),
        (7, '\u9152\u5e97', 'tag/%E9%85%92%E5%BA%97'),
        (8, '\u7ea6\u70ae', 'tag/%E7%BA%A6%E7%82%AE'),
        (9, '\u53f0\u6e7e', 'tag/%E5%8F%B0%E6%B9%BE'),
        (10, '\u4eba\u59bb', 'tag/%E4%BA%BA%E5%A6%BB'),
        (11, '\u7f8e\u5973', 'tag/%E7%BE%8E%E5%A5%B3'),
        (12, '\u9ebb\u8c46\u4f20\u5a92', 'tag/%E9%BA%BB%E8%B1%86%E4%BC%A0%E5%AA%92'),
        (13, '\u5236\u670d', 'tag/%E5%88%B6%E6%9C%8D'),
        (14, '3P', 'tag/3P'),
        (15, '\u5de8\u4e73', 'tag/%E5%B7%A8%E4%B9%B3'),
        (16, '\u53e3\u7206', 'tag/%E5%8F%A3%E7%88%86'),
        (17, '\u6781\u54c1', 'tag/%E6%9E%81%E5%93%81'),
        (18, '\u4e2d\u51fa', 'tag/%E4%B8%AD%E5%87%BA'),
        (19, '\u63a8\u7279', 'tag/%E6%8E%A8%E7%89%B9'),
        (20, '\u591aP', 'tag/%E5%A4%9AP'),
        (21, '\u52a0\u52d2\u6bd4', 'tag/%E5%8A%A0%E5%8B%92%E6%AF%94'),
        (22, '\u65e0\u6bdb', 'tag/%E6%97%A0%E6%AF%9B'),
        (23, '\u9ad8\u989c\u503c', 'tag/%E9%AB%98%E9%A2%9C%E5%80%BC'),
        (24, 'FansOne', 'tag/FansOne'),
        (25, '\u7d20\u4eba', 'tag/%E7%B4%A0%E4%BA%BA'),
        (26, '\u7c89\u5ae9', 'tag/%E7%B2%89%E5%AB%A9'),
        (27, '\u79c1\u62cd', 'tag/%E7%A7%81%E6%8B%8D'),
        (28, '\u8c03\u6559', 'tag/%E8%B0%83%E6%95%99'),
        (29, '\u4e00\u672c\u9053', 'tag/%E4%B8%80%E6%9C%AC%E9%81%93'),
        (30, '\u767d\u864e', 'tag/%E7%99%BD%E8%99%8E'),
        (31, '\u9732\u51fa', 'tag/%E9%9C%B2%E5%87%BA'),
        (32, '\u88f8\u4f53', 'tag/%E8%A3%B8%E4%BD%93'),
        (33, '\u5c11\u5987', 'tag/%E5%B0%91%E5%A6%87'),
        (34, '\u7f51\u7ea2', 'tag/%E7%BD%91%E7%BA%A2'),
        (35, '\u5973\u540c', 'tag/%E5%A5%B3%E5%90%8C'),
        (36, '\u5fa1\u59d0', 'tag/%E5%BE%A1%E5%A7%90'),
        (37, '\u7ee7\u6bcd', 'tag/%E7%BB%A7%E6%AF%8D'),
        (38, '\u541e\u7cbe', 'tag/%E5%90%9E%E7%B2%BE'),
        (39, '\u53cc\u98de', 'tag/%E5%8F%8C%E9%A3%9E'),
        (40, 'VIP', 'tag/VIP'),
        (41, 'OnlyFans', 'tag/onlyfans'),
        (42, 'Fansly', 'tag/Fansly'),
    ]
    _CAT_MAP = {str(cid): path for cid, name, path in _CATS}

    def getName(self):
        return 'BaoPorn'

    def isVideoFormat(self, url):
        return bool(url and re.search(r'\.(m3u8|mp4|ts|flv|mkv)', url, re.I))

    def init(self, extend=""):
        pass

    def destroy(self):
        pass

    def localProxy(self, param):
        return [404, 'text/plain', '']

    # ---------- HTTP ----------
    def _http_get(self, url, timeout=20, retries=2):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        opener = build_opener(HTTPSHandler(context=ctx))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip',
        }
        for i in range(retries):
            try:
                req = Request(url, headers=headers)
                resp = opener.open(req, timeout=timeout)
                data = resp.read()
                if resp.headers.get('Content-Encoding') == 'gzip':
                    try:
                        data = gzip.decompress(data)
                    except Exception:
                        pass
                return data.decode('utf-8', errors='replace')
            except Exception:
                time.sleep(1)
        return ''

    def _fetch(self, url):
        return self._http_get(url)

    @staticmethod
    def _decrypt_data_url(encoded):
        """\u89e3\u5bc6 data-url: atob(reverse(base64))"""
        try:
            s = encoded[::-1]
            pad = len(s) % 4
            if pad:
                s += '=' * (4 - pad)
            return base64.b64decode(s).decode('utf-8', errors='replace')
        except Exception:
            return ''

    def _parse_cards(self, html):
        items = []
        parts = html.split('class="video-card group"')
        for part in parts[1:]:
            m = re.search(r'href="/video/([A-Za-z0-9]+)"', part)
            if not m:
                continue
            vid = m.group(1)
            m2 = re.search(r'<img src="([^"]+)" alt="([^"]*)"', part)
            pic = m2.group(1) if m2 else ''
            title = m2.group(2) if m2 else ''
            if not title:
                m3 = re.search(r'<p class="text-sm[^"]*">([^<]+)</p>', part)
                title = m3.group(1).strip() if m3 else vid
            m4 = re.search(r'right-1 bg-black[^>]*>([^<]+)</span>', part)
            duration = m4.group(1) if m4 else ''
            m5 = re.search(r'fa-eye[^>]*></i>([\d.]+[KMW]?)', part)
            views = m5.group(1) if m5 else ''
            remark = duration
            if views:
                remark = (remark + ' | ' if remark else '') + views + '\u64ad\u653e'
            items.append({
                'vod_id': vid,
                'vod_name': title,
                'vod_pic': pic,
                'vod_remarks': remark,
            })
        return items

    # ---------- \u9996\u9875 ----------
    def homeContent(self, filter):
        try:
            classes = [{'type_id': str(cid), 'type_name': name} for cid, name, _ in self._CATS]
            return {'class': classes, 'filters': {}}
        except Exception as e:
            return {'class': [], 'filters': {}}

    def homeVideoContent(self):
        try:
            html = self._fetch(self.host + '/video')
            items = self._parse_cards(html)
            return {'list': items}
        except Exception:
            return {'list': []}

    # ---------- \u5206\u7c7b ----------
    def categoryContent(self, tid, pg, filter, extend):
        try:
            path = self._CAT_MAP.get(str(tid), 'video')
            if int(pg) <= 1:
                url = f'{self.host}/{path}'
            else:
                url = f'{self.host}/{path}/page/{pg}'
            html = self._fetch(url)
            items = self._parse_cards(html)

            max_pg = 1
            for p in re.findall(r'/page/(\d+)', html):
                try:
                    max_pg = max(max_pg, int(p))
                except Exception:
                    pass

            return {
                'page': int(pg) if pg else 1,
                'pagecount': max_pg,
                'limit': 16,
                'total': len(items),
                'list': items,
            }
        except Exception:
            return {'page': 1, 'pagecount': 1, 'limit': 16, 'total': 0, 'list': []}

    # ---------- \u8be6\u60c5 ----------
    def detailContent(self, ids):
        try:
            did = str(ids[0] if isinstance(ids, list) else ids)
            html = self._fetch(f'{self.host}/video/{did}')

            title = ''
            m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
            if m:
                title = m.group(1).strip()

            pic = ''
            m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
            if m:
                pic = m.group(1)

            play_url = ''
            m = re.search(r'data-url="([^"]+)"', html)
            if m:
                play_url = self._decrypt_data_url(m.group(1))

            tags = re.findall(r'href="/tag/[^"]+"[^>]*>#([^<]+)</a>', html)
            tag_str = '\u3001'.join(tags[:8]) if tags else ''

            content = title or ''
            if tag_str:
                content += f'\n\n标签: {tag_str}'

            if not play_url:
                return {'list': []}

            return {'list': [{
                'vod_id': did,
                'vod_name': title or did,
                'vod_pic': pic,
                'vod_content': content,
                'vod_play_from': 'BaoPorn',
                'vod_play_url': f'播放${play_url}',
                'vod_remarks': 'MP4',
            }]}
        except Exception:
            return {'list': []}

    # ---------- \u641c\u7d22 ----------
    def searchContent(self, key, quick, pg=1):
        try:
            url = f'{self.host}/search?q={quote(key)}'
            if pg > 1:
                url += f'&page={pg}'
            html = self._fetch(url)
            items = self._parse_cards(html)
            return {'list': items, 'page': int(pg) if pg else 1, 'pagecount': 1}
        except Exception:
            return {'list': [], 'page': 1, 'pagecount': 1}

    # ---------- \u64ad\u653e ----------
    def playerContent(self, flag, id, vipFlags=None):
        return {
            'parse': 0,
            'url': id,
            'jx': 0,
            'header': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
                'Referer': self.host + '/',
            }
        }
