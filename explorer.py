# -*- coding: utf-8 -*-
"""
explorer.py \u2014\u2014 \u591a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22 v1\uff08\u6e90\u7ad9\u57df\u540d\u6c60\u5168\u6302\u65f6\u7684\u515c\u5e95\u53d1\u73b0\u6e20\u9053\uff09

\u80cc\u666f\uff1a\u7ad9\u65b9\u57df\u540d\u8f6e\u6362\u5feb\uff0c\u5185\u7f6e\u5019\u9009\u6c60 + \u53d1\u5e03\u9875(hostresolver v2)\u4e4b\u5916\uff0c
\u5bfc\u822a\u7ad9\uff08\u7eff\u8272\u5c0f\u5bfc\u822a\u7b49\uff09\u957f\u671f\u5b58\u6d3b\u4e14\u5b9e\u65f6\u6536\u5f55\u5404\u5bb6\u6700\u65b0\u57df\u540d\u3002\u628a\u5bfc\u822a\u7ad9\u672c\u8eab
\u505a\u6210\u300c\u53d1\u73b0\u6e20\u9053\u6c60\u300d\uff1a
  \u79cd\u5b50\u5bfc\u822a(\u542b\u5176\u53d1\u5e03\u9875\u955c\u50cf) -> \u6293\u5168\u91cf\u5916\u94fe\u5f97 {\u57df\u540d: \u7ad9\u540d} \u6620\u5c04
  -> \u6309\u6e90\u522b\u540d\u8fc7\u6ee4\u5019\u9009 -> \u8c03\u7528\u65b9\u534f\u8bae\u7ea7\u9a8c\u8bc1 -> \u6d3b\u57df\u63d2\u6c60

\u81ea\u6536\u96c6\uff1a\u5bfc\u822a\u9875\u4e92\u6302\u7684\u5176\u5b83\u5bfc\u822a\u7ad9\uff08\u7ad9\u540d\u542b\"\u5bfc\u822a\"\uff09\u52a8\u6001\u6269\u5145\u79cd\u5b50\u6c60\u5e76\u6301\u4e45\u5316\u3002

\u5bfc\u822a\u7ad9\u4e00\u6761 = \u4e00\u4e2a\u7ad9\u70b9\uff082026-09-10 \u5b9a\uff0c\u4e0e\u6e90\u7ad9\u6a21\u578b\u5bf9\u9f50\uff09\uff1a
  {url:\u4e3b\u57df, urls:[\u5907\u7528\u57df...], note:\u663e\u793a\u540d, pub:\u53d1\u5e03\u9875}
  \u7eff\u8272\u5c0f\u5bfc\u822a\u7684\u4e3b\u57df\u4e0e\u955c\u50cf\u57df\u5c5e\u4e8e**\u540c\u4e00\u6761**\uff0c\u4e0d\u518d\u62c6\u6210\u4e24\u4e2a\u79cd\u5b50\u3002
  \u79cd\u5b50\u6c60\u5c55\u5f00\u65f6\u4e3b\u57df\u4e0e\u5907\u7528\u57df\u90fd\u4f1a\u8fdb\u6c60\uff08\u591a\u4e00\u4e2a\u53ef\u6293\u5165\u53e3\uff0c\u4e92\u4e3a\u515c\u5e95\uff09\u3002

\u5bfc\u822a\u7ad9\u53d1\u5e03\u9875\uff1a\u5bfc\u822a\u7ad9\u548c\u6e90\u7ad9\u4e00\u6837\u4e5f\u6709\u53d1\u5e03\u9875\uff08\u5982\u7eff\u8272\u5c0f\u5bfc\u822a\u7684 1800ga.com
\u300c\u5730\u5740\u53d1\u5e03\u300d\u9875\uff0c\u5217 1/2/3 \u4e09\u4e2a\u5f53\u524d\u5165\u53e3\uff09\u3002\u79cd\u5b50\u6c60\u5168\u6302\u65f6\u6293\u5b83\u53d6\u56de\u5f53\u524d\u751f\u6548\u7684
\u57df\u540d\u5e76\u5165\u6c60\u3002\u53d1\u5e03\u9875\u5df2\u5185\u8054\u8fdb user_navs \u7684 pub \u5b57\u6bb5\uff1bnav_pubs \u4f5c\u4e3a\u65e7\u683c\u5f0f
\u517c\u5bb9\u8bfb\u53d6\uff08\u8001\u914d\u7f6e/\u8001\u8bbe\u5907\u7f13\u5b58\u91cc\u4ecd\u6709\uff09\u3002\u6ce8\u610f\u533a\u5206\uff1a**\u6e90\u7ad9\u81ea\u5df1\u7684**\u53d1\u5e03\u9875/
\u5907\u7528\u57df\u5f52\u8be5\u6e90 ext \u7684 publish@/hosts@\uff08\u7531\u6e90\u81ea\u5df1\u8bfb\uff09\uff0c\u4e0d\u5728\u672c\u6a21\u5757\u3002

\u516c\u5f00\u63a5\u53e3\uff1a
  nav_site_map(force=False)          -> {host: name}\uff08\u5408\u5e76\u591a\u5bfc\u822a\u7ad9\uff0c\u7f13\u5b586h\uff09
  deep_site_map(extra=6)             -> (map, \u65b0\u6293\u6e90) \u6df1\u5ea6\u6a21\u5f0f\uff0c\u591a\u6293\u81ea\u6536\u96c6\u5bfc\u822a\u7ad9
  seeds() / nav_pool()               -> \u79cd\u5b50\u6c60\uff08\u7528\u6237\u81ea\u914d\u00b7\u542b\u53ef\u7f16\u8f91\u9884\u7f6e + \u81ea\u6536\u96c6\uff1b\u5168\u7a7a\u65f6\u51fa\u5382\u515c\u5e95\uff09/ \u5f53\u524d\u6c60
  user_navs()                        -> \u7528\u6237\u81ea\u914d\u5bfc\u822a\u7ad9 [{url,urls,note,pub}]\uff08explorer_admin \u7ef4\u62a4\uff09
  nav_urls(x)                        -> \u4e00\u6761\u5bfc\u822a\u7ad9\u7684\u5168\u90e8\u57df [\u4e3b\u57df, \u5907\u7528\u57df...]
  nav_pages()                        -> [{nav,name,pub}] \u53d1\u5e03\u9875\uff08\u5185\u8054 pub + \u65e7 nav_pubs\uff0c\u515c\u5e95\u53d6\u65b0\u57df\uff09
  discover(aliases, validate, ...)   -> [\u6d3b\u57dfURL]   validate(host)->bool
  remember(alias, hosts)             -> \u63a2\u7d22\u6210\u679c\u6301\u4e45\u5316\uff08\u4e0b\u6b21 init \u9884\u8f7d\uff09
  known(alias)                       -> \u5386\u53f2\u63a2\u7d22\u6210\u679c\uff08\u53ef\u80fd\u8fc7\u671f\uff0c\u8c03\u7528\u65b9\u81ea\u4f1a\u5b9e\u6d4b\uff09

\u63a5\u5165\u793a\u4f8b\uff08xbpq/\u9ec4\u8c46.py\uff0cAPI \u578b\uff09\uff1a
  try:
      from explorer import discover, remember, known
  except Exception:
      discover = None
  # init():      self.hosts += [h for h in known('huangdou') if h not in self.hosts]
  # _api() \u6c60\u5168\u6302: discover(['huangdou','\u9ec4\u8c46'], validate=self._check_host) -> \u63d2\u6c60\u91cd\u8bd5

\u63a5\u5165\u793a\u4f8b\uff08py/ \u4e0b web \u578b\u6e90\uff0c\u7edf\u4e00\u8d70 explore_hosts\uff09\uff1a
  try:
      from explorer import explore_hosts
  except Exception:
      explore_hosts = None
  # get_working_host() \u7ec8\u6781\u515c\u5e95\uff08\u5185\u7f6e\u6c60+\u53d1\u5e03\u9875\u5168\u5931\u8d25\u540e\uff09\uff1a
  #   hs = explore_hosts(['douyin','\u6296\u9634'], probe=_probe)   # probe \u6293\u9996\u9875\u9a8c\u7ad9\u540d
  #   if hs: return hs[0]
  # explore_hosts \u5185\u7f6e\uff1aknown \u5386\u53f2\u5feb\u9a8c \u2192 \u539f\u59cb\u5019\u9009\u5e76\u884c\u300c\u951a\u70b9\u58f3\u8ddf\u968f\u2192Base64\u95e8\u6237
  # \u89e3\u7801\u2192\u6cdb\u89e3\u6790\u57fa\u57df\u751f\u6210\u300d\u4e24\u7ea7\u7a7f\u900f \u2192 \u5165\u53e3\u95e8\u6237\u590d\u6838\uff08\u62d2 SEO \u95e8\u7ad9\uff09\u2192 remember
"""
import base64
import json
import os
import re
import time

