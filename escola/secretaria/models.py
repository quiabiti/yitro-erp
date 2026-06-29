# escola/secretaria/models.py

from django.db import models
from django.contrib.auth import get_user_model
from escola.configuracao.models import Instituicao
from escola.pedagogico.models import Classe, Turma, Disciplina, AnoLectivo
import logging
from datetime import date, datetime

logger = logging.getLogger(__name__)
User = get_user_model()


class Aluno(models.Model):
    """Modelo para Alunos - Dados do BI Angolano"""
    tenant_id = models.IntegerField('ID da Escola', db_index=True, null=True, blank=True)
    
    # Dados do BI (Documento Principal)
    nome_completo = models.CharField('Nome Completo', max_length=200)
    data_nascimento = models.DateField('Data de Nascimento')
    genero = models.CharField('Gênero', max_length=10, choices=[
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ], default='M')
    naturalidade = models.CharField('Naturalidade', max_length=100, blank=True)
    nacionalidade = models.CharField('Nacionalidade', max_length=50, default='Angola')
    bi = models.CharField('BI', max_length=20, unique=True)
    nif = models.CharField('NIF', max_length=20, blank=True, null=True)
    data_emissao_bi = models.DateField('Data de Emissão do BI', null=True, blank=True)
    data_validade_bi = models.DateField('Data de Validade do BI', null=True, blank=True)
    
    # Contato
    email = models.EmailField('E-mail', blank=True, null=True)
    telefone = models.CharField('Telefone', max_length=20)
    endereco = models.TextField('Endereço', blank=True)
    
    # Responsáveis (Filiação - conforme BI)
    nome_pai = models.CharField('Nome do Pai', max_length=200, blank=True)
    nome_mae = models.CharField('Nome da Mãe', max_length=200, blank=True)
    telefone_responsavel = models.CharField('Telefone do Responsável', max_length=20, blank=True)
    email_responsavel = models.EmailField('E-mail do Responsável', blank=True)
    
    # Vínculo com usuário (futuro login)
    usuario = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='aluno')
    
    # Dados acadêmicos (via matrícula atual)
    # Estes campos são preenchidos automaticamente pela matrícula ativa
    
    # Controle
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['nome_completo']
        unique_together = [['tenant_id', 'bi']]
        indexes = [
            models.Index(fields=['tenant_id', 'ativo']),
            models.Index(fields=['tenant_id', 'bi']),
            models.Index(fields=['tenant_id', 'nome_completo']),
        ]

    def __str__(self):
        return f"{self.nome_completo} ({self.bi})"
    
    def get_idade(self):
        """Calcula a idade do aluno de forma segura"""
        data = self.data_nascimento
        if not data:
            return 0
        
        # 🔥 Se for string, converter para date
        if isinstance(data, str):
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    data = datetime.strptime(data, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                return 0
        
        # 🔥 Se for objeto date ou datetime
        if hasattr(data, 'year'):
            today = date.today()
            return today.year - data.year - ((today.month, today.day) < (data.month, data.day))
        
        return 0
    
    def get_matricula_atual(self):
        """Retorna a matrícula ativa do aluno"""
        return self.matriculas.filter(ativo=True, status__in=['pendente', 'confirmada']).first()
    
    def get_ultima_matricula(self):
        """Retorna a última matrícula do aluno"""
        return self.matriculas.filter(ativo=True).order_by('-ano_lectivo__ano').first()
    
    def get_classe_atual(self):
        """Retorna a classe atual do aluno"""
        matricula = self.get_matricula_atual()
        return matricula.classe if matricula else None
    
    def get_turma_atual(self):
        """Retorna a turma atual do aluno"""
        matricula = self.get_matricula_atual()
        return matricula.turma if matricula else None
    
    def get_ano_lectivo_atual(self):
        """Retorna o ano lectivo atual do aluno"""
        matricula = self.get_matricula_atual()
        return matricula.ano_lectivo if matricula else None
    
    # 🔥 Função segura para formatar datas
    def safe_strftime(self, value, format='%d/%m/%Y'):
        """Converte data para string de forma segura"""
        if not value:
            return None
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        if isinstance(value, str):
            # Tenta diferentes formatos de data
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    return datetime.strptime(value, fmt).strftime(format)
                except ValueError:
                    continue
            return value
        return str(value)
    
    def to_dict(self):
        """Retorna dados do aluno em dicionário (otimizado para API)"""
        matricula = self.get_matricula_atual()
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'bi': self.bi,
            'nif': self.nif,
            'data_nascimento': self.safe_strftime(self.data_nascimento),
            'idade': self.get_idade(),
            'genero': self.genero,
            'naturalidade': self.naturalidade,
            'nacionalidade': self.nacionalidade,
            'telefone': self.telefone,
            'email': self.email,
            'endereco': self.endereco,
            'nome_pai': self.nome_pai,
            'nome_mae': self.nome_mae,
            'telefone_responsavel': self.telefone_responsavel,
            'email_responsavel': self.email_responsavel,
            'classe': matricula.classe.nome if matricula and matricula.classe else None,
            'classe_id': matricula.classe.id if matricula and matricula.classe else None,
            'turma': matricula.turma.nome if matricula and matricula.turma else None,
            'turma_id': matricula.turma.id if matricula and matricula.turma else None,
            'ano_lectivo': str(matricula.ano_lectivo) if matricula and matricula.ano_lectivo else None,
            'ano_lectivo_id': matricula.ano_lectivo.id if matricula and matricula.ano_lectivo else None,
            'status_matricula': matricula.status if matricula else None,
            'ativo': self.ativo,
        }


