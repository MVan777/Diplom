from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class Task(models.Model):

    # Приоритеты
    ORDINARY = 'ordinary'
    AVERAGE = 'average'
    URGENT = 'urgent'

    PRIORITY_CHOICES = [
        (ORDINARY, 'Обычный'),
        (AVERAGE, 'Средний'),
        (URGENT, 'Срочный'),
    ]

    # Основные поля
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(max_length=1000, blank=True, verbose_name='Описание')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES,
                                default=ORDINARY,verbose_name='Приоритет')

    deadline = models.DateTimeField(verbose_name='Дедлайн')

    # Статус
    is_completed = models.BooleanField(default=False, verbose_name='Выполнено')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    deadline_end = models.DateTimeField(null=True, blank=True, verbose_name='Конец задачи')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks',
                             verbose_name='Пользователь')

    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='project_tasks')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'deadline']),
            models.Index(fields=['user', 'is_completed']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return not self.is_completed and self.deadline < timezone.now()

    @property
    def is_today(self):
        return self.deadline.date() == timezone.now().date()

    @property
    def priority_label(self):
        return dict(self.PRIORITY_CHOICES).get(self.priority, 'Неизвестно')

    def clean(self):
        if self.deadline and self.deadline < timezone.now() and not self.pk:
            raise ValidationError({'deadline': 'Дедлайн не может быть в прошлом'})

        if self.deadline_end and self.deadline and self.deadline_end < self.deadline:
            raise ValidationError({'deadline_end': 'Конец задачи должен быть позже дедлайна'})

    def save(self, *args, **kwargs):

        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None

        self.full_clean()

        super().save(*args, **kwargs)