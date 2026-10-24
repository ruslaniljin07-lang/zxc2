import os, json

print('=== Языки ===')
for f in sorted(os.listdir('data/languages')):
    d = json.load(open(f'data/languages/{f}'))
    modules_count = len(d['modules'])
    lessons_count = sum(len(m.get('lessons', [])) for m in d['modules'])
    tests_count = sum(len(m.get('test', [])) for m in d['modules'])
    tasks_count = sum(len(m.get('tasks', [])) for m in d['modules'])
    print(f'{f}: модули={modules_count} | уроки={lessons_count} | тесты={tests_count} | задачи={tasks_count}')

print('\n=== Задачи ===')
if os.path.exists('data/tasks'):
    for f in sorted(os.listdir('data/tasks')):
        d = json.load(open(f'data/tasks/{f}'))
        print(f'{f}: {len(d)} задач')
else:
    print('Нет папки tasks')
