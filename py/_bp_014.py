            data = resp1.get('data', {})
            if data.get('deviceId'):
                self._device_id = data['deviceId']
            if data.get('typeTitleList'):
                self._categories = data['typeTitleList']
        self._api_request('/ht/users/initH5_2', _t=shared_t)
        resp = self._api_request('/ht/users/deviceLogin', {
            'bundleId': BUNDLE_ID, 'brandId': BRAND_ID, 'projectId': PROJECT_ID
        })
        if resp and resp.get('code') == 10000:
            data = resp.get('data', {})
            self._user_id = data.get('userId', '')
            self._session_id = data.get('sessionId', '')
        if not self._categories:
            self._categories = [
                {'contentId': 'home', 'title': '最新'},
                {'contentId': 'hot', 'title': '热门'},
            ]
        self._session_inited = True
        self._save_session_cache()

    def _refresh_video_type_list(self):
        appcfg = self._api_request('/ht/users/appConfig')
        if appcfg and appcfg.get('code') == 10000:
            ac_data = appcfg.get('data', {})
            if isinstance(ac_data, dict) and ac_data.get('appConfig'):
                ac_cfg = ac_data['appConfig']
                if isinstance(ac_cfg, dict) and ac_cfg.get('videoTypeList'):
                    self._video_type_list = ac_cfg['videoTypeList']

    def get_proxy_image_url(self, img_url):
        if not img_url:
            return ''
        base = self.getProxyUrl() or 'http://127.0.0.1:9980/proxy?do=py'
        return base + '&type=' + PROXY_TYPE + '&url=' + quote(img_url, safe='')

    def _fmt_duration(self, seconds):
        try:
            s = int(seconds or 0)
        except: return ''
        if s <= 0:
            return ''
        m, s = divmod(s, 60)
        return f"{m}:{s:02d}"

    def init(self, extend=""):
        cached_host, valid = self._get_cached_site()
        if valid:
            self.host = cached_host
            self._speed_test_done = True

    _CATEGORY_BLACKLIST = {'成人游戏', '漫画', '小说', '蜜穴女友', '一键脱衣', '春药商城', '同城交友', '吃瓜', '成人漫画'}

    def homeContent(self, filter):
        self._select_best_site()
        self._ensure_session()
        if not self._categories:
            self._session_inited = False
            self._ensure_session()
        classes, filters = [], {}
        for cat in self._categories:
            cid, title = str(cat.get('contentId', '')), cat.get('title', '')
            if not cid or not title or title in self._CATEGORY_BLACKLIST:
                continue
            classes.append({'type_id': cid, 'type_name': title})
            cat_filters = []
            sub_cats = [v for v in self._video_type_list if str(v.get('typePid', '')) == cid]
            if sub_cats:
                sub_values = [{'n': '全部', 'v': ''}]
                for sc in sub_cats:
                    sc_id, sc_name = str(sc.get('typeId', '')), sc.get('typeName', '')
                    if sc_id and sc_name:
                        sub_values.append({'n': sc_name, 'v': sc_id})
                if len(sub_values) > 1:
                    cat_filters.append({'key': 'label', 'name': '分类', 'value': sub_values})
            first_level = [v for v in self._video_type_list if str(v.get('typePid', '')) == '0' and str(v.get('typeId', '')) == cid]
            if first_level:
                tags_str = first_level[0].get('tags', '')
                if tags_str:
                    tag_list = [t.strip() for t in tags_str.split(',') if t.strip()]
                    if tag_list:
                        tag_values = [{'n': '全部', 'v': ''}]
                        for t in tag_list:
                            tag_values.append({'n': t, 'v': t})
                        cat_filters.append({'key': 'tag', 'name': '标签', 'value': tag_values})
            cat_filters.append({'key': 'sort', 'name': '排序', 'value': [
                {'n': '最近更新', 'v': '0'}, {'n': '最多播放', 'v': '1'}, {'n': '最多收藏', 'v': '2'}
            ]})
            if cat_filters:
                filters[cid] = cat_filters
        # 添加涩库分类
        classes.append({'type_id': 'siku', 'type_name': '涩库'})
        filters['siku'] = []
        classes.append({'type_id': 'topic', 'type_name': '专题'})
        home_videos = self.categoryContent('home', 1, '', {})
        return {
            'class': classes, 'filters': filters, 'type': '影视',
            'list': home_videos.get('list', []), 'page': home_videos.get('page', 1),
            'pagecount': home_videos.get('pagecount', 1), 'limit': home_videos.get('limit', 0),
            'total': home_videos.get('total', 0)
        }

    def homeVideoContent(self, tid, pg, filter, extend):
        return self.categoryContent(tid or 'home', pg, filter, extend)

    # ========== 分类路由 ==========
    def categoryContent(self, tid, pg, filter, extend):
        tid, pg = str(tid), int(pg)
        # 涩库首页
        if tid == 'siku':
            siku_home = self.siku.homeContent({})
            vod_list = []
            for cls in siku_home.get('class', []):
                vod_list.append({
                    'vod_id': cls['type_id'],      # 已包含 siku: 前缀
                    'vod_name': cls['type_name'],
                    'vod_pic': cls.get('vod_pic', ''),
                    'vod_tag': 'folder'
                })
            return {'list': vod_list, 'page': 1, 'pagecount': 1, 'limit': len(vod_list), 'total': len(vod_list)}
        # 涩库子分类 (tid 以 siku: 开头)
        if tid.startswith('siku:'):
            return self.siku.categoryContent(tid, pg)

        # 蜜桃在线分类
        if tid.startswith('topic_') and '@' in tid:
            topic_id = tid[len('topic_'):].replace('@', '')
            resp = self._api_request('/ht/content/queryOriTopicVideos', {'topicId': topic_id, 'pageNo': str(pg-1), 'pageSize': '20'})
            if resp and resp.get('code') == 10000:
                vod_list = self._extract_videos_from_data(resp.get('data', {}))
            else:
                vod_list = []
            total_page = max(1, len(vod_list) // 20 + (1 if len(vod_list) % 20 else 0))
            return {'list': vod_list, 'page': pg, 'pagecount': total_page, 'limit': len(vod_list), 'total': len(vod_list)}
        if tid == 'topic':
            resp = self._api_request('/ht/content/getOriTopicList', {'pageNo': str(pg-1), 'pageSize': '20'})
            if resp and resp.get('code') == 10000:
                vod_list = self._parse_topic_list(resp.get('data', {}))
                return {'list': vod_list, 'page': pg, 'pagecount': 50, 'limit': len(vod_list), 'total': len(vod_list)*50}
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 0, 'total': 0}
        if tid in ('home', 'new', 'hot'):
            sort_map = {'home':'1','new':'1','hot':'2'}
            resp = self._api_request('/ht/content/queryTypeVideosH5', {'pageNo': str(pg-1), 'pageSize': '20', 'sort': sort_map.get(tid,'1'), 'type': '1'})
            if resp and resp.get('code') == 10000:
                data = resp.get('data', {})
                items = data.get('typeVideoList') or data.get('list') or data.get('data') or data.get('videoList') or []
                vod_list = [self._parse_video(v) for v in items if isinstance(v, dict) and self._parse_video(v)]
                total_page = int(data.get('totalPage') or 1)
                return {'list': vod_list, 'page': pg, 'pagecount': total_page, 'limit': len(vod_list), 'total': total_page*20}
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 0, 'total': 0}
        # 数值分类
        api_params = {'pageNo': str(pg-1), 'pageSize': '20', 'typeId': tid, 'type': '1'}
        if isinstance(extend, dict):
            for key in ('label','tag','sort'):
                if extend.get(key):
                    api_params[key] = extend[key]
        resp = self._api_request('/ht/content/queryTypeVideosH5', api_params)
        if resp and resp.get('code') == 10000:
            data = resp.get('data', {})
            items = data.get('typeVideoList') or data.get('list') or data.get('data') or data.get('videoList') or []
            vod_list = [self._parse_video(v) for v in items if isinstance(v, dict) and self._parse_video(v)]
            total_page = int(data.get('totalPage') or 1)
            return {'list': vod_list, 'page': pg, 'pagecount': total_page, 'limit': len(vod_list), 'total': total_page*20}
        return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 0, 'total': 0}

    def _extract_videos_from_data(self, data):
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = (data.get('videoList') or data.get('list') or data.get('data') or data.get('videos') or
                     data.get('typeVideoList') or data.get('topicVideoIdList') or data.get('searchList') or
                     data.get('contentList') or data.get('records') or data.get('pageData') or data.get('resultList') or [])
        else:
            return []
        return [self._parse_video(v) for v in items if isinstance(v, dict) and self._parse_video(v)]

    @staticmethod
    def _try_get(item, *keys):
        for k in keys:
            v = item.get(k)
            if v is not None and v != '':
                return v
        return ''

    def _parse_topic_list(self, data):
        items = data if isinstance(data, list) else data.get('topicList') or data.get('oriTopicList') or data.get('list') or data.get('data') or data.get('topics') or []
        if not isinstance(items, list):
            return []
        results, seen = [], set()
        for item in items:
            if not isinstance(item, dict): continue
            tid = str(self._try_get(item, 'topicId','id','contentId','oriTopicId','topic_id'))
            name = str(self._try_get(item, 'topicName','name','title','oriTopicName','topic_name','topic'))
            img = str(self._try_get(item, 'topicPic','topicImg','img','cover','imageUrl','pic','thumb','image','topic_img','oriTopicImg'))
            cnt = str(self._try_get(item, 'videoCount','count','contentCount','totalCount','total','video_count'))
            if not tid or tid in seen: continue
            seen.add(tid)
            results.append({
                'vod_id': 'topic_' + tid + '@', 'vod_name': name or ('专题'+tid),
                'vod_pic': self.get_proxy_image_url(img or self.host+'/favicon.ico'), 'vod_tag': 'folder',
                'vod_remarks': f'{cnt}部' if cnt else ''
            })
        return results

    def _parse_video(self, item):
        if item.get('contentType') is not None and item.get('contentType') != 1:
            return None
        vid = str(self._try_get(item, 'contentId','id','videoId'))
        title = self._try_get(item, 'title','name','videoTitle')
        pic = self._try_get(item, 'img','cover','coverUrl','pic','imageUrl')
        remarks = self._try_get(item, 'duration','playCount','remark')
        if remarks and str(remarks).isdigit():
            remarks = self._fmt_duration(remarks)
        return {'vod_id': vid, 'vod_name': title, 'vod_pic': self.get_proxy_image_url(pic) if pic else '', 'vod_remarks': str(remarks) if remarks else ''}

    # ========== 详情路由 ==========
    def detailContent(self, ids):
        did = ids[0] if isinstance(ids, list) else ids
        if did.startswith('siku:'):
            return self.siku.detailContent([did])
        self._select_best_site()
        self._ensure_session()
        resp = self._api_request('/ht/content/detail', {'contentId': str(did)})
        if not resp or resp.get('code') != 10000:
            return {'list': []}
        detail = resp.get('data', {})
        if not detail:
            return {'list': []}
        title = self._try_get(detail, 'title','name','videoTitle') or '未知标题'
        pic = self._try_get(detail, 'cover','coverUrl','img','imageUrl')
        desc = self._try_get(detail, 'description','desc','intro')
        duration = detail.get('duration', 0)
        actor = self._try_get(detail, 'actor','actors')
        play_url = self._try_get(detail, 'videoUrl','playUrl','url','m3u8Url','sl')
        vod_play_url = '播放$' + (play_url or str(did))
        return {'list': [{
            'vod_id': str(did), 'vod_name': title,
            'vod_pic': self.get_proxy_image_url(pic) if pic else '',
            'vod_actor': str(actor) if actor else '', 'vod_director': '',
            'vod_content': desc, 'vod_year': '', 'vod_area': '',
            'vod_remarks': self._fmt_duration(duration),
            'vod_play_from': '蜜桃视频', 'vod_play_url': vod_play_url, 'type': 'video'
        }]}

    def searchContent(self, key, quick, pg=1):
        self._select_best_site()
        self._ensure_session()
        pg = int(pg)
        resp = self._api_request('/ht/content/search', {'keywords': key, 'pageNo': pg-1, 'pageSize': 20})
        if not resp or resp.get('code') != 10000:
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 0, 'total': 0}
        data = resp.get('data', {})
        items = data if isinstance(data, list) else data.get('searchList') or data.get('list') or data.get('data') or data.get('videoList') or data.get('records') or data.get('resultList') or data.get('content') or []
        if not isinstance(items, list):
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 0, 'total': 0}
        vod_list = [self._parse_video(v) for v in items if isinstance(v, dict) and self._parse_video(v)]
        total_page = int(data.get('totalPage') or 1) if isinstance(data, dict) else max(1, len(vod_list)//20)
        return {'list': vod_list, 'page': pg, 'pagecount': total_page, 'limit': len(vod_list), 'total': total_page*20}

    # ========== 播放路由 ==========
    def playerContent(self, flag, id, vipFlags=None):
        if id.startswith('siku:'):
            return self.siku.playerContent(flag, id[5:], vipFlags)
        url = id.split('$')[-1]
        if url.startswith('http'):
            return {'parse':0, 'url':url, 'jx':0, 'header':{'User-Agent':self.headers['User-Agent'], 'Referer':self.host+'/'}}
        self._select_best_site()
        self._ensure_session()
        resp = self._api_request('/ht/content/detail', {'contentId': url})
        if not resp or resp.get('code') != 10000:
            return {'parse':0, 'url':'', 'jx':0}
        detail = resp.get('data', {})
        play_url = self._try_get(detail, 'videoUrl','playUrl','url','m3u8Url','sl')
        return {'parse':0, 'url':play_url or '', 'jx':0, 'header':{'User-Agent':self.headers['User-Agent'], 'Referer':self.host+'/'}}

    # ========== 图片代理 ==========
    def localProxy(self, params):
        try:
            if params.get('type') != PROXY_TYPE:
                return [404, 'text/plain', 'not found']
            img_url = params.get('url', '')
            if not img_url:
                return [400, 'text/plain', 'missing url']
            img_url = unquote(img_url)
            r = requests.get(img_url, headers={'User-Agent':self.headers['User-Agent'], 'Referer':self.host+'/'}, timeout=TIMEOUT, verify=False)
            if r.status_code != 200:
                return [404, 'text/plain', 'image not found']
            data = r.content
            if data[:2] != b'\xff\xd8' and data[:4] != b'\x89PNG' and not (data[:4]==b'RIFF' and data[8:12]==b'WEBP'):
                decoded = bytes(b ^ 0x88 for b in data)
                if decoded[:2] == b'\xff\xd8' or decoded[:4] == b'\x89PNG' or (decoded[:4]==b'RIFF' and decoded[8:12]==b'WEBP'):
                    data = decoded
            if data[:2] == b'\xff\xd8':
                return [200, 'image/jpeg', data, {'Content-Length': str(len(data))}]
            elif data[:4] == b'\x89PNG':
                return [200, 'image/png', data, {'Content-Length': str(len(data))}]
            elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
                return [200, 'image/webp', data, {'Content-Length': str(len(data))}]
            else:
                mime = r.headers.get('Content-Type', 'image/jpeg')
                if mime.startswith('image/'):
                    return [200, mime, data, {'Content-Length': str(len(data))}]
                return [404, 'text/plain', 'invalid image format']
        except Exception as e:
            log(f"图片代理错误: {e}")
            return [500, 'text/plain', 'proxy error']