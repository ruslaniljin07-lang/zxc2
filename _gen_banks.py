# -*- coding: utf-8 -*-
"""Temp generator: банки задач data/tasks/<lang>.json (по 30 задач)."""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.join(ROOT, 'data', 'tasks')

CHECK_TYPE = {
    'python': 'stdout', 'javascript': 'stdout_js', 'java': 'stdout_java',
    'cpp': 'stdout_cpp', 'go': 'stdout_go', 'csharp': 'stdout_csharp',
    'typescript': 'stdout_ts', 'php': 'stdout_php', 'rust': 'stdout_rust',
}

SCAFFOLD = {
    'python': '# Твой код здесь\n',
    'javascript': '// Твой код здесь\n',
    'typescript': '// Твой код здесь\n',
    'java': ('public class Main {\n    public static void main(String[] args) {\n'
             '        // Твой код здесь\n    }\n}\n'),
    'cpp': ('#include <iostream>\nusing namespace std;\n\nint main() {\n'
            '    // Твой код здесь\n    return 0;\n}\n'),
    'go': 'package main\n\nimport "fmt"\n\nfunc main() {\n\t// Твой код здесь\n}\n',
    'csharp': ('using System;\n\nclass Program {\n    static void Main() {\n'
               '        // Твой код здесь\n    }\n}\n'),
    'php': '<?php\n// Твой код здесь\n',
    'rust': 'fn main() {\n    // Твой код здесь\n}\n',
}

# ключевая конструкция вывода для языков без тулчейна (проверка contains)
LANG_TOKEN = {
    'java': 'System.out.println', 'cpp': 'cout', 'csharp': 'Console.WriteLine',
    'php': 'echo', 'rust': 'println!',
}


def j(body, extra=''):
    """Обёртка Java-программы. extra — дополнительные методы класса."""
    pad = '\n'.join('        ' + line for line in body.split('\n'))
    tail = ('\n\n' + '\n'.join('    ' + line for line in extra.split('\n'))
            if extra else '')
    return ('public class Main {\n    public static void main(String[] args) {\n'
            + pad + '\n    }' + tail + '\n}')


def cs(body, extra=''):
    """Обёртка C#-программы. extra — дополнительные методы класса."""
    pad = '\n'.join('        ' + line for line in body.split('\n'))
    tail = ('\n\n' + '\n'.join('    ' + line for line in extra.split('\n'))
            if extra else '')
    return ('using System;\n\nclass Program {\n    static void Main() {\n'
            + pad + '\n    }' + tail + '\n}')


def go(body, imports='fmt', extra=''):
    """Обёртка Go-программы. Несколько импортов — через ';'."""
    pad = '\n'.join('\t' + line for line in body.split('\n'))
    if ';' in imports:
        block = ''.join('\t"' + i.strip() + '"\n' for i in imports.split(';'))
        head = 'import (\n' + block + ')'
    else:
        head = 'import "' + imports + '"'
    tail = '\n\n' + extra if extra else ''
    return f'package main\n\n{head}\n\nfunc main() {{\n{pad}\n}}{tail}'


def cpp(body, incs=(), pre=''):
    """Обёртка C++-программы. pre — код перед main (например, функции)."""
    head = ''.join('#include <' + i + '>\n' for i in incs)
    pad = '\n'.join('    ' + line for line in body.split('\n'))
    before = pre + '\n\n' if pre else ''
    return (head + '#include <iostream>\nusing namespace std;\n\n' + before
            + 'int main() {\n' + pad + '\n    return 0;\n}')


def rs(body, pre=''):
    """Обёртка Rust-программы. pre — код перед main (например, функции)."""
    pad = '\n'.join('    ' + line for line in body.split('\n'))
    before = pre + '\n\n' if pre else ''
    return before + 'fn main() {\n' + pad + '\n}'


TASKS = []


def add(**kw):
    TASKS.append(kw)


def _require(spec, lang):
    """Собирает список обязательных конструкций для языка."""
    lit = spec.get('lit')
    if isinstance(lit, dict):
        literals = lit.get(lang, [])
    else:
        literals = lit or []
    if lang not in LANG_TOKEN:
        return None
    return [LANG_TOKEN[lang]] + list(literals)


def _task(spec, lang):
    check = {'type': CHECK_TYPE[lang], 'expected': spec['expected']}
    if spec.get('mode'):
        check['mode'] = spec['mode']
    req = _require(spec, lang)
    if req:
        check['require'] = req
    return {
        'id': spec['id'],
        'title': spec['title'],
        'topic': spec['topic'],
        'difficulty': spec['diff'],
        'xp': spec['xp'],
        'description': spec['desc'],
        'initial_code': spec.get('initial', SCAFFOLD[lang]),
        'check': check,
        'hints': spec['hints'],
        'solution': spec['code'][lang],
    }


def build(langs):
    """Пишет банки задач: файл целиком (единый набор задач для всех языков)."""
    for lang in langs:
        path = os.path.join(TASKS_DIR, lang + '.json')
        tasks = [_task(s, lang) for s in TASKS if lang in s['code']]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'tasks': tasks}, f, ensure_ascii=False, indent=1)
        print(lang, '->', len(tasks), 'задач')


# ===== TASKS =====

add(id=6, title='Положительное или нет', topic='Условия', diff='easy', xp=10,
    desc='Число a = 10. Если оно больше нуля — выведи «положительное», '
         'иначе — «отрицательное».',
    expected='положительное', lit=['10'],
    hints=['Используй конструкцию if / else.',
           'Условие: a > 0. Тело условия выделяется фигурными скобками '
           'или отступами — зависит от языка.'],
    code={
        'python': 'a = 10\nif a > 0:\n    print("положительное")\n'
                  'else:\n    print("отрицательное")',
        'javascript': 'const a = 10;\nif (a > 0) {\n'
                      '  console.log("положительное");\n} else {\n'
                      '  console.log("отрицательное");\n}',
        'typescript': 'const a: number = 10;\nif (a > 0) {\n'
                      '  console.log("положительное");\n} else {\n'
                      '  console.log("отрицательное");\n}',
        'java': j('int a = 10;\nif (a > 0) {\n'
                  '    System.out.println("положительное");\n} else {\n'
                  '    System.out.println("отрицательное");\n}'),
        'cpp': cpp('int a = 10;\nif (a > 0) {\n'
                   '    cout << "положительное" << endl;\n} else {\n'
                   '    cout << "отрицательное" << endl;\n}'),
        'csharp': cs('int a = 10;\nif (a > 0) {\n'
                     '    Console.WriteLine("положительное");\n} else {\n'
                     '    Console.WriteLine("отрицательное");\n}'),
        'go': go('a := 10\nif a > 0 {\n\tfmt.Println("положительное")\n'
                 '} else {\n\tfmt.Println("отрицательное")\n}'),
        'php': '<?php\n$a = 10;\nif ($a > 0) {\n'
               '    echo "положительное";\n} else {\n'
               '    echo "отрицательное";\n}',
        'rust': rs('let a = 10;\nif a > 0 {\n'
                   '    println!("положительное");\n} else {\n'
                   '    println!("отрицательное");\n}'),
    })

add(id=7, title='Чётное или нечётное', topic='Условия', diff='easy', xp=10,
    desc='Число n = 8. Выведи «чётное», если оно делится на 2 без остатка, '
         'иначе — «нечётное».',
    expected='чётное', lit=['8', '%'],
    hints=['Остаток от деления даёт оператор %.',
           'Чётное число даёт остаток 0: n % 2 == 0.'],
    code={
        'python': 'n = 8\nif n % 2 == 0:\n    print("чётное")\n'
                  'else:\n    print("нечётное")',
        'javascript': 'const n = 8;\nif (n % 2 === 0) {\n'
                      '  console.log("чётное");\n} else {\n'
                      '  console.log("нечётное");\n}',
        'typescript': 'const n: number = 8;\nif (n % 2 === 0) {\n'
                      '  console.log("чётное");\n} else {\n'
                      '  console.log("нечётное");\n}',
        'java': j('int n = 8;\nif (n % 2 == 0) {\n'
                  '    System.out.println("чётное");\n} else {\n'
                  '    System.out.println("нечётное");\n}'),
        'cpp': cpp('int n = 8;\nif (n % 2 == 0) {\n'
                   '    cout << "чётное" << endl;\n} else {\n'
                   '    cout << "нечётное" << endl;\n}'),
        'csharp': cs('int n = 8;\nif (n % 2 == 0) {\n'
                     '    Console.WriteLine("чётное");\n} else {\n'
                     '    Console.WriteLine("нечётное");\n}'),
        'go': go('n := 8\nif n%2 == 0 {\n\tfmt.Println("чётное")\n'
                 '} else {\n\tfmt.Println("нечётное")\n}'),
        'php': '<?php\n$n = 8;\nif ($n % 2 == 0) {\n'
               '    echo "чётное";\n} else {\n    echo "нечётное";\n}',
        'rust': rs('let n = 8;\nif n % 2 == 0 {\n'
                   '    println!("чётное");\n} else {\n'
                   '    println!("нечётное");\n}'),
    })

