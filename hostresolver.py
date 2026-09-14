# -*- coding: utf-8 -*-
"""
hostresolver.py \u2014\u2014 \u901a\u7528\u52a8\u6001\u57df\u540d\u89e3\u6790 v2.3\uff08\u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe + \u5019\u9009\u955c\u50cf\u5e76\u884c\u5b9e\u6d4b + \u6210\u529f\u7f13\u5b58\uff09

\u89e3\u51b3\uff1a\u5f71\u89c6\u7c7b\u7ad9\u70b9\u57df\u540d\u9891\u7e41\u8f6e\u6362\uff08\u6cdb\u5b50\u57df + \u53d1\u5e03\u9875\u52a8\u6001\u751f\u6210\uff09\uff0cpy \u6e90\u5185\u7f6e\u5019\u9009\u6c60\u6ede\u540e\u5931\u6548\u3002

v2 \u76f8\u5bf9 v1 \u7684\u6839\u56e0\u7ea7\u5347\u7ea7\uff1a
  1.\u3010\u6df1\u5ea6\u62bd\u94fe\u3011\u53d1\u5e03\u9875\u82e5\u628a\u5185\u5bb9\u85cf\u8fdb document.write(Base64.decode('...'))\uff08\u6bcf\u65e5\u5927\u8d5b/\u9ed1\u6599
     \u4e0d\u6253\u70ca\u540c\u6b3e\uff09\uff0c\u5148\u89e3\u7801\u518d\u626b\uff1b\u5e76\u8bc6\u522b\u300c\u968f\u673a\u8bcd + '.\u6cdb\u89e3\u6790\u57fa\u57df'\u300d\u751f\u6210\u7b97\u6cd5\uff08words.random()
     + '.xxx.cc'\uff09\uff0c\u81ea\u52a8\u6309\u8bcd\u8868\u751f\u6210 4 \u6761\u5019\u9009\u7ebf\u8def\u2014\u2014\u7ad9\u65b9\u6362\u57fa\u57df\u65f6\u53d1\u5e03\u9875\u89e3\u7801\u5373\u5f97\u65b0\u57df\uff0c\u5019\u9009\u6c60
     \u6c38\u4e0d\u8fc7\u671f\u3002
  2.\u3010\u5e76\u884c\u63a2\u6d4b\u3011\u5168\u90e8\u5019\u9009\u5e76\u53d1\u5b9e\u6d4b\uff08\u603b\u8017\u65f6\u2248\u5355\u6b21\u8d85\u65f6\uff0c\u4e0d\u518d\u4e32\u884c\u53e0\u52a0 8s\u00d7N\uff09\u3002
  3.\u3010\u6210\u529f\u7f13\u5b58\u3011\u9009\u7ad9\u7ed3\u679c\u7f13\u5b58 30 \u5206\u949f\uff0c\u540c\u4e00\u6b21\u4f1a\u8bdd\u5185\u91cd\u590d init \u4e0d\u518d\u63a2\u6d4b\uff0c\u79d2\u5f00\u3002
  4.\u3010\u5931\u8d25\u663e\u5f0f\u5316\u3011\u5168\u90e8\u5019\u9009\u5931\u8d25\u65f6\u8fd4\u56de ''\uff08\u4e0d\u56de\u9000\u6b7b\u57df\u9996\u9879\u9759\u9ed8\u7a7a\u8f6c\uff09\u3002\u8c03\u7528\u65b9\u5e94\u8ba9\u5404\u63a5\u53e3
     \u8d70\u81ea\u8eab try/except \u8fd4\u56de\u7a7a\u7ed3\u679c\uff0cApp \u7aef\u8868\u73b0\u4e3a\u660e\u786e\u7684\u5931\u8d25\u800c\u975e\u5047\u52a0\u8f7d\u3002

v2.3 \u76f8\u5bf9 v2 \u7684\u6839\u56e0\u7ea7\u5347\u7ea7\uff082026-09-11\uff0c\u56e0 91\u7206\u6599\u300c\u8f6c\u5708 50 \u79d2\u65e0\u5185\u5bb9\u300d\u590d\u76d8\uff09\uff1a
  5.\u3010\u7ebf\u8def\u8868\u62bd\u94fe\u3011\u7ad9\u65b9\u628a\u57fa\u57df\u6309\u884c\u585e\u8fdb**\u53cd\u5f15\u53f7\u6a21\u677f\u5b57\u7b26\u4e32**\uff0891\u7206\u6599 zz_line \u540c\u6b3e\uff1a
     var zz_line = `xndzecer.cc\ndgebtuip.cc\n...`\uff09\uff0c\u57fa\u57df\u672c\u8eab\u4e0d\u518d\u4ee5\u5b57\u9762\u91cf\u51fa\u73b0\u5728
     random() \u62fc\u63a5\u91cc\u2014\u2014_WILD_PAT \u5bf9\u6b64**\u62bd 0 \u6761**\u3002\u65b0\u589e\u6309\u884c/\u6309\u6570\u7ec4\u62bd\u53d6\u7ebf\u8def\u8868\u57fa\u57df\u3002
  6.\u3010\u53cc\u5f62\u6001\u5019\u9009\u3011\u6bcf\u4e2a\u57fa\u57df\u540c\u65f6\u751f\u6210 `{\u8bcd}.{\u57fa\u57df}`\uff08\u6cdb\u89e3\u6790\uff09\u4e0e\u88f8 `{\u57fa\u57df}`\uff08\u7ad9\u65b9\u56fa\u5b9a\u7ebf
     \u8def\u4e0d\u52a0\u524d\u7f00\uff09\uff0c\u4e0d\u518d\u53ea\u8d4c\u6cdb\u89e3\u6790\u4e00\u79cd\u5f62\u6001\u3002
  7.\u3010\u5185\u5bb9\u5f62\u6001\u5224\u3011\u65b0\u589e**\u6b63\u5411**\u5224\u636e\u300c\u50cf\u5185\u5bb9\u7ad9\u5417\u300d\uff08\u6709\u5185\u5bb9\u7ed3\u6784\u6807\u8bb0 / \u22655 \u6761\u5185\u5bb9\u578b\u5185\u94fe /
     \u9875\u9762 >80KB\uff09\u2014\u2014\u5b83\u624d\u662f\u5047\u95e8\u7ad9\u7684\u6b63\u89e3\u3002\u7ad9\u65b9\u5e38\u628a\u300c\u53d1\u5e03\u9875\u300d\u505a\u6210\u4e3b\u57df\u7684\u6d3b\u955c\u50cf
     \uff0851\u5403\u74dc advise.nlwkmsv.cc = 260KB \u5b8c\u6574\u7ad9\uff09\uff0c\u6240\u4ee5\u53d1\u5e03\u9875\u5730\u5740\u5217\u4e3a**\u9996\u9009\u5019\u9009**\u800c\u4e0d\u662f
     \u9884\u5148\u6392\u9664\uff1b\u53cd\u4f8b\u662f 51\u5403\u74dc 20KB \u7684\u300c\u65b0\u5730\u5740\u516c\u544a\u9875\u300d\uff08\u542b\u7ad9\u540d\u3001\u65e0\u5185\u5bb9\u7ed3\u6784\uff09\u4e0e
     \u6bcf\u65e5\u5927\u4e71\u6597 18KB \u7684\u95e8\u6237\u9875\uff0c\u90fd\u88ab\u5f62\u6001\u5224\u6321\u4e0b\u3002
  8.\u3010\u6821\u9a8c\u9ed8\u8ba4\u5316\u3011\u65b0\u589e site_key \u53c2\u6570\uff1bvalidate \u7f3a\u7701\u65f6\u81ea\u52a8\u6309\u7ad9\u540d\u751f\u6210\u6821\u9a8c\u51fd\u6570\u3002**\u4e0d\u4f20\u6821\u9a8c
     \u4e0d\u518d\u7b49\u4e8e\u4e0d\u6821\u9a8c**\uff08\u5f62\u6001\u5224\u59cb\u7ec8\u751f\u6548\uff09\u3002
  9.\u3010\u5e76\u884c\u515c\u5e95\u5bfc\u51fa\u3011probe_first() = \u5e76\u884c\u63a2\u6d4b\u9996\u6210\u529f\u5373\u8fd4\uff1b\u5404\u6e90\u539f\u6765\u7684 5\u00d78s \u4e32\u884c\u515c\u5e95\u5faa\u73af
     \u5e94\u6539\u7528\u5b83\uff0840s \u2192 8s\uff09\u3002
 10.\u3010\u53ef\u89c2\u6d4b\u3011last_trace() \u8fd4\u56de\u4e0a\u4e00\u6b21\u9009\u7ad9\u5168\u8fc7\u7a0b\u7684\u9010\u884c\u8bb0\u5f55\uff08\u53d1\u5e03\u9875\u6293\u53d6\u3001\u62bd\u5230\u7684\u57fa\u57df\u3001
     \u5019\u9009\u6e05\u5355\u3001\u6bcf\u4e2a\u5019\u9009\u7684\u5b9e\u6d4b\u7ed3\u679c\uff09\uff0c\u4f9b\u6e90\u5185\u300c\u8bca\u65ad\u300d\u680f\u76ee\u76f4\u63a5\u5c55\u793a\u3002

v2.4 \u76f8\u5bf9 v2.3 \u7684\u6839\u56e0\u7ea7\u5347\u7ea7\uff082026-09-13\uff0c\u56e0\u9ec4\u679c\u77ed\u5267\u300cpublish.js \u91cc\u7684\u65b0\u57fa\u57df\u5403\u4e0d\u5230\u300d\u590d\u76d8\uff09\uff1a
 11.\u3010\u53d1\u5e03\u9875\u5e76\u884c\u6293\u53d6\u3011\u591a\u53d1\u5e03\u9875\uff08\u7f51\u5740\u578b + GitHub \u578b + GitLab \u578b\u6df7\u7f16\uff09\u7531**\u9010\u9875\u4e32\u884c**\u6539\u4e3a
     \u5e76\u884c\uff08`_extract_pages`\uff09\uff1aN \u9875\u8017\u65f6\u4ece N\u00d7 \u964d\u4e3a \u2248max\u3002\u5408\u5e76\u987a\u5e8f\u4ecd\u6309 pages \u539f\u5e8f \u2192
     \u7ed3\u679c\u786e\u5b9a\uff0c\u4e0d\u53d7\u7ebf\u7a0b\u5b8c\u6210\u65f6\u5e8f\u5f71\u54cd\uff1b\u6bcf\u9875 trace \u72ec\u7acb\u6536\u96c6\u540e\u6309\u5e8f\u5199\u56de\uff08\u591a\u7ebf\u7a0b\u5199\u540c\u4e00
     _TRACE \u4f1a\u4e32\u884c\u4e71\u5e8f\uff09\u3002
 12.\u3010\u8ddf\u968f\u5916\u94fe JS\u3011\u53d1\u5e03\u9875\u5e38\u505a\u6210 **JS \u58f3**\uff08HTML \u53ea\u6709 `<div id=\"main\">` + 
     `<script src=\"publish.js\">`\uff0c\u9ec4\u679c pages.dev/github.io \u540c\u6b3e\uff09\u2014\u2014HTML \u62bd\u5230\u7684\u57fa\u57df\u4e3a 0\uff0c
     \u771f\u5b9e\u7ebf\u8def\uff08`urls=['xxx.cc/', ...]`\uff09\u5168\u5728\u90a3\u4e2a JS \u91cc\u3002\u65b0\u589e\uff1aHTML \u9636\u6bb5\u62bd\u4e0d\u5230\u57fa\u57df\u65f6\uff0c
     \u8ddf\u968f\u540c\u6e90\u5916\u94fe JS\uff08\u22643 \u4e2a\u3001\u22642MB\u3001\u5254\u7b2c\u4e09\u65b9 CDN\uff09\u518d\u626b\u4e00\u904d\u3002
 13.\u3010\u6570\u7ec4\u5bb9\u5fcd\u5c3e\u659c\u6760\u3011\u7ad9\u65b9\u6570\u7ec4\u5199\u6cd5\u662f `urls=['mvbessfgf.cc/', 'huxrzdjnv.cc/']`\uff08**\u5e26\u5c3e\u659c\u6760**\uff09\uff0c
     \u65e7 _ARR_PAT \u8981\u6c42\u6570\u7ec4\u5143\u7d20\u4e3a\u7eaf\u57df\u540d \u2192 \u62bd 0 \u6761\u3002\u73b0\u5141\u8bb8\u5143\u7d20\u5c3e\u90e8 `/`\u3002
     \uff08`urls[randomNum(0,urls.length-1)]` \u8fd9\u79cd**\u53d8\u91cf\u5f15\u7528**\u5f62\u6001\u65e0\u9700\u5355\u72ec\u89e3\u6790\u2014\u2014\u6570\u7ec4\u672c\u4f53
      \u5df2\u88ab\u62bd\u51fa\uff0c\u57fa\u57df\u5373\u6570\u7ec4\u503c\u3002\uff09

\u8c03\u7528\u65b9\uff08\u5404 py \u6e90\uff09\u53ea\u9700\u58f0\u660e\uff1a
  PUBLISH_PAGE = 'https://xxx.xxx/'          # \u7a33\u5b9a\u53d1\u5e03\u9875\uff08\u53ef\u7a7a\uff09
  CANDIDATE_HOSTS = ['https://a/', ...]      # \u5df2\u77e5\u955c\u50cf\uff0c\u6309\u5b58\u6d3b\u6392\u5e8f
  self.host = resolve_host(PUBLISH_PAGE, CANDIDATE_HOSTS, headers=..., proxies=...,
                           site_key='\u7ad9\u540d')   # site_key \u5f3a\u70c8\u5efa\u8bae\u4f20\uff0c\u7f3a\u7701\u9000\u56de\u5f62\u6001\u5224
  # \u8fd4\u56de\u53ef\u80fd\u662f ''\uff0c\u8c03\u7528\u65b9\u63a5\u53e3\u5c42 try/except \u515c\u4f4f\u5373\u53ef

ext \u673a\u5236\uff08\u5f71\u89c6.json \u7ad9\u70b9\u6761\u76ee ext \u5b57\u6bb5\uff0cgitee \u7f51\u9875\u53ef\u76f4\u63a5\u6539\uff09\uff1a
  \u6587\u672c: publish@https://a,https://b;hosts@https://c,https://d;host@https://e;mail@x@y.com
  JSON: {\"publish\":[\"...\"],\"hosts\":[\"...\"],\"host\":\"...\",\"mails\":[\"...\"],\"proxies\":{...}}
  - host@   \u9501\u5b9a\u4e3b\u9875\uff08\u6700\u9ad8\u4f18\u5148\u7ea7\uff0c\u8df3\u8fc7\u4e00\u5207\u63a2\u6d4b\uff0c\u7ad9\u70b9\u7ed3\u6784\u5927\u6539\u65f6\u7528\uff1b**\u53ea\u8ba4\u4e00\u4e2a**\uff09
  - publish@ \u53d1\u5e03\u9875\u5730\u5740\uff082026-09-13 \u8d77**\u53ef\u591a\u4e2a**\uff1a\u9017\u53f7\u5206\u9694\uff0c\u5982 \u7f51\u5740\u578b + GitHub \u578b\u5e76\u5b58\uff1b
             **\u5e76\u884c**\u6293\u53d6\u3001\u7ed3\u679c\u6309\u586b\u5199\u987a\u5e8f\u5408\u5e76\u2014\u2014\u4e00\u4e2a\u6302\u4e86\u4e0d\u5f71\u54cd\u53e6\u4e00\u4e2a\uff0c\u8017\u65f6\u4e0d\u53e0\u52a0\uff09
  - hosts@  \u65b0\u589e\u5019\u9009\u955c\u50cf\uff08\u5b9e\u6d4b\u987a\u5e8f\u4ec5\u6392\u5728\u53d1\u5e03\u9875\u6cdb\u89e3\u6790\u5019\u9009\u4e4b\u540e\uff09
  - mail@   \u90ae\u7bb1\u6e20\u9053\uff08\u53ef\u591a\u4e2a\uff1b\u6e90\u4fa7\u4e0d\u6d88\u8d39\uff0c\u4f9b\u7ba1\u7406\u53f0/\u624b\u673a\u7aef\u53ef\u8bfb\u53ef\u590d\u5236\uff0c\u5931\u8054\u65f6\u4eba\u5de5\u53d1\u4fe1\u53d6\u65b0\u5740\uff09
"""
import re
import time
import random
import base64
from urllib.parse import urljoin

