# -*- coding: utf-8 -*-
"""
make_gitee.py —— 本地母本 -> gitee 发布版

母本 source_local.json（本地维护，明文无删减，gitignore 不入库）：
  sites 里带 "local": 1 的条目 = 本地专属备用源（gitee 451 扫描风险，不下发）
发布版 source.json（由本脚本生成后随 git push 下发）：
  剔除 local:1 条目，warningText 还原远程版，sites_count 重算

用法：
    python make_gitee.py           # 母本有变时重新生成 source.json（无差异则不写盘）
    explorer_admin 的「推送」会自动先跑本脚本再 git commit+push

铁律：source_local.json 含明文站名/敏感词，绝不 git add / push。
"""
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
    pub['sites'] = [s for s in master['sites'] if not s.get('local')]
    pub['warningText'] = WT_REMOTE
    pub['sites_count'] = len(pub['sites'])
    # sites_off 等其余字段随母本原样下发（现内容已通过 gitee 扫描；若新增敏感条目需自行验证）

    if os.path.exists(OUT):
        with open(OUT, encoding='utf-8') as f:
            cur = json.load(f)
        if cur == pub:
            print('source.json 与母本同步，无变化，跳过写盘')
            return 0
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pub, f, ensure_ascii=False, indent=2)
        f.write('\n')
    local_n = len(master['sites']) - len(pub['sites'])
    print('source.json 已生成: 远程 sites=%d（母本 %d 条，其中本地专属 %d 条未下发）'
          % (len(pub['sites']), len(master['sites']), local_n))
    return 0


if __name__ == '__main__':
    sys.exit(build())
