# Детское кафе
Веб-сайт детского кафе на Django: меню, отзывы, аренда зала, вакансии и админ-панель со статистикой.
##  Возможности

-  **Каталог меню** — блюда с фото, категориями и детальной страницей
-  **Комментарии** — пользователи могут оставлять отзывы к блюдам
-  **Обратная связь** — форма обратной связи + список отзывов
-  **Аренда зала** — заявка на проведение мероприятия
-  **Вакансии** — список вакансий и форма отклика
-  **Регистрация и профиль** — вход, регистрация, личный кабинет
-  **Админ-статистика** — популярные блюда, негативные отзывы, общая статистика
#  Стек

- Python 3.11
- Django 5.2
- SQLite (по умолчанию)
- HTML / CSS (шаблоны Django)
- Pillow (для изображений)

## Структура проекта

| Путь | Назначение |
|---|---|
| `cafe_project/` | Конфигурация Django-проекта (`settings.py`, `urls.py`, `wsgi.py`) |
| `kids_cafe/` | Основное приложение: модели, вьюхи, формы, админка |
| `kids_cafe/migrations/` | Миграции БД (5 штук: от `initial` до `feedback`) |
| `kids_cafe/templatetags/` | Кастомные фильтры для шаблонов (`base64`, `custom_filters`) |
| `templates/` | HTML-шаблоны: `base.html`, страницы сайта, регистрация, админка |
| `templates/kids_cafe/` | Страницы пользовательской части (главная, каталог, аренда, вакансии) |
| `templates/registration/` | `login.html`, `register.html`, `profile.html` |
| `templates/admin/` | Кастомные страницы статистики в админке |
| `media/` | Загружаемые пользователем файлы (фото меню) |
| `static_dev/` | Статика для разработки (логотип, favicon, картинки) |
| `manage.py` | Управляющий скрипт Django |
| `requirements.txt` | Список Python-зависимостей |

## Модели данных

| Модель | Назначение | Ключевые поля |
|---|---|---|
| `Product` | Блюдо из меню | `name`, `description`, `price`, `image`, `category` |
| `ItemComment` | Комментарий пользователя к блюду | `item`, `user`, `text`, `created_at` |
| `Feedback` | Отзыв / обращение через форму обратной связи | `user`, `text`, `rating`, `created_at` |
| `HallRental` | Заявка на аренду зала | `user`, `date`, `contact`, `comment` |
| `JobApplication` | Отклик на вакансию | `user`, `position`, `resume`, `created_at` |
| `UserProfile` | Дополнительная информация о пользователе | `user`, `phone`, `avatar`, `birth_date` |

### Связи между моделями

```
User ──1:1── UserProfile
User ──1:N── ItemComment ──N:1── Product
User ──1:N── Feedback
User ──1:N── HallRental
User ──1:N── JobApplication
```

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Banan41k78/children_cafe.git
cd children_cafe
```

### 2. Создать виртуальное окружение

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```
Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Применить миграции

```bash
python manage.py migrate
```

### 5. Создать суперпользователя (для доступа в админку)

```bash
python manage.py createsuperuser
```

### 6. Запустить сервер

```bash
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

Админ панель: http://127.0.0.1:8000/admin/

