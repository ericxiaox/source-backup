# -*- coding: utf-8 -*-
import requests
import re
import sys
import base64
import json
import urllib.parse
from base.spider import Spider
from urllib.parse import urljoin

sys.path.append('..')
from base.spider import Spider
from urllib.parse import urljoin
try:
    from hostresolver import ext_of
except ImportError:
    ext_of = None
except Exception:
    try:
        import os as _os
        sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        try:
            from hostresolver import ext_of
        except ImportError:
            ext_of = None
    except Exception:
        ext_of = None


class Spider(Spider):
    CANDIDATE_DOMAINS = [
        "https://mdcmai4.xyz",
        "https://mdcmai5.xyz",
        "https://mdcmai3.xyz",
        "https://mdcmai2.xyz",
    ]
    decode_mode = 0

    # \u7f51\u7ad9 menu \u7ed3\u6784 (menuId -> \u83dc\u5355\u540d)
    MENU_NAMES = {
        1: base64.b64decode('6bq76LGG5Y6f5Yib').decode('utf-8'),
        2: base64.b64decode('5Zu95LqnQVY=').decode('utf-8'),
        3: base64.b64decode('5bKb5Zu9QVY=').decode('utf-8'),
        4: "\u9ed1\u6599\u5403\u74dc",
    }

    def __init__(self):
        super().__init__()
        self._xurl = None
        self._headers = None
        self._cache_cats = None  # \u7f13\u5b58\u5206\u7c7b\u5217\u8868

    def getName(self):
        return base64.b64decode('6bq76LGG5Lyg5aqSQUk=').decode('utf-8')

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

    def init(self, extend=""):
        # ext \u652f\u6301\uff1ahost@ \u9501\u5b9a / hosts@ \u8ffd\u52a0\u5019\u9009 / publish@ \u9884\u7559\uff08\u7ad9\u65b9\u6682\u65e0\u7a33\u5b9a\u53d1\u5e03\u9875\uff09
        self._ext = ext_of(extend) if ext_of else {}
        self._detect_domain()

    def _detect_domain(self):
        """\u5019\u9009\u57df\u5e76\u884c\u5b9e\u6d4b\uff08hostresolver \u7f3a\u5931\u65f6\u4ecd\u53ef\u7528\uff09\uff1aext host \u9501\u5b9a > ext hosts > \u5185\u7f6e\u5019\u9009\u3002
        \u539f\u4e32\u884c 3s\u00d7N \u6539\u4e3a\u5e76\u884c\uff0c\u907f\u514d App \u7aef\u7a7a\u8f6c\u3002\u7b2c\u4e00\u4e2a\u6210\u529f\u5373\u91c7\u7528\u3002"""
        import threading
        ext = getattr(self, '_ext', {}) or {}
        hosts = []
        if ext.get('host'):
            hosts.append(ext['host'].rstrip('/'))
        hosts += [h.rstrip('/') for h in (ext.get('hosts') or [])]
        hosts += [d.rstrip('/') for d in self.CANDIDATE_DOMAINS]
        result = [None]
        UAMOB = 'Mozilla/5.0 (Linux; Android 13; M2102J2SC Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.31 Mobile Safari/537.36'

        def _try(d):
            if result[0]:
                return
            try:
                h = {'User-Agent': UAMOB, 'Referer': d}
                r = requests.get(f"{d}/api/v1/categories", headers=h, timeout=3)
                if r.status_code == 200:
                    data = r.json()
                    if data.get('code') == 200 and not result[0]:
                        result[0] = (d, h)
            except Exception:
                pass
        threads = [threading.Thread(target=_try, args=(d,)) for d in hosts]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=4)
        if result[0]:
            self._xurl, self._headers = result[0]
        else:
            self._xurl = self.CANDIDATE_DOMAINS[0]
            self._headers = {'User-Agent': UAMOB, 'Referer': self._xurl}

    def _domain(self):
        if self._xurl is None:
            self._detect_domain()
        return self._xurl

    def _req_headers(self):
        if self._headers is None:
            self._detect_domain()
        return self._headers

    def _fetch_api(self, path, params=None):
        url = f"{self._domain()}/api/v1{path}"
        resp = requests.get(url, headers=self._req_headers(), params=params, timeout=15)
        resp.encoding = resp.apparent_encoding or 'utf-8'
        return json.loads(resp.text)

    def _get_categories(self):
        """\u83b7\u53d6\u5e76\u7f13\u5b58\u6240\u6709\u5206\u7c7b"""
        if self._cache_cats is None:
            try:
                data = self._fetch_api('/categories')
                self._cache_cats = data.get('data', [])
            except Exception:
                self._cache_cats = []
        return self._cache_cats

    def _build_image_url(self, cover_url):
        if not cover_url:
            return ''
        if cover_url.startswith('http'):
            return cover_url
        if '/api/v1/image/proxy' in cover_url:
            return urljoin(self._domain(), cover_url)
        if cover_url.startswith('/uploads/'):
            return urljoin(self._domain(), cover_url)
        encoded = urllib.parse.quote(cover_url, safe='')
        return f"{self._domain()}/api/v1/image/proxy?path={encoded}"

    def _build_m3u8_proxy_url(self, video_url):
        if not video_url:
            return ''
        if video_url.startswith('http'):
            parsed = urllib.parse.urlparse(video_url)
            path = parsed.path.lstrip('/')
        else:
            path = video_url.lstrip('/')
        encoded = urllib.parse.quote(path, safe='')
        return f"{self._domain()}/api/v1/m3u8/proxy?path={encoded}"

    def _parse_video_items(self, items):
        videos = []
        for item in items:
            vid = str(item.get('id', ''))
            if not vid:
                continue
            title = item.get('title', '').strip()
            if not title:
                continue
            pic = self._build_image_url(item.get('coverUrl', ''))
            remark = ''
            dur = item.get('durationSec', 0)
            if dur and dur > 0:
                mins = dur // 60
                secs = dur % 60
                remark = f'{mins:02d}:{secs:02d}'
            videos.append({
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": remark
            })
        return videos

    def _parse_short_drama_items(self, items):
        videos = []
        for item in items:
            vid = str(item.get('id', ''))
            if not vid:
                continue
            title = item.get('title', '').strip()
            if not title:
                continue
            pic = self._build_image_url(item.get('coverUrl', ''))
            ep_count = item.get('episodeCount', 0)
            if ep_count:
                remark = f'{ep_count}集'
            else:
                remark = ''
            videos.append({
                "vod_id": f'sd_{vid}',
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": remark
            })
        return videos

    def _parse_post_items(self, items):
        """\u5e16\u5b50/\u9ed1\u6599\u7c7b\u5185\u5bb9"""
        videos = []
        for item in items:
            pid = str(item.get('id', ''))
            if not pid:
                continue
            title = (item.get('title') or item.get('name') or '').strip()
            if not title:
                continue
            pic = self._build_image_url(item.get('coverUrl') or item.get('cover') or '')
            published = item.get('publishedAt', '')
            if published:
                m = re.match(r'(\d{4})-(\d{2})-(\d{2})', published)
                if m:
                    title += f' [{m.group(1)}-{m.group(2)}-{m.group(3)}]'
            videos.append({
                "vod_id": f'post_{pid}',
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": item.get('categoryName', '')
            })
        return videos

    # ============ \u9996\u9875\u5206\u7c7b\uff1a4 \u4e2a\u83dc\u5355 folder + AI\u77ed\u5267 ============
    def homeContent(self, filter):
        class_items = []
        filters = {}

        # 4 \u4e2a\u4e00\u7ea7\u83dc\u5355\uff08\u6309 menuId \u5206\u7ec4\uff09\u4f5c\u4e3a folder
        for mid in [1, 2, 3, 4]:
            name = self.MENU_NAMES.get(mid, f"菜单{mid}")
            class_items.append({
                "type_id": f"menu_{mid}",
                "type_name": name
            })
            # \u6392\u5e8f\u7b5b\u9009\uff08\u83dc\u5355 1/2/3 \u89c6\u9891\u7528\uff09
            if mid in (1, 2, 3):
                filters[f"menu_{mid}"] = [self._video_sort_filter(), self._time_filter(), self._duration_filter()]
            else:
                # \u9ed1\u6599\u5403\u74dc(\u5e16\u5b50)\u53ea\u9700\u65f6\u95f4
                filters[f"menu_{mid}"] = [self._time_filter()]

        # AI\u77ed\u5267\uff08\u72ec\u7acb\u4e00\u7ea7\uff09
        class_items.append({"type_id": "short-dramas", "type_name": "AI\u77ed\u5267"})
        filters["short-dramas"] = [self._time_filter()]

        return {"class": class_items, "filters": filters}

    def _video_sort_filter(self):
        return {
            "key": "sortBy",
            "name": "\u6392\u5e8f",
            "value": [
                {"n": "\u6700\u70ed", "v": "heat"},
                {"n": "\u6700\u65b0", "v": "newest"},
                {"n": "\u6700\u65e9", "v": "oldest"},
                {"n": "\u64ad\u653e\u6700\u591a", "v": "views"},
                {"n": "\u70b9\u8d5e\u6700\u591a", "v": "likes"},
            ]
        }

    def _time_filter(self):
        return {
            "key": "timeRange",
            "name": "\u66f4\u65b0\u65f6\u95f4",
            "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "\u8fd17\u5929", "v": "7d"},
                {"n": "\u8fd11\u6708", "v": "1m"},
                {"n": "\u8fd13\u6708", "v": "3m"},
            ]
        }

    def _duration_filter(self):
        return {
            "key": "minDuration",
            "name": "\u89c6\u9891\u65f6\u957f",
            "value": [
                {"n": "\u5168\u90e8", "v": ""},
                {"n": "10\u5206\u949f\u4ee5\u4e0a", "v": "10"},
                {"n": "20\u5206\u949f\u4ee5\u4e0a", "v": "20"},
            ]
        }

    def homeVideoContent(self):
        """\u63a8\u8350\u9875 = \u6bcf\u65e5\u66f4\u65b0 (menuId=1 \u6392\u5e8f)"""
        try:
            data = self._fetch_api('/videos', params={'page': 1, 'size': 20, 'sortBy': 'heat'})
            items = data.get('data', {}).get('items', [])
            return {'list': self._parse_video_items(items)}
        except:
            return {'list': []}

    # ============ \u5206\u7c7b\u5185\u5bb9 ============
    def categoryContent(self, cid, pg, filter, ext):
        page = int(pg) if pg else 1
        cid = str(cid)

        # \u4e8c\u7ea7\u76ee\u5f55\uff1a\u8fdb\u5165\u83dc\u5355 \u2192 \u5217\u5b50\u5206\u7c7b
        if cid.startswith('menu_'):
            return self._category_menu(cid, page, filter, ext)

        # AI\u77ed\u5267
        if cid == 'short-dramas':
            return self._category_short_dramas(page, ext)

        # \u89c6\u9891\u5206\u7c7b
        if cid.isdigit():
            return self._category_videos(int(cid), page, ext)

        # \u5e16\u5b50\u5206\u7c7b
        if cid.startswith('post_cat_'):
            return self._category_posts(int(cid[9:]), page, ext)

        return {'list': [], 'page': page, 'pagecount': 1, 'limit': 20, 'total': 0}

    def _category_menu(self, cid, page, filter, ext):
        """\u8fdb\u5165\u83dc\u5355\uff0c\u5217\u51fa\u5b50\u5206\u7c7b\u4f5c\u4e3a folder \u9879"""
        menu_id = int(cid.split('_')[1])
        all_cats = self._get_categories()
        sub_cats = [c for c in all_cats
                    if c.get('menuId') == menu_id
                    and c.get('enabled')
                    and c.get('type') in ('video', 'post', 'shortdrama')]
        sub_cats.sort(key=lambda x: x.get('sortOrder', 0))

        videos = []
        for c in sub_cats:
            c_id = c.get('id')
            c_type = c.get('type', 'video')
            # video/post \u7528\u5206\u7c7b ID\uff0c\u77ed\u5267\u7528 short-dramas
            if c_type == 'post':
                vod_id = f'post_cat_{c_id}'
            elif c_type == 'video':
                vod_id = str(c_id)
            else:
                continue
            videos.append({
                "vod_id": vod_id,
                "vod_name": c.get('name', ''),
                "vod_pic": '',
                "vod_remarks": '',
                "vod_tag": "folder"
            })
        return {'list': videos, 'page': 1, 'pagecount': 1, 'limit': 100, 'total': len(videos)}

    def _category_short_dramas(self, page, ext):
        size = 12
        params = {'productId': 1, 'sortBy': 'heat', 'page': page, 'size': size}
        if isinstance(ext, dict):
            tr = ext.get('timeRange', '')
            if tr:
                params['timeRange'] = tr
        try:
            data = self._fetch_api('/short-dramas', params=params)
            d = data.get('data', {})
            items = d.get('items', [])
            total = d.get('total', 0)
            pagecount = d.get('totalPages', (total + size - 1) // size if total > 0 else 1)
            return {
                'list': self._parse_short_drama_items(items),
                'page': page, 'pagecount': pagecount, 'limit': size, 'total': total
            }
        except:
            return {'list': [], 'page': page, 'pagecount': 1, 'limit': size, 'total': 0}

    def _category_videos(self, cat_id, page, ext):
        size = 20
        params = {'page': page, 'size': size, 'categoryId': cat_id}
        if isinstance(ext, dict):
            for k, param in [('sortBy', 'sortBy'), ('timeRange', 'timeRange'), ('minDuration', 'minDuration')]:
                v = ext.get(k, '')
                if v:
                    params[param] = v
        try:
            data = self._fetch_api('/videos', params=params)
            d = data.get('data', {})
            items = d.get('items', [])
            total = d.get('total', 0)
            pagecount = (total + size - 1) // size if total > 0 else 1
            return {
                'list': self._parse_video_items(items),
                'page': page, 'pagecount': pagecount, 'limit': size, 'total': total
            }
        except:
            return {'list': [], 'page': page, 'pagecount': 1, 'limit': size, 'total': 0}

    def _category_posts(self, cat_id, page, ext):
        size = 20
        params = {'page': page, 'size': size, 'categoryId': cat_id}
        if isinstance(ext, dict):
            tr = ext.get('timeRange', '')
            if tr:
                params['timeRange'] = tr
        try:
            data = self._fetch_api('/posts', params=params)
            d = data.get('data', {})
            items = d.get('items', [])
            total = d.get('total', 0)
            pagecount = (total + size - 1) // size if total > 0 else 1
            return {
                'list': self._parse_post_items(items),
                'page': page, 'pagecount': pagecount, 'limit': size, 'total': total
            }
        except:
            return {'list': [], 'page': page, 'pagecount': 1, 'limit': size, 'total': 0}

    # ============ \u8be6\u60c5 ============
    def detailContent(self, ids):
        vid = ids[0]
        if vid.startswith('sd_'):
            return self._detail_short_drama(vid)
        if vid.startswith('post_'):
            return self._detail_post(vid)
        try:
            data = self._fetch_api(f'/videos/{vid}')
            item = data.get('data', {})
        except:
            return {'list': []}

        vod = {}
        vod["vod_id"] = vid
        vod["vod_name"] = item.get('title', '')
        vod["vod_pic"] = self._build_image_url(item.get('coverUrl', ''))
        published = item.get('publishedAt', '')
        if published:
            ym = re.match(r'(\d{4})', published)
            if ym:
                vod["vod_year"] = ym.group(1)
        vod["type_name"] = item.get('categoryName', '')
        author = item.get('authorName', '')
        if author:
            vod["vod_actor"] = author
        desc = item.get('description', '')
        if desc:
            vod["vod_content"] = desc
        dur = item.get('durationSec', 0)
        if dur and dur > 0:
            mins = dur // 60
            secs = dur % 60
            vod["vod_remarks"] = f'{mins:02d}:{secs:02d}'
        video_url = item.get('videoUrl', '')
        if video_url:
            m3u8_url = self._build_m3u8_proxy_url(video_url)
            if m3u8_url:
                vod["vod_play_from"] = base64.b64decode('6bq76LGG').decode('utf-8')
                vod["vod_play_url"] = f'正片${m3u8_url}'
        return {'list': [vod]}

    def _detail_short_drama(self, vid):
        sd_id = vid[3:]
        try:
            data = self._fetch_api(f'/short-dramas/{sd_id}', params={'productId': 1})
            item = data.get('data', {})
        except:
            return {'list': []}
        vod = {}
        vod["vod_id"] = vid
        vod["vod_name"] = item.get('title', '')
        vod["vod_pic"] = self._build_image_url(item.get('coverUrl', ''))
        published = item.get('publishedAt', '')
        if published:
            ym = re.match(r'(\d{4})', published)
            if ym:
                vod["vod_year"] = ym.group(1)
        vod["type_name"] = 'AI\u77ed\u5267'
        desc = item.get('description', '')
        if desc:
            vod["vod_content"] = desc
        ep_count = item.get('episodeCount', 0)
        if ep_count:
            vod["vod_remarks"] = f'{ep_count}集'
        episodes = item.get('episodes', [])
        play_list = []
        for ep in episodes:
            ep_title = ep.get('titleOverride') or ep.get('title') or f"第{ep.get('episodeNo', '')}集"
            ep_url = self._build_m3u8_proxy_url(ep.get('videoUrl', ''))
            if ep_url:
                play_list.append(f'{ep_title}${ep_url}')
        if play_list:
            vod["vod_play_from"] = base64.b64decode('6bq76LGG').decode('utf-8')
            vod["vod_play_url"] = '#'.join(play_list)
        return {'list': [vod]}

    def _detail_post(self, vid):
        post_id = vid[5:]
        try:
            data = self._fetch_api(f'/posts/{post_id}')
            item = data.get('data', {})
        except:
            return {'list': []}
        vod = {}
        vod["vod_id"] = vid
        vod["vod_name"] = item.get('title', '')
        vod["vod_pic"] = self._build_image_url(item.get('coverUrl') or item.get('cover') or '')
        published = item.get('publishedAt', '')
        if published:
            ym = re.match(r'(\d{4})', published)
            if ym:
                vod["vod_year"] = ym.group(1)
        vod["type_name"] = item.get('categoryName', '\u9ed1\u6599\u5403\u74dc')
        # \u63cf\u8ff0
        desc = item.get('content') or item.get('description') or ''
        if desc:
            vod["vod_content"] = str(desc)[:1000]
        # \u89c6\u9891\uff08\u9876\u5c42 videoUrl \u5b57\u6bb5\uff09
        video_url = item.get('videoUrl', '')
        if video_url:
            m3u8_url = self._build_m3u8_proxy_url(video_url)
            if m3u8_url:
                vod["vod_play_from"] = base64.b64decode('6bq76LGG').decode('utf-8')
                vod["vod_play_url"] = f'正片${m3u8_url}'
        # \u56fe\u7247\u5217\u8868\u62fc\u5230\u5185\u5bb9\uff08\u9ed1\u6599\u591a\u56fe\u6587\uff09
        images = item.get('images') or []
        img_urls = []
        for img in images:
            if isinstance(img, dict):
                url = img.get('url') or img.get('path') or img.get('imageUrl')
            else:
                url = img
            if url:
                img_urls.append(self._build_image_url(url))
        if img_urls:
            vod["vod_content"] = (vod.get("vod_content", "") + '\n\n' + '\n'.join(img_urls))
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags):
        try:
            if id.startswith('http') and '/m3u8/proxy' in id:
                return {"parse": 0, "playUrl": "", "url": id, "header": json.dumps(self._req_headers())}
            if not id.startswith('http'):
                proxy_url = self._build_m3u8_proxy_url(id)
                if proxy_url:
                    return {"parse": 0, "playUrl": "", "url": proxy_url, "header": json.dumps(self._req_headers())}
            play_url = id if id.startswith(('http://', 'https://')) else urljoin(self._domain(), id)
            return {"parse": 1, "playUrl": "", "url": play_url, "header": json.dumps(self._req_headers())}
        except Exception as e:
            print(f"player error: {e}")
            return {"parse": 1, "playUrl": "", "url": id, "header": json.dumps(self._req_headers())}

    def searchContent(self, key, quick, page='1'):
        page = int(page) if page else 1
        size = 20
        params = {'page': page, 'size': size, 'keyword': key}
        try:
            data = self._fetch_api('/videos', params=params)
            d = data.get('data', {})
            items = d.get('items', [])
            total = d.get('total', 0)
            pagecount = (total + size - 1) // size if total > 0 else 1
            return {
                'list': self._parse_video_items(items),
                'page': page, 'pagecount': pagecount, 'limit': size, 'total': total
            }
        except:
            return {'list': [], 'page': page, 'pagecount': 1, 'limit': size, 'total': 0}