add(id=8, title='Максимум из трёх', topic='Условия', diff='medium', xp=15,
    desc='Даны числа 3, 9 и 5. Выведи наибольшее из них, '
         'не используя встроенную функцию максимума.',
    expected='9', lit=['9', '3', '5'],
    hints=['Сравни первое число со вторым и третьим по очереди.',
           'Если a больше b и больше c — максимум равен a.'],
    code={
        'python': 'a, b, c = 3, 9, 5\nif a >= b and a >= c:\n    print(a)\n'
                  'elif b >= c:\n    print(b)\nelse:\n    print(c)',
        'javascript': 'const a = 3, b = 9, c = 5;\n'
                      'if (a >= b && a >= c) console.log(a);\n'
                      'else if (b >= c) console.log(b);\nelse console.log(c);',
        'typescript': 'const a: number = 3, b: number = 9, c: number = 5;\n'
                      'if (a >= b && a >= c) console.log(a);\n'
                      'else if (b >= c) console.log(b);\nelse console.log(c);',
        'java': j('int a = 3, b = 9, c = 5;\n'
                  'if (a >= b && a >= c) { System.out.println(a); }\n'
                  'else if (b >= c) { System.out.println(b); }\n'
                  'else { System.out.println(c); }'),
        'cpp': cpp('int a = 3, b = 9, c = 5;\n'
                   'if (a >= b && a >= c) { cout << a << endl; }\n'
                   'else if (b >= c) { cout << b << endl; }\n'
                   'else { cout << c << endl; }'),
        'csharp': cs('int a = 3, b = 9, c = 5;\n'
                     'if (a >= b && a >= c) { Console.WriteLine(a); }\n'
                     'else if (b >= c) { Console.WriteLine(b); }\n'
                     'else { Console.WriteLine(c); }'),
        'go': go('a, b, c := 3, 9, 5\nif a >= b && a >= c {\n'
                 '\tfmt.Println(a)\n} else if b >= c {\n\tfmt.Println(b)\n'
                 '} else {\n\tfmt.Println(c)\n}'),
        'php': '<?php\n$a = 3;\n$b = 9;\n$c = 5;\n'
               'if ($a >= $b && $a >= $c) { echo $a; }\n'
               'elseif ($b >= $c) { echo $b; }\nelse { echo $c; }',
        'rust': rs('let (a, b, c) = (3, 9, 5);\nif a >= b && a >= c {\n'
                   '    println!("{}", a);\n} else if b >= c {\n'
                   '    println!("{}", b);\n} else {\n'
                   '    println!("{}", c);\n}'),
    })

add(id=9, title='День недели по номеру', topic='Условия', diff='medium', xp=15,
    desc='Дано число 3. Выведи название дня недели: 1 — понедельник, '
         '2 — вторник и так далее.',
    expected='среда', lit=['3', 'среда'],
    hints=['Тут удобнее цепочка условий else if.',
           '1 — понедельник, 2 — вторник, 3 — среда.'],
    code={
        'python': 'day = 3\nif day == 1:\n    print("понедельник")\n'
                  'elif day == 2:\n    print("вторник")\n'
                  'elif day == 3:\n    print("среда")\n'
                  'else:\n    print("другой день")',
        'javascript': 'const day = 3;\nif (day === 1) console.log("понедельник");\n'
                      'else if (day === 2) console.log("вторник");\n'
                      'else if (day === 3) console.log("среда");\n'
                      'else console.log("другой день");',
        'typescript': 'const day: number = 3;\n'
                      'if (day === 1) console.log("понедельник");\n'
                      'else if (day === 2) console.log("вторник");\n'
                      'else if (day === 3) console.log("среда");\n'
                      'else console.log("другой день");',
        'java': j('int day = 3;\n'
                  'if (day == 1) { System.out.println("понедельник"); }\n'
                  'else if (day == 2) { System.out.println("вторник"); }\n'
                  'else if (day == 3) { System.out.println("среда"); }\n'
                  'else { System.out.println("другой день"); }'),
        'cpp': cpp('int day = 3;\n'
                   'if (day == 1) { cout << "понедельник" << endl; }\n'
                   'else if (day == 2) { cout << "вторник" << endl; }\n'
                   'else if (day == 3) { cout << "среда" << endl; }\n'
                   'else { cout << "другой день" << endl; }'),
        'csharp': cs('int day = 3;\n'
                     'if (day == 1) { Console.WriteLine("понедельник"); }\n'
                     'else if (day == 2) { Console.WriteLine("вторник"); }\n'
                     'else if (day == 3) { Console.WriteLine("среда"); }\n'
                     'else { Console.WriteLine("другой день"); }'),
        'go': go('day := 3\nif day == 1 {\n\tfmt.Println("понедельник")\n'
                 '} else if day == 2 {\n\tfmt.Println("вторник")\n'
                 '} else if day == 3 {\n\tfmt.Println("среда")\n} else {\n'
                 '\tfmt.Println("другой день")\n}'),
        'php': '<?php\n$day = 3;\nif ($day == 1) { echo "понедельник"; }\n'
               'elseif ($day == 2) { echo "вторник"; }\n'
               'elseif ($day == 3) { echo "среда"; }\n'
               'else { echo "другой день"; }',
        'rust': rs('let day = 3;\nif day == 1 { println!("понедельник"); }\n'
                   'else if day == 2 { println!("вторник"); }\n'
                   'else if day == 3 { println!("среда"); }\n'
                   'else { println!("другой день"); }'),
    })

add(id=10, title='Сумма чисел от 1 до 10', topic='Циклы', diff='easy', xp=10,
    desc='Посчитай сумму всех целых чисел от 1 до 10 включительно '
         'и выведи результат.',
    expected='55', lit=['10'],
    hints=['Заведи переменную-накопитель со значением 0.',
           'В цикле прибавляй к накопителю счётчик, потом выведи накопитель.'],
    code={
        'python': 'total = 0\nfor i in range(1, 11):\n    total += i\nprint(total)',
        'javascript': 'let total = 0;\nfor (let i = 1; i <= 10; i++) total += i;\n'
                      'console.log(total);',
        'typescript': 'let total: number = 0;\n'
                      'for (let i = 1; i <= 10; i++) total += i;\n'
                      'console.log(total);',
        'java': j('int total = 0;\n'
                  'for (int i = 1; i <= 10; i++) { total += i; }\n'
                  'System.out.println(total);'),
        'cpp': cpp('int total = 0;\n'
                   'for (int i = 1; i <= 10; i++) { total += i; }\n'
                   'cout << total << endl;'),
        'csharp': cs('int total = 0;\n'
                     'for (int i = 1; i <= 10; i++) { total += i; }\n'
                     'Console.WriteLine(total);'),
        'go': go('total := 0\nfor i := 1; i <= 10; i++ {\n\ttotal += i\n}\n'
                 'fmt.Println(total)'),
        'php': '<?php\n$total = 0;\n'
               'for ($i = 1; $i <= 10; $i++) { $total += $i; }\necho $total;',
        'rust': rs('let mut total = 0;\nfor i in 1..=10 { total += i; }\n'
                   'println!("{}", total);'),
    })

add(id=11, title='Таблица умножения на 3', topic='Циклы', diff='medium', xp=15,
    desc='Выведи в одну строку результаты умножения числа 3 на 1, 2, … 10, '
         'разделённые пробелом.',
    expected='3 6 9 12 15 18 21 24 27 30', lit=['3', '10'],
    hints=['Пройди циклом от 1 до 10 и умножай счётчик на 3.',
           'Чтобы всё было в одной строке, выводи без перевода строки '
           'и добавляй пробел между числами.'],
    code={
        'python': 'print(*[i * 3 for i in range(1, 11)])',
        'javascript': 'console.log(Array.from({length: 10}, (_, i) => '
                      '(i + 1) * 3).join(" "));',
        'typescript': 'const table: number[] = [];\n'
                      'for (let i = 1; i <= 10; i++) table.push(i * 3);\n'
                      'console.log(table.join(" "));',
        'java': j('for (int i = 1; i <= 10; i++) {\n'
                  '    System.out.print(i * 3);\n'
                  '    if (i < 10) System.out.print(" ");\n}\n'
                  'System.out.println();'),
        'cpp': cpp('for (int i = 1; i <= 10; i++) {\n'
                   '    cout << i * 3;\n    if (i < 10) cout << " ";\n}\n'
                   'cout << endl;'),
        'csharp': cs('for (int i = 1; i <= 10; i++) {\n'
                     '    Console.Write(i * 3);\n'
                     '    if (i < 10) Console.Write(" ");\n}\n'
                     'Console.WriteLine();'),
        'go': go('for i := 1; i <= 10; i++ {\n\tfmt.Print(i * 3)\n'
                 '\tif i < 10 {\n\t\tfmt.Print(" ")\n\t}\n}\nfmt.Println()'),
        'php': '<?php\nfor ($i = 1; $i <= 10; $i++) {\n'
               '    echo $i * 3;\n    if ($i < 10) echo " ";\n}',
        'rust': rs('for i in 1..=10 {\n    print!("{}", i * 3);\n'
                   '    if i < 10 { print!(" "); }\n}\nprintln!();'),
    })

add(id=12, title='Факториал числа 5', topic='Циклы', diff='medium', xp=15,
    desc='Посчитай факториал числа 5 (1 · 2 · 3 · 4 · 5) и выведи результат.',
    expected='120', lit=['5'],
    hints=['Факториал — это произведение всех чисел от 1 до n.',
           'Начни накопитель с 1 и в цикле умножай его на счётчик.'],
    code={
        'python': 'n = 5\nfact = 1\nfor i in range(1, n + 1):\n    fact *= i\n'
                  'print(fact)',
        'javascript': 'const n = 5;\nlet fact = 1;\n'
                      'for (let i = 1; i <= n; i++) fact *= i;\n'
                      'console.log(fact);',
        'typescript': 'const n: number = 5;\nlet fact: number = 1;\n'
                      'for (let i = 1; i <= n; i++) fact *= i;\n'
                      'console.log(fact);',
        'java': j('int n = 5;\nint fact = 1;\n'
                  'for (int i = 1; i <= n; i++) { fact *= i; }\n'
                  'System.out.println(fact);'),
        'cpp': cpp('int n = 5;\nint fact = 1;\n'
                   'for (int i = 1; i <= n; i++) { fact *= i; }\n'
                   'cout << fact << endl;'),
        'csharp': cs('int n = 5;\nint fact = 1;\n'
                     'for (int i = 1; i <= n; i++) { fact *= i; }\n'
                     'Console.WriteLine(fact);'),
        'go': go('n := 5\nfact := 1\nfor i := 1; i <= n; i++ {\n'
                 '\tfact *= i\n}\nfmt.Println(fact)'),
        'php': '<?php\n$n = 5;\n$fact = 1;\n'
               'for ($i = 1; $i <= $n; $i++) { $fact *= $i; }\necho $fact;',
        'rust': rs('let n = 5;\nlet mut fact = 1;\n'
                   'for i in 1..=n { fact *= i; }\nprintln!("{}", fact);'),
    })

add(id=13, title='Сумма цифр числа', topic='Циклы', diff='medium', xp=15,
    desc='Дано число 456. Посчитай сумму его цифр (4 + 5 + 6) и выведи её.',
    expected='15', lit=['456'],
    hints=['Последнюю цифру числа даёт остаток от деления на 10.',
           'После каждой цифры уменьшай число целочисленным делением на 10, '
           'пока оно не станет нулём.'],
    code={
        'python': 'n = 456\ntotal = 0\nwhile n > 0:\n    total += n % 10\n'
                  '    n //= 10\nprint(total)',
        'javascript': 'let n = 456;\nlet total = 0;\nwhile (n > 0) {\n'
                      '  total += n % 10;\n  n = Math.floor(n / 10);\n}\n'
                      'console.log(total);',
        'typescript': 'let n: number = 456;\nlet total: number = 0;\n'
                      'while (n > 0) {\n  total += n % 10;\n'
                      '  n = Math.floor(n / 10);\n}\nconsole.log(total);',
        'java': j('int n = 456;\nint total = 0;\n'
                  'while (n > 0) { total += n % 10; n /= 10; }\n'
                  'System.out.println(total);'),
        'cpp': cpp('int n = 456;\nint total = 0;\n'
                   'while (n > 0) { total += n % 10; n /= 10; }\n'
                   'cout << total << endl;'),
        'csharp': cs('int n = 456;\nint total = 0;\n'
                     'while (n > 0) { total += n % 10; n /= 10; }\n'
                     'Console.WriteLine(total);'),
        'go': go('n := 456\ntotal := 0\nfor n > 0 {\n\ttotal += n % 10\n'
                 '\tn /= 10\n}\nfmt.Println(total)'),
        'php': '<?php\n$n = 456;\n$total = 0;\n'
               'while ($n > 0) { $total += $n % 10; $n = intdiv($n, 10); }\n'
               'echo $total;',
        'rust': rs('let mut n = 456;\nlet mut total = 0;\n'
                   'while n > 0 {\n    total += n % 10;\n    n /= 10;\n}\n'
                   'println!("{}", total);'),
    })

add(id=14, title='Реверс строки', topic='Строки', diff='medium', xp=15,
    desc='Дана строка «hello». Выведи её символы в обратном порядке: olleh',
    expected='olleh', lit=['hello'],
    hints=['Во многих языках есть готовый метод переворота строки '
           'или массива символов.',
           'Если готового метода нет — перебери символы от последнего '
           'к первому и собери новую строку.'],
    code={
        'python': 's = "hello"\nprint(s[::-1])',
        'javascript': 'const s = "hello";\n'
                      'console.log([...s].reverse().join(""));',
        'typescript': 'const s: string = "hello";\n'
                      'console.log([...s].reverse().join(""));',
        'java': j('String s = "hello";\n'
                  'System.out.println(new StringBuilder(s).reverse().toString());'),
        'cpp': cpp('string s = "hello";\nreverse(s.begin(), s.end());\n'
                   'cout << s << endl;', incs=['string', 'algorithm']),
        'csharp': cs('string s = "hello";\nchar[] arr = s.ToCharArray();\n'
                     'Array.Reverse(arr);\n'
                     'Console.WriteLine(new string(arr));'),
        'go': go('s := "hello"\nr := []rune(s)\n'
                 'for i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {\n'
                 '\tr[i], r[j] = r[j], r[i]\n}\nfmt.Println(string(r))'),
        'php': '<?php\n$s = "hello";\necho strrev($s);',
        'rust': rs('let s = "hello";\n'
                   'let r: String = s.chars().rev().collect();\n'
                   'println!("{}", r);'),
    })

add(id=15, title='Длина строки', topic='Строки', diff='easy', xp=10,
    desc='Дана строка «Hello, world!». Выведи количество символов в ней.',
    expected='13', lit=['Hello, world!'],
    hints=['Длину строки возвращает функция или свойство length.',
           'Строка задана точно: «Hello, world!» — в ней 13 символов.'],
    code={
        'python': 's = "Hello, world!"\nprint(len(s))',
        'javascript': 'const s = "Hello, world!";\nconsole.log(s.length);',
        'typescript': 'const s: string = "Hello, world!";\n'
                      'console.log(s.length);',
        'java': j('String s = "Hello, world!";\n'
                  'System.out.println(s.length());'),
        'cpp': cpp('string s = "Hello, world!";\ncout << s.length() << endl;',
                   incs=['string']),
        'csharp': cs('string s = "Hello, world!";\n'
                     'Console.WriteLine(s.Length);'),
        'go': go('s := "Hello, world!"\nfmt.Println(len(s))'),
        'php': '<?php\n$s = "Hello, world!";\necho strlen($s);',
        'rust': rs('let s = "Hello, world!";\n'
                   'println!("{}", s.chars().count());'),
    })

