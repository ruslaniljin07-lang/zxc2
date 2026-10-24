"""Защита приложения: CSRF, ограничение частоты запросов, заголовки
безопасности (в том числе CSP с nonce), логирование событий и валидация
пользовательского ввода.

Модуль намеренно не тянет внешние зависимости (Flask-WTF, flask-limiter):
проект ставится из requirements.txt, а свои 250 строк прозрачнее и не
ломают существующие тесты.
"""

import logging
import os
import re
import secrets
import threading
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

from flask import (current_app, g, jsonify, render_template, request,
                   session)

# --- CSRF -----------------------------------------------------------------
SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS', 'TRACE')
CSRF_SESSION_KEY = '_csrf_token'
CSRF_FORM_FIELD = 'csrf_token'
CSRF_HEADER = 'X-CSRF-Token'
CSRF_EXEMPT_ENDPOINTS = set()

# --- ограничение частоты --------------------------------------------------
# имя правила -> (лимит запросов, окно в секундах, сообщение)
DEFAULT_LIMITS = {
    'login': (10, 300, 'Слишком много попыток входа. Подожди 5 минут.'),
    'register': (5, 3600, 'Слишком много регистраций с этого адреса. '
                          'Попробуй позже.'),
    'run_code': (40, 60, 'Слишком часто запускаешь код. Подожди минуту.'),
    'submit_solution': (60, 60, 'Слишком много отправок. Подожди минуту.'),
    'submit_test': (20, 300, 'Слишком много тестов подряд. Подожди 5 минут.'),
}

# --- валидация ввода ------------------------------------------------------
# Имя: буквы (латиница и кириллица), цифры, пробел, точка, дефис,
# подчёркивание. Ограничение по алфавиту нужно, чтобы в логин нельзя было
# подставить спецсимволы и HTML.
USERNAME_RE = re.compile(
    r'^[A-Za-zА-Яа-яЁё0-9_. -]{3,30}$')
EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]{1,63}'
                      r'(\.[A-Za-z0-9-]{1,63})+$')
MAX_EMAIL_LENGTH = 120
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
COMMON_PASSWORDS = {
    'password', 'password1', 'password123', '12345678', '123456789',
    '1234567890', 'qwerty123', 'qwertyui', 'iloveyou', 'admin123',
    'administrator', 'letmein1', 'welcome1', 'sunshine', 'princess',
    'football', 'monkey123', 'dragon123', 'baseball', 'superman',
    'qwerty12345', 'test1234', 'test12345', 'codigo123', 'student1',
    'changeme', '12345678901', 'qwerty1234', 'пароль123',
}


class RateLimiter:
    """Потокобезопасный лимитер по скользящему окну.

    Хранит время последних обращений по ключу; память ограничена
    периодической чисткой устаревших записей.
    """

    def __init__(self):
        self._hits = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.time()

    def check(self, key, limit, window):
        """True, если запрос разрешён; False при переборе лимита."""
        now = time.time()
        with self._lock:
            self._cleanup(now)
            hits = [t for t in self._hits.get(key, []) if now - t < window]
            if len(hits) >= limit:
                self._hits[key] = hits
                return False
            hits.append(now)
            self._hits[key] = hits
            return True

    def reset(self, key):
        with self._lock:
            self._hits.pop(key, None)

    def _cleanup(self, now):
        if now - self._last_cleanup < 300:
            return
        self._last_cleanup = now
        for key in list(self._hits):
            kept = [t for t in self._hits[key] if now - t < 3600]
            if kept:
                self._hits[key] = kept
            else:
                self._hits.pop(key, None)


rate_limiter = RateLimiter()



def client_ip():
    """IP клиента. X-Forwarded-For учитываем только для доверенного
    прокси (TRUST_PROXY=1): иначе заголовок легко подделать и обойти
    ограничение частоты."""
    if current_app.config.get('TRUST_PROXY'):
        forwarded = (request.headers.get('X-Forwarded-For') or '').split(',')
        if forwarded and forwarded[0].strip():
            return forwarded[0].strip()[:45]
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip.strip()[:45]
    return (request.remote_addr or 'unknown')[:45]


