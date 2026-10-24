# -*- coding: utf-8 -*-
"""Проверяет, что в каждой шпаргалке есть «для чего» и «где используется»."""
import io
import json
import os
import re
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TMP_DB = os.path.join(tempfile.gettempdir(), 'codigo_cheat_test.db')
if os.path.exists(TMP_DB):
    os.remove(TMP_DB)
os.environ['DATABASE_URL'] = 'sqlite:///' + TMP_DB.replace('\\', '/')

from app import app  # noqa: E402
from utils.language_manager import LANGUAGES  # noqa: E402

app.config['TESTING'] = True
client = app.test_client()

problems = []
checks = [0]


def ok(cond, message):
    checks[0] += 1
    if not cond:
        problems.append(message)
        print('  ПРОБЛЕМА:', message)


# --- данные --------------------------------------------------------------
for code in LANGUAGES:
    path = os.path.join(BASE, 'data', 'languages', code + '.json')
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    data = data.get(code, data)
    sheets = data.get('cheatsheets', [])
    ok(bool(sheets), 'у языка %s нет шпаргалок' % code)
    for sheet in sheets:
        title = sheet.get('title', '?')
        ok(bool(sheet.get('code')), '%s: %s — нет кода' % (code, title))
        why = (sheet.get('why') or '').strip()
        where = (sheet.get('where') or '').strip()
        ok(len(why) > 40,
           '%s: %s — короткое пояснение «для чего» (%d символов)'
           % (code, title, len(why)))
        ok(len(where) > 30,
           '%s: %s — короткое «где используется» (%d символов)'
           % (code, title, len(where)))
        ok(why != where, '%s: %s — одинаковые тексты' % (code, title))

# --- страница ------------------------------------------------------------
page = client.get('/cheat_sheet/python')
ok(page.status_code == 200, 'страница шпаргалок: HTTP %s' % page.status_code)
body = page.get_data(as_text=True)
ok('Для чего это нужно' in body, 'нет заголовка «Для чего это нужно»')
ok('Где это используется' in body, 'нет заголовка «Где это используется»')
ok('Обрати внимание' not in body, 'лишний блок «Обрати внимание»')
ok(body.count('cs-why') >= 10, 'блоков «для чего»: %d' % body.count('cs-why'))
ok(body.count('cs-where') >= 10,
   'блоков «где используется»: %d' % body.count('cs-where'))
ok('pre class="code-block"' in body, 'не отображается код в шпаргалке')

# --- все языки открываются ------------------------------------------------
for code in LANGUAGES:
    resp = client.get('/cheat_sheet/%s' % code)
    ok(resp.status_code == 200, 'шпаргалки %s: HTTP %s' % (code, resp.status_code))
    text = resp.get_data(as_text=True)
    ok('cs-why' in text, 'у языка %s нет блоков «для чего»' % code)

print()
print('Проверок: %d, проблем: %d' % (checks[0], len(problems)))
if problems:
    for item in problems:
        print('  - ' + item)
    sys.exit(1)
print('Шпаргалки заполнены везде')
