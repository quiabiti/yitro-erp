from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from ..models import Item, Stock, MovimentoStock, ReservaStock, Local, BancoHoras
from django.contrib.auth import get_user_model
from django.db.models import Sum

User = get_user_model()

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
        
        # Atualiza stock
        stock.quantidade_atual = quantidade_nova
        stock.save()
        
        # Registra movimento
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
        
        # Verifica alertas de stock
        alertas = StockService.verificar_alertas_stock(item, local)
        
        return movimento, alertas
    
    @staticmethod
    @transaction.atomic
    def saida_stock(item_id, local_id, quantidade, motivo, usuario_id, observacao='', venda_id=None):
        """Registra uma saída de stock"""
        item = Item.objects.get(id=item_id, tipo='produto')
        local = Local.objects.get(id=local_id)
        usuario = User.objects.get(id=usuario_id)
        
        # Bloqueia a linha do stock para evitar race conditions
        try:
            stock = Stock.objects.select_for_update().get(item=item, local=local)
        except Stock.DoesNotExist:
            raise ValueError(f"Stock não encontrado para {item.nome} em {local.nome}")
        
        # Verifica disponibilidade
        disponivel = StockService.verificar_disponibilidade(item_id, local_id, quantidade)
        if not disponivel:
            raise ValueError(f"Stock insuficiente para {item.nome}")
        
        quantidade_anterior = stock.quantidade_atual
        quantidade_nova = quantidade_anterior - quantidade
        
        # Atualiza stock
        stock.quantidade_atual = quantidade_nova
        stock.save()
        
        # Registra movimento
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
        
        # Verifica alertas
        alertas = StockService.verificar_alertas_stock(item, local)
        
        return movimento, alertas
    
    @staticmethod
    def verificar_disponibilidade(item_id, local_id, quantidade):
        """Verifica se há quantidade suficiente disponível"""
        disponivel = Item.objects.get(id=item_id).get_stock_disponivel(local_id)
        return disponivel >= quantidade
    
    @staticmethod
    def verificar_alertas_stock(item, local):
        """Verifica e retorna alertas de stock"""
        try:
            stock = Stock.objects.get(item=item, local=local)
            alertas = []
            
            if stock.is_abaixo_minimo():
                alertas.append({
                    'item': item.nome,
                    'local': local.nome,
                    'atual': stock.quantidade_atual,
                    'minimo': stock.stock_minimo,
                    'nivel': 'critico'
                })
            
            if stock.quantidade_atual <= stock.ponto_reposicao and stock.ponto_reposicao > 0:
                alertas.append({
                    'item': item.nome,
                    'local': local.nome,
                    'atual': stock.quantidade_atual,
                    'ponto_reposicao': stock.ponto_reposicao,
                    'nivel': 'alerta'
                })
            
            return alertas
        except Stock.DoesNotExist:
            return []
    
    @staticmethod
    @transaction.atomic
    def reservar_stock(item_id, local_id, quantidade, sessao_id=None, usuario_id=None, minutos=30):
        """Reserva stock para um carrinho de compras"""
        item = Item.objects.get(id=item_id, tipo='produto')
        local = Local.objects.get(id=local_id)
        
        # Verifica disponibilidade
        if not StockService.verificar_disponibilidade(item_id, local_id, quantidade):
            raise ValueError(f"Stock insuficiente para {item.nome}")
        
        # Cria reserva
        reserva = ReservaStock.objects.create(
            item=item,
            local=local,
            quantidade=quantidade,
            sessao_id=sessao_id,
            usuario_id=usuario_id,
            expira_em=timezone.now() + timezone.timedelta(minutes=minutos)
        )
        
        return reserva
    
    @staticmethod
    @transaction.atomic
    def confirmar_reserva(reserva_id):
        """Confirma uma reserva e converte em saída"""
        reserva = ReservaStock.objects.select_for_update().get(id=reserva_id)
        
        if reserva.is_expirado():
            reserva.status = 'expirado'
            reserva.save()
            raise ValueError("Reserva expirada")
        
        # Converte em saída
        movimento, alertas = StockService.saida_stock(
            item_id=reserva.item.id,
            local_id=reserva.local.id,
            quantidade=reserva.quantidade,
            motivo='venda',
            usuario_id=reserva.usuario.id if reserva.usuario else None,
            venda_id=reserva.id
        )
        
        reserva.status = 'confirmado'
        reserva.save()
        
        return movimento
    
    @staticmethod
    @transaction.atomic
    def cancelar_reserva(reserva_id):
        """Cancela uma reserva"""
        reserva = ReservaStock.objects.select_for_update().get(id=reserva_id)
        reserva.status = 'cancelado'
        reserva.save()
        return reserva
    
    @staticmethod
    def limpar_reservas_expiradas():
        """Limpa reservas expiradas"""
        expiradas = ReservaStock.objects.filter(
            status='reservado',
            expira_em__lte=timezone.now()
        )
        
        count = expiradas.update(status='expirado')
        return count


class LicencaService:
    """Serviço para gerenciar licenças de software"""
    
    @staticmethod
    def gerar_chave_licenca():
        """Gera uma chave de licença única"""
        import uuid
        import hashlib
        from django.utils.crypto import get_random_string
        
        # Gera uma chave no formato XXXX-XXXX-XXXX-XXXX
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
        data_expiracao = timezone.now() + timezone.timedelta(days=dias_validade)
        
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


class BancoHorasService:
    """Serviço para gerenciar banco de horas de consultoria"""
    
    @staticmethod
    @transaction.atomic
    def criar_banco_horas(cliente_id, item_id, horas, dias_validade, venda_id=None):
        """Cria um banco de horas para um cliente"""
        cliente = User.objects.get(id=cliente_id)
        item = Item.objects.get(id=item_id, tipo='consultoria')
        
        banco = BancoHoras.objects.create(
            cliente=cliente,
            item=item,
            horas_totais=horas,
            horas_utilizadas=0,
            horas_restantes=horas,  # Será recalculado no save()
            data_compra=timezone.now(),
            data_expiracao=timezone.now() + timezone.timedelta(days=dias_validade),
            venda_id=venda_id
        )
        
        return banco
    
    @staticmethod
    @transaction.atomic
    def consumir_horas(cliente_id, item_id, horas, observacao=''):
        """Consome horas de um banco de horas com segurança"""
        try:
            # Bloqueia a linha para evitar race conditions
            banco = BancoHoras.objects.select_for_update().get(
                cliente_id=cliente_id,
                item_id=item_id,
                status='ativo'
            )
        except BancoHoras.DoesNotExist:
            raise ValueError("Banco de horas não encontrado ou inativo")
        
        if not banco.consumir_horas(horas):
            raise ValueError("Horas insuficientes no banco")
        
        if banco.horas_restantes <= 0:
            banco.status = 'expirado'
            banco.save()
        
        return banco