add(id=16, title='Гласные в строке', topic='Строки', diff='hard', xp=20,
    desc='Дана строка «программирование». Посчитай, сколько в ней '
         'гласных букв.',
    expected='7', lit=['программирование'],
    hints=['Гласные русского алфавита: а, е, ё, и, о, у, ы, э, ю, я.',
           'Перебери символы строки и проверь, входит ли символ '
           'в набор гласных.'],
    code={
        'python': 's = "программирование"\nvowels = "аеёиоуыэюя"\n'
                  'count = sum(1 for ch in s if ch in vowels)\nprint(count)',
        'javascript': 'const s = "программирование";\n'
                      'const vowels = "аеёиоуыэюя";\nlet count = 0;\n'
                      'for (const ch of s) if (vowels.includes(ch)) count++;\n'
                      'console.log(count);',
        'typescript': 'const s: string = "программирование";\n'
                      'const vowels: string = "аеёиоуыэюя";\n'
                      'let count: number = 0;\n'
                      'for (const ch of s) if (vowels.includes(ch)) count++;\n'
                      'console.log(count);',
        'java': j('String s = "программирование";\n'
                  'String vowels = "аеёиоуыэюя";\nint count = 0;\n'
                  'for (char ch : s.toCharArray()) {\n'
                  '    if (vowels.indexOf(ch) >= 0) count++;\n}\n'
                  'System.out.println(count);'),
        'cpp': cpp('string s = "программирование";\n'
                   'string vowels = "аеёиоуыэюя";\nint count = 0;\n'
                   'for (char ch : s) {\n'
                   '    if (vowels.find(ch) != string::npos) count++;\n}\n'
                   'cout << count << endl;', incs=['string']),
        'csharp': cs('string s = "программирование";\n'
                     'string vowels = "аеёиоуыэюя";\nint count = 0;\n'
                     'foreach (char ch in s) {\n'
                     '    if (vowels.IndexOf(ch) >= 0) count++;\n}\n'
                     'Console.WriteLine(count);'),
        'go': go('s := "программирование"\nvowels := "аеёиоуыэюя"\n'
                 'count := 0\nfor _, ch := range s {\n'
                 '\tif strings.ContainsRune(vowels, ch) {\n\t\tcount++\n'
                 '\t}\n}\nfmt.Println(count)', imports='fmt;strings'),
        'php': '<?php\n$s = "программирование";\n$vowels = "аеёиоуыэюя";\n'
               '$count = 0;\nforeach (str_split($s) as $ch) {\n'
               '    if (strpos($vowels, $ch) !== false) $count++;\n}\n'
               'echo $count;',
        'rust': rs('let s = "программирование";\n'
                   'let vowels = "аеёиоуыэюя";\n'
                   'let count = s.chars().filter(|c| vowels.contains(*c)).count();\n'
                   'println!("{}", count);'),
    })

add(id=17, title='Сумма элементов массива', topic='Массивы', diff='easy', xp=10,
    desc='Дан массив [1, 2, 3, 4, 5]. Выведи сумму всех его элементов.',
    expected='15', lit=['1', '2', '3', '4', '5'],
    hints=['Сумму массива можно посчитать циклом или готовой функцией.',
           'Пройди по всем элементам и прибавляй их к накопителю.'],
    code={
        'python': 'nums = [1, 2, 3, 4, 5]\nprint(sum(nums))',
        'javascript': 'const nums = [1, 2, 3, 4, 5];\n'
                      'console.log(nums.reduce((a, b) => a + b, 0));',
        'typescript': 'const nums: number[] = [1, 2, 3, 4, 5];\n'
                      'console.log(nums.reduce((a, b) => a + b, 0));',
        'java': j('int[] nums = {1, 2, 3, 4, 5};\nint total = 0;\n'
                  'for (int n : nums) { total += n; }\n'
                  'System.out.println(total);'),
        'cpp': cpp('int nums[] = {1, 2, 3, 4, 5};\nint total = 0;\n'
                   'for (int n : nums) { total += n; }\ncout << total << endl;'),
        'csharp': cs('int[] nums = {1, 2, 3, 4, 5};\nint total = 0;\n'
                     'foreach (int n in nums) { total += n; }\n'
                     'Console.WriteLine(total);'),
        'go': go('nums := []int{1, 2, 3, 4, 5}\ntotal := 0\n'
                 'for _, n := range nums {\n\ttotal += n\n}\n'
                 'fmt.Println(total)'),
        'php': '<?php\n$nums = [1, 2, 3, 4, 5];\necho array_sum($nums);',
        'rust': rs('let nums = [1, 2, 3, 4, 5];\n'
                   'let total: i32 = nums.iter().sum();\n'
                   'println!("{}", total);'),
    })

add(id=18, title='Максимум в массиве', topic='Массивы', diff='medium', xp=15,
    desc='Дан массив [4, 8, 15, 16, 23, 42]. Выведи его наибольший элемент.',
    expected='42', lit=['4', '8', '15', '16', '23', '42'],
    hints=['Начни с первого элемента как текущего максимума.',
           'Сравнивай каждый элемент с текущим максимумом и обновляй его.'],
    code={
        'python': 'nums = [4, 8, 15, 16, 23, 42]\nbest = nums[0]\n'
                  'for n in nums:\n    if n > best:\n        best = n\nprint(best)',
        'javascript': 'const nums = [4, 8, 15, 16, 23, 42];\n'
                      'let best = nums[0];\n'
                      'for (const n of nums) if (n > best) best = n;\n'
                      'console.log(best);',
        'typescript': 'const nums: number[] = [4, 8, 15, 16, 23, 42];\n'
                      'let best: number = nums[0];\n'
                      'for (const n of nums) if (n > best) best = n;\n'
                      'console.log(best);',
        'java': j('int[] nums = {4, 8, 15, 16, 23, 42};\nint best = nums[0];\n'
                  'for (int n : nums) { if (n > best) best = n; }\n'
                  'System.out.println(best);'),
        'cpp': cpp('int nums[] = {4, 8, 15, 16, 23, 42};\nint best = nums[0];\n'
                   'for (int n : nums) { if (n > best) best = n; }\n'
                   'cout << best << endl;'),
        'csharp': cs('int[] nums = {4, 8, 15, 16, 23, 42};\n'
                     'int best = nums[0];\n'
                     'foreach (int n in nums) { if (n > best) best = n; }\n'
                     'Console.WriteLine(best);'),
        'go': go('nums := []int{4, 8, 15, 16, 23, 42}\nbest := nums[0]\n'
                 'for _, n := range nums {\n\tif n > best {\n\t\tbest = n\n'
                 '\t}\n}\nfmt.Println(best)'),
        'php': '<?php\n$nums = [4, 8, 15, 16, 23, 42];\n$best = $nums[0];\n'
               'foreach ($nums as $n) { if ($n > $best) $best = $n; }\n'
               'echo $best;',
        'rust': rs('let nums = [4, 8, 15, 16, 23, 42];\n'
                   'let mut best = nums[0];\n'
                   'for &n in nums.iter() { if n > best { best = n; } }\n'
                   'println!("{}", best);'),
    })

add(id=1, title='Привет, мир!', topic='Основы', diff='easy', xp=10,
    desc='Выведи в консоль текст: Привет, мир!',
    expected='Привет, мир!', lit=['Привет, мир!'],
    hints=['Найди функцию вывода текста на экран в своём языке.',
           'Строка должна совпадать точно: «Привет, мир!» — большая буква '
           'и восклицательный знак.'],
    code={
        'python': 'print("Привет, мир!")',
        'javascript': 'console.log("Привет, мир!");',
        'typescript': 'console.log("Привет, мир!");',
        'java': j('System.out.println("Привет, мир!");'),
        'cpp': cpp('cout << "Привет, мир!" << endl;'),
        'csharp': cs('Console.WriteLine("Привет, мир!");'),
        'go': go('fmt.Println("Привет, мир!")'),
        'php': '<?php\necho "Привет, мир!";',
        'rust': rs('println!("Привет, мир!");'),
    })

add(id=2, title='Сумма двух чисел', topic='Основы', diff='easy', xp=10,
    desc='Даны числа 5 и 7. Выведи их сумму.',
    expected='12', lit=['5', '7'],
    hints=['Объяви две переменные: a = 5 и b = 7.',
           'Выведи результат сложения оператором +.'],
    code={
        'python': 'a = 5\nb = 7\nprint(a + b)',
        'javascript': 'const a = 5;\nconst b = 7;\nconsole.log(a + b);',
        'typescript': 'const a: number = 5;\nconst b: number = 7;\n'
                      'console.log(a + b);',
        'java': j('int a = 5;\nint b = 7;\nSystem.out.println(a + b);'),
        'cpp': cpp('int a = 5;\nint b = 7;\ncout << a + b << endl;'),
        'csharp': cs('int a = 5;\nint b = 7;\nConsole.WriteLine(a + b);'),
        'go': go('a := 5\nb := 7\nfmt.Println(a + b)'),
        'php': '<?php\n$a = 5;\n$b = 7;\necho $a + $b;',
        'rust': rs('let a = 5;\nlet b = 7;\nprintln!("{}", a + b);'),
    })

