
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
