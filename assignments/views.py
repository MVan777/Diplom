from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import TaskAssignment
from comments.models import Comment


@login_required
def start_task(request, assignment_id):
    """Начать работу над задачей"""
    assignment = get_object_or_404(TaskAssignment, id=assignment_id, user=request.user)
    
    if request.method == 'POST':
        assignment.start_work()
        messages.success(request, '✅ Работа начата!')
        
        Comment.objects.create(
            author=request.user,
            text=f'Начал работу над задачей',
            content_type='task',
            task=assignment.task
        )
    
    return redirect('tasks:task_detail', pk=assignment.task.pk)


@login_required
def complete_task(request, assignment_id):
    """Завершить задачу с отчетом"""
    assignment = get_object_or_404(TaskAssignment, id=assignment_id, user=request.user)
    
    if request.method == 'POST':
        report = request.POST.get('report', '')
        assignment.complete_work(report)
        messages.success(request, '✅ Задача выполнена! Отправлено на проверку')
        
        Comment.objects.create(
            author=request.user,
            text=f'Отчет о выполнении:\n{report}',
            content_type='report',
            task=assignment.task
        )
    
    return redirect('tasks:task_detail', pk=assignment.task.pk)


@login_required
def reject_task(request, assignment_id):
    """Вернуть задачу на доработку (для проверяющего)"""
    assignment = get_object_or_404(TaskAssignment, id=assignment_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        assignment.reject_work(reason)
        messages.info(request, '↩️ Задача возвращена на доработку')
        
        Comment.objects.create(
            author=request.user,
            text=f'Задача возвращена: {reason}',
            content_type='task',
            task=assignment.task
        )
    
    return redirect('tasks:task_detail', pk=assignment.task.pk)


@login_required
def assign_task(request, task_id):
    """Назначить задачу пользователю"""
    from tasks.models import Task
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
    return render(request, 'assignments/assign_task.html', context)


@login_required
def cancel_assignment(request, assignment_id):
    """Отменить назначение задачи"""
    assignment = get_object_or_404(TaskAssignment, id=assignment_id)
    
    if request.method == 'POST':
        task_id = assignment.task.id
        user_name = assignment.user.username
        assignment.delete()
        messages.success(request, f'✅ Назначение задачи пользователю {user_name} отменено!')
        
        Comment.objects.create(
            author=request.user,
            text=f'Назначение отменено для пользователя {user_name}',
            content_type='task',
            task_id=task_id
        )
        
        return redirect('tasks:task_detail', pk=task_id)
    
    context = {'assignment': assignment}
    return render(request, 'assignments/confirm_cancel_assignment.html', context)

@login_required
def assign_task_view(request, task_id):
    """Назначить задачу пользователю"""
    from assignments.models import TaskAssignment
    from django.contrib.auth.models import User

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