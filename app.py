import os
import json
from datetime import datetime, date
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, jsonify)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash

from utils.code_checker import (check_code, run_sandbox_code,
                                sandbox_status, sandbox_timeout,
                                SANDBOX_TYPES)
from utils.gamification import (get_status_emoji, get_status_name,
                                get_status_color, check_streak_rewards,
                                level_progress)
from utils.level_engine import determine_level
from utils.security import (init_security, rate_limit, log_event,
                            is_rate_limited, rate_limiter, clean_code,
                            validate_username, validate_email,
                            validate_password, normalize_username)
from utils.language_manager import (load_language, get_all_languages,
                                    get_language_info, get_module, get_lesson,
                                    get_total_lessons, get_lesson_progress,
                                    get_entrance_test, get_cheatsheets,
                                    get_module_progress, get_total_tasks,
                                    get_file_ext, LANGUAGES,
                                    get_flat_lessons,
                                    load_tasks, get_task, get_task_progress,
                                    get_sandbox_langs, get_sandbox_example)

from models import (db, User, TestResult, LessonProgress, StreakReward,
                    Achievement, UserAchievement, LeaderboardEntry,
                    LanguageProgress, TaskProgress)

app = Flask(__name__)
app.config.from_object('config.Config')
MAX_CODE_LENGTH = app.config['MAX_CODE_LENGTH']
app.jinja_env.globals.update(enumerate=enumerate)

