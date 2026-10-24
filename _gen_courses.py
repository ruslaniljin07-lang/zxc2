# -*- coding: utf-8 -*-
"""Temp generator: курсы data/languages/{go,csharp,typescript,php,rust}.json."""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
LANG_DIR = os.path.join(ROOT, 'data', 'languages')

CHECK = {'go': 'stdout_go', 'csharp': 'stdout_csharp',
         'typescript': 'stdout_ts', 'php': 'stdout_php',
         'rust': 'stdout_rust'}

COURSES = {}


def q(question, options, correct, explain=None):
    """Вопрос теста."""
    item = {'question': question, 'options': options, 'correct': correct}
    if explain:
        item['explain'] = explain
    return item


def task(lang, tid, title, desc, expected, code, require, hints,
         initial='', difficulty='easy'):
    """Задание урока: запуск кода, при отсутствии тулчейна — contains."""
    return {
        'id': tid, 'title': title, 'description': desc,
        'difficulty': difficulty, 'initial_code': initial,
        'check': {'type': CHECK[lang], 'expected': expected,
                  'require': require},
        'hints': hints, 'solution': code, 'examples': [],
    }


def lesson(lid, title, desc, theory, examples, lesson_task, test, cheat,
           xp=20, difficulty='easy'):
    return {'id': lid, 'title': title, 'description': desc, 'theory': theory,
            'examples': examples, 'tasks': [lesson_task], 'test': test,
            'cheatsheet': cheat, 'xp_reward': xp, 'difficulty': difficulty}


def module(mid, title, description, lessons, questions):
    return {'id': mid, 'title': title, 'description': description,
            'lessons': lessons, 'test': {'questions': questions}}


CHEAT_ICONS = ['\U0001F3D7\uFE0F', '\U0001F3F7\uFE0F', '\U0001F500',
               '\U0001F501', '\U0001F4DA', '\U0001F9E9']


def cheat(index, title, code, note):
    """Элемент списка шпаргалок (иконка по порядку)."""
    return {'title': title, 'icon': CHEAT_ICONS[index], 'code': code,
            'note': note}


def build(lang, course):
    path = os.path.join(LANG_DIR, lang + '.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({lang: course}, f, ensure_ascii=False, indent=1)
    lessons = sum(len(m['lessons']) for m in course['modules'])
    tasks = sum(len(l['tasks']) for m in course['modules']
                for l in m['lessons'])
    print(f'{lang}: модулей {len(course["modules"])}, уроков {lessons}, '
          f'заданий {tasks}, тестов входа {len(course["entrance_test"])}, '
          f'шпаргалок {len(course["cheatsheets"])}')


# ===== DATA =====

COURSES['go'] = {
    'name': 'Go', 'icon': '\U0001F439', 'color': '#00ADD8',
    'description': 'Простой и быстрый компилируемый язык от Google — '
                   'любимец серверной разработки и микросервисов.',
    'difficulty': 'Средний старт',
    'final_project': 'Консольный калькулятор расходов',
    'modules': [],
}

COURSES['go']['modules'].append(module(
    1, 'Основы Go', 'Первая программа, переменные и типы', [
        lesson(
            1, 'Первая программа', 'Знакомимся с Go и пакетом fmt',
            ['Go — компилируемый язык со строгой типизацией.',
             'Программа начинается с package main, вход — func main().',
             'Пакет fmt печатает данные, Println добавляет перевод строки.'],
            [{'title': 'Привет, мир',
              'code': 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Привет, мир!")\n}',
              'explanation': 'package main и func main() — минимальная программа.'}],
            task('go', 1, 'Первый вывод', 'Выведи строку: Go — это просто!',
                 'Go — это просто!',
                 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Go — это просто!")\n}',
                 ['fmt.Println', 'Go — это просто!'],
                 ['Используй fmt.Println("текст").',
                  'Текст должен совпадать точно: «Go — это просто!»'],
                 initial='package main\n\nimport "fmt"\n\nfunc main() {\n\t// твой код\n}'),
            [q('Как вывести текст в Go?',
               ['print()', 'fmt.Println()', 'console.log()', 'echo'], 1),
             q('С какой функции начинается программа?',
               ['main()', 'start()', 'init()', 'run()'], 0)],
            'package main — исполняемая программа\nfunc main() — точка входа\n'
            'fmt.Println("текст") — вывод с переводом строки'),
        lesson(
            2, 'Переменные и типы', 'var, короткое объявление и типы',
            ['var name string = "Го" — полное объявление.',
             'Короткое объявление := выводит тип автоматически.',
             'Основные типы: int, float64, string, bool.',
             'Неиспользуемая переменная — ошибка компиляции.'],
            [{'title': 'Объявление переменных',
              'code': 'var name string = "Артур"\nage := 25\nfmt.Println(name, age)',
              'explanation': ':= работает только внутри функций.'}],
            task('go', 2, 'Переменная города',
                 'Объяви переменную city со значением «Москва» и выведи её.',
                 'Москва',
                 'package main\n\nimport "fmt"\n\nfunc main() {\n\tcity := "Москва"\n\tfmt.Println(city)\n}',
                 ['city', 'fmt.Println'],
                 ['Используй короткое объявление city := "Москва".',
                  'Выведи переменную через fmt.Println(city).'],
                 initial='package main\n\nimport "fmt"\n\nfunc main() {\n\t// объяви city\n}'),
            [q('Как объявить переменную с автоматическим типом?',
               ['var x int = 5', 'x := 5', 'int x = 5', 'let x = 5'], 1),
             q('Какой тип подходит для текста?',
               ['string', 'text', 'str', 'char[]'], 0)],
            'var x int = 5 — явный тип\nname := "Го" — короткое объявление\n'
            'var pi float64 = 3.14\nvar ok bool = true'),
    ], [
        q('Какая строка обязательна в начале программы?',
          ['package main', 'import main', 'func main()', 'begin'], 0,
          'Пакет main объявляется первым.'),
        q('Что произойдёт с неиспользуемой переменной?',
          ['ошибка компиляции', 'предупреждение', 'ничего', 'она удалится'], 0,
          'Компилятор Go требует использовать все переменные.'),
    ]))

_G3 = [
    lesson(
        5, 'Слайсы и map', 'Коллекции Go',
        ['Слайс — динамический массив: nums := []int{1, 2, 3}.',
         'len(nums) — длина, append(nums, 4) — добавление.',
         'map хранит пары ключ-значение: map[string]int.',
         'Пустой map создаётся через make или литерал.'],
        [{'title': 'Сумма слайса',
          'code': 'nums := []int{3, 6, 9}\nsum := 0\nfor _, v := range nums {\n\tsum += v\n}\nfmt.Println(sum)',
          'explanation': '_ пропускает индекс, если он не нужен.'},
         {'title': 'Map',
          'code': 'ages := map[string]int{"Анна": 25}\nfmt.Println(ages["Анна"])',
          'explanation': 'Ключом может быть строка или число.'}],
        task('go', 5, 'Сумма слайса',
             'Дан слайс [3, 6, 9] — выведи сумму его элементов.',
             '18',
             'package main\n\nimport "fmt"\n\nfunc main() {\n\tnums := []int{3, 6, 9}\n\tsum := 0\n\tfor _, v := range nums {\n\t\tsum += v\n\t}\n\tfmt.Println(sum)\n}',
             ['range', 'fmt.Println'],
             ['Пройди слайс циклом for range.',
              'Складывай значения в переменную-накопитель.'],
             initial='package main\n\nimport "fmt"\n\nfunc main() {\n\tnums := []int{3, 6, 9}\n\t// посчитай сумму\n}',
             difficulty='medium'),
        [q('Как создать слайс из трёх чисел?',
           ['[]int{1, 2, 3}', 'int[]{1,2,3}', '[1, 2, 3]', '(1, 2, 3)'], 0),
         q('Что делает len(nums)?',
           ['возвращает длину', 'считает сумму', 'удаляет элемент',
            'сортирует'], 0)],
        'nums := []int{1, 2, 3}\nnums = append(nums, 4)\nlen(nums)\n'
        'm := map[string]int{"a": 1}\nfor i, v := range nums { ... }'),
    lesson(
        6, 'Функции', 'func, параметры и возвращаемые значения',
        ['Функция объявляется словом func.',
         'Тип параметра указывается после имени: func add(a int) int.',
         'return возвращает значение.',
         'Go умеет возвращать несколько значений сразу.'],
        [{'title': 'Простая функция',
          'code': 'func double(n int) int {\n\treturn n * 2\n}\n\nfmt.Println(double(7))',
          'explanation': 'Тип результата пишется после скобок параметров.'},
         {'title': 'Два результата',
          'code': 'func divmod(a, b int) (int, int) {\n\treturn a / b, a % b\n}\nq, r := divmod(17, 5)',
          'explanation': 'Несколько типов в скобках — несколько результатов.'}],
        task('go', 6, 'Функция double',
             'Напиши функцию double(n int) int, которая возвращает '
             'удвоенное число, и выведи double(7).',
             '14',
             'package main\n\nimport "fmt"\n\nfunc double(n int) int {\n\treturn n * 2\n}\n\nfunc main() {\n\tfmt.Println(double(7))\n}',
             ['func double', 'return'],
             ['Объяви функцию рядом с main.',
              'Умножь параметр на 2 и верни результат через return.'],
             initial='package main\n\nimport "fmt"\n\n// объяви функцию double\n\nfunc main() {\n\t// выведи double(7)\n}',
             difficulty='hard'),
        [q('Как объявить функцию в Go?',
           ['func add(a int) int', 'function add(a)', 'def add(a)',
            'void add(a)'], 0),
         q('Сколько значений может вернуть функция?',
           ['несколько', 'только одно', 'ни одного', 'ровно два'], 0)],
        'func add(a int, b int) int {\n\treturn a + b\n}\n'
        'func swap(a, b int) (int, int)\nreturn / defer / panic'),
]

COURSES['go']['modules'].append(module(
    2, 'Условия и циклы', 'Ветвление, switch и цикл for', [
        lesson(
            3, 'Условия if / else', 'Ветвление и switch',
            ['Скобки вокруг условия не нужны, фигурные — обязательны.',
             'else пишется в строке с закрывающей скобкой if.',
             'Логика: && (и), || (или), ! (не). В switch break не нужен.'],
            [{'title': 'if / else',
              'code': 'n := 10\nif n > 0 {\n\tfmt.Println("положительное")\n} else {\n\tfmt.Println("отрицательное")\n}',
              'explanation': 'else должен идти сразу после } в той же строке.'}],
            task('go', 3, 'Большое число',
                 'Если n = 12 больше 10 — выведи «большое», иначе «маленькое».',
                 'большое',
                 'package main\n\nimport "fmt"\n\nfunc main() {\n\tn := 12\n\tif n > 10 {\n\t\tfmt.Println("большое")\n\t} else {\n\t\tfmt.Println("маленькое")\n\t}\n}',
                 ['if n > 10', 'fmt.Println'],
                 ['Напиши условие n > 10.', 'В блоках выведи нужный текст.'],
                 initial='package main\n\nimport "fmt"\n\nfunc main() {\n\tn := 12\n\t// проверь условие\n}',
                 difficulty='medium'),
            [q('Нужны ли круглые скобки вокруг условия?',
               ['да, всегда', 'нет, скобки не нужны', 'только в switch',
                'только с else'], 1),
             q('Какой оператор означает «и»?', ['&&', 'and', '&', '++'], 0)],
            'if n > 0 { ... } else { ... }\nswitch x {\ncase 1: ...\ndefault: ...\n}\n&&, ||, !'),
        lesson(
            4, 'Циклы', 'Единственный цикл for и перебор range',
            ['В Go единственный цикл — for.',
             'Классическая форма: for i := 0; i < n; i++.',
             'Бесконечный цикл: for { }. Перебор: for i, v := range nums.'],
            [{'title': 'Счётчик',
              'code': 'for i := 1; i <= 3; i++ {\n\tfmt.Println(i)\n}',
              'explanation': 'i++ увеличивает счётчик после итерации.'}],
            task('go', 4, 'Числа от 1 до 5',
                 'Выведи числа от 1 до 5 через пробел в одной строке.',
                 '1 2 3 4 5',
                 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfor i := 1; i <= 5; i++ {\n\t\tfmt.Print(i)\n\t\tif i < 5 {\n\t\t\tfmt.Print(" ")\n\t\t}\n\t}\n\tfmt.Println()\n}',
                 ['for i := 1', 'fmt.Print'],
                 ['Используй for i := 1; i <= 5; i++.',
                  'Между числами печатай пробел, в конце — перевод строки.'],
                 initial='package main\n\nimport "fmt"\n\nfunc main() {\n\t// цикл от 1 до 5\n}',
                 difficulty='medium'),
            [q('Какой цикл есть в Go?',
               ['for', 'while', 'do..while', 'loop'], 0),
             q('Что делает break?',
               ['выходит из цикла', 'пропускает итерацию',
                'перезапускает цикл', 'ничего'], 0)],
            'for i := 0; i < 5; i++ { ... }\nfor { ... } — бесконечный\n'
            'for i, v := range nums { ... }\nbreak / continue'),
    ], [
        q('Как пишется else в Go?',
          ['на строке с закрывающей скобкой if', 'с новой строки',
           'без фигурных скобок', 'через elseif'], 0,
          'Иначе компилятор вставит точку с запятой.'),
        q('Сколько видов циклов в Go?',
          ['один — for', 'два', 'три', 'четыре'], 0,
          'while реализуется через for.'),
    ]))

