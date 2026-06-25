# autenticacao/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    cargo = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    
    # Campos adicionais para o sistema Yitro
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
        if self.is_superuser:
            from core.models import Departamento
            return Departamento.objects.filter(ativo=True)
        
        from core.models import UsuarioDepartamento
        return [ud.departamento for ud in UsuarioDepartamento.objects.filter(
            usuario=self,
            ativo=True
        ).select_related('departamento')]
    
    def get_departamentos_slugs(self):
        """Retorna lista de slugs dos departamentos do usuário"""
        return [dep.slug for dep in self.get_departamentos()]
    
    def tem_acesso_departamento(self, departamento_slug):
        """Verifica se o usuário tem acesso a um departamento específico"""
        if self.is_superuser:
            return True
        
        from core.models import UsuarioDepartamento
        return UsuarioDepartamento.objects.filter(
            usuario=self,
            departamento__slug=departamento_slug,
            ativo=True
        ).exists()
    
    def get_nivel_acesso_departamento(self, departamento_slug):
        """Retorna o nível de acesso do usuário em um departamento"""
        if self.is_superuser:
            return 'ADMIN'
        
        from core.models import UsuarioDepartamento
        try:
            ud = UsuarioDepartamento.objects.get(
                usuario=self,
                departamento__slug=departamento_slug,
                ativo=True
            )
            return ud.nivel_acesso
        except UsuarioDepartamento.DoesNotExist:
            return None
    
    def pode_editar_departamento(self, departamento_slug):
        """Verifica se o usuário pode editar no departamento"""
        nivel = self.get_nivel_acesso_departamento(departamento_slug)
        return nivel in ['EDIT', 'MANAGE', 'ADMIN'] or self.is_superuser
    
    def pode_gerenciar_departamento(self, departamento_slug):
        """Verifica se o usuário pode gerenciar no departamento"""
        nivel = self.get_nivel_acesso_departamento(departamento_slug)
        return nivel in ['MANAGE', 'ADMIN'] or self.is_superuser