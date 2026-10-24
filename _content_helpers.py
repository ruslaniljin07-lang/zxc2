# -*- coding: utf-8 -*-
"""Хелперы для сборки учебного контента: задачи, уроки, модули, шпаргалки."""
import json
import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(BASE, 'data', 'languages')


def t(title, desc, diff, initial, check, hints, sol):
    """Создаёт задачу урока."""
    return {'id': 0, 'title': title, 'description': desc, 'difficulty': diff,
            'initial_code': initial, 'check': check, 'hints': hints,
            'solution': sol, 'examples': []}


def out(expected, mode='exact'):
    """Проверка по выводу (Python)."""
    return {'type': 'stdout', 'expected': expected, 'mode': mode}


def out_js(expected, mode='exact'):
    """Проверка по выводу (JavaScript, через Node)."""
    return {'type': 'stdout_js', 'expected': expected, 'mode': mode}


def req(*require, reject=()):
    """Проверка по ключевым конструкциям (Java / C++ / fallback JS)."""
    return {'type': 'contains', 'require': list(require), 'reject': list(reject)}


def q(question, options, correct, explain=''):
    """Вопрос мини-теста."""
    return {'question': question, 'options': options,
            'correct': correct, 'explain': explain}


def ex(code, explain=''):
    """Пример кода с пояснением."""
    return {'code': code, 'explain': explain}


def L(mod_id, title, desc, theory, examples, tasks, test, cheat, xp=15,
      difficulty='easy'):
    """Урок: теория + примеры + задачи + мини-тест + шпаргалка."""
    return {'id': 0, 'title': title, 'description': desc, 'theory': theory,
            'examples': examples, 'tasks': tasks, 'test': test,
            'cheatsheet': cheat, 'xp_reward': xp, 'difficulty': difficulty}


def M(mod_id, title, desc, lessons):
    """Новый модуль с уроками."""
    return {'id': mod_id, 'title': title, 'description': desc,
            'lessons': lessons}


def load_raw(code):
    p = os.path.join(D, code + '.json')
    with open(p, encoding='utf-8') as f:
        return json.load(f), p


def run_py(code):
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False,
                                     encoding='utf-8') as f:
        f.write(code)
        p = f.name
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    r = subprocess.run([sys.executable, p], capture_output=True, text=True,
                       encoding='utf-8', timeout=10, env=env)
    os.unlink(p)
    return r


def run_js(code):
    import shutil
    node = shutil.which('node')
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False,
                                     encoding='utf-8') as f:
        f.write(code)
        p = f.name
    r = subprocess.run([node, p], capture_output=True, text=True,
                       encoding='utf-8', timeout=10)
    os.unlink(p)
    return r


def verify(lang, tasks):
    """Проверяет, что решения задач дают ожидаемый вывод."""
    errs = 0
    for tk in tasks:
        check = tk['check']
        sol = tk['solution']
        ctype = check.get('type')
        if ctype == 'stdout':
            r = run_py(sol)
            if r.returncode != 0 or norm(r.stdout) != norm(check['expected']):
                print(f'  [PY FAIL] {tk["title"]}')
                print('   stdout:', repr(r.stdout[:200]))
                print('   stderr:', repr(r.stderr[:300]))
                errs += 1
        elif ctype == 'stdout_js':
            r = run_js(sol)
            if r.returncode != 0 or norm(r.stdout) != norm(check['expected']):
                print(f'  [JS FAIL] {tk["title"]}')
                print('   stdout:', repr(r.stdout[:200]))
                print('   stderr:', repr(r.stderr[:300]))
                errs += 1
        elif ctype == 'contains':
            low = sol.lower()
            for req_str in check.get('require', []):
                if req_str.lower() not in low:
                    print(f'  [REQ MISS] {lang}: {tk["title"]} — {req_str!r}')
                    errs += 1
    return errs


def apply(code, new_modules, cheatsheets=None):
    """Добавляет новые модули/уроки в JSON языка и заменяет шпаргалки."""
    raw, path = load_raw(code)
    data = raw.get(code) if code in raw else raw

    existing_mods = {m['id']: m for m in data.get('modules', [])}
    max_lesson = max((l['id'] for m in data.get('modules', [])
                      for l in m.get('lessons', [])), default=0)
    max_task = max((tk['id'] for m in data.get('modules', [])
                    for l in m.get('lessons', [])
                    for tk in l.get('tasks', [])), default=0)

    lesson_id = max_lesson
    task_id = max_task
    for nm in new_modules:
        mid = nm['id']
        new_lessons = nm['lessons']
        for lsn in new_lessons:
            lesson_id += 1
            lsn['id'] = lesson_id
            for tk in lsn['tasks']:
                task_id += 1
                tk['id'] = task_id
        if mid in existing_mods:
            existing_mods[mid]['lessons'].extend(new_lessons)
        else:
            data['modules'].append({'id': mid, 'title': nm['title'],
                                    'description': nm['description'],
                                    'lessons': new_lessons})

    if cheatsheets is not None:
        data['cheatsheets'] = cheatsheets

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    print(f'  {code}: сохранено, уроки до #{lesson_id}, задач до #{task_id}')


def stats(code):
    raw, _ = load_raw(code)
    data = raw.get(code) if code in raw else raw
    lessons = sum(len(m.get('lessons', [])) for m in data.get('modules', []))
    tasks = sum(len(l.get('tasks', [])) for m in data.get('modules', [])
                for l in m.get('lessons', []))
    tests = sum(len(l.get('test', [])) for m in data.get('modules', [])
                for l in m.get('lessons', []))
    return lessons, tasks, tests, len(data.get('cheatsheets', []))
