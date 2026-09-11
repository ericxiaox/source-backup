# -*- coding: utf-8 -*-
# JPTT \u7ad9\u6e90\uff08\u7981\u7247\u5929\u5802 \u00b7 Laravel \u98ce\u683c + Cloudflare\uff0c2026-09-08 \u73b0\u5f79\u955c\u50cf\u91cd\u5199\u7248\uff09
# \u57df\u540d: jptt.tv 301 -> 2026ajptttv.work\uff08.work \u53cc\u955c\u50cf\uff09\uff1b\u4ee5 jptt.tv \u4e3a\u53d1\u5e03\u94fe
# \u7ed3\u6784: \u5206\u7c7b /tag_list?tid={id}&idx={pg}\uff1b\u641c\u7d22 /search?kw={kw}
#       \u5217\u8868\u6761\u76ee oneVideo \u5361\u7247\uff08\u6807\u9898 h3|h5|img@alt \u4e09\u7ea7\u515c\u5e95\uff0c\u94fe\u63a5 /video/{slug}\uff09
#       \u64ad\u653e <source data-src="//cdn-*.jptt1.cc/hlsredirect/...m3u8">\uff08\u7b7e\u540d\u77ed\u6548\uff09
# \u7eaa\u5f8b: 2026-09-08 App \u7aef\u96f6\u6570\u636e\u6839\u56e0=\u5168\u5e93\u552f\u4e00\u7528 self.fetch() \u7684\u6e90\uff08App base \u7c7b\u8fd4\u56de
#       \u7c7b\u578b\u4e0e rsp.text \u9884\u671f\u4e0d\u7b26\u2192\u5404\u65b9\u6cd5 except \u541e\u9519\u8fd4\u7a7a\uff09\uff0c\u6539 requests \u76f4\u8fde\u4e0e\u5168\u5e93\u5bf9\u9f50
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
        return "\u7981\u7247\u5929\u5802"

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
        # \u52a8\u6001\u57df\u540d\u89e3\u6790 v2\uff1a2026-09-08 \u5b9e\u6d4b jptt.tv \u6b63\u5728\u9000\u5f79\uff08302 -> 2026ajptttv.work\uff09\uff0c
        # \u4ee5 jptt.tv \u4e3a\u53d1\u5e03\u94fe\uff08\u8df3\u8f6c\u5373\u73b0\u5f79\uff09\uff0c.work \u53cc\u955c\u50cf\u4e3a\u5185\u7f6e\u5019\u9009\uff1b\u5168\u5931\u8d25\u8fd4\u56de '' \u515c\u7a7a\u3002
        ext = self._ext
        publish = ext.get('publish') or 'https://jptt.tv/'
        builtin_hosts = [
            'https://2026ajptttv.work/',      # 2026-09-08 \u5b9e\u6d4b\u73b0\u5f79\u955c\u50cf(222KB\u5b8c\u6574\u7ad9)
            'https://jptttv2026a.work/',
            'https://jptt.tv/',               # \u65e7\u4e3b\u57df\uff0c302 -> 2026ajptttv.work
        ]
        if ext.get('host'):
            self.host = ext['host'].rstrip('/')
        elif resolve_host:
            self.host = resolve_host(
                publish_page=publish,
                candidate_hosts=list(ext.get('hosts') or []) + builtin_hosts,
                headers=self.headers,
                proxies=self.proxies,
                timeout=8,
            ) or ''
        else:
            if not getattr(self, 'host', ''):
                h = self._resolve_inline(publish, builtin_hosts, lambda hh,tt: 'jptt' in (hh or '') or '\u7981\u7247' in (tt or ''))
                if h:
                    self.host = h
        # \u5168\u5931\u8d25\u515c\u5e95\uff1a\u9000\u56de\u9996\u4e2a\u5185\u7f6e\u5019\u9009\uff0c\u907f\u514d init \u56e0 self.host \u672a\u8bbe\u800c\u5d29\u6e83
        # \uff08\u7ad9\u70b9\u771f\u5168\u6b7b\u65f6 homeContent \u8d70\u515c\u5e95\u5206\u7c7b/\u8bca\u65ad\uff0c\u800c\u4e0d\u662f init \u629b AttributeError\uff09
        if not getattr(self, 'host', ''):
            self.host = builtin_hosts[0].rstrip('/')
        self.headers.update({'Referer': self.host + '/', 'Origin': self.host})

    def _resolve_inline(self, publish, builtin, validate):
        """hostresolver \u672a\u52a0\u8f7d\u65f6\u7684\u5185\u8054\u5e76\u884c\u63a2\u6d4b\uff1a\u907f\u514d\u4e32\u884c\u8d85\u65f6\u5bfc\u81f4 App \u7aef\u7a7a\u8f6c\u51e0\u5341\u79d2\u3002
        \u5e26\u5185\u5bb9\u5f62\u6001\u5224\uff0c\u9632\u6b62\u547d\u4e2d\u53d1\u5e03\u9875/\u95e8\u6237\u516c\u544a\u9875\uff08\u6709\u7ad9\u540d\u4f46\u65e0\u5185\u5bb9\uff09\u3002"""
        import threading
        candidates = []
        if publish:
            candidates.append(publish)
        candidates += list(self._ext.get('hosts') or [])
        candidates += list(builtin or [])
        seen = set(); deduped = []
        for u in candidates:
            u = (u or '').strip().rstrip('/')
            if not u:
                continue
            if not u.startswith('http'):
                u = 'https://' + u
            if u not in seen:
                seen.add(u); deduped.append(u)
        if not deduped:
            return ''
        result = [None]
        content_marks = ('<article', 'post-card', 'entry-title', 'post-title',
                         'video-item', 'oneVideo', 'playlist', 'class="video')
        content_link_pat = re.compile(
            r'href=["\'] [^"\']*/(?:archives?|video|videos|category|categories|post|vod|'
            r'watch|tag|detail|thread|topic)[/"\']', re.I)
        def _looks_like_content(t):
            return bool(t and (len(t) > 80000 or any(k in t for k in content_marks)
                               or len(content_link_pat.findall(t)) >= 5))
        def _probe_one(u):
            if result[0]:
                return
            try:
                r = requests.get(u + '/', headers=self.headers, proxies=self.proxies,
                                 timeout=5, verify=False, allow_redirects=True)
                if r.status_code == 200 and validate(r.url, r.text) and _looks_like_content(r.text):
                    if not result[0]:
                        result[0] = r.url.rstrip('/')
            except Exception:
                pass
        threads = [threading.Thread(target=_probe_one, args=(u,)) for u in deduped]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
        return result[0] or ''

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
        """oneVideo \u5361\u7247\u7edf\u4e00\u89e3\u6790\u3002
        2026-09-08 \u6539\u7248\u540e\u6bcf\u89c6\u9891\u542b 3-4 \u4e2a\u91cd\u590d oneVideo \u5757\uff08\u5b8c\u6574\u5757/\u5934\u5757/\u4f53\u5757/\u788e\u7247\uff09\uff0c
        \u6309\u94fe\u63a5\u53bb\u91cd\u53d6\u5b8c\u6574\u5757\uff1b\u5206\u7c7b\u9875\u6807\u9898 h3\u3001\u641c\u7d22\u9875 h5\u3001img alt \u4e09\u7ea7\u515c\u5e95\u3002"""
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
            title = title_elements[0].strip() if title_elements else "\u672a\u77e5\u6807\u9898"

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
                "vod_play_from": "\u6ce8\u610f\u8eab\u4f53",
                "vod_play_url": "\u591a\u770b\u5c11\u6253\u5361$" + play_url
            }
            return {'list': [vod]}
        except Exception as e:
            print(f"[detailContent error]: {e}")
            return {'list': []}

    def extractVideoUrl(self, html):
        try:
            # 2026-09-08: <source src= \u6539\u7248\u4e3a data-src=\uff08\u61d2\u52a0\u8f7d\uff09\uff0c\u4e24\u79cd\u90fd\u8ba4
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
