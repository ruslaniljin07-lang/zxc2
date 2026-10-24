"""Temp: состояние _gen_courses.py."""
src = open('_gen_courses.py', encoding='utf-8').read()
for key in ["COURSES['go'] = {", "_G1", "_G2", "_G3", "modules'].append(module(",
            "'entrance_test']", "'cheatsheets']"]:
    print(key, '->', src.count(key))
try:
    import ast
    ast.parse(src)
    print('syntax OK')
except SyntaxError as e:
    print('SYNTAX ERROR:', e)