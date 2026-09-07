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
