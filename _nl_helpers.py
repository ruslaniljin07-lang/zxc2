# -*- coding: utf-8 -*-
"""Temp: помощники для _add_lessons.py."""


def T(id_, title, desc, diff, initial, check, hints, solution):
    return {'id': id_, 'title': title, 'description': desc,
            'difficulty': diff, 'initial_code': initial, 'check': check,
            'hints': hints, 'solution': solution}


def Q(question, options, correct, explain):
    return {'question': question, 'options': options, 'correct': correct,
            'explain': explain}


def L(id_, title, desc, theory, examples, tasks, test, cheat, xp, diff):
    return {'id': id_, 'title': title, 'description': desc,
            'theory': theory, 'examples': examples, 'tasks': tasks,
            'test': test, 'cheatsheet': cheat, 'xp_reward': xp,
            'difficulty': diff}


def EX(title, code, explanation):
    return {'title': title, 'code': code, 'explanation': explanation}


def MOD(id_, title, desc, lessons, mtest):
    return {'id': id_, 'title': title, 'description': desc,
            'lessons': lessons, 'test': {'questions': mtest}}
