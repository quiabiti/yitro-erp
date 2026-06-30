# servicos/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, Count
from django.db import models
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model
from decimal import Decimal
import json
import os
import io
from datetime import datetime, timedelta

from .models import (
    Item, Stock, MovimentoStock, Local, Licenca,
    ContratoServico, OrdemServico, LancamentoHoras, FaturamentoRecorrente,
    ConfiguracaoSistema, Pedido, ItemPedido
)
from .services import ServicoService
from .forms import (
    ItemForm, ContratoServicoForm, OrdemServicoForm, LancamentoHorasForm
)

User = get_user_model()


# ============================================
# LISTA DE ITENS (CORRIGIDO COM JSON)
# ============================================

@login_required
def lista_itens(request):
    """Lista todos os itens (produtos, serviços, software, consultoria)"""
    from django.core.serializers.json import DjangoJSONEncoder
    
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    status = request.GET.get('status', '')
    
    itens = Item.objects.all()
    
    if query:
        itens = itens.filter(
            Q(nome__icontains=query) |
            Q(codigo__icontains=query) |
            Q(descricao__icontains=query)
        )
    
    if tipo:
        itens = itens.filter(tipo=tipo)
    
    if status:
        itens = itens.filter(status=status)
    
    # 🔥 PREPARAR DADOS PARA JSON (ITENS)
    itens_json = []
    for item in itens:
        # Calcular stock para produtos
        stock_atual = 0
        if item.tipo == 'produto':
            stock_total = Stock.objects.filter(item=item).aggregate(total=Sum('quantidade_atual'))['total']
            stock_atual = stock_total or 0
        
        itens_json.append({
            'id': item.id,
            'codigo': item.codigo,
            'nome': item.nome,
            'tipo': item.tipo,
            'tipo_display': item.get_tipo_display(),
            'status': item.status,
            'status_display': item.get_status_display(),
            'preco_venda': float(item.preco_venda) if item.preco_venda else 0,
            'is_recorrente': item.is_recorrente(),
            'recorrencia_display': item.get_recorrencia_display() if item.is_recorrente() else None,
            'stock_atual': stock_atual,
            'imagem_url': item.imagem.url if item.imagem else '',
            'descricao': item.descricao,
        })
    
    # 🔥 ESTATÍSTICAS POR TIPO (USANDO O FILTRO ATUAL)
    total_itens = itens.count()
    total_produtos = itens.filter(tipo='produto').count() if tipo == '' or tipo == 'produto' else 0
    total_servicos = itens.filter(tipo='servico').count() if tipo == '' or tipo == 'servico' else 0
    total_software = itens.filter(tipo='software').count() if tipo == '' or tipo == 'software' else 0
    total_consultoria = itens.filter(tipo='consultoria').count() if tipo == '' or tipo == 'consultoria' else 0
    
    # 🔥 ESTATÍSTICAS GERAIS (TODOS OS ITENS)
    total_itens_geral = Item.objects.count()
    total_produtos_geral = Item.objects.filter(tipo='produto').count()
    total_servicos_geral = Item.objects.filter(tipo='servico').count()
    total_software_geral = Item.objects.filter(tipo='software').count()
    total_consultoria_geral = Item.objects.filter(tipo='consultoria').count()
    itens_ativos = Item.objects.filter(status='ativo').count()
    itens_inativos = Item.objects.filter(status='inativo').count()
    
    # Alertas de stock
    alertas_stock = []
    produtos = Item.objects.filter(tipo='produto', status='ativo')
    for produto in produtos:
        stocks = Stock.objects.filter(item=produto)
        for stock in stocks:
            if stock.quantidade_atual <= stock.stock_minimo:
                alertas_stock.append({
                    'item': produto.nome,
                    'local': stock.local.nome,
                    'atual': stock.quantidade_atual,
                    'minimo': stock.stock_minimo
                })
    
    context = {
        'itens': itens,
        'itens_json': json.dumps(itens_json, cls=DjangoJSONEncoder),  # 🔥 JSON PARA JS
        'total_itens': total_itens_geral,
        'itens_ativos': itens_ativos,
        'itens_inativos': itens_inativos,
        'total_produtos': total_produtos_geral,
        'total_servicos': total_servicos_geral,
        'total_softwares': total_software_geral,
        'total_consultorias': total_consultoria_geral,
        'alertas_stock': alertas_stock,
        'query': query,
        'tipo': tipo,
        'status': status,
        'tipos': Item.TIPO_CHOICES,
        'status_options': Item.STATUS_CHOICES,
    }
    return render(request, 'servicos/lista_itens.html', context)


# ============================================
# DASHBOARD (CORRIGIDO)
# ============================================

@login_required
def dashboard_servicos(request):
    """Dashboard principal - Vitrine de Produtos e Serviços"""
    from django.core.serializers.json import DjangoJSONEncoder
    
    # ============================================
    # ITENS (Produtos e Serviços)
    # ============================================
    itens = Item.objects.filter(status='ativo').order_by('tipo', 'nome')
    
    # Separar por tipo
    produtos = itens.filter(tipo='produto')
    servicos = itens.filter(tipo__in=['servico', 'consultoria'])
    softwares = itens.filter(tipo='software')
    
    # 🔥 PREPARAR ITENS JSON PARA O TEMPLATE
    itens_json = []
    for item in itens:
        stock_atual = 0
        if item.tipo == 'produto':
            stock_total = Stock.objects.filter(item=item).aggregate(total=Sum('quantidade_atual'))['total']
            stock_atual = stock_total or 0
        
        itens_json.append({
            'id': item.id,
            'codigo': item.codigo,
            'nome': item.nome,
            'tipo': item.tipo,
            'tipo_display': item.get_tipo_display(),
            'status': item.status,
            'status_display': item.get_status_display(),
            'preco_venda': float(item.preco_venda) if item.preco_venda else 0,
            'is_recorrente': item.is_recorrente(),
            'recorrencia_display': item.get_recorrencia_display() if item.is_recorrente() else None,
            'stock_atual': stock_atual,
            'imagem_url': item.imagem.url if item.imagem else '',
        })
    
    # ============================================
    # ESTATÍSTICAS
    # ============================================
    total_itens = Item.objects.count()
    total_produtos = Item.objects.filter(tipo='produto').count()
    total_servicos = Item.objects.filter(tipo='servico').count()
    total_software = Item.objects.filter(tipo='software').count()
    total_consultoria = Item.objects.filter(tipo='consultoria').count()
    itens_ativos = Item.objects.filter(status='ativo').count()
    itens_inativos = Item.objects.filter(status='inativo').count()
    valor_total_itens = Item.objects.aggregate(total=Sum('preco_venda'))['total'] or 0
    
    # ============================================
    # ALERTAS DE STOCK
    # ============================================
    alertas_stock = []
    for produto in Item.objects.filter(tipo='produto', status='ativo'):
        stocks = Stock.objects.filter(item=produto)
        for stock in stocks:
            if stock.quantidade_atual <= stock.stock_minimo:
                alertas_stock.append({
                    'item': produto.nome,
                    'codigo': produto.codigo,
                    'local': stock.local.nome,
                    'atual': stock.quantidade_atual,
                    'minimo': stock.stock_minimo,
                    'status': 'critico' if stock.quantidade_atual == 0 else 'baixo'
                })
    
    # ============================================
    # ITENS EM DESTAQUE (mais recentes)
    # ============================================
    destaque = itens.order_by('-criado_em')[:6]
    
    # ============================================
    # CONTRATOS E ORDENS
    # ============================================
    total_contratos = ContratoServico.objects.filter(status='ativo').count()
    total_ordens = OrdemServico.objects.exclude(status='concluida').count()
    total_faturamentos = FaturamentoRecorrente.objects.filter(status='ativo').count()
    
    ordens_urgentes = OrdemServico.objects.filter(
        prioridade='urgente', 
        status__in=['aberta', 'em_andamento']
    ).select_related('cliente', 'contrato')
    
    contratos_expirando = ContratoServico.objects.filter(
        status='ativo',
        data_fim__lte=timezone.now() + timezone.timedelta(days=30)
    ).select_related('cliente', 'servico').order_by('data_fim')[:10]
    
    ultimos_itens = Item.objects.all().order_by('-criado_em')[:10]
    
    # ============================================
    # CARRINHO (Sessão)
    # ============================================
    if 'carrinho' not in request.session:
        request.session['carrinho'] = []
        request.session['carrinho_total'] = 0
    
    carrinho_itens = request.session.get('carrinho', [])
    total_carrinho = request.session.get('carrinho_total', 0)
    
    # ============================================
    # CONTEXTO
    # ============================================
    context = {
        'itens': itens,
        'itens_json': json.dumps(itens_json, cls=DjangoJSONEncoder),  # 🔥 JSON PARA JS
        'produtos': produtos,
        'servicos': servicos,
        'softwares': softwares,
        'produtos_com_stock': [],  # Será preenchido se necessário
        'destaque': destaque,
        'total_itens': total_itens,
        'total_produtos': total_produtos,
        'total_servicos': total_servicos,
        'total_softwares': total_software,
        'total_consultorias': total_consultoria,
        'itens_ativos': itens_ativos,
        'itens_inativos': itens_inativos,
        'valor_total_itens': valor_total_itens,
        'alertas_stock': alertas_stock,
        'total_alertas': len(alertas_stock),
        'total_contratos': total_contratos,
        'total_ordens': total_ordens,
        'total_faturamentos': total_faturamentos,
        'ordens_urgentes': ordens_urgentes,
        'contratos_expirando': contratos_expirando,
        'ultimos_itens': ultimos_itens,
        'carrinho_itens': carrinho_itens,
        'total_carrinho': total_carrinho,
        'total_carrinho_itens': len(carrinho_itens),
    }
    
    return render(request, 'loja_yitro.html', context)