try:
    import requests
except Exception:
    requests = None

try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
except Exception:
    ThreadPoolExecutor = None
    as_completed = None

_UA = {'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'}

# \u51fa\u5382\u515c\u5e95\u79cd\u5b50\uff082026-09-10 \u964d\u7ea7\u4e3a\u300c\u53ef\u7f16\u8f91\u9884\u7f6e\u300d\u65b9\u6848\uff09\uff1a
# \u5e38\u89c4\u79cd\u5b50\u5df2\u642c\u8fdb explorer_seeds.json \u7684 user_navs\u2014\u2014\u7ba1\u7406\u53f0\u300c\u5bfc\u822a\u7ad9\u7ba1\u7406\u300d\u53ef\u589e\u5220/\u6539\uff0c
# \u968f\u63a8\u9001\u4e0b\u53d1\u8bbe\u5907\u3002\u8fd9\u91cc\u7684 2 \u6761**\u53ea\u5728\u914d\u7f6e\u91cc\u4e00\u6761\u79cd\u5b50\u90fd\u6ca1\u6709\u65f6**\u542f\u7528
# \uff08\u9632\u300c\u914d\u7f6e\u8bfb\u4e0d\u5230 + \u65b0\u8bbe\u5907\u9996\u6b21\u542f\u52a8\u300d\u5bfc\u81f4\u6c60\u7a7a\u3001\u63a2\u7d22\u5b8c\u5168\u8d77\u4e0d\u6765\uff09\u3002
# \u6ce8\uff1a\u7eff\u8272\u5c0f\u5bfc\u822a\u4e3b\u57df+\u955c\u50cf\u57df\u5728\u914d\u7f6e\u91cc\u662f**\u540c\u4e00\u6761**\uff08urls \u5907\u7528\u57df\uff09\uff1b
#     1800ga.com\uff08\u5176\u53d1\u5e03\u9875\uff09\u4e5f\u4e0d\u5728\u6b64\u5217\uff0c\u5f52 nav_pages()/pub_hosts() \u7ba1\u3002
_FALLBACK_SEEDS = [
    'https://xn--m-3h9b.lvse71.date/%E9%A3%8E%E6%99%AF/',
    'https://green61.net/',
]
_NAV_HINT = '\u5bfc\u822a'
_NAV_POOL_MAX = 24      # \u81ea\u6536\u96c6\u5bfc\u822a\u7ad9\u4e0a\u9650
_NAV_FETCH_MAX = 4      # \u6bcf\u6b21\u6784\u5efa\u6620\u5c04\u6700\u591a\u5b9e\u6293\u7684\u5bfc\u822a\u7ad9\u6570\uff08\u63a7\u5236\u8017\u65f6\uff09
_TTL = 7 * 24 * 3600         # \u7ad9\u70b9\u6620\u5c04\u7f13\u5b58

