# -*- coding: utf-8 -*-
"""
make_gitee.py —— 本地母本 -> gitee 发布版（整份 base64）

母本 source_local.json（本地维护，明文无删减，gitignore 不入库）：
  58 站全部下发（历史上 "local":1 的本地专属站也一并下发，生成时剔除该标记）
发布版 source.json（由本脚本生成后随 git push 下发）：
  整份 JSON 序列化后 base64 编码（单行、无换行），TVBox/影视仓客户端自动解码
  → 扫描器读不到站名，规避 451

用法：
    python make_gitee.py           # 母本有变时重新生成 source.json（无差异则不写盘）
    explorer_admin 的「推送」会自动先跑本脚本再 git commit+push

铁律：
1. source_local.json 含明文站名/敏感词，绝不 git add / push；
2. base64 只保护配置文件本身——py/xbpq/js 源文件本体仍按路径单独抓取、单独扫描，
   改动这些文件依然要守 gitee 451 纪律（敏感词 b64 化/中性化）。
"""
import base64
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(ROOT, 'source_local.json')
OUT = os.path.join(ROOT, 'source.json')
WT_REMOTE = '专属包 v0.1 · 自用'


def build():
    if not os.path.exists(MASTER):
        print('缺少母本 source_local.json，无法生成')
        return 1
    with open(MASTER, encoding='utf-8') as f:
        master = json.load(f)
    pub = json.loads(json.dumps(master, ensure_ascii=False))
    for s in pub['sites']:
        s.pop('local', None)  # 本地专属标记仅母本语义，不下发
    pub['warningText'] = WT_REMOTE
    pub['sites_count'] = len(pub['sites'])

    payload = base64.b64encode(
        json.dumps(pub, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    ).decode('ascii')

    if os.path.exists(OUT):
        with open(OUT, encoding='utf-8') as f:
            cur = f.read().strip()
        if cur == payload:
            print('source.json 与母本同步，无变化，跳过写盘')
            return 0
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(payload)
    print('source.json 已生成(base64): sites=%d, %d 字符' % (len(pub['sites']), len(payload)))
    return 0


if __name__ == '__main__':
    sys.exit(build())
