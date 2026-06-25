from django.urls import path
from . import views

app_name = 'administrativo'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]