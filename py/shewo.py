# -*- coding: utf-8 -*-
# \u5c04\u7a9d \u7ad9\u6e90\uff08\u82f9\u679cCMS \u578b \u00b7 \u6cdb\u89e3\u6790\u6362\u57df\u7248\uff0c2026-09-12 \u7531 xbpq/\u5c04\u7a9d.json py \u5316\uff09
# \u53d6\u57df\u673a\u5236\uff082026-09-12 \u5b9e\u6d4b\uff09\uff1a
#   \u4efb\u610f {\u8bcd}.shewo22.cc \u90fd\u89e3\u6790\uff08\u6cdb\u89e3\u6790=\u53d1\u5e03\u673a\u5236\uff0c\u65e0\u4f20\u7edf\u53d1\u5e03\u9875\uff09\uff1a
#     - \u6839\u8def\u5f84 /            = \u843d\u5730\u58f3\uff083214B\uff0cJS \u70b9\u51fb\u8df3 /{\u4e2d\u6587\u8bcd}/\uff09
#     - /vodtype|vodsearch|voddetail|vodplay/... \u6df1\u94fe = \u4efb\u610f\u6d3b\u8282\u70b9\u76f4\u63a5\u51fa\u5185\u5bb9
#     - /{\u4e2d\u6587\u8bcd}/          = \u5185\u5bb9\u9996\u9875\uff08\u529b\u4e89\u4e0a\u6e38/\u594b\u53d1\u56fe\u5f3a/\u6301\u4e4b\u4ee5\u6052\uff09
#   \u2192 \u63a2\u6d3b\u5fc5\u987b\u63a2\u6df1\u94fe\uff08/vodtype/55-1.html \u542b pornkvideos\uff09\uff0c\u4e0d\u80fd\u63a2\u6839\u3002
#   \u4e0d\u540c\u5b50\u57df\u662f\u4e0d\u540c\u5185\u5bb9\u8282\u70b9\uff08md5 \u4e0d\u540c\uff09\uff0c\u4efb\u4e00\u53ef\u7528\u5373\u53ef\u3002
# \u7ed3\u6784: \u5206\u7c7b /vodtype/{tid}-{pg}.html\uff1b\u641c\u7d22 /vodsearch/{wd}----------{pg}---.html
#       \u8be6\u60c5 /voddetail/{id}.html\uff1b\u64ad\u653e /vodplay/{id}-{sid}-{nid}.html
#       \u64ad\u653e\u9875 var player_aaaa={...url:m3u8}\uff08encrypt=0\uff09
#       \u6ce8\u610f\u522b\u6293\u5230\u5e7f\u544a\u56fe\uff08\u6a2a\u5e45/\u5e95\u98d8\uff0chost \u9ed1\u540d\u5355\u89c1 _AD_HOST_RE\uff09\u3002
import json
import re
import sys
import os
import random
import html as _html
from urllib.parse import urljoin

import requests
try:
    from base.spider import Spider as BaseSpider
except ImportError:
    class BaseSpider(object):
        def fetch(self, url, headers=None, timeout=10):
            try:
                res = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
                res.encoding = 'utf-8'
                return res
            except Exception:
                return None


from hostresolver import resolve_host, parse_ext, probe_first
_UA = ('Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 '
       '(KHTML, like Gecko) Chrome/143.0.7499.192 Mobile Safari/537.36')

