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
