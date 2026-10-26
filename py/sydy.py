# coding=utf-8
import base64
import html
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.append('..')

try:
    from base.spider import Spider as BaseSpider
except Exception:
    class BaseSpider(object):
        def log(self, msg):
            pass

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

DEFAULT_URL = "https://xn--essr89b.shenye.sbs"
UA = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"

MODULES = [
    ("9", "\u77ed\u5267\u533a"),
    ("4", "\u597d\u7535\u5f71"),
    ("5", "\u65b0\u5267\u96c6"),
    ("7", "\u52a8\u6f2b\u533a"),
    ("6", "\u7efc\u827a\u7247"),
    ("1", "\u5341\u516b\u7981"),
    ("2", "\u79c1\u5bc6\u533a"),
    ("3", "\u5348\u591c\u533a"),
    ("8", "\u4f26\u7406\u533a"),
    ("10", "\u4f53\u80b2\u533a")
]

SUB_FILTERS = {
    "9": [
        {"n": "\u5168\u90e8", "v": "9"},
        {"n": "\u91cd\u751f", "v": "64"},
        {"n": "\u7a7f\u8d8a", "v": "65"},
        {"n": "\u53cd\u8f6c", "v": "66"},
        {"n": "\u8a00\u60c5", "v": "67"},
        {"n": "\u73b0\u4ee3", "v": "68"},
        {"n": "\u53e4\u88c5", "v": "69"},
        {"n": "\u60ac\u7591", "v": "70"}
    ],
    "4": [
        {"n": "\u5168\u90e8", "v": "4"},
        {"n": "\u52a8\u6f2b", "v": "78"},
        {"n": "\u52a8\u4f5c", "v": "38"},
        {"n": "\u7231\u60c5", "v": "39"},
        {"n": "\u559c\u5267", "v": "40"},
        {"n": "\u79d1\u5e7b", "v": "41"},
        {"n": "\u6050\u6016", "v": "42"},
        {"n": "\u5267\u60c5", "v": "43"},
        {"n": "\u6218\u4e89", "v": "44"},
        {"n": "\u60ca\u609a", "v": "45"},
        {"n": "\u7eaa\u5f55", "v": "46"}
    ],
    "5": [
        {"n": "\u5168\u90e8", "v": "5"},
        {"n": "\u56fd\u4ea7", "v": "47"},
        {"n": "\u9999\u6e2f", "v": "48"},
        {"n": "\u97e9\u5267", "v": "49"},
        {"n": "\u6b27\u7f8e", "v": "50"},
        {"n": "\u65e5\u672c", "v": "51"},
        {"n": "\u6cf0\u56fd", "v": "52"},
        {"n": "\u53f0\u6e7e", "v": "53"},
        {"n": "\u6d77\u5916", "v": "54"}
    ],
    "7": [
        {"n": "\u5168\u90e8", "v": "7"},
        {"n": "\u56fd\u4ea7", "v": "60"},
        {"n": "\u65e5\u672c", "v": "61"},
        {"n": "\u6b27\u7f8e", "v": "62"},
        {"n": "\u6d77\u5916", "v": "63"}
    ],
    "6": [
        {"n": "\u5168\u90e8", "v": "6"},
        {"n": "\u5927\u9646", "v": "55"},
        {"n": "\u65e5\u97e9", "v": "56"},
        {"n": "\u6e2f\u53f0", "v": "57"},
        {"n": "\u6b27\u7f8e", "v": "58"},
        {"n": "\u6f14\u5531", "v": "59"}
    ],
    "1": [
        {"n": "\u5168\u90e8", "v": "1"},
        {"n": "\u5f3a\u5978", "v": "11"},
        {"n": "\u7f51\u66dd", "v": "12"},
        {"n": "\u56fd\u4ea7", "v": "13"},
        {"n": "\u4e1d\u889c", "v": "14"},
        {"n": "\u4e3b\u64ad", "v": "15"},
        {"n": "AI", "v": "16"},
        {"n": "\u5bb6\u5ead", "v": "17"},
        {"n": "SM", "v": "18"},
        {"n": "\u7fa4\u4ea4", "v": "19"}
    ],
    "2": [
        {"n": "\u5168\u90e8", "v": "2"},
        {"n": "\u5b66\u751f", "v": "20"},
        {"n": "\u81ea\u62cd", "v": "21"},
        {"n": "\u53e3\u4ea4", "v": "22"},
        {"n": "\u56fd\u4ea7", "v": "23"},
        {"n": "\u7d20\u4eba", "v": "24"},
        {"n": "\u65e0\u7801", "v": "25"},
        {"n": "\u7ecf\u5178", "v": "26"},
        {"n": "\u4e2d\u6587", "v": "27"},
        {"n": "\u65e5\u97e9", "v": "28"}
    ],
    "3": [
        {"n": "\u5168\u90e8", "v": "3"},
        {"n": "\u65e5\u97e9", "v": "29"},
        {"n": "\u56fd\u4ea7", "v": "30"},
        {"n": "\u6b27\u7f8e", "v": "31"},
        {"n": "VR", "v": "32"},
        {"n": "\u5382\u724c", "v": "33"},
        {"n": "\u91cd\u53e3", "v": "34"},
        {"n": "\u4eba\u517d", "v": "35"},
        {"n": "\u6fc0\u60c5", "v": "36"},
        {"n": "\u5f02\u65cf", "v": "37"}
    ]
}

