from django import forms
from django.db import models
from .models import Task
from projects.models import Project
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'deadline', 'project']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Название задачи',
                'class': 'form-input',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Описание задачи (необязательно)',
                'class': 'form-textarea',
                'maxlength': 1000
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-input'
            }),
            'project': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'priority': 'Приоритет',
            'deadline': 'Срок выполнения',
            'project': 'Проект',
        }

    def __init__(self, *args, **kwargs):
        # Извлекаем user из kwargs, если он есть
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Устанавливаем минимальную дату (сегодня)
        now_local = timezone.localtime()
        now_str = now_local.strftime('%Y-%m-%dT%H:%M')
        self.fields['deadline'].widget.attrs['min'] = now_str

        if self.user and not self.user.is_anonymous:
            from django.db.models import Q
            self.fields['project'].queryset = Project.objects.filter(
                Q(owner=self.user) | Q(members=self.user)
            ).distinct()
            self.fields['project'].required = False
            self.fields['project'].empty_label = "--- Без проекта ---"
        else:
            # Если пользователь не аутентифицирован, показываем пустой queryset
            self.fields['project'].queryset = Project.objects.none()
            self.fields['project'].required = False

        # Устанавливаем дедлайн по умолчанию (завтра 18:00)
        if not self.instance.pk:
            tomorrow = timezone.localtime(timezone.now()) + timedelta(days=1)
            tomorrow = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)
            self.fields['deadline'].initial = tomorrow.strftime('%Y-%m-%dT%H:%M')

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline:
            if timezone.is_naive(deadline):
                deadline = timezone.make_aware(deadline, timezone.get_current_timezone())
            if deadline < timezone.now():
                raise ValidationError("Дедлайн не может быть в прошлом")
        return deadline

    def clean(self):
        cleaned = super().clean()
        deadline = cleaned.get('deadline')
        if deadline:
            if timezone.is_naive(deadline):
                deadline = timezone.make_aware(deadline, timezone.get_current_timezone())
                cleaned['deadline'] = deadline
        return cleaned

    def save(self, commit=True):
        task = super().save(commit=False)
        if self.user:
            task.user = self.user
        if commit:
            task.save()
        return task


class TaskFilterForm(forms.Form):
    PRIORITY_CHOICES = [
        ('', 'Все приоритеты'),
        ('ordinary', 'Обычный'),
        ('average', 'Средний'),
        ('urgent', 'Срочный'),
    ]

    STATUS_CHOICES = [
        ('', 'Все статусы'),
        ('active', 'Активные'),
        ('completed', 'Завершенные'),
        ('overdue', 'Просроченные'),
    ]

    SORT_CHOICES = [
        ('-created_at', 'Новые сначала'),
        ('created_at', 'Старые сначала'),
        ('deadline', 'По сроку (ближайшие)'),
        ('-deadline', 'По сроку (дальние)'),
        ('priority', 'По приоритету'),
    ]

    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Поиск...',
            'class': 'form-input'
        })
    )

    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )