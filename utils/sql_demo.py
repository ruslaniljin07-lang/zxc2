"""Учебная база данных для курса SQL и песочницы.

Схема и данные магазина: товары, покупатели и заказы. Один и тот же набор
используется и в заданиях, и в песочнице, поэтому ученик не удивляется
результату между уроками.
"""

DEMO_SCHEMA = """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
);

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    age INTEGER NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    order_date TEXT NOT NULL
);
"""

DEMO_DATA = """
INSERT INTO products (id, name, category, price, stock) VALUES
 (1, 'Ноутбук', 'Электроника', 75000, 12),
 (2, 'Мышь', 'Электроника', 1200, 140),
 (3, 'Клавиатура', 'Электроника', 3400, 85),
 (4, 'Стол', 'Мебель', 8900, 30),
 (5, 'Кресло', 'Мебель', 12500, 22),
 (6, 'Кофе', 'Продукты', 450, 300),
 (7, 'Чай', 'Продукты', 380, 250),
 (8, 'Ручка', 'Канцелярия', 90, 500),
 (9, 'Тетрадь', 'Канцелярия', 220, 400),
 (10, 'Рюкзак', 'Канцелярия', 3100, 64);

INSERT INTO customers (id, name, city, age) VALUES
 (1, 'Анна', 'Москва', 28),
 (2, 'Борис', 'Москва', 45),
 (3, 'Вера', 'Санкт-Петербург', 34),
 (4, 'Глеб', 'Казань', 19),
 (5, 'Дарья', 'Казань', 52),
 (6, 'Егор', 'Новосибирск', 31),
 (7, 'Зоя', 'Новосибирск', 25),
 (8, 'Иван', 'Екатеринбург', 40);

INSERT INTO orders (id, customer_id, product_id, quantity, order_date) VALUES
 (1, 1, 2, 2, '2024-01-15'),
 (2, 1, 8, 5, '2024-01-16'),
 (3, 2, 1, 1, '2024-01-20'),
 (4, 3, 6, 4, '2024-02-02'),
 (5, 3, 4, 1, '2024-02-03'),
 (6, 4, 9, 3, '2024-02-10'),
 (7, 5, 3, 1, '2024-02-14'),
 (8, 5, 10, 2, '2024-02-15'),
 (9, 6, 7, 6, '2024-03-01'),
 (10, 6, 5, 1, '2024-03-02'),
 (11, 7, 6, 2, '2024-03-05'),
 (12, 8, 1, 1, '2024-03-09'),
 (13, 8, 9, 4, '2024-03-10'),
 (14, 2, 5, 1, '2024-03-11');
"""

# полный скрипт подготовки базы (используется и заданиями, и песочницей)
DEMO_SETUP = DEMO_SCHEMA + DEMO_DATA

# Подписи для таблиц на странице урока: код -> человеческое имя
TABLE_TITLES = {
    'products': ('Товары', 'Что продаём в магазине'),
    'customers': ('Покупатели', 'Кто покупает'),
    'orders': ('Заказы', 'Кто что и когда заказал'),
}


def demo_tables():
    """Содержимое таблиц для показа рядом с редактором.

    Возвращает [{'code', 'title', 'note', 'columns', 'rows'}], чтобы в
    уроке ученик видел реальные значения и мог писать запрос «на глаз».
    """
    import sqlite3

    result = []
    conn = sqlite3.connect(':memory:')
    try:
        conn.executescript(DEMO_SETUP)
        cur = conn.cursor()
        for code in ('products', 'customers', 'orders'):
            try:
                cur.execute('SELECT * FROM %s LIMIT 12' % code)
                columns = [d[0] for d in cur.description or []]
                rows = [[('' if v is None else str(v)) for v in row]
                        for row in cur.fetchall()]
            except sqlite3.Error:
                continue
            title, note = TABLE_TITLES.get(code, (code, ''))
            result.append({'code': code, 'title': title, 'note': note,
                           'columns': columns, 'rows': rows})
    finally:
        conn.close()
    return result
