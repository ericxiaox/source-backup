        self.session.headers.update(self.HEADERS)

    def getName(self):
        return '亚色影库'

    def init(self, extend=''):
        return None

    def isVideoFormat(self, url):
        return any(x in url.lower() for x in ['.m3u8','.mp4','.flv','.mkv','.avi','.ts'])

    def manualVideoCheck(self):
        return True

    def destroy(self):
        return None

    def _get(self, url):
        url = url if str(url).startswith('http') else urljoin(self.BASE_URL, url)
        try:
            r = self.session.get(url, timeout=12, verify=False, allow_redirects=True)
            if not r.encoding or r.encoding.lower() == 'iso-8859-1':
