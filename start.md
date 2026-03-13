📁 СОЗДАНИЕ ПРОЕКТА DJANGO
1. Подготовка окружения:
bash
# Создать папку для проекта
mkdir myproject
cd myproject

# Создать виртуальное окружение
python -m venv .venv

# Активировать виртуальное окружение (Windows)
.venv\Scripts\activate

# Активировать (Mac/Linux)
# source .venv/bin/activate

# Установить Django
pip install django
2. Создать проект Django:
bash
# Создать новый проект Django
django-admin startproject core .

# Создать приложения
python manage.py startapp users
python manage.py startapp tasks
3. Настройки проекта (core/settings.py):
python
"""
Django settings for core project.
"""

from pathlib import Path
import os

# Базовый путь
BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность
SECRET_KEY
стоп пиши в однов фаеле что бы я скапировал один раз
🚀 ПОЛНЫЙ ГАЙД DJANGO + GIT: ВСЕ КОМАНДЫ ОТ НАЧАЛА ДО КОНЦА
📁 1. СОЗДАНИЕ ПРОЕКТА
Настройка окружения:
bash
# 1. Создать папку проекта
mkdir myproject
cd myproject

# 2. Создать виртуальное окружение
python -m venv .venv

# Создания суперплользвателья 
python manage.py createsuperuser

# 3. Активировать виртуальное окружение
# Windows:
.venv\Scripts\activate
# Mac/Linux:
# source .venv/bin/activate

# 4. Установить Django
pip install django
Создание проекта Django:
bash
# 5. Создать проект Django
django-admin startproject core .

# 6. Создать приложения
python manage.py startapp users
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),    
    path('planner/', include('tasks.urls')),
    path('projects/', include('projects.urls')),
    path('assignments/', include('assignments.urls')),
    path('users/', include('users.urls')),
] tasks
⚙️ 2. НАСТРОЙКА ПРОЕКТА
Файл core/settings.py:
python
# Основные настройки Django
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-твой-секретный-ключ'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',    # ваше приложение
    'tasks',    # ваше приложение
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
Файл core/urls.py:
python
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('users/', include('users.urls')),
    path('tasks/', include('tasks.urls')),
]
Файл core/views.py:
python
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')
📦 3. СОЗДАНИЕ МОДЕЛЕЙ
Файл tasks/models.py:
python
from django.db import models
from django.contrib.auth.models import User

class Tasks(models.Model):
    PRIORITY_CHOICES = [
        ('ordinary', 'Обычный'),
        ('average', 'Средний'),
        ('urgent', 'Срочный'),
    ]
    
    title = models.CharField(max_length=50, verbose_name='Название задачи')
    description = models.TextField(max_length=500, verbose_name='Описание задачи')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='ordinary', verbose_name='Приоритет')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    deadline = models.DateTimeField(verbose_name='Дедлайн')
    is_completed = models.BooleanField(default=False, verbose_name='Выполнено')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

Файл users/models.py:
python
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True)
    
    def __str__(self):
        return f"{self.user.username}"
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
🔄 4. МИГРАЦИИ И АДМИНКА
Команды для базы данных:
bash
# Создать миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser
Файл tasks/admin.py:
python
from django.contrib import admin
from .models import Tasks

@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'deadline', 'is_completed']
    list_filter = ['priority', 'is_completed']
Файл users/admin.py:
python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
🎨 5. ШАБЛОНЫ И СТАТИКА
Структура папок:
bash
# Создать папки для шаблонов и статики
mkdir templates
mkdir static
mkdir static/css

# Создать базовый шаблон
# templates/base.html
# templates/home.html
# static/css/style.css
Пример templates/base.html:
html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Мой проект{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header>Навигация</header>
    <main>{% block content %}{% endblock %}</main>
    <footer>Подвал</footer>
</body>
</html>
🚀 6. РАБОТА С GITHUB
Подготовка к GitHub:
bash
# Создать файл .gitignore
echo ".venv/" > .gitignore
echo "db.sqlite3" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# Создать requirements.txt
pip freeze > requirements.txt
Загрузка на GitHub:
bash
# 1. Инициализировать Git
git init

# 2. Добавить все файлы
git add .

# 3. Создать первый коммит
git commit -m "Initial commit: Django project"

# 4. Привязать к GitHub (ССЫЛКУ БЕРИ С СВОЕГО GITHUB)
git remote add origin https://github.com/ВАШ_ЛОГИН/НАЗВАНИЕ.git

# 5. Переименовать ветку если нужно
git branch -M main

# 6. Отправить на GitHub
git push -u origin main
💻 7. РАБОТА С ДВУХ КОМПЬЮТЕРОВ
На втором компьютере:
bash
# 1. Клонировать проект
git clone https://github.com/ВАШ_ЛОГИН/НАЗВАНИЕ.git

# 2. Перейти в папку
cd НАЗВАНИЕ

# 3. Создать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Применить миграции
python manage.py migrate

# 6. Запустить сервер
python manage.py runserver
🔄 8. ЕЖЕДНЕВНЫЕ КОМАНДЫ
Перед работой:
bash
# Получить свежие изменения
git pull origin main

# Запустить сервер для проверки
python manage.py runserver
После изменений:
bash
# 1. Добавить изменения
git add .

# 2. Сохранить локально
git commit -m "Описание изменений"

# 3. Отправить на GitHub
git push origin main
🔧 9. ПОЛЕЗНЫЕ КОМАНДЫ
Для проекта Django:
bash
# Проверить проект на ошибки
python manage.py check

# Создать миграции для конкретного приложения
python manage.py makemigrations tasks

# Запустить Python shell с Django
python manage.py shell

# Создать статические файлы для продакшена
python manage.py collectstatic
Для Git:
bash
# Показать историю коммитов
git log --oneline

# Показать изменения
git diff

# Показать статус
git status

# Отменить последний коммит (сохранив изменения)
git reset --soft HEAD~1

# Вернуть файл к последнему коммиту
git checkout -- имя_файла.py
⚠️ 10. РЕШЕНИЕ ПРОБЛЕМ
Если Git не пушится:
bash
# Сначала получить изменения
git pull origin main --allow-unrelated-histories

# Затем отправить
git push origin main
Если конфликт слияния:
bash
# Решить конфликты вручную в файлах
# Затем:
git add .
git commit -m "Resolved conflicts"
git push origin main
Если забыл пароль от GitHub:
bash
# Использовать токен как пароль
# Или настроить SSH ключи:
ssh-keygen -t rsa -b 4096
# Добавить ключ на GitHub: Settings → SSH and GPG keys
# Клонировать через SSH: git clone git@github.com:...
✅ 11. БЫСТРАЯ ШПАРГАЛКА
bash
# НОВЫЙ ПРОЕКТ:
mkdir project && cd project
python -m venv .venv && .venv\Scripts\activate
pip install django
django-admin startproject core .
python manage.py startapp myapp
python manage.py runserver

# GITHUB:
echo ".venv/" > .gitignore
pip freeze > requirements.txt
git init && git add . && git commit -m "First"
git remote add origin https://github.com/...
git push -u origin main

# ЕЖЕДНЕВНО:
git pull origin main
# работа...
git add . && git commit -m "Update" && git push origin main
🎯 ВАЖНЫЕ ФАЙЛЫ, КОТОРЫЕ НУЖНО СОЗДАТЬ:
.gitignore - игнорируемые файлы

requirements.txt - зависимости Python

templates/base.html - базовый шаблон

templates/home.html - главная страница

static/css/style.css - стили

Приложения: urls.py, views.py, forms.py в каждой папке