add(id=3, title='Деление с остатком', topic='Основы', diff='easy', xp=10,
    desc='Даны числа 17 и 5. Выведи в одной строке частное целочисленного '
         'деления и остаток через пробел: 3 2',
    expected='3 2', lit=['17', '5'],
    hints=['Для целочисленного деления используй оператор своего языка, '
           'остаток даёт оператор %.',
           'Выведи два значения в одной строке через пробел.'],
    code={
        'python': 'a = 17\nb = 5\nprint(a // b, a % b)',
        'javascript': 'const a = 17;\nconst b = 5;\n'
                      'console.log(Math.floor(a / b), a % b);',
        'typescript': 'const a: number = 17;\nconst b: number = 5;\n'
                      'console.log(Math.floor(a / b), a % b);',
        'java': j('int a = 17;\nint b = 5;\n'
                  'System.out.println(a / b + " " + a % b);'),
        'cpp': cpp('int a = 17;\nint b = 5;\n'
                   'cout << a / b << " " << a % b << endl;'),
        'csharp': cs('int a = 17;\nint b = 5;\n'
                     'Console.WriteLine(a / b + " " + a % b);'),
        'go': go('a := 17\nb := 5\nfmt.Println(a/b, a%b)'),
        'php': '<?php\n$a = 17;\n$b = 5;\n'
               'echo intdiv($a, $b) . " " . $a % $b;',
        'rust': rs('let a = 17;\nlet b = 5;\n'
                   'println!("{} {}", a / b, a % b);'),
    })

add(id=4, title='Знакомство', topic='Основы', diff='easy', xp=10,
    desc='Создай переменные name = "Анна" и age = 25. '
         'Выведи ровно: Меня зовут Анна, мне 25',
    expected='Меня зовут Анна, мне 25', lit=['Анна', '25'],
    hints=['Подставь значения переменных в строку — интерполяцией '
           'или конкатенацией.',
           'Вывод должен быть точно «Меня зовут Анна, мне 25» — '
           'с запятой после имени.'],
    code={
        'python': 'name = "Анна"\nage = 25\n'
                  'print(f"Меня зовут {name}, мне {age}")',
        'javascript': 'const name = "Анна";\nconst age = 25;\n'
                      'console.log(`Меня зовут ${name}, мне ${age}`);',
        'typescript': 'const name: string = "Анна";\nconst age: number = 25;\n'
                      'console.log(`Меня зовут ${name}, мне ${age}`);',
        'java': j('String name = "Анна";\nint age = 25;\n'
                  'System.out.println("Меня зовут " + name + ", мне " + age);'),
        'cpp': cpp('string name = "Анна";\nint age = 25;\n'
                   'cout << "Меня зовут " << name << ", мне " << age << endl;',
                   incs=['string']),
        'csharp': cs('string name = "Анна";\nint age = 25;\n'
                     'Console.WriteLine($"Меня зовут {name}, мне {age}");'),
        'go': go('name := "Анна"\nage := 25\n'
                 'fmt.Println("Меня зовут", name+",", "мне", age)'),
        'php': '<?php\n$name = "Анна";\n$age = 25;\n'
               'echo "Меня зовут {$name}, мне {$age}";',
        'rust': rs('let name = "Анна";\nlet age = 25;\n'
                   'println!("Меня зовут {}, мне {}", name, age);'),
    })

add(id=5, title='Площадь прямоугольника', topic='Основы', diff='easy', xp=10,
    desc='Прямоугольник 6 × 4. Выведи его площадь: перемножь стороны.',
    expected='24', lit=['6', '4'],
    hints=['Площадь прямоугольника = ширина × высота.',
           'Перемножь переменные width и height и выведи результат.'],
    code={
        'python': 'width = 6\nheight = 4\nprint(width * height)',
        'javascript': 'const width = 6;\nconst height = 4;\n'
                      'console.log(width * height);',
        'typescript': 'const width: number = 6;\nconst height: number = 4;\n'
                      'console.log(width * height);',
        'java': j('int width = 6;\nint height = 4;\n'
                  'System.out.println(width * height);'),
        'cpp': cpp('int width = 6;\nint height = 4;\n'
                   'cout << width * height << endl;'),
        'csharp': cs('int width = 6;\nint height = 4;\n'
                     'Console.WriteLine(width * height);'),
        'go': go('width := 6\nheight := 4\nfmt.Println(width * height)'),
        'php': '<?php\n$width = 6;\n$height = 4;\necho $width * $height;',
        'rust': rs('let width = 6;\nlet height = 4;\n'
                   'println!("{}", width * height);'),
    })

add(id=19, title='Минимум в массиве', topic='Массивы', diff='medium', xp=15,
    desc='Дан массив [4, 8, 15, 16, 23, 42]. Выведи его наименьший элемент.',
    expected='4', lit=['4', '8', '15', '16', '23', '42'],
    hints=['Начни с первого элемента как текущего минимума.',
           'Сравнивай каждый элемент с текущим минимумом и обновляй его.'],
    code={
        'python': 'nums = [4, 8, 15, 16, 23, 42]\nbest = nums[0]\n'
                  'for n in nums:\n    if n < best:\n        best = n\nprint(best)',
        'javascript': 'const nums = [4, 8, 15, 16, 23, 42];\n'
                      'let best = nums[0];\n'
                      'for (const n of nums) if (n < best) best = n;\n'
                      'console.log(best);',
        'typescript': 'const nums: number[] = [4, 8, 15, 16, 23, 42];\n'
                      'let best: number = nums[0];\n'
                      'for (const n of nums) if (n < best) best = n;\n'
                      'console.log(best);',
        'java': j('int[] nums = {4, 8, 15, 16, 23, 42};\nint best = nums[0];\n'
                  'for (int n : nums) { if (n < best) best = n; }\n'
                  'System.out.println(best);'),
        'cpp': cpp('int nums[] = {4, 8, 15, 16, 23, 42};\nint best = nums[0];\n'
                   'for (int n : nums) { if (n < best) best = n; }\n'
                   'cout << best << endl;'),
        'csharp': cs('int[] nums = {4, 8, 15, 16, 23, 42};\n'
                     'int best = nums[0];\n'
                     'foreach (int n in nums) { if (n < best) best = n; }\n'
                     'Console.WriteLine(best);'),
        'go': go('nums := []int{4, 8, 15, 16, 23, 42}\nbest := nums[0]\n'
                 'for _, n := range nums {\n\tif n < best {\n\t\tbest = n\n'
                 '\t}\n}\nfmt.Println(best)'),
        'php': '<?php\n$nums = [4, 8, 15, 16, 23, 42];\n$best = $nums[0];\n'
               'foreach ($nums as $n) { if ($n < $best) $best = $n; }\n'
               'echo $best;',
        'rust': rs('let nums = [4, 8, 15, 16, 23, 42];\n'
                   'let mut best = nums[0];\n'
                   'for &n in nums.iter() { if n < best { best = n; } }\n'
                   'println!("{}", best);'),
    })

add(id=20, title='Среднее арифметическое', topic='Массивы', diff='medium', xp=15,
    desc='Дан массив [2, 4, 6]. Выведи среднее арифметическое его элементов '
         'целым числом.',
    expected='4', lit=['2', '4', '6'],
    hints=['Сначала посчитай сумму элементов.',
           'Среднее — это сумма, делённая на количество элементов '
           '(целочисленно).'],
    code={
        'python': 'nums = [2, 4, 6]\nprint(sum(nums) // len(nums))',
        'javascript': 'const nums = [2, 4, 6];\n'
                      'console.log(nums.reduce((a, b) => a + b, 0) / nums.length);',
        'typescript': 'const nums: number[] = [2, 4, 6];\n'
                      'console.log(nums.reduce((a, b) => a + b, 0) / nums.length);',
        'java': j('int[] nums = {2, 4, 6};\nint total = 0;\n'
                  'for (int n : nums) { total += n; }\n'
                  'System.out.println(total / nums.length);'),
        'cpp': cpp('int nums[] = {2, 4, 6};\nint total = 0;\n'
                   'for (int n : nums) { total += n; }\n'
                   'cout << total / 3 << endl;'),
        'csharp': cs('int[] nums = {2, 4, 6};\nint total = 0;\n'
                     'foreach (int n in nums) { total += n; }\n'
                     'Console.WriteLine(total / nums.Length);'),
        'go': go('nums := []int{2, 4, 6}\ntotal := 0\n'
                 'for _, n := range nums {\n\ttotal += n\n}\n'
                 'fmt.Println(total / len(nums))'),
        'php': '<?php\n$nums = [2, 4, 6];\necho array_sum($nums) / count($nums);',
        'rust': rs('let nums = [2, 4, 6];\n'
                   'let total: i32 = nums.iter().sum();\n'
                   'println!("{}", total / nums.len() as i32);'),
    })

