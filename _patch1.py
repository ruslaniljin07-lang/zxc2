# -*- coding: utf-8 -*-
"""Applies language-aware routing patches to app.py and templates."""
import io
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def patch(rel, old, new, required=True):
    path = os.path.join(BASE, rel)
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        src = f.read()
    if old not in src:
        if required:
            raise SystemExit('NOT FOUND in %s:\n%r' % (rel, old[:200]))
        print('  skip (already patched or absent):', rel)
        return False
    if src.count(old) != 1:
        raise SystemExit('AMBIGUOUS (%d) in %s: %r' % (src.count(old), rel, old[:120]))
    src = src.replace(old, new)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(src)
    print('  patched:', rel)
    return True


# ---------------------------------------------------------------- app.py
patch('app.py',
"""@app.route('/lessons')
@login_required
def lessons():
    lang_code = current_user.current_language or 'python'""",
"""@app.route('/lessons/<lang_code>')
@app.route('/lessons')
@login_required
def lessons(lang_code=None):
    lang_code = lang_code or current_user.current_language or 'python'""")

patch('app.py',
"""    lang_info = get_language_info(lang_code)
    return render_template('lessons.html',
                           modules=lang_data.get('modules', []),
                           progress_map=progress_map,
                           total=total, done=done,
                           lang_code=lang_code, lang_info=lang_info)""",
"""    lang_info = get_language_info(lang_code)
    return render_template('lessons.html',
                           modules=lang_data.get('modules', []),
                           progress_map=progress_map,
                           total=total, done=done,
                           lang_code=lang_code, lang_info=lang_info,
                           languages=get_all_languages())""")

patch('app.py',
"""@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def lesson(lesson_id):
    lang_code = request.args.get('lang') or current_user.current_language or 'python'""",
"""@app.route('/lesson/<lang_code>/<int:lesson_id>', methods=['GET', 'POST'])
@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def lesson(lesson_id, lang_code=None):
    lang_code = (lang_code or request.args.get('lang')
                 or current_user.current_language or 'python')""")

patch('app.py',
"""    lesson_data, module = get_lesson(lang_code, lesson_id)
    if not lesson_data:
        flash('Урок не найден', 'danger')
        return redirect(url_for('lessons'))""",
"""    lesson_data, module = get_lesson(lang_code, lesson_id)
    if not lesson_data:
        flash('Урок не найден', 'danger')
        return redirect(url_for('lessons', lang_code=lang_code))""")

patch('app.py',
"""        return redirect(url_for('language_course', lang_code=lang_code))

    lang_info = get_language_info(lang_code)
    return render_template('test.html', questions=questions,""",
"""        return redirect(url_for('language_course', lang_code=lang_code))

    lang_info = get_language_info(lang_code)
    return render_template('test.html', questions=questions,""")

# mark task progress inside the lesson POST handler
patch('app.py',
"""        if result['success']:
            progress.completed = True
            progress.best_code = user_code
            current_user.xp += lesson_data.get('xp_reward', 15)""",
"""        if result['success']:
            progress.completed = True
            progress.best_code = user_code
            # фиксируем решённую задачу в отдельной таблице
            for t_idx, t in enumerate(tasks):
                t_id = t.get('id', t_idx + 1)
                tp = TaskProgress.query.filter_by(
                    user_id=current_user.id, language=lang_code,
                    task_id=t_id).first()
                if not tp:
                    tp = TaskProgress(user_id=current_user.id,
                                      language=lang_code, task_id=t_id,
                                      completed=True, code=user_code,
                                      attempts=progress.attempts)
                    db.session.add(tp)
                else:
                    tp.completed = True
                    tp.code = user_code
                    tp.attempts = progress.attempts
            current_user.xp += lesson_data.get('xp_reward', 15)""")

# leaderboard endpoint must not crash on empty DB
patch('app.py',
"""    entries = LeaderboardEntry.query.order_by(
        LeaderboardEntry.xp.desc()
    ).limit(50).all()
    return render_template('leaderboard.html', entries=entries,
                           current_user=current_user)""",
"""    entries = LeaderboardEntry.query.order_by(
        LeaderboardEntry.xp.desc()
    ).limit(50).all()
    # если записей нет — показываем актуальный рейтинг по XP
    if not entries:
        entries = []
        for rank, usr in enumerate(
                User.query.order_by(User.xp.desc()).limit(50).all(), 1):
            entries.append({'rank': rank, 'xp': usr.xp, 'user': usr})
    return render_template('leaderboard.html', entries=entries,
                           current_user=current_user)""")

print('app.py OK')