# -*- coding: utf-8 -*-
import os, sys, json, io
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE); os.chdir(BASE)
from utils.language_manager import LANGUAGES, DATA_DIR

out = io.StringIO()
def log(*a):
    print(*a); print(*a, file=out)

for code in LANGUAGES:
    d = json.load(open(os.path.join(DATA_DIR, f'{code}.json'), encoding='utf-8'))
    d = d.get(code, d)
    mods = d.get('modules', [])
    nlessons = sum(len(m.get('lessons', [])) for m in mods)
    ntasks = sum(len(l.get('tasks', [])) for m in mods for l in m.get('lessons', []))
    ntest = sum(len(l.get('test', [])) for m in mods for l in m.get('lessons', []))
    # lessons missing test or tasks
    no_test = [l.get('id') for m in mods for l in m.get('lessons', []) if not l.get('test')]
    no_task = [l.get('id') for m in mods for l in m.get('lessons', []) if not l.get('tasks')]
    no_theory = [l.get('id') for m in mods for l in m.get('lessons', []) if not l.get('theory')]
    no_ex = [l.get('id') for m in mods for l in m.get('lessons', []) if not l.get('examples')]
    log(f"--- {code} ---")
    log(f"  modules={len(mods)} lessons={nlessons} tasks={ntasks} lessonTests={ntest} entrance={len(d.get('entrance_test', []))} cheatsheets={len(d.get('cheatsheets', []))}")
    log(f"  final_project={d.get('final_project')!r}")
    if no_test: log(f"  !! lessons without mini-test: {no_test}")
    if no_task: log(f"  !! lessons without tasks: {no_task}")
    if no_theory: log(f"  !! lessons without theory: {no_theory}")
    if no_ex: log(f"  !! lessons without examples: {no_ex}")

with open(os.path.join(BASE, '_content_out.txt'), 'w', encoding='utf-8') as f:
    f.write(out.getvalue())