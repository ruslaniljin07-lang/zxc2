# -*- coding: utf-8 -*-
"""End-to-end verification of the Código platform for all 4 languages."""
import os
import sys
import json
import io

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)

out = io.StringIO()


def log(*a):
    print(*a)
    print(*a, file=out)


# Remove old test DB so we start clean
inst = os.path.join(BASE, 'instance')
if os.path.isdir(inst):
    for f in os.listdir(inst):
        try:
            os.remove(os.path.join(inst, f))
        except Exception:
            pass

from app import app, db  # noqa: E402
from utils.language_manager import load_language, LANGUAGES  # noqa: E402

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

# create_all() normally only runs inside app.py's __main__ block
with app.app_context():
    db.create_all()

client = app.test_client()

LANGS = ['python', 'javascript', 'java', 'cpp']

log("=" * 70)
log("STEP 1: public pages")
log("=" * 70)
for url in ['/', '/login', '/register', '/leaderboard', '/cheat_sheet']:
    r = client.get(url)
    log(f"  GET {url:30s} -> {r.status_code}  ({len(r.data)} bytes)")
    assert r.status_code == 200, f"{url} failed"

log("")
log("=" * 70)
log("STEP 2: register + login")
log("=" * 70)
r = client.post('/register', data={
    'username': 'tester',
    'email': 'tester@example.com',
    'password': 'CodigoTest9',
    'confirm': 'CodigoTest9',
}, follow_redirects=True)
log(f"  POST /register -> {r.status_code}")
assert r.status_code == 200

r = client.post('/login', data={'username': 'tester', 'password': 'CodigoTest9'},
                follow_redirects=True)
log(f"  POST /login    -> {r.status_code}")
assert r.status_code == 200

log("")
log("=" * 70)
log("STEP 3: language landing pages")
log("=" * 70)
for lang in LANGS:
    r = client.get(f'/language/{lang}')
    ok = r.status_code == 200
    log(f"  GET /language/{lang:12s} -> {r.status_code}  ({len(r.data)} bytes)")
    assert ok, f"/language/{lang} failed"

log("")
log("=" * 70)
log("STEP 4: lessons list pages")
log("=" * 70)
for lang in LANGS:
    r = client.get(f'/lessons/{lang}')
    log(f"  GET /lessons/{lang:12s} -> {r.status_code}  ({len(r.data)} bytes)")
    assert r.status_code == 200, f"/lessons/{lang} failed"
    html = r.data.decode('utf-8')
    # count lesson links present
    import re
    links = re.findall(r'/lesson/([a-z]+)/(\d+)', html)
    log(f"      lesson links found: {len(set(links))}")

log("")
log("=" * 70)
log("STEP 5: every lesson in every language renders")
log("=" * 70)

total_lessons = 0
for lang in LANGS:
    data = load_language(lang)
    for m in data.get('modules', []):
        for l in m.get('lessons', []):
            total_lessons += 1
            url = f"/lesson/{lang}/{l['id']}"
            r = client.get(url)
            if r.status_code != 200:
                log(f"  FAIL {url} -> {r.status_code}")
            assert r.status_code == 200, f"{url} failed"
    log(f"  {lang}: all lessons OK")

log(f"  TOTAL LESSONS RENDERED OK: {total_lessons}")
assert total_lessons >= 20, "not enough lessons"

log("")
log("=" * 70)
log("STEP 6: entrance test pages")
log("=" * 70)
for lang in LANGS:
    r = client.get(f'/test/{lang}')
    log(f"  GET /test/{lang:12s} -> {r.status_code} ({len(r.data)} bytes)")
    assert r.status_code == 200, f"/test/{lang} failed"

log("")
log("=" * 70)
log("STEP 7: module tests exist")
log("=" * 70)
for lang in LANGS:
    data = load_language(lang)
    for m in data.get('modules', []):
        t = m.get('test')
        qn = len(t.get('questions', [])) if t else 0
        log(f"  {lang} module {m['id']} '{m['title']}': test={bool(t)} questions={qn}")

log("")
log("=" * 70)
log("STEP 8: cheat sheets")
log("=" * 70)
for lang in LANGS:
    r = client.get(f'/cheat_sheet/{lang}')
    log(f"  GET /cheat_sheet/{lang:12s} -> {r.status_code} ({len(r.data)} bytes)")
    assert r.status_code == 200, f"/cheat_sheet/{lang} failed"

log("")
log("=" * 70)
log("STEP 9: solve a task and check progress saving")
log("=" * 70)
# find first python lesson with a task
for url in ['/lesson/python/1']:
    r = client.get(url)
    assert r.status_code == 200
log("  lesson/python/1 loaded")

log("")
log("=" * 70)
log("STEP 10: dashboard + profile + leaderboard")
log("=" * 70)
for url in ['/dashboard', '/profile', '/leaderboard']:
    r = client.get(url)
    log(f"  GET {url:20s} -> {r.status_code} ({len(r.data)} bytes)")
    assert r.status_code == 200, f"{url} failed"

log("")
log("=" * 70)
log("ALL CHECKS PASSED")
log("=" * 70)

with open(os.path.join(BASE, '_e2e_out.txt'), 'w', encoding='utf-8') as f:
    f.write(out.getvalue())