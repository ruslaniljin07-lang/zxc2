import subprocess
import sys
import os
import shutil
import tempfile
import re
import time

from utils.sandbox_guard import run_limited, kill_tree

# Строгий режим для Python-кода: audit hook внутри самого процесса
BOOTSTRAP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'sandbox_bootstrap.py')


def _python_argv(target, workdir):
    """Команда запуска пользовательского кода в строгом режиме.

    -I — изолированный режим (нет PYTHONPATH/PYTHONSTARTUP, каталог
    скрипта не попадает в sys.path), затем bootstrap ставит audit hook,
    который запрещает сеть, процессы и доступ к файлам вне песочницы.
    """
    python = sys.executable or 'python'
    return [python, '-I', '-X', 'utf8', BOOTSTRAP, target, workdir]


def _run_python_code(code, timeout=5):
    """Выполняет Python-код в изолированном процессе с лимитами."""
    workdir = tempfile.mkdtemp(prefix='codigo_py_')
    try:
        target = os.path.join(workdir, 'main.py')
        with open(target, 'w', encoding='utf-8', newline='') as f:
            f.write(code)
        return run_limited(_python_argv(target, workdir), workdir, timeout,
                           memory_mb=512, cpu_seconds=timeout)
    except Exception as e:
        return {
            'success': False, 'returncode': None,
            'stdout': '', 'stderr': 'Ошибка при выполнении: ' + str(e)
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _run_js_code(code, timeout=5):
    """Запускает JavaScript-код через Node.js с лимитами и UTF-8."""
    node = shutil.which('node')
    if not node:
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': '', 'no_node': True}
    workdir = tempfile.mkdtemp(prefix='codigo_js_')
    try:
        target = os.path.join(workdir, 'main.js')
        with open(target, 'w', encoding='utf-8', newline='') as f:
            f.write(code)
        return run_limited(
            [node, '--max-old-space-size=256', target], workdir, timeout,
            memory_mb=512, cpu_seconds=timeout)
    except Exception as e:
        return {
            'success': False, 'returncode': None,
            'stdout': '', 'stderr': 'Ошибка при выполнении: ' + str(e)
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _run_java_code(code, timeout=20):
    """Компилирует и запускает Java-код. Имя публичного класса берём из кода."""
    javac = shutil.which('javac')
    java = shutil.which('java')
    if not javac or not java:
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': '', 'no_toolchain': True}
    m = re.search(r'public\s+class\s+([A-Za-z_][A-Za-z0-9_]*)', code)
    cls = m.group(1) if m else 'Main'
    workdir = tempfile.mkdtemp()
    src = os.path.join(workdir, cls + '.java')
    try:
        with open(src, 'w', encoding='utf-8') as f:
            f.write(code)
        comp = run_limited([javac, src], workdir, timeout,
                           memory_mb=1536, cpu_seconds=timeout)
        if comp['returncode'] != 0:
            return {'success': False, 'returncode': comp['returncode'],
                    'stdout': '', 'stderr': comp['stderr']}
        run = run_limited([java, '-cp', workdir, cls], workdir, timeout,
                          memory_mb=768, cpu_seconds=timeout)
        return {'success': run['returncode'] == 0, 'returncode': run['returncode'],
                'stdout': run['stdout'], 'stderr': run['stderr']}
    except subprocess.TimeoutExpired:
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': 'Превышено время выполнения.'}
    except Exception as e:
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': 'Ошибка при выполнении: ' + str(e)}
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _run_cpp_code(code, timeout=20):
    """Компилирует (g++/clang++) и запускает C++-код."""
    compiler = shutil.which('g++') or shutil.which('clang++')
    if not compiler:
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': '', 'no_toolchain': True}
    workdir = tempfile.mkdtemp()
    src = os.path.join(workdir, 'main.cpp')
    out = os.path.join(workdir, 'main.exe')
    try:
        with open(src, 'w', encoding='utf-8') as f:
            f.write(code)
        comp = run_limited([compiler, src, '-o', out], workdir, timeout,
                           memory_mb=1536, cpu_seconds=timeout)
        if comp['returncode'] != 0:
            return {'success': False, 'returncode': comp['returncode'],
                    'stdout': '', 'stderr': comp['stderr']}
        run = run_limited([out], workdir, timeout,
                          memory_mb=512, cpu_seconds=timeout)
        return {'success': run['returncode'] == 0, 'returncode': run['returncode'],
                'stdout': run['stdout'], 'stderr': run['stderr']}
    except subprocess.TimeoutExpired:
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': 'Превышено время выполнения.'}
    except Exception as e:
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': 'Ошибка при выполнении: ' + str(e)}
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _check_sql(code, check, timeout=5):
    """Проверяет SQL-запрос: сравнивает результат с эталонным.

    В задании можно указать:
      setup    — как подготовить базу (схема и данные)
      query    — эталонный запрос (если задан, сравниваются строки)
      expected — строки результата текстом
      columns  — обязательные названия колонок
      mode     — exact | contains
    """
    result = _run_sql_code(code, timeout=timeout,
                           setup=check.get('setup', ''))
    if not result['success']:
        return result
    got = result['stdout'].strip()

    # названия колонок проверяем отдельно: они часть ответа
    columns = check.get('columns')
    if columns:
        names = _sql_columns(code, check.get('setup', ''), timeout)
        if names is None:
            return {'success': False, 'stdout': '',
                    'stderr': 'Ошибка SQL: не удалось прочитать результат.'}
        missing = [c for c in columns if c not in names]
        if missing:
            return {'success': False, 'stdout': result['stdout'],
                    'stderr': ('В результате нет колонок: '
                               + ', '.join(missing) + '. Сейчас есть: '
                               + (', '.join(names) or '(нет данных)'))}

    expected = check.get('expected')
    if expected is None and check.get('query'):
        ref = _run_sql_code(check['query'], timeout=timeout,
                            setup=check.get('setup', ''))
        if not ref['success']:
            return ref
        expected = ref['stdout']
    if expected is None:
        # эталон не задан — запрос просто должен выполниться
        return {'success': True, 'stdout': result['stdout'], 'stderr': ''}

    expected = str(expected).strip()
    if check.get('mode', 'exact') == 'contains':
        matched = expected.lower() in got.lower()
    else:
        def _norm(text):
            return '\n'.join(line.strip() for line in text.splitlines()
                             if line.strip())
        matched = _norm(got) == _norm(expected)
    if matched:
        return {'success': True, 'stdout': result['stdout'], 'stderr': '',
                'expected': expected}
    return {'success': False, 'stdout': result['stdout'],
            'stderr': ('Ожидался такой результат:\n' + expected +
                       '\n\nПолучилось:\n' + (got or '(пусто)')),
            'expected': expected}


def _sql_columns(code, setup, timeout=5):
    """Названия колонок результата запроса (None при ошибке)."""
    import sqlite3

    conn = sqlite3.connect(':memory:')
    try:
        deadline = [time.time() + timeout]
        conn.set_progress_handler(
            lambda: 1 if time.time() > deadline[0] else 0, 10000)
        if setup:
            conn.executescript(setup)
        cur = conn.cursor()
        cur.execute(code.strip())
        return [d[0] for d in (cur.description or [])]
    except Exception:                                            # noqa: BLE001
        return None
    finally:
        conn.close()


def _no_toolchain():
    """Единый ответ, когда для языка нет компилятора или интерпретатора."""
    return {'success': False, 'returncode': None, 'stdout': '',
            'stderr': '', 'no_toolchain': True}


def _build_and_run(code, filename, build_cmd, run_cmd, timeout):
    """Пишет исходник во временную папку, собирает и запускает программу.

    build_cmd / run_cmd — списки команд; {src} и {exe} заменяются на пути.
    Если build_cmd пуст, файл сразу выполняется (интерпретируемые языки).
    """
    workdir = tempfile.mkdtemp()
    try:
        src = os.path.join(workdir, filename)
        exe = os.path.join(workdir, 'prog.exe')
        with open(src, 'w', encoding='utf-8') as f:
            f.write(code)
        if build_cmd:
            build = [part.format(src=src, exe=exe) for part in build_cmd]
            comp = run_limited(build, workdir, timeout,
                               memory_mb=2048, cpu_seconds=timeout)
            if comp['returncode'] != 0:
                return {'success': False, 'returncode': comp['returncode'],
                        'stdout': '', 'stderr': comp['stderr']}
        run = [part.format(src=src, exe=exe) for part in run_cmd]
        result = run_limited(run, workdir, timeout,
                             memory_mb=512, cpu_seconds=timeout)
        return {'success': result['returncode'] == 0,
                'returncode': result['returncode'],
                'stdout': result['stdout'], 'stderr': result['stderr']}
    except subprocess.TimeoutExpired:
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': 'Превышено время выполнения: ' + str(timeout) + ' с.'}
    except Exception as e:
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': 'Ошибка при выполнении: ' + str(e)}
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _run_go_code(code, timeout=60):
    """Собирает Go-код командой go build и запускает полученный файл."""
    go = shutil.which('go')
    if not go:
        return _no_toolchain()
    return _build_and_run(code, 'main.go',
                          [go, 'build', '-o', '{exe}', '{src}'],
                          ['{exe}'], timeout)


def _run_ts_code(code, timeout=60):
    """Запускает TypeScript через Node.js (type stripping, Node 22.6+)."""
    node = shutil.which('node')
    if not node:
        return _no_toolchain()
    result = _build_and_run(code, 'main.ts', [], [node, '{src}'], timeout)
    if (not result['success'] and result.get('returncode') is not None
            and 'Unknown file extension' in (result.get('stderr') or '')):
        # на старых версиях Node флаг для .ts нужно указывать явно
        return _build_and_run(code, 'main.ts', [],
                              [node, '--experimental-strip-types', '{src}'],
                              timeout)
    return result


def _run_php_code(code, timeout=20):
    """Запускает PHP-код интерпретатором php."""
    php = shutil.which('php')
    if not php:
        return _no_toolchain()
    return _build_and_run(code, 'main.php', [], [php, '{src}'], timeout)


def _run_rust_code(code, timeout=60):
    """Компилирует код через rustc и запускает полученный бинарник."""
    rustc = shutil.which('rustc')
    if not rustc:
        return _no_toolchain()
    return _build_and_run(code, 'main.rs',
                          [rustc, '{src}', '-o', '{exe}'],
                          ['{exe}'], timeout)


# --- SQL: запросы выполняются в настоящей базе SQLite в памяти ------------
# Проверяем не текст запроса, а результат: ученик пишет SELECT, а мы
# сравниваем реальные строки, которые вернула база.
SQL_DANGEROUS = (
    'attach', 'pragma', 'load_extension', 'writefile', 'readfile',
    'vacuum', 'backup',
)


def _sql_is_safe(query):
    """Отсекает конструкции, выходящие за рамки базы в памяти."""
    lowered = query.lower()
    return not any(word in lowered for word in SQL_DANGEROUS)


def _format_rows(rows, limit=50):
    """Печатает результат запроса так, чтобы его было видно ученику."""
    lines = []
    for row in rows[:limit]:
        lines.append(' | '.join('' if v is None else str(v) for v in row))
    if len(rows) > limit:
        lines.append('... ещё %d строк' % (len(rows) - limit))
    return '\n'.join(lines)


def _run_sql_code(code, timeout=5, setup=''):
    """Выполняет SQL-запрос в базе SQLite в памяти.

    setup — SQL, который готовит базу перед проверкой (схема и данные).
    Возвращает строки результата в stdout, как и остальные раннеры.
    """
    import sqlite3

    query = (code or '').strip()
    if not query:
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': 'Напиши SQL-запрос.'}
    if not _sql_is_safe(query):
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': 'Песочница: запрещены команды ATTACH, PRAGMA, '
                          'VACUUM и подключение расширений.'}

    conn = None
    try:
        conn = sqlite3.connect(':memory:')
        # ограничение по времени: прерываем слишком долгий запрос
        deadline = [time.time() + timeout]

        def _on_progress():
            return 1 if time.time() > deadline[0] else 0

        conn.set_progress_handler(_on_progress, 10000)
        if setup:
            conn.executescript(setup)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return {'success': True, 'returncode': 0,
                'stdout': _format_rows(rows), 'stderr': ''}
    except Exception as exc:                                     # noqa: BLE001
        message = str(exc)
        if 'interrupted' in message.lower():
            message = ('Запрос выполняется слишком долго (%.0f с).'
                       % timeout)
        return {'success': False, 'returncode': None, 'stdout': '',
                'stderr': 'Ошибка SQL: ' + message}
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def _run_csharp_code(code, timeout=60):
    """Запускает C#: csc/mcs либо dotnet (file-based apps, .NET 10+)."""
    csc = shutil.which('csc') or shutil.which('mcs')
    if csc:
        if os.path.basename(csc).lower().startswith('mcs'):
            build = [csc, '-out:{exe}', '{src}']
        else:
            build = [csc, '/nologo', '/out:{exe}', '{src}']
        return _build_and_run(code, 'Program.cs', build, ['{exe}'], timeout)
    dotnet = shutil.which('dotnet')
    if not dotnet:
        return _no_toolchain()
    try:
        sdk = subprocess.run([dotnet, '--list-sdks'], capture_output=True,
                             text=True, encoding='utf-8', timeout=30)
    except Exception:
        return _no_toolchain()
    listed = sdk.stdout.strip() if sdk.returncode == 0 else ''
    major = 0
    if listed:
        try:
            major = int(listed.splitlines()[0].split('.')[0])
        except (ValueError, IndexError):
            major = 0
    if major < 10:
        # без SDK 10+ одиночный .cs-файл запустить нельзя
        return _no_toolchain()
    return _build_and_run(code, 'Program.cs', [],
                          [dotnet, 'run', '{src}'], timeout)


# тип проверки -> раннер запуска кода
_STDOUT_RUNNERS = {
    'stdout': _run_python_code,
    'stdout_python': _run_python_code,
    'stdout_js': _run_js_code,
    'stdout_java': _run_java_code,
    'stdout_cpp': _run_cpp_code,
    'stdout_go': _run_go_code,
    'stdout_csharp': _run_csharp_code,
    'stdout_ts': _run_ts_code,
    'stdout_php': _run_php_code,
    'stdout_rust': _run_rust_code,
}

# типы, где код нужно компилировать — даём больше времени
_SLOW_TYPES = {'stdout_java', 'stdout_cpp', 'stdout_go', 'stdout_csharp',
               'stdout_ts', 'stdout_rust'}

# код языка приложения -> тип проверки для песочницы
SANDBOX_TYPES = {
    'python': 'stdout',
    'javascript': 'stdout_js',
    'java': 'stdout_java',
    'cpp': 'stdout_cpp',
    'go': 'stdout_go',
    'csharp': 'stdout_csharp',
    'typescript': 'stdout_ts',
    'php': 'stdout_php',
    'rust': 'stdout_rust',
    'sql': 'sql',
}


def _check_stdout_any(code, check, runner, timeout):
    """Запускает код переданным раннером и сверяет вывод с ожидаемым."""
    expected = str(check.get('expected', '')).strip()
    mode = check.get('mode', 'exact')  # exact | contains
    result = runner(code, timeout)
    if result.get('no_toolchain') or result.get('no_node'):
        if check.get('require'):
            # тулчейна нет — проверяем хотя бы ключевые конструкции
            return _check_contains(code, check)
        return {'success': False, 'stdout': '',
                'stderr': 'Нет компилятора или интерпретатора для этого '
                          'языка — запустить код не получится.'}
    if not result['success']:
        return result
    got = result['stdout'].strip()
    if mode == 'contains':
        ok = expected.lower() in got.lower()
    else:
        norm = lambda s: '\n'.join(line.rstrip()
                                   for line in s.strip().splitlines())
        ok = norm(got) == norm(expected)
    if ok:
        return {'success': True, 'stdout': result['stdout'],
                'stderr': '', 'expected': expected}
    return {
        'success': False,
        'stdout': result['stdout'],
        'stderr': ('Ожидался вывод:\n' + expected +
                   '\n\nТвой вывод:\n' + (got or '(пусто)')),
        'expected': expected
    }


def _check_stdout_js(code, check, timeout=5):
    """Проверка JS-кода: запуск через Node.js и сверка вывода."""
    return _check_stdout_any(code, check, _run_js_code, timeout)


def _check_contains(code, check):
    """Проверка для JS/Java/C++: в коде должны присутствовать конструкции."""
    require = check.get('require') or []
    reject = check.get('reject') or []
    missing = [p for p in require if p.lower() not in code.lower()]
    bad = [p for p in reject if p.lower() in code.lower()]
    if missing:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Не хватает ключевых конструкций: '
                      + ', '.join(f'«{m}»' for m in missing),
            'missing': missing
        }
    if bad:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Лишние конструкции (попробуй упростить): '
                      + ', '.join(f'«{b}»' for b in bad),
            'bad': bad
        }
    return {
        'success': True,
        'stdout': 'Код содержит все необходимые конструкции. Отлично!',
        'stderr': ''
    }