def wants_json():
    """Запрос из JS (fetch) или ожидает JSON — отвечаем JSON-ошибкой."""
    if request.is_json:
        return True
    if request.headers.get(CSRF_HEADER):
        return True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    accept = request.accept_mimetypes
    return accept['application/json'] > accept['text/html']


def error_response(code, message):
    """Единый ответ об ошибке: JSON для JS, страница для браузера."""
    if wants_json():
        return jsonify({'success': False, 'stdout': '', 'stderr': message,
                        'error': message}), code
    return render_template('error.html', code=code, message=message), code


# --- CSRF -----------------------------------------------------------------
def get_csrf_token():
    """Токен CSRF для текущей сессии (создаётся при первом обращении)."""
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def csrf_field():
    """Готовое скрытое поле для формы (в шаблоне: {{ csrf_field()|safe }})."""
    return ('<input type="hidden" name="' + CSRF_FORM_FIELD +
            '" value="' + get_csrf_token() + '">')


def _request_csrf_token():
    header = request.headers.get(CSRF_HEADER)
    if header:
        return header.strip()
    if request.is_json:
        payload = request.get_json(silent=True)
        if isinstance(payload, dict):
            value = payload.get(CSRF_FORM_FIELD) or payload.get(CSRF_HEADER)
            if value:
                return str(value)
        return ''
    return (request.form.get(CSRF_FORM_FIELD) or '').strip()


def csrf_active():
    """Нужно ли проверять токен для текущего запроса."""
    if not current_app.config.get('CSRF_ENABLED', True):
        return False
    if request.method in SAFE_METHODS:
        return False
    if request.endpoint in CSRF_EXEMPT_ENDPOINTS:
        return False
    if (current_app.config.get('TESTING') and
            not current_app.config.get('CSRF_STRICT_TESTING')):
        return False
    return True


def validate_csrf():
    """Сверяет токен запроса с токеном сессии (безопасное сравнение)."""
    expected = session.get(CSRF_SESSION_KEY)
    provided = _request_csrf_token()
    if not expected or not provided:
        return False
    return secrets.compare_digest(str(expected), str(provided))


# --- логирование ----------------------------------------------------------
_logger = None


def security_logger():
    """Лог событий безопасности в instance/security.log (ротация 512 КБ)."""
    global _logger
    if _logger is not None:
        return _logger
    logger = logging.getLogger('codigo.security')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers and current_app.config.get('SECURITY_LOG', True):
        try:
            folder = os.path.join(current_app.root_path, 'instance')
            os.makedirs(folder, exist_ok=True)
            handler = RotatingFileHandler(
                os.path.join(folder, 'security.log'), maxBytes=512 * 1024,
                backupCount=3, encoding='utf-8')
            handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s %(message)s'))
            logger.addHandler(handler)
        except OSError:
            handler = logging.NullHandler()
            logger.addHandler(handler)
    _logger = logger
    return logger


def log_event(event, **fields):
    """Пишет событие безопасности с IP и дополнительными полями."""
    try:
        ip = client_ip()
    except Exception:
        ip = 'n/a'
    if not current_app.config.get('SECURITY_LOG', True):
        return
    details = ' '.join(f'{k}={v!r}' for k, v in sorted(fields.items()))
    try:
        security_logger().info('event=%s ip=%s %s', event, ip, details)
    except Exception:
        pass


# --- заголовки безопасности ----------------------------------------------
CSP_CDN = 'https://cdn.jsdelivr.net'
CSP_FONTS = 'https://fonts.gstatic.com'
CSP_GOOGLE_FONTS = 'https://fonts.googleapis.com'


