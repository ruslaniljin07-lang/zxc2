# -*- coding: utf-8 -*-
"""Temp: чем отличается старый файл от нового на уровне текста."""
import difflib
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))

for lang in ['python', 'javascript', 'java', 'cpp', 'go']:
    a = open(os.path.join(ROOT, '_backup_lang', lang + '.json'),
             encoding='utf-8').read().splitlines()
    b = open(os.path.join(ROOT, 'data', 'languages', lang + '.json'),
             encoding='utf-8').read().splitlines()
    diff = list(difflib.unified_diff(a, b, lineterm='', n=0))
    removed = [l for l in diff if l.startswith('-') and not l.startswith('---')]
    added = [l for l in diff if l.startswith('+') and not l.startswith('+++')]
    print(f'{lang:11} строк убрано: {len(removed):4}  добавлено: {len(added):4}')
    if lang == 'python':
        print('  примеры удалённых строк:')
        for line in removed[:6]:
            print('   ', repr(line))
        print('  индентация шпаргалок в старом файле:',
              repr(removed[1]) if len(removed) > 1 else '')
