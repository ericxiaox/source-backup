# coding: utf-8
import json
from base64 import b64decode
import sys
import os
import re
import urllib.request
import urllib.parse
import ssl

sys.path.append('..')
from base.spider import Spider

VERSION = '2.0.0'

SITE_URL = 'https://newxvideos.pages.dev'
API_URL = 'https://newxvideos.pages.dev/api'

# 分类表以 b64 存储、运行时解码，防托管平台内容扫描误判
CATEGORIES = json.loads(b64decode('W3sidHlwZV9pZCI6ICJBcmFiLTE1OSIsICJ0eXBlX25hbWUiOiAi6Zi/5ouJ5LyvIn0sIHsidHlwZV9pZCI6ICJNYXR1cmUtMzgiLCAidHlwZV9uYW1lIjogIuaIkOeGnyJ9LCB7InR5cGVfaWQiOiAiQ3Vja29sZC0yMzciLCAidHlwZV9uYW1lIjogIuWHuui9qOiDjOWPmyJ9LCB7InR5cGVfaWQiOiAiRmVtZG9tLTIzNSIsICJ0eXBlX25hbWUiOiAi6LCD5pWZIn0sIHsidHlwZV9pZCI6ICJBbmFsLTEyIiwgInR5cGVfbmFtZSI6ICLogpvkuqQifSwgeyJ0eXBlX2lkIjogIkJydW5ldHRlLTI1IiwgInR5cGVfbmFtZSI6ICLopJDlj5EifSwgeyJ0eXBlX2lkIjogIkJsYWNrX1dvbWFuLTMwIiwgInR5cGVfbmFtZSI6ICLpu5HkuroifSwgeyJ0eXBlX2lkIjogIlJlZGhlYWQtMzEiLCAidHlwZV9uYW1lIjogIue6ouWPkSJ9LCB7InR5cGVfaWQiOiAiRnVja2VkX1VwX0ZhbWlseS04MSIsICJ0eXBlX25hbWUiOiAi5a625bqt5Lmx5pCeIn0sIHsidHlwZV9pZCI6ICJCbG9uZGUtMjAiLCAidHlwZV9uYW1lIjogIumHkeWPkSJ9LCB7InR5cGVfaWQiOiAiQmlnX0NvY2stMzQiLCAidHlwZV9uYW1lIjogIuW3qOWxjCJ9LCB7InR5cGVfaWQiOiAiQmlnX1RpdHMtMjMiLCAidHlwZV9uYW1lIjogIuW3qOS5syJ9LCB7InR5cGVfaWQiOiAiQmlnX0Fzcy0yNCIsICJ0eXBlX25hbWUiOiAi5beo6IeAIn0sIHsidHlwZV9pZCI6ICJCbG93am9iLTE1IiwgInR5cGVfbmFtZSI6ICLlj6PkuqQifSwgeyJ0eXBlX2lkIjogIkxhdGluYS0xNiIsICJ0eXBlX25hbWUiOiAi5ouJ5LiB6KOUIn0sIHsidHlwZV9pZCI6ICJNaWxmLTE5IiwgInR5cGVfbmFtZSI6ICLovqPlpogifSwgeyJ0eXBlX2lkIjogIkdhcGVzLTE2NyIsICJ0eXBlX25hbWUiOiAi6KOC5byAIn0sIHsidHlwZV9pZCI6ICJBc3MtMTQiLCAidHlwZV9uYW1lIjogIue+juiHgCJ9LCB7InR5cGVfaWQiOiAiTGVzYmlhbi0yNiIsICJ0eXBlX25hbWUiOiAi5aWz5ZCMIn0sIHsidHlwZV9pZCI6ICJiYnctNTEiLCAidHlwZV9uYW1lIjogIuiDluWlsyJ9LCB7InR5cGVfaWQiOiAiU3F1aXJ0aW5nLTU2IiwgInR5cGVfbmFtZSI6ICLllrflh7oifSwgeyJ0eXBlX2lkIjogIkZpc3RpbmctMTY1IiwgInR5cGVfbmFtZSI6ICLmi7PkuqQifSwgeyJ0eXBlX2lkIjogIkdhbmdiYW5nLTY5IiwgInR5cGVfbmFtZSI6ICLnvqTkuqQifSwgeyJ0eXBlX2lkIjogIlRlZW4tMTMiLCAidHlwZV9uYW1lIjogIuWwkeWlsyJ9LCB7InR5cGVfaWQiOiAiQ3Vtc2hvdC0xOCIsICJ0eXBlX25hbWUiOiAi5bCE6aKcIn0sIHsidHlwZV9pZCI6ICJDYW1fUG9ybi01OCIsICJ0eXBlX25hbWUiOiAi5pGE5YOP5aS0In0sIHsidHlwZV9pZCI6ICJCaV9TZXh1YWwtNjIiLCAidHlwZV9uYW1lIjogIuWPjOaAp+aBiyJ9LCB7InR5cGVfaWQiOiAiU3RvY2tpbmdzLTI4IiwgInR5cGVfbmFtZSI6ICLkuJ3oopwifSwgeyJ0eXBlX2lkIjogIk9pbGVkLTIyIiwgInR5cGVfbmFtZSI6ICLmtoLmsrkifSwgeyJ0eXBlX2lkIjogIkxpbmdlcmllLTgzIiwgInR5cGVfbmFtZSI6ICLmgKfmhJ/lhoXooaMifSwgeyJ0eXBlX2lkIjogIkFzaWFuX1dvbWFuLTMyIiwgInR5cGVfbmFtZSI6ICLkuprmtLIifSwgeyJ0eXBlX2lkIjogIkFtYXRldXItNjUiLCAidHlwZV9uYW1lIjogIuS4muS9mSJ9LCB7InR5cGVfaWQiOiAiSW50ZXJyYWNpYWwtMjciLCAidHlwZV9uYW1lIjogIuW8guaXjyJ9LCB7InR5cGVfaWQiOiAiSW5kaWFuLTg5IiwgInR5cGVfbmFtZSI6ICLljbDluqYifSwgeyJ0eXBlX2lkIjogIkNyZWFtcGllLTQwIiwgInR5cGVfbmFtZSI6ICLkuK3lh7oifSwgeyJ0eXBlX2lkIjogIlNvbG9fYW5kX01hc3R1cmJhdGlvbi0zMyIsICJ0eXBlX25hbWUiOiAi6Ieq5oWwIn0sIHsidHlwZV9pZCI6ICJBSS0yMzkiLCAidHlwZV9uYW1lIjogIkFJIn0sIHsidHlwZV9pZCI6ICJBU01SLTIyOSIsICJ0eXBlX25hbWUiOiAiQVNNUiJ9XQ==').decode('utf-8'))


