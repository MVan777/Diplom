from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [

    # Главная страница
    path('planner/', views.planner, name='planner'),
    path('project/<int:project_id>/', views.project_planner, name='project_planner'),

    # Задачи
    path('list/', views.task_list, name='task_list'),
    path('filter/', views.task_list_filtered, name='task_filter'),

    # CRUD операции
    path('create/', views.create_task, name='create_task'),
    path('<int:pk>/', views.task_detail, name='task_detail'),
    path('<int:pk>/edit/', views.edit_task, name='edit_task'),
    path('<int:pk>/delete/', views.delete_task, name='delete_task'),
    path('<int:pk>/complete/', views.complete_task, name='complete_task'),

    # Комментарии и назначения
    path('<int:task_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:task_id>/assign/', views.assign_task_view, name='assign_task'),

    # API endpoints
    path('api/calendar-data/', views.calendar_data_api, name='calendar_data'),
    path('api/day-tasks/', views.day_tasks_api, name='day_tasks'),
    path('api/task-stats/', views.task_stats_api, name='task_stats'),
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),

    #Изменения статуса работы задачи
    path('api/task/<int:pk>/status/', views.task_status_api, name='task_status_api'),
    path('<int:pk>/start/', views.start_task, name='start_task'),
    path('<int:pk>/pause/', views.pause_task, name='pause_task'),
]