        for domain in self.CANDIDATE_DOMAINS:
            try:
                h = {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; M2102J2SC Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.31 Mobile Safari/537.36',
                    'Referer': domain,
                }
                r = requests.get(f"{domain}/api/v1/categories", headers=h, timeout=3)
                if r.status_code == 200:
