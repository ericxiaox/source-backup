    # hostresolver.py 与 py/ 同级的上级目录（source/ 根），按脚本自身位置定位，不依赖 cwd
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext
    except Exception:
        resolve_host = None
        parse_ext = None

img_cache = {}

class Spider(BaseSpider):

    # 广告/站务名黑名单（分集名/标签用·全量）：联系方式、外站推广、APP下载、详情页组件标题等
    AD_NAME_RE = re.compile(
        r'联系|合作|广告|发布页|最新地址|永久地址|备用地址|导航|版权|免责|声明|投稿|赞助|招商'
        r'|返利|推广|客服|微信|QQ|qq|群|频道|TG|电报|[Tt]elegram|官网|登录|注册|留言|评论'
        r'|标签云|归档|搜索|关于|帮助|打赏|捐赠|充值|开通会员|商城|网购|彩票|棋牌|支付|汇款'
