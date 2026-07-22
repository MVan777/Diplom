from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Project, ProjectMembership
# from tasks.models import Task
# from comments.models import Comment
from django.apps import apps
Task = apps.get_model('tasks', 'Task')
Comment = apps.get_model('comments', 'Comment')
from django.db.models import Count, Q

@login_required
def project_list(request):

    # Проекты, где пользователь владелец
    owned_projects = Project.objects.filter(owner=request.user).annotate(
        total_tasks=Count('project_tasks'),
        completed_tasks=Count('project_tasks', filter=Q(project_tasks__is_completed=True))
    ).prefetch_related('members')

    # Проекты, где пользователь участник
    member_projects = Project.objects.filter(members=request.user).exclude(
        owner=request.user
    ).annotate(
        total_tasks=Count('project_tasks'),
        completed_tasks=Count('project_tasks', filter=Q(project_tasks__is_completed=True))
    ).prefetch_related('members')

    context = {
        'owned_projects': owned_projects,
        'member_projects': member_projects,
        'total_projects': owned_projects.count() + member_projects.count(),
    }

    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail(request, project_id):
    """Детали проекта с задачами и чатом"""
    project = get_object_or_404(Project, id=project_id)

    # Проверка доступа
    if request.user != project.owner and not project.members.filter(id=request.user.id).exists():
        messages.error(request, 'У вас нет доступа к этому проекту')
        return redirect('projects:list')

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Comment.objects.create(
                author=request.user,
                text=text,
                content_type='project',
                project=project
            )
            messages.success(request, '💬 Сообщение отправлено!')
        return redirect('projects:detail', project_id=project.id)


    tasks = project.project_tasks.all()
    members = project.members.all()
    comments = Comment.objects.filter(
        content_type='project',
        project=project
    ).select_related('author').order_by('created_at')

    # Статистика выполнения
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True).count()

    context = {
        'comments': comments,
        'project': project,
        'tasks': tasks,
        'members': members,
        'is_owner': request.user == project.owner,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def create_project(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, 'Название проекта не может быть пустым')
            return redirect('projects:create')
        
        project = Project.objects.create(
            name=name,
            description=description,
            owner=request.user
        )
        
        # Добавляем создателя как участника
        ProjectMembership.objects.create(
            project=project,
            user=request.user,
            role=ProjectMembership.Role.OWNER
        )
        
        messages.success(request, f'✅ Проект "{name}" создан!')
        return redirect('projects:detail', project_id=project.id)
    
    return render(request, 'projects/create_project.html')


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        project.name = request.POST.get('name', '').strip() or project.name
        project.description = request.POST.get('description', '').strip()
        project.save()
        
        messages.success(request, '✅ Проект обновлен!')
        return redirect('projects:detail', project_id=project.id)
    
    context = {'project': project}
    return render(request, 'projects/edit_project.html', context)


@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'🗑️ Проект "{project_name}" удален!')
        return redirect('projects:list')
    
    context = {'project': project}
    return render(request, 'projects/confirm_delete_project.html', context)


@login_required
def add_member(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        role = request.POST.get('role', ProjectMembership.Role.MEMBER)
        
        try:
            user = User.objects.get(username=username)
            
            if ProjectMembership.objects.filter(project=project, user=user).exists():
                messages.warning(request, f'Пользователь {username} уже участник проекта')
            else:
                ProjectMembership.objects.create(
                    project=project,
                    user=user,
                    role=role
                )
                messages.success(request, f'✅ Пользователь {username} добавлен в проект!')
        except User.DoesNotExist:
            messages.error(request, f'Пользователь {username} не найден')
        
        return redirect('projects:detail', project_id=project.id)
    
    context = {'project': project}
    return render(request, 'projects/add_member.html', context)


@login_required
def remove_member(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        ProjectMembership.objects.filter(project=project, user=user).delete()
        messages.success(request, f'✅ Пользователь {user.username} удален из проекта!')
        return redirect('projects:detail', project_id=project.id)
    
    context = {'project': project, 'user': user}
    return render(request, 'projects/confirm_remove_member.html', context)


@login_required
def project_chat(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, 'У вас нет доступа к этому проекту')
        return redirect('projects:list')
    
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Comment.objects.create(
                author=request.user,
                text=text,
                content_type='project',
                project=project
            )
            messages.success(request, '💬 Сообщение отправлено!')
        return redirect('projects:chat', project_id=project.id)
    
    comments = Comment.objects.filter(
        content_type='project',
        project=project
    ).select_related('author').order_by('created_at')
    
    context = {
        'project': project,
        'comments': comments,
    }
    return render(request, 'projects/project_chat.html', context)
