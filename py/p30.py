import json
import re
import sys
import os
import hashlib
from base64 import b64decode, b64encode
from urllib.parse import urlparse

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider as BaseSpider
try:
    from hostresolver import resolve_host, parse_ext
except Exception:
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
                cfg = json.loads(ext_str)
                if isinstance(cfg, dict):
                    self.proxies = cfg.get('proxies') or {}
                    for k in ('publish', 'host'):
                        if cfg.get(k):
                            self._ext[k] = str(cfg[k]).strip()
                    if cfg.get('hosts'):
                        hs = cfg['hosts'] if isinstance(cfg['hosts'], list) else [cfg['hosts']]
                        self._ext['hosts'] = [str(h).strip() for h in hs if str(h).strip()]
            except Exception:
                self.proxies = {}
                if parse_ext:
                    try:
                        self._ext = parse_ext(ext_str)
                    except Exception:
                        self._ext = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        }
        self.host = self.get_working_host()
        self.headers.update({'Origin': self.host, 'Referer': f"{self.host}/"})
        print(f"使用站点: {self.host}")

    def getName(self):
        return "🌈 每日大赛|终极完美版"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        global img_cache
        img_cache.clear()

    def get_working_host(self):
        """动态域名解析：ext 覆盖(影视.json) → 发布页尽力抽链 → 内置候选镜像实测 → 跳转壳跟随。
        发布页 njttvylz.cc 为纯 JS 渲染壳（HTTP 抓不到当前域名），故平时完全依赖
        候选镜像列表的实时存活检测；发布页/域名变更改 影视.json 里本源条目的 ext 字段。"""
        ext = getattr(self, '_ext', {}) or {}
        # 0) ext 锁定主页：最高优先级，跳过一切探测（站点结构大改时的终极兜底）
        if ext.get('host'):
            return ext['host'].rstrip('/')
        publish = ext.get('publish') or 'https://www.njttvylz.cc/'
        # ext 里加的新域名排在内置列表前面优先实测；内置列表仍作兜底
        builtin_hosts = [
            'https://barrel.lsaazihd.cc/',   # 当前活镜像(实测253KB完整站)
            'https://big.ktgchwz.xyz/',
            'https://adjust.ktgchwz.xyz/',
            'https://borrow.ktgchwz.xyz/',
            'https://black.ktgchwz.xyz/',
            'https://mrds72.com/',            # 跳转壳 -> biryqddqj.cc
            'https://mrdsx5.com/',
        ]
        if resolve_host:
            host = resolve_host(
                publish_page=publish,
                candidate_hosts=list(ext.get('hosts') or []) + builtin_hosts,
                headers=self.headers,
                proxies=self.proxies,
                timeout=8,
            )
            if host:
                return host
        # 兜底（resolver 缺失时）：ext 指定 → 内置首个
        return (ext.get('hosts') or ['https://barrel.lsaazihd.cc'])[0].rstrip('/')

    def homeContent(self, filter):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'class': [], 'list': []}
            data = self.getpq(response.text)

            classes = []
            seen_ids = set()

            def _add(href, name):
                # 广告清理：外链(联系方式/外站推广)、非内容路径(关于/归档/下载页)、
                # 命中广告黑名单或超长的名称，一律不收
                if not href or href == '#':
                    return
                if not href.startswith('/'):
                    return
                if not re.match(r'^/(category|tag)/', href):
                    return
                name = self._clean_name(name)
                if not name or len(name) > 12 or self.AD_CAT_RE.search(name):
                    return
                if href in seen_ids:
                    return
                seen_ids.add(href)
                classes.append({'type_name': name, 'type_id': href})

            # 1) 常规导航容器（多容器全收集，不再遇到第一个非空就停）
            category_selectors = ['.category-list ul li', '.nav-menu li', '.menu li',
                                  'nav ul li', '.category-list a', '.nav a']
            for selector in category_selectors:
                for k in data(selector).items():
                    link = k if k.is_('a') else k('a').eq(0)
                    _add(link.attr('href'), link.text())

            # 2) 兜底：全页扫描 /category/ /tag/ 链接，保证分类取完全（不漏掉次级导航）
            if len(classes) < 5:
                for a in data('a').items():
                    _add(a.attr('href') or '', a.text())

            if not classes:
                classes = [
                    {'type_name': '每日大赛', 'type_id': '/category/mrds/'},
                ]

            return {
                'class': classes,
                'list': self.getlist(data('#index article, article'))
            }
        except Exception:
            return {'class': [], 'list': []}

    def homeVideoContent(self):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {'list': []}
            data = self.getpq(response.text)
            return {'list': self.getlist(data('#index article, article'))}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            if '@folder' in tid:
                v = self.getfod(tid.replace('@folder', ''))
                return {'list': v, 'page': 1, 'pagecount': 1, 'limit': 90, 'total': len(v)}

            pg = int(pg) if pg else 1

            if tid.startswith('http'):
                base_url = tid.rstrip('/')
            else:
                path = tid if tid.startswith('/') else f"/{tid}"
                base_url = f"{self.host}{path}".rstrip('/')

            if pg == 1:
                url = f"{base_url}/"
            else:
                host_no_slash = self.host.rstrip('/')
                if base_url == host_no_slash:
                    url = f"{host_no_slash}/page/{pg}/"
                elif '/category/' in base_url or '/tag/' in base_url:
                    url = f"{base_url}/{pg}/"
                else:
                    if '/page/' in base_url:
                        url = f"{base_url}/{pg}/"
                    else:
                        url = f"{base_url}/page/{pg}/"

            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            if response.status_code != 200:
                return {
                    'list': [],
                    'page': pg,
                    'pagecount': 9999,
                    'limit': 90,
                    'total': 0
                }

            data = self.getpq(response.text)
            videos = self.getlist(data('#archive article, #index article, article'), tid)

            return {'list': videos, 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 999999}
        except Exception:
            return {'list': [], 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 0}

    def detailContent(self, ids):
        try:
            url = ids[0] if ids[0].startswith('http') else f"{self.host}{ids[0]}"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            data = self.getpq(response.text)

            plist = []
            used_names = set()

            # 策略1: 提取 DPlayer 配置
            if data('.dplayer'):
                for c, k in enumerate(data('.dplayer').items(), start=1):
                    try:
                        config_attr = k.attr('data-config')
                        if config_attr:
                            config = json.loads(config_attr)
                            video_url = config.get('video', {}).get('url', '')

                            if video_url:
                                ep_name = ''
                                parent = k.parents().eq(0)
                                for _ in range(4):
                                    if not parent: break
                                    heading = self._valid_ep_name(parent.find('h2, h3, h4').eq(0).text())
                                    if heading:
                                        ep_name = heading
                                        break
                                    parent = parent.parents().eq(0)
