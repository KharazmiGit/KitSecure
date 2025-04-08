from django.urls import path
from . import views

app_name = 'auth_process'
urlpatterns = [
    path('login/logic', views.login_logic_view, name='login-logic')
]
