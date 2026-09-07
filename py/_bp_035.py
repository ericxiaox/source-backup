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
