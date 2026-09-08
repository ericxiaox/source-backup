# -*- coding: utf-8 -*-
"""
hostresolver.py —— 通用动态域名解析 v2（发布页深度抽链 + 候选镜像并行实测 + 成功缓存）

解决：成人/影视类站点域名频繁轮换（泛子域 + 发布页动态生成），py 源内置候选池滞后失效。

v2 相对 v1 的根因级升级：
  1.【深度抽链】发布页若把内容藏进 document.write(Base64.decode('...'))（每日大赛/黑料
     不打烊同款），先解码再扫；并识别「随机词 + '.泛解析基域'」生成算法（words.random()
     + '.xxx.cc'），自动按词表生成 4 条候选线路——站方换基域时发布页解码即得新域，候选池
     永不过期。
  2.【并行探测】全部候选并发实测（总耗时≈单次超时，不再串行叠加 8s×N）。
  3.【成功缓存】选站结果缓存 30 分钟，同一次会话内重复 init 不再探测，秒开。
  4.【失败显式化】全部候选失败时返回 ''（不回退死域首项静默空转）。调用方应让各接口
     走自身 try/except 返回空结果，App 端表现为明确的失败而非假加载。

调用方（各 py 源）只需声明：
  PUBLISH_PAGE = 'https://xxx.xxx/'          # 稳定发布页（可空）
  CANDIDATE_HOSTS = ['https://a/', ...]      # 已知镜像，按存活排序
  self.host = resolve_host(PUBLISH_PAGE, CANDIDATE_HOSTS, headers=..., proxies=...)
  # 返回可能是 ''，调用方接口层 try/except 兜住即可

ext 机制（影视.json 站点条目 ext 字段，gitee 网页可直接改）：
  文本: publish@https://...;hosts@https://a,https://b;host@https://...
  JSON: {"publish":"...","hosts":["..."],"host":"...","proxies":{...}}
  - host@   锁定主页（最高优先级，跳过一切探测，站点结构大改时用）
  - publish@ 发布页地址（发布页换了改这里）
  - hosts@  新增候选镜像（实测顺序仅排在发布页泛解析候选之后）
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

# ---------------------------------------------------------------- 缓存
_CACHE = {}
_CACHE_TTL = 1800  # 成功选站缓存 30 分钟


def clear_cache():
    """清空选站缓存（调试用；调用方一般不需要）"""
    _CACHE.clear()


# ---------------------------------------------------------------- ext 解析
def parse_ext(ext_str):
    """解析影视.json 站点条目的 ext 字段（文本格式，分号分隔 @ 键值）。
    无法识别的片段自动忽略；解析失败返回 {}（py 回退内置默认值，不会崩源）。"""
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
    """App 传给 Spider.init() 的 extend 统一解析入口。
    兼容 None / dict(JSON) / str(文本或JSON)。任何异常返回 {}（不崩源）。"""
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


# ---------------------------------------------------------------- 发布页深度抽链
# 泛解析随机词池（与站方发布页同源取常用英文词；泛解析 DNS 下任意词均可解析）
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

# 「随机词 + '.泛解析基域'」生成算法（如 words.random() + '.iljzezhab.cc'）
_WILD_PAT = re.compile(
    r"[\w.]*random\s*\(\s*\)\s*\+\s*['\"]\.([a-z0-9-]+(?:\.[a-z0-9-]+)+)['\"]", re.I)
# 发布页 b64 壳（document.write(Base64.decode('...')) 整页 HTML 藏 base64）
_B64_SHELL_PAT = re.compile(r"Base64\.decode\(\s*['\"]([A-Za-z0-9+/=]{100,})['\"]")


def _expand_b64_shells(text):
    """展开发布页里的 Base64 壳，返回 [原文, 解码页1, 解码页2...]"""
    texts = [text]
    for m in _B64_SHELL_PAT.finditer(text):
        try:
            texts.append(base64.b64decode(m.group(1)).decode('utf-8', 'ignore'))
        except Exception:
            continue
    return texts


def extract_publish_domains(publish_page, headers, proxies, timeout):
    """发布页深度抽链。返回 (静态镜像链接列表, 泛解析基域列表)。
    JS 渲染但无 b64 壳的页面静态链接仍可能为空——泛解析基域识别是主通道。"""
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
            if m:
                static.append('https://' + m.group(1))
        for m in _WILD_PAT.finditer(t):
            wilds.add(m.group(1))
    return list(dict.fromkeys(static)), list(wilds)


# ---------------------------------------------------------------- 探测
def _probe(url, headers, proxies, timeout, depth=0):
    """测试单域名：跳转壳则跟随 <a href>（最多2层）；真内容返回最终 host；失败 None。"""
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
                    return _probe(target, headers, proxies, timeout, depth + 1)
        if len(t) > 5000 or ('article' in t and 'category' in t):
            return final
        return None
    except Exception:
        return None


def _probe_all(urls, headers, proxies, timeout):
    """并行探测，任一候选成功即刻返回（取消其余任务）；全败返回 ''。
    总耗时 ≈ 单次超时，不再随候选数量叠加。"""
    if not urls:
        return ''
    if not (ThreadPoolExecutor and as_completed) or len(urls) == 1:
        for u in urls:
            h = _probe(u, headers, proxies, timeout)
            if h:
                return h
        return ''
    ex = ThreadPoolExecutor(max_workers=min(12, len(urls)))
    try:
        futs = [ex.submit(_probe, u, headers, proxies, timeout) for u in urls]
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


# ---------------------------------------------------------------- 主入口
def resolve_host(publish_page=None, candidate_hosts=None, headers=None,
                 proxies=None, timeout=8, use_cache=True):
    """返回当前可用 host（去尾斜杠）。全部失败返回 ''（调用方接口层自行兜空）。
    顺序：发布页泛解析候选(最新鲜) > ext/内置候选 > 发布页静态链接。"""
    candidate_hosts = candidate_hosts or []
    key = (publish_page or '', tuple(candidate_hosts))
    if use_cache:
        hit = _CACHE.get(key)
        if hit and time.time() < hit[1]:
            return hit[0]

    # 1) 发布页深度抽链（泛解析基域自动生成候选 + 静态镜像链接）
    pub_domains, wild_bases = [], []
    if publish_page:
        try:
            pub_domains, wild_bases = extract_publish_domains(
                publish_page, headers, proxies, timeout)
        except Exception:
            pub_domains, wild_bases = [], []
    words = random.sample(_WILD_WORDS, min(4, len(_WILD_WORDS)))
    wild_candidates = ['https://%s.%s' % (w, b) for b in wild_bases for w in words]

    # 2) 合并候选（保序去重）：泛解析 > 外部候选 > 发布页静态链接
    combined = wild_candidates + list(candidate_hosts) + pub_domains
    seen = set()
    ordered = []
    for u in combined:
        u2 = (u or '').strip().rstrip('/')
        if not re.match(r'^https?://', u2):
            u2 = 'https://' + u2
        if u2 and u2 not in seen:
            seen.add(u2)
            ordered.append(u2)
    if not ordered:
        return ''

    # 3) 并行实测（use_cache=False=强制刷新，但成功结果仍写缓存供后续 init 秒开）
    host = _probe_all(ordered, headers, proxies, timeout)
    if host:
        _CACHE[key] = (host, time.time() + _CACHE_TTL)
    return host
