from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import Item, Stock, MovimentoStock, Local
from .services.stock_service import StockService
from .forms import ItemForm, MovimentoStockForm

@login_required
def lista_itens(request):
    """Lista todos os itens com filtros"""
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    
    items = Item.objects.all()
    
    if query:
        items = items.filter(
            Q(nome__icontains=query) |
            Q(codigo__icontains=query) |
            Q(descricao__icontains=query)
        )
    
    if tipo:
        items = items.filter(tipo=tipo)
    
    # Prepara dados para o modal (otimizado com to_dict)
    items_data = [item.to_dict() for item in items]
    
    context = {
        'items': items,
        'items_json': json.dumps(items_data),  # Para usar no JavaScript
        'query': query,
        'tipo': tipo,
        'tipos': Item.TIPO_CHOICES,
    }
    return render(request, 'core/lista_itens.html', context)


@login_required
def detalhe_item(request, item_id):
    """Detalhes de um item específico"""
    item = get_object_or_404(Item, id=item_id)
    
    # Stock se for produto
    stocks = []
    if item.is_produto():
        stocks = Stock.objects.filter(item=item).select_related('local')
    
    # Histórico de movimentos
    movimentos = MovimentoStock.objects.filter(item=item).order_by('-criado_em')[:50]
    
    # Licenças se for software
    licencas = []
    if item.is_software():
        licencas = Licenca.objects.filter(item=item)
    
    # Dados para o modal
    item_data = item.to_dict()
    
    context = {
        'item': item,
        'item_json': json.dumps(item_data),
        'stocks': stocks,
        'movimentos': movimentos,
        'licencas': licencas,
    }
    return render(request, 'core/detalhe_item.html', context)


@login_required
def api_item_data(request, item_id):
    """API para buscar dados do item em JSON (para modals)"""
    try:
        item = get_object_or_404(Item, id=item_id)
        data = item.to_dict()
        
        # Adiciona informações adicionais para o modal
        if item.is_produto():
            data['stocks'] = [
                {
                    'local': stock.local.nome,
                    'quantidade': stock.quantidade_atual,
                    'minimo': stock.stock_minimo,
                    'ponto_reposicao': stock.ponto_reposicao
                }
                for stock in Stock.objects.filter(item=item).select_related('local')
            ]
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)