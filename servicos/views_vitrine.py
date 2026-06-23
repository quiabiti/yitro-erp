# servicos/views_vitrine.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.views.decorators.csrf import csrf_exempt
from .models import Item, Stock
from financeiro.models import Fatura, ItemFatura
from clientes.models import Cliente
import json
import uuid

# ============================================
# VITRINE - PÁGINA PRINCIPAL
# ============================================

def vitrine(request):
    """Página principal da vitrine de produtos e serviços"""
    
    # Buscar todos os itens ativos
    itens = Item.objects.filter(status='ativo').order_by('tipo', 'nome')
    
    # Separar por tipo
    produtos = itens.filter(tipo='produto')
    servicos = itens.filter(tipo__in=['servico', 'consultoria'])
    softwares = itens.filter(tipo='software')
    
    # Produtos com stock disponível
    produtos_com_stock = []
    for produto in produtos:
        stock_total = Stock.objects.filter(item=produto).aggregate(total=Sum('quantidade_atual'))['total'] or 0
        if stock_total > 0:
            produtos_com_stock.append({
                'item': produto,
                'stock': stock_total
            })
    
    # Itens em destaque (mais recentes)
    destaque = Item.objects.filter(status='ativo').order_by('-criado_em')[:6]
    
    # Categorias para filtro
    categorias = {
        'produto': produtos.count(),
        'servico': servicos.count(),
        'software': softwares.count(),
    }
    
    context = {
        'produtos': produtos,
        'servicos': servicos,
        'softwares': softwares,
        'produtos_com_stock': produtos_com_stock,
        'destaque': destaque,
        'categorias': categorias,
        'total_itens': itens.count(),
    }
    
    return render(request, 'servicos/vitrine.html', context)


# ============================================
# VITRINE - CATEGORIAS
# ============================================

def vitrine_categoria(request, categoria):
    """Filtrar itens por categoria"""
    itens = Item.objects.filter(tipo=categoria, status='ativo')
    
    context = {
        'itens': itens,
        'categoria': categoria,
        'total_itens': itens.count(),
    }
    
    return render(request, 'servicos/vitrine_categoria.html', context)


# ============================================
# VITRINE - DETALHES DO PRODUTO
# ============================================

def vitrine_detalhe(request, item_id):
    """Página de detalhes do produto/serviço"""
    item = get_object_or_404(Item, id=item_id, status='ativo')
    
    # Verificar stock se for produto
    stock_disponivel = 0
    if item.tipo == 'produto':
        stock_disponivel = Stock.objects.filter(item=item).aggregate(total=Sum('quantidade_atual'))['total'] or 0
    
    # Itens relacionados (mesmo tipo)
    relacionados = Item.objects.filter(
        tipo=item.tipo, 
        status='ativo'
    ).exclude(id=item.id)[:4]
    
    context = {
        'item': item,
        'stock_disponivel': stock_disponivel,
        'relacionados': relacionados,
        'is_produto': item.tipo == 'produto',
    }
    
    return render(request, 'servicos/vitrine_detalhe.html', context)


# ============================================
# CARRINHO DE COMPRAS (Sessão)
# ============================================

def carrinho(request):
    """Página do carrinho de compras"""
    
    # Inicializar carrinho na sessão
    if 'carrinho' not in request.session:
        request.session['carrinho'] = []
        request.session['carrinho_total'] = 0
    
    carrinho = request.session.get('carrinho', [])
    total = request.session.get('carrinho_total', 0)
    
    # Buscar dados completos dos itens no carrinho
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


@csrf_exempt
def carrinho_adicionar(request):
    """Adicionar item ao carrinho (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantidade = int(data.get('quantidade', 1))
        
        item = get_object_or_404(Item, id=item_id, status='ativo')
        
        # Verificar stock para produtos
        if item.tipo == 'produto':
            stock = Stock.objects.filter(item=item).aggregate(total=Sum('quantidade_atual'))['total'] or 0
            if stock < quantidade:
                return JsonResponse({
                    'error': f'Stock insuficiente. Disponível: {stock}'
                }, status=400)
        
        # Inicializar carrinho
        if 'carrinho' not in request.session:
            request.session['carrinho'] = []
            request.session['carrinho_total'] = 0
        
        carrinho = request.session['carrinho']
        
        # Verificar se item já está no carrinho
        for i, item_data in enumerate(carrinho):
            if item_data['id'] == item_id:
                carrinho[i]['quantidade'] += quantidade
                break
        else:
            carrinho.append({
                'id': item_id,
                'quantidade': quantidade
            })
        
        # Atualizar total
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
            'message': f'{item.nome} adicionado ao carrinho!',
            'total_itens': len(carrinho),
            'total': float(total)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def carrinho_remover(request):
    """Remover item do carrinho (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        carrinho = request.session.get('carrinho', [])
        carrinho = [item for item in carrinho if item['id'] != item_id]
        
        # Recalcular total
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
def carrinho_limpar(request):
    """Limpar carrinho"""
    if 'carrinho' in request.session:
        del request.session['carrinho']
        request.session['carrinho_total'] = 0
        request.session.modified = True
    
    messages.success(request, 'Carrinho esvaziado com sucesso!')
    return redirect('servicos:vitrine')


# ============================================
# FINALIZAR COMPRA
# ============================================

@login_required
def finalizar_compra(request):
    """Finalizar compra e gerar fatura"""
    
    carrinho = request.session.get('carrinho', [])
    
    if not carrinho:
        messages.warning(request, 'O carrinho está vazio!')
        return redirect('servicos:vitrine')
    
    # Buscar ou criar cliente (se for cliente logado)
    cliente = Cliente.objects.filter(email=request.user.email).first()
    if not cliente:
        cliente = Cliente.objects.create(
            nome=request.user.get_full_name() or request.user.username,
            email=request.user.email,
            nif='999999999',  # NIF temporário
            ativo=True
        )
    
    # Criar fatura
    fatura = Fatura.objects.create(
        cliente=cliente,
        data_emissao=timezone.now().date(),
        status='PENDENTE',
        observacoes='Compra realizada via vitrine',
        criado_por=request.user
    )
    
    # Adicionar itens à fatura
    total = 0
    for item_data in carrinho:
        try:
            item = Item.objects.get(id=item_data['id'])
            quantidade = item_data['quantidade']
            preco = item.preco_venda
            subtotal = preco * quantidade
            
            ItemFatura.objects.create(
                fatura=fatura,
                produto=item,
                quantidade=quantidade,
                preco_unitario=preco,
                total=subtotal,
                descricao=item.nome
            )
            
            total += subtotal
            
            # Atualizar stock se for produto
            if item.tipo == 'produto':
                # Buscar primeiro stock disponível
                stock = Stock.objects.filter(item=item, quantidade_atual__gt=0).first()
                if stock:
                    stock.quantidade_atual -= quantidade
                    stock.save()
                    
        except Exception as e:
            messages.error(request, f'Erro ao processar item: {e}')
    
    fatura.valor_total = total
    fatura.save()
    
    # Limpar carrinho
    del request.session['carrinho']
    request.session['carrinho_total'] = 0
    request.session.modified = True
    
    messages.success(request, f'✅ Compra finalizada! Fatura #{fatura.numero} criada.')
    
    return redirect('financeiro:fatura_detail', pk=fatura.id)