COURSES['go']['modules'].append(module(
    3, 'Слайсы и функции', 'Коллекции, map и свои функции', _G3, [
        q('Как добавить элемент в слайс?',
          ['append(nums, 4)', 'push(nums, 4)', 'nums.add(4)', 'add(nums, 4)'],
          0, 'append возвращает новый слайс.'),
        q('Что такое map?',
          ['набор пар ключ-значение', 'динамический массив', 'строка',
           'цикл'], 0, 'map похож на словарь в Python.'),
        q('Что делает return?',
          ['возвращает значение из функции', 'завершает программу',
           'печатает значение', 'объявляет переменную'], 0,
          'Без return программа не вернёт результат.'),
    ]))

COURSES['go']['entrance_test'] = [
    q('Как вывести текст в Go?',
      ['print()', 'fmt.Println()', 'console.log()', 'echo'], 1),
    q('Какая функция — точка входа?',
      ['start()', 'main()', 'init()', 'run()'], 1),
    q('Что означает := ?',
      ['присваивание с выводом типа', 'сравнение', 'остаток деления',
       'логическое «и»'], 0),
    q('Какой цикл есть в Go?', ['for', 'while', 'loop', 'repeat'], 0),
    q('Как объявить переменную с типом?',
      ['var x int = 5', 'int x = 5', 'x: int = 5', 'let x = 5'], 0),
    q('Как перебрать слайс?', ['for range', 'foreach', 'for in', 'each'], 0),
    q('Как объявить функцию?',
      ['func add(a int) int', 'function add(a)', 'def add(a)',
       'void add(a)'], 0),
    q('Что делает fmt.Print вместо fmt.Println?',
      ['не добавляет перевод строки', 'ничего не выводит', 'пишет в файл',
       'очищает консоль'], 0),
]

COURSES['go']['cheatsheets'] = [
    cheat(0, 'Основы',
          'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Привет")\n}',
          'package main + func main() — скелет любой программы.'),
    cheat(1, 'Переменные',
          'var x int = 5\nname := "Го"\nvar pi float64 = 3.14\nvar ok bool = true',
          ':= работает только внутри функций.'),
    cheat(2, 'Условия',
          'if n > 0 {\n\tfmt.Println("плюс")\n} else {\n\tfmt.Println("минус")\n}',
          'Круглые скобки не нужны, break в switch тоже.'),
    cheat(3, 'Циклы',
          'for i := 0; i < 5; i++ { ... }\nfor i, v := range nums { ... }',
          'В Go только один цикл — for.'),
    cheat(4, 'Слайсы и map',
          'nums := []int{1, 2, 3}\nnums = append(nums, 4)\nlen(nums)\nm := map[string]int{"a": 1}',
          'Слайс — динамический массив, map — словарь.'),
    cheat(5, 'Функции',
          'func add(a int, b int) int {\n\treturn a + b\n}',
          'Функция может вернуть несколько значений: (int, error).'),
]

COURSES['csharp'] = {
    'name': 'C#', 'icon': '\U0001F49C', 'color': '#9B4F96',
    'description': 'Язык платформы .NET: строгая типизация, классы '
                   'и огромная стандартная библиотека.',
    'difficulty': 'Средний старт',
    'final_project': 'Учёт личных финансов на C#',
    'modules': [],
}

COURSES['csharp']['modules'].append(module(
    1, 'Основы C#', 'Первая программа, переменные и типы', [
        lesson(
            1, 'Первая программа', 'Класс Program и Console.WriteLine',
            ['Код C# компилируется в промежуточный язык .NET и исполняется CLR.',
             'Точка входа — метод Main внутри класса.',
             'Console.WriteLine выводит строку и переводит курсор.'],
            [{'title': 'Привет, мир',
              'code': 'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("Привет, мир!");\n    }\n}',
              'explanation': 'using System подключает пространство имён с Console.'}],
            task('csharp', 1, 'Первый вывод',
                 'Выведи строку: C# — это просто!', 'C# — это просто!',
                 'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("C# — это просто!");\n    }\n}',
                 ['Console.WriteLine', 'C# — это просто!'],
                 ['Используй Console.WriteLine("текст");',
                  'Текст должен совпадать точно: «C# — это просто!»'],
                 initial='using System;\n\nclass Program {\n    static void Main() {\n        // твой код\n    }\n}'),
            [q('Как вывести текст в C#?',
               ['print()', 'Console.WriteLine()', 'echo', 'console.log()'], 1),
             q('Как называется метод — точка входа?',
               ['Main', 'main', 'Start', 'Run'], 0)],
            'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("текст");\n    }\n}'),
        lesson(
            2, 'Переменные и типы', 'int, double, string, bool и var',
            ['Тип указывается явно: int x = 5;',
             'var выводит тип из значения автоматически.',
             'Основные типы: int, double, string, bool, char.'],
            [{'title': 'Переменные',
              'code': 'int age = 25;\nvar city = "Москва";\nConsole.WriteLine(city + ", " + age);',
              'explanation': 'Строки склеиваются оператором +.'}],
            task('csharp', 2, 'Переменная года',
                 'Создай переменную year со значением 2026 и выведи её.',
                 '2026',
                 'using System;\n\nclass Program {\n    static void Main() {\n        int year = 2026;\n        Console.WriteLine(year);\n    }\n}',
                 ['year', 'Console.WriteLine'],
                 ['Объяви переменную: int year = 2026;',
                  'Выведи её через Console.WriteLine(year);'],
                 initial='using System;\n\nclass Program {\n    static void Main() {\n        // объяви year\n    }\n}'),
            [q('Как объявить переменную с автоматическим типом?',
               ['var x = 5;', 'let x = 5;', 'x := 5', 'dynamic x = 5'], 0),
             q('Какой тип подходит для текста?',
               ['string', 'text', 'str', 'char'], 0)],
            'int x = 5;\nvar name = "Аня";\ndouble pi = 3.14;\nbool ok = true;'),
    ], [
        q('Из чего состоит программа C#?',
          ['из классов и методов', 'из функций верхнего уровня', 'из модулей',
           'из пакетов'], 0, 'Код обязан лежать внутри класса.'),
        q('Что подключает using System?',
          ['пространство имён System', 'пакет System', 'библиотеку ввода',
           'ничего'], 0, 'Без него Console придётся писать полностью.'),
    ]))

COURSES['csharp']['modules'].append(module(
    2, 'Условия и циклы', 'Ветвление, switch, for и foreach', [
        lesson(
            3, 'Условия if / else', 'Ветвление и switch',
            ['Скобки вокруг условия обязательны.',
             'Цепочки условий строятся через else if.',
             'switch работает со строками и числами, break обязателен.'],
            [{'title': 'if / else',
              'code': 'int n = 10;\nif (n > 0) {\n    Console.WriteLine("положительное");\n} else {\n    Console.WriteLine("отрицательное");\n}',
              'explanation': 'Тело условия обязательно в фигурных скобках.'}],
            task('csharp', 3, 'Большое число',
                 'Если n = 12 больше 10 — выведи «большое», иначе «маленькое».',
                 'большое',
                 'using System;\n\nclass Program {\n    static void Main() {\n        int n = 12;\n        if (n > 10) {\n            Console.WriteLine("большое");\n        } else {\n            Console.WriteLine("маленькое");\n        }\n    }\n}',
                 ['if (n > 10)', 'Console.WriteLine'],
                 ['Условие: n > 10.', 'В блоках выведи нужный текст.'],
                 initial='using System;\n\nclass Program {\n    static void Main() {\n        int n = 12;\n        // проверь условие\n    }\n}',
                 difficulty='medium'),
            [q('Что обязательно в условии C#?',
               ['круглые скобки', 'ключевое слово then', 'двоеточие',
                'слово do'], 0),
             q('Какой оператор означает «и»?', ['&&', 'and', '&', '|'], 0)],
            'if (n > 0) { ... } else if (n == 0) { ... } else { ... }\n'
            'switch (x) {\n    case 1: ...; break;\n    default: ...; break;\n}'),
        lesson(
            4, 'Циклы', 'for, foreach и while',
            ['for (int i = 0; i < n; i++) — классический счётчик.',
             'foreach перебирает элементы коллекции.',
             'while и do..while выполняются, пока условие истинно.'],
            [{'title': 'Счётчик',
              'code': 'for (int i = 1; i <= 3; i++) {\n    Console.WriteLine(i);\n}',
              'explanation': 'i++ увеличивает счётчик после каждой итерации.'}],
            task('csharp', 4, 'Числа от 1 до 5',
                 'Выведи числа от 1 до 5 через пробел в одной строке.',
                 '1 2 3 4 5',
                 'using System;\n\nclass Program {\n    static void Main() {\n        for (int i = 1; i <= 5; i++) {\n            Console.Write(i);\n            if (i < 5) Console.Write(" ");\n        }\n        Console.WriteLine();\n    }\n}',
                 ['for (int i = 1', 'Console.Write'],
                 ['Используй for (int i = 1; i <= 5; i++).',
                  'Печатай числа без перевода строки и разделяй пробелом.'],
                 initial='using System;\n\nclass Program {\n    static void Main() {\n        // цикл от 1 до 5\n    }\n}',
                 difficulty='medium'),
            [q('Какой цикл перебирает коллекцию?',
               ['foreach', 'for', 'while', 'repeat'], 0),
             q('Что делает break?',
               ['выходит из цикла', 'пропускает итерацию', 'перезапускает цикл',
                'ничего'], 0)],
            'for (int i = 0; i < 5; i++) { ... }\nforeach (var x in items) { ... }\n'
            'while (условие) { ... }\nbreak / continue'),
    ], [
        q('Чем switch отличается от цепочки if?',
          ['сравнивает одно значение с вариантами', 'работает только с числами',
           'не требует break', 'быстрее в 10 раз'], 0,
          'switch удобен для перебора вариантов.'),
        q('Что делает Console.Write?',
          ['выводит без перевода строки', 'выводит с переводом строки',
           'пишет в файл', 'ничего'], 0, 'WriteLine добавляет перевод строки.'),
    ]))

COURSES['csharp']['modules'].append(module(
    3, 'Массивы и методы', 'Массивы, коллекции и свои методы', [
        lesson(
            5, 'Массивы и коллекции', 'Массивы, Length и List',
            ['Массив объявляется так: int[] nums = {1, 2, 3};',
             'nums.Length — длина, nums[0] — первый элемент.',
             'List<int> — динамический список из System.Collections.Generic.'],
            [{'title': 'Сумма массива',
              'code': 'int[] nums = {3, 6, 9};\nint sum = 0;\nforeach (int n in nums) sum += n;\nConsole.WriteLine(sum);',
              'explanation': 'foreach складывает все элементы массива.'}],
            task('csharp', 5, 'Сумма массива',
                 'Дан массив [3, 6, 9] — выведи сумму его элементов.', '18',
                 'using System;\n\nclass Program {\n    static void Main() {\n        int[] nums = {3, 6, 9};\n        int sum = 0;\n        foreach (int n in nums) sum += n;\n        Console.WriteLine(sum);\n    }\n}',
                 ['int[] nums', 'Console.WriteLine'],
                 ['Пройди массив циклом foreach.',
                  'Складывай элементы в переменную-накопитель.'],
                 initial='using System;\n\nclass Program {\n    static void Main() {\n        int[] nums = {3, 6, 9};\n        // посчитай сумму\n    }\n}',
                 difficulty='medium'),
            [q('Как узнать длину массива?',
               ['nums.Length', 'nums.length', 'len(nums)', 'size(nums)'], 0),
             q('Какой индекс у первого элемента?', ['0', '1', '-1', 'любой'], 0)],
            'int[] nums = {1, 2, 3};\nnums.Length\nnums[0]\n'
            'var list = new List<int> { 1, 2, 3 };\nlist.Add(4);'),
        lesson(
            6, 'Методы', 'static-методы и return',
            ['Тип возврата указывается перед именем: static int Double(int n).',
             'static позволяет вызывать метод из статического Main.',
             'return возвращает результат.'],
            [{'title': 'Метод',
              'code': 'static int Double(int n) {\n    return n * 2;\n}',
              'explanation': 'Имя метода в C# принято писать с большой буквы.'}],
            task('csharp', 6, 'Метод Double',
                 'Напиши метод Double(int n), возвращающий удвоенное число, '
                 'и выведи Double(7).', '14',
                 'using System;\n\nclass Program {\n    static int Double(int n) {\n        return n * 2;\n    }\n\n    static void Main() {\n        Console.WriteLine(Double(7));\n    }\n}',
                 ['static int Double', 'return'],
                 ['Объяви метод рядом с Main.',
                  'Умножь параметр на 2 и верни результат через return.'],
                 initial='using System;\n\nclass Program {\n    // объяви метод Double\n\n    static void Main() {\n        // выведи Double(7)\n    }\n}',
                 difficulty='hard'),
            [q('Как объявить метод в C#?',
               ['static int Double(int n)', 'func double(n int)', 'def double(n)',
                'function double(n)'], 0),
             q('Что делает return?',
               ['возвращает значение', 'печатает значение', 'завершает программу',
                'объявляет переменную'], 0)],
            'static int Add(int a, int b) { return a + b; }\n'
            'static void Print(string s) { Console.WriteLine(s); }\nreturn;'),
    ], [
        q('Что делает foreach?',
          ['перебирает элементы коллекции', 'создаёт массив', 'сортирует',
           'ищет элемент'], 0, 'Индекс при этом недоступен.'),
        q('Зачем методу модификатор static?',
          ['чтобы вызывать его из Main', 'чтобы он был быстрым', 'чтобы вернуть значение',
           'чтобы объявить переменную'], 0, 'Main статичен, поэтому и метод статичен.'),
    ]))

