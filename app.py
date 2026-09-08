import os
import json
from datetime import datetime, date

from flask import (Flask, render_template, request, redirect, url_for,
                   flash, jsonify)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash

from utils.code_checker import check_code, run_sandbox_code
from utils.gamification import (get_status_emoji, get_status_name,
                                get_status_color, check_streak_rewards,
                                level_progress)
from utils.level_engine import TEST_QUESTIONS, determine_level

from models import (db, User, TestResult, LessonProgress, StreakReward,
                    Achievement, UserAchievement, LeaderboardEntry)

app = Flask(__name__)
app.config.from_object('config.Config')
app.jinja_env.globals.update(enumerate=enumerate)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with open(os.path.join(os.path.dirname(__file__), 'data', 'lessons.json'),
          encoding='utf-8') as f:
    LESSONS_DATA = json.load(f)


def _find_lesson(lesson_id):
    for module in LESSONS_DATA.get('modules', []):
        for lesson in module.get('lessons', []):
            if lesson['id'] == lesson_id:
                return lesson
    return None


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


def grant_achievements(user):
    """Проверяет условия достижений и выдаёт те, что выполнены.
    Возвращает список новых достижений (каждое даёт бонусный XP)."""
    achieved_ids = {ua.achievement_id for ua in
                    UserAchievement.query.filter_by(user_id=user.id)}
    completed = LessonProgress.query.filter_by(
        user_id=user.id, completed=True).count()
    has_test = TestResult.query.filter_by(user_id=user.id).count() > 0
    first_try = LessonProgress.query.filter_by(
        user_id=user.id, completed=True, attempts=1).count() > 0
    total_lessons = sum(len(m.get('lessons', []))
                        for m in LESSONS_DATA.get('modules', []))

    new = []
    for ach in Achievement.query.all():
        if ach.id in achieved_ids:
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
    # Уровень всегда пересчитываем по накопленному XP и сразу сохраняем:
    # иначе открытие дашборда/профиля не поднимает уровень от уже набранных XP.
    recalc_level(user)
    db.session.commit()
    return new


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not username or not email or not password:
            flash('Заполните все поля', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Пароли не совпадают', 'danger')
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
        grant_achievements(user)
        flash('Регистрация прошла успешно! Войдите в аккаунт.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.now()
            db.session.commit()
            grant_achievements(user)
            flash('Добро пожаловать!', 'success')
            return redirect(url_for('dashboard'))

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

    return render_template('dashboard.html',
                           streak=streak, status_emoji=status_emoji,
                           status_name=status_name, status_color=status_color,
                           xp=current_user.xp, xp_to_next=xp_to_next,
                           level_xp=level_xp, level=current_user.level,
                           user=current_user,
                           earned_achievements=earned_achievements)


@app.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    if request.method == 'POST':
        answers = {
            'q1': request.form.get('q1', ''),
            'q2': request.form.get('q2', ''),
            'q3': request.form.get('q3', ''),
            'q4': request.form.get('q4', ''),
            'q5': request.form.get('q5', ''),
        }
        score = 0
        for key, answer in answers.items():
            correct = TEST_QUESTIONS.get(key, {}).get('correct', '')
            if answer.strip() == str(correct):
                score += 1

        level = determine_level(score)
        result = TestResult(user_id=current_user.id, score=score, level=level)
        db.session.add(result)
        current_user.level = max(current_user.level, level)
        current_user.xp += score * 20
        current_user.streak_count += 1
        check_streak_rewards(current_user)
        recalc_level(current_user)
        db.session.commit()
        grant_achievements(current_user)
        flash('Тест пройден! Счёт: {}/5. Уровень: {}'.format(score, level),
              'success')
        return redirect(url_for('dashboard'))

    return render_template('test.html', questions=TEST_QUESTIONS)


@app.route('/lessons')
@login_required
def lessons():
    progress_map = {
        p.lesson_id: p for p in LessonProgress.query.filter_by(
            user_id=current_user.id
        ).all()
    }
    total = sum(
        1 for mod in LESSONS_DATA.get('modules', [])
        for _ in mod.get('lessons', [])
    )
    done = sum(1 for p in progress_map.values() if p.completed)
    return render_template('lessons.html',
                           modules=LESSONS_DATA.get('modules', []),
                           progress_map=progress_map,
                           total=total, done=done)


@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def lesson(lesson_id):
    lesson = _find_lesson(lesson_id)
    if not lesson:
        flash('Урок не найден', 'danger')
        return redirect(url_for('dashboard'))

    # собрать плоский список уроков для навигации
    all_lessons = [l for m in LESSONS_DATA.get('modules', []) for l in m.get('lessons', [])]
    order_ids = [l['id'] for l in all_lessons]
    cur_idx = next((i for i, lid in enumerate(order_ids) if lid == lesson_id), -1)
    prev_lesson = all_lessons[cur_idx - 1] if cur_idx > 0 else None
    next_lesson = all_lessons[cur_idx + 1] if 0 <= cur_idx < len(order_ids) - 1 else None

    if request.method == 'POST':
        user_code = request.form.get('code', '')
        test_code = lesson.get('test_code', '')
        result = check_code(user_code, test_code)

        progress = LessonProgress.query.filter_by(
            user_id=current_user.id, lesson_id=lesson_id
        ).first()
        if not progress:
            progress = LessonProgress(
                user_id=current_user.id, lesson_id=lesson_id,
                completed=False, attempts=0, best_code=''
            )
            db.session.add(progress)
        progress.attempts += 1

        if result['success']:
            progress.completed = True
            progress.best_code = user_code
            current_user.xp += lesson.get('xp_reward', 50)
            check_streak_rewards(current_user)
            recalc_level(current_user)
            db.session.commit()
            new_achievements = grant_achievements(current_user)
            return jsonify({
                'success': True,
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'level': current_user.level,
                'xp': current_user.xp,
                'new_achievements': [a.name for a in new_achievements]
            })
        else:
            db.session.commit()
            # прогрессивные подсказки: 1-я и 2-я ошибки — без подсказок,
            # с 3-й ошибки — лампочка с подсказкой, с 4-й — полное решение
            hint = None
            solution = None
            attempts = progress.attempts
            if attempts >= 3 and lesson.get('hints'):
                hint = lesson['hints'][0]
            if attempts >= 4:
                solution = lesson.get('solution') or lesson.get('initial_code', '')
            return jsonify({
                'success': False,
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'attempts': attempts,
                'hint': hint,
                'solution': solution
            })

    progress = LessonProgress.query.filter_by(
        user_id=current_user.id, lesson_id=lesson_id
    ).first()
    # начальный код не показываем: ученик пишет решение сам.
    # Восстанавливаем только его собственный сохранённый код (best_code)
    initial_code = progress.best_code if (progress and progress.best_code) else ''
    # прогрессивные подсказки при повторном открытии урока:
    # с 3-й попытки — подсказка, с 4-й — полное решение
    attempts = progress.attempts if progress else 0
    hint = lesson['hints'][0] if (attempts >= 3 and lesson.get('hints')) else None
    solution = (lesson.get('solution') or lesson.get('initial_code', '')) \
        if attempts >= 4 else None

    return render_template('lesson.html', lesson=lesson,
                           initial_code=initial_code, hint=hint,
                           solution=solution, progress=progress,
                           prev_lesson=prev_lesson, next_lesson=next_lesson)


@app.route('/sandbox', methods=['GET', 'POST'])
@login_required
def sandbox():
    output = None
    if request.method == 'POST':
        # фронт шлёт JSON, подстрахуемся и читаем form-data тоже
        if request.is_json:
            code = (request.get_json(silent=True) or {}).get('code', '')
        else:
            code = request.form.get('code', '')
        result = run_sandbox_code(code)
        output = {
            'success': result['success'],
            'stdout': result['stdout'],
            'stderr': result['stderr']
        }
        return jsonify(output)
    return render_template('sandbox.html', output=output)


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
def cheat_sheet():
    return render_template('cheat_sheet.html')


def update_leaderboard():
    users = User.query.order_by(User.xp.desc()).limit(50).all()
    for rank, user in enumerate(users, 1):
        entry = LeaderboardEntry.query.filter_by(user_id=user.id).first()
        if not entry:
            entry = LeaderboardEntry(user_id=user.id, rank=rank, xp=user.xp)
        else:
            entry.rank = rank
            entry.xp = user.xp
        entry.last_updated = datetime.now()
        db.session.add(entry)
    db.session.commit()


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
    with app.app_context():
        db.create_all()
        init_achievements()
    app.run(debug=True)
