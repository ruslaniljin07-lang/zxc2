# -*- coding: utf-8 -*-
"""Temp: расширение шпаргалок всех курсов data/languages/*.json.

Скрипт доводит каждую шпаргалку до 10 тем: существующие темы сохраняются
(переносятся в нужном порядке), недостающие добавляются ниже блока CHEATS.
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
LANG_DIR = os.path.join(ROOT, 'data', 'languages')

# порядок тем на странице шпаргалок (существующие + новые)
ORDER = {
    'python': ['Переменные и типы', 'Строки и f-строки', 'Условия', 'Циклы',
               'Списки', 'Словари', 'Функции', 'Модули и импорты', 'Классы',
               'Ошибки'],
    'javascript': ['Переменные', 'Строки и шаблоны', 'Условия', 'Циклы',
                   'Массивы', 'Методы массива', 'Объекты и JSON', 'Функции',
                   'Классы', 'Ошибки'],
    'java': ['Основы', 'Переменные', 'Условия', 'Циклы', 'Массивы', 'Строки',
             'Коллекции', 'Методы', 'ООП', 'Ошибки'],
    'cpp': ['Основы', 'Переменные', 'Условия', 'Циклы', 'Массивы и строки',
            'Векторы', 'Функции и указатели', 'Ссылки', 'Структуры и классы',
            'Ввод с клавиатуры'],
    'go': ['Основы', 'Переменные', 'Условия', 'Циклы', 'Слайсы и map',
           'Строки и fmt', 'Функции', 'Методы и структуры', 'Ошибки',
           'Пакеты и импорты'],
    'csharp': ['Основы', 'Переменные', 'Строки', 'Условия', 'Циклы',
               'Массивы', 'Коллекции', 'Методы', 'Классы и объекты',
               'Ошибки'],
    'typescript': ['Основы', 'Типы', 'Строки и шаблоны', 'Условия', 'Циклы',
                   'Массивы', 'Функции', 'Интерфейсы', 'Объединения типов',
                   'Классы'],
    'php': ['Основы', 'Переменные', 'Строки', 'Условия', 'Циклы', 'Массивы',
            'Функции', 'Классы', 'Ошибки', 'Подключение файлов'],
    'rust': ['Основы', 'Переменные', 'Строки', 'Условия', 'Циклы',
             'Коллекции', 'Функции', 'Структуры', 'Владение и заимствование',
             'Ошибки'],
}

# язык -> {тема: {'icon': ..., 'code': ..., 'note': ...}}
CHEATS = {}


def item(icon, code, note):
    """Новая тема шпаргалки."""
    return {'icon': icon, 'code': code, 'note': note}


def detect_indent(path):
    """Отступ JSON-файла, чтобы не переформатировать существующие данные."""
    with open(path, encoding='utf-8') as f:
        lines = f.read().splitlines()
    if len(lines) > 1:
        return len(lines[1]) - len(lines[1].lstrip(' '))
    return 1


def expand(lang):
    """Перестраивает список шпаргалок языка по ORDER + CHEATS."""
    path = os.path.join(LANG_DIR, lang + '.json')
    indent = detect_indent(path)
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)
    data = raw.get(lang, raw)

    old = data.get('cheatsheets') or []
    by_title = {c['title']: c for c in old}
    plan = ORDER[lang]
    additions = CHEATS.get(lang, {})

    unknown = [t for t in by_title if t not in plan]
    if unknown:
        raise SystemExit(f'{lang}: темы вне ORDER: {unknown}')
    lost = [t for t in plan if t not in by_title and t not in additions]
    if lost:
        raise SystemExit(f'{lang}: нет ни старой, ни новой темы: {lost}')

    items = []
    added = []
    for title in plan:
        if title in by_title:
            items.append(by_title[title])
            continue
        extra = additions[title]
        items.append({'title': title, 'icon': extra['icon'],
                      'code': extra['code'], 'note': extra['note']})
        added.append(title)

    data['cheatsheets'] = items
    # обычный текстовый режим: как и остальные файлы проекта, сохраняем CRLF
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({lang: data}, f, ensure_ascii=False, indent=indent)
    print(f'{lang:11} шпаргалок: {len(old)} -> {len(items)} '
          f'(новые: {", ".join(added) or "нет"})')


# ===== НОВЫЕ ТЕМЫ =====

CHEATS['python'] = {
    'Строки и f-строки': item(
        '\U0001F4DD',
        "s = 'Привет'\ns.upper()            # ПРИВЕТ\ns.lower()            # привет\n"
        "len(s)               # 6\ns.split(' ')         # список слов\n\n"
        "name = 'Аня'\nf'Привет, {name}!'    # подставит значение",
        'F-строка — самый короткий способ собрать текст из значений.'),
    'Модули и импорты': item(
        '\U0001F9F0',
        'import math\n\nprint(math.sqrt(16))   # 4.0\n\n'
        'from random import randint\nprint(randint(1, 6))   # случайное число\n\n'
        '# свой файл utils.py рядом:\n# import utils',
        'Импорт подключает код стандартной библиотеки или своего файла.'),
}

CHEATS['javascript'] = {
    'Строки и шаблоны': item(
        '\U0001F4DD',
        "let name = 'Аня';\nname.length;                    // 3\n"
        "name.toUpperCase();             // АНЯ\n"
        "let msg = `Привет, ${name}!`;   // шаблонная строка\n"
        "let parts = 'a,b,c'.split(','); // ['a','b','c']",
        'Обратные кавычки позволяют вставлять значения прямо в текст.'),
    'Методы массива': item(
        '\U0001F9EE',
        'let nums = [1, 2, 3, 4];\nnums.map(n => n * 2);           // [2,4,6,8]\n'
        'nums.filter(n => n % 2 === 0);     // [2,4]\n'
        'nums.reduce((a, b) => a + b, 0); // 10\n'
        'nums.includes(3);               // true',
        'map меняет элементы, filter отбирает, reduce сворачивает их в одно '
        'значение.'),
    'Классы': item(
        '\U0001F3DB\uFE0F',
        "class User {\n  constructor(name) {\n    this.name = name;\n  }\n"
        "  hello() {\n    return 'Привет, ' + this.name;\n  }\n}\n\n"
        "let u = new User('Аня');\nu.hello();",
        'class и new работают так же, как в других языках.'),
    'Ошибки': item(
        '\U0001F6E1\uFE0F',
        "try {\n  JSON.parse('не json');\n} catch (e) {\n  "
        "console.log('Ошибка: ' + e.message);\n} finally {\n  "
        "console.log('выполнится всегда');\n}",
        'try/catch не даёт программе упасть из-за неожиданных данных.'),
}

CHEATS['java'] = {
    'Циклы': item(
        '\U0001F501',
        'for (int i = 0; i < 5; i++) {\n    System.out.println(i);\n}\n\n'
        'int n = 0;\nwhile (n < 3) { n++; }\n\n'
        'for (int x : new int[]{1, 2, 3}) {\n    System.out.println(x);\n}',
        'for-each перебирает элементы массива или коллекции без индексов.'),
    'Коллекции': item(
        '\U0001F5C2\uFE0F',
        'import java.util.ArrayList;\n\n'
        'ArrayList<String> list = new ArrayList<>();\nlist.add("Аня");\n'
        'list.add("Иван");\nlist.size();            // 2\n'
        'list.get(0);            // "Аня"\nlist.contains("Аня");    // true',
        'ArrayList растёт сам, а массив имеет фиксированную длину.'),
    'Методы': item(
        '\U0001F6E0\uFE0F',
        'static int add(int a, int b) {\n    return a + b;\n}\n\n'
        'static void greet(String name) {\n    '
        'System.out.println("Привет, " + name);\n}',
        'static позволяет вызывать метод из main без создания объекта.'),
    'Ошибки': item(
        '\U0001F6E1\uFE0F',
        'try {\n    int x = Integer.parseInt("abc");\n'
        '} catch (NumberFormatException e) {\n    '
        'System.out.println("Не число: " + e.getMessage());\n'
        '} finally {\n    System.out.println("всегда");\n}',
        'catch указывает конкретный класс исключения — так точнее.'),
}

CHEATS['cpp'] = {
    'Векторы': item(
        '\U0001F4DA',
        'vector<int> nums = {1, 2, 3};\nnums.push_back(4);   // {1,2,3,4}\n'
        'nums.size();        // 4\nnums[0];            // 1\n\n'
        '// нужен #include <vector>',
        'vector — растущий массив из стандартной библиотеки.'),
    'Ссылки': item(
        '\U0001F517',
        'void addOne(int& x) {   // ссылка: меняет сам аргумент\n    x += 1;\n}\n\n'
        'int a = 5;\naddOne(a);   // a == 6',
        'Ссылка — второе имя переменной, указатель — адрес в памяти.'),
    'Структуры и классы': item(
        '\U0001F3DB\uFE0F',
        'struct Point {\n    int x;\n    int y;\n};\n\n'
        'Point p{3, 4};\ncout << p.x << " " << p.y;\n\n'
        'class Cat {\npublic:\n    string name;\n'
        '    Cat(string n) : name(n) {}\n};',
        'В struct поля открыты по умолчанию, в class — закрыты.'),
    'Ввод с клавиатуры': item(
        '\u2328\uFE0F',
        'int n;\ncout << "Число: ";\ncin >> n;\n\n'
        'string line;\ngetline(cin, line);   // вся строка целиком\n\n'
        'cout << "Ты ввёл " << n;',
        'cin читает до пробела, getline — всю строку.'),
}

CHEATS['go'] = {
    'Строки и fmt': item(
        '\U0001F4DD',
        'name := "Аня"\nfmt.Println("Привет,", name)\n'
        'fmt.Printf("Имя: %s, возраст: %d\\n", name, 25)\n'
        's := fmt.Sprintf("%s!", name)   // собрать в строку\n'
        'len(name)                       // длина в байтах',
        'Printf печатает по шаблону, Sprintf возвращает строку.'),
    'Методы и структуры': item(
        '\U0001F3DB\uFE0F',
        'type User struct {\n\tName string\n\tAge  int\n}\n\n'
        'func (u User) Hello() string {\n\treturn "Привет, " + u.Name\n}\n\n'
        'u := User{Name: "Аня", Age: 25}\nfmt.Println(u.Hello())',
        'Метод — обычная функция, у которой перед именем указан получатель.'),
    'Ошибки': item(
        '\U0001F6E1\uFE0F',
        'n, err := strconv.Atoi("abc")\nif err != nil {\n'
        '\tfmt.Println("ошибка:", err)\n}\n\n'
        'func div(a, b float64) (float64, error) {\n\tif b == 0 {\n'
        '\t\treturn 0, fmt.Errorf("деление на ноль")\n\t}\n'
        '\treturn a / b, nil\n}',
        'Ошибка в Go — обычное возвращаемое значение, её проверяют через '
        'if err != nil.'),
    'Пакеты и импорты': item(
        '\U0001F9F0',
        'package main\n\nimport (\n\t"fmt"\n\t"strconv"\n\t"strings"\n)\n\n'
        'func main() {\n\tfmt.Println(strings.ToUpper("привет"))\n}',
        'Импортировать нужно только те пакеты, которые реально используются.'),
}

CHEATS['csharp'] = {
    'Строки': item(
        '\U0001F4DD',
        'string name = "Аня";\nname.Length;             // 3\n'
        'name.ToUpper();          // АНЯ\nname.Contains("н");      // true\n'
        'string msg = $"Привет, {name}!";   // интерполяция',
        'Знак $ перед строкой включает подстановку значений в фигурных скобках.'),
    'Коллекции': item(
        '\U0001F5C2\uFE0F',
        'var list = new List<string> { "Аня", "Иван" };\nlist.Add("Пётр");\n'
        'list.Remove("Иван");\nlist.Count;             // 2\n'
        'list.Contains("Аня");   // true\n\n'
        'var ages = new Dictionary<string, int> { { "Аня", 20 } };\n'
        'ages["Иван"] = 25;\nages.Count;             // 2',
        'List — растущий список, Dictionary — словарь «ключ: значение».'),
    'Классы и объекты': item(
        '\U0001F3DB\uFE0F',
        'class User {\n    public string Name { get; set; }\n\n'
        '    public User(string name) {\n        Name = name;\n    }\n\n'
        '    public string Hello() => "Привет, " + Name;\n}\n\n'
        'var u = new User("Аня");\nConsole.WriteLine(u.Hello());',
        'Свойства с get/set удобнее публичных полей.'),
    'Ошибки': item(
        '\U0001F6E1\uFE0F',
        'try {\n    int n = int.Parse("abc");\n'
        '} catch (FormatException e) {\n    '
        'Console.WriteLine("Не число: " + e.Message);\n'
        '} finally {\n    Console.WriteLine("всегда");\n}',
        'catch ловит конкретный тип исключения, finally выполняется всегда.'),
}

CHEATS['typescript'] = {
    'Строки и шаблоны': item(
        '\U0001F4DD',
        "const name: string = 'Аня';\nconst msg: string = `Привет, ${name}!`;\n"
        "name.length;\nname.toUpperCase();\n"
        "const parts: string[] = 'a,b,c'.split(',');",
        'Шаблонная строка в обратных кавычках подставляет значения любого типа.'),
    'Интерфейсы': item(
        '\U0001F9F1',
        "interface User {\n  name: string;\n  age?: number;      "
        "// необязательное поле\n}\n\nconst u: User = { name: 'Аня' };\n\n"
        "function greet(user: User): string {\n  return 'Привет, ' + user.name;\n}",
        'Интерфейс описывает форму объекта, и компилятор следит за ней.'),
    'Объединения типов': item(
        '\U0001F517',
        'function fmt(value: string | number): string {\n'
        "  if (typeof value === 'number') {\n"
        '    return value.toFixed(1);    // здесь TS знает: число\n  }\n'
        '  return value.toUpperCase();   // а здесь — строка\n}',
        'Union-тип разрешает несколько вариантов, typeof их различает.'),
    'Классы': item(
        '\U0001F3DB\uFE0F',
        'class User {\n  constructor(public name: string, '
        'private age: number = 0) {}\n\n  hello(): string {\n'
        '    return `Привет, ${this.name}`;\n  }\n}\n\n'
        "const u = new User('Аня');\nu.hello();",
        'Модификаторы public/private в конструкторе сразу создают свойства.'),
}

CHEATS['php'] = {
    'Строки': item(
        '\U0001F4DD',
        '$name = "Аня";\nstrlen($name);              // 6 — байты\n'
        'mb_strlen($name);           // 3 — символы\n'
        'strtoupper($name);\nstr_replace("А", "О", $name);\n'
        '$msg = "Привет, {$name}!";  // интерполяция в двойных кавычках',
        'Для юникода бери mb_* функции: обычные считают байты, а не символы.'),
    'Классы': item(
        '\U0001F3DB\uFE0F',
        'class User {\n    public $name;\n\n'
        '    public function __construct($name) {\n        $this->name = $name;\n'
        '    }\n\n    public function hello() {\n'
        '        return "Привет, {$this->name}";\n    }\n}\n\n'
        '$u = new User("Аня");\necho $u->hello();',
        'Стрелка -> обращается к свойствам и методам объекта.'),
    'Ошибки': item(
        '\U0001F6E1\uFE0F',
        'try {\n    $n = intdiv(10, 0);\n} catch (DivisionByZeroError $e) {\n'
        '    echo "Ошибка: " . $e->getMessage();\n} finally {\n'
        '    echo "всегда";\n}',
        'Исключения ловят через try/catch, как в других языках.'),
    'Подключение файлов': item(
        '\U0001F9F0',
        "require 'config.php';     // обязательный файл\n"
        "include 'header.php';     // необязательный\n"
        "require_once 'db.php';    // подключить только один раз",
        'require падает с ошибкой, если файла нет, include — только '
        'предупреждает.'),
}

CHEATS['rust'] = {
    'Строки': item(
        '\U0001F4DD',
        'let s: &str = "Привет";        // строковый литерал\n'
        'let mut owned = String::from("Привет");\nowned.push_str(", мир");\n'
        'owned.len()                      // длина в байтах\n'
        'let up = owned.to_uppercase();\n'
        'let n = owned.chars().count();   // число символов',
        '&str — заимствованный текст, String — своя изменяемая строка.'),
    'Структуры': item(
        '\U0001F3DB\uFE0F',
        'struct User {\n    name: String,\n    age: u32,\n}\n\n'
        'impl User {\n    fn hello(&self) -> String {\n'
        '        format!("Привет, {}", self.name)\n    }\n}\n\n'
        'let u = User { name: String::from("Аня"), age: 25 };\n'
        'println!("{}", u.hello());',
        'Блок impl добавляет методам структуру-получателя.'),
    'Владение и заимствование': item(
        '\U0001F512',
        'let s = String::from("привет");\n'
        'let moved = s;          // владение перешло в moved\n'
        '// println!("{}", s);   // ошибка: s больше ничем не владеет\n\n'
        'let a = String::from("привет");\n'
        'let borrowed = &a;      // заимствование: a остаётся владельцем\n'
        'println!("{}", borrowed);\nprintln!("{}", a);',
        'У значения один владелец: либо передаём владение, либо ссылку.'),
    'Ошибки': item(
        '\U0001F6E1\uFE0F',
        'let parsed: Result<i32, _> = "12".parse::<i32>();\n\n'
        'match parsed {\n    Ok(value) => println!("число {}", value),\n'
        '    Err(_) => println!("не число"),\n}\n\n'
        'let opt: Option<i32> = Some(5);\nif let Some(v) = opt {\n'
        '    println!("есть значение {}", v);\n}',
        'Result — для ошибок, Option — для случая «значения может не быть».'),
}

LANGS = ['python', 'javascript', 'java', 'cpp', 'go', 'csharp', 'typescript',
         'php', 'rust']

for _lang in LANGS:
    expand(_lang)
