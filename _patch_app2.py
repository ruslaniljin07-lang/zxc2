# -*- coding: utf-8 -*-
"""Patch 2: import get_flat_lessons + lightweight SQLite schema migration."""
import io

P = 'app.py'
src = io.open(P, 'r', encoding='utf-8', newline='').read()
applied = 0
missed = []

# --- import ---
old = "                                    get_file_ext, LANGUAGES)"
new = "                                    get_file_ext, LANGUAGES,\r\n" \
      "                                    get_flat_lessons)"
if old in src:
    src = src.replace(old, new, 1)
    applied += 1
else:
    missed.append('import')

# --- schema guard: добавляет недостающие колонки в старых БД ---------------
old = "def init_achievements():"
new = '''def ensure_schema():
    """Добавляет недостающие колонки, если база создана старой версией."""
    from sqlalchemy import text
    expected = {
        'users': {'current_language': "VARCHAR(20) DEFAULT 'python'"},
        'leaderboard': {'language': "VARCHAR(20) DEFAULT 'python'"},
        'test_results': {'language': "VARCHAR(20) DEFAULT 'python'"},
        'lesson_progress': {'language': "VARCHAR(20) DEFAULT 'python'",
                            'module_id': 'INTEGER DEFAULT 0',
                            'best_code': 'TEXT DEFAULT \'\''},
        'achievements': {'language': "VARCHAR(20) DEFAULT 'all'"},
    }
    for table, columns in expected.items():
        try:
            rows = db.session.execute(
                text(f'PRAGMA table_info({table})')).fetchall()
        except Exception:
            continue
        existing = {r[1] for r in rows}
        if not existing:
            continue
        for col, ddl in columns.items():
            if col in existing:
                continue
            try:
                db.session.execute(
                    text(f'ALTER TABLE {table} ADD COLUMN {col} {ddl}'))
                db.session.commit()
            except Exception:
                db.session.rollback()


def init_achievements():'''
if old in src:
    src = src.replace(old, new, 1)
    applied += 1
else:
    missed.append('ensure_schema')

# --- вызов миграции при старте --------------------------------------------
old = ("    with app.app_context():\r\n"
       "        db.create_all()\r\n"
       "        init_achievements()")
new = ("    with app.app_context():\r\n"
       "        db.create_all()\r\n"
       "        ensure_schema()\r\n"
       "        init_achievements()")
if old in src:
    src = src.replace(old, new, 1)
    applied += 1
else:
    missed.append('startup')

print('applied', applied, 'missed', missed)
io.open(P, 'w', encoding='utf-8', newline='').write(src)