# -*- coding: utf-8 -*-
# TVBox / \u5f71\u89c6\u4ed3 / OK\u5f71\u89c6 Python \u6807\u51c6\u722c\u866b
import sys
import re
import json
import base64
import html
from urllib.parse import quote, unquote, urljoin, urlparse, urlunparse

sys.path.append('..')
try:
    from base.spider import Spider
except Exception:
    class Spider(object):
        pass


class Spider(Spider):
    def getName(self):
        return 'N2\u5f71\u89c6'

    def init(self, extend=''):
        self.last_error = ''
        self.load_extend(extend)

    # host \u53ea\u662f\u542f\u52a8\u9ed8\u8ba4\u503c\uff1b\u771f\u6b63\u4f7f\u7528\u524d\u4f1a\u901a\u8fc7 ensure_host \u5b9e\u65f6\u63a2\u6d4b\u5f53\u524d\u5185\u5bb9\u57df\u540d\u3002
    # \u65e7\u57df\u540d o4z6i / n2d4z \u5df2\u53d8\u6210\u5165\u53e3\u8df3\u8f6c\uff0c\u4fdd\u7559\u5728 entry_hosts \u7528\u6765\u53d1\u73b0\u65b0\u57df\u540d\u3002
    host = 'https://www.c9z7j.top'
    content_hosts = [
        'https://www.c9z7j.top',
        'https://www.j2r7q.top',
    ]
    entry_hosts = [
        'https://www.o4z6i.top',
        'https://www.n2d4z.top',
        'https://www.c9z7j.top',
        'https://www.j2r7q.top',
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Mobile) AppleWebKit/537.36 Chrome/120.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'close',
    }

    classes = [
        {'type_name': '\u6700\u65b0\u5267\u60c5', 'type_id': 'juqing'},
        {'type_name': '\u6700\u65b0\u7535\u5f71', 'type_id': 'shipin'},
        {'type_name': '\u6700\u65b0\u7cbe\u9009', 'type_id': 'jingpin'},
        {'type_name': '\u5267\u60c5-\u9ebb\u8c46\u4f20\u5a92', 'type_id': 'juqing|\u9ebb\u8c46\u4f20\u5a92'},
        {'type_name': '\u5267\u60c5-\u5929\u7f8e\u4f20\u5a92', 'type_id': 'juqing|\u5929\u7f8e\u4f20\u5a92'},
        {'type_name': '\u5267\u60c5-\u661f\u7a7a\u679c\u51bb', 'type_id': 'juqing|\u661f\u7a7a\u679c\u51bb'},
        {'type_name': '\u5267\u60c5-\u871c\u6843\u7cbe\u4e1c', 'type_id': 'juqing|\u871c\u6843\u7cbe\u4e1c'},
        {'type_name': '\u5267\u60c5-\u97e9\u56fd\u4f26\u7406', 'type_id': 'juqing|\u97e9\u56fd\u4f26\u7406'},
        {'type_name': '\u5267\u60c5-COSPLAY', 'type_id': 'juqing|COSPLAY'},
        {'type_name': '\u5267\u60c5-\u7ecf\u5178\u4e09\u7ea7', 'type_id': 'juqing|\u7ecf\u5178\u4e09\u7ea7'},
        {'type_name': '\u5267\u60c5-\u4e2d\u6587\u5b57\u5e55', 'type_id': 'juqing|\u4e2d\u6587\u5b57\u5e55'},
        {'type_name': '\u7535\u5f71-\u65e5\u672cav', 'type_id': 'shipin|\u65e5\u672cav'},
        {'type_name': '\u7535\u5f71-\u97e9\u56fd\u70ed\u821e', 'type_id': 'shipin|\u97e9\u56fd\u70ed\u821e'},
        {'type_name': '\u7535\u5f71-\u6b27\u7f8e\u7cbe\u54c1', 'type_id': 'shipin|\u6b27\u7f8e\u7cbe\u54c1'},
        {'type_name': '\u7535\u5f71-\u52a8\u6f2b\u7535\u5f71', 'type_id': 'shipin|\u52a8\u6f2b\u7535\u5f71'},
        {'type_name': '\u7535\u5f71-\u56fd\u4ea7\u81ea\u62cd', 'type_id': 'shipin|\u56fd\u4ea7\u81ea\u62cd'},
        {'type_name': '\u7535\u5f71-\u5c9b\u56fd\u65e0\u7801', 'type_id': 'shipin|\u5c9b\u56fd\u65e0\u7801'},
        {'type_name': '\u7535\u5f71-JVID', 'type_id': 'shipin|JVID'},
        {'type_name': '\u7535\u5f71-SM\u8c03\u6559', 'type_id': 'shipin|SM\u8c03\u6559'},
        {'type_name': '\u7cbe\u54c1-\u8f6f\u840c\u798f\u5229\u59ec', 'type_id': 'jingpin|\u8f6f\u840c\u798f\u5229\u59ec'},
        {'type_name': '\u7cbe\u54c1-\u9ed1\u6599\u5934\u6761', 'type_id': 'jingpin|\u9ed1\u6599\u5934\u6761'},
        {'type_name': '\u7cbe\u54c1-\u660e\u661fAI', 'type_id': 'jingpin|\u660e\u661fAI'},
        {'type_name': '\u7cbe\u54c1-\u4eba\u5996\u4f2a\u5a18', 'type_id': 'jingpin|\u4eba\u5996\u4f2a\u5a18'},
        {'type_name': '\u7cbe\u54c1-onlyfans', 'type_id': 'jingpin|onlyfans'},
        {'type_name': '\u7cbe\u54c1-\u63a2\u82b1\u7cfb\u5217', 'type_id': 'jingpin|\u63a2\u82b1\u7cfb\u5217'},
        {'type_name': '\u7cbe\u54c1-\u4e3b\u64ad\u5927\u79c0', 'type_id': 'jingpin|\u4e3b\u64ad\u5927\u79c0'},
        {'type_name': '\u7cbe\u54c1-\u97e9\u56fd\u4e3b\u64ad', 'type_id': 'jingpin|\u97e9\u56fd\u4e3b\u64ad'},
    ]

    filters = {
        'juqing': [{'key': 'tag', 'name': '\u5267\u60c5\u7b5b\u9009', 'value': [
            {'n': '\u5168\u90e8', 'v': ''}, {'n': '\u9ebb\u8c46\u4f20\u5a92', 'v': '\u9ebb\u8c46\u4f20\u5a92'}, {'n': '\u5929\u7f8e\u4f20\u5a92', 'v': '\u5929\u7f8e\u4f20\u5a92'},
            {'n': '\u661f\u7a7a\u679c\u51bb', 'v': '\u661f\u7a7a\u679c\u51bb'}, {'n': '\u871c\u6843\u7cbe\u4e1c', 'v': '\u871c\u6843\u7cbe\u4e1c'}, {'n': '\u97e9\u56fd\u4f26\u7406', 'v': '\u97e9\u56fd\u4f26\u7406'},
            {'n': 'COSPLAY', 'v': 'COSPLAY'}, {'n': '\u7ecf\u5178\u4e09\u7ea7', 'v': '\u7ecf\u5178\u4e09\u7ea7'}, {'n': '\u4e2d\u6587\u5b57\u5e55', 'v': '\u4e2d\u6587\u5b57\u5e55'},
        ]}],
        'shipin': [{'key': 'tag', 'name': '\u7535\u5f71\u7b5b\u9009', 'value': [
            {'n': '\u5168\u90e8', 'v': ''}, {'n': '\u65e5\u672cav', 'v': '\u65e5\u672cav'}, {'n': '\u97e9\u56fd\u70ed\u821e', 'v': '\u97e9\u56fd\u70ed\u821e'},
            {'n': '\u6b27\u7f8e\u7cbe\u54c1', 'v': '\u6b27\u7f8e\u7cbe\u54c1'}, {'n': '\u52a8\u6f2b\u7535\u5f71', 'v': '\u52a8\u6f2b\u7535\u5f71'}, {'n': '\u56fd\u4ea7\u81ea\u62cd', 'v': '\u56fd\u4ea7\u81ea\u62cd'},
            {'n': '\u5c9b\u56fd\u65e0\u7801', 'v': '\u5c9b\u56fd\u65e0\u7801'}, {'n': 'JVID', 'v': 'JVID'}, {'n': 'SM\u8c03\u6559', 'v': 'SM\u8c03\u6559'},
        ]}],
        'jingpin': [{'key': 'tag', 'name': '\u7cbe\u54c1\u7b5b\u9009', 'value': [
            {'n': '\u5168\u90e8', 'v': ''}, {'n': '\u8f6f\u840c\u798f\u5229\u59ec', 'v': '\u8f6f\u840c\u798f\u5229\u59ec'}, {'n': '\u9ed1\u6599\u5934\u6761', 'v': '\u9ed1\u6599\u5934\u6761'},
            {'n': '\u660e\u661fAI', 'v': '\u660e\u661fAI'}, {'n': '\u4eba\u5996\u4f2a\u5a18', 'v': '\u4eba\u5996\u4f2a\u5a18'}, {'n': 'onlyfans', 'v': 'onlyfans'},
            {'n': '\u63a2\u82b1\u7cfb\u5217', 'v': '\u63a2\u82b1\u7cfb\u5217'}, {'n': '\u4e3b\u64ad\u5927\u79c0', 'v': '\u4e3b\u64ad\u5927\u79c0'}, {'n': '\u97e9\u56fd\u4e3b\u64ad', 'v': '\u97e9\u56fd\u4e3b\u64ad'},
        ]}],
    }

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def homeContent(self, filter):
        result = {'class': self.classes}
        if filter:
            result['filters'] = self.filters
        return result

    def homeVideoContent(self):
        html_text = self.fetch(self.host + '/index/home.html', require_video=True)
        vods = self.parse_vod_list(html_text)
        if not vods:
            vods = [self.debug_vod('\u9996\u9875\u65e0\u6570\u636e', self.host + '/index/home.html', html_text)]
        return {'list': vods[:30]}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            pg = int(pg or 1)
            channel, tag = self.split_tid(tid)
            if isinstance(extend, dict) and extend.get('tag'):
                tag = extend.get('tag') or ''
            url = self.build_list_url(channel, tag, pg)
            html_text = self.fetch(url, require_video=True)
            vods = self.parse_vod_list(html_text)
            total = self.parse_total_page(html_text)
            if (not vods) and pg == 1:
                vods = [self.debug_vod('\u5206\u7c7b\u65e0\u6570\u636e', url, html_text)]
            return {
                'page': pg,
                'pagecount': total if total > 0 else (pg + 1 if vods else pg),
                'limit': 20,
                'total': (total if total > 0 else pg + 1) * 20,
                'list': vods,
            }
        except Exception as e:
            return {'page': 1, 'pagecount': 1, 'limit': 20, 'total': 1, 'list': [self.debug_vod('\u5206\u7c7b\u5f02\u5e38', str(e), '')]}

    def detailContent(self, ids):
        vod_id = ids[0]
        if str(vod_id).startswith('debug$'):
            msg = str(vod_id).split('$', 1)[1]
            return {'list': [{
                'vod_id': vod_id, 'vod_name': '\u8bca\u65ad\u4fe1\u606f', 'vod_pic': '', 'type_name': '\u8bca\u65ad',
                'vod_year': '', 'vod_area': '', 'vod_remarks': '\u8bf7\u628a\u8fd9\u6761\u5185\u5bb9\u53d1\u7ed9\u6211',
                'vod_actor': '', 'vod_director': '', 'vod_content': msg,
                'vod_play_from': '\u8bca\u65ad', 'vod_play_url': '\u8bca\u65ad$' + vod_id,
            }]}
        url = self.abs_url(vod_id)
        html_text = self.fetch(url)
        title = self.parse_detail_title(html_text) or self.title_from_id(vod_id)
        pic = self.parse_detail_pic(html_text)
        date = self.search_first(r'<div class=["\']video-item-date["\']>([^<]+)', html_text)
        vod = {
            'vod_id': vod_id,
            'vod_name': title,
            'vod_pic': pic,
            'type_name': '',
            'vod_year': date or '',
            'vod_area': '',
            'vod_remarks': date or '\u64ad\u653e',
            'vod_actor': '',
            'vod_director': '',
            'vod_content': title,
            'vod_play_from': '\u7ebf\u8def\u4e00$$$\u7ebf\u8def\u4e8c',
            'vod_play_url': '\u64ad\u653e$%s#\u5907\u7528$%s' % (vod_id + '@1', vod_id + '@2'),
        }
        return {'list': [vod]}

    def searchContent(self, key, quick, pg='1'):
        return self.searchContentPage(key, quick, pg)

    def searchContentPage(self, key, quick, pg):
        pg = int(pg or 1)
        self.ensure_host()
        vods = []
        urls = []
        for code in ['juqing', 'shipin', 'jingpin']:
            url = self.host + '/' + self.encode_path('/search/%s-%s-%s.html' % (code, key, pg)) + '.html'
            urls.append(url)
            text = self.fetch(url)
            vods.extend(self.parse_search_json(text, code))
        vods = self.dedupe(vods)
        if not vods and pg == 1:
            vods = [self.debug_vod('\u641c\u7d22\u65e0\u6570\u636e', ' ; '.join(urls), '')]
        return {'page': pg, 'pagecount': 1, 'limit': 20, 'total': len(vods), 'list': vods}

    def playerContent(self, flag, id, vipFlags):
        if str(id).startswith('debug$'):
            return {'parse': 0, 'playUrl': '', 'url': '', 'header': {}}
        if '@' in id:
            page_id, road = id.rsplit('@', 1)
        else:
            page_id, road = id, '1'
        page_url = self.abs_url(page_id)
        html_text = self.fetch(page_url)
        video = self.b64_from_js(html_text, 'video')
        host1 = self.b64_from_js(html_text, 'm3u8_host')
        host2 = self.b64_from_js(html_text, 'm3u8_host1')
        play_host = host1 if str(road) == '1' else (host2 or host1)
        play_url = urljoin(play_host or self.host, video or '')
        return {
            'parse': 0,
            'playUrl': '',
            'url': play_url,
            'header': {
                'User-Agent': self.headers['User-Agent'],
                'Referer': page_url,
            },
        }

    def localProxy(self, params):
        return [404, 'text/plain', '']

    def load_extend(self, extend):
        try:
            hosts = []
            if isinstance(extend, dict):
                hosts = extend.get('hosts') or extend.get('host') or []
            elif isinstance(extend, str) and extend.strip():
                ext = extend.strip()
                if ext.startswith('{'):
                    data = json.loads(ext)
                    hosts = data.get('hosts') or data.get('host') or []
                else:
                    hosts = re.split('[,\uff0c\\s]+', ext)
            if isinstance(hosts, str):
                hosts = [hosts]
            for h in hosts:
                h = self.normalize_host(h)
                if h:
                    self.content_hosts.insert(0, h)
            self.content_hosts = self.unique_hosts(self.content_hosts)
        except Exception:
            pass

    def ensure_host(self):
        # \u5148\u6d4b\u8bd5\u5df2\u6709\u5185\u5bb9\u57df\u540d\uff0c\u6210\u529f\u5c31\u76f4\u63a5\u7528\u3002
        for h in self.unique_hosts([self.host] + self.content_hosts):
            text, final_url = self.fetch_once(h + '/index/home.html')
            if self.looks_like_video_page(text):
                self.host = self.normalize_host(final_url) or h
                return self.host
        # \u5df2\u6709\u5185\u5bb9\u57df\u540d\u5931\u6548\u65f6\uff0c\u4ece\u5165\u53e3\u57df\u540d\u3001\u8df3\u8f6c\u7ed3\u679c\u3001\u9875\u9762\u91cc\u7684\u94fe\u63a5\u5b9e\u65f6\u53d1\u73b0\u65b0\u57df\u540d\u3002
        for h in self.discover_hosts():
            text, final_url = self.fetch_once(h + '/index/home.html')
            if self.looks_like_video_page(text):
                self.host = self.normalize_host(final_url) or h
                if self.host not in self.content_hosts:
                    self.content_hosts.insert(0, self.host)
                return self.host
        return self.host

    def discover_hosts(self):
        found = []
        seeds = self.unique_hosts([self.host] + self.content_hosts + self.entry_hosts)
        for h in seeds:
            for path in ['/', '/enter/index.html', '/index/home.html']:
                text, final_url = self.fetch_once(h + path)
                final_host = self.normalize_host(final_url)
                if final_host:
                    found.append(final_host)
                # \u5165\u53e3\u9875\u6216\u811a\u672c\u91cc\u5982\u679c\u51fa\u73b0\u5b8c\u6574\u57df\u540d\uff0c\u4e5f\u52a0\u5165\u5019\u9009\u3002
                for u in re.findall(r'https?://[A-Za-z0-9.-]+', text or ''):
                    uh = self.normalize_host(u)
                    if uh and uh.endswith('.top'):
                        found.append(uh)
                # \u6709\u4e9b\u5165\u53e3\u9875\u53ea\u5199 //www.xxx.top\u3002
                for u in re.findall(r'//[A-Za-z0-9.-]+\.top', text or ''):
                    uh = self.normalize_host('https:' + u)
                    if uh:
                        found.append(uh)
        # \u65b0\u53d1\u73b0\u7684\u57df\u540d\u6392\u524d\u9762\uff0c\u4e0b\u4e00\u6b21\u76f4\u63a5\u4f7f\u7528\uff1b\u4e0d\u628a\u5931\u6548\u7684\u542f\u52a8 host \u5f3a\u884c\u585e\u8fdb\u5185\u5bb9\u57df\u540d\u6c60\u3002
        hosts = self.unique_hosts(found)
        if hosts:
            self.content_hosts = self.unique_hosts(hosts + self.content_hosts)
        return hosts

    def fetch(self, url, require_video=False):
        self.last_error = ''
        if require_video:
            self.ensure_host()
        best = ''
        for u in self.candidate_urls(url):
            text, final_url = self.fetch_once(u)
            if not text:
                continue
            if not best:
                best = text
            final_host = self.normalize_host(final_url)
            if final_host and self.looks_like_video_page(text):
                self.host = final_host
            if (not require_video) or self.looks_like_video_page(text):
                return text
        return best

    def fetch_once(self, url):
        errors = []
        headers = self.get_headers(url)
        try:
            from urllib.request import Request, urlopen
            req = Request(url, headers=headers)
            with urlopen(req, timeout=8) as r:
                return self.to_text(r.read()), getattr(r, 'url', url)
        except Exception as e:
            errors.append('urllib=' + repr(e))
        try:
            import requests
            r = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
            return self.to_text(r.text), getattr(r, 'url', url)
        except Exception as e:
            errors.append('requests=' + repr(e))
        try:
            rsp = super().fetch(url, headers=headers)
            text, final_url = self.response_to_text(rsp, url)
            if text:
                return text, final_url
        except Exception as e:
            errors.append('super=' + repr(e))
        self.last_error = ' ; '.join(errors)[-500:]
        return '', url

    def build_list_url(self, channel, tag, pg):
        pg = int(pg or 1)
        if tag:
            path = '/%s/list-%s.html' % (channel, tag) if pg <= 1 else '/%s/list-%s-%s.html' % (channel, tag, pg)
        else:
            path = '/%s/list.html' % channel if pg <= 1 else '/%s/list-%s.html' % (channel, pg)
        return self.host + '/' + self.encode_path(path) + '.html'

    def encode_path(self, path):
        return 'cYc' + base64.b64encode(path.encode('utf-8')).decode('utf-8')

    def candidate_urls(self, url):
        url = self.abs_url(url)
        out = []
        for h in self.unique_hosts([self.host] + self.content_hosts):
            for v in self.url_variants(self.replace_host(url, h)):
                out.append(v)
        return self.unique_urls(out)

    def url_variants(self, url):
        out = [url]
        try:
            raw = unquote(url)
            out.append(raw)
            p = urlparse(raw)
            out.append(urlunparse((p.scheme, p.netloc, quote(p.path, safe='/%+='), p.params, p.query, p.fragment)))
            out.append(urlunparse((p.scheme, p.netloc, quote(p.path, safe='/'), p.params, p.query, p.fragment)))
        except Exception:
            pass
        return self.unique_urls(out)

    def parse_vod_list(self, html_text):
        vods = []
        if not html_text:
            return vods
        blocks = re.findall(r'<a\b[^>]*class=["\'][^"\']*\bvideo-item\b[^"\']*["\'][\s\S]*?</a>', html_text)
        for block in blocks:
            href = self.search_first(r'href=["\']([^"\']+)["\']', block)
            if not href:
                continue
            pic = self.search_first(r'<img[^>]+data-base64=["\']([^"\']+)["\']', block)
            title_enc = self.search_first(r'<div[^>]+video-item-title[^>]+title=["\']([^"\']*)["\']', block)
            title = self.decode_title(title_enc)
            if not title:
                title = self.clean_text(self.search_first(r'<div[^>]+video-item-title[^>]*>([\s\S]*?)</div>', block))
            date = self.search_first(r'<div class=["\']video-item-date["\']>([^<]+)', block)
            if not title:
                title = self.title_from_id(href)
            vods.append({
                'vod_id': href,
                'vod_name': title,
                'vod_pic': self.abs_url(pic),
                'vod_remarks': date or '\u64ad\u653e',
            })
        return self.dedupe(vods)

    def parse_search_json(self, text, default_channel):
        vods = []
        try:
            data = json.loads(text or '[]')
        except Exception:
            return vods
        if not isinstance(data, list):
            return vods
        for item in data:
            if not isinstance(item, dict):
                continue
            vid = item.get('id')
            channel = item.get('channel') or default_channel
            if not vid or channel not in ['juqing', 'shipin', 'jingpin']:
                continue
            title = self.decode_title(item.get('title') or '') or ('\u89c6\u9891' + str(vid))
            pic = item.get('thumb') or ''
            try:
                date = self.format_date(int(item.get('insert_time') or 0))
            except Exception:
                date = ''
            vods.append({
                'vod_id': '/' + self.encode_path('/%s/play-%s.html' % (channel, vid)) + '.html',
                'vod_name': title,
                'vod_pic': self.abs_url(pic),
                'vod_remarks': date or '\u64ad\u653e',
            })
        return vods

    def parse_total_page(self, html_text):
        nums = re.findall('title=["\\\']\u7b2c"?(\\d+)"?\u9875["\\\']', html_text or '')
        nums += re.findall(r'>(\d+)</a>', html_text or '')
        arr = []
        for n in nums:
            try:
                arr.append(int(n))
            except Exception:
                pass
        return max(arr) if arr else 0

    def parse_detail_title(self, html_text):
        play_title = self.search_first(r'<div class=["\']play-title["\'][\s\S]*?title=["\']([^"\']+)["\']', html_text or '')
        txt = self.decode_title(play_title)
        if txt:
            return txt
        candidates = re.findall(r'class=["\'][^"\']*dec-ti[^"\']*["\'][^>]*title=["\']([^"\']+)["\']', html_text or '')
        decoded = []
        for item in candidates:
            txt = self.decode_title(item)
            if txt:
                decoded.append(txt)
        bad = set(['\u5267\u60c5\u533a', '\u7535\u5f71\u533a', '\u7cbe\u54c1\u533a', '\u56fe\u7247\u533a', '\u5c0f\u8bf4\u533a', '\u64b8\u64b8\u533a', '\u535a\u5f69\u533a', '\u7279\u8272\u533a', '\u7ebf\u8def\u4e00', '\u7ebf\u8def\u4e8c', '\u4e2d\u6587\u5b57\u5e55'])
        for txt in decoded:
            if txt in bad or '\u9996\u9875' in txt:
                continue
            if len(txt) >= 18 or re.search(r'[A-Z]{2,6}[-_ ]?\d{2,}', txt):
                return txt
        for txt in decoded:
            if txt not in bad and '\u9996\u9875' not in txt and len(txt) > 2:
                return txt
        return ''

    def parse_detail_pic(self, html_text):
        pic = self.search_first(r'<img[^>]+data-base64=["\']([^"\']+)["\']', html_text or '')
        return self.abs_url(pic)

    def b64_from_js(self, html_text, var_name):
        pattern = r'var\s+' + re.escape(var_name) + r'\s*=\s*decodeString\([\'"]([^\'"]+)[\'"]\)'
        enc = self.search_first(pattern, html_text or '')
        return self.decode_base64_utf8(enc) if enc else ''

    def decode_title(self, data):
        data = html.unescape(data or '').strip()
        if not data:
            return ''
        if self.has_cn(data):
            return data
        txt = self.decode_base64_utf8(data)
        if txt and self.has_readable(txt):
            return txt
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
            key = base64.b64decode('SWRUSnEwSGtscHVJNm11OGlCJU9PQCF2ZF40SyZ1WFc=')
            iv = base64.b64decode('JDB2QGtySDdWMg==') + b'883346'
            raw = base64.b64decode(data + '===')
            dec = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(raw), AES.block_size)
            return dec.decode('utf-8', 'ignore').replace('"', '').strip()
        except Exception:
            return ''

    def decode_base64_utf8(self, data):
        try:
            return base64.b64decode((data or '') + '===').decode('utf-8')
        except Exception:
            return ''

    def split_tid(self, tid):
        if '|' in tid:
            return tid.split('|', 1)
        return tid, ''

    def title_from_id(self, href):
        try:
            s = unquote(href or '')
            s = s.rsplit('.html', 1)[0].rsplit('/', 1)[-1]
            if s.startswith('cYc'):
                path = base64.b64decode(s[3:] + '===').decode('utf-8')
                m = re.search(r'play-(\d+)', path)
                if m:
                    return '\u89c6\u9891' + m.group(1)
        except Exception:
            pass
        return '\u89c6\u9891'

    def abs_url(self, url):
        if not url:
            return ''
        url = html.unescape(url)
        if url.startswith('//'):
            return 'https:' + url
        if url.startswith('http://') or url.startswith('https://'):
            return url
        return urljoin(self.host, url)

    def replace_host(self, url, host):
        try:
            p = urlparse(url)
            hp = urlparse(host)
            return urlunparse((hp.scheme, hp.netloc, p.path, p.params, p.query, p.fragment))
        except Exception:
            return url

    def get_headers(self, referer=''):
        h = dict(self.headers)
        h['Referer'] = referer if str(referer).startswith('http') else self.host + '/index/home.html'
        return h

    def normalize_host(self, url):
        try:
            if not url:
                return ''
            if not str(url).startswith('http'):
                url = 'https://' + str(url).strip().strip('/')
            p = urlparse(str(url).strip())
            if not p.scheme or not p.netloc:
                return ''
            return p.scheme + '://' + p.netloc
        except Exception:
            return ''

    def unique_hosts(self, hosts):
        out, seen = [], set()
        for h in hosts:
            h = self.normalize_host(h)
            if h and h not in seen:
                seen.add(h)
                out.append(h)
        return out

    def unique_urls(self, urls):
        out, seen = [], set()
        for u in urls:
            if u and u not in seen:
                seen.add(u)
                out.append(u)
        return out

    def response_to_text(self, rsp, url):
        if rsp is None:
            return '', url
        if isinstance(rsp, dict):
            return self.to_text(rsp.get('content') or rsp.get('body') or rsp.get('text') or ''), rsp.get('url') or url
        if isinstance(rsp, (str, bytes)):
            return self.to_text(rsp), url
        for key in ('text', 'content', 'body'):
            try:
                data = getattr(rsp, key)
                if data:
                    return self.to_text(data), getattr(rsp, 'url', url)
            except Exception:
                pass
        return self.to_text(rsp), getattr(rsp, 'url', url)

    def to_text(self, data):
        if data is None:
            return ''
        if isinstance(data, bytes):
            for enc in ('utf-8', 'gbk', 'gb18030'):
                try:
                    return data.decode(enc)
                except Exception:
                    pass
            return data.decode('utf-8', 'ignore')
        return str(data)

    def clean_text(self, text):
        text = re.sub(r'<[^>]+>', ' ', text or '')
        text = html.unescape(text)
        return re.sub(r'\s+', ' ', text).strip()

    def format_date(self, ts):
        try:
            import time
            return time.strftime('%Y-%m-%d', time.localtime(int(ts)))
        except Exception:
            return ''

    def search_first(self, pattern, text):
        m = re.search(pattern, text or '', re.S)
        return html.unescape(m.group(1).strip()) if m else ''

    def has_cn(self, text):
        return bool(re.search(r'[\u4e00-\u9fff]', text or ''))

    def has_readable(self, text):
        return bool(re.search(r'[\u4e00-\u9fffA-Za-z0-9]', text or ''))

    def looks_like_video_page(self, text):
        return bool(text and ('video-item' in text or 'data-base64' in text or 'm3u8_host' in text))

    def dedupe(self, vods):
        seen, out = set(), []
        for v in vods:
            vid = v.get('vod_id')
            if vid and vid not in seen:
                seen.add(vid)
                out.append(v)
        return out

    def debug_vod(self, title, url, html_text):
        info = [
            title,
            'host=' + str(self.host),
            'url=' + str(url),
            'html_len=' + str(len(html_text or '')),
            'video_item=' + str((html_text or '').count('video-item')),
            'data_base64=' + str((html_text or '').count('data-base64')),
            'm3u8_host=' + str((html_text or '').count('m3u8_host')),
            'error=' + str(getattr(self, 'last_error', '')),
            'snippet=' + self.clean_text((html_text or '')[:180]),
        ]
        msg = ' | '.join(info)
        return {'vod_id': 'debug$' + msg, 'vod_name': '\u3010\u8bca\u65ad\u3011' + msg[:180], 'vod_pic': '', 'vod_remarks': '\u628a\u8fd9\u6761\u5185\u5bb9\u53d1\u7ed9\u6211'}
