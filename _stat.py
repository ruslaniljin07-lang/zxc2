import os, json

print('\n=== Языки ===')
lang_dir = 'data/languages'
if os.path.exists(lang_dir):
    for f in sorted(os.listdir(lang_dir)):
        if f.endswith('.json'):
            d = json.load(open(f'{lang_dir}/{f}'))
            modules = len(d.get('modules', []))
            lessons = sum(len(m.get('lessons', [])) for m in d.get('modules', []))
            tests = sum(len(m.get('test', [])) for m in d.get('modules', []))
            print(f'{f}: модули={modules} | уроки={lessons} | тесты={tests}')
else:
    print('Нет папки languages')

print('\n=== Задачи ===')
tasks_dir = 'data/tasks'
if os.path.exists(tasks_dir):
    for f in sorted(os.listdir(tasks_dir)):
        if f.endswith('.json'):
            try:
                d = json.load(open(f'{tasks_dir}/{f}'))
                if isinstance(d, list):
                    print(f'{f}: {len(d)} задач')
                else:
                    print(f'{f}: dict с keys={list(d.keys())}')
            except:
                print(f'{f}: ошибка чтения')
else:
    print('Нет папки tasks')

# -*- coding: utf-8 -*-
import json

for f in ['python', 'javascript', 'java', 'cpp']:
    d = json.load(open(f'data/languages/{f}.json', encoding='utf-8'))
    body = d[f]
    print(f'=== {f} ===')
    for m in body['modules']:
        for l in m['lessons']:
            t0 = l['tasks'][0] if l.get('tasks') else {}
            print(f"L{l['id']} [{m['id']}] {l['title']}")
            print(f"   desc: {l['description'][:70]}")
            print(f"   task1: {t0.get('title','?')} | init={repr(t0.get('initial_code',''))[:60]}")
            cs = l.get('cheatsheet', '')
            print(f"   cheat: {len(cs)} chars")