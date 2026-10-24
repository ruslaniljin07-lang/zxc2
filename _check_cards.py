# -*- coding: utf-8 -*-
"""Проверяет, что карточка языка ведёт на страницу именно своего курса."""
import io
import os
import re
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TMP_DB = os.path.join(tempfile.gettempdir(), 'codigo_cards_check.db')
if os.path.exists(TMP_DB):
    os.remove(TMP_DB)
os.environ['DATABASE_URL'] = 'sqlite:///' + TMP_DB.replace('\\', '/')

from app import app  # noqa: E402
from utils.language_manager import LANGUAGES  # noqa: E402

app.config['TESTING'] = True
client = app.test_client()
TAG = re.compile(r'<[^>]+>')
SPACE = re.compile(r'\s+')

problems = []
checks = [0]


def ok(cond, message):
    checks[0] += 1
    if not cond:
        problems.append(message)
        print('  ПРОБЛЕМА:', message)


def clean(html):
    return SPACE.sub(' ', TAG.sub(' ', html)).strip()


# --- карточки на главной --------------------------------------------------
index = client.get('/').get_data(as_text=True)
print('=== карточки на главной ===')
for match in re.finditer(
        r'<div class="card h-100 language-card".*?'
        r'<a href="(/language/([a-z]+))"',
        index, re.S):
    card = match.group(0)
    title = re.search(r'card-title">(.*?)</h5>', card, re.S)
    desc = re.search(r'card-text[^"]*">(.*?)</p>', card, re.S)
    name = clean(title.group(1)) if title else '?'
    text = clean(desc.group(1))[:64] if desc else '?'
    code = match.group(2)
    print('%-11s %-12s %s' % (code, name, text))
    # название в интерфейсе не обязано совпадать с кодом из адреса:
    # C++ -> cpp, C# -> csharp
    alias = {'cpp': 'C++', 'csharp': 'C#'}.get(code, code)
    ok(name == alias or name.lower() in code.lower(),
       'карточка «%s» ведёт на другой язык «%s»' % (name, code))

print()
print('=== страницы курсов ===')
for code, info in LANGUAGES.items():
    page = client.get('/language/' + code).get_data(as_text=True)
    title = re.search(r'<h1[^>]*>(.*?)</h1>', page, re.S)
    heading = clean(title.group(1)) if title else '(нет h1)'
    print('%-11s -> %s' % (code, heading))
    ok(info['name'] in heading,
       'страница языка %s показывает «%s» вместо «%s»'
       % (code, heading, info['name']))

# --- самое важное: TS и JS не должны путаться ----------------------------
js_page = client.get('/language/javascript').get_data(as_text=True)
ts_page = client.get('/language/typescript').get_data(as_text=True)
ok('/language/typescript/' not in js_page,
   'на странице JS есть ссылки на курс TypeScript')
ok('/language/javascript/' not in ts_page,
   'на странице TS есть ссылки на курс JavaScript')

js_lessons = client.get('/lessons/javascript').get_data(as_text=True)
ts_lessons = client.get('/lessons/typescript').get_data(as_text=True)
ok('javascript' in js_lessons and 'typescript' in ts_lessons,
   'страница уроков не различает JS и TS')

print()
print('Проверок: %d, проблем: %d' % (checks[0], len(problems)))
if problems:
    for item in problems:
        print('  - ' + item)
    sys.exit(1)
print('Карточки и страницы языков корректны')
