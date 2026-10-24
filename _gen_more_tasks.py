"""Дополняет банки задач до 38 штук и добавляет сложных заданий.

Новые задачи идут после существующих: id продолжаются, чтобы не потерять
прогресс пользователей. Эталоны обязаны реально проходить проверку —
это проверяет _check_lessons.py.
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.join(ROOT, 'data', 'tasks')

# Тип проверки для каждого языка
TYPES = {
    'python': 'stdout', 'javascript': 'stdout_js',
    'typescript': 'stdout_ts', 'java': 'stdout_java', 'cpp': 'stdout_cpp',
    'go': 'stdout_go', 'csharp': 'stdout_csharp', 'php': 'stdout_php',
    'rust': 'stdout_rust',
}

NEW = {}


def add(lang, title, topic, description, solution, expected, difficulty,
        require=None):
    NEW.setdefault(lang, []).append(
        (title, topic, description, solution, expected, difficulty,
         require or []))


# ============================== PYTHON ===================================
add('python', 'Сумма цифр числа', 'Строки и числа',
    'Напиши функцию digit_sum(n), которая возвращает сумму цифр числа n.',
    'def digit_sum(n):\n    total = 0\n    while n > 0:\n        total += n '
    '% 10\n        n //= 10\n    return total\n\nprint(digit_sum(1234))',
    '10', 'medium', ['def', 'while'])
add('python', 'Проверка на чётность', 'Условия',
    'Выведи «чётное» или «нечётное» для чисел от 1 до 5, каждое с новой '
    'строки.',
    'for n in range(1, 6):\n    if n % 2 == 0:\n        print("чётное")\n'
    '    else:\n        print("нечётное")',
    'нечётное\nчётное\nнечётное\nчётное\nнечётное', 'easy', ['for', 'if'])
add('python', 'Найди максимум', 'Списки',
    'Дан список чисел. Выведи наибольшее из них без использования max().',
    'nums = [12, 7, 45, 3, 89]\nbest = nums[0]\nfor n in nums:\n    if n '
    '> best:\n        best = n\nprint(best)',
    '89', 'medium', ['for'])
add('python', 'Разворот строки', 'Строки и f-строки',
    'Выведи строку «olleH» (слово «Hello» задом наперёд), не используя '
    'срезы.',
    's = "Hello"\nresult = ""\nfor ch in s:\n    result = ch + result\n'
    'print(result)',
    'olleH', 'medium', ['for'])
add('python', 'Словарь заказов', 'Словари',
    'Создай словарь с количеством товаров и выведи его по одному ключу на '
    'строку в формате «товар: количество».',
    'stock = {"яблоки": 5, "бананы": 3}\nfor name, count in '
    'stock.items():\n    print(f"{name}: {count}")',
    'яблоки: 5\nбананы: 3', 'medium', ['for'])
add('python', 'Простые числа', 'Циклы',
    'Выведи все простые числа от 2 до 20, каждое с новой строки.',
    'for n in range(2, 21):\n    is_prime = True\n    for d in range(2, n):\n'
    '        if n % d == 0:\n            is_prime = False\n            break\n'
    '    if is_prime:\n        print(n)',
    '2\n3\n5\n7\n11\n13\n17\n19', 'hard', ['for', 'if', 'break'])
add('python', 'Класс «Кошелёк»', 'Классы',
    'Создай класс Wallet с балансом, методом add(amount) и свойством '
    'balance. Выведи баланс после пополнения на 500.',
    'class Wallet:\n    def __init__(self):\n        self._balance = 0\n\n'
    '    def add(self, amount):\n        self._balance += amount\n\n'
    '    @property\n    def balance(self):\n        return '
    'self._balance\n\nw = Wallet()\nw.add(500)\nprint(w.balance)',
    '500', 'hard', ['class', 'def'])
add('python', 'Сортировка пузырьком', 'Списки',
    'Отсортируй список чисел по возрастанию вручную (пузырьком) и выведи '
    'его через запятую.',
    'nums = [5, 3, 8, 1]\nfor i in range(len(nums)):\n    for j in '
    'range(len(nums) - i - 1):\n        if nums[j] > nums[j + 1]:\n'
    '            nums[j], nums[j + 1] = nums[j + 1], nums[j]\n'
    'print(", ".join(str(n) for n in nums))',
    '1, 3, 5, 8', 'hard', ['for', 'if'])
