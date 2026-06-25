from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    # 🔥 ROTA PRINCIPAL DA ESCOLA
    path('', views.index, name='index'),
    
    # API - Retornam HTML parcial para AJAX
    path('api/dashboard/', views.api_dashboard, name='api_dashboard'),
    
    # Alunos
    path('api/alunos/', views.api_alunos, name='api_alunos'),
    path('api/alunos/novo/', views.api_alunos_novo, name='api_alunos_novo'),
    path('api/alunos/editar/<int:aluno_id>/', views.api_alunos_editar, name='api_alunos_editar'),
    path('api/alunos/salvar/', views.api_alunos_salvar, name='api_alunos_salvar'),
    path('api/alunos/deletar/<int:aluno_id>/', views.api_alunos_deletar, name='api_alunos_deletar'),
    
    # Turmas
    path('api/turmas/', views.api_turmas, name='api_turmas'),
    path('api/turmas/novo/', views.api_turmas_novo, name='api_turmas_novo'),
    path('api/turmas/editar/<int:turma_id>/', views.api_turmas_editar, name='api_turmas_editar'),
    path('api/turmas/salvar/', views.api_turmas_salvar, name='api_turmas_salvar'),
    path('api/turmas/deletar/<int:turma_id>/', views.api_turmas_deletar, name='api_turmas_deletar'),
    
    # Matrículas
    path('api/matriculas/', views.api_matriculas, name='api_matriculas'),
    path('api/matriculas/nova/', views.api_matriculas_nova, name='api_matriculas_nova'),
    path('api/matriculas/salvar/', views.api_matriculas_salvar, name='api_matriculas_salvar'),
    path('api/matriculas/deletar/<int:matricula_id>/', views.api_matriculas_deletar, name='api_matriculas_deletar'),
    
    # Disciplinas
    path('api/disciplinas/', views.api_disciplinas, name='api_disciplinas'),
    path('api/disciplinas/novo/', views.api_disciplinas_novo, name='api_disciplinas_novo'),
    path('api/disciplinas/salvar/', views.api_disciplinas_salvar, name='api_disciplinas_salvar'),
    
    # Professores
    path('api/professores/', views.api_professores, name='api_professores'),
    path('api/professores/novo/', views.api_professores_novo, name='api_professores_novo'),
    path('api/professores/salvar/', views.api_professores_salvar, name='api_professores_salvar'),
    
    # Configurações
    path('api/configuracoes/', views.api_configuracoes, name='api_configuracoes'),
    path('api/configuracoes/salvar/', views.api_configuracoes_salvar, name='api_configuracoes_salvar'),
]