# ============================================
# CARRINHO DE COMPRAS
# ============================================

@login_required
def carrinho(request):
    """Página do carrinho de compras"""
    carrinho = request.session.get('carrinho', [])
    total = request.session.get('carrinho_total', 0)
    
    itens_carrinho = []
    for item_data in carrinho:
        try:
            item = Item.objects.get(id=item_data['id'])
            itens_carrinho.append({
                'item': item,
                'quantidade': item_data['quantidade'],
                'subtotal': item.preco_venda * item_data['quantidade']
            })
        except Item.DoesNotExist:
            continue
    
    context = {
        'itens_carrinho': itens_carrinho,
        'total': total,
        'total_itens': len(itens_carrinho),
    }
    return render(request, 'servicos/carrinho.html', context)


import logging
import json
import traceback

# Configurar logger específico para esta função
logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def carrinho_adicionar(request):
    """
    Adicionar item ao carrinho (AJAX)
    """
    # Log inicial
    logger.info("="*50)
    logger.info("🚀 INICIANDO carrinho_adicionar")
    logger.info(f"📌 Método: {request.method}")
    logger.info(f"📌 Usuário: {request.user}")
    logger.info(f"📌 Session: {request.session.keys()}")
    logger.info(f"📌 Content-Type: {request.content_type}")
    
    # Verificar método
    if request.method != 'POST':
        logger.warning("❌ Método não permitido")
        return JsonResponse({
            'success': False,
            'error': 'Método não permitido. Use POST.'
        }, status=405)
    
    try:
        # Ler o body
        body = request.body.decode('utf-8')
        logger.info(f"📦 Body recebido: {body}")
        
        if not body:
            logger.error("❌ Body vazio")
            return JsonResponse({
                'success': False,
                'error': 'Body da requisição está vazio'
            }, status=400)
        
        # Parsear JSON
        try:
            data = json.loads(body)
            logger.info(f"📦 Dados parseados: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao parsear JSON: {e}")
            logger.error(f"Body: {body}")
            return JsonResponse({
                'success': False,
                'error': f'JSON inválido: {str(e)}'
            }, status=400)
        
        # Validar dados
        item_id = data.get('item_id')
        quantidade = data.get('quantidade', 1)
        
        logger.info(f"📦 item_id: {item_id}, quantidade: {quantidade}")
        
        if not item_id:
            logger.error("❌ item_id não fornecido")
            return JsonResponse({
                'success': False,
                'error': 'ID do item não fornecido'
            }, status=400)
        
        # Converter quantidade para int
        try:
            quantidade = int(quantidade)
            if quantidade <= 0:
                quantidade = 1
        except (ValueError, TypeError):
            quantidade = 1
        
        logger.info(f"📦 Quantidade convertida: {quantidade}")
        
        # Buscar o item
        try:
            item = Item.objects.get(id=item_id, status='ativo')
            logger.info(f"✅ Item encontrado: {item.id} - {item.nome}")
            logger.info(f"   Tipo: {item.tipo}, Preço: {item.preco_venda}")
        except Item.DoesNotExist:
            logger.error(f"❌ Item {item_id} não encontrado ou inativo")
            return JsonResponse({
                'success': False,
                'error': f'Item {item_id} não encontrado ou inativo'
            }, status=404)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar item: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Erro ao buscar item: {str(e)}'
            }, status=500)
        
        # Verificar stock para produtos
        if item.tipo == 'produto':
            try:
                stock_total = Stock.objects.filter(item=item).aggregate(
                    total=Sum('quantidade_atual')
                )['total'] or 0
                logger.info(f"📦 Stock total disponível: {stock_total}")
                
                if stock_total < quantidade:
                    logger.warning(f"⚠️ Stock insuficiente: {stock_total} < {quantidade}")
                    return JsonResponse({
                        'success': False,
                        'error': f'Stock insuficiente. Disponível: {stock_total}'
                    }, status=400)
            except Exception as e:
                logger.error(f"❌ Erro ao verificar stock: {e}")
                # Continua mesmo com erro no stock
        
        # Inicializar carrinho na sessão
        try:
            if 'carrinho' not in request.session:
                request.session['carrinho'] = []
                request.session['carrinho_total'] = 0
                logger.info("📦 Carrinho inicializado na sessão")
            
            carrinho = request.session.get('carrinho', [])
            logger.info(f"📦 Carrinho atual: {carrinho}")
            
            # Verificar se o item já existe no carrinho
            item_existente = False
            for i, item_data in enumerate(carrinho):
                if item_data.get('id') == item_id:
                    carrinho[i]['quantidade'] += quantidade
                    item_existente = True
                    logger.info(f"📦 Item já existente, nova quantidade: {carrinho[i]['quantidade']}")
                    break
            
            if not item_existente:
                carrinho.append({
                    'id': item_id,
                    'quantidade': quantidade
                })
                logger.info(f"📦 Novo item adicionado: {item_id} x {quantidade}")
            
            # Recalcular total
            total = 0
            for item_data in carrinho:
                try:
                    i = Item.objects.get(id=item_data['id'])
                    subtotal = i.preco_venda * item_data['quantidade']
                    total += subtotal
                    logger.info(f"   {i.nome} x {item_data['quantidade']} = {subtotal}")
                except Item.DoesNotExist:
                    logger.warning(f"⚠️ Item {item_data['id']} não encontrado no banco")
                    continue
            
            logger.info(f"📦 Total calculado: {total}")
            
            # Salvar na sessão
            request.session['carrinho'] = carrinho
            request.session['carrinho_total'] = float(total)
            request.session.modified = True
            
            logger.info(f"✅ Sessão atualizada: {len(carrinho)} itens, total: {total}")
            
            # Resposta de sucesso
            response_data = {
                'success': True,
                'message': f'{item.nome} adicionado ao carrinho!',
                'total_itens': len(carrinho),
                'total': float(total),
                'item': {
                    'id': item.id,
                    'nome': item.nome,
                    'preco': float(item.preco_venda),
                    'quantidade': quantidade
                }
            }
            
            logger.info(f"📤 Resposta: {response_data}")
            logger.info("="*50)
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"❌ Erro na sessão: {e}")
            logger.error(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'error': f'Erro na sessão: {str(e)}'
            }, status=500)
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)


