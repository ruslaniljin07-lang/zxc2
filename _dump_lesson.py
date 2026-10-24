# -*- coding: utf-8 -*-
import json
import os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'languages')
j = json.load(open(os.path.join(D, 'python.json'), encoding='utf-8'))['python']
l = j['modules'][0]['lessons'][0]
print('LESSON KEYS:', list(l.keys()))
print(json.dumps(l, ensure_ascii=False, indent=1)[:2500])
print('--------- tasks of lesson 2 ---------')
l2 = j['modules'][0]['lessons'][1]
print(json.dumps(l2.get('tasks', []), ensure_ascii=False, indent=1)[:1500])
print('--------- entrance q0 ---------')
print(json.dumps(j['entrance_test'][0], ensure_ascii=False, indent=1))
print('--------- cheatsheet 0 ---------')
print(json.dumps(j['cheatsheets'][0], ensure_ascii=False, indent=1)[:700])
print('--------- final_project ---------')
print(json.dumps(j.get('final_project'), ensure_ascii=False, indent=1)[:700])