# -*- coding: utf-8 -*-
import io, os
BASE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(BASE, 'templates', 'base.html')
with open(p, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
lines = src.split('\n')
# find the duplicated injected block: starts with '<li class="nav-item dropdown">' right after dashboard li,
# ends with the lessons li that uses nav_current_language
start = None
for i, ln in enumerate(lines):
    if 'nav_current_language' in ln and 'lessons' in ln:
        start = i
        break
assert start is not None, 'anchor not found'
# walk backwards to the injected dropdown start
end = start
s = None
for j in range(start, 0, -1):
    if lines[j].strip() == '<li class="nav-item dropdown">':
        s = j
        break
assert s is not None, 'dropdown start not found'
# also remove the dashboard nav item duplicate? no. remove lines s..end (inclusive)
new_lines = lines[:s] + lines[end + 1:]
# now normalize the remaining dropdown to use nav_langs / current lang consistent vars
out = '\n'.join(new_lines)
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(out)
print('removed lines', s + 1, 'to', end + 1)