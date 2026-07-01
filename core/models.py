# core/models.py

from django.db import models
from django.conf import settings

class Departamento(models.Model):
    """Departamentos da Yitro"""
    nome = models.CharField('Nome', max_length=100)
    slug = models.SlugField('Identificador', max_length=50, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    icone = models.CharField('Ícone CSS', max_length=50, blank=True, 
                            help_text='Classe CSS do ícone (ex: fa-store)')
    ativo = models.BooleanField('Ativo', default=True)
    ordem = models.IntegerField('Ordem de Exibição', default=0)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['ordem', 'nome']
        db_table = 'core_departamento'
    
    def __str__(self):
        return self.nome
    
    def get_url_prefix(self):
        """Retorna o prefixo da URL do departamento"""
        return f'/{self.slug}/'


# ============================================
# 🔥 DESCOMENTADO - MODELO DE ASSOCIAÇÃO
# ============================================

class UsuarioDepartamento(models.Model):
    """Associação usuário-departamento com níveis de acesso"""
    
    NIVEL_ACESSO = [
        ('VIEW', 'Visualizar'),
        ('EDIT', 'Editar'),
        ('MANAGE', 'Gerenciar'),
        ('ADMIN', 'Administrador'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='departamentos_associados'
    )
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='usuarios_associados'
    )
    nivel_acesso = models.CharField(
        'Nível de Acesso',
        max_length=20,
        choices=NIVEL_ACESSO,
        default='VIEW'
    )
    ativo = models.BooleanField('Ativo', default=True)
    data_atribuicao = models.DateTimeField('Data de Atribuição', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Usuário por Departamento'
        verbose_name_plural = 'Usuários por Departamento'
        unique_together = ['usuario', 'departamento']
        db_table = 'core_usuario_departamento'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.departamento.nome} ({self.get_nivel_acesso_display()})"


# ============================================
# 🔥 DESCOMENTADO - FUNÇÕES AUXILIARES
# ============================================

def get_departamentos_usuario(usuario):
    """
    Retorna lista de departamentos que o usuário tem acesso
    """
    if usuario.is_superuser:
        return Departamento.objects.filter(ativo=True)
    
    return [ud.departamento for ud in UsuarioDepartamento.objects.filter(
        usuario=usuario,
        ativo=True
    ).select_related('departamento')]


def get_departamentos_slugs_usuario(usuario):
    """
    Retorna lista de slugs dos departamentos do usuário
    """
    return [dep.slug for dep in get_departamentos_usuario(usuario)]


def tem_acesso_departamento(usuario, departamento_slug):
    """
    Verifica se o usuário tem acesso a um departamento específico
    """
    if usuario.is_superuser:
        return True
    
    return UsuarioDepartamento.objects.filter(
        usuario=usuario,
        departamento__slug=departamento_slug,
        ativo=True
    ).exists()


def get_nivel_acesso_departamento(usuario, departamento_slug):
    """
    Retorna o nível de acesso do usuário em um departamento
    """
    if usuario.is_superuser:
        return 'ADMIN'
    
    try:
        ud = UsuarioDepartamento.objects.get(
            usuario=usuario,
            departamento__slug=departamento_slug,
            ativo=True
        )
        return ud.nivel_acesso
    except UsuarioDepartamento.DoesNotExist:
        return None


def pode_editar_departamento(usuario, departamento_slug):
    """
    Verifica se o usuário pode editar no departamento
    """
    nivel = get_nivel_acesso_departamento(usuario, departamento_slug)
    return nivel in ['EDIT', 'MANAGE', 'ADMIN'] or usuario.is_superuser


def pode_gerenciar_departamento(usuario, departamento_slug):
    """
    Verifica se o usuário pode gerenciar no departamento
    """
    nivel = get_nivel_acesso_departamento(usuario, departamento_slug)
    return nivel in ['MANAGE', 'ADMIN'] or usuario.is_superuser


def get_departamentos_do_usuario(usuario):
    """
    Retorna um dicionário com informações dos departamentos do usuário
    """
    if usuario.is_superuser:
        deps = Departamento.objects.filter(ativo=True)
    else:
        deps = [ud.departamento for ud in UsuarioDepartamento.objects.filter(
            usuario=usuario,
            ativo=True
        ).select_related('departamento')]
    
    result = []
    for dep in deps:
        result.append({
            'id': dep.id,
            'nome': dep.nome,
            'slug': dep.slug,
            'icone': dep.icone,
            'nivel_acesso': get_nivel_acesso_departamento(usuario, dep.slug),
        })
    
    return result