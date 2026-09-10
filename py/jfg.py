# -*- coding: utf-8 -*-
# JFG \u7ad9\u6e90\uff08\u96c6\u82b3\u9601\u4e91\u641c \u00b7 HTML \u76f4\u6293\u7248\uff09
# \u57df\u540d: sourceUrl \u81ea\u5e26\u7684 punycode \u82b1\u5f0f\u57df\u540d\uff08"\u8bf7\u8bb0\u4f4f-jifangge\u70b9com.\u4e91\u641c\u798f\u5229.com"\uff09
#       \u5373\u73b0\u5f79\u5165\u53e3\uff0c2026-09-08 \u5b9e\u6d4b 200\uff08Cloudflare\uff09\uff1b\u7ad9\u5185\u4e92\u94fe twin \u57df\u540c\u6837\u53ef\u7528
# \u7ed3\u6784: \u5206\u7c7b = newlist.php?p={n}(\u4eca\u65e5\u66f4\u65b0) / toplist.php?p={n}(\u4eca\u65e5\u70ed\u64adTop100)
#       \u6761\u76ee <a href="content/{md5}.html"> + cover \u80cc\u666f\u56fe + ctitle \u6807\u9898 + vodtime
#       \u8be6\u60c5 m3u8 \u5728 <a playdata="..."> \u660e\u6587\u5c5e\u6027
#       \u641c\u7d22 /search-0-{pg}-{AES\u5bc6\u6587b64}.html\uff1a\u8bcd\u6761 AES-CBC(key/iv \u5747 16 \u5b57\u8282 ASCII)
#       \u52a0\u5bc6\u2192base64\u2192URL \u7f16\u7801\uff082026-09-08 \u5b9e\u6d4b 200\uff0c\u4e0e\u5217\u8868\u9875\u540c\u6b3e li \u7ed3\u6784\u53ef\u590d\u7528\u89e3\u6790\uff09
import json
import re
import sys
import os
import base64
import html as _html
from urllib.parse import urljoin, quote

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
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

# \u5217\u8868\u6761\u76ee: \u6309 <li> \u5206\u5757\uff1b\u5757\u5185 <a href="content/{md5}.html..."> + cover \u80cc\u666f\u56fe
#           + <p>\u6807\u9898</p> + vodtime
_RE_LINK = re.compile(r'<a[^>]*href="(content/[a-f0-9]+\.html[^"]*)"')
_RE_COVER = re.compile(r"background-image:\s*url\('([^']+)'\)")
_RE_CTITLE = re.compile(r'<div class="ctitle">\s*<p>([^<]+)</p>')
_RE_VT = re.compile(r'<span class="vodtime">([^<]+)</span>')
_RE_HREF = re.compile(r'<a[^>]*href="([^"]+)"')
_RE_POSTER = re.compile(r"poster=['\"]([^'\"]+)['\"]")
_RE_PLAY = re.compile(r'<a[^>]*playdata="([^"]+\.m3u8[^"]*)"')