add(id=21, title='Только чётные числа', topic='Массивы', diff='medium', xp=15,
    desc='Дан массив [1, 2, 3, 4, 5, 6, 7, 8]. Выведи в одну строку '
         'только чётные числа через пробел.',
    expected='2 4 6 8', lit=['8'],
    hints=['Проверяй каждый элемент: n % 2 == 0.',
           'Собери чётные числа и выведи их через пробел.'],
    code={
        'python': 'nums = [1, 2, 3, 4, 5, 6, 7, 8]\n'
                  'print(*[n for n in nums if n % 2 == 0])',
        'javascript': 'const nums = [1, 2, 3, 4, 5, 6, 7, 8];\n'
                      'console.log(nums.filter(n => n % 2 === 0).join(" "));',
        'typescript': 'const nums: number[] = [1, 2, 3, 4, 5, 6, 7, 8];\n'
                      'console.log(nums.filter(n => n % 2 === 0).join(" "));',
        'java': j('int[] nums = {1, 2, 3, 4, 5, 6, 7, 8};\n'
                  'for (int n : nums) {\n'
                  '    if (n % 2 == 0) System.out.print(n + " ");\n}\n'
                  'System.out.println();'),
        'cpp': cpp('int nums[] = {1, 2, 3, 4, 5, 6, 7, 8};\n'
                   'for (int n : nums) {\n'
                   '    if (n % 2 == 0) cout << n << " ";\n}\ncout << endl;'),
        'csharp': cs('int[] nums = {1, 2, 3, 4, 5, 6, 7, 8};\n'
                     'foreach (int n in nums) {\n'
                     '    if (n % 2 == 0) Console.Write(n + " ");\n}\n'
                     'Console.WriteLine();'),
        'go': go('nums := []int{1, 2, 3, 4, 5, 6, 7, 8}\n'
                 'for _, n := range nums {\n\tif n%2 == 0 {\n'
                 '\t\tfmt.Print(n, " ")\n\t}\n}\nfmt.Println()'),
        'php': '<?php\n$nums = [1, 2, 3, 4, 5, 6, 7, 8];\n'
               'foreach ($nums as $n) { if ($n % 2 == 0) echo $n . " "; }',
        'rust': rs('let nums = [1, 2, 3, 4, 5, 6, 7, 8];\n'
                   'for n in nums.iter().filter(|n| *n % 2 == 0) {\n'
                   '    print!("{} ", n);\n}\nprintln!();'),
    })

add(id=22, title='Реверс массива', topic='Массивы', diff='medium', xp=15,
    desc='Дан массив [1, 2, 3, 4, 5]. Выведи его элементы '
         'в обратном порядке через пробел.',
    expected='5 4 3 2 1', lit=['5'],
    hints=['Можно перевернуть массив готовым методом или пройти его с конца.',
           'Выводи элементы через пробел, чтобы получить «5 4 3 2 1».'],
    code={
        'python': 'nums = [1, 2, 3, 4, 5]\nprint(*reversed(nums))',
        'javascript': 'const nums = [1, 2, 3, 4, 5];\n'
                      'console.log([...nums].reverse().join(" "));',
        'typescript': 'const nums: number[] = [1, 2, 3, 4, 5];\n'
                      'console.log([...nums].reverse().join(" "));',
        'java': j('int[] nums = {1, 2, 3, 4, 5};\n'
                  'for (int i = nums.length - 1; i >= 0; i--)\n'
                  '    System.out.print(nums[i] + " ");\n'
                  'System.out.println();'),
        'cpp': cpp('int nums[] = {1, 2, 3, 4, 5};\n'
                   'for (int i = 4; i >= 0; i--) cout << nums[i] << " ";\n'
                   'cout << endl;'),
        'csharp': cs('int[] nums = {1, 2, 3, 4, 5};\n'
                     'for (int i = nums.Length - 1; i >= 0; i--)\n'
                     '    Console.Write(nums[i] + " ");\n'
                     'Console.WriteLine();'),
        'go': go('nums := []int{1, 2, 3, 4, 5}\n'
                 'for i := len(nums) - 1; i >= 0; i-- {\n'
                 '\tfmt.Print(nums[i], " ")\n}\nfmt.Println()'),
        'php': '<?php\n$nums = [1, 2, 3, 4, 5];\n'
               'foreach (array_reverse($nums) as $n) { echo $n . " "; }',
        'rust': rs('let nums = [1, 2, 3, 4, 5];\n'
                   'for n in nums.iter().rev() {\n    print!("{} ", n);\n}\n'
                   'println!();'),
    })

add(id=23, title='Сколько чётных чисел', topic='Массивы', diff='easy', xp=10,
    desc='Дан массив [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]. Посчитай, сколько '
         'в нём чётных чисел, и выведи счётчик.',
    expected='5', lit=['10'],
    hints=['Счётчик начинается с нуля.',
           'Увеличивай счётчик, когда элемент делится на 2 без остатка.'],
    code={
        'python': 'nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n'
                  'print(sum(1 for n in nums if n % 2 == 0))',
        'javascript': 'const nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];\n'
                      'console.log(nums.filter(n => n % 2 === 0).length);',
        'typescript': 'const nums: number[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];\n'
                      'console.log(nums.filter(n => n % 2 === 0).length);',
        'java': j('int[] nums = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};\n'
                  'int count = 0;\n'
                  'for (int n : nums) { if (n % 2 == 0) count++; }\n'
                  'System.out.println(count);'),
        'cpp': cpp('int nums[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};\n'
                   'int count = 0;\n'
                   'for (int n : nums) { if (n % 2 == 0) count++; }\n'
                   'cout << count << endl;'),
        'csharp': cs('int[] nums = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};\n'
                     'int count = 0;\n'
                     'foreach (int n in nums) { if (n % 2 == 0) count++; }\n'
                     'Console.WriteLine(count);'),
        'go': go('nums := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}\ncount := 0\n'
                 'for _, n := range nums {\n\tif n%2 == 0 {\n\t\tcount++\n'
                 '\t}\n}\nfmt.Println(count)'),
        'php': '<?php\n$nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];\n$count = 0;\n'
               'foreach ($nums as $n) { if ($n % 2 == 0) $count++; }\n'
               'echo $count;',
        'rust': rs('let nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];\n'
                   'let count = nums.iter().filter(|n| *n % 2 == 0).count();\n'
                   'println!("{}", count);'),
    })

add(id=24, title='Функция сложения', topic='Функции', diff='medium', xp=15,
    desc='Напиши функцию add(a, b), которая возвращает сумму двух чисел, '
         'и выведи результат add(3, 4).',
    expected='7',
    lit={'java': ['static int add', '3', '4'],
         'cpp': ['int add', '3', '4'],
         'csharp': ['static int Add', '3', '4'],
         'php': ['function add', '3', '4'],
         'rust': ['fn add', '3', '4']},
    hints=['Объяви функцию с двумя параметрами и верни их сумму.',
           'Вызови функцию с аргументами 3 и 4 и выведи результат.'],
    code={
        'python': 'def add(a, b):\n    return a + b\n\nprint(add(3, 4))',
        'javascript': 'function add(a, b) {\n  return a + b;\n}\n\n'
                      'console.log(add(3, 4));',
        'typescript': 'function add(a: number, b: number): number {\n'
                      '  return a + b;\n}\n\nconsole.log(add(3, 4));',
        'java': j('System.out.println(add(3, 4));',
                  extra='static int add(int a, int b) {\n    return a + b;\n}'),
        'cpp': cpp('cout << add(3, 4) << endl;',
                   pre='int add(int a, int b) {\n    return a + b;\n}'),
        'csharp': cs('Console.WriteLine(Add(3, 4));',
                     extra='static int Add(int a, int b) {\n'
                           '    return a + b;\n}'),
        'go': go('fmt.Println(add(3, 4))',
                 extra='func add(a int, b int) int {\n\treturn a + b\n}'),
        'php': '<?php\nfunction add($a, $b) {\n    return $a + $b;\n}\n\n'
               'echo add(3, 4);',
        'rust': rs('println!("{}", add(3, 4));',
                   pre='fn add(a: i32, b: i32) -> i32 {\n    a + b\n}'),
    })

