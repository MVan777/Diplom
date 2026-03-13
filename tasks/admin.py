from django.contrib import admin
from .models import Task

@admin.register(Task)
class TasksAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'deadline', 'is_completed']
    list_filter = ['priority', 'is_completed', 'user']
    search_fields = ['title', 'description']
    list_editable = ['is_completed']
    readonly_fields = ['created_at']