COURSES['csharp']['entrance_test'] = [
    q('Как вывести текст в C#?',
      ['print()', 'Console.WriteLine()', 'echo', 'console.log()'], 1),
    q('Как называется точка входа?',
      ['Main', 'main', 'Start', 'Run'], 0),
    q('Какой тип подходит для текста?', ['string', 'str', 'text', 'char'], 0),
    q('Как объявить массив?', ['int[] a = {1, 2};', 'int a[] = (1, 2);',
                               'array a = [1, 2];', 'a = [1, 2];'], 0),
    q('Какой цикл перебирает коллекцию?',
      ['foreach', 'for', 'while', 'repeat'], 0),
    q('Что подключает using System?',
      ['пространство имён', 'пакет', 'класс', 'файл'], 0),
    q('Как объявить переменную с автоматическим типом?',
      ['var x = 5;', 'let x = 5;', 'x := 5', 'auto x = 5;'], 0),
    q('Что означает static у метода?',
      ['метод принадлежит классу, а не объекту', 'метод неизменяемый',
       'метод вернёт число', 'метод приватный'], 0),
]

COURSES['csharp']['cheatsheets'] = [
    cheat(0, 'Основы',
          'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("Привет");\n    }\n}',
          'Код C# живёт внутри классов.'),
    cheat(1, 'Переменные',
          'int x = 5;\nvar name = "Аня";\ndouble pi = 3.14;\nbool ok = true;',
          'var выводит тип из значения.'),
    cheat(2, 'Условия',
          'if (n > 0) { ... } else { ... }\nswitch (x) {\n    case 1: ...; break;\n    default: ...; break;\n}',
          'Скобки в условии обязательны.'),
    cheat(3, 'Циклы',
          'for (int i = 0; i < 5; i++) { ... }\nforeach (var x in items) { ... }\nwhile (условие) { ... }',
          'foreach удобен для коллекций.'),
    cheat(4, 'Массивы',
          'int[] nums = {1, 2, 3};\nnums.Length\nvar list = new List<int> { 1, 2 };\nlist.Add(3);',
          'List<int> умеет расти, массив — нет.'),
    cheat(5, 'Методы',
          'static int Add(int a, int b) {\n    return a + b;\n}',
          'static нужен, чтобы вызывать метод из Main.'),
]

COURSES['typescript'] = {
    'name': 'TypeScript', 'icon': '\U0001F4D8', 'color': '#3178C6',
    'description': 'JavaScript со статическими типами: подсказки в редакторе '
                   'и меньше ошибок во время выполнения.',
    'difficulty': 'Лёгкий старт',
    'final_project': 'Список задач на TypeScript',
    'modules': [],
}

COURSES['typescript']['modules'].append(module(
    1, 'Основы TypeScript', 'Типы, let и const', [
        lesson(
            1, 'Первая программа', 'TypeScript и console.log',
            ['TypeScript — надмножество JavaScript: любой JS-код подходит.',
             'Типы указываются аннотацией: let x: number = 5.',
             'console.log выводит данные в консоль.'],
            [{'title': 'Привет, мир',
              'code': 'const greeting: string = "Привет, мир!";\nconsole.log(greeting);',
              'explanation': 'Аннотация : string подсказывает редактору тип.'}],
            task('typescript', 1, 'Первый вывод',
                 'Выведи строку: TypeScript — это просто!',
                 'TypeScript — это просто!',
                 'const text: string = "TypeScript — это просто!";\nconsole.log(text);',
                 ['console.log', 'TypeScript — это просто!'],
                 ['Используй console.log("текст").',
                  'Текст должен совпадать точно: «TypeScript — это просто!»'],
                 initial='// выведи строку через console.log\n'),
            [q('Как вывести текст в TypeScript?',
               ['print()', 'console.log()', 'echo', 'fmt.Println()'], 1),
             q('Что такое TypeScript?',
               ['JavaScript с типами', 'новый язык без связи с JS',
                'библиотека для стилей', 'фреймворк для игр'], 0)],
            'const x: number = 5;\nconsole.log(x);\n// tsc main.ts — компиляция\n'
            '// node main.js — запуск'),
        lesson(
            2, 'Переменные и типы', 'let, const и аннотации типов',
            ['let — изменяемая переменная, const — константа.',
             'Основные типы: number, string, boolean, any.',
             'TypeScript выводит тип из значения, аннотация не обязательна.'],
            [{'title': 'Переменные',
              'code': 'let age: number = 25;\nconst name: string = "Аня";\nconsole.log(`${name}, ${age}`);',
              'explanation': 'Шаблонная строка подставляет значения через ${}.'}],
            task('typescript', 2, 'Константа города',
                 'Создай константу city со значением «Казань» и выведи её.',
                 'Казань',
                 'const city: string = "Казань";\nconsole.log(city);',
                 ['city', 'console.log'],
                 ['Объяви: const city: string = "Казань";',
                  'Выведи её через console.log(city).'],
                 initial='// объяви константу city\n'),
            [q('Чем const отличается от let?',
               ['const нельзя переназначить', 'let нельзя переназначить',
                'они одинаковы', 'const устарел'], 0),
             q('Какой тип подходит для текста?',
               ['string', 'text', 'str', 'char'], 0)],
            'let count: number = 0;\ncount += 1;\nconst name: string = "Аня";\n'
            'let flag: boolean = true;\nlet anything: any = 5;'),
    ], [
        q('Что даёт аннотация типа?',
          ['проверку типов и подсказки', 'ускорение кода', 'сжатие файла',
           'ничего'], 0, 'Аннотации проверяет компилятор TS.'),
        q('Как вывести строку с подстановкой переменной?',
          ['console.log(`${name}`)', 'console.log($name)', 'echo name',
           'print(name)'], 0, 'В JS и TS используются шаблонные строки.'),
    ]))

