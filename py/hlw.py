# -*- coding: utf-8 -*-
# HLW \u7ad9\u6e90\uff08\u9ed1\u6599\u7f51 \u00b7 Typecho \u98ce\u683c HTML \u76f4\u6293\u7248\uff09
# \u53d1\u5e03\u9875: hlwf6.com\uff08"\u9ed1\u6599\u7f51\u6700\u65b0\u5165\u53e3-\u5b9e\u65f6\u66f4\u65b0\u8bbf\u95ee\u7ebf\u8def"\uff0c2026-09-08 \u5b9e\u6d4b 200\uff0c
#         \u5217 4 \u4e2a .cc \u6cdb\u57fa\u57df\u7ebf\u8def + cloudfront \u515c\u5e95\uff0c\u57fa\u57df\u8f6e\u6362\u540e\u53d1\u5e03\u9875\u5373\u66f4\u65b0\uff09
# \u7ed3\u6784: \u5206\u7c7b /{slug}/ \u7ffb\u9875 /{slug}/page/{n}/\uff1b\u8be6\u60c5 /archives/{id}/
#       \u5217\u8868\u6761\u76ee video-item\uff08\u5c01\u9762 img \u7684 z-image-loader-url \u5c5e\u6027 + alt \u6807\u9898\uff09
#       \u64ad\u653e dplayer config='{...}' JSON\uff08\/ \u8f6c\u4e49\u987b\u8fd8\u539f\uff09\uff0c\u591a\u89c6\u9891=\u591a config \u5757
import json
import re
import sys
import os
import html as _html
import base64
from collections import OrderedDict
from urllib.parse import quote

import requests
from Crypto.Cipher import AES
sys.path.append('..')
from base.spider import Spider as BaseSpider

try:
    from hostresolver import resolve_host, parse_ext, probe_first
except Exception:
    # hostresolver.py \u5728 source/ \u6839\uff08py/ \u7684\u4e0a\u7ea7\uff09\uff0c\u6309\u811a\u672c\u81ea\u8eab\u4f4d\u7f6e\u5b9a\u4f4d\uff0c\u4e0d\u4f9d\u8d56 cwd
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# \u2500\u2500 \u5c01\u9762\u56fe\u5e8a\uff1apic.hdhwqx.cn \u4e3a CDN \u7ea7 AES \u52a0\u5bc6\u56fe\uff08\u4e0e\u9ed1\u6599\u4e0d\u6253\u70ca\u540c\u6b3e key\uff09\uff0c
#    App \u76f4\u63a5\u52a0\u8f7d\u662f\u5bc6\u6587=\u5c01\u9762\u5168\u7a7a\uff0c\u7edf\u4e00\u8d70 localProxy \u53d6\u56fe+\u6309\u9700\u89e3\u5bc6+LRU \u7f13\u5b58
_img_session = requests.Session()
_img_session.verify = False
_img_cache = OrderedDict()
_IMG_CACHE_MAX = 60


def _img_fetch(url, referer):
    """\u53d6\u56fe+magic \u9884\u68c0+\u6309\u9700\u89e3\u5bc6+\u7f13\u5b58\uff0c\u8fd4\u56de (status, content_type, bytes)\u3002"""
    if url in _img_cache:
        _img_cache.move_to_end(url)
        return (200,) + _img_cache[url]
    h = {'User-Agent': _UA, 'Referer': referer}
    try:
        r = _img_session.get(url, headers=h, timeout=10)
    except Exception:
        return [404, 'text/plain', b'']
    if r.status_code != 200:
        return [404, 'text/plain', b'']
    raw = r.content
    ct = 'image/jpeg'
    if raw[:3] == b'\xff\xd8\xff':
        b = raw
    elif raw[:8] == b'\x89PNG\r\n\x1a\n':
        b, ct = raw, 'image/png'
    elif raw[:4] == b'GIF8':
        b, ct = raw, 'image/gif'
    else:
        try:
            b = AES.new(b'f5d965df75336270', AES.MODE_CBC, b'97b60394abc2fbe1').decrypt(raw)
        except Exception:
            return [404, 'text/plain', b'']
        if b[:8] == b'\x89PNG\r\n\x1a\n':
            ct = 'image/png'
        elif b[:4] == b'GIF8':
            ct = 'image/gif'
    if b:
        _img_cache[url] = (ct, b)
        if len(_img_cache) > _IMG_CACHE_MAX:
            _img_cache.popitem(last=False)
    return [200, ct, b]

