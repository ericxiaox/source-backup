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
