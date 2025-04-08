from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'account'

urlpatterns = [
    path('users/list', views.UserListApiView.as_view(), name='user-list'),
    path('create/user', views.CreateUserApiView.as_view(), name='create-user')
]
