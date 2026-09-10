# -*- coding: utf-8 -*-
"""
hostresolver.py \u2014\u2014 \u901a\u7528\u52a8\u6001\u57df\u540d\u89e3\u6790 v2\uff08\u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe + \u5019\u9009\u955c\u50cf\u5e76\u884c\u5b9e\u6d4b + \u6210\u529f\u7f13\u5b58\uff09

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

\u8c03\u7528\u65b9\uff08\u5404 py \u6e90\uff09\u53ea\u9700\u58f0\u660e\uff1a
  PUBLISH_PAGE = 'https://xxx.xxx/'          # \u7a33\u5b9a\u53d1\u5e03\u9875\uff08\u53ef\u7a7a\uff09
  CANDIDATE_HOSTS = ['https://a/', ...]      # \u5df2\u77e5\u955c\u50cf\uff0c\u6309\u5b58\u6d3b\u6392\u5e8f
  self.host = resolve_host(PUBLISH_PAGE, CANDIDATE_HOSTS, headers=..., proxies=...)
  # \u8fd4\u56de\u53ef\u80fd\u662f ''\uff0c\u8c03\u7528\u65b9\u63a5\u53e3\u5c42 try/except \u515c\u4f4f\u5373\u53ef

ext \u673a\u5236\uff08\u5f71\u89c6.json \u7ad9\u70b9\u6761\u76ee ext \u5b57\u6bb5\uff0cgitee \u7f51\u9875\u53ef\u76f4\u63a5\u6539\uff09\uff1a
  \u6587\u672c: publish@https://...;hosts@https://a,https://b;host@https://...
  JSON: {\"publish\":\"...\",\"hosts\":[\"...\"],\"host\":\"...\",\"proxies\":{...}}
  - host@   \u9501\u5b9a\u4e3b\u9875\uff08\u6700\u9ad8\u4f18\u5148\u7ea7\uff0c\u8df3\u8fc7\u4e00\u5207\u63a2\u6d4b\uff0c\u7ad9\u70b9\u7ed3\u6784\u5927\u6539\u65f6\u7528\uff09
  - publish@ \u53d1\u5e03\u9875\u5730\u5740\uff08\u53d1\u5e03\u9875\u6362\u4e86\u6539\u8fd9\u91cc\uff09
  - hosts@  \u65b0\u589e\u5019\u9009\u955c\u50cf\uff08\u5b9e\u6d4b\u987a\u5e8f\u4ec5\u6392\u5728\u53d1\u5e03\u9875\u6cdb\u89e3\u6790\u5019\u9009\u4e4b\u540e\uff09
"""
import re
import time
import random
import base64

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


def clear_cache():
    """\u6e05\u7a7a\u9009\u7ad9\u7f13\u5b58\uff08\u8c03\u8bd5\u7528\uff1b\u8c03\u7528\u65b9\u4e00\u822c\u4e0d\u9700\u8981\uff09"""
    _CACHE.clear()


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
        elif k in ('publish', 'host'):
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
                    out[k] = str(extend[k]).strip()
            if extend.get('hosts'):
                hs = extend['hosts'] if isinstance(extend['hosts'], list) else [extend['hosts']]
                out['hosts'] = [str(h).strip() for h in hs if str(h).strip()]
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
# \u53d1\u5e03\u9875\u91cc\u5fc5\u7136\u6df7\u5165\u7684\u7b2c\u4e09\u65b9\u5927\u5e73\u53f0/\u7edf\u8ba1/\u5e7f\u544a\u57df\u2014\u2014\u63a2\u6d4b\u5b83\u4eec\u4f1a\u628a\u5927\u9875\u9762\u8bef\u5224\u6210"\u7ad9\u70b9\u53ef\u7528"
_JUNK_HOST_PAT = re.compile(
    r'(googletagmanager|google-analytics|googleads|gstatic|google\.|gitlab\.|github\.|'
    r'youtube\.|ytimg\.|twitter\.|x\.com|t\.me|telegram\.|addtoany\.|yandex\.|'
    r'browsehappy|schema\.org|w3\.org|qq\.com|apple\.com|bing\.com|baidu\.com|'
    r'magsrv\.|adsrv|ad-provider|chnsrv|stripchat|jsdelivr|unpkg|npmjs|shields\.io|'
    r'699pic|meituan|fontawesome|jquery|bootstrap)', re.I)