# \u7528\u6237\u81ea\u914d\u5bfc\u822a\u7ad9\uff08explorer_admin.py \u7ba1\u7406\u53f0\u7ef4\u62a4\uff0cpush \u5230 gitee \u540e\u8bbe\u5907\u81ea\u52a8\u751f\u6548\uff09
_USER_CFG_URL = 'https://gitee.com/mallox/source/raw/master/xbpq/explorer_seeds.json'

# \u5fc5\u7136\u6df7\u5165\u7684\u5927\u5e73\u53f0/\u7edf\u8ba1/\u9759\u6001\u8d44\u6e90\u57df\uff0c\u4e0d\u5f53\u5019\u9009
_JUNK = re.compile(
    r'(googletagmanager|google-analytics|gstatic|google\.|gmail\.|cloudfront|gitlab\.|github\.|'
    r'youtube\.|twitter\.|x\.com|t\.me|telegram\.|schema\.org|w3\.org|'
    r'qq\.com|baidu\.com|bing\.com|jsdelivr|unpkg|npmjs|jquery|bootstrap|'
    r'fontawesome|statcounter|cloudflare|email-protection|favicon|apple\.com)', re.I)

_A_RE = re.compile(r'<a\s[^>]*href="(https?://[^"\s]+)"[^>]*>(.*?)</a>', re.S | re.I)
_HOST_RE = re.compile(r'^https?://([a-z0-9][a-z0-9.\-]*\.[a-z]{2,})', re.I)
# \u951a\u70b9\u8df3\u8f6c\u58f3\uff1a~300B\uff0c<a href=\u76ee\u6807>\u52a0\u8f7d\u4e2d...</a><script>\u2026location.replace\u2026\uff09
_RE_ANCHOR = re.compile(r'<a[^>]{0,120}?href="(https?://[^"\s]+)"', re.I)
# Base64 \u5165\u53e3\u58f3\uff1a\u89e3\u7801\u51fa\u7684\u5b98\u65b9\u95e8\u6237\u9875\u91cc\u5217\u7684\u57df\u540d\uff08\u5165\u53e3\u57df/\u6cdb\u89e3\u6790\u57fa\u57df\uff09
_RE_DOM = re.compile(r'[a-z0-9][a-z0-9\-]{2,25}\.(?:cc|top|com|net|xyz|vip|icu|cyou|club|fun|me|tv|info|ltd|buzz)', re.I)
# \u6cdb\u89e3\u6790\u63a2\u6d4b\u8bcd\uff08\u7ad9\u65b9\u666e\u904d\u4efb\u610f\u8bcd\u5b50\u57df\u5168\u7ad9\uff0c\u5982 {word}.bqmnxlid.cc\uff09
_WILD_WORDS = ['apple', 'berry', 'kiwi', 'lemon', 'mango', 'melon', 'pear', 'peach']
# \u5165\u53e3\u95e8\u6237\u7279\u5f81\uff08\u300cXX-\u5b98\u65b9\u5165\u53e3/\u66f4\u65b0\u5165\u53e3\u300dSEO \u95e8\u7ad9\u4e5f\u5e26\u7ad9\u540d\uff0c\u5355\u9760\u8eab\u4efd\u4e32\u4f1a\u8bef\u6536\uff09
_PORTAL_KW = re.compile('\u66f4\u65b0\u5165\u53e3|\u5b98\u65b9\u5165\u53e3|\u5730\u5740\u53d1\u5e03|\u56de\u5bb6\u7684\u8def|\u6c38\u4e45\u5730\u5740|\u7ebf\u8def[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d]')

_FP = None
_MEM = {'map': None, 'ts': 0, 'navs': None, 'pubts': 0}


# ---------------------------------------------------------------- \u6301\u4e45\u5316\uff08best-effort\uff09
def _file():
    global _FP
    if _FP:
        return _FP
    cands = []
    try:
        import tempfile
        cands.append(tempfile.gettempdir())
    except Exception:
        pass
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        pass
    for d in cands:
        if d and os.path.isdir(d):
            p = os.path.join(d, 'explorer_cache.json')
            try:
                open(p, 'a', encoding='utf-8').close()
                _FP = p
                return p
            except Exception:
                continue
    return None


def _load():
    p = _file()
    if not p:
        return {}
    try:
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save(d):
    p = _file()
    if not p:
        return
    try:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False)
    except Exception:
        pass


# ---------------------------------------------------------------- \u6293\u53d6\u4e0e\u89e3\u6790
def _cfemail(text):
    """Cloudflare email-protection \u6df7\u6dc6\u8fd8\u539f\uff08\u5bfc\u822a\u9875\u516c\u544a\u90ae\u7bb1/\u8054\u7cfb\u65b9\u5f0f\u7528\uff09"""
    def rep(m):
        try:
            raw = bytes.fromhex(m.group(1))
            return ''.join(chr(b ^ raw[0]) for b in raw[1:])
        except Exception:
            return m.group(0)
    return re.sub(r'data-cfemail="([0-9a-fA-F]+)"', rep, text)


def _get(url, timeout=10):
    if requests is None or not url:
        return ''
    try:
        r = requests.get(url, headers=_UA, timeout=timeout, verify=False, allow_redirects=True)
        if r.status_code != 200:
            return ''
        head = r.content[:600].decode('ascii', 'ignore').lower()
        r.encoding = 'gb18030' if ('gb2312' in head or 'gbk' in head) else 'utf-8'
        return r.text or ''
    except Exception:
        return ''


def _entries(html):
    """\u9875\u9762\u5168\u90e8\u5916\u94fe -> {host: \u7ad9\u540d}"""
    out = {}
    for u, inner in _A_RE.findall(_cfemail(html)):
        m = _HOST_RE.match(u)
        if not m or _JUNK.search(m.group(1)):
            continue
        nm = re.search(r'class="name">([^<]+)<', inner) or re.search(r'alt="([^"]+)"', inner)
        name = nm.group(1).strip() if nm else re.sub(r'<[^>]+>', ' ', inner)
        name = re.sub(r'\s+', ' ', name).strip()[:30]
        out.setdefault(m.group(1).lower(), name)
    return out


