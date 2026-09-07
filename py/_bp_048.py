
class Spider(Spider):
    def getName(self):
        return "V-HUB[成人]"

    def init(self, extend):
        # ext 统一解析：host@ 锁定主页 > JSON/文本 ext > 内置 SITE_URL（见 hostresolver.ext_of）
        try:
            from hostresolver import ext_of
            self._ext = ext_of(extend)
        except Exception:
            try:
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from hostresolver import ext_of
                self._ext = ext_of(extend)
            except Exception:
                self._ext = {}
        self.host = self._ext.get('host', '').rstrip('/') or SITE_URL
        self.api_url = self.host.rstrip('/') + '/api'
        self.headers = {
