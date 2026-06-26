from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    # 🔥 ROTA PRINCIPAL DA ESCOLA
    path('', views.index, name='index'),
    
    # 🔥 ROTA PARA ENTRAR NA ESCOLA PELO SLUG
    path('<str:slug>/', views.entrar_escola, name='entrar_escola'),
    
    # ============================================
    # API - GESTÃO DE ESCOLAS (YITRO)
    # ============================================
    path('api/escolas/', views.api_escolas_listar, name='api_escolas_listar'),
    path('api/escolas/nova/', views.api_escola_nova, name='api_escola_nova'),
    path('api/escolas/editar/<int:escola_id>/', views.api_escola_editar, name='api_escola_editar'),
    path('api/escolas/salvar/', views.api_escola_salvar, name='api_escola_salvar'),
    path('api/escolas/deletar/<int:escola_id>/', views.api_escola_deletar, name='api_escola_deletar'),
    
    # ============================================
    # API - DASHBOARD
    # ============================================
    path('api/dashboard/', views.api_dashboard, name='api_dashboard'),
]