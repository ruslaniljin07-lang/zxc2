# -*- coding: utf-8 -*-
"""Проверка безопасности: заголовки, CSRF, лимиты, валидация, изоляция.

Использует временную sqlite-базу (DATABASE_URL), рабочие данные не трогает.
"""
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

_REPORT = open(os.path.join(BASE, '_test_security_out.txt'), 'w',
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

TMP_DB = os.path.join(tempfile.gettempdir(), 'codigo_security_test.db')
if os.path.exists(TMP_DB):
    os.remove(TMP_DB)
os.environ['DATABASE_URL'] = 'sqlite:///' + TMP_DB.replace('\\', '/')

from app import app, db  # noqa: E402
from utils.security import rate_limiter  # noqa: E402
from utils.language_manager import load_language  # noqa: E402

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['RATE_LIMIT_ENABLED'] = True
app.config['CSRF_STRICT_TESTING'] = False

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

# --- 1. заголовки безопасности -------------------------------------------
resp = client.get('/login')
csp = resp.headers.get('Content-Security-Policy', '')
ok('nonce-' in csp, 'CSP: нет nonce')
ok("'strict-dynamic'" in csp, 'CSP: нет strict-dynamic')
ok("object-src 'none'" in csp, 'CSP: нет object-src none')
ok("frame-ancestors 'none'" in csp, 'CSP: нет frame-ancestors none')
ok("form-action 'self'" in csp, 'CSP: нет form-action self')
ok(resp.headers.get('X-Frame-Options') == 'DENY', 'нет X-Frame-Options: DENY')
ok(resp.headers.get('X-Content-Type-Options') == 'nosniff', 'нет nosniff')
ok('no-referrer' in resp.headers.get('Referrer-Policy', '') or
   'strict-origin' in resp.headers.get('Referrer-Policy', ''),
   'нет Referrer-Policy')
ok('geolocation=()' in resp.headers.get('Permissions-Policy', ''),
   'нет Permissions-Policy')
ok(resp.headers.get('Cache-Control') == 'no-store', 'нет Cache-Control')

body = resp.get_data(as_text=True)
nonce_in_header = re.search(r"nonce-([^']+)'", csp)
nonce_in_html = re.search(r'<script[^>]*\snonce="([^"]+)"', body)
ok(bool(nonce_in_header) and bool(nonce_in_html) and
   nonce_in_header.group(1) == nonce_in_html.group(1),
   'nonce в заголовке и в странице не совпадают')
ok('name="csrf-token"' in body, 'нет meta csrf-token')
ok('<form method="POST">' in body and 'csrf_token' in body,
   'нет скрытого поля CSRF в форме входа')

cookie_headers = resp.headers.getlist('Set-Cookie')
session_cookie = next((c for c in cookie_headers if 'session' in c), '')
ok('HttpOnly' in session_cookie, 'у сессионной куки нет HttpOnly')
ok('SameSite=Lax' in session_cookie or 'SameSite=Lax'.lower()
   in session_cookie.lower(), 'у сессионной куки нет SameSite=Lax')

# --- 2. CSRF --------------------------------------------------------------
app.config['CSRF_STRICT_TESTING'] = True
resp = client.post('/login', data={'username': 'x', 'password': 'y'})
ok(resp.status_code == 400, 'POST без токена должен отклоняться (получено %d)'
   % resp.status_code)

html = client.get('/login').get_data(as_text=True)
token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
resp = client.post('/login', data={'username': 'x', 'password': 'y',
                                   'csrf_token': token})
ok(resp.status_code != 400, 'POST с токеном должен проходить (получено %d)'
   % resp.status_code)
ok(resp.status_code != 500, 'POST с токеном дал 500')

resp = client.post('/login', data={'username': 'x', 'password': 'y',
                                   'csrf_token': token + 'x'},
                   headers={'X-Requested-With': 'XMLHttpRequest'})
ok(resp.status_code == 400, 'неверный токен должен отклоняться')

resp = client.post('/sandbox', json={'code': 'print(1)', 'lang': 'python'},
                   headers={'X-CSRF-Token': token})
ok(resp.status_code in (302, 401, 200, 403, 400) and resp.status_code != 500,
   'песочница с заголовком CSRF не должна падать (получено %d)'
   % resp.status_code)
app.config['CSRF_STRICT_TESTING'] = False

# --- 3. ограничение частоты ----------------------------------------------
rate_limiter._hits.clear()
last = None
for _ in range(12):
    last = client.post('/login', data={'username': 'nobody',
                                       'password': 'wrong'})
ok(last.status_code == 429, '12-я попытка входа должна дать 429 (получено %d)'
   % last.status_code)
rate_limiter._hits.clear()


# --- 4. валидация регистрации --------------------------------------------
def try_register(username, email, password):
    rate_limiter._hits.clear()
    return client.post('/register', data={
        'username': username, 'email': email,
        'password': password, 'confirm': password})


def page_text(resp):
    return resp.get_data(as_text=True)


resp = try_register('student1', 'a@b.com', 'short1')
ok('8 символов' in page_text(resp), 'короткий пароль не отклонён')

resp = try_register('student2', 'a@b.com', 'password123')
ok('взламывают' in page_text(resp), 'популярный пароль не отклонён')

resp = try_register('<script>alert(1)</script>', 'a@b.com', 'StrongPass9')
ok('Имя' in page_text(resp), 'логин со спецсимволами не отклонён')

resp = try_register('okuser', 'не-почта', 'StrongPass9')
ok('адрес почты' in page_text(resp), 'некорректный email не отклонён')

resp = try_register('okuser', 'okuser@example.com', 'StrongPass9')
ok(resp.status_code == 302 or 'уже' in page_text(resp),
   'валидная регистрация не прошла (получено %d)' % resp.status_code)

# --- 5. обход через путь в адресе ----------------------------------------
ok(load_language('../../etc/passwd') is None,
   'load_language должен отклонять чужие коды языков')
resp = client.get('/language/..%2f..%2fconfig')
ok(resp.status_code in (302, 404), 'обход через путь не отклонён (получено %d)'
   % resp.status_code)
ok(resp.status_code != 500, 'обход через путь дал 500')

resp = client.get('/language/python')
ok(resp.status_code == 200, '/language/python должен открываться')

# --- 6. размер запроса ----------------------------------------------------
# 413 срабатывает там, где сервер читает тело запроса
rate_limiter._hits.clear()
resp = client.post('/login', data={'username': 'u' * (600 * 1024),
                                   'password': 'p'})
ok(resp.status_code == 413, 'огромный запрос должен давать 413 (получено %d)'
   % resp.status_code)

# --- 7. ошибки -------------------------------------------------------------
resp = client.get('/no-such-page-here')
ok(resp.status_code == 404, 'несуществующая страница должна давать 404')
ok('Ошибка 404' in page_text(resp), 'нет страницы ошибки 404')

resp = client.post('/leaderboard')
ok(resp.status_code == 405, 'неверный метод должен давать 405 (получено %d)'
   % resp.status_code)

# --- 8. изоляция песочницы ------------------------------------------------
client2 = app.test_client()
try_register('sandboxsec', 'sandboxsec@example.com', 'StrongPass9')
client2.post('/login', data={'username': 'sandboxsec',
                             'password': 'StrongPass9'})
csrf_html = client2.get('/sandbox').get_data(as_text=True)
sandbox_token = re.search(r'name="csrf-token" content="([^"]+)"',
                          csrf_html).group(1)
HEADERS = {'X-CSRF-Token': sandbox_token}


def run_code(code):
    rate_limiter._hits.clear()
    return client2.post('/sandbox', json={'code': code, 'lang': 'python'},
                        headers=HEADERS).get_json()


data = run_code('print(6 * 7)')
ok(data['success'] and '42' in data['stdout'], 'песочница не запускает код')

data = run_code('import socket\nprint(socket.gethostname())')
ok(not data['success'] and 'отключён' in data['stderr'],
   'песочница: сеть не заблокирована')

data = run_code("print(open('instance/codigo.db', 'rb').read()[:10])")
ok(not data['success'], 'песочница: чтение базы не заблокировано')

data = run_code('import subprocess\nsubprocess.run(["whoami"])')
ok(not data['success'], 'песочница: запуск процессов не заблокирован')

data = run_code('while True:\n    pass')
ok(not data['success'] and 'время' in data['stderr'].lower(),
   'песочница: бесконечный цикл не останавливается')

# --- 9. секреты ------------------------------------------------------------
ok(len(app.config['SECRET_KEY']) >= 32, 'слишком короткий SECRET_KEY')
ok('dev-secret' not in app.config['SECRET_KEY'], 'SECRET_KEY остался дефолтным')
ok(app.config['MAX_CONTENT_LENGTH'] <= 2 * 1024 * 1024,
   'нет ограничения размера запроса')

print()
print('Проверок: %d, проблем: %d' % (checks[0], len(problems)))
if problems:
    for item in problems:
        print('  - ' + item)
    sys.exit(1)
print('Все проверки безопасности пройдены')
