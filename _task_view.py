# -*- coding: utf-8 -*-
"""Добавляет по 2 задачи к каждому уроку Python (12 уроков -> 36 задач)."""
import json

PATH = 'data/languages/python.json'
d = json.load(open(PATH, encoding='utf-8'))
data = d['python'] if 'python' in d else d

def add(lesson_id, tasks):
    for m in data['modules']:
        for l in m['lessons']:
            if l['id'] == lesson_id:
                for t in tasks:
                    t['id'] = len(l['tasks']) + 1
                    l['tasks'].append(t)
                return True
    print(f'LESSON {lesson_id} NOT FOUND')
    return False

def py(title, desc, init, test_code, hints, solution, diff='medium'):
    return {'title': title, 'description': desc, 'difficulty': diff,
            'initial_code': init,
            'check': {'type': 'python', 'test_code': test_code},
            'hints': hints, 'solution': solution, 'examples': []}

def outp(title, desc, init, expected, hints, solution, diff='easy'):
    return {'title': title, 'description': desc, 'difficulty': diff,
            'initial_code': init,
            'check': {'type': 'stdout', 'expected': expected, 'mode': 'exact'},
            'hints': hints, 'solution': solution, 'examples': []}

T = []  # (lesson_id, task)

# L1 Первая программа
T.append((1, outp('Сумма чисел', 'Выведи на экран сумму чисел 7 и 5 (должно получиться 12).',
    '# Посчитай и выведи сумму\n', '12',
    ['Числа в Python складываются через +', 'print(7 + 5)'],
    'print(7 + 5)')))
T.append((1, outp('Несколько строк', 'Выведи три строки: «Меня зовут Аня», «Мне 20 лет», «Я учу Python» — каждая на своей строке.',
    '# Три команды print\n', 'Меня зовут Аня\nМне 20 лет\nЯ учу Python',
    ['Каждый print() выводит новую строку', 'Нужно три команды print'],
    "print('Меня зовут Аня')\nprint('Мне 20 лет')\nprint('Я учу Python')")))

# L2 Переменные и типы
T.append((2, outp('Сумма переменных', 'Создай переменные a = 5 и b = 10, затем выведи их сумму.',
    'a = 5\nb = 10\n# выведи сумму\n', '15',
    ['Сумма: a + b', 'print(a + b)'], 'a = 5\nb = 10\nprint(a + b)')))
T.append((2, py('Обмен значениями', 'Переменные a = 5 и b = 10. Поменяй их значения местами (a должна стать 10, b — 5).',
    'a = 5\nb = 10\n# поменяй значения местами\n',
    'assert a == 10 and b == 5',
    ['В Python можно менять местами так: a, b = b, a', 'Или через третью переменную temp'],
    'a = 5\nb = 10\na, b = b, a')))

# L3 Арифметика и строки
T.append((3, outp('Умножение', 'Перемножь 17 и 6 и выведи результат.',
    'r = 17 * 6\n# выведи r\n', '102',
    ['print(r)'], 'r = 17 * 6\nprint(r)')))
T.append((3, py('Склейка строк', 'Из first = "Иван" и last = "Петров" собери полную строку full = "Иван Петров" (с пробелом).',
    "first = 'Иван'\nlast = 'Петров'\n# собери full\n",
    "assert full == 'Иван Петров'",
    ['Строки складываются через +', "Не забудь пробел: first + ' ' + last"],
    "first = 'Иван'\nlast = 'Петров'\nfull = first + ' ' + last")))

# L4 if / else
T.append((4, py('Максимум из двух', 'Даны x = 7 и y = 12. С помощью if / else найди большее число и запиши его в max_num.',
    'x = 7\ny = 12\n# найди максимум\n',
    'assert max_num == 12',
    ['Сравни x и y в условии if', 'if x > y: max_num = x, иначе max_num = y'],
    'x = 7\ny = 12\nif x > y:\n    max_num = x\nelse:\n    max_num = y')))
T.append((4, py('Чётное или нет', 'Дано number = 8. Запиши в is_even True, если число чётное, и False — если нет.',
    'number = 8\n# проверь чётность\n',
    'assert is_even == True',
    ['Чётность проверяют остатком: number % 2 == 0'],
    'number = 8\nif number % 2 == 0:\n    is_even = True\nelse:\n    is_even = False')))

# L5 elif и логика
T.append((5, py('Оценка за тест', 'Дан score = 85. Запиши в grade: «A» если score >= 90, «B» если score >= 80, иначе «C».',
    'score = 85\n# определи оценку\n',
    "assert grade == 'B'",
    ['Цепочка if / elif / else', 'Проверяй сначала большее условие'],
    "score = 85\nif score >= 90:\n    grade = 'A'\nelif score >= 80:\n    grade = 'B'\nelse:\n    grade = 'C'")))
T.append((5, py('Время суток', 'Дано hour = 14. Запиши в part: «утро» если hour < 12, «день» если hour < 18, иначе «вечер».',
    'hour = 14\n# определи часть суток\n',
    "assert part == 'день'",
    ['Одно условие if и один elif хватит'],
    "hour = 14\nif hour < 12:\n    part = 'утро'\nelif hour < 18:\n    part = 'день'\nelse:\n    part = 'вечер'")))

# L6 Циклы
T.append((6, outp('Сумма от 1 до 10', 'С помощью цикла посчитай сумму всех чисел от 1 до 10 и выведи её.',
    'total = 0\n# цикл for i in range(1, 11)\n# выведи total\n', '55',
    ['range(1, 11) даёт числа 1..10', 'total += i внутри цикла'],
    'total = 0\nfor i in range(1, 11):\n    total += i\nprint(total)')))
T.append((6, py('Квадраты чисел', 'Заполни список squares квадратами чисел от 1 до 5: [1, 4, 9, 16, 25].',
    'squares = []\n# заполни список\n',
    'assert squares == [1, 4, 9, 16, 25]',
    ['for i in range(1, 6): squares.append(i * i)', 'Можно и list comprehension'],
    'squares = [i * i for i in range(1, 6)]')))