"""Строгий режим запуска пользовательского Python-кода.

Запускается как: python -I -X utf8 sandbox_bootstrap.py <файл> <рабочая папка>

Внутри процесса ставится audit hook, который запрещает:
* сеть (socket/ssl/http/urllib/requests/...);
* запуск процессов и загрузку нативных библиотек
  (subprocess/os.system/os.exec/ctypes);
* импорт опасных модулей (multiprocessing, winreg, pickle, psutil...);
* чтение файлов вне песочницы и вне стандартной библиотеки;
* запись/удаление/переименование вне песочницы.

Так «просто запустить код» через сайт нельзя превратить в захват сервера:
код не видит файлы проекта, базу и не может отправить данные наружу.
"""

import os
import runpy
import sys

BLOCKED_MODULES = {
    'socket', 'socketserver', 'ssl', 'http', 'urllib', 'urllib3', 'requests',
    'httpx', 'aiohttp', 'ftplib', 'smtplib', 'poplib', 'imaplib',
    'telnetlib', 'xmlrpc', 'subprocess', 'ctypes', 'multiprocessing',
    'winreg', '_winreg', 'msvcrt', 'pty', 'pickle', 'shelve', 'marshal',
    'psutil', 'pynput', 'pyautogui', 'keyboard', 'mouse', 'joblib',
    'webbrowser', 'asyncio', 'asynchat', 'asyncore', 'smtpd', 'xmlrpc.client',
}

NET_EVENTS = {
    'socket.connect', 'socket.bind', 'socket.getaddrinfo',
    'socket.gethostbyname', 'socket.gethostbyaddr', 'socket.sendto',
    'socket.sethostname', 'socket.__new__', 'ssl.wrap_socket',
    'ftplib.connect', 'smtplib.connect', 'imaplib.open',
}

PROCESS_EVENTS = {
    'subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn',
    'os.spawn', 'os.fork', 'os.forkpty', 'os.startfile',
    'ctypes.dlopen', 'ctypes.dlsym', 'ctypes.call_function',
    'webbrowser.open', 'os.kill', 'os.killpg',
}

FS_WRITE_EVENTS = {
    'os.remove', 'os.rename', 'os.replace', 'os.mkdir', 'os.rmdir',
    'os.chmod', 'os.chown', 'os.truncate', 'os.link', 'os.symlink',
    'shutil.copyfile', 'shutil.copymode', 'shutil.copystat',
    'shutil.rmtree', 'shutil.move',
}


def _roots(sandbox):
    """Папки, чтение из которых разрешено (песочница + стандартная
    библиотека Python). Всё остальное — в том числе файлы проекта,
    база данных и ключи — читать нельзя."""
    read_roots = [sandbox, sys.prefix, sys.base_prefix, sys.exec_prefix]
    try:
        import os as _os
        read_roots.append(_os.path.dirname(_os.__file__))
    except Exception:
        pass
    # виртуальное окружение, если оно есть
    for name in ('base_exec_prefix', 'exec_prefix'):
        value = getattr(sys, name, None)
        if value:
            read_roots.append(value)
    return read_roots


def _real(path):
    try:
        return os.path.realpath(path).lower()
    except Exception:
        return ''


def _inside(path, roots):
    real = _real(path)
    if not real:
        return False
    for root in roots:
        root_real = _real(root)
        if root_real and (real == root_real or
                          real.startswith(root_real + os.sep)):
            return True
    return False


def install_hook(sandbox):
    read_roots = _roots(sandbox)
    write_roots = [sandbox]

    def audit(event, args):
        if event == 'open':
            path, mode = args[0], args[1]
            if isinstance(path, int):
                return
            text_mode = str(mode)
            writing = any(ch in text_mode for ch in 'wax+')
            if writing:
                if not _inside(str(path), write_roots):
                    raise PermissionError(
                        'Песочница: запись файлов разрешена только внутри '
                        'рабочей папки.')
            elif not _inside(str(path), read_roots):
                raise PermissionError(
                    'Песочница: чтение файлов вне рабочей папки запрещено.')
            return

        if event in NET_EVENTS:
            raise PermissionError('Песочница: сеть недоступна.')
        if event in PROCESS_EVENTS:
            raise PermissionError(
                'Песочница: запуск процессов и нативных вызовов запрещён.')
        if event == 'import':
            name = str(args[0] or '').split('.')[0]
            if name in BLOCKED_MODULES:
                raise ImportError(
                    'Песочница: модуль «%s» отключён.' % name)
            return
        if event == 'os.chdir':
            if not _inside(str(args[0]), read_roots):
                raise PermissionError('Песочница: смена каталога запрещена.')
            return
        if event in ('os.listdir', 'os.scandir'):
            if not _inside(str(args[0]), read_roots):
                raise PermissionError(
                    'Песочница: просмотр каталогов вне рабочей папки '
                    'запрещён.')
            return
        if event in FS_WRITE_EVENTS:
            if args and isinstance(args[0], str):
                # у shutil первый аргумент — исходный путь (только чтение)
                index = 1 if event.startswith('shutil.') else 0
                if len(args) > index and isinstance(args[index], str):
                    if not _inside(args[index], write_roots):
                        raise PermissionError(
                            'Песочница: изменение файлов вне рабочей папки '
                            'запрещено.')
            return
        if event == 'ctypes.dlopen' or event.startswith('winreg'):
            raise PermissionError('Песочница: доступ к системе запрещён.')

    sys.addaudithook(audit)


def main():
    if len(sys.argv) < 3:
        sys.stderr.write('sandbox bootstrap: нужны аргументы <файл> <папка>\n')
        return 2
    target = os.path.abspath(sys.argv[1])
    sandbox = os.path.abspath(sys.argv[2])
    os.chdir(sandbox)
    if sandbox not in sys.path:
        sys.path.insert(0, sandbox)
    install_hook(sandbox)
    try:
        runpy.run_path(target, run_name='__main__')
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        return code if isinstance(code, int) else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