@csrf_exempt
@login_required
def carrinho_remover(request):
    """Remover item do carrinho (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        carrinho = request.session.get('carrinho', [])
        carrinho = [item for item in carrinho if item['id'] != item_id]
        
        total = 0
        for item_data in carrinho:
            try:
                i = Item.objects.get(id=item_data['id'])
                total += i.preco_venda * item_data['quantidade']
            except:
                pass
        
        request.session['carrinho'] = carrinho
        request.session['carrinho_total'] = total
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Item removido do carrinho!',
            'total_itens': len(carrinho),
            'total': float(total)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@login_required
def carrinho_limpar(request):
    """Limpar carrinho"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    if 'carrinho' in request.session:
        del request.session['carrinho']
        request.session['carrinho_total'] = 0
        request.session.modified = True
    
    return JsonResponse({
        'success': True,
        'message': 'Carrinho esvaziado com sucesso!'
    })


# ============================================
# CHECKOUT
# ============================================

@login_required
def checkout(request):
    """Página de checkout/finalização da compra"""
    carrinho = request.session.get('carrinho', [])
    total = request.session.get('carrinho_total', 0)
    
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('servicos:dashboard')
    
    itens_carrinho = []
    for item_data in carrinho:
        try:
            item = Item.objects.get(id=item_data['id'])
            itens_carrinho.append({
                'item': item,
                'quantidade': item_data['quantidade'],
                'subtotal': item.preco_venda * item_data['quantidade']
            })
        except Item.DoesNotExist:
            continue
    
    # Verificar se os itens ainda estão disponíveis
    for item_data in itens_carrinho:
        if item_data['item'].tipo == 'produto':
            stock = Stock.objects.filter(item=item_data['item']).aggregate(
                total=Sum('quantidade_atual')
            )['total'] or 0
            if stock < item_data['quantidade']:
                messages.error(
                    request, 
                    f'Stock insuficiente para "{item_data["item"].nome}". Disponível: {stock}'
                )
                return redirect('servicos:carrinho')
    
    context = {
        'itens_carrinho': itens_carrinho,
        'total': total,
        'total_itens': len(itens_carrinho),
        'user': request.user,
    }
    return render(request, 'servicos/checkout.html', context)


# ============================================
# ITENS (UNIFICADO) - CRUD
# ============================================

@login_required
def detalhe_item(request, item_id):
    """Detalhes de um item"""
    item = get_object_or_404(Item, id=item_id)
    
    # Se for produto, busca stock
    stocks = []
    movimentos = []
    if item.is_produto():
        stocks = Stock.objects.filter(item=item).select_related('local')
        movimentos = MovimentoStock.objects.filter(item=item).order_by('-criado_em')[:50]
    
    # Se for software, busca licenças
    licencas = []
    if item.is_software():
        licencas = Licenca.objects.filter(item=item)
    
    # Contratos e ordens (se for serviço/consultoria)
    contratos = []
    ordens = []
    if item.is_servico() or item.is_software():
        contratos = ContratoServico.objects.filter(servico=item).select_related('cliente')
        ordens = OrdemServico.objects.filter(contrato__servico=item).select_related('cliente', 'contrato')
    
    context = {
        'item': item,
        'stocks': stocks,
        'movimentos': movimentos,
        'licencas': licencas,
        'contratos': contratos,
        'ordens': ordens,
    }
    return render(request, 'servicos/detalhe_item.html', context)


@login_required
def criar_item(request):
    """Redireciona para a lista com modal de criação"""
    messages.info(request, 'Clique em "Novo Item" para criar um item.')
    return redirect('servicos:lista_itens')


@login_required
def editar_item(request, item_id):
    """Redireciona para a lista com modal de edição"""
    messages.info(request, 'Edite o item clicando no ícone de lápis na lista.')
    return redirect('servicos:lista_itens')


# ============================================
# COMPATIBILIDADE (APIs antigas)
# ============================================

@login_required
def lista_servicos(request):
    """Redireciona para a lista unificada de itens"""
    return redirect('servicos:lista_itens')


@login_required
def detalhe_servico(request, servico_id):
    """Redireciona para detalhes do item"""
    return redirect('servicos:detalhe_item', item_id=servico_id)


# ============================================
# APIS PARA MODAIS
# ============================================