def _read_nav(url, depth=0):
    """\u8bfb\u4e00\u4e2a\u5bfc\u822a\u7ad9\uff1a\u8fd4\u56de (\u662f\u5426\u6709\u6548\u5bfc\u822a, {host: name}, \u5176\u5b83\u5bfc\u822a\u7ad9\u5217\u8868)\u3002
    \u94fe\u63a5\u6781\u5c11\u5219\u89c6\u4e3a\u8df3\u8f6c\u58f3/\u5730\u5740\u53d1\u5e03\u9875\uff0c\u8ddf\u968f\u7b2c\u4e00\u4e2a\u5916\u94fe\uff08\u5982 1800ga.com -> \u6700\u65b0\u5bfc\u822a\u57df\uff09\u3002"""
    html = _get(url, 10)
    if not html:
        return False, {}, []
    ent = _entries(html)
    if len(ent) < 5 and depth < 2:
        m = re.search(r'href="(https?://[^"\s]+)"', html, re.I)
        if m:
            ok2, ent2, nv2 = _read_nav(m.group(1), depth + 1)
            if ok2:
                return True, ent2, nv2
    if len(ent) < 10:
        return False, {}, []
    navs = []
    for host, name in ent.items():
        if _NAV_HINT in name and len(navs) < _NAV_POOL_MAX:
            navs.append('https://' + host + '/')
    return True, ent, navs


# ---------------------------------------------------------------- \u4e3b\u63a5\u53e3
def nav_site_map(force=False):
    """\u5408\u5e76\u591a\u5bfc\u822a\u7ad9\u7684\u5916\u94fe\u6620\u5c04 {host: \u7ad9\u540d}\u3002\u5185\u5b58+\u78c1\u76d8\u7f13\u5b58 6h\uff1b
    \u5168\u90e8\u5bfc\u822a\u7ad9\u5931\u8d25\u65f6\u56de\u843d\u78c1\u76d8\u65e7\u7f13\u5b58\uff08\u65e7\u6570\u636e\u597d\u8fc7\u6ca1\u6709\uff09\uff0c
    \u5e76\u987a\u5e26\u6293\u5bfc\u822a\u7ad9\u53d1\u5e03\u9875\uff0c\u628a\u65b0\u57df\u8865\u8fdb\u6c60\u5b50\uff08\u4e0b\u6b21\u76f4\u63a5\u5c1d\u8bd5\uff09\u3002"""
    now = time.time()
    if not force and _MEM.get('map') is not None and now < _MEM.get('ts', 0):
        return _MEM['map']
    disk = _load()
    if not force and disk.get('map') and now < disk.get('ts', 0):
        _MEM.update({'map': disk['map'], 'ts': disk['ts'],
                     'navs': disk.get('navs')})
        return disk['map']

    seeds_l = seeds()[:12]
    mmap, srcmap, navs_ok, extra = {}, {}, [], []
    for u in seeds_l:
        try:
            ok, ent, nv = _read_nav(u)
        except Exception:
            continue
        if not ok:
            continue
        for h, n in ent.items():
            mmap.setdefault(h, n)
            srcmap.setdefault(h, u)
        navs_ok.append(u)
        for x in nv:
            if x not in seeds_l and x not in extra:
                extra.append(x)
        if len(navs_ok) >= _NAV_FETCH_MAX:
            break

    if navs_ok:
        _MEM.update({'map': mmap, 'ts': now + _TTL, 'navs': navs_ok + extra,
                     'src': srcmap})
        d = dict(disk)                  # \u57fa\u4e8e\u51fd\u6570\u5f00\u5934\u90a3\u6b21\u5b8c\u6574\u8bfb\u76d8\uff0c\u52ff\u6574\u5305\u8986\u76d6
        d.update({'map': mmap, 'ts': now + _TTL, 'navs': navs_ok + extra,
                  'src': srcmap})
        _save(d)
        return mmap
    # \u5168\u6302\uff1a\u6293\u5bfc\u822a\u7ad9\u53d1\u5e03\u9875\u8981\u65b0\u57df\uff0830 \u5206\u949f\u8282\u6d41\uff09\u2014\u2014\u5148\u5f53\u573a\u8bd5\u8bfb\u4e00\u8f6e\uff0c
    # \u65e0\u8bba\u6210\u529f\u4e0e\u5426\u90fd\u628a\u5019\u9009\u5e76\u5165\u6c60\u5b50\uff0c\u4f9b\u4e0b\u6b21\u76f4\u63a5\u5c1d\u8bd5
    if now >= _MEM.get('pubts', 0):
        _MEM['pubts'] = now + 1800
        fresh = pub_hosts()
        for u in fresh[:_NAV_FETCH_MAX]:
            try:
                ok, ent, nv = _read_nav(u)
            except Exception:
                ok = False
            if not ok:
                continue
            for h, n in ent.items():
                mmap.setdefault(h, n)
                srcmap.setdefault(h, u)
            navs_ok.append(u)
            for x in nv:
                if x not in extra:
                    extra.append(x)
        if fresh:
            d = dict(disk)              # \u540c\u4e0a\uff1a\u7528\u5f00\u5934\u8bfb\u5230\u7684\u5b8c\u6574\u7f13\u5b58\uff0c\u907f\u514d\u4e8c\u6b21\u8bfb\u76d8\u5931\u8d25\u6e05\u7a7a
            pool = list(dict.fromkeys(list(d.get('navs') or []) + fresh))
            if navs_ok:
                pool = list(dict.fromkeys(pool + navs_ok + extra))
                d.update({'map': mmap, 'ts': now + _TTL, 'navs': pool, 'src': srcmap})
                _MEM.update({'map': mmap, 'ts': now + _TTL, 'navs': pool})
                _save(d)
                return mmap
            d['navs'] = pool            # \u53ea\u8865\u6c60\u5b50\uff0c\u4e0d\u52a8\u65e7 map \u7f13\u5b58
            _save(d)
    if disk.get('map'):
        return disk['map']          # \u5168\u6302\u56de\u843d\u65e7\u7f13\u5b58
    return mmap or {}


