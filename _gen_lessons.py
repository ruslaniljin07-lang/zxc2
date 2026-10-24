"""Собирает 30+ уроков каждого курса из банка задач.

Почему так: в банке уже 30-33 задачи с проверенными эталонами и
уровнем сложности. Урок = тема + задание с разбором, поэтому каждый
урок рабочий: задание из него точно засчитывается.

Дополнительно в каждом уроке явно указана сложность (easy / medium /
hard) — она показывается в интерфейсе цветным бейджем.
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
LANG_DIR = os.path.join(ROOT, 'data', 'languages')
TASKS_DIR = os.path.join(ROOT, 'data', 'tasks')

LEVEL_TITLE = {'easy': 'Лёгкий', 'medium': 'Средний', 'hard': 'Сложный'}
LEVEL_ORDER = {'easy': 0, 'medium': 1, 'hard': 2}

# Порядок тем внутри курса: от простого к сложному
TOPIC_ORDER = ['Основы', 'Переменные', 'Типы', 'Строки', 'Условия',
               'Циклы', 'Списки', 'Массивы', 'Коллекции', 'Словари',
               'Фильтрация', 'Методы массива', 'Функции', 'Классы',
               'Агрегаты', 'GROUP BY', 'Объекты и JSON', 'Соединения',
               'JOIN', 'Ошибки']

LEVEL_ADVICE = {
    'easy': 'Уровень «Лёгкий»: повтори синтаксис и собери программу по '
            'образцу.',
    'medium': 'Уровень «Средний»: выбери подходящий алгоритм и напиши '
              'решение сам.',
    'hard': 'Уровень «Сложный»: задача как в реальной работе — собери '
            'решение из нескольких шагов.',
}


def difficulty_of(task):
    value = (task.get('difficulty') or 'easy').lower()
    return value if value in LEVEL_ORDER else 'easy'


def topic_key(topic):
    """Порядковый номер темы (для сортировки)."""
    for index, name in enumerate(TOPIC_ORDER):
        if name.lower() in (topic or '').lower():
            return index
    return len(TOPIC_ORDER)


def build_theory(task, topic):
    """Три пункта теории под конкретное задание."""
    require = (task.get('check') or {}).get('require') or []
    level = difficulty_of(task)
    points = ['Тема урока — «%s». Разберём её на задании: %s'
              % (topic.lower(), (task.get('description') or '').lower())]
    if require:
        points.append('В задании обязательно используются: %s. Именно их '
                      'ищет проверка, поэтому без них решение не '
                      'засчитается.'
                      % ', '.join('«%s»' % part for part in require))
    else:
        points.append('Проверка сравнивает результат работы программы, '
                      'поэтому важен точный ответ, а не похожий код.')
    points.append(LEVEL_ADVICE[level])
    if level == 'hard':
        points.append('Совет: разбей задачу на шаги и проверь каждый шаг '
                      'отдельно — так проще найти ошибку.')
    return points


def build_examples(task):
    """Пример решения с пояснением — чтобы было видно, как это работает."""
    require = (task.get('check') or {}).get('require') or []
    explanation = ('Разбор эталонного решения: так задание засчитывается. '
                   'Сравни со своим и найди, что упустил.')
    if require:
        explanation += ' Обрати внимание на: %s.' % ', '.join(require)
    return [{'title': 'Решение задания «%s»' % task.get('title', ''),
             'code': task.get('solution') or '',
             'explanation': explanation}]


def build_quiz(topic, tasks):
    """Вопросы теста модуля — на основе реальных конструкций курса."""
    needed = []
    for task in tasks:
        for part in (task.get('check') or {}).get('require') or []:
            if part not in needed:
                needed.append(part)
    if not needed:
        needed = ['присваивание переменной', 'условие if', 'цикл for']
    return [
        {'question': 'Что чаще всего используют в теме «%s»?' % topic,
         'options': [needed[0], 'ничего из этого', 'только теория',
                     'что-то совсем другое'],
         'correct': 0,
         'explain': 'В заданиях этого модуля проверяется: %s.'
                    % ', '.join(needed[:3])},
        {'question': 'Сколько заданий в этом модуле?',
         'options': [str(len(tasks)), 'одно', 'десять',
                     'столько же, сколько уроков'],
         'correct': 0,
         'explain': 'В модуле %d заданий — по одному на урок.' % len(tasks)},
        {'question': 'Что делать, если задание не засчитывается?',
         'options': ['Посмотреть подсказку и разобрать пример',
                     'Переписать всё с нуля', 'Пропустить модуль',
                     'Ничего'],
         'correct': 0,
         'explain': 'После третьей попытки появляется подсказка, после '
                    'четвёртой — полное решение.'},
    ]


def build_course(lang):
    """Собирает модули и уроки языка из его банка задач."""
    with open(os.path.join(TASKS_DIR, lang + '.json'), encoding='utf-8') as f:
        tasks = json.load(f)['tasks']

    groups = {}
    for task in tasks:
        groups.setdefault(task.get('topic') or 'Основы', []).append(task)
    ordered = sorted(groups.items(), key=lambda kv: topic_key(kv[0]))

    modules = []
    lesson_id = 0
    for module_id, (topic, items) in enumerate(ordered, 1):
        items.sort(key=lambda t: (LEVEL_ORDER[difficulty_of(t)],
                                  t.get('id', 0)))
        lessons = []
        for item in items:
            lesson_id += 1
            level = difficulty_of(item)
            lessons.append({
                'id': lesson_id,
                'title': '%s. %s' % (topic, item.get('title', 'Задание')),
                'description': item.get('description', ''),
                'difficulty': level,
                'level_title': LEVEL_TITLE[level],
                'theory': build_theory(item, topic),
                'examples': build_examples(item),
                'tasks': [dict(item, id=lesson_id * 100 + 1)],
                'test': [],
                'cheatsheet': topic,
                'xp_reward': 10 if level == 'easy' else 15,
            })
        hardest = max(lessons,
                      key=lambda l: LEVEL_ORDER[l['difficulty']])['difficulty']
        modules.append({
            'id': module_id,
            'title': topic,
            'description': 'Уровень модуля: %s' % LEVEL_TITLE[hardest],
            'difficulty': hardest,
            'lessons': lessons,
            'test': {'title': 'Тест: %s' % topic,
                     'questions': build_quiz(topic, items)},
        })
    return modules, lesson_id


# ------------------------- запись в файлы языков --------------------------
report = []
for lang in sorted(name[:-5] for name in os.listdir(TASKS_DIR)
                   if name.endswith('.json')):
    path = os.path.join(LANG_DIR, lang + '.json')
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)
    data = raw.get(lang, raw)

    modules, count = build_course(lang)
    levels = {'easy': 0, 'medium': 0, 'hard': 0}
    for module in modules:
        for lesson in module['lessons']:
            levels[lesson['difficulty']] += 1
    data['modules'] = modules
    data['levels'] = levels

    with open(path, 'w', encoding='utf-8', newline='') as f:
        json.dump({lang: data}, f, ensure_ascii=False, indent=1)

    report.append('%-11s уроков %2d  (лёгкий %2d, средний %2d, сложный %2d)'
                  % (lang, count, levels['easy'], levels['medium'],
                     levels['hard']))

for line in report:
    print(line)
print('всего уроков:', sum(int(line.split()[2]) for line in report))

