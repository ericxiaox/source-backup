# coding=utf-8
import json, ssl, re, base64, random, urllib.parse, time, hashlib
from base.spider import Spider
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class Spider(Spider):
    def getName(self): return "51\u77ed\u5267"

    def init(self, extend=""):
        self.publish = "https://51dj20.com/"
        self.ua = "Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 Chrome/143.0 Mobile Safari/537.36"
        self.headers = {"User-Agent": self.ua, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "zh-CN,zh;q=0.9", "Referer": self.publish}
        self.session = requests.Session()
        self.media_key = b"f5d965df75336270"
        self.media_iv = b"97b60394abc2fbe1"
        self.api_host = "https://api.51dj1.com"
        self.api_key = b"2acf7e91e9864673"
        self.api_iv = b"1c29882d3ddfcfd6"
        try: ssl._create_default_https_context = ssl._create_unverified_context
        except Exception: pass
        self.host = "https://ceiling.sysrycady.com/"
        self._resolve_domain()
        self.image_map = {}; self.image_id_map = {}
        try:
            with open("/storage/emulated/0/\u5f71\u89c6/AI/51\u77ed\u5267/51\u77ed\u5267\u56fe\u7247\u6620\u5c04.json", "r", encoding="utf-8") as f: raw = f.read()
            for x in self._walk(self._payload(raw), ["video_id", "title"]):
                title = str(x.get("title") or ""); cover = self._pic(x.get("cover") or x.get("cover_img") or x.get("cover_image"))
                if title and cover: self.image_map[title] = cover; self.image_id_map[str(x.get("video_id"))] = cover
            for title, cover in re.findall(r'\"title\"\s*:\s*\"([^\"]+)\"[\s\S]{0,300}?\"cover\"\s*:\s*\"([^\"]+)\"', raw):
                self.image_map.setdefault(title, self._pic(cover))
            print(f"[51短剧] 图片映射: 标题{len(self.image_map)}条, ID{len(self.image_id_map)}条")
        except Exception as e: print(f"[51短剧] 图片映射读取失败: {e}")
        self.classes = [{"type_id":"actor","type_name":"\u6f14\u5458"},{"type_id":"drama","type_name":"\u5267\u96c6"},{"type_id":"drama_week","type_name":"\u5267\u96c6\u5468\u699c"},{"type_id":"drama_month","type_name":"\u5267\u96c6\u6708\u699c"},{"type_id":"aisd","type_name":"AI\u6210\u4eba\u77ed\u5267"}]
        self.filters = {"actor":[{"key":"sort","name":"\u6f14\u5458","value":[{"n":"\u70ed\u95e8","v":"hot"},{"n":"\u7537\u6f14\u5458","v":"2"},{"n":"\u5973\u6f14\u5458","v":"1"}]}],"drama":[{"key":"theme","name":"\u4e3b\u9898","value":[{"n":"\u5168\u90e8","v":"0"},{"n":"\u6210\u4eba","v":"1"},{"n":"AI\u6f2b\u5267","v":"46"},{"n":"51\u539f\u521b","v":"47"},{"n":"AI\u9b54\u6539\u77ed\u5267","v":"51"},{"n":"\u81f4\u5bcc","v":"63"},{"n":"\u4fee\u4ed9","v":"59"},{"n":"\u53a8\u795e","v":"60"},{"n":"\u8bfb\u5fc3","v":"61"},{"n":"\u4eca\u53e4\u8054\u901a","v":"62"},{"n":"\u5973\u6027\u6210\u957f","v":"4"},{"n":"\u9274\u5b9d","v":"64"},{"n":"\u4eb2\u60c5","v":"65"},{"n":"\u672b\u4e16","v":"66"},{"n":"\u6b66\u4fa0","v":"67"},{"n":"\u840c\u5ba0","v":"68"},{"n":"\u840c\u5b9d","v":"69"},{"n":"\u771f\u5047\u5343\u91d1","v":"70"},{"n":"\u9752\u6625","v":"18"},{"n":"\u73b0\u8a00","v":"3"},{"n":"\u5947\u5e7b","v":"5"},{"n":"\u6218\u795e","v":"6"},{"n":"\u5bab\u6597","v":"7"},{"n":"\u53e4\u8a00","v":"8"},{"n":"\u7384\u5e7b","v":"9"},{"n":"\u8111\u6d1e","v":"10"},{"n":"\u6743\u8c0b","v":"11"},{"n":"\u5e74\u4ee3\u7231\u60c5","v":"12"},{"n":"\u79cd\u7530","v":"15"},{"n":"\u60ac\u7591","v":"13"},{"n":"\u6c11\u56fd\u7231\u60c5","v":"16"},{"n":"\u8f7b\u677e\u559c\u5267","v":"17"},{"n":"\u5fd7\u602a","v":"19"},{"n":"\u8d85\u80fd","v":"58"},{"n":"\u5f3a\u5236","v":"57"},{"n":"\u5f02\u4e16\u754c","v":"56"},{"n":"NTR","v":"55"},{"n":"\u7eaf\u7231","v":"71"},{"n":"\u7fa4\u50cf","v":"78"}]},{"key":"setting","name":"\u8bbe\u5b9a","value":[{"n":"\u5168\u90e8","v":"0"},{"n":"\u540e\u5bab","v":"20"},{"n":"NTR","v":"55"},{"n":"\u53cd\u5dee","v":"38"},{"n":"\u6deb\u59bb","v":"74"},{"n":"\u5c11\u5987","v":"73"},{"n":"\u5927\u7537\u4e3b","v":"20"},{"n":"\u5927\u5973\u4e3b","v":"7"},{"n":"\u7cfb\u7edf","v":"29"},{"n":"\u91cd\u751f","v":"27"},{"n":"\u7a7f\u8d8a","v":"28"},{"n":"\u795e\u8c6a","v":"23"},{"n":"\u6253\u8138\u8650\u6e23","v":"25"},{"n":"\u9a6c\u7532","v":"26"},{"n":"\u8ffd\u59bb/\u592b\u706b\u846c\u573a","v":"72"},{"n":"\u4e92\u76f8\u6551\u8d4e","v":"22"},{"n":"\u751c\u5ba0","v":"88"},{"n":"\u53cc\u5411\u5954\u8d74","v":"48"},{"n":"\u4f20\u627f\u89c9\u9192","v":"38"},{"n":"\u5bb6\u957f\u91cc\u77ed","v":"37"},{"n":"\u7834\u955c\u91cd\u5706","v":"36"},{"n":"\u8650\u604b","v":"35"},{"n":"\u9738\u603b","v":"34"},{"n":"\u5f3a\u8005\u56de\u5f52","v":"33"},{"n":"\u5148\u5a5a\u540e\u7231","v":"32"},{"n":"\u5c0f\u4eba\u7269","v":"31"},{"n":"\u9006\u88ad","v":"39"},{"n":"\u4f26\u7406","v":"92"},{"n":"\u51fa\u8f68","v":"98"},{"n":"\u5077\u60c5","v":"97"},{"n":"\u5fa1\u59d0","v":"89"},{"n":"\u841d\u8389","v":"88"},{"n":"\u66ff\u5ac1","v":"82"},{"n":"\u56e2\u5ba0","v":"81"},{"n":"\u65e0CP","v":"80"}]},{"key":"background","name":"\u80cc\u666f","value":[{"n":"\u5168\u90e8","v":"0"},{"n":"\u6821\u56ed","v":"54"},{"n":"\u67b6\u7a7a","v":"53"},{"n":"\u6c11\u56fd","v":"52"},{"n":"\u804c\u573a","v":"45"},{"n":"\u5e74\u4ee3","v":"44"},{"n":"\u73b0\u4ee3","v":"40"},{"n":"\u90fd\u5e02","v":"41"},{"n":"\u53e4\u4ee3","v":"42"},{"n":"\u4e61\u6751","v":"43"}]},{"key":"audience","name":"\u53d7\u4f17","value":[{"n":"\u5168\u90e8","v":"0"},{"n":"\u7537","v":"1"},{"n":"\u5973","v":"2"}]},{"key":"time","name":"\u65f6\u95f4","value":[{"n":"\u5168\u90e8","v":"0"},{"n":"7\u5929\u5185","v":"7"},{"n":"14\u5929\u5185","v":"14"},{"n":"30\u5929\u5185","v":"30"},{"n":"90\u5929\u5185","v":"90"}]},{"key":"recommend","name":"\u63a8\u8350","value":[{"n":"\u9ed8\u8ba4","v":"0"},{"n":"\u6700\u65b0","v":"time"},{"n":"\u6700\u70ed","v":"hits"},{"n":"\u539f\u521b","v":"original"}]}]}

        self.filters["actor"][0]["value"] += [{"n":"\u65b0\u4eba\u699c","v":"new"},{"n":"\u70ed\u5ea6\u699c","v":"hot"},{"n":"\u63a8\u8350\u699c","v":"recommend"}]

    def _resolve_domain(self):
        try:
            h = self.session.get(self.publish, headers=self.headers, timeout=12, verify=False).text
            m = re.search(r'<a[^>]+href=["\'](https?://[^"\']+)', h, re.I)
            if not m: return
            h = self.session.get(m.group(1), headers=self.headers, timeout=12, verify=False).text
            m = re.search(r'Base64\.decode\(["\']([^"\']+)["\']\)', h, re.I)
            if not m: return
            decoded = base64.b64decode(m.group(1)).decode("utf-8", "ignore")
            m = re.search(r"words\.random\(\)\s*\+\s*[\"']([^\"']+)[\"']", decoded, re.I)
            if not m: return
            suffix = m.group(1).strip()
            prefix = "".join(random.choice("abcdefghjkmnpqrstuvwxy23456789") for _ in range(5))
            self.host = "https://" + prefix + suffix.lstrip("/")
            if not self.host.endswith("/"): self.host += "/"
            self.headers["Referer"] = self.host
            print(f"[51短剧] 域名: {self.host}")
        except Exception as e: print(f"[51短剧] 域名解析失败: {e}")

    def _req(self, url):
        try:
            r = self.session.get(url, headers=self.headers, timeout=20, verify=False)
            return r.text if r.status_code == 200 else ""
        except Exception as e:
            print(f"[51短剧] 请求失败: {url} {e}")
            return ""

    def _payload(self, html):
        m = re.search(r'<script[^>]+id=["\']__NUXT_DATA__["\'][^>]*>(.*?)</script>', html, re.S | re.I)
        if not m: return None
        try:
            raw=json.loads(m.group(1).strip()); memo={}
            def get(i):
                if not isinstance(i,int) or i<0 or i>=len(raw): return i
                if i in memo: return memo[i]
                x=raw[i]
                if isinstance(x,list):
                    out=[]; memo[i]=out
                    for v in x: out.append(get(v))
                    return out
                if isinstance(x,dict):
                    out={}; memo[i]=out
                    for k,v in x.items(): out[k]=get(v)
                    return out
                memo[i]=x; return x
            return get(0)
        except Exception as e:
            print(f"[51短剧] Nuxt解析失败: {e}")
            return None

    def _walk(self, obj, keys):
        out, seen = [], set()
        def go(x):
            if isinstance(x, dict):
                if all(k in x for k in keys):
                    mark = str(x.get(keys[0])) + str(x.get(keys[1]))
                    if mark not in seen: seen.add(mark); out.append(x)
                for v in x.values(): go(v)
            elif isinstance(x, list):
                for v in x: go(v)
        go(obj); return out

    def _pic(self, x):
        if not isinstance(x, str): return ""
        url=x.replace("\\u002F", "/").replace("\\/", "/").replace("&amp;", "&").strip()
        if not url: return ""
        if url.startswith("//"): url = "https:" + url
        elif not url.startswith("http"): url = self._fix(url)
        try: return self.getProxyUrl()+"&url="+urllib.parse.quote(self.e64(url), safe="")+"&type=img"
        except Exception: return url

    def _media(self, x):
        if not isinstance(x, str): return ""
        url=x.replace("\\u002F", "/").replace("\\/", "/").replace("&amp;", "&").strip()
        if not url: return ""
        if url.startswith("//"): return "https:" + url
        if url.startswith("http"): return url
        return self._fix(url)

    def _num(self, n):
        try:
            n=int(float(str(n).replace(",","")))
            return str(round(n/10000,1)).rstrip(".0")+"W" if n>=10000 else str(n)
        except Exception: return ""

    def _xml(self, s):
        s = str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        q = chr(34)
        return s.replace(q, "\x26quot;")


    def _api_decrypt(self, obj):
        try:
            if isinstance(obj, str): obj=json.loads(obj)
            data=str(obj.get("data") or "").replace(" ","+")
            if not data: return obj if isinstance(obj, dict) else {}
            raw=base64.b64decode(data)
            txt=unpad(AES.new(self.api_key,AES.MODE_CBC,self.api_iv).decrypt(raw), AES.block_size).decode("utf-8","ignore")
            return json.loads(txt)
        except Exception as e:
            print(f"[51短剧] API解密失败: {e}")
            return {}

    def _api_post(self, path, data):
        try:
            hdr=dict(self.headers)
            hdr.update({"Accept":"application/json, text/plain, */*","Content-Type":"application/x-www-form-urlencoded","Origin":self.host.rstrip("/"),"Referer":self.host})
            body={"bundleId":"com.pwa.mater","version":"1.3.2","oauth_id":"7d05538c4b8a5e74e82f93c0dab0163c","oauth_type":"web","language":"zh","via":"pwa","token":"","trace_id":"7d05538c4b8a5e74e82f93c0dab0163c"}
            body.update(data or {})
            r=self.session.post(self.api_host.rstrip("/") + path, data=body, headers=hdr, timeout=15, verify=False)
            return self._api_decrypt(r.json()) if r.status_code == 200 else {}
        except Exception as e:
            print(f"[51短剧] API请求失败: {path} {e}")
            return {}

    def _danmaku_url(self, url):
        try:
            sid=(re.search(r"(?:id|video_id|playlet_id)=(\d+)", str(url)) or [None,""])[1]
            eid=(re.search(r"episode_id=(\d+)", str(url)) or [None,""])[1]
            if not sid or not eid: return ""
            return self.getProxyUrl()+"&type=danmu&vid="+urllib.parse.quote(str(sid))+"&eid="+urllib.parse.quote(str(eid))
        except Exception: return ""

    def _danmaku_xml(self, vid, eid):
        rows=[]
        data=self._api_post("/api/playlet/danmakuList", {"video_id":vid,"playlet_id":vid,"id":vid,"episode_id":eid,"page":1,"limit":500})
        try: rows=((data.get("data") or {}).get("list") or []) if isinstance(data, dict) else []
        except Exception: rows=[]
        ts=int(time.time())
        lines=['<?xml version="1.0" encoding="UTF-8"?><i>','<chatserver>51\u77ed\u5267</chatserver>','<chatid>'+self._xml(str(vid)+"_"+str(eid))+'</chatid>','<mission>0</mission>','<maxlimit>'+str(len(rows))+'</maxlimit>','<state>0</state>','<real_name>0</real_name>','<source>51dj</source>']
        n=0
        for x in rows:
            try:
                text=str(x.get("text") or x.get("content") or "")
                if not text: continue
                tm=max(0,float(x.get("time") or 0)); mode=int(x.get("mode") or 0)
                dm=5 if mode == 1 else (4 if mode == 2 else 1)
                c=str(x.get("color") or "#FFFFFF").strip().lstrip("#")[:6]
                color=int(c,16) if re.match(r"^[0-9a-fA-F]{6}$", c) else 16777215
                lines.append('<d p="%.3f,%d,25,%d,%d,0,51dj,%d">%s</d>' % (tm,dm,color,ts,n,self._xml(text)))
                n+=1
            except Exception: continue
        lines.append('</i>')
        print(f"[51短剧] 弹幕 {vid}/{eid}: {n} 条")
        return "\n".join(lines)

    def _vod(self, x, actor=False):
        title = str(x.get("title") or x.get("name") or x.get("video_title") or x.get("drama_name") or "")
        vid = x.get("actor_id") if actor else (x.get("video_id") or x.get("playlet_id") or x.get("id") or x.get("actor_id"))
        if not title or vid is None: return None
        if actor and x.get("actor_id") is not None:
            aid=str(x.get("actor_id")); pic=self._pic(x.get("avatar"))
            works=self._num(x.get("works")); fans=self._num(x.get("fans_count")); plays=self._num(x.get("play_count"))
            remark=("\u4f5c\u54c1"+works if works else "\u6f14\u5458\u4f5c\u54c1") + ((" \u00b7 \u7c89\u4e1d"+fans) if fans else "") + ((" \u00b7 \u64ad\u653e"+plays) if plays else "")
            return {"vod_id":"actor_detail_"+aid,"vod_name":title,"vod_pic":pic,"vod_remarks":remark,"vod_tag":"folder","vod_play_from":"","vod_play_url":""}
        eid = x.get("episode_id") or ""
        # \u8be6\u60c5\u9875\u7528\u7ad9\u70b9\u771f\u5b9e\u8def\u5f84 drama-detail/{video_id}/\uff08\u65e7\u5199\u6cd5 drama-play?id=..&episode_id=.. 
        # \u670d\u52a1\u7aef\u4e0d\u8ba4\uff0c\u9875\u5185 payload \u4f1a\u9000\u5316\u6210\u522b\u90e8\u5267 \u2014\u2014 \u8fd9\u6b63\u662f"\u70b9\u4efb\u4f55\u4e00\u96c6\u90fd\u662f\u7b2c\u4e00\u96c6"\u7684\u6839\u56e0\uff09
        play_id = self.host + "drama-detail/" + str(vid) + "/"
        pic=self.image_id_map.get(str(vid)) or self.image_map.get(title) or self._pic(x.get("cover") or x.get("cover_img") or x.get("cover_image") or x.get("image") or x.get("poster") or x.get("thumb"))
        plays=str(x.get("play_count_text") or "") or self._num(x.get("play_count")); chase=self._num(x.get("chase_count")); status=str(x.get("serialize_status_text") or ("\u64ad\u653e" if eid else ""))
        remark=(("\u64ad\u653e"+plays) if plays else "") + ((" \u00b7 \u8ffd\u5267"+chase) if chase else "")
        return {"vod_id":play_id,"vod_name":title,"vod_pic":pic,"vod_remarks":remark or status,"vod_tag":"video","vod_play_id":str(eid)}

    def _meta(self, html):
        data = self._payload(html)
        for x in self._walk(data, ["total","page","limit"]):
            total = int(x.get("total") or 0); limit = int(x.get("limit") or 20)
            return total, limit, max(1, (total + limit - 1) // limit)
        for x in self._walk(data, ["total","page"]):
            total = int(x.get("total") or 0); limit = 30
            return total, limit, max(1, (total + limit - 1) // limit)
        return 0, 20, 1

    def _load_filters(self):
        if getattr(self, "_filters_loaded", False): return
        self._filters_loaded = True
        try:
            data = self._payload(self._req(self.host + "rank-drama/week/"))
            found=[]
            def go(x):
                if isinstance(x, dict):
                    if isinstance(x.get("video_filter"), dict): found.append(x)
                    for v in x.values(): go(v)
                elif isinstance(x, list):
                    for v in x: go(v)
            go(data)
            opt = found[0] if found else {}
            vf = opt.get("video_filter") or {}
            fs=[]
            for k in ("theme","setting","background","audience","time","recommend"):
                b = vf.get(k)
                if not isinstance(b, dict): continue
                vals=[{"n":"\u5168\u90e8","v":"0"}]; seen={"0"}
                for it in b.get("list") or []:
                    v=str(it.get("value","")); n=str(it.get("name",""))
                    if v and n and v not in seen: seen.add(v); vals.append({"n":n,"v":v})
                fs.append({"key":str(b.get("parameter") or k),"name":str(b.get("title") or k),"value":vals})
            if fs: self.filters["drama"] = fs
            af = opt.get("actor_filter")
            if isinstance(af, list):
                vals=[{"n":str(i.get("name")),"v":str(i.get("value"))} for i in af if i.get("name") and i.get("value") is not None]
                if vals: self.filters["actor"] = [{"key":"sort","name":"\u6f14\u5458","value":vals}]
            print(f"[51短剧] 动态筛选: 剧集{len(self.filters.get('drama', []))}组")
        except Exception as e: print(f"[51短剧] 动态筛选失败: {e}")

    def _page(self, html, actor=False):
        data = self._payload(html); keys = ["actor_id","name"] if actor else ["video_id","title"]
        if not actor:
            html_pics=re.findall(r'(?:data-original|data-src|src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)', html, re.I)
        else: html_pics=[]
        arr = self._walk(data, keys) if data else []; result=[]; seen=set()
        if actor:
            links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>[\s\S]{0,300}?</a>', html, re.I)
            actor_links = [u for u in links if ("/actor" in u or "actor_id" in u) and "explore-actor" not in u and "rank-actor" not in u]
        else: actor_links=[]
        for i,x in enumerate(arr):
            if actor:
                v=self._vod(x, True)
                if v and not v.get("vod_id"): v["vod_id"] = self._fix(actor_links[i]) if i < len(actor_links) else v.get("vod_id","")
            else:
                v=self._vod(x, False)
                if v and not v.get("vod_pic") and i < len(html_pics): v["vod_pic"] = self._fix(html_pics[i])
            if v and v["vod_id"] not in seen: seen.add(v["vod_id"]); result.append(v)
        return result

    def _fix(self, url):
        url=str(url or "").replace("\\u002F","/").replace("\\/","/")
        if url.startswith("http"): return url
        return self.host.rstrip("/") + "/" + url.lstrip("/")

    def _sid(self, vid):
        """\u4ece\u5404\u79cd\u5f62\u6001\u7684 id \u91cc\u53d6\u51fa\u5267\u7684 video_id\uff08\u7eaf\u6570\u5b57\uff09\u3002
        \u517c\u5bb9\uff1a12878 / drama-detail/12878/ / play/12878/2/ / drama-play?id=12878&episode_id=811467"""
        s = str(vid or "").strip()
        m = re.search(r"[?&](?:id|video_id)=(\d+)", s)
        if m: return m.group(1)
        m = re.search(r"/(?:drama-detail|drama-play|drama|play|video)/(\d+)", s)
        if m: return m.group(1)
        m = re.search(r"(\d+)", s)
        return m.group(1) if m else s

    def _cget(self, sid, field):
        c=self.__dict__.setdefault("_cache", {}).get(str(sid)) or {}
        if c.get(field) is not None and time.time()-c.get("t", 0) < 300: return c[field]
        return None

    def _cput(self, sid, field, val):
        c=self.__dict__.setdefault("_cache", {}).setdefault(str(sid), {})
        c["t"]=time.time(); c[field]=val

    def _episode_rows(self, vid):
        """\u5267\u96c6\u6743\u5a01\u987a\u5e8f\uff1adrama-detail \u9875\u7684 episodes\uff08id \u5373 episode_id\uff0c\u5e26 sort / \u89e3\u9501\u6807\u8bb0\uff09\u3002"""
        sid=self._sid(vid)
        hit=self._cget(sid, "eps")
        if hit is not None: return hit
        eps=[]
        try:
            data=self._payload(self._req(self.host+"drama-detail/"+sid+"/"))
            candidates=self._walk(data,["video_id","title"]) or self._walk(data,["video_id","video_title"])
            for row in candidates:
                if str(row.get("video_id")) == sid and isinstance(row.get("episodes"), list):
                    for e in row.get("episodes"):
                        if isinstance(e, dict) and e.get("id") is not None:
                            eps.append({"id":e.get("id"),"sort":e.get("sort") or 0,
                                        "title":e.get("title") or (str(row.get("title"))+"-\u7b2c"+str(e.get("sort"))+"\u96c6"),
                                        "locked": not bool(e.get("web_unlocked", True)),
                                        "duration":e.get("duration") or 0})
                    break
            eps=sorted(eps, key=lambda x:int(x.get("sort") or 0))
        except Exception as e: print(f"[51短剧] 剧集列表失败: {e}")
        if eps: self._cput(sid, "eps", eps)
        return eps

    def _url_map(self, sid):
        """\u64ad\u653e\u9875 /play/{sid}/1/ \u7684 payload \u4e00\u6b21\u5e26\u5168\u5267\u96c6\u8282\u70b9\uff1a
        \u5df2\u89e3\u9501\u96c6\u6709 video_url\uff0c\u672a\u89e3\u9501\u96c6\uff08web_unlocked=false\uff09\u6ca1\u6709\u3002\u8fd4\u56de {episode_id: \u76f4\u94fe}\u3002"""
        sid=str(sid or "").strip()
        hit=self._cget(sid, "umap")
        if hit is not None: return hit
        out={}
        try:
            data=self._payload(self._req(self.host+"play/"+sid+"/1/"))
            def go(x):
                if isinstance(x, dict):
                    if x.get("episode_title") is not None and x.get("id") is not None:
                        u=self._media(x.get("video_url"))
                        if u: out.setdefault(str(x.get("id")), u)
                    for v in x.values(): go(v)
                elif isinstance(x, list):
                    for v in x: go(v)
            go(data)
        except Exception as e: print(f"[51短剧] 播放页直链失败: {e}")
        if out: self._cput(sid, "umap", out)
        return out

    def _url(self, cid, pg, ext=None):
        pg=max(1,int(pg)); e=ext if isinstance(ext,dict) else {}
        if cid == "actor":
            sort=str(e.get("sort") or "popular")
            if sort == "1": base=self.host + "explore-actor/1/"
            elif sort == "2": base=self.host + "explore-actor/2/"
            elif sort in ("new","hot","recommend"): base=self.host + "rank-actor/" + sort + "/"
            else: base=self.host + "rank-actor/"
            return base if pg == 1 else base + "page/" + str(pg) + "/"
        if cid == "drama":
            vals=[str(e.get(k,0) or 0) for k in ("theme","setting","background","audience","time","recommend")]
            base=self.host + "explore-drama/" + "-".join(vals) + "/"
            return base if pg == 1 else base + "page/" + str(pg) + "/"
        if cid == "drama_week":
            base=self.host + "rank-drama/week/"; return base if pg == 1 else base + "page/" + str(pg) + "/"
        if cid == "drama_month":
            base=self.host + "rank-drama/month/"; return base if pg == 1 else base + "page/" + str(pg) + "/"
        if cid == "aisd":
            base=self.host + "drama/AISD/"; return base if pg == 1 else base + "page/" + str(pg) + "/"
        if cid == "explore":
            e=ext if isinstance(ext,dict) else {}; vals=[str(e.get(k,0) or 0) for k in ("theme","setting","background","audience","time","recommend")]
            u=self.host+"explore-drama/"+"-".join(vals)+"/"; return u if pg==1 else u+"page/"+str(pg)+"/"
        if cid == "male": return self.host+"explore-actor/2/"+("page/"+str(pg)+"/" if pg>1 else "")
        if cid == "female": return self.host+"explore-actor/1/"+("page/"+str(pg)+"/" if pg>1 else "")
        if cid in ("actor_recommend","actor_new","actor_hot"):
            kind={"actor_recommend":"recommend","actor_new":"new","actor_hot":"hot"}[cid]; return self.host+"rank-actor/"+kind+"/"+("page/"+str(pg)+"/" if pg>1 else "")
        if cid.startswith("drama_"):
            kind="week" if cid=="drama_week" else "month"; return self.host+"rank-drama/"+kind+"/"+("page/"+str(pg)+"/" if pg>1 else "")
        if cid == "aisd": return self.host+"drama/AISD/"+("page/"+str(pg)+"/" if pg>1 else "")
        if cid.startswith("actor$"): return self.host+"actor/"+cid.split("$",1)[1]+"/"
        return self.host

    def homeContent(self, filter):
        self._load_filters()
        return {"class":self.classes,"filters":self.filters,"list":[]}
    def homeVideoContent(self): return self.categoryContent("drama",1,{}, {"source":"week"})

    def categoryContent(self, cid, pg, filter, ext):
        try:
            pg=int(pg) if str(pg).isdigit() else 1
            if str(cid).startswith("actor_detail_") or str(cid).startswith("actor-detail$") or str(cid).startswith("actor$") or "/actor-detail/" in str(cid) or "/actor/" in str(cid):
                aid=re.search(r"actor_detail_(\d+)", str(cid)).group(1) if str(cid).startswith("actor_detail_") else (str(cid).split("$")[1] if "$" in str(cid) else (re.search(r"actor-detail/(\d+)", str(cid)) or re.search(r"actor/(\d+)", str(cid)) or re.search(r"(\d+)", str(cid))).group(1))
                url=self.host+"actor-detail/"+aid+"/"+("?page="+str(pg) if pg>1 else "")
                html=self._req(url)
                if not html: return {"list":[],"page":pg,"pagecount":1,"limit":20,"total":0}
                data=self._payload(html)
                arr=[]; seen=set()
                works=self._walk(data,["video_id","title"]) or self._walk(data,["video_id","video_title"])
                for x in works:
                    v=self._vod(x,False)
                    if v and v["vod_id"] not in seen: seen.add(v["vod_id"]); arr.append(v)
                total, limit, pagecount = self._meta(html)
                print(f"[51短剧] 演员二级 {cid} 第{pg}页: {len(arr)} 条, 共{total}条")
                return {"list":arr,"page":pg,"pagecount":pagecount,"limit":limit,"total":total or len(arr)}
            actor=cid == "actor"
            html=self._req(self._url(cid,pg,ext)); vods=self._page(html,actor)
            total, limit, pagecount = self._meta(html)
            if cid == "aisd" and vods:
                limit = limit or 30
                pagecount = max(pagecount, pg + 1) if len(vods) >= limit else pg
                total = max(total, pagecount * limit)
            print(f"[51短剧] 分类 {cid} 第{pg}页: {len(vods)} 条")
            return {"list":vods,"page":pg,"pagecount":pagecount,"limit":limit,"total":total or len(vods)}
        except Exception as e:
            print(f"[51短剧] 分类失败: {e}"); return {"list":[],"page":1,"pagecount":1,"limit":20,"total":0}

    def detailContent(self, ids):
        try:
            vid=str(ids[0])
            if vid.startswith("actor_detail_") or vid.startswith("actor-detail$") or vid.startswith("actor$") or "/actor-detail/" in vid or "/actor/" in vid:
                aid=re.search(r"actor_detail_(\d+)", vid).group(1) if vid.startswith("actor_detail_") else (vid.split("$")[1] if "$" in vid else (re.search(r"actor-detail/(\d+)", vid) or re.search(r"actor/(\d+)", vid) or re.search(r"(\d+)", vid)).group(1))
                url=self.host+"actor-detail/"+aid+"/"
                html=self._req(url)
                if not html: return {"list":[]}
                data=self._payload(html)
                arr=[]; seen=set()
                works=self._walk(data,["video_id","title"]) or self._walk(data,["video_id","video_title"])
                for x in works:
                    v=self._vod(x,False)
                    if v and v["vod_id"] not in seen: seen.add(v["vod_id"]); arr.append(v)
                print(f"[51短剧] 演员 {aid} 作品: {len(arr)} 条")
                return {"list":[{"vod_id":x["vod_id"],"vod_name":x["vod_name"],"vod_pic":x.get("vod_pic",""),"vod_remarks":"\u53c2\u6f14\u5267\u96c6","vod_tag":"video","vod_play_id":x.get("vod_play_id","")} for x in arr]}
            sid=self._sid(vid)
            html=self._req(self.host+"drama-detail/"+sid+"/"); data=self._payload(html)
            # \u8be6\u60c5\u9875\u91cc\u540c\u65f6\u6df7\u7740 related_list\uff08\u522b\u7684\u5267\uff09\u2014\u2014 \u5fc5\u987b\u6309 video_id \u7cbe\u786e\u6311\u672c\u5267\uff0c\u5426\u5219\u6807\u9898/\u5c01\u9762\u4f1a\u4e32
            pics=[r for r in (self._walk(data,["video_id","title"]) or self._walk(data,["video_id","video_title"])) if str(r.get("video_id"))==sid]
            if not pics: pics=self._walk(data,["video_title","cover_img"])
            info=pics[0] if pics else {}
            title=str(info.get("title") or info.get("video_title") or info.get("drama_name") or sid)
            pic=self.image_map.get(title) or self._pic(info.get("cover") or info.get("cover_img") or info.get("cover_image") or info.get("image") or info.get("poster") or info.get("thumb")) if info else self.image_map.get(title, "")
            desc=str(info.get("description") or info.get("video_desc") or info.get("content") or "")
            tags=info.get("tags") or info.get("tag") or []
            vod_class=",".join([str(t) for t in tags]) if isinstance(tags,list) else str(tags or "")
            plays=str(info.get("play_count_text") or "") or self._num(info.get("play_count")); chase=self._num(info.get("chase_count")); remarks=(("\u64ad\u653e"+plays) if plays else "") + ((" \u00b7 \u8ffd\u5267"+chase) if chase else "")
            eps=self._episode_rows(sid)
            umap=self._url_map(sid)
            urls=[]; seen=set()
            if eps:
                for x in eps:
                    eid=str(x.get("id")); sort=int(x.get("sort") or 0)
                    n=str(x.get("title") or ("\u7b2c"+str(sort)+"\u96c6" if sort else "\u64ad\u653e"))
                    if not umap.get(eid): n=n+"[\u672a\u89e3\u9501]"
                    # \u7528\u7ad9\u70b9\u81ea\u5df1\u7684\u96c6\u9875\u5730\u5740\uff08/play/{sid}/{\u96c6\u5e8f\u53f7}/\uff09\uff1a\u70b9\u64ad\u65f6\u6309\u65f6\u5e8f\u53f7\u5b9a\u4f4d\uff0c
                    # \u4ece\u6839\u4e0a\u675c\u7edd"\u4efb\u4f55\u4e00\u96c6\u90fd\u64ad\u7b2c\u4e00\u96c6"\u3002\u76f4\u94fe\u5728\u64ad\u653e\u9636\u6bb5\u7531\u7f13\u5b58/\u73b0\u6293\u7ed9\u51fa\u3002
                    u=self.host+"play/"+sid+"/"+str(sort)+"/"
                    if u not in seen: seen.add(u); urls.append((n,u))
                if len(umap)<len(eps): remarks+=(" \u00b7 \u53ef\u770b%d/%d\u96c6" % (min(len(umap),len(eps)), len(eps)))
            elif umap:
                urls=[(("\u7b2c"+k+"\u96c6"),v) for k,v in sorted(umap.items(), key=lambda z:z[0])]
            else:
                for x in (self._walk(data,["episode_title","video_url"]) or []):
                    u=self._media(x.get("video_url"))
                    if u and u not in seen: seen.add(u); urls.append((str(x.get("episode_title") or "\u6b63\u7247"),u))
                if not urls:
                    pu=self._media(info.get("play_url"))
                    if pu: urls.append(("\u6b63\u7247",pu))
            return {"list":[{"vod_id":vid,"vod_name":title,"vod_pic":pic,"vod_remarks":remarks,"vod_class":vod_class,"vod_content":desc,"vod_play_from":"51\u77ed\u5267" if urls else "","vod_play_url":"#".join(n+"$"+u for n,u in urls)}]}
        except Exception as e: print(f"[51短剧] 详情失败: {e}"); return {"list":[]}

    def searchContent(self, key, quick, pg="1"):
        try:
            pg=int(pg) if str(pg).isdigit() else 1
            q=urllib.parse.quote(str(key))
            u=self.host+"search-drama/"+q+"/"+("page/"+str(pg)+"/" if pg>1 else "")
            html=self._req(u); vods=self._page(html,False); total,limit,pagecount=self._meta(html)
            print(f"[51短剧] 搜索 {key} 第{pg}页: {len(vods)} 条")
            return {"list":vods,"page":pg,"pagecount":pagecount,"limit":limit,"total":total or len(vods)}
        except Exception as e:
            print(f"[51短剧] 搜索失败: {e}"); return {"list":[],"page":pg,"pagecount":1,"limit":20,"total":0}

    def playerContent(self, flag, id, vipFlags):
        try:
            url=str(id).replace("\\u002F","/").replace("\\/","/")
            sid=""; target=""; want_sort=0
            if not self.isVideoFormat(url):
                # \u76ee\u6807\u96c6\u5b9a\u4f4d\uff1a/play/{sid}/{n}/ \u7528\u96c6\u5e8f\u53f7\uff0c\u65e7 drama-play?id=..&episode_id=.. \u7528 episode_id
                sid=self._sid(url) if ("/play/" in url or "drama-play" in url) else ""
                mn=re.search(r"/play/\d+/(\d+)", url); me=re.search(r"episode_id=(\d+)", url)
                if mn: want_sort=int(mn.group(1))
                elif me: target=me.group(1)
                best=""
                if sid:
                    umap=self._url_map(sid)
                    if not target and want_sort:
                        eps=self._episode_rows(sid)
                        hit=[str(e.get("id")) for e in eps if int(e.get("sort") or 0)==want_sort]
                        target=hit[0] if hit else ""
                    best=umap.get(target) or ""
                    if not best and want_sort:
                        # \u7f13\u5b58\u6ca1\u7ed9 \u2192 \u73b0\u6293\u8be5\u96c6\u9875\u9762\u515c\u5e95\uff08\u6309\u96c6\u5e8f\u53f7\u5339\u914d\uff0c\u7edd\u4e0d\u56de\u5230\u7b2c\u4e00\u96c6\uff09
                        d2=self._payload(self._req(self.host+"play/"+sid+"/"+str(want_sort)+"/"))
                        def go2(x):
                            nonlocal best, target
                            if best: return
                            if isinstance(x, dict):
                                if int(x.get("sort") or 0)==want_sort and x.get("video_url"):
                                    best=self._media(x.get("video_url"))
                                    target=str(x.get("id") or target); return
                                for v in x.values(): go2(v)
                            elif isinstance(x, list):
                                for v in x: go2(v)
                        go2(d2)
                    if not best:
                        print(f"[51短剧] 第{target or want_sort}集无可用直链（多半未解锁），不做兜底串集")
                elif "drama-play" in url:
                    html=self._req(url); data=self._payload(html)
                    def go(x):
                        nonlocal best
                        if best: return
                        if isinstance(x, dict):
                            if str(x.get("id") or x.get("episode_id") or "") == target:
                                u=x.get("video_url") or x.get("play_url") or ""
                                if u: best=self._media(u); return
                            for v in x.values(): go(v)
                        elif isinstance(x, list):
                            for v in x: go(v)
                    if target: go(data)
                    if not best:
                        m=re.search(r"https?:[^\"'<>\s]+\.(?:m3u8|mp4)[^\"'<>\s]*", html)
                        if m: best=m.group(0).replace("\\u002F","/").replace("\\/","/")
                if best: url=best
            dm_url=""
            if sid and target:   # \u62ff\u5230\u51c6\u786e\u7684\u5267/\u96c6 id \u624d\u6302\u5f39\u5e55\uff0c\u907f\u514d\u8bef\u7528\u7b2c\u4e00\u96c6\u7684\u5f39\u5e55
                dm_url=self.getProxyUrl()+"&type=danmu&vid="+urllib.parse.quote(str(sid))+"&eid="+urllib.parse.quote(str(target))
            ret={"parse":0,"url":url,"header":json.dumps(self.headers,ensure_ascii=False)}
            if dm_url: ret["danmaku"]=[{"name":"51\u77ed\u5267\u5f39\u5e55","url":dm_url}]
            return ret
        except Exception as e:
            print(f"[51短剧] 播放解析失败: {e}")
            return {"parse":0,"url":str(id),"header":json.dumps(self.headers,ensure_ascii=False)}
    def isVideoFormat(self, url): return bool(re.search(r'\.(m3u8|mp4|m4v|ts)(\?|$)',str(url),re.I))
    def e64(self, text):
        try: return base64.b64encode(str(text).encode("utf-8")).decode("utf-8")
        except Exception: return ""

    def d64(self, text):
        try: return base64.b64decode(str(text).encode("utf-8")).decode("utf-8")
        except Exception: return ""

    def localProxy(self, param):
        if param.get("type") == "danmu":
            try:
                vid=str(param.get("vid") or param.get("video_id") or "")
                eid=str(param.get("eid") or param.get("episode_id") or "")
                if not vid or not eid: return [404,"text/plain","",""]
                return [200,"application/xml; charset=utf-8",self._danmaku_xml(vid,eid),{"Cache-Control":"no-store"}]
            except Exception as e:
                print(f"[51短剧] 弹幕代理失败: {e}")
                return [404,"text/plain","",""]
        if param.get("type") != "img": return [404,"text/plain","",""]
        try:
            url=self.d64(param.get("url", ""))
            if not url: return [404,"text/plain","",""]
            r=self.session.get(url,headers=self.headers,timeout=15,verify=False)
            content=r.content
            try: content=unpad(AES.new(self.media_key,AES.MODE_CBC,self.media_iv).decrypt(content), AES.block_size)
            except Exception: pass
            ctype="image/jpeg"
            if content.startswith(b"\x89PNG"): ctype="image/png"
            elif content[:4] == b"RIFF" and content[8:12] == b"WEBP": ctype="image/webp"
            elif content.startswith(b"GIF"): ctype="image/gif"
            return [r.status_code,ctype,content,{}]
        except Exception as e:
            print(f"[51短剧] 图片代理失败: {e}")
            return [404,"text/plain","",""]

    def destroy(self):
        try: self.session.close()
        except Exception: pass