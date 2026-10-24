import subprocess
import sys
import os
import time

def main():
    print("\n" + "="*60)
    print("  Código - Запуск сервера")
    print("="*60)
    
    # Запускаем Flask
    print("\n[1/2] Запускаю Flask сервер...")
    # ВАЖНО: app.py по умолчанию стартует без отладочной консоли Werkzeug
    # и слушает только 127.0.0.1. Отладочная консоль — это удалённый
    # доступ к выполнению кода, её нельзя выставлять в интернет.
    flask_process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(3)

    print("[2/2] Создаю публичный туннель...")
    print("\n" + "="*60)
    print("  ИНСТРУКЦИЯ:")
    print("  1. Подождите 10-15 секунд")
    print("  2. В этом окне появится адрес сайта")
    print("  3. Отправьте его друзьям")
    print("  4. Для остановки нажмите Ctrl+C")
    print("")
    print("  БЕЗОПАСНОСТЬ: сайт будет доступен любому, кто знает адрес.")
    print("  Не публикуй туннель, пока не поднимешь HTTPS и COOKIE_SECURE=1,")
    print("  иначе пароль можно перехватить. Лучше сначала попробуй локально.")
    print("="*60 + "\n")
    
    # Запускаем localtunnel
    try:
        lt_process = subprocess.Popen(
            ["C:\\Users\\rusla\\AppData\\Roaming\\npm\\lt.cmd", "--port", "5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Читаем вывод и ищем адрес
        for line in lt_process.stdout:
            print(line, end="")
            if "loca.lt" in line:
                print("\n" + "="*60)
                print(f"  АДРЕС САЙТА: {line.strip()}")
                print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nОстанавливаю сервер...")
    finally:
        flask_process.terminate()
        lt_process.terminate()

if __name__ == "__main__":
    main()