# \u5206\u7c7b\u8868\uff08\u4e0e xbpq/\u5c04\u7a9d.json \u5206\u7c7b\u9010\u5b57\u4e00\u81f4\uff09
_CATS = [
    ('\u56fd\u4ea7\u7cbe\u54c1', '55'), ('\u534e\u8bed\u7cbe\u54c1', '63'), ('\u9ed1\u6599\u5403\u74dc', '58'), ('\u6b27\u7f8e\u5927\u5c4c', '60'),
    ('\u52a8\u6f2b\u7981\u6f2b', '57'), ('\u5b66\u751f\u5408\u96c6', '65'), ('\u4e71\u4f26\u7cbe\u54c1', '64'), ('\u63a2\u82b1\u7ea6\u70ae', '61'),
    ('\u65e5\u672c\u65e0\u7801', '86'), ('\u65e5\u672c\u6709\u7801', '80'), ('\u4e3b\u64ad\u7f51\u7ea2', '81'), ('\u56fd\u4ea7\u8272\u60c5', '12'),
    ('\u65e5\u672c\u65e0\u78012', '20'), ('\u81ea\u62cd\u5077\u62cd', '21'), ('\u4eba\u59bb\u719f\u5973', '22'), ('\u9ed1\u4eba\u6d0b\u5c4c', '23'),
    ('\u6b27\u7f8e\u7cbe\u54c1', '24'), ('\u5361\u901a\u52a8\u6f2b', '69'), ('\u4e71\u4f26\u4e2d\u51fa', '70'), ('\u4f20\u5a92\u539f\u521b', '71'),
    ('\u53e3\u7206\u989c\u5c04', '72'), ('\u5c9b\u56fd\u5973\u4f18', '25'), ('\u841d\u8389\u5c11\u5973', '26'), ('\u91cd\u53e3\u8c03\u6559', '88'),
    ('\u56fd\u4ea7\u76f4\u64ad', '56'), ('\u5c9b\u56fd\u7fa4\u4ea4', '73'), ('\u65e5\u672c\u6709\u78012', '74'), ('\u4e2d\u6587\u5b57\u5e55', '75'),
    ('\u5403\u74dc\u7206\u6599', '76'), ('\u89d2\u8272\u626e\u6f14', '77'), ('\u6deb\u5a03\u81ea\u6170', '78'), ('\u97e9\u56fd\u76f4\u64ad', '84'),
    ('\u516c\u5f00\u6f0f\u51fa', '85'), ('\u6237\u5916\u6253\u91ce', '89'),
]

# \u63a2\u6d3b\u6df1\u94fe\uff1a\u5206\u7c7b 55 \u7b2c\u4e00\u9875\uff08\u4efb\u4f55\u6d3b\u8282\u70b9\u90fd 200+pornkvideos\uff09
_PROBE_PATH = '/vodtype/55-1.html'
_MARK = 'pornkvideos'

# \u5185\u7f6e\u5019\u9009\u8bcd\uff08yjewvzfn=2026-09-12 \u5b9e\u6d4b\u8282\u70b9\uff1b\u5176\u4f59\u4e3a\u5e38\u7528\u5b50\u57df\u8bcd\uff0c\u6cdb\u89e3\u6790\u4efb\u610f\u8bcd\u5747\u89e3\u6790\uff09
_BUILTIN_WORDS = ['yjewvzfn', 'www', 'm', 'wap', 'app', 'tv', 'h5', 'vip']

_RE_ITEM = re.compile(
    r'<div class="pornkvideos[^"]*">\s*<a href="(/voddetail/(\d+)\.html)"[^>]*>(.*?)</a>', re.S)
# \u5c01\u9762\u56fe\u5e8a\u4e0d\u6b62\u4e00\u5bb6\uff1a\u524d\u6bb5\u5206\u7c7b thjpg*.vip/upload/vod\uff0c\u540e\u6bb5\u5206\u7c7b img.xxibaocdn.com/video/...
# \uff082026-09-12 \u5b9e\u6d4b tid=55 vs tid=12/89\uff09\uff0c\u6545\u53ea\u8ba4 data-src \u4efb\u610f http \u56fe + \u5e7f\u544a host \u9ed1\u540d\u5355\u3002
_RE_IMG = re.compile(r'data-src="(https?://[^"]+)"')
# \u5e7f\u544a\u56fe host\uff08\u9875\u5185\u6a2a\u5e45/\u5e95\u98d8\uff0c\u4e0d\u5728\u6761\u76ee\u5757\u5185\uff0c\u9632\u5fa1\u6027\u8fc7\u6ee4\uff09
_AD_HOST_RE = re.compile(r'alicdn\.com|baiducdn2img\.top|oss-accelerate\.aliyuncs\.com|shsrdzs\.com')
_RE_TITLE = re.compile(r'<h2>\s*(.*?)\s*</h2>', re.S)
_RE_DATE = re.compile(r'<div class="vlength">\s*(.*?)\s*</div>', re.S)
_RE_PAGE = re.compile(r'/vodtype/(?:\d+)-(\d+)\.html')
_RE_EP = re.compile(r'<a[^>]*href="(/vodplay/(\d+)-(\d+)-(\d+)\.html)"[^>]*>(.*?)</a>', re.S)
_RE_PLAYER = re.compile(r'var\s+player_aaaa\s*=\s*(\{.*?\})\s*;?\s*</script>', re.S)


