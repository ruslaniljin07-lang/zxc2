# -*- coding: utf-8 -*-
import os
import sys
import json
import io

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
out = io.StringIO()


def log(*a):
    print(*a)
    print(*a, file=out)


log("### LANGUAGE JSON FILES ###")
for f in sorted(os.listdir(os.path.join(BASE, 'data', 'languages'))):
    p = os.path.join(BASE, 'data', 'languages', f)
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        log(f"  {f}: JSON ERROR {e}")
        continue
    mods = d.get('modules', [])
    totals = sum(len(m.get('lessons', [])) for m in mods)
    tasks = sum(len(l.get('tasks', [])) for m in mods for l in m.get('lessons', []))
    tests = sum(len(l.get('test', [])) for m in mods for l in m.get('lessons', []))
    log(f"  {f:20s} modules={len(mods):3d} lessons={totals:3d} tasks={tasks:3d} minitests={tests:3d} entrance={len(d.get('entrance_test', [])):3d} cheats={len(d.get('cheatsheets', []))}")
    for m in mods[:3]:
        log(f"      M{m.get('id')}. {m.get('title')} -> {len(m.get('lessons', []))} lessons")
    log("      keys:", sorted(d.keys()))

log("")
log("### TEMPLATE URL_FOR USAGE ###")
import re
for f in sorted(os.listdir(os.path.join(BASE, 'templates'))):
    txt = open(os.path.join(BASE, 'templates', f), encoding='utf-8').read()
    hits = set(re.findall(r"url_for\('([a-zA-Z_]+)'([^)]*)\)", txt))
    if hits:
        log(f"  {f}")
        for name, args in sorted(hits):
            log(f"      {name}({args.strip()})")

with open(os.path.join(BASE, '_state_out.txt'), 'w', encoding='utf-8') as fh:
    fh.write(out.getvalue())