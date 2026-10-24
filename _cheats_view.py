# -*- coding: utf-8 -*-
"""Temp: просмотр шпаргалок по всем языкам."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
LANGS = ['python', 'javascript', 'java', 'cpp', 'go', 'csharp', 'typescript',
         'php', 'rust']

for lang in LANGS:
    with open(os.path.join(ROOT, 'data', 'languages', lang + '.json'),
              encoding='utf-8') as f:
        data = json.load(f)[lang]
    print('=' * 70)
    print(lang, '| шпаргалок:', len(data['cheatsheets']))
    for i, c in enumerate(data['cheatsheets'], 1):
        print(f"  {i}. keys={sorted(c.keys())} icon={c.get('icon')!r} "
              f"title={c.get('title')!r}")
        print(f"     note={str(c.get('note'))[:100]!r}")
        print(f"     code={c.get('code', '')[:200]!r}")
