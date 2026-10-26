# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

import re
import json
import base64
import hashlib
import hmac
import time
import uuid
import gzip
import os
import random
import requests
from base.spider import Spider

img_cache = {}

class Spider(Spider):
    def __init__(self):
        self.host = "https://adjust.cbpjoocbe.com"
        self.api_host = "https://api.51dj1.com"
        self.platform_key = "7961beb44246e3012ce228d6b5ced05a"
        self.version = "2.0.0"
        self.device_type = "web"
        self.session_id = uuid.uuid4().hex
        self.device_id = self.session_id
        self.token = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept": "*/*",
            "Origin": self.host,
            "Referer": self.host + "/home",
            "Content-Type": "application/octet-stream"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._all_videos = {}
        self._categories = []
        self._category_videos = {}  # \u6309\u5206\u7c7b\u5b58\u50a8\u89c6\u9891
        self._loaded = False
        self.class_cache = None
        self.filter_cache = {}

    def init(self, extend=""):
        if extend:
            try:
                cfg = json.loads(extend)
                self.host = (cfg.get("site") or cfg.get("base_url") or self.host).rstrip("/")
                self.api_host = self.host.replace("adjust", "api")
                self.token = cfg.get("token", self.token)
                self.headers["Origin"] = self.host
                self.headers["Referer"] = self.host + "/home"
                self.session.headers.update(self.headers)
            except Exception:
                pass
        self._ensure_token()

    def _ensure_token(self):
        if self.token:
            return True
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            import random
            
            uid = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for _ in range(16)) + str(int(time.time() * 1000))
            
            key = b"BxJand%xf5h3sycH"
            iv = b"BxJand%xf5h3sycH"
            raw = json.dumps({"devID": uid, "sysType": "pc", "isAppStore": False}, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
            encrypted = base64.b64encode(AES.new(key, AES.MODE_CBC, iv).encrypt(pad(raw, 16))).decode()
            
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Referer": self.host + "/",
                "Origin": self.host,
            }
            r = self.session.post(self.api_host + "/api/app/mine/login/h5", json={"data": encrypted}, headers=headers, timeout=15, verify=False)
            if r.status_code == 200:
                j = r.json()
                if j.get("code") == 200:
                    data = j.get("data", {})
                    if isinstance(data, dict):
                        self.token = data.get("token", "")
                    elif isinstance(data, str):
                        self.token = data
                    if self.token:
                        self.headers["Authorization"] = self.token
                        self.session.headers.update(self.headers)
                        return True
            return False
        except Exception as e:
            print("[51\u77ed\u5267] token\u83b7\u53d6\u5931\u8d25:", e)
            return False

    def _sha_bytes(self, arr):
        return hashlib.sha256(bytes.fromhex(''.join(format((int(v) + 256) % 256, 'x') for v in arr))).digest()

    def _hex_bytes(self, arr):
        return ''.join(format((int(v) + 256) % 256, 'x') for v in arr)

    def _decrypt_91_data(self, enc_data):
        """91guochan \u98ce\u683c\u7684\u89e3\u5bc6\u65b9\u6cd5"""
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
            import hashlib
            
            interface_key = '0a958fb9ac062420af6ba5f4caad779f'
            
            I = base64.b64decode(str(enc_data).replace('\n', '').replace('\r', ''))
            if len(I) < 12:
                return None
            
            e = list(interface_key.encode('utf-8')) + list(I[:12])
            n = list(self._sha_bytes(e)[8:24])
            M = len(e) // 2
            m = list(self._sha_bytes(n + e[:M]))
            a = list(self._sha_bytes(e[M:] + n))
            
            key = bytes.fromhex(self._hex_bytes(m[:8] + a[8:24] + m[24:]))
            iv = bytes.fromhex(self._hex_bytes(a[:4] + m[12:20] + a[28:]))
            
            ch = self._hex_bytes(list(I[12:]))
            ct = b''
            for i in range(0, len(ch), 5000):
                part = ch[i:i + 5000]
                if len(part) % 2:
                    part = part[:-1]
                if part:
                    ct += bytes.fromhex(part)
            
            pt = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), 16)
            return json.loads(pt.decode('utf-8'))
        except Exception as e:
            print("[51\u77ed\u5267] \u89e3\u5bc6\u5931\u8d25:", e)
            return None

    def _call_encrypted_api(self, path, params=None):
        """\u8c03\u7528\u52a0\u5bc6 API"""
        params = params or {}
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            import gzip
            import uuid
            import os
            
            rid = str(uuid.uuid4())
            iv = os.urandom(16)
            raw = json.dumps({
                "token": self.token or "",
                "deviceId": self.device_id,
                "data": params
            }, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            compressed = gzip.compress(raw)
            
            # \u4f7f\u7528 91guochan \u7684\u5bc6\u94a5\u6d3e\u751f\u65b9\u5f0f
            key = b"2acf7e91e9864673"
            iv_aes = b"1c29882d3ddfcfd6"
            cipher = AES.new(key, AES.MODE_CBC, iv_aes)
            encrypted = cipher.encrypt(pad(compressed, 16))
            encrypted_b64 = base64.b64encode(encrypted).decode()
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json, text/plain, */*",
                "Origin": self.host,
                "Referer": self.host + "/",
            }
            if self.token:
                headers["Authorization"] = self.token
            
            url = self.api_host + path
            data = {"data": encrypted_b64, "crypt": "1"}
            r = self.session.post(url, data=data, headers=headers, timeout=15, verify=False)
            
            if r.status_code == 200:
                j = r.json()
                if j.get("crypt") and j.get("data"):
                    decrypted = self._decrypt_91_data(j.get("data"))
                    if decrypted:
                        return decrypted
                return j
            return {}
        except Exception as e:
            print("[51\u77ed\u5267] API\u8c03\u7528\u5931\u8d25:", e)
            return {}

    def _decrypt_91guochan(self, enc_data):
        """91guochan \u98ce\u683c\u7684\u6570\u636e\u89e3\u5bc6"""
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
            import hashlib
            
            interface_key = '0a958fb9ac062420af6ba5f4caad779f'
            
            # \u89e3\u7801 base64
            I = base64.b64decode(str(enc_data).replace('\n', '').replace('\r', ''))
            if len(I) < 12:
                return None
            
            # \u8ba1\u7b97\u5bc6\u94a5\u548c IV\uff0891guochan \u7684\u6d3e\u751f\u65b9\u5f0f\uff09
            e = list(interface_key.encode('utf-8')) + list(I[:12])
            n = list(hashlib.sha256(bytes.fromhex(''.join(format((int(v) + 256) % 256, 'x') for v in e))).digest()[8:24])
            M = len(e) // 2
            m = list(hashlib.sha256(bytes.fromhex(''.join(format((int(v) + 256) % 256, 'x') for v in (n + e[:M])))).digest())
            a = list(hashlib.sha256(bytes.fromhex(''.join(format((int(v) + 256) % 256, 'x') for v in (e[M:] + n)))).digest())
            
            key = bytes.fromhex(''.join(format((int(v) + 256) % 256, 'x') for v in (m[:8] + a[8:24] + m[24:])))
            iv = bytes.fromhex(''.join(format((int(v) + 256) % 256, 'x') for v in (a[:4] + m[12:20] + a[28:])))
            
            # \u89e3\u5bc6\u6570\u636e
            ch = ''.join(format((int(v) + 256) % 256, 'x') for v in list(I[12:]))
            ct = b''
            for i in range(0, len(ch), 5000):
                part = ch[i:i + 5000]
                if len(part) % 2:
                    part = part[:-1]
                if part:
                    ct += bytes.fromhex(part)
            
            pt = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), 16)
            return json.loads(pt.decode('utf-8'))
        except Exception as e:
            print("[51\u77ed\u5267] \u89e3\u5bc6\u5931\u8d25:", e)
            return None

    def getName(self):
        return "51\u77ed\u5267"

    def _fetch_html(self, url):
        try:
            r = self.session.get(url, timeout=30, verify=False)
            r.encoding = 'utf-8'
            return r.text
        except Exception:
            return ""

    def _proxy_image(self, url):
        if not url:
            return ""
        if url.startswith("data:"):
            return url
        proxy = self.getProxyUrl()
        if not proxy:
            proxy = "http://127.0.0.1:9978/proxy?do=py"
        elif "?" not in proxy:
            proxy = proxy + "?do=py"
        elif "do=py" not in proxy:
            proxy = proxy + "&do=py"
        encoded = base64.b64encode(url.encode()).decode()
        return f"{proxy}&type=img&url={encoded}"

    def _list(self, data):
        if isinstance(data, list):
            return data
        if not isinstance(data, dict):
            return []
        if isinstance(data.get("list"), list):
            return data["list"]
        if isinstance(data.get("items"), list):
            return data["items"]
        if isinstance(data.get("data"), list):
            return data["data"]
        if isinstance(data.get("data"), dict):
            return self._list(data["data"])
        return []

    def _vod(self, item):
        item = item or {}
        vid = str(item.get("id") or item.get("video_id") or item.get("drama_id") or "")
        name = item.get("name") or item.get("title") or item.get("vod_name") or vid
        pic = item.get("cover") or item.get("img_y") or item.get("img_x") or item.get("img") or item.get("pic") or ""
        return {
            "vod_id": vid,
            "vod_name": name,
            "vod_pic": self._proxy_image(pic) if pic else "",
            "vod_remarks": item.get("update_label") or item.get("remarks") or "",
            "vod_content": item.get("description") or item.get("intro") or "",
            "latest_episode_id": str(item.get("latest_episode_id") or "")
        }

    def _load_data(self):
        if hasattr(self, '_loaded') and self._loaded:
            return
        if not hasattr(self, '_all_videos'):
            self._all_videos = {}
        if not hasattr(self, '_categories'):
            self._categories = []
        if not hasattr(self, '_category_videos'):
            self._category_videos = {}
        
        # \u4ece\u63a2\u7d22\u9875\u83b7\u53d6\u6570\u636e\uff08\u5305\u542b\u5168\u90e8\u5206\u7c7b\u548c\u66f4\u591a\u89c6\u9891\uff09
        explore_url = self.host + "/explore-drama?page=1"
        html = self._fetch_html(explore_url)
        if not html:
            html = self._fetch_html(self.host)
            if not html:
                return
        
        data = self._parse_nuxt_data(html)
        if not data or not isinstance(data, list):
            return
        
        # \u67e5\u627e\u5305\u542b list \u548c total \u7684\u6570\u636e
        video_list = []
        total = 0
        
        for item in data:
            if isinstance(item, dict):
                # \u68c0\u67e5\u662f\u5426\u6709 list \u5b57\u6bb5
                if "list" in item and isinstance(item["list"], list):
                    lst = item["list"]
                    if lst and len(lst) > 0:
                        # \u68c0\u67e5\u7b2c\u4e00\u4e2a\u5143\u7d20\u662f\u5426\u6709 video_id
                        first = lst[0] if lst else None
                        if isinstance(first, dict) and "video_id" in first:
                            video_list = lst
                            total = item.get("total", len(lst))
                            break
                        # \u68c0\u67e5\u662f\u5426\u662f data \u5305\u88c5
                        inner_data = item.get("data")
                        if isinstance(inner_data, dict) and "list" in inner_data:
                            video_list = inner_data["list"]
                            total = inner_data.get("total", len(video_list))
                            break
        
        # \u5982\u679c\u627e\u5230\u4e86\u89c6\u9891\u5217\u8868\uff0c\u89e3\u6790\u5b83
        if video_list:
            # \u63d0\u53d6\u5206\u7c7b\uff08\u4ece\u9875\u9762\u4e2d\u7684\u7b5b\u9009\u6807\u7b7e\uff09
            categories = []
            # \u4ece HTML \u4e2d\u63d0\u53d6\u5206\u7c7b\u6807\u7b7e
            theme_pattern = r'<span[^>]*data-active="[^"]*"[^>]*>([^<]+)</span>'
            theme_matches = re.findall(theme_pattern, html)
            # \u8fc7\u6ee4\u51fa\u5206\u7c7b\u540d\u79f0
            seen = set()
            for name in theme_matches:
                name = name.strip()
                if name and name not in seen and len(name) <= 10:
                    seen.add(name)
                    categories.append({"type_id": str(len(categories) + 1), "type_name": name})
            
            # \u5982\u679c\u6ca1\u6709\u63d0\u53d6\u5230\u5206\u7c7b\uff0c\u4f7f\u7528\u9ed8\u8ba4\u5206\u7c7b
            if not categories:
                categories = [
                    {"type_id": "1", "type_name": "\u5168\u90e8\u77ed\u5267"},
                    {"type_id": "2", "type_name": "\u70ed\u95e8\u63a8\u8350"},
                    {"type_id": "3", "type_name": "\u6700\u65b0\u4e0a\u7ebf"}
                ]
            
            self._categories = categories
            self._category_videos = {c["type_id"]: [] for c in categories}
            
            # \u89e3\u6790\u89c6\u9891\u5217\u8868
            for v in video_list:
                if isinstance(v, dict):
                    vid = str(v.get("video_id", ""))
                    if vid and vid.isdigit():
                        cover = v.get("cover", "")
                        if cover and not cover.startswith("http"):
                            cover = self.host + cover
                        video_info = {
                            "vod_id": vid,
                            "vod_name": v.get("title", ""),
                            "vod_pic": self._proxy_image(cover) if cover else "",
                            "vod_remarks": "",
                            "vod_content": v.get("intro", "")[:200] if v.get("intro") else "",
                            "latest_episode_id": str(v.get("latest_episode_id", ""))
                        }
                        self._all_videos[vid] = video_info
                        # \u6dfb\u52a0\u5230\u7b2c\u4e00\u4e2a\u5206\u7c7b
                        if self._categories:
                            first_tid = self._categories[0]["type_id"]
                            self._category_videos[first_tid].append(video_info)
            
            self._loaded = True
            return
        
        # \u5982\u679c\u63a2\u7d22\u9875\u6ca1\u6709\u63d0\u53d6\u5230\u6570\u636e\uff0c\u56de\u9000\u5230\u9996\u9875\u89e3\u6790
        html = self._fetch_html(self.host)
        if not html:
            return
        
        data = self._parse_nuxt_data(html)
        if not data or not isinstance(data, list):
            return
        
        target_idx = None
        for item in data:
            if isinstance(item, dict) and "data" in item:
                idx = item["data"]
                if isinstance(idx, int) and idx < len(data):
                    target = data[idx]
                    if isinstance(target, dict) and ("top_list" in target or "modules" in target):
                        target_idx = idx
                        break
        
        if target_idx is None:
            return
        
        target = data[target_idx]
        
        # \u63d0\u53d6\u5206\u7c7b\u5217\u8868\uff08\u4ece modules\uff09
        modules_idx = target.get("modules")
        if modules_idx is not None and isinstance(modules_idx, int) and modules_idx < len(data):
            modules_container = data[modules_idx]
            if isinstance(modules_container, dict):
                list_idx = modules_container.get("list")
                if isinstance(list_idx, int):
                    modules = data[list_idx]
                elif isinstance(list_idx, list):
                    modules = list_idx
                else:
                    modules = []
            elif isinstance(modules_container, list):
                modules = modules_container
            else:
                modules = []
            
            if isinstance(modules, list):
                for mod_idx in modules:
                    if isinstance(mod_idx, int) and mod_idx < len(data):
                        mod = data[mod_idx]
                        if isinstance(mod, dict):
                            tid = str(self._get_value(data, mod.get("id", "")))
                            name = self._get_value(data, mod.get("title", ""))
                            if tid and name:
                                self._categories.append({"type_id": tid, "type_name": str(name)})
                                if tid not in self._category_videos:
                                    self._category_videos[tid] = []
                                
                                items_idx = mod.get("items", [])
                                if isinstance(items_idx, int) and items_idx < len(data):
                                    actual_items = data[items_idx]
                                elif isinstance(items_idx, list):
                                    actual_items = items_idx
                                else:
                                    actual_items = []
                                
                                if isinstance(actual_items, list):
                                    for item_idx in actual_items:
                                        if isinstance(item_idx, int) and item_idx < len(data):
                                            v = data[item_idx]
                                            if isinstance(v, dict):
                                                vid = str(self._get_value(data, v.get("video_id", "")))
                                                if vid and vid.isdigit() and vid not in self._all_videos:
                                                    pic_url = self._get_value(data, v.get("cover", ""))
                                                    video_info = {
                                                        "vod_id": vid,
                                                        "vod_name": self._get_value(data, v.get("title", "")),
                                                        "vod_pic": self._proxy_image(pic_url) if pic_url else "",
                                                        "vod_remarks": "",
                                                        "vod_content": self._get_value(data, v.get("intro", ""))[:200],
                                                        "latest_episode_id": str(self._get_value(data, v.get("latest_episode_id", "")))
                                                    }
                                                    self._all_videos[vid] = video_info
                                                    self._category_videos[tid].append(video_info)
        
        # \u5982\u679c\u5206\u7c7b\u4e3a\u7a7a\uff0c\u6dfb\u52a0\u9ed8\u8ba4\u5206\u7c7b
        if not self._categories:
            self._categories = [
                {"type_id": "1", "type_name": "AI\u6210\u4eba\u77ed\u5267"},
                {"type_id": "2", "type_name": "\u539f\u521b\u77ed\u5267"},
                {"type_id": "3", "type_name": "\u70ed\u95e8\u7cbe\u9009\u77ed\u5267"}
            ]
            self._category_videos = {c["type_id"]: [] for c in self._categories}
        
        # \u63d0\u53d6 top_list\uff08\u9996\u9875\u63a8\u8350\uff09
        top_list_idx = target.get("top_list")
        if top_list_idx is not None and isinstance(top_list_idx, int) and top_list_idx < len(data):
            top_list = data[top_list_idx]
            if isinstance(top_list, list):
                for idx in top_list:
                    if isinstance(idx, int) and idx < len(data):
                        v = data[idx]
                        if isinstance(v, dict):
                            vid = str(self._get_value(data, v.get("video_id", "")))
                            if vid and vid.isdigit() and vid not in self._all_videos:
                                pic_url = self._get_value(data, v.get("cover", ""))
                                video_info = {
                                    "vod_id": vid,
                                    "vod_name": self._get_value(data, v.get("title", "")),
                                    "vod_pic": self._proxy_image(pic_url) if pic_url else "",
                                    "vod_remarks": "",
                                    "vod_content": self._get_value(data, v.get("intro", ""))[:200],
                                    "latest_episode_id": str(self._get_value(data, v.get("latest_episode_id", "")))
                                }
                                self._all_videos[vid] = video_info
                                if self._categories and len(self._categories) > 0:
                                    first_tid = self._categories[0]["type_id"]
                                    if first_tid not in self._category_videos:
                                        self._category_videos[first_tid] = []
                                    self._category_videos[first_tid].append(video_info)
        
        self._loaded = True

    def _get_value(self, data, idx):
        if isinstance(idx, int) and idx < len(data):
            return data[idx]
        return idx

    def _parse_nuxt_data(self, html):
        pattern = r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>'
        m = re.search(pattern, html, re.S)
        if not m:
            return None
        try:
            return json.loads(m.group(1))
        except Exception:
            return None

    def homeContent(self, filter=False):
        self._load_data()
        return {"class": self._categories, "list": list(self._all_videos.values())[:20]}

    def homeVideoContent(self):
        # \u5c1d\u8bd5\u4ece\u52a0\u5bc6 API \u83b7\u53d6\u6570\u636e
        data = self._call_encrypted_api("/api.php/api/theater/exploreList", {})
        # \u8c03\u8bd5\uff1a\u5982\u679c data \u662f dict\uff0c\u68c0\u67e5\u662f\u5426\u6709 list
        if data and isinstance(data, dict):
            print("[51\u77ed\u5267] API\u8fd4\u56dekeys:", list(data.keys()))
            # \u68c0\u67e5 data.data \u6216 data.list
            items = self._list(data.get("data", data) if isinstance(data, dict) else data)
            if items:
                print("[51\u77ed\u5267] API\u8fd4\u56deitems\u6570\u91cf:", len(items))
                return {"list": [self._vod(x) for x in items[:20]]}
        # \u56de\u9000\u5230\u9759\u6001 HTML \u89e3\u6790
        print("[51\u77ed\u5267] \u56de\u9000\u5230\u9759\u6001\u89e3\u6790")
        self._load_data()
        return {"list": list(self._all_videos.values())[:20]}

    def categoryContent(self, tid, pg=1, filter=False, extend=""):
        page = int(pg) if str(pg).isdigit() else 1
        page_size = 24
        
        # \u52a8\u6001\u8bf7\u6c42\u63a2\u7d22\u9875
        explore_url = self.host + "/explore-drama?page=" + str(page)
        html = self._fetch_html(explore_url)
        
        videos = []
        total = 0
        
        if html:
            data = self._parse_nuxt_data(html)
            if data and isinstance(data, list):
                # \u67e5\u627e list \u6570\u636e
                for item in data:
                    if isinstance(item, dict):
                        if "list" in item and isinstance(item["list"], list):
                            lst = item["list"]
                            if lst and len(lst) > 0:
                                first = lst[0] if lst else None
                                if isinstance(first, dict) and "video_id" in first:
                                    total = item.get("total", len(lst))
                                    for v in lst:
                                        if isinstance(v, dict):
                                            vid = str(v.get("video_id", ""))
                                            if vid and vid.isdigit():
                                                cover = v.get("cover", "")
                                                if cover and not cover.startswith("http"):
                                                    cover = self.host + cover
                                                videos.append({
                                                    "vod_id": vid,
                                                    "vod_name": v.get("title", ""),
                                                    "vod_pic": self._proxy_image(cover) if cover else "",
                                                    "vod_remarks": "",
                                                    "vod_content": v.get("intro", "")[:200] if v.get("intro") else "",
                                                    "latest_episode_id": str(v.get("latest_episode_id", ""))
                                                })
                                    break
                        # \u68c0\u67e5 data \u5305\u88c5
                        inner_data = item.get("data")
                        if isinstance(inner_data, dict) and "list" in inner_data:
                            lst = inner_data["list"]
                            if lst and len(lst) > 0:
                                total = inner_data.get("total", len(lst))
                                for v in lst:
                                    if isinstance(v, dict):
                                        vid = str(v.get("video_id", ""))
                                        if vid and vid.isdigit():
                                            cover = v.get("cover", "")
                                            if cover and not cover.startswith("http"):
                                                cover = self.host + cover
                                            videos.append({
                                                "vod_id": vid,
                                                "vod_name": v.get("title", ""),
                                                "vod_pic": self._proxy_image(cover) if cover else "",
                                                "vod_remarks": "",
                                                "vod_content": v.get("intro", "")[:200] if v.get("intro") else "",
                                                "latest_episode_id": str(v.get("latest_episode_id", ""))
                                            })
                                break
        
        # \u5982\u679c\u63d0\u53d6\u5931\u8d25\uff0c\u56de\u9000\u5230\u7f13\u5b58
        if not videos:
            self._load_data()
            if tid and tid in self._category_videos:
                items = self._category_videos.get(tid, [])
            else:
                items = list(self._all_videos.values())
            
            total = len(items)
            pagecount = (total + page_size - 1) // page_size if total > 0 else 1
            start = (page - 1) * page_size
            end = start + page_size
            paginated = items[start:end] if items else []
            return {"page": page, "pagecount": pagecount, "limit": page_size, "total": total, "list": paginated}
        
        pagecount = (total + page_size - 1) // page_size if total > 0 else 1
        
        return {"page": page, "pagecount": pagecount, "limit": page_size, "total": total, "list": videos}

    def detailContent(self, ids):
        vid = str(ids[0]) if ids and isinstance(ids, list) else str(ids)
        if not vid:
            return {"list": []}
        self._load_data()
        detail = self._all_videos.get(vid, {})
        if not detail:
            html = self._fetch_html(self.host + "/drama-detail/" + vid + "/")
            name = re.search(r'<title>(.*?)</title>', html)
            if name:
                detail["vod_name"] = name.group(1).split(" - ")[0].strip()
            pic = re.search(r'<meta property="og:image" content="([^"]+)"', html)
            if pic:
                detail["vod_pic"] = pic.group(1)
        vod_name = detail.get("vod_name", "51\u77ed\u5267")
        vod_pic = detail.get("vod_pic", "")
        episodes = []
        html = self._fetch_html(self.host + "/drama-play?id=" + vid)
        if html:
            play_url = re.search(r'<source[^>]+src="([^"]+)"', html)
            if play_url:
                episodes.append("\u5168\u96c6$%s" % play_url.group(1))
        if not episodes:
            m3u8 = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html) if html else None
            if m3u8:
                episodes.append("\u5168\u96c6$%s" % m3u8.group(1))
        if not episodes:
            episodes.append("\u5168\u96c6$%s" % vid)
        vod_play_url = "#".join(episodes) if episodes else ""
        vod = {
            "vod_id": vid,
            "vod_name": vod_name,
            "vod_pic": self._proxy_image(vod_pic) if vod_pic else "",
            "vod_play_from": "51\u77ed\u5267",
            "vod_play_url": vod_play_url,
            "vod_content": detail.get("vod_content", ""),
            "vod_remarks": ("\u5171%d\u96c6" % len(episodes)) if episodes else ""
        }
        return {"list": [vod]}

    def searchContent(self, key, quick=False, pg=1):
        self._load_data()
        results = []
        key_lower = key.lower()
        for vid, info in self._all_videos.items():
            if key_lower in info.get("vod_name", "").lower():
                results.append({"vod_id": vid, "vod_name": info.get("vod_name", ""), "vod_pic": info.get("vod_pic", ""), "vod_remarks": ""})
        return {"list": results[:20]}

    def playerContent(self, flag, id, vipFlags=None):
        if isinstance(id, str) and id.startswith("http"):
            return {"playUrl": "", "url": id, "parse": 0, "header": self.headers, "position": "0"}
        html = self._fetch_html(self.host + "/drama-play?id=" + str(id))
        if html:
            m3u8 = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html)
            if m3u8:
                return {"playUrl": "", "url": m3u8.group(1), "parse": 0, "header": self.headers, "position": "0"}
            mp4 = re.search(r'(https?://[^\s"\']+\.mp4[^\s"\']*)', html)
            if mp4:
                return {"playUrl": "", "url": mp4.group(1), "parse": 0, "header": self.headers, "position": "0"}
        return {"playUrl": "", "msg": "\u65e0\u6cd5\u83b7\u53d6\u64ad\u653e\u5730\u5740: %s" % id}

    def localProxy(self, param):
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
            type_ = param.get('type')
            url = param.get('url')
            if type_ == 'img':
                try:
                    real_url = base64.b64decode(url).decode('utf-8')
                except Exception:
                    real_url = url
                if not real_url.startswith('http'):
                    return [404, 'text/plain', b'Invalid URL']
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Referer": self.host + "/"}
                res = requests.get(real_url, headers=headers, timeout=20)
                if res.status_code != 200:
                    return [404, 'text/plain', b'Image not found']
                data = res.content
                key = b"f5d965df75336270"
                iv = b"97b60394abc2fbe1"
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted = unpad(cipher.decrypt(data), AES.block_size)
                if decrypted[:3] == b"\xff\xd8\xff":
                    return [200, 'image/jpeg', decrypted, {'Content-Length': str(len(decrypted))}]
                if decrypted[:4] == b"\x89PNG":
                    return [200, 'image/png', decrypted, {'Content-Length': str(len(decrypted))}]
                if decrypted[:4] == b"GIF8":
                    return [200, 'image/gif', decrypted, {'Content-Length': str(len(decrypted))}]
                return [200, 'image/jpeg', decrypted, {'Content-Length': str(len(decrypted))}]
            return [404, 'text/plain', b'Unknown type']
        except Exception as e:
            return [500, 'text/plain', str(e).encode()]

    def destroy(self):
        global img_cache
        img_cache.clear()
        if hasattr(self, 'session'):
            self.session.close()