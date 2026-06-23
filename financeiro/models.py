# financeiro/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import hashlib
import json

User = get_user_model()


class Empresa(models.Model):
    """Empresa que utiliza o sistema"""
    nome = models.CharField('Nome', max_length=200)
    nif = models.CharField('NIF', max_length=20, unique=True)
    endereco = models.TextField('Endereço', blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


# ============================================
# 🔥 CLIENTE REMOVIDO - Usar o do app clientes
# ============================================


class Produto(models.Model):
    """Produto/Serviço para faturação"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='produtos', null=True, blank=True)
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    codigo = models.CharField('Código', max_length=50, blank=True)
    preco = models.DecimalField('Preço Unitário', max_digits=12, decimal_places=2, default=0)
    iva = models.DecimalField('IVA (%)', max_digits=5, decimal_places=2, default=14)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.preco} Kz"


class Fatura(models.Model):
    """Fatura emitida para cliente"""
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADA', 'Aprovada'),
        ('REJEITADA', 'Rejeitada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='faturas', null=True, blank=True)
    # 🔥 FK APONTANDO PARA O APP CLIENTES
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, related_name='faturas')
    numero = models.CharField('Nº Fatura', max_length=50, unique=True)
    data_emissao = models.DateField('Data de Emissão', default=timezone.now)
    data_vencimento = models.DateField('Data de Vencimento', null=True, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    valor_total = models.DecimalField('Valor Total', max_digits=12, decimal_places=2, default=0)
    valor_iva = models.DecimalField('Valor IVA', max_digits=12, decimal_places=2, default=0)
    valor_liquido = models.DecimalField('Valor Líquido', max_digits=12, decimal_places=2, default=0)
    hash_controlo = models.CharField('Hash de Controlo', max_length=100, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='faturas_criadas')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturas'
        ordering = ['-data_emissao']
    
    def __str__(self):
        return f"{self.numero} - {self.cliente.nome}"
    
    def save(self, *args, **kwargs):
        # Calcular totais
        self.valor_total = sum(item.total for item in self.itens.all()) if self.pk else 0
        self.valor_iva = self.valor_total * 0.14
        self.valor_liquido = self.valor_total + self.valor_iva
        
        # Gerar hash de controlo
        if not self.hash_controlo:
            dados = f"{self.numero}{self.cliente.nif}{self.valor_total}{self.data_emissao}"
            self.hash_controlo = hashlib.sha256(dados.encode()).hexdigest()[:32]
        
        super().save(*args, **kwargs)
    
    @property
    def itens_count(self):
        return self.itens.count()


class ItemFatura(models.Model):
    """Item da fatura"""
    fatura = models.ForeignKey(Fatura, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='itens_fatura', null=True, blank=True)
    descricao = models.CharField('Descrição', max_length=200)
    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=2, default=1)
    preco_unitario = models.DecimalField('Preço Unitário', max_digits=12, decimal_places=2)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item da Fatura'
        verbose_name_plural = 'Itens da Fatura'
    
    def __str__(self):
        return f"{self.descricao} - {self.quantidade} x {self.preco_unitario}"
    
    def save(self, *args, **kwargs):
        self.total = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)