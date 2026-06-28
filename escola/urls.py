from django.urls import path, include
from .pedagogico import views as pedagogico_views
from . import views as escola_views

app_name = 'escola'

urlpatterns = [
    # ============================================
    # 🏫 LISTA DE ESCOLAS (ACESSADO PELO MENU)
    # ============================================
    path('', escola_views.api_escolas_listar, name='lista_escolas'),
    
    # ============================================
    # 🏫 AMBIENTE DA ESCOLA (DASHBOARD DA ESCOLA)
    # ============================================
    path('ambiente/', escola_views.index, name='ambiente'),
    
    # ============================================
    # 🎯 ENTRAR NA ESCOLA (REDIRECIONA PARA O AMBIENTE)
    # ============================================
    path('entrar/<slug:slug>/', escola_views.entrar_escola, name='entrar_escola'),
    
    # ============================================
    # 🔥 API DASHBOARD
    # ============================================
    path('api/dashboard/', escola_views.api_dashboard, name='api_dashboard'),
    
    # ============================================
    # 🔥 API PEDAGÓGICO (NOVA URL - ADICIONADA)
    # ============================================
    path('api/pedagogico/', pedagogico_views.api_pedagogico_dashboard, name='api_pedagogico'),
    
    # ============================================
    # API DAS ESCOLAS (CRUD)
    # ============================================
    path('api/escolas/nova/', escola_views.api_escola_nova, name='nova_escola'),
    path('api/escolas/editar/<int:escola_id>/', escola_views.api_escola_editar, name='editar_escola'),
    path('api/escolas/salvar/', escola_views.api_escola_salvar, name='salvar_escola'),
    path('api/escolas/salvar/<int:escola_id>/', escola_views.api_escola_salvar, name='salvar_escola'),
    path('api/escolas/deletar/<int:escola_id>/', escola_views.api_escola_deletar, name='deletar_escola'),
    
    # ============================================
    # PEDAGÓGICO - URLs da API
    # ============================================
    path('api/pedagogico/stats/', pedagogico_views.api_stats, name='api_stats'),
    
    # ============================================
    # ANO LECTIVO
    # ============================================
    path('api/pedagogico/ano_lectivo/listar/', pedagogico_views.api_listar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_listar'),
    path('api/pedagogico/ano_lectivo/criar/', pedagogico_views.api_form_criar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_criar'),
    path('api/pedagogico/ano_lectivo/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_editar'),
    path('api/pedagogico/ano_lectivo/salvar/', pedagogico_views.api_salvar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_salvar'),
    path('api/pedagogico/ano_lectivo/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_atualizar'),
    path('api/pedagogico/ano_lectivo/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_deletar'),
    
    # ============================================
    # TRIMESTRE
    # ============================================
    path('api/pedagogico/trimestre/listar/', pedagogico_views.api_listar, {'categoria': 'trimestre'}, name='trimestre_listar'),
    path('api/pedagogico/trimestre/criar/', pedagogico_views.api_form_criar, {'categoria': 'trimestre'}, name='trimestre_criar'),
    path('api/pedagogico/trimestre/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'trimestre'}, name='trimestre_editar'),
    path('api/pedagogico/trimestre/salvar/', pedagogico_views.api_salvar, {'categoria': 'trimestre'}, name='trimestre_salvar'),
    path('api/pedagogico/trimestre/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'trimestre'}, name='trimestre_atualizar'),
    path('api/pedagogico/trimestre/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'trimestre'}, name='trimestre_deletar'),
    
    # ============================================
    # NÍVEL DE ENSINO
    # ============================================
    path('api/pedagogico/nivel_ensino/listar/', pedagogico_views.api_listar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_listar'),
    path('api/pedagogico/nivel_ensino/criar/', pedagogico_views.api_form_criar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_criar'),
    path('api/pedagogico/nivel_ensino/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_editar'),
    path('api/pedagogico/nivel_ensino/salvar/', pedagogico_views.api_salvar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_salvar'),
    path('api/pedagogico/nivel_ensino/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_atualizar'),
    path('api/pedagogico/nivel_ensino/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_deletar'),
    
    # ============================================
    # CLASSE
    # ============================================
    path('api/pedagogico/classe/listar/', pedagogico_views.api_listar, {'categoria': 'classe'}, name='classe_listar'),
    path('api/pedagogico/classe/criar/', pedagogico_views.api_form_criar, {'categoria': 'classe'}, name='classe_criar'),
    path('api/pedagogico/classe/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'classe'}, name='classe_editar'),
    path('api/pedagogico/classe/salvar/', pedagogico_views.api_salvar, {'categoria': 'classe'}, name='classe_salvar'),
    path('api/pedagogico/classe/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'classe'}, name='classe_atualizar'),
    path('api/pedagogico/classe/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'classe'}, name='classe_deletar'),
    
    # ============================================
    # DISCIPLINA
    # ============================================
    path('api/pedagogico/disciplina/listar/', pedagogico_views.api_listar, {'categoria': 'disciplina'}, name='disciplina_listar'),
    path('api/pedagogico/disciplina/criar/', pedagogico_views.api_form_criar, {'categoria': 'disciplina'}, name='disciplina_criar'),
    path('api/pedagogico/disciplina/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'disciplina'}, name='disciplina_editar'),
    path('api/pedagogico/disciplina/salvar/', pedagogico_views.api_salvar, {'categoria': 'disciplina'}, name='disciplina_salvar'),
    path('api/pedagogico/disciplina/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'disciplina'}, name='disciplina_atualizar'),
    path('api/pedagogico/disciplina/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'disciplina'}, name='disciplina_deletar'),
    
    # ============================================
    # TURMA
    # ============================================
    path('api/pedagogico/turma/listar/', pedagogico_views.api_listar, {'categoria': 'turma'}, name='turma_listar'),
    path('api/pedagogico/turma/criar/', pedagogico_views.api_form_criar, {'categoria': 'turma'}, name='turma_criar'),
    path('api/pedagogico/turma/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'turma'}, name='turma_editar'),
    path('api/pedagogico/turma/salvar/', pedagogico_views.api_salvar, {'categoria': 'turma'}, name='turma_salvar'),
    path('api/pedagogico/turma/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'turma'}, name='turma_atualizar'),
    path('api/pedagogico/turma/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'turma'}, name='turma_deletar'),
]