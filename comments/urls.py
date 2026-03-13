from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('task/<int:task_id>/add/', views.add_task_comment, name='add_task_comment'),
    path('project/<int:project_id>/add/', views.add_project_comment, name='add_project_comment'),
]