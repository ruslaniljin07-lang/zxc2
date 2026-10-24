# -*- coding: utf-8 -*-
"""Temp: csharp — часть 2 (урок 9) + тест модуля 4."""
from _nl_helpers import L, T, Q, EX

LANG = 'csharp'

LESSONS = [
    L(9, 'Методы строк', 'Работа со string в C#',
      ['Length — длина строки, s[i] — символ.',
       'ToUpper() поднимает регистр, Substring(a, b) вырезает часть.',
       'Склейка строк — плюс: "Привет, " + name.'],
      [EX('Операции со строкой',
          'using System;\n\nclass Program {\n    static void Main() {\n        string s = "csharp";\n        Console.WriteLine(s.ToUpper());\n        Console.WriteLine(s.Substring(0, 2));\n        Console.WriteLine(s.Length);\n    }\n}',
          'CSHARP, первые две буквы "cs" и длина 6.')],
      [T(1, 'Приветствие',
         'Создай строку name = "Аня" и выведи «Привет, Аня!».',
         'easy', 'using System;\n\nclass Program {\n    static void Main() {\n        // твой код\n    }\n}',
         {'type': 'contains',
          'require': ['string', 'Console.WriteLine', 'Привет, Аня!']},
         ['string name = "Аня";', 'Console.WriteLine("Привет, " + name + "!");'],
         'using System;\n\nclass Program {\n    static void Main() {\n        string name = "Аня";\n        Console.WriteLine("Привет, " + name + "!");\n    }\n}')],
      [Q('Как узнать длину строки?', ['s.Length', 's.length()', 'len(s)', 'size(s)'], 0,
         'Length — свойство.'),
       Q('Что сделает s.ToUpper()?', ['подняет регистр', 'опустит регистр', 'обрежет строку', 'разделит строку'], 0,
         'Верхний регистр.'),
       Q('Как сравнить строки по содержимому?', ['s == t (тоже работает)', 'только s.Equals(t)', 's.compare', 'равны никогда'], 0,
         'И ==, и Equals сравнивают содержимое string.'),
       Q('Что вернёт Substring(1) для "код"?', ["од", "ко", "код", "ошибку"], 0,
         'С индекса 1 до конца.'),
       Q('Склейка строк это...', ['плюс', 'точка', 'запятая', 'амперсанд &'], 0,
         'В C# — оператор +.')],
      's.Length — длина, s[i] — символ\ns.ToUpper() — верхний регистр\ns.Substring(a, b) — часть\n"a" + b — склейка',
      30, 'easy'),
]

MTEST = [
    Q('Как добавить элемент в List?', ['Add', 'push', 'append', 'put'], 0, 'Метод Add.'),
    Q('Что вернёт Count?', ['число элементов', 'байты', 'ёмкость', 'индекс'], 0, 'Количество.'),
    Q('Как создать объект?', ['new Имя()', 'Имя()', 'create Имя', 'make Имя'], 0, 'Оператор new.'),
    Q('Что означает public?', ['открытый доступ', 'приватный', 'статический', 'виртуальный'], 0,
      'Модификатор доступа.'),
    Q('Длина строки это...', ['Length', 'length()', 'size()', 'len'], 0, 'Свойство Length.'),
]
