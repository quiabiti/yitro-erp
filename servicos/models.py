# servicos/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum
from django.forms import model_to_dict
from datetime import timedelta

User = get_user_model()

# ============================================
# MODELO UNIFICADO: ITEM
# ============================================

class Item(models.Model):
    """Modelo unificado para todos os itens comerciais (produtos e serviços)"""
    
    TIPO_CHOICES = (
        ('produto', 'Produto Físico'),
        ('servico', 'Serviço'),
        ('software', 'Software/SaaS'),
        ('consultoria', 'Consultoria'),
    )
    
    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('descontinuado', 'Descontinuado'),
    )
    
    RECORRENCIA_CHOICES = (
        ('unico', 'Pagamento Único'),
        ('mensal', 'Mensal'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    )
    
    # Dados básicos
    codigo = models.CharField('Código', max_length=50, unique=True)
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ativo')
    
    # 🔥 IMAGEM DO PRODUTO/SERVIÇO
    imagem = models.ImageField(
        'Imagem do Produto', 
        upload_to='produtos/', 
        null=True, 
        blank=True,
        help_text='Imagem para exibição na vitrine'
    )
    
    # Preços
    preco_venda = models.DecimalField('Preço de Venda', max_digits=10, decimal_places=2)
    preco_custo = models.DecimalField('Preço de Custo', max_digits=10, decimal_places=2, null=True, blank=True)
    margem_lucro = models.DecimalField('Margem de Lucro (%)', max_digits=5, decimal_places=2, default=0)
    
    # Recorrência
    recorrencia = models.CharField('Recorrência', max_length=20, choices=RECORRENCIA_CHOICES, default='unico')
    duracao_padrao = models.IntegerField('Duração Padrão (dias)', null=True, blank=True)
    
    # Específico para serviços
    horas_estimadas = models.DecimalField('Horas Estimadas', max_digits=8, decimal_places=2, null=True, blank=True)
    preco_hora = models.DecimalField('Preço por Hora', max_digits=10, decimal_places=2, null=True, blank=True)
    nivel_prioridade = models.IntegerField('Nível de Prioridade', default=1, choices=[
        (1, 'Baixa'),
        (2, 'Média'),
        (3, 'Alta'),
        (4, 'Urgente'),
    ])
    requer_visita = models.BooleanField('Requer Visita Técnica', default=False)
    requer_equipamento = models.BooleanField('Requer Equipamento Especial', default=False)
    tempo_medio_execucao = models.DurationField('Tempo Médio de Execução', null=True, blank=True)
    
    # Específico para software
    requer_ativacao = models.BooleanField('Requer Ativação', default=False)
    numero_usuarios_incluidos = models.IntegerField('Nº de Usuários Incluídos', default=1)
    permite_upgrade = models.BooleanField('Permite Upgrade', default=True)
    
    # Específico para produtos físicos
    peso = models.DecimalField('Peso (kg)', max_digits=8, decimal_places=2, null=True, blank=True)
    dimensoes = models.CharField('Dimensões', max_length=100, blank=True)
    codigo_barras = models.CharField('Código de Barras', max_length=50, blank=True)
    unidade_medida = models.CharField('Unidade de Medida', max_length=20, default='un')
    
    # Campos de controle
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='itens_criados')
    
    class Meta:
        db_table = 'servicos_itens'
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo', 'status']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    def save(self, *args, **kwargs):
        if self.preco_venda and self.preco_custo and self.preco_venda > 0:
            self.margem_lucro = ((self.preco_venda - self.preco_custo) / self.preco_venda) * 100
        
        if self.tipo == 'software' and not self.duracao_padrao:
            if self.recorrencia == 'mensal':
                self.duracao_padrao = 30
            elif self.recorrencia == 'anual':
                self.duracao_padrao = 365
        
        super().save(*args, **kwargs)
    
    def is_produto(self):
        return self.tipo == 'produto'
    
    def is_servico(self):
        return self.tipo in ['servico', 'consultoria']
    
    def is_software(self):
        return self.tipo == 'software'
    
    def is_recorrente(self):
        return self.recorrencia != 'unico'
    
    def get_stock_atual(self, local_id=None):
        if not self.is_produto():
            return None
        
        if local_id:
            try:
                stock = Stock.objects.get(item=self, local_id=local_id)
                return stock.quantidade_atual
            except Stock.DoesNotExist:
                return 0
        else:
            total = Stock.objects.filter(item=self).aggregate(
                total=Sum('quantidade_atual')
            )['total']
            return total or 0
    
    def to_dict(self):
        """Converte o item para dicionário (para APIs)"""
        data = model_to_dict(self, exclude=['criado_por', 'imagem'])
        data['preco_venda'] = float(self.preco_venda) if self.preco_venda else 0
        data['preco_custo'] = float(self.preco_custo) if self.preco_custo else 0
        data['margem_lucro'] = float(self.margem_lucro) if self.margem_lucro else 0
        data['tipo_display'] = self.get_tipo_display()
        data['status_display'] = self.get_status_display()
        data['recorrencia_display'] = self.get_recorrencia_display()
        data['is_recorrente'] = self.is_recorrente()
        data['imagem_url'] = self.imagem.url if self.imagem else None
        
        if self.is_produto():
            data['stock_atual'] = self.get_stock_atual()
            stock = Stock.objects.filter(item=self).first()
            data['stock_inicial'] = stock.quantidade_atual if stock else 0
            data['stock_minimo'] = stock.stock_minimo if stock else 5
        else:
            data['stock_atual'] = None
            data['stock_inicial'] = 0
            data['stock_minimo'] = 5
        
        return data


