from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta
import calendar

from .forms import TaskForm, TaskFilterForm
from .task_service import TaskStatsService, TaskQueryService, TaskCRUDService
from .models import Task
from comments.models import Comment
from projects.models import Project
from assignments.models import TaskAssignment
from django.contrib.auth.models import User


@login_required
def planner(request):
    user = request.user

    # Проекты пользователя
    active_projects = Project.objects.filter(
        Q(owner=user) | Q(members=user)
    ).distinct().annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__is_completed=True))
    ).order_by('-updated_at')

    # Данные для календаря
    now = timezone.now()
    calendar_data = get_calendar_data(user, now.year, now.month)

    # Данные для статистики
    stats_data = get_task_stats_data(user)

    context = {
        # Существующие данные
        'profile': request.user.profile,
        'stats': TaskStatsService.get_user_stats(user),
        'urgent_tasks': TaskQueryService.get_priority_tasks(user, Task.URGENT),
        'medium_tasks': TaskQueryService.get_priority_tasks(user, Task.AVERAGE),
        'low_tasks': TaskQueryService.get_priority_tasks(user, Task.ORDINARY),
        'active_projects': active_projects,
        'all_projects': active_projects,
        # Данные для календаря
        'current_month': now.strftime('%B %Y'),
        'calendar_days': calendar_data['days'],
        # Данные для диаграммы
        'total_tasks': stats_data['total'],
        'completed_percent': stats_data['completed_percent'],
        'overdue_percent': stats_data['overdue_percent'],
        'pending_percent': stats_data['pending_percent'],
        'completed_deg': stats_data['completed_deg'],
        'overdue_deg': stats_data['overdue_deg'],
        'avg_completion_time': stats_data['avg_completion_time'],
        'productivity': stats_data['productivity'],
    }
    return render(request, 'planner/planner.html', context)


def project_planner(request, project_id):
    user = request.user

    project = get_object_or_404(Project, id=project_id)

    # Проверяем доступ (владелец или участник)
    if user != project.owner and user not in project.members.all():
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("У вас нет доступа к этому проекту")

    all_project_tasks = project.project_tasks.all()

    # Фильтруем по приоритетам
    urgent_tasks = all_project_tasks.filter(priority='urgent', is_completed=False)
    medium_tasks = all_project_tasks.filter(priority='average', is_completed=False)
    low_tasks = all_project_tasks.filter(priority='ordinary', is_completed=False)

    # Проекты для выпадающего списка
    active_projects = Project.objects.filter(
        Q(owner=user) | Q(members=user)
    ).distinct().annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__is_completed=True))
    ).order_by('-updated_at')

    # Данные для календаря (только задачи проекта)
    now = timezone.now()
    calendar_data = get_calendar_data(user, now.year, now.month, project_id=project_id)

    # Данные для статистики (только для проекта)
    stats_data = get_task_stats_data(user, project_id=project_id)

    context = {
        'current_project': project,
        'urgent_tasks': urgent_tasks,
        'medium_tasks': medium_tasks,
        'low_tasks': low_tasks,
        'active_projects': active_projects,
        'all_projects': active_projects,
        'current_month': now.strftime('%B %Y'),
        'calendar_days': calendar_data['days'],
        'total_tasks': stats_data['total'],
        'completed_percent': stats_data['completed_percent'],
        'overdue_percent': stats_data['overdue_percent'],
        'pending_percent': stats_data['pending_percent'],
        'completed_deg': stats_data['completed_deg'],
        'overdue_deg': stats_data['overdue_deg'],
        'avg_completion_time': stats_data['avg_completion_time'],
        'productivity': stats_data['productivity'],
    }
    return render(request, 'planner/project_planner.html', context)


def get_calendar_data(user, year, month, project_id=None):
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])

    month_tasks = Task.objects.filter(
        Q(user=user) | Q(assignments__user=user),
        deadline__date__gte=first_day,
        deadline__date__lte=last_day
    ).distinct()

    if project_id:
        month_tasks = month_tasks.filter(project_id=project_id)

    task_dates = set(month_tasks.values_list('deadline__date', flat=True))

    days = []
    for day in range(1, last_day.day + 1):
        date = datetime(year, month, day).date()
        days.append({
            'day': day,
            'date': date,
            'has_tasks': date in task_dates,
            'tasks_count': month_tasks.filter(deadline__date=date).count(),
            'is_today': date == timezone.now().date()
        })

    return {'days': days}


