# autenticacao/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    cargo = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    
    departamento_principal = models.ForeignKey(
        'core.Departamento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_principais'
    )
    foto_perfil = models.ImageField(
        upload_to='perfil/%Y/%m/',
        blank=True,
        null=True
    )
    data_admissao = models.DateField('Data de Admissão', null=True, blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    def __str__(self):
        return self.get_full_name() or self.username
    
    def get_departamentos(self):
        """Retorna lista de departamentos que o usuário tem acesso"""
        from core.models import get_departamentos_usuario
        return get_departamentos_usuario(self)
    
    def get_departamentos_slugs(self):
        """Retorna lista de slugs dos departamentos do usuário"""
        from core.models import get_departamentos_slugs_usuario
        return get_departamentos_slugs_usuario(self)
    
    def tem_acesso_departamento(self, departamento_slug):
        """Verifica se o usuário tem acesso a um departamento específico"""
        from core.models import tem_acesso_departamento
        return tem_acesso_departamento(self, departamento_slug)
    
    def get_nivel_acesso_departamento(self, departamento_slug):
        """Retorna o nível de acesso do usuário em um departamento"""
        from core.models import get_nivel_acesso_departamento
        return get_nivel_acesso_departamento(self, departamento_slug)
    
    def pode_editar_departamento(self, departamento_slug):
        """Verifica se o usuário pode editar no departamento"""
        from core.models import pode_editar_departamento
        return pode_editar_departamento(self, departamento_slug)
    
    def pode_gerenciar_departamento(self, departamento_slug):
        """Verifica se o usuário pode gerenciar no departamento"""
        from core.models import pode_gerenciar_departamento
        return pode_gerenciar_departamento(self, departamento_slug)
    
    def get_departamentos_info(self):
        """Retorna informações detalhadas dos departamentos do usuário"""
        from core.models import get_departamentos_do_usuario
        return get_departamentos_do_usuario(self)
    
    def tem_acesso_escola(self, escola_id):
        """Verifica se o usuário tem acesso a uma escola específica"""
        from escola.configuracao.models import UsuarioInstituicao
        if self.is_superuser:
            return True
        return UsuarioInstituicao.objects.filter(
            usuario=self,
            instituicao_id=escola_id,
            ativo=True
        ).exists()
    
    def get_escolas(self):
        """Retorna lista de escolas que o usuário tem acesso"""
        from escola.configuracao.models import UsuarioInstituicao, Instituicao
        if self.is_superuser:
            return Instituicao.objects.filter(ativo=True)
        
        return [ui.instituicao for ui in UsuarioInstituicao.objects.filter(
            usuario=self,
            ativo=True
        ).select_related('instituicao')]