class Spider(BaseSpider):

    # \u5185\u7f6e\u5019\u9009\uff082026-09-08 \u5b9e\u6d4b 200\uff1bpunycode = \u8bf7\u8bb0\u4f4f-jifangge\u70b9com.\u4e91\u641c\u798f\u5229.com\uff09
    BUILTIN_HOSTS = [
        'https://xn---jifanggecom-ud8sv658aesydp6a.xn--9kq80g37uthu.com',
        'https://xn--u2uy07cd3d2mxd2a.com',
    ]
    # \u65e0\u72ec\u7acb\u53d1\u5e03\u9875\uff1a\u5165\u53e3\u57df\u540d\u5373\u82b1\u5f0f\u57df\u540d\uff08\u7ad9\u65b9\u8bbe\u8ba1\u4e3a\u597d\u8bb0\u4e0d\u6613\u5c01\uff09
    PUBLISH_PAGE = ''

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
        return "\u96c6\u82b3\u9601"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def get_working_host(self):
        builtin = self.BUILTIN_HOSTS
        publish = self._ext.get('publish') or self.PUBLISH_PAGE or builtin[0]

        def _validate(host, text):
            t = text or ''
            return '\u96c6\u82b3\u9601' in t or 'h_d_key' in t

        if resolve_host:
            try:
                h = resolve_host(
                    publish_page=publish,
                    candidate_hosts=list(self._ext.get('hosts') or []) + builtin,
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=8,
                    validate=_validate,
                )
                if h:
                    return h
            except Exception:
                pass
        for h in list(self._ext.get('hosts') or []) + builtin:
            try:
                r = requests.get(h.rstrip('/') + '/', headers=self.headers,
                                 proxies=self.proxies, timeout=8, verify=False)
                if r.status_code == 200 and _validate(h, r.text):
                    return h.rstrip('/')
            except Exception:
                continue
        return builtin[0]

    def _get(self, path):
        if path.startswith('http'):
            url = path
        else:
            url = self.host.rstrip('/') + '/' + path.lstrip('/')
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False)

    @staticmethod
    def _parse_list(html_text):
        out = []
        seen = set()
        for blk in html_text.split('<li>')[1:]:
            ml = _RE_LINK.search(blk)
            if not ml:
                continue
            link = ml.group(1)
            key = link.split('?')[0]
            if key in seen:
                continue
            mt = _RE_CTITLE.search(blk)
            title = _html.unescape(mt.group(1)).strip() if mt else ''
            if not title:
                continue
            seen.add(key)
            pic = ''
            mc = _RE_COVER.search(blk)
            if mc:
                pic = _html.unescape(mc.group(1)).strip()
            remark = ''
            mv = _RE_VT.search(blk)
            if mv:
                remark = mv.group(1).strip()
            out.append({
                'vod_id': key,
                'vod_name': title,
                'vod_pic': pic,
                'vod_remarks': remark,
            })
        return out

    def homeContent(self, flag):
        result = {'class': [
            {'type_id': 'newlist', 'type_name': '\u4eca\u65e5\u66f4\u65b0'},
            {'type_id': 'toplist', 'type_name': '\u4eca\u65e5\u70ed\u64adTop100'},
        ], 'list': []}
        try:
            result['list'] = self._parse_list(self._get('/newlist.php?p=1').text or '')
        except Exception:
            pass
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        result = {'list': []}
        try:
            result['list'] = self._parse_list(
                self._get(f'/{tid}.php?p={pg}').text or '')
        except Exception:
            pass
        return result

    def _search_ct(self, key):
        """\u641c\u7d22\u8bcd\u6761 AES-CBC \u52a0\u5bc6 \u2192 base64\uff08key/iv \u4e0e\u7ad9\u65b9 JS \u540c\u53c2\u6570\uff09\u3002"""
        ct = AES.new(b'2d4ebb7cb767dab1', AES.MODE_CBC, b'7563ca4af41bd0fb')
        return base64.b64encode(ct.encrypt(pad(key.encode('utf-8'), 16))).decode()

    def _search(self, key, pg):
        result = {'list': []}
        try:
            kw = (key or '').strip()
            if not kw:
                return result
            n = int(pg) if str(pg).isdigit() else 1
            path = f'/search-0-{n}-{quote(self._search_ct(kw), safe="")}.html'
            result['list'] = self._parse_list(self._get(path).text or '')
        except Exception:
            pass
        return result

    def searchContent(self, key, quick, pg='1'):
        return self._search(key, pg)

    def searchContentPage(self, key, quick, pg):
        return self._search(key, pg)

    def detailContent(self, ids):
        result = {'list': []}
        try:
            key = str(ids[0]).split('?')[0]
            body = self._get(key).text or ''
            title = ''
            m = re.search(r'<title>([^<]+)</title>', body)
            if m:
                title = _html.unescape(m.group(1)).strip()
                title = re.sub('\\s*[-|]\\s*\u96c6\u82b3\u9601.*$', '', title).strip()
            pic = ''
            mp = _RE_POSTER.search(body)
            if mp:
                pic = (mp.group(1) or mp.group(2) or '').strip()
            url = _absolute(self.host, key)
            result['list'].append({
                'vod_id': key,
                'vod_name': title or key,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': '',
                'vod_director': '',
                'vod_content': '',
                'vod_play_from': 'jfg',
                'vod_play_url': f'播放${url}',
            })
        except Exception:
            pass
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {'parse': 0, 'playUrl': '', 'url': '', 'header': {'User-Agent': _UA}}
        try:
            url = str(id)
            body = self._get(url).text or ''
            mp = _RE_PLAY.search(body)
            if mp:
                result['url'] = mp.group(1).strip()
                result['header'] = {'User-Agent': _UA, 'Referer': self.host + '/'}
        except Exception:
            pass
        return result


def _absolute(host, path):
    if path.startswith('http'):
        return path
    return host + '/' + path.lstrip('/')
