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
                r.encoding = 'utf-8'
            return r.text
        except requests.RequestException:
            return ''

    def _soup(self, html):
        return BeautifulSoup(html, 'html.parser') if BeautifulSoup else None

    def _txt(self, s):
        return re.sub(r'\s+', ' ', s or '').strip()

    def _abs(self, u):
        if not u:
            return ''
        if u.startswith('//'):
            return 'https:' + u
        return urljoin(self.BASE_URL, u)

    def _meta(self, html, name):
        m = re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)' % re.escape(name), html, re.I)
        return self._txt(m.group(1)) if m else ''

    def _id(self, url):
        url = self._abs(url).split('?')[0].rstrip('/')
        return url.replace(self.BASE_URL + '/', '')

    def _parse_list(self, html):
        arr = []
        if BeautifulSoup and html:
            soup = self._soup(html)
            for a in soup.select('article.loop-video.thumb-block a[href]'):
                href = self._abs(a.get('href'))
                if '/video/' not in href:
                    continue
                img = a.select_one('img')
                title = self._txt(a.get('title') or (img.get('alt') if img else '') or (a.select_one('header.entry-header span').get_text(' ', strip=True) if a.select_one('header.entry-header span') else ''))
                pic = self._abs((img.get('data-src') or img.get('src') or img.get('data-original')) if img else '')
                remark = self._txt(' '.join([x.get_text(' ', strip=True) for x in a.select('span.hd-video,span.views,span.duration')]))
                if title and href:
                    arr.append({'vod_id':self._id(href),'vod_name':title,'vod_pic':pic,'vod_remarks':remark})
        if not arr:
            for it in re.findall(r'<article[^>]+loop-video[\s\S]*?</article>', html, re.I):
                h = re.search(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*title=["\']([^"\']+)', it, re.I)
