# -*- coding: utf-8 -*-
"""Проверяет страницу урока SQL: примеры, боковую таблицу, подсветку."""
import io
import os
import re
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TMP_DB = os.path.join(tempfile.gettempdir(), 'codigo_sql_ui.db')
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


client = app.test_client()
html = client.get('/login').get_data(as_text=True)
token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
rate_limiter._hits.clear()
client.post('/register', data={
    'username': 'sqlui', 'email': 'sqlui@test.ru', 'password': 'CodigoTest9',
    'confirm': 'CodigoTest9', 'csrf_token': token})
rate_limiter._hits.clear()
client.post('/login', data={'username': 'sqlui', 'password': 'CodigoTest9',
                            'csrf_token': token})

# --- урок SQL -------------------------------------------------------------
page = client.get('/lesson/sql/1')
ok(page.status_code == 200, 'урок SQL: HTTP %s' % page.status_code)
body = page.get_data(as_text=True)

ok('example-label' in body, 'блок примеров кода не найден')
labels = re.findall(r'example-label[^>]*>\s*([^<]+)', body)
ok(bool(labels), 'нет подписей примеров')
ok(any(len(t.strip()) > 3 for t in labels),
   'подпись примера пустая: %r' % labels[:2])
ok('class="code-block' in body, 'нет блока с кодом примера')

ok('db-side-card' in body, 'нет боковой панели с таблицами')
ok(body.count('db-side-table') >= 3,
   'показано таблиц: %d (ожидается 3)' % body.count('db-side-table'))
rows = body.count('<tr>')
ok(rows > 30, 'в таблицах мало строк: %d' % rows)
for column in ('products', 'customers', 'orders'):
    ok(column in body, 'в панели нет таблицы %s' % column)
for value in ('Ноутбук', 'Анна', '75000'):
    ok(value in body, 'в панели нет значения «%s»' % value)

ok('data-codeeditor="sql"' in body, 'редактор не настроен на SQL')

# --- теория и примеры есть во всех уроках SQL ----------------------------
from utils.language_manager import get_flat_lessons  # noqa: E402

lessons = get_flat_lessons('sql')
ok(len(lessons) == 12, 'уроков SQL: %d' % len(lessons))
for lesson in lessons:
    data = client.get('/lesson/sql/%d' % lesson['id']).get_data(as_text=True)
    ok('db-side-card' in data,
       'в уроке %d нет таблицы БД' % lesson['id'])
    ok('example-label' in data,
       'в уроке %d нет примеров кода' % lesson['id'])

# --- у других языков панели быть не должно -------------------------------
for code in ('python', 'javascript'):
    other = client.get('/lesson/%s/1' % code).get_data(as_text=True)
    ok('db-side-card' not in other,
       'у языка %s не должно быть панели БД' % code)
    ok('example-label' in other, 'у языка %s пропали примеры' % code)

print()
print('Проверок: %d, проблем: %d' % (checks[0], len(problems)))
if problems:
    for item in problems:
        print('  - ' + item)
    sys.exit(1)
print('Страница урока SQL корректна')