def nav_urls(x):
    """\u4e00\u6761\u5bfc\u822a\u7ad9\u7684\u5168\u90e8\u57df\uff1a\u4e3b\u57df + \u5907\u7528\u57df\uff08\u53bb\u91cd\u3001\u4fdd\u5e8f\uff09\u3002
    2026-09-10\uff1a\u7eff\u8272\u5c0f\u5bfc\u822a\u7684\u4e3b\u57df\u4e0e\u955c\u50cf\u57df\u5408\u4e3a\u4e00\u6761\u540e\uff0c\u6c60\u5b50\u8981\u628a\u4e24\u4e2a\u57df\u90fd\u6536\u8fdb\u6765\u3002"""
    out = []
    for u in [x.get('url')] + list(x.get('urls') or []):
        u = (u or '').strip()
        if u and u not in out:
            out.append(u)
    return out


def nav_pool():
    """\u5f53\u524d\u6c60\uff1a\u7528\u6237\u81ea\u914d\uff08\u542b\u53ef\u7f16\u8f91\u9884\u7f6e\uff09+ \u81ea\u6536\u96c6\uff1b\u4e24\u8005\u7686\u7a7a\u65f6\u624d\u7528\u51fa\u5382\u515c\u5e95\u3002"""
    d = _MEM.get('navs') if _MEM.get('navs') else _load().get('navs')
    out = []
    for x in user_navs():
        for u in nav_urls(x):
            if u not in out:
                out.append(u)
    for n in (d or []):
        if n not in out:
            out.append(n)
    if not out:
        out = list(_FALLBACK_SEEDS)
    return out


def nav_pages(force=False):
    """\u5bfc\u822a\u7ad9\u53d1\u5e03\u9875 [{nav,name,pub}]\uff08\u7ba1\u7406\u53f0\u300c\u5bfc\u822a\u7ad9\u7ba1\u7406\u300d\u7ef4\u62a4\uff0c\u63a8\u9001\u540e\u8bbe\u5907\u751f\u6548\uff09\u3002
    \u5bfc\u822a\u7ad9\u548c\u6e90\u7ad9\u4e00\u6837\u4e5f\u6709\u53d1\u5e03\u9875\uff08\u5982\u7eff\u8272\u5c0f\u5bfc\u822a\u7684 1800ga.com\u300c\u5730\u5740\u53d1\u5e03\u300d\u9875\uff09\uff0c
    \u4e3b\u57df\u8f6e\u6362\u540e\u4ece\u8fd9\u91cc\u627e\u56de\u5f53\u524d\u751f\u6548\u7684\u5730\u5740\u3002
    2026-09-10\uff1a\u53d1\u5e03\u9875\u5df2\u5185\u8054\u8fdb user_navs \u7684 pub \u5b57\u6bb5\uff08\u4e00\u6761\u4e00\u7ad9\uff09\uff1b
    \u9876\u5c42 nav_pubs \u4f5c\u4e3a\u65e7\u683c\u5f0f\u517c\u5bb9\u8bfb\u53d6\uff0c\u540c\u4e00\u6761\u7ad9\u53ea\u62a5\u4e00\u6b21\u3002"""
    c = _user_cfg(force)
    out, seen = [], set()
    for x in (c.get('user_navs') or []):
        if not isinstance(x, dict):
            continue
        pub, nav = (x.get('pub') or '').strip(), (x.get('url') or '').strip()
        if pub and nav and nav.rstrip('/') not in seen:
            seen.add(nav.rstrip('/'))
            out.append({'nav': nav, 'name': x.get('note') or nav.split('//')[-1].rstrip('/'),
                        'pub': pub})
    for x in (c.get('nav_pubs') or []):
        if not isinstance(x, dict) or not x.get('pub'):
            continue
        nav = (x.get('nav') or '').strip()
        if nav and nav.rstrip('/') in seen:
            continue
        if nav:
            seen.add(nav.rstrip('/'))
        out.append(x)
    return out


def pub_hosts(timeout=8):
    """\u5bfc\u822a\u7ad9\u53d1\u5e03\u9875\u91cc\u5217\u7684\u5019\u9009\u5bfc\u822a\u57df\u3002\u9875\u9762\u91cc\u7684\u5165\u53e3\u94fe\u63a5\u6587\u5b57\u5e38\u662f 1/2/3\uff0c\u6545\u4e0d\u770b\u6587\u5b57\uff0c
    \u53d6\u5168\u90e8\u5916\u94fe\u57df\uff1b\u8fd9\u4e9b\u57df\u53ef\u80fd\u4e34\u65f6\u6302\u9632\u722c\u9875\uff0c\u6545\u6b64\u5904\u4e0d\u9a8c\u8bc1\uff0c\u53ea\u4f5c\u5019\u9009\u3002"""
    out = []
    for x in nav_pages():
        t = _get(x['pub'], timeout)
        if not t:
            continue
        for m in re.finditer(r'href="(https?://[^"\s]+)"', t, re.I):
            hm = _HOST_RE.match(m.group(1))
            if not hm or _JUNK.search(hm.group(1)):
                continue
            u = 'https://' + hm.group(1) + '/'
            if u not in out:
                out.append(u)
    return out[:12]