def _expand_b64_shells(text):
    """\u5c55\u5f00\u53d1\u5e03\u9875\u91cc\u7684 Base64 \u58f3\uff0c\u8fd4\u56de [\u539f\u6587, \u89e3\u7801\u98751, \u89e3\u7801\u98752...]"""
    texts = [text]
    for m in _B64_SHELL_PAT.finditer(text):
        try:
            texts.append(base64.b64decode(m.group(1)).decode('utf-8', 'ignore'))
        except Exception:
            continue
    return texts


def extract_publish_domains(publish_page, headers, proxies, timeout):
    """\u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe\u3002\u8fd4\u56de (\u9759\u6001\u955c\u50cf\u94fe\u63a5\u5217\u8868, \u6cdb\u89e3\u6790\u57fa\u57df\u5217\u8868)\u3002
    JS \u6e32\u67d3\u4f46\u65e0 b64 \u58f3\u7684\u9875\u9762\u9759\u6001\u94fe\u63a5\u4ecd\u53ef\u80fd\u4e3a\u7a7a\u2014\u2014\u6cdb\u89e3\u6790\u57fa\u57df\u8bc6\u522b\u662f\u4e3b\u901a\u9053\u3002"""
    if requests is None or not publish_page:
        return [], []
    try:
        r = requests.get(publish_page, headers=headers, proxies=proxies,
                         timeout=timeout, verify=False, allow_redirects=True)
        if r.status_code != 200:
            return [], []
    except Exception:
        return [], []
    texts = _expand_b64_shells(r.text or '')
    static, wilds = [], set()
    for t in texts:
        for l in re.findall(r'href=["\'](https?://[^"\']+)["\']', t, re.I):
            m = re.match(r'https?://([a-z0-9.-]+\.[a-z]{2,})', l, re.I)
            if m and not _JUNK_HOST_PAT.search(m.group(1)):
                static.append('https://' + m.group(1))
        for m in _WILD_PAT.finditer(t):
            wilds.add(m.group(1))
    return list(dict.fromkeys(static)), list(wilds)


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


# ---------------------------------------------------------------- \u63a2\u6d4b
def _probe(url, headers, proxies, timeout, depth=0, validate=None):
    """\u6d4b\u8bd5\u5355\u57df\u540d\uff1a\u8df3\u8f6c\u58f3\u5219\u8ddf\u968f <a href>\uff08\u6700\u591a2\u5c42\uff09\uff1b\u771f\u5185\u5bb9\u8fd4\u56de\u6700\u7ec8 host\uff1b\u5931\u8d25 None\u3002
    validate(final_host, text) -> bool\uff1a\u5185\u5bb9\u8eab\u4efd\u6821\u9a8c\uff08\u9632\u5e7f\u544a\u95e8\u7ad9/\u7b2c\u4e09\u65b9\u9875\u5192\u5145\uff09\u3002"""
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
        if len(t) > 5000 or ('article' in t and 'category' in t):
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


def _probe_all(urls, headers, proxies, timeout, validate=None):
    """\u5e76\u884c\u63a2\u6d4b\uff0c\u4efb\u4e00\u5019\u9009\u6210\u529f\u5373\u523b\u8fd4\u56de\uff08\u53d6\u6d88\u5176\u4f59\u4efb\u52a1\uff09\uff1b\u5168\u8d25\u8fd4\u56de ''\u3002
    \u603b\u8017\u65f6 \u2248 \u5355\u6b21\u8d85\u65f6\uff0c\u4e0d\u518d\u968f\u5019\u9009\u6570\u91cf\u53e0\u52a0\u3002"""
    if not urls:
        return ''
    if not (ThreadPoolExecutor and as_completed) or len(urls) == 1:
        for u in urls:
            h = _probe(u, headers, proxies, timeout, 0, validate)
            if h:
                return h
        return ''
    ex = ThreadPoolExecutor(max_workers=min(12, len(urls)))
    try:
        futs = [ex.submit(_probe, u, headers, proxies, timeout, 0, validate) for u in urls]
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception:
                continue
            if r:
                for x in futs:
                    x.cancel()
                return r
        return ''
    finally:
        ex.shutdown(wait=False)


