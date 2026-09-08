# -*- coding: utf-8 -*-
# JPTT 站源（禁片天堂 · Laravel 风格 + Cloudflare，2026-09-08 现役镜像重写版）
# 域名: jptt.tv 301 -> 2026ajptttv.work（.work 双镜像）；以 jptt.tv 为发布链
# 结构: 分类 /tag_list?tid={id}&idx={pg}；搜索 /search?kw={kw}
#       列表条目 oneVideo 卡片（标题 h3|h5|img@alt 三级兜底，链接 /video/{slug}）
#       播放 <source data-src="//cdn-*.jptt1.cc/hlsredirect/...m3u8">（签名短效）
# 纪律: 2026-09-08 App 端零数据根因=全库唯一用 self.fetch() 的源（App base 类返回
#       类型与 rsp.text 预期不符→各方法 except 吞错返空），改 requests 直连与全库对齐
import sys
import re
import json
import requests
from lxml import etree
from base64 import b64decode
from urllib.parse import quote

sys.path.append('..')
from base.spider import Spider
try:
    from hostresolver import resolve_host, parse_ext
except Exception:
    try:
        import os as _os
        sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext
    except Exception:
        resolve_host = None
        parse_ext = None

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'


class Spider(Spider):
    def getName(self):
        return "禁片天堂"

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
                if parse_ext:
                    try:
                        self._ext = parse_ext(ext_str)
                    except Exception:
                        self._ext = {}
        self.headers = {
            'User-Agent': _UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9',
            'Connection': 'keep-alive',
        }
        # 动态域名解析 v2：2026-09-08 实测 jptt.tv 正在退役（302 -> 2026ajptttv.work），
        # 以 jptt.tv 为发布链（跳转即现役），.work 双镜像为内置候选；全失败返回 '' 兜空。
        ext = self._ext
        if ext.get('host'):
            self.host = ext['host'].rstrip('/')
        else:
            publish = ext.get('publish') or 'https://jptt.tv/'
            builtin_hosts = [
                'https://2026ajptttv.work/',      # 2026-09-08 实测现役镜像(222KB完整站)
                'https://jptttv2026a.work/',
                'https://jptt.tv/',               # 旧主域，302 -> 2026ajptttv.work
            ]
            if resolve_host:
                self.host = resolve_host(
                    publish_page=publish,
                    candidate_hosts=list(ext.get('hosts') or []) + builtin_hosts,
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=8,
                ) or ''
            else:
                self.host = (ext.get('hosts') or builtin_hosts)[0].rstrip('/')
        self.headers.update({'Referer': self.host + '/', 'Origin': self.host})

    def _get(self, path):
        url = path if path.startswith('http') else self.host + path
        return requests.get(url, headers=self.headers, proxies=self.proxies,
                            timeout=15, verify=False)

    def homeContent(self, filter):
        cateManual = json.loads(b64decode('eyLkuK3mlociOiAiMjc4IiwgIuW3qOS5syI6ICIxNSIsICLnhp/lpbMiOiAiOTUiLCAi6aiO5LmY5L2NIjogIjc0IiwgIuWPo+S6pCI6ICIzNCIsICLnmaHlpbMiOiAiNzUiLCAi5r2u5ZC5IjogIjMyIiwgIuS8geWKg+eJhyI6ICI4NCIsICLnvo7lsLsiOiAiMTU2IiwgIuaJk+aJi+anjSI6ICI5OCIsICLmiLLliofjgIHpgKPnuozliociOiAiNTgiLCAi5Yi25pyNIjogIjE5IiwgIue+juiFvyI6ICIxNTciLCAi6IiU6a6RIjogIjEyMiIsICLnvo7kubMiOiAiMTY2IiwgIuaQreiolSI6ICIxMiIsICLlpoTmg7Pml48iOiAiMTg0IiwgIuesrOS4gOS6uueoseimlum7niI6ICIxNjciLCAi5aq95aq957O7IjogIjE5MyIsICLkurrlprvjg7vkuLvlqaYiOiAiMjYiLCAi5aSa56iu6IG35qWtIjogIjg0IiwgIue+nui+sSI6ICIxNjMiLCAi5aWz5pWZ5birIjogIjEzMSIsICLmt6voqp4iOiAiMTUxIiwgIuiCieaEnyI6ICIxMzYiLCAi5oSb576O6IeAIjogIjExMSIsICLog4zlvozkvY0iOiAiMTc4IiwgIuiqv+aVmSI6ICIzOTUiLCAi6JmV55S3IjogIjIzIiwgIuitt+WjqyI6ICIyODMiLCAi5L+u6ZW3IjogIjE0NyIsICLpnLLlhafopLIiOiAiMTY5IiwgIue1suilqiI6ICIxMTUiLCAi5oSb5beo5LmzIjogIjIwMCIsICLnnLzpj6EiOiAiMjkwIiwgIui2heS5syI6ICIyMTEiLCAi6aGP6Z2i6aiO5LmYIjogIjI2MyIsICLmg6HkvZzliociOiAiMTQ1IiwgIue+qeavjSI6ICIxNDQiLCAi5rer5LqC44O76YGO5r+A57O7IjogIjYzIiwgIuaEm+e+juiFvyI6ICIxMSIsICLniIbkubMiOiAiNDgzIiwgIuWls+S4iuWPuCI6ICIxMzciLCAi5q2j5aSqIjogIjQxNSIsICLnqb/ooaPlubnnoLIiOiAiMTc5IiwgIue3iui6q+earuihoyI6ICIzMDQiLCAi5a245ZySIjogIjQyMSIsICLnqbrlp5AiOiAiMTMyIiwgIueyiee1suaEn+isneelrSI6ICIxOTAiLCAi6IOM6Z2i6aiO5LmX5L2NIjogIjY0NiIsICLnp5jmm7giOiAiMzYzIiwgIuWls+S4u+aSrSI6ICIxMDYiLCAi5Y+N5ZCR5pCt6KiVIjogIjMwNSIsICLlgaXouqvmlZnnt7QiOiAiMjMzIiwgIumDqOS4i+ODu+WQjOWDmiI6ICIxNTAiLCAi6Iie6LmIIjogIjEzMCIsICLnt4rouqvooaPmv4Dlh7giOiAiMzIxIiwgIjNE5b2x54mHIjogIjUwOCIsICLml6nmtKkiOiAiNDAzIn0=').decode('utf-8'))
        result = {'class': [{'type_name': k, 'type_id': v} for k, v in cateManual.items()]}
        return result

    def homeVideoContent(self):
        return {}

    @staticmethod
    def _parse_cards(root):
        """oneVideo 卡片统一解析。
        2026-09-08 改版后每视频含 3-4 个重复 oneVideo 块（完整块/头块/体块/碎片），
        按链接去重取完整块；分类页标题 h3、搜索页 h5、img alt 三级兜底。"""
        out = []
        seen = set()
        for video in root.xpath('//div[contains(@class,"oneVideo")]'):
            try:
                links = video.xpath('.//a/@href')
                if not links:
                    continue
                link = links[0]
                if '/video/' not in link or link in seen:
                    continue
                seen.add(link)
                name = ''
                for xp in ('.//h3/text()', './/h5/text()'):
                    n = video.xpath(xp)
                    if n:
                        name = n[0].strip()
                        break
                if not name:
                    alts = video.xpath('.//img/@alt')
                    if alts:
                        name = alts[0].strip()
                if not name:
                    continue
                img = ''
                imgs = video.xpath('.//img/@src')
                if imgs and imgs[0].strip():
                    img = imgs[0]
                    if img.startswith('//'):
                        img = 'https:' + img
                    elif not img.startswith('http'):
                        img = 'https://2026ajptttv.work' + img
                desc = ''
                ds = video.xpath('.//p[contains(@class,"p_duration")]/text()')
                if ds:
                    desc = ds[0].strip()
                out.append({
                    'vod_name': name,
                    'vod_pic': img,
                    'vod_remarks': desc,
                    'vod_id': link,
                })
            except Exception as e:
                print(f'[parse card error]: {e}')
                continue
        return out

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        url = f'{self.host}/tag_list?tid={tid}&idx={pg}'
        try:
            rsp = self._get(url)
            root = etree.HTML(rsp.text.encode() if isinstance(rsp.text, str) else rsp.content)
            result['list'] = self._parse_cards(root)
            result['page'] = pg
            result['pagecount'] = 9999
            result['limit'] = 90
            result['total'] = 999999
        except Exception as e:
            print(f'[categoryContent fetch error]: {e}')
            result['list'] = []
            result['page'] = pg
            result['pagecount'] = 0
            result['limit'] = 0
            result['total'] = 0
        return result

    def detailContent(self, array):
        tid = array[0]
        url = tid if tid.startswith('http') else f'{self.host}{tid}'
        try:
            rsp = self._get(url)
            root = etree.HTML(rsp.text.encode() if isinstance(rsp.text, str) else rsp.content)

            title_elements = root.xpath('//h1[@class="h1_title"]/text()')
            title = title_elements[0].strip() if title_elements else "未知标题"

            pic_elements = root.xpath('//video/@poster')
            pic = pic_elements[0] if pic_elements else ""
            if pic and not pic.startswith('http'):
                pic = 'https:' + pic if pic.startswith('//') else self.host + pic

            desc_elements = root.xpath('//div[contains(@class,"info_original")]//p/text()')
            desc = desc_elements[0].strip() if desc_elements else title

            play_url = self.extractVideoUrl(rsp.text)

            vod = {
                "vod_id": tid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_content": desc,
                "vod_play_from": "注意身体",
                "vod_play_url": "多看少打卡$" + play_url
            }
            return {'list': [vod]}
        except Exception as e:
            print(f"[detailContent error]: {e}")
            return {'list': []}

    def extractVideoUrl(self, html):
        try:
            # 2026-09-08: <source src= 改版为 data-src=（懒加载），两种都认
            source_match = re.search(r'<source\s+(?:data-)?src="([^"]+)"', html)
            if source_match:
                video_url = source_match.group(1)
                if video_url.startswith('//'):
                    video_url = 'https:' + video_url
                return video_url

            hls_patterns = [
                r'//cdn-[^"\']+\.m3u8[^"\']*',
                r'https?://[^"\']+\.m3u8[^"\']*',
                r'/hlsredirect/[^"\']+\.m3u8'
            ]
            for pattern in hls_patterns:
                matches = re.findall(pattern, html)
                if matches:
                    for match in matches:
                        if match.startswith('//'):
                            return 'https:' + match
                        elif match.startswith('http'):
                            return match
                        else:
                            return self.host + match

            js_patterns = [
                r'src\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'url\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']'
            ]
            for pattern in js_patterns:
                match = re.search(pattern, html)
                if match:
                    video_url = match.group(1)
                    if video_url.startswith('//'):
                        return 'https:' + video_url
                    elif video_url.startswith('http'):
                        return video_url
                    else:
                        return self.host + video_url

            all_m3u8 = re.findall(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', html)
            if all_m3u8:
                return all_m3u8[0]
        except Exception as e:
            print(f"[extractVideoUrl error]: {e}")

        return ""

    def searchContent(self, key, quick, pg="1"):
        result = {}
        url = f'{self.host}/search?kw={quote(key)}'
        try:
            rsp = self._get(url)
            root = etree.HTML(rsp.text.encode() if isinstance(rsp.text, str) else rsp.content)
            result['list'] = self._parse_cards(root)
        except Exception as e:
            print(f"[searchContent fetch error]: {e}")
            result['list'] = []
        return result

    def searchContentPage(self, key, quick, pg):
        return self.searchContent(key, quick, pg)

    def playerContent(self, flag, id, vipFlags):
        result = {'parse': 0, 'playUrl': '', 'url': '',
                  'header': {'User-Agent': _UA, 'Referer': self.host + '/', 'Origin': self.host}}
        try:
            if id.startswith('http') and '.m3u8' in id:
                result["url"] = id
            else:
                url = id if id.startswith('http') else f'{self.host}{id}'
                rsp = self._get(url)
                play_url = self.extractVideoUrl(rsp.text)
                result["url"] = play_url
        except Exception as e:
            print(f"[playerContent error]: {e}")
        return result

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        pass