COURSES['typescript']['modules'].append(module(
    2, 'Условия и циклы', 'if, for и while', [
        lesson(
            3, 'Условия', 'if / else и тернарный оператор',
            ['Условие пишется в круглых скобках: if (n > 0) { }.',
             'else и else if образуют цепочки условий.',
             'Тернарный оператор: условие ? да : нет.'],
            [{'title': 'if / else',
              'code': 'const n: number = 10;\nif (n > 0) {\n  console.log("положительное");\n} else {\n  console.log("отрицательное");\n}',
              'explanation': 'Фигурные скобки нужны для многострочного тела.'}],
            task('typescript', 3, 'Большое число',
                 'Если n = 12 больше 10 — выведи «большое», иначе «маленькое».',
                 'большое',
                 'const n: number = 12;\nif (n > 10) {\n  console.log("большое");\n} else {\n  console.log("маленькое");\n}',
                 ['if (n > 10)', 'console.log'],
                 ['Условие: n > 10.', 'В блоках выведи нужный текст.'],
                 initial='const n: number = 12;\n// проверь условие\n',
                 difficulty='medium'),
            [q('Какой оператор строгого сравнения в TS?',
               ['===', '==', '=', 'eq'], 0),
             q('Как записать тернарный оператор?',
               ['условие ? да : нет', 'if ? да : нет', 'да || нет',
                'условие -> да'], 0)],
            'if (n > 0) { ... } else if (n === 0) { ... } else { ... }\n'
            'const text = n > 0 ? "плюс" : "минус";'),
        lesson(
            4, 'Циклы', 'for, while и перебор массива',
            ['Классический цикл: for (let i = 0; i < n; i++).',
             'Перебор массива: for (const item of items).',
             'while выполняется, пока условие истинно.'],
            [{'title': 'Счётчик',
              'code': 'for (let i = 1; i <= 3; i++) {\n  console.log(i);\n}',
              'explanation': 'i++ увеличивает счётчик после итерации.'}],
            task('typescript', 4, 'Числа от 1 до 5',
                 'Выведи числа от 1 до 5 через пробел в одной строке.',
                 '1 2 3 4 5',
                 'const nums: number[] = [];\nfor (let i = 1; i <= 5; i++) nums.push(i);\nconsole.log(nums.join(" "));',
                 ['for (let i = 1', 'join'],
                 ['Собери числа 1..5 в массив.',
                  'Выведи его через console.log(nums.join(" ")).'],
                 initial='// выведи числа от 1 до 5 через пробел\n',
                 difficulty='medium'),
            [q('Как перебрать элементы массива?',
               ['for (const x of arr)', 'for (x in arr)', 'foreach (x)',
                'loop x'], 0),
             q('Что делает break?',
               ['выходит из цикла', 'пропускает итерацию',
                'перезапускает цикл', 'ничего'], 0)],
            'for (let i = 0; i < 5; i++) { ... }\nfor (const x of arr) { ... }\n'
            'while (условие) { ... }\nbreak / continue'),
    ], [
        q('Что вернёт 7 % 2 === 0 ? "чёт" : "нечет"?',
          ['нечет', 'чёт', 'ошибку', 'ничего'], 0,
          '7 % 2 равно 1, значит условие ложно.'),
        q('Зачем нужен === вместо ==?',
          ['сравнение без приведения типов', 'быстрее', 'короче',
           'они одинаковы'], 0, '== приводит типы и даёт сюрпризы.'),
    ]))

COURSES['typescript']['modules'].append(module(
    3, 'Массивы и функции', 'Массивы, типизация функций', [
        lesson(
            5, 'Массивы', 'Массивы и методы',
            ['Массив типизируется как number[] или string[].',
             'push добавляет элемент, length даёт длину.',
             'reduce сворачивает массив в одно значение.'],
            [{'title': 'Сумма массива',
              'code': 'const nums: number[] = [3, 6, 9];\nconst sum = nums.reduce((a, b) => a + b, 0);\nconsole.log(sum);',
              'explanation': 'reduce принимает функцию и стартовое значение.'}],
            task('typescript', 5, 'Сумма массива',
                 'Дан массив [3, 6, 9] — выведи сумму его элементов.', '18',
                 'const nums: number[] = [3, 6, 9];\nlet sum = 0;\nfor (const n of nums) sum += n;\nconsole.log(sum);',
                 ['const nums', 'console.log'],
                 ['Пройди массив циклом for..of.',
                  'Складывай элементы в переменную-накопитель.'],
                 initial='const nums: number[] = [3, 6, 9];\n// посчитай сумму\n',
                 difficulty='medium'),
            [q('Как типизировать массив чисел?',
               ['number[]', 'array<number>', 'numbers', 'int[]'], 0),
             q('Что делает push?',
               ['добавляет элемент в конец', 'удаляет элемент', 'сортирует',
                'возвращает длину'], 0)],
            'const nums: number[] = [1, 2, 3];\nnums.push(4);\nnums.length\n'
            'const sum = nums.reduce((a, b) => a + b, 0);\nnums.map(n => n * 2);'),
        lesson(
            6, 'Функции', 'Аргументы, возвращаемый тип и стрелки',
            ['Типы аргументов указываются после имени: (a: number, b: number).',
             'Тип возврата пишется после скобок: ): number { ... }.',
             'Стрелочная функция: const add = (a: number, b: number) => a + b.'],
            [{'title': 'Функция сложения',
              'code': 'function add(a: number, b: number): number {\n  return a + b;\n}\nconsole.log(add(3, 4));',
              'explanation': 'Тип возврата помогает редактору подсказывать.'}],
            task('typescript', 6, 'Функция double',
                 'Напиши функцию double(n: number): number, возвращающую '
                 'удвоенное число, и выведи double(7).', '14',
                 'function double(n: number): number {\n  return n * 2;\n}\nconsole.log(double(7));',
                 ['function double', 'return'],
                 ['Объяви функцию до её вызова.',
                  'Умножь параметр на 2 и верни результат.'],
                 initial='// объяви функцию double и выведи double(7)\n',
                 difficulty='hard'),
            [q('Как указать тип возврата?',
               ['после скобок: ): number', 'до имени функции', 'внутри тела',
                'никак'], 0),
             q('Что такое стрелочная функция?',
               ['const f = (a: number) => a * 2', 'function f(a) => a * 2',
                'def f(a): a * 2', 'f = (a) -> a * 2'], 0)],
            'function add(a: number, b: number): number { return a + b; }\n'
            'const double = (n: number): number => n * 2;\nvoid — нет результата'),
    ], [
        q('Что делает reduce?',
          ['сворачивает массив в одно значение', 'сортирует массив',
           'фильтрует элементы', 'добавляет элемент'], 0,
          'Например, сумму всех чисел.'),
        q('Зачем типизировать функции?',
          ['редактор проверяет аргументы и результат', 'код работает быстрее',
           'уменьшается файл', 'ни за чем'], 0,
          'Ошибки находятся ещё до запуска.'),
    ]))

COURSES['typescript']['entrance_test'] = [
    q('Как вывести текст в TypeScript?',
      ['print()', 'console.log()', 'echo', 'fmt.Println()'], 1),
    q('Чем const отличается от let?',
      ['const нельзя переназначить', 'let нельзя переназначить',
       'они одинаковы', 'const устарел'], 0),
    q('Какой тип подходит для текста?', ['string', 'text', 'str', 'char'], 0),
    q('Как типизировать массив чисел?',
      ['number[]', 'array<number>', 'int[]', 'numbers'], 0),
    q('Какой оператор строгого сравнения?', ['===', '==', '=', 'eq'], 0),
    q('Как объявить тип возврата функции?',
      ['после скобок через :', 'до имени функции', 'внутри тела', 'никак'], 0),
    q('Что делает push?',
      ['добавляет элемент в конец массива', 'удаляет элемент',
       'сортирует массив', 'возвращает длину'], 0),
    q('Из какого языка TypeScript получил основу?',
      ['JavaScript', 'Java', 'C#', 'Python'], 0),
]

COURSES['typescript']['cheatsheets'] = [
    cheat(0, 'Основы',
          'const x: number = 5;\nconsole.log(x);\n// tsc main.ts\n// node main.js',
          'Любой корректный JavaScript-код подходит и для TypeScript.'),
    cheat(1, 'Типы',
          'let n: number = 5;\nlet s: string = "текст";\nlet b: boolean = true;\n'
          'let a: any = null;',
          'any отключает проверку типов.'),
    cheat(2, 'Условия',
          'if (n > 0) { ... } else { ... }\n'
          'const text = n > 0 ? "плюс" : "минус";',
          'Используй === вместо ==.'),
    cheat(3, 'Циклы',
          'for (let i = 0; i < 5; i++) { ... }\nfor (const x of arr) { ... }\n'
          'while (условие) { ... }',
          'for..in перебирает ключи, for..of — значения.'),
    cheat(4, 'Массивы',
          'const nums: number[] = [1, 2, 3];\nnums.push(4);\nnums.length\n'
          'nums.map(n => n * 2)\nnums.reduce((a, b) => a + b, 0)',
          'Методы массива возвращают новые значения.'),
    cheat(5, 'Функции',
          'function add(a: number, b: number): number {\n  return a + b;\n}\n'
          'const double = (n: number): number => n * 2;',
          'Тип возврата указывается после скобок.'),
]

COURSES['php'] = {
    'name': 'PHP', 'icon': '\U0001F7E1', 'color': '#777BB4',
    'description': 'Язык веб-разработки: на PHP работает большинство сайтов, '
                   'он отлично подходит для серверной части.',
    'difficulty': 'Лёгкий старт',
    'final_project': 'Обработчик формы обратной связи',
    'modules': [],
}

