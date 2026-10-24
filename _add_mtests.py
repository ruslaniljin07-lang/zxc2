# -*- coding: utf-8 -*-
"""Temp: доводим тесты модулей в go/csharp/typescript/php/rust до 5 вопросов.

В этих курсах в тесте модуля было 2 вопроса (в python/javascript/java/cpp — 5),
из-за чего одна ошибка уже означала «не зачтено» (порог 60%).
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
LANG_DIR = os.path.join(ROOT, 'data', 'languages')

# язык -> номер модуля -> [(вопрос, варианты, индекс верного, пояснение)]
EXTRA = {}


def ex(lang, module_id, question, options, correct, explain):
    """Дополнительный вопрос теста модуля."""
    EXTRA.setdefault(lang, {}).setdefault(module_id, []).append(
        (question, options, correct, explain))


# ===== GO =====
ex('go', 1, 'Какая функция выводит текст на экран?',
   ['fmt.Println', 'print', 'console.log', 'echo'], 0,
   'fmt.Println печатает значение и переносит строку.')
ex('go', 1, 'Как объявить переменную с выводом типа?',
   ['x := 5', 'var x', 'x = int(5)', 'let x = 5'], 0,
   'Оператор := сам выводит тип и присваивает значение.')
ex('go', 1, 'Какой тип у значения "Го"?',
   ['string', 'int', 'bool', 'float64'], 0,
   'Текст в двойных кавычках — строка.')
ex('go', 2, 'Что вернёт 7 % 2?',
   ['1', '0', '3', '3.5'], 0,
   '% — остаток от деления, 7 % 2 равно 1.')
ex('go', 2, 'Как пропустить одну итерацию цикла?',
   ['continue', 'break', 'skip', 'next'], 0,
   'continue переходит к следующему шагу, break выходит из цикла.')
ex('go', 2, 'Как записать бесконечный цикл?',
   ['for { ... }', 'while true { ... }', 'loop { ... }', 'for (;;) { }'], 0,
   'В Go бесконечный цикл — это for без условия.')
ex('go', 3, 'Что вернёт len([]int{1, 2, 3})?',
   ['3', '2', '4', 'Ошибку'], 0,
   'len() возвращает количество элементов.')
ex('go', 3, 'Сколько значений может вернуть функция Go?',
   ['несколько', 'только одно', 'ни одного', 'ровно два'], 0,
   'Например (int, error) — результат и ошибка сразу.')
ex('go', 3, 'Как объявить map со строковыми ключами?',
   ['map[string]int{}', 'map<int>[]', 'dict[string]', 'map(string)int'], 0,
   'Синтаксис: map[тип_ключа]тип_значения.')

# ===== C# =====
ex('csharp', 1, 'Какой метод выводит строку с переводом строки?',
   ['Console.WriteLine', 'Console.Write', 'print', 'cout'], 0,
   'WriteLine добавляет перевод строки, Write — нет.')
ex('csharp', 1, 'Что означает var в C#?',
   ['тип выводится из значения', 'любой тип', 'строка', 'константа'], 0,
   'var — вывод типа компилятором, а не динамический тип.')
ex('csharp', 1, 'Какой тип подходит для дробного числа?',
   ['double', 'int', 'string', 'bool'], 0,
   'Для дробных чисел бери double, для целых — int.')
ex('csharp', 2, 'Какой блок выполнится, если условие ложно?',
   ['else', 'case', 'catch', 'default'], 0,
   'else — ветка для ложного условия.')
ex('csharp', 2, 'Как выйти из цикла досрочно?',
   ['break', 'continue', 'exit', 'return true'], 0,
   'break прерывает цикл, continue пропускает шаг.')
ex('csharp', 2, 'Как перебрать элементы коллекции?',
   ['foreach (var x in items)', 'for (x : items)', 'loop x in items',
    'each (var x)'], 0,
   'foreach идёт по элементам без индексов.')
ex('csharp', 3, 'Как узнать длину массива nums?',
   ['nums.Length', 'nums.Size', 'len(nums)', 'nums.Count'], 0,
   'У массива свойство Length, у List — Count.')
ex('csharp', 3, 'Что вернёт метод с типом void?',
   ['ничего', '0', 'null', 'false'], 0,
   'void означает «без результата».')
ex('csharp', 3, 'Как создать список, который умеет расти?',
   ['new List<int>()', 'new Array<int>()', 'int[] list', 'new Vector<int>()'],
   0, 'List<T> — динамическая коллекция, массив — фиксированный.')

# ===== TypeScript =====
ex('typescript', 1, 'Что означает ": number" в объявлении переменной?',
   ['тип переменной', 'значение', 'комментарий', 'длину'], 0,
   'После двоеточия указывают тип.')
ex('typescript', 1, 'Какой тип у значения true?',
   ['boolean', 'bool', 'number', 'string'], 0,
   'В TypeScript логический тип называется boolean.')
ex('typescript', 1, 'Что произойдёт при неверном типе?',
   ['ошибка компиляции', 'ничего', 'значение изменится',
    'программа ускорится'], 0,
   'Компилятор TS проверяет типы ещё до запуска.')
ex('typescript', 2, 'Что вернёт выражение n > 0 ? "плюс" : "минус"?',
   ['одну из строк', 'число', 'boolean', 'undefined'], 0,
   'Тернарный оператор возвращает одно из двух значений.')
ex('typescript', 2, 'Как перебрать значения массива?',
   ['for (const x of arr)', 'for (const x in arr)', 'foreach (x)',
    'loop (x)'], 0,
   'for..of идёт по значениям, for..in — по ключам.')
ex('typescript', 2, 'Сколько повторов сделает for (let i = 0; i < 3; i++)?',
   ['3', '2', '4', 'бесконечно'], 0,
   'i примет значения 0, 1 и 2.')
ex('typescript', 3, 'Как получить длину массива nums?',
   ['nums.length', 'nums.length()', 'len(nums)', 'nums.size'], 0,
   'length — это свойство, а не метод.')
ex('typescript', 3, 'Что делает метод map?',
   ['создаёт новый массив из результатов', 'сортирует элементы',
    'удаляет элементы', 'складывает числа'], 0,
   'map применяет функцию к каждому элементу.')
ex('typescript', 3, 'Что указывают после скобок функции?',
   ['тип результата', 'тип аргумента', 'имя функции', 'ничего'], 0,
   'Например: function add(a: number): number.')

# ===== PHP =====
ex('php', 1, 'Как вывести текст в PHP?',
   ['echo "текст";', 'print "текст"()', 'console.log("текст")',
    'cout << "текст"'], 0,
   'echo и print — конструкции вывода.')
ex('php', 1, 'Как склеить две строки?',
   ['точкой .', 'плюсом +', 'запятой ,', 'амперсандом &'], 0,
   'В PHP конкатенация строк выполняется точкой.')
ex('php', 1, 'С какого тега начинается PHP-файл?',
   ['<?php', '<php>', '<?', '<script php>'], 0,
   'Интерпретатор ищет открывающий тег <?php.')
ex('php', 2, 'Что делает if ($n > 0) { ... }?',
   ['выполняет блок при истинном условии', 'создаёт переменную',
    'повторяет блок', 'объявляет функцию'], 0,
   'Скобки вокруг условия в PHP обязательны.')
ex('php', 2, 'Как пропустить одну итерацию цикла?',
   ['continue', 'break', 'skip', 'next'], 0,
   'continue переходит к следующему шагу.')
ex('php', 2, 'Что вернёт 10 % 3?',
   ['1', '0', '3', '3.3'], 0,
   '% возвращает остаток от деления.')
ex('php', 3, 'Как добавить элемент в массив $nums?',
   ['$nums[] = 4;', '$nums.append(4);', 'push($nums, 4);', '$nums.add(4);'],
   0, 'Пустые квадратные скобки добавляют элемент в конец.')
ex('php', 3, 'Что вернёт count($nums)?',
   ['количество элементов', 'сумму элементов', 'отсортированный массив',
    'максимальный элемент'], 0,
   'count считает элементы массива.')
ex('php', 3, 'Каким словом объявляется функция?',
   ['function', 'def', 'func', 'fn'], 0,
   'Функция объявляется словом function.')

# ===== Rust =====
ex('rust', 1, 'Как вывести значение переменной?',
   ['println!("{}", x);', 'print(x)', 'echo x', 'Console.WriteLine(x)'], 0,
   'Фигурные скобки — место подстановки значения.')
ex('rust', 1, 'Какой тип у числа 3.14?',
   ['f64', 'i32', 'bool', 'String'], 0,
   'Дробные числа по умолчанию имеют тип f64.')
ex('rust', 1, 'Что будет при изменении переменной без mut?',
   ['ошибка компиляции', 'значение изменится', 'переменная станет строкой',
    'ничего'], 0,
   'По умолчанию переменные неизменяемы.')
ex('rust', 2, 'Как сделать цикл от 1 до 5 включительно?',
   ['for i in 1..=5', 'for i in 1..5', 'for (i = 1; i <= 5)', 'loop 1..5'], 0,
   'Оператор ..= включает правую границу.')
ex('rust', 2, 'Как в match описать все оставшиеся варианты?',
   ['_ =>', 'else =>', 'default =>', 'other =>'], 0,
   'Шаблон _ закрывает все оставшиеся случаи.')
ex('rust', 2, 'Как выйти из бесконечного цикла loop?',
   ['break', 'continue', 'exit', 'stop'], 0,
   'Бесконечный loop завершают через break.')
ex('rust', 3, 'Как создать вектор из чисел?',
   ['vec![1, 2, 3]', '[1, 2, 3]', 'Vec(1, 2, 3)', 'vector![1, 2, 3]'], 0,
   'Вектор создаётся макросом vec!.')
ex('rust', 3, 'Что делает nums.len()?',
   ['возвращает длину', 'считает сумму', 'сортирует вектор',
    'добавляет элемент'], 0,
   'len() сообщает количество элементов.')
ex('rust', 3, 'Что вернёт функция, если последнее выражение без ;?',
   ['это значение и станет результатом', 'ничего', '0', 'ошибку'], 0,
   'Выражение без точки с запятой становится результатом функции.')


def apply_module_tests(lang):
    """Дописывает вопросы в тесты модулей языка."""
    path = os.path.join(LANG_DIR, lang + '.json')
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)
    data = raw.get(lang, raw)

    before = sum(len((m.get('test') or {}).get('questions') or [])
                 for m in data['modules'])
    for module in data['modules']:
        extras = EXTRA.get(lang, {}).get(module['id'])
        if not extras:
            continue
        test = module.setdefault('test', {})
        questions = test.setdefault('questions', [])
        existing = {q['question'] for q in questions}
        for question, options, correct, explain in extras:
            if question in existing:
                continue
            questions.append({'question': question, 'options': options,
                              'correct': correct, 'explain': explain})
    after = sum(len((m.get('test') or {}).get('questions') or [])
                for m in data['modules'])

    with open(path, 'w', encoding='utf-8') as f:
        json.dump({lang: data}, f, ensure_ascii=False, indent=1)
    print(f'{lang:11} вопросы тестов модулей: {before} -> {after}')


for _lang in ['go', 'csharp', 'typescript', 'php', 'rust']:
    apply_module_tests(_lang)
