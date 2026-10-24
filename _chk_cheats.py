# -*- coding: utf-8 -*-
"""Temp: проверка, что изменились только блоки cheatsheets."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
LANGS = ['python', 'javascript', 'java', 'cpp', 'go', 'csharp', 'typescript',
         'php', 'rust']
LF = bytes([10])
CRLF = bytes([13, 10])

problems = []
for lang in LANGS:
    cur_path = os.path.join(ROOT, 'data', 'languages', lang + '.json')
    old_path = os.path.join(ROOT, '_backup_lang', lang + '.json')
    with open(cur_path, encoding='utf-8') as f:
        cur = json.load(f)[lang]
    with open(old_path, encoding='utf-8') as f:
        old = json.load(f)[lang]

    for key in sorted(set(old) | set(cur)):
        if key == 'cheatsheets':
            continue
        if old.get(key) != cur.get(key):
            problems.append(f'{lang}: изменилось поле {key}')

    sheets = cur.get('cheatsheets') or []
    old_sheets = {c['title']: c for c in (old.get('cheatsheets') or [])}
    for card in sheets:
        if card['title'] in old_sheets and old_sheets[card['title']] != card:
            problems.append(f'{lang}/{card["title"]}: старая тема изменилась')
    lost = [t for t in old_sheets if t not in {c['title'] for c in sheets}]
    if lost:
        problems.append(f'{lang}: потеряны темы {lost}')
    titles = [c.get('title') for c in sheets]
    if len(set(titles)) != len(titles):
        problems.append(f'{lang}: дубли тем шпаргалок {titles}')
    for card in sheets:
        if sorted(card) != ['code', 'icon', 'note', 'title']:
            problems.append(f'{lang}/{card.get("title")}: поля {sorted(card)}')
        for field in ('icon', 'code', 'note', 'title'):
            if not (card.get(field) or '').strip():
                problems.append(f'{lang}/{card.get("title")}: пустое {field}')
    if len(sheets) != 10:
        problems.append(f'{lang}: шпаргалок {len(sheets)}, ожидалось 10')

    raw = open(cur_path, 'rb').read()
    old_raw = open(old_path, 'rb').read()
    indent = len(raw.decode('utf-8').splitlines()[1]) - len(
        raw.decode('utf-8').splitlines()[1].lstrip(' '))
    old_indent = len(old_raw.decode('utf-8').splitlines()[1]) - len(
        old_raw.decode('utf-8').splitlines()[1].lstrip(' '))
    if indent != old_indent:
        problems.append(f'{lang}: отступ {old_indent} -> {indent}')
    lf, crlf = raw.count(LF), raw.count(CRLF)
    old_lf, old_crlf = old_raw.count(LF), old_raw.count(CRLF)
    if lf != crlf or old_lf != old_crlf:
        problems.append(f'{lang}: переводы строк были {old_crlf}/{old_lf} '
                        f'(CRLF/LF), стали {crlf}/{lf}')
    print(f'{lang:11} тем {len(sheets):2}  отступ={indent}  '
          f'CRLF={crlf}  байт {len(old_raw)} -> {len(raw)}')

print()
print('ПРОБЛЕМЫ:', len(problems))
for p in problems:
    print(' -', p)
