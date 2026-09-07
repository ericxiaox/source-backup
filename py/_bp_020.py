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