def _s(v):
    if v is None:
        return ""
    if isinstance(v, (dict, list, tuple)):
        return ""
    return str(v).strip()

def _to_int(v, dft=0, low=None, high=None):
    try:
        n = int(float(str(v).strip()))
    except Exception:
        n = dft
    if low is not None and n < low:
        n = low
    if high is not None and n > high:
        n = high
    return n

def _clean_text(s):
    t = _s(s)
    if not t:
        return ""
    t = html.unescape(t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'[\r\n\t]+', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

class Spider(BaseSpider):
    def __init__(self):
        self.host = DEFAULT_URL
        self.ua = UA
        self._detail_cache = {}
        self._play_cache = {}
        self._opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=_ssl_ctx))

    def getName(self):
        return "\u6df1\u591c\u7535\u5f71"

    def init(self, extend=""):
        if extend:
            self.host = extend.rstrip('/')

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def action(self, action):
        return None

    def liveContent(self):
        return []

    def _fetch(self, url, headers=None, timeout=6):
        req_headers = {
            "User-Agent": self.ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Referer": self.host + "/"
        }
        if headers:
            req_headers.update(headers)
        req = urllib.request.Request(url, headers=req_headers)
        try:
            with self._opener.open(req, timeout=timeout) as resp:
                final_url = resp.geturl()
                status = resp.status
                body = resp.read()
                try:
                    html_text = body.decode("utf-8")
                except Exception:
                    html_text = body.decode("gbk", "ignore")
                return status, final_url, html_text
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode("utf-8", "ignore")
            except Exception:
                body = ""
            return e.code, url, body
        except Exception as e:
            return 0, url, str(e)

    def _abs(self, u):
        u = _s(u)
        if not u:
            return ""
        if u.startswith('//'):
            return "https:" + u
        if u.startswith('/'):
            return self.host + u
        return u

    def homeContent(self, filter=True):
        classes = []
        for tid, name in MODULES:
            classes.append({"type_id": tid, "type_name": name})

        filters = {}
        for tid, sub_items in SUB_FILTERS.items():
            filters[tid] = [
                {
                    "key": "sub_tid",
                    "name": "\u5b50\u7c7b",
                    "value": sub_items
                }
            ]

        return {"class": classes, "filters": filters}

    def homeVideoContent(self):
        return {"list": []}

    def _parse_cards(self, html_content):
        vlist = []
        if not html_content:
            return vlist
        link_matches = re.findall(r'<a[^>]+href=["\'](/vod(?:play|detail)/(\d+)[^"\']*)["\'][^>]*>(.*?)</a>', html_content, re.I | re.S)
        seen_ids = set()
        for href, vid, inner in link_matches:
            if vid in seen_ids:
                continue

            title = ""
            title_m = re.search(r'title=["\']([^"\']+)["\']', inner, re.I)
            if title_m:
                title = _clean_text(title_m.group(1))
            if not title:
                alt_m = re.search(r'alt=["\']([^"\']+)["\']', inner, re.I)
                if alt_m:
                    title = _clean_text(alt_m.group(1))
            if not title:
                clean_inner = _clean_text(inner)
                if 1 < len(clean_inner) <= 30 and not re.match(r'^\d+(\.\d+)?$', clean_inner):
                    title = clean_inner

            if not title:
                continue

            pic = ""
            pic_m = re.search(r'(?:data-original|data-src|src)=["\']([^"\']+)["\']', inner, re.I)
            if pic_m:
                pic = self._abs(pic_m.group(1))

            remarks_raw = ""
            rem_m = re.search(r'<(?:span|em|i)[^>]*>([^<]+)</(?:span|em|i)>', inner, re.I)
            if rem_m:
                r_text = _clean_text(rem_m.group(1))
                if r_text != title and len(r_text) <= 15:
                    remarks_raw = r_text

            if remarks_raw:
                remarks = "\u8774\u8776\u5f71\u89c6 | %s" % remarks_raw
            else:
                remarks = "\u8774\u8776\u5f71\u89c6"

            seen_ids.add(vid)
            vlist.append({
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": remarks
            })
        return vlist

    def categoryContent(self, tid, pg="1", filter=None, extend=None):
        page = _to_int(pg, 1, 1)
        ext = extend if isinstance(extend, dict) else {}
        sub_id = _s(ext.get("sub_tid"))
        target_id = sub_id if sub_id else _s(tid)

        base_clean = self.host.rstrip('/')
        url = "%s/vodshow/%s--------%s---.html" % (base_clean, target_id, page)
        status, final_url, html_content = self._fetch(url, timeout=6)

        vlist = []
        if status == 200 and html_content:
            vlist = self._parse_cards(html_content)

        max_page_found = page
        if html_content:
            all_page_nums = re.findall(r'/vodshow/\d+--------(\d+)---.html', html_content)
            for p_str in all_page_nums:
                p_val = _to_int(p_str, 0)
                if p_val > max_page_found:
                    max_page_found = p_val

        if max_page_found > page:
            total_pages = max_page_found
        elif len(vlist) > 0:
            total_pages = page + 10
        else:
            total_pages = page

        return {
            "list": vlist,
            "page": page,
            "pagecount": total_pages,
            "limit": len(vlist) if vlist else 18,
            "total": total_pages * (len(vlist) if vlist else 18)
        }

    def _extract_stream_from_html(self, html_content):
        if not html_content:
            return ""
        player_m = re.search(r'var\s+player_aaaa\s*=\s*({[^;]+?});?', html_content, re.I)
        if player_m:
            try:
                cfg_str = player_m.group(1).strip()
                p_obj = json.loads(cfg_str)
                raw_u = _s(p_obj.get("url"))
                if raw_u.startswith("http"):
                    return raw_u
                elif raw_u:
                    return self._abs(raw_u)
            except Exception:
                pass

        url_assign_m = re.search(r'["\']url["\']\s*:\s*["\'](https?://[^"\']+?\.m3u8[^"\']*?)["\']', html_content, re.I)
        if url_assign_m:
            return url_assign_m.group(1).replace('\\/', '/')

        m3u8_matches = re.findall(r'(https?://[^"\'\s<>\\]+?\.(?:m3u8|mp4)[^"\'\s<>\\]*)', html_content, re.I)
        if m3u8_matches:
            return m3u8_matches[0].replace('\\/', '/')
        return ""

    def detailContent(self, ids):
        vid = ""
        if isinstance(ids, (list, tuple)):
            vid = _s(ids[0]) if ids else ""
        else:
            vid = _s(ids)
        if not vid:
            return {"list": []}

        now_ts = time.time()
        cached = self._detail_cache.get(vid)
        if cached and (now_ts - cached[0] < 300):
            return {"list": [cached[1]]}

        base_clean = self.host.rstrip('/')
        play_direct_url = "%s/vodplay/%s-1-1.html" % (base_clean, vid)
        status, final_url, html_content = self._fetch(play_direct_url, timeout=6)

        if not html_content:
            return {"list": []}

        first_stream = self._extract_stream_from_html(html_content)
        if first_stream:
            self._play_cache[play_direct_url] = first_stream

        title = ""
        t_m = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content, re.I)
        if t_m:
            title = _clean_text(t_m.group(1))
        if not title:
            meta_m = re.search(r'<title>([^<_]+)', html_content, re.I)
            if meta_m:
                title = _clean_text(meta_m.group(1))

        pic = ""
        pic_m = re.search(r'<div[^>]+class=["\'][^"\']*(?:poster|pic|thumb)[^"\']*["\'][^>]*>.*?<img[^>]+src=["\']([^"\']+)["\']', html_content, re.I | re.S)
        if pic_m:
            pic = self._abs(pic_m.group(1))
        if not pic:
            og_pic = re.search(r'<meta property="og:image" content="([^"]+)"', html_content, re.I)
            if og_pic:
                pic = self._abs(og_pic.group(1))

        desc = ""
        desc_m = re.search(r'<(?:div|p)[^>]+class=["\'][^"\']*(?:desc|content|detail-sketch)[^"\']*["\'][^>]*>(.*?)</(?:div|p)>', html_content, re.I | re.S)
        if desc_m:
            desc = _clean_text(desc_m.group(1))
        if not desc:
            meta_desc = re.search(r'<meta name="description" content="([^"]+)"', html_content, re.I)
            if meta_desc:
                desc = _clean_text(meta_desc.group(1))

        notice = "\U0001f98b TG\u7fa4: @tvshare23 \u63d0\u9192\u60a8\uff1a\u8bf7\u52ff\u76f8\u4fe1\u89c6\u9891\u4e2d\u4efb\u4f55\u5185\u5d4c\u5e7f\u544a\uff01"
        full_desc = "%s\n%s" % (notice, desc) if desc else notice

        ep_links = re.findall(r'<a[^>]+href=["\'](/vodplay/%s-(\d+)-(\d+)\.html)["\'][^>]*>(.*?)</a>' % vid, html_content, re.I | re.S)
        
        play_dict = {}
        if ep_links:
            for ep_href, sid_str, nid_str, ep_name in ep_links:
                sid = _to_int(sid_str, 1)
                nid = _to_int(nid_str, 1)
                clean_name = _clean_text(ep_name)
                if not clean_name or len(clean_name) > 20:
                    clean_name = "\u7b2c%s\u96c6" % nid
                if sid not in play_dict:
                    play_dict[sid] = []
                play_item = "%s$%s" % (clean_name, self._abs(ep_href))
                if play_item not in play_dict[sid]:
                    play_dict[sid].append(play_item)

        if not play_dict:
            play_dict[1] = ["\u6b63\u7247$%s" % play_direct_url]

        from_list = []
        url_list = []
        for sid in sorted(play_dict.keys()):
            from_list.append("\u7ebf\u8def%s" % sid)
            url_list.append("#".join(play_dict[sid]))

        vod_item = {
            "vod_id": vid,
            "vod_name": title if title else "\u5f71\u89c6\u6b63\u7247",
            "vod_pic": pic,
            "vod_actor": "\U0001f98b TG\u7fa4: @tvshare23",
            "vod_director": "\U0001f98b \u8774\u8776\u5f71\u89c6",
            "vod_content": full_desc,
            "vod_remarks": "\u8774\u8776\u5f71\u89c6",
            "vod_play_from": "$$$".join(from_list),
            "vod_play_url": "$$$".join(url_list)
        }

        self._detail_cache[vid] = (now_ts, vod_item)
        if len(self._detail_cache) > 50:
            self._detail_cache.clear()

        return {"list": [vod_item]}

    def playerContent(self, flag, id, vipFlags):
        res = {"parse": 0, "url": ""}
        raw_url = _s(id)
        if not raw_url:
            return res

        play_page_url = self._abs(raw_url)
        header = {
            "User-Agent": self.ua,
            "Referer": play_page_url
        }

        cached_stream = self._play_cache.get(play_page_url)
        if cached_stream:
            res["url"] = cached_stream
            res["header"] = header
            res["parse"] = 0
            return res

        status, final_url, html_content = self._fetch(play_page_url, timeout=5)
        direct_url = self._extract_stream_from_html(html_content)

        if not direct_url:
            iframe_m = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', html_content, re.I)
            if iframe_m:
                iframe_src = self._abs(iframe_m.group(1))
                qs = urllib.parse.urlparse(iframe_src).query
                params = urllib.parse.parse_qs(qs)
                cand_keys = ["url", "v", "vid", "link"]
                for k in cand_keys:
                    if k in params and params[k]:
                        param_u = params[k][0]
                        if param_u.startswith("http"):
                            direct_url = param_u
                            break

        if direct_url:
            self._play_cache[play_page_url] = direct_url
            if len(self._play_cache) > 100:
                self._play_cache.clear()
            res["url"] = direct_url
            res["header"] = header
            res["parse"] = 0
        else:
            res["url"] = play_page_url
            res["header"] = header
            res["parse"] = 1

        return res

    def searchContent(self, key, quick, pg="1"):
        kw = _s(key)
        page = _to_int(pg, 1, 1)
        if not kw:
            return {"list": [], "page": page, "pagecount": page, "limit": 18, "total": 0}

        base_clean = self.host.rstrip('/')
        encoded_kw = urllib.parse.quote(kw)
        search_url = "%s/vodsearch/%s----------%s---.html" % (base_clean, encoded_kw, page)
        status, final_url, html_content = self._fetch(search_url, timeout=6)

        vlist = []
        if status == 200 and html_content:
            vlist = self._parse_cards(html_content)

        max_page_found = page
        if html_content:
            all_page_nums = re.findall(r'/vodsearch/[^/]+----------(\d+)---.html', html_content)
            for p_str in all_page_nums:
                p_val = _to_int(p_str, 0)
                if p_val > max_page_found:
                    max_page_found = p_val

        total_pages = max_page_found if max_page_found > page else (page + 1 if len(vlist) >= 15 else page)

        return {
            "list": vlist,
            "page": page,
            "pagecount": total_pages,
            "limit": len(vlist) if vlist else 18,
            "total": total_pages * (len(vlist) if vlist else 18)
        }

    def localProxy(self, params):
        return [404, "text/plain", ""]

    def destroy(self):
        pass