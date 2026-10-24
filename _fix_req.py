# -*- coding: utf-8 -*-
"""Temp: чинит contains-требования задач новых уроков."""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
LANG_DIR = os.path.join(ROOT, 'data', 'languages')

FIX = {
    ('javascript', 7): ['name', 'hello', 'console.log'],
    ('javascript', 9): ['{ name }', 'Привет, ', 'console.log'],
    ('java', 10): ['String name', 'System.out.println', 'Привет, '],
    ('csharp', 7): ['List<int>', 'foreach', 'sum'],
    ('csharp', 9): ['string name', 'Console.WriteLine', 'Привет, '],
    ('php', 7): ['$user', 'echo', 'Привет, '],
    ('php', 9): ['$name', 'echo', 'Привет, '],
}

LESSON_ID = {'javascript': 7, 'java': 10, 'csharp': 7, 'php': 7}

for (lang, lid), req in FIX.items():
    path = os.path.join(LANG_DIR, lang + '.json')
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)
    data = raw.get(lang, raw)
    changed = 0
    for m in data['modules']:
        for l in m['lessons']:
            if l['id'] != lid:
                continue
            for t in l.get('tasks') or []:
                if t['check'].get('type') != 'contains':
                    continue
                sol = t['solution']
                if not all(r in sol for r in req):
                    continue
                t['check']['require'] = req
                changed += 1
    with open(path, 'w', encoding='utf-8', newline='') as f:
        json.dump(raw, f, ensure_ascii=False, indent=1)
    print(lang, f'L{lid}', 'обновлено задач:', changed)