# ============================================
# STOCK
# ============================================

class Local(models.Model):
    """Modelo para locais de stock"""
    
    TIPO_CHOICES = (
        ('loja_fisica', 'Loja Física'),
        ('armazem_online', 'Armazém Vendas Online'),
        ('armazem_central', 'Armazém Central'),
        ('estoque_terceiro', 'Estoque em Terceiros'),
    )
    
    nome = models.CharField('Nome', max_length=100)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    endereco = models.TextField('Endereço', blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    def __str__(self):
        return self.nome


class Stock(models.Model):
    """Modelo para controle de stock"""
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='stocks')
    local = models.ForeignKey(Local, on_delete=models.CASCADE, related_name='stocks')
    quantidade_atual = models.PositiveIntegerField('Quantidade Atual', default=0)
    stock_minimo = models.PositiveIntegerField('Stock Mínimo', default=0)
    ponto_reposicao = models.PositiveIntegerField('Ponto de Reposição', default=0)
    stock_maximo = models.PositiveIntegerField('Stock Máximo', default=0)
    ultima_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        unique_together = ['item', 'local']
    
    def __str__(self):
        return f"{self.item.nome} - {self.local.nome}: {self.quantidade_atual}"


class MovimentoStock(models.Model):
    """Modelo para histórico de movimentações"""
    
    TIPO_CHOICES = (
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ajuste', 'Ajuste'),
        ('reserva', 'Reserva'),
        ('cancelamento', 'Cancelamento'),
        ('devolucao', 'Devolução'),
    )
    
    MOTIVO_CHOICES = (
        ('compra', 'Compra'),
        ('venda', 'Venda'),
        ('ajuste', 'Ajuste Manual'),
        ('inventario', 'Inventário'),
        ('devolucao', 'Devolução'),
        ('transferencia', 'Transferência'),
        ('perda', 'Perda/Danificado'),
    )
    
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='movimentos')
    local = models.ForeignKey(Local, on_delete=models.PROTECT, related_name='movimentos')
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    motivo = models.CharField('Motivo', max_length=20, choices=MOTIVO_CHOICES)
    quantidade = models.PositiveIntegerField('Quantidade')
    quantidade_anterior = models.PositiveIntegerField('Quantidade Anterior')
    quantidade_nova = models.PositiveIntegerField('Quantidade Nova')
    observacao = models.TextField('Observação', blank=True)
    venda_id = models.PositiveIntegerField('ID da Venda', null=True, blank=True)
    compra_id = models.PositiveIntegerField('ID da Compra', null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='movimentos_stock')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        ordering = ['-criado_em']