COURSES['php']['modules'].append(module(
    1, 'Основы PHP', 'Теги PHP, переменные и типы', [
        lesson(
            1, 'Первая программа', 'Тег <?php и echo',
            ['PHP-код вставляется между <?php и ?> (закрывающий тег не обязателен).',
             'Переменные начинаются со знака $ — тип определяется сам.',
             'echo выводит текст, каждый оператор заканчивается точкой с запятой.'],
            [{'title': 'Привет, мир', 'code': '<?php\necho "Привет, мир!";',
              'explanation': 'echo — самая простая команда вывода в PHP.'}],
            task('php', 1, 'Первый вывод', 'Выведи строку: PHP — это просто!',
                 'PHP — это просто!', '<?php\necho "PHP — это просто!";',
                 ['echo', 'PHP — это просто!'],
                 ['Напиши echo "PHP — это просто!";',
                  'Не забудь точку с запятой в конце строки.'],
                 initial='<?php\n// выведи строку через echo\n'),
            [q('Как вывести текст в PHP?',
               ['print()', 'echo', 'console.log()', 'cout <<'], 1),
             q('Как начинается PHP-файл?',
               ['<?php', '<php>', '#php', 'package php;'], 0)],
            '<?php\necho "текст";\n// комментарий\n/* многострочный комментарий */'),
        lesson(
            2, 'Переменные и типы', 'Переменные со знаком $',
            ['Переменная объявляется так: $name = "Аня";',
             'Основные типы: int, float, string, bool, array.',
             'Склейка строк — точка, в двойных кавычках переменные подставляются.'],
            [{'title': 'Переменные',
              'code': '<?php\n$name = "Артур";\n$age = 25;\n'
                      'echo "Меня зовут {$name}, мне {$age}";',
              'explanation': 'Фигурные скобки помогают подставить переменную.'}],
            task('php', 2, 'Переменная года',
                 'Создай переменную $year со значением 2026 и выведи её.',
                 '2026', '<?php\n$year = 2026;\necho $year;',
                 ['$year = 2026', 'echo $year'],
                 ['Объяви переменную: $year = 2026;',
                  'Выведи её командой echo $year;'],
                 initial='<?php\n// объяви $year\n'),
            [q('Как в PHP обозначается переменная?',
               ['$name', 'name', '@name', 'var name'], 0),
             q('Чем склеиваются строки?',
               ['точкой .', 'плюсом +', 'запятой', 'амперсандом &'], 0)],
            '$name = "Аня";\n$age = 25;\n$price = 199.9;\n$ok = true;\n'
            '$items = [1, 2, 3];\necho "Привет, {$name}!";'),
    ], [
        q('Что означает $ в начале имени?',
          ['признак переменной', 'оператор', 'комментарий', 'конец строки'], 0,
          'Без $ интерпретатор не поймёт, что это переменная.'),
        q('Как закончить оператор?',
          ['точкой с запятой ;', 'точкой .', 'двоеточием :', 'ничем'], 0,
          'Иначе получите синтаксическую ошибку.'),
    ]))

COURSES['php']['modules'].append(module(
    2, 'Условия и циклы', 'if, elseif и циклы', [
        lesson(
            3, 'Условия', 'if / else и elseif',
            ['Условие пишется в круглых скобках, тело — в фигурных.',
             'elseif даёт цепочку проверок.',
             'Логика: && (и), || (или), ! (не).'],
            [{'title': 'if / else',
              'code': '<?php\n$n = 10;\nif ($n > 0) {\n    echo "положительное";\n'
                      '} else {\n    echo "отрицательное";\n}',
              'explanation': 'PHP не требуется объявлять тип переменной.'}],
            task('php', 3, 'Большое число',
                 'Если $n = 12 больше 10 — выведи «большое», иначе «маленькое».',
                 'большое',
                 '<?php\n$n = 12;\nif ($n > 10) {\n    echo "большое";\n'
                 '} else {\n    echo "маленькое";\n}',
                 ['if ($n > 10)', 'echo'],
                 ['Условие: $n > 10.', 'В блоках выведи нужный текст.'],
                 initial='<?php\n$n = 12;\n// проверь условие\n',
                 difficulty='medium'),
            [q('Какой оператор сравнения строгий?', ['===', '==', '=', 'eq'], 0),
             q('Как записать «и»?', ['&&', 'and()', '&', '+'], 0)],
            'if ($n > 0) { ... } elseif ($n === 0) { ... } else { ... }\n'
            '$text = $n > 0 ? "плюс" : "минус";'),
        lesson(
            4, 'Циклы', 'for, while и foreach',
            ['for ($i = 0; $i < 5; $i++) — счётчик с тремя секциями.',
             'foreach перебирает массивы.',
             'while и do..while работают по условию.'],
            [{'title': 'Счётчик',
              'code': '<?php\nfor ($i = 1; $i <= 3; $i++) {\n    echo $i . " ";\n}',
              'explanation': 'Секции for разделяются точкой с запятой.'}],
            task('php', 4, 'Числа от 1 до 5',
                 'Выведи числа от 1 до 5 через пробел в одной строке.',
                 '1 2 3 4 5',
                 '<?php\nfor ($i = 1; $i <= 5; $i++) {\n    echo $i;\n'
                 '    if ($i < 5) echo " ";\n}',
                 ['for ($i = 1', 'echo'],
                 ['Используй for ($i = 1; $i <= 5; $i++).',
                  'После каждого числа, кроме последнего, выводи пробел.'],
                 initial='<?php\n// выведи числа от 1 до 5\n',
                 difficulty='medium'),
            [q('Какой цикл перебирает массив?',
               ['foreach', 'for', 'while', 'repeat'], 0),
             q('Что делает break?',
               ['выходит из цикла', 'пропускает итерацию',
                'перезапускает цикл', 'ничего'], 0)],
            'for ($i = 0; $i < 5; $i++) { ... }\n'
            'foreach ($items as $item) { ... }\nwhile ($условие) { ... }\n'
            'break / continue'),
    ], [
        q('Сколько секций у цикла for?', ['три', 'две', 'одна', 'четыре'], 0,
          'Инициализация, условие и шаг.'),
        q('Что делает var_dump?',
          ['печатает структуру и тип переменной', 'удаляет переменную',
           'сортирует массив', 'считает длину'], 0,
          'Незаменимо при отладке.'),
    ]))

COURSES['php']['modules'].append(module(
    3, 'Массивы и функции', 'Массивы, count и свои функции', [
        lesson(
            5, 'Массивы', 'Индексные массивы и count',
            ['Массив создаётся так: $nums = [3, 6, 9];',
             'count($nums) — количество элементов.',
             'array_sum складывает элементы, sort сортирует массив.'],
            [{'title': 'Сумма массива',
              'code': '<?php\n$nums = [3, 6, 9];\n$sum = 0;\n'
                      'foreach ($nums as $n) {\n    $sum += $n;\n}\necho $sum;',
              'explanation': 'foreach перебирает значения массива.'}],
            task('php', 5, 'Сумма массива',
                 'Дан массив $nums = [3, 6, 9] — выведи сумму его элементов.',
                 '18',
                 '<?php\n$nums = [3, 6, 9];\n$sum = 0;\n'
                 'foreach ($nums as $n) {\n    $sum += $n;\n}\necho $sum;',
                 ['$nums = [3, 6, 9]', 'foreach'],
                 ['Пройди массив циклом foreach.',
                  'Складывай значения в переменную-накопитель.'],
                 initial='<?php\n$nums = [3, 6, 9];\n// посчитай сумму\n',
                 difficulty='medium'),
            [q('Как узнать количество элементов массива?',
               ['count($nums)', '$nums.length', 'len($nums)', 'size($nums)'], 0),
             q('Как создать массив?', ['$a = [1, 2, 3];', '$a = (1, 2, 3);',
                                       'array a = 1,2,3;', 'a = [1, 2];'], 0)],
            '$nums = [1, 2, 3];\n$nums[] = 4;\ncount($nums)\n'
            'array_sum($nums)\nsort($nums);\n$user = ["name" => "Аня", "age" => 25];'),
        lesson(
            6, 'Функции', 'function, аргументы и return',
            ['Функция объявляется словом function.',
             'Параметры перечисляются в скобках: function add($a, $b).',
             'return возвращает значение, тип не объявляется.'],
            [{'title': 'Функция сложения',
              'code': '<?php\nfunction add($a, $b) {\n    return $a + $b;\n}\n'
                      'echo add(3, 4);',
              'explanation': 'Вызов функции может стоять прямо внутри echo.'}],
            task('php', 6, 'Функция double',
                 'Напиши функцию double($n), возвращающую $n * 2, '
                 'и выведи double(7).', '14',
                 '<?php\nfunction double($n) {\n    return $n * 2;\n}\n'
                 'echo double(7);',
                 ['function double', 'return'],
                 ['Объяви функцию до её вызова.',
                  'Умножь параметр на 2 и верни результат через return.'],
                 initial='<?php\n// объяви функцию double и выведи double(7)\n',
                 difficulty='hard'),
            [q('Как объявить функцию в PHP?',
               ['function add($a, $b)', 'def add(a, b)', 'func add(a int)',
                'void add(a, b)'], 0),
             q('Что делает return?',
               ['возвращает значение', 'печатает значение',
                'завершает программу', 'объявляет переменную'], 0)],
            'function add($a, $b) {\n    return $a + $b;\n}\n'
            'echo add(3, 4);\nfunction greet(string $name): string { ... }'),
    ], [
        q('Что делает array_sum?',
          ['складывает элементы массива', 'сортирует массив',
           'фильтрует массив', 'создаёт массив'], 0,
          'А count даёт количество элементов.'),
        q('Нужно ли указывать тип параметра?',
          ['нет, но можно указать', 'да, обязательно', 'только для строк',
           'только для чисел'], 0, 'PHP динамический, но типы поддерживает.'),
    ]))