add(id=25, title='Функция факториала', topic='Функции', diff='hard', xp=20,
    desc='Напиши функцию fact(n), которая считает факториал, и выведи '
         'fact(5).',
    expected='120', lit=['5'],
    hints=['Факториал 5 — это 1 · 2 · 3 · 4 · 5.',
           'Внутри функции используй цикл и накопитель, начиная с 1.'],
    code={
        'python': 'def fact(n):\n    result = 1\n    for i in range(1, n + 1):\n'
                  '        result *= i\n    return result\n\nprint(fact(5))',
        'javascript': 'function fact(n) {\n  let result = 1;\n'
                      '  for (let i = 1; i <= n; i++) result *= i;\n'
                      '  return result;\n}\n\nconsole.log(fact(5));',
        'typescript': 'function fact(n: number): number {\n  let result: number = 1;\n'
                      '  for (let i = 1; i <= n; i++) result *= i;\n'
                      '  return result;\n}\n\nconsole.log(fact(5));',
        'java': j('System.out.println(fact(5));',
                  extra='static int fact(int n) {\n    int result = 1;\n'
                        '    for (int i = 1; i <= n; i++) result *= i;\n'
                        '    return result;\n}'),
        'cpp': cpp('cout << fact(5) << endl;',
                   pre='int fact(int n) {\n    int result = 1;\n'
                       '    for (int i = 1; i <= n; i++) result *= i;\n'
                       '    return result;\n}'),
        'csharp': cs('Console.WriteLine(Fact(5));',
                     extra='static int Fact(int n) {\n    int result = 1;\n'
                           '    for (int i = 1; i <= n; i++) result *= i;\n'
                           '    return result;\n}'),
        'go': go('fmt.Println(fact(5))',
                 extra='func fact(n int) int {\n\tresult := 1\n'
                       '\tfor i := 1; i <= n; i++ {\n\t\tresult *= i\n\t}\n'
                       '\treturn result\n}'),
        'php': '<?php\nfunction fact($n) {\n    $result = 1;\n'
               '    for ($i = 1; $i <= $n; $i++) { $result *= $i; }\n'
               '    return $result;\n}\n\necho fact(5);',
        'rust': rs('println!("{}", fact(5));',
                   pre='fn fact(n: i32) -> i32 {\n    let mut result = 1;\n'
                       '    for i in 1..=n { result *= i; }\n    result\n}'),
    })

add(id=28, title='Палиндром', topic='Строки', diff='hard', xp=20,
    desc='Дана строка «шалаш». Проверь, читается ли она одинаково в обе '
         'стороны, и выведи «палиндром» или «не палиндром».',
    expected='палиндром', lit=['шалаш'],
    hints=['Сравни строку с её перевёрнутой версией.',
           '«шалаш» читается одинаково слева направо и справа налево — '
           'значит, это палиндром.'],
    code={
        'python': 's = "шалаш"\n'
                  'print("палиндром" if s == s[::-1] else "не палиндром")',
        'javascript': 'const s = "шалаш";\n'
                      'console.log(s === [...s].reverse().join("") '
                      '? "палиндром" : "не палиндром");',
        'typescript': 'const s: string = "шалаш";\n'
                      'console.log(s === [...s].reverse().join("") '
                      '? "палиндром" : "не палиндром");',
        'java': j('String s = "шалаш";\n'
                  'String r = new StringBuilder(s).reverse().toString();\n'
                  'System.out.println(s.equals(r) ? "палиндром" : "не палиндром");'),
        'cpp': cpp('string s = "шалаш";\nstring r = s;\n'
                   'reverse(r.begin(), r.end());\n'
                   'cout << (s == r ? "палиндром" : "не палиндром") << endl;',
                   incs=['string', 'algorithm']),
        'csharp': cs('string s = "шалаш";\nchar[] arr = s.ToCharArray();\n'
                     'Array.Reverse(arr);\n'
                     'Console.WriteLine(s == new string(arr) '
                     '? "палиндром" : "не палиндром");'),
        'go': go('s := "шалаш"\nr := []rune(s)\n'
                 'for i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {\n'
                 '\tr[i], r[j] = r[j], r[i]\n}\nif s == string(r) {\n'
                 '\tfmt.Println("палиндром")\n} else {\n'
                 '\tfmt.Println("не палиндром")\n}'),
        'php': '<?php\n$s = "шалаш";\n'
               '$r = implode("", array_reverse(preg_split("//u", $s, -1, '
               'PREG_SPLIT_NO_EMPTY)));\n'
               'echo $s === $r ? "палиндром" : "не палиндром";',
        'rust': rs('let s = "шалаш";\n'
                   'let r: String = s.chars().rev().collect();\n'
                   'println!("{}", if s == r { "палиндром" } else { "не палиндром" });'),
    })

add(id=29, title='Обмен значений', topic='Основы', diff='easy', xp=10,
    desc='Даны переменные a = 5 и b = 7. Поменяй их значения местами '
         'и выведи сначала новое a, потом новое b через пробел.',
    expected='7 5', lit=['5', '7'],
    hints=['Запомни одно значение во временной переменной.',
           'Либо используй множественное присваивание, если язык его '
           'поддерживает.'],
    code={
        'python': 'a = 5\nb = 7\na, b = b, a\nprint(a, b)',
        'javascript': 'let a = 5;\nlet b = 7;\n[a, b] = [b, a];\n'
                      'console.log(a, b);',
        'typescript': 'let a: number = 5;\nlet b: number = 7;\n'
                      '[a, b] = [b, a];\nconsole.log(a, b);',
        'java': j('int a = 5, b = 7;\nint t = a;\na = b;\nb = t;\n'
                  'System.out.println(a + " " + b);'),
        'cpp': cpp('int a = 5, b = 7;\nint t = a;\na = b;\nb = t;\n'
                   'cout << a << " " << b << endl;'),
        'csharp': cs('int a = 5, b = 7;\nint t = a;\na = b;\nb = t;\n'
                     'Console.WriteLine(a + " " + b);'),
        'go': go('a, b := 5, 7\na, b = b, a\nfmt.Println(a, b)'),
        'php': '<?php\n$a = 5;\n$b = 7;\n$t = $a;\n$a = $b;\n$b = $t;\n'
               'echo $a . " " . $b;',
        'rust': rs('let a = 5;\nlet b = 7;\nlet (a, b) = (b, a);\n'
                   'println!("{} {}", a, b);'),
    })

