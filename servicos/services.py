# servicos/services.py
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import (
    Item, ContratoServico, OrdemServico, LancamentoHoras, 
    FaturamentoRecorrente, Stock, MovimentoStock, Local, Licenca
)
from django.contrib.auth import get_user_model

User = get_user_model()

# ============================================
# SERVIÇO DE STOCK
# ============================================

class StockService:
    """Serviço para gerenciar operações de stock"""
    
    @staticmethod
    @transaction.atomic
    def entrada_stock(item_id, local_id, quantidade, motivo, usuario_id, observacao='', compra_id=None):
        """Registra uma entrada de stock"""
        item = Item.objects.get(id=item_id, tipo='produto')
        local = Local.objects.get(id=local_id)
        usuario = User.objects.get(id=usuario_id)
        
        stock, created = Stock.objects.get_or_create(
            item=item,
            local=local,
            defaults={'quantidade_atual': 0}
        )
        
        quantidade_anterior = stock.quantidade_atual
        quantidade_nova = quantidade_anterior + quantidade
        
        stock.quantidade_atual = quantidade_nova
        stock.save()
        
        movimento = MovimentoStock.objects.create(
            item=item,
            local=local,
            tipo='entrada',
            motivo=motivo,
            quantidade=quantidade,
            quantidade_anterior=quantidade_anterior,
            quantidade_nova=quantidade_nova,
            observacao=observacao,
            compra_id=compra_id,
            usuario=usuario
        )
        
        alertas = StockService.verificar_alertas_stock(item, local)
        
        return movimento, alertas
    
    @staticmethod
    @transaction.atomic
    def saida_stock(item_id, local_id, quantidade, motivo, usuario_id, observacao='', venda_id=None):
        """Registra uma saída de stock"""
        item = Item.objects.get(id=item_id, tipo='produto')
        local = Local.objects.get(id=local_id)
        usuario = User.objects.get(id=usuario_id)
        
        try:
            stock = Stock.objects.select_for_update().get(item=item, local=local)
        except Stock.DoesNotExist:
            raise ValueError(f"Stock não encontrado para {item.nome} em {local.nome}")
        
        if stock.quantidade_atual < quantidade:
            raise ValueError(f"Stock insuficiente para {item.nome}. Disponível: {stock.quantidade_atual}")
        
        quantidade_anterior = stock.quantidade_atual
        quantidade_nova = quantidade_anterior - quantidade
        
        stock.quantidade_atual = quantidade_nova
        stock.save()
        
        movimento = MovimentoStock.objects.create(
            item=item,
            local=local,
            tipo='saida',
            motivo=motivo,
            quantidade=quantidade,
            quantidade_anterior=quantidade_anterior,
            quantidade_nova=quantidade_nova,
            observacao=observacao,
            venda_id=venda_id,
            usuario=usuario
        )
        
        alertas = StockService.verificar_alertas_stock(item, local)
        
        return movimento, alertas
    
    @staticmethod
    def verificar_alertas_stock(item, local):
        """Verifica e retorna alertas de stock"""
        try:
            stock = Stock.objects.get(item=item, local=local)
            alertas = []
            
            if stock.quantidade_atual <= stock.stock_minimo:
                alertas.append({
                    'item': item.nome,
                    'local': local.nome,
                    'atual': stock.quantidade_atual,
                    'minimo': stock.stock_minimo,
                    'nivel': 'critico' if stock.quantidade_atual == 0 else 'alerta'
                })
            
            return alertas
        except Stock.DoesNotExist:
            return []


# ============================================
# SERVIÇO DE SERVIÇOS
# ============================================