try:
    import requests
except Exception:
    requests = None

try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
except Exception:
    ThreadPoolExecutor = None
    as_completed = None

# ---------------------------------------------------------------- \u7f13\u5b58
_CACHE = {}
_CACHE_TTL = 1800  # \u6210\u529f\u9009\u7ad9\u7f13\u5b58 30 \u5206\u949f

# \u9009\u7ad9\u8fc7\u7a0b\u8bb0\u5f55\uff08\u4f9b\u6e90\u5185\u300c\u8bca\u65ad\u300d\u680f\u76ee\u5c55\u793a\uff0cApp \u7aef\u65e0\u9700\u65e5\u5fd7\u5de5\u5177\u5373\u53ef\u770b\u5230\u5168\u94fe\u8def\uff09
_TRACE = []


def _tr(msg):
    """\u8ffd\u52a0\u4e00\u884c\u9009\u7ad9\u8fc7\u7a0b\u8bb0\u5f55\uff08\u4e0a\u9650 60 \u884c\uff0c\u9632\u9875\u9762\u4e0a\u5237\u5c4f\uff09"""
    try:
        if len(_TRACE) < 60:
            _TRACE.append(str(msg))
    except Exception:
        pass


def last_trace():
    """\u8fd4\u56de\u4e0a\u4e00\u6b21\u9009\u7ad9\u7684\u9010\u884c\u8bb0\u5f55\uff08\u526f\u672c\uff09"""
    return list(_TRACE)


