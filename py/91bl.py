# -*- coding: utf-8 -*-
# 91BL 站源（Typecho + Mirages 主题 · HTML 直抓版）
# 发布页: t91bl.com（b64 壳中转落地页，解码后 zz_line 列泛解析基域线路）
# 线路: {word}.quibepqh.cc / {word}.matutgbj.cc（泛解析任意词可用）+ cloudfront 兜底
#       （91bla1.com 主线域名本机实测 000，线路表以泛解析为主）
# 结构: 分类 /category/{slug}/ 翻页 /category/{slug}/{n}/；搜索 /search/{kw}/
#       列表条目 <article> 内 <a href="/archives/{id}/"> + 封面 img z-image-loader-url + alt 标题
#       详情播放 dplayer data-config='{...}' JSON（\/ 转义还原），多视频=多 dplayer
# 封面图床 pic.hdhwqx.cn 为 CDN 级 AES 加密图，须走 localProxy 解密
# 分类名不落盘明文（b64 兜底表），实时分类从 nav 获取
import json
import re
import sys
import os
import html as _html
import time
import base64
from collections import OrderedDict
from urllib.parse import quote

import requests
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

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# ---- 封面代理（imgfetch 纪律：Session keep-alive + LRU + magic 预检 + 解密兜底）----
_img_session = requests.Session()
_img_session.verify = False
try:
    from requests.adapters import HTTPAdapter
    _ad = HTTPAdapter(pool_connections=4, pool_maxsize=12)
    _img_session.mount('https://', _ad)
    _img_session.mount('http://', _ad)
except Exception:
    pass
_img_cache = OrderedDict()
_IMG_CACHE_MAX = 60


def _img_fetch(url, referer):
    """取图+按需解密+缓存，返回 [status, content_type, bytes]。"""
    if url in _img_cache:
        _img_cache.move_to_end(url)
        return _img_cache[url]
    try:
        r = _img_session.get(url, headers={'User-Agent': _UA, 'Referer': referer}, timeout=10)
        if r.status_code != 200:
            return [404, 'text/plain', b'']
        raw = r.content
        ct = 'image/jpeg'
        if raw[:3] == b'\xff\xd8\xff':
            b = raw                                   # JPEG 直传免解密
        elif raw[:8] == b'\x89PNG\r\n\x1a\n':
            b, ct = raw, 'image/png'
        elif raw[:4] == b'GIF8':
            b, ct = raw, 'image/gif'
        else:                                         # CDN 级 AES 加密图（黑料系同 key）
            from Crypto.Cipher import AES
            b = AES.new(b'f5d965df75336270', AES.MODE_CBC, b'97b60394abc2fbe1').decrypt(raw)
            if b[:8] == b'\x89PNG\r\n\x1a\n':
                ct = 'image/png'
            elif b[:4] == b'GIF8':
                ct = 'image/gif'
        if b:
            _img_cache[url] = [200, ct, b]
            if len(_img_cache) > _IMG_CACHE_MAX:
                _img_cache.popitem(last=False)
            return [200, ct, b]
        return [404, 'text/plain', b'']
    except Exception:
        return [404, 'text/plain', b'']


# 分类兜底表 {slug: 名称}（b64 of UTF-8 JSON，2026-09-08 首页 nav 实时采集）
def _b64d(s):
    return base64.b64decode(s + '=' * (-len(s) % 4)).decode('utf-8')


_CATS = json.loads(_b64d(
    'eyJqcmNnMSI6IuS7iuaXpeWQg+eTnCIsIm1yZHMiOiLmr4/ml6XlpKfotZsiLCJhaWR1YW5qdSI6'
    'IkFJ55+t5YmnIiwibGxqayI6IuiQneiOiWprIiwieWxneCI6Iue9kem7hOi1hOa6kCIsInJnangi'
    'OiLng63pl6jlpKfnk5wiLCJsbHpxIjoi5rW36KeS5Lym55CGIiwiZmNzaiI6IuWPjeW3rueIhuaW'
    'mSIsInN0enpiIjoic3Tnq5nnm7Tmkq3lm57mlL4iLCJ4eXJnIjoi5qCh5Zut54iG5paZIiwibHB6'
    'cSI6IuaOouiKseWBt+aLjSIsImdjcXMiOiJBVuWKqOa8qyIsInF3ZnEiOiLlhajnvZHnlq/msYIi'
    'LCJ3aGJnIjoi5piO5pif54iG5paZIiwicXd5cyI6IuWlh+mXu+W8guS6iyIsInR5Y2ciOiLkvZPo'
    'grLnm7Tmkq0ifQ=='
))

