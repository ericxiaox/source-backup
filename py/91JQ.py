# -*- coding: utf-8 -*-
# 91JQ\uff0891\u6fc0\u60c5\uff09\u7ad9\u6e90 \u2014\u2014 \u81ea\u7814\u58f3\u7ad9\u578b\uff0c2026-09-16 \u7531 xbpq/\u4e00\u8d77\u73a9.json py \u5316\u91cd\u5199
#
# \u26a0 \u65e7 jar \u914d\u7f6e\uff08xbpq/\u4e00\u8d77\u73a9.json\uff09\u63cf\u8ff0\u7684\u662f\u300c\u6d77\u89d2\u7cfb\u300d\u7ad9\u70b9\uff08video-item / grid /
#   actorshow / haijiaod.life\uff09\uff0c\u4e0e\u53d1\u5e03\u9875 91fby.com \u73b0\u5728\u6307\u5411\u7684\u7ad9**\u5df2\u5b8c\u5168\u4e0d\u540c** \u2192
#   \u65e7\u89c4\u5219\u6574\u4efd\u4f5c\u5e9f\uff0c\u672c\u6e90\u6309\u5b9e\u6d4b\u7ed3\u6784\u91cd\u5199\u3002
#
# \u7ad9\u70b9\u5b9e\u6d4b\u7ed3\u6784\uff082026-09-16\uff09\uff1a
#   \u00b7 **\u53cc\u5f62\u6001\u540c\u65f6\u73b0\u5f79**\uff082026-09-16 \u9010\u6761\u5b9e\u6d4b\uff0c\u5b57\u8282\u6570\u4e3a\u5f53\u65e5\u5b9e\u6d4b\uff09\uff1a
#       `/`                = \u52a0\u5bc6\u58f3\u843d\u5730\u9875 48961B\uff08\u53cd\u722c\u95e8\u9762\uff09
#       `/Html-enc/{tid}/` = \u52a0\u5bc6\u58f3\u5206\u7c7b\u9875 45645B\uff08\u5185\u90e8\u94fe\u4ecd\u6307\u56de /Html-enc/ \u65cf\uff09
#       `/Html/{tid}/`     = **\u660e\u6587\u9875** 25918B   \u2190 \u6e90\u4fa7\u56fa\u5b9a\u8d70\u8fd9\u4e00\u65cf
#     \u58f3\u9875\u89e3\u7801\uff1d\u81ea\u5b9a\u4e49\u5b57\u6bcd\u8868 \u2192 base64 \u2192 XOR(16B key) \u2192 decodeURIComponent(escape())\uff0c
#     \u5df2\u5185\u8054 `_unmask()`\uff1b`_is_shell()` \u5b9e\u6d4b\u53ef\u547d\u4e2d\uff08\u6620\u5c04\u8868\u8de8\u591a\u884c\u4e5f\u80fd\u5339\u5230\uff09\u3002
#     \u26a0 \u58f3\u65cf\u5185\u90e8\u94fe\u662f `/Html-enc/...`\uff0c\u6e90\u4fa7**\u672a\u5b9e\u73b0** enc \u8def\u5f84\u65cf\u8def\u7531\uff08\u660e\u6587\u65cf\u73b0\u5f79\u6545\u591f\u7528\uff09\u3002
#   \u00b7 \u9996\u9875 /Html/index.html\uff08\u5bfc\u822a + 22 \u6761\u6700\u65b0\uff09
#   \u00b7 \u5206\u7c7b /Html/{tid}/ \uff0c\u5206\u9875 /Html/{tid}/index-{pg}.html\uff08tid=60 \u5b9e\u6d4b 335 \u9875\uff09
#   \u00b7 \u8be6\u60c5 /Html/{cate}/{id}.html
#   \u00b7 \u64ad\u653e /Html/player/play-{nid}-0-1.html \u2192 `mp4("<path>.m3u8")`
#   \u00b7 **\u65e0\u641c\u7d22\u529f\u80fd**\uff08/search* \u5168\u90e8\u56de\u843d\u9996\u9875\uff0c/Html/index.php \u76f4\u63a5 404\uff09
#
# \u64ad\u653e/\u5c01\u9762\u57df\u540d\uff08\u7ad9\u65b9\u6309\u6d41\u91cf\u5206\u914d\uff0c\u4f1a\u8f6e\u6362 \u2192 \u6e90\u4fa7\u4ece /js/u.js \u52a8\u6001\u8bfb\u6c60\uff0c\u5185\u7f6e\u515c\u5e95\uff09\uff1a
#   \u64ad\u653e\u6c60 purls\uff1ajqbo26818/26606/26333/26111/26666.com  \u2192 `{purl}{path}` \u5b9e\u6d4b 200 + #EXTM3U
#   \u56fe\u7247\u6c60 durls\uff1ajqxia26312/26999.com                   \u2192 \u5b9e\u6d4b 200 image/webp\uff08RIFF/WEBP\uff09
#   d.9xxav.com \u662f\u7ad9\u65b9\u539f\u59cb\u8d44\u6e90\u57df\uff0c\u672c\u673a DNS \u4e0d\u53ef\u89e3\u6790 \u2192 \u53ea\u4f5c\u8def\u5f84\u6765\u6e90\uff0c\u4e0d\u5f53 host
#
# \u53d6\u57df\uff1a
#   \u53d1\u5e03\u9875 https://91fby.com/index_fby.html\uff08\u72ec\u7acb\u57df\uff0c\u5b9e\u6d4b 200\u300c\u6700\u65b0\u5730\u5740\u53d1\u5e03\u9875\u300d\uff1b
#   \u65e7 91fby.cc \u5df2\u505c\u7528 \u2192 DNS \u8fd4 0.0.0.0\uff09\u3002\u53d1\u5e03\u9875\u7ed9\u7684\u662f **5 \u6761 IP:\u7aef\u53e3 \u9632\u52ab\u6301\u901a\u9053**\uff1a
#     198.200.45.72:7018 / .74:7019 / .75:7020 / .77:7021 / .83:7022\uff08\u5168\u90e8 200\uff09
#   \u26a0 hostresolver \u7684\u57df\u62bd\u53d6\u542b TLD \u767d\u540d\u5355 \u2192 **\u62bd\u4e0d\u51fa IP:\u7aef\u53e3 \u5f62\u6001**\uff0c\u6545\u6e90\u5185\u81ea\u7814\u3002
#   \u81ea\u7814\u53d6\u57df**\u4e09\u7ea7\u987a\u5e8f**\uff08\u524d\u4e00\u7ea7\u547d\u4e2d\u5373\u8fd4\u56de\uff09\uff1a
#     \u2460 \u5185\u7f6e/ext \u7684 IP:\u7aef\u53e3 \u6c60\uff08_BUILTIN_HOSTS\uff0cext \u7684 host@/hosts@ \u4ea6\u53ef\u8986\u76d6\uff09
#     \u2461 **\u53d1\u5e03\u9875\u540c\u6e90\u7684 /get_dm.php \u52a8\u6001\u57df\u63a5\u53e3**\uff08\u7ad9\u65b9 index_fby_tiao.html \u7684\u5b98\u65b9\u673a\u5236\uff09
#        \u2192 b64\u2192\u5220K1\u2192b64\u2192\u5220K2 \u89e3\u5f97 `16.91jq466.com:16888`\uff0c\u53d6\u672b\u4e24\u6bb5 \u2192 https://91jq466.com
#        \uff08\u5b9e\u6d4b 200 / 28376B \u4e0e IP \u901a\u9053\u540c\u5185\u5bb9\uff1b\u7ed9\u7684\u662f**\u57df\u540d\u8def\u7ebf**\uff0cIP \u642c\u673a\u4e5f\u81ea\u6108\uff09
#     \u2462 \u6293\u53d1\u5e03\u9875 HTML \u73b0\u62bd IP:\u7aef\u53e3 / \u660e\u6587\u4e3b\u673a
#     \u5168\u8d25\u8fd4 ''\uff08\u63a5\u53e3\u5c42\u81ea\u884c\u515c\u7a7a\uff1b\u53e6\u6709\u4e00\u6b21\u61d2\u91cd\u8bd5\uff09\u3002
#   \u53d1\u5e03\u9875\u53e6\u6709\uff1a\u9632\u5c01\u90ae\u7bb1 dizhi@91JQX.com\uff08\u2192 \u6bcd\u672c ext \u7684 mail@\uff09\u00b7
#   \u6d77\u5916\u6c38\u4e45\u5740 91jq.tv\uff08\u53d1\u5e03\u9875\u81ea\u8ff0"\u56fd\u5916\u7f51\u7edc\u8bbf\u95ee"\uff0c\u672c\u673a SSL \u63e1\u624b\u5373\u8d25\uff09\u2192 \u5f52\u6bcd\u672c `vpn`\u3002
#
#   \u5730\u5740\u751f\u6001\uff082026-09-16 \u5b9e\u6d4b\uff0c\u4e09\u6761\u4e92\u4e0d\u76f8\u540c\u7684\u53d1\u5e03\u6e90\u90fd\u901a\uff09\uff1a
#     a) 91fby.com/index_fby.html \u2192 5 \u6761 IP:\u7aef\u53e3\u300c\u9632\u52ab\u6301\u901a\u9053\u300d\uff08\u9759\u6001\u5199\u6b7b\u5728\u9875\u9762 JS \u91cc\uff09
#     b) bitbucket \u2026/dizhifabu/raw/master/README.md \u2192 91jqdizhi21/88/92/50.com
#        \uff08\u5b9e\u6d4b 88/92/50 \u7684 /Html/index.html \u662f**\u771f\u7ad9**\uff1a\u6807\u9898\u300c91JQ\u5c31\u8981\u6fc0\u60c5\u300d\u3001valid=True\u300122 \u6761\uff09
#     c) raw.githubusercontent.com/daxiangjiao888/dizhifabu/main/README.md \u2192 6 \u6761
#        `91fby.91jq463.com:16888` \u5f62\u5f0f\u7684\u300c\u57df:\u7aef\u53e3\u300d
#   \u2192 \u6bcd\u672c ext \u53d6 a+b \u4e24\u6761\uff08\u5747\u672c\u673a**\u76f4\u8fde** 200\uff09\uff1bc \u672a\u7eb3\u5165\uff1araw.githubusercontent \u5728\u914d\u7f6e\u6587\u4ef6
#     `rules` \u7684 proxy \u540d\u5355\u5185 \u2192 \u771f\u673a\u5927\u6982\u7387\u8981\u68af\u5b50\uff0c\u522b\u8ba9\u5b83\u62d6\u6162\u515c\u5e95\u94fe\u3002
#   \u7531 b/c \u53ef\u89c1\u57fa\u57df\u4f1a\u8f6e\u6362\uff0891jq463/464/465/466\u2026\uff09\uff0c\u4e0e get_dm.php \u7684\u52a8\u6001\u503c\u540c\u65cf \u2014\u2014 \u8fd9\u6b63\u662f
#   \u2461 \u7ea7\u4ef7\u503c\u6700\u9ad8\u4e4b\u5904\uff1a**\u57df\u540d\u968f\u8f6e\u6362\u81ea\u6108\uff0c\u4e0d\u4f9d\u8d56\u4efb\u4f55\u9759\u6001\u5199\u6b7b\u7684 IP**\u3002
import json
import re
import sys
import os
import time
import random
import html as _html
from urllib.parse import urljoin, quote

import requests
try:
    from base.spider import Spider as BaseSpider
except ImportError:
    class BaseSpider(object):
        pass


try:
    from hostresolver import resolve_host, parse_ext, probe_first
except Exception:
    # hostresolver.py \u5728\u5305\u6839\uff08py/ \u7684\u4e0a\u7ea7\uff09\u3002App \u7aef\uff08gitee \u52a0\u8f7d\uff09\u5b83\u4e0d\u5728\u73b0\u573a\uff0c
    # \u5bfc\u5165\u5fc5\u987b\u53ef\u964d\u7ea7\u4e3a None \u2192 \u8fd0\u884c\u65f6\u8d70\u672c\u6e90\u81ea\u7814\u53d6\u57df\u3002\u6a21\u5757\u7ea7\u7981\u88f8\u5bfc\u5165\u3002
    try:
        import os as _os
        sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        from hostresolver import resolve_host, parse_ext, probe_first
    except Exception:
        resolve_host = None
        parse_ext = None
        probe_first = None

_UA = ('Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 '
       '(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36')

_SITE_KEY = '91JQ'

# \u53d1\u5e03\u9875\uff08\u72ec\u7acb\u57df\uff1b\u7ed9 IP:\u7aef\u53e3 \u901a\u9053\u6e05\u5355 + \u6d77\u5916\u6c38\u4e45\u5740\uff09
_PUBLISH = 'https://91fby.com/index_fby.html'
# \u5185\u7f6e\u515c\u5e95\uff1a\u53d1\u5e03\u9875\u5b9e\u6d4b\u7ed9\u51fa\u7684 5 \u6761\u9632\u52ab\u6301\u901a\u9053\uff08\u5e26\u7aef\u53e3\uff0c\u6545\u4e0d\u8d70 hostresolver\uff09
_BUILTIN_HOSTS = [
    'https://198.200.45.72:7018',
    'https://198.200.45.74:7019',
    'https://198.200.45.75:7020',
    'https://198.200.45.77:7021',
    'https://198.200.45.83:7022',
]

# \u63a2\u6d3b\u6df1\u94fe\uff08\u9996\u9875\u660e\u6587\u7248\uff1b\u5b9e\u6d4b 28KB \u6863\uff0c\u542b movie2_list \u4e0e >10 \u6761\u76ee\uff09
_PROBE_PATH = '/Html/index.html'

# \u64ad\u653e/\u5c01\u9762\u57df\u540d\u6c60\u515c\u5e95\uff08\u7ad9\u65b9\u8f6e\u6362\u65f6\u4ee5 /js/u.js \u5b9e\u65f6\u89e3\u6790\u4e3a\u51c6\uff09
_BUILTIN_PURLS = [
    'https://jqbo26818.com', 'https://jqbo26606.com', 'https://jqbo26333.com',
    'https://jqbo26111.com', 'https://jqbo26666.com',
]
_BUILTIN_DURLS = ['https://jqxia26312.com', 'https://jqxia26999.com']

# \u2500\u2500 \u5907\u7528\u53d6\u57df\uff1a\u53d1\u5e03\u9875\u540c\u6e90\u7684 /get_dm.php\uff08\u7ad9\u65b9 JS \u7684\u5b98\u65b9\u52a8\u6001\u57df\u63a5\u53e3\uff09\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# \u94fe\u8def\u8fd8\u539f\uff082026-09-16 \u6293 index_fby_tiao.html + jm.js\uff09\uff1aXHR \u62c9 /get_dm.php\uff0c
#   \u54cd\u5e94 = \u5916\u5c42 b64\uff1bjjmm() = \u300cb64 \u2192 \u5220 _DM_K1 \u2192 \u518d b64 \u2192 \u5220 _DM_K2\u300d\u3002
#   jm.js \u91cc\u4e24\u6bb5 key \u7528 \x \u8f6c\u4e49\u85cf\u5b57\u9762\u91cf\uff0c\u8fd8\u539f\u5373\u4e0b\u65b9\u4e24\u5e38\u91cf\u3002
#   \u89e3\u5f97\u5f62\u5982 `16.91jq466.com:16888`\uff1a\u524d\u7f00\u6570\u5b57\u4e0e\u7aef\u53e3\u662f**\u53cd\u722c\u88c5\u9970**\uff08\u7ad9\u65b9 JS \u81ea\u5df1\u4e5f\u4f1a
#   \u91cd\u968f\u673a\u524d\u7f00\uff09\uff0c\u771f\u57df\u53d6**\u672b\u4e24\u6bb5**\uff08\u7b49\u540c jm.js \u7684 hq_yj_ym\uff09\u2192 https://91jq466.com\u3002
#   \u26a0 \u4e0e\u53d1\u5e03\u9875**\u540c\u6e90**\uff0c\u4e0d\u662f\u72ec\u7acb\u515c\u5e95\uff1b\u4ef7\u503c\u5728\u7ed9**\u57df\u540d\u8def\u7ebf**\uff08IP:\u7aef\u53e3\u968f\u7ad9\u65b9\u642c\u673a\u5373\u5e9f\uff0c
#   \u57df\u540d\u8d70 DNS \u53ef\u81ea\u6108\uff09\u3002\u4efb\u4e00\u6b65\u5931\u8d25\u9759\u9ed8\u8fd4\u56de []\uff0c\u4e0d\u5f71\u54cd\u4e3b\u6d41\u7a0b\u3002
_DM_K1, _DM_K2 = 'UMNNtgrUTUeUSEHT', 'MP7goNfyl0IMG8DR'
_DM_ORIGIN = 'https://91fby.com'

