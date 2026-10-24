# -*- coding: utf-8 -*-
"""Temp: модульные тесты новых курсов (go/csharp/typescript/php/rust)."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))

for lang in ['go', 'csharp', 'typescript', 'php', 'rust']:
    with open(os.path.join(ROOT, 'data', 'languages', lang + '.json'),
              encoding='utf-8') as f:
        data = json.load(f)[lang]
    print('=' * 72)
    print('###', lang)
    for module in data['modules']:
        test = module.get('test') or {}
        print(f"  модуль {module['id']} «{module['title']}» — "
              f"ключи теста: {sorted(test.keys())}")
        for i, quest in enumerate(test.get('questions') or [], 1):
            print(f"    q{i}: {quest['question']}")
            print(f"        варианты: {' | '.join(quest['options'])}")
            print(f"        верный: {quest['options'][quest['correct']]}")
            print(f"        explain: {quest.get('explain')}")
