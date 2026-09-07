                r.encoding = 'utf-8'
            return r.text
        except requests.RequestException:
            return ''

    def _soup(self, html):
        return BeautifulSoup(html, 'html.parser') if BeautifulSoup else None

    def _txt(self, s):
        return re.sub(r'\s+', ' ', s or '').strip()

    def _abs(self, u):
        if not u:
            return ''
        if u.startswith('//'):
            return 'https:' + u
        return urljoin(self.BASE_URL, u)

    def _meta(self, html, name):
        m = re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)' % re.escape(name), html, re.I)
        return self._txt(m.group(1)) if m else ''

    def _id(self, url):
        url = self._abs(url).split('?')[0].rstrip('/')
        return url.replace(self.BASE_URL + '/', '')

    def _parse_list(self, html):
        arr = []
        if BeautifulSoup and html:
            soup = self._soup(html)
            for a in soup.select('article.loop-video.thumb-block a[href]'):
                href = self._abs(a.get('href'))
                if '/video/' not in href:
                    continue
                img = a.select_one('img')
                title = self._txt(a.get('title') or (img.get('alt') if img else '') or (a.select_one('header.entry-header span').get_text(' ', strip=True) if a.select_one('header.entry-header span') else ''))
                pic = self._abs((img.get('data-src') or img.get('src') or img.get('data-original')) if img else '')
                remark = self._txt(' '.join([x.get_text(' ', strip=True) for x in a.select('span.hd-video,span.views,span.duration')]))
                if title and href:
                    arr.append({'vod_id':self._id(href),'vod_name':title,'vod_pic':pic,'vod_remarks':remark})
        if not arr:
            for it in re.findall(r'<article[^>]+loop-video[\s\S]*?</article>', html, re.I):
                h = re.search(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*title=["\']([^"\']+)', it, re.I)
