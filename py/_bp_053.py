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
