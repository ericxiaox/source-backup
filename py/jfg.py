# -*- coding: utf-8 -*-
# JFG 站源（集芳阁云搜 · HTML 直抓版）
# 域名: sourceUrl 自带的 punycode 花式域名（"请记住-jifangge点com.云搜福利.com"）
#       即现役入口，2026-09-08 实测 200（Cloudflare）；站内互链 twin 域同样可用
# 结构: 分类 = newlist.php?p={n}(今日更新) / toplist.php?p={n}(今日热播Top100)
#       条目 <a href="content/{md5}.html"> + cover 背景图 + ctitle 标题 + vodtime
#       详情 m3u8 在 <a playdata="..."> 明文属性；搜索为 AES 加密词条，不做
import json
import re
import sys
import os
import html as _html
from urllib.parse import urljoin

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

# 列表条目: 按 <li> 分块；块内 <a href="content/{md5}.html..."> + cover 背景图
#           + <p>标题</p> + vodtime
_RE_LINK = re.compile(r'<a[^>]*href="(content/[a-f0-9]+\.html[^"]*)"')
_RE_COVER = re.compile(r"background-image:\s*url\('([^']+)'\)")
_RE_CTITLE = re.compile(r'<div class="ctitle">\s*<p>([^<]+)</p>')
_RE_VT = re.compile(r'<span class="vodtime">([^<]+)</span>')
_RE_HREF = re.compile(r'<a[^>]*href="([^"]+)"')
_RE_POSTER = re.compile(r"poster=['\"]([^'\"]+)['\"]")
_RE_PLAY = re.compile(r'<a[^>]*playdata="([^"]+\.m3u8[^"]*)"')


class Spider(BaseSpider):

    # 内置候选（2026-09-08 实测 200；punycode = 请记住-jifangge点com.云搜福利.com）
    BUILTIN_HOSTS = [
        'https://xn---jifanggecom-ud8sv658aesydp6a.xn--9kq80g37uthu.com',
        'https://xn--u2uy07cd3d2mxd2a.com',
    ]
    # 无独立发布页：入口域名即花式域名（站方设计为好记不易封）
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
        return "集芳阁"

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
            return '集芳阁' in t or 'h_d_key' in t

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
            {'type_id': 'newlist', 'type_name': '今日更新'},
            {'type_id': 'toplist', 'type_name': '今日热播Top100'},
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

    def searchContent(self, key, quick, pg='1'):
        # 站方搜索词条为 AES 加密 JS 生成（与阅读源同决策：不做搜索）
        return {'list': []}

    def searchContentPage(self, key, quick, pg):
        return {'list': []}

    def detailContent(self, ids):
        result = {'list': []}
        try:
            key = str(ids[0]).split('?')[0]
            body = self._get(key).text or ''
            title = ''
            m = re.search(r'<title>([^<]+)</title>', body)
            if m:
                title = _html.unescape(m.group(1)).strip()
                title = re.sub(r'\s*[-|]\s*集芳阁.*$', '', title).strip()
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
