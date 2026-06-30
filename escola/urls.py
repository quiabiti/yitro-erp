from django.urls import path, include
from .pedagogico import views as pedagogico_views
from . import views as escola_views
from .secretaria import views as secretaria_views

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
    # 🔥 API PEDAGÓGICO
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
    
    # ANO LECTIVO
    path('api/pedagogico/ano_lectivo/listar/', pedagogico_views.api_listar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_listar'),
    path('api/pedagogico/ano_lectivo/criar/', pedagogico_views.api_form_criar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_criar'),
    path('api/pedagogico/ano_lectivo/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_editar'),
    path('api/pedagogico/ano_lectivo/salvar/', pedagogico_views.api_salvar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_salvar'),
    path('api/pedagogico/ano_lectivo/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_atualizar'),
    path('api/pedagogico/ano_lectivo/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'ano_lectivo'}, name='ano_lectivo_deletar'),
    
    # TRIMESTRE
    path('api/pedagogico/trimestre/listar/', pedagogico_views.api_listar, {'categoria': 'trimestre'}, name='trimestre_listar'),
    path('api/pedagogico/trimestre/criar/', pedagogico_views.api_form_criar, {'categoria': 'trimestre'}, name='trimestre_criar'),
    path('api/pedagogico/trimestre/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'trimestre'}, name='trimestre_editar'),
    path('api/pedagogico/trimestre/salvar/', pedagogico_views.api_salvar, {'categoria': 'trimestre'}, name='trimestre_salvar'),
    path('api/pedagogico/trimestre/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'trimestre'}, name='trimestre_atualizar'),
    path('api/pedagogico/trimestre/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'trimestre'}, name='trimestre_deletar'),
    
    # NÍVEL DE ENSINO
    path('api/pedagogico/nivel_ensino/listar/', pedagogico_views.api_listar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_listar'),
    path('api/pedagogico/nivel_ensino/criar/', pedagogico_views.api_form_criar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_criar'),
    path('api/pedagogico/nivel_ensino/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_editar'),
    path('api/pedagogico/nivel_ensino/salvar/', pedagogico_views.api_salvar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_salvar'),
    path('api/pedagogico/nivel_ensino/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_atualizar'),
    path('api/pedagogico/nivel_ensino/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'nivel_ensino'}, name='nivel_ensino_deletar'),
    
    # CLASSE
    path('api/pedagogico/classe/listar/', pedagogico_views.api_listar, {'categoria': 'classe'}, name='classe_listar'),
    path('api/pedagogico/classe/criar/', pedagogico_views.api_form_criar, {'categoria': 'classe'}, name='classe_criar'),
    path('api/pedagogico/classe/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'classe'}, name='classe_editar'),
    path('api/pedagogico/classe/salvar/', pedagogico_views.api_salvar, {'categoria': 'classe'}, name='classe_salvar'),
    path('api/pedagogico/classe/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'classe'}, name='classe_atualizar'),
    path('api/pedagogico/classe/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'classe'}, name='classe_deletar'),
    
    # DISCIPLINA
    path('api/pedagogico/disciplina/listar/', pedagogico_views.api_listar, {'categoria': 'disciplina'}, name='disciplina_listar'),
    path('api/pedagogico/disciplina/criar/', pedagogico_views.api_form_criar, {'categoria': 'disciplina'}, name='disciplina_criar'),
    path('api/pedagogico/disciplina/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'disciplina'}, name='disciplina_editar'),
    path('api/pedagogico/disciplina/salvar/', pedagogico_views.api_salvar, {'categoria': 'disciplina'}, name='disciplina_salvar'),
    path('api/pedagogico/disciplina/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'disciplina'}, name='disciplina_atualizar'),
    path('api/pedagogico/disciplina/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'disciplina'}, name='disciplina_deletar'),
    
    # TURMA
    path('api/pedagogico/turma/listar/', pedagogico_views.api_listar, {'categoria': 'turma'}, name='turma_listar'),
    path('api/pedagogico/turma/criar/', pedagogico_views.api_form_criar, {'categoria': 'turma'}, name='turma_criar'),
    path('api/pedagogico/turma/editar/<int:item_id>/', pedagogico_views.api_form_editar, {'categoria': 'turma'}, name='turma_editar'),
    path('api/pedagogico/turma/salvar/', pedagogico_views.api_salvar, {'categoria': 'turma'}, name='turma_salvar'),
    path('api/pedagogico/turma/salvar/<int:item_id>/', pedagogico_views.api_salvar, {'categoria': 'turma'}, name='turma_atualizar'),
    path('api/pedagogico/turma/deletar/<int:item_id>/', pedagogico_views.api_deletar, {'categoria': 'turma'}, name='turma_deletar'),
    
    # ============================================
    # 🔥 SECRETARIA GERAL - PÁGINAS (HTML)
    # ============================================
    path('secretaria/matriculas/', secretaria_views.secretaria_matriculas, name='secretaria_matriculas'),
    path('secretaria/pagamentos/', secretaria_views.secretaria_pagamentos, name='secretaria_pagamentos'),
    path('secretaria/alunos/', secretaria_views.secretaria_alunos, name='secretaria_alunos'),  # 🔥 ADICIONAR ESTA!
    path('secretaria/documentos/', secretaria_views.secretaria_documentos, name='secretaria_documentos'),
    
    # ============================================
    # 🔥 SECRETARIA GERAL - URLs da API (JSON)
    # ============================================
    # MATRÍCULAS
    path('api/secretaria/matriculas/', secretaria_views.api_matriculas_listar, name='api_matriculas_listar'),
    path('api/secretaria/matriculas/stats/', secretaria_views.api_matriculas_stats, name='api_matriculas_stats'),
    path('api/secretaria/matricula/form/', secretaria_views.api_matricula_form, name='api_matricula_form'),
    path('api/secretaria/matricula/form/<int:matricula_id>/', secretaria_views.api_matricula_form, name='api_matricula_form_edit'),
    path('api/secretaria/matricula/salvar/', secretaria_views.api_matricula_salvar, name='api_matricula_salvar'),
    path('api/secretaria/matricula/salvar/<int:matricula_id>/', secretaria_views.api_matricula_salvar, name='api_matricula_salvar_edit'),
    path('api/secretaria/matricula/confirmar/<int:matricula_id>/', secretaria_views.api_matricula_confirmar, name='api_matricula_confirmar'),
    path('api/secretaria/matricula/cancelar/<int:matricula_id>/', secretaria_views.api_matricula_cancelar, name='api_matricula_cancelar'),
    path('api/secretaria/matricula/trancar/<int:matricula_id>/', secretaria_views.api_matricula_trancar, name='api_matricula_trancar'),
    path('api/secretaria/matricula/deletar/<int:matricula_id>/', secretaria_views.api_matricula_deletar, name='api_matricula_deletar'),
    
    # ALUNOS
    path('api/secretaria/alunos/', secretaria_views.api_alunos_listar, name='api_alunos_listar'),
    path('api/secretaria/alunos/buscar/', secretaria_views.api_alunos_buscar, name='api_alunos_buscar'),
    path('api/secretaria/alunos/stats/', secretaria_views.api_alunos_stats, name='api_alunos_stats'),
    path('api/secretaria/alunos/historico/<int:aluno_id>/', secretaria_views.api_historico_aluno, name='api_historico_aluno'),
    
    # TURMAS
    path('api/secretaria/turmas/listar/', secretaria_views.api_turmas_listar, name='api_turmas_listar'),
    
    # IMPRESSÃO
    path('impressao/matricula/<int:matricula_id>/', secretaria_views.impressao_matricula, name='impressao_matricula'),
    
    # ============================================
    # 🔥 ÁREA ADMINISTRATIVA - URLs da API
    # ============================================
    path('api/admin/funcionarios/', escola_views.admin_funcionarios, name='api_admin_funcionarios'),
    path('api/admin/documentos/', escola_views.admin_documentos, name='api_admin_documentos'),
    path('api/admin/relatorios/', escola_views.admin_relatorios, name='api_admin_relatorios'),
    path('api/admin/custos/', escola_views.admin_custos, name='api_admin_custos'),
    path('api/admin/folha_salarial/', escola_views.admin_folha_salarial, name='api_admin_folha_salarial'),
    path('api/admin/usuarios/', escola_views.admin_usuarios, name='api_admin_usuarios'),
    
    # ============================================
    # 🔥 ÁREA FINANCEIRA - URLs da API
    # ============================================
    path('api/financeiro/relatorio/', escola_views.financeiro_relatorio, name='api_financeiro_relatorio'),
    path('api/financeiro/tributario/', escola_views.financeiro_tributario, name='api_financeiro_tributario'),
]