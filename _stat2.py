# -*- coding: utf-8 -*-
import json

for f in ['python', 'javascript', 'java', 'cpp']:
    d = json.load(open(f'data/languages/{f}.json', encoding='utf-8'))
    lang = list(d.keys())[0]
    L = d[lang]
    lessons = sum(len(m['lessons']) for m in L['modules'])
    tasks = sum(len(l.get('tasks', [])) for m in L['modules'] for l in m['lessons'])
    tests = sum(1 for m in L['modules'] if m.get('test'))
    cheats = len(L.get('cheatsheets', []))
    print(f'{lang}: modules={len(L["modules"])} lessons={lessons} '
          f'tasks={tasks} module_tests={tests} cheatsheets={cheats}')
    ids = [l['id'] for m in L['modules'] for l in m['lessons']]
    print(f'   lesson ids: {ids}')