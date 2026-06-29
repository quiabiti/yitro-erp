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
    list_display = ['nome', 'nivel_ensino', 'ano_lectivo', 'ativo', 'data_criacao']
    list_filter = ['nivel_ensino', 'ano_lectivo', 'ativo']
    search_fields = ['nome', 'descricao']
    ordering = ['ano_lectivo', 'nivel_ensino', 'nome']


# 🔥 ADMIN DE DISCIPLINA CORRIGIDO
@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    # 🔥 REMOVER 'classe' e adicionar 'get_classes_display'
    list_display = [
        'nome', 
        'codigo', 
        'get_classes_display',  # 🔥 Método para exibir as classes
        'carga_horaria', 
        'tipo', 
        'is_chave',
        'ativo', 
        'data_criacao'
    ]
    
    # 🔥 REMOVER 'classe' do list_filter
    list_filter = ['tipo', 'is_chave', 'ativo']
    
    search_fields = ['nome', 'codigo', 'descricao']
    
    date_hierarchy = 'data_criacao'
    
    # 🔥 REMOVER 'classe' do ordering
    ordering = ['nome']
    
    # 🔥 Para ManyToMany no admin
    filter_horizontal = ['classes']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'codigo', 'descricao')
        }),
        ('Configurações', {
            'fields': ('classes', 'carga_horaria', 'tipo', 'is_chave', 'ativo')
        }),
    )
    
    def get_classes_display(self, obj):
        """Retorna as classes associadas à disciplina"""
        classes = obj.classes.all()
        if classes:
            return ", ".join([c.nome for c in classes])
        return "Nenhuma classe associada"
    get_classes_display.short_description = 'Classes Associadas'


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'classe', 'ano_lectivo', 'capacidade', 'ativo', 'data_criacao']
    list_filter = ['classe', 'ano_lectivo', 'ativo']
    search_fields = ['nome', 'codigo', 'descricao']
    date_hierarchy = 'data_criacao'
    ordering = ['ano_lectivo', 'classe', 'nome']