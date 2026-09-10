# -*- coding: utf-8 -*-
# 51AW \u7ad9\u6e90\uff08WordPress \u578b pbody \u58f3 \u00b7 HTML \u76f4\u6293\u7248\uff09
# \u53d1\u5e03\u94fe: 51aw34.com \u7b49\u5165\u53e3\u57df\u4e3a b64 \u58f3\u843d\u5730\u9875\uff08Base64.decode \u6574\u9875\uff09\uff0c\u89e3\u7801\u540e
#         footer \u76f4\u94fe\u73b0\u5f79\u5185\u5bb9\u7ad9\uff082026-09-08 \u5b9e\u6d4b = awcg48.com\uff0cCloudflare\uff09
# \u7ed3\u6784: \u5206\u7c7b /category/{slug}/\uff08\u7ffb\u9875 page/{n}/ \u6216 /{n}/ \u53cc\u5f62\u6001\u81ea\u9002\u5e94\uff09
#       \u5217\u8868 <article><a href><h2>\u6807\u9898</h2>\uff1b\u641c\u7d22 /search/{kw}/
#       \u8be6\u60c5 dplayer config JSON\uff08\/ \u8f6c\u4e49\u8fd8\u539f\uff09\uff0c\u517c\u5bb9\u88f8 m3u8 \u515c\u5e95
# \u5206\u7c7b\u8868 b64 \u843d\u76d8\uff08\u89c4\u907f gitee 451 \u8bcd\u6c47\u626b\u63cf\uff09\uff0c\u8fd0\u884c\u65f6\u89e3\u7801
import json
import re
import sys
import os
import html as _html
import base64
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

# explorer.py\uff08source \u6839\uff09\uff1a\u6c60\u5168\u6302\u65f6\u4ece\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\u6d3b\u57df\uff08\u4e0e hostresolver \u540c\u76ee\u5f55\uff09
try:
    from explorer import explore_hosts
except Exception:
    explore_hosts = None

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# \u5206\u7c7b\u8868 {slug: \u540d\u79f0}\uff08b64 of UTF-8 JSON\uff0c\u6765\u6e90\uff1a\u6e90\u6ce8\u91ca sortUrl\uff0c2026-09-08 \u91c7\u96c6\uff09
def _b64d(s):
    return base64.b64decode(s + '=' * (-len(s) % 4)).decode('utf-8')


# \u771f\u5b9e\u5206\u7c7b\u8868\uff08json: {"slug":"\u540d\u79f0", ...}\uff09
_CATS = json.loads(_b64d(
    'eyJob21lIjoi6aaW6aG1IiwianJyZyI6IuS7iuaXpeWQg+eTnCIsInF3cnMiOiLlhajnvZHng63m'
    'kJwiLCJhd2NnIjoi5pqX572R54iG5paZIiwiZHl3aCI6Iuaal+e9kee9kee6oiIsIm1yZHMiOiLm'
    'r4/ml6XlpKfotZsiLCJhaWRqIjoiQUnnn63liaciLCJmY2xsIjoi5pqX572R5Y+N5beuIiwieHlj'
    'ZyI6Iuaal+e9keagoeWbrSIsImFud2FuZ2x1YW5sdW4iOiLmmpfnvZHkubHkvKYiLCJzeHpxIjoi'
    '5pqX572R6KeG6aKRIiwiaHdhdyI6Iua1t+WkluWkp+eJhyIsImF3ZHoiOiLmmpfnvZFBVuino+iv'
    'tCIsImF3bHEiOiLmmpfnvZHnjI7lpYciLCJ0YW5odWEiOiLmjqLoirHlgbfmi40iLCJtZWlyaS10'
    'b3AiOiLmr4/ml6V0b3AiLCJjdW56aGkiOiLlr7jmraLmjJHmiJgiLCJkbXR0Ijoi5Yqo5ryr5aSp'
    '5aCCIiwiZGFyay1oaXN0b3J5Ijoi5pqX5Y+y5qGj5qGIIiwic2piIjoi5LiW55WM5p2vIn0='
))