def clear_cache():
    """\u6e05\u7a7a\u9009\u7ad9\u7f13\u5b58\uff08\u8c03\u8bd5\u7528\uff1b\u8c03\u7528\u65b9\u4e00\u822c\u4e0d\u9700\u8981\uff09"""
    _CACHE.clear()
    del _TRACE[:]


# ---------------------------------------------------------------- ext \u89e3\u6790
def parse_ext(ext_str):
    """\u89e3\u6790\u5f71\u89c6.json \u7ad9\u70b9\u6761\u76ee\u7684 ext \u5b57\u6bb5\uff08\u6587\u672c\u683c\u5f0f\uff0c\u5206\u53f7\u5206\u9694 @ \u952e\u503c\uff09\u3002
    \u65e0\u6cd5\u8bc6\u522b\u7684\u7247\u6bb5\u81ea\u52a8\u5ffd\u7565\uff1b\u89e3\u6790\u5931\u8d25\u8fd4\u56de {}\uff08py \u56de\u9000\u5185\u7f6e\u9ed8\u8ba4\u503c\uff0c\u4e0d\u4f1a\u5d29\u6e90\uff09\u3002"""
    out = {}
    for part in str(ext_str or '').split(';'):
        part = part.strip()
        if not part or '@' not in part:
            continue
        k, _, v = part.partition('@')
        k = k.strip().lower()
        v = v.strip().rstrip('/')
        if not v:
            continue
        if k == 'hosts':
            items = [x.strip().rstrip('/') for x in v.split(',') if x.strip()]
            if items:
                out.setdefault('hosts', []).extend(items)
        elif k == 'publish':
            # \u591a\u53d1\u5e03\u9875\uff082026-09-13 \u7528\u6237\u5b9a\uff1a\u7f51\u5740\u578b + GitHub \u578b\u7b49\u53ef\u5e76\u5b58\uff09\uff1a
            # `publish@a,b` \u9017\u53f7\u5206\u9694\uff1b\u5199\u6210\u4e24\u6761 publish@ \u4e5f\u7d2f\u52a0\uff0c\u4e0d\u4e92\u76f8\u8986\u76d6\u3002
            # \u5bf9\u5916\u4ecd\u662f**\u4e00\u4e2a\u9017\u53f7\u4e32**\u2014\u2014\u5404\u6e90\u7167\u65e7 `ext.get('publish') or ''` \u53d6\u7528\uff0c
            # \u7531 resolve_host \u5185\u90e8\u62c6\u5206\uff0c\u6545\u6240\u6709\u5df2\u4e0a\u7ebf\u6e90\u96f6\u6539\u52a8\u3002
            items = [x.strip().rstrip('/') for x in v.split(',') if x.strip()]
            if items:
                cur = [x for x in (out.get('publish') or '').split(',') if x]
                out['publish'] = ','.join(dict.fromkeys(cur + items))
        elif k == 'mail':
            # \u90ae\u7bb1\u6e20\u9053\uff082026-09-13 \u65b0\u589e\uff09\uff1a`mail@a@x.com,b@y.com`\u3002\u6e90\u4fa7\u4e0d\u6d88\u8d39\uff0c
            # \u4f9b\u7ba1\u7406\u53f0/\u624b\u673a\u7aef\u53ef\u8bfb\u53ef\u590d\u5236\uff08\u5931\u8054\u65f6\u4eba\u5de5\u53d1\u4fe1\u53d6\u65b0\u5740\uff09\u3002
            items = [x.strip() for x in v.split(',') if x.strip()]
            if items:
                out.setdefault('mails', []).extend(items)
        elif k == 'host':
            out[k] = v
    return out


def ext_of(extend):
    """App \u4f20\u7ed9 Spider.init() \u7684 extend \u7edf\u4e00\u89e3\u6790\u5165\u53e3\u3002
    \u517c\u5bb9 None / dict(JSON) / str(\u6587\u672c\u6216JSON)\u3002\u4efb\u4f55\u5f02\u5e38\u8fd4\u56de {}\uff08\u4e0d\u5d29\u6e90\uff09\u3002"""
    import json as _json
    try:
        if not extend:
            return {}
        if isinstance(extend, dict):
            out = {}
            for k in ('publish', 'host'):
                if extend.get(k):
                    v = extend[k]
                    if k == 'publish' and isinstance(v, (list, tuple)):
                        v = ','.join(str(x).strip() for x in v if str(x).strip())
                    out[k] = str(v).strip()
            if extend.get('hosts'):
                hs = extend['hosts'] if isinstance(extend['hosts'], list) else [extend['hosts']]
                out['hosts'] = [str(h).strip() for h in hs if str(h).strip()]
            ms = extend.get('mails') or extend.get('mail')
            if ms:
                ms = ms if isinstance(ms, list) else [ms]
                out['mails'] = [str(m).strip() for m in ms if str(m).strip()]
            return out
        s = str(extend).strip()
        if not s:
            return {}
        try:
            cfg = _json.loads(s)
            if isinstance(cfg, dict):
                return ext_of(cfg)
        except Exception:
            pass
        return parse_ext(s)
    except Exception:
        return {}


# ---------------------------------------------------------------- \u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe
# \u6cdb\u89e3\u6790\u968f\u673a\u8bcd\u6c60\uff08\u4e0e\u7ad9\u65b9\u53d1\u5e03\u9875\u540c\u6e90\u53d6\u5e38\u7528\u82f1\u6587\u8bcd\uff1b\u6cdb\u89e3\u6790 DNS \u4e0b\u4efb\u610f\u8bcd\u5747\u53ef\u89e3\u6790\uff09
_WILD_WORDS = (
    'abandon,ability,able,above,absence,accept,access,achieve,across,action,active,'
    'actual,adapt,address,adjust,admit,adopt,adult,advance,advice,afford,afraid,'
    'after,again,against,agency,agent,agree,ahead,airline,airport,album,alcohol,'
    'alive,allow,almost,alone,already,always,amazing,among,amount,ancient,another,'
    'answer,anxiety,anyone,anyway,apart,appear,apple,apply,approve,area,argue,'
    'around,arrange,arrive,article,artist,aspect,assault,assess,asset,assign,'
    'assist,assume,assure,athlete,attack,attempt,attend,attract,author,average,'
    'avoid,award,aware,baby,balance,ball,band,bank,barely,barrel,barrier,base,'
    'basic,basket,battle,beach,beauty,because,become,before,behind,being,belief,'
    'believe,belong,below,bench,beneath,benefit,beside,best,better,between,beyond,'
    'bible,bike,bill,billion,bind,bird,birth,bite,black,blade,blame,blanket,blind,'
    'block,blood,blow,blue,board,boat,body,bomb,bond,bone,book,boom,boot,border,'
    'born,borrow,boss,both,bottle,bottom,bowl,box,brain,branch,brand,bread,break,'
    'breath,breathe,brick,bridge,brief,bright,bring,broad,broken,brother,brown,'
    'brush,budget,build,bullet,bunch,burden,burn,bury,bus,busy,butter,buyer,'
    'cabin,cable,cake,call,camera,campus,cancer,capable,capital,captain,capture,'
    'carbon,card,career,careful,carrier,carry,case,cash,cast,catch,cause,ceiling,'
    'cell,center,central,century,certain,chain,chair'
).split(',')

# \u300c\u968f\u673a\u8bcd + '.\u6cdb\u89e3\u6790\u57fa\u57df'\u300d\u751f\u6210\u7b97\u6cd5\uff08\u5982 words.random() + '.iljzezhab.cc'\uff09
_WILD_PAT = re.compile(
    r"[\w.]*random\s*\(\s*\)\s*\+\s*['\"]\.([a-z0-9-]+(?:\.[a-z0-9-]+)+)['\"]", re.I)
