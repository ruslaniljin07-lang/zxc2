# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout.reconfigure(encoding='utf-8')
for lang in ['python', 'javascript', 'java', 'cpp']:
    d = json.load(open(f'data/languages/{lang}.json', encoding='utf-8'))
    data = d[lang] if lang in d else d
    print('='*20, lang, '='*20)
    for m in data.get('modules', []):
        print(f"M{m['id']} {m['title']}")
        for l in m.get('lessons', []):
            tasks = l.get('tasks', [])
            t0 = tasks[0] if tasks else {}
            chk = t0.get('check', '') or ''
            if isinstance(chk, dict):
                chk = json.dumps(chk, ensure_ascii=False)
            print(f"  L{l['id']}: {l['title']} | tasks={len(tasks)} | check={str(chk)[:60]!r}")