def build_csp_header(nonce):
    """Content-Security-Policy: скрипты только свои и с nonce.

    'strict-dynamic' означает, что внешние и inline-скрипты без nonce
    не выполняются вообще — это закрывает большую часть XSS.
    """
    return '; '.join([
        "default-src 'self'",
        "script-src 'nonce-" + nonce + "' 'strict-dynamic' 'self' " + CSP_CDN,
        "style-src 'self' 'unsafe-inline' " + CSP_CDN + ' ' + CSP_GOOGLE_FONTS,
        "font-src 'self' data: " + CSP_FONTS + ' ' + CSP_CDN,
        "img-src 'self' data:",
        "connect-src 'self'",
        "form-action 'self'",
        "base-uri 'self'",
        "object-src 'none'",
        "frame-ancestors 'none'",
    ])


def _before_request():
    g.csp_nonce = secrets.token_urlsafe(16)

    # абсолютное время жизни сессии, чтобы украденная кука не жила вечно
    lifetime = current_app.config.get('MAX_SESSION_LIFETIME')
    now = time.time()
    started = session.get('_started_at')
    if started is None:
        session['_started_at'] = now
    elif lifetime is not None and now - float(started) > lifetime.total_seconds():
        session.clear()
        session['_started_at'] = now
        log_event('session_expired')

    if csrf_active() and not validate_csrf():
        log_event('csrf_rejected', endpoint=request.endpoint,
                  method=request.method)
        return error_response(
            400, 'Запрос отклонён защитой от подделки (CSRF). '
                 'Обнови страницу и отправь форму снова.')
    return None


def _after_request(response):
    nonce = getattr(g, 'csp_nonce', '')
    response.headers['Content-Security-Policy'] = build_csp_header(nonce)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = (
        'geolocation=(), microphone=(), camera=(), payment=(), usb=()')
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
    if not request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'no-store'
    if current_app.config.get('SESSION_COOKIE_SECURE'):
        response.headers['Strict-Transport-Security'] = \
            'max-age=31536000; includeSubDomains'
    return response

    provided = _request_csrf_token()
    if not expected or not provided:
        return False


# --- ограничение частоты: декоратор --------------------------------------
def rate_limit(rule, limit=None, window=None, message=None, by_user=True):
    """Ограничивает частоту вызовов представления.

    Ключ — IP клиента и (для авторизованных) id пользователя, поэтому
    обойти лимит сменой сессии не получится.
    """
    from functools import wraps
    from flask_login import current_user

    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not current_app.config.get('RATE_LIMIT_ENABLED', True):
                return view(*args, **kwargs)
            # Лимитируем только небезопасные методы (POST/PUT/DELETE и т.д.),
            # чтобы просмотр страниц (GET) не расходовал квоту отправок.
            if request.method in SAFE_METHODS:
                return view(*args, **kwargs)
            max_hits, window_s, text = DEFAULT_LIMITS.get(
                rule, (limit or 60, window or 60,
                       'Слишком много запросов. Попробуй позже.'))
            keys = ['%s:ip:%s' % (rule, client_ip())]
            if by_user and current_user.is_authenticated:
                keys.append('%s:user:%s' % (rule, current_user.id))
            for key in keys:
                if not rate_limiter.check(key, max_hits, window_s):
                    log_event('rate_limit', rule=rule, key=key)
                    return error_response(429, message or text)
            return view(*args, **kwargs)
        return wrapper
    return decorator


def is_rate_limited(rule, extra_key=None, limit=None, window=None):
    """Ручная проверка лимита (например, по введённому логину)."""
    if not current_app.config.get('RATE_LIMIT_ENABLED', True):
        return False
    max_hits, window_s, _ = DEFAULT_LIMITS.get(
        rule, (limit or 60, window or 60, ''))
    keys = ['%s:ip:%s' % (rule, client_ip())]
    if extra_key:
        keys.append('%s:name:%s' % (rule, extra_key[:60].lower()))
    return any(not rate_limiter.check(key, max_hits, window_s) for key in keys)


# --- обработчики ошибок ---------------------------------------------------
ERROR_TEXTS = {
    400: 'Запрос отклонён.',
    403: 'Доступ запрещён.',
    404: 'Страница не найдена.',
    405: 'Этот метод запроса не поддерживается.',
    413: 'Слишком большой запрос.',
    429: 'Слишком много запросов.',
    500: 'Внутренняя ошибка сервера.',
}


def _error_handler(code):
    def handler(exc):
        if code == 500:
            log_event('server_error', path=request.path,
                      error=type(exc).__name__)
        description = getattr(exc, 'description', None)
        message = ERROR_TEXTS.get(code, 'Ошибка.')
        if request.path.startswith('/static/'):
            return message, code
        if code == 500 and description and current_app.debug:
            message = str(description)
        return error_response(code, message)
    return handler


# --- валидация пользовательского ввода -----------------------------------
def normalize_username(value):
    """Приводит имя пользователя к единому виду: без лишних пробелов.

    Регистрация и вход используют одну и ту же функцию, иначе «Иван  Петров»
    и «Иван Петров» считались бы разными аккаунтами.
    """
    return ' '.join((value or '').split())


def validate_username(value):
    """Логин: 3-30 символов, буквы (любого языка), цифры, точка, дефис,
    подчёркивание и одиночные пробелы внутри имени."""
    if not value:
        return False, 'Введите имя пользователя.'
    value = ' '.join(value.split())
    if not USERNAME_RE.match(value):
        return False, ('Имя: 3-30 символов, буквы, цифры, точка, дефис, '
                       'подчёркивание или пробел между словами.')
    return True, ''


def validate_email(value):
    if not value:
        return False, 'Введите электронную почту.'
    if len(value) > MAX_EMAIL_LENGTH or not EMAIL_RE.match(value):
        return False, 'Похоже, это не корректный адрес почты.'
    return True, ''


def validate_password(value, username='', email=''):
    """Пароль: 8-128 символов, буква и цифра/спецсимвол, не из слива."""
    if not value or len(value) < MIN_PASSWORD_LENGTH:
        return False, ('Пароль должен быть не короче %d символов.'
                       % MIN_PASSWORD_LENGTH)
    if len(value) > MAX_PASSWORD_LENGTH:
        return False, 'Пароль слишком длинный (максимум 128 символов).'
    lowered = value.lower()
    if lowered in COMMON_PASSWORDS:
        return False, 'Такой пароль слишком часто взламывают. Выбери другой.'
    if lowered in (username.lower(), email.lower()):
        return False, 'Пароль не должен совпадать с логином или почтой.'
    if not re.search(r'[A-Za-zА-Яа-я]', value) or \
            not re.search(r'[0-9\W_]', value):
        return False, 'Добавь в пароль хотя бы одну цифру или символ.'
    if len(set(value)) < 4:
        return False, 'Пароль слишком простой: используй разные символы.'
    return True, ''


def clean_code(value, limit=None):
    """Нормализует код из формы/JSON: строка, без NUL, с ограничением."""
    if not isinstance(value, str):
        return ''
    limit = limit or current_app.config.get('MAX_CODE_LENGTH', 20000)
    cleaned = value.replace('\x00', '')
    return cleaned[:limit]


def init_security(app):
    """Подключает все защиты к приложению Flask."""
    app.config.setdefault('TRUST_PROXY', False)
    app.jinja_env.globals['csrf_token'] = get_csrf_token
    app.jinja_env.globals['csrf_field'] = csrf_field
    app.jinja_env.globals['csp_nonce'] = lambda: getattr(g, 'csp_nonce', '')
    app.before_request(_before_request)
    app.after_request(_after_request)
    for code in (400, 403, 404, 405, 413, 429, 500):
        app.register_error_handler(code, _error_handler(code))
    return app

    return secrets.compare_digest(str(expected), str(provided))
