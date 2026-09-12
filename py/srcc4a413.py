# -*- coding: utf-8 -*-
# \u6781\u4e50\u7981\u533a \u7ad9\u6e90\uff08\u82f9\u679cCMS \u578b \u00b7 \u6cdb\u89e3\u6790\u6362\u57df\u7248\uff0c2026-09-12 \u7531 xbpq/\u6781\u4e50\u7981\u533a.json py \u5316\uff09
# \u53d6\u57df\u673a\u5236\uff082026-09-12 \u5b9e\u6d4b\uff09\uff1a
#   \u6cdb\u89e3\u6790\u65cf\uff1a*.hscwang26y2m.xyz\uff08\u53e6\u89c1 maccms \u914d\u7f6e\u57df\u65cf *.hscwang7y9m1.cc\uff09
#     - \u4efb\u610f\u968f\u673a\u5b50\u57df\u5747\u89e3\u6790\u4e14\u5404\u56de\u5404 IP\uff08CDN \u8f6e\u6362\u6c60\uff09\uff0c\u4efb\u4e00\u53ef\u7528\u5373\u53ef
#     - \u6839\u57df\u65e0 A \u8bb0\u5f55\uff0c\u7eaf\u6cdb\u89e3\u6790
#     - \u6ce8\u610f\uff1a\u672c\u5730/PC DNS \u53ef\u80fd\u89e3\u6790\u4e0d\u4e86\uff08\u6c61\u67d3/\u4ee3\u7406\u62e6\u622a\uff09\uff0c\u771f\u673a\u7f51\u7edc\u6b63\u5e38\uff1b
#       \u63a2\u6d3b\u5fc5\u987b\u63a2\u6df1\u94fe /vodtype/45-1/\uff08\u542b video-info\uff09\uff0clabel \u9875\u662f\u7a7a\u58f3\u522b\u7528
#   \u539f\u7248 4 \u4e2a\u7279\u6b8a\u5206\u7c7b\uff08\u767e\u5927\u5973\u4f18/\u756a\u53f7\u4ed3\u5e93/\u56fd\u4ea7\u4f20\u5a92/91\u63a2\u82b1 \u2192 /label/sortxx/\uff09
#   \u5b9e\u6d4b 0 \u6761\u89c6\u9891\u6570\u636e\uff0c\u5df2\u780d\u6389\uff1b\u53ea\u4fdd\u7559\u4e09\u4e2a\u5e38\u89c4\u5927\u533a\uff0845/46/47+\u5b50\u5206\u7c7b\uff09\u3002
# \u7ed3\u6784: \u5206\u7c7b /vodtype/{tid}-{pg}/\uff1b\u641c\u7d22 /vodsearch/{wd}----------{pg}---/
#       \u8be6\u60c5 /voddetail/{id}/\uff1b\u64ad\u653e /vodplay/{id}-1-1/
#       \u64ad\u653e\u9875 var player_aaaa={...url:m3u8}\uff08encrypt=0\uff0c\u4e0e\u5c04\u7a9d\u540c\u6784\uff09
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
        pass

try:
    from hostresolver import resolve_host, parse_ext, probe_first
except Exception:
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext, probe_first
    except Exception:
        resolve_host = None
        probe_first = None
        parse_ext = None

_UA = ('Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 '
       '(KHTML, like Gecko) Chrome/143.0.7499.192 Mobile Safari/537.36')

# \u5206\u7c7b\u8868\uff08\u4e0e xbpq \u7c7b\u578b\u5b57\u6bb5\u4e00\u81f4\uff1blabel \u7a7a\u58f3\u5206\u7c7b\u5df2\u780d\uff09
_CATS = [
    ('\u89c6\u9891\u4e00\u533a', '45'),
    ('\u7cbe\u54c1\u65e5\u97e9', '51'), ('\u56fd\u4ea7\u7cbe\u54c1', '49'), ('\u65e5\u97e9\u65e0\u7801', '50'), ('\u4e2d\u6587\u5b57\u5e55', '52'),
    ('\u6b27\u7f8e\u6781\u54c1', '53'), ('\u52a8\u6f2b\u7cbe\u54c1', '54'), ('\u6deb\u6b32\u75f4\u5973', '55'), ('SM\u53d8\u6001', '56'),
    ('\u89c6\u9891\u4e8c\u533a', '46'),
    ('\u5077\u62cd\u5077\u7aa5', '57'), ('\u6027\u611f\u4eba\u59bb', '61'), ('\u7f51\u7ea2\u4e3b\u64ad', '64'), ('\u9ed1\u4e1d\u8bf1\u60d1', '63'),
    ('\u4e09\u7ea7\u4f26\u7406', '62'), ('\u7ae5\u989c\u5de8\u4e73', '58'), ('\u660e\u661f\u6362\u8138', '517'), ('\u5973\u4f18\u660e\u661f', '59'),
    ('\u89c6\u9891\u4e09\u533a', '47'),
    ('\u56fd\u4ea7\u81ea\u62cd', '66'), ('\u5267\u60c5\u89e3\u8bf4', '68'), ('\u7f51\u66dd\u9ed1\u6599', '71'), ('\u841d\u8389\u5c11\u5973', '73'),
    ('\u540c\u6027\u4e16\u754c', '70'), ('\u5236\u670d\u8bf1\u60d1', '69'), ('\u7f51\u66dd\u5403\u74dc', '67'), ('\u95e8\u4e8b\u4ef6', '72'),
]

