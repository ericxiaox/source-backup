    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        """获取首页内容和分类"""
        result = {}
        # 只保留指定的分类
        classes = [
            {'type_id': '618013.xyz_1', 'type_name': '全部视频'},
            {'type_id': '618013.xyz_13', 'type_name': '香蕉精品'},
            {'type_id': '618013.xyz_22', 'type_name': '制服诱惑'},
            {'type_id': '618013.xyz_6', 'type_name': '国产视频'},
            {'type_id': '618013.xyz_8', 'type_name': '清纯少女'},
            {'type_id': '618013.xyz_9', 'type_name': '辣妹大奶'},
            {'type_id': '618013.xyz_10', 'type_name': '女同专属'},
            {'type_id': '618013.xyz_11', 'type_name': '素人出演'},
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
