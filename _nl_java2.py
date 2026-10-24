# -*- coding: utf-8 -*-
"""Temp: java — часть 2 (урок 10) + тест модуля 4."""
from _nl_helpers import L, T, Q, EX

LANG = 'java'

LESSONS = [
    L(10, 'Методы строк', 'Полезные операции со String',
      ['length() даёт длину строки, charAt(i) — символ по индексу.',
       'equals(s) сравнивает строки (не ==), toUpperCase() поднимает регистр.',
       'substring(a, b) вырезает часть строки от a до b-1.'],
      [EX('Работа со строкой',
          'String word = "Java";\nSystem.out.println(word.length());\nSystem.out.println(word.toUpperCase());\nSystem.out.println(word.substring(0, 2));',
          'Длина 4, "JAVA", первые две буквы "Ja".')],
      [T(1, 'Привет, имя',
         'Создай строку name = "Аня" и выведи «Привет, Аня!», соединив строки.',
         'easy', 'String name = "Аня";\n// твой код',
         {'type': 'contains',
          'require': ['String name', 'System.out.println', 'Привет, Аня!']},
         ['Строки соединяются плюсом.', 'System.out.println("Привет, " + name + "!");'],
         'String name = "Аня";\nSystem.out.println("Привет, " + name + "!");')],
      [Q('Как сравнить строки в Java?', ['a.equals(b)', 'a == b', 'a.eq(b)', 'a.same(b)'], 0,
         '== сравнивает ссылки, equals — содержимое.'),
       Q('Что вернёт "код".length()?', ['3', '2', '4', 'ошибку'], 0,
         'В строке три буквы.'),
       Q('Что даст "abc".substring(1)?', ['"bc"', '"ab"', '"a"', '"abc"'], 0,
         'С индекса 1 до конца.'),
       Q('Что делает toUpperCase()?', ['поднимает регистр', 'опускает регистр', 'убирает пробелы', 'делит строку'], 0,
         'Возвращает строку в верхнем регистре.'),
       Q('Что вернёт charAt(0) для "Hi"?', ["H", "i", "Hi", "ошибку"], 0,
         'Символ по индексу 0.')],
      's.length() — длина\ns.charAt(i) — символ\nequals(s2) — сравнение\ns.substring(a, b) — часть строки\ns.toUpperCase() — верхний регистр',
      30, 'easy'),
]

MTEST = [
    Q('Как создать объект?', ['new Имя()', 'Имя()', 'create Имя', 'Имя.create()'], 0,
      'Оператор new выделяет объект.'),
    Q('Как добавить элемент в ArrayList?', ['add', 'push', 'insert', 'append'], 0,
      'Метод add.'),
    Q('Как сравнить строки?', ['equals', '==', '===', 'compare'], 0,
      'equals сравнивает содержимое.'),
    Q('Что вернёт size()?', ['число элементов', 'размер в байтах', 'длину строки', 'индекс'], 0,
      'size() — количество элементов.'),
    Q('Какой цикл перебирает список?', ['for (Тип x : list)', 'for x in list', 'foreach list as x', 'loop list'], 0,
      'Java for-each.'),
]
