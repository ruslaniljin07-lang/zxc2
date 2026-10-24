# -*- coding: utf-8 -*-
"""Temp: валидация банков задач — прогон эталонных решений через check_code."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from utils.code_checker import check_code  # noqa: E402

LANGS = ['python', 'javascript', 'java', 'cpp', 'go', 'csharp', 'typescript',
         'php', 'rust']
REQUIRED = ['id', 'title', 'topic', 'difficulty', 'xp', 'description',
            'initial_code', 'check', 'hints', 'solution']

problems = []
for lang in LANGS:
    path = os.path.join(ROOT, 'data', 'tasks', lang + '.json')
    if not os.path.exists(path):
        problems.append(f'{lang}: файла банка нет')
        continue
    with open(path, encoding='utf-8') as f:
        tasks = json.load(f).get('tasks', [])
    ids = [t['id'] for t in tasks]
    dup = {i for i in ids if ids.count(i) > 1}
    print(f'=== {lang}: {len(tasks)} задач, id {min(ids)}..{max(ids)}'
          + (f', ДУБЛИ: {sorted(dup)}' if dup else ''))
    for t in tasks:
        miss = [k for k in REQUIRED if k not in t]
        if miss:
            problems.append(f"{lang} #{t['id']}: нет полей {miss}")
        if not t.get('hints'):
            problems.append(f"{lang} #{t['id']}: пустые hints")
        res = check_code(t['solution'], t['check'])
        if not res.get('success'):
            problems.append(
                f"{lang} #{t['id']} ({t['title']}): проверка не прошла -> "
                f"{(res.get('stderr') or '')[:120]!r}")

print()
print('ПРОБЛЕМЫ:', len(problems))
for p in problems:
    print(' -', p)