# -*- coding: utf-8 -*-
"""Temp: почему изменился размер python.json после пересборки шпаргалок."""
import difflib
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))

pa = os.path.join(ROOT, '_backup_lang', 'python.json')
pb = os.path.join(ROOT, 'data', 'languages', 'python.json')
old = open(pa, encoding='utf-8').read()
new = open(pb, encoding='utf-8').read()
print('символов:', len(old), '->', len(new))
print('строк:', old.count('\n') + 1, '->', new.count('\n') + 1)

sm = difflib.SequenceMatcher(None, old.splitlines(), new.splitlines())
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        for k in range(i2 - i1):
            a = old.splitlines()[i1 + k]
            b = new.splitlines()[j1 + k]
            if a != b:
                print('РАЗНЫЕ при equal:', repr(a), repr(b))
        continue
    print(f'{tag:8} старые строки {i1 + 1}-{i2}  новые {j1 + 1}-{j2}')
    for line in old.splitlines()[i1:i2]:
        print('   -', repr(line[:90]))
    for line in new.splitlines()[j1:j2]:
        print('   +', repr(line[:90]))
