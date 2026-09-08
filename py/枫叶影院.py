# -*- coding: utf-8 -*-
import os
import sys
import re, urllib.parse
import json
from bs4 import BeautifulSoup
import requests
from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    # 域名池：原枫叶影院/枫叶影院1 两克隆合并，init 时探测择活
    CANDIDATE_HOSTS = ('https://maihaolian.com', 'https://www.shzchc.com')

    def init(self, extend=""):
        # ext 统一解析：host@ 锁定 > JSON/文本 ext > 内置域名池探测（见 hostresolver.ext_of）
        self._ext = {}
        try:
            from hostresolver import ext_of
            self._ext = ext_of(extend)
        except ImportError:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            try:
                from hostresolver import ext_of
                self._ext = ext_of(extend)
            except Exception:
                self._ext = {}
        except Exception:
            self._ext = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        self.host = (self._ext.get('host') or '').rstrip('/') or self._detect_host()

    def _detect_host(self):
        # v2 resolver：并行探测 + 成功缓存30分钟；全败返回 ''（接口层 except 兜空，不静默回死域）
        try:
            from hostresolver import resolve_host
            return resolve_host(
                publish_page=None,
                candidate_hosts=list(self.CANDIDATE_HOSTS),
                headers=self.headers,
                timeout=6,
            )
        except Exception:
            pass
        # resolver 缺失时（不应发生）：退回串行探测
        for h in self.CANDIDATE_HOSTS:
            try:
                r = requests.head(h, headers=self.headers, timeout=6, allow_redirects=True)
                if r.status_code < 500:
                    return h
            except Exception:
                continue
        return ''

    def getName(self):
        return '枫叶影院'

    def homeContent(self, filter):
        # 站方列表验证码墙：ajax_show 通道不支持筛选参数，故不提供 filters（避免假筛选 UI）
        return {"class": [
            {'type_id': "/label/qq", 'type_name': "腾讯VIP精选"},
            {'type_id': "/label/bli", 'type_name': "B站VIP精选"},
            {'type_id': "/label/youku", 'type_name': "优酷VIP精选"},
            {"type_id": "5", "type_name": "红果短剧"},
            {"type_id": "2", "type_name": "电视剧"},
            {"type_id": "1", "type_name": "电影"},
            {"type_id": "4", "type_name": "动漫"},
            {"type_id": "3", "type_name": "综艺"},
        ]}

    def homeVideoContent(self):
        html = self._fetch('/')
        return {"list": self._parse_video_list(html)}

    def categoryContent(self, tid, pg, filter, extend):
        # 构建筛选参数：参照歪比巴卜，直接取extend里的值，fallback到filter
        if tid.startswith('/label'):
            url = f'{tid}/page/{pg}.html'
            html = self._fetch(url)
            items = self._parse_video_list(html)
            page = int(pg)
            page_count = page if len(items) < 24 else page + 2
            return {"list": items, "page": page, "pagecount": page_count, "limit": 24, "total": page_count * 24}

        args = {}
        if extend and isinstance(extend, dict):
            for k, v in extend.items():
                if v:
                    args[k] = str(v)
        if isinstance(filter, dict):
            for k, v in filter.items():
                if v and k not in args:
                    args[k] = str(v)
        route_tid = args.get('class', args.get('tid', str(tid)))
        area = args.get('area', '')
        genre = args.get('genre', '')
        year = args.get('year', '')
        lang = args.get('lang', '')
        letter = args.get('letter', '')
        sort = args.get('sort', '')
        # 无筛选走正常分页（cupfox-list 路由被站方验证码墙拦截，改走免验证的 ajax_show；
        # 注意：页码必须放独立的 /page/N 段，写在 id 槽位里会被忽略）
        if not area and not genre and not year and not lang and not letter and not sort:
            url = f'/index.php?s=/vod/ajax_show/id/{route_tid}--------1---/page/{pg}.html'
            html = self._fetch(url)
            items = self._parse_video_list(html)
            page = int(pg)
            soup = BeautifulSoup(html, 'html.parser')
            pagecount = page
            for a in soup.select('a.page-link'):
                if a.text == '尾页':
                    m = re.search(r'/page/(\d+)\.html', a.get('href', ''))
                    if m:
                        pagecount = int(m.group(1))
                    break
            if not items:
                pagecount = 0
            return {"list": items, "page": page, "pagecount": pagecount, "limit": 36, "total": 9999}
        # 有筛选：{tid}-{area}-{sort}-{genre}-{lang}-{letter}------{year}.html（同样走免验证 ajax_show）
        segs = [route_tid, area, sort, genre, lang, letter, '', '', year]
        url = '/index.php?s=/vod/ajax_show/id/' + '-'.join(segs) + '.html'
        html = self._fetch(url)
        items = self._parse_video_list(html)
        return {"list": items, "page": 1, "pagecount": 1, "limit": 36, "total": 9999}

    def detailContent(self, ids):
        result = {"list": []}
        vid = ids[0].split(',')[0].strip()
        try:
            html = self._fetch(f'/detail/{vid}.html')
            if not html: return result
            soup = BeautifulSoup(html, 'html.parser')
            vod_name = soup.select_one('h3.slide-info-title')
            vod_name = vod_name.text.strip() if vod_name else ''
            vod_pic = soup.select_one('img.lazy')
            vod_pic = self._fix_pic(vod_pic.get('data-src', '')) if vod_pic else ''
            vod_director = ''
            vod_actor = ''
            for el in soup.select('.slide-info'):
                text = el.get_text(' ').strip()
                if text.startswith('导演：'):
                    vod_director = text.replace('导演：', '').strip()
                elif text.startswith('演员：'):
                    vod_actor = text.replace('演员：', '').strip()
            vod_content = soup.select_one('#height_limit')
            vod_content = vod_content.get_text(' ', strip=True) if vod_content else ''
            play_from, play_url = [], []
            for tab in soup.select('.anthology-tab a.swiper-slide'):
                src_name = re.sub(r'<[^>]+>', '', str(tab)).strip() or tab.get_text(' ', strip=True).strip()
                if src_name:
                    play_from.append(src_name)
            tab_blocks = soup.select('.anthology-list-box')
            for i, block in enumerate(tab_blocks):
                ep_list = []
                for a in block.select('li a'):
                    href = a.get('href', '')
                    m = re.search(r'/play/(.*?)\.html', href)
                    if m:
                        ep_list.append(f'{a.text.strip()}${vid}-{m.group(1)}')
                ep_list.reverse()
                if ep_list and i < len(play_from):
                    play_url.append('#'.join(ep_list))
            valid_from = [pf for i, pf in enumerate(play_from) if i < len(play_url)]
            result["list"].append({
                "vod_id": vid, "vod_name": vod_name, "vod_pic": vod_pic,
                "vod_director": vod_director, "vod_actor": vod_actor,
                "vod_content": vod_content,
                "vod_play_from": "$$$".join(valid_from),
                "vod_play_url": "$$$".join(play_url),
            })
        except:
            pass
        return result

    def searchContent(self, key, quick, pg="1"):
        try:
            decoded = urllib.parse.unquote(key)
        except:
            decoded = key
        html = self._fetch(f'/index.php?s=/vod/ajax_search/wd/{urllib.parse.quote(decoded)}/pg/{pg}')
        items = self._parse_search_list(html)
        return {"list": items, "page": int(pg), "pagecount": 1, "limit": 36, "total": len(items)}

    def playerContent(self, flag, id, vipFlags):
        url = ''
        try:
            url = id if id.startswith('http') else f'{self.host}/play/{id}.html'
            html = self._fetch(url)
            if html:
                m = re.search(r'player_aaaa=(.*?)</script>', html, re.S)
                if m:

                    try:
                        pd = json.loads(m.group(1))
                    except Exception as e:
                        print(e)
                        pd = {}
                    # print('pd:', pd)
                    play_url = pd.get('url')
                    play_id = pd.get('from')

                    api_map = {
                        'YYNB': 'https://zzrs.mfdyvip.com/player/mplayer.php',
                        'JD4K': 'https://fgsrg.hzqingshan.com/player/mplayer.php',
                    }
                    if not play_url:
                        return {"parse": 0, "url": 'https://php.doube.eu.org/error.m3u8',
                                "header": {'User-Agent': 'Mozilla/5.0'}}
                    if play_url.startswith('http') and (play_url.endswith('.m3u8') or play_url.endswith('.mp4')):
                        return {"parse": 0, "url": play_url, "header": {'User-Agent': 'Mozilla/5.0'}}

                    else:
                        headers = {
                            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
                            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                            'accept-language': "zh-CN,zh;q=0.9",
                            'cache-control': "no-cache",
                            'pragma': "no-cache",
                            'priority': "u=0, i",
                            'referer': "https://www.ht10010.com/",
                            'Content-Type': 'application/x-www-form-urlencoded',
                        }
                        response = requests.get(f"https://fgsrg.hzqingshan.com/player/?url={play_url}", headers=headers)
                        token = re.search(r'data-te="(.*?)"', response.text)
                        if token:
                            token = token.group(1)
                            payload = {
                                'url': play_url,
                                'token': token
                            }
                            # print('payload', payload)
                            try:
                                response = self.post(api_map[play_id], data=payload, headers=headers)

                                response.raise_for_status()
                                result = response.json()
                                # print('result:', result)
                                if result['code'] == 200 and 'url' in result:
                                    play_url = result['url']
                                    return {"parse": 0, "url": play_url, "header": {
                                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'}}
                            except Exception as e:
                                print(e)
        except Exception as e:
            print(e)
        return {"parse": 1, "url": url}

    def localProxy(self, param=''):
        return {}

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def _fetch(self, url):
        try:
            if not url.startswith('http'):
                url = self.host + url
            rsp = self.fetch(url, headers=self.headers)
            return rsp.text if rsp else ''
        except:
            return ''

    def _fix_pic(self, u):
        if not u: return ''
        if u.startswith('//'): return 'https:' + u
        return u.replace('&amp;', '&')

    def _parse_video_list(self, html):
        videos, seen = [], set()
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.select('a.public-list-exp')
        for a in cards:
            href = a.get('href', '')
            m = re.search(r'/detail/(\d+)\.html', href)
            if not m: continue
            vod_id = m.group(1)
            if vod_id in seen: continue
            seen.add(vod_id)
            span = ','.join([span.text for span in a.select('span.public-prt')])
            # print('span', span)
            vod_name = a.get('title', '') or (a.select_one('img') and a.select_one('img').get('alt', '')) or ''
            pic_el = a.select_one('img')
            vod_pic = self._fix_pic(pic_el.get('data-src', '')) if pic_el else ''
            remark_el = a.select_one('.ft2') or a.select_one('.public-list-prb')
            vod_remarks = remark_el.text.strip() if remark_el else ''
            videos.append(
                {"vod_id": vod_id, "vod_name": vod_name.strip(), "vod_pic": vod_pic, "vod_remarks": vod_remarks, "vod_year": span})
        return videos

    def _parse_search_list(self, html):
        videos, seen = [], set()
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.select('a.public-list-exp')
        for a in cards:
            href = a.get('href', '')
            m = re.search(r'/detail/(\d+)\.html', href)
            if not m: continue
            vod_id = m.group(1)
            if vod_id in seen: continue
            seen.add(vod_id)
            pic_el = a.select_one('img')
            vod_pic = self._fix_pic(pic_el.get('data-src', '')) if pic_el else ''
            title_el = soup.select_one(f'a.thumb-txt[href="/detail/{vod_id}.html"]')
            if title_el:
                vod_name = title_el.text.strip()
            else:
                vod_name = a.select_one('img') and a.select_one('img').get('alt', '') or ''
            remark_el = a.select_one('.public-list-prb') or a.select_one('.ft2')
            vod_remarks = remark_el.text.strip() if remark_el else ''
            videos.append(
                {"vod_id": vod_id, "vod_name": vod_name.strip(), "vod_pic": vod_pic, "vod_remarks": vod_remarks})
        return videos


if __name__ == '__main__':
    sp = Spider()
    sp.init()
    # 20067-5-189
    print(sp.categoryContent('/label/qq','1',True, {}))
    # print(sp.playerContent('', '20067-6-189', []))
    # print(sp.playerContent('', '20067-5-189', []))
    pass
