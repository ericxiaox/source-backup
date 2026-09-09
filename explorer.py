# -*- coding: utf-8 -*-
"""
explorer.py —— 多导航站自动探索 v1（源站域名池全挂时的兜底发现渠道）

背景：站方域名轮换快，内置候选池 + 发布页(hostresolver v2)之外，
导航站（绿色小导航等）长期存活且实时收录各家最新域名。把导航站本身
做成「发现渠道池」：
  种子导航(含其发布页镜像) -> 抓全量外链得 {域名: 站名} 映射
  -> 按源别名过滤候选 -> 调用方协议级验证 -> 活域插池

自收集：导航页互挂的其它导航站（站名含"导航"）动态扩充种子池并持久化；
"入口/最新地址/发布"类页面（各站发布页）记入 publish_pages() 备用。

公开接口：
  nav_site_map(force=False)          -> {host: name}（合并多导航站，缓存6h）
  deep_site_map(extra=6)             -> (map, 新抓源) 深度模式，多抓自收集导航站
  seeds() / nav_pool()               -> 种子池（内置+用户自配+自收集）/ 当前池
  user_navs()                        -> 用户自配导航站（explorer_admin 维护）
  publish_pages()                    -> {站名: host}（各站入口/发布页，备用）
  discover(aliases, validate, ...)   -> [活域URL]   validate(host)->bool
  remember(alias, hosts)             -> 探索成果持久化（下次 init 预载）
  known(alias)                       -> 历史探索成果（可能过期，调用方自会实测）

接入示例（xbpq/黄豆.py）：
  try:
      from explorer import discover, remember, known
  except Exception:
      discover = None
  # init():      self.hosts += [h for h in known('huangdou') if h not in self.hosts]
  # _api() 池全挂: discover(['huangdou','黄豆'], validate=self._check_host) -> 插池重试
"""
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

# 种子导航池：绿色小导航主域 + 其发布页镜像（about 页「地址发布」栏）
_NAV_SEEDS = [
    'https://xn--m-3h9b.lvse71.date/%E9%A3%8E%E6%99%AF/',
    'https://green61.net/',
    'https://1800ga.com/',
]
_NAV_HINT = '导航'
_PUB_HINTS = ('入口', '最新地址', '发布')
_NAV_POOL_MAX = 24      # 自收集导航站上限
_NAV_FETCH_MAX = 4      # 每次构建映射最多实抓的导航站数（控制耗时）
_PUB_MAX = 40
_TTL = 6 * 3600         # 站点映射缓存

# 用户自配导航站（explorer_admin.py 管理台维护，push 到 gitee 后设备自动生效）
_USER_CFG_URL = 'https://gitee.com/mallox/source/raw/master/xbpq/explorer_seeds.json'

# 必然混入的大平台/统计/静态资源域，不当候选
_JUNK = re.compile(
    r'(googletagmanager|google-analytics|gstatic|google\.|gitlab\.|github\.|'
    r'youtube\.|twitter\.|x\.com|t\.me|telegram\.|schema\.org|w3\.org|'
    r'qq\.com|baidu\.com|bing\.com|jsdelivr|unpkg|npmjs|jquery|bootstrap|'
    r'fontawesome|statcounter|cloudflare|email-protection|favicon|apple\.com)', re.I)

_A_RE = re.compile(r'<a\s[^>]*href="(https?://[^"\s]+)"[^>]*>(.*?)</a>', re.S | re.I)
_HOST_RE = re.compile(r'^https?://([a-z0-9][a-z0-9.\-]*\.[a-z]{2,})', re.I)

_FP = None
_MEM = {'map': None, 'ts': 0, 'navs': None, 'pubs': None}


# ---------------------------------------------------------------- 持久化（best-effort）
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


# ---------------------------------------------------------------- 抓取与解析
def _cfemail(text):
    """Cloudflare email-protection 混淆还原（导航页公告邮箱/联系方式用）"""
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
    """页面全部外链 -> {host: 站名}"""
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
    """读一个导航站：返回 (是否有效导航, {host: name}, 其它导航站列表, 发布页dict)。
    链接极少则视为跳转壳，跟随第一个外链（如 1800ga.com -> 最新导航域）。"""
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


# ---------------------------------------------------------------- 主接口
def nav_site_map(force=False):
    """合并多导航站的外链映射 {host: 站名}。内存+磁盘缓存 6h；
    全部导航站失败时回落磁盘旧缓存（旧数据好过没有）。"""
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
        d = _load()                     # 保留 hosts/ucfg，勿整包覆盖
        d.update({'map': mmap, 'ts': now + _TTL, 'navs': navs_ok + extra,
                  'pubs': pubs, 'src': srcmap})
        _save(d)
        return mmap
    if disk.get('map'):
        return disk['map']          # 全挂回落旧缓存
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
    """用户自配导航站 [{url, note}]。本地文件优先（PC 管理台刚改完的场景），
    设备上无本地文件时走 gitee raw（6h 缓存，失败回落磁盘旧值）。"""
    loc = _cfg_local()
    if loc and isinstance(loc.get('user_navs'), list) and loc['user_navs']:
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
    if navs or uc:
        d = _load()
        d['ucfg'] = {'navs': navs or uc.get('navs') or [], 'ts': time.time() + _TTL}
        _save(d)
    return navs or (uc.get('navs') or [])


def seeds():
    """完整种子池：内置 + 用户自配（本地/gitee）+ 自收集（磁盘）"""
    out = list(_NAV_SEEDS)
    for x in user_navs():
        if x['url'] not in out:
            out.append(x['url'])
    for n in (_load().get('navs') or []):
        if n not in out:
            out.append(n)
    return out


def deep_site_map(extra=6):
    """深度模式：在现有映射上继续实抓种子池中未抓过的导航站（从池尾自收集/用户站开始）。
    返回 (合并映射, 新抓成功的源列表)。"""
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
    """探索成果持久化（每个别名最多留 8 条，供下次 init 预载）"""
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


def discover(aliases, validate=None, timeout=8, max_candidates=12, max_results=3):
    """从导航站映射里按别名筛候选并验证，返回活域 URL 列表。
    aliases: ['huangdou','黄豆'] 同时匹配域名与站名（忽略大小写）
    validate(host)->bool: 调用方协议级验证（API 型源必传，防广告壳冒充）；
    缺省退化为 HTTP 探测（200 且正文 >3000 字）。"""
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