@login_required
def api_item_data(request, item_id):
    """API para buscar dados do item (para modals)"""
    try:
        item = get_object_or_404(Item, id=item_id)
        data = item.to_dict()
        
        # Adiciona informações de stock se for produto
        if item.is_produto():
            stocks = Stock.objects.filter(item=item).select_related('local')
            data['stocks'] = [
                {
                    'local': stock.local.nome,
                    'local_id': stock.local.id,
                    'quantidade': stock.quantidade_atual,
                    'minimo': stock.stock_minimo,
                    'ponto_reposicao': stock.ponto_reposicao
                }
                for stock in stocks
            ]
            data['total_stock'] = sum(s['quantidade'] for s in data['stocks'])
        
        # Adiciona informações de contratos se for serviço
        if item.is_servico() or item.is_software():
            data['contratos_ativos'] = ContratoServico.objects.filter(
                servico=item,
                status='ativo'
            ).count()
            data['total_receita'] = float(
                ContratoServico.objects.filter(
                    servico=item,
                    status='ativo'
                ).aggregate(total=Sum('valor_total'))['total'] or 0
            )
        
        # Garantir imagem_url
        if item.imagem:
            data['imagem_url'] = item.imagem.url
        else:
            data['imagem_url'] = None
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro em api_item_data: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def api_criar_item(request):
    """API para criar um novo item via modal"""
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)
    
    try:
        # Verificar se é um upload de arquivo ou JSON
        if request.FILES:
            data = request.POST.dict()
            imagem = request.FILES.get('imagem')
        else:
            data = json.loads(request.body) if request.body else {}
            imagem = None
        
        logger.info(f"📦 Criando item - Dados: {data}")
        
        # Validações
        if not data.get('codigo'):
            return JsonResponse({'success': False, 'error': 'Código é obrigatório'}, status=400)
        if not data.get('nome'):
            return JsonResponse({'success': False, 'error': 'Nome é obrigatório'}, status=400)
        if not data.get('tipo'):
            return JsonResponse({'success': False, 'error': 'Tipo é obrigatório'}, status=400)
        
        # Preço
        try:
            preco_venda = float(data.get('preco_venda', 0))
        except (ValueError, TypeError):
            preco_venda = 0
        
        if preco_venda <= 0:
            return JsonResponse({'success': False, 'error': 'Preço de venda deve ser maior que zero'}, status=400)
        
        # Verifica duplicidade de código
        if Item.objects.filter(codigo=data.get('codigo')).exists():
            return JsonResponse({'success': False, 'error': 'Já existe um item com este código'}, status=400)
        
        # Converter campos
        def to_bool(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', 'on', '1', 'yes')
            return bool(value)
        
        # Criar o item
        item = Item.objects.create(
            codigo=data.get('codigo'),
            nome=data.get('nome'),
            descricao=data.get('descricao', ''),
            tipo=data.get('tipo'),
            status=data.get('status', 'ativo'),
            recorrencia=data.get('recorrencia', 'unico'),
            preco_venda=preco_venda,
            preco_custo=float(data.get('preco_custo')) if data.get('preco_custo') and data.get('preco_custo') != '' else None,
            duracao_padrao=int(data.get('duracao_padrao')) if data.get('duracao_padrao') and data.get('duracao_padrao') != '' else None,
            horas_estimadas=float(data.get('horas_estimadas')) if data.get('horas_estimadas') and data.get('horas_estimadas') != '' else None,
            preco_hora=float(data.get('preco_hora')) if data.get('preco_hora') and data.get('preco_hora') != '' else None,
            nivel_prioridade=int(data.get('nivel_prioridade', 1)),
            requer_visita=to_bool(data.get('requer_visita')),
            requer_equipamento=to_bool(data.get('requer_equipamento')),
            requer_ativacao=to_bool(data.get('requer_ativacao')),
            numero_usuarios_incluidos=int(data.get('numero_usuarios_incluidos', 1)),
            permite_upgrade=to_bool(data.get('permite_upgrade')),
            peso=float(data.get('peso')) if data.get('peso') and data.get('peso') != '' else None,
            dimensoes=data.get('dimensoes', ''),
            codigo_barras=data.get('codigo_barras', ''),
            unidade_medida=data.get('unidade_medida', 'un'),
            imagem=imagem,
            criado_por=request.user
        )
        
        # Se for produto, cria o stock inicial
        if item.is_produto():
            try:
                stock_inicial = int(data.get('stock_inicial', 0) or 0)
                stock_minimo = int(data.get('stock_minimo', 5) or 5)
            except (ValueError, TypeError):
                stock_inicial = 0
                stock_minimo = 5
            
            local, _ = Local.objects.get_or_create(
                nome='Armazém Principal',
                defaults={'tipo': 'armazem_central', 'ativo': True}
            )
            
            Stock.objects.create(
                item=item,
                local=local,
                quantidade_atual=stock_inicial,
                stock_minimo=stock_minimo
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Item {item.nome} criado com sucesso!',
            'id': item.id,
            'imagem_url': item.imagem.url if item.imagem else None
        })
    except Exception as e:
        logger.error(f"❌ Erro ao criar item: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def api_editar_item(request, item_id):
    """API para editar um item existente via modal"""
    import json
    import logging
    import os
    logger = logging.getLogger(__name__)
    
    if request.method not in ['POST', 'PUT']:
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)
    
    try:
        item = get_object_or_404(Item, id=item_id)
        
        # Processar dados para PUT com FormData
        if request.method == 'PUT':
            from django.http import QueryDict
            import urllib.parse
            
            body = request.body.decode('utf-8')
            if body:
                data = {}
                for part in body.split('&'):
                    if '=' in part:
                        key, value = part.split('=', 1)
                        data[key] = urllib.parse.unquote(value)
                imagem = request.FILES.get('imagem')
            else:
                data = {}
                imagem = None
            
            logger.info(f"📦 PUT FORM DATA - Dados: {data}")
        else:
            if request.content_type and 'application/json' in request.content_type:
                try:
                    data = json.loads(request.body) if request.body else {}
                    imagem = None
                    logger.info(f"📦 POST JSON - Dados: {data}")
                except json.JSONDecodeError as e:
                    return JsonResponse({'success': False, 'error': f'JSON inválido: {str(e)}'}, status=400)
            else:
                data = request.POST.dict()
                imagem = request.FILES.get('imagem')
                logger.info(f"📦 POST FORM DATA - Dados: {data}")
        
        # ATUALIZAR CAMPOS
        if data.get('codigo'):
            item.codigo = data.get('codigo')
        if data.get('nome'):
            item.nome = data.get('nome')
        if 'descricao' in data:
            item.descricao = data.get('descricao', '')
        if data.get('tipo'):
            item.tipo = data.get('tipo')
        if data.get('status'):
            item.status = data.get('status')
        if data.get('recorrencia'):
            item.recorrencia = data.get('recorrencia')
        
        try:
            preco_venda = data.get('preco_venda', 0)
            item.preco_venda = float(preco_venda) if preco_venda and preco_venda != '' else 0
        except (ValueError, TypeError):
            item.preco_venda = 0
        
        try:
            preco_custo = data.get('preco_custo')
            item.preco_custo = float(preco_custo) if preco_custo and preco_custo != '' else None
        except (ValueError, TypeError):
            item.preco_custo = None
        
        try:
            duracao = data.get('duracao_padrao')
            item.duracao_padrao = int(duracao) if duracao and duracao != '' else None
        except (ValueError, TypeError):
            item.duracao_padrao = None
        
        try:
            horas = data.get('horas_estimadas')
            item.horas_estimadas = float(horas) if horas and horas != '' else None
        except (ValueError, TypeError):
            item.horas_estimadas = None
        
        try:
            preco_hora = data.get('preco_hora')
            item.preco_hora = float(preco_hora) if preco_hora and preco_hora != '' else None
        except (ValueError, TypeError):
            item.preco_hora = None
        
        try:
            prioridade = data.get('nivel_prioridade', 1)
            item.nivel_prioridade = int(prioridade) if prioridade and prioridade != '' else 1
        except (ValueError, TypeError):
            item.nivel_prioridade = 1
        
        # Booleanos
        item.requer_visita = str(data.get('requer_visita', 'false')).lower() in ('true', 'on', '1', 'yes')
        item.requer_equipamento = str(data.get('requer_equipamento', 'false')).lower() in ('true', 'on', '1', 'yes')
        item.requer_ativacao = str(data.get('requer_ativacao', 'false')).lower() in ('true', 'on', '1', 'yes')
        item.permite_upgrade = str(data.get('permite_upgrade', 'true')).lower() in ('true', 'on', '1', 'yes')
        
        try:
            usuarios = data.get('numero_usuarios_incluidos', 1)
            item.numero_usuarios_incluidos = int(usuarios) if usuarios and usuarios != '' else 1
        except (ValueError, TypeError):
            item.numero_usuarios_incluidos = 1
        
        try:
            peso_val = data.get('peso')
            item.peso = float(peso_val) if peso_val and peso_val != '' else None
        except (ValueError, TypeError):
            item.peso = None
        
        item.dimensoes = data.get('dimensoes', '')
        item.codigo_barras = data.get('codigo_barras', '')
        item.unidade_medida = data.get('unidade_medida', 'un')
        
        # Imagem
        if imagem:
            if item.imagem and os.path.isfile(item.imagem.path):
                try:
                    os.remove(item.imagem.path)
                except:
                    pass
            item.imagem = imagem
        
        item.save()
        logger.info(f"✅ Item {item.id} atualizado: {item.nome}")
        
        # ATUALIZAR STOCK
        if item.is_produto():
            try:
                stock_inicial_str = data.get('stock_inicial', '0')
                stock_minimo_str = data.get('stock_minimo', '5')
                
                try:
                    stock_inicial = int(stock_inicial_str) if stock_inicial_str and str(stock_inicial_str).strip() != '' else 0
                except (ValueError, TypeError):
                    stock_inicial = 0
                
                try:
                    stock_minimo = int(stock_minimo_str) if stock_minimo_str and str(stock_minimo_str).strip() != '' else 5
                except (ValueError, TypeError):
                    stock_minimo = 5
                
                logger.info(f"📦 Stock para salvar: inicial={stock_inicial}, minimo={stock_minimo}")
                
                stock = Stock.objects.filter(item=item).first()
                
                if stock:
                    stock.quantidade_atual = stock_inicial
                    stock.stock_minimo = stock_minimo
                    stock.save()
                    logger.info(f"✅ Stock atualizado: {stock.quantidade_atual}")
                else:
                    local, _ = Local.objects.get_or_create(
                        nome='Armazém Principal',
                        defaults={'tipo': 'armazem_central', 'ativo': True}
                    )
                    stock = Stock.objects.create(
                        item=item,
                        local=local,
                        quantidade_atual=stock_inicial,
                        stock_minimo=stock_minimo
                    )
                    logger.info(f"✅ Stock criado: {stock.quantidade_atual}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar stock: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'Item {item.nome} atualizado com sucesso!',
            'id': item.id,
            'imagem_url': item.imagem.url if item.imagem else None
        })
    except Exception as e:
        logger.error(f"❌ Erro ao editar item: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def api_excluir_item(request, item_id):
    """API para excluir um item"""
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)
    
    try:
        item = get_object_or_404(Item, id=item_id)
        nome = item.nome
        
        # Remover imagem se existir
        if item.imagem:
            if os.path.isfile(item.imagem.path):
                os.remove(item.imagem.path)
        
        item.delete()
        return JsonResponse({
            'success': True,
            'message': f'Item {nome} excluído com sucesso!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================
# STOCK (APENAS PARA PRODUTOS)
# ============================================

@login_required
def api_movimento_stock(request):
    """API para registrar movimentos de stock"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        local_id = data.get('local_id')
        tipo = data.get('tipo')
        quantidade = data.get('quantidade', 0)
        motivo = data.get('motivo')
        observacao = data.get('observacao', '')
        
        item = get_object_or_404(Item, id=item_id)
        
        if not item.is_produto():
            return JsonResponse({'success': False, 'error': 'Apenas produtos têm stock'}, status=400)
        
        local = get_object_or_404(Local, id=local_id)
        
        if tipo == 'entrada':
            from .services import StockService
            movimento, alertas = StockService.entrada_stock(
                item_id=item_id,
                local_id=local_id,
                quantidade=quantidade,
                motivo=motivo,
                usuario_id=request.user.id,
                observacao=observacao
            )
        elif tipo == 'saida':
            from .services import StockService
            movimento, alertas = StockService.saida_stock(
                item_id=item_id,
                local_id=local_id,
                quantidade=quantidade,
                motivo=motivo,
                usuario_id=request.user.id,
                observacao=observacao
            )
        else:
            return JsonResponse({'success': False, 'error': 'Tipo de movimento inválido'}, status=400)
        
        return JsonResponse({
            'success': True,
            'message': 'Movimento registrado com sucesso!',
            'movimento_id': movimento.id,
            'alertas': alertas
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================
# CONTRATOS
# ============================================

@login_required
def lista_contratos(request):
    """Lista todos os contratos"""
    status_filter = request.GET.get('status', '')
    cliente_filter = request.GET.get('cliente', '')
    
    contratos = ContratoServico.objects.all().select_related('cliente', 'servico', 'criado_por')
    
    if status_filter:
        contratos = contratos.filter(status=status_filter)
    
    if cliente_filter:
        contratos = contratos.filter(cliente_id=cliente_filter)
    
    context = {
        'contratos': contratos,
        'status_filter': status_filter,
        'status_options': ContratoServico.STATUS_CHOICES,
        'clientes': User.objects.filter(is_active=True),
    }
    return render(request, 'servicos/lista_contratos.html', context)


@login_required
def detalhe_contrato(request, contrato_id):
    """Detalhes de um contrato"""
    contrato = get_object_or_404(ContratoServico, id=contrato_id)
    ordens = OrdemServico.objects.filter(contrato=contrato).select_related('cliente', 'responsavel')
    faturamentos = FaturamentoRecorrente.objects.filter(contrato=contrato)
    
    stats = {
        'total_ordens': ordens.count(),
        'ordens_concluidas': ordens.filter(status='concluida').count(),
        'total_horas': ordens.aggregate(total=Sum('horas_trabalhadas'))['total'] or 0,
        'total_faturado': faturamentos.aggregate(total=Sum('valor'))['total'] or 0,
    }
    
    context = {
        'contrato': contrato,
        'ordens': ordens,
        'faturamentos': faturamentos,
        'stats': stats,
    }
    return render(request, 'servicos/detalhe_contrato.html', context)


@login_required
def criar_contrato(request):
    """Cria um novo contrato"""
    if request.method == 'POST':
        form = ContratoServicoForm(request.POST)
        if form.is_valid():
            contrato = ServicoService.criar_contrato(
                cliente_id=form.cleaned_data['cliente'].id,
                servico_id=form.cleaned_data['servico'].id,
                preco_acordado=form.cleaned_data['preco_acordado'],
                desconto=form.cleaned_data.get('desconto', 0),
                horas_contratadas=form.cleaned_data.get('horas_contratadas')
            )
            messages.success(request, 'Contrato criado com sucesso!')
            return redirect('servicos:detalhe_contrato', contrato_id=contrato.id)
    else:
        form = ContratoServicoForm()
        cliente_id = request.GET.get('cliente')
        if cliente_id:
            form.fields['cliente'].initial = cliente_id
    
    return render(request, 'servicos/form_contrato.html', {'form': form})


# ============================================
# ORDENS DE SERVIÇO
# ============================================

@login_required
def lista_ordens(request):
    """Lista todas as ordens de serviço"""
    status_filter = request.GET.get('status', '')
    prioridade_filter = request.GET.get('prioridade', '')
    
    ordens = OrdemServico.objects.all().select_related('cliente', 'contrato', 'responsavel')
    
    if status_filter:
        ordens = ordens.filter(status=status_filter)
    
    if prioridade_filter:
        ordens = ordens.filter(prioridade=prioridade_filter)
    
    stats = {
        'total': ordens.count(),
        'abertas': ordens.filter(status='aberta').count(),
        'em_andamento': ordens.filter(status='em_andamento').count(),
        'concluidas': ordens.filter(status='concluida').count(),
        'urgentes': ordens.filter(prioridade='urgente').count(),
    }
    
    context = {
        'ordens': ordens,
        'stats': stats,
        'status_filter': status_filter,
        'prioridade_filter': prioridade_filter,
        'status_options': OrdemServico.STATUS_CHOICES,
        'prioridade_options': OrdemServico.PRIORIDADE_CHOICES,
    }
    return render(request, 'servicos/lista_ordens.html', context)


@login_required
def dashboard_ordens(request):
    """Dashboard de ordens de serviço"""
    status_filter = request.GET.get('status', '')
    prioridade_filter = request.GET.get('prioridade', '')
    
    ordens = OrdemServico.objects.all().select_related('cliente', 'contrato', 'responsavel')
    
    if status_filter:
        ordens = ordens.filter(status=status_filter)
    
    if prioridade_filter:
        ordens = ordens.filter(prioridade=prioridade_filter)
    
    stats = {
        'total': ordens.count(),
        'abertas': ordens.filter(status='aberta').count(),
        'em_andamento': ordens.filter(status='em_andamento').count(),
        'concluidas': ordens.filter(status='concluida').count(),
        'urgentes': ordens.filter(prioridade='urgente').count(),
    }
    
    context = {
        'ordens': ordens,
        'stats': stats,
        'status_filter': status_filter,
        'prioridade_filter': prioridade_filter,
        'status_options': OrdemServico.STATUS_CHOICES,
        'prioridade_options': OrdemServico.PRIORIDADE_CHOICES,
    }
    return render(request, 'servicos/dashboard_ordens.html', context)


@login_required
def detalhe_ordem(request, ordem_id):
    """Detalhes de uma ordem de serviço"""
    ordem = get_object_or_404(OrdemServico, id=ordem_id)
    lancamentos = LancamentoHoras.objects.filter(ordem=ordem).select_related('funcionario')
    
    context = {
        'ordem': ordem,
        'lancamentos': lancamentos,
        'total_horas': sum(l.horas for l in lancamentos),
        'form_lancamento': LancamentoHorasForm(initial={
            'ordem': ordem,
            'funcionario': request.user,
            'data': timezone.now()
        }),
    }
    return render(request, 'servicos/detalhe_ordem.html', context)


@login_required
def criar_ordem(request):
    """Cria uma nova ordem de serviço"""
    if request.method == 'POST':
        form = OrdemServicoForm(request.POST)
        if form.is_valid():
            ordem = form.save(commit=False)
            ordem.save()
            messages.success(request, f'Ordem {ordem.numero} criada com sucesso!')
            return redirect('servicos:detalhe_ordem', ordem_id=ordem.id)
    else:
        form = OrdemServicoForm()
        cliente_id = request.GET.get('cliente')
        if cliente_id:
            form.fields['cliente'].initial = cliente_id
        contrato_id = request.GET.get('contrato')
        if contrato_id:
            form.fields['contrato'].initial = contrato_id
    
    return render(request, 'servicos/form_ordem.html', {'form': form})


@login_required
def lancar_horas(request, ordem_id):
    """Lançamento de horas em uma ordem"""
    ordem = get_object_or_404(OrdemServico, id=ordem_id)
    
    if request.method == 'POST':
        form = LancamentoHorasForm(request.POST)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.ordem = ordem
            lancamento.save()
            
            messages.success(request, f'{lancamento.horas}h lançadas com sucesso!')
            return redirect('servicos:detalhe_ordem', ordem_id=ordem.id)
    else:
        form = LancamentoHorasForm(initial={
            'ordem': ordem,
            'funcionario': request.user,
            'data': timezone.now()
        })
    
    context = {
        'form': form,
        'ordem': ordem,
    }
    return render(request, 'servicos/lancar_horas.html', context)


# ============================================
# FATURAMENTO RECORRENTE
# ============================================

@login_required
def lista_faturamentos(request):
    """Lista faturamentos recorrentes"""
    faturamentos = FaturamentoRecorrente.objects.all().select_related('cliente', 'servico', 'contrato')
    
    context = {
        'faturamentos': faturamentos,
    }
    return render(request, 'servicos/lista_faturamentos.html', context)


# ============================================
# APIS ADICIONAIS (Compatibilidade)
# ============================================

@login_required
def api_servico_data(request, servico_id):
    """Compatibilidade: redireciona para api_item_data"""
    return api_item_data(request, servico_id)


@login_required
def api_contrato_data(request, contrato_id):
    """API para dados do contrato (modals)"""
    try:
        contrato = get_object_or_404(ContratoServico, id=contrato_id)
        ordens = OrdemServico.objects.filter(contrato=contrato)
        
        data = {
            'id': contrato.id,
            'cliente': contrato.cliente.username,
            'cliente_id': contrato.cliente.id,
            'servico': contrato.servico.nome,
            'servico_id': contrato.servico.id,
            'data_inicio': contrato.data_inicio.strftime('%d/%m/%Y %H:%M'),
            'data_fim': contrato.data_fim.strftime('%d/%m/%Y %H:%M') if contrato.data_fim else 'N/A',
            'status': contrato.get_status_display(),
            'preco_acordado': float(contrato.preco_acordado),
            'desconto': float(contrato.desconto),
            'valor_total': float(contrato.valor_total),
            'horas_contratadas': float(contrato.horas_contratadas) if contrato.horas_contratadas else 0,
            'horas_utilizadas': float(contrato.horas_utilizadas),
            'horas_restantes': float(contrato.horas_restantes) if contrato.horas_restantes else 0,
            'renovacao_automatica': contrato.renovacao_automatica,
            'total_ordens': ordens.count(),
            'ordens_concluidas': ordens.filter(status='concluida').count(),
        }
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def api_ordem_data(request, ordem_id):
    """API para dados da ordem (modals)"""
    try:
        ordem = get_object_or_404(OrdemServico, id=ordem_id)
        lancamentos = LancamentoHoras.objects.filter(ordem=ordem).select_related('funcionario')
        
        data = {
            'id': ordem.id,
            'numero': ordem.numero,
            'titulo': ordem.titulo,
            'descricao': ordem.descricao,
            'status': ordem.get_status_display(),
            'prioridade': ordem.get_prioridade_display(),
            'cliente': ordem.cliente.username,
            'contrato_id': ordem.contrato.id,
            'responsavel': ordem.responsavel.username if ordem.responsavel else 'Não definido',
            'data_abertura': ordem.data_abertura.strftime('%d/%m/%Y %H:%M'),
            'data_inicio': ordem.data_inicio.strftime('%d/%m/%Y %H:%M') if ordem.data_inicio else 'N/A',
            'data_conclusao': ordem.data_conclusao.strftime('%d/%m/%Y %H:%M') if ordem.data_conclusao else 'N/A',
            'prazo': ordem.prazo.strftime('%d/%m/%Y %H:%M') if ordem.prazo else 'N/A',
            'horas_estimadas': float(ordem.horas_estimadas) if ordem.horas_estimadas else 0,
            'horas_trabalhadas': float(ordem.horas_trabalhadas),
            'lancamentos': [
                {
                    'id': l.id,
                    'data': l.data.strftime('%d/%m/%Y %H:%M'),
                    'horas': float(l.horas),
                    'descricao': l.descricao,
                    'funcionario': l.funcionario.username
                }
                for l in lancamentos
            ]
        }
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def api_lancar_horas(request):
    """API para lançar horas via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        ordem_id = request.POST.get('ordem_id')
        horas = float(request.POST.get('horas', 0))
        descricao = request.POST.get('descricao', '')
        data_str = request.POST.get('data', None)
        
        ordem = get_object_or_404(OrdemServico, id=ordem_id)
        
        if data_str:
            from dateutil import parser
            data = parser.parse(data_str)
        else:
            data = timezone.now()
        
        if ordem.contrato.horas_restantes and horas > ordem.contrato.horas_restantes:
            return JsonResponse({
                'success': False,
                'error': f'Horas insuficientes. Disponível: {ordem.contrato.horas_restantes}h'
            }, status=400)
        
        lancamento = LancamentoHoras.objects.create(
            ordem=ordem,
            funcionario=request.user,
            horas=horas,
            descricao=descricao,
            data=data
        )
        
        return JsonResponse({
            'success': True,
            'lancamento': {
                'id': lancamento.id,
                'horas': float(lancamento.horas),
                'descricao': lancamento.descricao,
                'data': lancamento.data.strftime('%d/%m/%Y %H:%M'),
                'funcionario': lancamento.funcionario.username
            },
            'total_horas': float(ordem.horas_trabalhadas),
            'horas_restantes': float(ordem.contrato.horas_restantes) if ordem.contrato.horas_restantes else None
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ============================================
# PAINEL ADMINISTRATIVO PERSONALIZADO
# ============================================

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from autenticacao.models import Usuario
from financeiro.models import Fatura
from servicos.models import Item
import json

def is_admin(user):
    """Verifica se o usuário é administrador"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def painel_admin(request):
    """Painel administrativo personalizado"""
    
    # Estatísticas
    total_usuarios = Usuario.objects.count()
    total_clientes = Usuario.objects.filter(is_staff=False).count()
    total_faturas = Fatura.objects.count()
    total_produtos = Item.objects.filter(tipo='produto').count()
    
    # Faturas por status
    faturas_aprovadas = Fatura.objects.filter(status='APROVADA').count()
    faturas_pendentes = Fatura.objects.filter(status='PENDENTE').count()
    faturas_rejeitadas = Fatura.objects.filter(status='REJEITADA').count()
    
    # Valor total das faturas
    valor_total_faturas = Fatura.objects.aggregate(total=Sum('valor_total'))['total'] or 0
    
    # Usuários ativos nos últimos 30 dias
    trinta_dias = timezone.now() - timedelta(days=30)
    usuarios_ativos = Usuario.objects.filter(last_login__gte=trinta_dias).count()
    
    # Últimos usuários cadastrados
    ultimos_usuarios = Usuario.objects.order_by('-date_joined')[:10]
    
    # Últimas faturas
    ultimas_faturas = Fatura.objects.select_related('cliente').order_by('-data_emissao')[:10]
    
    # Últimos clientes
    ultimos_clientes = Usuario.objects.filter(is_staff=False).order_by('-date_joined')[:10]
    
    # Gráfico
    meses = []
    valores = []
    for i in range(6, 0, -1):
        mes = timezone.now() - timedelta(days=i*30)
        mes_str = mes.strftime('%b')
        meses.append(mes_str)
        total_mes = Fatura.objects.filter(
            data_emissao__month=mes.month,
            data_emissao__year=mes.year
        ).aggregate(total=Sum('valor_total'))['total'] or 0
        valores.append(float(total_mes))
    
    context = {
        'titulo': 'Painel Administrativo',
        'total_usuarios': total_usuarios,
        'total_clientes': total_clientes,
        'total_faturas': total_faturas,
        'total_produtos': total_produtos,
        'faturas_aprovadas': faturas_aprovadas,
        'faturas_pendentes': faturas_pendentes,
        'faturas_rejeitadas': faturas_rejeitadas,
        'valor_total_faturas': valor_total_faturas,
        'usuarios_ativos': usuarios_ativos,
        'ultimos_usuarios': ultimos_usuarios,
        'ultimas_faturas': ultimas_faturas,
        'ultimos_clientes': ultimos_clientes,
        'meses': meses,
        'valores': valores,
        'meses_json': json.dumps(meses),
        'valores_json': json.dumps(valores),
    }
    
    return render(request, 'admin_panel/painel.html', context)


# ============================================
# RELATÓRIOS
# ============================================

@login_required
@never_cache
def configuracoes(request):
    """Página de configurações"""
    try:
        config = ConfiguracaoSistema.objects.first()
        if not config:
            config = ConfiguracaoSistema.objects.create()
        config.refresh_from_db()
    except Exception as e:
        config = ConfiguracaoSistema.objects.create()
    
    context = {
        'titulo': 'Configurações',
        'config_sistema': config,
    }
    return render(request, 'servicos/configuracoes.html', context)


@login_required
def gerar_pdf_pedido(request):
    """Gera um PDF com os dados do pedido"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        nome = data.get('nome', '')
        email = data.get('email', '')
        telefone = data.get('telefone', '')
        nif = data.get('nif', '')
        endereco = data.get('endereco', '')
        complemento = data.get('complemento', '')
        observacoes = data.get('observacoes', '')
        itens = data.get('itens', [])
        total = data.get('total', 0)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )
        
        styles = getSampleStyleSheet()
        style_normal = styles['Normal']
        style_heading = styles['Heading1']
        style_heading2 = styles['Heading2']
        
        style_title = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00d4ff'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        style_header = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#7b2ffc'),
            spaceAfter=12
        )
        
        elements = []
        
        elements.append(Paragraph("YITRO ERP", style_title))
        elements.append(Paragraph("Pedido de Compra", style_heading2))
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph(f"Data: {timezone.now().strftime('%d/%m/%Y %H:%M')}", style_normal))
        elements.append(Spacer(1, 1*cm))
        
        elements.append(Paragraph("DADOS DO CLIENTE", style_header))
        elements.append(Spacer(1, 0.3*cm))
        
        dados_cliente = [
            ['Nome:', nome],
            ['Email:', email],
            ['Telefone:', telefone],
            ['NIF:', nif if nif else 'Não informado'],
        ]
        
        table_cliente = Table(dados_cliente, colWidths=[4*cm, 8*cm])
        table_cliente.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#00d4ff')),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#1a1a2e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#00d4ff')),
        ]))
        elements.append(table_cliente)
        elements.append(Spacer(1, 0.5*cm))
        
        elements.append(Paragraph("ENDEREÇO DE ENTREGA", style_header))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(endereco, style_normal))
        if complemento:
            elements.append(Paragraph(f"Complemento: {complemento}", style_normal))
        elements.append(Spacer(1, 0.5*cm))
        
        elements.append(Paragraph("ITENS DO PEDIDO", style_header))
        elements.append(Spacer(1, 0.3*cm))
        
        tabela_dados = [['Item', 'Quantidade', 'Preço Unit.', 'Subtotal']]
        for item in itens:
            tabela_dados.append([
                item.get('nome', ''),
                str(item.get('quantidade', 1)),
                f"Kz {item.get('preco', 0):,.2f}",
                f"Kz {item.get('subtotal', 0):,.2f}"
            ])
        
        tabela_dados.append(['', '', 'TOTAL:', f"Kz {total:,.2f}"])
        
        table_itens = Table(tabela_dados, colWidths=[6*cm, 2.5*cm, 3*cm, 3.5*cm])
        table_itens.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00d4ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.white),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#1a1a2e')),
            ('BACKGROUND', (2, -1), (3, -1), colors.HexColor('#ffa502')),
            ('TEXTCOLOR', (2, -1), (3, -1), colors.white),
            ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (2, -1), (3, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#333333')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#00d4ff')),
            ('ALIGN', (2, -1), (2, -1), 'RIGHT'),
        ]))
        elements.append(table_itens)
        elements.append(Spacer(1, 0.5*cm))
        
        if observacoes:
            elements.append(Paragraph("OBSERVAÇÕES", style_header))
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph(observacoes, style_normal))
            elements.append(Spacer(1, 0.5*cm))
        
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph("🔒 Compra segura • Suporte 24h", ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )))
        elements.append(Paragraph("Yitro ERP - Soluções Tecnológicas", ParagraphStyle(
            'FooterStyle2',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )))
        
        doc.build(elements)
        buffer.seek(0)
        
        return HttpResponse(buffer, content_type='application/pdf')
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao gerar PDF: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# SALVAR CONFIGURAÇÕES (API)
# ============================================

