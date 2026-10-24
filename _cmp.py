# -*- coding: utf-8 -*-
import json, os, io
BASE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(BASE, 'data', 'languages')
out = io.StringIO()

def L(code):
    return json.load(open(os.path.join(D, code + '.json'), encoding='utf-8'))[code]

py = L('python')
js = L('javascript')

def first_lesson(d):
    m = d['modules'][0]['lessons'][0]
    return m

a = first_lesson(py)
b = first_lesson(js)

for name, lesson in (('PYTHON', a), ('JAVASCRIPT', b)):
    print('=' * 60, file=out)
    print(name, '|', lesson['title'], '| id', lesson['id'], file=out)
    print('description:', lesson['description'], file=out)
    print('-- theory --', file=out)
    for t in lesson.get('theory', []):
        print('  *', t[:120], file=out)
    print('-- examples --', file=out)
    for e in lesson.get('examples', []):
        print('  #', repr(e.get('code', ''))[:150], file=out)
    print('-- task check --', file=out)
    for t in lesson.get('tasks', []):
        print('  task:', t.get('title'), file=out)
        print('   check:', json.dumps(t.get('check'), ensure_ascii=False)[:200], file=out)
        print('   solution:', repr(t.get('solution', ''))[:200], file=out)
        print('   initial:', repr(t.get('initial_code', ''))[:200], file=out)
    print('-- test --', file=out)
    for q in lesson.get('test', []):
        print('  Q:', q.get('question'), '| opts', len(q.get('options', [])), '| correct', q.get('correct'), file=out)

print('=' * 60, file=out)
print('IDS per language:', file=out)
for code in ['python', 'javascript', 'java', 'cpp']:
    d = L(code)
    ids = [l['id'] for m in d['modules'] for l in m['lessons']]
    print(f'  {code}: module_ids={[m["id"] for m in d["modules"]]} lesson_ids={ids}', file=out)

with open(os.path.join(BASE, '_cmp_out.txt'), 'w', encoding='utf-8') as f:
    f.write(out.getvalue())
print(out.getvalue())