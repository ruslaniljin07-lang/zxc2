# -*- coding: utf-8 -*-
"""Temp: формат JSON-файлов языков (отступ, экранирование, перевод строки)."""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))

for name in sorted(os.listdir(os.path.join(ROOT, 'data', 'languages'))):
    path = os.path.join(ROOT, 'data', 'languages', name)
    raw = open(path, 'rb').read()
    text = raw.decode('utf-8')
    lines = text.splitlines()
    indent = len(lines[1]) - len(lines[1].lstrip(' ')) if len(lines) > 1 else 0
    print(f'{name:18} indent={indent} crlf={b"\\r\\n" in raw} '
          f'ends_nl={text.endswith(chr(10))} '
          f'unicode_escapes={text.count(chr(92) + "u0")} '
          f'escaped_slash={text.count(chr(92) + "/")} '
          f'size={len(raw)}')
