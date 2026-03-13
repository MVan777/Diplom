from django.db import models
from django.conf import settings
from tasks.models import Task

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_projects')
    
    # Участники проекта
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ProjectMembership')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Задачи проекта (связь через many-to-many)
    tasks = models.ManyToManyField(Task, blank=True, related_name='projects')
    
    def __str__(self):
        return self.name

    def get_completed_tasks_count(self):
        """Возвращает количество выполненных задач"""
        return self.tasks.filter(is_completed=True).count()


class ProjectMembership(models.Model):
    """Участие в проекте"""
    
    class Role(models.TextChoices):
        OWNER = 'owner', 'Владелец'
        MANAGER = 'manager', 'Менеджер'
        MEMBER = 'member', 'Участник'
        OBSERVER = 'observer', 'Наблюдатель'
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'user']