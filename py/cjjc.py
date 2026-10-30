# -*- coding: utf-8 -*-
# \u4e13\u5c5e\u5168\u7f51\u805a\u5408 Python\u7248
# \u9002\u914d\u5e38\u89c1 Cat/TVBox Python Spider
#\u672c\u5730py\u9002\u914d  \ud83d\ude02  

import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from base.spider import Spider

# \u5b50\u6e90\u5931\u8d25\u8bb0\u5fc6\uff082026-10-30 \u63d0\u901f\uff09\uff1a\u8fde\u4e0d\u4e0a / \u8fd4\u56de\u7a7a \u2192 5 \u5206\u949f\u5185\u4e0d\u518d\u6253\u5b83\u3002
# \u8d77\u56e0\uff1a\u67d0\u4e00\u5b50\u6e90 DNS \u6302\u8d77\u65f6 requests \u7684 timeout \u7ba1\u4e0d\u5230\uff08\u5b9e\u6d4b s3 \u5355\u6e90\u5361 12s\uff09\uff0c
# \u5e76\u53d1\u8dd1\u5b8c\u5c31\u7b49\u540c\u6700\u6162\u90a3\u4e2a\uff0c\u628a\u6574\u4e2a\u9996\u9875\u62d6\u6210 12s\u3002
_DEAD_UNTIL = {}
_DEAD_TTL = 300
# \u5206\u7c7b\u8868\u7f13\u5b58\uff1a`?ac=list` \u8fd4\u56de\u7684\u662f\u5b50\u6e90\u5206\u7c7b\u6e05\u5355\uff0c\u51e0\u4e4e\u4e0d\u53d8\uff0c\u6ca1\u5fc5\u8981\u6bcf\u6b21\u5f00\u9996\u9875\u90fd\u91cd\u6458\u3002
# \u5b9e\u6d4b 26 \u4e2a\u5b50\u6e90\u91cc\u6700\u6162\u7684\u4e00\u4e2a\u8981 4.26s\uff0c\u7f13\u5b58\u540e\u6b21\u8f6e\u9996\u9875 \u22480s\u3002
_CLS_CACHE = {}
_CLS_TTL = 6 * 3600
# \u9996\u9875\u603b\u622a\u6b62\uff1a\u5230\u70b9\u5c31\u7528\u624b\u4e0a\u5df2\u6709\u7684\u5206\u7c7b\u8fd4\u56de\uff0c\u4e0d\u7b49\u5361\u4f4f\u7684\u5b50\u6e90\u3002
_HOME_DEADLINE = 4.0


