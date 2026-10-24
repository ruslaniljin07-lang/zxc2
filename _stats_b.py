# -*- coding: utf-8 -*-
import json
import os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'languages')
rows = []
for f in ['python.json', 'javascript.json', 'java.json', 'cpp.json']:
    j = json.load(open(os.path.join(D, f), encoding='utf-8'))
    mods = j.get('modules', [])
    les = [l for m in mods for l in m.get('lessons', [])]
    ts = [l for l in les if l.get('test')]
    mt = [m for m in mods if m.get('test')]
    tk = [t for l in les for t in l.get('tasks', [])]
    ent = j.get('entrance_test') or []
    fin = j.get('final_test') or []
    ch = j.get('cheatsheets') or []
    fp = j.get('final_project')
    rows.append(
        f"{f:16s} mods={len(mods):2d} lessons={len(les):3d} mini={len(ts):3d} "
        f"mod_test={len(mt):2d} tasks={len(tk):3d} entrance={len(ent):2d} "
        f"final={len(fin):2d} cheats={len(ch):2d} proj={'yes' if fp else 'no'}")
print('\n'.join(rows))