COURSES['php']['entrance_test'] = [
    q('Как вывести текст в PHP?', ['print()', 'echo', 'console.log()',
                                  'cout <<'], 1),
    q('Как начинается PHP-файл?', ['<?php', '<php>', '#php', 'package php;'], 0),
    q('Как обозначается переменная?', ['$name', 'name', '@name', 'var name'], 0),
    q('Чем склеиваются строки?', ['точкой .', 'плюсом +', 'запятой', '&'], 0),
    q('Какой цикл перебирает массив?', ['foreach', 'for', 'while', 'repeat'], 0),
    q('Как создать массив?', ['$a = [1, 2, 3];', '$a = (1, 2, 3);',
                              'array a = 1,2,3;', 'a = [1, 2];'], 0),
    q('Как объявить функцию?', ['function add($a, $b)', 'def add(a, b)',
                                'func add(a int)', 'void add(a, b)'], 0),
    q('Что делает count($nums)?',
      ['возвращает количество элементов', 'сумму элементов', 'сортирует',
       'создаёт массив'], 0),
]

COURSES['php']['cheatsheets'] = [
    cheat(0, 'Основы', '<?php\necho "Привет";\n// комментарий',
          'Закрывающий тег ?> в конце файла не обязателен.'),
    cheat(1, 'Переменные',
          '$name = "Аня";\n$age = 25;\n$price = 199.9;\n$ok = true;\n'
          'echo "Привет, {$name}!";',
          'Тип переменной определяется по значению.'),
    cheat(2, 'Условия',
          'if ($n > 0) { ... } elseif ($n === 0) { ... } else { ... }\n'
          '$text = $n > 0 ? "плюс" : "минус";',
          '=== сравнивает без приведения типов.'),
    cheat(3, 'Циклы',
          'for ($i = 0; $i < 5; $i++) { ... }\n'
          'foreach ($items as $item) { ... }\nwhile ($условие) { ... }',
          'foreach работает и со значениями, и с ключами.'),
    cheat(4, 'Массивы',
          '$nums = [1, 2, 3];\n$nums[] = 4;\ncount($nums)\narray_sum($nums)\n'
          '$user = ["name" => "Аня"];',
          'Массивы бывают индексные и ассоциативные.'),
    cheat(5, 'Функции',
          'function add($a, $b) {\n    return $a + $b;\n}\n\necho add(3, 4);',
          'Типы параметров можно указывать, но не обязательно.'),
]

COURSES['rust'] = {
    'name': 'Rust', 'icon': '\U0001F980', 'color': '#DEA584',
    'description': 'Системный язык без сборщика мусора: безопасная работа '
                   'с памятью и скорость C++.',
    'difficulty': 'Сложный старт',
    'final_project': 'Утилита подсчёта слов в файле',
    'modules': [],
}

COURSES['rust']['modules'].append(module(
    1, 'Основы Rust', 'Привет, мир, переменные и типы', [
        lesson(
            1, 'Первая программа', 'fn main и макрос println!',
            ['Rust компилируется в машинный код без сборщика мусора.',
             'Точка входа — функция fn main().',
             'println! — макрос вывода, обрати внимание на восклицательный знак.'],
            [{'title': 'Привет, мир',
              'code': 'fn main() {\n    println!("Привет, мир!");\n}',
              'explanation': 'Фигурные скобки задают тело функции.'}],
            task('rust', 1, 'Первый вывод',
                 'Выведи строку: Rust — это просто!', 'Rust — это просто!',
                 'fn main() {\n    println!("Rust — это просто!");\n}',
                 ['println!', 'Rust — это просто!'],
                 ['Используй println!("текст");',
                  'Не забудь точку с запятой и восклицательный знак в имени макроса.'],
                 initial='fn main() {\n    // выведи строку\n}'),
            [q('Как вывести текст в Rust?',
               ['print()', 'println!("текст")', 'echo', 'console.log()'], 1),
             q('Как объявляется точка входа?',
               ['fn main()', 'void main()', 'function main()', 'main()'], 0)],
            'fn main() {\n    println!("Привет");\n}\n// cargo run — сборка и запуск\n'
            '// rustc main.rs — компиляция'),
        lesson(
            2, 'Переменные и типы', 'let, mut и типы',
            ['let объявляет переменную, по умолчанию она неизменяемая.',
             'mut делает переменную изменяемой: let mut x = 5;',
             'Основные типы: i32, f64, bool, String, &str.',
             'Тип можно не указывать — компилятор выведет его сам.'],
            [{'title': 'Переменные',
              'code': 'let name = "Артур";\nlet mut age = 25;\nage += 1;\n'
                      'println!("{} {}", name, age);',
              'explanation': '{} — плейсхолдер для значения.'}],
            task('rust', 2, 'Переменная города',
                 'Создай переменную city со значением «Казань» и выведи её.',
                 'Казань',
                 'fn main() {\n    let city = "Казань";\n    println!("{}", city);\n}',
                 ['let city', 'println!'],
                 ['Объяви: let city = "Казань";',
                  'Выведи её через println!("{}", city);'],
                 initial='fn main() {\n    // объяви city\n}'),
            [q('Как сделать переменную изменяемой?',
               ['let mut x = 5;', 'let x = 5;', 'var x = 5;', 'mutable x = 5;'], 0),
             q('Какой тип у строкового литерала?',
               ['&str', 'String', 'char', 'text'], 0)],
            'let x = 5;          // неизменяемая\nlet mut y = 10;     // изменяемая\n'
            'let pi: f64 = 3.14;\nlet ok: bool = true;'),
    ], [
        q('Что означает восклицательный знак в println!?',
          ['это макрос', 'это ошибка', 'это комментарий', 'это тип'], 0,
          'В Rust макросы вызываются с !.'),
        q('Какая переменная изменяемая?',
          ['let mut x = 5;', 'let x = 5;', 'const x = 5;', 'static x = 5;'], 0,
          'Без mut значение менять нельзя.'),
    ]))

