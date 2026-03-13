from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from .forms import TaskForm, TaskFilterForm
from django.utils import timezone
from datetime import datetime
from .task_service import TaskStatsService, TaskQueryService, TaskCRUDService
from comments.models import Comment
# from projects.models import Project
from assignments.models import TaskAssignment
from django.contrib.auth.models import User
from django.apps import apps
Project = apps.get_model('projects', 'Project')


@login_required
def planner(request):
    context = {
        'stats': TaskStatsService.get_user_stats(request.user),
        'urgent_tasks': TaskQueryService.get_priority_tasks(request.user, Task.URGENT),
        'medium_tasks': TaskQueryService.get_priority_tasks(request.user, Task.AVERAGE),
        'low_tasks': TaskQueryService.get_priority_tasks(request.user, Task.ORDINARY),
    }
    return render(request, 'planner/planner.html', context)

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'planner/task_list.html', {'tasks': tasks})


@login_required
def create_task(request):
    # Получаем проект из GET параметра (если есть)
    project_id = request.GET.get('project')
    selected_project = None

    if project_id:
        try:
            selected_project = Project.objects.get(id=project_id)
            # Проверяем доступ пользователя к проекту
            if not (selected_project.owner == request.user or
                    request.user in selected_project.members.all()):
                selected_project = None
                messages.warning(request, 'У вас нет доступа к этому проекту')
        except Project.DoesNotExist:
            pass

    if request.method == 'POST':
        # Проверяем, пришла ли форма с несколькими задачами
        titles = request.POST.getlist('titles[]')
        deadlines = request.POST.getlist('deadlines[]')
        priorities = request.POST.getlist('priorities[]')

        # Получаем проект из POST (если есть)
        project_post_id = request.POST.get('project')
        task_project = None
        if project_post_id:
            try:
                task_project = Project.objects.get(id=project_post_id)
                # Проверяем доступ
                if not (task_project.owner == request.user or
                        request.user in task_project.members.all()):
                    task_project = None
                    messages.warning(request, 'У вас нет доступа к этому проекту')
            except Project.DoesNotExist:
                pass

        # Обработка множественного создания задач
        if titles and deadlines and len(titles) > 1:  # Несколько задач
            created_count = 0
            errors = []

            for i, (title, deadline, priority) in enumerate(zip(titles, deadlines, priorities)):
                if not title.strip():
                    errors.append(f"Задача #{i + 1}: название не может быть пустым")
                    continue

                if not deadline:
                    errors.append(f"Задача '{title}': срок выполнения не указан")
                    continue

                try:
                    dt = datetime.fromisoformat(deadline)
                    if timezone.is_naive(dt):
                        deadline_aware = timezone.make_aware(
                            dt,
                            timezone.get_current_timezone()
                        )
                    else:
                        deadline_aware = dt

                    # Создаем задачу
                    Task.objects.create(
                        user=request.user,
                        title=title.strip(),
                        priority=priority or Task.AVERAGE,
                        deadline=deadline_aware,
                        project=task_project
                    )
                    created_count += 1

                except ValueError as e:
                    errors.append(f"Задача '{title}': неверный формат даты")
                except Exception as e:
                    errors.append(f"Задача '{title}': {str(e)}")

            # Показываем сообщения об ошибках
            for error in errors:
                messages.warning(request, f'⚠️ {error}')

            if created_count > 0:
                messages.success(request, f'✅ Создано {created_count} задач!')

            # Редирект обратно в проект, если задача создавалась в проекте
            if task_project:
                return redirect('projects:detail', project_id=task_project.id)
            return redirect('tasks:planner')

        else:  # Одна задача (обычная форма)
            form = TaskForm(request.POST, user=request.user)
            if form.is_valid():
                task = form.save(commit=False)
                task.user = request.user

                # Устанавливаем проект из POST данных
                if form.cleaned_data.get('project'):
                    task.project = form.cleaned_data['project']

                task.save()
                messages.success(request, '✅ Задача создана!')

                # Создаем комментарий, если задача в проекте
                if task.project:
                    Comment.objects.create(
                        author=request.user,
                        text=f'Создана задача: {task.title}',
                        content_type='task',
                        task=task
                    )

                # Редирект обратно в проект
                if task.project:
                    return redirect('projects:detail', project_id=task.project.id)
                return redirect('tasks:planner')
            else:
                # Показываем ошибки формы
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'❌ {field}: {error}')

                return render(request, 'planner/create_task.html', {
                    'form': form,
                    'selected_project': selected_project
                })
    else:
        # Для GET запроса - передаем выбранный проект в форму
        initial_data = {}
        if selected_project:
            initial_data['project'] = selected_project.id  # Передаем ID, а не объект
        if 'priority' in request.GET:
            initial_data['priority'] = request.GET.get('priority')

        form = TaskForm(user=request.user, initial=initial_data)

    return render(request, 'planner/create_task.html', {
        'form': form,
        'selected_project': selected_project
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'planner/task_detail.html', {'task': task})


@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        # 👇 ИСПРАВЛЕНО: сначала request.POST, потом instance, потом user
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            updated = form.save()
            messages.success(request, '✅ Задача обновлена!')
            return redirect('tasks:task_detail', pk=updated.pk)
    else:
        # 👇 ИСПРАВЛЕНО: сначала instance, потом user
        form = TaskForm(instance=task, user=request.user)

    return render(request, 'planner/edit_task.html', {'form': form, 'task': task})


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        TaskCRUDService.delete_task(task)
        messages.success(request, '🗑️ Задача удалена!')
        return redirect(request.META.get('HTTP_REFERER','tasks:planner'))

    return render(request, 'planner/confirm_delete.html', {'task': task})


@login_required
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        is_completed = TaskCRUDService.toggle_complete(task)
        if is_completed:
            messages.success(request, '✅ Задача выполнена!')
        else:
            messages.info(request, '↩️ Задача возвращена в работу')

    return redirect(request.META.get('HTTP_REFERER', 'tasks:planner'))


@login_required
def task_list_filtered(request):
    form = TaskFilterForm(request.GET or None)
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')

    if form.is_valid() and any(form.cleaned_data.values()):
        tasks = TaskQueryService.get_filtered_tasks(request.user, form.cleaned_data)

    context = {
        'tasks': tasks,
        'filter_form': form,
        'total_count': tasks.count(),
    }
    return render(request, 'planner/task_list_filtered.html', context)


@login_required
def add_comment(request, task_id):
    """Добавить комментарий к задаче"""
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
    """Назначить задачу пользователю"""


    task = get_object_or_404(Task, pk=task_id, user=request.user)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        deadline = request.POST.get('deadline')

        try:
            user = User.objects.get(username=username)

            if TaskAssignment.objects.filter(task=task, user=user).exists():
                messages.warning(request, f'Задача уже назначена пользователю {username}')
            else:
                assignment = TaskAssignment.objects.create(
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

    context = {'task': task}
    return render(request, 'tasks/assign_task.html', context)