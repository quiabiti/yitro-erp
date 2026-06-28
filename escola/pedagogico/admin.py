from django.contrib import admin
from .models import AnoLectivo, Trimestre, NivelEnsino, Classe, Disciplina, Turma

@admin.register(AnoLectivo)
class AnoLectivoAdmin(admin.ModelAdmin):
    list_display = ['ano', 'data_inicio', 'data_fim', 'ativo', 'data_criacao']
    list_filter = ['ativo']
    search_fields = ['ano', 'descricao']
    date_hierarchy = 'data_criacao'
    ordering = ['-ano']

@admin.register(Trimestre)
class TrimestreAdmin(admin.ModelAdmin):
    list_display = ['ano_lectivo', 'numero', 'nome', 'data_inicio', 'data_fim', 'ativo']
    list_filter = ['ano_lectivo', 'numero', 'ativo']
    search_fields = ['nome', 'descricao']
    date_hierarchy = 'data_criacao'
    ordering = ['ano_lectivo', 'numero']

@admin.register(NivelEnsino)
class NivelEnsinoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ordem', 'ativo', 'data_criacao']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    ordering = ['ordem', 'nome']

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ['nome', 'nivel_ensino', 'ano_lectivo', 'ativo', 'data_criacao']  # Mudado de 'nivel' para 'nivel_ensino'
    list_filter = ['nivel_ensino', 'ano_lectivo', 'ativo']  # Mudado de 'nivel' para 'nivel_ensino'
    search_fields = ['nome', 'descricao']
    ordering = ['ano_lectivo', 'nivel_ensino', 'nome']

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'carga_horaria', 'classe', 'ativo', 'data_criacao']
    list_filter = ['classe', 'ativo']
    search_fields = ['nome', 'codigo', 'descricao']
    ordering = ['classe', 'nome']

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'classe', 'ano_lectivo', 'capacidade', 'ativo', 'data_criacao']
    list_filter = ['classe', 'ano_lectivo', 'ativo']
    search_fields = ['nome', 'codigo', 'descricao']
    ordering = ['ano_lectivo', 'classe', 'nome']
