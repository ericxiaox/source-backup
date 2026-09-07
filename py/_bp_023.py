#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import requests
from urllib.parse import quote, urljoin
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None
try:
    from base.spider import Spider as BaseSpider
except Exception:
    BaseSpider = object

class Spider(BaseSpider):
    BASE_URL = 'https://www.yasetube.com'
    HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8','Referer':'https://www.yasetube.com/'}
    CATS = {'nvce':'女厕偷拍','fc2-ppv':'FC2 PPV','me':'Mesubuta系列','milf':'MILF人妻无码','dalu':'自拍偷拍','madou':'品牌传媒'}

    def __init__(self):
        self.session = requests.Session()
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
