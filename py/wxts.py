# -*- coding: utf-8 -*-
# WXTS \u7ad9\u6e90\uff08MacCMS \u6a21\u677f \u00b7 HTML \u76f4\u6293\u7248\uff09
# \u53d1\u5e03\u9875: \u7ad9\u65b9 github.io\uff08\u9759\u6001\u5217\u51fa 966~969 \u56db\u955c\u50cf\uff0c2026-09-08 \u5b9e\u6d4b\u5168\u6d3b\uff09
# \u7ed3\u6784: \u5206\u7c7b /index.php/vod/type/id/{tid}/page/{pg}.html\uff08\u5217\u8868\u76f4\u94fe\u64ad\u653e\u9875\uff09
#       \u64ad\u653e\u9875 var player_aaaa = {...} \u5185\u542b url(m3u8)/poster/link
# \u5206\u7c7b\u540d\u4e0d\u843d\u76d8\uff0chomeContent \u4ece\u9996\u9875\u5b9e\u65f6\u83b7\u53d6\uff08\u8bcd\u8868 b64 \u4e5f\u4e0d\u9700\u8981\uff09
import json
import re
import sys
import os
import html as _html
from urllib.parse import quote

import requests
sys.path.append('..')
from base.spider import Spider as BaseSpider

try:
    from hostresolver import resolve_host, parse_ext
except Exception:
    # hostresolver.py \u5728 source/ \u6839\uff08py/ \u7684\u4e0a\u7ea7\uff09\uff0c\u6309\u811a\u672c\u81ea\u8eab\u4f4d\u7f6e\u5b9a\u4f4d\uff0c\u4e0d\u4f9d\u8d56 cwd
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext
    except Exception:
        resolve_host = None
        parse_ext = None

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# \u5217\u8868\u6761\u76ee: <a class="thumbnail" href="..."><img src=\u5c01\u9762 alt=\u6807\u9898>
# \u5206\u7c7b\u9875 href=\u64ad\u653e\u9875(/vod/play/id/N/sid/N/nid/N.html)\uff1b\u641c\u7d22\u9875 href=\u8be6\u60c5\u9875(/vod/detail/id/N.html)
_RE_ITEM = re.compile(
    r'<a[^>]*class="[^"]*thumbnail[^"]*"[^>]*href="(/index\.php/vod/(?:play/id/(\d+)/sid/(\d+)/nid/(\d+)|detail/id/(\d+))\.html)"[^>]*>\s*<img([^>]*)>')
_RE_ATTR = re.compile(r'(src|alt)\s*=\s*"([^"]*)"')
_RE_PLAY_HREF = re.compile(r'/index\.php/vod/play/id/(\d+)/sid/(\d+)/nid/(\d+)\.html')


