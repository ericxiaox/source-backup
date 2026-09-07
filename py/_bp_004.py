            classes.append({'type_id': cat['type_id'], 'type_name': cat['type_name']})

        raw_data = self._xhttp({'play': 'list', 'page': 1})
        videos = self._build_vod_list(raw_data)

        return {'class': classes, 'list': videos}

    def homeVideoContent(self):
        return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        """分类内容"""
        raw_data = self._xhttp({'play': 'class', 'c': tid, 'page': pg})
        videos = self._build_vod_list(raw_data)

        type_name = tid
        for cat in CATEGORIES:
            if cat['type_id'] == tid:
                type_name = cat['type_name']
                break

        return {
            'page': int(pg),
            'pagecount': 9999,
            'limit': 90,
            'total': 9999,
            'type_name': type_name,
            'list': videos
        }

    def detailContent(self, array):
        """详情：通过xvid获取视频播放地址"""
        result = {}
        if not array or not array[0]:
            return result

        xvid = array[0]
        vod = {
            'vod_id': xvid,
            'vod_name': '视频详情',
            'vod_pic': '',
            'vod_remarks': '',
            'vod_play_from': 'newxvideos',
            'vod_play_url': ''
        }

        try:
            qs = urllib.parse.urlencode({'xvid': xvid})
            full_url = self.api_url + '?' + qs
            req = urllib.request.Request(full_url, headers=self.headers, method='GET')
            resp = urllib.request.urlopen(req, context=self._ssl_context, timeout=15)
            data = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            print('detailContent error: %s' % str(e), file=sys.stderr)
            result['list'] = [vod]
            return result

        play_urls = []

        if isinstance(data, dict):
            item = data
            if 'data' in data and isinstance(data['data'], dict):
                item = data['data']

            hls_url = item.get('hls') or item.get('m3u8') or ''
            hight_url = item.get('hight') or item.get('high') or item.get('hd') or ''
            low_url = item.get('low') or item.get('sd') or ''

            if hls_url:
                play_urls.append('高清HLS$' + hls_url)
            if hight_url:
                play_urls.append('高清MP4$' + hight_url)
            if low_url:
                play_urls.append('低清MP4$' + low_url)

            title = item.get('title', '')
            if title:
                clean_title = re.sub(r'^AVOTC资源网[—-]+\s*', '', title).strip()
                if clean_title:
                    vod['vod_name'] = clean_title

            img = item.get('img', '')
            if img:
                vod['vod_pic'] = img

            time_str = item.get('time', '')
            if time_str:
                vod['vod_remarks'] = self._format_time_cn(time_str)

        elif isinstance(data, list):
            for item in data:
                hls_url = item.get('hls') or item.get('m3u8') or ''
                hight_url = item.get('hight') or item.get('high') or item.get('hd') or ''
                low_url = item.get('low') or item.get('sd') or ''

                if hls_url:
                    play_urls.append('高清HLS$' + hls_url)
                if hight_url:
                    play_urls.append('高清MP4$' + hight_url)
                if low_url:
                    play_urls.append('低清MP4$' + low_url)

                if vod['vod_name'] == '视频详情':
                    title = item.get('title', '')
                    if title:
                        clean_title = re.sub(r'^AVOTC资源网[—-]+\s*', '', title).strip()
                        if clean_title:
                            vod['vod_name'] = clean_title
                    img = item.get('img', '')
                    if img:
                        vod['vod_pic'] = img
                    time_str = item.get('time', '')
                    if time_str:
                        vod['vod_remarks'] = self._format_time_cn(time_str)

        if play_urls:
            vod['vod_play_url'] = '#'.join(play_urls)

        result['list'] = [vod]
        return result

    def searchContent(self, key, quick, pg='1'):
        """搜索"""
        raw_data = self._xhttp({'play': 'k', 'k': key, 'page': pg})
        videos = self._build_vod_list(raw_data)

        return {
            'page': int(pg),
            'pagecount': 9999,
            'limit': 90,
            'total': 9999,
            'list': videos
        }

    def playerContent(self, flag, id, vipFlags):
        """播放地址解析 - 直接返回用户选择的清晰度地址"""
        if id and (id.startswith('http://') or id.startswith('https://')):
            return {
                'parse': 0,
                'playUrl': '',
                'url': id,
                'header': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': self.host + '/'
                }
            }
        return {'parse': 0, 'playUrl': '', 'url': '', 'header': {}}

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return {}