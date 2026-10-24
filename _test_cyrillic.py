# -*- coding: utf-8 -*-
"""Проверка, что кириллические имена пользователей принимаются."""
import io
import os
import re
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TMP_DB = os.path.join(tempfile.gettempdir(), 'codigo_cyrillic_test.db')
if os.path.exists(TMP_DB):
    os.remove(TMP_DB)
os.environ['DATABASE_URL'] = 'sqlite:///' + TMP_DB.replace('\\', '/')

from app import app, db  # noqa: E402
from utils.security import (validate_username, normalize_username,  # noqa
                            rate_limiter)

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


# --- проверка самой функции ------------------------------------------------
for name in ['Иван', 'Иван Петров', 'Аня-2', 'ivan_petrov', 'Ёжик',
             'Мария_Иванова', 'Пётр.В']:
    valid, _ = validate_username(normalize_username(name))
    ok(valid, 'имя не принято: %r' % name)

for name in ['ab', 'Ёж', '<script>alert(1)</script>', 'a' * 40,
             'name$here', 'drop;table', "o'brien"]:
    valid, _ = validate_username(normalize_username(name))
    ok(not valid, 'имя wrongly принято: %r' % name)

ok(normalize_username('  Иван   Петров  ') == 'Иван Петров',
   'normalize_username не убирает лишние пробелы')

# --- проверка формы регистрации -------------------------------------------
client = app.test_client()
html = client.get('/register').get_data(as_text=True)
token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
ok('3–30 символов' in html, 'в форме нет подсказки о формате имени')

NAMES = [('Иван Петров', 'ivan@test.ru'), ('Анна', 'anna@test.ru'),
         ('Ёжкин', 'ezh@test.ru'), ('Мария_Иванова', 'maria@test.ru')]

for name, email in NAMES:
    # сбрасываем лимит регистраций: тест делает больше 5 попыток подряд
    rate_limiter._hits.clear()
    resp = client.post('/register', data={
        'username': name, 'email': email, 'password': 'CodigoTest9',
        'confirm': 'CodigoTest9', 'csrf_token': token})
    ok(resp.status_code == 302,
       'регистрация «%s» не прошла (HTTP %d)' % (name, resp.status_code))

# --- вход с лишними пробелами ---------------------------------------------
rate_limiter._hits.clear()
resp = client.post('/login', data={'username': '  Иван   Петров ',
                                   'password': 'CodigoTest9',
                                   'csrf_token': token})
ok(b'location' in resp.headers or resp.status_code == 302,
   'вход с лишними пробелами не сработал (HTTP %d)' % resp.status_code)

# --- имя отображается без поломок ------------------------------------------
resp = client.get('/dashboard')
ok(resp.status_code == 200, 'дашборд не открылся')

# --- безопасность: спецсимволы по-прежнему запрещены ------------------------
rate_limiter._hits.clear()
resp = client.post('/register', data={
    'username': '<script>alert(1)</script>', 'email': 'xss@test.ru',
    'password': 'CodigoTest9', 'confirm': 'CodigoTest9',
    'csrf_token': token})
# 200 означает, что форма перерисована, то есть имя отклонено (302 был бы
# при успешной регистрации)
ok(resp.status_code == 200, 'имя с HTML-тегом принято — это дыра')
# Имя не должно попасть в страницу вообще: форма перерисовывается
# пустой, а пользователь видит только текст ошибки. Так безопаснее, чем
# отражать введённое значение обратно.
ok('<script>alert(1)</script>' not in resp.get_data(as_text=True),
   'имя с HTML-тегом отражено в странице')
ok('alert(1)' not in resp.get_data(as_text=True),
   'введённое имя отражено в странице')
ok('Имя: 3-30 символов' in resp.get_data(as_text=True),
   'нет сообщения об ошибке имени')

print()
print('Проверок: %d, проблем: %d' % (checks[0], len(problems)))
if problems:
    for item in problems:
        print('  - ' + item)
    sys.exit(1)
print('Кириллические имена работают')
