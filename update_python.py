import json

data = {
  "python": {
    "name": "Python",
    "icon": "🐍",
    "color": "#3776AB",
    "description": "Основы программирования и разработка приложений",
    "modules": [
      {
        "id": 1,
        "title": "Основы Python",
        "description": "Введение в Python: переменные, типы данных, операции",
        "lessons": [
          {"id": 1, "title": "Что такое программирование", "theory": ["Программирование — это процесс создания инструкций для компьютера", "Компьютер понимает только машинный код — нули и единицы", "Языки программирования позволяют писать понятные человеку команды", "Python — один из самых популярных и простых языков для начала"], "examples": [{"title": "Первая программа", "code": "print('Привет, мир!')", "explanation": "Функция print() выводит текст на экран"}], "tasks": [{"id": 1, "difficulty": "easy", "title": "Приветствие", "description": "Напишите программу, которая выводит 'Привет, мир!'", "initial_code": "# Напишите ваш код здесь\n", "test_code": "assert 'Привет, мир!' in open(__file__).read()", "hints": ["Используйте функцию print()", "Текст должен быть в кавычках"]}], "test": [{"question": "Что делает функция print()?", "options": ["Вводит данные", "Выводит данные", "Считает", "Завершает программу"], "correct": 1}], "cheatsheet": "print('текст') — вывод на экран\ninput() — ввод от пользователя"},
          {"id": 2, "title": "Переменные", "theory": ["Переменная — это именованная ячейка памяти для хранения данных", "В Python переменные создаются при присваивании значения", "Имена переменных могут содержать буквы, цифры и подчёркивание", "Python определяет тип данных автоматически"], "examples": [{"title": "Создание переменных", "code": "name = 'Алексей'\nage = 25\nheight = 1.75\nis_student = True", "explanation": "Создали 4 переменных разных типов"}], "tasks": [{"id": 1, "difficulty": "easy", "title": "Создание переменных", "description": "Создайте переменную name со своим именем", "initial_code": "# Создайте переменную name\n", "test_code": "assert name == name", "hints": ["name = 'Ваше имя'", "print(name)"]}], "test": [{"question": "Как создать переменную в Python?", "options": ["var x = 5", "x = 5", "int x = 5", "let x = 5"], "correct": 1}], "cheatsheet": "name = 'текст' — строка\nage = 25 — целое число"},
          {"id": 3, "title": "Типы данных", "theory": ["int — целые числа", "float — дробные числа", "str — строки", "bool — логические значения"], "examples": [{"title": "Типы данных", "code": "print(type(42))\nprint(type(3.14))", "explanation": "Функция type() показывает тип данных"}], "tasks": [{"id": 1, "difficulty": "easy", "title": "Определение типа", "description": "Создайте переменную num = 42 и выведите её тип", "initial_code": "# Создайте переменную\n", "test_code": "assert num == 42", "hints": ["num = 42", "print(type(num))"]}], "test": [{"question": "Какой тип у значения 3.14?", "options": ["int", "float", "str", "bool"], "correct": 1}], "cheatsheet": "int — целые числа\nfloat — дробные числа\nstr — строки\nbool — True/False"},
          {"id": 4, "title": "Арифметика", "theory": ["+ сложение", "- вычитание", "* умножение", "/ деление"], "examples": [{"title": "Арифметика", "code": "print(10 + 3)\nprint(10 - 3)", "explanation": "Основные арифметические операции"}], "tasks": [{"id": 1, "difficulty": "easy", "title": "Калькулятор", "description": "Вычислите 25 + 17", "initial_code": "# Вычислите сумму\n", "test_code": "assert 25 + 17 == 42", "hints": ["print(25 + 17)"]}], "test": [{"question": "Что выведет 10 // 3?", "options": ["3.33", "3", "4", "1"], "correct": 1}], "cheatsheet": "+ сложение\n- вычитание\n* умножение\n/ деление"},
          {"id": 5, "title": "Строки", "theory": ["Строки в кавычках", "Конкатенация через +", "len() — длина строки"], "examples": [{"title": "Работа со строками", "code": "name = 'Python'\nprint(name + ' 3.12')", "explanation": "Основные операции со строками"}], "tasks": [{"id": 1, "difficulty": "easy", "title": "Приветствие", "description": "Создайте name = 'Мир' и выведите 'Привет, Мир!'", "initial_code": "# Создайте переменную\n", "test_code": "assert name == 'Мир'", "hints": ["name = 'Мир'", "print('Привет, ' + name + '!')"]}], "test": [{"question": "Что выведет 'abc' * 2?", "options": ["abcabc", "abc2", "2abc", "Ошибка"], "correct": 0}], "cheatsheet": "'текст' — строка\ns + s — объединение\nlen(s) — длина"}
        ]
      }
    ]
  }
}

with open('C:/Users/rusla/.cline/data/workspaces/chat/zxc2/data/languages/python.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done')
