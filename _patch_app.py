# -*- coding: utf-8 -*-
"""One-off patch script for app.py (CRLF-safe)."""
import io
import sys

P = 'app.py'
src = io.open(P, 'r', encoding='utf-8', newline='').read()

REPLACEMENTS = []

# --- 1. import get_flat_lessons -------------------------------------------
REPLACEMENTS.append((
    "                                    get_module_progress, get_total_tasks,\r\n"
    "                                    get_file_ext)",
    "                                    get_module_progress, get_total_tasks,\r\n"
    "                                    get_file_ext, get_flat_lessons)"
))

# --- 2. index(): show cards with progress for everyone --------------------
REPLACEMENTS.append((
    "@app.route('/')\r\n"
    "def index():\r\n"
    "    languages = get_all_languages()\r\n"
    "    if current_user.is_authenticated:\r\n"
    "        return redirect(url_for('dashboard'))\r\n"
    "    return render_template('index.html', languages=languages)",
    "@app.route('/')\r\n"
    "def index():\r\n"
    "    languages = get_all_languages()\r\n"
    "    lang_progress = {}\r\n"
    "    if current_user.is_authenticated:\r\n"
    "        for lang in languages:\r\n"
    "            lang_progress[lang['code']] = get_lesson_progress(\r\n"
    "                current_user, lang['code'])\r\n"
    "    return render_template('index.html', languages=languages,\r\n"
    "                           lang_progress=lang_progress)"
))

# --- 3. lessons route: language aware -------------------------------------
REPLACEMENTS.append((
    "@app.route('/lessons')\r\n"
    "@login_required\r\n"
    "def lessons():\r\n"
    "    lang_code = current_user.current_language or 'python'\r\n",
    "@app.route('/lessons')\r\n"
    "@app.route('/lessons/<lang_code>')\r\n"
    "@login_required\r\n"
    "def lessons(lang_code=None):\r\n"
    "    lang_code = lang_code or current_user.current_language or 'python'\r\n"
))

# --- 4. lesson route: language aware --------------------------------------
REPLACEMENTS.append((
    "@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])\r\n"
    "@login_required\r\n"
    "def lesson(lesson_id):\r\n"
    "    lang_code = request.args.get('lang') or current_user.current_language or 'python'\r\n",
    "@app.route('/lesson/<lang_code>/<int:lesson_id>', methods=['GET', 'POST'])\r\n"
    "@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])\r\n"
    "@login_required\r\n"
    "def lesson(lesson_id, lang_code=None):\r\n"
    "    lang_code = (lang_code or request.args.get('lang')\r\n"
    "                 or current_user.current_language or 'python')\r\n"
))

# --- 5. lesson(): flat list helper ----------------------------------------
REPLACEMENTS.append((
    "    # собрать плоский список уроков для навигации\r\n"
    "    lang_data = load_language(lang_code)\r\n"
    "    all_lessons = [l for m in lang_data.get('modules', []) for l in m.get('lessons', [])]\r\n",
    "    # собрать плоский список уроков для навигации\r\n"
    "    lang_data = load_language(lang_code)\r\n"
    "    all_lessons = get_flat_lessons(lang_code)\r\n"
))

# --- 6. lesson GET: progress must be language+module scoped ---------------
REPLACEMENTS.append((
    "    progress = LessonProgress.query.filter_by(\r\n"
    "        user_id=current_user.id, lesson_id=lesson_id\r\n"
    "    ).first()\r\n",
    "    progress = LessonProgress.query.filter_by(\r\n"
    "        user_id=current_user.id, language=lang_code,\r\n"
    "        lesson_id=lesson_id, module_id=module_id\r\n"
    "    ).first()\r\n"
))

# --- 7. cheat_sheet(): clean leftovers ------------------------------------
REPLACEMENTS.append((
    "def cheat_sheet():\r\n"
    "    langs = get_language_info  # лёгкая ссылка, но нужно импортировать список языков\r\n"
    "    languages = {}\r\n"
    "    sheets = {}\r\n"
    "    from utils.language_manager import LANGUAGES, get_cheatsheets\r\n"
    "    for code, info in LANGUAGES.items():\r\n"
    "        cheats = get_cheatsheets(code)\r\n"
    "        if cheats:\r\n"
    "            languages[code] = info\r\n"
    "            sheets[code] = cheats\r\n",
    "def cheat_sheet():\r\n"
    "    from utils.language_manager import LANGUAGES\r\n"
    "    languages = {}\r\n"
    "    sheets = {}\r\n"
    "    for code, info in LANGUAGES.items():\r\n"
    "        cheats = get_cheatsheets(code)\r\n"
    "        if cheats:\r\n"
    "            languages[code] = info\r\n"
    "            sheets[code] = cheats\r\n"
))

applied = 0
for old, new in REPLACEMENTS:
    if old not in src:
        print('MISS:', old.splitlines()[0][:70])
        continue
    src = src.replace(old, new, 1)
    applied += 1

print('applied', applied, 'of', len(REPLACEMENTS))
io.open(P, 'w', encoding='utf-8', newline='').write(src)