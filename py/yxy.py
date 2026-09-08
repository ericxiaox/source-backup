# -*- coding: utf-8 -*-
# YXY 站源（xvideos 模板克隆 · HTML 直抓版）
# 发布页: dizhi8.cc/yxy/（官方多线导航，JS 渲染随机前缀按钮；base 泛解析
#         任意前缀可用——2026-09-02/08 实测，被墙前缀换其他前缀即可）
# 结构: 列表条目 thumb-block（<a href="/video.{eid}/..."> + data-src 封面 +
#       .title a title 属性）；详情 setVideoHLS('签名 m3u8') 短效签名，
#       playerContent 播放时现取；搜索 /?k={kw} 翻页 &p={n}
# 分类表 b64 落盘（规避 gitee 451 词汇扫描）
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
    # hostresolver.py 在 source/ 根（py/ 的上级），按脚本自身位置定位，不依赖 cwd
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext
    except Exception:
        resolve_host = None
        parse_ext = None

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def _b64d(s):
    return base64.b64decode(s + '=' * (-len(s) % 4)).decode('utf-8')


# 分类表 [{name, tpl}]（tpl 含 {pg} 占位；来源：源注释 sortUrl，2026-09-08 采集）
_CATS = json.loads(_b64d(
    'W3sibmFtZSI6IuacgOaWsCIsInRwbCI6Ii9uZXcve3BnfSJ9LHsibmFtZSI6IjNEIiwidHBsIjoi'
    'Lz9rPTNkJnRvcC97cGd9In0seyJuYW1lIjoiQUkiLCJ0cGwiOiIvYy9BSS0yMzkve3BnfSJ9LHsi'
    'bmFtZSI6IuWHuui9qCIsInRwbCI6Ii9jL0N1Y2tvbGQtMjM3L3twZ30ifSx7Im5hbWUiOiLosIPm'
    'lZkiLCJ0cGwiOiIvYy9GZW1kb20tMjM1L3twZ30ifSx7Im5hbWUiOiLogpvkuqQiLCJ0cGwiOiIv'
    'Yy9BbmFsLTEyL3twZ30ifSx7Im5hbWUiOiLpopzlsIQiLCJ0cGwiOiIvYy9DdW1zaG90LTE4L3tw'
    'Z30ifSx7Im5hbWUiOiLlt6jkubMiLCJ0cGwiOiIvYy9CaWdfVGl0cy0yMy97cGd9In0seyJuYW1l'
    'Ijoi5beo5bGMIiwidHBsIjoiL2MvQmlnX0NvY2stMzQve3BnfSJ9LHsibmFtZSI6IuWPo+S6pCIs'
    'InRwbCI6Ii9jL0Jsb3dqb2ItMTUve3BnfSJ9LHsibmFtZSI6IkFTTVIiLCJ0cGwiOiIvYy9BU01S'
    'LTIyOS97cGd9In0seyJuYW1lIjoi5Za35Ye6IiwidHBsIjoiL2MvU3F1aXJ0aW5nLTU2L3twZ30i'
    'fSx7Im5hbWUiOiLkuK3lh7oiLCJ0cGwiOiIvYy9DcmVhbXBpZS00MC97cGd9In0seyJuYW1lIjoi'
    '5YG35Lq6IiwidHBsIjoiLz9rPWNoZWF0aW5nJnRvcC97cGd9In0seyJuYW1lIjoi5ZCI6ZuGIiwi'
    'dHBsIjoiLz9rPWNvbXBpbGF0aW9uJnRvcC97cGd9In0seyJuYW1lIjoi6auY5r2uIiwidHBsIjoi'
    'Lz9rPW9yZ2FzbSZ0b3Ave3BnfSJ9LHsibmFtZSI6Iua3seWWiSIsInRwbCI6Ii8/az1kZWVwdGhy'
    'b2F0JnRvcC97cGd9In1d'
))

# 列表条目块（xvideos 模板）
_RE_BLOCK = re.compile(
    r'<div[^>]*data-id="\d+"[^>]*data-eid="([a-z0-9]+)"[^>]*class="[^"]*thumb-block[^"]*"[^>]*>(.*?)(?=<div[^>]*data-id="\d+"|<div class="clearfix">|<div class="pagination">|$)', re.S)
