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