def _cfg_local():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xbpq', 'explorer_seeds.json')
    try:
        with open(p, encoding='utf-8') as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _user_cfg(force=False):
    """\u7528\u6237\u81ea\u914d\u914d\u7f6e {user_navs, nav_pubs}\u3002\u672c\u5730\u6587\u4ef6\u4f18\u5148\uff08PC \u7ba1\u7406\u53f0\u521a\u6539\u5b8c\u7684\u573a\u666f\uff09\uff0c
    \u8bbe\u5907\u4e0a\u65e0\u672c\u5730\u6587\u4ef6\u65f6\u8d70 gitee raw\uff086h \u7f13\u5b58\uff0c\u5931\u8d25\u56de\u843d\u78c1\u76d8\u65e7\u503c\uff09\u3002
    \u4e24\u4e2a\u5b57\u6bb5\u5171\u7528\u672c\u51fd\u6570\uff0c\u53ea\u8054\u7f51\u4e00\u6b21\uff08\u66fe\u5404\u81ea\u8054\u7f51\u81f4 status \u63a5\u53e3 16s\uff09\u3002"""
    loc = _cfg_local()
    # \u672c\u5730\u6587\u4ef6\u5b58\u5728\u5373\u4fe1\u4efb\uff08\u542b\u7a7a\u5217\u8868\uff09\uff1aPC \u7ba1\u7406\u53f0\u573a\u666f\u4e0d\u518d\u6bcf\u6b21\u8054\u7f51\u6293 gitee
    if loc is not None:
        return loc
    uc = _load().get('ucfg') or {}
    if not force and uc.get('ts') and time.time() < uc.get('ts', 0):
        return {'user_navs': uc.get('navs') or [], 'nav_pubs': uc.get('nav_pubs') or []}
    obj, got = {}, False
    if requests is not None:
        t = _get(_USER_CFG_URL, 8)
        try:
            obj = json.loads(t) if t else {}
        except Exception:
            obj = {}
        got = bool(t)
    if got:
        navs = [x for x in (obj.get('user_navs') or []) if isinstance(x, dict) and x.get('url')]
        npubs = [x for x in (obj.get('nav_pubs') or []) if isinstance(x, dict) and x.get('pub')]
        d = _load()
        d['ucfg'] = {'navs': navs, 'nav_pubs': npubs, 'ts': time.time() + _TTL}
        _save(d)
        return {'user_navs': navs, 'nav_pubs': npubs}
    return {'user_navs': uc.get('navs') or [], 'nav_pubs': uc.get('nav_pubs') or []}


def user_navs(force=False):
    """\u7528\u6237\u81ea\u914d\u5bfc\u822a\u7ad9 [{url,urls,note,pub}]\u2014\u2014\u4e00\u6761 = \u4e00\u4e2a\u7ad9\u70b9\uff08\u4e3b\u57df+\u5907\u7528\u57df+\u53d1\u5e03\u9875\uff09"""
    return [x for x in (_user_cfg(force).get('user_navs') or [])
            if isinstance(x, dict) and x.get('url')]


def seeds():
    """\u5b8c\u6574\u79cd\u5b50\u6c60\uff1a\u7528\u6237\u81ea\u914d\uff08\u542b\u53ef\u7f16\u8f91\u9884\u7f6e\uff0c\u672c\u5730/gitee\uff09+ \u81ea\u6536\u96c6\uff08\u78c1\u76d8\uff09\uff1b
    \u4e24\u8005\u7686\u7a7a\u65f6\u56de\u843d\u5230\u51fa\u5382\u515c\u5e95\uff0c\u4fdd\u8bc1\u63a2\u7d22\u6c38\u8fdc\u6709\u8d77\u70b9\u3002"""
    out = []
    for x in user_navs():
        for u in nav_urls(x):
            if u not in out:
                out.append(u)
    for n in (_load().get('navs') or []):
        if n not in out:
            out.append(n)
    if not out:
        out = list(_FALLBACK_SEEDS)
    return out


def deep_site_map(extra=6):
    """\u6df1\u5ea6\u6a21\u5f0f\uff1a\u5728\u73b0\u6709\u6620\u5c04\u4e0a\u7ee7\u7eed\u5b9e\u6293\u79cd\u5b50\u6c60\u4e2d\u672a\u6293\u8fc7\u7684\u5bfc\u822a\u7ad9\uff08\u4ece\u6c60\u5c3e\u81ea\u6536\u96c6/\u7528\u6237\u7ad9\u5f00\u59cb\uff09\u3002
    \u8fd4\u56de (\u5408\u5e76\u6620\u5c04, \u65b0\u6293\u6210\u529f\u7684\u6e90\u5217\u8868)\u3002"""
    base = dict(nav_site_map() or {})
    src = dict(_load().get('src') or {})
    got = []
    for u in reversed(seeds()):
        if len(got) >= extra:
            break
        try:
            ok, ent, nv = _read_nav(u)
        except Exception:
            continue
        if not ok:
            continue
        got.append(u)
        for h, n in ent.items():
            if h not in base:
                base[h] = n
                src.setdefault(h, u)
    if got:
        _MEM.update({'map': base, 'src': src, 'ts': _MEM.get('ts', 0)})
        d = _load()
        d['map'] = base
        d['src'] = src
        _save(d)
    return base, got


def remember(alias, hosts):
    """\u63a2\u7d22\u6210\u679c\u6301\u4e45\u5316\uff08\u6bcf\u4e2a\u522b\u540d\u6700\u591a\u7559 8 \u6761\uff0c\u4f9b\u4e0b\u6b21 init \u9884\u8f7d\uff09"""
    if not hosts:
        return
    d = _load()
    cur = d.setdefault('hosts', {})
    lst = cur.get(alias, [])
    old = [x[0] for x in lst]
    for h in hosts:
        if h not in old:
            lst.append([h, time.time()])
    cur[alias] = lst[-8:]
    d['hosts'] = cur
    _save(d)


def known(alias):
    return [h for h, _ in (_load().get('hosts', {}).get(alias) or [])]


