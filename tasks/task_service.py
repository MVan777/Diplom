from django.db.models import Q
from .models import Task
from django.utils import timezone
from datetime import datetime, time, timedelta


class TaskStatsService:

    @staticmethod
    def get_user_stats(user):
        user_tasks = Task.objects.filter(user=user)
        tz = timezone.get_current_timezone()
        now = timezone.localtime()
        today = now.date()
        start_of_day = timezone.make_aware(datetime.combine(today, time.min), tz)
        end_of_day = start_of_day + timedelta(days=1)
        total_tasks = user_tasks.count()
        completed_tasks = user_tasks.filter(is_completed=True).count()

        return {
            'total': total_tasks,
            'completed': completed_tasks,
            'urgent': user_tasks.filter(priority=Task.URGENT, is_completed=False).count(),
            'today': user_tasks.filter(deadline__gte=start_of_day, deadline__lt=end_of_day, is_completed=False).count(),
            'upcoming': user_tasks.filter(deadline__gte=end_of_day, is_completed=False).count(),
            'completion_rate': int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        }

# Запрос задач
class TaskQueryService:

    @staticmethod
    def get_priority_tasks(user, priority, limit=10):
        return Task.objects.filter(
            user=user,
            priority=priority,
            is_completed=False
        ).order_by('deadline')[:limit]

    @staticmethod
    def get_today_tasks(user, limit=15):
        today = timezone.now().date()
        return Task.objects.filter(
            user=user,
            deadline__date=today,
            is_completed=False
        ).order_by('deadline')[:limit]

    @staticmethod
    def get_filtered_tasks(user, filters):
        tasks = Task.objects.filter(user=user)

        if priority := filters.get('priority'):
            tasks = tasks.filter(priority=priority)

        if status := filters.get('status'):
            now = timezone.now()
            if status == 'active':
                tasks = tasks.filter(is_completed=False, deadline__gte=now)
            elif status == 'completed':
                tasks = tasks.filter(is_completed=True)
            elif status == 'overdue':
                tasks = tasks.filter(is_completed=False, deadline__lt=now)

        if search := filters.get('search'):
            tasks = tasks.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        if sort := filters.get('sort'):
            tasks = tasks.order_by(sort)
        else:
            tasks = tasks.order_by('-created_at')

        return tasks


# Стандартные методы
class TaskCRUDService:

    @staticmethod
    def create_task(user, data):
        task = Task(user=user, **data)
        task.save()
        return task

    @staticmethod
    def update_task(task, data):
        for key, value in data.items():
            setattr(task, key, value)
        task.save()
        return task

    @staticmethod
    def delete_task(task):
        task.delete()

    @staticmethod
    def toggle_complete(task):
        task.is_completed = not task.is_completed
        task.save()
        return task.is_completed