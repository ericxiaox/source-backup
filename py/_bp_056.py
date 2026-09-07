            {'type_id': '618013.xyz_44', 'type_name': '国产传媒'},
            {'type_id': '618013.xyz_32', 'type_name': '国产自拍'}
        ]
        result['class'] = classes
        try:
            rsp = self.fetch(self.host, headers=self.headers)
            doc = self.html(rsp.text)
            videos = self._get_videos(doc, limit=20)
            result['list'] = videos
        except Exception as e:
            self.log(f"首页获取出错: {str(e)}")
            result['list'] = []
        return result

    def homeVideoContent(self):
        """分类定义 - 兼容性方法"""
        return {
            'class': [
                {'type_id': '618013.xyz_1', 'type_name': '全部视频'},
                {'type_id': '618013.xyz_13', 'type_name': '香蕉精品'},
                {'type_id': '618013.xyz_22', 'type_name': '制服诱惑'},
                {'type_id': '618013.xyz_6', 'type_name': '国产视频'},
                {'type_id': '618013.xyz_8', 'type_name': '清纯少女'},
                {'type_id': '618013.xyz_9', 'type_name': '辣妹大奶'},
                {'type_id': '618013.xyz_10', 'type_name': '女同专属'},
                {'type_id': '618013.xyz_11', 'type_name': '素人出演'},
