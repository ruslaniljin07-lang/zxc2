# -*- coding: utf-8 -*-
"""Проверка песочницы: все 9 языков, страница, запуск, ошибки.

Использует временную sqlite-базу (DATABASE_URL), рабочие данные не трогает.
"""
import io
import json
import os
import sys
import tempfile
import html as html_lib

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

_REPORT = open(os.path.join(BASE, '_test_sandbox_out.txt'), 'w',
               encoding='utf-8')


class _Tee(io.TextIOBase):
    """Пишем и в консоль, и в файл (в файле всегда UTF-8)."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
        return len(text)

    def flush(self):
        for stream in self.streams:
            stream.flush()


sys.stdout = _Tee(sys.stdout, _REPORT)

TMP_DB = os.path.join(tempfile.gettempdir(), 'codigo_sandbox_test.db')
if os.path.exists(TMP_DB):
    os.remove(TMP_DB)
os.environ['DATABASE_URL'] = 'sqlite:///' + TMP_DB.replace('\\', '/')

from app import app, db  # noqa: E402
from utils.language_manager import (LANGUAGES,  # noqa: E402
                                    get_sandbox_example,
                                    get_flat_lessons, load_tasks)
from utils.code_checker import sandbox_status  # noqa: E402

_flat_lessons = get_flat_lessons
_tasks = load_tasks

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

problems = []
checks = [0]


def ok(cond, message):
    checks[0] += 1
    if not cond:
        problems.append(message)
        print('  ПРОБЛЕМА:', message)
    return cond


with app.app_context():
    db.create_all()

client = app.test_client()
client.post('/register', data={'username': 'sandboxer',
                               'email': 'sandbox@example.com',
                               'password': 'CodigoTest9',
                               'confirm': 'CodigoTest9'},
            follow_redirects=True)
r = client.post('/login', data={'username': 'sandboxer',
                                'password': 'CodigoTest9'},
                follow_redirects=True)
ok(r.status_code == 200, 'логин: %s' % r.status_code)

status = sandbox_status()
langs = list(LANGUAGES)
print('Языков в песочнице:', len(langs))
print('Есть тулчейн:', ', '.join(k for k, v in status.items() if v) or 'нет')
print('Нет тулчейна:', ', '.join(k for k, v in status.items() if not v) or 'нет')
print()


# --- 1. страницы песочницы по каждому языку -------------------------------
print('[1] GET /sandbox/<lang> — страница на каждый язык')
for lang in langs:
    example = get_sandbox_example(lang)
    r = client.get('/sandbox/' + lang)
    html = r.get_data(as_text=True)
    ok(r.status_code == 200, 'GET /sandbox/%s: %s' % (lang, r.status_code))
    ok('data-codeeditor="%s"' % lang in html,
       '/sandbox/%s: нет data-codeeditor' % lang)
    ok(example['file'] in html, '/sandbox/%s: нет имени файла %s'
       % (lang, example['file']))
    ok('var LANG = "%s"' % lang in html or "var LANG = '%s'" % lang in html,
       '/sandbox/%s: язык не передан в JS' % lang)
    ok('data-sandbox-lang="%s"' % lang in html,
       '/sandbox/%s: нет пункта в переключателе' % lang)
    ok(example['starter'].splitlines()[0] in html_lib.unescape(html),
       '/sandbox/%s: нет стартового примера' % lang)
    ok(('тулчейн найден' if status[lang] else 'тулчейн не найден') in html,
       '/sandbox/%s: не показан статус тулчейна' % lang)
    ok('id="runSandbox"' in html and 'id="resetSandbox"' in html,
       '/sandbox/%s: нет кнопок запуска/сброса' % lang)
    if not status[lang]:
        ok('сейчас недоступен' in html,
           '/sandbox/%s: нет предупреждения про отсутствующий тулчейн' % lang)
        ok(example['hint'] in html,
           '/sandbox/%s: нет подсказки, как поставить тулчейн' % lang)

r = client.get('/sandbox')
ok(r.status_code == 200 and 'data-codeeditor="python"' in
   r.get_data(as_text=True), 'GET /sandbox: должен открываться как python')
r = client.get('/sandbox/cobol')
ok(r.status_code == 302, 'GET /sandbox/cobol: ждали редирект, получили %s'
   % r.status_code)

# --- 2. запуск кода на каждом языке ---------------------------------------
print('[2] POST /sandbox — запуск кода на каждом языке')
for lang in langs:
    example = get_sandbox_example(lang)
    r = client.post('/sandbox', json={'code': example['starter'],
                                      'lang': lang})
    ok(r.status_code == 200, 'POST %s: %s' % (lang, r.status_code))
    data = r.get_json() or {}
    ok('success' in data and 'stdout' in data and 'stderr' in data,
       'POST %s: нет ключей ответа' % lang)
    ok(data.get('lang') == lang, 'POST %s: вернулся другой язык' % lang)
    if status[lang]:
        ok(data.get('success') is True,
           'POST %s: пример не запустился: %s'
           % (lang, (data.get('stderr') or '')[:200]))
        out = data.get('stdout') or ''
        if lang == 'sql':
            # SQL печатает таблицу, а не приветствие
            ok(out.strip() and ('|' in out),
               'POST %s: пустая таблица: %r' % (lang, out[:80]))
        else:
            ok('Привет' in out or 'Hello' in out,
               'POST %s: странный вывод: %r' % (lang, out[:80]))
    else:
        ok(data.get('no_toolchain') is True,
           'POST %s: нет флага no_toolchain' % lang)
        ok('тулчейн' in (data.get('stderr') or ''),
           'POST %s: нет подсказки про тулчейн' % lang)
        ok(data.get('success') is False,
           'POST %s: недоступный язык помечен успехом' % lang)
    print('   %-11s доступен=%-5s success=%-5s stdout=%r'
          % (lang, status[lang], data.get('success'),
             (data.get('stdout') or '')[:40].replace('\n', ' | ')))


# --- 3. ошибки, лимиты, формы запроса -------------------------------------
print('[3] Ошибки, лимиты, формы запроса')
r = client.post('/sandbox', json={'code': 'print(1)', 'lang': 'cobol'})
ok(r.status_code == 400, 'неизвестный язык: ждали 400, получили %s'
   % r.status_code)

r = client.post('/sandbox', json={'code': 'x' * 20001, 'lang': 'python'})
ok(r.status_code == 200 and 'Слишком большой код' in
   (r.get_json() or {}).get('stderr', ''), 'не сработал лимит размера кода')

r = client.post('/sandbox/go', data={'code': 'package main\n\nfunc main() {}\n'})
ok(r.status_code == 200 and (r.get_json() or {}).get('lang') == 'go',
   'язык из пути не подхватился: %s' % r.status_code)

r = client.post('/sandbox', json={'code': 'print(1/0)', 'lang': 'python'})
data = r.get_json() or {}
ok(data.get('success') is False and 'ZeroDivisionError' in
   (data.get('stderr') or ''), 'ошибка python не показана: %r' % data)

r = client.post('/sandbox', json={'code': '', 'lang': 'python'})
ok(r.status_code == 200, 'пустой код: %s' % r.status_code)

# --- 4. регресс: страницы языков, уроки и задачи ---------------------------
print('[4] Регресс: страницы языков, уроки, задачи')
for lang in langs:
    r = client.get('/language/%s' % lang)
    ok(r.status_code == 200, 'GET /language/%s: %s' % (lang, r.status_code))

    first = client.get('/language/%s' % lang).get_data(as_text=True)
    first = client.get('/language/%s' % lang).get_data(as_text=True)
    ok(bool(first), '/language/%s: пустая страница' % lang)
    # первый урок языка доступен по /lesson/<lang>/<id>
    flat = _flat_lessons(lang)
    if flat:
        lesson_id = flat[0]['id']
        r = client.get('/lesson/%s/%s' % (lang, lesson_id))
        page = r.get_data(as_text=True)
        ok(r.status_code == 200, 'GET /lesson/%s/%s: %s'
           % (lang, lesson_id, r.status_code))
        ok(('data-codeeditor' in page or 'data-pyeditor' in page or
             'data-jseditor' in page or 'data-javaeditor' in page or
             'data-cppeditor' in page),
           '/lesson/%s/%s: нет контейнера редактора кода' % (lang, lesson_id))

    tasks = _tasks(lang)
    if tasks:
        r = client.get('/language/%s/tasks/%s' % (lang, tasks[0]['id']))
        ok(r.status_code == 200, 'GET задачи %s/%s: %s'
           % (lang, tasks[0]['id'], r.status_code))

# --- 5. STARTER корректно доезжает до JS ----------------------------------
print('[5] Проверка передачи примера и языка в JS')
for lang in langs:
    example = get_sandbox_example(lang)
    html = client.get('/sandbox/' + lang).get_data(as_text=True)
    marker = html.find('var STARTER = ')
    ok(marker != -1, '/sandbox/%s: нет STARTER в JS' % lang)
    if marker != -1:
        chunk = html[marker + len('var STARTER = '):]
        chunk = chunk[:chunk.find('\n')].rstrip(';')
        try:
            decoded = json.loads(chunk)
        except ValueError as exc:
            decoded = None
            ok(False, '/sandbox/%s: STARTER не JSON (%s)' % (lang, exc))
        if decoded is not None:
            ok(decoded == example['starter'],
               '/sandbox/%s: STARTER не совпал с примером' % lang)

print()
print('Проверок: %d, проблем: %d' % (checks[0], len(problems)))
if problems:
    for p in problems:
        print(' -', p)
    sys.exit(1)
print('ПЕСОЧНИЦА: все проверки пройдены')