# \u5206\u7c7b\u515c\u5e95\u8868\uff082026-09-16 \u4ece\u7ad9\u5185\u5bfc\u822a\u5b9e\u6d4b\u62bd\u53d6\uff1bhomeContent \u4f1a\u5148\u8bd5\u5b9e\u65f6\u89e3\u6790\uff09
_CATS = [
    ('\u56fd\u4ea7\u7cbe\u54c1', '60'), ('\u4e2d\u6587\u5b57\u5e55', '94'), ('S\u7ea7\u5973\u4f18', '100'), ('\u6b27\u7f8e\u6fc0\u60c5', '62'),
    ('\u6210\u4eba\u52a8\u6f2b', '101'), ('\u72ec\u5bb6\u955c\u5934', '89'), ('\u592b\u59bb\u540c\u623f', '87'), ('\u5f00\u653e00\u540e', '93'),
    ('\u7f51\u7ea2\u4e3b\u64ad', '91'), ('\u624b\u673a\u89c6\u9891', '88'), ('\u7ecf\u5178\u4e09\u7ea7', '109'), ('\u7f8e\u989c\u5de8\u4e73', '112'),
    ('\u989c\u5c04\u5403\u7cbe', '113'), ('\u719f\u5973\u4eba\u59bb', '111'), ('\u4e1d\u889c\u5236\u670d', '114'), ('\u6362\u59bb\u6e38\u620f', '90'),
    ('\u79d8\u7231\u5c0f\u8bf4', '84'),
]

_RE_CAT = re.compile(r'href="(?:/Html/|\{\{host\}\}/Html/)(\d+)/"[^>]*>([^<]{1,12})<')
_RE_ITEM = re.compile(r'<li>\s*<a\s+href="(/Html/\d+/\d+\.html)"[^>]*>(.*?)</li>', re.S)
_RE_PIC = re.compile(r'get_local\(\s*"([^"]+\.(?:webp|jpg|jpeg|png))"')
_RE_ITEM_TITLE = re.compile(r'<h3>(.*?)</h3>', re.S)
_RE_ITEM_DATE = re.compile(r'class="movie_date">([^<]{4,20})<')
_RE_PAGE = re.compile(r'/index-(\d+)\.html')
_RE_DET_TITLE = re.compile(r'<dd class="film_title">\s*<h1>(.*?)</h1>', re.S)
_RE_DOWN = re.compile(r"down_url\s*=\s*'((?:https?:)?//[^']+)'")
_RE_MP4 = re.compile(r'mp4\(\s*"([^"]+\.m3u8[^"]*)"\s*\)')
_RE_PURLS = re.compile(r'var\s+purls\s*=\s*\[(.*?)\]', re.S)
_RE_DURLS = re.compile(r'var\s+durls\s*=\s*\[(.*?)\]', re.S)
_RE_URL_IN_ARR = re.compile(r'"(https?://[a-z0-9.\-]+)"', re.I)
# \u58f3\u9875\u4e09\u6bb5\u5f0f\uff1ablob / xor-key / \u81ea\u5b9a\u4e49\u5b57\u6bcd\u8868\uff08\u6620\u5c04\u8868\u5728\u540c\u4e00\u884c\u5185\u4ee5 }; \u6536\u5c3e\uff09
_RE_SHELL = re.compile(
    r'var\s+\w+\s*=\s*"([A-Za-z0-9+/=]{200,})"\s*;\s*'
    r'var\s+\w+\s*=\s*"([^"]{4,64})"\s*;\s*'
    r'var\s+\w+\s*=\s*(\{[^\n]{20,}\})\s*;')

# \u5206\u96c6\u540d\u5e7f\u544a\u9ed1\u540d\u5355\uff08\u5bf9\u9f50\u5df2\u9a8c\u8bc1\u6e90\u7eaa\u5f8b\uff09
_AD_NAME_RE = re.compile('(<|http|www\\.|\\.com|\\.cc|\u516c\u4f17\u53f7|\u5173\u6ce8|\u798f\u5229|\u66f4\u591a|APP|app|\u4e0b\u8f7d|\u5730\u5740\u53d1\u5e03|\u6700\u65b0\u5730\u5740)')


def _clean(s):
    return _html.unescape(re.sub(r'<[^>]+>', '', s or '')).replace('\xa0', ' ').strip()


def _is_shell(text):
    """\u662f\u4e0d\u662f\u52a0\u5bc6\u58f3\u9875\uff08\u5224\u5b9a\uff1a\u542b\u8d85\u957f b64 blob + \u7d27\u8ddf xor key + \u6620\u5c04\u8868\u4e09\u6bb5\u5f0f\uff09\u3002"""
    return bool(_RE_SHELL.search(text or ''))


def _unmask(text):
    """\u5c31\u5730\u89e3\u58f3\uff1a\u81ea\u5b9a\u4e49\u5b57\u6bcd\u8868\u6620\u5c04 \u2192 base64 \u2192 \u6309 key \u5faa\u73af XOR \u2192 utf-8\u3002
    \u5b9e\u6d4b\u7ad9\u70b9\u5b9e\u73b0\uff1atable[\u5b57\u7b26] \u8fd8\u539f\u6210\u6807\u51c6 b64 \u5b57\u7b26\u96c6\uff0c\u518d\u65e0 padding \u89e3\u3001XOR\u3001
    decodeURIComponent(escape()) \u8f6c UTF-8\u3002\u4efb\u4e00\u6b65\u5931\u8d25\u8fd4\u56de\u539f\u6587\uff08\u4e0d\u541e\u6570\u636e\uff09\u3002"""
    m = _RE_SHELL.search(text or '')
    if not m:
        return text
    try:
        import base64
        blob, key, tbl_raw = m.group(1), m.group(2), m.group(3)
        table = json.loads(tbl_raw)
        if not isinstance(table, dict) or len(table) < 16:
            return text
        s = ''.join(str(table.get(c, c)) for c in blob)
        raw = base64.b64decode(s + '=' * (-len(s) % 4))
        out = bytes(b ^ ord(key[i % len(key)]) for i, b in enumerate(raw))
        return out.decode('utf-8', 'replace')
    except Exception:
        return text


def _dm_unwrap(raw):
    """\u590d\u523b jm.js \u7684 jjmm()\uff1a\u5916\u5c42 b64 \u2192 \u5220 K1 \u2192 \u518d b64 \u2192 \u5220 K2\u3002
    \u4efb\u4e00\u6b65\u5931\u8d25\u8fd4\u56de ''\uff08\u8c03\u7528\u65b9\u9759\u9ed8\u8df3\u8fc7\uff0c\u7edd\u4e0d\u629b\uff09\u3002"""
    try:
        import base64
        s = str(raw or '').strip()
        if not s:
            return ''
        a = base64.b64decode(s + '=' * (-len(s) % 4)).decode('utf-8', 'replace')
        a = a.replace(_DM_K1, '')
        if not a:
            return ''
        b = base64.b64decode(a + '=' * (-len(a) % 4)).decode('utf-8', 'replace')
        return b.replace(_DM_K2, '').strip()
    except Exception:
        return ''


def _dm_regdomain(s):
    """`16.91jq466.com:16888` \u2192 `91jq466.com`\uff08\u53bb\u53cd\u722c\u524d\u7f00\u4e0e\u7aef\u53e3\uff0c\u53d6\u672b\u4e24\u6bb5\uff09\u3002
    \u672b\u4e24\u6bb5\u4e0d\u8db3\u6216\u542b\u975e\u6cd5\u5b57\u7b26\u8fd4\u56de ''\u3002"""
    s = (s or '').split('/')[0].split(':')[0].strip().strip('.')
    parts = [p for p in s.split('.') if p]
    if len(parts) < 2:
        return ''
    dom = '.'.join(parts[-2:])
    if not re.match(r'^[a-z0-9][a-z0-9.\-]{2,60}\.[a-z]{2,10}$', dom, re.I):
        return ''
    return dom


def _valid_page(text):
    """\u5185\u5bb9\u9875\u5224\u5b9a\uff1a\u660e\u6587\u6216\u89e3\u5bc6\u540e\u542b\u5217\u8868\u9aa8\u67b6\u4e14\u6761\u76ee\u8db3\u591f\u6ee1\u3002
    \u26a0 \u94fe\u63a5\u65cf**\u660e/\u58f3\u90fd\u8ba4**\uff1a\u660e\u6587\u9875\u662f `/Html/{tid}/{id}.html`\uff0c\u89e3\u5bc6\u540e\u7684\u58f3\u9875\u5185\u90e8\u94fe\u662f
    `/Html-enc/{tid}/{id}.html` \u2014\u2014 \u53ea\u8ba4\u660e\u6587\u65cf\u4f1a\u628a\u300c\u547d\u4e2d\u58f3\u9875\u4f46\u5185\u5bb9\u5b8c\u597d\u300d\u7684\u901a\u9053\u8bef\u5224\u6b7b\u3002"""
    t = text or ''
    if _is_shell(t):
        t = _unmask(t)
    return (('movie2_list' in t) or ('video_obxobx' in t)) and \
        len(re.findall(r'/Html(?:-enc)?/\d+/\d+\.html', t)) >= 4


