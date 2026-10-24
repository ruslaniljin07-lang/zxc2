"""Temp: состояние _gen_courses.py (ASCII-вывод)."""
src = open('_gen_courses.py', encoding='utf-8').read()
lines = src.splitlines()
for i, l in enumerate(lines, 1):
    if l.startswith('COURSES[') or l.startswith('_G') or '=====' in l:
        print(i, l)
print('---')
print('go icon repr:', repr([l for l in lines if "'name': 'Go'" in l]))
print('cheatsheet icons:', [repr(l.strip()) for l in lines
                            if l.strip().startswith("'icon': '")][:6])