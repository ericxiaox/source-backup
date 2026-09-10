# -*- coding: utf-8 -*-
"""
explorer.py \u2014\u2014 \u591a\u5bfc\u822a\u7ad9\u81ea\u52a8\u63a2\u7d22 v1\uff08\u6e90\u7ad9\u57df\u540d\u6c60\u5168\u6302\u65f6\u7684\u515c\u5e95\u53d1\u73b0\u6e20\u9053\uff09

\u80cc\u666f\uff1a\u7ad9\u65b9\u57df\u540d\u8f6e\u6362\u5feb\uff0c\u5185\u7f6e\u5019\u9009\u6c60 + \u53d1\u5e03\u9875(hostresolver v2)\u4e4b\u5916\uff0c
\u5bfc\u822a\u7ad9\uff08\u7eff\u8272\u5c0f\u5bfc\u822a\u7b49\uff09\u957f\u671f\u5b58\u6d3b\u4e14\u5b9e\u65f6\u6536\u5f55\u5404\u5bb6\u6700\u65b0\u57df\u540d\u3002\u628a\u5bfc\u822a\u7ad9\u672c\u8eab
\u505a\u6210\u300c\u53d1\u73b0\u6e20\u9053\u6c60\u300d\uff1a
  \u79cd\u5b50\u5bfc\u822a(\u542b\u5176\u53d1\u5e03\u9875\u955c\u50cf) -> \u6293\u5168\u91cf\u5916\u94fe\u5f97 {\u57df\u540d: \u7ad9\u540d} \u6620\u5c04
  -> \u6309\u6e90\u522b\u540d\u8fc7\u6ee4\u5019\u9009 -> \u8c03\u7528\u65b9\u534f\u8bae\u7ea7\u9a8c\u8bc1 -> \u6d3b\u57df\u63d2\u6c60

\u81ea\u6536\u96c6\uff1a\u5bfc\u822a\u9875\u4e92\u6302\u7684\u5176\u5b83\u5bfc\u822a\u7ad9\uff08\u7ad9\u540d\u542b\"\u5bfc\u822a\"\uff09\u52a8\u6001\u6269\u5145\u79cd\u5b50\u6c60\u5e76\u6301\u4e45\u5316\uff1b
\"\u5165\u53e3/\u6700\u65b0\u5730\u5740/\u53d1\u5e03\"\u7c7b\u9875\u9762\uff08\u5404\u7ad9\u53d1\u5e03\u9875\uff09\u8bb0\u5165 publish_pages() \u5907\u7528\u3002

\u516c\u5f00\u63a5\u53e3\uff1a
  nav_site_map(force=False)          -> {host: name}\uff08\u5408\u5e76\u591a\u5bfc\u822a\u7ad9\uff0c\u7f13\u5b586h\uff09
  deep_site_map(extra=6)             -> (map, \u65b0\u6293\u6e90) \u6df1\u5ea6\u6a21\u5f0f\uff0c\u591a\u6293\u81ea\u6536\u96c6\u5bfc\u822a\u7ad9
  seeds() / nav_pool()               -> \u79cd\u5b50\u6c60\uff08\u5185\u7f6e+\u7528\u6237\u81ea\u914d+\u81ea\u6536\u96c6\uff09/ \u5f53\u524d\u6c60
  user_navs()                        -> \u7528\u6237\u81ea\u914d\u5bfc\u822a\u7ad9\uff08explorer_admin \u7ef4\u62a4\uff09
  publish_pages()                    -> {\u7ad9\u540d: host}\uff08\u5404\u7ad9\u5165\u53e3/\u53d1\u5e03\u9875\uff0c\u5907\u7528\uff09
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

# \u79cd\u5b50\u5bfc\u822a\u6c60\uff1a\u7eff\u8272\u5c0f\u5bfc\u822a\u4e3b\u57df + \u5176\u53d1\u5e03\u9875\u955c\u50cf\uff08about \u9875\u300c\u5730\u5740\u53d1\u5e03\u300d\u680f\uff09
_NAV_SEEDS = [
    'https://xn--m-3h9b.lvse71.date/%E9%A3%8E%E6%99%AF/',
    'https://green61.net/',
    'https://1800ga.com/',
]
_NAV_HINT = '\u5bfc\u822a'
_PUB_HINTS = ('\u5165\u53e3', '\u6700\u65b0\u5730\u5740', '\u53d1\u5e03')
_NAV_POOL_MAX = 24      # \u81ea\u6536\u96c6\u5bfc\u822a\u7ad9\u4e0a\u9650
_NAV_FETCH_MAX = 4      # \u6bcf\u6b21\u6784\u5efa\u6620\u5c04\u6700\u591a\u5b9e\u6293\u7684\u5bfc\u822a\u7ad9\u6570\uff08\u63a7\u5236\u8017\u65f6\uff09
_PUB_MAX = 40
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
_MEM = {'map': None, 'ts': 0, 'navs': None, 'pubs': None}


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
    """\u8bfb\u4e00\u4e2a\u5bfc\u822a\u7ad9\uff1a\u8fd4\u56de (\u662f\u5426\u6709\u6548\u5bfc\u822a, {host: name}, \u5176\u5b83\u5bfc\u822a\u7ad9\u5217\u8868, \u53d1\u5e03\u9875dict)\u3002
    \u94fe\u63a5\u6781\u5c11\u5219\u89c6\u4e3a\u8df3\u8f6c\u58f3\uff0c\u8ddf\u968f\u7b2c\u4e00\u4e2a\u5916\u94fe\uff08\u5982 1800ga.com -> \u6700\u65b0\u5bfc\u822a\u57df\uff09\u3002"""
    html = _get(url, 10)
    if not html:
        return False, {}, [], {}
    ent = _entries(html)
    if len(ent) < 5 and depth < 2:
        m = re.search(r'href="(https?://[^"\s]+)"', html, re.I)
        if m:
            ok2, ent2, nv2, pb2 = _read_nav(m.group(1), depth + 1)
            if ok2:
                return True, ent2, nv2, pb2
    if len(ent) < 10:
        return False, {}, [], {}
    navs, pubs = [], {}
    for host, name in ent.items():
        if _NAV_HINT in name and len(navs) < _NAV_POOL_MAX:
            navs.append('https://' + host + '/')
        elif any(h in name for h in _PUB_HINTS) and len(pubs) < _PUB_MAX:
            pubs[name[:20]] = 'https://' + host
    return True, ent, navs, pubs


# ---------------------------------------------------------------- \u4e3b\u63a5\u53e3
def nav_site_map(force=False):
    """\u5408\u5e76\u591a\u5bfc\u822a\u7ad9\u7684\u5916\u94fe\u6620\u5c04 {host: \u7ad9\u540d}\u3002\u5185\u5b58+\u78c1\u76d8\u7f13\u5b58 6h\uff1b
    \u5168\u90e8\u5bfc\u822a\u7ad9\u5931\u8d25\u65f6\u56de\u843d\u78c1\u76d8\u65e7\u7f13\u5b58\uff08\u65e7\u6570\u636e\u597d\u8fc7\u6ca1\u6709\uff09\u3002"""
    now = time.time()
    if not force and _MEM.get('map') is not None and now < _MEM.get('ts', 0):
        return _MEM['map']
    disk = _load()
    if not force and disk.get('map') and now < disk.get('ts', 0):
        _MEM.update({'map': disk['map'], 'ts': disk['ts'],
                     'navs': disk.get('navs'), 'pubs': disk.get('pubs')})
        return disk['map']

    seeds_l = seeds()[:12]
    mmap, srcmap, navs_ok, pubs, extra = {}, {}, [], {}, []
    for u in seeds_l:
        try:
            ok, ent, nv, pb = _read_nav(u)
        except Exception:
            continue
        if not ok:
            continue
        for h, n in ent.items():
            mmap.setdefault(h, n)
            srcmap.setdefault(h, u)
        for k, v in pb.items():
            pubs.setdefault(k, v)
        navs_ok.append(u)
        for x in nv:
            if x not in seeds_l and x not in extra:
                extra.append(x)
        if len(navs_ok) >= _NAV_FETCH_MAX:
            break

    if navs_ok:
        _MEM.update({'map': mmap, 'ts': now + _TTL, 'navs': navs_ok + extra,
                     'pubs': pubs, 'src': srcmap})
        d = _load()                     # \u4fdd\u7559 hosts/ucfg\uff0c\u52ff\u6574\u5305\u8986\u76d6
        d.update({'map': mmap, 'ts': now + _TTL, 'navs': navs_ok + extra,
                  'pubs': pubs, 'src': srcmap})
        _save(d)
        return mmap
    if disk.get('map'):
        return disk['map']          # \u5168\u6302\u56de\u843d\u65e7\u7f13\u5b58
    return mmap or {}


def nav_pool():
    d = _MEM.get('navs') if _MEM.get('navs') else _load().get('navs')
    out = list(_NAV_SEEDS)
    for x in user_navs():
        if x['url'] not in out:
            out.append(x['url'])
    for n in (d or []):
        if n not in out:
            out.append(n)
    return out


def publish_pages():
    d = _MEM.get('pubs') if _MEM.get('pubs') else _load().get('pubs')
    return d or {}


def _cfg_local():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xbpq', 'explorer_seeds.json')
    try:
        with open(p, encoding='utf-8') as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def user_navs(force=False):
    """\u7528\u6237\u81ea\u914d\u5bfc\u822a\u7ad9 [{url, note}]\u3002\u672c\u5730\u6587\u4ef6\u4f18\u5148\uff08PC \u7ba1\u7406\u53f0\u521a\u6539\u5b8c\u7684\u573a\u666f\uff09\uff0c
    \u8bbe\u5907\u4e0a\u65e0\u672c\u5730\u6587\u4ef6\u65f6\u8d70 gitee raw\uff086h \u7f13\u5b58\uff0c\u5931\u8d25\u56de\u843d\u78c1\u76d8\u65e7\u503c\uff09\u3002"""
    loc = _cfg_local()
    # \u672c\u5730\u6587\u4ef6\u5b58\u5728\u5373\u4fe1\u4efb\uff08\u542b\u7a7a\u5217\u8868\uff09\uff1aPC \u7ba1\u7406\u53f0\u573a\u666f\u4e0d\u518d\u6bcf\u6b21\u8054\u7f51\u6293 gitee\uff08\u66fe\u81f4 status \u63a5\u53e3 16s\uff09
    if loc is not None and isinstance(loc.get('user_navs'), list):
        return [x for x in loc['user_navs'] if isinstance(x, dict) and x.get('url')]
    disk = _load()
    uc = disk.get('ucfg') or {}
    if not force and isinstance(uc.get('navs'), list) and time.time() < uc.get('ts', 0):
        return uc['navs']
    navs = []
    if requests is not None:
        t = _get(_USER_CFG_URL, 8)
        try:
            obj = json.loads(t) if t else {}
        except Exception:
            obj = {}
        if isinstance(obj.get('user_navs'), list):
            navs = [x for x in obj['user_navs'] if isinstance(x, dict) and x.get('url')]
    if t:
        # \u6293\u53d6\u6210\u529f\u624d\u5199\u7f13\u5b58\uff08\u5931\u8d25\u4e0d\u7f13\u5b58\uff0c\u907f\u514d\u628a\u7f51\u7edc\u6545\u969c\u5f53\u7a7a\u914d\u7f6e\u7f13\u5b58 6h\uff09
        d = _load()
        d['ucfg'] = {'navs': navs, 'ts': time.time() + _TTL}
        _save(d)
    return navs or (uc.get('navs') or [])


def seeds():
    """\u5b8c\u6574\u79cd\u5b50\u6c60\uff1a\u5185\u7f6e + \u7528\u6237\u81ea\u914d\uff08\u672c\u5730/gitee\uff09+ \u81ea\u6536\u96c6\uff08\u78c1\u76d8\uff09"""
    out = list(_NAV_SEEDS)
    for x in user_navs():
        if x['url'] not in out:
            out.append(x['url'])
    for n in (_load().get('navs') or []):
        if n not in out:
            out.append(n)
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
            ok, ent, nv, pb = _read_nav(u)
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