COURSES['rust']['modules'].append(module(
    2, 'Условия и циклы', 'if, match, for и while', [
        lesson(
            3, 'Условия', 'if, else и match',
            ['Условие пишется без круглых скобок: if n > 0 { }.',
             'if — это выражение: ветвь возвращает значение.',
             'match сравнивает значение с шаблонами и требует все случаи.'],
            [{'title': 'if / else',
              'code': 'let n = 10;\nif n > 0 {\n    println!("положительное");\n'
                      '} else {\n    println!("отрицательное");\n}',
              'explanation': 'Круглые скобки в условии не нужны.'}],
            task('rust', 3, 'Большое число',
                 'Если n = 12 больше 10 — выведи «большое», иначе «маленькое».',
                 'большое',
                 'fn main() {\n    let n = 12;\n    if n > 10 {\n'
                 '        println!("большое");\n    } else {\n'
                 '        println!("маленькое");\n    }\n}',
                 ['if n > 10', 'println!'],
                 ['Условие: n > 10.', 'В блоках выведи нужный текст.'],
                 initial='fn main() {\n    let n = 12;\n    // проверь условие\n}',
                 difficulty='medium'),
            [q('Нужны ли круглые скобки вокруг условия?',
               ['нет', 'да', 'только с else', 'только для чисел'], 0),
             q('Какой оператор означает «и»?', ['&&', 'and', '&', '++'], 0)],
            'if n > 0 { ... } else { ... }\n'
            'let text = if n > 0 { "плюс" } else { "минус" };\n'
            'match n {\n    0 => println!("ноль"),\n    _ => println!("другое"),\n}'),
        lesson(
            4, 'Циклы', 'for, while и диапазоны',
            ['Диапазон: 1..=5 включает 5, 1..5 — нет.',
             'for перебирает диапазоны и коллекции.',
             'while выполняется, пока условие истинно; loop — бесконечный цикл.'],
            [{'title': 'Счётчик',
              'code': 'for i in 1..=3 {\n    println!("{}", i);\n}',
              'explanation': '1..=3 — диапазон с включённым правым концом.'}],
            task('rust', 4, 'Числа от 1 до 5',
                 'Выведи числа от 1 до 5 через пробел в одной строке.',
                 '1 2 3 4 5',
                 'fn main() {\n    for i in 1..=5 {\n        print!("{}", i);\n'
                 '        if i < 5 {\n            print!(" ");\n        }\n    }\n'
                 '    println!();\n}',
                 ['for i in 1..=5', 'print!'],
                 ['Используй цикл for i in 1..=5.',
                  'Печатай числа макросом print! и разделяй пробелом.'],
                 initial='fn main() {\n    // выведи числа от 1 до 5\n}',
                 difficulty='medium'),
            [q('Какой диапазон включает 5?',
               ['1..=5', '1..5', '[1..5]', '1:5'], 0),
             q('Что делает break?',
               ['выходит из цикла', 'пропускает итерацию',
                'перезапускает цикл', 'ничего'], 0)],
            'for i in 1..=5 { ... }\nfor x in items.iter() { ... }\n'
            'while условие { ... }\nloop { break; }'),
    ], [
        q('Чем if отличается от других языков?',
          ['это выражение, возвращающее значение', 'требует круглых скобок',
           'не имеет else', 'работает только с числами'], 0,
          'Значение ветви можно присвоить переменной.'),
        q('Что обязательно в match?',
          ['все случаи должны быть покрыты', 'наличие break',
           'круглые скобки', 'ключевое слово else'], 0,
          'Шаблон _ закрывает оставшиеся варианты.'),
    ]))

COURSES['rust']['modules'].append(module(
    3, 'Коллекции и функции', 'Vec, итераторы и свои функции', [
        lesson(
            5, 'Векторы и итераторы', 'Vec и перебор значений',
            ['Вектор создаётся макросом vec![1, 2, 3].',
             'len() даёт длину, push добавляет элемент.',
             'Итераторы: nums.iter() и метод sum().'],
            [{'title': 'Сумма вектора',
              'code': 'let nums = vec![3, 6, 9];\nlet sum: i32 = nums.iter().sum();\n'
                      'println!("{}", sum);',
              'explanation': 'iter() создаёт итератор, sum() суммирует значения.'}],
            task('rust', 5, 'Сумма вектора',
                 'Дан вектор vec![3, 6, 9] — выведи сумму его элементов.', '18',
                 'fn main() {\n    let nums = vec![3, 6, 9];\n    let mut sum = 0;\n'
                 '    for n in nums.iter() {\n        sum += n;\n    }\n'
                 '    println!("{}", sum);\n}',
                 ['vec![3, 6, 9]', 'println!'],
                 ['Пройди вектор циклом for или используй nums.iter().sum().',
                  'Складывай значения в накопитель и выведи его.'],
                 initial='fn main() {\n    let nums = vec![3, 6, 9];\n    // посчитай сумму\n}',
                 difficulty='medium'),
            [q('Как создать вектор?',
               ['vec![1, 2, 3]', '[1, 2, 3]', 'Vec(1, 2, 3)', 'array![1, 2, 3]'], 0),
             q('Что делает nums.len()?',
               ['возвращает длину', 'сумму', 'сортирует', 'добавляет элемент'], 0)],
            'let nums = vec![1, 2, 3];\nnums.push(4);\nnums.len()\n'
            'let sum: i32 = nums.iter().sum();\n'
            'let doubled: Vec<i32> = nums.iter().map(|n| n * 2).collect();'),
        lesson(
            6, 'Функции', 'fn, типы и возвращаемые значения',
            ['Функция объявляется словом fn.',
             'Типы параметров указываются обязательно: fn double(n: i32) -> i32.',
             'Последнее выражение без точки с запятой становится результатом.'],
            [{'title': 'Функция сложения',
              'code': 'fn add(a: i32, b: i32) -> i32 {\n    a + b\n}\n\n'
                      'println!("{}", add(3, 4));',
              'explanation': 'Без ; строка становится возвращаемым значением.'}],
            task('rust', 6, 'Функция double',
                 'Напиши функцию double(n: i32) -> i32, возвращающую удвоенное '
                 'число, и выведи double(7).', '14',
                 'fn double(n: i32) -> i32 {\n    n * 2\n}\n\n'
                 'fn main() {\n    println!("{}", double(7));\n}',
                 ['fn double', 'fn main'],
                 ['Объяви функцию перед main.',
                  'Верни n * 2 — выражением без ; или через return.'],
                 initial='fn main() {\n    // выведи double(7)\n}',
                 difficulty='hard'),
            [q('Как объявить функцию в Rust?',
               ['fn double(n: i32) -> i32', 'func double(n int) int',
                'def double(n)', 'function double(n)'], 0),
             q('Что означает -> i32?',
               ['тип возвращаемого значения', 'тип аргумента', 'комментарий',
                'макрос'], 0)],
            'fn add(a: i32, b: i32) -> i32 {\n    a + b\n}\n'
            'fn print_it(s: &str) { println!("{}", s); }\n'
            'if a > b { a } else { b }'),
    ], [
        q('Что делает iter().sum()?',
          ['суммирует элементы', 'сортирует', 'фильтрует', 'печатает'], 0,
          'Итераторы позволяют писать короткие цепочки вызовов.'),
        q('Как вернуть значение из функции?',
          ['выражением без ; или через return', 'только через return',
           'через echo', 'функция не может вернуть значение'], 0,
          'Последнее выражение становится результатом.'),
    ]))

COURSES['rust']['entrance_test'] = [
    q('Как вывести текст в Rust?',
      ['print()', 'println!("текст")', 'echo', 'console.log()'], 1),
    q('Как объявляется точка входа?',
      ['fn main()', 'void main()', 'function main()', 'main()'], 0),
    q('Как сделать переменную изменяемой?',
      ['let mut x = 5;', 'let x = 5;', 'var x = 5;', 'mutable x = 5;'], 0),
    q('Какой диапазон включает 5?', ['1..=5', '1..5', '[1..5]', '1:5'], 0),
    q('Как создать вектор?',
      ['vec![1, 2, 3]', '[1, 2, 3]', 'Vec(1, 2, 3)', 'array![1, 2, 3]'], 0),
    q('Как объявить функцию?',
      ['fn double(n: i32) -> i32', 'func double(n int) int', 'def double(n)',
       'function double(n)'], 0),
    q('Нужны ли круглые скобки вокруг условия?',
      ['нет', 'да', 'только с else', 'только для чисел'], 0),
    q('Что означает восклицательный знак в println!?',
      ['это макрос', 'это ошибка', 'это комментарий', 'это тип'], 0),
]

COURSES['rust']['cheatsheets'] = [
    cheat(0, 'Основы',
          'fn main() {\n    println!("Привет");\n}\n// rustc main.rs\n// cargo run',
          'println! — макрос, поэтому нужен восклицательный знак.'),
    cheat(1, 'Переменные',
          'let x = 5;\nlet mut y = 10;\nlet pi: f64 = 3.14;\nlet ok: bool = true;',
          'По умолчанию переменные неизменяемы.'),
    cheat(2, 'Условия',
          'if n > 0 { ... } else { ... }\n'
          'let text = if n > 0 { "плюс" } else { "минус" };\n'
          'match n {\n    0 => println!("ноль"),\n    _ => println!("другое"),\n}',
          'match обязан покрывать все варианты.'),
    cheat(3, 'Циклы',
          'for i in 1..=5 { ... }\nwhile условие { ... }\nloop { break; }',
          '1..=5 включает 5, 1..5 — нет.'),
    cheat(4, 'Коллекции',
          'let mut nums = vec![1, 2, 3];\nnums.push(4);\nnums.len()\n'
          'let sum: i32 = nums.iter().sum();',
          'Vec — растущий массив из стандартной библиотеки.'),
    cheat(5, 'Функции',
          'fn add(a: i32, b: i32) -> i32 {\n    a + b\n}',
          'Последнее выражение без ; становится результатом.'),
]

# ===== END DATA =====


if __name__ == '__main__':
    for code, course in COURSES.items():
        build(code, course)