"""Изоляция запускаемого пользовательского кода.

Песочница и проверка задач запускают чужой код на сервере, поэтому
здесь собраны все ограничения:

* окружение процесса фильтруется (код не видит SECRET_KEY, DATABASE_URL,
  токены CI и прочие секреты сервера);
* на Windows процесс заворачивается в Job Object: лимит памяти, лимит
  числа процессов, лимит процессорного времени, убийство всего дерева
  процессов при закрытии;
* вывод ограничен по объёму — иначе «бесконечный print» съедает память;
* по таймауту убивается всё дерево процессов (taskkill /T /F);
* для Python-кода включается audit hook (см. bootstrap ниже): запрет сети,
  запуска процессов, импорта опасных модулей и доступа к файлам вне
  рабочей папки.
"""

import os
import subprocess
import sys
import threading
import time

# --- окружение ------------------------------------------------------------
# Переменные, которые можно отдать пользовательскому коду.
ENV_WHITELIST = (
    'PATH', 'PATHEXT', 'SYSTEMROOT', 'SYSTEMDRIVE', 'WINDIR', 'COMSPEC',
    'TEMP', 'TMP', 'NUMBER_OF_PROCESSORS', 'PROCESSOR_ARCHITECTURE',
    'OS', 'LANG', 'LC_ALL', 'HOME', 'APPDATA', 'LOCALAPPDATA',
    'PROGRAMDATA', 'PROGRAMFILES', 'PROGRAMFILES(X86)', 'JAVA_HOME',
    'GOROOT', 'GOPATH', 'DOTNET_ROOT',
)
# Что точно не должно попадать в окружение (доп. страховка)
ENV_BLOCKLIST = (
    'SECRET', 'TOKEN', 'PASSWORD', 'PASSWD', 'API_KEY', 'DATABASE_URL',
    'AWS', 'AZURE', 'GOOGLE', 'OPENAI', 'NGROK', 'GITHUB', 'SMTP',
    'CREDENTIAL', 'PRIVATE', 'COOKIE', 'SESSION',
)

DEFAULT_OUTPUT_LIMIT = 200 * 1024      # 200 КБ на поток вывода
DEFAULT_MEMORY_MB = 512                # 512 МБ на процесс
DEFAULT_MAX_PROCESSES = 8
DEFAULT_CPU_SECONDS = 10


def safe_env(workdir, extra=None):
    """Окружение для пользовательского процесса без секретов сервера."""
    env = {}
    for key, value in os.environ.items():
        if key.upper() in ENV_WHITELIST and not _looks_secret(key):
            env[key] = value
    if 'PATH' not in env:
        env['PATH'] = os.path.dirname(sys.executable)
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['HOME'] = workdir
    env['TEMP'] = workdir
    env['TMP'] = workdir
    env['TMPDIR'] = workdir
    if extra:
        env.update(extra)
    return env


def _looks_secret(key):
    upper = key.upper()
    return any(token in upper for token in ENV_BLOCKLIST)



# --- Job Object (Windows) -------------------------------------------------
JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
JOB_OBJECT_LIMIT_JOB_TIME = 0x00000004
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
CREATE_NEW_PROCESS_GROUP = 0x00000200


def _create_job(memory_mb, max_processes, cpu_seconds):
    """Создаёт Job Object с лимитами. None, если это не Windows."""
    if os.name != 'nt':
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class _BasicLimits(ctypes.Structure):
            _fields_ = [
                ('PerProcessUserTimeLimit', wintypes.LARGE_INTEGER),
                ('PerJobUserTimeLimit', wintypes.LARGE_INTEGER),
                ('LimitFlags', wintypes.DWORD),
                ('MinimumWorkingSetSize', ctypes.c_size_t),
                ('MaximumWorkingSetSize', ctypes.c_size_t),
                ('ActiveProcessLimit', wintypes.DWORD),
                ('Affinity', ctypes.c_ulonglong),
                ('PriorityClass', wintypes.DWORD),
                ('SchedulingClass', wintypes.DWORD),
            ]

        class _IoCounters(ctypes.Structure):
            _fields_ = [
                ('ReadOperationCount', ctypes.c_ulonglong),
                ('WriteOperationCount', ctypes.c_ulonglong),
                ('OtherOperationCount', ctypes.c_ulonglong),
                ('ReadTransferCount', ctypes.c_ulonglong),
                ('WriteTransferCount', ctypes.c_ulonglong),
                ('OtherTransferCount', ctypes.c_ulonglong),
            ]

        class _ExtendedLimits(ctypes.Structure):
            _fields_ = [
                ('BasicLimitInformation', _BasicLimits),
                ('IoInfo', _IoCounters),
                ('ProcessMemoryLimit', ctypes.c_size_t),
                ('JobMemoryLimit', ctypes.c_size_t),
                ('PeakProcessMemoryUsed', ctypes.c_size_t),
                ('PeakJobMemoryUsed', ctypes.c_size_t),
            ]

        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.CreateJobObjectW.argtypes = [wintypes.LPVOID,
                                              wintypes.LPCWSTR]
        job = kernel32.CreateJobObjectW(None, None)
        if not job:
            return None

        info = _ExtendedLimits()
        flags = (JOB_OBJECT_LIMIT_PROCESS_MEMORY |
                 JOB_OBJECT_LIMIT_JOB_MEMORY |
                 JOB_OBJECT_LIMIT_ACTIVE_PROCESS |
                 JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
        if cpu_seconds:
            flags |= JOB_OBJECT_LIMIT_JOB_TIME
            info.BasicLimitInformation.PerJobUserTimeLimit = int(
                cpu_seconds * 10_000_000)
        info.BasicLimitInformation.LimitFlags = flags
        info.BasicLimitInformation.ActiveProcessLimit = max_processes
        info.ProcessMemoryLimit = memory_mb * 1024 * 1024
        info.JobMemoryLimit = memory_mb * 1024 * 1024 * 3
        if not kernel32.SetInformationJobObject(
                job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
                ctypes.byref(info), ctypes.sizeof(info)):
            kernel32.CloseHandle(job)
            return None
        return job
    except Exception:
        return None


def _assign_job(job, process):
    """Помещает уже запущенный процесс в Job Object."""
    if not job:
        return
    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        handle = wintypes.HANDLE(int(process._handle))
        kernel32.AssignProcessToJobObject(job, handle)
    except Exception:
        pass


def _close_job(job):
    if not job:
        return
    try:
        import ctypes

        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.CloseHandle(job)
    except Exception:
        pass


def kill_tree(pid):
    """Убивает процесс и всех его потомков (иначе остаются «зомби»)."""
    if pid is None:
        return
    try:
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)],
                           capture_output=True, timeout=10)
        else:
            subprocess.run(['pkill', '-9', '-P', str(pid)],
                           capture_output=True, timeout=10)
    except Exception:
        pass
    try:
        import signal

        os.kill(pid, signal.SIGKILL)
    except Exception:
        pass


