# escola/configuracao/models.py
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
import uuid

class Instituicao(models.Model):
    """
    Modelo central para multi-tenancy - cada escola/cliente é uma instância
    """
    # ============================================
    # PROVÍNCIAS DE ANGOLA (OPÇÕES)
    # ============================================
    PROVINCIA_CHOICES = [
        ('AO-BGO', 'Bengo'),
        ('AO-BGU', 'Benguela'),
        ('AO-BIE', 'Bié'),
        ('AO-CAB', 'Cabinda'),
        ('AO-CCU', 'Cuando Cubango'),
        ('AO-CNO', 'Cuanza Norte'),
        ('AO-CUS', 'Cuanza Sul'),
        ('AO-CNN', 'Cunene'),
        ('AO-HUA', 'Huambo'),
        ('AO-HUI', 'Huíla'),
        ('AO-LUA', 'Luanda'),
        ('AO-LNO', 'Lunda Norte'),
        ('AO-LSU', 'Lunda Sul'),
        ('AO-MAL', 'Malanje'),
        ('AO-MOX', 'Moxico'),
        ('AO-NAM', 'Namibe'),
        ('AO-UIG', 'Uíge'),
        ('AO-ZAI', 'Zaire'),
    ]
    
    # Identificação
    nome = models.CharField('Nome da Instituição', max_length=200)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=200, blank=True)
    cnpj = models.CharField('NIF', max_length=18, unique=True)
    inscricao_estadual = models.CharField('Inscrição Estadual', max_length=20, blank=True)
    
    # Identificador único do tenant (usado no subdomínio ou path)
    slug = models.SlugField('Identificador', max_length=50, unique=True, 
                           help_text='Usado na URL: escola.slug.yitro.com')
    
    # Dados de contato
    email = models.EmailField('E-mail')
    telefone = models.CharField('Telefone', max_length=20)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    
    # Endereço
    endereco = models.TextField('Endereço')
    cidade = models.CharField('Cidade', max_length=100)
    # 🔥 CORRIGIDO: max_length=50 para aceitar nomes completos
    estado = models.CharField(
        'Província', 
        max_length=50,  # 🔥 MUDADO DE 2 PARA 50
        choices=PROVINCIA_CHOICES,
        default='AO-LUA'
    )
    cep = models.CharField('Código Postal', max_length=10, blank=True)  # 🔥 TORNADO OPCIONAL
    
    # Configurações visuais
    logo = models.ImageField(
        'Logo',
        upload_to='logos/%Y/%m/',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg'])],
        blank=True,
        null=True
    )
    cor_primaria = models.CharField('Cor Primária', max_length=7, default='#6C63FF')
    cor_secundaria = models.CharField('Cor Secundária', max_length=7, default='#FF6584')
    
    # Configurações fiscais
    regime_tributario = models.CharField(
        'Regime Tributário',
        max_length=20,
        choices=[
            ('SN', 'Simples Nacional'),
            ('MEI', 'MEI'),
            ('LP', 'Lucro Presumido'),
            ('LR', 'Lucro Real'),
        ],
        default='SN'
    )
    aliquota_iss = models.DecimalField('Alíquota ISS', max_digits=5, decimal_places=2, default=2.0)
    
    # Configurações do sistema
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    ativo = models.BooleanField('Ativo', default=True)
    plano = models.CharField(
        'Plano',
        max_length=20,
        choices=[
            ('BASIC', 'Básico'),
            ('PRO', 'Profissional'),
            ('ENTERPRISE', 'Enterprise'),
        ],
        default='BASIC'
    )
    
    # Configurações específicas (JSON para flexibilidade)
    configuracao_extra = models.JSONField('Configurações Extras', default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Instituição'
        verbose_name_plural = 'Instituições'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['cnpj']),
        ]
    
    def __str__(self):
        return f"{self.nome} ({self.slug})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.nome.lower().replace(' ', '-')[:50]
        super().save(*args, **kwargs)
    
    @property
    def logo_url(self):
        if self.logo:
            return self.logo.url
        return None
    
    @property
    def estado_nome(self):
        """Retorna o nome completo da província"""
        for codigo, nome in self.PROVINCIA_CHOICES:
            if codigo == self.estado:
                return nome
        return self.estado


class UsuarioInstituicao(models.Model):
    """
    Relaciona usuários com instituições - cada usuário pode ter acesso a múltiplas escolas
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instituicoes'
    )
    instituicao = models.ForeignKey(
        Instituicao,
        on_delete=models.CASCADE,
        related_name='usuarios'
    )
    
    # Perfis de acesso
    perfil = models.CharField(
        'Perfil',
        max_length=20,
        choices=[
            ('ADMIN', 'Administrador'),
            ('SECRETARIA', 'Secretaria'),
            ('DOCENTE', 'Docente'),
            ('PEDAGOGICO', 'Pedagógico'),
            ('FINANCEIRO', 'Financeiro'),
            ('ALUNO', 'Aluno'),
            ('RESPONSAVEL', 'Responsável'),
        ],
        default='SECRETARIA'
    )
    
    # Permissões específicas (JSON para flexibilidade)
    permissoes_extra = models.JSONField('Permissões Extras', default=dict, blank=True)
    
    data_atribuicao = models.DateTimeField('Data de Atribuição', auto_now_add=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Usuário da Instituição'
        verbose_name_plural = 'Usuários das Instituições'
        unique_together = ['usuario', 'instituicao']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.instituicao.nome} ({self.perfil})"