# -*- coding: utf-8 -*-
"""Проверка читаемости бейджа прогресса модуля."""
import io
import os
import re
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TMP_DB = os.path.join(tempfile.gettempdir(), 'codigo_badge_test.db')
if os.path.exists(TMP_DB):
    os.remove(TMP_DB)
os.environ['DATABASE_URL'] = 'sqlite:///' + TMP_DB.replace('\\', '/')

from app import app, db  # noqa: E402
from utils.security import rate_limiter  # noqa: E402

app.config['TESTING'] = True
with app.app_context():
    db.create_all()

problems = []
checks = [0]


def ok(cond, message):
    checks[0] += 1
    if not cond:
        problems.append(message)
        print('  ПРОБЛЕМА:', message)


# --- стили на месте -------------------------------------------------------
css = open(os.path.join(BASE, 'static', 'style.css'), encoding='utf-8').read()
ok('.badge-mod' in css, 'нет класса .badge-mod в style.css')
ok('.badge-mod.is-done' in css, 'нет состояния is-done')
ok('.badge-mod.is-partial' in css, 'нет состояния is-partial')
ok(css.count('font-family: var(--mono)') > 0,
   'счётчик не переведён в моноширинный шрифт')

# версия CSS обновлена, иначе браузер отдаст старый файл из кэша
base = open(os.path.join(BASE, 'templates', 'base.html'),
            encoding='utf-8').read()
ok('?v=19' in base, 'в base.html не поднята версия style.css (нужна v=19)')

# --- разметка страницы ----------------------------------------------------
client = app.test_client()
html = client.get('/login').get_data(as_text=True)
token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)

rate_limiter._hits.clear()
client.post('/register', data={
    'username': 'badgeuser', 'email': 'badge@test.ru',
    'password': 'CodigoTest9', 'confirm': 'CodigoTest9',
    'csrf_token': token})
rate_limiter._hits.clear()
client.post('/login', data={'username': 'badgeuser',
                            'password': 'CodigoTest9',
                            'csrf_token': token})

page = client.get('/language/python').get_data(as_text=True)
badges = re.findall(r'<span class="badge badge-mod[^"]*">\s*([^<]+?)\s*</span>',
                     page)
ok(bool(badges), 'на странице курса нет бейджей badge-mod')
ok(all(re.fullmatch(r'\d+/\d+', b.strip()) for b in badges),
   'бейдж не в формате «1/3»: %r' % badges[:3])
ok('bg-primary' not in page,
   'остался старый нечитаемый bg-primary в бейдже')

# первый модуль ещё не начат -> должен быть 0/N
ok(any(b.strip().startswith('0/') for b in badges),
   'у неза��онченного модуля нет счётчика 0/N: %r' % badges[:3])

# пустой прогресс-бар теперь тоже рисуется
ok(page.count('class="progress mb-3"') >= len(badges),
   'прогресс-бар показан не для всех модулей')

# --- все 9 языков ---------------------------------------------------------
from utils.language_manager import LANGUAGES  # noqa: E402

for code in LANGUAGES:
    resp = client.get('/language/' + code)
    ok(resp.status_code == 200, 'страница языка %s: HTTP %s'
       % (code, resp.status_code))
    body = resp.get_data(as_text=True)
    found = re.findall(r'<span class="badge badge-mod[^"]*">\s*([^<]+?)\s*</span>',
                       body)
    ok(bool(found), 'у языка %s нет бейджей' % code)
    ok(all(re.fullmatch(r'\d+/\d+', b.strip()) for b in found),
       'у языка %s бейджи неверного формата: %r' % (code, found[:3]))

print()
print('Проверок: %d, проблем: %d' % (checks[0], len(problems)))
if problems:
    for item in problems:
        print('  - ' + item)
    sys.exit(1)
print('Бейджи прогресса читаемы')
