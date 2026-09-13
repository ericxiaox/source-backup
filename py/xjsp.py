# coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
import re
import random
import requests
from base64 import b64decode

try:
    import urllib3
    urllib3.disable_warnings()
except Exception:
    pass


class Spider(Spider):
    """\u9999\u8549\u89c6\u9891 \u2014\u2014 2026-09-10 \u5168\u91cf\u91cd\u505a\u3002

    \u6362\u5f62\u6001\u8bf4\u660e\uff1a\u8001\u7ad9\uff08\u82f9\u679cCMS\uff0c/index.php/vod/...\uff09\u5df2\u5e9f\u5f03\uff0c\u4e3b\u57df 618013.xyz \u53d8\u6210\u505c\u653e\u9875\u3002
    \u73b0\u5f79\u5f62\u6001\u662f\u300c\u5b98\u7f51 + H5 \u7ad9\u300d\u4e24\u6761\u817f\uff1a
      \u00b7 \u5b98\u7f51  www.xjxjxj.co\uff08302 \u2192 \u5f53\u524d\u4e3b\u57df\uff09\uff0c\u5176 /static/js/config.js \u66b4\u9732 h5_url
      \u00b7 H5 \u7ad9 h5_url \u6307\u5411\u7684\u57df\uff0c\u627f\u8f7d\u5168\u90e8\u5185\u5bb9\u63a5\u53e3\uff08\u524d\u540e\u7aef\u5206\u79bb SPA\uff0c\u63a5\u53e3\u5728 /api/*\uff09
    \u672c\u6e90\u53ea\u5bf9\u63a5 H5 \u63a5\u53e3\uff1b\u5b98\u7f51\u4ec5\u5f53\u300c\u53d1\u5e03\u9875\u300d\u7528\u2014\u2014\u4ece config.js \u91cc\u62a0\u51fa\u5f53\u524d h5_url\u3002

    \u53d6\u57df\u94fe\uff08get_working_host\uff09\uff1a
      ext host@ \u9501 > \u53d1\u5e03\u9875 config.js \u7684 h5_url > ext hosts@ + \u5185\u7f6e\u5019\u9009\u4f9d\u6b21\u5b9e\u6d4b > \u5185\u7f6e\u9996\u4e2a\u515c\u5e95
      \u2014\u2014 \u4e0d\u9501\u6b7b\u5355\u57df\uff1a\u7ad9\u70b9\u6362\u57df\u65f6\u53d1\u5e03\u9875\u4f1a\u540c\u6b65\u66f4\u65b0\uff0c\u6e90\u81ea\u52a8\u8ddf\u4e0a\u3002

    \u63a5\u53e3\u4e00\u89c8\uff08base = {host}/api\uff09\uff1a
      GET /init                                  \u2192 globalData.hotcategories\uff08\u5206\u7c7b\u8868\uff0c\u52a8\u6001\u53d6\uff09
      GET /vod/latest-{9\u53c2\u6570}-{page}              \u2192 \u6700\u65b0\u5217\u8868\uff08\u9996\u9875\uff09
      GET /v2/vod/listing-{9\u53c2\u6570}-{page}          \u2192 \u5206\u7c7b\u5217\u8868
      GET /search?wd=&page=&free=1               \u2192 \u641c\u7d22
      GET /vod/show/{id}                         \u2192 \u8be6\u60c5
      GET /v2/vod/reqplay/{id}                   \u2192 \u64ad\u653e\u5730\u5740\uff08m3u8\uff09
    listing \u7684 9 \u4e2a\u4f4d\u7f6e\u53c2\u6570\u987a\u5e8f\uff1a
      cateid-areaid-yearid-definition-duration-freetype-mosaic-langvoice-orderby
    """

    # \u53d1\u5e03\u9875\uff08\u7ad9\u70b9\u6362\u57df\u65f6\u8fd9\u91cc\u7684\u5185\u5bb9\u4f1a\u540c\u6b65\u53d8\uff0c\u662f\u672c\u6e90\u7684\u300c\u6d3b\u5730\u5740\u6e90\u300d\uff09
    PUBLISH_PAGES = [
        'https://www.xjxjxj.co/static/js/config.js',
        'https://www.xjxjxj.co/',
        'https://www.xjxj459.org/static/js/config.js',
    ]
    # \u5185\u7f6e\u5019\u9009 H5 \u57df\uff08\u65b0\u2192\u65e7\uff09\uff1bext \u7684 hosts@ \u4f1a\u6392\u5230\u5b83\u4eec\u524d\u9762
    CANDIDATE_HOSTS = ['https://h5.xxoox35.org', 'https://h5.xxoo168.org']
    # \u5206\u7c7b\u515c\u5e95\u8868\uff08/init \u53d6\u4e0d\u5230\u65f6\u7528\uff1bb64 \u5b58\u653e\uff0c\u9632\u6258\u7ba1\u5e73\u53f0\u5173\u952e\u8bcd\u626b\u63cf\uff09
    CLASS_FALLBACK_B64 = 'W3sidHlwZV9pZCI6IjAtMC0wLTAtMC0wLTItMC0wIiwidHlwZV9uYW1lIjoi5peg56CB6KeG6aKRIn0seyJ0eXBlX2lkIjoiNC0wLTAtMC0wLTAtMi0wLTAiLCJ0eXBlX25hbWUiOiLlgbfmi43oh6rmi40ifSx7InR5cGVfaWQiOiI1LTAtMC0wLTAtMC0wLTAtMCIsInR5cGVfbmFtZSI6IuWItuacjeivseaDkSJ9LHsidHlwZV9pZCI6IjktMC0wLTAtMC0wLTAtMC0wIiwidHlwZV9uYW1lIjoi57Sg5Lq65Ye65ryUIn0seyJ0eXBlX2lkIjoiMTQtMC0wLTAtMC0wLTAtMC0wIiwidHlwZV9uYW1lIjoi57uP5YW45LiJ57qnIn0seyJ0eXBlX2lkIjoiMC0zLTAtMC0wLTAtMC0xLTAiLCJ0eXBlX25hbWUiOiLkuK3mloflrZfluZUifSx7InR5cGVfaWQiOiI3LTMtMC0wLTAtMC0wLTAtMCIsInR5cGVfbmFtZSI6IuaXpeacrOi+o+WmuSJ9LHsidHlwZV9pZCI6IjExLTAtMC0wLTAtMC0wLTAtMCIsInR5cGVfbmFtZSI6IuaIkOS6uuWKqOa8qyJ9LHsidHlwZV9pZCI6IjAtNi0wLTAtMC0wLTAtMC0wIiwidHlwZV9uYW1lIjoi5qyn576O5r+A5oOFIn0seyJ0eXBlX2lkIjoiMC01LTAtMC0wLTAtMC0wLTIiLCJ0eXBlX25hbWUiOiLpn6nlm73ng63mkq0ifSx7InR5cGVfaWQiOiIwLTAtMy0wLTAtMC0wLTAtMiIsInR5cGVfbmFtZSI6IjIwMjLmlrDniYcifSx7InR5cGVfaWQiOiIxMy0wLTAtMC0wLTAtMC0wLTAiLCJ0eXBlX25hbWUiOiLlj5jmgIHlj6bnsbsifV0='
    # \u63a2\u9488\uff1areqplay/1 \u53ea\u6709\u51e0\u767e\u5b57\u8282\uff0c\u9a8c\u6d3b\u6700\u5feb
    PROBE = '/v2/vod/reqplay/1'

    def getName(self):
        return "\u9999\u8549\u89c6\u9891"

    def init(self, extend=""):
        try:
            from hostresolver import ext_of
        except Exception:
            ext_of = None
        self.proxies = {}
        self._ext = {}
        if ext_of:
            try:
                self._ext = ext_of(extend) or {}
            except Exception:
                self._ext = {}
        if self._ext.get('proxies'):
            self.proxies = self._ext['proxies']
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
        }
        self.host = self.get_working_host()
        self.headers['Referer'] = self.host + '/'
        self.log(f"香蕉视频初始化完成，API域: {self.host}")

    # ========== \u53d6\u57df ==========

    def get_working_host(self):
        """\u53d6\u5f53\u524d\u53ef\u7528 API \u57df\uff1aext host@ \u9501 > \u53d1\u5e03\u9875 h5_url > hosts@ + \u5185\u7f6e\u5019\u9009\u5b9e\u6d4b > \u5185\u7f6e\u9996\u4e2a\u515c\u5e95\u3002"""
        lock = self._ext.get('host')
        if lock:
            return str(lock).rstrip('/')
        cands = []
        for h in (self._ext.get('hosts') or []):
            h = str(h).strip().rstrip('/')
            if h and h not in cands:
                cands.append(h)
        for h in self.CANDIDATE_HOSTS:
            if h not in cands:
                cands.append(h)
        pub = self._ext.get('publish')
        # \u591a\u53d1\u5e03\u9875\uff082026-09-13\uff09\uff1aext \u7684 publish@ \u53ef\u80fd\u662f\u9017\u53f7\u4e32\uff08\u7f51\u5740\u578b + GitHub \u578b\u5e76\u5b58\uff09\uff0c
        # \u5148\u62c6\u5f00\uff0c\u518d\u62fc\u5185\u7f6e\u53d1\u5e03\u9875\u6e05\u5355\uff0c\u4e00\u8d77\u5e76\u884c\u6293\u3002
        pub_pages = [x for x in re.split(r'[,\s;]+', str(pub or '')) if x.startswith('http')]
        pages = pub_pages + self.PUBLISH_PAGES
        h = self._host_from_publish(pages)
        if h:
            if h in cands:
                cands.remove(h)
            cands.insert(0, h)
        import threading
        result = [None]
        def _p(c):
            if result[0]:
                return
            if self._alive(c):
                result[0] = c
        threads = [threading.Thread(target=_p, args=(c,)) for c in cands]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
        return result[0] or (cands[0] if cands else '')

    def _host_from_publish(self, pages):
        """\u4ece\u53d1\u5e03\u9875\u62a0\u5f53\u524d h5_url\uff08config.js \u662f\u7eaf JS \u914d\u7f6e\uff0c\u6b63\u5219\u6700\u7a33\uff09\u3002

        \u591a\u53d1\u5e03\u9875**\u5e76\u884c**\u6293\u53d6\uff082026-09-13\uff09\uff1aN \u9875\u8017\u65f6 \u2248max\uff08\u539f\u4e3a\u9010\u9875\u4e32\u884c\uff0c\u7ad9\u65b9\u9875\u6162\u65f6
        \u51b7\u542f\u52a8\u767d\u7b49 N\u00d78s\uff09\uff1b\u4efb\u4e00\u9875\u5148\u547d\u4e2d\u5373\u91c7\u7528\uff0c\u5176\u4f59\u7ebf\u7a0b\u81ea\u7136\u7ed3\u675f\u3002"""
        import threading
        found = []
        _ua = self.headers['User-Agent']

        def _one(p):
            if found:
                return
            try:
                r = self._req(str(p), headers={'User-Agent': _ua}, timeout=8)
                if not r or r.status_code != 200:
                    return
                m = re.search(r'''["']h5_url["']\s*:\s*["'](https?://[^"']+)["']''', r.text)
                if m:
                    if not found:
                        found.append(m.group(1).strip().rstrip('/'))
                    return
                m2 = re.search(r'https?://h5\.[a-zA-Z0-9.\-]+', r.text)
                if m2 and not found:
                    found.append(m2.group(0).strip().rstrip('/'))
            except Exception:
                return

        ths = [threading.Thread(target=_one, args=(p,)) for p in pages]
        for t in ths:
            t.start()
        for t in ths:
            t.join(timeout=8)
        return found[0] if found else ''

    def _alive(self, host):
        """\u9a8c\u6d3b\uff1a\u80fd\u62ff\u5230 retcode \u5373\u89c6\u4e3a\u53ef\u7528\u63a5\u53e3\u57df\u3002"""
        try:
            r = self._req(str(host).rstrip('/') + '/api' + self.PROBE, timeout=8)
            if not r or r.status_code != 200:
                return False
            d = r.json()
            return isinstance(d, dict) and 'retcode' in d
        except Exception:
            return False

    # ========== \u53d6\u6570\u57fa\u7840 ==========

    def _req(self, url, headers=None, params=None, timeout=15):
        """\u7edf\u4e00\u53d6\u9875\uff1arequests \u76f4\u8fde\uff08\u5168\u5e93\u7eaa\u5f8b\uff0c\u4e0d\u7528 self.fetch\uff09\uff0cverify=False \u5bb9\u5fcd\u81ea\u7b7e\u8bc1\u4e66\u3002"""
        try:
            return requests.get(url, headers=headers or self.headers, params=params,
                                proxies=self.proxies, timeout=timeout, verify=False)
        except Exception as e:
            self.log(f"请求失败 {url}: {str(e)}")
            return None

    def _get_json(self, path, params=None, host=None):
        """\u53d6\u63a5\u53e3 JSON\uff08path \u4ece / \u5f00\u5934\uff0c\u5982 /vod/show/1\uff09\u3002"""
        base = str(host or self.host).rstrip('/')
        url = base + '/api' + (path if path.startswith('/') else '/' + path)
        r = self._req(url, params=params)
        if not r or r.status_code != 200:
            self.log(f"接口异常 {url} -> {getattr(r, 'status_code', 'None')}")
            return {}
        try:
            d = r.json()
            return d if isinstance(d, dict) else {}
        except Exception:
            return {}

    # ========== \u5217\u8868/\u8be6\u60c5 ==========

    def _fix_pic(self, pic):
        """\u5c01\u9762\u8865\u5168\uff1a{rand} \u5360\u4f4d\u7b26\u968f\u673a\u5316\uff08\u8001\u6570\u636e\u9057\u7559\uff09\u3001\u76f8\u5bf9\u8def\u5f84\u8865\u57df\u3002"""
        if not pic:
            return ''
        if '{rand}' in pic:
            pic = pic.replace('{rand}', str(random.randint(1, 9)))
        if pic.startswith('//'):
            pic = 'https:' + pic
        elif pic.startswith('/'):
            pic = self.host + pic
        return pic

    def _rows(self, rows):
        """\u7edf\u4e00\u628a vodrows \u8f6c\u6210 Legado \u5217\u8868\u9879\u3002"""
        out = []
        for r in rows or []:
            if not isinstance(r, dict):
                continue
            vid = str(r.get('vodid') or '').strip()
            title = (r.get('title') or '').strip()
            if not vid or not title:
                continue
            out.append({
                'vod_id': vid,
                'vod_name': title,
                'vod_pic': self._fix_pic(r.get('coverpic') or ''),
                'vod_remarks': (r.get('duration') or '').strip(),
                'vod_year': str(r.get('yearname') or '').strip(),
            })
        return out

    def _classes(self):
        """\u5206\u7c7b\u8868\uff1a\u4f18\u5148\u4ece /init \u52a8\u6001\u53d6\uff08\u5206\u7c7b\u4f1a\u53d8\uff0c\u5199\u6b7b\u4f1a\u8fc7\u671f\uff09\uff0c\u5931\u8d25\u56de\u843d\u5230\u5185\u7f6e\u8868\u3002"""
        d = self._get_json('/init')
        cats = (((d.get('data') or {}).get('globalData') or {}).get('hotcategories')) or []
        out = []
        for c in cats:
            if not isinstance(c, dict):
                continue
            m = re.search(r'listing-([0-9-]+)\.html', c.get('url') or '')
            if not m:
                continue
            seg = '-'.join(m.group(1).split('-')[:9])
            name = (c.get('catename') or '').strip()
            if seg and name:
                out.append({'type_id': seg, 'type_name': name})
        if out:
            return out
        try:
            return json.loads(b64decode(self.CLASS_FALLBACK_B64).decode('utf-8'))
        except Exception:
            return []

    def homeContent(self, filter):
        """\u9996\u9875\uff1a\u5206\u7c7b\u8868\uff08\u52a8\u6001\uff09+ \u6700\u65b0\u5217\u8868\u3002"""
        result = {'class': self._classes()}
        try:
            d = self._get_json('/vod/latest-0-0-0-0-0-0-0-0-0-1')
            result['list'] = self._rows((d.get('data') or {}).get('vodrows'))
        except Exception as e:
            self.log(f"首页出错: {str(e)}")
            result['list'] = []
        return result

    def homeVideoContent(self):
        """\u517c\u5bb9\u6027\u65b9\u6cd5\uff1a\u53ea\u8fd4\u56de\u6700\u65b0\u5217\u8868\u3002"""
        try:
            d = self._get_json('/vod/latest-0-0-0-0-0-0-0-0-0-1')
            return {'list': self._rows((d.get('data') or {}).get('vodrows'))}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        """\u5206\u7c7b\u5217\u8868\uff1atid = 9 \u6bb5\u53c2\u6570\u4e32\uff08cateid-areaid-...-orderby\uff09\uff0c\u517c\u5bb9\u7eaf\u6570\u5b57 cateid\u3002"""
        try:
            pg = int(pg or 1)
            if pg < 1:
                pg = 1
            tid = str(tid or '').strip()
            if '_' in tid:                      # \u517c\u5bb9\u65e7\u7f13\u5b58\u300c\u57df\u540d_1\u300d\u5f62\u6001
                tid = tid.split('_')[-1]
            if not re.match(r'^\d+(-\d+){8}$', tid):
                m = re.search(r'(\d+)', tid)
                cid = m.group(1) if m else '0'
                tid = f'{cid}-0-0-0-0-0-0-0-0'
            d = self._get_json(f'/v2/vod/listing-{tid}-{pg}')
            data = d.get('data') or {}
            pi = data.get('pageinfo') or {}
            return {
                'list': self._rows(data.get('vodrows')),
                'page': pg,
                'pagecount': int(pi.get('totalpage') or 999),
                'limit': int(pi.get('pagesize') or 16),
                'total': int(pi.get('total') or 0),
            }
        except Exception as e:
            self.log(f"分类出错: {str(e)}")
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        """\u641c\u7d22\uff1a/search?wd=&page=&free=1\uff08free=1 \u53ea\u641c\u514d\u8d39\u53ef\u64ad\u5185\u5bb9\uff09\u3002"""
        try:
            d = self._get_json('/search', params={'wd': key, 'page': pg, 'free': 1})
            return {'list': self._rows((d.get('data') or {}).get('vodrows'))}
        except Exception as e:
            self.log(f"搜索出错: {str(e)}")
            return {'list': []}

    def detailContent(self, ids):
        """\u8be6\u60c5\uff1a/vod/show/{id}\uff1b\u64ad\u653e\u6807\u8bc6\u7edf\u4e00\u7528 vodid\uff0c\u57df\u540d\u4e00\u5f8b\u8fd0\u884c\u65f6\u53d6\u3002"""
        try:
            vid = str(ids[0])
            if '_' in vid:                      # \u517c\u5bb9\u65e7\u7f13\u5b58\u300c\u57df\u540d_\u6570\u5b57\u300d
                vid = vid.split('_', 1)[1]
            d = self._get_json(f'/vod/show/{vid}')
            row = (d.get('data') or {}).get('vodrow') or {}
            if not row:
                self.log(f"详情为空: {vid}")
                return {'list': []}
            tags = row.get('tags') or []
            actor = ''
            if isinstance(tags, list):
                actor = ','.join([t.get('tagname', '') for t in tags if isinstance(t, dict) and t.get('tagname')])
            real_id = str(row.get('vodid') or vid)
            info = {
                'vod_id': real_id,
                'vod_name': row.get('title') or '',
                'vod_pic': self._fix_pic(row.get('coverpic') or ''),
                'type_name': row.get('catename') or '',
                'vod_year': str(row.get('yearname') or ''),
                'vod_area': row.get('areaname') or '',
                'vod_remarks': row.get('duration') or '',
                'vod_actor': actor,
                'vod_director': '',
                'vod_content': (row.get('intro') or '').strip() or '\u65e0\u7b80\u4ecb',
                'vod_play_from': '\u9999\u8549\u89c6\u9891',
                'vod_play_url': f"播放${real_id}",
            }
            return {'list': [info]}
        except Exception as e:
            self.log(f"详情出错: {str(e)}")
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        """\u64ad\u653e\uff1a/v2/vod/reqplay/{id} \u76f4\u63a5\u7ed9 m3u8\uff1bretcode=3 \u65f6\u7528\u9884\u89c8\u5730\u5740\uff0c\u53d6\u4e0d\u5230\u5219\u56de\u843d\u7f51\u9875\u3002"""
        try:
            vid = str(id)
            if '_' in vid:
                vid = vid.split('_', 1)[1]
            d = self._get_json(f'/v2/vod/reqplay/{vid}')
            data = d.get('data') or {}
            url = ''
            if d.get('retcode') == 3:
                url = data.get('httpurl_preview') or ''
            if not url:
                url = data.get('httpurl') or ''
            if not url:
                urls = data.get('httpurls') or []
                if isinstance(urls, list) and urls:
                    first = urls[0]
                    url = (first.get('httpurl') or '') if isinstance(first, dict) else str(first)
            if url:
                url = url.replace('?300', '')
                self.log(f"播放地址: {url}")
                return {'parse': 0, 'playUrl': '', 'url': url}
            self.log(f"未取到播放地址 retcode={d.get('retcode')} msg={d.get('errmsg')}")
            return {'parse': 1, 'playUrl': '', 'url': self.host + '/'}
        except Exception as e:
            self.log(f"播放出错: {str(e)}")
            return {'parse': 1, 'playUrl': '', 'url': self.host + '/'}

    # ========== \u517c\u5bb9\u5360\u4f4d ==========

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass
