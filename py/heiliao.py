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
    # hostresolver.py \u5728 source/ \u6839\uff08py/ \u7684\u4e0a\u7ea7\uff09\uff0c\u6309\u811a\u672c\u81ea\u8eab\u4f4d\u7f6e\u5b9a\u4f4d\uff0c\u4e0d\u4f9d\u8d56 cwd
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from hostresolver import ext_of, resolve_host
    except Exception:
        ext_of = None
        resolve_host = None

# explorer.py\uff08source \u6839\uff09\uff1a\u6c60\u5168\u6302\u65f6\u4ece\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\u6d3b\u57df\uff08\u4e0e hostresolver \u540c\u76ee\u5f55\uff09
try:
    from explorer import explore_hosts
except Exception:
    explore_hosts = None

_UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.96 Safari/537.36'

# ---- \u5c01\u9762\u56fe\u4ee3\u7406\u63d0\u901f\uff08\u5217\u8868\u52a0\u8f7d\u6162\u7684\u4e3b\u56e0\uff1a\u6bcf\u56fe\u4e00\u6b21 TLS \u63e1\u624b + \u65e0\u7f13\u5b58 + \u65e0\u6761\u4ef6\u89e3\u5bc6\uff09----
from collections import OrderedDict
_img_session=requests.Session()          # \u8fde\u63a5\u590d\u7528\uff1a\u540c\u56fe\u5e8a TLS keep-alive
_img_session.verify=False
try:                                      # \u8fde\u63a5\u6c60\uff08App \u4fa7\u5e76\u53d1\u62c9\u56fe\u65f6\u4e0d\u6392\u961f\uff09
    from requests.adapters import HTTPAdapter
    _ad=HTTPAdapter(pool_connections=4,pool_maxsize=12)
    _img_session.mount('https://',_ad); _img_session.mount('http://',_ad)
except Exception:pass
_img_cache=OrderedDict()                  # \u89e3\u5bc6\u7ed3\u679c LRU\uff1a\u6eda\u52a8\u56de\u770b/\u91cd\u590d\u5c01\u9762\u79d2\u51fa
_IMG_CACHE_MAX=60

def _img_fetch(url,referer):
    """\u53d6\u56fe+\u6309\u9700\u89e3\u5bc6+\u7f13\u5b58\uff0c\u8fd4\u56de (content_type, bytes)\u3002url \u9700\u5df2\u662f\u7edd\u5bf9\u5730\u5740\u3002"""
    if url in _img_cache:
        _img_cache.move_to_end(url)
        return _img_cache[url]
    h={'User-Agent':_UA,'Referer':referer}
    r=_img_session.get(url,headers=h,timeout=10)
    if r.status_code!=200:return[404,'text/plain',b'']
    raw=r.content
    ct='image/jpeg'
    if raw[:3]==b'\xff\xd8\xff':b=raw                 # \u88f8 JPEG \u514d\u89e3\u5bc6
    elif raw[:8]==b'\x89PNG\r\n\x1a\n':b,ct=raw,'image/png'
    elif raw[:4]==b'GIF8':b,ct=raw,'image/gif'
    else:                                             # CDN \u7ea7 AES \u52a0\u5bc6\u56fe
        b=AES.new(b'f5d965df75336270',AES.MODE_CBC,b'97b60394abc2fbe1').decrypt(raw)
        if b[:8]==b'\x89PNG\r\n\x1a\n':ct='image/png'
        elif b[:4]==b'GIF8':ct='image/gif'
    if b:
        _img_cache[url]=(ct,b)
        if len(_img_cache)>_IMG_CACHE_MAX:_img_cache.popitem(last=False)
    return[200,ct,b]

# \u5b98\u65b9\u5730\u5740\u53d1\u5e03\u9875\uff08\u7a33\u5b9a\uff0c\u7ad9\u70b9\u6362\u57df\u540d\u53ea\u52a8\u8fd9\u91cc\u6216 ext \u7684 publish@\uff09
PUBLISH_PAGE='https://wkcdhiqk.cc/'
# \u53d1\u5e03\u9875 JS \u6bcf\u6b21\u968f\u673a\u53d6\u82f1\u6587\u5355\u8bcd\u62fc\u6cdb\u5b50\u57df\uff08{word}.bqmnxlid.cc \u4e3b\u7ebf / {word}.xstcnjbf.cc \u5907\u7ebf\uff09\uff0c
# HTTP \u6293\u4e0d\u5230\u5177\u4f53\u57df\u540d\uff0c\u53ea\u80fd\u5185\u7f6e\u5019\u9009\u8bcd\u5b9e\u6d4b\u3002\u6cdb\u89e3\u6790\u4efb\u610f\u5355\u8bcd\u5747\u53ef\uff0c\u6362\u8bcd\u4e0d\u7528\u6539\u4ee3\u7801\u3002
BUILTIN_HOSTS=[
    'https://berry.bqmnxlid.cc/',    # 2026-09-07 \u5b9e\u6d4b 240KB \u5b8c\u6574\u7ad9
    'https://melon.bqmnxlid.cc/',
    'https://apple.bqmnxlid.cc/',
    'https://d2ley8cif9a5yt.cloudfront.net/',  # cloudfront \u56fa\u5b9a\u7ebf\u8def
    'https://kiwi.xstcnjbf.cc/',     # \u53d1\u5e03\u9875\u5907\u7ebf\u57df\u6c60\uff08\u90e8\u5206\u7f51\u7edc\u4e0d\u901a\uff0c\u4f5c\u672b\u4f4d\u515c\u5e95\uff09
    'https://lemon.xstcnjbf.cc/',
]

# \u5206\u7c7b\u540d\u5e7f\u544a/\u7ad9\u52a1\u9ed1\u540d\u5355\uff08\u53d1\u5e03\u9875\u5bfc\u822a\u63a8\u5e7f\u8bcd\uff0c\u5747\u4e3a\u4e2d\u6027\u8bcd\uff0c\u65e0\u9700 b64\uff09
AD_CAT_RE=re.compile('(?i)app|\u4e0b\u8f7d|qq|\u5fae\u4fe1|\u63a8\u7279|tg\u7fa4|\u5bfc\u822a|\u8054\u7cfb|\u5408\u4f5c|\u90ae\u7bb1|\u5173\u4e8e|\u5b58\u6863|\u6536\u85cf|forgot|\u767b\u9646|\u767b\u5f55')

class Spider(Spider):
    SELECTORS=['.post-card','.video-item','.video-list .item','.list-item','.post-item']
    def getName(self):return"\u9ed1\u6599\u4e0d\u6253\u70ca"
    def init(self,extend=""):
        # ext \u52a0\u56fa\uff08\u4e0e\u6bcf\u65e5\u5927\u8d5b\u540c\u6b3e\uff0cgitee \u7f51\u9875\u4e0a\u53ef\u76f4\u63a5\u6539\u672c\u6e90\u6761\u76ee\u7684 ext \u5b57\u6bb5\uff09\uff1a
        #   host@https://...     \u9501\u5b9a\u4e3b\u9875\uff08\u6700\u9ad8\u4f18\u5148\u7ea7\uff0c\u7ad9\u70b9\u5927\u6539\u65f6\u7ec8\u6781\u515c\u5e95\uff09
        #   publish@https://...  \u6362\u53d1\u5e03\u9875
        #   hosts@https://a,https://b  \u8ffd\u52a0\u65b0\u955c\u50cf\uff08\u6392\u5185\u7f6e\u524d\u4f18\u5148\u5b9e\u6d4b\uff09
        #   {"host":...,"publish":...,"hosts":[...],"proxies":{...}}  JSON \u5199\u6cd5\u4ea6\u53ef
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
        """\u52a8\u6001\u57df\u540d\u89e3\u6790 v2\uff08hostresolver\uff09\uff1aext \u9501\u5b9a \u2192 \u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe(b64\u58f3\u89e3\u7801+\u6cdb\u89e3\u6790\u57fa\u57df
        \u81ea\u52a8\u751f\u6210\u5019\u9009) \u2192 \u5185\u7f6e\u5019\u9009\u5e76\u884c\u5b9e\u6d4b \u2192 \u6210\u529f\u7f13\u5b5830\u5206\u949f\u3002\u5168\u90e8\u5931\u8d25\u8fd4\u56de ''\uff08\u63a5\u53e3\u5c42\u515c\u7a7a\uff0c
        \u4e0d\u56de\u9000\u6b7b\u57df\u9759\u9ed8\u7a7a\u8f6c\uff09\u3002"""
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
                if h:
                    return h
            except Exception:
                pass
        # \u7ec8\u6781\u515c\u5e95\uff1a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22\uff08\u8df3\u8f6c\u58f3/\u95e8\u6237/\u6cdb\u89e3\u6790\u8ddf\u968f + \u7ad9\u540d\u8eab\u4efd\u9a8c\u8bc1\uff09
        if explore_hosts:
            try:
                def _probe(u):
                    r=requests.get(u.rstrip('/')+'/',headers={'User-Agent':_UA},
                                   proxies=getattr(self,'proxies',{}) or {},timeout=8,verify=False)
                    return r.status_code==200 and '\u9ed1\u6599\u4e0d\u6253\u70ca' in (r.text or '')
                hs=explore_hosts(['hlbdy','\u9ed1\u6599\u4e0d\u6253\u70ca'],probe=_probe)
                if hs:
                    return hs[0]
            except Exception:
                pass
        return ''
    # \u515c\u5e95\u5206\u7c7b\uff082026-09-07 \u6539\u7248\u540e\u5bfc\u822a\u5b9e\u6d4b\uff0cb64 \u5b58\u50a8\u9632\u6258\u7ba1\u5e73\u53f0\u5185\u5bb9\u626b\u63cf\u8bef\u5224\uff09\u2014\u2014
    # \u4ec5\u5f53\u9996\u9875\u5b9e\u65f6\u6293\u53d6\u5931\u8d25\u65f6\u4f7f\u7528\uff0c\u6b63\u5e38\u60c5\u51b5\u5206\u7c7b\u4e00\u5f8b\u4ece\u7f51\u7ad9\u5b9e\u65f6\u83b7\u53d6
    CATE_MANUAL_B64='IHsi5LuK5pel55yL5paZIjoiMjRoY2ciLCLmr4/ml6XlpKfotZsiOiJtcmRzIiwiQUnnn63liaciOiJzd2RqIiwi54Ot6Zeo5ZCD55OcIjoicmd0aiIsIuavj+aXpeeDreeTnCI6Im1ycmciLCLpu5HmlpnlpKfkuosiOiJobGRhIiwi5Y+N5beu5aWz56WeIjoiZmNucyIsIuWtpumZoueDreeTnCI6Inh5cmciLCLnvZHnuqLlkIPnk5wiOiJ3aGhsIiwi6buR5paZ5p2C6LCIIjoiaGx6dCIsIuaYjuaYn+WQg+eTnCI6Im14YmciLCLlrpjlnLrnp5jpl7siOiJnY213Iiwi56aB5pKt5Yqo5ryrIjoibXJzdCIsIuaSuOWPi+eci+eJhyI6Imx5ZHQiLCLmtbfop5LkubHkvKYiOiJsbHNxIiwiYXbop6Por7QiOiJhdmpzIiwi5o6i6Iqx5aSn5YWoIjoidGhkcSIsIue9kem7hOS4k+i+kSI6IndoemoiLCLljp/liJvmipXnqL8iOiJxZ3pxIiwi5oCn54ix5oqA5benIjoid3l4cyIsIlBNVua3t+WJqiI6InBtdiIsIuWBt+aLjeebl+aRhCI6ImNoamxiIiwi5LiW55WM5p2v55CD5ZGY6buR5paZIjoic2piLWhsIiwi5LiW55WM5p2v5aSq5aSq5ZuiIjoic2piLXR0dCIsIuS4lueVjOadr+eDreaQnCI6InNqYi1ycyIsIuS4lueVjOadr+WNmuW9qeS4k+WMuiI6InNqYi1iYyIsIueQg+i/t+eOsOWcuiI6InNqYi1xbSJ9'
    def homeContent(self,filter):
        # \u5206\u7c7b\u5b9e\u65f6\u83b7\u53d6\uff08\u4e0e\u6bcf\u65e5\u5927\u8d5b\u540c\u6b3e\uff09\uff1a\u5168\u9875\u626b /category/{slug}/ \u94fe\u63a5\uff0c\u7ad9\u65b9\u52a0\u5206\u7c7b/\u6539\u540d\u81ea\u52a8\u8ddf\u968f
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
        # 2026-09-07 \u6539\u7248\u540e\u5206\u7c7b\u8def\u7531\u4e3a /category/{slug}/\uff0c\u5206\u9875\u4e3a /category/{slug}/{pg}/
        # tid \u517c\u5bb9\u4e24\u79cd\u5f62\u6001\uff1a\u5b9e\u65f6\u626b\u63cf('/category/slug/'\u5168\u8def\u5f84) \u4e0e b64\u515c\u5e95\u8868(\u88f8slug)
        if not str(tid).startswith('/'):
            tid=f'/category/{tid}'
        url=f'{self.HOST}{tid}/'if int(pg)==1 else f'{self.HOST}{tid}/{pg}/'
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
        # 2026-09-08 \u6539\u7248: \u65b0\u56fe\u5e8a pic.hdhwqx.cn\uff08/hc237/ \u8def\u5f84\uff09\u540c\u4e3a CDN \u7ea7 AES \u52a0\u5bc6\u56fe\uff0c
        # \u4e0e\u65e7\u56fe\u5e8a\u540c key\uff1bgeneric \u6309 pic.* \u57df\u540d + /hc237/ \u8def\u5f84\u515c\u4f4f\u540e\u7eed\u6362\u57df
        u=(url or'').lower()
        host=u.split('/')[2]if u.startswith('http')and u.count('/')>2 else''
        return any(x in u for x in['pic.gylhaa.cn','new.slfpld.cn','pic.hdhwqx.cn','/upload_01/','/upload/','/hc237/'])or host.startswith('pic.')
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
        u=''if img_node is None else(img_node.attr('z-image-loader-url')or img_node.attr('src')or img_node.attr('data-src')or'')
        enc=''if img_node is None else self._extract_img_from_onload(img_node)
        t=enc or u
        return f"{self.getProxyUrl()}&url={self.e64(t)}&type=hlimg"if t and(enc or self._should_decrypt(t))else self._abs(t)
    def _parse_items(self,root):
        vids=[]
        for sel in self.SELECTORS:
            for it in root(sel).items():
                if 'ad-item' in (it.attr('class') or ''):continue
                if it.find('.corner-badge--ad'):continue  # 2026-09-08 \u6539\u7248\u5e7f\u544a\u5361\uff08\u89d2\u6807"\u5e7f\u544a"\uff09
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
        if' - \u9ed1\u6599\u7f51'in title:title=title.replace(' - \u9ed1\u6599\u7f51','')
        if' - \u9ed1\u6599\u4e0d\u6253\u70ca'in title:title=title.replace(' - \u9ed1\u6599\u4e0d\u6253\u70ca','')
        pic=''
        # 2026-09-08: \u8be6\u60c5\u9875 og:image=\u4e3b\u9898\u793e\u4ea4\u56fe\u6807\u3001\u9875\u9762\u5185 img \u5168\u662f\u9876\u90e8\u5e7f\u544a banner/\u63a8\u8350\u4f4d\u7f29\u7565\u56fe\uff0c
        # \u5747\u4e0d\u9002\u5408\u5f53\u5c01\u9762\uff0c\u5b81\u7a7a\u52ff\u9519\uff08\u5217\u8868\u8fdb\u8be6\u60c5\u65f6 App \u4fa7\u901a\u5e38\u6cbf\u7528\u5217\u8868\u5c01\u9762\uff09
        detail=''
        if root_text:
            detail=root_text('meta[name="description"]').attr('content')or''
            if not detail:detail=root_text('.content').text()[:200]
        play_from,play_url=[],[]
        article_id = self._extract_article_id(tid)
        if root_content:
            # 2026-09-08: \u5206\u96c6\u5728 .dplayer \u7684 data-config \u5c5e\u6027\uff08\u65e7\u7248\u8bfb config \u5df2\u5931\u6548\uff09\uff0c
            # \u5e7f\u544a\u8d34\u7247\u89c6\u9891\u53ea\u5b58\u5728\u4e8e\u9875\u9762\u5e7f\u544a JSON\uff08advert_player_*\uff09\uff0c\u4e0d\u5728 dplayer \u91cc\uff0c
            # \u56e0\u6b64\u53ea\u8ba4 dplayer \u5206\u96c6\u5373\u53ef\u5929\u7136\u514d\u5e7f\u544a\uff1b\u4e0d\u518d\u7528\u5bbd\u677e js \u6b63\u5219\u515c\u5e95\uff08\u4f1a\u628a\u5e7f\u544a m3u8 \u635e\u8fdb\u5206\u96c6\uff09
            parts=[]
            for p in root_content('.dplayer').items():
                c=p.attr('data-config')or p.attr('config')
                if not c:continue
                try:s=(c.replace('&quot;','"').replace('&#34;','"').replace('&amp;','&').replace('&#38;','&').replace('&lt;','<').replace('&#60;','<').replace('&gt;','>').replace('&#62;','>'));u=(json.loads(s).get('video',{})or{}).get('url','')
                except:m=re.search(r'"url"\s*:\s*"([^"]+)"',c);u=m.group(1)if m else''
                if not u:continue
                u=u.replace('\\/','/');u=self._abs(u)
                idx=p.attr('data-video_index')
                try:idx=int(idx)
                except:idx=len(parts)
                parts.append((idx,u))
            parts.sort(key=lambda x:x[0])
            for idx,u in parts:
                if article_id:
                    play_from.append(f'视频{len(play_from)+1}');play_url.append(f"{article_id}_dm_{u}")
                else:
                    play_from.append(f'视频{len(play_from)+1}');play_url.append(u)
        if not play_url:
            # \u515c\u5e95\u4ec5\u9650 hls \u4e13\u5c5e\u5f62\u6001\u7684\u88f8 m3u8\uff08\u8d34\u7247\u5e7f\u544a\u7d20\u6750 host \u4e0d\u540c\uff0c\u4e0d\u4f1a\u547d\u4e2d hls. \u524d\u7f00\u7279\u5f81\uff09
            for pat in[r'https://hls\.[^"\']+\.m3u8[^"\']*',r'https://[^"\']+\.m3u8\?auth_key=[^"\']+',r'//hls\.[^"\']+\.m3u8[^"\']*']:
                for u in re.findall(pat,html_text):
                    u=self._abs(u)
                    if article_id:
                        play_from.append(f'视频{len(play_from)+1}');play_url.append(f"{article_id}_dm_{u}")
                    else:
                        play_from.append(f'视频{len(play_from)+1}');play_url.append(u)
                    if len(play_url)>=3:break
                if play_url:break
        if not play_url:
            article_id = self._extract_article_id(tid)
            example_url = "https://hls.obmoti.cn/videos5/b9699667fbbffcd464f8874395b91c81/b9699667fbbffcd464f8874395b91c81.m3u8?auth_key=1760372539-68ed273b94e7a-0-3a53bc0df110c5f149b7d374122ef1ed&v=2"
            if article_id:
                play_from.append('\u793a\u4f8b\u89c6\u9891');play_url.append(f"{article_id}_dm_{example_url}")
            else:
                play_from.append('\u793a\u4f8b\u89c6\u9891');play_url.append(example_url)
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
                return _img_fetch(url,self.HOST+'/')
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
                print('[INFO] \u83b7\u53d6\u89c6\u9891\u65f6\u957f\u6210\u529f', times)
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