class ServicoService:
    """Serviço para gerenciar operações de serviços"""
    
    @staticmethod
    @transaction.atomic
    def criar_contrato(cliente_id, servico_id, preco_acordado, data_inicio=None, 
                       desconto=0, horas_contratadas=None):
        """Cria um novo contrato de serviço"""
        cliente = User.objects.get(id=cliente_id)
        servico = Item.objects.get(id=servico_id, status='ativo')
        
        if not data_inicio:
            data_inicio = timezone.now()
        
        valor_total = preco_acordado - (preco_acordado * (desconto / 100))
        
        contrato = ContratoServico.objects.create(
            cliente=cliente,
            servico=servico,
            data_inicio=data_inicio,
            preco_acordado=preco_acordado,
            desconto=desconto,
            valor_total=valor_total,
            horas_contratadas=horas_contratadas,
            criado_por=cliente
        )
        
        # Se for recorrente, cria faturamento
        if servico.is_recorrente():
            FaturamentoRecorrente.objects.create(
                contrato=contrato,
                cliente=cliente,
                servico=servico,
                frequencia=servico.recorrencia,
                valor=servico.preco_venda,
                proxima_cobranca=data_inicio + timedelta(days=30)
            )
        
        return contrato
    
    @staticmethod
    @transaction.atomic
    def criar_ordem_servico(contrato_id, titulo, descricao, prioridade='media', 
                           responsavel_id=None, horas_estimadas=None, prazo=None):
        """Cria uma ordem de serviço"""
        contrato = ContratoServico.objects.get(id=contrato_id)
        cliente = contrato.cliente
        
        ordem = OrdemServico.objects.create(
            contrato=contrato,
            cliente=cliente,
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            horas_estimadas=horas_estimadas,
            prazo=prazo,
            responsavel_id=responsavel_id
        )
        
        return ordem
    
    @staticmethod
    @transaction.atomic
    def lancar_horas(ordem_id, funcionario_id, horas, descricao):
        """Lança horas em uma ordem de serviço"""
        ordem = OrdemServico.objects.get(id=ordem_id)
        funcionario = User.objects.get(id=funcionario_id)
        
        lancamento = LancamentoHoras.objects.create(
            ordem=ordem,
            funcionario=funcionario,
            horas=horas,
            descricao=descricao
        )
        
        return lancamento
    
    @staticmethod
    def processar_cobrancas_recorrentes():
        """Processa cobranças recorrentes que estão vencidas"""
        hoje = timezone.now()
        faturamentos = FaturamentoRecorrente.objects.filter(
            status='ativo',
            proxima_cobranca__lte=hoje
        )
        
        processados = []
        for faturamento in faturamentos:
            # Atualiza a próxima cobrança
            if faturamento.frequencia == 'mensal':
                proxima = faturamento.proxima_cobranca + timedelta(days=30)
            elif faturamento.frequencia == 'trimestral':
                proxima = faturamento.proxima_cobranca + timedelta(days=90)
            elif faturamento.frequencia == 'semestral':
                proxima = faturamento.proxima_cobranca + timedelta(days=180)
            elif faturamento.frequencia == 'anual':
                proxima = faturamento.proxima_cobranca + timedelta(days=365)
            else:
                proxima = faturamento.proxima_cobranca + timedelta(days=30)
            
            faturamento.ultima_cobranca = faturamento.proxima_cobranca
            faturamento.proxima_cobranca = proxima
            faturamento.save()
            processados.append(faturamento)
        
        return processados
    
    @staticmethod
    def verificar_contratos_expirados():
        """Verifica e atualiza contratos expirados"""
        hoje = timezone.now()
        expirados = ContratoServico.objects.filter(
            status='ativo',
            data_fim__lte=hoje
        )
        
        count = expirados.update(status='expirado')
        return count


# ============================================
# SERVIÇO DE LICENÇAS
# ============================================

class LicencaService:
    """Serviço para gerenciar licenças de software"""
    
    @staticmethod
    def gerar_chave_licenca():
        """Gera uma chave de licença única"""
        from django.utils.crypto import get_random_string
        
        partes = []
        for _ in range(4):
            partes.append(get_random_string(4, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))
        return '-'.join(partes)
    
    @staticmethod
    @transaction.atomic
    def criar_licenca(item_id, usuario_id, dias_validade, venda_id=None):
        """Cria uma nova licença para um software"""
        item = Item.objects.get(id=item_id, tipo='software')
        usuario = User.objects.get(id=usuario_id)
        
        chave = LicencaService.gerar_chave_licenca()
        data_expiracao = timezone.now() + timedelta(days=dias_validade)
        
        licenca = Licenca.objects.create(
            item=item,
            usuario=usuario,
            chave=chave,
            data_expiracao=data_expiracao,
            status='ativa',
            venda_id=venda_id
        )
        
        return licenca
    
    @staticmethod
    def ativar_licenca(licenca_id, usuario_id):
        """Ativa uma licença"""
        licenca = Licenca.objects.select_for_update().get(id=licenca_id)
        usuario = User.objects.get(id=usuario_id)
        
        licenca.status = 'ativa'
        licenca.ativada_em = timezone.now()
        licenca.ativada_por = usuario
        licenca.save()
        
        return licenca
    
    @staticmethod
    def verificar_licencas_expiradas():
        """Verifica e atualiza licenças expiradas"""
        expiradas = Licenca.objects.filter(
            status='ativa',
            data_expiracao__lte=timezone.now()
        )
        
        count = expiradas.update(status='expirada')
        return count


# ============================================
# SERVIÇO DE CONSULTORIA
# ============================================

class ConsultoriaService:
    """Serviço específico para consultoria"""
    
    @staticmethod
    @transaction.atomic
    def criar_banco_horas(cliente_id, servico_id, horas, preco_hora, venda_id=None):
        """Cria um banco de horas para consultoria"""
        cliente = User.objects.get(id=cliente_id)
        servico = Item.objects.get(id=servico_id, tipo='consultoria')
        
        # Cria um contrato com as horas
        valor_total = horas * preco_hora
        
        contrato = ContratoServico.objects.create(
            cliente=cliente,
            servico=servico,
            preco_acordado=valor_total,
            valor_total=valor_total,
            horas_contratadas=horas,
            horas_restantes=horas,
            criado_por=cliente
        )
        
        return contrato
    
    @staticmethod
    def validar_disponibilidade_horas(cliente_id, servico_id, horas_necessarias):
        """Valida se o cliente tem horas disponíveis"""
        try:
            contrato = ContratoServico.objects.get(
                cliente_id=cliente_id,
                servico_id=servico_id,
                status='ativo'
            )
            return contrato.horas_restantes and contrato.horas_restantes >= horas_necessarias
        except ContratoServico.DoesNotExist:
            return False