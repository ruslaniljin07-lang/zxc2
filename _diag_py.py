# -*- coding: utf-8 -*-
"""Temp: диагностика python-уроков, где эталон не проходит проверку."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from utils.code_checker import check_code  # noqa: E402

with open(os.path.join(ROOT, 'data', 'languages', 'python.json'),
          encoding='utf-8') as f:
    data = json.load(f)['python']

for module in data['modules']:
    for lesson in module['lessons']:
        for num, task in enumerate(lesson.get('tasks') or [], 1):
            res = check_code(task['solution'], task['check'])
            if res.get('success'):
                continue
            print('=' * 72)
            print(f'УРОК {lesson["id"]} "{lesson["title"]}" задача {num}')
            print('check:', json.dumps(task['check'], ensure_ascii=False))
            print('solution:', repr(task['solution']))
            print('stderr:', res.get('stderr'))