# \u53d1\u5e03\u9875 b64 \u58f3\uff08document.write(Base64.decode('...')) \u6574\u9875 HTML \u85cf base64\uff09
_B64_SHELL_PAT = re.compile(r"Base64\.decode\(\s*['\"]([A-Za-z0-9+/=]{100,})['\"]")
# v2.3 \u7ebf\u8def\u8868\uff08\u57fa\u57df\u88ab\u85cf\u8fdb\u6a21\u677f\u5b57\u7b26\u4e32 / \u6570\u7ec4\uff0c\u4e0d\u518d\u4ee5 random()+'.\u57fa\u57df' \u5f62\u6001\u51fa\u73b0\uff09
_TICK_PAT = re.compile(r'`([^`]{4,800})`', re.S)
# v2.5 \u7ebf\u8def\u8868\u7b2c\u4e09\u79cd\u5f62\u6001\uff082026-09-14 \u00b7 91\u7206\u6599\u771f\u673a\u5931\u8054\u5b9e\u6d4b\u63ea\u51fa\uff09\uff1a**\u5f15\u53f7\u4e32 + \u6362\u884c**\u2014\u2014
#   var zz_line = "gdubugsu.cc\ncekzqgmk.cc\nd3f9.cloudfront.net";
# \u65e7\u7248\u53ea\u8ba4\u53cd\u5f15\u53f7\u6a21\u677f \u2192 \u6b64\u5f62\u6001\u6574\u7ec4\u62bd 0 \u6761\uff1ab64 \u58f3\u660e\u660e\u89e3\u5f00\u4e86\uff0c\u57fa\u57df\u4ecd\u7136\u770b\u4e0d\u89c1\uff08\u6362\u4e0d\u5230\u57df\uff09\u3002
# \u26a0\u5fc5\u987b**\u951a\u5b9a**\uff08\u57df\u540d+\u6362\u884c+\u57df\u540d\uff09\u800c\u4e0d\u80fd\u7528\u300c\u901a\u7528\u5f15\u53f7\u914d\u5bf9\u300d\u626b\u5168\u9875\uff1a\u5b9e\u6d4b 91\u7206\u6599 \u89e3\u7801\u9875\u6709
#  424 \u4e2a\u5f15\u53f7\u4e32\uff0c\u901a\u7528\u914d\u5bf9\u4f1a\u88ab\u9875\u9996 attr \u8c10\u97f3\u4e32\uff08zh-CN / UTF-8 / X-UA-Compatible\uff09\u6574\u4f53\u9519\u4f4d\uff0c
#  \u771f\u6b63\u7684 zz_line \u4e32\u6c38\u8fdc\u8f6e\u4e0d\u5230 \u2014\u2014 \u8be5\u5199\u6cd5\u5f53\u5929\u5df2\u88ab\u8bc1\u4f2a\u3002
_QUOTED_TABLE_PAT = re.compile(
    r"""['"`]("""
    r"""[a-z0-9][a-z0-9.-]*\.[a-z]{2,15}"""
    r"""(?:(?:\\r\\n|\\n|\r\n|\n)[a-z0-9][a-z0-9.-]*\.[a-z]{2,15})+"""
    r"""(?:\\r\\n|\\n|\r\n|\n)?"""
    r""")['"`]""",
    re.I)
_DOMLINE_PAT = re.compile(r'^[a-z0-9][a-z0-9.-]*\.[a-z]{2,15}$', re.I)
# v2.5 TLD \u767d\u540d\u5355\uff1a\u7ebf\u8def\u8868\u884c\u5c3e\u5fc5\u987b\u843d\u5728**\u771f\u5b9e TLD**\u4e0a\u3002\u65e7\u7248 `[a-z]{2,15}` \u592a\u5bbd\uff0c
# \u4f1a\u628a JS \u5bf9\u8c61\u5c5e\u6027\u4e32\u5f53\u57df\u540d\u62bd\u51fa\uff08\u7389\u7f9e\u56ed \u5b9e\u6d4b\u62bd\u5230 ui.loading.render / ui.router.router /
# ui.close \u2014\u2014 \u5168\u662f JS \u547d\u540d\u7a7a\u95f4\uff0c\u767d\u5360\u63a2\u6d3b\u540d\u989d\u3001\u628a\u771f\u5019\u9009\u6324\u51fa\u53bb\uff09\u3002
_TLD_OK = frozenset((
    'cc com net org cn tv io co me top xyz vip app link click info site online '
    'icu club fun store live shop work sbs cfd dev pro space website press host '
    'art name biz mobi asia wiki news blog ltd group tech cloud world today life '
    'us uk jp kr hk tw sg de fr nl ru in id my th vn ph au ca it es pl se no fi'
).split())
# \u6570\u7ec4\u5143\u7d20**\u5141\u8bb8\u5c3e\u90e8 / **\uff082026-09-13 v2.4\uff09\uff1a\u7ad9\u65b9\u5199\u4f5c urls=['mvbessfgf.cc/','huxrzdjnv.cc/']
# \u2014\u2014\u5c3e\u659c\u6760\u5f88\u5e38\u89c1\uff0c\u65e7\u6b63\u5219\u8981\u6c42\u7eaf\u57df\u540d \u2192 \u6574\u7ec4\u62bd 0 \u6761\uff08\u9ec4\u679c publish.js \u5c31\u662f\u8fd9\u5f62\u6001\uff09\u3002
# **\u7ec4\u5916\u5fc5\u987b\u5bb9\u5c3e\u7a7a\u767d**\uff082026-09-13 \u5b9e\u6d4b\u63ea\u51fa\uff09\uff1a\u771f\u5b9e\u5199\u6cd5\u662f\u591a\u884c\u6570\u7ec4\u3001\u672b\u5143\u7d20\u540e\u8fd8\u6709 `,\n]`\uff0c
# \u65e7\u5f0f `...,?)\]` \u8981\u6c42 `]` \u7d27\u8ddf\u6700\u540e\u4e00\u4e2a\u5143\u7d20 \u2192 \u8de8\u884c\u6570\u7ec4\u5168\u6570\u6f0f\u62bd\uff08\u5355\u884c\u624d\u78b0\u5de7\u80fd\u8fc7\uff09\u3002
_ARR_PAT = re.compile(
    r'\[((?:\s*[\'"][a-z0-9.-]*\.[a-z]{2,15}/?[\'"]\s*,?)+)\s*\]', re.I)
# v2.4 JS \u58f3\u8ddf\u968f\uff1a\u53d1\u5e03\u9875\u628a\u5185\u5bb9\u653e\u8fdb\u5916\u94fe JS\uff08<div id="main"> + <script src="publish.js">\uff09
_JS_SRC_PAT = re.compile(r'<script[^>]+src\s*=\s*["\']([^"\']+)["\']', re.I)
_MAX_JS_PAGES = 3                     # \u6bcf\u4e2a\u53d1\u5e03\u9875\u6700\u591a\u8ddf\u968f\u51e0\u4e2a\u5916\u94fe JS
_MAX_JS_BYTES = 2 * 1024 * 1024       # \u5355\u4e2a JS \u622a\u65ad\u4e0a\u9650\uff08\u9632\u70b8\u5185\u5b58\uff09
# \u53d1\u5e03\u9875\u91cc\u5fc5\u7136\u6df7\u5165\u7684\u7b2c\u4e09\u65b9\u5927\u5e73\u53f0/\u7edf\u8ba1/\u5e7f\u544a\u57df\u2014\u2014\u63a2\u6d4b\u5b83\u4eec\u4f1a\u628a\u5927\u9875\u9762\u8bef\u5224\u6210"\u7ad9\u70b9\u53ef\u7528"
_JUNK_HOST_PAT = re.compile(
    r'(googletagmanager|google-analytics|googleads|gstatic|google\.|gitlab\.|github\.|'
    r'youtube\.|ytimg\.|twitter\.|x\.com|t\.me|telegram\.|addtoany\.|yandex\.|'
    r'browsehappy|schema\.org|w3\.org|qq\.com|apple\.com|bing\.com|baidu\.com|'
    r'magsrv\.|adsrv|ad-provider|chnsrv|stripchat|jsdelivr|unpkg|npmjs|shields\.io|'
    r'699pic|meituan|fontawesome|jquery|bootstrap)', re.I)


def _host_of(url):
    """\u53d6 URL \u7684 host\uff08\u5c0f\u5199\u3001\u65e0\u7aef\u53e3\u534f\u8bae\uff09\uff0c\u5931\u8d25\u8fd4\u56de ''"""
    m = re.match(r'https?://([^/:?#\s]+)', str(url or ''), re.I)
    return m.group(1).lower() if m else ''


def _is_junk(cand):
    return bool(_JUNK_HOST_PAT.search(_host_of(cand) or cand or ''))


