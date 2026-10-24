# -*- coding: utf-8 -*-
"""Temp: полная проверка платформы по всем 9 языкам (Flask test client)."""
import io
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class _Tee(io.TextIOBase):
    """Пишем отчёт и в консоль, и в файл (в файле — всегда UTF-8)."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
        return len(text)

    def flush(self):
        for stream in self.streams:
            stream.flush()


sys.stdout = _Tee(sys.stdout, open(os.path.join(BASE, '_e2e_all_out.txt'),
                                   'w', encoding='utf-8'))

inst = os.path.join(BASE, 'instance')
if os.path.isdir(inst):
    for f in os.listdir(inst):
        try:
            os.remove(os.path.join(inst, f))
        except OSError:
            pass

from app import app, db  # noqa: E402
from utils.language_manager import (load_language, load_tasks,  # noqa: E402
                                    LANGUAGES)
from utils.code_checker import check_code  # noqa: E402

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
with app.app_context():
    db.create_all()

client = app.test_client()
LANGS = list(LANGUAGES)

problems = []
checks = [0]


def ok(cond, message):
    checks[0] += 1
    if not cond:
        problems.append(message)
    return cond


def get(url, code=200):
    r = client.get(url)
    ok(r.status_code == code, f'GET {url} -> {r.status_code}, ждали {code}')
    return r


print('=' * 72)
print('1. Публичные страницы')
print('=' * 72)
for url in ['/', '/login', '/register', '/leaderboard', '/cheat_sheet']:
    r = get(url)
    print(f'  {url:24} {r.status_code}  {len(r.data):6} байт')

print()
print('=' * 72)
print('2. Регистрация и вход')
print('=' * 72)
r = client.post('/register', data={
    'username': 'tester', 'email': 'tester@example.com',
    'password': 'CodigoTest9', 'confirm': 'CodigoTest9'}, follow_redirects=True)
print('  POST /register', r.status_code)
r = client.post('/login', data={'username': 'tester', 'password': 'CodigoTest9'},
                follow_redirects=True)
print('  POST /login   ', r.status_code)
ok(r.status_code == 200, 'вход не удался')

print()
print('=' * 72)
print('3. Шпаргалки: 10 тем в каждой из 9 колонок')
print('=' * 72)
r = get('/cheat_sheet')
html = r.data.decode('utf-8')
ok(html.count('cs-lang-btn') >= 9, 'на странице не все языки')
ok('10 тем' in html, 'нет подписи «10 тем»')
for lang in LANGS:
    r = get(f'/cheat_sheet/{lang}')
    page = r.data.decode('utf-8')
    sheets = load_language(lang).get('cheatsheets', [])
    ok(len(sheets) == 10, f'{lang}: тем {len(sheets)}')
    for card in sheets:
        ok(card['title'] in page, f'{lang}: тема «{card["title"]}» не выведена')
    print(f'  /cheat_sheet/{lang:11} тем: {len(sheets)}')

print()
print('=' * 72)
print('4. Курс, уроки, тесты модулей, банк задач')
print('=' * 72)
for lang in LANGS:
    data = load_language(lang)
    get(f'/language/{lang}')
    get(f'/lessons/{lang}')
    get(f'/test/{lang}')
    tasks = load_tasks(lang)
    r = get(f'/language/{lang}/tasks')
    page = r.data.decode('utf-8')
    for t in tasks:
        ok(f'/language/{lang}/tasks/{t["id"]}' in page,
           f'{lang}: задача #{t["id"]} не показана в списке')
    lessons = [l for m in data['modules'] for l in m.get('lessons', [])]
    for lesson in lessons:
        get(f'/lesson/{lang}/{lesson["id"]}')
    for module in data['modules']:
        qs = (module.get('test') or {}).get('questions') or []
        if qs:
            get(f'/module_test/{lang}/{module["id"]}')
    print(f'  {lang:11} уроков {len(lessons):2}, задач в банке {len(tasks):2}, '
          f'шпаргалок {len(data["cheatsheets"]):2}')

print()
print('=' * 72)
print('5. Решения: уроки (AJAX), банк задач, тесты')
print('=' * 72)
for lang in LANGS:
    data = load_language(lang)
    solved_lessons = 0
    failed = []
    for module in data['modules']:
        for lesson in module.get('lessons', []):
            for num, task in enumerate(lesson.get('tasks') or [], 1):
                res = check_code(task['solution'], task['check'])
                if res.get('success'):
                    solved_lessons += 1
                else:
                    failed.append(f'{lang} урок {lesson["id"]} '
                                  f'задача {num}: '
                                  f'{(res.get("stderr") or "")[:110]}')
                r = client.post(f'/lesson/{lang}/{lesson["id"]}',
                                data={'code': task['solution'],
                                      'task_num': num})
                ok(r.is_json, f'{lang}: урок {lesson["id"]} вернул не JSON')
                if r.is_json:
                    ok(r.get_json().get('success'),
                       f'{lang}: эталон не прошёл на уроке {lesson["id"]}')
        qs = (module.get('test') or {}).get('questions') or []
        if qs:
            form = {f'q{i}': str(q.get('correct', 0))
                    for i, q in enumerate(qs, 1)}
            r = client.post(f'/module_test/{lang}/{module["id"]}', data=form)
            ok(r.status_code == 302,
               f'{lang}: тест модуля {module["id"]} -> {r.status_code}')

    solved_bank = 0
    for task in load_tasks(lang):
        res = check_code(task['solution'], task['check'])
        if res.get('success'):
            solved_bank += 1
        else:
            failed.append(f'{lang} банк #{task["id"]}: '
                          f'{(res.get("stderr") or "")[:110]}')
        r = client.post(f'/language/{lang}/tasks/{task["id"]}',
                        data={'code': task['solution']})
        ok(r.is_json and r.get_json().get('success'),
           f'{lang}: решение задачи #{task["id"]} не принято')

    qs = data.get('entrance_test') or []
    form = {f'q{i}': str(q.get('correct', 0)) for i, q in enumerate(qs, 1)}
    r = client.post(f'/test/{lang}', data=form)
    ok(r.status_code == 302, f'{lang}: входной тест -> {r.status_code}')

    print(f'  {lang:11} эталонов уроков ок: {solved_lessons}, '
          f'банк ок: {solved_bank}/{len(load_tasks(lang))}')
    for line in failed:
        problems.append(line)

print()
print('=' * 72)
print('6. Песочница и личные страницы')
print('=' * 72)
r = client.post('/sandbox', json={'code': "print('привет')"})
ok(r.is_json, 'песочница вернула не JSON')
print('  POST /sandbox ->', r.status_code, r.get_json())
for url in ['/dashboard', '/profile', '/leaderboard']:
    r = get(url)
    print(f'  {url:14} {r.status_code}  {len(r.data):6} байт')

print()
print('=' * 72)
print(f'ПРОВЕРОК: {checks[0]}   ПРОБЛЕМ: {len(problems)}')
print('=' * 72)
for p in problems:
    print(' -', p)
