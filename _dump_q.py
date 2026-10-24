# -*- coding: utf-8 -*-
"""Temp: выгрузка вопросов уроков там, где нет пояснения explain."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, '_questions.txt')
LANGS = ['python', 'javascript', 'java', 'cpp']

lines = []
total = 0
for lang in LANGS:
    with open(os.path.join(ROOT, 'data', 'languages', lang + '.json'),
              encoding='utf-8') as f:
        data = json.load(f)[lang]
    lines.append('=' * 72)
    lines.append(f'### {lang}')
    for module in data['modules']:
        for lesson in module['lessons']:
            for i, quest in enumerate(lesson.get('test') or [], 1):
                if (quest.get('explain') or '').strip():
                    continue
                total += 1
                opts = quest.get('options') or []
                correct = opts[quest['correct']] if 0 <= quest.get(
                    'correct', -1) < len(opts) else '?'
                lines.append(f"[{lang} / урок {lesson['id']} / q{i}] "
                             f"{quest['question']}")
                lines.append(f"    варианты: {' | '.join(opts)}")
                lines.append(f"    верный: {correct}")

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('вопросов без explain:', total, '->', OUT)
