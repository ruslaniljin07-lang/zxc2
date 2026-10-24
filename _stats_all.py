# -*- coding: utf-8 -*-
"""Temp: сводка по курсам и банкам задач."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))

print('--- data/languages ---')
for name in sorted(os.listdir(os.path.join(ROOT, 'data', 'languages'))):
    code = name[:-5]
    with open(os.path.join(ROOT, 'data', 'languages', name),
              encoding='utf-8') as f:
        raw = json.load(f)
    c = raw.get(code, raw)
    mods = c.get('modules') or []
    lessons = sum(len(m.get('lessons') or []) for m in mods)
    tasks = sum(len(l.get('tasks') or []) for m in mods
                for l in (m.get('lessons') or []))
    mtests = sum(len((m.get('test') or {}).get('questions') or []) for m in mods)
    ltests = sum(len(l.get('test') or []) for m in mods
                 for l in (m.get('lessons') or []))
    print(f"{code:11} mod={len(mods)} les={lessons} ltasks={tasks} "
          f"ltests={ltests} mtests={mtests} "
          f"entrance={len(c.get('entrance_test') or [])} "
          f"cheats={len(c.get('cheatsheets') or [])} "
          f"name={c.get('name')!r} keys={sorted(c.keys())}")

print('--- data/tasks ---')
for name in sorted(os.listdir(os.path.join(ROOT, 'data', 'tasks'))):
    with open(os.path.join(ROOT, 'data', 'tasks', name),
              encoding='utf-8') as f:
        d = json.load(f)
    t = d.get('tasks') or []
    print(f"{name[:-5]:11} tasks={len(t)} keys={sorted(d.keys())}")

print('--- lessons.json ---')
with open(os.path.join(ROOT, 'data', 'lessons.json'), encoding='utf-8') as f:
    les = json.load(f)
print('type:', type(les).__name__, 'size:',
      len(les) if hasattr(les, '__len__') else '?')
