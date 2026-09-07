# -*- coding: utf-8 -*-
"""
hostresolver.py —— 通用动态域名解析（发布页 + 候选镜像 + 跳转壳跟随）

用途：成人/影视类站点域名频繁失效，本模块提供“随时换域名”的统一机制：
  1. 尽力从【稳定发布页】抽取静态镜像链接（JS 渲染页通常抽不到，返回 []，属正常）；
  2. 合并一份【已知候选镜像列表】（按近期存活优先排序，来自发布页注释/历史记录）；
  3. 逐个 HTTP 实测：跳转壳(<a href> 跟随一次) → 真内容站(体积足够/含列表标记) 即采用；
  4. 全部失效则回退到候选列表首项（宁可用旧域也不让源崩溃）。

调用方（各 py 源）只需声明：
  PUBLISH_PAGE = 'https://xxx.xxx/'          # 稳定发布页（可空）
  CANDIDATE_HOSTS = ['https://a/', ...]      # 已知镜像，按存活排序
  self.host = resolve_host(PUBLISH_PAGE, CANDIDATE_HOSTS, headers=..., proxies=...)

注意：发布页若为纯 JS 渲染（域名客户端算出来），HTTP 抓取拿不到当前域名，
此时完全依赖 CANDIDATE_HOSTS 的实时实测——发现新活域名时补充进列表即可。
"""
import re

try:
    import requests
except Exception:
    requests = None


def resolve_host(publish_page=None, candidate_hosts=None, headers=None, proxies=None, timeout=8):
    """
    返回当前可用 host（去尾斜杠字符串）。全部失败返回候选首项去尾斜杠。
    """
    candidate_hosts = candidate_hosts or []
    # 1) 发布页静态链接（尽力而为，JS 壳返回 []）
    pub_domains = extract_publish_domains(publish_page, headers, proxies, timeout) if publish_page else []
    # 2) 合并候选并保持顺序去重
    combined = list(pub_domains) + list(candidate_hosts)
    seen = set()
    ordered = []
    for u in combined:
        u2 = (u or '').strip().rstrip('/')
        if u2 and u2 not in seen:
            seen.add(u2)
            ordered.append(u2)
    if not ordered:
        return (publish_page or '').rstrip('/')
    # 3) 逐个实测
    for url in ordered:
        h = _probe(url, headers, proxies, timeout)
        if h:
            return h
    # 4) 全部失效回退首项
    return ordered[0]


def extract_publish_domains(publish_page, headers, proxies, timeout):
    """尽力从发布页抽取镜像域名。JS 渲染页通常返回 []。"""
    if requests is None:
        return []
    try:
        r = requests.get(publish_page, headers=headers, proxies=proxies,
                         timeout=timeout, verify=False, allow_redirects=True)
        if r.status_code != 200:
            return []
        t = r.text or ''
        links = re.findall(r'href=["\'](https?://[^"\']+)["\']', t, re.I)
        out = []
        for l in links:
            m = re.match(r'https?://([a-z0-9.-]+\.[a-z]{2,})', l)
            if m:
                out.append(m.group(1))
        return out
    except Exception:
        return []


def _probe(url, headers, proxies, timeout, depth=0):
    """测试单域名：跳转壳则跟随 <a href> 一次；真内容则返回 host；否则 None。"""
    if requests is None:
        return None
    try:
        r = requests.get(url, headers=headers, proxies=proxies,
                         timeout=timeout, verify=False, allow_redirects=True)
        if r.status_code != 200:
            return None
        t = r.text or ''
        final = (r.url or url).rstrip('/')
        # 跳转壳：体积很小且含一个外链 → 跟随一次
        if len(t) < 3000 and depth < 2:
            m = re.search(r'href=["\'](https?://[^"\']+)["\']', t, re.I)
            if m:
                target = m.group(1).rstrip('/')
                if target and target != final:
                    return _probe(target, headers, proxies, timeout, depth + 1)
        # 真内容判定：体积足够 或 同时含 article 与 category 标记
        if len(t) > 5000 or ('article' in t and 'category' in t):
            return final
        return None
    except Exception:
        return None
