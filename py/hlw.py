# -*- coding: utf-8 -*-
# HLW 站源（黑料网 · Typecho 风格 HTML 直抓版）
# 发布页: hlwf6.com（"黑料网最新入口-实时更新访问线路"，2026-09-08 实测 200，
#         列 4 个 .cc 泛基域线路 + cloudfront 兜底，基域轮换后发布页即更新）
# 结构: 分类 /{slug}/ 翻页 /{slug}/page/{n}/；详情 /archives/{id}/
#       列表条目 video-item（封面 img 的 z-image-loader-url 属性 + alt 标题）
#       播放 dplayer config='{...}' JSON（\/ 转义须还原），多视频=多 config 块
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
    from hostresolver import resolve_host, parse_ext
except Exception:
    # hostresolver.py 在 source/ 根（py/ 的上级），按脚本自身位置定位，不依赖 cwd
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext
    except Exception:
        resolve_host = None
        parse_ext = None

# explorer.py（source 根）：池全挂时从导航站自动探索活域（与 hostresolver 同目录）
try:
    from explorer import explore_hosts
except Exception:
    explore_hosts = None

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# ── 封面图床：pic.hdhwqx.cn 为 CDN 级 AES 加密图（与黑料不打烊同款 key），
#    App 直接加载是密文=封面全空，统一走 localProxy 取图+按需解密+LRU 缓存
_img_session = requests.Session()
_img_session.verify = False
_img_cache = OrderedDict()
_IMG_CACHE_MAX = 60


def _img_fetch(url, referer):
    """取图+magic 预检+按需解密+缓存，返回 (status, content_type, bytes)。"""
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

# 列表条目: <a class="cursor-pointer" href="/archives/{id}/"> ... z-image-loader-url="封面" alt="标题"
_RE_CARD = re.compile(
    r'<a[^>]*href="(/archives/(\d+)/)"[^>]*>\s*<div[^>]*>.*?z-image-loader-url="([^"]+)"[^>]*alt="([^"]*)"',
    re.S)
# 搜索结果条目: <li class="tag-item"><a href="/archives/{id}/">标题</a>
_RE_SEARCH = re.compile(r'<a[^>]*href="(/archives/(\d+)/)"[^>]*>([^<]{2,80})</a>')
# 播放 config JSON（单引号包裹）
_RE_CONFIG = re.compile(r"config='(\{.*?\})'", re.S)
# 分类导航: <a class="slider-item ..." href="/{slug}/"><div class="span">名称</div>
_RE_NAV = re.compile(r'href="(/[a-z0-9\-]{2,10}/)"[^>]*>\s*<div class="span">([^<]{2,12})</div>')


class Spider(BaseSpider):

    # 站方发布页
    PUBLISH_PAGE = 'https://hlwf6.com/'
    # 内置候选（2026-09-08 发布页实测：发布页 5 条线路中仅 3 条是真站镜像，
    # rkrnimmm=18se导航广告站、bxouulcs=68字节空壳，已剔除；以"标题含黑料网"验身）
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
        self.headers.update({'Origin': self.host, 'Referer': self.host + '/'})
        print(f'使用站点: {self.host}')

    def getName(self):
        return "黑料网"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def get_working_host(self):
        publish = self._ext.get('publish') or self.PUBLISH_PAGE
        builtin = self.BUILTIN_HOSTS

        # 身份校验：发布页混有广告门站（如 18se导航），标题/正文不含站名的不算真站
        def _validate(host, text):
            return '黑料网' in (text or '')

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
                # 身份校验：发布页混有广告门站（如 18se导航），标题不含站名的不算
                if r.status_code == 200 and '黑料网' in (r.text or ''):
                    return h.rstrip('/')
            except Exception:
                continue
        # 终极兜底：导航站自动探索（跳转壳/门户/泛解析跟随 + 站名身份验证）
        if explore_hosts:
            try:
                def _probe(u):
                    r = requests.get(u.rstrip('/') + '/', headers=self.headers,
                                     proxies=self.proxies, timeout=8, verify=False)
                    t = r.text or ''
                    # 加密封面主题特征 + 站名双条件（防「818黑料网」等同名站混入）
                    return r.status_code == 200 and '黑料网' in t and 'z-image-loader-url' in t
                hs = explore_hosts(['hlw', '黑料网'], probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        return builtin[0]

    def _should_pic(self, url):
        """加密图床判定：pic.* 域名 + 已知加密路径前缀。"""
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
        """加密图床封面统一走代理；其余直连。"""
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

    def homeContent(self, flag):
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
        """从详情页提取全部视频 config → [{url,pic}...]"""
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
                title = re.sub(r'-黑料网\s*$', '', title).strip()
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
