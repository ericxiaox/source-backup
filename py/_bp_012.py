                p = re.search(r'<img[^>]+(?:data-src|src)=["\']([^"\']+)', it, re.I)
                if h:
                    arr.append({'vod_id':self._id(h.group(1)),'vod_name':self._txt(h.group(2)),'vod_pic':self._abs(p.group(1)) if p else '','vod_remarks':'HD' if 'hd-video' in it else ''})
        seen, out = set(), []
        for v in arr:
            if v['vod_id'] not in seen:
                seen.add(v['vod_id'])
                out.append(v)
        return out

    def _cats(self):
        html = self._get('/categories')
        classes = []
        if BeautifulSoup and html:
            soup = self._soup(html)
            for a in soup.select('a[href*="/video/category/"]'):
                href = a.get('href') or ''
                slug = href.rstrip('/').split('/')[-1]
                name = self._txt(a.get('title') or a.get_text(' ', strip=True))
                if slug and name and slug not in [x['type_id'] for x in classes]:
                    classes.append({'type_id':slug,'type_name':name})
        if not classes:
            classes = [{'type_id':k,'type_name':v} for k,v in self.CATS.items()]
        return classes[:30]

    def homeContent(self, filter=False):
        return {'class':self._cats(),'filters':{},'list':self.homeVideoContent()['list']}

    def homeVideoContent(self):
        return {'list':self._parse_list(self._get('/'))[:20]}

    def categoryContent(self, tid, pg, filter, ext):
        pg = str(pg or '1')
        if tid in ['latest','home','']:
            url = '/' if pg == '1' else '/page/%s/' % pg
        else:
            url = '/video/category/%s/' % tid if pg == '1' else '/video/category/%s/page/%s/' % (tid, pg)
        return {'page':int(pg),'pagecount':999,'limit':20,'total':999,'list':self._parse_list(self._get(url))}

    def detailContent(self, ids):
        vid = ids[0] if isinstance(ids, list) else ids
        url = vid if str(vid).startswith('http') else self.BASE_URL + '/' + str(vid).lstrip('/')
        html = self._get(url)
        name = self._meta(html, 'og:title')
        pic = self._meta(html, 'og:image')
        desc = self._meta(html, 'og:description')
        if BeautifulSoup and html:
            soup = self._soup(html)
            h = soup.select_one('h1.entry-title')
            if h:
                name = self._txt(h.get_text(' ', strip=True)) or name
            im = soup.select_one('meta[itemprop="thumbnailUrl"]')
            if im and im.get('content'):
                pic = im.get('content') or pic
            ds = soup.select_one('meta[itemprop="description"]')
            if ds and ds.get('content'):
                desc = ds.get('content') or desc
        play = self._find_play(html) or url
        vod = {'vod_id':vid,'vod_name':name or str(vid),'vod_pic':self._abs(pic),'type_name':'','vod_year':'','vod_area':'','vod_actor':'','vod_director':'','vod_content':desc or name or '','vod_play_from':'嗅探','vod_play_url':'正片$%s' % play}
        return {'list':[vod]}

    def searchContent(self, key, quick, pg='1'):
        pg = str(pg or '1')
        kw = quote(key)
        url = '/?s=%s' % kw if pg == '1' else '/page/%s/?s=%s' % (pg, kw)
        return {'page':int(pg),'pagecount':999,'limit':20,'total':999,'list':self._parse_list(self._get(url))}

    def playerContent(self, flag, id, vipFlags):
        u = self._abs(id)
        if self.isVideoFormat(u):
            return {'parse':0,'playUrl':'','url':u,'header':self.HEADERS}
        html = self._get(u)
        play = self._find_play(html)
        if play and self.isVideoFormat(play):
            return {'parse':0,'playUrl':'','url':play,'header':self.HEADERS}
        return {'parse':1,'playUrl':'','url':u,'header':self.HEADERS}

    def _find_play(self, html):
        if not html:
            return ''
        pats = [r'<source[^>]+src=["\']([^"\']+)',r'<video[^>]+src=["\']([^"\']+)',r'(https?:\\?/\\?/[^"\'<>]+?\.(?:m3u8|mp4)(?:\?[^"\'<>]*)?)',r'file["\']?\s*[:=]\s*["\']([^"\']+)',r'url["\']?\s*[:=]\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)']
        for p in pats:
            m = re.search(p, html, re.I)
            if m:
                return self._abs(m.group(1).replace('\\/','/'))
        return ''