# \u5217\u8868\u6761\u76ee: <a class="cursor-pointer" href="/archives/{id}/"> ... z-image-loader-url="\u5c01\u9762" alt="\u6807\u9898"
_RE_CARD = re.compile(
    r'<a[^>]*href="(/archives/(\d+)/)"[^>]*>\s*<div[^>]*>.*?z-image-loader-url="([^"]+)"[^>]*alt="([^"]*)"',
    re.S)
# \u641c\u7d22\u7ed3\u679c\u6761\u76ee: <li class="tag-item"><a href="/archives/{id}/">\u6807\u9898</a>
_RE_SEARCH = re.compile(r'<a[^>]*href="(/archives/(\d+)/)"[^>]*>([^<]{2,80})</a>')
# \u64ad\u653e config JSON\uff08\u5355\u5f15\u53f7\u5305\u88f9\uff09
_RE_CONFIG = re.compile(r"config='(\{.*?\})'", re.S)
# \u5206\u7c7b\u5bfc\u822a: <a class="slider-item ..." href="/{slug}/"><div class="span">\u540d\u79f0</div>
_RE_NAV = re.compile(r'href="(/[a-z0-9\-]{2,10}/)"[^>]*>\s*<div class="span">([^<]{2,12})</div>')


# \u2500\u2500 \u81ea\u8bca\u65ad\uff08\u4e34\u65f6\u6392\u969c\u7528\uff0c2026-09-11\uff09\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# \u76ee\u7684\uff1aApp \u7aef\u53d6\u4e0d\u5230\u65e5\u5fd7\uff0c\u628a\u300c\u53d6\u57df\u5168\u8fc7\u7a0b\u300d\u76f4\u63a5\u644a\u6210 App \u91cc\u80fd\u770b\u89c1\u7684\u6587\u5b57\u3002
# \u8bbe\u8ba1\uff1a\u5b8c\u5168\u81ea\u5305\u542b\u2014\u2014\u6700\u9700\u8981\u6392\u67e5\u7684\u573a\u666f\u6070\u6070\u662f\u300c\u540c\u7ea7\u6a21\u5757 hostresolver/explorer \u6ca1\u52a0\u8f7d\u5230\u300d\uff0c
#      \u6240\u4ee5\u672c\u51fd\u6570\u4e0d\u4f9d\u8d56\u5b83\u4eec\uff0cimport \u5931\u8d25\u4e5f\u7167\u6837\u8f93\u51fa\u3002
DIAG_TID = '__diag__'


def _diag_lines(sp, key=''):
    """\u628a\u53d6\u57df\u94fe\u8def\u644a\u6210\u53ef\u8bfb\u6587\u672c\u884c\uff08\u5728\u300c\u26a0\u8bca\u65ad\u300d\u5206\u7c7b\u91cc\u9010\u6761\u663e\u793a\uff09"""
    out = []
    g = globals()

    def add(k, v):
        out.append('%s: %s' % (k, v))

    add('\u6700\u7ec8\u9009\u5b9a host', getattr(sp, 'host', '') or '(\u7a7a\u2605\u5730\u5740\u6ca1\u89e3\u6790\u51fa\u6765)')
    add('hostresolver \u6a21\u5757', '\u5df2\u52a0\u8f7d' if g.get('resolve_host') else '\u2605\u672a\u52a0\u8f7d(\u540c\u7ea7\u6a21\u5757\u6ca1\u8fdb\u8bbe\u5907)')
    add('explorer \u6a21\u5757', '\u5df2\u52a0\u8f7d' if g.get('explore_hosts') else '\u672a\u52a0\u8f7d')
    ext = getattr(sp, '_ext', {}) or {}
    add('ext.publish', ext.get('publish') or '(\u7a7a\uff0c\u7528\u5185\u7f6e)')
    add('ext.hosts', ','.join(ext.get('hosts') or []) or '(\u7a7a)')
    if not key:
        try:
            key = sp.getName()
        except Exception:
            key = ''
    add('\u672c\u6587\u4ef6\u58f0\u660e\u7684\u7ad9\u540d', key or '(\u672a\u77e5)')
    _rq = g.get('requests') or g.get('rq')
    u = getattr(sp, 'host', '') or ''
    if u and _rq is not None:
        hh = dict(getattr(sp, 'headers', None) or {})
        if not hh.get('User-Agent'):
            hh['User-Agent'] = g.get('_UA') or g.get('UA') or 'Mozilla/5.0'
        try:
            r = _rq.get(u.rstrip('/') + '/', headers=hh,
                        proxies=getattr(sp, 'proxies', {}) or {}, timeout=6, verify=False)
            t = r.text or ''
            add('\u5b9e\u6d4b\u8be5 host', 'HTTP %s / %dB / \u542b\u7ad9\u540d:%s'
                % (r.status_code, len(t), ('\u662f' if key in t else '\u5426\u2605') if key else '\u672a\u5224\u5b9a'))
        except Exception as e:
            add('\u5b9e\u6d4b\u8be5 host', '\u2605\u8fde\u4e0d\u4e0a: %s' % str(e)[:60])
    else:
        add('\u5b9e\u6d4b\u8be5 host', '(\u8df3\u8fc7\uff1ahost \u4e3a\u7a7a\u6216 requests \u4e0d\u53ef\u7528)')
    try:
        import hostresolver as _hr
        tr = _hr.last_trace()
        if tr:
            out.append('\u2500\u2500 \u9009\u7ad9\u8fc7\u7a0b \u2500\u2500')
            out += tr[:30]
    except Exception as e:
        out.append('\u2605 \u8bfb\u9009\u7ad9\u8fc7\u7a0b\u5931\u8d25: %s' % str(e)[:60])
    return out