class Spider(Spider):
    # 2026-10-30\uff1a\u5220 7 \u4e2a\u786e\u8ba4\u5df2\u6b7b\u5b50\u6e90\uff08\u57df\u540d\u8fc7\u671f / \u505c\u653e\u9875 / \u6e90\u7ad9 502\uff0c\u89c1\u4e0b\u65b9\u6ce8\u91ca\uff09
    sources = {
        's1': {'name': '\u674f\u5427\u8d44\u6e90', 'api': 'https://xingba111.com/api.php/provide/vod/'},
        's2': {'name': '\u6781\u54c1\u8d44\u6e90', 'api': 'https://jipinvip1.com/api.php/provide/vod/'},
        's4': {'name': '\u756a\u8304\u8d44\u6e90', 'api': 'https://fqzy.me//api.php/provide/vod/'},
        's5': {'name': '\u9ed1\u6599\u8d44\u6e90', 'api': 'https://heiliaozyapi.com/api.php/seaxml/vod/'},
        's6': {'name': '\u9ec4\u8272\u4ed3\u5e93', 'api': 'https://\u0068\u0073\u0063\u006bzy.vip/api.php/provide/vod/'},
        's8': {'name': '\u6843\u82b1\u8d44\u6e90', 'api': 'https://thzy1.me/api.php/provide/vod/'},
        's9': {'name': 'CK\u4f26\u7406\u8d44\u6e90', 'api': 'https://ckzy.me/api.php/provide/vod/'},
        's10': {'name': '\u5927\u5976\u5b50\u8d44\u6e90', 'api': 'https://apidanaizi.com/api.php/provide/vod/'},
        's11': {'name': '\u641cav\u8d44\u6e90', 'api': 'https://api.souavzyw.net/api.php/provide/vod/'},
        's12': {'name': '\u5965\u65af\u5361\u8d44\u6e90', 'api': 'https://aosikazy1.com/api.php/provide/vod/'},
        's13': {'name': '\u6ef4\u6ef4\u8d44\u6e90', 'api': 'https://api.ddapi.cc/api.php/provide/vod/at/json/'},
        's14': {'name': '\u8c46\u8c46\u8d44\u6e90', 'api': 'https://api.douapi.cc/api.php/provide/vod/'},
        's17': {'name': '\u68ee\u6797\u8d44\u6e90', 'api': 'https://slapibf.com/api.php/provide/vod/'},
        's18': {'name': '155\u8d44\u6e90', 'api': 'https://155api.com/api.php/provide/vod/'},
        's19': {'name': '\u4e50\u64ad\u8d44\u6e90', 'api': 'https://lbapi9.com/api.php/provide/vod/'},
        's20': {'name': '\u7389\u5154\u8d44\u6e90', 'api': 'https://apiyutu.com/api.php/provide/vod/'},
        's21': {'name': '\u756a\u53f7\u8d44\u6e90', 'api': 'http://fhapi9.com/api.php/provide/vod/'},
        's23': {'name': 'jkun\u8d44\u6e90', 'api': 'https://jkunzyapi.com/api.php/provide/vod/'},
        's24': {'name': '\u6e7f\u4e50\u56ed', 'api': 'https://xxavs.com/api.php/provide/vod/'},
        's25': {'name': '\u8d8a\u5357\u8d44\u6e90', 'api': 'https://www.vnzyz.com/api.php/provide/vod/'},
        's26': {'name': '\u7ea2\u6843\u89c6\u9891', 'api': 'https://apidanaizi.com/api.php/provide/vod/'},
        's27': {'name': '\u9e21\u5764\u8d44\u6e90', 'api': 'https://jkunzyapi.com/api.php/provide/vod/'},
        's29': {'name': 'lsb\u8d44\u6e90', 'api': 'https://apilsbzy1.com/api.php/provide/vod/'},
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
            hit = _CLS_CACHE.get(key)
            if hit and hit[0] > time.time():
                return key, hit[1]

            url = f"{source['api']}?ac=list"
            html = self.fetch(url, 5)

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

            if len(vals) <= 1:
                # \u6253\u4e0d\u901a / \u4e00\u4e2a\u5206\u7c7b\u90fd\u6ca1\u8fd4\u56de \u2192 \u8bb0 5 \u5206\u949f\uff0c\u4e0b\u8f6e\u76f4\u63a5\u8df3\u8fc7
                _DEAD_UNTIL[key] = time.time() + _DEAD_TTL
            else:
                _CLS_CACHE[key] = (time.time() + _CLS_TTL, vals)

            return key, vals

        now = time.time()
        # \u4e00\u6b21\u5168\u53d1\uff0c\u522b\u8ba9\u5b50\u6e90\u5728\u7ebf\u7a0b\u6c60\u91cc\u6392\u961f\uff08\u5206\u6279\u4f1a\u8ba9\u6700\u6162\u90a3\u4e2a\u4ece\u6392\u961f\u540e\u624d\u5f00\u59cb\u8ba1\u65f6\uff09
        executor = ThreadPoolExecutor(max_workers=max(8, len(self.sources)))
        futures = []

        for key, source in self.sources.items():
            classes.append({
                "type_id": key,
                "type_name": source["name"]
            })

            if _DEAD_UNTIL.get(key, 0.0) > now:
                # \u8bb0\u5fc6\u91cc\u8fd8\u6b7b\u7740 \u2192 \u53ea\u7ed9\u300c\u5168\u90e8(\u6700\u65b0)\u300d\uff0c\u4e0d\u53d1\u8bf7\u6c42
                filters[key] = [{
                    "key": "cateId",
                    "name": "\u5206\u7c7b",
                    "value": [{"n": "\u5168\u90e8(\u6700\u65b0)", "v": ""}]
                }]
                continue

            futures.append(executor.submit(load_class, key, source))

        # \u603b\u622a\u6b62\uff1await \u4e00\u5b9a\u5728 deadline \u8fd4\u56de\uff0c\u4e0d\u7b49\u5361\u4f4f\u7684\u5b50\u6e90\uff1b
        # shutdown(wait=False) \u8ba9\u540e\u53f0\u7ebf\u7a0b\u81ea\u5df1\u8dd1\u5b8c\uff0c\u522b\u628a\u9996\u9875\u5835\u5728\u8fd9\u91cc\u3002
        done, _ = wait(futures, timeout=_HOME_DEADLINE)
        for future in done:
            try:
                key, vals = future.result()

                filters[key] = [{
                    "key": "cateId",
                    "name": "\u5206\u7c7b",
                    "value": vals
                }]
            except:
                pass

        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except TypeError:
            executor.shutdown(wait=False)

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

        now = time.time()
        pairs = [(k, s) for k, s in self.sources.items()
                 if _DEAD_UNTIL.get(k, 0.0) <= now]

        executor = ThreadPoolExecutor(max_workers=max(8, len(pairs)))
        futures = [
            executor.submit(self.search_one, source_key, source, key, pg)
            for source_key, source in pairs
        ]

        # \u603b\u622a\u6b62\uff1a\u4e0e\u9996\u9875\u540c\u7406\uff0c\u522b\u88ab\u5355\u4e2a\u5361\u4f4f\u7684\u5b50\u6e90\u62d6\u6b7b\u641c\u7d22\uff08\u641c\u7d22\u65e0\u7ed3\u679c\u4e5f\u4e0d\u8bb0\u6b7b\uff09
        done, _ = wait(futures, timeout=8.0)
        for future in done:
            try:
                data = future.result()

                result.extend(data["list"])

                if data["pagecount"] > max_page:
                    max_page = data["pagecount"]

            except:
                pass

        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except TypeError:
            executor.shutdown(wait=False)

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
