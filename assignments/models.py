from django.db import models
from django.conf import settings
from tasks.models import Task
from django.utils import timezone

class TaskAssignment(models.Model):
    """Назначение задачи пользователю"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        IN_PROGRESS = 'in_progress', 'В работе'
        REVIEW = 'review', 'На проверке'
        COMPLETED = 'completed', 'Завершена'
        REJECTED = 'rejected', 'Возвращена'
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_assignments')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Время
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField()  # Срок для этого пользователя
    
    # Отчет
    report = models.TextField(blank=True, verbose_name='Отчет о выполненной работе')
    
    class Meta:
        unique_together = ['task', 'user']  # Один пользователь - одна задача
    
    def start_work(self):
        """Начать работу"""
        self.status = self.Status.IN_PROGRESS
        self.started_at = timezone.now()
        self.save()
    
    def complete_work(self, report=''):
        """Завершить работу"""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if report:
            self.report = report
        self.save()
    
    def reject_work(self, reason=''):
        """Вернуть на доработку"""
        self.status = self.Status.REJECTED
        self.save()