class Spider(BaseSpider):

    # \u7ad9\u65b9\u53d1\u5e03\u9875
    PUBLISH_PAGE = 'https://hlwf6.com/'
    # \u5185\u7f6e\u5019\u9009\uff082026-09-08 \u53d1\u5e03\u9875\u5b9e\u6d4b\uff1a\u53d1\u5e03\u9875 5 \u6761\u7ebf\u8def\u4e2d\u4ec5 3 \u6761\u662f\u771f\u7ad9\u955c\u50cf\uff0c
    # rkrnimmm=18se\u5bfc\u822a\u5e7f\u544a\u7ad9\u3001bxouulcs=68\u5b57\u8282\u7a7a\u58f3\uff0c\u5df2\u5254\u9664\uff1b\u4ee5"\u6807\u9898\u542b\u9ed1\u6599\u7f51"\u9a8c\u8eab\uff09
    BUILTIN_HOSTS = [
        'https://fzyxd.vhksymsv.cc',
        'https://d3oyu.zbzrembr.cc',
        'https://ds6r63epm75a1.cloudfront.net',
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
        try:
            self._diag = _diag_lines(self, '\u9ed1\u6599\u7f51')
        except Exception:
            self._diag = []
        self.headers.update({'Origin': self.host, 'Referer': self.host + '/'})
        print(f'使用站点: {self.host}')

    def getName(self):
        return "\u9ed1\u6599\u7f51"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def get_working_host(self):
        publish = self._ext.get('publish') or self.PUBLISH_PAGE
        builtin = self.BUILTIN_HOSTS

        # \u8eab\u4efd\u6821\u9a8c\uff1a\u53d1\u5e03\u9875\u6df7\u6709\u5e7f\u544a\u95e8\u7ad9\uff08\u5982 18se\u5bfc\u822a\uff09\uff0c\u6807\u9898/\u6b63\u6587\u4e0d\u542b\u7ad9\u540d\u7684\u4e0d\u7b97\u771f\u7ad9
        def _validate(host, text):
            return '\u9ed1\u6599\u7f51' in (text or '')

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
        # \u515c\u5e95\uff1aext/\u5185\u7f6e\u5019\u9009**\u5e76\u884c**\u5b9e\u6d4b\uff08\u539f\u4e3a 5\u00d78s \u4e32\u884c\uff0c\u662f\u300c\u8f6c\u5708\u5f88\u4e45\u300d\u7684\u76f4\u63a5\u6765\u6e90\uff09
        cands = list(self._ext.get('hosts') or []) + builtin
        if probe_first:
            try:
                h = probe_first(cands, headers=self.headers, proxies=self.proxies,
                                timeout=8, validate=_validate, tag='\u515c\u5e95')
                if h:
                    return h
            except Exception:
                pass
        else:
            for h in cands:
                try:
                    r = requests.get(h.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=8, verify=False)
                    # \u8eab\u4efd\u6821\u9a8c\uff1a\u53d1\u5e03\u9875\u6df7\u6709\u5e7f\u544a\u95e8\u7ad9\uff08\u5982 18se\u5bfc\u822a\uff09\uff0c\u6807\u9898\u4e0d\u542b\u7ad9\u540d\u7684\u4e0d\u7b97
                    if r.status_code == 200 and '\u9ed1\u6599\u7f51' in (r.text or ''):
                        return h.rstrip('/')
                except Exception:
                    continue
        # \u7ec8\u6781\u515c\u5e95\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\uff08\u8df3\u8f6c\u58f3/\u95e8\u6237/\u6cdb\u89e3\u6790\u8ddf\u968f + \u7ad9\u540d\u8eab\u4efd\u9a8c\u8bc1\uff09
        if explore_hosts:
            try:
                def _probe(u):
                    r = requests.get(u.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=8, verify=False)
                    t = r.text or ''
                    # \u52a0\u5bc6\u5c01\u9762\u4e3b\u9898\u7279\u5f81 + \u7ad9\u540d\u53cc\u6761\u4ef6\uff08\u9632\u300c818\u9ed1\u6599\u7f51\u300d\u7b49\u540c\u540d\u7ad9\u6df7\u5165\uff09
                    return r.status_code == 200 and '\u9ed1\u6599\u7f51' in t and 'z-image-loader-url' in t
                hs = explore_hosts(['hlw', '\u9ed1\u6599\u7f51'], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        # \u5168\u8d25\uff1a\u663e\u5f0f\u8fd4\u56de\u7a7a\uff08\u63a5\u53e3\u5c42\u79d2\u7a7a\uff0c\u4e0d\u518d\u56de\u9000\u6b7b\u57df\u9759\u9ed8\u7a7a\u8f6c\uff09
        return ''

    def _should_pic(self, url):
        """\u52a0\u5bc6\u56fe\u5e8a\u5224\u5b9a\uff1apic.* \u57df\u540d + \u5df2\u77e5\u52a0\u5bc6\u8def\u5f84\u524d\u7f00\u3002"""
        u = (url or '').lower()
        host = u.split('/')[2] if u.startswith('http') and u.count('/') > 2 else ''
        return any(x in u for x in ['pic.hdhwqx.cn', '/upload_01/', '/hc237/']) or host.startswith('pic.')

    def e64(self, s):
        try:
            return base64.b64encode((s or '').encode()).decode()
        except Exception:
            return ''

    def d64(self, s):
        try:
            return base64.b64decode((s or '').encode()).decode()
        except Exception:
            return ''

    def _pic(self, u):
        """\u52a0\u5bc6\u56fe\u5e8a\u5c01\u9762\u7edf\u4e00\u8d70\u4ee3\u7406\uff1b\u5176\u4f59\u76f4\u8fde\u3002"""
        u = _html.unescape(u or '').strip()
        if not u:
            return ''
        if self._should_pic(u):
            return f'{self.getProxyUrl()}&url={self.e64(u)}&type=hlwimg'
        return u

    def _get(self, path):
        url = path if path.startswith('http') else self.host + path
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False)

    def _parse_cards(self, html_text):
        out = []
        seen = set()
        for m in _RE_CARD.finditer(html_text):
            vid = m.group(2)
            if vid in seen:
                continue
            seen.add(vid)
            out.append({
                'vod_id': vid,
                'vod_name': _html.unescape(m.group(4)).strip() or vid,
                'vod_pic': self._pic(m.group(3)),
                'vod_remarks': '',
            })
        return out

    def _diag_items(self):
        """\u8bca\u65ad\u884c \u2192 App \u5217\u8868\u6761\u76ee\uff08\u70b9\u300c\u26a0\u8bca\u65ad\u300d\u5206\u7c7b\u5373\u53ef\u770b\u5230\u5168\u90e8\u53d6\u57df\u8fc7\u7a0b\uff09"""
        return [{'vod_id': 'diag%d' % i, 'vod_name': '\u26a0 ' + str(x),
                 'vod_pic': '', 'vod_remarks': ''}
                for i, x in enumerate(getattr(self, '_diag', []) or [])]
    def homeContent(self, *a, **kw):
        """\u5916\u5c42\u5305\u88c5\uff1a\u539f\u5b9e\u73b0\u7ed3\u679c + \u8ffd\u52a0\u300c\u26a0\u8bca\u65ad\u300d\u5206\u7c7b\uff08\u4e34\u65f6\u6392\u969c\uff0c\u5b9a\u4f4d App \u7aef\u65e0\u5185\u5bb9\u6839\u56e0\uff09"""
        try:
            r = self._homeContent(*a, **kw)
        except Exception:
            r = {}
        try:
            if isinstance(r, dict):
                r['class'] = list(r.get('class') or []) + \
                    [{'type_id': DIAG_TID, 'type_name': '\u26a0\u8bca\u65ad'}]
        except Exception:
            pass
        return r

    def _homeContent(self, flag):

        result = {'class': [], 'list': []}
        try:
            body = self._get('/').text or ''
        except Exception:
            return result
        seen = set()
        for m in _RE_NAV.finditer(body):
            slug, name = m.group(1).strip('/'), _html.unescape(m.group(2)).strip()
            if slug in seen or not name:
                continue
            seen.add(slug)
            result['class'].append({'type_id': slug, 'type_name': name})
        result['list'] = self._parse_cards(body)
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        if tid == DIAG_TID:
            items = self._diag_items()
            return {'page': 1, 'pagecount': 1, 'limit': len(items),
                    'total': len(items), 'list': items}
        result = {'list': []}
        path = f'/{tid}/page/{pg}/' if str(pg) not in ('1', '') else f'/{tid}/'
        try:
            result['list'] = self._parse_cards(self._get(path).text or '')
        except Exception:
            pass
        return result

    def searchContent(self, key, quick, pg='1'):
        result = {'list': []}
        try:
            body = self._get(f'/index/search?search_term_string={quote(key)}').text or ''
            seen = set()
            for m in _RE_SEARCH.finditer(body):
                vid = m.group(2)
                if vid in seen:
                    continue
                seen.add(vid)
                result['list'].append({
                    'vod_id': vid,
                    'vod_name': _html.unescape(m.group(3)).strip(),
                    'vod_pic': '',
                    'vod_remarks': '',
                })
        except Exception:
            pass
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    @staticmethod
    def _videos(html_text):
        """\u4ece\u8be6\u60c5\u9875\u63d0\u53d6\u5168\u90e8\u89c6\u9891 config \u2192 [{url,pic}...]"""
        vids = []
        for m in _RE_CONFIG.finditer(html_text):
            try:
                cfg = json.loads(m.group(1).replace('\\/', '/'))
                v = cfg.get('video') or {}
                url = str(v.get('url') or '').strip()
                if url:
                    vids.append({'url': url, 'pic': str(v.get('pic') or '').strip()})
            except Exception:
                continue
        return vids

    def detailContent(self, ids):
        result = {'list': []}
        try:
            vid = str(ids[0])
            body = self._get(f'/archives/{vid}/').text or ''
            title = ''
            m = re.search(r'<title>([^<]+)</title>', body)
            if m:
                title = _html.unescape(m.group(1)).strip()
                title = re.sub('-\u9ed1\u6599\u7f51\\s*$', '', title).strip()
            pic = ''
            mi = re.search(r'z-image-loader-url="([^"]+)"', body)
            if mi:
                pic = self._pic(mi.group(1))
            vids = self._videos(body)
            if vids:
                play = '#'.join(f'第{i + 1}集${vid}-{i}' for i in range(len(vids)))
            else:
                play = f'第1集${vid}-0'
            result['list'].append({
                'vod_id': vid,
                'vod_name': title or vid,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': '',
                'vod_director': '',
                'vod_content': '',
                'vod_play_from': 'hlw',
                'vod_play_url': play,
            })
        except Exception:
            pass
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {'parse': 0, 'playUrl': '', 'url': '', 'header': {'User-Agent': _UA}}
        try:
            vid, idx = (str(id).split('-') + ['0'])[:2]
            body = self._get(f'/archives/{vid}/').text or ''
            vids = self._videos(body)
            i = int(idx) if idx.isdigit() else 0
            if vids:
                result['url'] = vids[min(i, len(vids) - 1)]['url']
                result['header'] = {'User-Agent': _UA, 'Referer': self.host + '/'}
        except Exception:
            pass
        return result

    def localProxy(self, param):
        try:
            if param.get('type') == 'hlwimg':
                url = self.d64(param.get('url'))
                if url.startswith('//'):
                    url = 'https:' + url
                elif url.startswith('/'):
                    url = self.host + url
                return _img_fetch(url, self.host + '/')
        except Exception as e:
            print(f'[ERROR] localProxy: {e}')
        return [404, 'text/plain', b'']