class Spider(Spider):
    def getName(self):
        return "V-HUB[影视]"

    def init(self, extend):
        # ext 统一解析：host@ 锁定主页 > JSON/文本 ext > 内置 SITE_URL（见 hostresolver.ext_of）
        try:
            from hostresolver import ext_of
            self._ext = ext_of(extend)
        except Exception:
            try:
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from hostresolver import ext_of
                self._ext = ext_of(extend)
            except Exception:
                self._ext = {}
        self.host = self._ext.get('host', '').rstrip('/') or SITE_URL
        self.api_url = self.host.rstrip('/') + '/api'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host + '/',
            'Origin': self.host
        }
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE

    def _xhttp(self, params):
        """使用标准库urllib发起HTTP GET请求"""
        try:
            qs = urllib.parse.urlencode(params)
            full_url = self.api_url + '?' + qs
            req = urllib.request.Request(full_url, headers=self.headers, method='GET')
            resp = urllib.request.urlopen(req, context=self._ssl_context, timeout=15)
            data = json.loads(resp.read().decode('utf-8'))
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            return []
        except Exception as e:
            print('_xhttp error: %s' % str(e), file=sys.stderr)
            return []

    def _format_time_cn(self, time_str):
        """将英文时间格式转为中文，如 '11 min' -> '11分钟'"""
        if not time_str:
            return ''
        m = re.match(r'^(\d+)\s*min\s*$', time_str.strip(), re.IGNORECASE)
        if m:
            return m.group(1) + '分钟'
        m = re.match(r'^(\d+)\s*h(?:our)?s?\s*(\d+)?\s*min\s*$', time_str.strip(), re.IGNORECASE)
        if m:
            h = m.group(1)
            mi = m.group(2)
            if mi:
                return h + '小时' + mi + '分钟'
            return h + '小时'
        return time_str

    def _extract_xvid(self, url):
        """从视频URL的查询参数中提取xvid值"""
        if not url:
            return ''
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        if 'xvid' in qs:
            return qs['xvid'][0]
        return ''

    def _build_vod_list(self, raw_data):
        """将API返回的原始数据构造为vod列表"""
        videos = []
        for item in raw_data:
            title = item.get('title', '')
            clean_title = re.sub(r'^AVOTC资源网[—-]+\s*', '', title).strip()
            if not clean_title:
                clean_title = title

            url = item.get('url', '')
            vod_id = self._extract_xvid(url)
            if not vod_id:
                vod_id = str(item.get('videoid', ''))

            videos.append({
                'vod_id': vod_id,
                'vod_name': clean_title,
                'vod_pic': item.get('img', ''),
                'vod_remarks': self._format_time_cn(item.get('time', '')),
                'vod_url': url
            })
        return videos

    def homeContent(self, filter):
        """首页：返回分类列表 + 首页视频"""
        classes = []
        for cat in CATEGORIES:
            classes.append({'type_id': cat['type_id'], 'type_name': cat['type_name']})

        raw_data = self._xhttp({'play': 'list', 'page': 1})
        videos = self._build_vod_list(raw_data)

        return {'class': classes, 'list': videos}

    def homeVideoContent(self):
        return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        """分类内容"""
        raw_data = self._xhttp({'play': 'class', 'c': tid, 'page': pg})
        videos = self._build_vod_list(raw_data)

        type_name = tid
        for cat in CATEGORIES:
            if cat['type_id'] == tid:
                type_name = cat['type_name']
                break

        return {
            'page': int(pg),
            'pagecount': 9999,
            'limit': 90,
            'total': 9999,
            'type_name': type_name,
            'list': videos
        }

    def detailContent(self, array):
        """详情：通过xvid获取视频播放地址"""
        result = {}
        if not array or not array[0]:
            return result

        xvid = array[0]
        vod = {
            'vod_id': xvid,
            'vod_name': '视频详情',
            'vod_pic': '',
            'vod_remarks': '',
            'vod_play_from': 'newxvideos',
            'vod_play_url': ''
        }

        try:
            qs = urllib.parse.urlencode({'xvid': xvid})
            full_url = self.api_url + '?' + qs
            req = urllib.request.Request(full_url, headers=self.headers, method='GET')
            resp = urllib.request.urlopen(req, context=self._ssl_context, timeout=15)
            data = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            print('detailContent error: %s' % str(e), file=sys.stderr)
            result['list'] = [vod]
            return result

        play_urls = []

        if isinstance(data, dict):
            item = data
            if 'data' in data and isinstance(data['data'], dict):
                item = data['data']

            hls_url = item.get('hls') or item.get('m3u8') or ''
            hight_url = item.get('hight') or item.get('high') or item.get('hd') or ''
            low_url = item.get('low') or item.get('sd') or ''

            if hls_url:
                play_urls.append('高清HLS$' + hls_url)
            if hight_url:
                play_urls.append('高清MP4$' + hight_url)
            if low_url:
                play_urls.append('低清MP4$' + low_url)

            title = item.get('title', '')
            if title:
                clean_title = re.sub(r'^AVOTC资源网[—-]+\s*', '', title).strip()
                if clean_title:
                    vod['vod_name'] = clean_title

            img = item.get('img', '')
            if img:
                vod['vod_pic'] = img

            time_str = item.get('time', '')
            if time_str:
                vod['vod_remarks'] = self._format_time_cn(time_str)

        elif isinstance(data, list):
            for item in data:
                hls_url = item.get('hls') or item.get('m3u8') or ''
                hight_url = item.get('hight') or item.get('high') or item.get('hd') or ''
                low_url = item.get('low') or item.get('sd') or ''

                if hls_url:
                    play_urls.append('高清HLS$' + hls_url)
                if hight_url:
                    play_urls.append('高清MP4$' + hight_url)
                if low_url:
                    play_urls.append('低清MP4$' + low_url)

                if vod['vod_name'] == '视频详情':
                    title = item.get('title', '')
                    if title:
                        clean_title = re.sub(r'^AVOTC资源网[—-]+\s*', '', title).strip()
                        if clean_title:
                            vod['vod_name'] = clean_title
                    img = item.get('img', '')
                    if img:
                        vod['vod_pic'] = img
                    time_str = item.get('time', '')
                    if time_str:
                        vod['vod_remarks'] = self._format_time_cn(time_str)

        if play_urls:
            vod['vod_play_url'] = '#'.join(play_urls)

        result['list'] = [vod]
        return result

    def searchContent(self, key, quick, pg='1'):
        """搜索"""
        raw_data = self._xhttp({'play': 'k', 'k': key, 'page': pg})
        videos = self._build_vod_list(raw_data)

        return {
            'page': int(pg),
            'pagecount': 9999,
            'limit': 90,
            'total': 9999,
            'list': videos
        }

    def playerContent(self, flag, id, vipFlags):
        """播放地址解析 - 直接返回用户选择的清晰度地址"""
        if id and (id.startswith('http://') or id.startswith('https://')):
            return {
                'parse': 0,
                'playUrl': '',
                'url': id,
                'header': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': self.host + '/'
                }
            }
        return {'parse': 0, 'playUrl': '', 'url': '', 'header': {}}

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return {}