# 列表条目（<article> 块内: /archives/{id}/ 链接 + z-image-loader-url 封面 + alt 标题）
_RE_ITEM = re.compile(r'<article[^>]*>(.*?)</article>', re.S)
_RE_LINK = re.compile(r'href="((?:https?://[^"]*?)?/archives/(\d+)/)"')
_RE_COVER = re.compile(r'z-image-loader-url="([^"]+)"', re.I)
_RE_TITLE = re.compile(r'alt="([^"]*)"')
# 分类 nav: <a href="/category/{slug}/">名称</a>
_RE_NAV = re.compile(r'href="(/category/[a-z0-9]+/)"[^>]*>([^<]{2,14})<')
# 详情播放: dplayer data-config='{...}'（旧版 config= 兼容）
_RE_CONFIG = re.compile(r"data-config='(\{.*?\})'|config='(\{.*?\})'", re.S)
_RE_VIDURL = re.compile(r'"url"\s*:\s*"([^"]+)"')
_RE_NEXT = re.compile(r'class="next"[^>]*><a href="([^"]+)"')
_AD_CAT_RE = re.compile(r'(?i)app|下载|qq|微信|推特|tg群|导航|联系|合作|邮箱|关于|存档|收藏|登陆|登录')


class Spider(BaseSpider):

    # 站方中转发布页（b64 壳，解码后 JS zz_line 列线路基域）
    PUBLISH_PAGE = 'https://t91bl.com/'
    # 内置候选（2026-09-08 实测 200/204KB，泛解析任意词子域可用）
    BUILTIN_HOSTS = [
        'https://main.quibepqh.cc',
        'https://apple.quibepqh.cc',
        'https://main.matutgbj.cc',
        'https://apple.matutgbj.cc',
        'https://dle7ftqaeg81q.cloudfront.net',
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
        return "91爆料"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def e64(self, s):
        try:
            return base64.b64encode((s or '').encode('utf-8')).decode('utf-8')
        except Exception:
            return ''

    def d64(self, s):
        try:
            return base64.b64decode((s or '').encode('utf-8')).decode('utf-8')
        except Exception:
            return ''

    def localProxy(self, param):
        try:
            if param.get('type') == 'blimg':
                url = self.d64(param.get('url'))
                if url.startswith('//'):
                    url = 'https:' + url
                elif url.startswith('/'):
                    url = self.host + url
                return _img_fetch(url, self.host + '/')
        except Exception:
            pass
        return [404, 'text/plain', b'']

    def _pic(self, u):
        """封面统一走代理（图床为加密图，代理内 magic 预检+解密+缓存）。"""
        if not u:
            return ''
        return f'{self.getProxyUrl()}&url={self.e64(u)}&type=blimg'

    def get_working_host(self):
        publish = self._ext.get('publish') or self.PUBLISH_PAGE
        builtin = self.BUILTIN_HOSTS

        def _validate(host, text):
            return '91爆料' in (text or '')

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
        url = path if path.startswith('http') else self.host + path
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False, allow_redirects=True)

    def _parse_list(self, html_text):
        out = []
        seen = set()
        for m in _RE_ITEM.finditer(html_text or ''):
            blk = m.group(1)
            ml = _RE_LINK.search(blk)
            if not ml:
                continue
            link, aid = ml.group(1), ml.group(2)
            if aid in seen:
                continue
            seen.add(aid)
            mt = _RE_TITLE.search(blk)
            title = _html.unescape(mt.group(1)).strip() if mt else ''
            if not title:
                continue
            pic = ''
            mu = _RE_COVER.search(blk)
            if mu:
                pic = _html.unescape(mu.group(1)).strip()
            out.append({
                'vod_id': link,
                'vod_name': title,
                'vod_pic': self._pic(pic),
                'vod_remarks': '',
            })
        return out

    def homeContent(self, flag):
        result = {'class': [], 'list': []}
        body = ''
        try:
            body = self._get('/').text or ''
        except Exception:
            pass
        seen = set()
        for m in _RE_NAV.finditer(body):
            path, name = m.group(1), _html.unescape(m.group(2)).strip()
            slug = path.split('/')[2]
            if slug in seen or not name or _AD_CAT_RE.search(name):
                continue
            seen.add(slug)
            result['class'].append({'type_id': slug, 'type_name': name})
        if not result['class']:
            result['class'] = [{'type_id': k, 'type_name': v} for k, v in _CATS.items()]
        try:
            result['list'] = self._parse_list(body)
        except Exception:
            pass
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        result = {'list': []}
        path = f'/category/{tid}/'
        if str(pg) not in ('1', ''):
            path = f'/category/{tid}/{pg}/'
        try:
            result['list'] = self._parse_list(self._get(path).text or '')
        except Exception:
            pass
        return result

    def searchContent(self, key, quick, pg='1'):
        result = {'list': []}
        try:
            path = f'/search/{quote(key)}/'
            if str(pg) not in ('1', ''):
                path = f'/search/{quote(key)}/page/{pg}/'
            result['list'] = self._parse_list(self._get(path).text or '')
        except Exception:
            pass
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    @staticmethod
    def _videos(html_text):
        """按 dplayer data-config 抽分集（贴片广告素材不在 dplayer 内，天然排除）。
        url = 站内票据端点 /action/player/get_play_url?cid=..&idx=..（播放时两步取真 m3u8）。"""
        vids = []
        for m in _RE_CONFIG.finditer(html_text or ''):
            c = m.group(1) or m.group(2)
            if not c:
                continue
            try:
                s = c.replace('&quot;', '"').replace('&#34;', '"').replace('&amp;', '&')
                cfg = json.loads(s)
                mv = cfg.get('video') or {}
                # 91爆料为 ArtPlayer 扁平结构（url/poster 顶层）；兼容黑料系 video:{} 嵌套
                u = str(mv.get('url') or cfg.get('url') or '').replace('\\/', '/')
                poster = str(mv.get('poster') or cfg.get('poster') or '').replace('\\/', '/')
            except Exception:
                mv2 = _RE_VIDURL.search(c)
                u = mv2.group(1).replace('\\/', '/') if mv2 else ''
                poster = ''
            if u:
                vids.append({'url': u, 'poster': poster})
        return vids

    def _resolve_play(self, url):
        """两步票据：POST /action/player/ticket 取短期一次性票（120s）→ POST 换签名 m3u8。
        服务端 env 验签宽松（空 env 可过）。"""
        m = re.search(r'cid=(\d+)&idx=(\d+)', url)
        if not m:
            return url
        cid, idx = m.group(1), m.group(2)
        try:
            tk_url = f'{self.host}/action/player/ticket?cid={cid}&idx={idx}&_={int(time.time()*1000)}'
            r1 = requests.post(tk_url, headers=self.headers, proxies=self.proxies, timeout=10, verify=False)
            tr = r1.json()
            if tr.get('status') != 0 or not (tr.get('data') or {}).get('ticket'):
                return ''
            ticket = tr['data']['ticket']
            r2 = requests.post(f'{self.host}/action/player/get_play_url?cid={cid}&idx={idx}',
                               headers=self.headers, proxies=self.proxies, timeout=10, verify=False,
                               data={'ticket': ticket, 'env': '{}', '_ver': 'v0'})
            pr = r2.json()
            if pr.get('status') == 0 and pr.get('data'):
                return pr['data']
        except Exception:
            pass
        return ''

    def detailContent(self, ids):
        result = {'list': []}
        try:
            link = str(ids[0])
            body = self._get(link).text or ''
            title = ''
            m = re.search(r'<title>([^<]+)</title>', body)
            if m:
                title = _html.unescape(m.group(1)).strip()
                title = re.sub(r'\s*-\s*91爆料\s*$', '', title).strip()
            pic = ''
            vids = self._videos(body)
            if vids and vids[0].get('poster'):
                pic = self._pic(vids[0]['poster'])
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
                'vod_play_from': '91bl',
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
                u = vids[min(i, len(vids) - 1)]['url']
                if 'get_play_url' in u:
                    u = self._resolve_play(u)
                if u and not u.startswith('http'):
                    u = self.host + u
                result['url'] = u
                result['header'] = {'User-Agent': _UA, 'Referer': self.host + '/'}
        except Exception:
            pass
        return result
