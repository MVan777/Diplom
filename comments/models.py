from django.db import models
from django.conf import settings
from tasks.models import Task
from projects.models import Project

class Comment(models.Model):

    class CommentType(models.TextChoices):
        TASK = 'task', 'Комментарий к задаче'
        PROJECT = 'project', 'Комментарий к проекту'
        REPORT = 'report', 'Отчет о работе'
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Привязка комментарий
    content_type = models.CharField(max_length=20, choices=CommentType.choices)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    
    attachment = models.FileField(upload_to='comment_attachments/', null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.author} - {self.created_at}'