# ---------------------------------------------------------------- \u4e3b\u5165\u53e3
def resolve_host(publish_page=None, candidate_hosts=None, headers=None,
                 proxies=None, timeout=8, use_cache=True, validate=None):
    """\u8fd4\u56de\u5f53\u524d\u53ef\u7528 host\uff08\u53bb\u5c3e\u659c\u6760\uff09\u3002\u5168\u90e8\u5931\u8d25\u8fd4\u56de ''\uff08\u8c03\u7528\u65b9\u63a5\u53e3\u5c42\u81ea\u884c\u515c\u7a7a\uff09\u3002
    validate(final_host, text)->bool\uff1a\u7ad9\u70b9\u8eab\u4efd\u6821\u9a8c\u56de\u8c03\uff0c\u9632\u53d1\u5e03\u9875\u6df7\u5165\u7684\u5e7f\u544a\u95e8\u7ad9
    \uff08\u5982 18se \u5bfc\u822a\uff09\u88ab\u5f53\u6210\u771f\u7ad9\u7f13\u5b58\u3002\u987a\u5e8f\uff1a\u53d1\u5e03\u9875\u6cdb\u89e3\u6790\u5019\u9009(\u6700\u65b0\u9c9c) > ext/\u5185\u7f6e\u5019\u9009
    > \u53d1\u5e03\u9875\u9759\u6001\u94fe\u63a5\u3002"""
    candidate_hosts = candidate_hosts or []
    key = (publish_page or '', tuple(candidate_hosts))
    if use_cache:
        hit = _CACHE.get(key)
        if hit and time.time() < hit[1]:
            return hit[0]

    # 1) \u53d1\u5e03\u9875\u6df1\u5ea6\u62bd\u94fe\uff08\u6cdb\u89e3\u6790\u57fa\u57df\u81ea\u52a8\u751f\u6210\u5019\u9009 + \u9759\u6001\u955c\u50cf\u94fe\u63a5\uff09
    pub_domains, wild_bases = [], []
    if publish_page:
        try:
            pub_domains, wild_bases = extract_publish_domains(
                publish_page, headers, proxies, timeout)
        except Exception:
            pub_domains, wild_bases = [], []
    words = random.sample(_WILD_WORDS, min(4, len(_WILD_WORDS)))
    wild_candidates = ['https://%s.%s' % (w, b) for b in wild_bases for w in words]

    # 2) \u5206\u5c42\u5019\u9009\uff08\u5404\u5c42\u4fdd\u5e8f\u53bb\u91cd\uff09\uff1a
    #    \u7b2c\u4e00\u5c42 = \u6cdb\u89e3\u6790\u5019\u9009 + ext/\u5185\u7f6e\u5019\u9009\uff08\u65b0\u9c9c\u4e14\u53ef\u4fe1\uff0c\u7edd\u5927\u591a\u6570\u573a\u666f\u6b64\u5c42\u5373\u547d\u4e2d\uff09
    #    \u7b2c\u4e8c\u5c42 = \u53d1\u5e03\u9875\u9759\u6001\u94fe\u63a5\uff08\u4ec5\u7b2c\u4e00\u5c42\u5168\u8d25\u65f6\u624d\u6d4b\uff0c\u9632\u7b2c\u4e09\u65b9\u5927\u9875\u9762\u8bef\u5224\u6210\u7ad9\u70b9\uff09
    tier1 = _dedupe(wild_candidates + list(candidate_hosts))
    tier2 = [u for u in _dedupe(pub_domains) if u not in set(tier1)]

    if not tier1 and not tier2:
        return ''

    # 3) \u5206\u6ce2\u5b9e\u6d4b\uff08use_cache=False=\u5f3a\u5236\u5237\u65b0\uff0c\u4f46\u6210\u529f\u7ed3\u679c\u4ecd\u5199\u7f13\u5b58\u4f9b\u540e\u7eed init \u79d2\u5f00\uff09
    host = _probe_all(tier1, headers, proxies, timeout, validate)
    if not host and tier2:
        host = _probe_all(tier2, headers, proxies, timeout, validate)
    if host:
        _CACHE[key] = (host, time.time() + _CACHE_TTL)
    return host