db.init_app(app)
# CSRF, лимиты частоты, заголовки безопасности, обработчики ошибок
init_security(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.context_processor
def inject_nav():
    """Передаёт во все шаблоны список языков и текущий выбранный язык,
    чтобы навигация и переключатель языков работали на любой странице."""
    active = current_user.current_language if current_user.is_authenticated else None
    active = active or request.args.get('lang') or 'python'
    if active not in LANGUAGES:
        active = 'python'
    return {
        'nav_languages': [dict(get_language_info(code), code=code)
                          for code in LANGUAGES],
        'nav_lang': active,
        'nav_lang_info': get_language_info(active),
        'nav_current_language': active,
    }


def _demo_tables_for(lang_code):
    """Содержимое таблиц БД для показа рядом с редактором (только SQL).

    Для остальных языков возвращается пустой список: показывать нечего.
    """
    if lang_code != 'sql':
        return []
    try:
        from utils.sql_demo import demo_tables

        return demo_tables()
    except Exception:                                            # noqa: BLE001
        return []


def recalc_level(user):
    """Уровень растёт вместе с XP (та же формула, что в прогресс-баре).
    Уровень никогда не понижается: тест может дать стартовый уровень."""
    xp = user.xp
    level = 0
    need = 100
    while xp >= need:
        xp -= need
        level += 1
        need = 100 * (level + 1) ** 2
    if level > user.level:
        user.level = level
    return user.level


def grant_achievements(user, language='python'):
    """Проверяет условия достижений и выдаёт те, что выполнены.
    Возвращает список новых достижений (каждое даёт бонусный XP)."""
    achieved_ids = {ua.achievement_id for ua in
                    UserAchievement.query.filter_by(user_id=user.id)}
    completed = LessonProgress.query.filter_by(
        user_id=user.id, language=language, completed=True).count()
    has_test = TestResult.query.filter_by(
        user_id=user.id, language=language).count() > 0
    first_try = LessonProgress.query.filter_by(
        user_id=user.id, language=language, completed=True, attempts=1).count() > 0
    total_lessons = get_total_lessons(language)

    new = []
    for ach in Achievement.query.all():
        if ach.id in achieved_ids:
            continue
        if ach.language != 'all' and ach.language != language:
            continue
        ct = ach.condition_type or ''
        cv = ach.condition_value or 1
        got = False
        if ct == 'register':
            got = True
        elif ct == 'test':
            got = has_test
        elif ct == 'lesson':
            got = completed >= 1
        elif ct == 'all_lessons':
            got = completed >= total_lessons
        elif ct == '10_correct':
            got = completed >= cv
        elif ct == 'first_try':
            got = first_try
        elif ct.startswith('streak_'):
            got = user.streak_count >= cv
        if not got:
            continue
        db.session.add(UserAchievement(user_id=user.id,
                                       achievement_id=ach.id))
        user.xp += ach.xp_reward or 0
        new.append(ach)
    recalc_level(user)
    db.session.commit()
    return new


@app.route('/')
def index():
    languages = get_all_languages()
    lang_progress = {}
    if current_user.is_authenticated:
        for lang in languages:
            lang_progress[lang['code']] = get_lesson_progress(
                current_user, lang['code'])
    return render_template('index.html', languages=languages,
                           lang_progress=lang_progress)


@app.route('/register', methods=['GET', 'POST'])
@rate_limit('register')
def register():
    if request.method == 'POST':
        username = normalize_username(request.form.get('username', ''))
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not username or not email or not password:
            flash('Заполните все поля', 'danger')
            return render_template('register.html')

        ok, message = validate_username(username)
        if not ok:
            flash(message, 'danger')
            return render_template('register.html')

        email = email.lower()
        ok, message = validate_email(email)
        if not ok:
            flash(message, 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Пароли не совпадают', 'danger')
            return render_template('register.html')

        ok, message = validate_password(password, username, email)
        if not ok:
            flash(message, 'danger')
            return render_template('register.html')

        existing = User.query.filter_by(username=username).first()
        if existing:
            flash('Пользователь с таким именем уже существует', 'danger')
            return render_template('register.html')

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Пользователь с такой почтой уже зарегистрирован', 'danger')
            return render_template('register.html')

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            xp=0, level=0, streak_count=0,
            last_login=datetime.now()
        )
        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Не удалось зарегистрировать пользователя', 'danger')
            return render_template('register.html')
        log_event('register_ok', username=username)
        grant_achievements(user)
        flash('Регистрация прошла успешно! Войдите в аккаунт.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
@rate_limit('login')
def login():
    if request.method == 'POST':
        username = normalize_username(request.form.get('username', ''))
        password = request.form.get('password', '')

        # отдельный счётчик по логину: перебор паролей с разных адресов
        # тоже упирается в лимит
        if is_rate_limited('login', extra_key=username):
            log_event('login_blocked', username=username)
            flash('Слишком много попыток входа. Подожди 5 минут.', 'danger')
            return render_template('login.html'), 429

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            rate_limiter.reset('login:name:%s' % username.lower())
            user.last_login = datetime.now()
            db.session.commit()
            grant_achievements(user)
            log_event('login_ok', username=username)
            flash('Добро пожаловать!', 'success')
            return redirect(url_for('dashboard'))

        log_event('login_failed', username=username)
        flash('Неверный логин или пароль', 'danger')
        return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    grant_achievements(current_user)
    streak = current_user.streak_count
    status_emoji = get_status_emoji(streak)
    status_name = get_status_name(streak)
    status_color = get_status_color(streak)
    level_xp, xp_to_next = level_progress(current_user.xp)
    # достижения пользователя для карточки на дашборде
    ua_rows = UserAchievement.query.filter_by(
        user_id=current_user.id).all()
    earned_achievements = []
    if ua_rows:
        ach_ids = [r.achievement_id for r in ua_rows]
        achs = Achievement.query.filter(
            Achievement.id.in_(ach_ids)).all()
        earned_achievements = [{'icon': a.icon, 'name': a.name,
                                'xp': a.xp_reward}
                               for a in achs]

    lang_progress = {}
    for lang in get_all_languages():
        p = get_lesson_progress(current_user, lang['code'])
        lang_progress[lang['code']] = p

    return render_template('dashboard.html',
                           streak=streak, status_emoji=status_emoji,
                           status_name=status_name, status_color=status_color,
                           xp=current_user.xp, xp_to_next=xp_to_next,
                           level_xp=level_xp, level=current_user.level,
                           user=current_user,
                           earned_achievements=earned_achievements,
                           languages=get_all_languages(),
                           lang_progress=lang_progress,
                           tasks_done=TaskProgress.query.filter_by(
                               user_id=current_user.id, completed=True).count(),
                           tests_done=TestResult.query.filter_by(
                               user_id=current_user.id).count(),
                           lessons_done=LessonProgress.query.filter_by(
                               user_id=current_user.id, completed=True).count())


@app.route('/language/<lang_code>')
def language_course(lang_code):
    if lang_code not in LANGUAGES:
        flash('Язык не найден', 'danger')
        return redirect(url_for('index'))
    lang_data = load_language(lang_code)
    if not lang_data:
        flash('Язык не найден', 'danger')
        return redirect(url_for('index'))
    if current_user.is_authenticated:
        current_user.current_language = lang_code
        db.session.commit()

    lang_info = get_language_info(lang_code)
    modules = lang_data.get('modules', [])
    progress = {'percent': 0, 'completed': 0, 'total': 0}
    module_progress = {}
    if current_user.is_authenticated:
        progress = get_lesson_progress(current_user, lang_code)
        module_progress = {
            m['id']: get_module_progress(current_user, lang_code, m['id'])
            for m in modules
        }
    return render_template(
        'language_course.html',
        language=lang_data, lang_code=lang_code, lang_info=lang_info,
        modules=modules, progress=progress, module_progress=module_progress
    )


def _grade_entrance(lang_code, form):
    """Проверяет ответы входного теста для языка, возвращает (score, total)."""
    questions = get_entrance_test(lang_code)
    score = 0
    for i, quest in enumerate(questions, 1):
        user_answer = form.get(f'q{i}', '').strip()
        if user_answer == str(quest.get('correct', -1)):
            score += 1
    return score, len(questions)


@app.route('/test', methods=['GET', 'POST'])
@app.route('/test/<lang_code>', methods=['GET', 'POST'])
@login_required
@rate_limit('submit_test')
def test(lang_code=None):
    lang_code = lang_code or current_user.current_language or 'python'
    questions = get_entrance_test(lang_code)
    if not questions:
        flash('Тест для этого языка пока не готов', 'warning')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        score, total = _grade_entrance(lang_code, request.form)
        percent = round(score / total * 100) if total else 0
        level = determine_level(score)
        result = TestResult(user_id=current_user.id, score=score,
                            language=lang_code, level=level)
        db.session.add(result)
        current_user.level = max(current_user.level, level)
        current_user.xp += score * 20
        current_user.streak_count += 1
        check_streak_rewards(current_user)
        recalc_level(current_user)
        db.session.commit()
        grant_achievements(current_user, language=lang_code)
        flash(f'Тест пройден! Счёт: {score}/{total} ({percent}%). '
              f'Рекомендуемый уровень: {"Beginner" if percent < 50 else "Elementary" if percent < 70 else "Intermediate" if percent < 90 else "Advanced"}',
              'success')
        return redirect(url_for('language_course', lang_code=lang_code))

    lang_info = get_language_info(lang_code)
    return render_template('test.html', questions=questions,
                           lang_code=lang_code, lang_info=lang_info)


@app.route('/lessons')
@app.route('/lessons/<lang_code>')
@login_required
def lessons(lang_code=None):
    lang_code = lang_code or request.args.get('lang') \
        or current_user.current_language or 'python'
    if lang_code not in LANGUAGES:
        lang_code = 'python'
    # запоминаем выбранный язык, чтобы навигация оставалась корректной
    if current_user.current_language != lang_code:
        current_user.current_language = lang_code
        db.session.commit()
    lang_data = load_language(lang_code)
    if not lang_data:
        flash('Язык не найден', 'danger')
        return redirect(url_for('dashboard'))

    progress_map = {
        p.lesson_id: p for p in LessonProgress.query.filter_by(
            user_id=current_user.id,
            language=lang_code
        ).all()
    }
    total = get_total_lessons(lang_code)
    done = sum(1 for p in progress_map.values() if p.completed)
    lang_info = get_language_info(lang_code)
    return render_template('lessons.html',
                           modules=lang_data.get('modules', []),
                           progress_map=progress_map,
                           total=total, done=done,
                           lang_code=lang_code, lang_info=lang_info,
                           languages=get_all_languages())


# --- SQL demo tables: парсит setup SQL и возвращает структуру для шаблона ---
def _parse_sql_demo_tables(setup_sql):
    """Извлекает таблицы и примеры данных из setup SQL для отображения на уроке."""
    import sqlite3, re
    tables = []
    if not setup_sql:
        return tables
    conn = sqlite3.connect(':memory:')
    try:
        conn.executescript(setup_sql)
        cur = conn.cursor()
        # список таблиц
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        for (tname,) in cur.fetchall():
            # колонки
            cur.execute(f'PRAGMA table_info("{tname}")')
            columns = [row[1] for row in cur.fetchall()]
            # пример данных (первые 10 строк)
            cur.execute(f'SELECT * FROM "{tname}" LIMIT 10')
            rows = [list(r) for r in cur.fetchall()]
            tables.append({
                'code': tname,
                'title': tname.capitalize(),
                'columns': columns,
                'rows': rows,
            })
    except Exception:
        pass
    finally:
        conn.close()
    return tables


@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])
@app.route('/lesson/<lang_code>/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
@rate_limit('submit_solution')
def lesson(lesson_id, lang_code=None):
    lang_code = lang_code or request.args.get('lang') \
        or current_user.current_language or 'python'
    if lang_code not in LANGUAGES:
        lang_code = 'python'
    if current_user.current_language != lang_code:
        current_user.current_language = lang_code
        db.session.commit()
    lesson_data, module = get_lesson(lang_code, lesson_id)
    if not lesson_data:
        flash('Урок не найден', 'danger')
        return redirect(url_for('lessons', lang_code=lang_code))

    module_id = module['id'] if module else 0
    tasks = lesson_data.get('tasks', [])

    # какую задачу показываем/проверяем (1-based)
    if request.method == 'POST':
        try:
            task_num = int(request.form.get('task_num', 1))
        except (TypeError, ValueError):
            task_num = 1
    else:
        try:
            task_num = int(request.args.get('task', 1))
        except (TypeError, ValueError):
            task_num = 1
    task_num = min(max(task_num, 1), max(len(tasks), 1))
    task_index = task_num - 1
    task = tasks[task_index] if tasks else {}

    # прогресс по каждой задаче урока (TaskProgress.task_id кодирует урок+задачу)
    def _tp_id(idx):
        return lesson_id * 100 + idx + 1

    def _task_progress_map():
        rows = TaskProgress.query.filter_by(
            user_id=current_user.id, language=lang_code,
            lesson_id=lesson_id).all()
        return {r.task_id % 100: r for r in rows}

    # собрать плоский список уроков для навигации
    lang_data = load_language(lang_code)
    all_lessons = get_flat_lessons(lang_code)
    order_ids = [l['id'] for l in all_lessons]
    cur_idx = next((i for i, lid in enumerate(order_ids) if lid == lesson_id), -1)
    prev_lesson = all_lessons[cur_idx - 1] if cur_idx > 0 else None
    next_lesson = all_lessons[cur_idx + 1] if 0 <= cur_idx < len(order_ids) - 1 else None

    progress = LessonProgress.query.filter_by(
        user_id=current_user.id, language=lang_code,
        lesson_id=lesson_id, module_id=module_id
    ).first()

    if request.method == 'POST':
        user_code = clean_code(request.form.get('code', ''))
        check = task.get('check') or lesson_data.get('test_code') or ''
        result = check_code(user_code, check)

        # прогресс урока (для списка уроков)
        if not progress:
            progress = LessonProgress(
                user_id=current_user.id, language=lang_code,
                lesson_id=lesson_id, module_id=module_id,
                completed=False, attempts=0, best_code=''
            )
            db.session.add(progress)
        progress.attempts += 1

        # прогресс конкретной задачи
        tp = TaskProgress.query.filter_by(
            user_id=current_user.id, language=lang_code,
            task_id=_tp_id(task_index)).first()
        if not tp:
            tp = TaskProgress(user_id=current_user.id, language=lang_code,
                              task_id=_tp_id(task_index), lesson_id=lesson_id,
                              completed=False, code='', attempts=0)
            db.session.add(tp)
        tp.attempts += 1

        first_success = result['success'] and not tp.completed

        if result['success']:
            tp.completed = True
            tp.code = user_code
            progress.best_code = user_code

            # XP за новую задачу (за повторное решение XP не начисляем)
            xp_gained = 0
            if first_success:
                xp_gained = 10
                current_user.xp += xp_gained

            # урок завершён, когда решены все его задачи
            tp_map_now = _task_progress_map()
            all_done = all(
                tp_map_now.get(i) is not None and tp_map_now[i].completed
                for i in range(1, len(tasks) + 1)
            ) if tasks else True
            if all_done and not progress.completed:
                progress.completed = True
                xp_gained += lesson_data.get('xp_reward', 15)
                current_user.xp += lesson_data.get('xp_reward', 15)

            check_streak_rewards(current_user)
            recalc_level(current_user)
            db.session.commit()
            new_achievements = grant_achievements(current_user, language=lang_code)
            next_task = task_num + 1 if task_num < len(tasks) else None
            return jsonify({
                'success': True,
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'level': current_user.level,
                'xp': current_user.xp,
                'xp_gained': xp_gained,
                'lesson_completed': progress.completed,
                'next_task': next_task,
                'new_achievements': [a.name for a in new_achievements]
            })
        else:
            db.session.commit()
            # прогрессивные подсказки: 1-я и 2-я ошибки — без подсказок,
            # с 3-й ошибки — лампочка с подсказкой, с 4-й — полное решение
            hint = None
            solution = None
            attempts = tp.attempts
            if attempts >= 3 and task.get('hints'):
                hint = task['hints'][0]
            if attempts >= 4:
                solution = task.get('solution') or task.get('initial_code', '')
            return jsonify({
                'success': False,
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'attempts': attempts,
                'hint': hint,
                'solution': solution
            })

    progress = LessonProgress.query.filter_by(
        user_id=current_user.id, language=lang_code,
        lesson_id=lesson_id, module_id=module_id
    ).first()
    tp_map = _task_progress_map()
    # начальный код: сохранённый код этой задачи, потом заготовка из задания
    tp = tp_map.get(task_num)
    if tp and tp.code:
        initial_code = tp.code
    elif progress and progress.best_code and task_num == 1:
        initial_code = progress.best_code
    else:
        initial_code = task.get('initial_code', '')
    # прогрессивные подсказки при повторном открытии урока:
    # с 3-й попытки — подсказка, с 4-й — полное решение
    attempts = tp.attempts if tp else 0
    hint = task['hints'][0] if (attempts >= 3 and task.get('hints')) else None
    solution = (task.get('solution') or task.get('initial_code', '')) \
        if attempts >= 4 else None

    # переключение языка прямо со страницы урока: тот же номер урока по порядку
    lang_links = []
    for info in get_all_languages():
        if info['code'] == lang_code:
            continue
        other_flat = get_flat_lessons(info['code'])
        if other_flat:
            same_pos = other_flat[min(cur_idx if cur_idx >= 0 else 0,
                                      len(other_flat) - 1)]
            lang_links.append({'code': info['code'], 'icon': info['icon'],
                               'name': info['name'],
                               'url': url_for('lesson', lang_code=info['code'],
                                              lesson_id=same_pos['id'])})

    # для SQL-уроков передаём схему базы, названия колонок и демо-таблицы
    sql_setup = None
    sql_columns = None
    demo_tables = None
    if lang_code == 'sql':
        check = task.get('check') or {}
        sql_setup = check.get('setup', '')
        sql_columns = check.get('columns', [])
        demo_tables = _parse_sql_demo_tables(sql_setup)
    return render_template('lesson.html', lesson=lesson_data,
                           initial_code=initial_code, hint=hint,
                           solution=solution, progress=progress,
                           prev_lesson=prev_lesson, next_lesson=next_lesson,
                           sql_setup=sql_setup, sql_columns=sql_columns,
                           demo_tables=demo_tables,
                           lang_code=lang_code, lang_info=get_language_info(lang_code),
                           task=task, file_name=get_file_ext(lang_code),
                           module=module, languages=get_all_languages(),
                           tasks=tasks, task_num=task_num,
                           tp_map={k: (v.completed, v.attempts)
                                   for k, v in tp_map.items()},
                           lang_links=lang_links)


@app.route('/language/<lang_code>/tasks')
@login_required
def language_tasks(lang_code):
    """Банк практических задач языка: список с прогрессом."""
    if lang_code not in LANGUAGES:
        flash('Язык не найден', 'danger')
        return redirect(url_for('dashboard'))
    if current_user.current_language != lang_code:
        current_user.current_language = lang_code
        db.session.commit()
    tp = get_task_progress(current_user, lang_code)
    topics = []
    for it in tp['items']:
        topic = it['task'].get('topic', 'Разное')
        if topic not in topics:
            topics.append(topic)
    return render_template('tasks.html', tp=tp, topics=topics,
                           lang_code=lang_code,
                           lang_info=get_language_info(lang_code),
                           languages=get_all_languages())


@app.route('/language/<lang_code>/tasks/<int:task_id>', methods=['GET', 'POST'])
@login_required
@rate_limit('submit_solution')
def solve_task(lang_code, task_id):
    """Страница решения задачи из банка + AJAX-проверка."""
    if lang_code not in LANGUAGES:
        flash('Язык не найден', 'danger')
        return redirect(url_for('dashboard'))
    tasks = load_tasks(lang_code)
    task = get_task(lang_code, task_id)
    if not task:
        flash('Задача не найдена', 'danger')
        return redirect(url_for('language_tasks', lang_code=lang_code))

    idx = next((i for i, t in enumerate(tasks) if t['id'] == task_id), -1)
    prev_task = tasks[idx - 1] if idx > 0 else None
    next_task = tasks[idx + 1] if 0 <= idx < len(tasks) - 1 else None

    # task_id банка = обычный id задачи, lesson_id=0 — не пересекается с уроками
    progress = TaskProgress.query.filter_by(
        user_id=current_user.id, language=lang_code,
        lesson_id=0, task_id=task_id).first()

    if request.method == 'POST':
        user_code = clean_code(request.form.get('code', ''))
        result = check_code(user_code, task.get('check'))
        if not progress:
            progress = TaskProgress(user_id=current_user.id,
                                    language=lang_code, lesson_id=0,
                                    task_id=task_id, completed=False,
                                    code='', attempts=0)
            db.session.add(progress)
        progress.attempts += 1

        if result['success']:
            first = not progress.completed
            progress.completed = True
            progress.code = user_code
            xp_gained = task.get('xp', 10) if first else 0
            if first:
                current_user.xp += xp_gained
                check_streak_rewards(current_user)
                recalc_level(current_user)
            db.session.commit()
            new_achievements = grant_achievements(current_user,
                                                  language=lang_code)
            return jsonify({
                'success': True,
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'xp': current_user.xp,
                'xp_gained': xp_gained,
                'level': current_user.level,
                'new_achievements': [a.name for a in new_achievements]
            })
        db.session.commit()
        attempts = progress.attempts
        hint = task['hints'][0] if (attempts >= 3 and task.get('hints')) else None
        solution = task.get('solution') if attempts >= 4 else None
        return jsonify({
            'success': False,
            'stdout': result['stdout'],
            'stderr': result['stderr'],
            'attempts': attempts,
            'hint': hint,
            'solution': solution
        })

    initial_code = (progress.code if progress and progress.code
                    else task.get('initial_code', ''))
    attempts = progress.attempts if progress else 0
    hint = task['hints'][0] if (attempts >= 3 and task.get('hints')) else None
    solution = task.get('solution') if attempts >= 4 else None

    return render_template('task.html', task=task,
                           initial_code=initial_code, hint=hint,
                           solution=solution, progress=progress,
                           prev_task=prev_task, next_task=next_task,
                           lang_code=lang_code,
                           lang_info=get_language_info(lang_code),
                           file_name=get_file_ext(lang_code))


@app.route('/sandbox', methods=['GET', 'POST'])
@app.route('/sandbox/<lang_code>', methods=['GET', 'POST'])
@login_required
@rate_limit('run_code')
def sandbox(lang_code=None):
    """Песочница: запускает код на любом из языков платформы."""
    available = sandbox_status()
    langs = get_sandbox_langs()
    for item in langs:
        item['available'] = bool(available.get(item['code']))

    if request.method == 'POST':
        # фронт шлёт JSON, подстрахуемся и читаем form-data тоже
        payload = (request.get_json(silent=True) or {}) if request.is_json \
            else request.form
        raw_code = payload.get('code', '') or ''
        if len(raw_code) > MAX_CODE_LENGTH:
            return jsonify({
                'success': False, 'stdout': '', 'lang': 'python',
                'stderr': 'Слишком большой код для песочницы (лимит %d '
                          'символов).' % MAX_CODE_LENGTH,
            })
        code = clean_code(raw_code)
        lang = (payload.get('lang') or lang_code or
                request.args.get('lang') or 'python').strip()
        if lang not in SANDBOX_TYPES:
            return jsonify({
                'success': False, 'stdout': '', 'lang': 'python',
                'stderr': 'Неизвестный язык для песочницы.',
            }), 400

        example = get_sandbox_example(lang)
        if not available.get(lang):
            return jsonify({
                'success': False,
                'stdout': '',
                'lang': lang,
                'no_toolchain': True,
                'stderr': ('Для запуска на этом языке нужен тулчейн. ' +
                           (example.get('hint') or '')),
            })

        result = run_sandbox_code(code, timeout=sandbox_timeout(lang),
                                  lang=lang)
        limit = 20000
        output = {
            'success': bool(result.get('success')),
            'stdout': (result.get('stdout') or '')[:limit],
            'stderr': (result.get('stderr') or '')[:limit],
            'lang': lang,
            'no_toolchain': bool(result.get('no_toolchain') or
                                 result.get('no_node')),
        }
        if output['no_toolchain']:
            output['success'] = False
            output['stderr'] = ('Для запуска на этом языке нужен тулчейн. ' +
                                (example.get('hint') or ''))
        return jsonify(output)

    active = lang_code or request.args.get('lang') or 'python'
    if active not in SANDBOX_TYPES:
        flash('Такого языка в песочнице нет', 'warning')
        return redirect(url_for('sandbox'))

    return render_template('sandbox.html',
                           sandbox_langs=langs,
                           active_lang=active,
                           active_info=get_language_info(active),
                           example=get_sandbox_example(active),
                           toolchain_ok=bool(available.get(active)),
                           timeout=sandbox_timeout(active))


@app.route('/profile')
@login_required
def profile():
    grant_achievements(current_user)
    achievements = UserAchievement.query.filter_by(
        user_id=current_user.id
    ).all()
    earned_ids = [ta.achievement_id for ta in achievements]
    all_achievements = Achievement.query.all()
    progress_records = LessonProgress.query.filter_by(
        user_id=current_user.id
    ).all()
    test_results = TestResult.query.filter_by(
        user_id=current_user.id
    ).order_by(TestResult.timestamp.desc()).all()
    status_emoji = get_status_emoji(current_user.streak_count)
    status_name = get_status_name(current_user.streak_count)

    return render_template('profile.html',
                           achievements=all_achievements,
                           earned_ids=earned_ids,
                           progress_records=progress_records,
                           test_results=test_results,
                           user=current_user,
                           status_emoji=status_emoji,
                           status_name=status_name)


@app.route('/leaderboard')
def leaderboard():
    update_leaderboard()
    entries = LeaderboardEntry.query.order_by(
        LeaderboardEntry.xp.desc()
    ).limit(50).all()
    return render_template('leaderboard.html', entries=entries,
                           current_user=current_user)


@app.route('/cheat_sheet')
@app.route('/cheat_sheet/<lang_code>')
def cheat_sheet(lang_code=None):
    from utils.language_manager import LANGUAGES
    if lang_code:
        info = LANGUAGES.get(lang_code)
        cheats = get_cheatsheets(lang_code) if info else None
        if not info or not cheats:
            flash('Шпаргалки для этого языка не найдены', 'warning')
            return redirect(url_for('cheat_sheet'))
        return render_template('cheat_sheet.html',
                               languages={lang_code: info},
                               sheets={lang_code: cheats},
                               only_lang=lang_code)
    languages = {}
    sheets = {}
    for code, info in LANGUAGES.items():
        cheats = get_cheatsheets(code)
        if cheats:
            languages[code] = info
            sheets[code] = cheats
    return render_template('cheat_sheet.html',
                           languages=languages, sheets=sheets)


@app.route('/module_test/<lang_code>/<int:module_id>', methods=['GET', 'POST'])
@login_required
@rate_limit('submit_test')
def module_test(lang_code, module_id):
    """Тест по модулю: открывается после уроков модуля."""
    if lang_code not in LANGUAGES:
        flash('Язык не найден', 'danger')
        return redirect(url_for('dashboard'))
    lang_data = load_language(lang_code)
    module = get_module(lang_code, module_id) if lang_data else None
    if not lang_data or not module:
        flash('Модуль не найден', 'danger')
        return redirect(url_for('dashboard'))

    test = module.get('test') or {}
    questions = test.get('questions', [])
    if not questions:
        flash('Тест для этого модуля пока не готов', 'warning')
        return redirect(url_for('language_course', lang_code=lang_code))

    if request.method == 'POST':
        score = 0
        for i, quest in enumerate(questions, 1):
            user_answer = request.form.get(f'q{i}', '').strip()
            if user_answer == str(quest.get('correct', -1)):
                score += 1
        total = len(questions)
        percent = round(score / total * 100) if total else 0
        passed = percent >= 60

        result = TestResult(user_id=current_user.id, score=score,
                            language=lang_code,
                            level=3 if percent >= 80 else
                            2 if percent >= 60 else 1)
        db.session.add(result)
        current_user.xp += score * 15
        check_streak_rewards(current_user)
        recalc_level(current_user)
        db.session.commit()
        grant_achievements(current_user, language=lang_code)

        if passed:
            flash(f'Модуль «{module["title"]}» пройден! '
                  f'Результат: {score}/{total} ({percent}%). '
                  f'Следующий модуль открыт!', 'success')
        else:
            flash(f'Результат: {score}/{total} ({percent}%). '
                  f'Для зачёта нужно минимум 60%. '
                  f'Повтори уроки модуля и попробуй снова.', 'warning')
        return redirect(url_for('language_course', lang_code=lang_code))

    lang_info = get_language_info(lang_code)
    return render_template('module_test.html',
                           module=module, questions=questions,
                           test_title=test.get('title', 'Тест модуля'),
                           lang_code=lang_code, lang_info=lang_info)


def update_leaderboard(language='python'):
    users = User.query.order_by(User.xp.desc()).limit(50).all()
    for rank, user in enumerate(users, 1):
        entry = LeaderboardEntry.query.filter_by(
            user_id=user.id, language=language).first()
        if not entry:
            entry = LeaderboardEntry(
                user_id=user.id, language=language, rank=rank, xp=user.xp)
        else:
            entry.rank = rank
            entry.xp = user.xp
        entry.last_updated = datetime.now()
        db.session.add(entry)
    db.session.commit()


def ensure_schema():
    """Добавляет недостающие колонки, если база создана старой версией."""
    from sqlalchemy import text
    expected = {
        'users': {'current_language': "VARCHAR(20) DEFAULT 'python'"},
        'leaderboard': {'language': "VARCHAR(20) DEFAULT 'python'"},
        'test_results': {'language': "VARCHAR(20) DEFAULT 'python'"},
        'lesson_progress': {'language': "VARCHAR(20) DEFAULT 'python'",
                            'module_id': 'INTEGER DEFAULT 0',
                            'best_code': 'TEXT DEFAULT '''},
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


def init_achievements():
    if Achievement.query.count() == 0:
        definitions = [
            {'name': 'Первый шаг', 'description': 'Зарегистрироваться',
             'icon': '👶', 'xp_reward': 10, 'condition_type': 'register',
             'condition_value': 1},
            {'name': 'Тестировщик', 'description': 'Сдать входной тест',
             'icon': '📝', 'xp_reward': 20, 'condition_type': 'test',
             'condition_value': 1},
            {'name': 'Ученик', 'description': 'Пройти первый урок',
             'icon': '📚', 'xp_reward': 30, 'condition_type': 'lesson',
             'condition_value': 1},
            {'name': 'Эксперт', 'description': 'Пройти все уроки',
             'icon': '🎓', 'xp_reward': 100, 'condition_type': 'all_lessons',
             'condition_value': 1},
            {'name': 'Кодер', 'description': 'Написать 10 правильных решений',
             'icon': '💻', 'xp_reward': 50, 'condition_type': '10_correct',
             'condition_value': 10},
            {'name': 'Без ошибок', 'description': 'Пройти урок с первого раза',
             'icon': '🎯', 'xp_reward': 40, 'condition_type': 'first_try',
             'condition_value': 1},
            {'name': 'Ставровец', 'description': '7 дней подряд',
             'icon': '🌊', 'xp_reward': 70, 'condition_type': 'streak_7',
             'condition_value': 7},
            {'name': 'Солнечный', 'description': '30 дней подряд',
             'icon': '☀️', 'xp_reward': 150, 'condition_type': 'streak_30',
             'condition_value': 30},
            {'name': 'Бессмертный', 'description': '100 дней подряд',
             'icon': '💎', 'xp_reward': 300, 'condition_type': 'streak_100',
             'condition_value': 100},
            {'name': 'Легенда', 'description': '365 дней подряд',
             'icon': '🔥', 'xp_reward': 1000, 'condition_type': 'streak_365',
             'condition_value': 365},
        ]
        for defn in definitions:
            ach = Achievement(**defn)
            db.session.add(ach)
        db.session.commit()


if __name__ == '__main__':
    import socket
    with app.app_context():
        db.create_all()
        ensure_schema()
        init_achievements()
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    port = app.config['PORT']
    local_only = app.config['HOST'] in ('127.0.0.1', 'localhost')
    if local_only:
        print(f"\n=== Codigo запущен ===")
        print(f"   http://127.0.0.1:{port}")
        print(f"   (только на этом компьютере — в сеть не открыт)")
        print(f"   Открыть для других устройств: запусти с HOST=0.0.0.0\n")
    else:
        print(f"\n=== Codigo запущен и доступен другим устройствам ===")
        print(f"   http://{local_ip}:{port}")
        print(f"   http://127.0.0.1:{port} (этот компьютер)\n")
    # не отдаём наружу версию Python и Werkzeug (мелочь, но лишний след)
    try:
        from werkzeug.serving import WSGIRequestHandler

        WSGIRequestHandler.server_version = 'Codigo'
        WSGIRequestHandler.sys_version = ''
    except Exception:
        pass
    if app.config['HOST'] not in ('127.0.0.1', 'localhost'):
        print('⚠  Сервер открыт для сети. Включай это только для проверки')
        print('   на своём устройстве: чужие люди могут регистрироваться.')
        if not app.config['SESSION_COOKIE_SECURE']:
            print('   Для публичного доступа включи HTTPS и COOKIE_SECURE=1.')
        print('   Отладочная консоль Werkzeug выключена намеренно:')
        print('   она даёт выполнить любой код на этом компьютере.')
    # debug=False: отладочный режим Werkzeug позволяет выполнить код
    # на сервере через браузер, поэтому включён только по FLASK_DEBUG=1
    app.run(debug=app.config['DEBUG'], use_reloader=False,
            host=app.config['HOST'], port=app.config['PORT'])
