# -*- coding: utf-8 -*-
"""Temp: сверка до/после добавления explain к вопросам уроков."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
LF = bytes([10])
CRLF = bytes([13, 10])
LANGS = ['python', 'javascript', 'java', 'cpp']

problems = []
for lang in LANGS:
    cur_path = os.path.join(ROOT, 'data', 'languages', lang + '.json')
    old_path = os.path.join(ROOT, '_backup_lang2', lang + '.json')
    cur = json.load(open(cur_path, encoding='utf-8'))[lang]
    old = json.load(open(old_path, encoding='utf-8'))[lang]

    added, changed = 0, 0
    old_lessons = {}
    for module in old['modules']:
        for lesson in module['lessons']:
            old_lessons[lesson['id']] = lesson['test']
    for module in cur['modules']:
        for lesson in module['lessons']:
            was = old_lessons[lesson['id']]
            for i, quest in enumerate(lesson['test']):
                before = dict(was[i])
                after = dict(quest)
                if before == after:
                    continue
                new_keys = set(after) - set(before)
                if new_keys == {'explain'} and all(
                        before[k] == after[k] for k in before):
                    added += 1
                else:
                    changed += 1
                    problems.append(f'{lang} урок {lesson["id"]} вопрос '
                                    f'{i + 1}: изменилось {sorted(new_keys)}')

    # остальные части файла не тронуты
    for key in sorted(set(old) | set(cur)):
        if key == 'modules':
            continue
        if old.get(key) != cur.get(key):
            problems.append(f'{lang}: изменилось поле {key}')
    for module_old, module_cur in zip(old['modules'], cur['modules']):
        for field in ('id', 'title', 'description', 'test'):
            if module_old.get(field) != module_cur.get(field):
                problems.append(f'{lang} модуль {module_old["id"]}: '
                                f'изменилось поле {field}')
        for lesson_old, lesson_cur in zip(module_old['lessons'],
                                          module_cur['lessons']):
            for field in ('id', 'title', 'description', 'theory', 'examples',
                          'tasks', 'cheatsheet', 'xp_reward', 'difficulty'):
                if lesson_old.get(field) != lesson_cur.get(field):
                    problems.append(f'{lang} урок {lesson_old["id"]}: '
                                    f'изменилось поле {field}')

    raw = open(cur_path, 'rb').read()
    old_raw = open(old_path, 'rb').read()
    lf, crlf = raw.count(LF), raw.count(CRLF)
    indent = len(raw.decode('utf-8').splitlines()[1]) - len(
        raw.decode('utf-8').splitlines()[1].lstrip(' '))
    print(f'{lang:11} explain добавлено: {added:2}  изменилось иначе: '
          f'{changed}  отступ={indent}  CRLF={crlf}  байт {len(old_raw)} -> '
          f'{len(raw)}')

print()
print('ПРОБЛЕМЫ:', len(problems))
for line in problems:
    print(' -', line)
