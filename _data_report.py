# -*- coding: utf-8 -*-
"""Отчёт о полноте учебных данных по всем языкам."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data', 'languages')
lines = []

for fname in sorted(os.listdir(DATA)):
    if not fname.endswith('.json'):
        continue
    path = os.path.join(DATA, fname)
    with open(path, encoding='utf-8') as fh:
        raw = json.load(fh)
    lines.append('=' * 70)
    lines.append(fname)
    lines.append(f'  top-level type: {type(raw).__name__}  keys: {list(raw.keys())[:8]}')
    data = raw
    if len(raw) == 1 and isinstance(list(raw.values())[0], dict):
        data = list(raw.values())[0]
        lines.append(f'  unwrapped inner keys: {list(data.keys())}')
    mods = data.get('modules', [])
    les = [l for m in mods for l in m.get('lessons', [])]
    lines.append(f'  modules={len(mods)} lessons={len(les)}')
    lines.append(f'  entrance_test={len(data.get("entrance_test", []))}')
    cs = data.get('cheatsheets')
    lines.append(f'  cheatsheets type={type(cs).__name__} len={len(cs) if cs else 0}')
    lines.append(f'  final_project={str(data.get("final_project"))[:80]}')
    for m in mods:
        ls = m.get('lessons', [])
        tasks = sum(len(l.get('tasks', [])) for l in ls)
        tests = sum(len(l.get('test', [])) for l in ls)
        lines.append(f'    M{m.get("id")}: {m.get("title")!r} lessons={len(ls)} '
                     f'tasks={tasks} quiz={tests}')
        for l in ls:
            lines.append(f'       L{l.get("id")}: {str(l.get("title"))[:50]!r} '
                         f'theory={len(l.get("theory", []))} '
                         f'ex={len(l.get("examples", []))} '
                         f'tasks={len(l.get("tasks", []))} '
                         f'test={len(l.get("test", []))}')

with open(os.path.join(BASE, '_data_report.txt'), 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
print('written', len(lines))