def _clean(s):
    return _html.unescape(re.sub(r'<[^>]+>', '', s or '')).replace('\xa0', ' ').strip()


# \u5206\u96c6\u540d\u5e7f\u544a\u9ed1\u540d\u5355\uff08\u5bf9\u9f50\u6bcf\u65e5\u5927\u8d5b._valid_ep_name \u7eaa\u5f8b\uff09
_AD_NAME_RE = re.compile('(<|http|www\\.|\\.com|\\.cc|\u516c\u4f17\u53f7|\u5173\u6ce8|\u798f\u5229|\u66f4\u591a|APP|app|\u4e0b\u8f7d|\u5730\u5740\u53d1\u5e03|\u6700\u65b0\u5730\u5740)')


class Spider(BaseSpider):

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
        self.trace = []
        # \u53d6\u57df\u7edd\u4e0d\u8bb8\u70b8 init\u2014\u2014\u5931\u8d25\u7559\u7a7a\uff0c\u61d2\u91cd\u8bd5\u515c\u5e95\uff0c\u4fdd\u8bc1\u5206\u7c7b\u5fc5\u51fa
        try:
            self.host = self.get_working_host()
        except Exception as e:
            self.host = ''
            self.trace.append('init\u53d6\u57df\u5f02\u5e38: %s' % str(e)[:60])
        self.headers.update({'Origin': self.host, 'Referer': self.host + '/'})
        print('\u4f7f\u7528\u7ad9\u70b9: %s' % self.host)

    def getName(self):
        return "\u5c04\u7a9d"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def localProxy(self, params):
        return [200, "video/MP2T", ""]

    def _http(self, url, headers=None, timeout=8):
        # requests \u76f4\u8fde\u5305\u88c5\u3002\u26a0\u523b\u610f\u4e0d\u53eb fetch\uff1aApp \u57fa\u7c7b\u6709\u540c\u540d\u65b9\u6cd5\uff08\u8fd4\u56de\u7c7b\u578b\u4e0e
        # rsp.text \u9884\u671f\u4e0d\u7b26\u65f6\u5404\u63a5\u53e3 except \u541e\u9519\u8fd4\u7a7a=\u96f6\u6570\u636e\u6839\u56e0\uff09\uff0c\u649e\u540d\u5fc5\u70b8\u771f\u673a\u3002
        try:
            req_headers = headers or self.headers
            res = requests.get(url, headers=req_headers, proxies=self.proxies,
                               timeout=timeout, verify=False, allow_redirects=True)
            res.encoding = 'utf-8'
            return res
        except Exception as e:
            print('http error: %s %s' % (url, e))
            return None

    # ---------- \u53d6\u57df ----------
    def _probe_one(self, host_base, result):
        """\u63a2\u6df1\u94fe\uff08\u6839\u662f\u843d\u5730\u58f3\uff0c\u63a2\u6839\u5fc5\u5931\u8d25\uff09\u3002host_base \u542b\u534f\u8bae\u4e0d\u542b\u8def\u5f84\u3002"""
        if result[0]:
            return
        try:
            r = requests.get(host_base + _PROBE_PATH, headers=self.headers,
                             proxies=self.proxies, timeout=5, verify=False,
                             allow_redirects=True)
            ok = (r.status_code == 200 and _MARK in (r.text or ''))
            self.trace.append('%s -> %s %s' % (host_base, r.status_code, 'OK' if ok else '\u975e\u5185\u5bb9'))
            if ok and not result[0]:
                result[0] = host_base
        except Exception as e:
            self.trace.append('%s -> FAIL %s' % (host_base, str(e)[:40]))

    def _candidate_hosts(self):
        """hostresolver \u7528\u7684\u5019\u9009\uff1aext + \u5185\u7f6e\u8bcd\uff08\u4e0d\u542b\u968f\u673a\u8bcd\uff0c\u63a7\u5236\u6700\u574f\u8017\u65f6\uff09\u3002"""
        cands = []
        if self._ext.get('host'):
            cands.append(self._ext['host'])
        cands += list(self._ext.get('hosts') or [])
        for w in _BUILTIN_WORDS:
            u = 'https://%s.shewo22.cc' % w
            if u not in cands:
                cands.append(u)
        return cands

    def _cands_random(self, n=8):
        """\u6cdb\u89e3\u6790\u4efb\u610f\u8bcd\u5747\u89e3\u6790\uff1a\u968f\u673a\u8bcd\u6269\u6c60\uff08\u4e0d\u540c\u8bcd=\u4e0d\u540c\u5185\u5bb9\u8282\u70b9\uff09\u3002"""
        out, seen = [], set()
        while len(out) < n:
            w = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6))
            if w in seen:
                continue
            seen.add(w)
            out.append('https://%s.shewo22.cc' % w)
        return out

    def _probe_round(self, cands, wait):
        """\u4e00\u8f6e\u5e76\u884c\u63a2\u6d4b\uff0cwait \u79d2\u603b\u95f8\uff08DNS \u5361\u6b7b\u7ebf\u7a0b\u7531\u95f8\u6536\u5c38\uff09\u3002\u8fd4\u56de\u547d\u4e2d\u6216 ''\u3002"""
        import threading
        if not cands:
            return ''
        result = [None]
        threads = [threading.Thread(target=self._probe_one, args=(u, result))
                   for u in cands[:16]]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=wait)
        return result[0] or ''

    def _resolve_inline(self, validate_probe):
        """hostresolver \u672a\u52a0\u8f7d\u65f6\u7684\u5185\u8054\u5e76\u884c\u63a2\u6d4b\uff08gitee \u8fdc\u7a0b\u5bfc\u5165\u5f62\u6001\u53ea\u5269\u8fd9\u6761\u8def\uff09\u3002
        \u4e24\u6bb5\u5f0f\uff1a\u5148\u5185\u7f6e\u9ad8\u547d\u4e2d\u8bcd\uff088s \u95f8\uff09\uff0c\u5168\u5931\u8d25\u518d\u968f\u673a\u8bcd\u6269\u6c60\uff088s \u95f8\uff09\u3002
        \u771f\u673a DNS \u5bf9\u6cdb\u89e3\u6790\u968f\u673a\u5b50\u57df\u53ef\u80fd\u5361\u5f88\u4e45\u2014\u2014\u603b\u95f8\u5fc5\u987b\u5b58\u5728\uff0c\u5426\u5219 App \u6390\u6b7b init\u3002"""
        h = self._probe_round(self._candidate_hosts(), 8)
        if h:
            return h
        self.trace.append('\u5185\u7f6e\u8bcd\u672a\u547d\u4e2d\uff0c\u968f\u673a\u8bcd\u6269\u6c60')
        return self._probe_round(self._cands_random(8), 8)

    def get_working_host(self):
        # \u9501\u5b9a\u57df\uff1ahostresolver \u9010\u6e90\u540c\u8bed\u4e49\u2014\u2014\u586b\u4e86 host@ \u5c31\u53ea\u7528\u5b83
        if self._ext.get('host'):
            return self._ext['host'].rstrip('/')
        if resolve_host:
            try:
                h = resolve_host(
                    publish_page='',
                    candidate_hosts=self._candidate_hosts(),
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=8,
                    validate=lambda host, text: _MARK in (text or ''),
                    probe_path=_PROBE_PATH,
                )
                if h:
                    return h.rstrip('/')
            except Exception:
                pass
        if probe_first:
            try:
                h = probe_first(self._candidate_hosts(), headers=self.headers,
                                proxies=self.proxies, timeout=8,
                                validate=lambda host, text: _MARK in (text or ''),
                                tag='\u5c04\u7a9d\u515c\u5e95')
                if h:
                    return h.rstrip('/')
            except Exception:
                pass
        return self._resolve_inline(None)

    # ---------- \u8bca\u65ad\uff08\u5df2\u968f\u771f\u673a\u9a8c\u8bc1\u901a\u8fc7\u79fb\u9664\uff0c2026-09-12\uff09 ----------

    def _valid_ep_name(self, s, max_len=20):
        """\u5206\u96c6\u540d\u6e05\u6d17\uff08\u5bf9\u9f50\u5df2\u9a8c\u8bc1\u6e90\u7eaa\u5f8b\uff09\uff1a\u7a7a\u3001\u8d85\u957f\u3001\u547d\u4e2d\u5e7f\u544a\u9ed1\u540d\u5355 \u2192 \u8fd4\u56de ''\u3002"""
        s = _clean(s)
        if not s or len(s) > max_len or _AD_NAME_RE.search(s):
            return ''
        return s

    def _ensure_host(self):
        """init \u65f6\u53d6\u57df\u5931\u8d25\uff08\u624b\u673a\u7f51\u7edc\u6162\uff09\u2192 \u9996\u6b21\u771f\u6b63\u8bbf\u95ee\u65f6\u518d\u8bd5\u4e00\u6b21\u3002"""
        if self.host:
            return
        self.trace.append('\u61d2\u91cd\u8bd5: \u91cd\u65b0\u53d6\u57df')
        h = self.get_working_host()
        if h:
            self.host = h
            self.headers.update({'Origin': self.host, 'Referer': self.host + '/'})
            print('\u61d2\u91cd\u8bd5\u547d\u4e2d: %s' % self.host)

    # ---------- \u63a5\u53e3 ----------
    def homeContent(self, filter):
        classes = [{'type_name': n, 'type_id': tid} for n, tid in _CATS]
        return {'class': classes, 'filters': {}}

    def homeVideoContent(self):
        # App \u9996\u9875\u5237\u65b0\u7684\u63a8\u8350\u4f4d\u8d70\u8fd9\u91cc\u2014\u2014\u6293\u7b2c\u4e00\u5206\u7c7b\u9875\u586b\u4e0a\uff08\u4e4b\u524d\u8fd4\u56de\u7a7a\u5bfc\u81f4\u300c\u5237\u65b0\u4e0d\u51fa\u4e1c\u897f\u300d\u89c2\u611f\uff09
        try:
            res = self._http(self.host + _PROBE_PATH)
            if res and res.status_code == 200:
                lst = self._parse_list(res.text or '')[:12]
                if lst:
                    return {'list': lst}
        except Exception:
            pass
        return {'list': []}

    def _parse_list(self, html):
        out = []
        for m in _RE_ITEM.finditer(html):
            href, vid, chunk = m.group(1), m.group(2), m.group(3)
            pic = ''
            for img in _RE_IMG.finditer(chunk):
                u = img.group(1)
                if _AD_HOST_RE.search(u):
                    continue
                pic = u
                break
            t = _RE_TITLE.search(chunk)
            name = _clean(t.group(1)) if t else ''
            d = _RE_DATE.search(chunk)
            remark = _clean(d.group(1))[:12] if d else ''
            if vid and name:
                out.append({'vod_id': vid, 'vod_name': name,
                            'vod_pic': pic, 'vod_remarks': remark})
        return out

    def _pagecount(self, html):
        nums = [int(x) for x in _RE_PAGE.findall(html)]
        return max(nums) if nums else 1

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg or 1)
        self._ensure_host()
        url = '%s/vodtype/%s-%d.html' % (self.host, tid, pg)
        res = self._http(url)
        result = {'list': [], 'page': pg, 'pagecount': 1, 'limit': 20, 'total': 0}
        if not res or res.status_code != 200:
            return result
        html = res.text or ''
        result['list'] = self._parse_list(html)
        result['pagecount'] = self._pagecount(html)
        result['limit'] = len(result['list'])
        result['total'] = result['pagecount'] * max(len(result['list']), 1)
        return result

    def searchContent(self, key, quick, pg=1):
        pg = int(pg or 1)
        self._ensure_host()
        url = '%s/vodsearch/%s----------%d---.html' % (self.host, key, pg)
        res = self._http(url)
        if not res or res.status_code != 200:
            return {'list': []}
        return {'list': self._parse_list(res.text or ''), 'page': pg}

    def detailContent(self, ids):
        vid = ids[0]
        self._ensure_host()
        url = '%s/voddetail/%s.html' % (self.host, vid)
        res = self._http(url)
        if not res or res.status_code != 200:
            return {'list': []}
        html = res.text or ''
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
        name = _clean(h1.group(1)) if h1 else str(vid)
        pic = ''
        # \u8be6\u60c5\u9875\u5c01\u9762\u540c\u6837\u662f\u591a\u56fe\u5e8a\uff08thjpg*.vip / xxibaocdn\uff09\uff0c\u53ea\u6ee4\u5e7f\u544a host
        for m in re.finditer(r'(https?://[^"\']+?\.(?:jpg|png|webp)(?:\?[^"\']*)?)', html):
            u = m.group(1)
            if _AD_HOST_RE.search(u):
                continue
            pic = u
            break
        # \u5206\u96c6\uff08\u77ed\u7247\u7ad9\u591a\u4e3a\u5355\u96c6\uff1b\u951a\u6587\u672c\u5e38\u4e3a\u7a7a \u2192 \u6309\u94fe\u63a5\u5e8f\u53f7\u751f\u6210\u300c\u7b2cN\u96c6\u300d\uff09
        eps = []
        for m in _RE_EP.finditer(html):
            path, sid, nid, text = m.group(1), m.group(3), m.group(4), _clean(m.group(5))
            ep_name = self._valid_ep_name(text) or ('\u7b2c%s\u96c6' % nid if int(nid) > 1 else '\u64ad\u653e')
            eps.append('%s$%s' % (ep_name, path))
        if not eps:
            eps = ['\u64ad\u653e$/vodplay/%s-1-1.html' % vid]
        vod = {
            'vod_id': vid,
            'vod_name': name,
            'vod_pic': pic,
            'vod_content': '\u8d44\u6e90\u6765\u81ea\u4e8e\u7f51\u7edc\uff0c\u8bf7\u52ff\u76f8\u4fe1\u4efb\u4f55\u5e7f\u544a',
            'vod_play_from': '\u5c04\u7a9d',
            'vod_play_url': '#'.join(eps),
        }
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags=None):
        # id \u5f62\u5982 /vodplay/491059-1-1.html \u6216 491059-1-1
        path = id if str(id).startswith('/') else '/vodplay/%s.html' % id
        self._ensure_host()
        play_url = self.host + path
        res = self._http(play_url)
        if not res or res.status_code != 200:
            return {'parse': 1, 'url': play_url}
        m = _RE_PLAYER.search(res.text or '')
        real = ''
        if m:
            try:
                cfg = json.loads(m.group(1))
                real = cfg.get('url', '') or ''
                if str(cfg.get('encrypt', '0')) == '1' and real:
                    import base64
                    real = base64.b64decode(real).decode('utf-8')
            except Exception:
                real = ''
        if not real:
            mm = re.search(r'(https?://[^"\'\\\s]+\.m3u8[^"\'\\\s]*)', res.text or '')
            real = mm.group(1) if mm else ''
        if not real:
            return {'parse': 1, 'url': play_url}
        real = real.replace('\\/', '/')
        if real.startswith('//'):
            real = 'https:' + real
        elif not real.startswith('http'):
            real = urljoin(play_url, real)
        return {
            'parse': 0,
            'playUrl': '',
            'url': real,
            'header': {
                'User-Agent': _UA,
                'Referer': play_url,
                'Origin': self.host,
            },
        }
