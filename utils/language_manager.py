import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'languages')

LANGUAGES = {
    'python': {'name': 'Python', 'icon': '🐍', 'color': '#3776AB'},
    'javascript': {'name': 'JavaScript', 'icon': '🟨', 'color': '#F7DF1E'},
    'java': {'name': 'Java', 'icon': '☕', 'color': '#ED8B00'},
    'cpp': {'name': 'C++', 'icon': '⚙️', 'color': '#00599C'},
    'go': {'name': 'Go', 'icon': '🐹', 'color': '#00ADD8'},
    'csharp': {'name': 'C#', 'icon': '💜', 'color': '#9B4F96'},
    'typescript': {'name': 'TypeScript', 'icon': '📘', 'color': '#3178C6'},
    'php': {'name': 'PHP', 'icon': '🟡', 'color': '#777BB4'},
    'rust': {'name': 'Rust', 'icon': '🦀', 'color': '#DEA584'},
    'sql': {'name': 'SQL', 'icon': '🗄️', 'color': '#4A9EFF'},
}
# расширения файлов для редактора в уроках
FILE_EXT = {
    'python': 'main.py',
    'javascript': 'main.js',
    'java': 'Main.java',
    'cpp': 'main.cpp',
    'go': 'main.go',
    'csharp': 'Program.cs',
    'typescript': 'main.ts',
    'php': 'main.php',
    'rust': 'main.rs',
    'sql': 'query.sql',
}

_language_cache = {}

def load_language(lang_code):
    """Загружает данные языка из JSON файла.

    lang_code приходит из адреса страницы, поэтому сверяем его с белым
    списком: иначе через «..» можно попросить файл за пределами data.
    """
    if lang_code not in LANGUAGES:
        return None
    if lang_code in _language_cache:
        return _language_cache[lang_code]

    file_path = os.path.join(DATA_DIR, f'{lang_code}.json')
    if not os.path.exists(file_path):
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    _language_cache[lang_code] = data.get(lang_code, data)
    return _language_cache[lang_code]

def invalidate_cache(lang_code=None):
    if lang_code:
        _language_cache.pop(lang_code, None)
        _tasks_cache.pop(lang_code, None)
    else:
        _language_cache.clear()
        _tasks_cache.clear()

def get_language_info(lang_code):
    """Возвращает информацию о языке"""
    return LANGUAGES.get(lang_code, {})

def get_file_ext(lang_code):
    return FILE_EXT.get(lang_code, 'main.py')

def get_all_languages():
    """Возвращает список всех языков с агрегированной статистикой"""
    result = []
    for code, info in LANGUAGES.items():
        lang_data = load_language(code)
        if not lang_data:
            continue
        modules = lang_data.get('modules', [])
        total_lessons = sum(len(m.get('lessons', [])) for m in modules)
        total_tasks = sum(len(l.get('tasks', []))
                          for m in modules for l in m.get('lessons', []))
        lesson_tests = sum(len(l.get('test', []))
                           for m in modules for l in m.get('lessons', []))
        entrance = len(lang_data.get('entrance_test', []))
        practice_count = len(load_tasks(code))
        final_modules = [m for m in modules
                         if 'проект' in m.get('title', '').lower()]
        result.append({
            'code': code,
            'name': info['name'],
            'icon': info['icon'],
            'color': info['color'],
            'description': lang_data.get('description', ''),
            'difficulty': lang_data.get('difficulty', ''),
            'final_project': lang_data.get('final_project', ''),
            'modules_count': len(modules),
            'lessons_count': total_lessons,
            'tasks_count': total_tasks + practice_count,
            'practice_count': practice_count,
            'tests_count': lesson_tests + entrance,
            'cheatsheets_count': len(lang_data.get('cheatsheets', [])),
            'has_final_project': bool(final_modules
                                      or lang_data.get('final_project')),
        })
    return result

def get_module(lang_code, module_id):
    """Возвращает модуль по ID"""
    lang_data = load_language(lang_code)
    if not lang_data:
        return None
    for module in lang_data.get('modules', []):
        if module['id'] == module_id:
            return module
    return None

def get_lesson(lang_code, lesson_id):
    """Возвращает урок по ID и модуль, в котором он находится"""
    lang_data = load_language(lang_code)
    if not lang_data:
        return None, None
    for module in lang_data.get('modules', []):
        for lesson in module.get('lessons', []):
            if lesson['id'] == lesson_id:
                return lesson, module
    return None, None

def get_entrance_test(lang_code):
    """Возвращает входной тест для языка"""
    lang_data = load_language(lang_code)
    if not lang_data:
        return []
    return lang_data.get('entrance_test', [])

def get_cheatsheets(lang_code):
    """Возвращает шпаргалки языка"""
    lang_data = load_language(lang_code)
    if not lang_data:
        return []
    return lang_data.get('cheatsheets', [])

# ---------- Банк практических задач (data/tasks/<lang>.json) ----------
TASKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         'data', 'tasks')
_tasks_cache = {}


