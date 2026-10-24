"""Temp: какие id отсутствуют в банке go."""
import json

with open('data/tasks/go.json', encoding='utf-8') as f:
    tasks = json.load(f)['tasks']
ids = sorted(t['id'] for t in tasks)
print('go ids:', ids)
print('missing:', sorted(set(range(1, 31)) - set(ids)))
for t in tasks:
    if t['id'] in (16, 25, 26):
        print(t['id'], t['title'], '| check:', list(t['check'].keys()))