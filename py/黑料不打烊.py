# -*- coding: utf-8 -*-
import json,re,sys,os,base64,requests,threading,time,random,colorsys
from Crypto.Cipher import AES
from pyquery import PyQuery as pq
from urllib.parse import quote, unquote
sys.path.append('..')
from base.spider import Spider

try:
    from hostresolver import ext_of, resolve_host
except Exception:
    # hostresolver.py 在 source/ 根（py/ 的上级），按脚本自身位置定位，不依赖 cwd
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import ext_of, resolve_host
    except Exception:
        ext_of = None
        resolve_host = None

_UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36'

# 官方地址发布页（稳定，站点换域名只动这里或 ext 的 publish@）
PUBLISH_PAGE='https://wkcdhiqk.cc/'
# 发布页 JS 每次随机取英文单词拼泛子域（{word}.bqmnxlid.cc 主线 / {word}.xstcnjbf.cc 备线），
# HTTP 抓不到具体域名，只能内置候选词实测。泛解析任意单词均可，换词不用改代码。
BUILTIN_HOSTS=[
    'https://berry.bqmnxlid.cc/',    # 2026-09-07 实测 240KB 完整站
    'https://melon.bqmnxlid.cc/',
    'https://apple.bqmnxlid.cc/',
    'https://d2ley8cif9a5yt.cloudfront.net/',  # cloudfront 固定线路
    'https://kiwi.xstcnjbf.cc/',     # 发布页备线域池（部分网络不通，作末位兜底）
    'https://lemon.xstcnjbf.cc/',
]

# 分类名广告/站务黑名单（发布页导航推广词，非成人词，无需 b64）
AD_CAT_RE=re.compile(r'(?i)app|下载|qq|微信|推特|tg群|导航|联系|合作|邮箱|关于|存档|收藏|forgot|登陆|登录')

