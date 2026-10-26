#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import base64
import random
import urllib.request
import urllib.parse
from urllib.parse import quote, unquote
import http.cookiejar
import gzip
import zlib
import ssl

try:
    from base.spider import Spider as SpiderBase
except ImportError:
    class SpiderBase(object):
        def getCache(self, key):
            return None
        def setCache(self, key, value):
            return "fail"
        def delCache(self, key):
            return "fail"

def format_remarks(brand="\u8774\u8776\u5f71\u89c6", meta=""):
    clean_meta = str(meta or "").strip()
    clean_meta = re.sub(r"[\r\n\t]+", " ", clean_meta).strip()
    if clean_meta:
        return "%s | %s" % (brand, clean_meta)
    return brand

class Spider(SpiderBase):
    def __init__(self):
        super(Spider, self).__init__()
        self.siteName = "\u7981\u679c\u77ed\u5267"
        self.siteUrl = "https://jinguoduanju.app"
        self.apiBase = "https://jinguoduanju.app"
        self.tgGroup = "https://t.me/tvshare23"
        self.brandActor = "\U0001f98b TG\u7fa4: @tvshare23"
        self.brandDirector = "\U0001f98b \u8774\u8776\u5f71\u89c6"
        self.brandName = "\u8774\u8776\u5f71\u89c6"
        self.cardStyle = {"type": "rect", "ratio": 0.75}
        self.pageSize = 24
        self._ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

        self._token = ""
        self._deviceId = ""
        self.options = {}

        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cj),
            urllib.request.HTTPSHandler(context=self.ctx)
        )

    def init(self, extend=""):
        if isinstance(extend, dict):
            self.options = extend
        elif extend:
            try:
                self.options = json.loads(extend)
            except Exception:
                self.options = {}
        if self.options.get("apiBase"):
            self.apiBase = self.options["apiBase"].rstrip("/")
            self.siteUrl = self.apiBase
        return True

    def getName(self):
        return self.siteName

    def isVideoFormat(self, url):
        low = (url or "").lower()
        return any(k in low for k in (".m3u8", ".mp4", ".flv", ".mkv", ".ts"))

    def manualVideoCheck(self):
        return False

    def destroy(self):
        self.options = {}
        self._token = ""

    def _rand_device(self):
        chars = "0123456789abcdef"
        return "".join(random.choice(chars) for _ in range(32))

    def _fetch(self, target_url, data=None, referer="", headers_custom=None):
        if not target_url:
            return {"code": 0, "text": "", "bytes": b"", "err": "", "final_url": ""}
        if target_url.startswith("//"):
            target_url = "https:" + target_url
        elif target_url.startswith("/"):
            target_url = self.siteUrl + target_url

        headers = {
            "User-Agent": self._ua,
            "Referer": referer if referer else (self.siteUrl + "/"),
            "Origin": self.siteUrl,
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        if headers_custom:
            headers.update(headers_custom)

        req_data = None
        if data is not None:
            if isinstance(data, (dict, list)):
                req_data = json.dumps(data).encode("utf-8")
                headers["Content-Type"] = "application/json;charset=UTF-8"
            elif isinstance(data, str):
                req_data = data.encode("utf-8")
            else:
                req_data = data

        for attempt in range(2):
            try:
                req = urllib.request.Request(target_url, data=req_data, headers=headers)
                with self.opener.open(req, timeout=10) as resp:
                    code = resp.getcode()
                    final_url = resp.geturl()
                    raw = resp.read()
                    enc = getattr(resp, "headers", {}).get("Content-Encoding", "")
                    if raw.startswith(b"\x1f\x8b") or enc == "gzip":
                        raw = gzip.decompress(raw)
                    elif enc == "deflate":
                        try:
                            raw = zlib.decompress(raw)
                        except Exception:
                            raw = zlib.decompress(raw, -zlib.MAX_WBITS)
                    try:
                        text = raw.decode("utf-8")
                    except Exception:
                        text = raw.decode("latin1", errors="ignore")
                    return {"code": code, "text": text, "bytes": raw, "err": "", "final_url": final_url}
            except urllib.error.HTTPError as e:
                if attempt == 0 and e.code in (429, 451):
                    continue
                err_raw = ""
                try:
                    err_raw = e.read().decode("utf-8", "ignore")
                except Exception:
                    pass
                return {"code": e.code, "text": err_raw, "bytes": b"", "err": str(e), "final_url": target_url}
            except Exception as e:
                if attempt == 0:
                    continue
                return {"code": -1, "text": "", "bytes": b"", "err": str(e), "final_url": target_url}

        return {"code": -1, "text": "", "bytes": b"", "err": "timeout", "final_url": target_url}

    def _ensure_token(self):
        if self._token:
            return self._token
        if not self._deviceId:
            self._deviceId = self._rand_device()

        url = "%s/api/v1/auth/device" % self.apiBase
        payload = {
            "deviceId": "h5:%s" % self._deviceId,
            "channelCode": "",
            "attributionToken": ""
        }
        res = self._fetch(url, data=payload)
        txt = res.get("text", "")
        if txt:
            try:
                d = json.loads(txt)
                self._token = str(d.get("token") or "").strip()
            except Exception:
                self._token = ""
        return self._token

    def _api_get(self, path, query=None, retry=False):
        tok = self._ensure_token()
        qs = ""
        if query:
            parts = []
            for k, v in query.items():
                if v is not None and str(v) != "":
                    parts.append("%s=%s" % (quote(str(k)), quote(str(v))))
            if parts:
                qs = "?" + "&".join(parts)

        url = "%s/api/v1%s%s" % (self.apiBase, path, qs)
        headers = {}
        if tok:
            headers["Authorization"] = "Bearer %s" % tok

        res = self._fetch(url, headers_custom=headers)
        if res.get("code") == 401 and not retry:
            self._token = ""
            return self._api_get(path, query=query, retry=True)

        txt = res.get("text", "")
        if not txt:
            return None
        try:
            return json.loads(txt)
        except Exception:
            return None

    def _fix_cover(self, u):
        raw = str(u or "").strip()
        if not raw:
            return "https://dummyimage.com/600x800/1e293b/ffffff.png&text=NO_COVER"
        if raw.startswith("http://") or raw.startswith("https://"):
            return raw
        if raw.startswith("//"):
            return "https:" + raw
        return "%s/%s" % (self.apiBase, raw.lstrip("/"))

    def _to_vod(self, it):
        if not isinstance(it, dict):
            return None
        vid = str(it.get("id") or "").strip()
        if not vid:
            return None
        title = str(it.get("title") or vid).strip()
        cover = self._fix_cover(it.get("coverUrl") or it.get("cover"))
        ep = it.get("episodeCount") or ""
        tags = it.get("tags") if isinstance(it.get("tags"), list) else []

        meta_parts = []
        if ep:
            meta_parts.append("\u5168%s\u96c6" % ep)
        if tags:
            meta_parts.append(" \u00b7 ".join(str(x) for x in tags[:2]))

        meta = " \u00b7 ".join(meta_parts)
        remarks = format_remarks(self.brandName, meta)

        return {
            "vod_id": vid,
            "vod_name": title,
            "vod_pic": cover,
            "vod_remarks": remarks,
            "style": self.cardStyle
        }

    def homeContent(self, filter):
        classes = [
            {"type_id": "latest", "type_name": "\u6700\u65b0\u4e0a\u7ebf"},
            {"type_id": "heat", "type_name": "\u70ed\u5ea6\u6392\u884c"},
            {"type_id": "landing", "type_name": "\u7cbe\u9009\u63a8\u8350"},
            {"type_id": "nav_2", "type_name": "\u5168\u90e8\u77ed\u5267"},
            {"type_id": "nav_7", "type_name": "\u539f\u521b\u7cbe\u54c1"},
            {"type_id": "nav_3", "type_name": "\u5355\u4f53\u4f5c\u54c1"},
            {"type_id": "nav_6", "type_name": "\u52a8\u6f2b\u6539\u7f16"},
            {"type_id": "nav_5", "type_name": "\u5f71\u89c6\u6539\u7f16"}
        ]

        filters = {}
        sub_filter = [
            {
                "key": "sort",
                "name": "\u6392\u5e8f",
                "init": "latest",
                "value": [
                    {"n": "\u6700\u65b0", "v": "latest"},
                    {"n": "\u6700\u70ed", "v": "heat"}
                ]
            },
            {
                "key": "length",
                "name": "\u96c6\u6570",
                "init": "",
                "value": [
                    {"n": "\u5168\u90e8", "v": ""},
                    {"n": "\u591a\u96c6", "v": "multi"},
                    {"n": "\u5355\u96c6", "v": "single"}
                ]
            },
            {
                "key": "tag",
                "name": "\u9898\u6750\u6807\u7b7e",
                "init": "",
                "value": [
                    {"n": "\u5168\u90e8", "v": ""},
                    {"n": "\u9b54\u6539", "v": "\u9b54\u6539"},
                    {"n": "\u90fd\u5e02", "v": "\u90fd\u5e02"},
                    {"n": "\u804c\u573a", "v": "\u804c\u573a"},
                    {"n": "\u5947\u5e7b", "v": "\u5947\u5e7b"},
                    {"n": "\u53e4\u88c5", "v": "\u53e4\u88c5"},
                    {"n": "\u52a8\u6f2b", "v": "\u52a8\u6f2b"}
                ]
            }
        ]

        for c in classes:
            filters[c["type_id"]] = sub_filter

        res = {"class": classes}
        if filter:
            res["filters"] = filters
        return res

    def homeVideoContent(self):
        data = self._api_get("/landing")
        list_data = []
        if isinstance(data, dict):
            list_data = data.get("dramas") or []
        elif isinstance(data, list):
            list_data = data

        v_list = []
        for it in list_data[:24]:
            v = self._to_vod(it)
            if v:
                v_list.append(v)
        return {"list": v_list}

    def categoryContent(self, tid, pg, filter, extend):
        del filter
        page = int(pg or 1)
        ext = extend if isinstance(extend, dict) else {}
        slug = str(tid).strip()

        if slug == "landing":
            data = self._api_get("/landing")
            all_items = []
            if isinstance(data, dict):
                all_items = data.get("dramas") or []
            elif isinstance(data, list):
                all_items = data

            start = (page - 1) * self.pageSize
            page_slice = all_items[start : start + self.pageSize]
            v_list = [self._to_vod(it) for it in page_slice if self._to_vod(it)]
            total = len(all_items)
            pagecount = (total + self.pageSize - 1) // self.pageSize
            return {
                "page": page,
                "pagecount": max(pagecount, 1),
                "limit": self.pageSize,
                "total": total,
                "list": v_list
            }

        q = {
            "sort": ext.get("sort") or ("heat" if slug == "heat" else "latest")
        }

        if slug.startswith("nav_"):
            q["navigationId"] = slug.split("_")[1]

        if ext.get("length"):
            q["length"] = ext.get("length")

        tag_filter = str(ext.get("tag") or "").strip()

        data = self._api_get("/dramas", query=q)
        all_dramas = data if isinstance(data, list) else []

        if tag_filter:
            filtered = []
            for it in all_dramas:
                tags = it.get("tags") if isinstance(it.get("tags"), list) else []
                if tag_filter in [str(x) for x in tags]:
                    filtered.append(it)
            all_dramas = filtered

        total = len(all_dramas)
        pagecount = (total + self.pageSize - 1) // self.pageSize
        start = (page - 1) * self.pageSize
        page_slice = all_dramas[start : start + self.pageSize]

        v_list = [self._to_vod(it) for it in page_slice if self._to_vod(it)]

        return {
            "page": page,
            "pagecount": max(pagecount, 1),
            "limit": self.pageSize,
            "total": total,
            "list": v_list
        }

    def detailContent(self, ids):
        raw_id = ids[0] if isinstance(ids, (list, tuple)) else str(ids)
        vid = str(raw_id).strip()

        data = self._api_get("/dramas/%s" % quote(vid))
        drama = data.get("drama") if isinstance(data, dict) else {}
        eps = data.get("episodes") if isinstance(data, dict) and isinstance(data.get("episodes"), list) else []

        title = str(drama.get("title") or vid).strip()
        cover = self._fix_cover(drama.get("coverUrl") or drama.get("cover"))
        tags = drama.get("tags") if isinstance(drama.get("tags"), list) else []
        raw_desc = str(drama.get("description") or ((" \u00b7 ".join(str(x) for x in tags)) if tags else "")).strip()

        play_urls = []
        if eps:
            for idx, ep in enumerate(eps):
                n = str(ep.get("number") or (idx + 1)).strip()
                ep_id = str(ep.get("id") or "").strip()
                t_name = str(ep.get("title") or ("\u7b2c%s\u96c6" % n)).strip()
                t_name = t_name.replace("$", "").replace("#", "")
                play_urls.append("%s$%s:%s:%s" % (t_name, vid, n, ep_id))
        else:
            play_urls.append("\u7b2c1\u96c6$%s:1:" % vid)

        full_desc = (
            "\u3010\U0001f525 \u5b98\u65b9\u4ea4\u6d41\u7fa4: %s\u3011\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "%s"
        ) % (self.tgGroup, raw_desc)

        vod = {
            "vod_id": vid,
            "vod_name": title,
            "vod_pic": cover,
            "vod_actor": self.brandActor,
            "vod_director": self.brandDirector,
            "vod_remarks": format_remarks(self.brandName, "\u5168%d\u96c6" % len(play_urls)),
            "vod_content": full_desc,
            "vod_play_from": "\u7981\u679c\u4e13\u7ebf",
            "vod_play_url": "#".join(play_urls),
            "style": self.cardStyle
        }
        return {"list": [vod]}

    def playerContent(self, flag, id, vipFlags):
        del flag, vipFlags
        raw = str(id or "").strip()
        parts = raw.split(":")
        drama_id = parts[0]
        ep_num = parts[1] if len(parts) > 1 else "1"
        ep_id = parts[2] if len(parts) > 2 else ""

        if not ep_id and drama_id:
            data = self._api_get("/dramas/%s" % quote(drama_id))
            eps = data.get("episodes") if isinstance(data, dict) and isinstance(data.get("episodes"), list) else []
            for ep in eps:
                if str(ep.get("number") or "") == str(ep_num) or str(ep.get("id") or "") == str(ep_num):
                    ep_id = str(ep.get("id") or "")
                    break
            if not ep_id and eps:
                ep_id = str(eps[0].get("id") or "")

        video_url = ""
        if ep_id:
            play = self._api_get("/episodes/%s/play" % quote(ep_id))
            if isinstance(play, dict):
                video_url = str(play.get("videoUrl") or "").strip()

        headers = {
            "User-Agent": self._ua,
            "Referer": self.siteUrl + "/",
            "Origin": self.siteUrl
        }

        return {
            "parse": 0,
            "playUrl": "",
            "url": video_url,
            "header": headers
        }

    def searchContent(self, key, quick, pg="1"):
        del quick
        kw = str(key or "").strip()
        if not kw:
            return {"page": 1, "pagecount": 1, "limit": 0, "total": 0, "list": []}
        page = int(pg or 1)

        data = self._api_get("/dramas", query={"sort": "latest", "q": kw})
        all_dramas = data if isinstance(data, list) else []

        total = len(all_dramas)
        pagecount = (total + self.pageSize - 1) // self.pageSize
        start = (page - 1) * self.pageSize
        page_slice = all_dramas[start : start + self.pageSize]

        v_list = [self._to_vod(it) for it in page_slice if self._to_vod(it)]

        return {
            "page": page,
            "pagecount": max(pagecount, 1),
            "limit": self.pageSize,
            "total": total,
            "list": v_list
        }

    def localProxy(self, params):
        return [404, "text/plain; charset=utf-8", "Proxy not configured"]

    def liveContent(self):
        return ""

    def action(self, action):
        return {"msg": "ok"}