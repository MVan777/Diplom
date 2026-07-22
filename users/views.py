from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from datetime import timedelta
from .forms import FeedBackForm, RegisterForm, UserUpdateForm, ProfileUpdateForm
from tasks.models import Task


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    email=form.cleaned_data['email'] or '',
                )

                if form.cleaned_data.get('phone'):
                    user.profile.phone = form.cleaned_data['phone']
                    user.profile.save()

                login(request, user)
                messages.success(request, f'Регистрация успешна! Добро пожаловать, {user.username}')
                return redirect('tasks:planner')

            except IntegrityError:
                messages.error(request, "Пользователь с такими данными уже существует")
            except ValidationError as e:
                messages.error(request, f"Ошибка валидации данных: {e}")
            except Exception as e:
                messages.error(request, f"Ошибка при регистрации: {str(e)}")

    else:
        form = RegisterForm()

    return render(request, 'users/signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Заполните все поля")
            return render(request, 'users/signin.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}')

            return redirect('tasks:planner')
        else:
            messages.error(request, "Неверный логин или пароль")

    return render(request, 'users/signin.html')


def forgot_password(request):
    return render(request, 'users/recovery.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('home')


@login_required
def user_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:user_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    try:
        tasks_count = Task.objects.filter(user=request.user).count()
        completed_tasks = Task.objects.filter(
            user=request.user,
            is_completed=True
        ).count()
    except Exception:
        tasks_count = 0
        completed_tasks = 0

    context = {
        'user': request.user,
        'profile': request.user.profile,
        'user_form': user_form,
        'profile_form': profile_form,
        'tasks_count': tasks_count,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': tasks_count - completed_tasks,
    }

    return render(request, 'users/user_profile.html', context)

def feedback(request):
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('home')
    else:
        form = FeedBackForm()
    return render(request, "users/feedback.html", {'form': form})


def contact(request):
    return render(request, 'users/contact.html')