# -*- coding: utf-8 -*-
# \u4e13\u5c5e\u5168\u7f51\u805a\u5408 Python\u7248
# \u9002\u914d\u5e38\u89c1 Cat/TVBox Python Spider
#\u672c\u5730py\u9002\u914d  \ud83d\ude02  

import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from base.spider import Spider


class Spider(Spider):
    sources = {
        's1': {'name': '\u674f\u5427\u8d44\u6e90', 'api': 'https://xingba111.com/api.php/provide/vod/'},
        's2': {'name': '\u6781\u54c1\u8d44\u6e90', 'api': 'https://jipinvip1.com/api.php/provide/vod/'},
        's3': {'name': '\u9999\u8549\u8d44\u6e90\u7f51', 'api': 'https://www.xiangjiaozyw.com/api.php/provide/vod/'},
        's4': {'name': '\u756a\u8304\u8d44\u6e90', 'api': 'https://fqzy.me//api.php/provide/vod/'},
        's5': {'name': '\u9ed1\u6599\u8d44\u6e90', 'api': 'https://heiliaozyapi.com/api.php/seaxml/vod/'},
        's6': {'name': '\u9ec4\u8272\u4ed3\u5e93', 'api': 'https://\u0068\u0073\u0063\u006bzy.vip/api.php/provide/vod/'},
        's7': {'name': '\u5976\u9999\u9999\u8d44\u6e90', 'api': 'https://naixxzy.com/api.php/provide/vod/'},
        's8': {'name': '\u6843\u82b1\u8d44\u6e90', 'api': 'https://thzy1.me/api.php/provide/vod/'},
        's9': {'name': 'CK\u4f26\u7406\u8d44\u6e90', 'api': 'https://ckzy.me/api.php/provide/vod/'},
        's10': {'name': '\u5927\u5976\u5b50\u8d44\u6e90', 'api': 'https://apidanaizi.com/api.php/provide/vod/'},
        's11': {'name': '\u641cav\u8d44\u6e90', 'api': 'https://api.souavzyw.net/api.php/provide/vod/'},
        's12': {'name': '\u5965\u65af\u5361\u8d44\u6e90', 'api': 'https://aosikazy1.com/api.php/provide/vod/'},
        's13': {'name': '\u6ef4\u6ef4\u8d44\u6e90', 'api': 'https://api.ddapi.cc/api.php/provide/vod/at/json/'},
        's14': {'name': '\u8c46\u8c46\u8d44\u6e90', 'api': 'https://api.douapi.cc/api.php/provide/vod/'},
        's15': {'name': '\u9ca8\u9c7c\u8d44\u6e90', 'api': 'https://shayuapi.com/api.php/provide/vod/'},
        's16': {'name': '\u8fa3\u6912\u8d44\u6e90', 'api': 'http://apilj.com/api.php/provide/vod/at/json/'},
        's17': {'name': '\u68ee\u6797\u8d44\u6e90', 'api': 'https://slapibf.com/api.php/provide/vod/'},
        's18': {'name': '155\u8d44\u6e90', 'api': 'https://155api.com/api.php/provide/vod/'},
        's19': {'name': '\u4e50\u64ad\u8d44\u6e90', 'api': 'https://lbapi9.com/api.php/provide/vod/'},
        's20': {'name': '\u7389\u5154\u8d44\u6e90', 'api': 'https://apiyutu.com/api.php/provide/vod/'},
        's21': {'name': '\u756a\u53f7\u8d44\u6e90', 'api': 'http://fhapi9.com/api.php/provide/vod/'},
        's22': {'name': '\u7cbe\u54c1X\u8d44\u6e90', 'api': 'https://www.jingpinx.com/api.php/provide/vod/'},
        's23': {'name': 'jkun\u8d44\u6e90', 'api': 'https://jkunzyapi.com/api.php/provide/vod/'},
        's24': {'name': '\u6e7f\u4e50\u56ed', 'api': 'https://xxavs.com/api.php/provide/vod/'},
        's25': {'name': '\u8d8a\u5357\u8d44\u6e90', 'api': 'https://www.vnzyz.com/api.php/provide/vod/'},
        's26': {'name': '\u7ea2\u6843\u89c6\u9891', 'api': 'https://apidanaizi.com/api.php/provide/vod/'},
        's27': {'name': '\u9e21\u5764\u8d44\u6e90', 'api': 'https://jkunzyapi.com/api.php/provide/vod/'},
        's28': {'name': 'AIvin', 'api': 'http://lbapiby.com/api.php/provide/vod/'},
        's29': {'name': 'lsb\u8d44\u6e90', 'api': 'https://apilsbzy1.com/api.php/provide/vod/'},
        's30': {'name': '91\u9ebb\u8c46', 'api': 'https://91md.me/api.php/provide/vod/'},
        's31': {'name': '\u8001\u8272\u903c\u8d44\u6e90', 'api': 'https://apilsbzy1.com/api.php/provide/vod/'},
        's32': {'name': '\u706b\u901f\u8bba\u7406\u8d44\u6e90', 'api': 'https://api.huosuapi.cc/api.php/provide/vod/'},
        's33': {'name': '\u563f\u563f\u8d44\u6e90', 'api': 'https://api.heiapi.cc/api.php/provide/vod/'},
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    def getName(self):
        return "\u5f71\u89c6+\u4e13\u5c5e\u5168\u7f51\u805a\u5408"

    def init(self, extend=""):
        pass

    def fetch(self, url, timeout=8):
        try:
            r = requests.get(
                url,
                headers=self.headers,
                timeout=timeout,
                verify=False
            )
            return r.text
        except Exception:
            return ""

    def clean_item(self, item, source_key, source_name, is_detail=False):
        item = dict(item)

        if not is_detail:
            item["vod_id"] = f"{source_key}@@{item.get('vod_id', '')}"

        remarks = item.get("vod_remarks", "")
        item["vod_remarks"] = f"{source_name} | {remarks}"

        if item.get("vod_play_from"):
            froms = item["vod_play_from"].split("$$$")
            froms = [f"{source_name}-{x}" for x in froms]
            item["vod_play_from"] = "$$$".join(froms)

        item.pop("vod_down_from", None)
        item.pop("vod_down_url", None)

        return item

    def homeContent(self, filter):
        classes = []
        filters = {}

        def load_class(key, source):
            url = f"{source['api']}?ac=list"
            html = self.fetch(url, 4)

            try:
                data = json.loads(html)
            except:
                data = {}

            vals = [{"n": "\u5168\u90e8(\u6700\u65b0)", "v": ""}]

            for c in data.get("class", []):
                vals.append({
                    "n": c.get("type_name", ""),
                    "v": c.get("type_id", "")
                })

            return key, vals

        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = []

            for key, source in self.sources.items():
                classes.append({
                    "type_id": key,
                    "type_name": source["name"]
                })

                futures.append(executor.submit(load_class, key, source))

            for future in as_completed(futures):
                try:
                    key, vals = future.result()

                    filters[key] = [{
                        "key": "cateId",
                        "name": "\u5206\u7c7b",
                        "value": vals
                    }]
                except:
                    pass

        return {
            "class": classes,
            "filters": filters,
            "list": []
        }

    def categoryContent(self, tid, pg, filter, extend):
        if tid not in self.sources:
            return {"list": []}

        source = self.sources[tid]

        cate_id = ""
        if isinstance(extend, dict):
            cate_id = extend.get("cateId", "")

        url = f"{source['api']}?ac=detail&pg={pg}"

        if cate_id:
            url += f"&t={cate_id}"

        html = self.fetch(url)

        try:
            data = json.loads(html)
        except:
            data = {}

        result = []

        for item in data.get("list", []):
            result.append(
                self.clean_item(
                    item,
                    tid,
                    source["name"],
                    False
                )
            )

        return {
            "list": result,
            "page": data.get("page", pg),
            "pagecount": data.get("pagecount", 1),
            "limit": data.get("limit", 20),
            "total": data.get("total", len(result))
        }

    def detailContent(self, ids):
        if isinstance(ids, list):
            ids = ids[0]

        if "@@" not in ids:
            return {"list": []}

        source_key, real_id = ids.split("@@", 1)

        if source_key not in self.sources:
            return {"list": []}

        source = self.sources[source_key]

        url = f"{source['api']}?ac=detail&ids={real_id}"

        html = self.fetch(url)

        try:
            data = json.loads(html)
        except:
            data = {}

        result = []

        for item in data.get("list", []):
            cleaned = self.clean_item(
                item,
                source_key,
                source["name"],
                True
            )

            cleaned["vod_id"] = ids

            result.append(cleaned)

        return {"list": result}

    def search_one(self, source_key, source, keyword, pg):
        url = f"{source['api']}?ac=detail&wd={keyword}&pg={pg}"

        html = self.fetch(url, 6)

        try:
            data = json.loads(html)
        except:
            data = {}

        result = []

        for item in data.get("list", []):
            result.append(
                self.clean_item(
                    item,
                    source_key,
                    source["name"],
                    False
                )
            )

        return {
            "list": result,
            "pagecount": data.get("pagecount", 1)
        }

    def searchContent(self, key, quick=False, pg=1):
        result = []
        max_page = 1

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []

            for source_key, source in self.sources.items():
                futures.append(
                    executor.submit(
                        self.search_one,
                        source_key,
                        source,
                        key,
                        pg
                    )
                )

            for future in as_completed(futures):
                try:
                    data = future.result()

                    result.extend(data["list"])

                    if data["pagecount"] > max_page:
                        max_page = data["pagecount"]

                except:
                    pass

        return {
            "list": result,
            "page": pg,
            "pagecount": max_page,
            "limit": 40,
            "total": 9999
        }

    def playerContent(self, flag, id, vipFlags):
        return {
            "parse": 0,
            "playUrl": "",
            "url": id,
            "header": self.headers
        }

    def localProxy(self, param):
        return [200, "text/plain", "ok"]


if __name__ == "__main__":
    Spider().run()