def get_task_stats_data(user, project_id=None):
    now = timezone.now()

    # Учитываем и авторские, и назначенные задачи
    tasks = Task.objects.filter(
        Q(user=user) | Q(assignments__user=user)
    ).distinct()

    if project_id:
        tasks = tasks.filter(project_id=project_id)

    total = tasks.count()
    completed = tasks.filter(is_completed=True).count()
    overdue = tasks.filter(is_completed=False, deadline__lt=now).count()
    pending = total - completed - overdue

    # Проценты и градусы
    if total > 0:
        completed_percent = round((completed / total) * 100)
        overdue_percent = round((overdue / total) * 100)
        pending_percent = 100 - completed_percent - overdue_percent
        completed_deg = (completed / total) * 360
        overdue_deg = ((completed + overdue) / total) * 360
        productivity = round((completed / total) * 100)
    else:
        completed_percent = overdue_percent = pending_percent = 0
        completed_deg = overdue_deg = 0
        productivity = 0

    # Среднее время выполнения
    completed_tasks = tasks.filter(is_completed=True, completed_at__isnull=False)
    if completed_tasks.exists():
        total_days = sum((t.completed_at - t.created_at).days for t in completed_tasks)
        avg_days = round(total_days / completed_tasks.count(), 1)
        avg_completion_time = f"{avg_days} дн."
    else:
        avg_completion_time = "Нет данных"

    return {
        'total': total,
        'completed': completed,
        'overdue': overdue,
        'pending': pending,
        'completed_percent': completed_percent,
        'overdue_percent': overdue_percent,
        'pending_percent': pending_percent,
        'completed_deg': completed_deg,
        'overdue_deg': overdue_deg,
        'productivity': productivity,
        'avg_completion_time': avg_completion_time,
    }

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'planner/task_list.html', {'tasks': tasks})


@login_required
def create_task(request):
    user = request.user
    project_id = request.GET.get('project') or request.POST.get('project')  # Добавляем получение из POST
    selected_project = validate_project_access(user, project_id) if project_id else None

    if request.method == 'POST':
        if request.POST.getlist('titles[]'):
            response = handle_multiple_tasks(request, user)
        else:
            response = handle_single_task(request, user)

        if project_id:
            return redirect('projects:detail', project_id=project_id)

        return response

    initial_data = {}
    if selected_project:
        initial_data['project'] = selected_project.id
    if 'priority' in request.GET:
        initial_data['priority'] = request.GET.get('priority')
    if 'deadline' in request.GET:
        initial_data['deadline'] = request.GET.get('deadline')

    form = TaskForm(user=user, initial=initial_data)
    return render(request, 'planner/create_task.html', {
        'form': form,
        'selected_project': selected_project
    })


def validate_project_access(user, project_id):
    try:
        project = Project.objects.get(id=project_id)
        if project.owner == user or user in project.members.all():
            return project
    except Project.DoesNotExist:
        pass
    return None


def handle_multiple_tasks(request, user):
    titles = request.POST.getlist('titles[]')
    deadlines = request.POST.getlist('deadlines[]')
    priorities = request.POST.getlist('priorities[]')

    project_id = request.GET.get('project')
    selected_project = validate_project_access(user, project_id) if project_id else None

    created_count = 0
    errors = []

    for i, (title, deadline, priority) in enumerate(zip(titles, deadlines, priorities)):
        if not title.strip():
            errors.append(f"Задача #{i + 1}: название не может быть пустым")
            continue

        try:
            deadline_aware = parse_datetime(deadline)
            Task.objects.create(
                user=user,
                title=title.strip(),
                priority=priority or Task.AVERAGE,
                deadline=deadline_aware,
                project=selected_project
            )
            created_count += 1
        except Exception as e:
            errors.append(f"Задача '{title}': {str(e)}")

    for error in errors:
        messages.warning(request, f'⚠️ {error}')
    if created_count > 0:
        messages.success(request, f'✅ Создано {created_count} задач!')

    # Редирект обратно на страницу проекта
    if selected_project:
        return redirect('tasks:project_planner', project_id=selected_project.id)
    return redirect('tasks:planner')