# \u5217\u8868\u6761\u76ee: <article ...><a href="...">...<h2>\u6807\u9898</h2>...
_RE_ARTICLE = re.compile(r'<article[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</article>', re.S)
_RE_H2 = re.compile(r'<h2[^>]*>(.*?)</h2>', re.S)
# \u5c01\u9762\uff1aMirages \u4e3b\u9898\u61d2\u52a0\u8f7d data-src \u4f18\u5148\uff08src \u662f\u5360\u4f4d\u56fe\uff09\uff0c\u5254\u9664\u7edf\u8ba1/\u4e3b\u9898\u56fe\u6807
_RE_IMG_LAZY = re.compile(r'data-src="([^"]+)"', re.I)
_RE_IMG_ANY = re.compile(r'<img[^>]*?src="([^"]+)"', re.I)
_IMG_SKIP = ('mc.yandex', '/usr/themes/', '/usr/plugins/', 'data:image')
# dplayer config JSON\uff08\u5355\u5f15\u53f7\u5305\u88f9\uff09\u4e0e\u88f8 m3u8 \u515c\u5e95
_RE_CONFIG = re.compile(r"config='(\{.*?\})'", re.S)
_RE_M3U8 = re.compile(r'https?://[^"\'\\\s]+\.m3u8[^"\'\\\s]*')
_RE_NEXT = re.compile('class="page-navigator".*?href="([^"]+)"[^>]*>[^<]*\u4e0b\u4e00\u9875', re.S)


