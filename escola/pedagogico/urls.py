from django.urls import path
from . import views

app_name = 'secretaria'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('alunos/', views.alunos, name='alunos'),
    path('turmas/', views.turmas, name='turmas'),
    path('matriculas/', views.matriculas, name='matriculas'),
]