Веб-приложение для управления учебным процессом с функциями администрирования, учительскими и ученическими модулями.

## 📌 Основные возможности
- **Административная панель**:
  - Управление пользователями (учителя, ученики, администраторы)
  - Создание и управление классами
  - Обработка обратной связи
- **Учительский модуль**:
  - Просмотр своих классов
  - Управление учениками
- **Ученический модуль**:
  - Доступ к учебным материалам

## 🚀 Установка и запуск
1. **Клонирование репозитория**:
   ```bash
   git clone https://github.com/Dinara317/math_learning_platform.git
   cd math_learning_platform
   ```
2. **Настройка окружения**:
   - Создайте файл `.env` на основе `.env.example`
   - Укажите свои настройки базы данных и почты
   - Создайте виртуальное окружение:
  ```bash
   python3 -m venv venv
   ```
   - Активируйте его:
  ```bash
   source venv/Scripts/activate
   ```
3. **Установка зависимостей**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Запуск приложения**:
   ```bash
   flask run.py
   ```

## ⚙️ Конфигурация
Основные настройки в `.env` файле:
```ini
# Flask
FLASK_APP=app
FLASK_ENV=development

# Безопасность
SECRET_KEY=ваш-secret-key

DATABASE_URL=sqlite:///math_platform.db

# Почтовый сервер (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=ваш-email@gmail.com
MAIL_PASSWORD=ваш-пароль
MAIL_DEFAULT_SENDER=ваш-email@gmail.com # Должен совпадать с MAIL_USERNAME
```

## 🧑‍💻 Технологии
- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Mail, Flask-Migrate
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **База данных**: SQLite (можно настроить PostgreSQL)

## 📂 Структура проекта
```
math_learning_platform/
├── app/
│   ├── templates/     # Шаблоны HTML
│   ├── static/        # CSS, JS, изображения
│   ├── models.py      # Модели базы данных
│   ├── auth.py        # Авторизация/регистрация
│   ├── admin.py       # Функционал администратора
│   ├── teacher.py     # Функционал учителя
│   ├── student.py     # Функционал обучающихся
│   ├── utils.py       # Общие утилиты
│   └── __init__.py    # Инициализация приложения
├── migrations/        # Миграции базы данных
├── run.py             # Точка входа
├── config.py          # Конфигурация 
├── requirements.txt   # Зависимости
├── .env               # Конфигурация
└── .env.example       # Пример конфигурации
```

## 🤝 Как помочь проекту
1. Форкните репозиторий
2. Создайте ветку для вашей фичи (`git checkout -b feature/amazing-feature`)
3. Сделайте коммит изменений (`git commit -m 'Add some amazing feature'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

> 🌐 **Демо**: http://45.11.26.87/