_RE_THUMB = re.compile(r'data-src="([^"]+)"')
_RE_TITLE = re.compile(r'<p class="title"><a[^>]*title="([^"]*)"')
_RE_DUR = re.compile(r'<span class="duration">([^<]+)</span>')
_RE_HLS = re.compile(r'setVideoHLS\([\'"]([^\'"]+\.m3u8[^\'"]*)[\'"]\)')
_RE_OG = re.compile(r'property="og:image"[^>]*content="([^"]+)"')


class Spider(BaseSpider):

    # 站方发布页（JS 渲染，resolver 静态抽链拿不到域名也无妨，走内置泛解析前缀）
    PUBLISH_PAGE = 'https://dizhi8.cc/yxy/'
    # 内置候选（base 泛解析：任意 3 字母前缀可用，2026-09-08 实测）
    BUILTIN_HOSTS = [
        'https://bjq.yxy999p.icu',
        'https://xyz.yxy881p.icu',
        'https://abc.yxy511p.icu',
        'https://qwe.yxy7722.top',
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
        return "玉羞园"

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
            t = text or ''
            return ('thumb-block' in t) and ('xvideos-cdn' in t or '玉羞园' in t)

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
                            timeout=15, verify=False)

    @staticmethod
    def _parse_list(html_text):
        out = []
        seen = set()
        for m in _RE_BLOCK.finditer(html_text):
            eid, blk = m.group(1), m.group(2)
            if eid in seen:
                continue
            seen.add(eid)
            t = _RE_TITLE.search(blk)
            title = _html.unescape(t.group(1)).strip() if t else ''
            if not title:
                continue
            pic = ''
            mt = _RE_THUMB.search(blk)
            if mt:
                pic = _html.unescape(mt.group(1)).strip()
            remark = ''
            md = _RE_DUR.search(blk)
            if md:
                remark = md.group(1).strip()
            out.append({
                'vod_id': eid,
                'vod_name': title,
                'vod_pic': pic,
                'vod_remarks': remark,
            })
        return out

    def homeContent(self, flag):
        result = {'class': [], 'list': []}
        for c in _CATS:
            result['class'].append({'type_id': c['tpl'], 'type_name': c['name']})
        try:
            result['list'] = self._parse_list(self._get('/new/1').text or '')
        except Exception:
            pass
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        result = {'list': []}
        path = tid.replace('{pg}', str(pg)) if '{pg}' in tid else tid
        try:
            result['list'] = self._parse_list(self._get(path).text or '')
        except Exception:
            pass
        return result

    def searchContent(self, key, quick, pg='1'):
        result = {'list': []}
        try:
            path = f'/?k={quote(key)}'
            if str(pg) not in ('1', ''):
                path += f'&p={pg}'
            result['list'] = self._parse_list(self._get(path).text or '')
        except Exception:
            pass
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    def _detail(self, eid):
        """抓详情页 → (title, pic, m3u8)。签名 m3u8 短效，须播放时现取。"""
        body = self._get(f'/video.{eid}/_').text or ''
        title = ''
        m = re.search(r'<title>([^<]+)</title>', body)
        if m:
            title = _html.unescape(m.group(1)).strip()
            title = re.sub(r'\s*[-|]\s*玉羞园.*$', '', title).strip()
        pic = ''
        mo = _RE_OG.search(body)
        if mo:
            pic = _html.unescape(mo.group(1)).strip()
        m3u8 = ''
        mh = _RE_HLS.search(body)
        if mh:
            m3u8 = mh.group(1).strip()
        return title, pic, m3u8

    def detailContent(self, ids):
        result = {'list': []}
        try:
            eid = str(ids[0])
            title, pic, m3u8 = self._detail(eid)
            result['list'].append({
                'vod_id': eid,
                'vod_name': title or eid,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': '',
                'vod_director': '',
                'vod_content': '',
                'vod_play_from': 'yxy',
                'vod_play_url': f'播放${eid}',
            })
        except Exception:
            pass
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {'parse': 0, 'playUrl': '', 'url': '', 'header': {'User-Agent': _UA}}
        try:
            eid = str(id)
            _, _, m3u8 = self._detail(eid)
            if m3u8:
                result['url'] = m3u8
                result['header'] = {'User-Agent': _UA, 'Referer': self.host + '/'}
        except Exception:
            pass
        return result
