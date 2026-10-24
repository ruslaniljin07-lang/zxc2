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


from utils.language_manager import load_language, LANGUAGES  # noqa: E402

log("### COURSE CONTENT ###")
for code in LANGUAGES:
    d = load_language(code)
    mods = d.get('modules', [])
    lessons = [l for m in mods for l in m.get('lessons', [])]
    tasks = [t for l in lessons for t in l.get('tasks', [])]
    mtests = [q for l in lessons for q in l.get('test', [])]
    et = d.get('entrance_test', [])
    log(f"{code:12s} modules={len(mods):3d} lessons={len(lessons):3d} tasks={len(tasks):3d} "
        f"minitest_q={len(mtests):3d} entrance={len(et):3d} cheats={len(d.get('cheatsheets', [])):3d} "
        f"final={d.get('final_project')!r}")
    for m in mods:
        log(f"    M{m.get('id'):>2}. {m.get('title'):42s} lessons={len(m.get('lessons', []))}")
    if lessons:
        s = lessons[0]
        log("    lesson keys:", sorted(s.keys()))
        if s.get('tasks'):
            log("    task keys:", sorted(s['tasks'][0].keys()))
    log("")

with open(os.path.join(BASE, '_content_check.txt'), 'w', encoding='utf-8') as fh:
    fh.write(out.getvalue())