def is_portal(u, timeout=8):
    """\u5165\u53e3\u95e8\u6237\u5224\u5b9a\uff1a\u9875\u9762\u542b\u95e8\u6237\u7279\u5f81\u8bcd \u4e14 \u7ad9\u5185\u7ed3\u6784\u94fe\u63a5\u6781\u5c11\u3002
    \u771f\u7ad9\u5373\u4f7f\u5e26\u300c\u4e0b\u8f7dapp\u300d\u7b49\u63a8\u5e7f\u8bcd\uff0c\u7ad9\u5185\u94fe\u63a5\u4e5f\u8fdc\u8d85\u9608\u503c\uff0c\u4e0d\u4f1a\u8bef\u6740\u3002"""
    t = _get(u, timeout)
    if not t:
        return False            # \u6293\u4e0d\u5230\u4e0d\u5f3a\u5224\uff08\u4ea4\u56de\u8eab\u4efd\u9a8c\u8bc1\u7ed3\u679c\u51b3\u5b9a\uff09
    if not _PORTAL_KW.search(t):    # \u5168\u6587\u5339\u914d\uff1a\u95e8\u6237\u7279\u5f81\u8bcd\u5e38\u5728\u9875\u811a
        return False
    m = _HOST_RE.match(u)
    host = m.group(1) if m else ''
    internal = sum(1 for x in re.findall(r'<a\s[^>]*href="([^"]+)"', t, re.I)
                   if x.startswith('/') or (host and host in x))
    return internal < 10


def alias_candidates(aliases, max_candidates=12):
    """\u5bfc\u822a\u6620\u5c04\u91cc\u6309\u522b\u540d\u7b5b\u51fa\u7684**\u539f\u59cb\u5019\u9009** URL\uff08\u672a\u9a8c\u8bc1\u2014\u2014\u53ef\u80fd\u662f\u6d3b\u57df/\u8df3\u8f6c\u58f3/\u5165\u53e3\u95e8\u6237\uff09\u3002
    \u4e0e discover \u7684\u533a\u522b\uff1a\u4e0d\u505a\u4efb\u4f55\u63a2\u6d4b\u8fc7\u6ee4\uff0c\u4ea4\u7ed9\u8c03\u7528\u65b9\u505a\u58f3\u8ddf\u968f+\u8eab\u4efd\u9a8c\u8bc1\u3002"""
    mmap = nav_site_map() or {}
    pats = [str(a).lower() for a in (aliases or []) if a]
    cands = []
    for host, name in mmap.items():
        hay = (host + ' ' + str(name)).lower()
        if any(p in hay for p in pats):
            url = 'https://' + host
            if url not in cands:
                cands.append(url)
        if len(cands) >= max_candidates:
            break
    return cands


def explore_hosts(aliases, probe=None, timeout=8):
    """web \u578b\u6e90\u7edf\u4e00\u63a5\u5165\u5165\u53e3\uff08\u57df\u540d\u6c60/\u53d1\u5e03\u9875\u5168\u6302\u540e\u8c03\u7528\uff09\u3002
    aliases: ['douyin','\u6296\u9634']\uff0c\u9996\u4e2a\u4f5c\u4e3a\u6301\u4e45\u5316\u4e3b\u952e
    probe(host_url)->bool: \u6e90\u81ea\u8eab\u8eab\u4efd\u9a8c\u8bc1\uff08\u6293\u9996\u9875\u67e5\u7ad9\u540d\u7b49\uff09\uff1b
    \u6d41\u7a0b\uff1a\u2460 known() \u5386\u53f2\u6210\u679c\u9010\u4e2a\u5feb\u9a8c\uff08\u6d3b\u57df\u76f4\u63a5\u590d\u7528\uff0c\u7701\u4e00\u6b21\u5168\u91cf\u63a2\u7d22\uff09
         \u2192 \u2461 \u5168\u91cf discover + \u58f3\u8ddf\u968f\uff08\u951a\u70b9\u58f3\u2192Base64\u95e8\u6237\u2192\u6cdb\u89e3\u6790\u57fa\u57df\uff09
         \u2192 \u2462 remember \u6301\u4e45\u5316\u3002
    \u8fd4\u56de [\u6d3b\u57dfURL]\uff08\u6309\u4f18\u5148\u7ea7\u6392\u5e8f\uff09\uff0c\u5931\u8d25\u8fd4\u56de []\u3002"""
    primary = str(aliases[0]) if aliases else ''

    def _ok(u):
        if probe is None:
            base = len(_get(u, timeout)) > 3000
        else:
            try:
                base = bool(probe(u))
            except Exception:
                base = False
        if not base:
            return False
        try:
            return not is_portal(u, timeout)    # \u5165\u53e3\u95e8\u6237\u590d\u6838\uff08\u9632 SEO \u95e8\u7ad9\u5047\u9633\u6027\uff09
        except Exception:
            return True

    def _par(urls):
        """\u5e76\u884c\u9a8c\u8bc1\uff0c\u8fd4\u56de\u6d3b\u57df\u5217\u8868\uff08\u539f\u5e8f\uff09\u3002"""
        urls = [u for u in urls if u]
        if not urls:
            return []
        if ThreadPoolExecutor and as_completed and len(urls) > 1:
            out = []
            ex = ThreadPoolExecutor(max_workers=min(8, len(urls)))
            try:
                futs = {ex.submit(_ok, u): u for u in urls}
                for f in as_completed(futs):
                    try:
                        if f.result():
                            out.append(futs[f])
                    except Exception:
                        pass
            finally:
                ex.shutdown(wait=False)
            return [u for u in urls if u in out]
        return [u for u in urls if _ok(u)]

    def _wild_variants(urls):
        """\u88f8\u57fa\u57df(xxx.cc)\u751f\u6210\u6cdb\u89e3\u6790\u5019\u9009\u3002"""
        out = []
        for u in urls:
            m = _HOST_RE.match(u)
            if m and m.group(1).count('.') == 1:
                for w in _WILD_WORDS[:3]:
                    out.append('https://%s.%s' % (w, m.group(1)))
        return out

    def _shell_targets(u):
        """u \u662f\u8df3\u8f6c/\u5165\u53e3\u58f3\u65f6\u8fd4\u56de\u6307\u5411\u5019\u9009\uff1a
        \u2460 \u951a\u70b9\u58f3(<1200B \u81ea\u52a8\u8df3\u8f6c) -> href \u76ee\u6807
        \u2461 Base64 \u5165\u53e3\u58f3 -> \u89e3\u7801\u62bd\u57df\u540d\uff08\u5b98\u65b9\u95e8\u6237\uff0c\u5217\u5165\u53e3\u57df/\u6cdb\u89e3\u6790\u57fa\u57df\uff09
        \u6b63\u5e38\u9875\u9762\u8fd4\u56de []\u3002"""
        t = _get(u, timeout)
        if not t:
            return []
        if len(t) < 1200:
            m = _RE_ANCHOR.search(t)
            if m and _HOST_RE.match(m.group(1)):
                return [m.group(1).rstrip('/')]
            return []
        head = t[:3000].lower()
        if 'base64' in head:
            out = []
            blobs = sorted(set(re.findall(r"['\"]([A-Za-z0-9+/=]{100,})['\"]", t)),
                           key=len, reverse=True)[:2]
            for s in blobs:
                try:
                    d = base64.b64decode(s + '=' * (-len(s) % 4)).decode('utf-8', errors='ignore')
                except Exception:
                    continue
                for h in _RE_DOM.findall(d):
                    hl = h.lower()
                    if _JUNK.search(hl) or hl in u:
                        continue
                    url = 'https://' + hl
                    if url not in out:
                        out.append(url)
            return out[:8]
        return []

    def _resolve(u):
        """\u5019\u9009 -> \u6d3b\u57df\uff1a\u76f4\u63a5\u9a8c \u2192 \u58f3\u8ddf\u968f(\u22642\u5c42\uff0c\u6bcf\u5c42\u9644\u6cdb\u89e3\u6790\u5019\u9009) \u2192 \u8fd4\u56de\u9996\u4e2a\u6d3b\u57df\u3002
        \u6cdb\u89e3\u6790\u5019\u9009\u6392\u5728\u88f8\u57fa\u57df\u524d\uff08\u88f8 apex \u901a\u5e38\u6b7b\uff0c\u4efb\u610f\u8bcd\u5b50\u57df\u624d\u662f\u771f\u7ad9\u5f62\u6001\uff09\u3002"""
        if _ok(u):
            return u.rstrip('/')
        lvl1 = _shell_targets(u)[:5]
        cand1 = (_wild_variants(lvl1) + lvl1)[:16]
        for live in _par(cand1):
            return live.rstrip('/')
        for t in lvl1[:3]:                      # \u4e8c\u5c42\uff1a\u95e8\u6237\u5217\u7684\u57df\u53ef\u80fd\u53c8\u662f\u951a\u70b9\u58f3
            lvl2 = _shell_targets(t)[:5]
            cand2 = (_wild_variants(lvl2) + lvl2)[:16]
            live = _par(cand2)
            if live:
                return live[0].rstrip('/')
        return None

    live = []
    for u in known(primary):
        try:
            r = _resolve(u)
        except Exception:
            r = None
        if r and r not in live:
            live.append(r)
    if live:
        remember(primary, live)
        return live
    # \u5168\u91cf\u63a2\u7d22\uff1a\u539f\u59cb\u5019\u9009\uff08\u53ef\u80fd\u662f\u6d3b\u57df/\u951a\u70b9\u58f3/Base64\u95e8\u6237\uff09\u5e76\u884c\u505a\u58f3\u8ddf\u968f\u89e3\u6790
    got = alias_candidates(aliases)

    def _task(u):
        try:
            return _resolve(u)
        except Exception:
            return None

    if ThreadPoolExecutor and as_completed and len(got) > 1:
        ex = ThreadPoolExecutor(max_workers=min(8, len(got)))
        try:
            futs = {ex.submit(_task, u): u for u in got}
            for f in as_completed(futs):
                r = f.result()
                if r and r not in live:
                    live.append(r)
        finally:
            ex.shutdown(wait=False)
    else:
        for u in got:
            r = _task(u)
            if r and r not in live:
                live.append(r)
    if live:
        remember(primary, live)
    return live[:3]


