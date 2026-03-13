from django.urls import path
from .views import (register_view, login_view, logout_view,
                    forgot_password, user_profile, contact, feedback)

app_name = 'users'

urlpatterns = [
    path('signup/', register_view, name='signup'),
    path('signin/', login_view, name='signin'),
    path('recovery/', forgot_password, name='recovery'),
    path('profile/', user_profile, name='user_profile'),
    path('logout/', logout_view, name='logout'),
    path('feedback/', feedback, name='feedback'),
    path('contact/', contact, name='contact'),
]