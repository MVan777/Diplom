from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('<int:assignment_id>/start/', views.start_task, name='start'),
    path('<int:assignment_id>/complete/', views.complete_task, name='complete'),
    path('<int:assignment_id>/reject/', views.reject_task, name='reject'),
    path('<int:assignment_id>/cancel/', views.cancel_assignment, name='cancel'),
]