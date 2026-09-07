    {"type_id": "Fisting-165", "type_name": "拳交"},
    {"type_id": "Gangbang-69", "type_name": "群交"},
    {"type_id": "Teen-13", "type_name": "少女"},
    {"type_id": "Cumshot-18", "type_name": "射颜"},
    {"type_id": "Cam_Porn-58", "type_name": "摄像头"},
    {"type_id": "Bi_Sexual-62", "type_name": "双性恋"},
    {"type_id": "Stockings-28", "type_name": "丝袜"},
    {"type_id": "Oiled-22", "type_name": "涂油"},
    {"type_id": "Lingerie-83", "type_name": "性感内衣"},
    {"type_id": "Asian_Woman-32", "type_name": "亚洲"},
    {"type_id": "Amateur-65", "type_name": "业余"},
    {"type_id": "Interracial-27", "type_name": "异族"},
    {"type_id": "Indian-89", "type_name": "印度"},
    {"type_id": "Creampie-40", "type_name": "中出"},
    {"type_id": "Solo_and_Masturbation-33", "type_name": "自慰"},
    {"type_id": "AI-239", "type_name": "AI"},
    {"type_id": "ASMR-229", "type_name": "ASMR"},
]


class Spider(Spider):
    def getName(self):
        return "V-HUB[成人]"

    def init(self, extend):
        # ext 统一解析：host@ 锁定主页 > JSON/文本 ext > 内置 SITE_URL（见 hostresolver.ext_of）
        try:
            from hostresolver import ext_of
            self._ext = ext_of(extend)
        except Exception:
            try:
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from hostresolver import ext_of
                self._ext = ext_of(extend)
            except Exception:
                self._ext = {}
        self.host = self._ext.get('host', '').rstrip('/') or SITE_URL
        self.api_url = self.host.rstrip('/') + '/api'
        self.headers = {
