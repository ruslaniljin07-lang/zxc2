# -*- coding: utf-8 -*-
"""Temp: проверка целостности данных курсов и банков задач."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
LANGS = ['python', 'javascript', 'java', 'cpp', 'go', 'csharp', 'typescript',
         'php', 'rust']
LESSON_KEYS = {'id', 'title', 'description', 'theory', 'examples', 'tasks',
               'test', 'cheatsheet', 'xp_reward', 'difficulty'}
TASK_KEYS = {'id', 'title', 'description', 'difficulty', 'initial_code',
             'check', 'hints', 'solution'}
BANK_KEYS = {'id', 'title', 'topic', 'difficulty', 'xp', 'description',
             'initial_code', 'check', 'hints', 'solution'}

problems = []
stats = []


def check_question(where, quest, need_explain=True):
    """Вопрос теста: текст, варианты и верный индекс."""
    opts = quest.get('options') or []
    if not (quest.get('question') or '').strip():
        problems.append(f'{where}: пустой текст вопроса')
    if len(opts) < 2:
        problems.append(f'{where}: вариантов {len(opts)}')
    if not isinstance(quest.get('correct'), int) or \
            not 0 <= quest['correct'] < len(opts):
        problems.append(f'{where}: correct={quest.get("correct")} при '
                        f'{len(opts)} вариантах')
    if len(set(opts)) != len(opts):
        problems.append(f'{where}: повторяющиеся варианты')
    if need_explain and not (quest.get('explain') or '').strip():
        problems.append(f'{where}: нет пояснения explain')


def check_task(where, task, keys):
    """Задание урока или банка задач."""
    missing = keys - set(task)
    if missing:
        problems.append(f'{where}: нет полей {sorted(missing)}')
    check = task.get('check') or {}
    if not check.get('type'):
        problems.append(f'{where}: check без type')
    if check.get('type') == 'contains':
        if not check.get('require'):
            problems.append(f'{where}: contains без require')
    elif not (check.get('expected') or check.get('test_code')):
        problems.append(f'{where}: нет expected/test_code')
    if not (task.get('hints') or []):
        problems.append(f'{where}: нет подсказок')
    if not (task.get('solution') or '').strip():
        problems.append(f'{where}: нет эталонного решения')
    if task.get('difficulty') not in ('easy', 'medium', 'hard'):
        problems.append(f'{where}: difficulty={task.get("difficulty")!r}')


for lang in LANGS:
    with open(os.path.join(ROOT, 'data', 'languages', lang + '.json'),
              encoding='utf-8') as f:
        data = json.load(f)[lang]
    with open(os.path.join(ROOT, 'data', 'tasks', lang + '.json'),
              encoding='utf-8') as f:
        bank = json.load(f)['tasks']

    module_ids = [m['id'] for m in data['modules']]
    if len(set(module_ids)) != len(module_ids):
        problems.append(f'{lang}: повторяющиеся id модулей {module_ids}')
    if module_ids != sorted(module_ids):
        problems.append(f'{lang}: модули не по порядку {module_ids}')

    lesson_ids = []
    for module in data['modules']:
        if not (module.get('title') or '').strip():
            problems.append(f'{lang} модуль {module["id"]}: пустой заголовок')
        if not (module.get('description') or '').strip():
            problems.append(f'{lang} модуль {module["id"]}: пустое описание')
        questions = (module.get('test') or {}).get('questions') or []
        if len(questions) < 5:
            problems.append(f'{lang} модуль {module["id"]}: вопросов '
                            f'{len(questions)}')
        for i, quest in enumerate(questions, 1):
            # explain в тестах модулей интерфейс не показывает
            check_question(f'{lang} модуль {module["id"]} вопрос {i}', quest,
                           need_explain=False)
        for lesson in module['lessons']:
            lesson_ids.append(lesson['id'])
            where = f'{lang} урок {lesson["id"]}'
            missing = LESSON_KEYS - set(lesson)
            if missing:
                problems.append(f'{where}: нет полей {sorted(missing)}')
            if len(lesson.get('theory') or []) < 3:
                problems.append(f'{where}: теории {len(lesson["theory"])}')
            if not (lesson.get('examples') or []):
                problems.append(f'{where}: нет примеров')
            for i, example in enumerate(lesson['examples'], 1):
                if not (example.get('code') or '').strip():
                    problems.append(f'{where} пример {i}: нет кода')
                if not (example.get('explanation')
                        or example.get('explain')):
                    problems.append(f'{where} пример {i}: нет пояснения')
            if not (lesson.get('cheatsheet') or '').strip():
                problems.append(f'{where}: нет мини-шпаргалки')
            if not isinstance(lesson.get('xp_reward'), int) \
                    or lesson['xp_reward'] <= 0:
                problems.append(f'{where}: xp_reward={lesson.get("xp_reward")}')
            for i, task in enumerate(lesson.get('tasks') or [], 1):
                check_task(f'{where} задача {i}', task, TASK_KEYS)
            for i, quest in enumerate(lesson.get('test') or [], 1):
                check_question(f'{where} вопрос {i}', quest)

    if len(set(lesson_ids)) != len(lesson_ids):
        problems.append(f'{lang}: повторяющиеся id уроков')
    if lesson_ids != sorted(lesson_ids):
        problems.append(f'{lang}: уроки не по порядку {lesson_ids}')

    for i, quest in enumerate(data.get('entrance_test') or [], 1):
        # входной тест на странице тоже без пояснений
        check_question(f'{lang} входной тест вопрос {i}', quest,
                       need_explain=False)

    for i, card in enumerate(data.get('cheatsheets') or [], 1):
        if not (card.get('icon') or '').strip():
            problems.append(f'{lang} шпаргалка {i}: нет иконки')

    bank_ids = [t['id'] for t in bank]
    if len(set(bank_ids)) != len(bank_ids):
        problems.append(f'{lang}: повторяющиеся id задач банка')
    if bank_ids != sorted(bank_ids):
        problems.append(f'{lang}: задачи банка не по порядку')
    for task in bank:
        check_task(f'{lang} банк #{task["id"]}', task, BANK_KEYS)

    stats.append((lang, len(data['modules']), len(lesson_ids), len(bank),
                  len(data.get('entrance_test') or []),
                  len(data['cheatsheets'])))

print('язык        модулей уроков задач_банка входных_тестов шпаргалок')
for lang, mods, lessons, bank, entrance, cheats in stats:
    print(f'{lang:11} {mods:7} {lessons:6} {bank:11} {entrance:14} {cheats:9}')
print()
print('ПРОБЛЕМ:', len(problems))
for line in problems:
    print(' -', line)
