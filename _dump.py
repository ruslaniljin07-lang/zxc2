import sys
sys.path.insert(0, '.')
from app import app, db
from models import User, TestResult, LessonProgress
import uuid

app.config['WTF_CSRF_ENABLED'] = False

with app.app_context():
    # удалить тестового пользователя
    u = User.query.filter_by(username='testuser').first()
    if u:
        db.session.delete(u)
        db.session.commit()

client = app.test_client()

# 1. Регистрация
r = client.post('/register', data={
    'username': 'testuser', 'email': 't@t.ru',
    'password': 'pass123', 'confirm': 'pass123'
})
print('1. register:', r.status_code, r.headers.get('Location'))

# логин
r = client.post('/login', data={'username': 'testuser', 'password': 'pass123'},
                follow_redirects=True)
print('2. login:', r.status_code, 'Дашборд' in r.get_data(as_text=True))

# 3. Страница курса Python
r = client.get('/language/python')
print('3. course python:', r.status_code, 'Основы Python' in r.get_data(as_text=True))

# 4. Входной тест python (правильные ответы)
questions = [0, 1, 2, 1, 0, 1, 3, 0]  # correct indexes
data = {f'q{i+1}': str(a) for i, a in enumerate(questions)}
r = client.post('/test/python', data=data, follow_redirects=True)
print('4. test python:', r.status_code, 'Тест пройден' in r.get_data(as_text=True))

# 5. Урок 1 python
r = client.get('/lesson/1')
body = r.get_data(as_text=True)
print('5. lesson 1:', r.status_code, 'Первая программа' in body)

# 6. Проверка кода python (правильное решение)
r = client.post('/lesson/1', data={'code': "print('Привет, мир!')"})
j = r.get_json()
print('6. check python:', r.status_code, j.get('success') if j else 'ERR')

# 7. Тест javascript
r = client.get('/test/javascript')
print('7. test JS page:', r.status_code, 'JavaScript' in r.get_data(as_text=True))

# 8. Курс java
r = client.get('/language/java')
body = r.get_data(as_text=True)
print('8. course java:', r.status_code, 'Java' in body)

# 9. Проверка кода JS (contains check)
client.get('/language/javascript')
r = client.post('/lesson/1', data={'code': "console.log('Привет, мир!');"})
j = r.get_json()
print('9. check JS:', r.status_code, j.get('success') if j else 'ERR')

print('DONE')