class Spider(BaseSpider):

    def init(self, extend=""):
        self.proxies = {}
        self._ext = {}
        ext_str = (extend or '').strip()
        if ext_str:
            try:
                cfg = json.loads(ext_str)
                if isinstance(cfg, dict):
                    self.proxies = cfg.get('proxies') or {}
                    for k in ('publish', 'host'):
                        if cfg.get(k):
                            self._ext[k] = str(cfg[k]).strip()
                    if cfg.get('hosts'):
                        hs = cfg['hosts'] if isinstance(cfg['hosts'], list) else [cfg['hosts']]
                        self._ext['hosts'] = [str(h).strip() for h in hs if str(h).strip()]
            except Exception:
                self.proxies = {}
                if parse_ext:
                    try:
                        self._ext = parse_ext(ext_str)
                    except Exception:
                        self._ext = {}
        self.headers = {
            'User-Agent': _UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
        }
        self.trace = []
        self._purls = []
        self._durls = []
        # \u53d6\u57df\u7edd\u4e0d\u8bb8\u70b8 init\u2014\u2014\u5931\u8d25\u7559\u7a7a\uff0c\u61d2\u91cd\u8bd5\u515c\u5e95\uff0c\u4fdd\u8bc1\u5206\u7c7b\u5fc5\u51fa
        try:
            self.host = self.get_working_host()
        except Exception as e:
            self.host = ''
            self.trace.append('init\u53d6\u57df\u5f02\u5e38: %s' % str(e)[:60])
        self.headers.update({'Origin': self.host, 'Referer': self.host + '/'})
        print('\u4f7f\u7528\u7ad9\u70b9: %s' % self.host)

    def getName(self):
        return _SITE_KEY

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def localProxy(self, params):
        return [200, 'video/MP2T', '']

    # ---------- \u7f51\u7edc ----------
    def _http(self, url, headers=None, timeout=10):
        # requests \u76f4\u8fde\u5305\u88c5\u3002\u26a0\u523b\u610f\u4e0d\u53eb fetch\uff1aApp \u57fa\u7c7b\u6709\u540c\u540d\u65b9\u6cd5\uff08\u649e\u540d=\u96f6\u6570\u636e\u6839\u56e0\uff09\u3002
        try:
            req_headers = headers or self.headers
            res = requests.get(url, headers=req_headers, proxies=self.proxies,
                               timeout=timeout, verify=False, allow_redirects=True)
            res.encoding = 'utf-8'
            return res
        except Exception as e:
            print('http error: %s %s' % (url, e))
            return None

    def _get_page(self, url, tries=3):
        """GET \u5e76\u5c31\u5730\u89e3\u58f3\uff1b\u7591\u4f3c\u58f3\u9875/\u7a7a\u7ed3\u679c\u91cd\u8bd5\u3002\u8fd4\u56de**\u5df2\u89e3\u5bc6**\u7684\u6587\u672c\u3002"""
        html = ''
        for i in range(tries):
            res = self._http(url)
            html = (res.text or '') if res else ''
            if _is_shell(html):
                self.trace.append('\u58f3\u9875\u89e3\u5bc6(\u7b2c%d\u6b21): %s' % (i + 1, len(html)))
                html = _unmask(html)
            if html and len(html) > 3000 and ('Html/' in html or 'movie2_list' in html
                                              or 'film_title' in html):
                return html
            self.trace.append('\u7591\u4f3c\u7a7a/\u5f02\u5e38(\u7b2c%d\u6b21): %s' % (i + 1, len(html)))
            time.sleep(0.5)
        return html

    # ---------- \u53d6\u57df\uff08\u81ea\u7814\uff1a\u7ad9\u65b9\u901a\u9053\u662f IP:\u7aef\u53e3\uff0chostresolver \u62bd\u4e0d\u5230\uff09 ----------
    def _candidate_hosts(self):
        cands = []
        if self._ext.get('host'):
            cands.append(self._ext['host'].rstrip('/'))
        for u in (self._ext.get('hosts') or []):
            u = str(u).rstrip('/')
            if u not in cands:
                cands.append(u)
        for u in _BUILTIN_HOSTS:
            if u not in cands:
                cands.append(u)
        return cands

    def _probe_one(self, host_base, result):
        if result[0]:
            return
        try:
            r = requests.get(host_base + _PROBE_PATH, headers=self.headers,
                             proxies=self.proxies, timeout=6, verify=False,
                             allow_redirects=True)
            body = r.text or ''
            ok = (r.status_code == 200 and _valid_page(body))
            self.trace.append('%s -> %s %s' % (host_base, r.status_code, 'OK' if ok else '\u975e\u5185\u5bb9'))
            if ok and not result[0]:
                result[0] = host_base
        except Exception as e:
            self.trace.append('%s -> FAIL %s' % (host_base, str(e)[:40]))

    def _probe_round(self, cands, wait=6):
        import threading
        if not cands:
            return ''
        result = [None]
        threads = [threading.Thread(target=self._probe_one, args=(u, result))
                   for u in cands[:16]]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=wait)
        return result[0] or ''

    def _fetch_publish_hosts(self):
        """\u6293\u53d1\u5e03\u9875\u62bd IP:\u7aef\u53e3 \u901a\u9053\uff08+ \u4efb\u610f\u660e\u6587 http(s) \u4e3b\u673a\uff0c\u53d6 TLD \u5408\u6cd5\u8005\uff09\u3002"""
        out = []
        pages = [self._ext.get('publish') or _PUBLISH]
        for u in str(self._ext.get('publish') or '').replace(';', ',').split(','):
            u = u.strip()
            if u.startswith('http') and u not in pages:
                pages.append(u)
        if _PUBLISH not in pages:
            pages.append(_PUBLISH)
        for pu in pages:
            try:
                r = self._http(pu, timeout=10)
                if not r or r.status_code != 200:
                    continue
                t = r.text or ''
                for m in re.finditer(r'https?://\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}', t):
                    u = m.group(0).rstrip('/')
                    if u not in out:
                        out.append(u)
                for m in re.finditer(r'https?://[a-z0-9][a-z0-9.\-]{3,60}\.[a-z]{2,10}\b', t, re.I):
                    u = m.group(0).rstrip('/')
                    if u not in out and '91fby' not in u:
                        out.append(u)
            except Exception as e:
                self.trace.append('\u53d1\u5e03\u9875\u5931\u8d25 %s %s' % (pu, str(e)[:40]))
        self.trace.append('\u53d1\u5e03\u9875\u62bd\u5230\u5019\u9009 %d \u6761' % len(out))
        return out

    def _dm_hosts(self):
        """\u53d1\u5e03\u9875\u540c\u6e90 /get_dm.php \u2192 \u52a8\u6001\u57df\u5019\u9009\uff08\u672b\u4e24\u6bb5\u57df\u540d\uff0c\u5e26 https\uff09\u3002
        \u7ad9\u65b9\u5b98\u65b9\u673a\u5236\uff1aindex_fby_tiao.html \u5c31\u662f\u8fd9\u4e48\u62ff\u5f53\u524d\u57df\u7684\u3002\u5931\u8d25\u9759\u9ed8\u8fd4 []\u3002"""
        out = []
        origins = []
        for pu in str(self._ext.get('publish') or _DM_ORIGIN).replace(';', ',').split(','):
            pu = pu.strip()
            if pu.startswith('http'):
                m = re.match(r'^(https?://[^/]+)', pu)
                if m and m.group(1) not in origins:
                    origins.append(m.group(1))
        if _DM_ORIGIN not in origins:
            origins.append(_DM_ORIGIN)
        for og in origins:
            try:
                r = self._http(og + '/get_dm.php', timeout=8)
                if not r or r.status_code != 200:
                    continue
                dom = _dm_regdomain(_dm_unwrap(r.text))
                if dom:
                    u = 'https://' + dom
                    if u not in out:
                        out.append(u)
            except Exception as e:
                self.trace.append('get_dm\u5931\u8d25 %s %s' % (og, str(e)[:40]))
        self.trace.append('get_dm\u62bd\u5230\u5019\u9009 %d \u6761' % len(out))
        return out

    def get_working_host(self):
        # \u9501\u5b9a\u57df\uff1a\u586b\u4e86 host@ \u5c31\u53ea\u7528\u5b83
        if self._ext.get('host'):
            return self._ext['host'].rstrip('/')
        # 1) \u5185\u7f6e/ext \u901a\u9053
        h = self._probe_round(self._candidate_hosts(), 8)
        if h:
            return h
        # 2) \u53d1\u5e03\u9875\u540c\u6e90 /get_dm.php \u7684\u52a8\u6001**\u57df\u540d**\u8def\u7ebf\uff08IP \u642c\u673a\u4e5f\u80fd\u81ea\u6108\uff09
        self.trace.append('\u5185\u7f6e\u672a\u547d\u4e2d \u2192 \u8bd5 get_dm.php')
        h = self._probe_round(self._dm_hosts(), 8)
        if h:
            return h
        # 3) \u53d1\u5e03\u9875\u73b0\u62bd IP:\u7aef\u53e3
        self.trace.append('\u4ecd\u672a\u547d\u4e2d \u2192 \u6293\u53d1\u5e03\u9875')
        h = self._probe_round(self._fetch_publish_hosts(), 8)
        if h:
            return h
        return ''

    def _ensure_host(self):
        """init \u53d6\u57df\u5931\u8d25\uff08\u624b\u673a\u7f51\u7edc\u6162\uff09\u2192 \u9996\u6b21\u771f\u6b63\u8bbf\u95ee\u65f6\u518d\u8bd5\u4e00\u6b21\u3002"""
        if self.host:
            return
        self.trace.append('\u61d2\u91cd\u8bd5: \u91cd\u65b0\u53d6\u57df')
        h = self.get_working_host()
        if h:
            self.host = h
            self.headers.update({'Origin': self.host, 'Referer': self.host + '/'})
            print('\u61d2\u91cd\u8bd5\u547d\u4e2d: %s' % self.host)

    # ---------- \u64ad\u653e/\u5c01\u9762\u57df\u540d\u6c60\uff08\u4ece /js/u.js \u5b9e\u65f6\u8bfb\uff0c\u7ad9\u65b9\u8f6e\u6362\u5373\u81ea\u6108\uff09 ----------
    def _pools(self):
        if self._purls and self._durls:
            return self._purls, self._durls
        purls, durls = list(_BUILTIN_PURLS), list(_BUILTIN_DURLS)
        try:
            if self.host:
                r = self._http(self.host + '/js/u.js', timeout=8)
                t = (r.text or '') if r else ''
                if t:
                    mp = _RE_PURLS.search(t)
                    md = _RE_DURLS.search(t)
                    a = _RE_URL_IN_ARR.findall(mp.group(1)) if mp else []
                    b = _RE_URL_IN_ARR.findall(md.group(1)) if md else []
                    if a:
                        purls = [x.rstrip('/') for x in a]
                    if b:
                        durls = [x.rstrip('/') for x in b]
                    self.trace.append('u.js \u6c60: purl=%d durl=%d' % (len(purls), len(durls)))
        except Exception as e:
            self.trace.append('u.js \u8bfb\u53d6\u5931\u8d25 %s' % str(e)[:40])
        self._purls, self._durls = purls, durls
        return purls, durls

    def _pic(self, path):
        """get_local(path) \u2192 \u5b8c\u6574\u56fe\u7247\u5730\u5740\uff08\u56fe\u5e8a\u6c60\u968f\u673a\uff0c\u7ad9\u65b9\u6309\u6d41\u91cf\u5206\u914d\uff09\u3002"""
        path = path or ''
        if not path:
            return ''
        if path.startswith('http'):
            return path
        if not path.startswith('/'):
            path = '/' + path
        _p, durls = self._pools()
        return (random.choice(durls) if durls else '') + path

    # ---------- \u63a5\u53e3 ----------
    def _parse_cats(self, html):
        """\u4ece\u5bfc\u822a\u533a\u5b9e\u65f6\u62bd\u5206\u7c7b\uff08\u7ad9\u65b9\u4f1a\u52a0\u7c7b\uff09\uff1b\u5931\u8d25\u8fd4\u56de []\u3002"""
        out, seen = [], set()
        for m in _RE_CAT.finditer(html or ''):
            tid, name = m.group(1), _clean(m.group(2))
            if not name or len(name) > 12 or tid in seen:
                continue
            if _AD_NAME_RE.search(name):
                continue
            seen.add(tid)
            out.append({'type_name': name, 'type_id': tid})
        return out

    def homeContent(self, filter):
        classes = []
        try:
            self._ensure_host()
            if self.host:
                html = self._get_page(self.host + '/Html/index.html')
                classes = self._parse_cats(html)
        except Exception:
            classes = []
        if not classes:
            classes = [{'type_name': n, 'type_id': t} for n, t in _CATS]
        return {'class': classes, 'filters': {}}

    def homeVideoContent(self):
        try:
            self._ensure_host()
            if not self.host:
                return {'list': []}
            html = self._get_page(self.host + '/Html/index.html')
            return {'list': self._parse_list(html)[:12]}
        except Exception:
            return {'list': []}

    def _parse_list(self, html):
        out = []
        for m in _RE_ITEM.finditer(html or ''):
            link, chunk = m.group(1), m.group(2)
            mm = re.match(r'/Html/(\d+)/(\d+)\.html', link)
            if not mm:
                continue
            vid = '%s/%s' % (mm.group(1), mm.group(2))
            t = _RE_ITEM_TITLE.search(chunk)
            name = _clean(t.group(1)) if t else ''
            if not name:
                continue
            p = _RE_PIC.search(chunk)
            pic = self._pic(p.group(1)) if p else ''
            d = _RE_ITEM_DATE.search(chunk)
            out.append({
                'vod_id': vid,
                'vod_name': name,
                'vod_pic': pic,
                'vod_remarks': _clean(d.group(1)) if d else '',
            })
        return out

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(str(pg or 1) or 1)
        self._ensure_host()
        if not self.host:
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 0, 'total': 0}
        url = ('%s/Html/%s/' % (self.host, tid)) if pg <= 1 else \
              ('%s/Html/%s/index-%d.html' % (self.host, tid, pg))
        html = self._get_page(url)
        lst = self._parse_list(html)
        if not lst and pg > 1:      # \u672b\u9875\u515c\u5e95\uff1a\u8d8a\u754c\u9875\u53ef\u80fd\u56de\u843d\u9996\u9875 \u2192 \u518d\u8bd5\u4e00\u6b21
            html = self._get_page('%s/Html/%s/index-%d.html' % (self.host, tid, pg))
            lst = self._parse_list(html)
        nums = [int(x) for x in _RE_PAGE.findall(html or '')]
        return {
            'list': lst, 'page': pg,
            'pagecount': max(nums) if nums else 1,
            'limit': len(lst), 'total': (max(nums) if nums else 1) * max(len(lst), 1),
        }

    def searchContent(self, key, quick, pg=1):
        # \u672c\u7ad9**\u65e0\u641c\u7d22\u529f\u80fd**\uff08/search* \u5168\u90e8\u56de\u843d\u9996\u9875\uff09\u2192 \u6052\u7a7a\uff0c\u7531 App \u63d0\u793a\u65e0\u7ed3\u679c
        return {'list': [], 'page': int(str(pg or 1) or 1)}

    def detailContent(self, ids):
        vid = str(ids[0])
        self._ensure_host()
        if not self.host:
            return {'list': []}
        url = '%s/Html/%s.html' % (self.host, vid)
        html = self._get_page(url)
        if not html:
            return {'list': []}
        name = ''
        mt = _RE_DET_TITLE.search(html)
        if mt:
            name = _clean(mt.group(1))
        if not name:
            tt = re.search(r'<title>(.*?)</title>', html, re.S)
            name = _clean(tt.group(1)).split('\u9ad8\u6e05\u5728\u7ebf\u89c2\u770b')[0] if tt else str(vid)
        p = _RE_PIC.search(html)
        pic = self._pic(p.group(1)) if p else ''
        nid = vid.rsplit('/', 1)[-1]
        path = '/Html/player/play-%s-0-1.html' % nid
        vod = {
            'vod_id': vid,
            'vod_name': name,
            'vod_pic': pic,
            'vod_content': '\u8d44\u6e90\u6765\u81ea\u4e8e\u7f51\u7edc\uff0c\u8bf7\u52ff\u76f8\u4fe1\u4efb\u4f55\u5e7f\u544a',
            'vod_play_from': _SITE_KEY,
            'vod_play_url': '\u64ad\u653e$%s' % path,
            'vod_remarks': '',
        }
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags=None):
        self._ensure_host()
        if not self.host:
            return {'parse': 1, 'url': ''}
        path = str(id)
        if path.startswith('http'):
            path = re.sub(r'^https?://[^/]+', '', path)
        if not path.startswith('/'):
            path = '/Html/player/play-%s-0-1.html' % path
        play_url = self.host + path
        html = self._get_page(play_url)
        m3u8_path = ''
        m = _RE_MP4.search(html or '')
        if m:
            m3u8_path = m.group(1)
        if not m3u8_path:
            # \u515c\u5e95\uff1a\u4ece down_url \u7684 .mp4 \u8def\u5f84\u63a8 .mp4.m3u8
            d = _RE_DOWN.search(html or '')
            if d:
                p2 = re.sub(r'^https?://[^/]+', '', d.group(1))
                if p2.endswith('.mp4'):
                    p2 += '.m3u8'
                m3u8_path = p2
        if not m3u8_path:
            return {'parse': 1, 'url': play_url}
        if m3u8_path.startswith('http'):
            real = m3u8_path
        else:
            purls, _d = self._pools()
            base = random.choice(purls) if purls else ''
            real = base + ('' if m3u8_path.startswith('/') else '/') + m3u8_path
        return {
            'parse': 0,
            'playUrl': '',
            'url': real,
            'header': {
                'User-Agent': _UA,
                'Referer': play_url,
                'Origin': self.host,
            },
        }

# >>> INLINE-GEN-START >>>
# -*- coding: utf-8 -*-
# \u672c\u533a\u81ea\u52a8\u751f\u6210\uff0c\u8bf7\u52ff\u624b\u6539\u3002\u771f\u6e90\uff1dlocal/hostresolver.py\uff1b\u6539\u4e86\u5b83\u8bf7\u91cd\u8dd1\uff1a
#     python tools/gen_inline_resolvers.py --write
# \u5b58\u5728\u7406\u7531\uff1ahostresolver.py \u4e0d\u662f\u4efb\u4f55\u7ad9\u7684 api\uff0cApp\uff08gitee \u5f62\u6001\uff09\u4e0d\u4f1a\u4e0b\u8f7d\u5b83
# \u2192 \u771f\u673a\u4e0a\u6e90\u5185\u5fc5\u987b\u81ea\u5e26\u6574\u5957\u53d6\u57df\u7b97\u6cd5\uff0c\u5426\u5219\u53ea\u80fd\u5403 v2.6 \u65f6\u4ee3\u7684\u624b\u6284\u7f29\u6c34\u7248\u3002
# FINGERPRINT: cca5f23da886\uff08\u672c\u5757\u5185\u5bb9\u6458\u8981\uff1b\u4e0e\u672c\u4f53\u91cd\u7b97\u4e0d\u7b26\uff1d\u5df2\u8fc7\u671f\uff09
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
_gen_CACHE = {}

_gen_CACHE_TTL = 1800  # \u6210\u529f\u9009\u7ad9\u7f13\u5b58 30 \u5206\u949f


# \u9009\u7ad9\u8fc7\u7a0b\u8bb0\u5f55\uff08\u4f9b\u6e90\u5185\u300c\u8bca\u65ad\u300d\u680f\u76ee\u5c55\u793a\uff0cApp \u7aef\u65e0\u9700\u65e5\u5fd7\u5de5\u5177\u5373\u53ef\u770b\u5230\u5168\u94fe\u8def\uff09
_gen_TRACE = []



def _gen_tr(msg):
    """\u8ffd\u52a0\u4e00\u884c\u9009\u7ad9\u8fc7\u7a0b\u8bb0\u5f55\uff08\u4e0a\u9650 60 \u884c\uff0c\u9632\u9875\u9762\u4e0a\u5237\u5c4f\uff09"""
    try:
        if len(_gen_TRACE) < 60:
            _gen_TRACE.append(str(msg))
    except Exception:
        pass



def _gen_last_trace():
    """\u8fd4\u56de\u4e0a\u4e00\u6b21\u9009\u7ad9\u7684\u9010\u884c\u8bb0\u5f55\uff08\u526f\u672c\uff09"""
    return list(_gen_TRACE)



def _gen_clear_cache():
    """\u6e05\u7a7a\u9009\u7ad9\u7f13\u5b58\uff08\u8c03\u8bd5\u7528\uff1b\u8c03\u7528\u65b9\u4e00\u822c\u4e0d\u9700\u8981\uff09"""
    _gen_CACHE.clear()
    del _gen_TRACE[:]



# ---------------------------------------------------------------- ext \u89e3\u6790
def _gen_parse_ext(ext_str):
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



def _gen_ext_of(extend):
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
                return _gen_ext_of(cfg)
        except Exception:
            pass
        return _gen_parse_ext(s)
    except Exception:
        return {}



# ---------------------------------------------------------------- \u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe
# \u6cdb\u89e3\u6790\u968f\u673a\u8bcd\u6c60\uff08\u4e0e\u7ad9\u65b9\u53d1\u5e03\u9875\u540c\u6e90\u53d6\u5e38\u7528\u82f1\u6587\u8bcd\uff1b\u6cdb\u89e3\u6790 DNS \u4e0b\u4efb\u610f\u8bcd\u5747\u53ef\u89e3\u6790\uff09
_gen_WILD_WORDS = (
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
_gen_WILD_PAT = re.compile(
    r"[\w.]*random\s*\(\s*\)\s*\+\s*['\"]\.([a-z0-9-]+(?:\.[a-z0-9-]+)+)['\"]", re.I)

# \u53d1\u5e03\u9875 b64 \u58f3\uff08document.write(Base64.decode('...')) \u6574\u9875 HTML \u85cf base64\uff09
_gen_B64_SHELL_PAT = re.compile(r"Base64\.decode\(\s*['\"]([A-Za-z0-9+/=]{100,})['\"]")

# v2.3 \u7ebf\u8def\u8868\uff08\u57fa\u57df\u88ab\u85cf\u8fdb\u6a21\u677f\u5b57\u7b26\u4e32 / \u6570\u7ec4\uff0c\u4e0d\u518d\u4ee5 random()+'.\u57fa\u57df' \u5f62\u6001\u51fa\u73b0\uff09
_gen_TICK_PAT = re.compile(r'`([^`]{4,800})`', re.S)

# v2.5 \u7ebf\u8def\u8868\u7b2c\u4e09\u79cd\u5f62\u6001\uff082026-09-14 \u00b7 91\u7206\u6599\u771f\u673a\u5931\u8054\u5b9e\u6d4b\u63ea\u51fa\uff09\uff1a**\u5f15\u53f7\u4e32 + \u6362\u884c**\u2014\u2014
#   var zz_line = "gdubugsu.cc\ncekzqgmk.cc\nd3f9.cloudfront.net";
# \u65e7\u7248\u53ea\u8ba4\u53cd\u5f15\u53f7\u6a21\u677f \u2192 \u6b64\u5f62\u6001\u6574\u7ec4\u62bd 0 \u6761\uff1ab64 \u58f3\u660e\u660e\u89e3\u5f00\u4e86\uff0c\u57fa\u57df\u4ecd\u7136\u770b\u4e0d\u89c1\uff08\u6362\u4e0d\u5230\u57df\uff09\u3002
# \u26a0\u5fc5\u987b**\u951a\u5b9a**\uff08\u57df\u540d+\u6362\u884c+\u57df\u540d\uff09\u800c\u4e0d\u80fd\u7528\u300c\u901a\u7528\u5f15\u53f7\u914d\u5bf9\u300d\u626b\u5168\u9875\uff1a\u5b9e\u6d4b 91\u7206\u6599 \u89e3\u7801\u9875\u6709
#  424 \u4e2a\u5f15\u53f7\u4e32\uff0c\u901a\u7528\u914d\u5bf9\u4f1a\u88ab\u9875\u9996 attr \u8c10\u97f3\u4e32\uff08zh-CN / UTF-8 / X-UA-Compatible\uff09\u6574\u4f53\u9519\u4f4d\uff0c
#  \u771f\u6b63\u7684 zz_line \u4e32\u6c38\u8fdc\u8f6e\u4e0d\u5230 \u2014\u2014 \u8be5\u5199\u6cd5\u5f53\u5929\u5df2\u88ab\u8bc1\u4f2a\u3002
_gen_QUOTED_TABLE_PAT = re.compile(
    r"""['"`]("""
    r"""[a-z0-9][a-z0-9.-]*\.[a-z]{2,15}"""
    r"""(?:(?:\\r\\n|\\n|\r\n|\n)[a-z0-9][a-z0-9.-]*\.[a-z]{2,15})+"""
    r"""(?:\\r\\n|\\n|\r\n|\n)?"""
    r""")['"`]""",
    re.I)

_gen_DOMLINE_PAT = re.compile(r'^[a-z0-9][a-z0-9.-]*\.[a-z]{2,15}$', re.I)

# v2.5 TLD \u767d\u540d\u5355\uff1a\u7ebf\u8def\u8868\u884c\u5c3e\u5fc5\u987b\u843d\u5728**\u771f\u5b9e TLD**\u4e0a\u3002\u65e7\u7248 `[a-z]{2,15}` \u592a\u5bbd\uff0c
# \u4f1a\u628a JS \u5bf9\u8c61\u5c5e\u6027\u4e32\u5f53\u57df\u540d\u62bd\u51fa\uff08\u7389\u7f9e\u56ed \u5b9e\u6d4b\u62bd\u5230 ui.loading.render / ui.router.router /
# ui.close \u2014\u2014 \u5168\u662f JS \u547d\u540d\u7a7a\u95f4\uff0c\u767d\u5360\u63a2\u6d3b\u540d\u989d\u3001\u628a\u771f\u5019\u9009\u6324\u51fa\u53bb\uff09\u3002
_gen_TLD_OK = frozenset((
    'cc com net org cn tv io co me top xyz vip app link click info site online '
    'icu club fun store live shop work sbs cfd dev pro space website press host '
    'art name biz mobi asia wiki news blog ltd group tech cloud world today life '
    'us uk jp kr hk tw sg de fr nl ru in id my th vn ph au ca it es pl se no fi'
).split())

# \u6570\u7ec4\u5143\u7d20**\u5141\u8bb8\u5c3e\u90e8 / **\uff082026-09-13 v2.4\uff09\uff1a\u7ad9\u65b9\u5199\u4f5c urls=['mvbessfgf.cc/','huxrzdjnv.cc/']
# \u2014\u2014\u5c3e\u659c\u6760\u5f88\u5e38\u89c1\uff0c\u65e7\u6b63\u5219\u8981\u6c42\u7eaf\u57df\u540d \u2192 \u6574\u7ec4\u62bd 0 \u6761\uff08\u9ec4\u679c publish.js \u5c31\u662f\u8fd9\u5f62\u6001\uff09\u3002
# **\u7ec4\u5916\u5fc5\u987b\u5bb9\u5c3e\u7a7a\u767d**\uff082026-09-13 \u5b9e\u6d4b\u63ea\u51fa\uff09\uff1a\u771f\u5b9e\u5199\u6cd5\u662f\u591a\u884c\u6570\u7ec4\u3001\u672b\u5143\u7d20\u540e\u8fd8\u6709 `,\n]`\uff0c
# \u65e7\u5f0f `...,?)\]` \u8981\u6c42 `]` \u7d27\u8ddf\u6700\u540e\u4e00\u4e2a\u5143\u7d20 \u2192 \u8de8\u884c\u6570\u7ec4\u5168\u6570\u6f0f\u62bd\uff08\u5355\u884c\u624d\u78b0\u5de7\u80fd\u8fc7\uff09\u3002
_gen_ARR_PAT = re.compile(
    r'\[((?:\s*[\'"][a-z0-9.-]*\.[a-z]{2,15}/?[\'"]\s*,?)+)\s*\]', re.I)

# v2.4 JS \u58f3\u8ddf\u968f\uff1a\u53d1\u5e03\u9875\u628a\u5185\u5bb9\u653e\u8fdb\u5916\u94fe JS\uff08<div id="main"> + <script src="publish.js">\uff09
_gen_JS_SRC_PAT = re.compile(r'<script[^>]+src\s*=\s*["\']([^"\']+)["\']', re.I)

_gen_MAX_JS_PAGES = 3                     # \u6bcf\u4e2a\u53d1\u5e03\u9875\u6700\u591a\u8ddf\u968f\u51e0\u4e2a\u5916\u94fe JS

_gen_MAX_JS_BYTES = 2 * 1024 * 1024       # \u5355\u4e2a JS \u622a\u65ad\u4e0a\u9650\uff08\u9632\u70b8\u5185\u5b58\uff09

# \u53d1\u5e03\u9875\u91cc\u5fc5\u7136\u6df7\u5165\u7684\u7b2c\u4e09\u65b9\u5927\u5e73\u53f0/\u7edf\u8ba1/\u5e7f\u544a\u57df\u2014\u2014\u63a2\u6d4b\u5b83\u4eec\u4f1a\u628a\u5927\u9875\u9762\u8bef\u5224\u6210"\u7ad9\u70b9\u53ef\u7528"
_gen_JUNK_HOST_PAT = re.compile(
    r'(googletagmanager|google-analytics|googleads|gstatic|google\.|gitlab\.|github\.|'
    r'youtube\.|ytimg\.|twitter\.|x\.com|t\.me|telegram\.|addtoany\.|yandex\.|'
    r'browsehappy|schema\.org|w3\.org|qq\.com|apple\.com|bing\.com|baidu\.com|'
    r'magsrv\.|adsrv|ad-provider|chnsrv|stripchat|jsdelivr|unpkg|npmjs|shields\.io|'
    r'699pic|meituan|fontawesome|jquery|bootstrap)', re.I)

# v2.7 \u5c5e\u6027\u85cf\u57df\uff08\u7389\u7f9e\u56ed\u5f62\u6001\uff09\uff1a\u57df\u540d\u62c6\u8fdb HTML \u5c5e\u6027\u3001\u7531 JS \u73b0\u573a\u62fc `${\u968f\u673a\u524d\u7f00}.${base}.${houzui}`\u3002
# \u5fc5\u987b**\u540c\u6807\u7b7e\u5185**\u5339\u914d\uff08`[^>]` \u9650\u5236\uff09\u2014\u2014\u8de8\u6807\u7b7e\u4f1a\u628a\u4e0d\u76f8\u5e72\u7684\u5c5e\u6027\u914d\u6210\u5047\u57df\u3002
_gen_ATTR_BASES_PAT = (
    re.compile(r'data-(?:base|host|domain|sub|prefix)\s*=\s*["\']([A-Za-z0-9][A-Za-z0-9.\-]{1,40})["\']'
               r'[^>]{0,160}?(?:houzui|houzhui|suffix|tld)\s*=\s*["\']([A-Za-z0-9][A-Za-z0-9.\-]{0,20})["\']',
               re.I),
    re.compile(r'(?:houzui|houzhui|suffix|tld)\s*=\s*["\']([A-Za-z0-9][A-Za-z0-9.\-]{0,20})["\']'
               r'[^>]{0,160}?data-(?:base|host|domain|sub|prefix)\s*=\s*["\']([A-Za-z0-9][A-Za-z0-9.\-]{1,40})["\']',
               re.I),
)

# v2.8 \u5360\u4f4d\u7b26\u6620\u5c04\uff08\u5c04\u7a9d\u5f62\u6001\uff09\uff1a\u57df\u540d\u88ab\u88c5\u9970\u7b26\u5f53\u5360\u4f4d\u6253\u6563\uff0c\u8fd0\u884c\u65f6 `.replace` \u624d\u62fc\u56de\u3002
#   var url1 = pre1+'.shewo43\u300a\u51e1\u4eba\u6b4c\u300bcc';
#   var newUrl = "https://"+arr[Num].replace(/\u300a\u51e1\u4eba\u6b4c\u300b/g, '.')+ ...
# \u5360\u4f4d\u7b26\u4e0d\u5199\u6b7b\u5b57\u7b26\u96c6\uff08\u53ef\u80fd\u662f\u300a\u300b/\u203b/\u2606/\u4efb\u610f\u88c5\u9970\u4e32\uff09\uff0c\u53ea\u951a\u5b9a `.replace(/X/g,'Y')` \u8fd9\u4e00\u5f62\u6001\u3002
_gen_PH_MAP_PAT = re.compile(
    r"""\.replace\s*\(\s*/\s*([^/\n]{1,12}?)\s*/\s*[gimsuy]*\s*,\s*['"]([^'"\n]{1,6})['"]\s*\)""")

# v2.8 \u300c\u53d8\u91cf + \u5b57\u9762\u57fa\u57df\u300d\u62fc\u63a5\u7247\u6bb5\uff08\u5c04\u7a9d `var url1 = pre1+'.shewo43.cc';`\uff09\u2014\u2014
#   `_WILD_PAT` \u8981\u6c42 random() \u524d\u7f00\u3001`extract_line_bases` \u8981\u6c42\u7eaf\u57df\u540d\u4e32/\u6570\u7ec4\uff0c
#   \u4e24\u8005\u90fd\u62bd\u4e0d\u5230\u8be5\u5f62\u6001\uff0c\u6545\u987b\u65b0\u62bd\u53d6\u5668\u3002
# \u26a0 **\u5fc5\u987b\u8981\u6c42\u7d27\u8ddf `+` \u62fc\u63a5\u7b26**\uff082026-09-14 \u56de\u5f52\u5b9e\u6d4b\u6559\u8bad\uff09\uff1a\u5360\u4f4d\u7b26\u8fd8\u539f\u4e00\u65e6\u653e\u5bbd\u5230
#   \u300c\u5f15\u53f7\u91cc\u7684\u57df\u540d\u5f62\u6001\u4e32\u300d\uff0c\u666e\u901a\u9875\u9762\u904d\u5730\u90fd\u662f\uff08`+'.'` \u8fd8\u539f\u540e `"www.paypalobjects.com"`\u3001
#   `"//type.googleapis.com"`\uff09\u2014\u2014\u5b9e\u6d4b penzu / car.pvtlbzgj \u4e24\u9875\u56e0\u6b64\u8bef\u62bd
#   paypal / braintree\u00d73 / googleapis \u5171 5 \u4e2a\u5047\u57fa\u57df\uff0c\u6bcf\u4e2a\u8fd8\u4f1a \u00d74 \u8bcd\u751f\u6210\u5b50\u57df\u5019\u9009\uff0c
#   \u628a\u771f\u5019\u9009\u6324\u51fa\u6f14\u6d3b\u540d\u989d\u3002`+` \u65ad\u8a00\u628a\u62bd\u53d6\u9650\u5b9a\u5728\u300c\u771f\u5728\u62fc\u57df\u540d\u300d\u7684\u8bed\u5883\u3002
_gen_FRAG_DOM_PAT = re.compile(
    r"""(?:\+|\.concat\(\s*)['"](\.[a-z0-9][a-z0-9.\-]{1,60}|[a-z0-9][a-z0-9.\-]{1,60})['"]""",
    re.I)

# \u7247\u6bb5\u62bd\u53d6**\u4e13\u7528**\u7684\u7b2c\u4e09\u65b9\u57df\u9ed1\u540d\u5355\uff08\u4e0d\u52a8\u5168\u5c40 _JUNK_HOST_PAT\uff0c\u907f\u514d\u5f71\u54cd\u65e2\u6709\u6e90\u7684\u884c\u4e3a\uff09
_gen_FRAG_JUNK_PAT = re.compile(
    r'(googleapis|google\.|gstatic|googlesyndication|paypal|braintree|stripe|'
    r'cloudflare|akamai|cloudfront|doubleclick|w3\.org|schema\.org|jquery|'
    r'bootstrap|fontawesome|cdnjs|unpkg|jsdelivr)', re.I)

# v2.8 \u76f8\u5bf9\u8def\u5f84\u8df3\u8f6c\uff08\u5c04\u7a9d\u9996\u8df3\u5f62\u6001\uff09\uff1a\u76ee\u6807\u53ea\u6709\u76f8\u5bf9\u8def\u5f84\uff0c\u65e0\u534f\u8bae\u65e0\u4e3b\u673a\u3002
#   var urlList=["\u529b\u4e89\u4e0a\u6e38/index.html","\u594b\u53d1\u56fe\u5f3a/index.html",...]; window.open(urlList[...])
_gen_REL_STR_PAT = re.compile(r"""['"]([^'"\\\s]{1,80})['"]""")

# \u53ea\u5728\u300c\u8df3\u8f6c/\u6253\u5f00\u300d\u8bed\u5883\u91cc\u62bd\u76f8\u5bf9\u8def\u5f84\uff08\u9632\u6b63\u6587/\u8d44\u6e90\u6e05\u5355\u8bef\u62bd\uff09
_gen_REL_CTX_PAT = re.compile(r'window\.open|location\.(?:href|replace|assign)|redirect|onload', re.I)

_gen_REL_MAX_TEXT = 12000                 # \u76f8\u5bf9\u8def\u5f84\u62bd\u53d6\u7684\u9875\u9762\u4f53\u91cf\u4e0a\u9650

# v2.9 \u53d8\u91cf\u62fc\u63a5\uff08\u53d1\u5e03\u9875\u5f62\u6001\uff0c2026-09-14 \u6781\u4e50 `nf198.hscwang7y5m.link/jm6s8/`\uff09\uff1a
#   var sub_str = "bjo-eh1buu5li9"; var tdn_str = "hscwang8s8m1"; var html_go = "https://";
#   html_go += sub_str; html_go += "."; html_go += tdn_str; html_go += "."; html_go += 'cc';
# \u57df\u540d\u88ab\u62c6\u6210\u300c\u72ec\u7acb var \u503c + TLD \u5b57\u9762\u91cf\u300d\uff0c\u9010\u6bb5 `+=` \u624d\u62fc\u56de\u3002\u7247\u6bb5\u65e2\u4e0d\u7d27\u8ddf `+`\uff08`_FRAG_DOM_PAT`
# \u62bd\u4e0d\u5230\uff09\uff0c\u4e5f\u65e0 `.replace` \u5360\u4f4d\u7b26\uff08`_restore_placeholders` \u4e0d\u89e6\u53d1\uff09\u2192 v2.8 \u4e24\u901a\u8def\u5168\u7a7a\u624b\u3002
_gen_JS_VARDEF_PAT = re.compile(
    r"""\b(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*['"]([^'"\n]{0,120})['"]""")

_gen_JS_APPEND_PAT = re.compile(
    r"""\b([A-Za-z_$][\w$]*)\s*\+=\s*(?:['"]([^'"\n]{0,120})['"]|([A-Za-z_$][\w$]*))""")

_gen_JS_CONCAT_MAX_TEXT = 4000            # \u53ea\u5728\u53d1\u5e03\u9875/\u58f3\u9875\u91cf\u7ea7\u542f\u7528\uff08\u6b63\u6587\u5927\u9875\u4e0d\u505a\uff0c\u9632\u8bef\u62bd\uff09



def _gen_host_of(url):
    """\u53d6 URL \u7684 host\uff08\u5c0f\u5199\u3001\u65e0\u7aef\u53e3\u534f\u8bae\uff09\uff0c\u5931\u8d25\u8fd4\u56de ''"""
    m = re.match(r'https?://([^/:?#\s]+)', str(url or ''), re.I)
    return m.group(1).lower() if m else ''



def _gen_is_junk(cand):
    return bool(_gen_JUNK_HOST_PAT.search(_gen_host_of(cand) or cand or ''))



# v2.31\uff1a\u5185\u5bb9\u5f62\u6001**\u6b63\u5411**\u5224\u636e\uff082026-09-11 51\u5403\u74dc\u590d\u76d8\u65b0\u589e\uff09
# \u80cc\u666f\uff1a51\u5403\u74dc \u6709\u4e00\u4e2a 20KB \u7684\u300c\u65b0\u5730\u5740\u516c\u544a\u9875\u300d\uff08401.dzyeamwh.cc\uff09\uff0c\u6b63\u6587\u542b\u7ad9\u540d\u3001\u80fd\u88ab
# \u7ad9\u540d\u6821\u9a8c\u653e\u8fc7\uff0c\u4f46\u6ca1\u6709\u4efb\u4f55\u5185\u5bb9\u7ed3\u6784\u2014\u2014\u9009\u4e2d\u5b83 \u2192 \u5206\u7c7b\u53ea\u6709 3 \u4e2a\u3001\u5217\u8868\u5168\u7a7a\uff0c
# \u6b63\u662f\u300c\u8fde\u5206\u7c7b\u90fd\u5237\u4e0d\u51fa\u6765\u300d\u3002\u6545\u5728\u7ad9\u540d\u6821\u9a8c\u4e4b\u4e0a\u518d\u8981\u6c42\u300c\u50cf\u5185\u5bb9\u7ad9\u300d\u3002
# \u6ce8\uff1av2.3 \u521d\u7248\u8fd8\u5199\u8fc7\u4e00\u4e2a**\u5426\u5b9a\u5f0f**\u5224\u636e _looks_like_nav\uff08\u5916\u94fe\u591a=\u5bfc\u822a\u9875\uff09\uff0c
#     \u540c\u65e5\u5373\u5220\u2014\u2014\u5b83\u5bf9\u7981\u7247\u5929\u5802\uff08oneVideo \u5361\u7247\u3001\u65e0 <article> \u5b57\u9762\u6807\u8bb0\uff09\u8bef\u6740\u3002
#     \u540c\u4e00\u4ef6\u4e8b\u53ea\u7559\u4e00\u4e2a\u6b63\u5411\u5224\u636e\u3002
_gen_CONTENT_MARKS = ('<article', 'post-card', 'video-item', 'oneVideo', 'entry-title',
                  'post-title', 'vod-img', 'vod-txt', 'playlist', 'class="video')

_gen_CONTENT_LINK_PAT = re.compile(
    r'href=["\'][^"\']*/(?:archives?|video|videos|category|categories|post|vod|'
    r'watch|tag|detail|thread|topic|tag_list)[/"\']', re.I)



def _gen_looks_like_content(text):
    """\u50cf\u5185\u5bb9\u7ad9\u5417\uff1a\u6709\u5185\u5bb9\u7ed3\u6784\u6807\u8bb0 / \u6709 \u22655 \u6761\u5185\u5bb9\u578b\u5185\u94fe / \u9875\u9762\u591f\u5927\uff08>80KB\uff09\u3002
    \u5047\u95e8\u7ad9\uff08\u516c\u544a\u9875/\u5bfc\u822a\u9875\uff09\u4e09\u6761\u5168\u4e0d\u6ee1\u8db3\u3002"""
    t = text or ''
    if any(k in t for k in _gen_CONTENT_MARKS):
        return True
    if len(_gen_CONTENT_LINK_PAT.findall(t)) >= 5:
        return True
    return len(t) > 80000



def _gen_b64_try(blob):
    """base64 blob \u2192 \u6587\u672c\uff08\u987b\u542b HTML \u6807\u7b7e\u624d\u7b97\u89e3\u51fa\uff09\uff1b\u5bb9\u9519\u65e0 padding / \u542b\u7a7a\u767d\u3002
    \u5931\u8d25\u8fd4\u56de ''\u3002"""
    try:
        s = re.sub(r'\s+', '', blob or '')
        if len(s) < 100:
            return ''
        s += '=' * (-len(s) % 4)          # v2.6 \u8865 padding\uff1a\u7ad9\u65b9 blob \u5e38\u7701\u5c3e\u90e8 `=`
        d = base64.b64decode(s, validate=False).decode('utf-8', 'ignore')
        return d if ('<' in d and '>' in d) else ''
    except Exception:
        return ''



def _gen_expand_b64_shells(text):
    """\u5c55\u5f00\u53d1\u5e03\u9875\u91cc\u7684 Base64 \u58f3\uff0c\u8fd4\u56de [\u539f\u6587, \u89e3\u7801\u98751, \u89e3\u7801\u98752...]

    v2.6\uff1a\u2460 \u8865 padding \u4fee\u590d\u2014\u2014\u7ad9\u65b9 blob \u5e38\u7701\u5c3e\u90e8 `=`\uff0c\u65e7\u7248\u76f4\u63a5 `b64decode` \u629b\u9519 \u2192
    \u6574\u9875\u58f3\u89e3\u4e0d\u5f00\uff08\u90a3\u4e00\u6b65\u6b63\u662f\u9ed1\u6599\u5bb6\u65cf\u6362\u57df\u94fe\u7684\u7b2c\u4e8c\u8df3\uff09\uff1b\u2461 \u627e\u4e0d\u5230 `Base64.decode('...')`
    \u5b57\u9762\u5f62\u6001\u65f6\uff0c\u9000\u5230\u901a\u7528\u957f blob \u626b\u63cf\uff08\u8986\u76d6 `Base64.decode(x)` \u53d8\u91cf\u5f62\u6001\uff09\u3002"""
    texts = [text]
    blobs = [m.group(1) for m in _gen_B64_SHELL_PAT.finditer(text or '')]
    if not blobs:
        blobs = re.findall(r'[A-Za-z0-9+/=]{400,}', text or '')
    for b in blobs[:3]:
        d = _gen_b64_try(b)
        if d:
            texts.append(d)
    return texts



def _gen_restore_placeholders(text):
    """\u8fd8\u539f\u300c\u5360\u4f4d\u7b26\u6253\u6563\u57df\u540d\u300d\u5199\u6cd5\uff08v2.8\uff0c\u5c04\u7a9d\u5f62\u6001 2026-09-14\uff09\u3002

    \u73b0\u7f51\u5199\u6cd5\uff08shewo1.cc \u4e8c\u7ea7\u58f3\uff09\uff1a\u57df\u540d\u88ab\u88c5\u9970\u7b26\u5f53\u5360\u4f4d\u6253\u6563\uff0c\u8fd0\u884c\u65f6\u624d replace \u62fc\u56de\u2014\u2014
      var url1 = pre1+'.shewo43\u300a\u51e1\u4eba\u6b4c\u300bcc';
      var newUrl = \"https://\"+arr[Num].replace(/\u300a\u51e1\u4eba\u6b4c\u300b/g, '.')+ mulu[...]+'?fby';
    \u76ee\u6807\u57df**\u4e0d\u5728\u4efb\u4f55\u5c5e\u6027\u6216\u5b57\u9762\u91cf\u91cc**\uff08\u524d\u7f00\u8fd8\u662f noncestr(2,2) \u968f\u673a\u91cf\uff09\u2192 \u9759\u6001\u62bd\u94fe
    \uff08_WILD_PAT / extract_line_bases / _attr_bases\uff09\u5168\u90e8\u7a7a\u624b\u3002
    \u672c\u51fd\u6570\u4ece `.replace(/\u5360\u4f4d/g,'\u66ff\u6362')` \u53d6\u6620\u5c04\uff0c\u628a**\u5168\u6587**\u5360\u4f4d\u7b26\u66ff\u6362\u6389 \u2192
    \u5f97\u5230 `pre1+'.shewo43.cc'` \u2192 \u4ea4\u7ed9 `_frag_bases` \u62bd\u57fa\u57df\u3002

    \u8fd4\u56de\u8fd8\u539f\u540e\u7684\u6587\u672c\uff1b\u65e0\u53ef\u8fd8\u539f\u6620\u5c04\u65f6\u8fd4\u56de ''\uff08\u4f9b\u8c03\u7528\u65b9\u5224\u300c\u662f\u5426\u771f\u53d1\u751f\u8fc7\u8fd8\u539f\u300d\uff09\u3002"""
    t = text or ''
    maps = []
    for m in _gen_PH_MAP_PAT.finditer(t):
        ph, rep = m.group(1), m.group(2)
        if len(ph) < 2 or ph == rep or ph not in t or (ph, rep) in maps:
            continue
        maps.append((ph, rep))
    if not maps:
        return ''
    for ph, rep in maps:
        t = t.replace(ph, rep)
    return t if t != (text or '') else ''



def _gen_frag_bases(text):
    """\u4ece\u300c\u8fd8\u539f\u540e\u7684 JS \u62fc\u63a5\u4e32\u300d\u62bd\u57fa\u57df\uff08v2.8\uff0c\u5c04\u7a9d\u5f62\u6001\uff09\u3002

    \u5199\u6cd5\uff1a`var url1 = pre1+'.shewo43.cc';` \u2014\u2014 \u524d\u7f00\u662f**\u53d8\u91cf**\uff08\u8fd0\u884c\u65f6\u968f\u673a\uff09\uff0c
    \u57fa\u57df\u662f\u5b57\u9762\u91cf\u3002`_WILD_PAT` \u8981\u6c42 `random() + '.\u57fa\u57df'`\u3001`extract_line_bases`
    \u8981\u6c42\u7eaf\u57df\u540d\u4e32/\u6570\u7ec4 \u2192 \u4e24\u8005\u90fd\u62bd 0 \u6761\uff1b\u672c\u51fd\u6570\u76f4\u63a5\u626b\u300c\u5f15\u53f7\u5185\u7684\u57df\u540d\u5f62\u6001\u7247\u6bb5\u300d\u3002

    \u26a0 \u53ea\u7531 `_scan_text` \u5728**\u53d1\u751f\u8fc7\u5360\u4f4d\u7b26\u8fd8\u539f**\u65f6\u8c03\u7528\uff1a\u6ee1\u9875\u5f15\u53f7\u4e32\uff08zh-CN /
    index.html / text/html / favicon.ico\uff09\u82e5\u4e0d\u8bbe\u9650\u4f1a\u767d\u5360\u63a2\u6d3b\u540d\u989d\u3002"""
    out = []
    for m in _gen_FRAG_DOM_PAT.finditer(text or ''):
        s = (m.group(1) or '').strip().strip('.').lower()
        if not s or len(s) > 60 or s.count('.') > 3:
            continue
        if not _gen_DOMLINE_PAT.match(s):
            continue
        if s.rsplit('.', 1)[-1] not in _gen_TLD_OK:
            continue
        if _gen_is_junk(s) or _gen_FRAG_JUNK_PAT.search(s):
            continue
        out.append(s)
    return list(dict.fromkeys(out))



def _gen_js_concat_strs(text):
    """\u8fd8\u539f\u300c\u72ec\u7acb var \u503c \uff0b \u8fde\u7eed `+=`\u300d\u62fc\u51fa\u7684\u5b8c\u6574\u4e32\uff08v2.9\uff0c\u53d1\u5e03\u9875\u5f62\u6001 2026-09-14\uff09\u3002

    \u73b0\u7f51\u5199\u6cd5\uff08\u6781\u4e50\u53d1\u5e03\u9875 `nf198.hscwang7y5m.link/jm6s8/`\uff0c2084B\uff09\uff1a
      var sub_str = \"bjo-eh1buu5li9\";
      var tdn_str = \"hscwang8s8m1\";
      var html_go = \"https://\";
      html_go += sub_str; html_go += \".\"; html_go += tdn_str; html_go += \".\"; html_go += 'cc';
      \u2192 https://bjo-eh1buu5li9.hscwang8s8m1.cc/jlhs/

    \u57df\u540d\u88ab\u62c6\u6210**\u72ec\u7acb var \u8d4b\u503c**\uff08\u4e0d\u7d27\u8ddf `+`\uff0c`_FRAG_DOM_PAT` \u62bd\u4e0d\u5230\uff09+ TLD \u5b57\u9762\u91cf\uff0c
    \u9760\u4e00\u4e32 `+=` \u624d\u62fc\u56de\uff1b\u4e5f\u6ca1\u6709 `.replace` \u5360\u4f4d\u7b26\u3002\u2192 v2.8 \u4e24\u6761\u901a\u8def\u5168\u7a7a\u624b\uff0c
    \u8be5\u53d1\u5e03\u9875\u53ea\u80fd\u62bd 0 \u6761\uff08=\u6781\u4e50\u6362\u57df\u540e\u6e90\u65e0\u4ece\u81ea\u6108\uff09\u3002

    \u8fd4\u56de**\u7d2f\u52a0\u8fc7\u7a0b\u4e2d\u6bcf\u4e00\u6b65\u7684\u7ed3\u679c\u4e32**\uff08\u4f9b\u62bd\u57df\u7528\uff1b\u5b8c\u6574\u4e32\u901a\u5e38\u5728\u672b\u6b65\u51fa\u73b0\uff09\u3002
    \u4e09\u91cd\u9650\u6d41\uff1a\u2460 \u6574\u9875 \u2264 `_JS_CONCAT_MAX_TEXT`\uff08\u53d1\u5e03\u9875/\u58f3\u9875\u91cf\u7ea7\uff0c\u6b63\u6587\u5927\u9875\u4e0d\u505a\uff09\uff1b
    \u2461 \u5fc5\u987b\u542b `+=`\uff1b\u2462 \u5355\u6bb5\u4e3a\u7a7a\u5219\u8df3\u8fc7\uff08\u4e0d\u7ed9\u65e0\u5173\u53d8\u91cf\u767d\u8bb0\uff09\u3002
    \u26a0 \u53ea\u505a\u300c\u540c\u4e00\u53d8\u91cf\u81ea\u7d2f\u52a0\u300d\u7684\u6734\u7d20\u8fd8\u539f\uff0c\u4e0d\u505a\u8de8\u53d8\u91cf\u4ee3\u6570\u63a8\u6f14\u2014\u2014**\u5b81\u53ef\u5c11\u62bd\u4e0d\u53ef\u8bef\u62bd**\u3002"""
    t = text or ''
    if not t or len(t) > _gen_JS_CONCAT_MAX_TEXT or '+=' not in t:
        return []
    vals = {}
    for m in _gen_JS_VARDEF_PAT.finditer(t):
        vals[m.group(1)] = m.group(2)
    acc, out = {}, []
    for m in _gen_JS_APPEND_PAT.finditer(t):
        tgt = m.group(1)
        seg = m.group(2) if m.group(2) is not None else vals.get(m.group(3), '')
        if not seg:
            continue
        acc[tgt] = acc.get(tgt, vals.get(tgt, '')) + seg
        out.append(acc[tgt])
    return out



def _gen_rel_paths(text, base_url, max_n=4):
    """\u4ece\u58f3\u9875\u62bd**\u76f8\u5bf9\u8def\u5f84**\u8df3\u8f6c\u76ee\u6807\uff08v2.8\uff0c\u5c04\u7a9d\u9996\u8df3\u5f62\u6001\uff09\u3002

    \u73b0\u7f51\u5199\u6cd5\uff08shewo1.cc \u9996\u8df3 = \u70b9\u51fb\u5f0f\u9009\u62e9\u9875\uff09\uff1a
      <div class=\"enter_button\">\u529b\u4e89\u4e0a\u6e38</div>
      var urlList=[\"\u529b\u4e89\u4e0a\u6e38/index.html\",\"\u594b\u53d1\u56fe\u5f3a/index.html\",\"\u6301\u4e4b\u4ee5\u6052/index.html\"];
      window.open(urlList[Math.floor(...)]+wenhao);
    \u76ee\u6807**\u53ea\u6709\u76f8\u5bf9\u8def\u5f84**\uff08\u65e0\u534f\u8bae\u65e0\u4e3b\u673a\uff09\u2192 `_shell_target` \u7684\u7edd\u5bf9 URL \u5206\u652f\u5168\u7a7a\u624b \u2192 \u6574\u94fe\u65ad\u3002
    \u672c\u51fd\u6570\u5728\u300c\u8df3\u8f6c/\u6253\u5f00\u8bed\u5883\u300d\u4e0b\u626b\u5f15\u53f7\u4e32\uff0c\u53d6\u5f62\u5982 `/a/` \u6216 `a/index.html` \u7684\u76ee\u5f55\u578b\u4e32\uff0c
    \u7528 urljoin \u8865\u6210\u7edd\u5bf9 URL\u3002

    **\u4e09\u91cd\u9650\u6d41\u9632\u8bef\u62bd**\uff1a\u2460 \u9875\u9762 \u2264 _REL_MAX_TEXT\uff1b\u2461 \u5fc5\u987b\u547d\u4e2d _REL_CTX_PAT\uff08window.open /
    location / redirect / onload\uff09\uff1b\u2462 \u5c3e\u6bb5\u5e26\u70b9\u4f46\u4e0d\u662f .html/.htm/.php \u7684\u4e00\u5f8b\u5f53\u8d44\u6e90\u6587\u4ef6\u8df3\u8fc7
    \uff08favicon.ico / indexfby.css / logo.png\uff09\u3002"""
    if not base_url or not text or len(text) > _gen_REL_MAX_TEXT:
        return []
    if not _gen_REL_CTX_PAT.search(text):
        return []
    out = []
    for m in _gen_REL_STR_PAT.finditer(text):
        s = (m.group(1) or '').strip()
        if not s or len(s) > 80 or '://' in s or s.startswith(('//', '#', 'data:')):
            continue
        if not (s.startswith('/') or re.match(r'^[\w\u4e00-\u9fff]+/', s)):
            continue
        tail = s.rstrip('/').rsplit('/', 1)[-1].lower()
        if '.' in tail and not tail.endswith(('.html', '.htm', '.php')):
            continue
        u = urljoin(base_url, s).rstrip('/')
        if re.match(r'^https?://', u) and u not in out and not _gen_is_junk(u):
            out.append(u)
        if len(out) >= max_n:
            break
    return out



def _gen_shell_targets(text, base_url=''):
    """\u4ece\u300c\u8df3\u8f6c\u58f3\u300d\u9875\u62bd\u4e0b\u4e00\u8df3\u5019\u9009 URL **\u5217\u8868**\uff08\u4fdd\u5e8f\uff0c\u22644\uff09\uff1b\u7a7a\u5217\u8868 = \u4e0d\u662f\u8df3\u8f6c\u58f3\u3002

    v2.8 \u8d77\u8fd4\u56de\u5217\u8868\uff08\u65e7 `_shell_target` \u53ea\u8fd4\u5355\u4e2a\uff09\uff1a\u7ad9\u65b9\u5e38\u628a\u58f3\u9875\u5199\u6210**\u591a\u7ebf\u8def\u968f\u673a\u6311\u4e00**
    \uff08\u5c04\u7a9d window.open \u4e09\u76ee\u5f55\uff09\uff0c\u5355\u5019\u9009\u8ddf\u4e0d\u4e0b\u53bb\u5c31\u6574\u94fe\u65ad\u3002

    \u9ed1\u6599\u5bb6\u65cf 2026-09 \u73b0\u7f51\u5f62\u6001\uff08\u6bcf\u65e5\u5927\u8d5b / 51\u5403\u74dc / 51\u6697\u7f51 \u540c\u6b3e\uff0c\u2248300B\uff09\uff1a
      <a id=\"\u968f\u673aID\" href=\"https://\u76ee\u6807\u57df/\" target=\"_self\">\u52a0\u8f7d\u4e2d...</a>
      <script>(function(\u968f\u673a\u53d8\u91cf){...window.location.replace(\u968f\u673a\u53d8\u91cf.href)})
             (document.getElementById(\"\u968f\u673aID\"))</script>
    \u26a0\u8df3\u8f6c\u76ee\u6807\u5728 `<a href>` \u91cc\u3001JS \u53ea\u5f15\u7528\u53d8\u91cf \u2014\u2014 \u65e7 `_js_redirect` \u53ea\u8ba4**\u5b57\u9762\u91cf**
      `location.replace('...')` \u2192 \u8fd9\u7c7b\u9875\u9762\u6574\u9875\u62bd 0 \u6761\u3002

    \u8986\u76d6\u56db\u7c7b\u5f62\u6001\uff08\u6309\u4f18\u5148\u7ea7\uff09\uff1a\u2460 `<a href>` \u52a0\u8f7d\u4e2d/\u8df3\u8f6c\u7c7b\u6587\u6848\uff1b\u2461 \u6781\u5c0f\u9875\u552f\u4e00\u7edd\u5bf9\u5916\u94fe\uff1b
    \u2462 \u5b57\u9762\u91cf JS \u8df3\u8f6c / meta refresh\uff1b\u2463 \u76f8\u5bf9\u8def\u5f84\u76ee\u5f55\uff08v2.8 \u5c04\u7a9d\u5f62\u6001\uff0c\u987b\u4f20 base_url\uff09\u3002"""
    t = text or ''
    if len(t) > 4000:                 # \u5927\u9875\u9762\u4e0d\u662f\u58f3\uff0c\u522b\u8bef\u62bd\u6b63\u6587\u91cc\u7684\u9996\u4e2a\u5916\u94fe
        return []
    out = []
    for _pat in ('<a[^>]+href\\s*=\\s*["\\\'](https?://[^"\\\']+)["\\\'][^>]*>\\s*\u52a0\u8f7d\u4e2d',
                 '<a[^>]+href\\s*=\\s*["\\\'](https?://[^"\\\']+)["\\\'][^>]*>\\s*(?:\u6b63\u5728)?\u8df3\u8f6c',
                 '<a[^>]+href\\s*=\\s*["\\\'](https?://[^"\\\']+)["\\\'][^>]*>\\s*\u8bf7\u7a0d\u5019'):
        m = re.search(_pat, t, re.I)
        if m:
            u = m.group(1).strip().rstrip('/')
            if re.match(r'^https?://', u):
                out.append(u)
            break
    if not out and len(t) < 900:
        hrefs = re.findall(r'<a[^>]+href\s*=\s*["\'](https?://[^"\']+)["\']', t, re.I)
        if len(hrefs) == 1:           # \u6781\u5c0f\u9875 + \u552f\u4e00\u7edd\u5bf9\u5916\u94fe \u2192 \u4e5f\u5f53\u58f3\uff08\u6587\u6848\u53d8\u4e86\u65f6\u515c\u5e95\uff09
            out.append(hrefs[0].strip().rstrip('/'))
    if not out:
        jr = _gen_js_redirect(t)
        if jr:
            out.append(jr)
    if not out and base_url:
        out = _gen_rel_paths(t, base_url)  # v2.8 \u76f8\u5bf9\u8def\u5f84\uff08\u5c04\u7a9d\u5f62\u6001\uff09
    return [u for u in dict.fromkeys(out) if u and not _gen_is_junk(u)]



def _gen_shell_target(text, base_url=''):
    """\u5355\u503c\u7248\uff08\u517c\u5bb9\u65e7\u8c03\u7528\u70b9\uff09\uff1a\u53d6 `_shell_targets` \u9996\u9879\uff1b'' = \u4e0d\u662f\u8df3\u8f6c\u58f3\u3002"""
    cs = _gen_shell_targets(text, base_url)
    return cs[0] if cs else ''



def _gen_follow_shell(url, text, headers, proxies, timeout, max_hop=3, _sink=None):
    """\u4ee5**\u5df2\u6293\u5230\u7684** text \u4e3a\u8d77\u70b9\uff0c\u8fde\u7eed\u8ddf\u968f\u8df3\u8f6c\u58f3\uff08\u2264max_hop \u8df3\uff0c\u9632\u73af\uff09\u3002

    \u8fd4\u56de (\u6700\u7ec8URL, \u5404\u8df3\u6587\u672c\u5217\u8868)\u2014\u2014\u5217\u8868**\u4e0d\u542b**\u8c03\u7528\u65b9\u5df2\u6301\u6709\u7684\u9996\u8df3 text\u3002
    \u7528\u9014\uff1a\u53d1\u5e03\u9875\u505a\u6210\u300c\u52a0\u8f7d\u4e2d\u4e2d\u8f6c\u58f3\u300d\u65f6\uff0c\u771f\u5b9e\u843d\u70b9\uff08b64 \u58f3 / \u660e\u6587\u7ebf\u8def\u8868\uff09\u5728\u4e0b\u4e00\u8df3\uff1b
    \u4e0d\u8ddf\u968f \u2192 \u62bd\u94fe 0 \u6761 \u2192 \u53ea\u80fd\u5403\u5185\u7f6e\u6c60\uff0c\u5185\u7f6e\u6c60\u4e00\u8f6e\u6362\u6574\u6e90\u5373\u6302\u3002

    v2.8\uff1a\u6bcf\u8df3\u53d6**\u5019\u9009\u5217\u8868**\u4f9d\u6b21\u5c1d\u8bd5\uff08\u7ad9\u65b9\u5e38\u5199\u591a\u7ebf\u8def\u968f\u673a\u6311\u4e00\uff0c\u5c04\u7a9d window.open \u4e09\u76ee\u5f55\uff09\uff0c
    \u5e76\u7ef4\u62a4 seen \u96c6\u5408\u9632\u300c\u76f8\u5bf9\u8def\u5f84\u6307\u56de\u81ea\u5df1\u6240\u5728\u76ee\u5f55\u300d\u9020\u6210\u7684\u91cd\u590d\u6293\u53d6\u3002
    **\u76f8\u5bf9\u8def\u5f84\u8df3\u8f6c\u53ea\u5141\u8bb8\u53d1\u751f\u4e00\u6b21**\uff1a\u4e8c\u7ea7\u58f3\u7684\u300c\u7ebf\u8def\u76ee\u5f55\u6570\u7ec4\u300d\uff08`mulu=[\"/a/\",\"/b/\"]`\uff09\u4e0e
    \u9996\u8df3\u9009\u62e9\u9875\u5f62\u6001\u5b8c\u5168\u76f8\u540c\uff0c\u518d\u8ddf\u53ea\u4f1a\u628a\u540c\u4e00\u58f3\u9875\u91cd\u590d\u6293 N \u6b21\uff08\u5c04\u7a9d\u5b9e\u6d4b\u7b2c 2/3 \u8df3\u5747\u56de\u540c\u4e00\u9875\uff0c
    \u767d\u8017 4 \u6b21\u8bf7\u6c42\uff09\u2014\u2014\u771f\u5b9e\u7684\u76f8\u5bf9\u8def\u5f84\u8df3\u8f6c\u53ea\u6709\u300c\u9009\u62e9\u9875 \u2192 \u5185\u5bb9\u58f3\u300d\u8fd9\u4e00\u8df3\u3002"""
    log = _sink.append if _sink is not None else _gen_tr
    cur_u, cur_t, hops = url, text, []
    seen = set([(url or '').rstrip('/')])
    used_rel = False
    for _ in range(max_hop):
        cands = [c for c in _gen_shell_targets(cur_t, cur_u) if c.rstrip('/') not in seen]
        if not cands:
            break
        rel = _gen_rel_paths(cur_t, cur_u)
        if rel and set(cands) <= set(rel):
            if used_rel:
                break
            used_rel = True
        nt, nxt = '', ''
        for c in cands:
            seen.add(c.rstrip('/'))
            _nt = _gen_fetch_text(c, headers, proxies, timeout)
            if _nt:
                nt, nxt = _nt, c
                break
            log('    \u2717 \u8df3\u8f6c\u58f3\u7b2c%d\u8df3\u5019\u9009 %s \u53d6\u4e0d\u5230' % (len(hops) + 1, _gen_host_of(c) or c))
        if not nt:
            break
        log('    \u8df3\u8f6c\u58f3\u7b2c%d\u8df3 \u2192 %s (%dB)' % (len(hops) + 1, _gen_host_of(nxt) or nxt, len(nt)))
        hops.append(nt)
        cur_u, cur_t = nxt, nt
    return cur_u, hops



def _gen_domlines(body):
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
    if len(lines) < 2 or not all(_gen_DOMLINE_PAT.match(l) for l in lines):
        return []
    return [l for l in lines if l.rsplit('.', 1)[-1].lower() in _gen_TLD_OK]



def _gen_extract_line_bases(text):
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
    for m in _gen_TICK_PAT.finditer(text):
        out += _gen_domlines(m.group(1))
    for m in _gen_QUOTED_TABLE_PAT.finditer(text):
        body = m.group(1)
        # \u53ea\u5904\u7406\u5e26\u6362\u884c\u8bed\u4e49\u7684\u4e32\uff08\u5b57\u9762 \n \u6216\u771f\u6362\u884c\uff09\uff1b\u666e\u901a\u5355\u884c\u5f15\u53f7\u4e32\u76f4\u63a5\u8df3\u8fc7\uff0c
        # \u514d\u5f97\u628a\u6ee1\u9875 JS \u5b57\u7b26\u4e32\u5168\u5582\u8fdb _domlines\uff08\u6027\u80fd + \u8bef\u62bd\u53cc\u4fdd\u9669\uff09\u3002
        if '\\n' not in body and '\n' not in body:
            continue
        out += _gen_domlines(body)
    for m in _gen_ARR_PAT.finditer(text):
        # \u5143\u7d20\u53ef\u5e26\u5c3e\u659c\u6760\uff08['a.cc/', 'b.cc/']\uff09\u2014\u2014v2.4 \u8d77\u5bb9\u5fcd
        items = re.findall(r'[\'"]([a-z0-9.-]*\.[a-z]{2,15})/?[\'"]', m.group(1), re.I)
        if len(items) >= 2:
            out += items
    return [b for b in dict.fromkeys(out)
            if not _gen_JUNK_HOST_PAT.search(b) and b.rsplit('.', 1)[-1].lower() in _gen_TLD_OK]



def _gen_attr_bases(t):
    """\u4ece HTML \u5c5e\u6027\u62bd\u300c\u88ab\u62c6\u5f00\u7684\u57df\u540d\u300d\uff08v2.7\uff0c\u7389\u7f9e\u56ed\u5f62\u6001\uff09\u3002
    `<a data-base=\"yxy999p\" houzui=\"icu\">` + JS \u62fc `${3\u4f4d\u968f\u673a\u5b57\u6bcd}.${base}.${houzui}`
    \u2192 \u8fd4\u56de\u57fa\u57df `yxy999p.icu`\uff08\u6e90\u4fa7\u518d\u62fc\u968f\u673a\u524d\u7f00\uff09\u3002\u540c\u6807\u7b7e\u5185\u5339\u914d\uff1b\u540e\u7f00\u987b\u8fc7 _TLD_OK\u3002"""
    out = []
    for i, pat in enumerate(_gen_ATTR_BASES_PAT):
        for m in pat.finditer(t or ''):
            _a, _b = m.group(1), m.group(2)
            base, suf = (_a, _b) if i == 0 else (_b, _a)
            base = (base or '').strip().strip('.').lower()
            suf = (suf or '').strip().strip('.').lower()
            if not base or suf not in _gen_TLD_OK:
                continue
            dom = base + '.' + suf
            if dom.count('.') > 3 or _gen_is_junk(dom):
                continue
            out.append(dom)
    return out



def _gen_scan_text(t, static, wilds):
    """\u4ece\u4e00\u6bb5\u6587\u672c\u62bd\u5019\u9009\uff08\u9759\u6001\u955c\u50cf\u94fe\u63a5\u8fdb static\u3001\u57fa\u57df\u8fdb wilds\uff09\u3002
    HTML \u672c\u4f53 / b64 \u89e3\u7801\u9875 / \u5916\u94fe JS \u4e09\u79cd\u6765\u6e90\u5171\u7528\u540c\u4e00\u5957\u5224\u636e\u3002

    v2.8\uff1a\u6587\u672c\u82e5\u542b\u300c\u5360\u4f4d\u7b26\u6253\u6563\u57df\u540d\u300d\u5199\u6cd5\uff08`.replace(/\u300a\u51e1\u4eba\u6b4c\u300b/g,'.')`\uff09\uff0c\u5148\u8fd8\u539f\u518d\u626b\u4e00\u904d\uff0c
    \u5e76\u5bf9\u8fd8\u539f\u6587\u672c\u542f\u7528 `_frag_bases`\uff08\u300c\u53d8\u91cf+\u5b57\u9762\u57fa\u57df\u300d\u62fc\u63a5\u5f62\u6001\uff0c\u5c04\u7a9d\u540c\u6b3e\uff09\u3002"""
    t = t or ''
    _gen_scan_one(t, static, wilds)
    rt = _gen_restore_placeholders(t)
    if rt:
        _gen_scan_one(rt, static, wilds, frag=True)



def _gen_scan_one(t, static, wilds, frag=False):
    """\u5355\u8f6e\u62bd\u53d6\u3002frag=True \u65f6\u989d\u5916\u8dd1 `_frag_bases`\uff08**\u4ec5\u8fd8\u539f\u6587\u672c**\uff0c\u9632\u6ee1\u9875\u5f15\u53f7\u4e32\u8bef\u62bd\uff09\u3002"""
    t = t or ''
    for l in re.findall(r'href=["\'](https?://[^"\']+)["\']', t, re.I):
        m = re.match(r'https?://([a-z0-9.-]+\.[a-z]{2,})', l, re.I)
        if m and not _gen_JUNK_HOST_PAT.search(m.group(1)):
            static.append('https://' + m.group(1))
    for m in _gen_WILD_PAT.finditer(t):
        wilds.add(m.group(1))
    for b in _gen_attr_bases(t):                    # v2.7 \u5c5e\u6027\u85cf\u57df\uff08data-base\u00d7houzui\uff09
        wilds.add(b)
    for b in _gen_extract_line_bases(t):
        wilds.add(b)
    if frag:
        for b in _gen_frag_bases(t):                # v2.8 \u5360\u4f4d\u7b26\u8fd8\u539f\u540e\u7684\u7247\u6bb5\u62fc\u63a5\u57df
            wilds.add(b)
    for s in _gen_js_concat_strs(t):                # v2.9 \u53d8\u91cf\u62fc\u63a5\u8fd8\u539f\uff08\u53d1\u5e03\u9875\u5f62\u6001\uff09
        m = re.match(r'https?://([a-z0-9][a-z0-9.\-]*)', s, re.I)
        if not m:
            continue
        h = m.group(1).strip('.').lower()
        # \u26a0 \u7d2f\u52a0\u662f**\u9010\u6bb5**\u7684\uff0c\u4e2d\u95f4\u6001\u4e5f\u662f\u5408\u6cd5\u5b57\u7b26\u4e32\uff08`https://bjo-eh1buu5li9`\u3001
        #   `...hscwang8s8m1`\uff09\u2014\u2014\u672b\u6bb5\u975e\u5408\u6cd5 TLD \u7684\u4e00\u5f8b\u4e22\u5f03\uff0c\u5426\u5219\u6bcf\u6b21\u767d\u8017\u63a2\u6d3b\u540d\u989d\u3002
        if (len(h) > 80 or h.count('.') > 4 or h.rsplit('.', 1)[-1] not in _gen_TLD_OK
                or _gen_is_junk(h) or _gen_FRAG_JUNK_PAT.search(h)):
            continue
        if ('https://' + h) not in static:
            static.append('https://' + h)
        parts = h.split('.')
        if len(parts) >= 3:                     # \u6cdb\u89e3\u6790\u65cf\uff1a\u5265\u6700\u5de6\u6807\u7b7e\u5f97\u57fa\u57df
            base = '.'.join(parts[1:])
            if (base.rsplit('.', 1)[-1] in _gen_TLD_OK and not _gen_is_junk(base)
                    and not _gen_FRAG_JUNK_PAT.search(base)):
                wilds.add(base)



def _gen_text_of(r):
    """\u4ece\u54cd\u5e94\u53d6\u6587\u672c\uff0c\u5e76\u4fee\u590d\u300cUTF-8 \u88ab\u8bef\u6309 Latin-1 \u89e3\u7801\u300d\u7684\u4e71\u7801\uff08v2.8\uff09\u3002

    \u26a0 \u6839\u56e0\u7ea7\u5751\uff082026-09-14 \u5c04\u7a9d\u5b9e\u6d4b\u63ea\u51fa\uff09\uff1a\u7ad9\u65b9\u54cd\u5e94\u5934\u5199 `Content-Type: text/html`
    **\u4e0d\u5e26 charset** \u2192 requests \u6309 HTTP \u89c4\u8303\u9ed8\u8ba4 `ISO-8859-1` \u89e3\u7801 UTF-8 \u5b57\u8282 \u2192
    \u9875\u9762\u6240\u6709\u4e2d\u6587\u53d8 Latin-1 \u9ad8\u4f4d\u5b57\u7b26\uff08`\u529b\u4e89\u4e0a\u6e38` \u2192 `\u00e5\\x8a\\x9b\u00e4\u00ba\\x89...`\uff09\uff0c
    \u5176\u4e2d\u7684 C1 \u63a7\u5236\u5b57\u7b26\uff08U+0080\u2013U+009F\uff09**\u4e0d\u6ee1\u8db3 `\\w`** \u2192 \u542b\u4e2d\u6587\u7684\u76f8\u5bf9\u8def\u5f84\u3001
    \u5206\u7c7b\u540d\u3001\u6807\u9898\u5168\u90e8\u5339\u914d\u5931\u8d25\uff08\u5c04\u7a9d\u9996\u8df3\u7684\u4e09\u6761\u4e2d\u6587\u76ee\u5f55\u56e0\u6b64\u62bd 0 \u6761\uff0c\u6574\u94fe\u65ad\uff09\u3002
    \uff08\u6613\u8bef\u5224\uff1a\u7ec8\u7aef GBK \u663e\u793a\u4e5f\u4f1a\u82b1\u5c4f\uff0c\u770b\u8d77\u6765\"\u50cf\u7f16\u7801\u95ee\u9898\"\u5176\u5b9e\u662f**\u53cc\u91cd\u4e71\u7801**\u2014\u2014
      requests \u89e3\u7801\u9519 + \u7ec8\u7aef\u663e\u793a\u9519\u3002\u5224\u636e\uff1a`r.encoding` \u4e3a ISO-8859-1 \u800c `r.content`
      \u662f\u5408\u6cd5 UTF-8\u3002\uff09

    \u4fee\u590d\uff1a\u51fa\u73b0 Latin-1 \u9ad8\u4f4d\u5b57\u7b26\u65f6\uff0c\u6309 latin-1 \u7f16\u56de\u5b57\u8282\u518d\u6309 utf-8 \u89e3\uff08\u5931\u8d25\u5373\u8fd4\u56de\u539f\u6587\uff0c
    \u5bf9\u7eaf ASCII / \u771f GBK \u9875\u9762\u96f6\u526f\u4f5c\u7528\uff09\u3002"""
    t = getattr(r, 'text', None) or ''
    if t and re.search(r'[\u0080-\u00ff]', t):
        try:
            return t.encode('latin-1').decode('utf-8')
        except Exception:
            pass
    return t



def _gen_fetch_text(url, headers, proxies, timeout, cap=_gen_MAX_JS_BYTES):
    """GET \u53d6\u6587\u672c\uff08\u5931\u8d25/\u975e 200 \u2192 ''\uff09\uff1b\u8d85 cap \u622a\u65ad\u3002\u7528\u4e8e\u8ddf\u968f\u5916\u94fe JS\u3002"""
    if requests is None or not url:
        return ''
    try:
        r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout,
                         verify=False, allow_redirects=True)
        if r.status_code != 200:
            return ''
        t = _gen_text_of(r)
        return t if len(t) <= cap else t[:cap]
    except Exception:
        return ''



