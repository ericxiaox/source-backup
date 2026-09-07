                {'type_id': '618013.xyz_12', 'type_name': '角色扮演'},
                {'type_id': '618013.xyz_20', 'type_name': '人妻熟女'},
                {'type_id': '618013.xyz_23', 'type_name': '日韩剧情'},
                {'type_id': '618013.xyz_21', 'type_name': '经典伦理'},
                {'type_id': '618013.xyz_7', 'type_name': '成人动漫'},
                {'type_id': '618013.xyz_14', 'type_name': '精品二区'},
                {'type_id': '618013.xyz_40', 'type_name': '精品三区'},
                {'type_id': '618013.xyz_53', 'type_name': '动漫中字'},
                {'type_id': '618013.xyz_52', 'type_name': '日本无码'},
                {'type_id': '618013.xyz_33', 'type_name': '中文字幕'},
                {'type_id': '618013.xyz_44', 'type_name': '国产传媒'},
                {'type_id': '618013.xyz_32', 'type_name': '国产自拍'}
            ]
        }

    def categoryContent(self, tid, pg, filter, extend):
        """分类内容 - 修改为使用固定页数设置"""
        try:
            domain, type_id = tid.split('_')
            url = f"https://{domain}/index.php/vod/type/id/{type_id}.html"
            if pg and pg != '1':
                url = url.replace('.html', f'/page/{pg}.html')
            self.log(f"访问分类URL: {url}")
            rsp = self.fetch(url, headers=self.headers)
            doc = self.html(rsp.text)