add(id=30, title='Мини-калькулятор', topic='Условия', diff='hard', xp=20,
    desc='Даны числа a = 3 и b = 4 и код операции op = "*". Выполни '
         'соответствующее действие (поддержи +, -, *, /) и выведи результат.',
    expected='12', lit=['3', '4'],
    hints=['Код операции хранится в переменной op.',
           'Выбери действие через switch / match или цепочку условий.'],
    code={
        'python': 'a = 3\nb = 4\nop = "*"\nif op == "+":\n    result = a + b\n'
                  'elif op == "-":\n    result = a - b\n'
                  'elif op == "*":\n    result = a * b\n'
                  'else:\n    result = a / b\nprint(result)',
        'javascript': 'const a = 3, b = 4, op = "*";\nlet result;\n'
                      'switch (op) {\n  case "+": result = a + b; break;\n'
                      '  case "-": result = a - b; break;\n'
                      '  case "*": result = a * b; break;\n'
                      '  default: result = a / b;\n}\nconsole.log(result);',
        'typescript': 'const a: number = 3, b: number = 4, op: string = "*";\n'
                      'let result: number;\nswitch (op) {\n'
                      '  case "+": result = a + b; break;\n'
                      '  case "-": result = a - b; break;\n'
                      '  case "*": result = a * b; break;\n'
                      '  default: result = a / b;\n}\nconsole.log(result);',
        'java': j('int a = 3, b = 4;\nString op = "*";\nint result = 0;\n'
                  'switch (op) {\n    case "+": result = a + b; break;\n'
                  '    case "-": result = a - b; break;\n'
                  '    case "*": result = a * b; break;\n'
                  '    default: result = a / b;\n}\n'
                  'System.out.println(result);'),
        'cpp': cpp("int a = 3, b = 4;\nchar op = '*';\nint result = 0;\n"
                   "switch (op) {\n    case '+': result = a + b; break;\n"
                   "    case '-': result = a - b; break;\n"
                   "    case '*': result = a * b; break;\n"
                   "    default: result = a / b;\n}\ncout << result << endl;"),
        'csharp': cs('int a = 3, b = 4;\nstring op = "*";\nint result = 0;\n'
                     'switch (op) {\n    case "+": result = a + b; break;\n'
                     '    case "-": result = a - b; break;\n'
                     '    case "*": result = a * b; break;\n'
                     '    default: result = a / b; break;\n}\n'
                     'Console.WriteLine(result);'),
        'go': go('a, b := 3, 4\nop := "*"\nresult := 0\nswitch op {\n'
                 'case "+":\n\tresult = a + b\ncase "-":\n\tresult = a - b\n'
                 'case "*":\n\tresult = a * b\ndefault:\n\tresult = a / b\n}\n'
                 'fmt.Println(result)'),
        'php': '<?php\n$a = 3;\n$b = 4;\n$op = "*";\nswitch ($op) {\n'
               '    case "+": $result = $a + $b; break;\n'
               '    case "-": $result = $a - $b; break;\n'
               '    case "*": $result = $a * $b; break;\n'
               '    default: $result = $a / $b;\n}\necho $result;',
        'rust': rs('let a = 3;\nlet b = 4;\nlet op = "*";\n'
                   'let result = match op {\n    "+" => a + b,\n'
                   '    "-" => a - b,\n    "*" => a * b,\n    _ => a / b,\n};\n'
                   'println!("{}", result);'),
    })

add(id=26, title='Числа Фибоначчи', topic='Циклы', diff='hard', xp=20,
    desc='Выведи первые 7 чисел Фибоначчи через пробел. '
         'Последовательность начинается с 0 и 1.',
    expected='0 1 1 2 3 5 8', lit=['7'],
    hints=['Первые два числа — 0 и 1.',
           'Каждое следующее число — сумма двух предыдущих: '
           'сдвигай a = b, b = a + b.'],
    code={
        'python': 'n = 7\na, b = 0, 1\nresult = []\nfor _ in range(n):\n'
                  '    result.append(a)\n    a, b = b, a + b\nprint(*result)',
        'javascript': 'const n = 7;\nlet a = 0, b = 1;\nconst result = [];\n'
                      'for (let i = 0; i < n; i++) {\n  result.push(a);\n'
                      '  [a, b] = [b, a + b];\n}\n'
                      'console.log(result.join(" "));',
        'typescript': 'const n: number = 7;\nlet a: number = 0, b: number = 1;\n'
                      'const result: number[] = [];\n'
                      'for (let i = 0; i < n; i++) {\n  result.push(a);\n'
                      '  [a, b] = [b, a + b];\n}\n'
                      'console.log(result.join(" "));',
        'java': j('int n = 7;\nint a = 0, b = 1;\nString out = "";\n'
                  'for (int i = 0; i < n; i++) {\n'
                  '    out += a + (i < n - 1 ? " " : "");\n'
                  '    int next = a + b;\n    a = b;\n    b = next;\n}\n'
                  'System.out.println(out);'),
        'cpp': cpp('int n = 7;\nint a = 0, b = 1;\n'
                   'for (int i = 0; i < n; i++) {\n    cout << a;\n'
                   '    if (i < n - 1) cout << " ";\n'
                   '    int next = a + b;\n    a = b;\n    b = next;\n}\n'
                   'cout << endl;'),
        'csharp': cs('int n = 7;\nint a = 0, b = 1;\nstring output = "";\n'
                     'for (int i = 0; i < n; i++) {\n'
                     '    output += a + (i < n - 1 ? " " : "");\n'
                     '    int next = a + b;\n    a = b;\n    b = next;\n}\n'
                     'Console.WriteLine(output);'),
        'go': go('n := 7\na, b := 0, 1\nfor i := 0; i < n; i++ {\n'
                 '\tfmt.Print(a)\n\tif i < n-1 {\n\t\tfmt.Print(" ")\n\t}\n'
                 '\ta, b = b, a+b\n}\nfmt.Println()'),
        'php': '<?php\n$n = 7;\n$a = 0;\n$b = 1;\n'
               'for ($i = 0; $i < $n; $i++) {\n    echo $a;\n'
               '    if ($i < $n - 1) echo " ";\n'
               '    $next = $a + $b;\n    $a = $b;\n    $b = $next;\n}',
        'rust': rs('let n = 7;\nlet mut a = 0;\nlet mut b = 1;\n'
                   'for i in 0..n {\n    print!("{}", a);\n'
                   '    if i < n - 1 { print!(" "); }\n'
                   '    let next = a + b;\n    a = b;\n    b = next;\n}\n'
                   'println!();'),
    })

add(id=27, title='Простое ли число', topic='Условия', diff='hard', xp=20,
    desc='Дано число 17. Проверь, простое ли оно (делится только на 1 '
         'и на само себя), и выведи «простое» или «составное».',
    expected='простое', lit=['17'],
    hints=['Число простое, если у него нет делителей кроме 1 и самого числа.',
           'Достаточно проверять делители до квадратного корня из числа.'],
    code={
        'python': 'n = 17\nis_prime = n > 1\n'
                  'for d in range(2, int(n ** 0.5) + 1):\n'
                  '    if n % d == 0:\n        is_prime = False\n        break\n'
                  'print("простое" if is_prime else "составное")',
        'javascript': 'const n = 17;\nlet isPrime = n > 1;\n'
                      'for (let d = 2; d * d <= n; d++) {\n'
                      '  if (n % d === 0) { isPrime = false; break; }\n}\n'
                      'console.log(isPrime ? "простое" : "составное");',
        'typescript': 'const n: number = 17;\nlet isPrime: boolean = n > 1;\n'
                      'for (let d = 2; d * d <= n; d++) {\n'
                      '  if (n % d === 0) { isPrime = false; break; }\n}\n'
                      'console.log(isPrime ? "простое" : "составное");',
        'java': j('int n = 17;\nboolean isPrime = n > 1;\n'
                  'for (int d = 2; d * d <= n; d++) {\n'
                  '    if (n % d == 0) { isPrime = false; break; }\n}\n'
                  'System.out.println(isPrime ? "простое" : "составное");'),
        'cpp': cpp('int n = 17;\nbool isPrime = n > 1;\n'
                   'for (int d = 2; d * d <= n; d++) {\n'
                   '    if (n % d == 0) { isPrime = false; break; }\n}\n'
                   'cout << (isPrime ? "простое" : "составное") << endl;'),
        'csharp': cs('int n = 17;\nbool isPrime = n > 1;\n'
                     'for (int d = 2; d * d <= n; d++) {\n'
                     '    if (n % d == 0) { isPrime = false; break; }\n}\n'
                     'Console.WriteLine(isPrime ? "простое" : "составное");'),
        'go': go('n := 17\nisPrime := n > 1\n'
                 'for d := 2; d*d <= n; d++ {\n\tif n%d == 0 {\n'
                 '\t\tisPrime = false\n\t\tbreak\n\t}\n}\n'
                 'if isPrime {\n\tfmt.Println("простое")\n} else {\n'
                 '\tfmt.Println("составное")\n}'),
        'php': '<?php\n$n = 17;\n$isPrime = $n > 1;\n'
               'for ($d = 2; $d * $d <= $n; $d++) {\n'
               '    if ($n % $d == 0) { $isPrime = false; break; }\n}\n'
               'echo $isPrime ? "простое" : "составное";',
        'rust': rs('let n = 17;\nlet mut is_prime = n > 1;\nlet mut d = 2;\n'
                   'while d * d <= n {\n    if n % d == 0 {\n'
                   '        is_prime = false;\n        break;\n    }\n'
                   '    d += 1;\n}\n'
                   'println!("{}", if is_prime { "простое" } else { "составное" });'),
    })

# ===== END =====


if __name__ == '__main__':
    import sys
    langs = sys.argv[1:] or ['java', 'cpp', 'go', 'csharp', 'typescript',
                             'php', 'rust']
    build(langs)