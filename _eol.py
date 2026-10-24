# -*- coding: utf-8 -*-
import io
import os
for f in ['templates/base.html', 'templates/index.html', 'templates/dashboard.html',
          'templates/lesson.html', 'templates/language_course.html',
          'templates/lessons.html', 'templates/test.html', 'templates/cheat_sheet.html',
          'templates/leaderboard.html', 'static/style.css']:
    d = io.open(f, 'rb').read()
    print(f, 'CRLF' if b'\r\n' in d else 'LF', len(d))