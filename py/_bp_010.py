            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host + '/',
            'Origin': self.host
        }
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE

    def _xhttp(self, params):
        """使用标准库urllib发起HTTP GET请求"""
        try:
            qs = urllib.parse.urlencode(params)
            full_url = self.api_url + '?' + qs
            req = urllib.request.Request(full_url, headers=self.headers, method='GET')
            resp = urllib.request.urlopen(req, context=self._ssl_context, timeout=15)
            data = json.loads(resp.read().decode('utf-8'))
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            return []
        except Exception as e:
            print('_xhttp error: %s' % str(e), file=sys.stderr)
            return []

    def _format_time_cn(self, time_str):
        """将英文时间格式转为中文，如 '11 min' -> '11分钟'"""
        if not time_str:
            return ''
        m = re.match(r'^(\d+)\s*min\s*$', time_str.strip(), re.IGNORECASE)
        if m:
            return m.group(1) + '分钟'
        m = re.match(r'^(\d+)\s*h(?:our)?s?\s*(\d+)?\s*min\s*$', time_str.strip(), re.IGNORECASE)
        if m:
            h = m.group(1)
            mi = m.group(2)
            if mi:
                return h + '小时' + mi + '分钟'
            return h + '小时'
        return time_str

    def _extract_xvid(self, url):
        """从视频URL的查询参数中提取xvid值"""
        if not url:
            return ''
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        if 'xvid' in qs:
            return qs['xvid'][0]
        return ''

    def _build_vod_list(self, raw_data):
        """将API返回的原始数据构造为vod列表"""
        videos = []
        for item in raw_data:
            title = item.get('title', '')
            clean_title = re.sub(r'^AVOTC资源网[—-]+\s*', '', title).strip()
            if not clean_title:
                clean_title = title

            url = item.get('url', '')
            vod_id = self._extract_xvid(url)
            if not vod_id:
                vod_id = str(item.get('videoid', ''))

            videos.append({
                'vod_id': vod_id,
                'vod_name': clean_title,
                'vod_pic': item.get('img', ''),
                'vod_remarks': self._format_time_cn(item.get('time', '')),
                'vod_url': url
            })
        return videos

    def homeContent(self, filter):
        """首页：返回分类列表 + 首页视频"""
        classes = []
        for cat in CATEGORIES:
