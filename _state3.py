"""Temp: inspection of language/task data schema."""
import json
import os
import collections
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))

for name in sorted(os.listdir(os.path.join(ROOT, 'data', 'languages'))):
    if not name.endswith('.json'):
        continue
    with open(os.path.join(ROOT, 'data', 'languages', name), encoding='utf-8') as f:
        raw = json.load(f)
    code = os.path.splitext(name)[0]
    data = raw.get(code, raw)
    print('=' * 70)
    print('LANG', name, '| keys:', sorted(data.keys()))
    print('  description:', str(data.get('description'))[:60])
    print('  difficulty:', data.get('difficulty'),
          '| final_project:', str(data.get('final_project'))[:50])
    print('  entrance_test:', len(data.get('entrance_test', [])))
    q = data.get('entrance_test', [])
    if q:
        print('  question keys:', sorted(q[0].keys()))
        print('  question sample:', json.dumps(q[0], ensure_ascii=False)[:220])
    for m in data.get('modules', []):
        print(f"  MODULE {m.get('id')}: {m.get('title')} [{len(m.get('lessons', []))} lessons]"
              f" keys={sorted(m.keys())}")
        for l in m.get('lessons', []):
            print(f"     lesson {l.get('id')}: {str(l.get('title'))[:45]}"
                  f" tasks={len(l.get('tasks', []))} test={len(l.get('test', []))}"
                  f" keys={sorted(l.keys())}")
    for c in data.get('cheatsheets', []):
        print('  CHEAT:', str(c.get('title'))[:40], '| keys:', sorted(c.keys()),
              '| items/len:', len(c.get('items', c.get('sections', [])) or []))
    print('  cheatsheet sample:', json.dumps(data.get('cheatsheets', [{}])[0],
                                           ensure_ascii=False)[:400])

print('=' * 70)
for name in sorted(os.listdir(os.path.join(ROOT, 'data', 'tasks'))):
    if not name.endswith('.json'):
        continue
    with open(os.path.join(ROOT, 'data', 'tasks', name), encoding='utf-8') as f:
        data = json.load(f)
    tasks = data.get('tasks', [])
    print('TASKS', name, '| keys:', sorted(data.keys()), '| count:', len(tasks))
    print('  task keys:', sorted(tasks[0].keys()))
    print('  topics:', collections.Counter(t.get('topic') for t in tasks))
    print('  check types:', collections.Counter(
        (t.get('check') or {}).get('type') for t in tasks))
    print('  difficulties:', collections.Counter(t.get('difficulty') for t in tasks))
    print('  sample:', json.dumps(tasks[0], ensure_ascii=False)[:400])