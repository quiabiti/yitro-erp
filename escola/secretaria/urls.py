from django.urls import path
from . import views

app_name = 'secretaria'

urlpatterns = [
    # ============================================
    # 🔥 PÁGINAS PRINCIPAIS
    # ============================================
    path('matriculas/', views.secretaria_matriculas, name='secretaria_matriculas'),
    path('pagamentos/', views.secretaria_pagamentos, name='secretaria_pagamentos'),
    path('alunos/', views.secretaria_alunos, name='secretaria_alunos'),
    path('documentos/', views.secretaria_documentos, name='secretaria_documentos'),
    
    # ============================================
    # 🔥 API - MATRÍCULAS
    # ============================================
    path('api/secretaria/matriculas/', views.api_matriculas_listar, name='api_matriculas_listar'),
    path('api/secretaria/matriculas/stats/', views.api_matriculas_stats, name='api_matriculas_stats'),
    path('api/secretaria/matricula/form/', views.api_matricula_form, name='api_matricula_form'),
    path('api/secretaria/matricula/form/<int:matricula_id>/', views.api_matricula_form, name='api_matricula_form_edit'),
    path('api/secretaria/matricula/salvar/', views.api_matricula_salvar, name='api_matricula_salvar'),
    path('api/secretaria/matricula/salvar/<int:matricula_id>/', views.api_matricula_salvar, name='api_matricula_salvar_edit'),
    path('api/secretaria/matricula/confirmar/<int:matricula_id>/', views.api_matricula_confirmar, name='api_matricula_confirmar'),
    path('api/secretaria/matricula/cancelar/<int:matricula_id>/', views.api_matricula_cancelar, name='api_matricula_cancelar'),
    path('api/secretaria/matricula/trancar/<int:matricula_id>/', views.api_matricula_trancar, name='api_matricula_trancar'),
    path('api/secretaria/matricula/deletar/<int:matricula_id>/', views.api_matricula_deletar, name='api_matricula_deletar'),
    
    # ============================================
    # 🔥 API - ALUNOS
    # ============================================
    path('api/secretaria/alunos/', views.api_alunos_listar, name='api_alunos_listar'),
    path('api/secretaria/alunos/buscar/', views.api_alunos_buscar, name='api_alunos_buscar'),
    path('api/secretaria/alunos/stats/', views.api_alunos_stats, name='api_alunos_stats'),
    path('api/secretaria/alunos/historico/<int:aluno_id>/', views.api_historico_aluno, name='api_historico_aluno'),
    
    # ============================================
    # 🔥 API - TURMAS
    # ============================================
    path('api/secretaria/turmas/listar/', views.api_turmas_listar, name='api_turmas_listar'),
    
    # ============================================
    # 🔥 IMPRESSÃO
    # ============================================
    path('impressao/matricula/<int:matricula_id>/', views.impressao_matricula, name='impressao_matricula'),
]