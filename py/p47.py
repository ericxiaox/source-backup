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
