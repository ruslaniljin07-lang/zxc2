import json, os, urllib.request, urllib.error, re, html, time, http.cookiejar, urllib.parse

BASE = "http://127.0.0.1:5000"
FAILS = []
checks = 0

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def check(name, cond, detail=""):
    global checks
    checks += 1
    if cond:
        print("  OK  " + name)
    else:
        print("  FAIL " + name + (" :: " + detail if detail else ""))
        FAILS.append(name)

def get(path, allow_redirect=True):
    time.sleep(0.5)
    try:
        r = opener.open(BASE + path, timeout=8)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")
    except Exception as e:
        return None, str(e)

def post(path, data, csrf_token=None):
    time.sleep(0.5)
    body = urllib.parse.urlencode(data).encode()
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    if csrf_token:
        headers['X-CSRF-Token'] = csrf_token
        data['csrf_token'] = csrf_token
        body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(BASE + path, data=body, headers=headers)
    try:
        r = opener.open(req, timeout=8)
        return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")
    except Exception as e:
        return None, str(e)

def get_csrf(body):
    m = re.search(r'<meta[^>]+name=["\']csrf-token["\'][^>]+content=["\']([^"\']+)', body)
    if m:
        return m.group(1)
    return None

print("=" * 60)
print("АУДИТ САЙТА (с авторизацией)")
print("=" * 60)

# --- Регистрация (один фиксированный пользователь на все циклы) ---
print("\n[0] Регистрация/вход")
TEST_USER = "audit_fixed"
TEST_PASS = "AuditPass2026!"
st, b = get("/register")
csrf = get_csrf(b)
check("Страница регистрации 200", st == 200, str(st))
check("CSRF токен есть", csrf is not None, "")
reg_data = {
    "username": TEST_USER,
    "email": TEST_USER + "@test.ru",
    "password": TEST_PASS,
    "confirm": TEST_PASS
}
if csrf:
    st, b = post("/register", reg_data, csrf_token=csrf)
else:
    st, b = post("/register", reg_data)
# 200 = форма с ошибкой (пользователь уже есть), 302 = удачно
check("Регистрация (200/302)", st in (200, 302), str(st))

# --- Логин ---
st, b = get("/login")
csrf = get_csrf(b)
check("Страница входа 200", st == 200, str(st))
login_data = {"username": TEST_USER, "password": TEST_PASS}
if csrf:
    st, b = post("/login", login_data, csrf_token=csrf)
else:
    st, b = post("/login", login_data)
check("Логин (редирект 302 или форма 200)", st in (200, 302), str(st))
# Проверяем реальную авторизацию по кнопке «Выйти»
st, b = get("/dashboard")
check("Дашборд доступен после логина", st == 200, str(st))
check("Пользователь авторизован (кнопка Выйти)", "Выйти" in b or "logout" in b.lower(), str(st))

# --- 1. Главная ---
print("\n[1] Главная")
st, body = get("/")
check("Главная 200", st == 200, str(st))
for lang in ["python", "javascript", "typescript", "java", "csharp", "cpp", "go", "rust", "php", "sql"]:
    check("Карточка " + lang, lang in body.lower(), "")

# --- 2. Языковые страницы ---
print("\n[2] Страницы языков")
for lang in ["python", "javascript", "typescript", "java", "csharp", "cpp", "go", "rust", "php", "sql"]:
    st, b = get("/language/" + lang)
    check(f"Язык {lang} доступен", st == 200, str(st))

# --- 3. Уроки ---
print("\n[3] Уроки")
for lang in ["python", "javascript", "typescript", "java", "csharp", "cpp", "go", "rust", "php", "sql"]:
    st, b = get("/lessons/" + lang)
    check(f"Уроки {lang}", st == 200, str(st))

# --- 4. Пример кода в уроке ---
print("\n[4] Пример кода в уроке")
st, b = get("/lesson/python/1")
check("Пример кода есть", "```" in b or "<pre" in b or "def " in b or "class " in b, "")
check("Не ошибка 500", st != 500, str(st))

# --- 5. Тесты модулей ---
print("\n[5] Тесты модулей")
for lang in ["python", "javascript", "typescript", "java", "csharp", "cpp", "go", "rust", "php", "sql"]:
    st, b = get("/module_test/" + lang + "/1")
    check(f"Тест {lang}/1", st == 200, str(st))

# --- 6. Задачи ---
print("\n[6] Задачи")
for lang in ["python", "javascript", "typescript", "java", "csharp", "cpp", "go", "rust", "php", "sql"]:
    st, b = get("/language/" + lang + "/tasks")
    check(f"Задачи {lang}", st == 200, str(st))

# --- 7. Шпаргалки ---
print("\n[7] Шпаргалки")
for lang in ["python", "javascript", "typescript", "java", "csharp", "cpp", "go", "rust", "php", "sql"]:
    st, b = get("/cheat_sheet/" + lang)
    check(f"Шпаргалка {lang}", st == 200, str(st))

# --- 8. Песочница ---
print("\n[8] Песочница")
for lang in ["python", "javascript", "typescript", "java", "csharp", "cpp", "go", "rust", "php", "sql"]:
    st, b = get("/sandbox/" + lang)
    check(f"Песочница {lang}", st == 200, str(st))

# --- 9. SQL урок с таблицей ---
print("\n[9] SQL урок с таблицей")
st, b = get("/lesson/sql/1")
check("SQL урок 200", st == 200, str(st))
check("Таблица SQL есть", "table" in b.lower() or "<table" in b, "")

# --- 10. Ошибки ---
print("\n[10] Ошибки")
st, b = get("/nonexistent-xyz")
check("404 существует", st == 404 or st == 302, str(st))

print("\n" + "=" * 60)
print("Всего проверок:", checks)
print("Ошибок:", len(FAILS))
if FAILS:
    print("Список ошибок:")
    for f in FAILS:
        print("  - " + f)
else:
    print("Всё чисто!")