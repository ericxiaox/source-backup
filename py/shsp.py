# coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
import time
import urllib.parse
import re
import requests
from lxml import etree

class Spider(Spider):
    def getName(self):
        return "\u56db\u864e\u89c6\u9891"

    def init(self, extend=""):
        self.baseUrl = "https://www.sihuhu.xyz"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Referer": self.baseUrl
        }

    def homeContent(self, filter):
        result = {}
        # \u4eceHTML\u4e2d\u63d0\u53d6\u5206\u7c7b\u4fe1\u606f
        cateManual = {
            "\u4f20\u5a92\u5382\u5546": "20",
            "\u9ebb\u8c46\u4f20\u5a92": "21",
            "91\u5236\u7247": "22",
            "\u871c\u6843\u4f20\u5a92": "23",
            "\u5929\u7f8e\u4f20\u5a92": "24",
            "\u7cbe\u4e1c\u5f71\u7247": "25",
            "\u661f\u7a7a\u4f20\u5a92": "26",
            "\u846b\u82a6\u5f71\u4e1a": "27",
            "\u7cd6\u5fc3VLOG": "28",
            "\u7cbe\u54c1\u63a8\u8350": "29",
            "\u65e5\u672c\u65e0\u7801": "30",
            "\u65e5\u672c\u6709\u7801": "31",
            "AV\u89e3\u8bf4": "32",
            "\u4e2d\u6587\u6709\u7801": "33",
            "\u4e2d\u6587\u65e0\u7801": "34",
            "\u65e5\u97e9\u6781\u54c1": "35",
            "\u65e5\u97e9\u65e0\u7801": "36",
            "\u5c11\u5973\u841d\u8389": "37",
            "\u6c34\u5ae9\u841d\u8389": "38",
            "\u6781\u54c1\u4e3b\u64ad": "40",
            "\u5361\u901a\u52a8\u6f2b": "43",
            "SM\u8c03\u6559": "44",
            "\u63a2\u82b1\u5408\u96c6": "50",
            "91\u5927\u795e": "51",
            "\u53f0\u6e7e\u841d\u8389": "54",
            "\u841d\u8389\u4f20\u5a92": "55",
            "\u767d\u864e\u53e3\u7206": "57",
            "\u5ae9\u5973\u7f51\u7206": "47",
            "\u5ae9\u903c\u4e4c\u9e21": "42",
            "\u4e09\u7ea7\u4f26\u7406": "45",
            "\u841d\u8389\u4e92\u53e3": "46",
            "\u9ed1\u6599\u7f51\u7206": "48",
            "\u91ce\u6218\u8f66\u9707": "52",
            "\u841d\u8389\u9ed1\u74dc": "53",
            "\u841d\u8389\u5de8\u4e73": "58",
            "\u660e\u661f\u6362\u8138": "73",
            "\u841d\u8389\u62a0\u903c": "56",
            "\u56fd\u4ea7\u5927\u4f5c": "39",
            "\u6b27\u7f8e\u841d\u8389": "41",
            "\u70ed\u95e8\u4e8b\u4ef6": "49",
            "\u5c11\u59733P": "59",
            "\u5077\u62cd\u841d\u8389": "60",
            "\u5f3a\u5978\u5c11\u5973": "61",
            "\u91cd\u53e3\u730e\u5947": "62",
            "\u5236\u670d\u841d\u63a7": "63",
            "\u6781\u54c1\u5c11\u5973": "64",
            "\u660e\u661f\u7206\u6599": "65",
            "X\u77ed\u89c6\u9891": "66",
            "AV\u660e\u661f": "67",
            "\u6781\u54c1\u841d\u8389": "68",
            "\u4eba\u59bb\u8279\u5988": "69",
            "VR\u89c6\u89d2": "70",
            "\u89d2\u8272\u626e\u6f14": "71",
            "\u7537\u540c\u7537\u5a18": "72"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })
        result['class'] = classes
        return result

    def homeVideoContent(self):
        result = {}
        # \u5c1d\u8bd5\u83b7\u53d6\u9996\u9875\u63a8\u8350\u89c6\u9891
        try:
            rsp = self.fetch(self.baseUrl, headers=self.headers)
            html = etree.HTML(rsp.text)
            
            videos = []
            # \u5c1d\u8bd5\u89e3\u6790\u9996\u9875\u89c6\u9891\u5217\u8868
            video_elements = html.xpath('//ul[@class="thumbnail-group clearfix"]/li')
            for element in video_elements:
                try:
                    name = element.xpath('.//h5/a/text()')[0].strip()
                    pic = element.xpath('.//img/@data-original')[0]
                    if not pic.startswith('http'):
                        pic = self.baseUrl + pic
                    href = element.xpath('.//a[@class="thumbnail"]/@href')[0]
                    vid = href.split('/')[-1].replace('.html', '')
                    remark = element.xpath('.//span[@class="title"]/text()')
                    remark = remark[0] if remark else ""
                    
                    videos.append({
                        "vod_id": vid,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                    })
                except:
                    continue
            
            result['list'] = videos
        except:
            result['list'] = []
        
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        url = f'{self.baseUrl}/vod/type/id/{tid}/page/{pg}.html'
        rsp = self.fetch(url, headers=self.headers)
        html = etree.HTML(rsp.text)
        
        vodList = []
        video_elements = html.xpath('//ul[@class="thumbnail-group clearfix"]/li')
        for element in video_elements:
            try:
                name = element.xpath('.//h5/a/text()')[0].strip()
                pic = element.xpath('.//img/@data-original')[0]
                if not pic.startswith('http'):
                    pic = self.baseUrl + pic
                href = element.xpath('.//a[@class="thumbnail"]/@href')[0]
                vid = href.split('/')[-1].replace('.html', '')
                remark = element.xpath('.//span[@class="title"]/text()')
                remark = remark[0] if remark else ""
                
                vodList.append({
                    "vod_id": vid,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_remarks": remark
                })
            except:
                continue
                
        result['list'] = vodList
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 20
        result['total'] = 999999
        return result

    def detailContent(self, array):
        tid = array[0]
        url = f'{self.baseUrl}/vod/detail/id/{tid}.html'
        rsp = self.fetch(url, headers=self.headers)
        html = etree.HTML(rsp.text)
        
        # \u83b7\u53d6\u89c6\u9891\u8be6\u60c5
        title = html.xpath('//title/text()')[0].replace(' - \u56db\u864e\u89c6\u9891', '')
        pic = html.xpath('//meta[@property="og:image"]/@content')
        pic = pic[0] if pic else ""
        desc = html.xpath('//meta[@name="description"]/@content')
        desc = desc[0] if desc else ""
        
        # \u83b7\u53d6\u64ad\u653e\u5217\u8868 - \u4fee\u590d\u64ad\u653e\u5730\u5740\u83b7\u53d6
        play_from = []
        play_url = []
        
        # \u5c1d\u8bd5\u83b7\u53d6\u6240\u6709\u64ad\u653e\u6e90
        play_sources = html.xpath('//div[@class="module-play-list"]/div')
        for source in play_sources:
            source_name = source.xpath('.//span/text()')
            if source_name:
                source_name = source_name[0].strip()
                play_from.append(source_name)
                
                # \u83b7\u53d6\u8be5\u6e90\u4e0b\u7684\u6240\u6709\u5267\u96c6
                episodes = source.xpath('.//a')
                episode_urls = []
                for episode in episodes:
                    ep_name = episode.xpath('./text()')[0].strip()
                    ep_href = episode.xpath('./@href')[0]
                    episode_urls.append(f"{ep_name}${self.baseUrl}{ep_href}")
                
                play_url.append("#".join(episode_urls))
        
        # \u5982\u679c\u6ca1\u6709\u627e\u5230\u64ad\u653e\u6e90\uff0c\u4f7f\u7528\u9ed8\u8ba4\u65b9\u5f0f
        if not play_from:
            play_from = ["\u9ed8\u8ba4"]
            play_page_url = f"{self.baseUrl}/vod/play/id/{tid}/sid/1/nid/1.html"
            play_url.append(f"第1集${play_page_url}")
        
        vod = {
            "vod_id": tid,
            "vod_name": title,
            "vod_pic": pic,
            "vod_content": desc,
            "vod_play_from": "$$$".join(play_from),
            "vod_play_url": "$$$".join(play_url)
        }
        
        return {'list': [vod]}

    def searchContent(self, key, quick):
        result = {}
        url = f'{self.baseUrl}/vod/search/page/1/wd/{urllib.parse.quote(key)}.html'
        rsp = self.fetch(url, headers=self.headers)
        html = etree.HTML(rsp.text)
        
        vodList = []
        video_elements = html.xpath('//ul[@class="thumbnail-group clearfix"]/li')
        for element in video_elements:
            try:
                name = element.xpath('.//h5/a/text()')[0].strip()
                pic = element.xpath('.//img/@data-original')[0]
                if not pic.startswith('http'):
                    pic = self.baseUrl + pic
                href = element.xpath('.//a[@class="thumbnail"]/@href')[0]
                vid = href.split('/')[-1].replace('.html', '')
                remark = element.xpath('.//span[@class="title"]/text()')
                remark = remark[0] if remark else ""
                
                vodList.append({
                    "vod_id": vid,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_remarks": remark
                })
            except:
                continue
                
        result['list'] = vodList
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        # \u89e3\u6790\u64ad\u653e\u5730\u5740
        url = f'{self.baseUrl}{id}' if id.startswith('/') else id
        
        # \u68c0\u67e5\u662f\u5426\u5df2\u7ecf\u662fm3u8\u94fe\u63a5
        if id.endswith('.m3u8'):
            result["parse"] = 0
            result["playUrl"] = ""
            result["url"] = id
            result["header"] = json.dumps(self.headers)
            return result
            
        rsp = self.fetch(url, headers=self.headers)
        
        # \u65b9\u6cd51: \u5c1d\u8bd5\u4eceJavaScript\u53d8\u91cf\u4e2d\u63d0\u53d6\u64ad\u653e\u4fe1\u606f
        pattern = r'var player_aaaa\s*=\s*({.*?});'
        match = re.search(pattern, rsp.text, re.DOTALL)
        
        if match:
            try:
                player_info = json.loads(match.group(1))
                video_url = player_info.get('url', '')
                
                if video_url:
                    # \u5904\u7406\u8f6c\u4e49\u5b57\u7b26
                    video_url = video_url.replace('\\/', '/')
                    result["parse"] = 0
                    result["playUrl"] = ""
                    result["url"] = video_url
                    result["header"] = json.dumps(self.headers)
                    return result
            except:
                pass
        
        # \u65b9\u6cd52: \u5c1d\u8bd5\u4eceJavaScript\u4e2d\u627e\u5230url\u5b57\u6bb5
        url_patterns = [
            r'"url"\s*:\s*"([^"]+)"',
            r"url\s*:\s*'([^']+)'",
            r'video_url\s*:\s*"([^"]+)"',
            r"video_url\s*:\s*'([^']+)'"
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, rsp.text)
            if match:
                video_url = match.group(1).replace('\\/', '/')
                if video_url and ('m3u8' in video_url or 'mp4' in video_url):
                    result["parse"] = 0
                    result["playUrl"] = ""
                    result["url"] = video_url
                    result["header"] = json.dumps(self.headers)
                    return result
        
        # \u65b9\u6cd53: \u5c1d\u8bd5\u4eceiframe\u4e2d\u63d0\u53d6\u89c6\u9891\u5730\u5740
        iframe_pattern = r'<iframe[^>]+src="([^"]+)"'
        iframe_match = re.search(iframe_pattern, rsp.text)
        if iframe_match:
            iframe_src = iframe_match.group(1)
            if iframe_src.startswith('//'):
                iframe_src = 'https:' + iframe_src
            elif iframe_src.startswith('/'):
                iframe_src = self.baseUrl + iframe_src
                
            # \u9012\u5f52\u83b7\u53d6iframe\u5185\u5bb9
            return self.playerContent(flag, iframe_src, vipFlags)
        
        # \u5982\u679c\u4ee5\u4e0a\u65b9\u6cd5\u90fd\u5931\u8d25\uff0c\u8fd4\u56de\u539f\u59cb\u9875\u9762\u4f9b\u8fdb\u4e00\u6b65\u89e3\u6790
        result["parse"] = 1
        result["playUrl"] = ""
        result["url"] = url
        result["header"] = json.dumps(self.headers)
        
        return result

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        return []
