# -*- coding: utf-8 -*-
"""Temp: приклеивает новый модуль каждому языку (данные в _nl_*.py)."""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import importlib

LANG_DIR = os.path.join(ROOT, 'data', 'languages')

LANGS = ['python', 'javascript', 'java', 'cpp', 'go', 'csharp',
         'typescript', 'php', 'rust']
PARTS = {
    'python': ['_nl_py1', '_nl_py2'],
    'javascript': ['_nl_js1', '_nl_js2'],
    'java': ['_nl_java1', '_nl_java2'],
    'cpp': ['_nl_cpp1', '_nl_cpp2'],
    'go': ['_nl_go1', '_nl_go2'],
    'csharp': ['_nl_cs1', '_nl_cs2'],
    'typescript': ['_nl_ts1', '_nl_ts2'],
    'php': ['_nl_php1', '_nl_php2'],
    'rust': ['_nl_rs1', '_nl_rs2'],
}


def build_module(lang):
    parts = [importlib.import_module(name) for name in PARTS[lang]]
    for p in parts:
        assert p.LANG == lang, f'{p.__name__}: LANG={p.LANG!r}'
    meta = parts[0].META
    lessons = []
    mtest = None
    for p in parts:
        lessons.extend(p.LESSONS)
        if hasattr(p, 'MTEST'):
            mtest = p.MTEST
    assert mtest is not None, f'{lang}: нет MTEST'
    assert len(mtest) >= 5, f'{lang}: в тесте модуля {len(mtest)} вопросов'
    return {'id': meta['id'], 'title': meta['title'],
            'description': meta['description'], 'lessons': lessons,
            'test': {'questions': mtest}}


def main():
    for lang in LANGS:
        path = os.path.join(LANG_DIR, lang + '.json')
        with open(path, encoding='utf-8') as f:
            raw = json.load(f)
        data = raw.get(lang, raw)

        mod = build_module(lang)
        ids = [m['id'] for m in data['modules']]
        assert mod['id'] not in ids, f'{lang}: модуль {mod["id"]} уже есть'
        assert ids == sorted(ids), f'{lang}: существующие модули не по порядку'
        assert mod['id'] == max(ids) + 1, \
            f'{lang}: id нового модуля {mod["id"]} != {max(ids) + 1}'

        lesson_ids = [l['id'] for m in data['modules'] for l in m['lessons']]
        new_ids = [l['id'] for l in mod['lessons']]
        assert len(set(new_ids)) == len(new_ids), f'{lang}: дубли уроков'
        assert not (set(new_ids) & set(lesson_ids)), f'{lang}: пересечение id'
        assert lesson_ids + new_ids == sorted(lesson_ids + new_ids), \
            f'{lang}: новые уроки должны продолжать нумерацию'

        for l in mod['lessons']:
            assert len(l['theory']) >= 3, f'{lang} L{l["id"]}: теория < 3'
            assert l['examples'], f'{lang} L{l["id"]}: нет примеров'
            assert len(l['test']) >= 5, f'{lang} L{l["id"]}: тест < 5'
            assert all((q.get('explain') or '').strip()
                       for q in l['test']), f'{lang} L{l["id"]}: нет explain'

        data['modules'].append(mod)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            json.dump({lang: data}, f, ensure_ascii=False, indent=1)
        print(f'{lang:11} +модуль {mod["id"]} «{mod["title"]}»: '
              f'уроки {new_ids[0]}-{new_ids[-1]}')


main()
