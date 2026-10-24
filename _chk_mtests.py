# -*- coding: utf-8 -*-
"""Temp: сверка до/после добавления вопросов в тесты модулей."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
LF = bytes([10])
CRLF = bytes([13, 10])
LANGS = ['go', 'csharp', 'typescript', 'php', 'rust']

problems = []
for lang in LANGS:
    cur_path = os.path.join(ROOT, 'data', 'languages', lang + '.json')
    old_path = os.path.join(ROOT, '_backup_lang3', lang + '.json')
    cur = json.load(open(cur_path, encoding='utf-8'))[lang]
    old = json.load(open(old_path, encoding='utf-8'))[lang]

    counts = []
    for module_old, module_cur in zip(old['modules'], cur['modules']):
        old_q = (module_old.get('test') or {}).get('questions') or []
        new_q = (module_cur.get('test') or {}).get('questions') or []
        counts.append(f"{module_old['id']}:{len(old_q)}->{len(new_q)}")
        if len(new_q) != 5:
            problems.append(f'{lang} модуль {module_old["id"]}: вопросов '
                            f'{len(new_q)}')
        for i, quest in enumerate(new_q):
            opts = quest.get('options') or []
            if not (quest.get('question') or '').strip():
                problems.append(f'{lang} модуль {module_old["id"]} q{i + 1}: '
                                f'пустой вопрос')
            if len(opts) != 4 or len(set(opts)) != 4:
                problems.append(f'{lang} модуль {module_old["id"]} q{i + 1}: '
                                f'варианты {opts}')
            if not 0 <= quest.get('correct', -1) < len(opts):
                problems.append(f'{lang} модуль {module_old["id"]} q{i + 1}: '
                                f'correct={quest.get("correct")}')
            if not (quest.get('explain') or '').strip():
                problems.append(f'{lang} модуль {module_old["id"]} q{i + 1}: '
                                f'нет explain')
        for i, quest_old in enumerate(old_q):
            if new_q[i] != quest_old:
                problems.append(f'{lang} модуль {module_old["id"]} q{i + 1}: '
                                f'старый вопрос изменился')

    # всё остальное в файле должно совпадать
    def mask(data):
        copy = json.loads(json.dumps(data))
        for module in copy['modules']:
            if isinstance(module.get('test'), dict):
                module['test']['questions'] = '__masked__'
        return copy

    if mask(old) != mask(cur):
        problems.append(f'{lang}: изменилось что-то кроме вопросов тестов')

    raw = open(cur_path, 'rb').read()
    lf, crlf = raw.count(LF), raw.count(CRLF)
    indent = len(raw.decode('utf-8').splitlines()[1]) - len(
        raw.decode('utf-8').splitlines()[1].lstrip(' '))
    print(f'{lang:11} вопросы: {" ".join(counts)}  отступ={indent}  '
          f'CRLF={crlf}  байт {os.path.getsize(old_path)} -> {len(raw)}')

print()
print('ПРОБЛЕМЫ:', len(problems))
for line in problems:
    print(' -', line)
