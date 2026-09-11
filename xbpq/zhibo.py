# -*- coding: utf-8 -*-
import json
import sys
import traceback
import requests
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    primary_host = 'http://api.hclyz.com:81/mf/'
    backup_host = 'http://api.maiyoux.com:81/mf/'
    host = primary_host
    platforms = []

    def fetch(self, url, params=None, cookies=None, headers=None, timeout=10, verify=True,
              stream=False, allow_redirects=True):
        """requests \u76f4\u8fde\uff082026-09-11 \u6539\uff09\u3002

        \u539f\u5b9e\u73b0\u7ee7\u627f App base \u7c7b\u7684 fetch\uff1b\u4e00\u65e6\u5176\u8fd4\u56de\u7c7b\u578b\u4e0e rsp.text \u9884\u671f\u4e0d\u7b26\uff0c
        init \u91cc platforms \u5c31\u4f1a\u662f\u7a7a\u5217\u8868 \u2192 \u9996\u9875 0 \u5206\u7c7b\uff082026-09-11 \u955c\u50cf\u5b9e\u6d4b \u5206\u7c7b0\uff09\u3002
        \u4e0e\u7981\u7247\u5929\u5802/UAA\u97f3\u753b\u540c\u6b3e\u6839\u56e0\uff0c\u6539\u76f4\u8fde\u4e0e\u5168\u5e93\u7eaa\u5f8b\u5bf9\u9f50\u3002\u5f02\u5e38\u8fd4\u56de None\u3002"""
        h = headers or {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'}
        try:
            return requests.get(url, params=params, headers=h, cookies=cookies,
                                timeout=timeout, verify=False, stream=stream,
                                allow_redirects=allow_redirects)
        except Exception as e:
            try:
                print('[\u76f4\u64ad] fetch \u5f02\u5e38 %s \u2192 %s' % (str(url)[:70], str(e)[:60]))
            except Exception:
                pass
            return None

    def init(self, extend=""):
        if extend:
            h = extend.strip()
            if not h.endswith('/'):
                h += '/'
            self.host = h
        else:
            self.host = self.primary_host

        content = None
        for base in [self.host, self.backup_host]:
            try:
                txt = self.fetch(base + 'json.txt').text
                data = None
                try:
                    data = json.loads(txt)
                except Exception:
                    data = None

                if data is not None:
                    self.host = base
                    self.platforms = self._parse_catalog_json(data)
                    if self.platforms:
                        return
                else:
                    plats = self._parse_catalog_text(txt)
                    if plats:
                        self.host = base
                        self.platforms = plats
                        return
            except Exception:
                continue

    def _parse_catalog_json(self, data):
        items = []
        if isinstance(data, dict):
            if 'pingtai' in data and isinstance(data['pingtai'], list):
                items = data['pingtai']
            else:
                if all(isinstance(v, dict) for v in data.values()):
                    items = list(data.values())
        elif isinstance(data, list):
            items = data

        platforms = []
        for it in items:
            name = it.get('mc') or it.get('title') or it.get('name') or ''
            img = it.get('tp1') or it.get('xinimg') or it.get('img') or ''
            file = it.get('dz') or it.get('address') or it.get('file') or ''
            count = it.get('sl') or it.get('Number') or it.get('count') or 0
            try:
                count = int(count)
            except Exception:
                pass
            if name and file:
                if not file.endswith('.txt'):
                    file += '.txt'
                if not file.startswith('json'):
                    file = 'json' + file
                platforms.append({
                    'name': name,
                    'img': img,
                    'file': file,
                    'count': count
                })
        return platforms

    def _parse_catalog_text(self, txt):
        plats = []
        block = txt.strip()
        if not block:
            return plats
        if block.startswith('{') and block.endswith('}'):
            block = block[1:-1]
        chunks = [c for c in block.split('|') if c.strip()]
        curr = {'mc': '', 'tp1': '', 'dz': '', 'sl': 0}
        def flush():
            if curr.get('mc') and curr.get('dz'):
                try:
                    sl = int(curr.get('sl') or 0)
                except Exception:
                    sl = curr.get('sl') or 0
                fname = curr.get('dz')
                if not fname.endswith('.txt'):
                    fname += '.txt'
                if not fname.startswith('json'):
                    fname = 'json' + fname
                plats.append({
                    'name': curr.get('mc'),
                    'img': curr.get('tp1'),
                    'file': fname,
                    'count': sl
                })
        for c in chunks:
            s = c.strip()
            if s.startswith('@mc'):
                if curr.get('mc') or curr.get('dz'):
                    flush()
                    curr = {'mc': '', 'tp1': '', 'dz': '', 'sl': 0}
                curr['mc'] = s.replace('@mc', '', 1)
            elif s.startswith('@tp1'):
                curr['tp1'] = s.replace('@tp1', '', 1)
            elif s.startswith('@dz'):
                curr['dz'] = s.replace('@dz', '', 1)
            elif s.startswith('@sl'):
                curr['sl'] = s.replace('@sl', '', 1)
        if curr.get('mc') or curr.get('dz'):
            flush()
        return plats

    def _load_platform_rooms(self, file_path, pg=1):
        url_candidates = [
            self.host + file_path,
        ]
        alt_path = file_path.replace('json', '', 1)
        if alt_path != file_path:
            url_candidates.insert(0, self.host + alt_path)

        data = None
        raw = None
        for u in url_candidates:
            try:
                raw = self.fetch(u).text
                data = json.loads(raw)
                break
            except Exception:
                data = None
                continue

        rooms = []
        if isinstance(data, dict):
            if 'zhubo' in data and isinstance(data['zhubo'], list):
                rooms = data['zhubo']
            elif 'list' in data and isinstance(data['list'], list):
                rooms = data['list']
            elif 'data' in data and isinstance(data['data'], list):
                rooms = data['data']
            elif 'rooms' in data and isinstance(data['rooms'], list):
                rooms = data['rooms']
        elif isinstance(data, list):
            rooms = data

        videos = []
        for idx, r in enumerate(rooms or [], 1):
            title = r.get('title') or r.get('name') or r.get('nickname') or f'主播{idx}'
            address = r.get('address') or r.get('url') or r.get('stream') or ''
            img = r.get('img') or r.get('pic') or r.get('avatar') or ''
            remarks = r.get('Number') or r.get('online') or r.get('viewers') or ''
            if title and address:
                videos.append({
                    'vod_id': address,
                    'vod_name': title,
                    'vod_pic': img,
                    'vod_remarks': str(remarks)
                })
        total = len(videos)
        if pg > 1:
            start = (pg - 1) * 20
            videos = videos[start:start + 20]
        return videos, total

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        pass

    def getName(self):
        return 'Leospring\u76f4\u64ad'

    def homeContent(self, filter):
        classes = []
        for p in self.platforms:
            classes.append({
                'type_id': p['file'],
                'type_name': p['name'],
            })
        return {'class': classes}

    def homeVideoContent(self):
        return {'list': []}

    def _find_platform(self, tid):
        for p in self.platforms:
            if p['file'] == tid or p['name'] == tid:
                return p
        return None

    def categoryContent(self, tid, pg, filter, extend):
        p = self._find_platform(tid)
        if not p:
            return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 0, 'total': 0}
        
        videos, total = self._load_platform_rooms(p['file'], int(pg))
        pagecount = (total + 19) // 20
        result = {
            'list': videos,
            'page': pg,
            'pagecount': pagecount,
            'limit': min(len(videos), 20),
            'total': total
        }
        return result

    def searchContent(self, key, quick, pg="1"):
        key = (key or '').strip().lower()
        out = []
        if not key:
            return {'list': out}
        for p in self.platforms:
            videos, _ = self._load_platform_rooms(p['file'])
            for v in videos:
                if key in v['vod_name'].lower():
                    out.append(v)
            if len(out) >= 50:
                break
        return {'list': out[:50]}

    def detailContent(self, ids):
        try:
            address = ids[0]
            if not address:
                return {'list': []}
            
            vod = {
                'vod_id': address,
                'vod_name': '\u76f4\u64ad\u6e90',
                'vod_play_from': '\u6bcf\u65e5\u5fc5\u4fee\u8bfe',
                'vod_play_url': address,
                'vod_content': '\u591a\u770b\u5c11\u6253\u5361',
            }
            return {'list': [vod]}
        except Exception as e:
            traceback.print_exc()
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        return {
            'parse': 0,
            'url': id
        }

    def localProxy(self, param):
        pass