# \u63a2\u6d3b\u6df1\u94fe\uff1a\u89c6\u9891\u4e00\u533a\u7b2c\u4e00\u9875\uff08\u4efb\u4f55\u6d3b\u8282\u70b9\u90fd 200+video-info\uff09
_PROBE_PATH = '/vodtype/45-1/'
_MARK = 'video-info'

# \u5185\u7f6e\u5019\u9009\uff08iegeewiet-4mag=xbpq \u539f\u57df\uff1b7y9m1.cc \u65cf\u6765\u81ea maccms \u914d\u7f6e\uff1b\u5176\u4f59\u6cdb\u89e3\u6790\u968f\u673a\u8bcd\u515c\u5e95\uff09
_BUILTIN_HOSTS = [
    'https://iegeewiet-4mag.hscwang26y2m.xyz',
    'https://www.hscwang26y2m.xyz',
    'https://aesonged-onu5a.hscwang7y9m1.cc',
]
_WILDCARD_BASES = ['hscwang26y2m.xyz', 'hscwang7y9m1.cc']

_RE_ITEM = re.compile(r'<li><a class="thumbnail" href="/voddetail/(\d+)/">(.*?)</li>', re.S)
_RE_IMG = re.compile(r'(?:data-original|src)="(https?://[^"]+)"')
_RE_TITLE = re.compile(r'<h5><a[^>]*>(.*?)</a></h5>', re.S)
_RE_MARK = re.compile(r'<p>(.*?)</p>', re.S)
_RE_PAGE = re.compile(r'/vodtype/(?:\d+)-(\d+)/')
_RE_PLAYER = re.compile(r'var\s+player_aaaa\s*=')
_AD_MARK = 'xn-tokaa2|fanpppas|jidi21df|ivvpdh'


def _clean(s):
    return _html.unescape(re.sub(r'<[^>]+>', '', s or '')).replace('\xa0', ' ').strip()


# \u5206\u96c6\u540d\u5e7f\u544a\u9ed1\u540d\u5355\uff08\u5bf9\u9f50\u6bcf\u65e5\u5927\u8d5b._valid_ep_name \u7eaa\u5f8b\uff09
_AD_NAME_RE = re.compile('(<|http|www\\.|\\.com|\\.cc|\u516c\u4f17\u53f7|\u5173\u6ce8|\u798f\u5229|\u66f4\u591a|APP|app|\u4e0b\u8f7d|\u5730\u5740\u53d1\u5e03|\u6700\u65b0\u5730\u5740)')


class Spider(BaseSpider):

    # \u8bca\u65ad\u680f\u76ee\uff08\u4e34\u65f6\u8bbe\u65bd\uff1a\u771f\u673a\u9a8c\u8bc1\u901a\u8fc7\u540e\u6574\u4f53\u79fb\u9664\uff09
    DIAG_TID = '__diag__'

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
        return "\u6781\u4e50\u7981\u533a"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def localProxy(self, params):
        return [200, "video/MP2T", ""]

    def _http(self, url, headers=None, timeout=8):
        # requests \u76f4\u8fde\u5305\u88c5\u3002\u26a0\u523b\u610f\u4e0d\u53eb fetch\uff1aApp \u57fa\u7c7b\u6709\u540c\u540d\u65b9\u6cd5\uff08\u649e\u540d=\u96f6\u6570\u636e\u6839\u56e0\uff09\u3002
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
        """\u63a2\u6df1\u94fe\u3002host_base \u542b\u534f\u8bae\u4e0d\u542b\u8def\u5f84\u3002"""
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
        """hostresolver \u7528\u7684\u5019\u9009\uff1aext + \u5185\u7f6e\uff08\u4e0d\u542b\u968f\u673a\u8bcd\uff0c\u63a7\u5236\u6700\u574f\u8017\u65f6\uff09\u3002"""
        cands = []
        if self._ext.get('host'):
            cands.append(self._ext['host'])
        cands += list(self._ext.get('hosts') or [])
        for u in _BUILTIN_HOSTS:
            if u not in cands:
                cands.append(u)
        return cands

    def _cands_random(self, n=8):
        """\u6cdb\u89e3\u6790\u4efb\u610f\u8bcd\u5747\u89e3\u6790\uff1a\u968f\u673a\u8bcd\u6269\u6c60\uff08\u4e0d\u540c\u8bcd=\u4e0d\u540c\u8282\u70b9\uff09\u3002"""
        out, seen = [], set(self._candidate_hosts())
        while len(out) < n:
            base = random.choice(_WILDCARD_BASES)
            w = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6))
            u = 'https://%s.%s' % (w, base)
            if u in seen:
                continue
            seen.add(u)
            out.append(u)
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
        \u4e24\u6bb5\u5f0f\uff1a\u5148\u5185\u7f6e\uff088s \u95f8\uff09\uff0c\u5168\u5931\u8d25\u518d\u968f\u673a\u8bcd\u6269\u6c60\uff088s \u95f8\uff09\u3002"""
        h = self._probe_round(self._candidate_hosts(), 8)
        if h:
            return h
        self.trace.append('\u5185\u7f6e\u672a\u547d\u4e2d\uff0c\u968f\u673a\u8bcd\u6269\u6c60')
        return self._probe_round(self._cands_random(8), 8)

    def get_working_host(self):
        # \u9501\u5b9a\u57df\uff1a\u586b\u4e86 host@ \u5c31\u53ea\u7528\u5b83
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
                                tag='\u6781\u4e50\u7981\u533a\u515c\u5e95')
                if h:
                    return h.rstrip('/')
            except Exception:
                pass
        return self._resolve_inline(None)

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

    # ---------- \u8bca\u65ad\uff08\u4e34\u65f6\u8bbe\u65bd\uff0c\u771f\u673a\u9a8c\u8bc1\u901a\u8fc7\u540e\u79fb\u9664\uff09 ----------
    def _diag_lines(self):
        lines = [
            '\u6a21\u5757: hostresolver=%s probe_first=%s parse_ext=%s' % (
                '\u6709' if resolve_host else '\u65e0', '\u6709' if probe_first else '\u65e0',
                '\u6709' if parse_ext else '\u65e0'),
            'ext: %s' % json.dumps(self._ext, ensure_ascii=False),
            'host: %s' % self.host,
        ]
        r = self._http(self.host + _PROBE_PATH, timeout=8)
        if r:
            lines.append('\u72ec\u7acb\u5b9e\u6d4b: %s %s %s' % (
                r.status_code, len(r.text or ''),
                '\u542b\u7ad9\u540d\u6807\u8bb0' if _MARK in (r.text or '') else '\u2757\u65e0\u7ad9\u540d\u6807\u8bb0'))
        else:
            lines.append('\u72ec\u7acb\u5b9e\u6d4b: \u8bf7\u6c42\u5931\u8d25')
        lines += ['trace] ' + x for x in self.trace[:12]]
        return lines

    # ---------- \u63a5\u53e3 ----------
    def homeContent(self, filter):
        classes = [{'type_name': n, 'type_id': tid} for n, tid in _CATS]
        classes.append({'type_name': '\u26a0\u8bca\u65ad', 'type_id': self.DIAG_TID})
        return {'class': classes, 'filters': {}}

    def homeVideoContent(self):
        # App \u9996\u9875\u5237\u65b0\u7684\u63a8\u8350\u4f4d\u8d70\u8fd9\u91cc\u2014\u2014\u6293 /jlhs\uff08\u6700\u65b0\u805a\u5408\u9875\uff0c\u5b9e\u6d4b 60 \u6761\uff09
        try:
            self._ensure_host()
            res = self._http(self.host + '/jlhs')
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
            vid, chunk = m.group(1), m.group(2)
            img = _RE_IMG.search(chunk)
            pic = img.group(1) if img else ''
            t = _RE_TITLE.search(chunk)
            name = _clean(t.group(1)) if t else ''
            mk = _RE_MARK.search(chunk)
            remark = _clean(mk.group(1))[:12] if mk else ''
            if vid and name:
                out.append({'vod_id': vid, 'vod_name': name,
                            'vod_pic': pic, 'vod_remarks': remark})
        return out

    def _pagecount(self, html):
        nums = [int(x) for x in _RE_PAGE.findall(html)]
        return max(nums) if nums else 1

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg or 1)
        if tid == self.DIAG_TID:
            lines = self._diag_lines()
            lst = [{'vod_id': 'diag', 'vod_name': l, 'vod_pic': '',
                    'vod_remarks': ''} for l in lines]
            return {'list': lst, 'page': 1, 'pagecount': 1, 'limit': len(lst),
                    'total': len(lst)}
        self._ensure_host()
        url = '%s/vodtype/%s-%d/' % (self.host, tid, pg)
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
        url = '%s/vodsearch/%s----------%d---/' % (self.host, key, pg)
        res = self._http(url)
        if not res or res.status_code != 200:
            return {'list': []}
        return {'list': self._parse_list(res.text or ''), 'page': pg}

    def detailContent(self, ids):
        vid = ids[0]
        self._ensure_host()
        url = '%s/voddetail/%s/' % (self.host, vid)
        res = self._http(url)
        if not res or res.status_code != 200:
            return {'list': []}
        html = res.text or ''
        tt = re.search(r'<title>(.*?)</title>', html, re.S)
        name = _clean(tt.group(1)) if tt else str(vid)
        pic = ''
        for m in re.finditer(r'(https?://[^"\']+/[^"\']+\.(?:jpg|png|webp)[^"\']*)', html):
            pic = m.group(1)
            break
        # \u5206\u96c6\uff08\u77ed\u7247\u7ad9\u591a\u4e3a\u5355\u96c6\uff1b\u951a\u6587\u672c\u5e38\u4e3a\u7a7a \u2192 \u6309\u94fe\u63a5\u5e8f\u53f7\u751f\u6210\u300c\u7b2cN\u96c6\u300d\uff09
        eps = []
        for m in re.finditer(r'<a[^>]*href="(/vodplay/(\d+)-(\d+)-(\d+)/)"[^>]*>(.*?)</a>', html, re.S):
            path, nid, text = m.group(1), m.group(4), _clean(m.group(5))
            ep_name = self._valid_ep_name(text) or ('\u7b2c%s\u96c6' % nid if int(nid) > 1 else '\u64ad\u653e')
            eps.append('%s$%s' % (ep_name, path))
        if not eps:
            eps = ['\u64ad\u653e$/vodplay/%s-1-1/' % vid]
        vod = {
            'vod_id': vid,
            'vod_name': name,
            'vod_pic': pic,
            'vod_content': '\u8d44\u6e90\u6765\u81ea\u4e8e\u7f51\u7edc\uff0c\u8bf7\u52ff\u76f8\u4fe1\u4efb\u4f55\u5e7f\u544a',
            'vod_play_from': '\u6781\u4e50\u7981\u533a',
            'vod_play_url': '#'.join(eps),
        }
        return {'list': [vod]}

    def _valid_ep_name(self, s, max_len=20):
        """\u5206\u96c6\u540d\u6e05\u6d17\uff08\u5bf9\u9f50\u5df2\u9a8c\u8bc1\u6e90\u7eaa\u5f8b\uff09\uff1a\u7a7a\u3001\u8d85\u957f\u3001\u547d\u4e2d\u5e7f\u544a\u9ed1\u540d\u5355 \u2192 \u8fd4\u56de ''\u3002"""
        s = _clean(s)
        if not s or len(s) > max_len or _AD_NAME_RE.search(s):
            return ''
        return s

    def playerContent(self, flag, id, vipFlags=None):
        # id \u5f62\u5982 /vodplay/422002-1-1/ \u6216 422002-1-1
        path = id if str(id).startswith('/') else '/vodplay/%s/' % id
        self._ensure_host()
        play_url = self.host + path
        res = self._http(play_url)
        if not res or res.status_code != 200:
            return {'parse': 1, 'url': play_url}
        real = ''
        html = res.text or ''
        m = _RE_PLAYER.search(html)
        if m:
            try:
                cfg, _ = json.JSONDecoder().raw_decode(html[m.end():].lstrip())
                real = cfg.get('url', '') or ''
                if str(cfg.get('encrypt', '0')) == '1' and real:
                    import base64
                    real = base64.b64decode(real).decode('utf-8')
            except Exception:
                real = ''
        if not real:
            mm = re.search(r'(https?://[^"\'\\\s]+\.m3u8[^"\'\\\s]*)', html)
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