class Spider(BaseSpider):

    # \u7ad9\u65b9\u53d1\u5e03\u9875\uff08github.io \u9759\u6001\u9875\uff0c\u5217\u6700\u65b0\u955c\u50cf\u57df\u540d\uff09
    PUBLISH_PAGE = 'https://wuxiants.github.io/'
    # \u5185\u7f6e\u5019\u9009\uff082026-09-08 \u5b9e\u6d4b\uff0c\u53d1\u5e03\u9875\u5217\u51fa\u7684\u56db\u4e2a\u955c\u50cf\uff09
    BUILTIN_HOSTS = [
        'https://wxts.wuxiants966.com',
        'https://wxts.wuxiants967.com',
        'https://wxts.wuxiants968.com',
        'https://wxts.wuxiants969.com',
    ]

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
                self.proxies = {}
                if parse_ext:
                    try:
                        self._ext = parse_ext(ext_str)
                    except Exception:
                        self._ext = {}
        self.headers = {
            'User-Agent': _UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
        }
        self.host = self.get_working_host()
        self.headers.update({'Origin': self.host, 'Referer': self.host + '/'})
        print(f'使用站点: {self.host}')

    def getName(self):
        return "\u65e0\u9650\u81c0\u5c71"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def get_working_host(self):
        publish = self._ext.get('publish') or self.PUBLISH_PAGE
        builtin = self.BUILTIN_HOSTS
        if resolve_host:
            try:
                h = resolve_host(
                    publish_page=publish,
                    candidate_hosts=list(self._ext.get('hosts') or []) + builtin,
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=8,
                )
                if h:
                    return h
            except Exception:
                pass
        # resolver \u7f3a\u5931\u515c\u5e95\uff1aext \u6307\u5b9a \u2192 \u5185\u7f6e\u9010\u4e2a\u8bd5
        for h in list(self._ext.get('hosts') or []) + builtin:
            try:
                r = requests.get(h.rstrip('/') + '/', headers=self.headers,
                                 proxies=self.proxies, timeout=8, verify=False)
                if r.status_code == 200 and 'vod/type' in (r.text or ''):
                    return h.rstrip('/')
            except Exception:
                continue
        return builtin[0]

    def _get(self, path):
        url = path if path.startswith('http') else self.host + path
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False)

    @staticmethod
    def _parse_items(html_text):
        out = []
        seen = set()
        for m in _RE_ITEM.finditer(html_text):
            img = m.group(6)
            pic = alt = ''
            for a in _RE_ATTR.finditer(img):
                if a.group(1) == 'src' and not pic:
                    pic = _html.unescape(a.group(2)).strip()
                elif a.group(1) == 'alt' and not alt:
                    alt = _html.unescape(a.group(2)).strip()
            if not alt:
                continue
            # vod_id \u4e24\u79cd\u5f62\u6001\uff1a\u64ad\u653e\u9875\u76f4\u94fe = vid-sid-nid\uff1b\u641c\u7d22\u8be6\u60c5\u9875 = d{vid}
            if m.group(2):
                vod_id = f'{m.group(2)}-{m.group(3)}-{m.group(4)}'
            else:
                vod_id = f'd{m.group(5)}'
            if vod_id in seen:
                continue
            seen.add(vod_id)
            out.append({
                'vod_id': vod_id,
                'vod_name': alt,
                'vod_pic': pic,
                'vod_remarks': '',
            })
        return out

    def homeContent(self, flag):
        result = {'class': [], 'list': []}
        try:
            r = self._get('/')
            body = r.text or ''
        except Exception:
            return result
        seen = set()
        for m in re.finditer(
                r'href="(/index\.php/vod/type/id/(\d+)\.html)"[^>]*>([^<]+)<', body):
            tid, name = m.group(2), _html.unescape(m.group(3)).strip()
            if tid in seen or not name or name == '\u66f4\u591a':
                continue
            seen.add(tid)
            result['class'].append({'type_id': tid, 'type_name': name})
        result['list'] = self._parse_items(body)
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        result = {'list': []}
        try:
            r = self._get(f'/index.php/vod/type/id/{tid}/page/{pg}.html')
            result['list'] = self._parse_items(r.text or '')
        except Exception:
            pass
        return result

    def searchContent(self, key, quick, pg='1'):
        result = {'list': []}
        try:
            path = f'/index.php/vod/search.html?wd={quote(key)}'
            if str(pg) not in ('1', ''):
                path += f'&page={pg}'
            r = self._get(path)
            result['list'] = self._parse_items(r.text or '')
        except Exception:
            pass
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    def _play_page(self, vid, sid, nid):
        return self._get(f'/index.php/vod/play/id/{vid}/sid/{sid}/nid/{nid}.html')

    @staticmethod
    def _player_cfg(html_text):
        j = html_text.find('player_aaaa')
        if j < 0:
            return {}
        start = html_text.find('{', j)
        if start < 0:
            return {}
        # \u627e\u542b "url" \u952e\u7684\u5bf9\u8c61\u7ec8\u70b9\uff1a\u4ece m3u8/mp4 \u5904\u5411\u540e\u627e "sid" \u540e\u7684\u6536\u5c3e }
        end = html_text.find('</script>', start)
        seg = html_text[start:end if end > 0 else start + 8000]
        try:
            return json.loads(seg.strip().rstrip(';').replace('\\/', '/'))
        except Exception:
            # \u515c\u5e95\uff1a\u622a\u5230\u6700\u540e\u4e00\u4e2a } \u524d
            k = seg.rfind('}')
            if k > 0:
                try:
                    return json.loads(seg[:k + 1].replace('\\/', '/'))
                except Exception:
                    return {}
            return {}

    def _resolve_play(self, vod_id):
        """\u5f52\u4e00 vod_id \u2192 (vid, sid, nid)\u3002'd{vid}' \u5f62\u6001\u5148\u6293\u8be6\u60c5\u9875\u89e3\u6790\u64ad\u653e\u94fe\u63a5\u3002"""
        vod_id = str(vod_id)
        if vod_id.startswith('d'):
            body = self._get(f'/index.php/vod/detail/id/{vod_id[1:]}.html').text or ''
            m = _RE_PLAY_HREF.search(body)
            if not m:
                return None, None, None
            return m.group(1), m.group(2), m.group(3)
        parts = (vod_id.split('-') + ['1', '1'])[:3]
        return parts[0], parts[1], parts[2]

    def detailContent(self, ids):
        result = {'list': []}
        try:
            vid, sid, nid = self._resolve_play(ids[0])
            if not vid:
                return result
            body = self._play_page(vid, sid, nid).text or ''
            cfg = self._player_cfg(body)
            title = ''
            m = re.search(r'<title>([^<]+)</title>', body)
            if m:
                title = _html.unescape(m.group(1)).strip()
                title = re.sub('^\u5728\u7ebf\u89c2\u770b', '', title).replace('_\u65e0\u9650\u81c0\u5c71', '').strip()
            pic = str(cfg.get('poster') or '').strip()
            if not pic:
                m2 = re.search(r'<img[^>]*src="([^"]*(?:upload|vod)[^"]*)"', body)
                pic = _html.unescape(m2.group(1)).strip() if m2 else ''
            vod_id = f'{vid}-{sid}-{nid}'
            result['list'].append({
                'vod_id': vod_id,
                'vod_name': title or vid,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': '',
                'vod_director': '',
                'vod_content': '',
                'vod_play_from': str(cfg.get('from') or 'wxts'),
                'vod_play_url': f'播放${vod_id}',
            })
        except Exception:
            pass
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {'parse': 0, 'playUrl': '', 'url': '', 'header': {'User-Agent': _UA}}
        try:
            vid, sid, nid = self._resolve_play(id)
            if not vid:
                return result
            body = self._play_page(vid, sid, nid).text or ''
            cfg = self._player_cfg(body)
            url = str(cfg.get('url') or '').strip()
            if url:
                result['url'] = url
                result['header'] = {'User-Agent': _UA, 'Referer': self.host + '/'}
        except Exception:
            pass
        return result
