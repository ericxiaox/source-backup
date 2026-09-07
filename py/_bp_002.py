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
                'ts': time.time(),
                'user_id': self._user_id,
                'session_id': self._session_id,
                'device_id': self._device_id,
                'categories': self._categories,
                'video_type_list': self._video_type_list,
            }
            with open(self._session_cache_file, 'w') as f:
                json.dump(data, f, ensure_ascii=False)
        except: pass

    def _load_session_cache(self):
        try:
            if not os.path.exists(self._session_cache_file):
                return False
            with open(self._session_cache_file, 'r') as f:
                data = json.load(f)
            if time.time() - data.get('ts', 0) >= self._session_cache_ttl:
                return False
            self._user_id = data.get('user_id', '')
            self._session_id = data.get('session_id', '')
            self._device_id = data.get('device_id', '')
            self._categories = data.get('categories', [])
            self._video_type_list = data.get('video_type_list', [])
            if not self._user_id or not self._session_id:
                return False
            return True
        except: return False

    @staticmethod
    def _zero_pad(data, block_size=16):
        pad_len = block_size - (len(data) % block_size)
        return data if pad_len == block_size else data + b'\x00' * pad_len

    @staticmethod
    def _zero_unpad(data):
        return data.rstrip(b'\x00')

    def _gen_key(self, timestamp):
        return str(timestamp)[-6:] + SIGN_KEY[:4] + BUNDLE_ID[:6]

    def _gen_iv(self):
        return BUNDLE_ID[-6:] + SIGN_KEY[-4:] + self._device_id[:6]

    def _aes_encrypt(self, plaintext, key_str, iv_str):
        key, iv = key_str.encode(), iv_str.encode()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded = self._zero_pad(plaintext.encode())
        return base64.b64encode(cipher.encrypt(padded)).decode()

    def _aes_decrypt(self, ciphertext_b64, key_str, iv_str):
        try:
            key, iv = key_str.encode(), iv_str.encode()
            cipher = AES.new(key, AES.MODE_CBC, iv)
            cleaned = re.sub(r'\s', '', ciphertext_b64)
            encrypted = base64.b64decode(cleaned)
            decrypted = cipher.decrypt(encrypted)
            try:
                return self._zero_unpad(decrypted).decode('utf-8', errors='replace')
            except:
                pad_len = decrypted[-1]
                if 1 <= pad_len <= 16:
                    return decrypted[:-pad_len].decode('utf-8', errors='replace')
                return decrypted.decode('utf-8', errors='replace')
        except Exception as e:
            log(f"AES解密失败: {e}")
            return ''

    def _generate_sign(self, params, api_path):
        sorted_keys = sorted(params.keys())
        concat = ''.join(str(params[k]) for k in sorted_keys)
        return hashlib.md5((concat + SIGN_KEY + api_path).encode()).hexdigest().upper()

    @staticmethod
    def _generate_device_id():
        return 'H5-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

    def _common_params(self):
        hostname = self.host.replace('https://', '').replace('http://', '')
        return {'timezone': 'Asia/Karachi', 'version': VERSION, 'channelId': 67,
                'channelId2': hostname, 'brandId': BRAND_ID}

    def _api_request(self, endpoint, params=None, skip_encrypt=False, _t=None, retry=2):
        if params is None:
            params = {}
        timestamp = str(_t) if _t else str(int(time.time() * 1000))
        key_str = self._gen_key(timestamp)
        iv_str = self._gen_iv()
        full_params = self._common_params()
        full_params['t'] = timestamp
        full_params.update(params)
        full_params['sign'] = self._generate_sign(full_params, endpoint)
        api_url = self.host + endpoint
        headers = dict(self.headers)
        headers['t'] = timestamp
        if self._user_id:
            headers['userId'] = self._user_id
        if self._session_id:
            headers['sessionId'] = self._session_id
        headers['deviceId'] = self._device_id or ''
        headers['bundleId'] = BUNDLE_ID
        if skip_encrypt:
            body = json.dumps(full_params, ensure_ascii=False, separators=(',', ':'))
            headers['Content-Type'] = 'application/json'
            headers['encrypt'] = 'false'
        else:
            plain = json.dumps(full_params, ensure_ascii=False, separators=(',', ':'))
            body = self._aes_encrypt(plain, key_str, iv_str)
            headers['Content-Type'] = 'text/plain'
            headers['encrypt'] = 'true'
        for attempt in range(retry):
            try:
                r = self.session.post(api_url, data=body, headers=headers, timeout=TIMEOUT, verify=False)
                resp = r.json()
                if resp.get('code') == 10000 and isinstance(resp.get('data'), str) and resp['data']:
                    decrypted = self._aes_decrypt(resp['data'], key_str, iv_str)
                    if decrypted:
                        resp['data'] = json.loads(decrypted)
                self._api_fail_count = 0
                return resp
            except Exception as e:
                log(f"API请求失败 {endpoint}: {e}")
                if attempt == retry - 1:
                    self._api_fail_count += 1
                    if self._api_fail_count >= self._max_api_fail:
                        log("连续失败次数过多，尝试切换站点...")
                        self._select_best_site(force=True)
                        self._api_fail_count = 0
                    return None
                time.sleep(0.5)
        return None

    def _ensure_session(self):
        if self._session_inited:
            return
        if self._load_session_cache():
            self._session_inited = True
            if not self._video_type_list:
                self._refresh_video_type_list()
            if self._categories:
                return
        if not self._device_id:
            self._device_id = self._generate_device_id()
        appcfg = self._api_request('/ht/users/appConfig')
        if appcfg and appcfg.get('code') == 10000:
            ac_data = appcfg.get('data', {})
            if isinstance(ac_data, dict) and ac_data.get('appConfig'):
                ac_cfg = ac_data['appConfig']
                if isinstance(ac_cfg, dict) and ac_cfg.get('videoTypeList'):
                    self._video_type_list = ac_cfg['videoTypeList']
        shared_t = int(time.time() * 1000)
        resp1 = self._api_request('/ht/users/initH5_1', _t=shared_t)
        if resp1 and resp1.get('code') == 10000:
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