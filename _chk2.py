"""Temp: check helpers and task ids in _gen_banks.py (ASCII output)."""
import re

src = open('_gen_banks.py', encoding='utf-8').read()
ids = [int(x) for x in re.findall(r'add\(id=(\d+)', src)]
print('count:', len(ids))
print('missing:', sorted(set(range(1, 31)) - set(ids)))
print('go extra:', "def go(body, imports='fmt', extra=''):" in src)
print('cpp pre:', "def cpp(body, incs=(), pre=''):" in src)
print('rs pre:', "def rs(body, pre=''):" in src)
print('j extra:', "def j(body, extra=''):" in src)
print('cs extra:', "def cs(body, extra=''):" in src)