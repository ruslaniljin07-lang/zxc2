# -*- coding: utf-8 -*-
"""Проверка, что страница песочницы выдаёт валидный JS для всех 9 языков."""
import io
import os
import re
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TMP_DB = os.path.join(tempfile.gettempdir(), 'codigo_js_test.db')
if os.path.exists(TMP_DB):
    os.remove(TMP_DB)
os.environ['DATABASE_URL'] = 'sqlite:///' + TMP_DB.replace('\\', '/')

from app import app, db  # noqa: E402
from utils.language_manager import LANGUAGES  # noqa: E402

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
with app.app_context():
    db.create_all()

client = app.test_client()
client.post('/register', data={'username': 'jschecker',
                               'email': 'js@example.com',
                               'password': 'CodigoTest9',
                               'confirm': 'CodigoTest9'}, follow_redirects=True)
client.post('/login', data={'username': 'jschecker',
                            'password': 'CodigoTest9'}, follow_redirects=True)

SCRIPT_RE = re.compile(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',
                       re.S | re.I)
problems = []
for lang in LANGUAGES:
    html = client.get('/sandbox/' + lang).get_data(as_text=True)
    blocks = SCRIPT_RE.findall(html)
    inline = '\n;\n'.join(blocks)
    path = '_page_js_%s.js' % lang
    with open(path, 'w', encoding='utf-8') as f:
        f.write(inline)
    r = subprocess.run(['node', '--check', path], capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    status = 'OK  ' if r.returncode == 0 else 'FAIL'
    if r.returncode != 0:
        problems.append('%s: %s' % (lang, (r.stderr or '').strip()[:200]))
    print('%s %-11s блоков <script>: %d, строк JS: %d'
          % (status, lang, len(blocks), inline.count('\n') + 1))
    os.remove(path)

print()
if problems:
    for p in problems:
        print('ПРОБЛЕМА:', p)
    sys.exit(1)
print('JS страницы песочницы: валиден для всех языков')
