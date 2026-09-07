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
