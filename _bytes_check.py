# -*- coding: utf-8 -*-
"""Temp: точная сверка байт файла и длины текста в UTF-8."""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))

for lang in ['python', 'javascript']:
    for tag, path in [
            ('backup', os.path.join(ROOT, '_backup_lang', lang + '.json')),
            ('current', os.path.join(ROOT, 'data', 'languages',
                                     lang + '.json'))]:
        raw = open(path, 'rb').read()
        text = raw.decode('utf-8')
        print(f'{lang:11} {tag:8} bytes={len(raw):6} '
              f'text_utf8={len(text.encode("utf-8")):6} '
              f'chars={len(text):6} bom={raw[:3] == b"\\xef\\xbb\\xbf"} '
              f'backslash_u={text.count(chr(92) + "u"):4} '
              f'crlf={raw.count(bytes([13, 10])):3} '
              f'lone_cr={raw.count(bytes([13])):3}')
