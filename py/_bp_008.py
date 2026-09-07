        if cid.startswith('menu_'):
            return self._category_menu(cid, page, filter, ext)

        # AI短剧
        if cid == 'short-dramas':
            return self._category_short_dramas(page, ext)

        # 视频分类
        if cid.isdigit():
            return self._category_videos(int(cid), page, ext)

        # 帖子分类
        if cid.startswith('post_cat_'):
            return self._category_posts(int(cid[9:]), page, ext)

        return {'list': [], 'page': page, 'pagecount': 1, 'limit': 20, 'total': 0}

    def _category_menu(self, cid, page, filter, ext):
        """进入菜单，列出子分类作为 folder 项"""
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
            # video/post 用分类 ID，短剧用 short-dramas
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

    # ============ 详情 ============
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
                vod["vod_play_from"] = '麻豆'
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
        vod["type_name"] = 'AI短剧'
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
            vod["vod_play_from"] = '麻豆'
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
        vod["type_name"] = item.get('categoryName', '黑料吃瓜')
        # 描述
        desc = item.get('content') or item.get('description') or ''
        if desc:
            vod["vod_content"] = str(desc)[:1000]
        # 视频（顶层 videoUrl 字段）
        video_url = item.get('videoUrl', '')
        if video_url:
            m3u8_url = self._build_m3u8_proxy_url(video_url)
            if m3u8_url:
                vod["vod_play_from"] = '麻豆'
                vod["vod_play_url"] = f'正片${m3u8_url}'
        # 图片列表拼到内容（黑料多图文）
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
