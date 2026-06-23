# clientes/admin.py

from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'nif', 'telefone', 'email', 'ativo', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'nif', 'email', 'telefone']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    ordering = ['nome']
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'nif', 'endereco', 'telefone', 'email')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )