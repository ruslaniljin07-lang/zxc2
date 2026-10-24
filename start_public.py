import os
import sys
import socket
import subprocess
from pyngrok import ngrok

# Настройки
PORT = 5000

def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def main():
    print("\n" + "="*50)
    print("  Código - Запуск с публичным доступом")
    print("="*50)
    
    # Создаём ngrok туннель
    print("\n🔄 Создаю публичный туннель...")
    public_url = ngrok.connect(PORT, "http")
    
    print(f"\n{'='*50}")
    print(f"  🌐 САЙТ ДОСТУПЕН ПО АДРЕСУ:")
    print(f"  {public_url}")
    print(f"{'='*50}")
    print(f"\n  Локально: http://127.0.0.1:{PORT}")
    print(f"  В сети:   http://{get_local_ip()}:{PORT}")
    print(f"\n  Для остановки нажмите Ctrl+C")
    print(f"\n  ⚠  Через туннель сайт видно всему интернету. Включи HTTPS")
    print(f"     (ngrok даёт его сам) и запусти сервер с COOKIE_SECURE=1,")
    print(f"     иначе сессию можно перехватить. Лучше сначала проверь локально.")
    print(f"{'='*50}\n")

    # Запускаем Flask
    # os.system(f"...") заменён на subprocess: строка с командой не
    # разбирается оболочкой, и в неё нельзя случайно подставить путь.
    env = dict(os.environ)
    env.setdefault('COOKIE_SECURE', '1')  # туннель отдаёт HTTPS
    subprocess.run([sys.executable, 'app.py'], env=env)

if __name__ == "__main__":
    main()