@csrf_exempt
@login_required
def salvar_configuracoes(request):
    """Salva as configurações via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        logger.info(f"📥 Dados recebidos para salvar: {data}")
        
        config = ConfiguracaoSistema.objects.first()
        if not config:
            config = ConfiguracaoSistema.objects.create()
            logger.info("🆕 Nova configuração criada")
        
        # Atualizar campos de texto
        config.whatsapp = data.get('whatsapp', config.whatsapp)
        config.email = data.get('email', config.email)
        config.telefone = data.get('telefone', config.telefone)
        config.endereco = data.get('endereco', config.endereco)
        config.horario = data.get('horario', config.horario)
        config.nome_sistema = data.get('nome_sistema', config.nome_sistema)
        config.moeda_padrao = data.get('moeda_padrao', config.moeda_padrao)
        config.fuso_horario = data.get('fuso_horario', config.fuso_horario)
        config.idioma_padrao = data.get('idioma_padrao', config.idioma_padrao)
        config.serie_padrao = data.get('serie_padrao', config.serie_padrao)
        
        # Atualizar booleanos
        config.dois_fatores = data.get('dois_fatores', config.dois_fatores)
        config.notificacoes_email = data.get('notificacoes_email', config.notificacoes_email)
        config.notificacoes_push = data.get('notificacoes_push', config.notificacoes_push)
        config.alertas_stock = data.get('alertas_stock', config.alertas_stock)
        config.validacao_automatica = data.get('validacao_automatica', config.validacao_automatica)
        config.backup_automatico = data.get('backup_automatico', config.backup_automatico)
        config.logs_sistema = data.get('logs_sistema', config.logs_sistema)
        config.modo_manutencao = data.get('modo_manutencao', config.modo_manutencao)
        
        # Atualizar números
        try:
            config.tempo_sessao = int(data.get('tempo_sessao', config.tempo_sessao))
        except (ValueError, TypeError):
            pass
        
        try:
            config.tentativas_login = int(data.get('tentativas_login', config.tentativas_login))
        except (ValueError, TypeError):
            pass
        
        try:
            config.iva_padrao = Decimal(str(data.get('iva_padrao', config.iva_padrao)))
        except (ValueError, TypeError):
            pass
        
        config.atualizado_por = request.user
        config.save()
        
        # 🔥 FORÇA REFRESH E RETORNA OS DADOS ATUALIZADOS
        config.refresh_from_db()
        
        logger.info(f"✅ Configurações salvas:")
        logger.info(f"  WhatsApp: {config.whatsapp}")
        logger.info(f"  Email: {config.email}")
        logger.info(f"  Telefone: {config.telefone}")
        
        return JsonResponse({
            'status': 'success',
            'message': '✅ Configurações salvas com sucesso!',
            'data': {
                'whatsapp': config.whatsapp,
                'email': config.email,
                'telefone': config.telefone,
                'endereco': config.endereco,
                'horario': config.horario,
                'nome_sistema': config.nome_sistema,
                'moeda_padrao': config.moeda_padrao,
                'fuso_horario': config.fuso_horario,
                'idioma_padrao': config.idioma_padrao,
                'serie_padrao': config.serie_padrao,
                'iva_padrao': float(config.iva_padrao) if config.iva_padrao else 14.0,
                'tempo_sessao': config.tempo_sessao,
                'tentativas_login': config.tentativas_login,
                'dois_fatores': config.dois_fatores,
                'notificacoes_email': config.notificacoes_email,
                'notificacoes_push': config.notificacoes_push,
                'alertas_stock': config.alertas_stock,
                'validacao_automatica': config.validacao_automatica,
                'backup_automatico': config.backup_automatico,
                'logs_sistema': config.logs_sistema,
                'modo_manutencao': config.modo_manutencao,
            }
        })
    except Exception as e:
        logger.error(f"❌ Erro ao salvar: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao salvar: {str(e)}'
        }, status=400)


# ============================================
# API CONFIGURAÇÕES
# ============================================

@login_required
def api_configuracoes(request):
    """API para buscar configurações"""
    config = ConfiguracaoSistema.objects.first()
    if not config:
        config = ConfiguracaoSistema.objects.create()
    
    data = {
        'nome_sistema': config.nome_sistema,
        'moeda_padrao': config.moeda_padrao,
        'fuso_horario': config.fuso_horario,
        'idioma_padrao': config.idioma_padrao,
        'dois_fatores': config.dois_fatores,
        'tempo_sessao': config.tempo_sessao,
        'tentativas_login': config.tentativas_login,
        'notificacoes_email': config.notificacoes_email,
        'notificacoes_push': config.notificacoes_push,
        'alertas_stock': config.alertas_stock,
        'serie_padrao': config.serie_padrao,
        'iva_padrao': float(config.iva_padrao) if config.iva_padrao else 14.0,
        'validacao_automatica': config.validacao_automatica,
        'backup_automatico': config.backup_automatico,
        'logs_sistema': config.logs_sistema,
        'modo_manutencao': config.modo_manutencao,
        'whatsapp': config.whatsapp,
        'email': config.email,
        'telefone': config.telefone,
        'endereco': config.endereco,
        'horario': config.horario,
    }
    
    return JsonResponse({'status': 'success', 'config': data})


# ============================================
# CENTRAL YITRO
# ============================================

@login_required
def central_yitro(request):
    """Central Yitro - Dashboard principal"""
    from financeiro.models import Fatura
    
    context = {
        'titulo': 'Central Yitro',
        'total_usuarios': User.objects.count(),
        'total_produtos': Item.objects.filter(tipo='produto', status='ativo').count(),
        'total_servicos': Item.objects.filter(tipo='servico', status='ativo').count(),
        'total_faturas': Fatura.objects.count(),
    }
    return render(request, 'central.html', context)


@login_required
def relatorios(request):
    """Página de relatórios"""
    context = {
        'titulo': 'Relatórios',
    }
    return render(request, 'servicos/relatorios.html', context)