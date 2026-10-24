# -*- coding: utf-8 -*-
import io
s = io.open('app.py', 'r', encoding='utf-8', newline='').read()
for needle in ['get_total_tasks', "@app.route('/lessons')",
               "@app.route('/lesson/<int:lesson_id>'",
               'progress = LessonProgress.query.filter_by']:
    i = s.find(needle)
    print('###', needle, '@', i)
    print(repr(s[max(0, i - 60):i + 300]))
    print()