# escola/configuracao/models.py
from django.db import models
from django.conf import settings  # 🔥 IMPORTANTE: usar settings.AUTH_USER_MODEL
from django.core.validators import FileExtensionValidator
import uuid

class Instituicao(models.Model):
    """
    Modelo central para multi-tenancy - cada escola/cliente é uma instância
    """
    # Identificação
    nome = models.CharField('Nome da Instituição', max_length=200)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=200, blank=True)
    cnpj = models.CharField('CNPJ', max_length=18, unique=True)
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
    estado = models.CharField('Estado', max_length=2)
    cep = models.CharField('CEP', max_length=10)
    
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


class UsuarioInstituicao(models.Model):
    """
    Relaciona usuários com instituições - cada usuário pode ter acesso a múltiplas escolas
    """
    # 🔥 CORRIGIDO: Usar settings.AUTH_USER_MODEL em vez de User diretamente
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 🔥 ISSO É O CORRETO!
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