# -*- coding: utf-8 -*-
"""
explorer_admin.py —— explorer 管理台（PC 本地运行）

功能：站点搜索（含深度搜索）/ 导航站管理（增删测活）/ 探索状态查看
推送：页面上点「推送」才 git push（explorer_seeds.json 变更下发到设备）

运行：
    C:/Users/xiaox/.workbuddy/binaries/python/envs/default/Scripts/python.exe explorer_admin.py
    浏览器打开 http://127.0.0.1:5010
"""
import json
import os
import re
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import explorer  # noqa: E402

try:
    from flask import Flask, jsonify, request
except ImportError:
    print('缺少 flask：请先在 venv 里 pip install flask')
    sys.exit(1)

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(ROOT, 'xbpq', 'explorer_seeds.json')
PORT = 5010

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

_HTML = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<title>explorer 管理台</title>
<style>
body{font:13px/1.6 system-ui,'Microsoft YaHei',sans-serif;margin:0;background:#f6f6f2;color:#2c2c2a}
.wrap{max-width:760px;margin:0 auto;padding:16px}
header{display:flex;align-items:center;gap:10px;padding:2px 0 12px}
.dot{width:9px;height:9px;border-radius:50%;background:#639922}
h1{font-size:16px;font-weight:500;margin:0}
#stato{margin-left:auto;font-size:12px;color:#888780}
.tabs{display:flex;gap:4px;border-bottom:1px solid #d3d1c7;margin-bottom:14px}
.tabs button{border:0;background:none;padding:8px 16px;font-size:13px;color:#5f5e5a;cursor:pointer;border-bottom:2px solid transparent}
.tabs button.on{color:#185fa5;border-bottom-color:#185fa5;font-weight:500}
.bar{display:flex;gap:8px;margin-bottom:10px}
input,select{flex:1;padding:7px 10px;border:1px solid #d3d1c7;border-radius:8px;font-size:13px;background:#fff}
button.op{padding:6px 14px;border:1px solid #d3d1c7;border-radius:8px;background:#fff;cursor:pointer;font-size:13px}
button.op:hover{border-color:#888780}
button.pri{background:#185fa5;color:#fff;border-color:#185fa5}
.card{background:#fff;border:1px solid #e2e1da;border-radius:10px;overflow:hidden;margin-bottom:14px}
.row{display:flex;align-items:center;gap:10px;padding:9px 12px;border-bottom:1px solid #f0efe9}
.row:last-child{border-bottom:0}
.row .main{min-width:0;flex:1}
.row .t{font-weight:500}
.row .s{font-size:12px;color:#888780;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tag{font-size:12px;padding:1px 8px;border-radius:5px;background:#e6f1fb;color:#0c447c;flex-shrink:0}
.tag.ok{background:#eaf3de;color:#27500a}
.tag.bad{background:#fcebeb;color:#791f1f}
.tag.mut{background:#f1efe8;color:#5f5e5a}
.mini{padding:2px 10px;font-size:12px;border-radius:6px}
.hint{font-size:12px;color:#888780;margin:6px 0 10px}
pre{background:#fff;border:1px solid #e2e1da;border-radius:8px;padding:10px;font-size:12px;white-space:pre-wrap;max-height:220px;overflow:auto}
.hide{display:none}
label.ck{display:flex;align-items:center;gap:6px;font-size:13px;white-space:nowrap}
</style></head><body><div class="wrap">
<header><div class="dot"></div><h1>explorer 管理台</h1><span id="stato">加载中…</span></header>
<div class="tabs">
<button class="on" data-p="search">站点搜索</button>
<button data-p="navs">导航站管理</button>
<button data-p="stat">探索状态</button>
</div>

<div id="p-search">
  <div class="bar">
    <input id="q" placeholder="输入站名或关键词，如：黄豆 / 抖阴 / 黑料 / dasai" onkeydown="if(event.key=='Enter')doSearch(0)">
    <label class="ck"><input type="checkbox" id="deep">深度搜索</label>
    <button class="op pri" onclick="doSearch(0)">搜索</button>
  </div>
  <div class="hint" id="sHint">域名+站名模糊匹配；深度搜索会临时多抓自收集导航站（慢 5~15 秒，结果并入缓存）</div>
  <div id="sOut"></div>
</div>

<div id="p-navs" class="hide">
  <div class="bar">
    <input id="nUrl" placeholder="粘贴导航站 URL，如 https://xxx.xxx/路径/">
    <input id="nNote" placeholder="备注（可选）" style="flex:0 0 160px">
    <button class="op pri" onclick="addNav()">添加</button>
  </div>
  <div class="hint">添加时自动验证（页面外链 ≥10 条才算导航站）；用户站排序最前，push 后设备 6h 内自动生效</div>
  <div class="bar" style="justify-content:flex-end">
    <button class="op" onclick="doRebuild()">重建映射缓存</button>
    <button class="op pri" onclick="doPush()">保存并推送到 gitee</button>
  </div>
  <div id="nOut"></div>
  <pre id="pushLog" class="hide"></pre>
</div>

<div id="p-stat" class="hide">
  <div class="hint">各源探索成果（known）与发布页字典</div>
  <div id="tOut"></div>
</div>
</div>
<script>
let POOL=[],USER=[];
const $=id=>document.getElementById(id);
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('.tabs button').forEach(x=>x.classList.remove('on'));
  b.classList.add('on');
  ['search','navs','stat'].forEach(p=>$('p-'+p).classList.toggle('hide',p!==b.dataset.p));
});
function esc(s){return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
async function status(){
  const r=await (await fetch('/api/status')).json();
  const ts=r.ts?new Date(r.ts*1000).toLocaleTimeString():'-';
  $('stato').textContent=`映射 ${r.count} 条 · 导航池 ${r.pool.length} 个 · 缓存至 ${ts}`;
  POOL=r.pool_with_kind; USER=r.user_navs;
  renderNavs();
  renderStat(r);
}
function rowNav(u,kind,note,live){
  const cls=kind=='用户'?'':(kind=='内置'?'mut':'mut');
  return `<div class="row"><div class="main"><div class="t">${esc(u.replace(/^https?:\\/\\//,''))}</div>
  <div class="s">${esc(note||kind)}</div></div>
  <span class="tag ${cls}" id="k${hash(u)}">${kind}</span>
  <button class="op mini" onclick="checkNav('${esc(u)}',this)">测活</button>
  ${kind=='用户'?`<button class="op mini" onclick="delNav('${esc(u)}')">删</button>`:''}
  </div>`;
}
function hash(s){let h=0;for(const c of s)h=(h*31+c.charCodeAt(0))|0;return Math.abs(h)}
function renderNavs(){
  $('nOut').innerHTML='<div class="card">'+POOL.map(x=>rowNav(x.url,x.kind,x.note)).join('')+'</div>';
}
function renderStat(r){
  const kn=Object.entries(r.hosts||{});
  const pb=Object.entries(r.pubs||{});
  $('tOut').innerHTML=
   `<div class="card">${kn.length?kn.map(([a,hs])=>`<div class="row"><div class="main"><div class="t">${esc(a)}</div><div class="s">${hs.map(esc).join(' · ')}</div></div></div>`).join(''):'<div class="row"><div class="s">暂无探索成果</div></div>'}</div>
    <div class="card">${pb.length?pb.map(([n,u])=>`<div class="row"><div class="main"><div class="t">${esc(n)}</div><div class="s">${esc(u)}</div></div></div>`).join(''):'<div class="row"><div class="s">发布页字典为空</div></div>'}</div>`;
}
async function doSearch(deepForce){
  const q=$('q').value.trim();if(!q)return;
  const deep=$('deep').checked||deepForce;
  $('sHint').textContent=deep?'深度搜索中，最多抓 6 个未抓过的导航站…':'搜索中…';
  const r=await (await fetch(`/api/search?q=${encodeURIComponent(q)}&deep=${deep?1:0}`)).json();
  $('sHint').textContent=r.deep?`深度搜索：新抓 ${r.deep_got.length} 个导航站 · 命中 ${r.list.length} 条`:`命中 ${r.list.length} 条`;
  $('sOut').innerHTML='<div class="card">'+(r.list.length?r.list.map(x=>`
    <div class="row"><div class="main"><div class="t">${esc(x.host)}</div>
    <div class="s">${esc(x.name||'?')} · 收录于 ${esc(x.src||'?')}</div></div>
    <span class="tag" id="c${hash(x.url)}">未验证</span>
    <button class="op mini" onclick="checkUrl('${esc(x.url)}',this)">测活</button>
    <button class="op mini" onclick="navigator.clipboard.writeText('${esc(x.url)}')">复制</button>
    </div>`).join(''):'<div class="row"><div class="s">无匹配（可试深度搜索）</div></div>')+'</div>';
}
async function checkUrl(u,btn){
  const id='c'+hash(u);const el=$(id);if(el)el.textContent='测活中…';
  const r=await (await fetch('/api/check?url='+encodeURIComponent(u))).json();
  if(el)el.textContent=r.ok?`活 ${r.status}·${r.title.slice(0,14)}`:`不通 ${r.err||r.status||''}`;
  el.className='tag '+(r.ok?'ok':'bad');
}
async function checkNav(u,btn){
  btn.textContent='…';
  const r=await (await fetch('/api/checknav?url='+encodeURIComponent(u))).json();
  btn.textContent=r.ok?`活·${r.links}链`:'不可用/非导航';
}
async function addNav(){
  const url=$('nUrl').value.trim();if(!url)return;
  const r=await (await fetch('/api/navs',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({url,note:$('nNote').value.trim()})})).json();
  if(!r.ok){alert('添加失败：'+r.err);return}
  $('nUrl').value='';$('nNote').value='';status();
}
async function delNav(u){
  if(!confirm('删除 '+u+' ？（保存并推送后才影响设备）'))return;
  await fetch('/api/navs/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:u})});
  status();
}
async function doRebuild(){
  $('stato').textContent='重建中…（约10秒）';
  const r=await (await fetch('/api/rebuild',{method:'POST'})).json();
  alert('重建完成：'+r.count+' 条映射');status();
}
async function doPush(){
  const el=$('pushLog');el.classList.remove('hidden');el.classList.remove('hide');el.textContent='推送中…';
  const r=await (await fetch('/api/push',{method:'POST'})).json();
  el.textContent=(r.ok?'✅ 推送成功\n':'❌ 推送失败\n')+r.log.join('\n');
  status();
}
status();
</script></body></html>"""


def _cfg_read():
    try:
        with open(CFG, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {'user_navs': []}


def _cfg_write(d):
    with open(CFG, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write('\n')


@app.get('/')
def index():
    return _HTML


@app.get('/api/status')
def api_status():
    m = explorer.nav_site_map() or {}
    d = explorer._load()
    pool = explorer.nav_pool()
    users = [x['url'] for x in explorer.user_navs()]
    pwk = [{'url': u, 'kind': '用户' if u in users else ('内置' if u in explorer._NAV_SEEDS else '自收集'),
            'note': next((x.get('note') for x in explorer.user_navs() if x['url'] == u), '')} for u in pool]
    return jsonify(ok=True, count=len(m), ts=d.get('ts'), pool=pool, pool_with_kind=pwk,
                   user_navs=explorer.user_navs(), pubs=explorer.publish_pages(),
                   hosts=d.get('hosts') or {})


@app.get('/api/search')
def api_search():
    q = request.args.get('q', '').strip().lower()
    deep = request.args.get('deep') == '1'
    deep_got = []
    if deep:
        m, deep_got = explorer.deep_site_map(6)
    else:
        m = explorer.nav_site_map() or {}
    src = explorer._load().get('src') or {}
    toks = [t for t in re.split(r'\s+', q) if t]
    hits = []
    for host, name in m.items():
        hay = (host + ' ' + str(name)).lower()
        if all(t in hay for t in toks):
            hits.append({'host': host, 'name': name, 'src': (src.get(host) or '').replace('https://', ''),
                         'url': 'https://' + host})
    hits.sort(key=lambda x: (0 if any(t == x['host'] for t in toks) else 1, x['host']))
    return jsonify(ok=True, list=hits[:60], deep=deep, deep_got=deep_got)


@app.get('/api/check')
def api_check():
    u = request.args.get('url', '')
    try:
        t = explorer._get(u, 10)
        if not t:
            return jsonify(ok=False, err='无响应/非200')
        import re as _re
        mt = _re.search(r'<title>([^<]*)</title>', t)
        return jsonify(ok=True, status=200, title=(mt.group(1).strip()[:30] if mt else ''), length=len(t))
    except Exception as e:
        return jsonify(ok=False, err=str(e)[:80])


@app.get('/api/checknav')
def api_checknav():
    u = request.args.get('url', '')
    try:
        ok, ent, nv, pb = explorer._read_nav(u)
        return jsonify(ok=bool(ok), links=len(ent))
    except Exception as e:
        return jsonify(ok=False, err=str(e)[:80])


@app.post('/api/navs')
def api_navs_add():
    u = (request.json or {}).get('url', '').strip()
    note = (request.json or {}).get('note', '').strip()
    if not re.match(r'^https?://', u):
        return jsonify(ok=False, err='URL 需以 http(s):// 开头')
    ok, ent, nv, pb = explorer._read_nav(u)
    if not ok:
        return jsonify(ok=False, err='验证未通过：不可达或页面外链 <10 条（不像导航站）')
    d = _cfg_read()
    d.setdefault('user_navs', [])
    if any(x.get('url') == u for x in d['user_navs']):
        return jsonify(ok=False, err='已存在')
    d['user_navs'].append({'url': u, 'note': note or f'外链{len(ent)}条', 'added': __import__('time').strftime('%Y-%m-%d')})
    _cfg_write(d)
    explorer._MEM['ts'] = 0        # 使内存缓存失效，下次构建即带上新站
    return jsonify(ok=True, links=len(ent))


@app.post('/api/navs/delete')
def api_navs_del():
    u = (request.json or {}).get('url', '')
    d = _cfg_read()
    d['user_navs'] = [x for x in d.get('user_navs', []) if x.get('url') != u]
    _cfg_write(d)
    explorer._MEM['ts'] = 0
    return jsonify(ok=True)


@app.post('/api/rebuild')
def api_rebuild():
    m = explorer.nav_site_map(force=True) or {}
    return jsonify(ok=True, count=len(m))


@app.post('/api/push')
def api_push():
    cmds = [['git', 'add', 'xbpq/explorer_seeds.json'],
            ['git', 'commit', '-m', 'explorer_seeds 用户配置更新 (explorer_admin)'],
            ['git', 'push']]
    log, ok = [], True
    for c in cmds:
        r = subprocess.run(c, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        out = ((r.stdout or '') + (r.stderr or '')).strip()
        log.append('$ ' + ' '.join(c) + '\n' + (out[:500] or '(无输出)'))
        if r.returncode != 0:
            if 'nothing to commit' in out or 'nothing added' in out:
                log.append('（无变更，跳过 push）')
                break
            ok = False
            break
    return jsonify(ok=ok, log=log)


if __name__ == '__main__':
    print(f'explorer 管理台: http://127.0.0.1:{PORT}')
    app.run(host='127.0.0.1', port=PORT, debug=False)
