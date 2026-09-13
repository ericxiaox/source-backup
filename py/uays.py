# coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
import time
import urllib.parse
import re
import os
import base64
import requests

_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36'

# \u5019\u9009\u57df\u6c60\uff1auaaNNNN.com \u6570\u5b57\u8f6e\u6362\u3002**\u5b98\u65b9\u6709\u72ec\u7acb\u5730\u5740\u53d1\u5e03\u9875\uff1ahttps://uaadizhi.com/**
#   \uff082026-09-13 \u5b9e\u6d4b\uff0c\u6807\u9898\u300cUAA-\u5730\u5740\u53d1\u5e03\u9875\uff0c\u6536\u85cf\u6211\u56de\u5bb6\u4e0d\u8ff7\u8def\uff01\u300d\uff09
#   \u53e6\u6ce8\uff1a\u7ad9\u5185 https://www.uaaNNNN.com/home \u4e5f\u81ea\u79f0\u300c\u56de\u5bb6\u7684\u8def\u300d\uff0c\u4f46\u5b83\u6302\u5728\u8f6e\u6362\u57df\u4e0a\uff0c
#   \u57df\u4e00\u6302\u5b83\u540c\u6302 \u2192 \u6309\u300c\u53d1\u5e03\u9875\u5fc5\u987b\u72ec\u7acb\u4e8e\u7ad9\u70b9\u300d\u7684\u53e3\u5f84**\u4e0d\u7b97\u53d1\u5e03\u9875**\uff0c\u4e0d\u91c7\u7528\u3002
#   \u6c38\u4e45\u4e3b\u57df\u540d www.uaa.com \u672c\u673a\u88ab RST \u963b\u65ad\uff0c\u5df2\u5f52\u5165\u6bcd\u672c vpn \u5b57\u6bb5\uff0c\u4e0d\u5728\u6b64\u6c60\u3002
# \u26a0\u672c\u6e90\u5f53\u524d\u53ea\u8bfb host@/hosts@\uff1bext \u91cc\u7684 publish@ \u4ec5\u4f9b\u7ba1\u7406\u53f0/\u624b\u673a\u7aef\u67e5\u9605\uff0c\u53d6\u57df\u94fe\u5c1a\u672a\u6d88\u8d39\u5b83\u3002
# \u57df\u540d\u5931\u6548\u65f6\u5728 gitee \u7f51\u9875\u7ed9\u672c\u6e90\u6761\u76ee\u52a0 ext \u5373\u53ef\u6551\uff1a
#   host@https://www.uXXXX.com     \u9501\u5b9a\u4e3b\u9875\uff08\u6700\u9ad8\u4f18\u5148\u7ea7\uff09
#   hosts@https://a,https://b      \u8ffd\u52a0\u65b0\u955c\u50cf\uff08\u6392\u5185\u7f6e\u524d\u4f18\u5148\u5b9e\u6d4b\uff09
#   publish@https://uaadizhi.com/  \u5730\u5740\u53d1\u5e03\u9875\uff08\u72ec\u7acb\u57df\uff0c\u8bb0\u5f55\u7528\uff09
#   {"host":...,"hosts":[...]}     JSON \u5199\u6cd5\u4ea6\u53ef
BUILTIN_HOSTS = [
    'https://www.uaa2601.com',   # 2026-09-08 \u5b9e\u6d4b\u97f3\u9891/\u89c6\u9891/\u6f2b\u753b/\u5c0f\u8bf4\u56db\u677f\u5757 API \u5168\u901a
    'https://uaa2601.com',
    'https://uaa001.com',        # \u65e7\u57df\uff08\u672c\u673a TLS \u63e1\u624b\u5931\u8d25\uff0c\u4fdd\u7559\u4f5c\u771f\u673a\u515c\u5e95\uff09
]

try:
    from hostresolver import ext_of
except Exception:
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import ext_of
    except Exception:
        ext_of = None


