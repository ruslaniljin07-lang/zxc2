# -*- coding: utf-8 -*-
"""Diagnose the real user flow for all 4 languages."""
import os, sys, io
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
out = io.StringIO()
def log(*a):
    print(*a)
    print(*a, file=out)

inst = os.path.join(BASE, 'instance')
if os.path.isdir(inst):
    for f in os.listdir(inst):
        try:
            os.remove(os.path.join(inst, f))
        except Exception:
            pass

from app import app, db
from utils.language_manager import load_language

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
with app.app_context():
    db.create_all()

client = app.test_client()
client.post('/register', data={'username': 'tester', 'email': 't@t.com',
                               'password': 'pass1234', 'confirm': 'pass1234'})
client.post('/login', data={'username': 'tester', 'password': 'pass1234'})

log("== dashboard ==")
r = client.get('/dashboard')
log("GET /dashboard ->", r.status_code, len(r.data))

log("\n== /lessons (uses current_language) ==")
r = client.get('/lessons')
log("GET /lessons ->", r.status_code, len(r.data))

for lang in ['python', 'javascript', 'java', 'cpp']:
    log(f"\n== {lang} ==")
    r = client.get(f'/language/{lang}')
    log(f"  GET /language/{lang} ->", r.status_code, len(r.data))
    r = client.get(f'/lessons?lang={lang}')
    log(f"  GET /lessons?lang={lang} ->", r.status_code, len(r.data))
    data = load_language(lang)
    mods = data.get('modules', [])
    for m in mods:
        for lsn in m.get('lessons', []):
            r = client.get(f'/lesson/{lsn["id"]}?lang={lang}')
            line = f"  GET /lesson/{lsn['id']}?lang={lang} -> {r.status_code} ({len(r.data)} b) {lsn['title'][:30]}"
            log(line)
            if r.status_code != 200:
                log("     BODY:", r.data.decode('utf-8', 'replace')[:300])
    r = client.get(f'/test/{lang}')
    log(f"  GET /test/{lang} ->", r.status_code, len(r.data))

with open(os.path.join(BASE, '_diag_out.txt'), 'w', encoding='utf-8') as f:
    f.write(out.getvalue())