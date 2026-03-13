from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Проекты
    path('', views.project_list, name='list'),
    path('create/', views.create_project, name='create'),
    path('<int:project_id>/', views.project_detail, name='detail'),
    path('<int:project_id>/edit/', views.edit_project, name='edit'),
    path('<int:project_id>/delete/', views.delete_project, name='delete'),
    
    # Участники
    path('<int:project_id>/members/add/', views.add_member, name='add_member'),
    path('<int:project_id>/members/<int:user_id>/remove/', views.remove_member, name='remove_member'),
    
    # Чат
    path('<int:project_id>/chat/', views.project_chat, name='chat'),
]