# -*- coding: utf-8 -*-
import requests
import re
import sys
import json
import urllib.parse
from base.spider import Spider
from urllib.parse import urljoin

sys.path.append('..')


class Spider(Spider):
    CANDIDATE_DOMAINS = [
        "https://mdcmai4.xyz",
        "https://mdcmai5.xyz",
    ]
    decode_mode = 0

    # 网站 menu 结构 (menuId -> 菜单名)
    MENU_NAMES = {
        1: "麻豆原创",
        2: "国产AV",
        3: "岛国AV",
        4: "黑料吃瓜",
    }

    def __init__(self):
        super().__init__()
        self._xurl = None
        self._headers = None
        self._cache_cats = None  # 缓存分类列表

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
