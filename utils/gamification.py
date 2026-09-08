from models import db, StreakReward
from datetime import datetime

STATUS_THRESHOLDS = [7, 14, 30, 60, 100, 180, 365]


def get_status_emoji(streak):
    if streak >= 180:
        return '🔥'
    elif streak >= 60:
        return '💎'
    elif streak >= 30:
        return '☀️'
    elif streak >= 7:
        return '🌊'
    elif streak >= 1:
        return '🌱'
    return '🌊'


def get_status_name(streak):
    if streak >= 180:
        return 'Огненный'
    elif streak >= 60:
        return 'Изумрудный'
    elif streak >= 30:
        return 'Солнечный'
    elif streak >= 7:
        return 'Глубокий'
    elif streak >= 1:
        return 'Новый'
    return 'Новичок'


def get_status_color(streak):
    if streak >= 180:
        return '#e74c3c'
    elif streak >= 60:
        return '#00b8d4'
    elif streak >= 30:
        return '#f1c40f'
    elif streak >= 7:
        return '#27ae60'
    elif streak >= 1:
        return '#3498db'
    return '#95a5a6'


def calculate_xp_for_next_level(xp):
    """Сколько XP не хватает до следующего уровня (для совместимости)."""
    _, need = level_progress(xp)
    return need


def level_progress(xp):
    """Возвращает (xp_накоплено_в_текущем_уровне, xp_нужно_до_следующего)."""
    left = xp
    level = 0
    need = 100
    while left >= need:
        left -= need
        level += 1
        need = 100 * (level + 1) ** 2
    return left, need


def check_streak_rewards(user):
    if user.streak_count >= 365:
        status = 'legendary'
    elif user.streak_count >= 100:
        status = 'epic'
    elif user.streak_count >= 30:
        status = 'rare'
    else:
        status = 'common'

    xp_bonus = {'common': 50, 'rare': 150, 'epic': 300, 'legendary': 500}.get(status, 0)
    if xp_bonus > 0:
        user.xp += xp_bonus

    for threshold in STATUS_THRESHOLDS:
        if user.streak_count >= threshold:
            existing = StreakReward.query.filter_by(
                user_id=user.id, days=threshold
            ).first()
            if not existing:
                reward = StreakReward(
                    user_id=user.id,
                    days=threshold,
                    reward_type=status,
                    reward_value=xp_bonus
                )
                db.session.add(reward)


def get_unlocked_achievements():
    return [
        {'id': 1, 'name': 'Первый шаг', 'desc': 'Зарегистрироваться', 'icon': '👶', 'xp': 10, 'type': 'register'},
        {'id': 2, 'name': 'Тестировщик', 'desc': 'Сдать входной тест', 'icon': '📝', 'xp': 20, 'type': 'test'},
        {'id': 3, 'name': 'Ученик', 'desc': 'Пройти первый урок', 'icon': '📚', 'xp': 30, 'type': 'lesson'},
        {'id': 4, 'name': 'Эксперт', 'desc': 'Пройти все уроки', 'icon': '🎓', 'xp': 100, 'type': 'all_lessons'},
        {'id': 5, 'name': 'Кодер', 'desc': 'Написать 10 правильных решений', 'icon': '💻', 'xp': 50, 'type': '10_correct'},
        {'id': 6, 'name': 'Без ошибок', 'desc': 'Пройти урок с первого раза', 'icon': '🎯', 'xp': 40, 'type': 'first_try'},
        {'id': 7, 'name': 'Ставровец', 'desc': '7 дней подряд', 'icon': '🌊', 'xp': 70, 'type': 'streak_7'},
        {'id': 8, 'name': 'Солнечный', 'desc': '30 дней подряд', 'icon': '☀️', 'xp': 150, 'type': 'streak_30'},
        {'id': 9, 'name': 'Бессмертный', 'desc': '100 дней подряд', 'icon': '💎', 'xp': 300, 'type': 'streak_100'},
        {'id': 10, 'name': 'Легенда', 'desc': '365 дней подряд', 'icon': '🔥', 'xp': 1000, 'type': 'streak_365'},
    ]