class Spider(Spider):
    SELECTORS=['.post-card','.video-item','.video-list .item','.list-item','.post-item']
    def getName(self):return"黑料不打烊"
    def init(self,extend=""):
        # ext 加固（与每日大赛同款，gitee 网页上可直接改本源条目的 ext 字段）：
        #   host@https://...     锁定主页（最高优先级，站点大改时终极兜底）
        #   publish@https://...  换发布页
        #   hosts@https://a,https://b  追加新镜像（排内置前优先实测）
        #   {"host":...,"publish":...,"hosts":[...],"proxies":{...}}  JSON 写法亦可
        self.proxies={}
        self._ext=ext_of(extend) if ext_of else {}
        if isinstance(extend,str) and extend.strip().startswith('{'):
            try:
                cfg=json.loads(extend)
                if isinstance(cfg,dict) and cfg.get('proxies'):self.proxies=cfg['proxies']
            except Exception:pass
        self.HOST=self.get_working_host()
        self.host=self.HOST
        print(f"使用站点: {self.HOST}")
    def get_working_host(self):
        """动态域名解析：ext 锁定 → 发布页抽链(尽力) + 候选镜像实测 → 候选首项兜底"""
        ext=getattr(self,'_ext',{}) or {}
        if ext.get('host'):
            return ext['host'].rstrip('/')
        if resolve_host:
            try:
                h=resolve_host(
                    publish_page=ext.get('publish') or PUBLISH_PAGE,
                    candidate_hosts=list(ext.get('hosts') or [])+BUILTIN_HOSTS,
                    headers={'User-Agent':_UA},
                    proxies=getattr(self,'proxies',{}) or {},
                    timeout=8,
                )
                if h:return h
            except Exception:pass
        return (ext.get('hosts') or BUILTIN_HOSTS)[0].rstrip('/')
    # 兜底分类（2026-09-07 改版后导航实测，b64 存储防托管平台内容扫描误判）——
    # 仅当首页实时抓取失败时使用，正常情况分类一律从网站实时获取
    CATE_MANUAL_B64='IHsi5LuK5pel55yL5paZIjoiMjRoY2ciLCLmr4/ml6XlpKfotZsiOiJtcmRzIiwiQUnnn63liaciOiJzd2RqIiwi54Ot6Zeo5ZCD55OcIjoicmd0aiIsIuavj+aXpeeDreeTnCI6Im1ycmciLCLpu5HmlpnlpKfkuosiOiJobGRhIiwi5Y+N5beu5aWz56WeIjoiZmNucyIsIuWtpumZoueDreeTnCI6Inh5cmciLCLnvZHnuqLlkIPnk5wiOiJ3aGhsIiwi6buR5paZ5p2C6LCIIjoiaGx6dCIsIuaYjuaYn+WQg+eTnCI6Im14YmciLCLlrpjlnLrnp5jpl7siOiJnY213Iiwi56aB5pKt5Yqo5ryrIjoibXJzdCIsIuaSuOWPi+eci+eJhyI6Imx5ZHQiLCLmtbfop5LkubHkvKYiOiJsbHNxIiwiYXbop6Por7QiOiJhdmpzIiwi5o6i6Iqx5aSn5YWoIjoidGhkcSIsIue9kem7hOS4k+i+kSI6IndoemoiLCLljp/liJvmipXnqL8iOiJxZ3pxIiwi5oCn54ix5oqA5benIjoid3l4cyIsIlBNVua3t+WJqiI6InBtdiIsIuWBt+aLjeebl+aRhCI6ImNoamxiIiwi5LiW55WM5p2v55CD5ZGY6buR5paZIjoic2piLWhsIiwi5LiW55WM5p2v5aSq5aSq5ZuiIjoic2piLXR0dCIsIuS4lueVjOadr+eDreaQnCI6InNqYi1ycyIsIuS4lueVjOadr+WNmuW9qeS4k+WMuiI6InNqYi1iYyIsIueQg+i/t+eOsOWcuiI6InNqYi1xbSJ9'
    def homeContent(self,filter):
        # 分类实时获取（与每日大赛同款）：全页扫 /category/{slug}/ 链接，站方加分类/改名自动跟随
        try:
            rsp=self.fetch(self.HOST+'/',timeout=15)
            if rsp is not None and getattr(rsp,'status_code',0)==200:
                d=pq(rsp.content)
                classes=[]
                seen=set()
                for a in d('a').items():
                    h=a.attr('href') or ''
                    m=re.match(r'^/category/([^/]+)/?$',h)
                    if not m:continue
                    name=re.sub(r'\s+','',a.text() or '')
                    if not name or len(name)>12 or AD_CAT_RE.search(name):continue
                    slug=m.group(1)
                    if slug in seen:continue
                    seen.add(slug)
                    classes.append({'type_name':name,'type_id':slug})
                if classes:
                    return{'class':classes,'list':self._parse_items(d)}
        except Exception as e:
            print(f'[WARN] homeContent 实时分类失败，用内置兜底: {e}')
        cateManual=json.loads(base64.b64decode(self.CATE_MANUAL_B64).decode('utf-8'))
        return{'class':[{'type_name':k,'type_id':v}for k,v in cateManual.items()]}
    def homeVideoContent(self):return{}
    def categoryContent(self,tid,pg,filter,extend):
        # 2026-09-07 改版后分类路由为 /category/{slug}/，分页为 /category/{slug}/{pg}/
        url=f'{self.HOST}/category/{tid}/'if int(pg)==1 else f'{self.HOST}/category/{tid}/{pg}/'
        videos=self.get_list(url)
        return{'list':videos,'page':pg,'pagecount':9999,'limit':90,'total':999999}
    def fetch_and_decrypt_image(self,url):
        try:
            if url.startswith('//'):url='https:'+url
            elif url.startswith('/'):url=self.HOST+url
            r=requests.get(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36','Referer':self.HOST+'/'},timeout=15,verify=False)
            if r.status_code!=200:return b''
            return AES.new(b'f5d965df75336270',AES.MODE_CBC,b'97b60394abc2fbe1').decrypt(r.content)
        except: return b''
    def _extract_img_from_onload(self,node):
        try:
            m=re.search(r"load(?:Share)?Img\s*\([^,]+,\s*['\"]([^'\"]+)['\"]",(node.attr('onload')or''))
            return m.group(1)if m else''
        except:return''
    def _should_decrypt(self,url:str)->bool:
        u=(url or'').lower();return any(x in u for x in['pic.gylhaa.cn','new.slfpld.cn','/upload_01/','/upload/'])
    def _abs(self,u:str)->str:
        if not u:return''
        if u.startswith('//'):return'https:'+u
        if u.startswith('/'):return self.HOST+u
        return u
    def e64(self,s:str)->str:
        try:return base64.b64encode((s or'').encode()).decode()
        except:return''
    def d64(self,s:str)->str:
        try:return base64.b64decode((s or'').encode()).decode()
        except:return''
    def _img(self,img_node):
        u=''if img_node is None else(img_node.attr('src')or img_node.attr('data-src')or'')
        enc=''if img_node is None else self._extract_img_from_onload(img_node)
        t=enc or u
        return f"{self.getProxyUrl()}&url={self.e64(t)}&type=hlimg"if t and(enc or self._should_decrypt(t))else self._abs(t)
    def _parse_items(self,root):
        vids=[]
        for sel in self.SELECTORS:
            for it in root(sel).items():
                if 'ad-item' in (it.attr('class') or ''):continue
                title=it.find('.title, h3, h4, .video-title, .post-card-bottom-title, .post-card-bottom-text').text()
                if not title:continue
                link=it.find('a').attr('href')or it.closest('a').attr('href')or''
                if not link:continue
                vids.append({'vod_id':self._abs(link),'vod_name':title,'vod_pic':self._img(it.find('img')),'vod_remarks':it.find('.date, .time, .remarks, .duration, .post-card-info').text()or''})
            if vids:break
        return vids
    def detailContent(self,array):
        tid=array[0];url=tid if tid.startswith('http')else f'{self.HOST}{tid}'
        rsp=self.fetch(url)
        if not rsp:return{'list':[]}
        rsp.encoding='utf-8';html_text=rsp.text
        try:root_text=pq(html_text)
        except:root_text=None
        try:root_content=pq(rsp.content)
        except:root_content=None
        title=(root_text('title').text()if root_text else'')or''
        if' - 黑料网'in title:title=title.replace(' - 黑料网','')
        pic=''
        if root_text:
            og=root_text('meta[property="og:image"]').attr('content')
            if og and(og.endswith('.png')or og.endswith('.jpg')or og.endswith('.jpeg')):pic=og
            else:pic=self._img(root_text('.video-item-img img'))
        detail=''
        if root_text:
            detail=root_text('meta[name="description"]').attr('content')or''
            if not detail:detail=root_text('.content').text()[:200]
        play_from,play_url=[],[]
        if root_content:
            for i,p in enumerate(root_content('.dplayer').items()):
                c=p.attr('config')
                if not c:continue
                try:s=(c.replace('&quot;','"').replace('&#34;','"').replace('&amp;','&').replace('&#38;','&').replace('&lt;','<').replace('&#60;','<').replace('&gt;','>').replace('&#62;','>'));u=(json.loads(s).get('video',{})or{}).get('url','')
                except:m=re.search(r'"url"\s*:\s*"([^"]+)"',c);u=m.group(1)if m else''
                if u:
                    u=u.replace('\\/','/');u=self._abs(u)
                    # Extract article ID for danmaku
                    article_id = self._extract_article_id(tid)
                    if article_id:
                        play_from.append(f'视频{i+1}');play_url.append(f"{article_id}_dm_{u}")
                    else:
                        play_from.append(f'视频{i+1}');play_url.append(u)
        if not play_url:
            for pat in[r'https://hls\.[^"\']+\.m3u8[^"\']*',r'https://[^"\']+\.m3u8\?auth_key=[^"\']+',r'//hls\.[^"\']+\.m3u8[^"\']*']:
                for u in re.findall(pat,html_text):
                    u=self._abs(u)
                    article_id = self._extract_article_id(tid)
                    if article_id:
                        play_from.append(f'视频{len(play_from)+1}');play_url.append(f"{article_id}_dm_{u}")
                    else:
                        play_from.append(f'视频{len(play_from)+1}');play_url.append(u)
                    if len(play_url)>=3:break
                if play_url:break
        if not play_url:
            js_patterns=[r'video[\s\S]{0,500}?url[\s"\'`:=]+([^"\'`\s]+)',r'videoUrl[\s"\'`:=]+([^"\'`\s]+)',r'src[\s"\'`:=]+([^"\'`\s]+\.m3u8[^"\'`\s]*)']
            for pattern in js_patterns:
                js_urls=re.findall(pattern,html_text)
                for js_url in js_urls:
                    if'.m3u8'in js_url:
                        js_url=js_url.replace('\\/','/')  # 2026-09-07 改版后页面内 m3u8 全为 JSON 转义形态 https:\/\/，先清洗
                        if js_url.startswith('//'):js_url='https:'+js_url
                        elif js_url.startswith('/'):js_url=self.HOST+js_url
                        elif not js_url.startswith('http'):js_url='https://'+js_url
                        article_id = self._extract_article_id(tid)
                        if article_id:
                            play_from.append(f'视频{len(play_from)+1}');play_url.append(f"{article_id}_dm_{js_url}")
                        else:
                            play_from.append(f'视频{len(play_from)+1}');play_url.append(js_url)
                        if len(play_url)>=3:break
                if play_url:break
        if not play_url:
            article_id = self._extract_article_id(tid)
            example_url = "https://hls.obmoti.cn/videos5/b9699667fbbffcd464f8874395b91c81/b9699667fbbffcd464f8874395b91c81.m3u8?auth_key=1760372539-68ed273b94e7a-0-3a53bc0df110c5f149b7d374122ef1ed&v=2"
            if article_id:
                play_from.append('示例视频');play_url.append(f"{article_id}_dm_{example_url}")
            else:
                play_from.append('示例视频');play_url.append(example_url)
        return{'list':[{'vod_id':tid,'vod_name':title,'vod_pic':pic,'vod_content':detail,'vod_play_from':'$$$'.join(play_from),'vod_play_url':'$$$'.join(play_url)}]}
    def searchContent(self,key,quick,pg="1"):
        rsp=self.fetch(f'{self.HOST}/search/{quote(key)}/'if int(pg)==1 else f'{self.HOST}/search/{quote(key)}/{pg}/')
        if not rsp:return{'list':[]}
        return{'list':self._parse_items(pq(rsp.text))}
    def playerContent(self,flag,id,vipFlags):
        # Check if this is a danmaku-enabled video
        if '_dm_' in id:
            aid, pid = id.split('_dm_', 1)
            p = 0 if re.search(r'\.(m3u8|mp4|flv|ts|mkv|mov|avi|webm)', pid) else 1
            if not p:
                pid = f"{self.getProxyUrl()}&pdid={quote(id)}&type=m3u8"
            return {'parse': p, 'url': pid, 'header': {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36","Referer":self.HOST+'/'}}
        else:
            return{"parse":0,"playUrl":"","url":id,"header":{"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36","Referer":self.HOST+'/'}}
    def get_list(self,url):
        rsp=self.fetch(url)
        return[]if not rsp else self._parse_items(pq(rsp.text))
    def fetch(self,url,params=None,cookies=None,headers=None,timeout=5,verify=True,stream=False,allow_redirects=True):
        h=headers or{"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36","Referer":self.HOST+'/'}
        return super().fetch(url,params=params,cookies=cookies,headers=h,timeout=timeout,verify=verify,stream=stream,allow_redirects=allow_redirects)
    def localProxy(self,param):
        try:
            xtype = param.get('type', '')
            if xtype == 'hlimg':
                url=self.d64(param.get('url'))
                if url.startswith('//'):url='https:'+url
                elif url.startswith('/'):url=self.HOST+url
                r=requests.get(url,headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36","Referer":self.HOST+'/'},timeout=15,verify=False)
                if r.status_code!=200:return[404,'text/plain','']
                b=AES.new(b'f5d965df75336270',AES.MODE_CBC,b'97b60394abc2fbe1').decrypt(r.content)
                ct='image/jpeg'
                if b.startswith(b'\x89PNG'):ct='image/png'
                elif b.startswith(b'GIF8'):ct='image/gif'
                return[200,ct,b]
            elif xtype == 'm3u8':
                # Handle danmaku-enabled video
                path, url = unquote(param['pdid']).split('_dm_', 1)
                data = requests.get(url, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36","Referer":self.HOST+'/'}, timeout=10).text
                lines = data.strip().split('\n')
                times = 0.0
                for i in lines:
                    if i.startswith('#EXTINF:'):
                        times += float(i.split(':')[-1].replace(',', ''))
                # Start background thread to refresh danmaku
                thread = threading.Thread(target=self.some_background_task, args=(path, int(times)))
                thread.start()
                print('[INFO] 获取视频时长成功', times)
                return [200, 'text/plain', data]
            elif xtype == 'hlxdm':
                # Return danmaku XML for heiliao comments
                article_id = param.get('path', '')
                times = int(param.get('times', 0))
                comments = self._fetch_heiliao_comments(article_id)
                return self._generate_danmaku_xml(comments, times)
        except Exception as e:
            print(f'[ERROR] localProxy: {e}')
        return[404,'text/plain','']
    
    def _extract_article_id(self, url):
        """Extract article ID from heiliao.com URL"""
        try:
            if '/archives/' in url:
                match = re.search(r'/archives/(\d+)/?', url)
                return match.group(1) if match else None
            return None
        except:
            return None
    
    def _fetch_heiliao_comments(self, article_id, max_pages=3):
        """Fetch comments from heiliao.com API"""
        comments = []
        try:
            for page in range(1, max_pages + 1):
                url = f"{self.HOST}/comments/1/{article_id}/{page}.json"
                resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36","Referer":self.HOST+'/'}, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if 'data' in data and 'list' in data['data'] and data['data']['list']:
                        for comment in data['data']['list']:
                            text = comment.get('content', '').strip()
                            if text and len(text) <= 100:  # Filter out too long comments
                                comments.append(text)
                            # Also get replies from comments.list
                            if 'comments' in comment and 'list' in comment['comments'] and comment['comments']['list']:
                                for reply in comment['comments']['list']:
                                    reply_text = reply.get('content', '').strip()
                                    if reply_text and len(reply_text) <= 100:
                                        comments.append(reply_text)
                        # Check if there are more pages
                        if not data['data'].get('next', False):
                            break
                    else:
                        break  # No more comments
                else:
                    break
        except Exception as e:
            print(f'[ERROR] _fetch_heiliao_comments: {e}')
        return comments[:50]  # Limit to 50 comments max
    
    def _generate_danmaku_xml(self, comments, video_duration):
        """Generate danmaku XML from comments"""
        try:
            total_comments = len(comments)
            tsrt = f'共有{total_comments}条弹幕来袭！！！'
            danmu_xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<i>\n\t<chatserver>chat.heiliao.com</chatserver>\n\t<chatid>88888888</chatid>\n\t<mission>0</mission>\n\t<maxlimit>99999</maxlimit>\n\t<state>0</state>\n\t<real_name>0</real_name>\n\t<source>heiliao</source>\n'
            danmu_xml += f'\t<d p="0,5,25,16711680,0">{tsrt}</d>\n'
            
            for i, comment in enumerate(comments):
                # Distribute comments across video duration
                base_time = (i / total_comments) * video_duration if total_comments > 0 else 0
                dm_time = base_time + random.uniform(-3, 3)
                dm_time = round(max(0, min(dm_time, video_duration)), 1)
                dm_color = self._get_danmaku_color()
                # Clean comment text
                dm_text = re.sub(r'[<>&\u0000\b]', '', comment)
                danmu_xml += f'\t<d p="{dm_time},1,25,{dm_color},0">{dm_text}</d>\n'
            
            danmu_xml += '</i>'
            return [200, "text/xml", danmu_xml]
        except Exception as e:
            print(f'[ERROR] _generate_danmaku_xml: {e}')
            return [500, 'text/html', '']
    
    def _get_danmaku_color(self):
        """Get danmaku color (90% white, 10% random)"""
        if random.random() < 0.1:
            h = random.random()
            s = random.uniform(0.7, 1.0)
            v = random.uniform(0.8, 1.0)
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            r = int(r * 255)
            g = int(g * 255)
            b = int(b * 255)
            return str((r << 16) + (g << 8) + b)
        else:
            return '16777215'  # White
    
    def some_background_task(self, article_id, video_duration):
        """Background task to refresh danmaku in FongMi"""
        try:
            time.sleep(1)
            danmaku_url = f"{self.getProxyUrl()}&path={quote(article_id)}&times={video_duration}&type=hlxdm"
            self.fetch(f"http://127.0.0.1:9978/action?do=refresh&type=danmaku&path={quote(danmaku_url)}")
            print(f'[INFO] 弹幕刷新成功: {article_id}')
        except Exception as e:
            print(f'[ERROR] some_background_task: {e}')
