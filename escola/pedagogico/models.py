# escola/pedagogico/models.py
from django.db import models
from django.utils import timezone

class AnoLectivo(models.Model):
    # 🔥 ADICIONAR ESTE CAMPO
    tenant_id = models.IntegerField('ID da Escola', db_index=True, null=True, blank=True, help_text='ID da instituição/tenant')
    
    ano = models.CharField('Ano', max_length=9, unique=True, help_text='Ex: 2024/2025')
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Fim')
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)

    class Meta:
        verbose_name = 'Ano Lectivo'
        verbose_name_plural = 'Anos Lectivos'
        ordering = ['-ano']
        # 🔥 REMOVA O unique=True do campo 'ano' se existir
        # unique_together = [['tenant_id', 'ano']]  # ← ADICIONAR

    def __str__(self):
        return self.ano


class Trimestre(models.Model):
    # 🔥 ADICIONAR ESTE CAMPO
    tenant_id = models.IntegerField('ID da Escola', db_index=True, null=True, blank=True, help_text='ID da instituição/tenant')
    
    NUMERO_CHOICES = [
        (1, '1º Trimestre'),
        (2, '2º Trimestre'),
        (3, '3º Trimestre'),
    ]

    ano_lectivo = models.ForeignKey(AnoLectivo, on_delete=models.CASCADE, related_name='trimestres')
    numero = models.IntegerField('Número', choices=NUMERO_CHOICES)
    nome = models.CharField('Nome', max_length=50)
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Fim')
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)

    class Meta:
        verbose_name = 'Trimestre'
        verbose_name_plural = 'Trimestres'
        ordering = ['ano_lectivo', 'numero']
        unique_together = [['tenant_id', 'ano_lectivo', 'numero']]  # 🔥 ALTERAR

    def __str__(self):
        return f"{self.ano_lectivo.ano} - {self.get_numero_display()}"


class NivelEnsino(models.Model):
    # 🔥 ADICIONAR ESTE CAMPO
    tenant_id = models.IntegerField('ID da Escola', db_index=True, null=True, blank=True, help_text='ID da instituição/tenant')
    
    nome = models.CharField('Nome', max_length=100, help_text='Ex: Ensino Fundamental, Ensino Médio')
    descricao = models.TextField('Descrição', blank=True)
    ordem = models.IntegerField('Ordem de Exibição', default=0, help_text='Números menores aparecem primeiro')
    ativo = models.BooleanField('Ativo', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)

    class Meta:
        verbose_name = 'Nível de Ensino'
        verbose_name_plural = 'Níveis de Ensino'
        ordering = ['ordem', 'nome']
        unique_together = [['tenant_id', 'nome']]  # 🔥 ALTERAR

    def __str__(self):
        return self.nome


class Classe(models.Model):
    # 🔥 ADICIONAR ESTE CAMPO
    tenant_id = models.IntegerField('ID da Escola', db_index=True, null=True, blank=True, help_text='ID da instituição/tenant')
    
    nome = models.CharField('Nome', max_length=50, help_text='Ex: 1º Ano A')
    nivel_ensino = models.ForeignKey(
        NivelEnsino, 
        on_delete=models.CASCADE, 
        related_name='classes',
        verbose_name='Nível de Ensino'
    )
    ano_lectivo = models.ForeignKey(AnoLectivo, on_delete=models.CASCADE, related_name='classes')
    descricao = models.TextField('Descrição', blank=True)
    is_exame = models.BooleanField('Classe de Exame', default=False, help_text='Indica se esta classe possui exames finais')
    ativo = models.BooleanField('Ativo', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)

    class Meta:
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        ordering = ['ano_lectivo', 'nivel_ensino', 'nome']
        unique_together = [['tenant_id', 'ano_lectivo', 'nivel_ensino', 'nome']]  # 🔥 ALTERAR

    def __str__(self):
        return f"{self.nome} ({self.nivel_ensino.nome})"


class Disciplina(models.Model):
    # 🔥 ADICIONAR ESTE CAMPO
    tenant_id = models.IntegerField('ID da Escola', db_index=True, null=True, blank=True, help_text='ID da instituição/tenant')
    
    TIPO_CHOICES = [
        ('curricular', 'Curricular'),
        ('extra_curricular', 'Extra-Curricular'),
        ('opcional', 'Opcional'),
    ]
    
    nome = models.CharField('Nome', max_length=100)
    codigo = models.CharField('Código', max_length=20)
    carga_horaria = models.IntegerField('Carga Horária (horas)', default=60)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='disciplinas')
    descricao = models.TextField('Descrição', blank=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, default='curricular')
    is_chave = models.BooleanField('Disciplina Chave', default=False, help_text='Disciplina fundamental para o currículo')
    ativo = models.BooleanField('Ativo', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)

    class Meta:
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        ordering = ['classe', 'nome']
        unique_together = [['tenant_id', 'classe', 'nome']]  # 🔥 ALTERAR

    def __str__(self):
        return f"{self.nome} ({self.codigo})"


class Turma(models.Model):
    # 🔥 ADICIONAR ESTE CAMPO
    tenant_id = models.IntegerField('ID da Escola', db_index=True, null=True, blank=True, help_text='ID da instituição/tenant')
    
    nome = models.CharField('Nome', max_length=50)
    codigo = models.CharField('Código', max_length=20)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='turmas')
    ano_lectivo = models.ForeignKey(AnoLectivo, on_delete=models.CASCADE, related_name='turmas')
    capacidade = models.IntegerField('Capacidade', default=30)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering = ['ano_lectivo', 'classe', 'nome']
        unique_together = [['tenant_id', 'ano_lectivo', 'classe', 'nome']]  # 🔥 ALTERAR

    def __str__(self):
        return f"{self.nome} - {self.classe.nome}"