def load_tasks(lang_code):
    """Возвращает банк задач языка (список словарей)."""
    if lang_code in _tasks_cache:
        return _tasks_cache[lang_code]
    path = os.path.join(TASKS_DIR, f'{lang_code}.json')
    tasks = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            tasks = json.load(f).get('tasks', [])
    _tasks_cache[lang_code] = tasks
    return tasks


def get_task(lang_code, task_id):
    """Возвращает задачу из банка по id."""
    for t in load_tasks(lang_code):
        if t['id'] == task_id:
            return t
    return None


def get_task_progress(user, lang_code):
    """Задачи языка + отметки выполнения пользователем."""
    from models import TaskProgress
    rows = TaskProgress.query.filter_by(
        user_id=user.id, language=lang_code).all()
    by_id = {t.task_id: t for t in rows}
    tasks = load_tasks(lang_code)
    done = 0
    items = []
    for t in tasks:
        p = by_id.get(t['id'])
        ok = bool(p and p.completed)
        if ok:
            done += 1
        items.append({'task': t, 'progress': p, 'completed': ok})
    total = len(tasks)
    return {'items': items, 'done': done, 'total': total,
            'percent': round(done / total * 100) if total else 0}

def get_total_lessons(lang_code):
    """Возвращает общее количество уроков"""
    lang_data = load_language(lang_code)
    if not lang_data:
        return 0
    return sum(len(m.get('lessons', [])) for m in lang_data.get('modules', []))

def get_total_tasks(lang_code):
    """Возвращает общее количество задач в курсе"""
    lang_data = load_language(lang_code)
    if not lang_data:
        return 0
    return sum(len(t.get('tasks', []))
               for m in lang_data.get('modules', [])
               for t in m.get('lessons', []))

def get_flat_lessons(lang_code):
    """Возвращает плоский список уроков курса по порядку."""
    lang_data = load_language(lang_code)
    if not lang_data:
        return []
    result = []
    for module in lang_data.get('modules', []):
        for lesson in module.get('lessons', []):
            item = dict(lesson)
            item['module_id'] = module.get('id')
            item['module_title'] = module.get('title')
            result.append(item)
    return result

def get_lesson_progress(user, lang_code):
    """Возвращает прогресс пользователя по урокам языка"""
    from models import LessonProgress
    progress = LessonProgress.query.filter_by(
        user_id=user.id,
        language=lang_code
    ).all()

    completed_ids = {p.lesson_id for p in progress if p.completed}
    total = get_total_lessons(lang_code)

    # следующий урок: первый непройденный, либо самый первый урок курса
    flat = get_flat_lessons(lang_code)
    next_lesson = None
    for lsn in flat:
        if lsn['id'] not in completed_ids:
            next_lesson = lsn
            break
    if next_lesson is None and flat:
        next_lesson = flat[-1]

    return {
        'completed': len(completed_ids),
        'total': total,
        'percent': round(len(completed_ids) / total * 100) if total > 0 else 0,
        'completed_ids': completed_ids,
        'next_lesson': next_lesson['id'] if next_lesson else None,
        'next_lesson_title': next_lesson['title'] if next_lesson else None,
        'finished': bool(total) and len(completed_ids) >= total
    }

def get_module_progress(user, lang_code, module_id):
    """Возвращает прогресс по конкретному модулю"""
    from models import LessonProgress
    module = get_module(lang_code, module_id)
    lessons = module.get('lessons', []) if module else []
    progress = LessonProgress.query.filter_by(
        user_id=user.id, language=lang_code,
        module_id=module_id
    ).all()
    by_id = {p.lesson_id: p for p in progress}
    items = []
    done = 0
    for lsn in lessons:
        p = by_id.get(lsn['id'])
        items.append({'lesson': lsn, 'completed': bool(p and p.completed),
                      'attempts': p.attempts if p else 0})
        if p and p.completed:
            done += 1
    total = len(lessons)
    percent = round(done / total * 100) if total else 0
    return {'items': items, 'done': done, 'total': total,
            'percent': percent, 'unlocked': True}

# ---------- Песочница (data/sandbox.json) ----------
SANDBOX_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'data', 'sandbox.json')
_sandbox_cache = {}


def load_sandbox_examples():
    """Возвращает примеры кода для песочницы по языкам."""
    if _sandbox_cache:
        return _sandbox_cache
    data = {}
    if os.path.exists(SANDBOX_FILE):
        with open(SANDBOX_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    _sandbox_cache.update(data)
    return _sandbox_cache


def get_sandbox_example(lang_code):
    """Пример (файл + стартовый код + подсказка) для конкретного языка."""
    default = {'file': FILE_EXT.get(lang_code, 'main.py'),
               'timeout': 5, 'starter': '', 'hint': ''}
    example = load_sandbox_examples().get(lang_code) or {}
    merged = dict(default)
    merged.update(example)
    return merged


def get_sandbox_langs():
    """Список языков песочницы для переключателя: код, иконка, имя, файл."""
    items = []
    for code, info in LANGUAGES.items():
        example = get_sandbox_example(code)
        items.append({
            'code': code,
            'name': info.get('name', code),
            'icon': info.get('icon', ''),
            'color': info.get('color', ''),
            'file': example.get('file', FILE_EXT.get(code, 'main.py')),
            'timeout': example.get('timeout', 5),
        })
    return items