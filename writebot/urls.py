from django.urls import path
from . import views

urlpatterns = [
    path('create/action' , views.CreateTrackedUserActions.as_view() , name='create-usr-act') , 
    path('download/python-code/', views.download_python_code_excel, name='download_python_code')
]