class ReservaStock(models.Model):
    """Modelo para reserva de stock"""
    
    STATUS_CHOICES = (
        ('reservado', 'Reservado'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('expirado', 'Expirado'),
    )
    
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='reservas')
    local = models.ForeignKey(Local, on_delete=models.PROTECT, related_name='reservas')
    quantidade = models.PositiveIntegerField('Quantidade')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='reservado')
    sessao_id = models.CharField('ID da Sessão', max_length=100, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas')
    expira_em = models.DateTimeField('Expira em')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    def is_expirado(self):
        return timezone.now() > self.expira_em


class Licenca(models.Model):
    """Modelo para licenças de software"""
    
    STATUS_CHOICES = (
        ('ativa', 'Ativa'),
        ('inativa', 'Inativa'),
        ('expirada', 'Expirada'),
        ('suspensa', 'Suspensa'),
        ('cancelada', 'Cancelada'),
    )
    
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='licencas')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='licencas')
    chave = models.CharField('Chave de Licença', max_length=100, unique=True)
    data_ativacao = models.DateTimeField('Data de Ativação', null=True, blank=True)
    data_expiracao = models.DateTimeField('Data de Expiração')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='inativa')
    venda_id = models.PositiveIntegerField('ID da Venda', null=True, blank=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    def is_expirada(self):
        return timezone.now() > self.data_expiracao


class ContratoServico(models.Model):
    """Modelo para contratos de serviço"""
    
    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('pendente', 'Pendente'),
        ('expirado', 'Expirado'),
        ('cancelado', 'Cancelado'),
        ('concluido', 'Concluído'),
    )
    
    cliente = models.ForeignKey(User, on_delete=models.PROTECT, related_name='contratos_servicos')
    servico = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='contratos')
    
    data_inicio = models.DateTimeField('Data de Início', default=timezone.now)
    data_fim = models.DateTimeField('Data de Fim', null=True, blank=True)
    data_proxima_cobranca = models.DateTimeField('Próxima Cobrança', null=True, blank=True)
    data_renovacao = models.DateTimeField('Data de Renovação', null=True, blank=True)
    
    preco_acordado = models.DecimalField('Preço Acordado', max_digits=10, decimal_places=2)
    desconto = models.DecimalField('Desconto (%)', max_digits=5, decimal_places=2, default=0)
    valor_total = models.DecimalField('Valor Total', max_digits=10, decimal_places=2)
    
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ativo')
    renovacao_automatica = models.BooleanField('Renovação Automática', default=False)
    
    horas_contratadas = models.DecimalField('Horas Contratadas', max_digits=8, decimal_places=2, null=True, blank=True)
    horas_utilizadas = models.DecimalField('Horas Utilizadas', max_digits=8, decimal_places=2, default=0)
    horas_restantes = models.DecimalField('Horas Restantes', max_digits=8, decimal_places=2, null=True, blank=True)
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contratos_criados')
    
    class Meta:
        verbose_name = 'Contrato de Serviço'
        verbose_name_plural = 'Contratos de Serviço'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"{self.cliente.username} - {self.servico.nome}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            if self.servico.duracao_padrao and not self.data_fim:
                self.data_fim = self.data_inicio + timedelta(days=self.servico.duracao_padrao)
            
            if not self.valor_total:
                self.valor_total = self.preco_acordado - (self.preco_acordado * (self.desconto / 100))
            
            if self.servico.is_servico() and self.horas_contratadas:
                self.horas_restantes = self.horas_contratadas
        super().save(*args, **kwargs)