def discover(aliases, validate=None, timeout=8, max_candidates=12, max_results=3):
    """\u4ece\u5bfc\u822a\u7ad9\u6620\u5c04\u91cc\u6309\u522b\u540d\u7b5b\u5019\u9009\u5e76\u9a8c\u8bc1\uff0c\u8fd4\u56de\u6d3b\u57df URL \u5217\u8868\u3002
    aliases: ['huangdou','\u9ec4\u8c46'] \u540c\u65f6\u5339\u914d\u57df\u540d\u4e0e\u7ad9\u540d\uff08\u5ffd\u7565\u5927\u5c0f\u5199\uff09
    validate(host)->bool: \u8c03\u7528\u65b9\u534f\u8bae\u7ea7\u9a8c\u8bc1\uff08API \u578b\u6e90\u5fc5\u4f20\uff0c\u9632\u5e7f\u544a\u58f3\u5192\u5145\uff09\uff1b
    \u7f3a\u7701\u9000\u5316\u4e3a HTTP \u63a2\u6d4b\uff08200 \u4e14\u6b63\u6587 >3000 \u5b57\uff09\u3002"""
    mmap = nav_site_map() or {}
    pats = [str(a).lower() for a in (aliases or []) if a]
    cands = []
    for host, name in mmap.items():
        hay = (host + ' ' + str(name)).lower()
        if any(p in hay for p in pats):
            url = 'https://' + host
            if url not in cands:
                cands.append(url)
        if len(cands) >= max_candidates:
            break
    if not cands:
        return []

    def _default(u):
        return len(_get(u, timeout)) > 3000

    def _check(u):
        try:
            return bool(validate(u))
        except Exception:
            return False

    fn = _check if validate else _default
    live = []
    if ThreadPoolExecutor and as_completed and len(cands) > 1:
        ex = ThreadPoolExecutor(max_workers=min(8, len(cands)))
        try:
            futs = {ex.submit(fn, u): u for u in cands}
            for f in as_completed(futs):
                try:
                    if f.result():
                        live.append(futs[f])
                except Exception:
                    pass
        finally:
            ex.shutdown(wait=False)
    else:
        live = [u for u in cands if fn(u)]
    return live[:max_results]