def handle_single_task(request, user):
    form = TaskForm(request.POST, user=user)

    # ПОЛУЧАЕМ project_id ИЗ GET ПАРАМЕТРА (из URL)
    project_id = request.GET.get('project')
    selected_project = validate_project_access(user, project_id) if project_id else None

    if form.is_valid():
        task = form.save(commit=False)
        task.user = user

        # ПРИВЯЗЫВАЕМ ЗАДАЧУ К ПРОЕКТУ
        if selected_project:
            task.project = selected_project

        task.save()

        messages.success(request, '✅ Задача создана!')

        # Редирект обратно на страницу проекта
        if selected_project:
            return redirect('tasks:project_planner', project_id=selected_project.id)
        return redirect('tasks:planner')

    # Ошибки формы
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f'❌ {field}: {error}')

    return render(request, 'planner/create_task.html', {'form': form})


def parse_datetime(dt_string):
    dt = datetime.fromisoformat(dt_string)
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def redirect_to_source(request, project=None):
    if project:
        return redirect('projects:detail', project_id=project.id)
    return redirect(request.META.get('HTTP_REFERER', 'tasks:planner'))


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'planner/task_detail.html', {'task': task})


@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            updated = form.save()
            messages.success(request, '✅ Задача обновлена!')
            return redirect('tasks:task_detail', pk=updated.pk)
    else:
        form = TaskForm(instance=task, user=request.user)

    return render(request, 'planner/edit_task.html', {'form': form, 'task': task})


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        TaskCRUDService.delete_task(task)
        messages.success(request, '🗑️ Задача удалена!')
        return redirect(request.META.get('HTTP_REFERER', 'tasks:planner'))

    return render(request, 'planner/confirm_delete.html', {'task': task})


@login_required
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        is_completed = TaskCRUDService.toggle_complete(task)
        messages.success(
            request,
            '✅ Задача выполнена!' if is_completed else '↩️ Задача возвращена в работу'
        )

    return redirect(request.META.get('HTTP_REFERER', 'tasks:planner'))


@login_required
def task_list_filtered(request,):
    form = TaskFilterForm(request.GET or None)
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')

    tasks.status = Task.IN_PROGRESS
    tasks.started_at = timezone.now()


    if form.is_valid() and any(form.cleaned_data.values()):
        tasks = TaskQueryService.get_filtered_tasks(request.user, form.cleaned_data)

    return render(request, 'planner/task_list_filtered.html', {
        'tasks': tasks,
        'filter_form': form,
        'total_count': tasks.count(),
        'status': 'started',
        'started_at': tasks.started_at.strftime('%d.%m.%Y %H:%M') if tasks.started_at else None
    })


@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Comment.objects.create(
                author=request.user,
                text=text,
                content_type='task',
                task=task
            )
            messages.success(request, '💬 Комментарий добавлен!')
        else:
            messages.warning(request, 'Комментарий не может быть пустым')

    return redirect('tasks:task_detail', pk=task_id)


@login_required
def assign_task_view(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        deadline = request.POST.get('deadline')

        try:
            user = User.objects.get(username=username)

            if TaskAssignment.objects.filter(task=task, user=user).exists():
                messages.warning(request, f'Задача уже назначена пользователю {username}')
            else:
                TaskAssignment.objects.create(
                    task=task,
                    user=user,
                    assigned_by=request.user,
                    deadline=deadline or task.deadline
                )
                messages.success(request, f'✅ Задача назначена {username}!')

                Comment.objects.create(
                    author=request.user,
                    text=f'Задача назначена пользователю {username}',
                    content_type='task',
                    task=task
                )
        except User.DoesNotExist:
            messages.error(request, f'Пользователь {username} не найден')

        return redirect('tasks:task_detail', pk=task_id)

    return render(request, 'tasks/assign_task.html', {'task': task})


@login_required
def calendar_data_api(request):
    """API для получения данных календаря"""
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))

    data = get_calendar_data(request.user, year, month)
    return JsonResponse(data)


@login_required
def day_tasks_api(request):
    """API для получения задач на конкретный день"""
    try:
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': 'Date parameter required'}, status=400)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': f'Invalid date format: {date_str}'}, status=400)

        # Получаем задачи
        tasks = Task.objects.filter(
            user=request.user,
            deadline__date=date
        ).order_by('priority', 'deadline')

        tasks_data = []
        for task in tasks:
            # Используем priority_label из модели
            priority_display = task.priority_label

            # Форматируем время
            deadline_time = task.deadline.strftime('%H:%M') if task.deadline else ''

            # Создаем URL для задачи
            task_url = f'/planner/{task.id}/'

            task_data = {
                'id': task.id,
                'title': task.title,
                'priority': priority_display,
                'deadline': deadline_time,
                'is_completed': task.is_completed,
                'url': task_url
            }
            tasks_data.append(task_data)

        return JsonResponse({'date': date_str, 'tasks': tasks_data})

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in day_tasks_api: {e}", exc_info=True)

        return JsonResponse({'error': str(e)}, status=500)


