# -*- coding: utf-8 -*-
# WXTS 站源（MacCMS 模板 · HTML 直抓版）
# 发布页: 站方 github.io（静态列出 966~969 四镜像，2026-09-08 实测全活）
# 结构: 分类 /index.php/vod/type/id/{tid}/page/{pg}.html（列表直链播放页）
#       播放页 var player_aaaa = {...} 内含 url(m3u8)/poster/link
# 分类名不落盘，homeContent 从首页实时获取（词表 b64 也不需要）
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
    # hostresolver.py 在 source/ 根（py/ 的上级），按脚本自身位置定位，不依赖 cwd
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext
    except Exception:
        resolve_host = None
        parse_ext = None

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# 列表条目: <a class="thumbnail" href="..."><img src=封面 alt=标题>
# 分类页 href=播放页(/vod/play/id/N/sid/N/nid/N.html)；搜索页 href=详情页(/vod/detail/id/N.html)
_RE_ITEM = re.compile(
    r'<a[^>]*class="[^"]*thumbnail[^"]*"[^>]*href="(/index\.php/vod/(?:play/id/(\d+)/sid/(\d+)/nid/(\d+)|detail/id/(\d+))\.html)"[^>]*>\s*<img([^>]*)>')
_RE_ATTR = re.compile(r'(src|alt)\s*=\s*"([^"]*)"')
_RE_PLAY_HREF = re.compile(r'/index\.php/vod/play/id/(\d+)/sid/(\d+)/nid/(\d+)\.html')


class Spider(BaseSpider):

    # 站方发布页（github.io 静态页，列最新镜像域名）
    PUBLISH_PAGE = 'https://wuxiants.github.io/'
    # 内置候选（2026-09-08 实测，发布页列出的四个镜像）
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
        return "无限臀山"

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
        # resolver 缺失兜底：ext 指定 → 内置逐个试
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
            # vod_id 两种形态：播放页直链 = vid-sid-nid；搜索详情页 = d{vid}
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
            if tid in seen or not name or name == '更多':
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
        # 找含 "url" 键的对象终点：从 m3u8/mp4 处向后找 "sid" 后的收尾 }
        end = html_text.find('</script>', start)
        seg = html_text[start:end if end > 0 else start + 8000]
        try:
            return json.loads(seg.strip().rstrip(';').replace('\\/', '/'))
        except Exception:
            # 兜底：截到最后一个 } 前
            k = seg.rfind('}')
            if k > 0:
                try:
                    return json.loads(seg[:k + 1].replace('\\/', '/'))
                except Exception:
                    return {}
            return {}

    def _resolve_play(self, vod_id):
        """归一 vod_id → (vid, sid, nid)。'd{vid}' 形态先抓详情页解析播放链接。"""
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
                title = re.sub(r'^在线观看', '', title).replace('_无限臀山', '').strip()
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