class OrdemServico(models.Model):
    """Modelo para ordens de serviço"""
    
    STATUS_CHOICES = (
        ('aberta', 'Aberta'),
        ('em_andamento', 'Em Andamento'),
        ('aguardando', 'Aguardando Cliente'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    )
    
    PRIORIDADE_CHOICES = (
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    )
    
    numero = models.CharField('Número', max_length=20, unique=True)
    contrato = models.ForeignKey(ContratoServico, on_delete=models.PROTECT, related_name='ordens')
    cliente = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ordens_servico')
    
    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='aberta')
    prioridade = models.CharField('Prioridade', max_length=20, choices=PRIORIDADE_CHOICES, default='media')
    
    data_abertura = models.DateTimeField('Data de Abertura', default=timezone.now)
    data_inicio = models.DateTimeField('Data de Início', null=True, blank=True)
    data_conclusao = models.DateTimeField('Data de Conclusão', null=True, blank=True)
    prazo = models.DateTimeField('Prazo', null=True, blank=True)
    
    horas_estimadas = models.DecimalField('Horas Estimadas', max_digits=8, decimal_places=2, null=True, blank=True)
    horas_trabalhadas = models.DecimalField('Horas Trabalhadas', max_digits=8, decimal_places=2, default=0)
    
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ordens_responsavel')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
        ordering = ['-data_abertura']
    
    def __str__(self):
        return f"{self.numero} - {self.titulo}"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            ano = timezone.now().year
            ultima = OrdemServico.objects.filter(
                numero__startswith=f'OS-{ano}'
            ).order_by('-numero').first()
            
            if ultima:
                num = int(ultima.numero.split('-')[-1]) + 1
            else:
                num = 1
            self.numero = f'OS-{ano}-{num:03d}'
        super().save(*args, **kwargs)


class LancamentoHoras(models.Model):
    """Modelo para lançamento de horas"""
    
    ordem = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, related_name='lancamentos_horas')
    funcionario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='lancamentos_horas')
    data = models.DateTimeField('Data', default=timezone.now)
    horas = models.DecimalField('Horas', max_digits=5, decimal_places=2)
    descricao = models.TextField('Descrição do Trabalho Realizado')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Lançamento de Horas'
        verbose_name_plural = 'Lançamentos de Horas'
        ordering = ['-data']
    
    def __str__(self):
        return f"{self.funcionario.username} - {self.horas}h em {self.ordem.titulo}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        total_horas = LancamentoHoras.objects.filter(ordem=self.ordem).aggregate(
            total=Sum('horas')
        )['total'] or 0
        self.ordem.horas_trabalhadas = total_horas
        self.ordem.save()


class FaturamentoRecorrente(models.Model):
    """Modelo para controle de faturamento recorrente"""
    
    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('pausado', 'Pausado'),
        ('cancelado', 'Cancelado'),
    )
    
    contrato = models.ForeignKey(ContratoServico, on_delete=models.CASCADE, related_name='faturamentos')
    cliente = models.ForeignKey(User, on_delete=models.PROTECT, related_name='faturamentos_recorrentes')
    servico = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='faturamentos')
    
    frequencia = models.CharField('Frequência', max_length=20, choices=Item.RECORRENCIA_CHOICES)
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    dia_cobranca = models.IntegerField('Dia da Cobrança', default=1)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ativo')
    
    proxima_cobranca = models.DateTimeField('Próxima Cobrança')
    ultima_cobranca = models.DateTimeField('Última Cobrança', null=True, blank=True)
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Faturamento Recorrente'
        verbose_name_plural = 'Faturamentos Recorrentes'
    
    def __str__(self):
        return f"{self.cliente.username} - {self.servico.nome} ({self.frequencia})"