class Matricula(models.Model):
    """Modelo para Matrículas"""
    tenant_id = models.IntegerField('ID da Escola', db_index=True, null=True, blank=True)
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('trancada', 'Trancada'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ]
    
    TIPO_CHOICES = [
        ('nova', 'Nova Matrícula'),
        ('renovacao', 'Renovação'),
        ('transferencia', 'Transferência'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='matriculas')
    ano_lectivo = models.ForeignKey(AnoLectivo, on_delete=models.CASCADE, related_name='matriculas')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='matriculas')
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, related_name='matriculas', null=True, blank=True)
    
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, default='nova')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    data_matricula = models.DateField('Data da Matrícula', auto_now_add=True)
    data_confirmacao = models.DateField('Data da Confirmação', null=True, blank=True)
    data_cancelamento = models.DateField('Data do Cancelamento', null=True, blank=True)
    
    # Matrícula anterior (para transferências/renovações)
    matricula_anterior = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='matriculas_seguintes')
    
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        ordering = ['-data_matricula']
        unique_together = [['tenant_id', 'aluno', 'ano_lectivo']]
        indexes = [
            models.Index(fields=['tenant_id', 'status']),
            models.Index(fields=['tenant_id', 'ano_lectivo']),
            models.Index(fields=['tenant_id', 'aluno']),
            models.Index(fields=['tenant_id', 'classe']),
            models.Index(fields=['tenant_id', 'turma']),
        ]

    def __str__(self):
        return f"{self.aluno.nome_completo} - {self.ano_lectivo.ano} ({self.status})"
    
    def get_status_display(self):
        """Retorna o status com emoji"""
        emojis = {
            'pendente': '⏳ Pendente',
            'confirmada': '✅ Confirmada',
            'trancada': '⏸️ Trancada',
            'cancelada': '❌ Cancelada',
            'concluida': '🎓 Concluída',
        }
        return emojis.get(self.status, self.status)
    
    def confirmar(self):
        """Confirma a matrícula"""
        self.status = 'confirmada'
        self.data_confirmacao = date.today()
        self.save()
    
    def cancelar(self):
        """Cancela a matrícula"""
        self.status = 'cancelada'
        self.data_cancelamento = date.today()
        self.ativo = False
        self.save()
    
    def trancar(self):
        """Tranca a matrícula"""
        self.status = 'trancada'
        self.ativo = False
        self.save()
    
    def concluir(self):
        """Conclui a matrícula"""
        self.status = 'concluida'
        self.ativo = False
        self.save()
    
    # 🔥 Função segura para formatar datas
    def safe_strftime(self, value, format='%d/%m/%Y'):
        """Converte data para string de forma segura"""
        if not value:
            return None
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        if isinstance(value, str):
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    return datetime.strptime(value, fmt).strftime(format)
                except ValueError:
                    continue
            return value
        return str(value)
    
    def to_dict(self):
        """Retorna dados da matrícula em dicionário (otimizado para API)"""
        return {
            'id': self.id,
            'aluno_id': self.aluno.id,
            'aluno_nome': self.aluno.nome_completo,
            'aluno_bi': self.aluno.bi,
            'ano_lectivo': str(self.ano_lectivo),
            'ano_lectivo_id': self.ano_lectivo.id,
            'classe': self.classe.nome if self.classe else None,
            'classe_id': self.classe.id if self.classe else None,
            'turma': self.turma.nome if self.turma else None,
            'turma_id': self.turma.id if self.turma else None,
            'tipo': self.tipo,
            'tipo_display': dict(self.TIPO_CHOICES).get(self.tipo, self.tipo),
            'status': self.status,
            'status_display': self.get_status_display(),
            'data_matricula': self.safe_strftime(self.data_matricula),
            'data_confirmacao': self.safe_strftime(self.data_confirmacao),
            'data_cancelamento': self.safe_strftime(self.data_cancelamento),
            'observacoes': self.observacoes,
            'ativo': self.ativo,
        }