def _gen_js_candidates(html, base_url):
    """\u53d1\u5e03\u9875\u91cc\u7684\u5916\u94fe JS\uff08JS \u58f3\u8ddf\u968f\u7528\uff09\u3002\u76f8\u5bf9\u8def\u5f84\u6309\u53d1\u5e03\u9875\u5730\u5740\u8865\u5168\uff1b
    \u5254\u7b2c\u4e09\u65b9 CDN/\u7edf\u8ba1\u57df\uff0c\u4fdd\u5e8f\u53bb\u91cd\uff0c\u6700\u591a _MAX_JS_PAGES \u4e2a\u3002"""
    out = []
    for m in _gen_JS_SRC_PAT.finditer(html or ''):
        raw = (m.group(1) or '').strip()
        if not raw or raw.startswith('data:'):
            continue
        u = urljoin(base_url or '', raw)
        if not re.match(r'^https?://', u):
            continue
        if _gen_is_junk(u) or u in out:
            continue
        out.append(u)
        if len(out) >= _gen_MAX_JS_PAGES:
            break
    return out



def _gen_extract_publish_domains(publish_page, headers, proxies, timeout, _sink=None):
    """\u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe\u3002\u8fd4\u56de (\u9759\u6001\u955c\u50cf\u94fe\u63a5\u5217\u8868, \u6cdb\u89e3\u6790/\u7ebf\u8def\u8868\u57fa\u57df\u5217\u8868)\u3002
    JS \u6e32\u67d3\u4f46\u65e0 b64 \u58f3\u7684\u9875\u9762\u9759\u6001\u94fe\u63a5\u4ecd\u53ef\u80fd\u4e3a\u7a7a\u2014\u2014\u57fa\u57df\u8bc6\u522b\u662f\u4e3b\u901a\u9053\uff1b
    \u82e5 HTML \u9636\u6bb5\u57fa\u57df\u4e3a 0\uff08JS \u58f3\u5f62\u6001\uff1a\u5185\u5bb9\u5728\u5916\u94fe js\uff09\uff0c\u81ea\u52a8**\u8ddf\u968f\u5916\u94fe JS** \u518d\u626b\u4e00\u904d\u3002

    _sink\uff1a\u53ef\u9009 list\uff0c\u672c\u9875\u7684 trace \u884c\u5199\u5165\u5b83\u800c\u975e\u5168\u5c40 _TRACE\u2014\u2014\u5e76\u884c\u6293\u591a\u9875\u65f6\u5404\u9875\u72ec\u7acb
    \u6536\u96c6\u3001\u7531\u8c03\u7528\u65b9\u6309\u5e8f\u5199\u56de\uff0c\u907f\u514d\u591a\u7ebf\u7a0b\u4ea4\u9519\u5bfc\u81f4\u8bca\u65ad\u8bb0\u5f55\u4e71\u5e8f\u3002"""
    log = _sink.append if _sink is not None else _gen_tr
    if requests is None or not publish_page:
        return [], []
    try:
        r = requests.get(publish_page, headers=headers, proxies=proxies,
                         timeout=timeout, verify=False, allow_redirects=True)
        html = _gen_text_of(r)
        log('[\u53d1\u5e03\u9875] %s \u2192 HTTP %s / %dB' % (_gen_host_of(publish_page) or publish_page,
                                             r.status_code, len(html)))
        if r.status_code != 200:
            log('  \u2717 \u53d1\u5e03\u9875\u975e 200\uff0c\u62bd\u94fe\u4e2d\u6b62')
            return [], []
    except Exception as e:
        log('[\u53d1\u5e03\u9875] %s \u6293\u53d6\u5f02\u5e38: %s' % (_gen_host_of(publish_page) or publish_page,
                                       str(e)[:60]))
        return [], []
    static, wilds = [], set()
    # \u24ea \u8df3\u8f6c\u58f3\u8ddf\u968f\uff08v2.6\uff0c2026-09-14\uff09\uff1a\u53d1\u5e03\u9875\u53ef\u80fd\u662f \u2248300B \u7684\u300c\u52a0\u8f7d\u4e2d\u300d\u4e2d\u8f6c\u58f3
    #    \uff08\u9ed1\u6599\u5bb6\u65cf\u73b0\u7f51\u540c\u6b3e\uff1a<a href>\u52a0\u8f7d\u4e2d</a> + location.replace(\u53d8\u91cf.href)\uff09\u3002
    #    \u771f\u5b9e\u843d\u70b9\uff08b64 \u58f3 / \u660e\u6587\u7ebf\u8def\u8868\uff09\u5728\u4e0b\u4e00\u8df3 \u2014\u2014 \u4e0d\u8ddf\u968f\u5219\u62bd\u94fe 0 \u6761\u3001\u53ea\u80fd\u5403\u5185\u7f6e\u6c60\uff0c
    #    \u5185\u7f6e\u6c60\u4e00\u65e6\u88ab DNS \u6c61\u67d3/\u8f6e\u6362\u6574\u6e90\u5373\u6302\uff0851\u6697\u7f51 \u590d\u76d8\uff09\u3002
    fin_u, hops = _gen_follow_shell(publish_page, html, headers, proxies, timeout, 3, _sink)
    texts = []
    for _t in [html] + hops:
        texts += _gen_expand_b64_shells(_t)
    # \u26a0 \u8ba1\u6570\u53e3\u5f84\u4fee\u6b63\uff08v2.8\uff09\uff1a_expand_b64_shells \u8fd4\u56de `[\u539f\u6587] + \u89e3\u51fa\u7684\u58f3`\uff0c
    #   \u6545\u300c\u89e3\u51fa\u4e2a\u6570\u300d= \u603b\u957f - \u8f93\u5165\u6587\u672c\u6570\uff0c\u800c\u975e \u603b\u957f-1\uff08\u65e7\u5199\u6cd5\u628a hops \u4e5f\u7b97\u6210 b64 \u58f3\uff0c
    #   \u5c04\u7a9d\u5b9e\u6d4b\u65e5\u5fd7\u62a5\u300c\u5c55\u5f00 b64 \u58f3 3 \u4e2a\u300d\u800c\u5b9e\u9645 0 \u4e2a\uff0c\u8bef\u5bfc\u6392\u67e5\uff09\u3002
    _n_b64 = len(texts) - (1 + len(hops))
    if _n_b64 > 0:
        log('  \u5c55\u5f00 b64 \u58f3 %d \u4e2a' % _n_b64)
    for t in texts:
        _gen_scan_text(t, static, wilds)
    if hops and fin_u and fin_u.rstrip('/') != (publish_page or '').rstrip('/'):
        static.append(fin_u)          # \u8df3\u8f6c\u843d\u70b9\u672c\u8eab\u4e5f\u662f\u5019\u9009\uff08\u7ad9\u65b9\u5e38\u628a\u843d\u70b9\u505a\u6210\u6d3b\u955c\u50cf\uff09
    # \u2461 JS \u58f3\u8ddf\u968f\uff1aHTML \u62bd\u4e0d\u5230\u57fa\u57df \u2192 \u7ebf\u8def\u5728 <script src="publish.js"> \u91cc\uff08\u9ec4\u679c\u540c\u6b3e\u5f62\u6001\uff09
    #    v2.6\uff1a\u82e5\u5df2\u8ddf\u968f\u8df3\u8f6c\u58f3\uff0c\u5219\u4ee5**\u843d\u70b9\u9875**\u4e3a\u57fa\u51c6\u8ddf\u968f\uff08\u843d\u70b9\u624d\u662f\u771f\u53d1\u5e03\u9875\uff09\u3002
    if not wilds:
        _base_html = (hops[-1] if hops else html)
        _base_url = fin_u or publish_page
        js_urls = _gen_js_candidates(_base_html, _base_url)
        if js_urls:
            log('  JS \u58f3\u8ddf\u968f %d \u4e2a: %s'
                % (len(js_urls), ', '.join(u.split('//', 1)[-1] for u in js_urls)))
            for ju in js_urls:
                jt = _gen_fetch_text(ju, headers, proxies, timeout)
                if not jt:
                    log('    \u2717 %s \u53d6\u4e0d\u5230' % _gen_host_of(ju))
                    continue
                log('    \u2713 %s %dB' % (_gen_host_of(ju), len(jt)))
                for t in _gen_expand_b64_shells(jt):
                    _gen_scan_text(t, static, wilds)
    log('  \u62bd\u94fe: \u9759\u6001\u94fe\u63a5 %d \u4e2a / \u57fa\u57df %d \u4e2a %s'
        % (len(dict.fromkeys(static)), len(wilds),
           ('\u2192 ' + ', '.join(sorted(wilds)[:6])) if wilds else ''))
    return list(dict.fromkeys(static)), list(wilds)



