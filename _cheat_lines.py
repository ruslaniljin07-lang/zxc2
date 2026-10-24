# -*- coding: utf-8 -*-
"""Temp: номера строк с 'cheatsheets' в файлах языков."""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))

for name in sorted(os.listdir(os.path.join(ROOT, 'data', 'languages'))):
    path = os.path.join(ROOT, 'data', 'languages', name)
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    hits = [i + 1 for i, l in enumerate(lines) if 'cheatsheets' in l]
    print(f'{name:18} lines={len(lines):5} cheatsheet_lines={hits}')
