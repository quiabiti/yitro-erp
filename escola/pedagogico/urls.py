from django.urls import path
from . import views

app_name = 'pedagogico'

urlpatterns = [
    # Página principal do módulo pedagógico
    path('', views.pedagogico_dashboard, name='dashboard'),  # <- Adicionado
    
    # Stats
    path('stats/', views.api_stats, name='stats'),
    
    # Ano Lectivo
    path('ano_lectivo/listar/', views.api_listar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_listar'),
    path('ano_lectivo/criar/', views.api_form_criar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_criar'),
    path('ano_lectivo/editar/<int:item_id>/', views.api_form_editar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_editar'),
    path('ano_lectivo/salvar/', views.api_salvar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_salvar'),
    path('ano_lectivo/salvar/<int:item_id>/', views.api_salvar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_atualizar'),
    path('ano_lectivo/deletar/<int:item_id>/', views.api_deletar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_deletar'),
    
    # Trimestre
    path('trimestre/listar/', views.api_listar, {'categoria': 'trimestre'}, name='trimestre_listar'),
    path('trimestre/criar/', views.api_form_criar, {'categoria': 'trimestre'}, name='trimestre_criar'),
    path('trimestre/editar/<int:item_id>/', views.api_form_editar, {'categoria': 'trimestre'}, name='trimestre_editar'),
    path('trimestre/salvar/', views.api_salvar, {'categoria': 'trimestre'}, name='trimestre_salvar'),
    path('trimestre/salvar/<int:item_id>/', views.api_salvar, {'categoria': 'trimestre'}, name='trimestre_atualizar'),
    path('trimestre/deletar/<int:item_id>/', views.api_deletar, {'categoria': 'trimestre'}, name='trimestre_deletar'),
    
    # Nível de Ensino
    path('nivel_ensino/listar/', views.api_listar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_listar'),
    path('nivel_ensino/criar/', views.api_form_criar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_criar'),
    path('nivel_ensino/editar/<int:item_id>/', views.api_form_editar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_editar'),
    path('nivel_ensino/salvar/', views.api_salvar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_salvar'),
    path('nivel_ensino/salvar/<int:item_id>/', views.api_salvar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_atualizar'),
    path('nivel_ensino/deletar/<int:item_id>/', views.api_deletar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_deletar'),
    
    # Classe
    path('classe/listar/', views.api_listar, {'categoria': 'classe'}, name='classe_listar'),
    path('classe/criar/', views.api_form_criar, {'categoria': 'classe'}, name='classe_criar'),
    path('classe/editar/<int:item_id>/', views.api_form_editar, {'categoria': 'classe'}, name='classe_editar'),
    path('classe/salvar/', views.api_salvar, {'categoria': 'classe'}, name='classe_salvar'),
    path('classe/salvar/<int:item_id>/', views.api_salvar, {'categoria': 'classe'}, name='classe_atualizar'),
    path('classe/deletar/<int:item_id>/', views.api_deletar, {'categoria': 'classe'}, name='classe_deletar'),
    
    # Disciplina
    path('disciplina/listar/', views.api_listar, {'categoria': 'disciplina'}, name='disciplina_listar'),
    path('disciplina/criar/', views.api_form_criar, {'categoria': 'disciplina'}, name='disciplina_criar'),
    path('disciplina/editar/<int:item_id>/', views.api_form_editar, {'categoria': 'disciplina'}, name='disciplina_editar'),
    path('disciplina/salvar/', views.api_salvar, {'categoria': 'disciplina'}, name='disciplina_salvar'),
    path('disciplina/salvar/<int:item_id>/', views.api_salvar, {'categoria': 'disciplina'}, name='disciplina_atualizar'),
    path('disciplina/deletar/<int:item_id>/', views.api_deletar, {'categoria': 'disciplina'}, name='disciplina_deletar'),
    
    # Turma
    path('turma/listar/', views.api_listar, {'categoria': 'turma'}, name='turma_listar'),
    path('turma/criar/', views.api_form_criar, {'categoria': 'turma'}, name='turma_criar'),
    path('turma/editar/<int:item_id>/', views.api_form_editar, {'categoria': 'turma'}, name='turma_editar'),
    path('turma/salvar/', views.api_salvar, {'categoria': 'turma'}, name='turma_salvar'),
    path('turma/salvar/<int:item_id>/', views.api_salvar, {'categoria': 'turma'}, name='turma_atualizar'),
    path('turma/deletar/<int:item_id>/', views.api_deletar, {'categoria': 'turma'}, name='turma_deletar'),
]