def _gen_extract_pages(pages, headers, proxies, timeout):
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
                results[i] = _gen_extract_publish_domains(pg, headers, proxies,
                                                     timeout, traces[i])
            except Exception:
                results[i] = ([], [])
    else:
        ex = ThreadPoolExecutor(max_workers=min(6, n))
        try:
            futs = {}
            for i, pg in enumerate(pages):
                futs[ex.submit(_gen_extract_publish_domains, pg, headers, proxies,
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



def _gen_dedupe(urls):
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



def _gen_split_publish_pages(publish_page):
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
def _gen_js_redirect(t):
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



def _gen_root_of(u):
    """\u53d6 URL \u7684 scheme://host \u6839\uff08\u53bb\u8def\u5f84/\u67e5\u8be2\uff09\u3002"""
    m = re.match(r'(https?://[^/?#]+)', str(u or ''), re.I)
    return m.group(1).rstrip('/') if m else ''



def _gen_probe(url, headers, proxies, timeout, depth=0, validate=None, probe_path=None):
    """\u6d4b\u8bd5\u5355\u57df\u540d\uff1a\u8df3\u8f6c\u58f3\u5219\u8ddf\u968f\uff08\u22643 \u5c42\uff0c`_shell_target` \u7edf\u4e00\u5224 <a href>\u52a0\u8f7d\u4e2d / \u5b57\u9762\u91cf JS /
    meta refresh / \u76f8\u5bf9\u8def\u5f84\u76ee\u5f55\uff09\uff1b\u6574\u9875 b64 \u58f3\u5219\u89e3\u7801\u540e\u6309\u5f62\u6001\u5224+\u6821\u9a8c\u8ba4\u5f53\u524d\u57df\u3002
    \u771f\u5185\u5bb9\u8fd4\u56de\u6700\u7ec8 host\uff1b\u5931\u8d25 None\u3002
    validate(final_host, text) -> bool\uff1a\u5185\u5bb9\u8eab\u4efd\u6821\u9a8c\uff08\u9632\u5e7f\u544a\u95e8\u7ad9/\u7b2c\u4e09\u65b9\u9875\u5192\u5145\uff09\u3002
    \u672a\u4f20 validate \u65f6\u9000\u5230\u300c\u5185\u5bb9\u5f62\u6001\u5224\u300d\uff1a\u5916\u94fe\u5f88\u591a\u53c8\u65e0\u5185\u5bb9\u7ed3\u6784 = \u5bfc\u822a\u9875 \u2192 \u62d2\u7edd\u3002

    probe_path\uff08v2.8\uff09\uff1a\u5019\u9009\u57df\u540d**\u6839\u8def\u5f84\u662f\u58f3\u9875 / \u9009\u62e9\u9875\u3001\u53ea\u6709\u6df1\u94fe\u624d\u662f\u771f\u5185\u5bb9**\u65f6\u4f20\u5b83
    \uff08\u5c04\u7a9d `/vodtype/55-1.html`\u3001\u6781\u4e50\u7981\u533a `/vodtype/45-1/`\uff1a\u6839 3214B \u9009\u62e9\u9875\u3001\u6df1\u94fe 64KB \u5185\u5bb9\uff09\u3002
    **\u53ea\u5728\u9996\u8df3\u62fc\u63a5**\uff08\u8df3\u8f6c\u843d\u70b9\u4e0d\u518d\u62fc\uff09\uff0c\u547d\u4e2d\u540e\u8fd4\u56de**\u7ad9\u70b9\u6839**\uff08scheme://host\uff09\u2014\u2014
    \u5426\u5219\u8c03\u7528\u65b9 `self.host + '/vodtype/...'` \u4f1a\u62fc\u51fa\u53cc\u8def\u5f84\u3002"""
    if requests is None:
        return None
    req = url
    if probe_path and depth == 0:
        req = url.rstrip('/') + '/' + str(probe_path).lstrip('/')
    try:
        r = requests.get(req, headers=headers, proxies=proxies,
                         timeout=timeout, verify=False, allow_redirects=True)
        if r.status_code != 200:
            return None
        t = _gen_text_of(r)
        final = (r.url or req).rstrip('/')
        ret = _gen_root_of(final) if probe_path else final
        if len(t) < 4000 and depth < 3:
            # \u2460 \u8df3\u8f6c\u58f3\u8ddf\u968f\uff1a<a href>\u52a0\u8f7d\u4e2d / \u53d8\u91cf.href / \u5b57\u9762\u91cf JS / meta refresh / \u76f8\u5bf9\u76ee\u5f55
            #    \u7edf\u4e00\u5224\uff08v2.6 \u9ed1\u6599\u5bb6\u65cf\u5f62\u6001\uff1bv2.8 \u8865\u76f8\u5bf9\u8def\u5f84\u76ee\u5f55\uff0c\u5c04\u7a9d\u9996\u8df3\uff09
            #    \u76f8\u5bf9\u8def\u5f84**\u53ea\u5728\u9996\u8df3**\u542f\u7528\uff08depth==0 \u624d\u4f20 base_url\uff09\u2014\u2014\u5426\u5219\u4e8c\u7ea7\u58f3\u7684\u7ebf\u8def\u76ee\u5f55
            #    \u6570\u7ec4\u4f1a\u88ab\u5f53\u4e0b\u4e00\u8df3\u3001\u628a\u540c\u4e00\u58f3\u9875\u53cd\u590d\u6293\uff08\u5c04\u7a9d\u5b9e\u6d4b\u767d\u8017 2 \u6b21\u8bf7\u6c42\uff09
            tgt = _gen_shell_target(t, final if depth == 0 else '')
            if tgt and tgt.rstrip('/') != final:
                return _gen_probe(tgt, headers, proxies, timeout, depth + 1, validate)
        # \u2460' \u6574\u9875 b64 \u58f3\uff08\u53d1\u5e03\u94fe\u7b2c\u4e8c\u8df3\uff09\uff1a\u89e3\u7801\u9875\u82e5\u300c\u50cf\u5185\u5bb9\u7ad9\u300d\u4e14\u8fc7\u8eab\u4efd\u6821\u9a8c \u2192 \u8ba4\u5f53\u524d\u57df
        #    \uff082026-09-14\uff1a\u8df3\u8f6c\u58f3\u2192b64\u58f3\u2192\u771f\u7ad9 \u662f\u9ed1\u6599\u5bb6\u65cf\u73b0\u7f51\u4e3b\u94fe\uff0c\u65e7\u7248\u5230\u7b2c\u4e8c\u8df3\u5373\u65ad\uff09
        if len(t) < 60000:
            for _d in _gen_expand_b64_shells(t)[1:]:
                if not _gen_looks_like_content(_d):
                    continue
                if validate is not None:
                    try:
                        if not validate(ret, _d):
                            continue
                    except Exception:
                        continue
                return ret
        if len(t) > 5000 or ('article' in t and 'category' in t):
            if not _gen_looks_like_content(t):
                return None                     # \u5047\u95e8\u7ad9\uff1a\u516c\u544a\u9875/\u5bfc\u822a\u9875\uff0c\u4e0d\u542b\u5185\u5bb9\u7ed3\u6784
            if validate is not None:
                try:
                    if not validate(ret, t):
                        return None
                except Exception:
                    return None
            return ret
        return None
    except Exception:
        return None



def _gen_probe_all(urls, headers, proxies, timeout, validate=None, tag='', probe_path=None):
    """\u5e76\u884c\u63a2\u6d4b\uff0c\u4efb\u4e00\u5019\u9009\u6210\u529f\u5373\u523b\u8fd4\u56de\uff08\u53d6\u6d88\u5176\u4f59\u4efb\u52a1\uff09\uff1b\u5168\u8d25\u8fd4\u56de ''\u3002
    \u603b\u8017\u65f6 \u2248 \u5355\u6b21\u8d85\u65f6\uff0c\u4e0d\u518d\u968f\u5019\u9009\u6570\u91cf\u53e0\u52a0\u3002"""
    if not urls:
        return ''
    if not (ThreadPoolExecutor and as_completed) or len(urls) == 1:
        for u in urls:
            h = _gen_probe(u, headers, proxies, timeout, 0, validate, probe_path)
            _gen_tr('  [%s] %s' % (tag or '\u4e32\u884c', ('\u2713 ' + h) if h else ('\u2717 ' + _gen_host_of(u))))
            if h:
                return h
        return ''
    ex = ThreadPoolExecutor(max_workers=min(12, len(urls)))
    try:
        futs = dict((ex.submit(_gen_probe, u, headers, proxies, timeout, 0, validate,
                               probe_path), u)
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
                _gen_tr('  [%s] \u2713 %s\uff08\u5019\u9009 %s \u547d\u4e2d\uff09' % (tag or '\u5e76\u884c', r, _gen_host_of(ok_u)))
                return r
        _gen_tr('  [%s] \u2717 %d \u4e2a\u5019\u9009\u5168\u90e8\u5931\u8d25' % (tag or '\u5e76\u884c', len(urls)))
        return ''
    finally:
        ex.shutdown(wait=False)



def _gen_probe_first(urls, headers=None, proxies=None, timeout=8, validate=None, tag='\u515c\u5e95',
                probe_path=None):
    """\u516c\u5f00\u7248\u5e76\u884c\u63a2\u6d4b\uff08\u4f9b\u5404\u6e90\u7684\u300c\u5185\u7f6e\u5019\u9009\u515c\u5e95\u300d\u7528\uff0c\u66ff\u4ee3 5\u00d78s \u4e32\u884c\u5faa\u73af\uff09\u3002
    \u4efb\u4e00\u6210\u529f\u5373\u8fd4\u56de\u5176 host\uff08\u53bb\u5c3e\u659c\u6760\uff09\uff0c\u5168\u8d25\u8fd4\u56de ''\u3002
    probe_path\uff1a\u6df1\u94fe\u63a2\u6d4b\u8def\u5f84\uff08v2.8\uff09\uff0c\u6839\u8def\u5f84\u662f\u58f3\u9875\u3001\u6df1\u94fe\u624d\u662f\u5185\u5bb9\u65f6\u4f20\uff08\u89c1 `_probe`\uff09\u3002"""
    return _gen_probe_all(_gen_dedupe(urls or []), headers, proxies, timeout, validate, tag,
                      probe_path)



def _gen_auto_validate(site_key):
    """\u6309\u7ad9\u540d\u751f\u6210\u8eab\u4efd\u6821\u9a8c\u51fd\u6570\uff08validate \u7f3a\u7701\u65f6\u7684\u9ed8\u8ba4\u5b9e\u73b0\uff09"""
    def _v(host, text):
        return site_key in (text or '')
    return _v



# ---------------------------------------------------------------- \u4e3b\u5165\u53e3
def _gen_resolve_host(publish_page=None, candidate_hosts=None, headers=None,
                 proxies=None, timeout=8, use_cache=True, validate=None,
                 site_key=None, probe_path=None):
    """\u8fd4\u56de\u5f53\u524d\u53ef\u7528 host\uff08\u53bb\u5c3e\u659c\u6760\uff09\u3002\u5168\u90e8\u5931\u8d25\u8fd4\u56de ''\uff08\u8c03\u7528\u65b9\u63a5\u53e3\u5c42\u81ea\u884c\u515c\u7a7a\uff09\u3002

    validate(final_host, text)->bool\uff1a\u7ad9\u70b9\u8eab\u4efd\u6821\u9a8c\u56de\u8c03\u3002
    site_key\uff1a\u7ad9\u540d\u5173\u952e\u8bcd\uff1bvalidate \u7f3a\u7701\u65f6\u81ea\u52a8\u7528\u5b83\u751f\u6210\u6821\u9a8c\uff08\u518d\u4e0d\u4f20\u5219\u9000\u5230\u5185\u5bb9\u5f62\u6001\u5224\uff09\u3002
    publish_page\uff1a\u5355\u4e2a\u53d1\u5e03\u9875 URL\uff0c\u6216\u591a\u4e2a\uff08\u5217\u8868 / \u9017\u53f7\u00b7\u5206\u53f7\u5206\u9694\u4e32\uff09\u2014\u2014**\u5e76\u884c\u6293\u3001\u6309\u5e8f\u5408\u5e76**\u3002
    probe_path\uff1a\u6df1\u94fe\u63a2\u6d4b\u8def\u5f84\uff08v2.8\uff09\u2014\u2014\u5019\u9009\u57df\u540d**\u6839\u8def\u5f84\u662f\u58f3\u9875/\u9009\u62e9\u9875\u3001\u53ea\u6709\u6df1\u94fe\u624d\u662f\u771f\u5185\u5bb9**
      \u65f6\u4f20\u5b83\uff08\u5c04\u7a9d `/vodtype/55-1.html`\u3001\u6781\u4e50\u7981\u533a `/vodtype/45-1/`\uff09\u3002\u547d\u4e2d\u540e\u8fd4\u56de**\u7ad9\u70b9\u6839**\u3002
    \u987a\u5e8f\uff1a\u53d1\u5e03\u9875\u57fa\u57df\u5019\u9009\uff08\u6700\u65b0\u9c9c\uff09> ext/\u5185\u7f6e\u5019\u9009 > \u53d1\u5e03\u9875\u9759\u6001\u94fe\u63a5\u3002
    \u5168\u8fc7\u7a0b\u5199\u5165 last_trace()\uff0c\u4f9b\u6e90\u5185\u300c\u8bca\u65ad\u300d\u680f\u76ee\u5c55\u793a\u3002"""
    del _gen_TRACE[:]
    candidate_hosts = candidate_hosts or []
    pages = _gen_split_publish_pages(publish_page)      # \u591a\u53d1\u5e03\u9875\uff082026-09-13\uff09
    _gen_tr('== \u9009\u7ad9\u5f00\u59cb (publish=%s | site_key=%s%s) =='
        % ('\u3001'.join([_gen_host_of(p) for p in pages]) or '(\u65e0)', site_key or '(\u672a\u4f20)',
           (' | probe=' + probe_path) if probe_path else ''))
    if validate is None and site_key:
        validate = _gen_auto_validate(site_key)
    key = (tuple(pages), tuple(candidate_hosts), site_key or '', probe_path or '')
    if use_cache:
        hit = _gen_CACHE.get(key)
        if hit and time.time() < hit[1]:
            _gen_tr('  \u547d\u4e2d\u9009\u7ad9\u7f13\u5b58 \u2192 %s\uff08%d \u79d2\u540e\u8fc7\u671f\uff09'
                % (hit[0], int(hit[1] - time.time())))
            return hit[0]

    # 1) \u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe\uff08\u57fa\u57df\u81ea\u52a8\u751f\u6210\u5019\u9009 + \u9759\u6001\u955c\u50cf\u94fe\u63a5\uff09
    #    \u591a\u4e2a\u53d1\u5e03\u9875\uff08\u7f51\u5740\u578b + GitHub \u578b\u7b49\uff09**\u5e76\u884c**\u6293\u53d6\u3001\u7ed3\u679c\u6309\u586b\u5199\u987a\u5e8f\u5408\u5e76\uff1a
    #    \u4e00\u9875\u6302\u4e86\u4e0d\u5f71\u54cd\u5176\u4ed6\u9875\uff0cN \u9875\u8017\u65f6\u4ece N\u00d7 \u964d\u4e3a \u2248max\uff08v2.4\uff0c2026-09-13\uff09\u3002
    pub_domains, bases, _pg_traces = _gen_extract_pages(pages, headers, proxies, timeout)
    for _lines in _pg_traces:                 # trace \u6309 pages \u539f\u5e8f\u5199\u56de\uff08\u5e76\u884c\u4e0b\u4e0d\u53ef\u4e71\u5e8f\uff09
        for _l in _lines:
            _gen_tr(_l)
    words = random.sample(_gen_WILD_WORDS, min(4, len(_gen_WILD_WORDS)))
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
    tier1 = [u for u in _gen_dedupe(list(pages) + wild_candidates + list(candidate_hosts))
             if not _gen_is_junk(u)]
    _t1 = set(tier1)
    tier2 = [u for u in _gen_dedupe(pub_domains) if u not in _t1 and not _gen_is_junk(u)]

    if not tier1 and not tier2:
        _gen_tr('  \u65e0\u4efb\u4f55\u5019\u9009\u53ef\u6d4b\uff08\u53d1\u5e03\u9875\u62bd\u94fe\u4e3a\u7a7a\u4e14\u65e0\u5185\u7f6e\u5019\u9009\uff09\u2192 \u8fd4\u56de\u7a7a')
        return ''
    _gen_tr('  \u5019\u9009: \u7b2c\u4e00\u5c42 %d \u4e2a / \u7b2c\u4e8c\u5c42 %d \u4e2a\uff08\u7b2c\u4e00\u5c42\u9996\u9009=%s\uff09'
        % (len(tier1), len(tier2),
           '\u3001'.join([_gen_host_of(p) for p in pages]) or '-'))

    # 3) \u5206\u6ce2\u5b9e\u6d4b\uff08use_cache=False=\u5f3a\u5236\u5237\u65b0\uff0c\u4f46\u6210\u529f\u7ed3\u679c\u4ecd\u5199\u7f13\u5b58\u4f9b\u540e\u7eed init \u79d2\u5f00\uff09
    host = _gen_probe_all(tier1, headers, proxies, timeout, validate, '\u4e00\u7ea7', probe_path)
    if not host and tier2:
        host = _gen_probe_all(tier2, headers, proxies, timeout, validate, '\u4e8c\u7ea7', probe_path)
    if host:
        _gen_CACHE[key] = (host, time.time() + _gen_CACHE_TTL)
        _gen_tr('  \u2605 \u9009\u4e2d %s\uff08\u7f13\u5b58 30 \u5206\u949f\uff09' % host)
    else:
        _gen_tr('  \u2605 \u5168\u90e8\u5931\u8d25 \u2192 \u8fd4\u56de\u7a7a\uff08\u8c03\u7528\u65b9\u5e94\u7acb\u5373\u5931\u8d25\uff0c\u4e0d\u518d\u9759\u9ed8\u7a7a\u8f6c\uff09')
    return host

# <<< INLINE-GEN-END <<<

# >>> INLINE-GEN-BIND-START >>>
# \u5185\u8054\u63a5\u9a73\uff08\u81ea\u52a8\u751f\u6210\uff09\uff1a\u8ba9\u672c\u6e90\u5728\u300cApp \u5f62\u6001\uff08\u65e0 hostresolver.py\uff09\u300d\u4e0b\u4e5f\u62ff\u5230\u5168\u91cf\u7b97\u6cd5\u3002
# \u2460 \u9876\u66ff\u6a21\u5757\u7ea7\u5168\u5c40\uff1a\u6e90\u9876\u90e8 except \u5206\u652f\u628a\u540d\u5b57\u8bbe\u6210\u4e86 None\uff0c\u65b9\u6cd5\u5185 `if resolve_host:`
#    \u8bfb\u7684\u5c31\u662f\u8fd9\u4e9b\u5168\u5c40\u3002\u2461 \u6ce8\u518c\u5047\u6a21\u5757\uff1a\u51fd\u6570\u5185 `from hostresolver import ext_of` \u7531\u6b64\u547d\u4e2d\u3002
# \u2462 \u771f\u6a21\u5757\u5df2\u5728\uff08PC \u7aef / \u672c\u5730\u5305\u5f62\u6001\uff09\u2192 \u8df3\u8fc7\uff0c\u884c\u4e3a\u96f6\u53d8\u5316\u3002
try:
    import sys as _gen_sys
    import types as _gen_types
    if 'hostresolver' not in _gen_sys.modules:
        _gen_mod = _gen_types.ModuleType('hostresolver')
        _gen_mod.resolve_host = _gen_resolve_host
        _gen_mod.probe_first = _gen_probe_first
        _gen_mod.parse_ext = _gen_parse_ext
        _gen_mod.ext_of = _gen_ext_of
        _gen_mod.last_trace = _gen_last_trace
        _gen_mod.clear_cache = _gen_clear_cache
        _gen_sys.modules['hostresolver'] = _gen_mod
    for _gen_n in ('resolve_host', 'probe_first', 'parse_ext', 'ext_of', 'last_trace', 'clear_cache',):
        if globals().get(_gen_n) is None:
            globals()[_gen_n] = globals().get('_gen_' + _gen_n.lstrip('_'))
except Exception:
    pass
# <<< INLINE-GEN-BIND-END <<<
