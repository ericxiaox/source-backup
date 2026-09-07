# -*- coding: utf-8 -*-

import sys
import urllib.parse
import re
from lxml import etree

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "禁片天堂"

    def init(self, extend):
        pass

    def homeContent(self, filter):
        cateManual = {
            "中文": "278",
            "巨乳": "15",
            "熟女": "95",
            "騎乘位": "74",
            "口交": "34",
            "癡女": "75",
            "潮吹": "32",
            "企劃片": "84",
            "美尻": "156",
            "打手槍": "98",
            "戲劇、連續劇": "58",
            "制服": "19",
            "美腿": "157",
            "舔鮑": "122",
            "美乳": "166",
            "搭訕": "12",
            "妄想族": "184",
            "第一人稱視點": "167",
            "媽媽系": "193",
            "人妻・主婦": "26",
            "多種職業": "84",
            "羞辱": "163",
            "女教師": "131",
            "淫語": "151",
            "肉感": "136",
            "愛美臀": "111",
            "背後位": "178",
            "調教": "395",
            "處男": "23",
            "護士": "283",
            "修長": "147",
            "露內褲": "169",
            "絲襪": "115",
            "愛巨乳": "200",
            "眼鏡": "290",
            "超乳": "211",
            "顏面騎乘": "263",
            "惡作劇": "145",
            "義母": "144",
            "淫亂・過激系": "63",
            "愛美腿": "11",
            "爆乳": "483",
            "女上司": "137",
            "正太": "415",
            "穿衣幹砲": "179",
            "緊身皮衣": "304",
            "學園": "421",
            "空姐": "132",
            "粉絲感謝祭": "190",
            "背面騎乗位": "646",
            "秘書": "363",
            "女主播": "106",
            "反向搭訕": "305",
            "健身教練": "233",
            "部下・同僚": "150",
            "舞蹈": "130",
            "緊身衣激凸": "321",
            "3D影片": "508",
            "早洩": "403"
        }
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