@login_required
def task_stats_api(request):
    """API для получения статистики задач"""
    period = request.GET.get('period', 'month')
    now = timezone.now()

    period_days = {'week': 7, 'month': 30, 'year': 365}
    start_date = now - timedelta(days=period_days.get(period, 30))

    tasks = Task.objects.filter(user=request.user, deadline__gte=start_date)

    stats = {
        'completed': tasks.filter(is_completed=True).count(),
        'overdue': tasks.filter(is_completed=False, deadline__lt=now).count(),
        'pending': tasks.filter(is_completed=False, deadline__gte=now).count(),
        'period': period
    }
    stats['total'] = stats['completed'] + stats['overdue'] + stats['pending']

    return JsonResponse(stats)


@login_required
def chart_data_api(request):
    """API для получения данных круговой диаграммы"""
    period = request.GET.get('period', 'month')
    now = timezone.now()

    # Определяем период
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'year':
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)

    # Фильтруем задачи по периоду
    tasks = Task.objects.filter(
        user=request.user,
        deadline__gte=start_date
    )

    total = tasks.count()
    completed = tasks.filter(is_completed=True).count()
    overdue = tasks.filter(is_completed=False, deadline__lt=now).count()
    pending = total - completed - overdue

    # Вычисляем проценты
    if total > 0:
        completed_percent = round((completed / total) * 100, 1)
        overdue_percent = round((overdue / total) * 100, 1)
        pending_percent = round((pending / total) * 100, 1)
        productivity = round((completed / total) * 100)
    else:
        completed_percent = overdue_percent = pending_percent = 0
        productivity = 0

    # Среднее время выполнения
    completed_tasks = tasks.filter(is_completed=True, completed_at__isnull=False)
    if completed_tasks.exists():
        total_days = sum((t.completed_at - t.created_at).days for t in completed_tasks)
        avg_days = round(total_days / completed_tasks.count(), 1)
        avg_completion_time = f"{avg_days} дн."
    else:
        avg_completion_time = "Нет данных"

    return JsonResponse({
        'total_tasks': total,
        'completed': completed,
        'overdue': overdue,
        'pending': pending,
        'completed_percent': completed_percent,
        'overdue_percent': overdue_percent,
        'pending_percent': pending_percent,
        'avg_completion_time': avg_completion_time,
        'productivity': productivity,
    })


@login_required
def start_task(request, pk):
    """Начать выполнение задачи"""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        if task.status != Task.IN_PROGRESS:
            task.status = Task.IN_PROGRESS
            task.started_at = timezone.now()
            task.save()
            messages.success(request, f'▶️ Начата работа над задачей: {task.title}')
        else:
            messages.info(request, f'Задача уже в работе')

    return redirect(request.META.get('HTTP_REFERER', 'tasks:planner'))


@login_required
def pause_task(request, pk):
    """Приостановить выполнение задачи"""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        if task.status == Task.IN_PROGRESS:
            task.status = Task.PENDING
            task.save()
            messages.success(request, f'⏸️ Задача приостановлена: {task.title}')

    return redirect(request.META.get('HTTP_REFERER', 'tasks:planner'))


@login_required
def task_status_api(request, pk):
    """API для изменения статуса задачи"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    task = get_object_or_404(Task, pk=pk, user=request.user)
    action = request.POST.get('action')

    if action == 'start':
        if task.status != Task.IN_PROGRESS:
            task.status = Task.IN_PROGRESS
            task.started_at = timezone.now()
            task.save()
            return JsonResponse({
                'status': 'started',
                'status_label': task.status_label,
                'started_at': task.started_at.strftime('%d.%m.%Y %H:%M') if task.started_at else None
            })

    elif action == 'pause':
        if task.status == Task.IN_PROGRESS:
            task.status = Task.PENDING
            task.save()
            return JsonResponse({
                'status': 'paused',
                'status_label': task.status_label
            })

    elif action == 'complete':
        task.status = Task.COMPLETED
        task.completed_at = timezone.now()
        task.is_completed = True
        task.save()
        return JsonResponse({
            'status': 'completed',
            'status_label': task.status_label
        })

    return JsonResponse({'error': 'Invalid action'}, status=400)