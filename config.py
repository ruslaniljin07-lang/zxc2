import os
import secrets
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')


def env_flag(name, default=False):
    """Читает булев флаг из окружения: SECRET=1/true/yes/on."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == '':
        return default
    return raw.strip().lower() in ('1', 'true', 'yes', 'on')


def _load_secret_key():
    """Ключ подписи сессий.

    Порядок: SECRET_KEY из окружения -> файл instance/secret.key ->
    новый случайный ключ (сохраняется в файл, чтобы сессии не слетали
    при перезапуске и чтобы ключ не был предсказуемым).
    """
    env_key = (os.environ.get('SECRET_KEY') or '').strip()
    if len(env_key) >= 16:
        return env_key

    os.makedirs(INSTANCE_DIR, exist_ok=True)
    path = os.path.join(INSTANCE_DIR, 'secret.key')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            key = f.read().strip()
        if len(key) >= 32:
            return key
    except OSError:
        pass

    key = secrets.token_hex(32)
    try:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(key)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    except OSError:
        pass
    return key


def _database_uri():
    uri = os.environ.get('DATABASE_URL', 'sqlite:///codigo.db')
    return uri


class Config:
    # --- секреты и сессии ------------------------------------------------
    SECRET_KEY = _load_secret_key()
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Включается (COOKIE_SECURE=1), когда сайт отдаётся по HTTPS —
    # например через ngrok/localtunnel, чтобы куку нельзя было снять с HTTP.
    SESSION_COOKIE_SECURE = env_flag('COOKIE_SECURE', False)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    SESSION_REFRESH_EACH_REQUEST = True
    # Максимум 8 часов абсолютного времени жизни сессии
    MAX_SESSION_LIFETIME = timedelta(hours=8)

    # --- база данных -----------------------------------------------------
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    if SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'connect_args': {'timeout': 15, 'check_same_thread': False},
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 1800,
        }

    # --- ограничение запросов -------------------------------------------
    # Ни один запрос (включая JSON песочницы) не может быть огромным:
    # защита от «залить гигабайт в POST и положить сервер».
    MAX_CONTENT_LENGTH = 512 * 1024
    MAX_FORM_MEMORY_SIZE = 512 * 1024
    MAX_FORM_PARTS = 50
    # Код для песочницы/задач не длиннее 20 000 символов (проверяется в app)
    MAX_CODE_LENGTH = 20000

    # --- защита форм и API ----------------------------------------------
    CSRF_ENABLED = not env_flag('CSRF_DISABLED', False)
    RATE_LIMIT_ENABLED = not env_flag('RATE_LIMIT_DISABLED', False)
    SECURITY_LOG = env_flag('SECURITY_LOG', True)

    # --- сервер ----------------------------------------------------------
    # debug выключен по умолчанию: отладочная консоль Werkzeug = RCE
    DEBUG = env_flag('FLASK_DEBUG', False)
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', '5000'))
