# clientes/models.py

from django.db import models
from django.utils import timezone


class Cliente(models.Model):
    """Cliente da empresa"""
    
    # Dados pessoais
    nome = models.CharField('Nome', max_length=255)
    nif = models.CharField('NIF', max_length=20, unique=True)
    endereco = models.TextField('Endereço', blank=True, null=True)
    email = models.EmailField('Email', blank=True, null=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True)
    
    # Status
    ativo = models.BooleanField('Ativo', default=True)
    
    # Datas
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nif']),
            models.Index(fields=['nome']),
            models.Index(fields=['ativo']),
        ]
    
    def __str__(self):
        return f"{self.nome} ({self.nif})"
    
    @property
    def esta_ativo(self):
        """Verifica se o cliente está ativo"""
        return self.ativo
    
    @property
    def total_faturas(self):
        """Retorna o total de faturas do cliente (se houver relacionamento)"""
        if hasattr(self, 'faturas'):
            return self.faturas.count()
        return 0
    
    @property
    def total_gasto(self):
        """Retorna o valor total gasto pelo cliente (se houver relacionamento)"""
        if hasattr(self, 'faturas'):
            return sum(fatura.valor_total for fatura in self.faturas.all())
        return 0