# v2.31\uff1a\u5185\u5bb9\u5f62\u6001**\u6b63\u5411**\u5224\u636e\uff082026-09-11 51\u5403\u74dc\u590d\u76d8\u65b0\u589e\uff09
# \u80cc\u666f\uff1a51\u5403\u74dc \u6709\u4e00\u4e2a 20KB \u7684\u300c\u65b0\u5730\u5740\u516c\u544a\u9875\u300d\uff08401.dzyeamwh.cc\uff09\uff0c\u6b63\u6587\u542b\u7ad9\u540d\u3001\u80fd\u88ab
# \u7ad9\u540d\u6821\u9a8c\u653e\u8fc7\uff0c\u4f46\u6ca1\u6709\u4efb\u4f55\u5185\u5bb9\u7ed3\u6784\u2014\u2014\u9009\u4e2d\u5b83 \u2192 \u5206\u7c7b\u53ea\u6709 3 \u4e2a\u3001\u5217\u8868\u5168\u7a7a\uff0c
# \u6b63\u662f\u300c\u8fde\u5206\u7c7b\u90fd\u5237\u4e0d\u51fa\u6765\u300d\u3002\u6545\u5728\u7ad9\u540d\u6821\u9a8c\u4e4b\u4e0a\u518d\u8981\u6c42\u300c\u50cf\u5185\u5bb9\u7ad9\u300d\u3002
# \u6ce8\uff1av2.3 \u521d\u7248\u8fd8\u5199\u8fc7\u4e00\u4e2a**\u5426\u5b9a\u5f0f**\u5224\u636e _looks_like_nav\uff08\u5916\u94fe\u591a=\u5bfc\u822a\u9875\uff09\uff0c
#     \u540c\u65e5\u5373\u5220\u2014\u2014\u5b83\u5bf9\u7981\u7247\u5929\u5802\uff08oneVideo \u5361\u7247\u3001\u65e0 <article> \u5b57\u9762\u6807\u8bb0\uff09\u8bef\u6740\u3002
#     \u540c\u4e00\u4ef6\u4e8b\u53ea\u7559\u4e00\u4e2a\u6b63\u5411\u5224\u636e\u3002
_CONTENT_MARKS = ('<article', 'post-card', 'video-item', 'oneVideo', 'entry-title',
                  'post-title', 'vod-img', 'vod-txt', 'playlist', 'class="video')
_CONTENT_LINK_PAT = re.compile(
    r'href=["\'][^"\']*/(?:archives?|video|videos|category|categories|post|vod|'
    r'watch|tag|detail|thread|topic|tag_list)[/"\']', re.I)


def _looks_like_content(text):
    """\u50cf\u5185\u5bb9\u7ad9\u5417\uff1a\u6709\u5185\u5bb9\u7ed3\u6784\u6807\u8bb0 / \u6709 \u22655 \u6761\u5185\u5bb9\u578b\u5185\u94fe / \u9875\u9762\u591f\u5927\uff08>80KB\uff09\u3002
    \u5047\u95e8\u7ad9\uff08\u516c\u544a\u9875/\u5bfc\u822a\u9875\uff09\u4e09\u6761\u5168\u4e0d\u6ee1\u8db3\u3002"""
    t = text or ''
    if any(k in t for k in _CONTENT_MARKS):
        return True
    if len(_CONTENT_LINK_PAT.findall(t)) >= 5:
        return True
    return len(t) > 80000


def _expand_b64_shells(text):
    """\u5c55\u5f00\u53d1\u5e03\u9875\u91cc\u7684 Base64 \u58f3\uff0c\u8fd4\u56de [\u539f\u6587, \u89e3\u7801\u98751, \u89e3\u7801\u98752...]"""
    texts = [text]
    for m in _B64_SHELL_PAT.finditer(text):
        try:
            texts.append(base64.b64decode(m.group(1)).decode('utf-8', 'ignore'))
        except Exception:
            continue
    return texts


def _domlines(body):
    """\u628a\u4e00\u6bb5\u300c\u7ebf\u8def\u8868\u300d\u6587\u672c\u5207\u6210\u88f8\u57df\u540d\u884c\u3002

    \u5bb9\u5fcd\uff1a\u771f\u6362\u884c / **\u5b57\u9762 `\\n`**\uff08JS \u53cc\u5f15\u53f7\u4e32\u91cc\u5199\u4f5c `\\n`\uff0cPython \u4fa7\u662f\u53cd\u659c\u6760+n \u4e24\u5b57\u7b26\uff09/
    `\\r\\n` / \u884c\u5c3e\u9017\u53f7 / \u884c\u9996\u5c3e\u5f15\u53f7 / \u884c\u5c3e\u659c\u6760\u3002
    \u8fd4\u56de\u5408\u6cd5\u57df\u540d\u884c\uff1b\u4e0d\u8db3 2 \u884c\u3001\u6216\u4efb\u4e00\u884c\u4e0d\u662f\u7eaf\u57df\u540d \u2192 []\uff08\u5b81\u7f3a\u52ff\u6ee5\uff0c\u9632\u628a\u6b63\u6587\u5f53\u7ebf\u8def\u8868\uff09\u3002"""
    s = (body or '').replace('\\r\\n', '\n').replace('\\n', '\n').replace('\r', '\n')
    lines = []
    for l in s.split('\n'):
        l = l.strip().strip(',').strip('"\'').strip().rstrip('/').strip()
        if l:
            lines.append(l)
    if len(lines) < 2 or not all(_DOMLINE_PAT.match(l) for l in lines):
        return []
    return [l for l in lines if l.rsplit('.', 1)[-1].lower() in _TLD_OK]


def extract_line_bases(text):
    """\u7ad9\u65b9\u300c\u7ebf\u8def\u8868\u300d\u57fa\u57df\u62bd\u53d6\uff08v2.3 \u65b0\u589e\uff0cv2.5 \u8865\u7b2c\u4e09\u5f62\u6001\uff09\u3002

    \u4e09\u7c7b\u5f62\u6001\uff08\u4e0e _WILD_PAT \u4e92\u8865\u2014\u2014_WILD_PAT \u6293\u300c\u5b57\u9762\u91cf .\u57fa\u57df\u300d\uff0c
    \u672c\u51fd\u6570\u6293\u300c\u57fa\u57df\u672c\u4f53\u88ab\u585e\u8fdb\u6a21\u677f\u4e32/\u5f15\u53f7\u4e32/\u6570\u7ec4\u3001\u524d\u7f00\u5728\u8fd0\u884c\u65f6\u624d\u62fc\u300d\uff09\uff1a
      \u2460 \u53cd\u5f15\u53f7\u6a21\u677f\u5185\u6309\u884c\u6392\u5217\u7684\u88f8\u57df\u540d\uff08\u6a21\u677f\u4e32\u91cc\u662f\u771f\u6362\u884c\uff09\uff1a
         var zz_line = `xndzecer.cc\\ndgebtuip.cc\\nd3f9.cloudfront.net`;
      \u2461 \u5f15\u53f7\u4e32 + \u5b57\u9762 `\\n`\uff08v2.5\uff0c91\u7206\u6599\u73b0\u7f51\u5199\u6cd5\uff09\uff1a
         var zz_line = \"gdubugsu.cc\\ncekzqgmk.cc\\nd3f9.cloudfront.net\";
      \u2462 JS \u6570\u7ec4\u5b57\u9762\u91cf\u91cc\u7684\u88f8\u57df\u540d\u4e32\uff1a['a.cc','b.cc']
    \u8fd4\u56de\u57fa\u57df\u5217\u8868\uff08\u65e0\u534f\u8bae\u3001\u4fdd\u5e8f\u53bb\u91cd\u3001\u5df2\u5254\u7b2c\u4e09\u65b9\u57df\u4e0e\u975e\u6cd5 TLD\uff09\u3002"""
    out, text = [], text or ''
    for m in _TICK_PAT.finditer(text):
        out += _domlines(m.group(1))
    for m in _QUOTED_TABLE_PAT.finditer(text):
        body = m.group(1)
        # \u53ea\u5904\u7406\u5e26\u6362\u884c\u8bed\u4e49\u7684\u4e32\uff08\u5b57\u9762 \n \u6216\u771f\u6362\u884c\uff09\uff1b\u666e\u901a\u5355\u884c\u5f15\u53f7\u4e32\u76f4\u63a5\u8df3\u8fc7\uff0c
        # \u514d\u5f97\u628a\u6ee1\u9875 JS \u5b57\u7b26\u4e32\u5168\u5582\u8fdb _domlines\uff08\u6027\u80fd + \u8bef\u62bd\u53cc\u4fdd\u9669\uff09\u3002
        if '\\n' not in body and '\n' not in body:
            continue
        out += _domlines(body)
    for m in _ARR_PAT.finditer(text):
        # \u5143\u7d20\u53ef\u5e26\u5c3e\u659c\u6760\uff08['a.cc/', 'b.cc/']\uff09\u2014\u2014v2.4 \u8d77\u5bb9\u5fcd
        items = re.findall(r'[\'"]([a-z0-9.-]*\.[a-z]{2,15})/?[\'"]', m.group(1), re.I)
        if len(items) >= 2:
            out += items
    return [b for b in dict.fromkeys(out)
            if not _JUNK_HOST_PAT.search(b) and b.rsplit('.', 1)[-1].lower() in _TLD_OK]


