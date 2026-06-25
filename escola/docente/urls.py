from django.urls import path
from . import views

app_name = 'docente'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('professores/', views.professores, name='professores'),
]