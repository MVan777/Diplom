from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),    
    path('planner/', include('tasks.urls')),
    path('projects/', include('projects.urls')),
    path('assignments/', include('assignments.urls')),
    path('users/', include('users.urls')),
]