def _scan_text(t, static, wilds):
    """\u4ece\u4e00\u6bb5\u6587\u672c\u62bd\u5019\u9009\uff08\u9759\u6001\u955c\u50cf\u94fe\u63a5\u8fdb static\u3001\u57fa\u57df\u8fdb wilds\uff09\u3002
    HTML \u672c\u4f53 / b64 \u89e3\u7801\u9875 / \u5916\u94fe JS \u4e09\u79cd\u6765\u6e90\u5171\u7528\u540c\u4e00\u5957\u5224\u636e\u3002"""
    t = t or ''
    for l in re.findall(r'href=["\'](https?://[^"\']+)["\']', t, re.I):
        m = re.match(r'https?://([a-z0-9.-]+\.[a-z]{2,})', l, re.I)
        if m and not _JUNK_HOST_PAT.search(m.group(1)):
            static.append('https://' + m.group(1))
    for m in _WILD_PAT.finditer(t):
        wilds.add(m.group(1))
    for b in extract_line_bases(t):
        wilds.add(b)


def _fetch_text(url, headers, proxies, timeout, cap=_MAX_JS_BYTES):
    """GET \u53d6\u6587\u672c\uff08\u5931\u8d25/\u975e 200 \u2192 ''\uff09\uff1b\u8d85 cap \u622a\u65ad\u3002\u7528\u4e8e\u8ddf\u968f\u5916\u94fe JS\u3002"""
    if requests is None or not url:
        return ''
    try:
        r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout,
                         verify=False, allow_redirects=True)
        if r.status_code != 200:
            return ''
        t = r.text or ''
        return t if len(t) <= cap else t[:cap]
    except Exception:
        return ''


def _js_candidates(html, base_url):
    """\u53d1\u5e03\u9875\u91cc\u7684\u5916\u94fe JS\uff08JS \u58f3\u8ddf\u968f\u7528\uff09\u3002\u76f8\u5bf9\u8def\u5f84\u6309\u53d1\u5e03\u9875\u5730\u5740\u8865\u5168\uff1b
    \u5254\u7b2c\u4e09\u65b9 CDN/\u7edf\u8ba1\u57df\uff0c\u4fdd\u5e8f\u53bb\u91cd\uff0c\u6700\u591a _MAX_JS_PAGES \u4e2a\u3002"""
    out = []
    for m in _JS_SRC_PAT.finditer(html or ''):
        raw = (m.group(1) or '').strip()
        if not raw or raw.startswith('data:'):
            continue
        u = urljoin(base_url or '', raw)
        if not re.match(r'^https?://', u):
            continue
        if _is_junk(u) or u in out:
            continue
        out.append(u)
        if len(out) >= _MAX_JS_PAGES:
            break
    return out


def extract_publish_domains(publish_page, headers, proxies, timeout, _sink=None):
    """\u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe\u3002\u8fd4\u56de (\u9759\u6001\u955c\u50cf\u94fe\u63a5\u5217\u8868, \u6cdb\u89e3\u6790/\u7ebf\u8def\u8868\u57fa\u57df\u5217\u8868)\u3002
    JS \u6e32\u67d3\u4f46\u65e0 b64 \u58f3\u7684\u9875\u9762\u9759\u6001\u94fe\u63a5\u4ecd\u53ef\u80fd\u4e3a\u7a7a\u2014\u2014\u57fa\u57df\u8bc6\u522b\u662f\u4e3b\u901a\u9053\uff1b
    \u82e5 HTML \u9636\u6bb5\u57fa\u57df\u4e3a 0\uff08JS \u58f3\u5f62\u6001\uff1a\u5185\u5bb9\u5728\u5916\u94fe js\uff09\uff0c\u81ea\u52a8**\u8ddf\u968f\u5916\u94fe JS** \u518d\u626b\u4e00\u904d\u3002

    _sink\uff1a\u53ef\u9009 list\uff0c\u672c\u9875\u7684 trace \u884c\u5199\u5165\u5b83\u800c\u975e\u5168\u5c40 _TRACE\u2014\u2014\u5e76\u884c\u6293\u591a\u9875\u65f6\u5404\u9875\u72ec\u7acb
    \u6536\u96c6\u3001\u7531\u8c03\u7528\u65b9\u6309\u5e8f\u5199\u56de\uff0c\u907f\u514d\u591a\u7ebf\u7a0b\u4ea4\u9519\u5bfc\u81f4\u8bca\u65ad\u8bb0\u5f55\u4e71\u5e8f\u3002"""
    log = _sink.append if _sink is not None else _tr
    if requests is None or not publish_page:
        return [], []
    try:
        r = requests.get(publish_page, headers=headers, proxies=proxies,
                         timeout=timeout, verify=False, allow_redirects=True)
        log('[\u53d1\u5e03\u9875] %s \u2192 HTTP %s / %dB' % (_host_of(publish_page) or publish_page,
                                             r.status_code, len(r.text or '')))
        if r.status_code != 200:
            log('  \u2717 \u53d1\u5e03\u9875\u975e 200\uff0c\u62bd\u94fe\u4e2d\u6b62')
            return [], []
    except Exception as e:
        log('[\u53d1\u5e03\u9875] %s \u6293\u53d6\u5f02\u5e38: %s' % (_host_of(publish_page) or publish_page,
                                       str(e)[:60]))
        return [], []
    html = r.text or ''
    static, wilds = [], set()
    # \u2460 HTML \u672c\u4f53\uff08\u542b b64 \u58f3\u89e3\u7801\u9875\uff09
    texts = _expand_b64_shells(html)
    if len(texts) > 1:
        log('  \u5c55\u5f00 b64 \u58f3 %d \u4e2a' % (len(texts) - 1))
    for t in texts:
        _scan_text(t, static, wilds)
    # \u2461 JS \u58f3\u8ddf\u968f\uff1aHTML \u62bd\u4e0d\u5230\u57fa\u57df \u2192 \u7ebf\u8def\u5728 <script src="publish.js"> \u91cc\uff08\u9ec4\u679c\u540c\u6b3e\u5f62\u6001\uff09
    if not wilds:
        js_urls = _js_candidates(html, publish_page)
        if js_urls:
            log('  JS \u58f3\u8ddf\u968f %d \u4e2a: %s'
                % (len(js_urls), ', '.join(u.split('//', 1)[-1] for u in js_urls)))
            for ju in js_urls:
                jt = _fetch_text(ju, headers, proxies, timeout)
                if not jt:
                    log('    \u2717 %s \u53d6\u4e0d\u5230' % _host_of(ju))
                    continue
                log('    \u2713 %s %dB' % (_host_of(ju), len(jt)))
                for t in _expand_b64_shells(jt):
                    _scan_text(t, static, wilds)
    log('  \u62bd\u94fe: \u9759\u6001\u94fe\u63a5 %d \u4e2a / \u57fa\u57df %d \u4e2a %s'
        % (len(dict.fromkeys(static)), len(wilds),
           ('\u2192 ' + ', '.join(sorted(wilds)[:6])) if wilds else ''))
    return list(dict.fromkeys(static)), list(wilds)


def _extract_pages(pages, headers, proxies, timeout):
    """**\u5e76\u884c**\u6293\u53d6\u591a\u4e2a\u53d1\u5e03\u9875\u5e76\u62bd\u94fe\uff08v2.4\uff0c2026-09-13\uff09\u3002

    \u8fd4\u56de (pub_domains, bases, traces)\uff1a
      - pub_domains / bases \u6309 **pages \u539f\u5e8f**\u5408\u5e76\uff08\u7ed3\u679c\u786e\u5b9a\uff0c\u4e0d\u53d7\u7ebf\u7a0b\u5b8c\u6210\u65f6\u5e8f\u5f71\u54cd\uff09
      - traces = \u9010\u9875 trace \u884c\u5217\u8868\uff0c\u8c03\u7528\u65b9\u6309\u5e8f\u5199\u56de _TRACE\uff08\u591a\u7ebf\u7a0b\u4e0d\u53ef\u76f4\u63a5\u5199\u5168\u5c40\u5217\u8868\uff09
    \u7ebf\u7a0b\u6c60\u4e0d\u53ef\u7528\u65f6\u9000\u56de\u4e32\u884c\uff0c\u884c\u4e3a\u7b49\u4ef7\u3002"""
    n = len(pages or [])
    if not n:
        return [], [], []
    results = [None] * n
    traces = [[] for _ in range(n)]
    if not (ThreadPoolExecutor and as_completed) or n == 1:
        for i, pg in enumerate(pages):
            try:
                results[i] = extract_publish_domains(pg, headers, proxies,
                                                     timeout, traces[i])
            except Exception:
                results[i] = ([], [])
    else:
        ex = ThreadPoolExecutor(max_workers=min(6, n))
        try:
            futs = {}
            for i, pg in enumerate(pages):
                futs[ex.submit(extract_publish_domains, pg, headers, proxies,
                               timeout, traces[i])] = i
            for f in as_completed(list(futs)):
                i = futs[f]
                try:
                    results[i] = f.result()
                except Exception:
                    results[i] = ([], [])
        finally:
            ex.shutdown(wait=False)
    pub_domains, bases = [], []
    for i in range(n):
        s, b = results[i] or ([], [])
        for u in s:
            if u not in pub_domains:
                pub_domains.append(u)
        for x in b:
            if x not in bases:
                bases.append(x)
    return pub_domains, bases, traces


