# -*- coding: utf-8 -*-
import os, sys, io, json
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
from utils.language_manager import load_language, LANGUAGES, DATA_DIR
buf = []
for code in LANGUAGES:
    p = os.path.join(DATA_DIR, code + '.json')
    raw = json.load(open(p, encoding='utf-8'))
    d = load_language(code)
    mods = d.get('modules', [])
    nl = sum(len(m.get('lessons', [])) for m in mods)
    nt = sum(len(l.get('test', [])) for m in mods for l in m.get('lessons', []))
    ntasks = sum(len(l.get('tasks', [])) for m in mods for l in m.get('lessons', []))
    tkeys = sorted({k for m in mods for l in m.get('lessons', []) for k in l.keys()})
    buf.append(f"{code}: top_keys={list(raw.keys())} modules={len(mods)} lessons={nl} "
               f"lesson_tests={nt} tasks={ntasks} cheats={len(d.get('cheatsheets', []))} "
               f"entrance={len(d.get('entrance_test', []))}")
    buf.append(f"   lesson_keys={tkeys}")
    buf.append(f"   final_project={d.get('final_project')!r}")
    buf.append("")
txt = '\n'.join(buf)
open(os.path.join(BASE, '_counts.txt'), 'w', encoding='utf-8').write(txt)
print(txt)