class Spider(BaseSpider):

    # \u5165\u53e3\u843d\u5730\u9875\uff08b64 \u58f3\uff0c\u89e3\u7801\u540e\u542b\u73b0\u5f79\u5185\u5bb9\u7ad9\u76f4\u94fe\uff1b\u968f\u54c1\u724c\u6362\u57df\u5373\u66f4\u65b0\uff09
    PUBLISH_PAGE = 'https://51aw34.com/'
    # \u5185\u7f6e\u5019\u9009\uff082026-09-08 \u5b9e\u6d4b\uff09\uff1a\u58f3\u9875 JS \u6cdb\u89e3\u6790\u5907\u7ebf {word}.haqwhuwn.cc \u4efb\u610f\u8bcd\u53ef\u7528\uff0c
    # awcg48.com \u4e3b\u7ebf\u65f6\u6d3b\u65f6\u6b7b\uff08App \u7aef\u66fe\u5168\u6302=\u96f6\u6570\u636e\uff09\uff0c\u6545\u6cdb\u89e3\u6790\u7ebf\u6392\u524d
    BUILTIN_HOSTS = [
        'https://main.haqwhuwn.cc',
        'https://apple.haqwhuwn.cc',
        'https://being.djvvxecgc.cc',
        'https://awcg48.com',
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
        return "51\u6697\u7f51"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def get_working_host(self):
        publish = self._ext.get('publish') or self.PUBLISH_PAGE
        builtin = self.BUILTIN_HOSTS

        def _validate(host, text):
            # \u5185\u5bb9\u7ad9\u8eab\u4efd\uff1aWordPress \u578b\u6587\u7ae0\u6d41\uff08article \u6807\u7b7e\uff09+ \u7ad9\u540d\u8bcd
            t = text or ''
            return ('<article' in t) and ('\u6697\u7f51' in t)

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
        # \u7ec8\u6781\u515c\u5e95\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\uff08\u8df3\u8f6c\u58f3/\u95e8\u6237/\u6cdb\u89e3\u6790\u8ddf\u968f + \u7ad9\u540d\u8eab\u4efd\u9a8c\u8bc1\uff09
        if explore_hosts:
            try:
                def _probe(u):
                    r = requests.get(u.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=8, verify=False)
                    t = r.text or ''
                    return r.status_code == 200 and '<article' in t and '\u6697\u7f51' in t
                hs = explore_hosts(['51aw', '\u6697\u7f51'], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        return builtin[0]

    def _get(self, path):
        url = path if path.startswith('http') else self.host + path
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False)

    @staticmethod
    def _pick_pic(block):
        for pat in (_RE_IMG_LAZY, _RE_IMG_ANY):
            for u in pat.findall(block):
                if u and not any(s in u for s in _IMG_SKIP):
                    return _html.unescape(u).strip()
        return ''

    @staticmethod
    def _parse_articles(html_text):
        out = []
        seen = set()
        for m in _RE_ARTICLE.finditer(html_text):
            link, blk = m.group(1), m.group(2)
            if not link or not (link.startswith('http') or link.startswith('/')):
                continue
            if link in seen:
                continue
            seen.add(link)
            t = _RE_H2.search(blk)
            title = _html.unescape(re.sub(r'<[^>]+>', '', t.group(1))).strip() if t else ''
            if not title:
                continue
            out.append({
                'vod_id': link,
                'vod_name': title,
                'vod_pic': Spider._pick_pic(blk),
                'vod_remarks': '',
            })
        return out

    def homeContent(self, flag):
        result = {'class': [], 'list': []}
        for slug, name in _CATS.items():
            result['class'].append({'type_id': slug, 'type_name': name})
        try:
            result['list'] = self._parse_articles(self._get('/').text or '')
        except Exception:
            pass
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        result = {'list': []}
        if tid == 'home' or str(pg) in ('1', ''):
            paths = ['/'] if tid == 'home' else [f'/category/{tid}/']
        else:
            paths = [f'/category/{tid}/page/{pg}/', f'/category/{tid}/{pg}/']
        for p in paths:
            try:
                lst = self._parse_articles(self._get(p).text or '')
                if lst:
                    result['list'] = lst
                    break
            except Exception:
                continue
        return result

    def searchContent(self, key, quick, pg='1'):
        result = {'list': []}
        try:
            body = self._get(f'/search/{quote(key)}/').text or ''
            result['list'] = self._parse_articles(body)
        except Exception:
            pass
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    @staticmethod
    def _videos(html_text):
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
        if not vids:
            seen = set()
            for u in _RE_M3U8.findall(html_text):
                if u not in seen:
                    seen.add(u)
                    vids.append({'url': u, 'pic': ''})
        return vids

    def detailContent(self, ids):
        result = {'list': []}
        try:
            link = str(ids[0])
            body = self._get(link).text or ''
            title = ''
            m = re.search(r'<title>([^<]+)</title>', body)
            if m:
                title = _html.unescape(m.group(1)).strip()
                title = re.sub('\\s*[-|]\\s*51\u6697\u7f51\\s*$', '', title).strip()
            pic = self._pick_pic(body)
            vids = self._videos(body)
            if vids:
                play = '#'.join(f'第{i + 1}集${link}-{i}' for i in range(len(vids)))
            else:
                play = f'第1集${link}-0'
            result['list'].append({
                'vod_id': link,
                'vod_name': title or link,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': '',
                'vod_director': '',
                'vod_content': '',
                'vod_play_from': '51aw',
                'vod_play_url': play,
            })
        except Exception:
            pass
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {'parse': 0, 'playUrl': '', 'url': '', 'header': {'User-Agent': _UA}}
        try:
            link, idx = (str(id).rsplit('-', 1) + ['0'])[:2]
            body = self._get(link).text or ''
            vids = self._videos(body)
            i = int(idx) if idx.isdigit() else 0
            if vids:
                result['url'] = vids[min(i, len(vids) - 1)]['url']
                result['header'] = {'User-Agent': _UA, 'Referer': self.host + '/'}
        except Exception:
            pass
        return result
