                
                if data.get('retcode') == 3:
                    video_url = data.get('data', {}).get('httpurl_preview', '')
                else:
                    video_url = data.get('data', {}).get('httpurl', '')
                
                if video_url:
                    # 移除可能的参数
                    video_url = video_url.replace('?300', '')
                    self.log(f"从API获取到视频地址: {video_url}")
                    return {'parse': 0, 'playUrl': '', 'url': video_url}
                else:
                    self.log("API响应中没有找到视频地址")
            else:
                self.log(f"API请求失败，状态码: {api_response.status_code if api_response else '无响应'}")
                
            # 如果API请求失败，回退到原来的方法
            if '_' in id:
                domain, play_id = id.split('_')
                play_url = f"https://{domain}/html/kkyd.html?m={play_id}"
            else:
                play_url = f"{self.host}/html/kkyd.html?m={id}"
                
            self.log(f"回退到播放页面: {play_url}")
            return {'parse': 1, 'playUrl': '', 'url': play_url}
            
        except Exception as e:
            self.log(f"播放链接获取出错: {str(e)}")
            # 出错时也返回播放页面URL
            if '_' in id:
                domain, play_id = id.split('_')
                play_url = f"https://{domain}/html/kkyd.html?m={play_id}"
            else:
                play_url = f"{self.host}/html/kkyd.html?m={id}"
            return {'parse': 1, 'playUrl': '', 'url': play_url}

    # ========== 辅助方法 ==========
    
    def _get_videos(self, doc, limit=None):
        """获取影片列表 - 根据实际网站结构"""
        try:
            videos = []
            elements = doc.xpath('//a[@class="vodbox"]')
            self.log(f"找到 {len(elements)} 个vodbox元素")
            for elem in elements:
                video = self._extract_video(elem)
                if video:
                    videos.append(video)
            return videos[:limit] if limit and videos else videos
        except Exception as e:
            self.log(f"获取影片列表出错: {str(e)}")
            return []

    def _extract_video(self, element):
        """提取影片信息 - 修复标题乱码问题，正确读取km-script标签文本"""
        try:
            # 1. 提取影片链接（获取vod_id的来源）
            link = element.xpath('./@href')[0]  # 获取a标签的href属性
            if link.startswith('/'):
                link = self.host + link  # 补全相对路径为完整URL
            
            # 2. 提取vod_id（从URL的m参数获取，而非hash，更准确）
            vod_id = self.regStr(r'm=(\d+)', link)  # 匹配 ?m=123 中的数字
            if not vod_id:
                vod_id = str(hash(link) % 1000000)  # 兜底：hash生成唯一ID
            
            # 3. 提取标题（关键修复：读取<p class="km-script">内的文本并解密）
            title_elem = element.xpath('./p[@class="km-script"]/text()')  # 定位km-script标签
            if not title_elem:
                # 尝试其他可能的标题选择器
                title_elem = element.xpath('.//p[contains(@class, "script")]/text()')
                if not title_elem:
                    title_elem = element.xpath('.//p/text()')
                    if not title_elem:
                        title_elem = element.xpath('.//h3/text()')
                        if not title_elem:
                            title_elem = element.xpath('.//h4/text()')
                            if not title_elem:
                                self.log(f"未找到标题元素，跳过该视频")
                                return None
            
            title_encrypted = title_elem[0].strip()  # 获取加密的标题文本
            
            # 4. 解密标题 - 使用网站的解密算法
            title = self._decrypt_title(title_encrypted)
            
            # 5. 提取封面图（逻辑不变，兼容data-original和src）
            pic_elem = element.xpath('.//img/@data-original')  # 优先懒加载地址
            if not pic_elem:
                pic_elem = element.xpath('.//img/@src')  # 兜底：直接src地址
            pic = pic_elem[0] if pic_elem else ''
            
            # 6. 补全图片URL（处理相对路径或无协议的情况）
            if pic:
                if pic.startswith('//'):
                    pic = 'https:' + pic  # 补全https协议
                elif pic.startswith('/'):
                    pic = self.host + pic  # 补全主域名
            
            # 7. 返回正确的视频信息
            return {
                'vod_id': f"618013.xyz_{vod_id}",
                'vod_name': title,  # 此时title已为正确文本
                'vod_pic': pic,
                'vod_remarks': '',
                'vod_year': ''
            }
        except Exception as e:
            self.log(f"提取影片信息出错: {str(e)}")
            return None

    def _decrypt_title(self, encrypted_text):
        """解密标题 - 使用网站的解密算法"""
        try:
            # 网站使用的解密算法：每个字符与128进行异或操作
            decrypted_chars = []
            for char in encrypted_text:
                # 将字符转换为Unicode码点
                code_point = ord(char)
                # 与128进行异或操作
                decrypted_code = code_point ^ 128
                # 转换回字符
                decrypted_char = chr(decrypted_code)
                decrypted_chars.append(decrypted_char)
            
            # 拼接解密后的字符
            decrypted_text = ''.join(decrypted_chars)
            return decrypted_text
        except Exception as e:
            self.log(f"标题解密失败: {str(e)}")
            return encrypted_text  # 如果解密失败，返回原文本

    def _get_detail(self, doc, vid):
        """获取详情信息 (优化版) - 修复播放源提取问题"""
        try:
            title = self._get_text(doc, ['//h1/text()', '//title/text()'])
            pic = self._get_text(doc, ['//div[@class="dyimg"]//img/@src', '//img[@class="poster"]/@src'])
            if pic and pic.startswith('/'):
                pic = self.host + pic
            desc = self._get_text(doc, ['//div[@class="yp_context"]/text()', '//div[@class="introduction"]//text()'])
            actor = self._get_text(doc, ['//span[contains(text(),"主演")]/following-sibling::*/text()'])
            director = self._get_text(doc, ['//span[contains(text(),"导演")]/following-sibling::*/text()'])

            play_from = []
            play_urls = []
            
            # 尝试查找播放源
            play_links = doc.xpath('//a[contains(@href, "m=")]')
            if play_links:
                episodes = []
                for link in play_links:
                    ep_title = link.xpath('./text()')
                    ep_href = link.xpath('./@href')[0]
                    if ep_title:
                        ep_title = ep_title[0].strip()
                        play_id = self.regStr(r'm=(\d+)', ep_href)
                        if play_id:
                            episodes.append(f"{ep_title}${play_id}")
                
                if episodes:
                    play_from.append("默认播放源")
                    play_urls.append('#'.join(episodes))

            if not play_from:
                self.log("未找到播放源元素，无法定位播放源列表")
                # 即使没有播放源，也返回基本信息
                return {
                    'vod_id': vid,
                    'vod_name': title,
                    'vod_pic': pic,
                    'type_name': '',
                    'vod_year': '',
                    'vod_area': '',
                    'vod_remarks': '',
                    'vod_actor': actor,
                    'vod_director': director,
                    'vod_content': desc,
                    'vod_play_from': '默认播放源',
                    'vod_play_url': f"第1集${vid}"
                }

            return {
                'vod_id': vid,
                'vod_name': title,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': actor,
                'vod_director': director,
                'vod_content': desc,
                'vod_play_from': '$$$'.join(play_from),
                'vod_play_url': '$$$'.join(play_urls)
            }
        except Exception as e:
            self.log(f"获取详情出错: {str(e)}")
            return None

    def _get_text(self, doc, selectors):
        """通用文本提取"""
        for selector in selectors:
            texts = doc.xpath(selector)
            for text in texts:
                if text and text.strip():
                    return text.strip()
        return ''
