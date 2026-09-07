# -*- coding: utf-8 -*-

import sys
import urllib.parse
import re
from lxml import etree
import json
from base64 import b64decode

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "禁片天堂"

    def init(self, extend):
        pass

    def homeContent(self, filter):
        cateManual = cateManual = json.loads(b64decode('eyLkuK3mlociOiAiMjc4IiwgIuW3qOS5syI6ICIxNSIsICLnhp/lpbMiOiAiOTUiLCAi6aiO5LmY5L2NIjogIjc0IiwgIuWPo+S6pCI6ICIzNCIsICLnmaHlpbMiOiAiNzUiLCAi5r2u5ZC5IjogIjMyIiwgIuS8geWKg+eJhyI6ICI4NCIsICLnvo7lsLsiOiAiMTU2IiwgIuaJk+aJi+anjSI6ICI5OCIsICLmiLLliofjgIHpgKPnuozliociOiAiNTgiLCAi5Yi25pyNIjogIjE5IiwgIue+juiFvyI6ICIxNTciLCAi6IiU6a6RIjogIjEyMiIsICLnvo7kubMiOiAiMTY2IiwgIuaQreiolSI6ICIxMiIsICLlpoTmg7Pml48iOiAiMTg0IiwgIuesrOS4gOS6uueoseimlum7niI6ICIxNjciLCAi5aq95aq957O7IjogIjE5MyIsICLkurrlprvjg7vkuLvlqaYiOiAiMjYiLCAi5aSa56iu6IG35qWtIjogIjg0IiwgIue+nui+sSI6ICIxNjMiLCAi5aWz5pWZ5birIjogIjEzMSIsICLmt6voqp4iOiAiMTUxIiwgIuiCieaEnyI6ICIxMzYiLCAi5oSb576O6IeAIjogIjExMSIsICLog4zlvozkvY0iOiAiMTc4IiwgIuiqv+aVmSI6ICIzOTUiLCAi6JmV55S3IjogIjIzIiwgIuitt+WjqyI6ICIyODMiLCAi5L+u6ZW3IjogIjE0NyIsICLpnLLlhafopLIiOiAiMTY5IiwgIue1suilqiI6ICIxMTUiLCAi5oSb5beo5LmzIjogIjIwMCIsICLnnLzpj6EiOiAiMjkwIiwgIui2heS5syI6ICIyMTEiLCAi6aGP6Z2i6aiO5LmYIjogIjI2MyIsICLmg6HkvZzliociOiAiMTQ1IiwgIue+qeavjSI6ICIxNDQiLCAi5rer5LqC44O76YGO5r+A57O7IjogIjYzIiwgIuaEm+e+juiFvyI6ICIxMSIsICLniIbkubMiOiAiNDgzIiwgIuWls+S4iuWPuCI6ICIxMzciLCAi5q2j5aSqIjogIjQxNSIsICLnqb/ooaPlubnnoLIiOiAiMTc5IiwgIue3iui6q+earuihoyI6ICIzMDQiLCAi5a245ZySIjogIjQyMSIsICLnqbrlp5AiOiAiMTMyIiwgIueyiee1suaEn+isneelrSI6ICIxOTAiLCAi6IOM6Z2i6aiO5LmX5L2NIjogIjY0NiIsICLnp5jmm7giOiAiMzYzIiwgIuWls+S4u+aSrSI6ICIxMDYiLCAi5Y+N5ZCR5pCt6KiVIjogIjMwNSIsICLlgaXouqvmlZnnt7QiOiAiMjMzIiwgIumDqOS4i+ODu+WQjOWDmiI6ICIxNTAiLCAi6Iie6LmIIjogIjEzMCIsICLnt4rouqvooaPmv4Dlh7giOiAiMzIxIiwgIjNE5b2x54mHIjogIjUwOCIsICLml6nmtKkiOiAiNDAzIn0=').decode('utf-8'))
        result = {'class': [{'type_name': k, 'type_id': v} for k, v in cateManual.items()]}
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        url = f'https://jptt.tv/tag_list?tid={tid}&idx={pg}'
        try:
            rsp = self.fetch(url)
            root = etree.HTML(rsp.text)
            videos = root.xpath('//div[contains(@class,"oneVideo")]')
            vodList = []
            for video in videos:
                try:
                    name_elements = video.xpath('.//h3/text()')
                    if not name_elements:
                        continue
                    name = name_elements[0].strip()

                    img_elements = video.xpath('.//img/@src')
                    if not img_elements:
                        continue
                    img = img_elements[0]
                    if not img.startswith('http'):
                        img = 'https://jptt.tv' + img

                    desc_elements = video.xpath('.//p[contains(@class,"p_duration")]/text()')
                    desc = desc_elements[0].strip() if desc_elements else ''

                    link_elements = video.xpath('.//a/@href')
                    if not link_elements:
                        continue
                    link = link_elements[0]

                    vodList.append({
                        "vod_name": name,
                        "vod_pic": img,
                        "vod_remarks": desc,
                        "vod_id": link
                    })
                except Exception as e:
                    print(f"[categoryContent video parse error]: {e}")
                    continue

            result['list'] = vodList
            result['page'] = pg
            result['pagecount'] = 9999
            result['limit'] = 90
            result['total'] = 999999
        except Exception as e:
            print(f"[categoryContent fetch error]: {e}")
            result['list'] = []
            result['page'] = pg
            result['pagecount'] = 0
            result['limit'] = 0
            result['total'] = 0
        return result

    def detailContent(self, array):
        tid = array[0]
        url = tid if tid.startswith('http') else f'https://jptt.tv{tid}'
        try:
            rsp = self.fetch(url)
            root = etree.HTML(rsp.text)

            title_elements = root.xpath('//h1[@class="h1_title"]/text()')
            title = title_elements[0].strip() if title_elements else "未知标题"

            pic_elements = root.xpath('//video/@poster')
            pic = pic_elements[0] if pic_elements else ""
            if pic and not pic.startswith('http'):
                pic = 'https://jptt.tv' + pic

            desc_elements = root.xpath('//div[contains(@class,"info_original")]//p/text()')
            desc = desc_elements[0].strip() if desc_elements else title

            play_url = self.extractVideoUrl(rsp.text)

            vod = {
                "vod_id": tid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_content": desc,
                "vod_play_from": "注意身体",
                "vod_play_url": "多看少打卡$" + play_url
            }
            return {'list': [vod]}
        except Exception as e:
            print(f"[detailContent error]: {e}")
            return {'list': []}

    def extractVideoUrl(self, html):
        try:
            source_match = re.search(r'<source\s+src="([^"]+)"', html)
            if source_match:
                video_url = source_match.group(1)
                if video_url.startswith('//'):
                    video_url = 'https:' + video_url
                return video_url

            hls_patterns = [
                r'//cdn-[^"\']+\.m3u8[^"\']*',
                r'https?://[^"\']+\.m3u8[^"\']*',
                r'/hlsredirect/[^"\']+\.m3u8'
            ]
            for pattern in hls_patterns:
                matches = re.findall(pattern, html)
                if matches:
                    for match in matches:
                        if match.startswith('//'):
                            return 'https:' + match
                        elif match.startswith('http'):
                            return match
                        else:
                            return 'https://jptt.tv' + match

            js_patterns = [
                r'src\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'url\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']'
            ]
            for pattern in js_patterns:
                match = re.search(pattern, html)
                if match:
                    video_url = match.group(1)
                    if video_url.startswith('//'):
                        return 'https:' + video_url
                    elif video_url.startswith('http'):
                        return video_url
                    else:
                        return 'https://jptt.tv' + video_url

            all_m3u8 = re.findall(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', html)
            if all_m3u8:
                return all_m3u8[0]
        except Exception as e:
            print(f"[extractVideoUrl error]: {e}")

        return "https://cdn-mso2.jptt1.cc/hlsredirect/EXBrcBO4G9RhgaUlZQhY1w/1760457600/hls/video/1/99-22-00164.3gp/index.m3u8"

    def searchContent(self, key, quick, pg="1"):
        result = {}
        url = f'https://jptt.tv/search?kw={urllib.parse.quote(key)}'
        try:
            rsp = self.fetch(url)
            root = etree.HTML(rsp.text)
            videos = root.xpath('//div[contains(@class,"oneVideo")]')
            vodList = []
            for video in videos:
                try:
                    name_elements = video.xpath('.//h3/text()')
                    if not name_elements:
                        continue
                    name = name_elements[0].strip()

                    img_elements = video.xpath('.//img/@src')
                    if not img_elements:
                        continue
                    img = img_elements[0]
                    if not img.startswith('http'):
                        img = 'https://jptt.tv' + img

                    desc_elements = video.xpath('.//p[contains(@class,"p_duration")]/text()')
                    desc = desc_elements[0].strip() if desc_elements else ''

                    link_elements = video.xpath('.//a/@href')
                    if not link_elements:
                        continue
                    link = link_elements[0]

                    vodList.append({
                        "vod_name": name,
                        "vod_pic": img,
                        "vod_remarks": desc,
                        "vod_id": link
                    })
                except Exception as e:
                    print(f"[searchContent video parse error]: {e}")
                    continue

            result['list'] = vodList
        except Exception as e:
            print(f"[searchContent fetch error]: {e}")
            result['list'] = []
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        if flag == "注意身体":
            try:
                if id.startswith('http') and '.m3u8' in id:
                    result["parse"] = 0
                    result["playUrl"] = ''
                    result["url"] = id
                else:
                    url = id if id.startswith('http') else f'https://jptt.tv{id}'
                    rsp = self.fetch(url)
                    play_url = self.extractVideoUrl(rsp.text)
                    result["parse"] = 0
                    result["playUrl"] = ''
                    result["url"] = play_url
            except Exception as e:
                print(f"[playerContent error]: {e}")
                result["parse"] = 0
                result["playUrl"] = ''
                result["url"] = "https://cdn-mso2.jptt1.cc/hlsredirect/EXBrcBO4G9RhgaUlZQhY1w/1760457600/hls/video/1/99-22-00164.3gp/index.m3u8"

            result["header"] = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
                "Referer": "https://jptt.tv/",
                "Origin": "https://jptt.tv"
            }
        return result

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        pass