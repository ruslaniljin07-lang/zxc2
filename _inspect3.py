# -*- coding: utf-8 -*-
import io
s = io.open('app.py', 'r', encoding='utf-8', newline='').read()
for needle in ['def index():', 'all_lessons =', 'def cheat_sheet():',
               'def get_flat_lessons', '@app.route']:
    idx = 0
    while True:
        i = s.find(needle, idx)
        if i == -1:
            break
        print('###', needle, '@', i)
        print(repr(s[i:i + 220]))
        print()
        idx = i + 1
        if needle != '@app.route':
            break