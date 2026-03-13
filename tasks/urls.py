from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [

    # Главная страница
    path('planner/', views.planner, name='planner'),

    # Задачи
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:pk>/list/', views.task_list, name='task_list'),
    path('tasks/<int:pk>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:pk>/delete/', views.delete_task, name='delete_task'),
    path('tasks/<int:pk>/complete/', views.complete_task, name='complete_task'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/assign/', views.assign_task_view, name='assign_task'),

    # Комментарии
    path('tasks/<int:task_id>/comment/', views.add_comment, name='add_comment'),

    # Фильтрация
    path('tasks/filter/', views.task_list_filtered, name='task_filter'),
]