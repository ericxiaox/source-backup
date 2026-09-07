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
