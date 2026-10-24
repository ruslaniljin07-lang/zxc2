# -*- coding: utf-8 -*-
"""Temp: вопросы уроков без explain в go/csharp/typescript/php/rust."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, '_questions2.txt')

lines = []
total = 0
for lang in ['go', 'csharp', 'typescript', 'php', 'rust']:
    with open(os.path.join(ROOT, 'data', 'languages', lang + '.json'),
              encoding='utf-8') as f:
        data = json.load(f)[lang]
    count = 0
    lines.append('=' * 72)
    lines.append(f'### {lang}')
    for module in data['modules']:
        for lesson in module['lessons']:
            for i, quest in enumerate(lesson.get('test') or [], 1):
                if (quest.get('explain') or '').strip():
                    continue
                count += 1
                total += 1
                opts = quest.get('options') or []
                correct = opts[quest['correct']]
                lines.append(f"[{lang} / урок {lesson['id']} / q{i}] "
                             f"{quest['question']}")
                lines.append(f"    варианты: {' | '.join(opts)}")
                lines.append(f"    верный: {correct}")
    print(f'{lang:11} без explain: {count}')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('всего:', total, '->', OUT)