def _dedupe(urls):
    """\u4fdd\u5e8f\u53bb\u91cd + \u8865\u534f\u8bae\u5934\u3002"""
    seen, out = set(), []
    for u in urls:
        u2 = (u or '').strip().rstrip('/')
        if not u2:
            continue
        if not re.match(r'^https?://', u2):
            u2 = 'https://' + u2
        if u2 not in seen:
            seen.add(u2)
            out.append(u2)
    return out


def split_publish_pages(publish_page):
    """\u5f52\u4e00 publish_page \u53c2\u6570 \u2192 \u53d1\u5e03\u9875 URL \u5217\u8868\uff08\u4fdd\u5e8f\u53bb\u91cd\uff0c2026-09-13 \u591a\u53d1\u5e03\u9875\uff09\u3002

    \u63a5\u53d7\uff1aNone / '' / 'https://a' / 'https://a,https://b' / ['https://a', ...]\u3002
    \u53ea\u8ba4 http(s) \u7edd\u5bf9\u5730\u5740\uff08\u76f8\u5bf9\u8def\u5f84\u5982 `/homeway.html` \u65e0\u6cd5\u72ec\u7acb\u6293\u53d6\uff0c\u76f4\u63a5\u4e22\u5f03\uff09\uff1b
    \u9017\u53f7\u3001\u5206\u53f7\u3001\u7a7a\u767d\u90fd\u5f53\u5206\u9694\u7b26\u2014\u2014ext \u91cc\u7528\u9017\u53f7\uff0c\u624b\u5de5\u586b\u65f6\u5206\u53f7\u4e5f\u5e38\u89c1\u3002"""
    if not publish_page:
        return []
    if isinstance(publish_page, (list, tuple)):
        raw = [str(x) for x in publish_page]
    else:
        raw = re.split(r'[,\s;]+', str(publish_page))
    out = []
    for u in raw:
        u = (u or '').strip().rstrip('/')
        if u and re.match(r'^https?://\S+$', u) and u not in out:
            out.append(u)
    return out


# ---------------------------------------------------------------- \u63a2\u6d4b
def _js_redirect(t):
    """\u4ece JS \u8df3\u8f6c\u58f3\u63d0\u53d6\u76ee\u6807 URL\uff08\u7eaf JS \u58f3\u65e0 <a href> \u65f6\u515c\u5e95\u8ddf\u968f\uff09\u3002

    \u8986\u76d6\uff1awindow.location.replace('...') / window.location.href='...' /
    location.replace('...') / location.href='...' / <meta http-equiv=refresh ... url=...>\u3002
    \u8fd4\u56de\u53bb\u5c3e\u659c\u6760\u7684\u7edd\u5bf9 http(s) URL\uff0c\u5426\u5219 ''\u3002"""
    pats = [
        r'window\.location\.replace\(\s*[\'"](https?://[^\'"]+)[\'"]',
        r'window\.location\.href\s*=\s*[\'"](https?://[^\'"]+)[\'"]',
        r'location\.replace\(\s*[\'"](https?://[^\'"]+)[\'"]',
        r'location\.href\s*=\s*[\'"](https?://[^\'"]+)[\'"]',
        r'<meta[^>]+http-equiv=["\']?refresh["\']?[^>]+content=["\']?[^\'">]*url=([^"\'>\s]+)',
    ]
    for p in pats:
        m = re.search(p, t, re.I)
        if m:
            u = m.group(1).strip().rstrip('/')
            if re.match(r'^https?://', u):
                return u
    return None


def _probe(url, headers, proxies, timeout, depth=0, validate=None):
    """\u6d4b\u8bd5\u5355\u57df\u540d\uff1a\u8df3\u8f6c\u58f3\u5219\u8ddf\u968f <a href>\uff08\u6700\u591a2\u5c42\uff09\uff1b\u771f\u5185\u5bb9\u8fd4\u56de\u6700\u7ec8 host\uff1b\u5931\u8d25 None\u3002
    validate(final_host, text) -> bool\uff1a\u5185\u5bb9\u8eab\u4efd\u6821\u9a8c\uff08\u9632\u5e7f\u544a\u95e8\u7ad9/\u7b2c\u4e09\u65b9\u9875\u5192\u5145\uff09\u3002
    \u672a\u4f20 validate \u65f6\u9000\u5230\u300c\u5185\u5bb9\u5f62\u6001\u5224\u300d\uff1a\u5916\u94fe\u5f88\u591a\u53c8\u65e0\u5185\u5bb9\u7ed3\u6784 = \u5bfc\u822a\u9875 \u2192 \u62d2\u7edd\u3002"""
    if requests is None:
        return None
    try:
        r = requests.get(url, headers=headers, proxies=proxies,
                         timeout=timeout, verify=False, allow_redirects=True)
        if r.status_code != 200:
            return None
        t = r.text or ''
        final = (r.url or url).rstrip('/')
        if len(t) < 3000 and depth < 2:
            m = re.search(r'href=["\'](https?://[^"\']+)["\']', t, re.I)
            if m:
                target = m.group(1).rstrip('/')
                if target and target != final:
                    return _probe(target, headers, proxies, timeout, depth + 1, validate)
            # \u2461 \u7eaf JS / meta \u8df3\u8f6c\u58f3\uff08\u65e0 <a href> \u65f6\uff09\uff1a\u8ddf\u968f window.location / location.replace / meta refresh
            js = _js_redirect(t)
            if js and js != final:
                return _probe(js, headers, proxies, timeout, depth + 1, validate)
        if len(t) > 5000 or ('article' in t and 'category' in t):
            if not _looks_like_content(t):
                return None                     # \u5047\u95e8\u7ad9\uff1a\u516c\u544a\u9875/\u5bfc\u822a\u9875\uff0c\u4e0d\u542b\u5185\u5bb9\u7ed3\u6784
            if validate is not None:
                try:
                    if not validate(final, t):
                        return None
                except Exception:
                    return None
            return final
        return None
    except Exception:
        return None


def _probe_all(urls, headers, proxies, timeout, validate=None, tag=''):
    """\u5e76\u884c\u63a2\u6d4b\uff0c\u4efb\u4e00\u5019\u9009\u6210\u529f\u5373\u523b\u8fd4\u56de\uff08\u53d6\u6d88\u5176\u4f59\u4efb\u52a1\uff09\uff1b\u5168\u8d25\u8fd4\u56de ''\u3002
    \u603b\u8017\u65f6 \u2248 \u5355\u6b21\u8d85\u65f6\uff0c\u4e0d\u518d\u968f\u5019\u9009\u6570\u91cf\u53e0\u52a0\u3002"""
    if not urls:
        return ''
    if not (ThreadPoolExecutor and as_completed) or len(urls) == 1:
        for u in urls:
            h = _probe(u, headers, proxies, timeout, 0, validate)
            _tr('  [%s] %s' % (tag or '\u4e32\u884c', ('\u2713 ' + h) if h else ('\u2717 ' + _host_of(u))))
            if h:
                return h
        return ''
    ex = ThreadPoolExecutor(max_workers=min(12, len(urls)))
    try:
        futs = dict((ex.submit(_probe, u, headers, proxies, timeout, 0, validate), u)
                    for u in urls)
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception:
                r = None
            if r:
                for x in futs:
                    x.cancel()
                ok_u = futs.get(f, '')
                _tr('  [%s] \u2713 %s\uff08\u5019\u9009 %s \u547d\u4e2d\uff09' % (tag or '\u5e76\u884c', r, _host_of(ok_u)))
                return r
        _tr('  [%s] \u2717 %d \u4e2a\u5019\u9009\u5168\u90e8\u5931\u8d25' % (tag or '\u5e76\u884c', len(urls)))
        return ''
    finally:
        ex.shutdown(wait=False)


def probe_first(urls, headers=None, proxies=None, timeout=8, validate=None, tag='\u515c\u5e95'):
    """\u516c\u5f00\u7248\u5e76\u884c\u63a2\u6d4b\uff08\u4f9b\u5404\u6e90\u7684\u300c\u5185\u7f6e\u5019\u9009\u515c\u5e95\u300d\u7528\uff0c\u66ff\u4ee3 5\u00d78s \u4e32\u884c\u5faa\u73af\uff09\u3002
    \u4efb\u4e00\u6210\u529f\u5373\u8fd4\u56de\u5176 host\uff08\u53bb\u5c3e\u659c\u6760\uff09\uff0c\u5168\u8d25\u8fd4\u56de ''\u3002"""
    return _probe_all(_dedupe(urls or []), headers, proxies, timeout, validate, tag)


def _auto_validate(site_key):
    """\u6309\u7ad9\u540d\u751f\u6210\u8eab\u4efd\u6821\u9a8c\u51fd\u6570\uff08validate \u7f3a\u7701\u65f6\u7684\u9ed8\u8ba4\u5b9e\u73b0\uff09"""
    def _v(host, text):
        return site_key in (text or '')
    return _v