def _check_stdout(code, check, timeout=5):
    """Проверка Python-кода: запуск и сверка вывода."""
    return _check_stdout_any(code, check, _run_python_code, timeout)


def check_code(user_code, check, timeout=5):
    """Проверяет решение по правилам задания.

    check — объект из задачи:
      {'type': 'python', 'test_code': '...'}   — реальный запуск Python
      {'type': 'stdout', 'expected': '...'}    — запуск и сверка вывода
      {'type': 'stdout_js', ...}               — запуск JS через Node
      {'type': 'stdout_java', ...}             — компиляция javac + запуск
      {'type': 'stdout_cpp', ...}              — компиляция g++ + запуск
      {'type': 'stdout_go', ...}               — сборка go build + запуск
      {'type': 'stdout_csharp', ...}           — csc/mcs либо dotnet run
      {'type': 'stdout_ts', ...}               — запуск TypeScript через Node
      {'type': 'stdout_php', ...}              — запуск PHP-интерпретатором
      {'type': 'stdout_rust', ...}             — компиляция rustc + запуск
      {'type': 'contains', 'require': [...]}   — проверка конструкций

    Если компилятора/интерпретатора для языка нет, проверка stdout
    откатывается на список конструкций из ключа 'require'.
    """
    if not isinstance(check, dict):
        # старая сигнатура: check_code(user_code, test_code)
        check = {'type': 'python', 'test_code': check}
    ctype = check.get('type', 'python')

    # SQL проверяется отдельно: сравнивается результат запроса, а не вывод
    if ctype == 'sql':
        return _check_sql(user_code, check, timeout)

    if ctype in _STDOUT_RUNNERS:
        expected = str(check.get('expected', '')).strip()
        mode = check.get('mode', 'exact')
        run_timeout = int(check.get('timeout') or
                          (60 if ctype in _SLOW_TYPES else timeout))
        result = _STDOUT_RUNNERS[ctype](user_code, run_timeout)
        if result.get('no_toolchain') or result.get('no_node'):
            if check.get('require'):
                return _check_contains(user_code, check)
            return {'success': False, 'stdout': '',
                    'stderr': 'Нет компилятора или интерпретатора для этого '
                              'языка — запустить код не получится.'}

        if not result['success']:
            return result
        got = result['stdout'].strip()
        if mode == 'contains':
            ok = expected.lower() in got.lower()
        else:
            norm = lambda s: '\n'.join(
                line.rstrip() for line in s.strip().splitlines())
            ok = norm(got) == norm(expected)
        if ok:
            return {'success': True, 'stdout': result['stdout'],
                    'stderr': '', 'expected': expected}
        return {
            'success': False,
            'stdout': result['stdout'],
            'stderr': ('Ожидался вывод:\n' + expected +
                       '\n\nТвой вывод:\n' + (got or '(пусто)')),
            'expected': expected
        }

    if ctype == 'contains':
        return _check_contains(user_code, check)
    full_code = user_code + '\n' + (check.get('test_code') or '')
    return _run_python_code(full_code, timeout)


