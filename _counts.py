# -*- coding: utf-8 -*-
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'languages')
lines = []
for f in sorted(os.listdir(D)):
    if not f.endswith('.json'):
        continue
    code = f[:-5]
    d = json.load(open(os.path.join(D, f), encoding='utf-8')).get(code, {})
    mods = d.get('modules', [])
    les = sum(len(m.get('lessons', [])) for m in mods)
    tsks = sum(len(l.get('tasks', [])) for m in mods for l in m.get('lessons', []))
    line = (f"{code:12s} modules={len(mods):3d} lessons={les:3d} tasks={tsks:3d} "
            f"test={len(d.get('entrance_test', [])):3d} cheats={len(d.get('cheatsheets', [])):3d} "
            f"final={bool(d.get('final_project'))} proj_steps={len(d.get('final_project_steps', []))}")
    lines.append(line)
    print(line)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_counts.txt'), 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