class HistoricoAluno(models.Model):
    """Modelo para Histórico Escolar do Aluno (Visão Agregada)"""
    tenant_id = models.IntegerField('ID da Escola', db_index=True, null=True, blank=True)
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='historico')
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='historico')
    
    ano_lectivo = models.ForeignKey(AnoLectivo, on_delete=models.CASCADE, related_name='historico_alunos')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='historico_alunos')
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, blank=True, related_name='historico_alunos')
    
    status = models.CharField('Status da Matrícula', max_length=20, choices=Matricula.STATUS_CHOICES)
    
    # Dados do Pedagógico
    aprovado = models.BooleanField('Aprovado', default=False)
    media_final = models.DecimalField('Média Final', max_digits=5, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Histórico do Aluno'
        verbose_name_plural = 'Histórico dos Alunos'
        ordering = ['-ano_lectivo']
        unique_together = [['tenant_id', 'aluno', 'ano_lectivo']]
        indexes = [
            models.Index(fields=['tenant_id', 'aluno']),
            models.Index(fields=['tenant_id', 'ano_lectivo']),
            models.Index(fields=['tenant_id', 'aluno', 'ano_lectivo']),
        ]

    def __str__(self):
        return f"{self.aluno.nome_completo} - {self.ano_lectivo.ano} ({self.status})"
    
    # 🔥 Função segura para formatar datas
    def safe_strftime(self, value, format='%d/%m/%Y'):
        """Converte data para string de forma segura"""
        if not value:
            return None
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        if isinstance(value, str):
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    return datetime.strptime(value, fmt).strftime(format)
                except ValueError:
                    continue
            return value
        return str(value)
    
    def to_dict(self):
        """Retorna dados do histórico em dicionário (otimizado para API)"""
        return {
            'id': self.id,
            'aluno_id': self.aluno.id,
            'aluno_nome': self.aluno.nome_completo,
            'ano_lectivo': str(self.ano_lectivo),
            'ano_lectivo_id': self.ano_lectivo.id,
            'classe': self.classe.nome if self.classe else None,
            'classe_id': self.classe.id if self.classe else None,
            'turma': self.turma.nome if self.turma else None,
            'turma_id': self.turma.id if self.turma else None,
            'status': self.status,
            'aprovado': self.aprovado,
            'media_final': float(self.media_final) if self.media_final else None,
            'observacoes': self.observacoes,
            'data_criacao': self.safe_strftime(self.data_criacao),
        }