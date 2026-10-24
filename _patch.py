# -*- coding: utf-8 -*-
"""Helper to patch templates with CRLF line endings."""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)


def patch(rel, pairs):
    path = os.path.join(BASE, rel)
    with open(path, 'r', encoding='utf-8', newline='') as f:
        text = f.read()
    for old, new in pairs:
        if old not in text:
            print(f"  !! NOT FOUND in {rel}: {old[:70]!r}")
            continue
        text = text.replace(old, new, 1)
        print(f"  ok {rel}: {old[:50]!r}")
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


NAV_OLD = (
    "                        <li class=\"nav-item\"><a class=\"nav-link nav-link-style {% if request.endpoint == 'dashboard' %}active{% endif %}\" href=\"{{ url_for('dashboard') }}\">Дашборд</a></li>\r\n"
    "                        <li class=\"nav-item\"><a class=\"nav-link nav-link-style {% if request.endpoint == 'test' %}active{% endif %}\" href=\"{{ url_for('test') }}\">Тест</a></li>\r\n"
    "                        <li class=\"nav-item\"><a class=\"nav-link nav-link-style {% if request.endpoint in ('lessons','lesson') %}active{% endif %}\" href=\"{{ url_for('lessons') }}\">Уроки</a></li>\r\n"
)

NAV_NEW = (
    "                        <li class=\"nav-item\"><a class=\"nav-link nav-link-style {% if request.endpoint == 'dashboard' %}active{% endif %}\" href=\"{{ url_for('dashboard') }}\">Дашборд</a></li>\r\n"
    "                        <li class=\"nav-item dropdown\">\r\n"
    "                            <a class=\"nav-link nav-link-style dropdown-toggle\" href=\"#\" role=\"button\" data-bs-toggle=\"dropdown\" aria-expanded=\"false\">Курсы</a>\r\n"
    "                            <ul class=\"dropdown-menu\">\r\n"
    "                                {% for nav_lang in nav_languages %}\r\n"
    "                                <li><a class=\"dropdown-item {% if nav_lang.code == nav_current_language %}active{% endif %}\" href=\"{{ url_for('language_course', lang_code=nav_lang.code) }}\">{{ nav_lang.icon }} {{ nav_lang.name }} <span class=\"text-muted small\">· {{ nav_lang.lessons_count }} ур.</span></a></li>\r\n"
    "                                {% endfor %}\r\n"
    "                            </ul>\r\n"
    "                        </li>\r\n"
    "                        <li class=\"nav-item\"><a class=\"nav-link nav-link-style {% if request.endpoint == 'test' %}active{% endif %}\" href=\"{{ url_for('test', lang_code=nav_current_language or 'python') }}\">Тест</a></li>\r\n"
    "                        <li class=\"nav-item\"><a class=\"nav-link nav-link-style {% if request.endpoint in ('lessons','lesson') %}active{% endif %}\" href=\"{{ url_for('lessons', lang_code=nav_current_language or 'python') }}\">Уроки</a></li>\r\n"
)

patch('templates/base.html', [(NAV_OLD, NAV_NEW)])

patch('templates/lesson.html', [
    ("href=\"{{ url_for('lesson', lesson_id=prev_lesson.id, lang=lang_code) }}\"",
     "href=\"{{ url_for('lesson', lang_code=lang_code, lesson_id=prev_lesson.id) }}\""),
    ("href=\"{{ url_for('lessons') }}\"",
     "href=\"{{ url_for('lessons', lang_code=lang_code) }}\""),
    ("href=\"{{ url_for('lesson', lesson_id=next_lesson.id, lang=lang_code) }}\"",
     "href=\"{{ url_for('lesson', lang_code=lang_code, lesson_id=next_lesson.id) }}\""),
])

patch('templates/dashboard.html', [
    ("<a href=\"{{ url_for('lessons') }}\" class=\"btn btn-primary btn-xl\">",
     "<a href=\"{{ url_for('lessons', lang_code=user.current_language or 'python') }}\" class=\"btn btn-primary btn-xl\">"),
    ("<a href=\"{{ url_for('test') }}\" class=\"btn btn-ghost btn-xl\">",
     "<a href=\"{{ url_for('test', lang_code=user.current_language or 'python') }}\" class=\"btn btn-ghost btn-xl\">"),
])

print("DONE")