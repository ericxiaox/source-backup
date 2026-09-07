        r'|APP|App|app|下载|商务|友链|申请链接|反馈|举报|用户|头像|签到'
        r'|温馨提示|重要提示|往期|回家的路')

    # 分类专用精简黑名单：只挡"几乎不可能是正式分类"的词（防止误杀"原创投稿"这类真分类）
    AD_CAT_RE = re.compile(
        r'联系|合作|广告|发布页|最新地址|永久地址|备用地址|导航|客服|微信|QQ|qq|群|频道'
        r'|TG|电报|[Tt]elegram|官网|登录|注册|APP|App|app|下载|商务|友链|商城|网购|彩票'
        r'|棋牌|支付|汇款|打赏|捐赠|充值')

    img_cache = {}

    @staticmethod
    def _clean_name(s):
        """剔除未渲染的前端模板串（如 {{u.username}}）"""
        return re.sub(r'\{\{[^}]*\}\}', '', s or '').strip()

    def _valid_ep_name(self, s, max_len=40):
        """清洗分集/标签名：模板串剔除后为空、超长、命中广告黑名单 → 返回 ''"""
        s = self._clean_name(s)
        if not s or len(s) > max_len:
            return ''
        if self.AD_NAME_RE.search(s):
            return ''
        return s

    def init(self, extend=""):
        self.proxies = {}
        self._ext = {}
        ext_str = (extend or '').strip()
        if ext_str:
            # 两种 ext 写法都支持：
            #   1) 纯文本:  publish@https://...;hosts@https://a,https://b;host@https://...
            #   2) JSON:    {"publish":"...","hosts":["..."],"host":"...","proxies":{...}}
            try:
