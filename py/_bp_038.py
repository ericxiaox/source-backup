            videos = self._get_videos(doc)
            return {'list': videos}
        except Exception as e:
            self.log(f"搜索出错: {str(e)}")
            return {'list': []}

    def detailContent(self, ids):
        """详情页面"""
        try:
            vid = ids[0]
            if '_' in vid:
                domain, video_id = vid.split('_')
                detail_url = f"https://{domain}/index.php/vod/detail/id/{video_id}.html"
            else:
                detail_url = f"{self.host}/index.php/vod/detail/id/{vid}.html"
            self.log(f"访问详情URL: {detail_url}")
            rsp = self.fetch(detail_url, headers=self.headers)
            doc = self.html(rsp.text)
            video_info = self._get_detail(doc, vid)
            return {'list': [video_info]} if video_info else {'list': []}
        except Exception as e:
            self.log(f"详情获取出错: {str(e)}")
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        """播放链接 - 直接使用API获取视频地址"""
        try:
            self.log(f"获取播放链接: flag={flag}, id={id}")
            
            # 提取视频ID
            if '_' in id:
                _, video_id = id.split('_')
            else:
                video_id = id
                
            self.log(f"视频ID: {video_id}")
            
            # 直接调用API获取视频地址
            api_url = f"{self.api_host}/api/v2/vod/reqplay/{video_id}"
            self.log(f"请求API获取视频地址: {api_url}")
            
            api_headers = self.headers.copy()
            api_headers.update({
                'Referer': f"{self.host}/",
                'Origin': self.host,
                'X-Requested-With': 'XMLHttpRequest'
            })
            
            api_response = self.fetch(api_url, headers=api_headers)
            if api_response and api_response.status_code == 200:
                data = api_response.json()
                self.log(f"API响应: {data}")
