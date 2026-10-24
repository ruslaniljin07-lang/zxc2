"""Temp: проверка состояния _gen_banks.py."""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = open('_gen_banks.py', encoding='utf-8').read()
print("task10 lit fixed:", "lit=['10']," in src)
print("task12 lit fixed:", "lit=['5']," in src)
print("task19:", 'Минимум в массиве' in src)
print("task20:", 'Среднее арифметическое' in src)
print("add(id= count:", src.count('add(id='))
import re
print("ids:", re.findall(r'add\(id=(\d+)', src))