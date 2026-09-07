"""
@header({
  searchable: 1,
  filterable: 1,
  quickSearch: 1,
  title: '茶杯狐-TJTCDL',
  lang: 'hipy',
})
"""

# -*- coding: utf-8 -*-
# !/usr/bin/python
import requests
import base64
import random
import re
import json
import sys
import urllib.parse
import ssl
import urllib3
import hashlib
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

urllib3.disable_warnings()
sys.path.append('..')
from base.spider import Spider


class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ciphers = (
            'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:'
            'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:'
            'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:'
            'DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384'
        )
        context = create_urllib3_context(ciphers=ciphers)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)


class Spider(Spider):
    def __init__(self):
        super(Spider, self).__init__()
        self.session = requests.Session()
        self.session.verify = False
        self.session.mount('https://', TLSAdapter())
        self.host = "https://www.tjtcdl.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Referer': f'{self.host}/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

    def getName(self):
        return "茶杯狐-TJTCDL"

    def init(self, extend):
        pass

    def homeContent(self, filter):
        # 数字分类路由(/type1~5.html、cupfox-list)被站方验证码墙拦截，仅 label 精选通道免验证可用
        classes = [
            {"type_id": "/label/qq", "type_name": "腾讯VIP精选"},
            {"type_id": "/label/yk", "type_name": "优酷VIP精选"},
            {"type_id": "/label/bli", "type_name": "B站VIP精选"},
        ]
        return {"class": classes}

    def homeVideoContent(self):
        return {'list': []}

    def categoryContent(self, cid, pg, filter, ext):
        page = int(pg)
        # label 精选通道（免验证）：/label/{name}/page/{pg}.html
        if cid.startswith('/label'):
            url = f"{self.host}{cid}/page/{pg}.html"
            res = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            videos = []
            for item in soup.select('.public-list-box'):
                link = item.select_one('.public-list-exp')
                if not link: continue
                vid_match = re.search(r'/chabeihu/(\d+)\.html', link.get('href', ''))
                if not vid_match: continue
                pic_img = link.select_one('img')
                note_tag = item.select_one('.public-list-prb')
                videos.append({
                    "vod_id": vid_match.group(1),
                    "vod_name": link.get('title', '').strip(),
                    "vod_pic": pic_img.get('data-src') or pic_img.get('src') or '' if pic_img else '',
                    "vod_remarks": note_tag.text.strip() if note_tag else ''
                })
            pagecount = page if len(videos) < 24 else page + 2
            return {'list': videos, 'page': page, 'pagecount': pagecount, 'limit': 24, 'total': 999999}
        ext = ext or {}
        area = urllib.parse.quote(ext.get('area', '')) if ext.get('area') else ''
        by = ext.get('by', '')
        class_name = urllib.parse.quote(ext.get('class', '')) if ext.get('class') else ''
        lang = urllib.parse.quote(ext.get('lang', '')) if ext.get('lang') else ''
        letter = ext.get('letter', '')
        year = ext.get('year', '')

        url = f"{self.host}/cupfox-list/{cid}-{area}-{by}-{class_name}-{lang}-{letter}---{page}---{year}.html"
        res = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        videos = []
        for item in soup.select('.public-list-box'):
            link = item.select_one('.public-list-exp')
            if not link: continue
            vid_match = re.search(r'/chabeihu/(\d+)\.html', link.get('href', ''))
            if not vid_match: continue

            pic_img = link.select_one('img')
            note_tag = item.select_one('.public-list-prb')

            videos.append({
                "vod_id": vid_match.group(1),
                "vod_name": link.get('title', '').strip(),
                "vod_pic": pic_img.get('data-src') or pic_img.get('src') or '' if pic_img else '',
                "vod_remarks": note_tag.text.strip() if note_tag else ''
            })

        return {'list': videos, 'page': page, 'pagecount': 9999, 'limit': 90, 'total': 999999}

    def detailContent(self, ids):
        did = ids[0]
        url = f"{self.host}/chabeihu/{did}.html"
        res = self.session.get(url, headers=self.headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        name, state, actor, director, year, content = "", "", "", "", "", ""
        for li in soup.select('.info-parameter li'):
            em = li.select_one('em')
            if not em: continue
            em_text = em.text.strip()
            val = li.text.replace(em_text, '').replace('\xa0', ' ').strip()

            if '片名' in em_text:
                name = val
            elif '状态' in em_text:
                state = val
            elif '主演' in em_text:
                actor = val
            elif '导演' in em_text:
                director = val
            elif '年份' in em_text:
                year = val
            elif '简介' in em_text:
                content = val

        if not name:
            title_tag = soup.select_one('.this-desc-title')
            name = title_tag.text.strip() if title_tag else ''

        play_from, play_url = [], []
        sources = [s.text.replace(s.select_one('.badge').text, '').strip() if s.select_one('.badge') else s.text.strip()
                   for s in soup.select('.anthology-tab .swiper-slide')]

        for idx, box in enumerate(soup.select('.anthology-list-box')):
            eps = [
                f"{a.text.strip()}${self.host + a.get('href') if not a.get('href').startswith('http') else a.get('href')}"
                for a in box.select('li a') if a.get('href')]
            if eps:
                eps.reverse()
                play_from.append(sources[idx] if idx < len(sources) else f"线路{idx + 1}")
                play_url.append('#'.join(eps))

        return {'list': [{
            "vod_id": did,
            "vod_name": name,
            "vod_actor": actor,
            "vod_director": director,
            "vod_content": content,
            "vod_remarks": state,
            "vod_year": year,
            "vod_play_from": '$$$'.join(play_from),
            "vod_play_url": '$$$'.join(play_url)
        }]}

  
    def playerContent(self, flag, id, vipFlags):
        try:

            res = self.session.get(id, headers=self.headers, timeout=5)
            match = re.search(r'var player_aaaa=(.*?)</script>', res.text)
            if not match:
                return {'parse': 0, 'url': ''}

            player_data = json.loads(match.group(1))
            durl = player_data.get('url', '')
            encrypt = player_data.get('encrypt', 0)
            from_flag = player_data.get('from', '')

            if encrypt == 1:
                durl = urllib.parse.unquote(durl)
            elif encrypt == 2:
                durl = urllib.parse.unquote(durl)
                durl = base64.b64decode(durl).decode('utf-8')
                durl = urllib.parse.unquote(durl)


            if durl.startswith('http') and ('.m3u8' in durl or '.mp4' in durl):

                return {'parse': 0, 'url': durl}




            config_url = f"{self.host}/static/js/playerconfig.js"
            config_res = self.session.get(config_url, headers=self.headers, verify=False, timeout=5)

            parse_api = ""
            if from_flag:
                m = re.search(f'"{from_flag}":\\{{[^}}]*"parse":"([^"]+)"', config_res.text)
                if m: parse_api = m.group(1).replace('\\/', '/')
            if not parse_api:
                m = re.search(r'"parse":"(http[^"]+)"', config_res.text)
                if m: parse_api = m.group(1).replace('\\/', '/')
            if not parse_api:
                parse_api = "https://fgsrg.hzqingshan.com/player/?url="

            iframe_url = parse_api + durl
            print(f"[*] 2. 锁定隐藏解析服务器(iframe): {iframe_url}")


            iframe_headers = self.headers.copy()
            iframe_headers['Referer'] = id
            iframe_res = self.session.get(iframe_url, headers=iframe_headers, verify=False, timeout=5)

            iframe_soup = BeautifulSoup(iframe_res.text, 'html.parser')
            player_data_tag = iframe_soup.select_one('#player-data')

            if not player_data_tag:

                return {'parse': 1, 'url': iframe_url}

            token = player_data_tag.get('data-te', '')
            bt = player_data_tag.get('data-bt', '/player/')



            api_base = urllib.parse.urlparse(parse_api)
            api_host = f"{api_base.scheme}://{api_base.netloc}"
            api_url = f"{api_host}{bt}mplayer.php"


            post_data = {'url': durl, 'token': token}

            api_headers = self.headers.copy()
            api_headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            api_headers['X-Requested-With'] = 'XMLHttpRequest'
            api_headers['Referer'] = iframe_url
            api_headers['Origin'] = api_host


            api_res = self.session.post(api_url, data=post_data, headers=api_headers, verify=False, timeout=10)

            if api_res.status_code == 200:
                api_json = api_res.json()
                print(f"[*] 5. 接口解密成功: {api_json}")

                real_url = api_json.get('url') or api_json.get('data', {}).get('url', '')
                urlmode = str(api_json.get('urlmode') or api_json.get('data', {}).get('urlmode', ''))

                if urlmode == '1':
                    real_url = self.js_decrypt1(real_url)
                elif urlmode == '2':
                    real_url = self.js_decrypt2(real_url)
                elif urlmode == '3':
                    real_url = self.js_decrypt3(real_url)

                for _ in range(3):
                    if real_url.startswith('WyJ') and '/' in real_url:
                        real_url = self.js_decrypt3(real_url)
                    else:
                        break

                if real_url:
                    print(f"[*] 6. 🎉斩获最终真实 M3U8: {real_url}")
                    return {'parse': 0 if ('.m3u8' in real_url or '.mp4' in real_url) else 1, 'url': real_url}


            return {'parse': 1, 'url': iframe_url}

        except Exception as e:

            return {'parse': 1, 'url': id}

    def searchContent(self, key, quick, pg="1"):
        search_url = f'{self.host}/cupfox-search/-------------.html'
        res = self.session.get(search_url, params={'wd': key}, headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        videos = []
        for item in soup.select('.public-list-box'):
            link = item.select_one('.public-list-exp')
            if not link: continue
            vid_match = re.search(r'/chabeihu/(\d+)\.html', link.get('href', ''))
            if not vid_match: continue

            pic_img = link.select_one('img')
            note_tag = item.select_one('.public-list-prb')

            videos.append({
                "vod_id": vid_match.group(1),
                "vod_name": link.get('title', '').strip(),
                "vod_pic": pic_img.get('data-src') or pic_img.get('src') or '' if pic_img else '',
                "vod_remarks": note_tag.text.strip() if note_tag else ''
            })

        return {'list': videos, 'page': int(pg), 'pagecount': 1, 'limit': len(videos), 'total': len(videos)}


    def js_decrypt1(self, data):
        try:
            key = hashlib.md5(b'test').hexdigest()
            dec1 = base64.b64decode(data)
            code = bytearray([dec1[i] ^ ord(key[i % len(key)]) for i in range(len(dec1))])
            return base64.b64decode(code).decode('utf-8')
        except:
            return data

    def js_decrypt2(self, data):
        staticchars = "PXhw7UT1B0a9kQDKZsjIASmOezxYG4CHo5Jyfg2b8FLpEvRr3WtVnlqMidu6cN"
        try:
            dec = base64.b64decode(data).decode('utf-8', errors='ignore')
            return "".join(
                [staticchars[(staticchars.find(dec[i]) + 59) % 62] if staticchars.find(dec[i]) != -1 else dec[i] for i
                 in range(1, len(dec), 3)])
        except:
            return data

    def js_decrypt3(self, data):
        def fix_b64(s):
            return s + '=' * (4 - len(s) % 4) if len(s) % 4 else s

        try:
            parts = data.split('/')
            if len(parts) >= 3:
                arr1 = json.loads(base64.b64decode(fix_b64(parts[0])).decode('utf-8'))
                arr2 = json.loads(base64.b64decode(fix_b64(parts[1])).decode('utf-8'))
                cipher = base64.b64decode(fix_b64('/'.join(parts[2:]))).decode('utf-8', errors='ignore')
                return "".join([arr1[arr2.index(c)] if c in arr2 else c for c in cipher])
        except:
            pass
        return data

