            "vod_year": row["vod_year"] or "",
            "vod_tags": tags,
            "vod_content": row["vod_content"] or "",
            "vod_play_from": row["vod_play_from"] or "whos.tv",
            "vod_play_url": play_url,
            "type_name": row["type_name"] or "成人影片"
        }]}

    def _fix_v_encoded_url(self, raw_url):
        if not raw_url:
            return raw_url
        for prefix in ["高清$ ", "高清$", "高清 ", "高清"]:
            if raw_url.startswith(prefix):
                raw_url = raw_url[len(prefix):]
                break
        url = raw_url.replace('://V', '://')
        url = url.replace('V', '/')
        return url

    # ==================== 播放 ====================
    def playerContent(self, flag, id, vipFlags=None):
        playurl = id.split("|")[0]
        playurl = self._fix_v_encoded_url(playurl)
        headers = {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; MIbox PRO Build/PI)"}
        if playurl.strip().lower().endswith('.m3u8'):
            try:
                parsed = urlparse(playurl)
                headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"
            except:
                pass
        return {"parse": 0, "url": playurl, "header": headers}

    # ==================== 搜索（暂不启用） ====================
    def searchContent(self, key, quick, pg="1"):
        return {"list": [], "page": pg}


# ========== 蜜桃主爬虫（不变） ==========
class Spider(BaseSpider):
    def getName(self):
        return "蜜桃视频"

    def isVideoFormat(self, url):
        return url and ('.mp4' in url or '.m3u8' in url or '.ts' in url)

    def manualVideoCheck(self):
        return False

    filterable = True
    searchable = True
    host = SITES[0]['host']
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "lang": "cn",
        "deviceType": "H5-android",
    }

    _speed_cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.mitao_cache.json')
    _speed_cache_ttl = 1800
    _lock = threading.Lock()
    _speed_test_done = False
    _api_fail_count = 0
    _max_api_fail = 3

    _user_id = ''
    _session_id = ''
    _device_id = ''
    _session_inited = False
    _categories = []
    _video_type_list = []

    _session_cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.mitao_session.json')
    _session_cache_ttl = 1800

    def __init__(self):
        super().__init__()
        self.siku = SikuEngine()
        self.siku.init()

    # ========== 蜜桃网络功能 ==========
    def _fetch_remote_sites(self):
        if not SITES_REMOTE_URL:
            return
        try:
            r = requests.get(SITES_REMOTE_URL, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and len(data) > 0 and 'host' in data[0]:
                    global SITES
                    SITES = data
                    log(f"远程站点更新成功，共 {len(SITES)} 个")
        except Exception as e:
            log(f"获取远程站点失败: {e}")

    def _get_cached_site(self):
        try:
            if os.path.exists(self._speed_cache_file):
                with open(self._speed_cache_file, 'r') as f:
                    data = json.load(f)
                if time.time() - data.get('ts', 0) < self._speed_cache_ttl:
                    return data.get('host', ''), True
        except: pass
        return '', False

    def _save_cached_site(self, host):
        try:
            with open(self._speed_cache_file, 'w') as f:
                json.dump({'host': host, 'ts': time.time()}, f)
        except: pass

    def _select_best_site(self, force=False):
        if self._speed_test_done and not force:
            return
        self._fetch_remote_sites()
        if not force:
            cached_host, valid = self._get_cached_site()
            if valid:
                self.host = cached_host
                self._speed_test_done = True
                return
        results = {}
        all_sites = SITES + BACKUP_SITES
        def test_site(site):
            try:
                start = time.time()
                r = requests.get(site['host'], headers=self.headers, timeout=TIMEOUT, verify=False)
                if 200 <= r.status_code < 500:
                    results[site['name']] = time.time() - start
                else:
                    results[site['name']] = 999
            except:
                results[site['name']] = 999
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(all_sites)) as executor:
            futures = [executor.submit(test_site, s) for s in all_sites]
            concurrent.futures.wait(futures, timeout=TIMEOUT + 2)
        valid_sites = [s for s in all_sites if results.get(s['name'], 999) < TIMEOUT]
        if valid_sites:
            best = min(valid_sites, key=lambda x: results[x['name']])
            self.host = best['host']
        else:
            self.host = all_sites[0]['host']
            log("所有站点测速失败，使用第一个站点")
        self._speed_test_done = True
        self._save_cached_site(self.host)
        log(f"当前工作站点: {self.host}")

    def _save_session_cache(self):
        try:
            data = {