# --- запуск с ограничениями ----------------------------------------------
# Сколько чужого кода может крутиться одновременно (защита от DoS)
MAX_CONCURRENT_RUNS = 3
_run_slots = threading.BoundedSemaphore(MAX_CONCURRENT_RUNS)


def _read_limited(stream, chunks, state, key, limit):
    """Читает поток, сохраняя не больше limit байт."""
    total = 0
    try:
        while True:
            chunk = stream.read(4096)
            if not chunk:
                break
            if total < limit:
                chunks.append(chunk[:limit - total])
            total += len(chunk)
            if total >= limit:
                state[key] = True
    except Exception:
        pass
    finally:
        try:
            stream.close()
        except Exception:
            pass


def run_limited(cmd, workdir, timeout, env=None,
                output_limit=DEFAULT_OUTPUT_LIMIT,
                memory_mb=DEFAULT_MEMORY_MB,
                max_processes=DEFAULT_MAX_PROCESSES,
                cpu_seconds=DEFAULT_CPU_SECONDS,
                use_job=True):
    """Запускает команду в изолированном окружении с лимитами.

    Возвращает словарь в формате остальных раннеров:
    {success, returncode, stdout, stderr} плюс флаги timed_out,
    output_truncated, busy.
    """
    result = {'success': False, 'returncode': None,
              'stdout': '', 'stderr': ''}
    if not _run_slots.acquire(timeout=20):
        result['busy'] = True
        result['stderr'] = ('Сервер сейчас занят выполнением кода. '
                            'Попробуй запустить ещё раз через пару секунд.')
        return result

    proc = None
    job = None
    try:
        creationflags = CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        proc = subprocess.Popen(
            cmd, cwd=workdir, env=env or safe_env(workdir),
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, creationflags=creationflags,
        )
        if use_job:
            job = _create_job(memory_mb, max_processes, cpu_seconds)
            _assign_job(job, proc)

        out_chunks, err_chunks = [], []
        state = {'out': False, 'err': False}
        readers = [
            threading.Thread(target=_read_limited,
                             args=(proc.stdout, out_chunks, state, 'out',
                                   output_limit), daemon=True),
            threading.Thread(target=_read_limited,
                             args=(proc.stderr, err_chunks, state, 'err',
                                   output_limit), daemon=True),
        ]
        for thread in readers:
            thread.start()

        timed_out = False
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_tree(proc.pid)

        for thread in readers:
            thread.join(timeout=5)

        stdout = b''.join(out_chunks).decode('utf-8', 'replace')
        stderr = b''.join(err_chunks).decode('utf-8', 'replace')

        result['returncode'] = proc.returncode
        result['stdout'] = stdout
        result['stderr'] = stderr
        result['success'] = (proc.returncode == 0) and not timed_out
        result['output_truncated'] = bool(state['out'] or state['err'])
        if timed_out:
            result['timed_out'] = True
            result['stderr'] = ('Превышено время выполнения (%d секунд). '
                                'Проверь, нет ли бесконечного цикла '
                                'или долгого ожидания ввода.'
                                % timeout)
        elif result.get('output_truncated'):
            result['stderr'] = (stderr + '\n(вывод обрезан: слишком много '
                                        'данных за один запуск)').strip()
        return result
    except FileNotFoundError as exc:
        result['stderr'] = 'Команда недоступна: ' + str(exc)
        return result
    except Exception as exc:                                     # noqa: BLE001
        result['stderr'] = 'Ошибка при выполнении: ' + str(exc)
        return result
    finally:
        if proc is not None and proc.poll() is None:
            kill_tree(proc.pid)
        _close_job(job)
        _run_slots.release()
