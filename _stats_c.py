# -*- coding: utf-8 -*-
import json
import os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'languages')
for f in ['python.json', 'javascript.json', 'java.json', 'cpp.json']:
    j = json.load(open(os.path.join(D, f), encoding='utf-8'))
    print(f, '=> top keys:', list(j.keys()))
    for k, v in j.items():
        if isinstance(v, dict):
            print('   ', k, 'sub keys:', list(v.keys())[:12])
            mods = v.get('modules', [])
            les = [l for m in mods for l in m.get('lessons', [])]
            print('        mods=', len(mods), 'lessons=', len(les),
                  'module_tests=', sum(1 for m in mods if m.get('test')),
                  'entrance=', len(v.get('entrance_test') or []),
                  'final=', len(v.get('final_test') or []),
                  'cheats=', len(v.get('cheatsheets') or []))