# ---------------------------------------------------------------- \u4e3b\u5165\u53e3
def resolve_host(publish_page=None, candidate_hosts=None, headers=None,
                 proxies=None, timeout=8, use_cache=True, validate=None,
                 site_key=None):
    """\u8fd4\u56de\u5f53\u524d\u53ef\u7528 host\uff08\u53bb\u5c3e\u659c\u6760\uff09\u3002\u5168\u90e8\u5931\u8d25\u8fd4\u56de ''\uff08\u8c03\u7528\u65b9\u63a5\u53e3\u5c42\u81ea\u884c\u515c\u7a7a\uff09\u3002

    validate(final_host, text)->bool\uff1a\u7ad9\u70b9\u8eab\u4efd\u6821\u9a8c\u56de\u8c03\u3002
    site_key\uff1a\u7ad9\u540d\u5173\u952e\u8bcd\uff1bvalidate \u7f3a\u7701\u65f6\u81ea\u52a8\u7528\u5b83\u751f\u6210\u6821\u9a8c\uff08\u518d\u4e0d\u4f20\u5219\u9000\u5230\u5185\u5bb9\u5f62\u6001\u5224\uff09\u3002
    publish_page\uff1a\u5355\u4e2a\u53d1\u5e03\u9875 URL\uff0c\u6216\u591a\u4e2a\uff08\u5217\u8868 / \u9017\u53f7\u00b7\u5206\u53f7\u5206\u9694\u4e32\uff09\u2014\u2014**\u5e76\u884c\u6293\u3001\u6309\u5e8f\u5408\u5e76**\u3002
    \u987a\u5e8f\uff1a\u53d1\u5e03\u9875\u57fa\u57df\u5019\u9009\uff08\u6700\u65b0\u9c9c\uff09> ext/\u5185\u7f6e\u5019\u9009 > \u53d1\u5e03\u9875\u9759\u6001\u94fe\u63a5\u3002
    \u5168\u8fc7\u7a0b\u5199\u5165 last_trace()\uff0c\u4f9b\u6e90\u5185\u300c\u8bca\u65ad\u300d\u680f\u76ee\u5c55\u793a\u3002"""
    del _TRACE[:]
    candidate_hosts = candidate_hosts or []
    pages = split_publish_pages(publish_page)      # \u591a\u53d1\u5e03\u9875\uff082026-09-13\uff09
    _tr('== \u9009\u7ad9\u5f00\u59cb (publish=%s | site_key=%s) =='
        % ('\u3001'.join([_host_of(p) for p in pages]) or '(\u65e0)', site_key or '(\u672a\u4f20)'))
    if validate is None and site_key:
        validate = _auto_validate(site_key)
    key = (tuple(pages), tuple(candidate_hosts), site_key or '')
    if use_cache:
        hit = _CACHE.get(key)
        if hit and time.time() < hit[1]:
            _tr('  \u547d\u4e2d\u9009\u7ad9\u7f13\u5b58 \u2192 %s\uff08%d \u79d2\u540e\u8fc7\u671f\uff09'
                % (hit[0], int(hit[1] - time.time())))
            return hit[0]

    # 1) \u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe\uff08\u57fa\u57df\u81ea\u52a8\u751f\u6210\u5019\u9009 + \u9759\u6001\u955c\u50cf\u94fe\u63a5\uff09
    #    \u591a\u4e2a\u53d1\u5e03\u9875\uff08\u7f51\u5740\u578b + GitHub \u578b\u7b49\uff09**\u5e76\u884c**\u6293\u53d6\u3001\u7ed3\u679c\u6309\u586b\u5199\u987a\u5e8f\u5408\u5e76\uff1a
    #    \u4e00\u9875\u6302\u4e86\u4e0d\u5f71\u54cd\u5176\u4ed6\u9875\uff0cN \u9875\u8017\u65f6\u4ece N\u00d7 \u964d\u4e3a \u2248max\uff08v2.4\uff0c2026-09-13\uff09\u3002
    pub_domains, bases, _pg_traces = _extract_pages(pages, headers, proxies, timeout)
    for _lines in _pg_traces:                 # trace \u6309 pages \u539f\u5e8f\u5199\u56de\uff08\u5e76\u884c\u4e0b\u4e0d\u53ef\u4e71\u5e8f\uff09
        for _l in _lines:
            _tr(_l)
    words = random.sample(_WILD_WORDS, min(4, len(_WILD_WORDS)))
    wild_candidates = []
    for b in bases:
        wild_candidates += ['https://%s.%s' % (w, b) for w in words]
        wild_candidates.append('https://%s' % b)      # \u7ad9\u65b9\u56fa\u5b9a\u7ebf\u8def\uff1a\u4e0d\u52a0\u524d\u7f00

    # 2) \u5206\u5c42\u5019\u9009\uff08\u5404\u5c42\u4fdd\u5e8f\u53bb\u91cd\uff09\uff1a
    #    \u53d1\u5e03\u9875\u5730\u5740**\u672c\u8eab\u5c31\u662f\u9996\u9009\u5019\u9009**\u2014\u2014\u7ad9\u65b9\u5e38\u628a\u300c\u53d1\u5e03\u9875\u300d\u76f4\u63a5\u505a\u6210\u4e3b\u57df\u7684\u6d3b\u955c\u50cf
    #    \uff0851\u5403\u74dc advise.nlwkmsv.cc \u5b9e\u6d4b 260KB \u5b8c\u6574\u7ad9 + 302 \u8df3\u65b0\u57df\uff1b\u82e5\u9884\u5148\u6392\u6389\u5b83\uff0c
    #    \u5c31\u53ea\u5269\u5047\u95e8\u7ad9\u53ef\u9009\uff09\u3002\u662f\u5426\u5408\u683c\u4ea4\u7ed9\u8eab\u4efd\u6821\u9a8c + \u5185\u5bb9\u5f62\u6001\u5224\u3002
    #    \u7b2c\u4e00\u5c42 = \u53d1\u5e03\u9875 + \u62bd\u94fe\u5019\u9009 + ext/\u5185\u7f6e\u5019\u9009\uff08\u65b0\u9c9c\u4e14\u53ef\u4fe1\uff09
    #    \u7b2c\u4e8c\u5c42 = \u53d1\u5e03\u9875\u91cc\u7684\u9759\u6001\u5916\u94fe\uff08\u591a\u4e3a\u5e7f\u544a/\u5bfc\u822a/\u5047\u95e8\u7ad9\uff0c\u4ec5\u7b2c\u4e00\u5c42\u5168\u8d25\u65f6\u624d\u8bd5\uff09
    tier1 = [u for u in _dedupe(list(pages) + wild_candidates + list(candidate_hosts))
             if not _is_junk(u)]
    _t1 = set(tier1)
    tier2 = [u for u in _dedupe(pub_domains) if u not in _t1 and not _is_junk(u)]

    if not tier1 and not tier2:
        _tr('  \u65e0\u4efb\u4f55\u5019\u9009\u53ef\u6d4b\uff08\u53d1\u5e03\u9875\u62bd\u94fe\u4e3a\u7a7a\u4e14\u65e0\u5185\u7f6e\u5019\u9009\uff09\u2192 \u8fd4\u56de\u7a7a')
        return ''
    _tr('  \u5019\u9009: \u7b2c\u4e00\u5c42 %d \u4e2a / \u7b2c\u4e8c\u5c42 %d \u4e2a\uff08\u7b2c\u4e00\u5c42\u9996\u9009=%s\uff09'
        % (len(tier1), len(tier2),
           '\u3001'.join([_host_of(p) for p in pages]) or '-'))

    # 3) \u5206\u6ce2\u5b9e\u6d4b\uff08use_cache=False=\u5f3a\u5236\u5237\u65b0\uff0c\u4f46\u6210\u529f\u7ed3\u679c\u4ecd\u5199\u7f13\u5b58\u4f9b\u540e\u7eed init \u79d2\u5f00\uff09
    host = _probe_all(tier1, headers, proxies, timeout, validate, '\u4e00\u7ea7')
    if not host and tier2:
        host = _probe_all(tier2, headers, proxies, timeout, validate, '\u4e8c\u7ea7')
    if host:
        _CACHE[key] = (host, time.time() + _CACHE_TTL)
        _tr('  \u2605 \u9009\u4e2d %s\uff08\u7f13\u5b58 30 \u5206\u949f\uff09' % host)
    else:
        _tr('  \u2605 \u5168\u90e8\u5931\u8d25 \u2192 \u8fd4\u56de\u7a7a\uff08\u8c03\u7528\u65b9\u5e94\u7acb\u5373\u5931\u8d25\uff0c\u4e0d\u518d\u9759\u9ed8\u7a7a\u8f6c\uff09')
    return host