class ConfiguracaoSistema(models.Model):
    """Modelo para armazenar configurações do sistema"""
    
    # ============================================
    # INFORMAÇÕES DA EMPRESA (NOVOS CAMPOS)
    # ============================================
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True, null=True, default='+244 900 000 000')
    email = models.EmailField('Email', blank=True, null=True, default='contato@yitro.ao')
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True, default='+244 222 000 000')
    endereco = models.TextField('Endereço', blank=True, null=True, default='Luanda, Angola')
    horario = models.CharField('Horário de Funcionamento', max_length=200, blank=True, null=True, default='Segunda a Sexta: 08h00 - 18h00, Sábado: 08h00 - 13h00')
    
    # ============================================
    # CONFIGURAÇÕES GERAIS
    # ============================================
    nome_sistema = models.CharField('Nome do Sistema', max_length=100, default='Yitro ERP')
    moeda_padrao = models.CharField('Moeda Padrão', max_length=10, default='Kz')
    fuso_horario = models.CharField('Fuso Horário', max_length=50, default='Africa/Luanda')
    idioma_padrao = models.CharField('Idioma Padrão', max_length=20, default='Português (PT)')
    
    # ============================================
    # SEGURANÇA
    # ============================================
    dois_fatores = models.BooleanField('Autenticação em Dois Fatores', default=True)
    tempo_sessao = models.IntegerField('Tempo de Sessão (minutos)', default=120)
    tentativas_login = models.IntegerField('Tentativas de Login', default=5)
    
    # ============================================
    # NOTIFICAÇÕES
    # ============================================
    notificacoes_email = models.BooleanField('Notificações por Email', default=True)
    notificacoes_push = models.BooleanField('Notificações Push', default=False)
    alertas_stock = models.BooleanField('Alertas de Stock', default=True)
    
    # ============================================
    # FATURAÇÃO
    # ============================================
    serie_padrao = models.CharField('Série Padrão', max_length=10, default='FT-')
    iva_padrao = models.DecimalField('IVA Padrão (%)', max_digits=5, decimal_places=2, default=14.00)
    validacao_automatica = models.BooleanField('Validação Automática', default=False)
    
    # ============================================
    # SISTEMA
    # ============================================
    backup_automatico = models.BooleanField('Backup Automático', default=True)
    logs_sistema = models.BooleanField('Logs do Sistema', default=True)
    modo_manutencao = models.BooleanField('Modo Manutenção', default=False)
    
    # ============================================
    # METADADOS
    # ============================================
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    atualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Atualizado por')
    
    class Meta:
        verbose_name = 'Configuração do Sistema'
        verbose_name_plural = 'Configurações do Sistema'
    
    def __str__(self):
        return f'Configurações - {self.nome_sistema}'


# ============================================
# PEDIDOS
# ============================================

class Pedido(models.Model):
    """Modelo para pedidos de compra"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('em_processamento', 'Em Processamento'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]
    
    numero = models.CharField('Número', max_length=50, unique=True)
    cliente = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pedidos')
    data_criacao = models.DateTimeField('Criado em', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Atualizado em', auto_now=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    subtotal = models.DecimalField('Subtotal', max_digits=15, decimal_places=2, default=0)
    desconto = models.DecimalField('Desconto', max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=15, decimal_places=2, default=0)
    
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True)
    nif = models.CharField('NIF', max_length=20, blank=True, null=True)
    endereco_entrega = models.TextField('Endereço de Entrega', blank=True, null=True)
    observacoes = models.TextField('Observações', blank=True, null=True)
    
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pedidos_criados')
    
    class Meta:
        db_table = 'servicos_pedidos'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f'Pedido {self.numero}'
    
    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo = Pedido.objects.all().order_by('-id').first()
            if ultimo and ultimo.numero:
                try:
                    partes = ultimo.numero.split('-')
                    if len(partes) >= 3:
                        numero_atual = int(partes[-1])
                        novo_numero = numero_atual + 1
                    else:
                        novo_numero = 1
                except (ValueError, IndexError):
                    novo_numero = 1
            else:
                novo_numero = 1
            self.numero = f'PED-{timezone.now().year}-{str(novo_numero).zfill(5)}'
        super().save(*args, **kwargs)


class ItemPedido(models.Model):
    """Itens do pedido"""
    
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='itens_pedido')
    quantidade = models.IntegerField('Quantidade', default=1)
    preco_unitario = models.DecimalField('Preço Unitário', max_digits=15, decimal_places=2)
    subtotal = models.DecimalField('Subtotal', max_digits=15, decimal_places=2)
    
    class Meta:
        db_table = 'servicos_item_pedido'
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
    
    def __str__(self):
        return f'{self.item.nome} x {self.quantidade}'
    
    def save(self, *args, **kwargs):
        self.subtotal = self.preco_unitario * self.quantidade
        super().save(*args, **kwargs)