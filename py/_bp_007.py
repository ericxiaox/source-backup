# -*- coding: utf-8 -*-
import requests
import re
import sys
import json
import urllib.parse
from base.spider import Spider
from urllib.parse import urljoin

sys.path.append('..')


class Spider(Spider):
    CANDIDATE_DOMAINS = [
        "https://mdcmai4.xyz",
        "https://mdcmai5.xyz",
    ]
    decode_mode = 0

    # 网站 menu 结构 (menuId -> 菜单名)
    MENU_NAMES = {
        1: "麻豆原创",
        2: "国产AV",
        3: "岛国AV",
        4: "黑料吃瓜",
    }

    def __init__(self):
        super().__init__()
        self._xurl = None
        self._headers = None
        self._cache_cats = None  # 缓存分类列表

    def getName(self):
        return "麻豆传媒AI"

    def init(self, extend):
        self._detect_domain()

    def _detect_domain(self):
        for domain in self.CANDIDATE_DOMAINS:
            try:
                h = {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; M2102J2SC Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.31 Mobile Safari/537.36',
                    'Referer': domain,
                }
                r = requests.get(f"{domain}/api/v1/categories", headers=h, timeout=3)
                if r.status_code == 200:
                    data = r.json()
                    if data.get('code') == 200:
                        self._xurl = domain
                        self._headers = h
                        return
            except Exception:
                continue
        self._xurl = self.CANDIDATE_DOMAINS[0]
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; M2102J2SC Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.31 Mobile Safari/537.36',
            'Referer': self._xurl,
        }

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
        """获取并缓存所有分类"""
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
        """帖子/黑料类内容"""
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

    # ============ 首页分类：4 个菜单 folder + AI短剧 ============
    def homeContent(self, filter):
        class_items = []
        filters = {}

        # 4 个一级菜单（按 menuId 分组）作为 folder
        for mid in [1, 2, 3, 4]:
            name = self.MENU_NAMES.get(mid, f"菜单{mid}")
            class_items.append({
                "type_id": f"menu_{mid}",
                "type_name": name
            })
            # 排序筛选（菜单 1/2/3 视频用）
            if mid in (1, 2, 3):
                filters[f"menu_{mid}"] = [self._video_sort_filter(), self._time_filter(), self._duration_filter()]
            else:
                # 黑料吃瓜(帖子)只需时间
                filters[f"menu_{mid}"] = [self._time_filter()]

        # AI短剧（独立一级）
        class_items.append({"type_id": "short-dramas", "type_name": "AI短剧"})
        filters["short-dramas"] = [self._time_filter()]

        return {"class": class_items, "filters": filters}

    def _video_sort_filter(self):
        return {
            "key": "sortBy",
            "name": "排序",
            "value": [
                {"n": "最热", "v": "heat"},
                {"n": "最新", "v": "newest"},
                {"n": "最早", "v": "oldest"},
                {"n": "播放最多", "v": "views"},
                {"n": "点赞最多", "v": "likes"},
            ]
        }

    def _time_filter(self):
        return {
            "key": "timeRange",
            "name": "更新时间",
            "value": [
                {"n": "全部", "v": ""},
                {"n": "近7天", "v": "7d"},
                {"n": "近1月", "v": "1m"},
                {"n": "近3月", "v": "3m"},
            ]
        }

    def _duration_filter(self):
        return {
            "key": "minDuration",
            "name": "视频时长",
            "value": [
                {"n": "全部", "v": ""},
                {"n": "10分钟以上", "v": "10"},
                {"n": "20分钟以上", "v": "20"},
            ]
        }

    def homeVideoContent(self):
        """推荐页 = 每日更新 (menuId=1 排序)"""
        try:
            data = self._fetch_api('/videos', params={'page': 1, 'size': 20, 'sortBy': 'heat'})
            items = data.get('data', {}).get('items', [])
            return {'list': self._parse_video_items(items)}
        except:
            return {'list': []}

    # ============ 分类内容 ============
    def categoryContent(self, cid, pg, filter, ext):
        page = int(pg) if pg else 1
        cid = str(cid)

        # 二级目录：进入菜单 → 列子分类
