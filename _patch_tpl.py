# -*- coding: utf-8 -*-
import io, os, sys
BASE = os.path.dirname(os.path.abspath(__file__))

def patch(path, old, new, count=1):
    p = os.path.join(BASE, path)
    with open(p, 'r', encoding='utf-8', newline='') as f:
        text = f.read()
    nl = '\r\n' if '\r\n' in text else '\n'
    o = old.replace('\n', nl)
    n = new.replace('\n', nl)
    if o not in text:
        print('NOT FOUND in', path)
        return False
    text = text.replace(o, n, count)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    print('OK', path)
    return True

patch('templates/base.html',
'''                        <li class="nav-item"><a class="nav-link nav-link-style {% if request.endpoint == 'test' %}active{% endif %}" href="{{ url_for('test') }}">Тест</a></li>
                        <li class="nav-item"><a class="nav-link nav-link-style {% if request.endpoint in ('lessons','lesson') %}active{% endif %}" href="{{ url_for('lessons') }}">Уроки</a></li>''',
'''                        <li class="nav-item dropdown">
                            <a class="nav-link nav-link-style dropdown-toggle" href="#" role="button"
                               data-bs-toggle="dropdown" aria-expanded="false">Курсы</a>
                            <ul class="dropdown-menu">
                                {% for nav_lang in nav_languages %}
                                <li>
                                    <a class="dropdown-item {% if nav_lang.code == nav_current_language %}active{% endif %}"
                                       href="{{ url_for('language_course', lang_code=nav_lang.code) }}">
                                        {{ nav_lang.icon }} {{ nav_lang.name }}
                                        <span class="text-muted small">· {{ nav_lang.lessons_count }} уроков</span>
                                    </a>
                                </li>
                                {% endfor %}
                            </ul>
                        </li>
                        <li class="nav-item"><a class="nav-link nav-link-style {% if request.endpoint == 'test' %}active{% endif %}" href="{{ url_for('test', lang_code=nav_current_language or 'python') }}">Тест</a></li>
                        <li class="nav-item"><a class="nav-link nav-link-style {% if request.endpoint in ('lessons','lesson') %}active{% endif %}" href="{{ url_for('lessons', lang_code=nav_current_language or 'python') }}">Уроки</a></li>''')

patch('templates/lesson.html',
'''href="{{ url_for('lesson', lesson_id=prev_lesson.id, lang=lang_code) }}"''',
'''href="{{ url_for('lesson', lang_code=lang_code, lesson_id=prev_lesson.id) }}"''')

patch('templates/lesson.html',
'''href="{{ url_for('lesson', lesson_id=next_lesson.id, lang=lang_code) }}"''',
'''href="{{ url_for('lesson', lang_code=lang_code, lesson_id=next_lesson.id) }}"''')

patch('templates/lesson.html',
'''<a class="np-all" href="{{ url_for('lessons') }}">''',
'''<a class="np-all" href="{{ url_for('lessons', lang_code=lang_code) }}">''')

patch('templates/dashboard.html',
'''<a href="{{ url_for('lessons') }}" class="btn btn-primary btn-xl">''',
'''<a href="{{ url_for('lessons', lang_code=lang_code) }}" class="btn btn-primary btn-xl">''')

patch('templates/dashboard.html',
'''<a href="{{ url_for('test') }}" class="btn btn-ghost btn-xl">''',
'''<a href="{{ url_for('test', lang_code=lang_code) }}" class="btn btn-ghost btn-xl">''')