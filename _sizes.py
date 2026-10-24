# -*- coding: utf-8 -*-
"""Temp: байтовые размеры файлов языков (бэкап и текущие)."""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))

for lang in ['python', 'javascript', 'java', 'cpp', 'go', 'csharp',
             'typescript', 'php', 'rust']:
    a = os.path.join(ROOT, '_backup_lang', lang + '.json')
    b = os.path.join(ROOT, 'data', 'languages', lang + '.json')
    ba = os.path.getsize(a)
    bb = os.path.getsize(b)
    print(f'{lang:11} {ba:6} -> {bb:6} байт  ({bb - ba:+d})')
