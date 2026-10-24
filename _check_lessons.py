# -*- coding: utf-8 -*-
"""Прогоняет все задачи уроков и банка для указанного языка.

Нужен после изменений в utils/code_checker.py: показывает, что эталоны
по-прежнему засчитываются после запуска кода в изоляции.
"""
import io
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LANGS = sys.argv[1:] or ['javascript']

from utils.code_checker import check_code  # noqa: E402
from utils.language_manager import (load_language, load_tasks)  # noqa: E402

total_ok = total_fail = 0
failures = []

for lang in LANGS:
    data = load_language(lang)
    if not data:
        print('%s: нет данных языка' % lang)
        continue
    print('=== %s ===' % lang)

    lesson_ok = lesson_fail = 0
    for module in data.get('modules', []):
        for lesson in module.get('lessons', []):
            for task in lesson.get('tasks', []):
                result = check_code(task.get('solution', ''),
                                    task.get('check'))
                if result.get('success'):
                    lesson_ok += 1
                else:
                    lesson_fail += 1
                    failures.append('урок %d, задача «%s»: %s'
                                    % (lesson.get('id', 0),
                                       task.get('title', '?'),
                                       (result.get('stderr') or '')[:110]))
    print('  уроки: %d ок, %d с ошибкой' % (lesson_ok, lesson_fail))

    bank_ok = bank_fail = 0
    for task in load_tasks(lang):
        result = check_code(task.get('solution', ''), task.get('check'))
        if result.get('success'):
            bank_ok += 1
        else:
            bank_fail += 1
            failures.append('банк, «%s»: %s'
                            % (task.get('title', '?'),
                               (result.get('stderr') or '')[:110]))
    print('  банк задач: %d ок, %d с ошибкой' % (bank_ok, bank_fail))

    total_ok += lesson_ok + bank_ok
    total_fail += lesson_fail + bank_fail

print()
for item in failures:
    print('  ! ' + item)
print()
print('Итого: %d ок, %d с ошибкой' % (total_ok, total_fail))
sys.exit(1 if total_fail else 0)
