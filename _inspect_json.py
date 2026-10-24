# -*- coding: utf-8 -*-
import json

d = json.load(open('data/languages/python.json', encoding='utf-8'))
body = d['python']

# посмотреть один урок целиком
l = body['modules'][0]['lessons'][0]
print(json.dumps(l, ensure_ascii=False, indent=1)[:3000])
print('---CHEATSHEET---')
cs = body.get('cheatsheets', [])
print('cheatsheets count:', len(cs))
print(json.dumps(cs[:2], ensure_ascii=False, indent=1)[:1500])