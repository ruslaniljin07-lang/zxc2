# -*- coding: utf-8 -*-
"""Temp: cpp — часть 2 (урок 9) + тест модуля 4."""
from _nl_helpers import L, T, Q, EX

LANG = 'cpp'

LESSONS = [
    L(9, 'std::string', 'Строки в C++',
      ['string s = "Привет"; — строка из заголовка <string>.',
       's.length() — длина, s[i] — символ, s + "!" — склейка.',
       'Сравнение строк — обычным ==, как у чисел.'],
      [EX('Операции со строкой',
          '#include <string>\n#include <iostream>\nusing namespace std;\n\nint main() {\n    string s = "Привет";\n    s = s + ", мир!";\n    cout << s << " " << s.length();\n}',
          'Плюс склеивает строки, length() даёт длину.')],
      [T(1, 'Длина имени',
         'Создай строку name = "C++" и выведи её длину (3).',
         'easy', '#include <string>\n#include <iostream>\nusing namespace std;\n\nint main() {\n    // твой код\n}',
         {'type': 'contains',
          'require': ['string', 'length', 'cout']},
         ['string name = "C++";', 'cout << name.length();'],
         '#include <string>\n#include <iostream>\nusing namespace std;\n\nint main() {\n    string name = "C++";\n    cout << name.length();\n}')],
      [Q('Какой заголовок нужен для string?', ['#include <string>', '#include <str>', '#include <text>', 'не нужен'], 0,
         'string объявлен в <string>.'),
       Q('Как склеить строки?', ['s + t', 's.concat only', 's ++ t', 'join(s, t)'], 0,
         'Оператор +.'),
       Q('Что вернёт s.length() для "abc"?', ['3', '2', '4', 'ошибку'], 0,
         'Три символа.'),
       Q('Как получить символ по индексу?', ['s[i]', 's(i)', 's->i', 'char(s, i)'], 0,
         'Квадратные скобки.'),
       Q('Как сравнить две строки?', ['s == t', 's.equals(t)', 'strcmp всегда', 's.cmp(t)'], 0,
         'В C++ для std::string работает ==.')],
      'string s = "текст";\ns.length() — длина, s[i] — символ\ns + t — склейка\ns == t — сравнение',
      30, 'easy'),
]

MTEST = [
    Q('Как добавить элемент в vector?', ['push_back', 'add', 'push', 'append'], 0,
      'push_back — в конец.'),
    Q('Что означает void у функции?', ['нет возвращаемого значения', 'пустой список', 'тип 0', 'ничего не делает'], 0,
      'void — функция без результата.'),
    Q('Как узнать длину vector?', ['v.size()', 'v.length()', 'len(v)', 'count(v)'], 0,
      'size().'),
    Q('Какой заголовок нужен для vector?', ['#include <vector>', '#include <list>', '#include <int>', 'не нужен'], 0,
      '<vector>.'),
    Q('Как объявить строку?', ['string s = "hi";', 'str s = "hi";', 'String s = "hi";', 'char* s only'], 0,
      'std::string из <string>.'),
]