def run_sandbox_code(code, timeout=5, lang='python'):
    """Песочница: запускает код на выбранном языке, если есть тулчейн."""
    ctype = SANDBOX_TYPES.get(lang, 'stdout')
    if ctype == 'sql':
        # в песочнице ученик работает с учебной базой
        from utils.sql_demo import DEMO_SETUP

        return _run_sql_code(code, timeout=timeout, setup=DEMO_SETUP)
    runner = _STDOUT_RUNNERS.get(ctype, _run_python_code)
    run_timeout = 60 if ctype in _SLOW_TYPES else timeout
    return runner(code, run_timeout)


def sandbox_timeout(lang):
    """Сколько секунд даём песочнице для языка (компилируемым — больше)."""
    ctype = SANDBOX_TYPES.get(lang, 'stdout')
    return 60 if ctype in _SLOW_TYPES else 5


def toolchain_available(lang):
    """Есть ли на машине компилятор/интерпретатор для языка песочницы."""
    if lang == 'sql':
        # SQLite встроен в Python — отдельный тулчейн не нужен
        try:
            import sqlite3

            sqlite3.connect(':memory:').close()
            return True
        except Exception:
            return False
    if lang == 'python':
        return os.path.exists(sys.executable)
    if lang in ('javascript', 'typescript'):
        return bool(shutil.which('node'))
    if lang == 'java':
        return bool(shutil.which('javac') and shutil.which('java'))
    if lang == 'cpp':
        return bool(shutil.which('g++') or shutil.which('clang++'))
    if lang == 'go':
        return bool(shutil.which('go'))
    if lang == 'php':
        return bool(shutil.which('php'))
    if lang == 'rust':
        return bool(shutil.which('rustc'))
    if lang == 'csharp':
        if shutil.which('csc') or shutil.which('mcs'):
            return True
        dotnet = shutil.which('dotnet')
        if not dotnet:
            return False
        try:
            sdk = subprocess.run([dotnet, '--list-sdks'], capture_output=True,
                                 text=True, encoding='utf-8', timeout=30)
        except Exception:
            return False
        listed = sdk.stdout.strip() if sdk.returncode == 0 else ''
        if not listed:
            return False
        try:
            return int(listed.splitlines()[0].split('.')[0]) >= 10
        except (ValueError, IndexError):
            return False
    return False


def sandbox_status(langs=None):
    """Доступность запуска по языкам: {lang: True/False} для переключателя."""
    return {lang: toolchain_available(lang)
            for lang in (langs or SANDBOX_TYPES)}