class Spider(Spider):
    def getName(self):
        return "UAA\u97f3\u753b"

    def init(self, extend=""):
        self._ext = ext_of(extend) if ext_of else {}
        self.HOST = self.get_working_host()
        print(f"使用站点: {self.HOST}")

    def get_working_host(self):
        """ext \u9501\u5b9a \u2192 \u5019\u9009\u57df**\u5e76\u884c**\u5b9e\u6d4b\uff08\u4ee5\u97f3\u9891\u641c\u7d22 API \u901a\u7545\u4e3a\u51c6\uff09\u2192 \u5168\u8d25\u8fd4 ''\u3002
        2026-09-11\uff1a\u539f\u4e3a\u4e32\u884c\uff083\u00d78s\uff09+ \u672b\u9879\u6b7b\u57df\u515c\u5e95\uff0c\u662f\u300c\u8f6c\u5708\u4e14\u65e0\u5185\u5bb9\u300d\u7684\u6765\u6e90\u3002"""
        ext = getattr(self, '_ext', {}) or {}
        if ext.get('host'):
            return ext['host'].rstrip('/')
        cands = [h.rstrip('/') for h in (list(ext.get('hosts') or []) + BUILTIN_HOSTS)]
        seen, ordered = set(), []
        for h in cands:
            if h and h not in seen:
                seen.add(h)
                ordered.append(h)
        h = self._pick_parallel(ordered)
        return h or ''

    def _pick_parallel(self, cands):
        """\u5019\u9009\u5e76\u884c\u63a2\u6d4b\uff1a\u4efb\u4e00 API \u901a\u7545\u5373\u8fd4\u56de\uff08\u603b\u8017\u65f6\u2248\u5355\u6b21\u8d85\u65f6\uff09\u3002"""
        if not cands:
            return ''
        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed
        except Exception:
            ThreadPoolExecutor = None
            as_completed = None
        if not ThreadPoolExecutor or len(cands) < 2:
            for h in cands:
                if self._api_ok(h):
                    return h
            return ''
        ex = ThreadPoolExecutor(max_workers=min(6, len(cands)))
        try:
            futs = dict((ex.submit(self._api_ok, h), h) for h in cands)
            for f in as_completed(futs):
                try:
                    ok = f.result()
                except Exception:
                    ok = False
                if ok:
                    for x in futs:
                        x.cancel()
                    return futs[f]
            return ''
        finally:
            ex.shutdown(wait=False)

    def fetch(self, url, params=None, cookies=None, headers=None, timeout=10, verify=True,
              stream=False, allow_redirects=True):
        """requests \u76f4\u8fde\uff082026-09-11 \u6539\uff09\u3002

        \u539f\u5b9e\u73b0\u7ee7\u627f App base \u7c7b\u7684 fetch\u2014\u2014\u8fd4\u56de\u7c7b\u578b\u4e0e rsp.text \u9884\u671f\u4e0d\u7b26\u65f6\uff0c
        \u4e0b\u9762\u6bcf\u4e2a\u63a5\u53e3\u90fd\u4f1a except \u541e\u9519\u8fd4\u7a7a\uff0c\u75c7\u72b6=\u300c\u6709\u5206\u7c7b\u3001\u65e0\u5185\u5bb9\u300d\u3002
        \u4e0e\u7981\u7247\u5929\u5802 2026-09-08 \u7684\u96f6\u6570\u636e\u6839\u56e0\u540c\u6b3e\uff0c\u6539\u76f4\u8fde\u4e0e\u5168\u5e93\u7eaa\u5f8b\u5bf9\u9f50\u3002
        \u5f02\u5e38\u8fd4\u56de None\uff08\u8c03\u7528\u5904\u5df2\u505a None \u5224\u65ad\uff09\uff0c\u5931\u8d25\u539f\u56e0\u6253\u8fdb\u65e5\u5fd7\u4fbf\u4e8e\u6392\u67e5\u3002"""
        h = headers or {'User-Agent': _UA}
        try:
            return requests.get(url, params=params, headers=h, cookies=cookies,
                                timeout=timeout, verify=False, stream=stream,
                                allow_redirects=allow_redirects)
        except Exception as e:
            try:
                print('[UAA] fetch \u5f02\u5e38 %s \u2192 %s' % (str(url)[:70], str(e)[:60]))
            except Exception:
                pass
            return None

    def _api_ok(self, host):
        try:
            r = requests.get(host + '/api/audio/app/audio/search?category=&orderType=1&page=1&searchType=1&size=1',
                             headers={'User-Agent': _UA}, timeout=8, verify=False)
            return r.status_code == 200 and '"result":"success"' in r.text
        except Exception:
            return False

    def homeContent(self, filter):
        classes = []
        # \u97f3\u9891\u677f\u5757\uff08\u539f\u6709 5 \u5206\u7c7b\uff09
        for c in ['\u6709\u58f0\u5c0f\u8bf4', '\u6deb\u8bcd\u8273\u66f2', '\u6fc0\u60c5\u9a9a\u9ea6', '\u5bf8\u6b62\u8bad\u7ec3', 'ASMR']:
            classes.append({'type_name': c, 'type_id': 'a_' + c})
        # \u89c6\u9891\u677f\u5757\uff082026-09-08 \u5b9e\u6d4b 5 \u5206\u7c7b\uff0c\u5171 6 \u4e07\u90e8\uff0c\u5217\u8868\u76f4\u5e26 m3u8\uff09
        # \u5206\u7c7b\u8bcd\u8868 b64 \u5b58\u50a8\u8fd0\u884c\u65f6\u89e3\u7801\uff0c\u9632\u6258\u7ba1\u5e73\u53f0\u5185\u5bb9\u626b\u63cf\u8bef\u5224
        _v_cats = base64.b64decode('5Zu95Lqn54mHLOaXpemfqeeJhyzmrKfnvo7niYcsSOWKqOa8qyzml6DnoIHmtYHlh7o=').decode('utf-8').split(',')
        for c in _v_cats:
            classes.append({'type_name': c, 'type_id': 'v_' + c})
        return {'class': classes}

    def homeVideoContent(self):
        try:
            url = self.HOST + '/api/video/app/video/search?category=&orderType=1&page=1&searchType=1&size=42'
            rsp = self.fetch(url, timeout=20)
            data = json.loads(rsp.text)
            return {'list': self._video_items(data['model']['data'])}
        except Exception as e:
            print(f'[WARN] homeVideoContent: {e}')
            return {'list': []}

    def _video_items(self, items):
        """\u89c6\u9891\u6761\u76ee \u2192 vod \u5217\u8868\u3002\u53ef\u64ad\u76f4\u94fe\u9759\u6001\u65e0\u7b7e\u540d\uff0c\u7f16\u7801\u8fdb vod_id \u4f9b detail \u4f7f\u7528\uff08intro \u63a5\u53e3\u533f\u540d\u4e0d\u53ef\u8bbf\u95ee\uff09"""
        videos = []
        for item in items:
            u = item.get('url') or ''
            if not u:
                continue  # \u65e0\u76f4\u94fe\uff08\u4f1a\u5458\u7247\uff09\u4e0d\u6536\uff0c\u907f\u514d\u7a7a\u58f3\u6761\u76ee
            meta = {'i': item.get('id', ''), 'u': u,
                    't': item.get('title', ''), 'p': item.get('coverUrl', ''),
                    'c': item.get('categories', ''), 's': item.get('brief') or item.get('description') or ''}
            videos.append({
                'vod_id': 'V$' + base64.b64encode(json.dumps(meta, ensure_ascii=False).encode('utf-8')).decode(),
                'vod_name': item.get('title', ''),
                'vod_pic': item.get('coverUrl', ''),
                'vod_remarks': item.get('durationFormat', ''),
            })
        return videos

    def _audio_items(self, items):
        videos = []
        for item in items:
            videos.append({
                'vod_id': item['id'],
                'vod_name': item['title'],
                'vod_pic': item['coverUrl'],
                'vod_remarks': item['categories'],
            })
        return videos

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg) if pg else 1
        result = {'page': pg, 'pagecount': 9999, 'limit': 42, 'total': 999999, 'list': []}
        try:
            if tid.startswith('v_'):
                cat = tid[2:]
                url = '{0}/api/video/app/video/search?category={1}&orderType=1&page={2}&searchType=1&size=42'.format(
                    self.HOST, urllib.parse.quote(cat), pg)
                rsp = self.fetch(url, timeout=20)
                data = json.loads(rsp.text)
                result['list'] = self._video_items(data['model']['data'])
                result['total'] = data['model'].get('totalCount', 999999)
            else:
                cat = tid[2:] if tid.startswith('a_') else tid
                url = '{0}/api/audio/app/audio/search?category={1}&orderType=1&page={2}&searchType=1&size=42'.format(
                    self.HOST, urllib.parse.quote(cat), pg)
                rsp = self.fetch(url, timeout=20)
                data = json.loads(rsp.text)
                result['list'] = self._audio_items(data['model']['data'])
                result['total'] = data['model'].get('totalCount', 999999)
        except Exception as e:
            print(f'[WARN] categoryContent: {e}')
        return result

    def detailContent(self, array):
        tid = array[0]
        if tid.startswith('V$'):
            return self._video_detail(tid[2:])
        return self._audio_detail(tid)

    def _video_detail(self, b64meta):
        vod = {'vod_id': 'V$' + b64meta, 'vod_play_from': 'UAA\u89c6\u9891'}
        try:
            meta = json.loads(base64.b64decode(b64meta.encode('utf-8')).decode('utf-8'))
            vod.update({
                'vod_name': meta.get('t', ''),
                'vod_pic': meta.get('p', ''),
                'vod_area': meta.get('c', ''),
                'vod_content': meta.get('s', '') or meta.get('t', ''),
                'vod_play_url': '\u64ad\u653e$' + meta.get('u', ''),
            })
        except Exception:
            vod['vod_play_url'] = ''
        return {'list': [vod]}

    def _audio_detail(self, tid):
        url = self.HOST + '/api/audio/app/audio/intro?id={0}'.format(tid)
        rsp = self.fetch(url, timeout=20)
        content = rsp.text
        data = json.loads(content)
        model = data.get('model') or {}

        # \u6784\u5efa\u64ad\u653e\u5217\u8868
        play_list = []
        if model.get('chapters'):
            for chapter in model['chapters']:
                chapter_id = chapter.get('id', '')
                chapter_title = chapter.get('title', '\u7b2c{}\u96c6'.format(chapter.get('order', 1)))
                chapter_url = self.getChapterUrl(chapter_id)
                if chapter_url:
                    play_list.append('{}${}'.format(chapter_title, chapter_url))

        # \u5982\u679c\u6ca1\u6709\u7ae0\u8282\u4fe1\u606f\uff0c\u4f7f\u7528\u9ed8\u8ba4\u64ad\u653e\u94fe\u63a5
        if not play_list and model.get('latestReadChapterUrl'):
            play_list.append('\u7b2c1\u96c6${}'.format(model['latestReadChapterUrl']))

        play_url = '#'.join(play_list) if play_list else ''

        vod_actor = model.get('author', '\u672a\u77e5')  # CV\u4fe1\u606f
        vod_area = model.get('categories', '')   # \u5206\u7c7b\u4fe1\u606f

        # \u5907\u6ce8\u4fe1\u606f\uff1a\u6536\u542c\u91cf + \u6536\u85cf\u91cf
        remarks_parts = []
        if 'playCount' in model:
            remarks_parts.append(f'收听:{self.format_count(model["playCount"])}')
        if 'collectCount' in model:
            remarks_parts.append(f'收藏:{self.format_count(model["collectCount"])}')
        vod_remarks = ' | '.join(remarks_parts) if remarks_parts else model.get('updateState', '')

        vod = {
            'vod_id': tid,
            'vod_name': model.get('title', ''),
            'vod_pic': model.get('coverUrl', ''),
            'vod_content': model.get('intro', ''),
            'vod_actor': vod_actor,
            'vod_area': vod_area,
            'vod_remarks': vod_remarks,
            'vod_play_from': 'UAA',
            'vod_play_url': play_url
        }
        return {'list': [vod]}

    def format_count(self, count):
        """\u683c\u5f0f\u5316\u6570\u5b57\u663e\u793a\uff0c\u598218200\u663e\u793a\u4e3a1.82\u4e07"""
        try:
            count = int(count)
            if count >= 10000:
                return f"{count/10000:.1f}万"
            elif count >= 1000:
                return f"{count/1000:.1f}K"
            else:
                return str(count)
        except:
            return str(count)

    def getChapterUrl(self, chapter_id):
        """\u83b7\u53d6\u7ae0\u8282\u64ad\u653e\u94fe\u63a5"""
        if not chapter_id:
            return ''
        try:
            url = self.HOST + '/api/audio/app/audio/chapter?id={}'.format(chapter_id)
            rsp = self.fetch(url, timeout=20)
            data = json.loads(rsp.text)
            if data.get('model') and data['model'].get('chapterUrl'):
                return data['model']['chapterUrl']
        except:
            pass
        return ''

    def searchContent(self, key, quick, page='1'):
        """\u805a\u5408\u641c\u7d22\uff1a\u89c6\u9891 + \u97f3\u9891\uff08\u539f uaa001.com \u57df TLS \u63e1\u624b\u5931\u8d25\u5df2\u5f03\u7528\uff0c\u7edf\u4e00\u8d70\u5f53\u524d HOST\uff09"""
        pg = int(page) if str(page).isdigit() else 1
        kw = urllib.parse.quote(key)
        videos = []
        try:
            url = '{0}/api/video/app/video/search?keyword={1}&orderType=1&page={2}&searchType=1&size=20'.format(self.HOST, kw, pg)
            rsp = self.fetch(url, timeout=20)
            videos.extend(self._video_items(json.loads(rsp.text)['model']['data']))
        except Exception as e:
            print(f'[WARN] searchVideo: {e}')
        try:
            url = '{0}/api/audio/app/audio/search?category=&keyword={1}&orderType=1&page={2}&searchType=1&size=20'.format(self.HOST, kw, pg)
            rsp = self.fetch(url, timeout=20)
            videos.extend(self._audio_items(json.loads(rsp.text)['model']['data']))
        except Exception:
            pass
        return {'list': videos, 'page': pg, 'pagecount': 9999}

    def playerContent(self, flag, id, vipFlags):
        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = id
        result["header"] = {
            "User-Agent": _UA,
            "Referer": self.HOST + '/'
        }
        return result

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        action = {}
        return [200, "video/MP2T", action, ""]
