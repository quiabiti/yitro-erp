# financeiro/views.py

import json
import logging
from datetime import datetime
from django.db import models
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Sum, Count, Q

# 🔥 IMPORTAR DO FINANCEIRO
from .models import Fatura, Produto, ItemFatura

# 🔥 IMPORTAR CLIENTE DO APP CLIENTES
from clientes.models import Cliente

from .forms import FaturaForm, ClienteForm, ProdutoForm

logger = logging.getLogger(__name__)


# ============================================================
# FUNÇÃO AUXILIAR
# ============================================================
def get_empresa_do_usuario(user):
    """Obtém a empresa do usuário"""
    try:
        if hasattr(user, 'perfil') and user.perfil:
            if hasattr(user.perfil, 'empresa') and user.perfil.empresa:
                return user.perfil.empresa
    except:
        pass
    return None


# ============================================================
# CLIENTES - LIST VIEW (para exibir no financeiro)
# ============================================================
class ClienteListView(LoginRequiredMixin, ListView):
    """Lista de clientes para exibição no financeiro"""
    model = Cliente
    template_name = 'financeiro/clientes/lista.html'
    context_object_name = 'clientes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Cliente.objects.all()
        
        # Busca
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(nif__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Filtrar por empresa (se tiver o campo empresa)
        if hasattr(Cliente, 'empresa') and not self.request.user.is_superuser:
            empresa = get_empresa_do_usuario(self.request.user)
            if empresa:
                queryset = queryset.filter(empresa=empresa)
            else:
                return Cliente.objects.none()
        
        return queryset.order_by('nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        context['titulo'] = 'Clientes'
        context['total_clientes'] = queryset.count()
        context['clientes_ativos'] = queryset.filter(ativo=True).count() if hasattr(Cliente, 'ativo') else queryset.count()
        context['clientes_inativos'] = queryset.filter(ativo=False).count() if hasattr(Cliente, 'ativo') else 0
        context['search_query'] = self.request.GET.get('q', '')
        
        return context


# ============================================================
# FATURA - LIST VIEW (com cards e modais)
# ============================================================
class FaturaListView(LoginRequiredMixin, ListView):
    """Lista de faturas com cards e modais"""
    model = Fatura
    template_name = 'financeiro/faturas/lista.html'
    context_object_name = 'faturas'
    paginate_by = 20
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Fatura.objects.all().order_by('-data_emissao')
        
        empresa = get_empresa_do_usuario(self.request.user)
        if empresa:
            return Fatura.objects.filter(empresa=empresa).order_by('-data_emissao')
        return Fatura.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        queryset = self.get_queryset()
        
        # Estatísticas para os cards
        context['total_faturas'] = queryset.count()
        context['faturas_aprovadas'] = queryset.filter(status='APROVADA').count()
        context['faturas_pendentes'] = queryset.filter(status='PENDENTE').count()
        context['faturas_rejeitadas'] = queryset.filter(status='REJEITADA').count()
        context['total_valor'] = queryset.aggregate(total=Sum('valor_total'))['total'] or 0
        
        # 🔥 CLIENTES PARA O MODAL - USANDO O APP CLIENTES
        if self.request.user.is_superuser:
            context['clientes'] = Cliente.objects.all().order_by('nome')
        else:
            empresa = get_empresa_do_usuario(self.request.user)
            if empresa and hasattr(Cliente, 'empresa'):
                context['clientes'] = Cliente.objects.filter(empresa=empresa, ativo=True).order_by('nome')
            else:
                context['clientes'] = Cliente.objects.all().order_by('nome') if self.request.user.is_superuser else Cliente.objects.none()
        
        # 🔥 LOG PARA DEBUG
        logger.info(f"📋 Total de clientes no contexto: {context['clientes'].count()}")
        for cliente in context['clientes']:
            logger.info(f"  - Cliente: {cliente.nome} (ID: {cliente.id})")
        
        # Data atual para o formulário
        context['today'] = datetime.now().date()
        
        return context


# ============================================================
# FATURA - CREATE VIEW (via modal)
# ============================================================
class FaturaCreateView(LoginRequiredMixin, CreateView):
    """Criar fatura via modal"""
    model = Fatura
    form_class = FaturaForm
    template_name = 'financeiro/faturas/lista.html'
    success_url = reverse_lazy('financeiro:faturas_lista')
    
    def form_valid(self, form):
        empresa = get_empresa_do_usuario(self.request.user)
        
        if not empresa and not self.request.user.is_superuser:
            messages.error(self.request, 'Usuário não tem empresa associada.')
            return self.form_invalid(form)
        
        if not self.request.user.is_superuser:
            form.instance.empresa = empresa
        
        form.instance.criado_por = self.request.user
        
        # Gerar número da fatura
        if not form.instance.numero:
            form.instance.numero = self.gerar_numero_fatura()
        
        messages.success(self.request, '✅ Fatura criada com sucesso!')
        return super().form_valid(form)
    
    def gerar_numero_fatura(self):
        """Gera número sequencial da fatura"""
        ano = datetime.now().year
        ultima = Fatura.objects.filter(data_emissao__year=ano).order_by('-numero').first()
        if ultima and ultima.numero:
            try:
                num = int(ultima.numero.split('/')[0]) + 1
            except:
                num = 1
        else:
            num = 1
        return f"{num:04d}/{ano}"


# ============================================================
# FATURA - UPDATE VIEW (via modal)
# ============================================================
class FaturaUpdateView(LoginRequiredMixin, UpdateView):
    """Editar fatura via modal"""
    model = Fatura
    form_class = FaturaForm
    template_name = 'financeiro/faturas/lista.html'
    success_url = reverse_lazy('financeiro:faturas_lista')
    
    def get_object(self, queryset=None):
        """Buscar com filtro por empresa"""
        obj = super().get_object(queryset)
        
        if not self.request.user.is_superuser:
            empresa = get_empresa_do_usuario(self.request.user)
            if obj.empresa != empresa:
                raise PermissionDenied("Você não tem permissão para editar esta fatura.")
        
        return obj
    
    def form_valid(self, form):
        messages.success(self.request, '✅ Fatura atualizada com sucesso!')
        return super().form_valid(form)


# ============================================================
# FATURA - DELETE VIEW (via modal)
# ============================================================
class FaturaDeleteView(LoginRequiredMixin, DeleteView):
    """Excluir fatura via modal"""
    model = Fatura
    template_name = 'financeiro/faturas/lista.html'
    success_url = reverse_lazy('financeiro:faturas_lista')
    
    def get_object(self, queryset=None):
        """Buscar com filtro por empresa"""
        obj = super().get_object(queryset)
        
        if not self.request.user.is_superuser:
            empresa = get_empresa_do_usuario(self.request.user)
            if obj.empresa != empresa:
                raise PermissionDenied("Você não tem permissão para excluir esta fatura.")
        
        return obj
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '✅ Fatura excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# ============================================================
# FATURA - DETAIL VIEW (via modal)
# ============================================================
class FaturaDetailView(LoginRequiredMixin, DetailView):
    """Detalhes da fatura via modal"""
    model = Fatura
    template_name = 'financeiro/faturas/lista.html'
    context_object_name = 'fatura'
    
    def get_object(self, queryset=None):
        """Buscar com filtro por empresa"""
        obj = super().get_object(queryset)
        
        if not self.request.user.is_superuser:
            empresa = get_empresa_do_usuario(self.request.user)
            if obj.empresa != empresa:
                raise PermissionDenied("Você não tem permissão para visualizar esta fatura.")
        
        return obj
    
    def get(self, request, *args, **kwargs):
        """Suporte para JSON (requisições AJAX)"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            self.object = self.get_object()
            data = {
                'id': self.object.id,
                'numero': self.object.numero,
                'cliente_nome': self.object.cliente.nome if self.object.cliente else '-',
                'cliente_id': self.object.cliente.id if self.object.cliente else None,
                'data_emissao': self.object.data_emissao.strftime('%Y-%m-%d'),
                'data_emissao_display': self.object.data_emissao.strftime('%d/%m/%Y'),
                'status': self.object.status,
                'status_display': self.object.get_status_display(),
                'valor_total': float(self.object.valor_total or 0),
                'hash_controlo': self.object.hash_controlo or '',
                'observacoes': self.object.observacoes or '',
                'itens': [
                    {
                        'produto_nome': item.produto.nome if item.produto else item.descricao,
                        'quantidade': float(item.quantidade),
                        'preco_unitario': float(item.preco_unitario),
                        'total': float(item.total)
                    } for item in self.object.itens.all()
                ],
                'total_geral': float(self.object.valor_total or 0)
            }
            return JsonResponse({'status': 'success', 'fatura': data})
        
        return super().get(request, *args, **kwargs)


# ============================================================
# API VIEWS PARA FATURAS (AJAX)
# ============================================================

class FaturaAPIListCreateView(LoginRequiredMixin, View):
    """API para listar e criar faturas via AJAX"""
    
    def get_empresa(self, request):
        return get_empresa_do_usuario(request.user)
    
    def get(self, request):
        """Listar faturas em JSON"""
        if request.user.is_superuser:
            faturas = Fatura.objects.all().order_by('-data_emissao')
        else:
            empresa = self.get_empresa(request)
            if not empresa:
                return JsonResponse({'error': 'Usuário sem empresa associada'}, status=400)
            faturas = Fatura.objects.filter(empresa=empresa).order_by('-data_emissao')
        
        data = []
        for fatura in faturas:
            data.append({
                'id': fatura.id,
                'numero': fatura.numero,
                'cliente_nome': fatura.cliente.nome if fatura.cliente else '-',
                'data_emissao_display': fatura.data_emissao.strftime('%d/%m/%Y'),
                'valor_total': float(fatura.valor_total or 0),
                'status': fatura.status,
                'status_display': fatura.get_status_display(),
                'status_class': 'success' if fatura.status == 'APROVADA' else 'warning' if fatura.status == 'PENDENTE' else 'danger',
                'hash_controlo': fatura.hash_controlo or ''
            })
        
        return JsonResponse({'status': 'success', 'faturas': data})
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Criar nova fatura via AJAX"""
        try:
            data = json.loads(request.body)
            
            empresa = self.get_empresa(request)
            if not empresa and not request.user.is_superuser:
                return JsonResponse({'error': 'Usuário sem empresa associada'}, status=400)
            
            # Validar campos obrigatórios
            cliente_id = data.get('cliente_id')
            data_emissao = data.get('data_emissao')
            itens = data.get('itens', [])
            
            if not cliente_id:
                return JsonResponse({'error': 'Selecione um cliente'}, status=400)
            if not itens:
                return JsonResponse({'error': 'Adicione pelo menos um item'}, status=400)
            
            # 🔥 BUSCAR CLIENTE DO APP CLIENTES
            cliente = get_object_or_404(Cliente, id=cliente_id)
            
            # Calcular total
            total = 0
            itens_objects = []
            for item_data in itens:
                quantidade = float(item_data.get('quantidade', 0))
                preco = float(item_data.get('preco_unitario', 0))
                total += quantidade * preco
                
                # Buscar ou criar produto
                produto_nome = item_data.get('produto_nome', 'Produto')
                produto = Produto.objects.filter(nome__iexact=produto_nome).first()
                if not produto:
                    produto = Produto.objects.create(
                        nome=produto_nome,
                        preco=preco,
                        empresa=empresa if not request.user.is_superuser else None
                    )
                
                itens_objects.append({
                    'produto': produto,
                    'quantidade': quantidade,
                    'preco_unitario': preco,
                    'total': quantidade * preco,
                    'descricao': produto_nome
                })
            
            # Criar fatura
            fatura = Fatura(
                cliente=cliente,
                data_emissao=datetime.strptime(data_emissao, '%Y-%m-%d').date(),
                status=data.get('status', 'PENDENTE'),
                observacoes=data.get('observacoes', ''),
                valor_total=total,
                criado_por=request.user
            )
            
            if not request.user.is_superuser:
                fatura.empresa = empresa
            
            # Gerar número da fatura
            fatura.numero = self.gerar_numero_fatura(empresa)
            
            fatura.save()
            
            # Salvar itens
            for item in itens_objects:
                ItemFatura.objects.create(
                    fatura=fatura,
                    produto=item['produto'],
                    quantidade=item['quantidade'],
                    preco_unitario=item['preco_unitario'],
                    total=item['total'],
                    descricao=item['descricao']
                )
            
            return JsonResponse({
                'status': 'success',
                'message': '✅ Fatura criada com sucesso!',
                'fatura': {
                    'id': fatura.id,
                    'numero': fatura.numero,
                    'cliente_nome': fatura.cliente.nome,
                    'data_emissao_display': fatura.data_emissao.strftime('%d/%m/%Y'),
                    'valor_total': float(fatura.valor_total),
                    'status': fatura.status,
                    'status_display': fatura.get_status_display()
                }
            })
            
        except Exception as e:
            logger.error(f"Erro ao criar fatura: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
    
    def gerar_numero_fatura(self, empresa):
        """Gera número sequencial da fatura"""
        ano = datetime.now().year
        query = Fatura.objects.filter(data_emissao__year=ano)
        if empresa:
            query = query.filter(empresa=empresa)
        ultima = query.order_by('-numero').first()
        
        if ultima and ultima.numero:
            try:
                num = int(ultima.numero.split('/')[0]) + 1
            except:
                num = 1
        else:
            num = 1
        return f"{num:04d}/{ano}"


class FaturaAPIUpdateView(LoginRequiredMixin, View):
    """API para atualizar fatura via AJAX"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        try:
            data = json.loads(request.body)
            
            # Buscar fatura com segurança
            if request.user.is_superuser:
                fatura = get_object_or_404(Fatura, id=pk)
            else:
                empresa = get_empresa_do_usuario(request.user)
                if not empresa:
                    return JsonResponse({'error': 'Usuário sem empresa associada'}, status=400)
                fatura = get_object_or_404(Fatura, id=pk, empresa=empresa)
            
            # Atualizar campos
            if 'cliente_id' in data:
                fatura.cliente = get_object_or_404(Cliente, id=data['cliente_id'])
            if 'data_emissao' in data:
                fatura.data_emissao = datetime.strptime(data['data_emissao'], '%Y-%m-%d').date()
            if 'status' in data:
                fatura.status = data['status']
            if 'observacoes' in data:
                fatura.observacoes = data['observacoes']
            
            # Atualizar itens (se fornecidos)
            if 'itens' in data:
                # Remover itens antigos
                fatura.itens.all().delete()
                
                total = 0
                for item_data in data['itens']:
                    quantidade = float(item_data.get('quantidade', 0))
                    preco = float(item_data.get('preco_unitario', 0))
                    total += quantidade * preco
                    
                    produto_nome = item_data.get('produto_nome', 'Produto')
                    produto = Produto.objects.filter(nome__iexact=produto_nome).first()
                    if not produto:
                        produto = Produto.objects.create(
                            nome=produto_nome,
                            preco=preco,
                            empresa=fatura.empresa
                        )
                    
                    ItemFatura.objects.create(
                        fatura=fatura,
                        produto=produto,
                        quantidade=quantidade,
                        preco_unitario=preco,
                        total=quantidade * preco,
                        descricao=produto_nome
                    )
                
                fatura.valor_total = total
                fatura.save()
            
            fatura.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '✅ Fatura atualizada com sucesso!',
                'fatura': {
                    'id': fatura.id,
                    'numero': fatura.numero,
                    'cliente_nome': fatura.cliente.nome,
                    'data_emissao_display': fatura.data_emissao.strftime('%d/%m/%Y'),
                    'valor_total': float(fatura.valor_total),
                    'status': fatura.status
                }
            })
            
        except Exception as e:
            logger.error(f"Erro ao atualizar fatura: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


class FaturaAPIDeleteView(LoginRequiredMixin, View):
    """API para excluir fatura via AJAX"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def delete(self, request, pk):
        try:
            # Buscar fatura com segurança
            if request.user.is_superuser:
                fatura = get_object_or_404(Fatura, id=pk)
            else:
                empresa = get_empresa_do_usuario(request.user)
                if not empresa:
                    return JsonResponse({'error': 'Usuário sem empresa associada'}, status=400)
                fatura = get_object_or_404(Fatura, id=pk, empresa=empresa)
            
            numero = fatura.numero
            fatura.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'✅ Fatura {numero} excluída com sucesso!'
            })
            
        except Exception as e:
            logger.error(f"Erro ao excluir fatura: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


# ============================================================
# VIEWS SIMPLES (FUNÇÃO) - COMPATIBILIDADE
# ============================================================

def lista_faturas(request):
    """View simples para compatibilidade com URLs existentes"""
    view = FaturaListView()
    view.request = request
    view.args = []
    view.kwargs = {}
    return view.get(request)

# financeiro/views.py - Adicionar função de upload

# ============================================================
# 🔥 UPLOAD DE IMAGEM - CORRIGIDO (com logs)
# ============================================================

import base64
import json
import logging
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from datetime import datetime

logger = logging.getLogger(__name__)


def detectar_tipo_imagem(arquivo):
    """Detecta o tipo de imagem pelos primeiros bytes (sem imghdr)"""
    try:
        if hasattr(arquivo, 'read'):
            posicao = arquivo.tell()
            cabecalho = arquivo.read(12)
            arquivo.seek(posicao)
        else:
            cabecalho = arquivo[:12]
        
        if cabecalho.startswith(b'\xFF\xD8\xFF'):
            return 'jpeg'
        elif cabecalho.startswith(b'\x89PNG\x0D\x0A\x1A\x0A'):
            return 'png'
        elif cabecalho.startswith(b'GIF87a') or cabecalho.startswith(b'GIF89a'):
            return 'gif'
        elif cabecalho.startswith(b'RIFF') and cabecalho[8:12] == b'WEBP':
            return 'webp'
        elif cabecalho.startswith(b'BM'):
            return 'bmp'
        elif cabecalho.startswith(b'II') or cabecalho.startswith(b'MM'):
            return 'tiff'
        return None
    except Exception as e:
        logger.error(f"Erro ao detectar tipo: {e}")
        return None


@csrf_exempt
def upload_produto_imagem(request, produto_id):
    """Upload de imagem para produto - compatível com todos os dispositivos"""
    
    # 🔥 LOG PARA DEBUG
    logger.info(f"📸 Upload de imagem - Produto ID: {produto_id}")
    logger.info(f"📸 Método: {request.method}")
    logger.info(f"📸 FILES: {request.FILES.keys()}")
    logger.info(f"📸 POST: {request.POST.keys()}")
    
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Método não permitido'}, status=405)
        
        # 🔥 VERIFICAR AUTENTICAÇÃO
        if not request.user.is_authenticated:
            logger.warning("❌ Usuário não autenticado")
            return JsonResponse({'error': 'Não autenticado'}, status=401)
        
        # 🔥 VERIFICAR PERMISSÃO
        if not request.user.is_superuser and not request.user.is_staff:
            logger.warning(f"❌ Usuário sem permissão: {request.user.username}")
            return JsonResponse({'error': 'Sem permissão'}, status=403)
        
        from .models import Produto
        produto = get_object_or_404(Produto, id=produto_id)
        logger.info(f"✅ Produto encontrado: {produto.nome}")
        
        # 🔥 VERIFICAR EMPRESA
        if not request.user.is_superuser:
            empresa = get_empresa_do_usuario(request.user)
            if hasattr(produto, 'empresa') and produto.empresa and produto.empresa != empresa:
                logger.warning(f"❌ Empresa não coincide: {produto.empresa} vs {empresa}")
                return JsonResponse({'error': 'Sem permissão'}, status=403)
        
        # 🔥 REMOVER IMAGEM
        if request.POST.get('remover') == 'true':
            logger.info("🗑️ Removendo imagem")
            if produto.imagem:
                produto.imagem.delete()
                produto.save()
            return JsonResponse({
                'success': True,
                'message': 'Imagem removida com sucesso!',
                'url': None
            })
        
        # 🔥 UPLOAD VIA FORM (COMPUTADOR)
        if request.FILES.get('imagem'):
            imagem = request.FILES['imagem']
            logger.info(f"📷 Upload via FORM - Tamanho: {imagem.size} bytes, Tipo: {imagem.content_type}")
            
            # Validar tamanho (5MB)
            if imagem.size > 5 * 1024 * 1024:
                return JsonResponse({'error': 'Imagem muito grande (máx 5MB)'}, status=400)
            
            # Validar tipo
            img_type = detectar_tipo_imagem(imagem)
            logger.info(f"📷 Tipo detectado: {img_type}")
            
            if img_type not in ['jpeg', 'png', 'gif', 'webp']:
                return JsonResponse({'error': f'Formato não suportado: {img_type}'}, status=400)
            
            produto.imagem = imagem
            produto.save()
            logger.info(f"✅ Imagem salva com sucesso: {produto.imagem.url}")
            
            return JsonResponse({
                'success': True,
                'message': 'Imagem atualizada com sucesso!',
                'url': produto.imagem.url if produto.imagem else None
            })
        
        # 🔥 UPLOAD VIA BASE64 (CELULAR)
        elif request.POST.get('imagem_base64'):
            imagem_base64 = request.POST.get('imagem_base64')
            logger.info(f"📱 Upload via Base64 - Tamanho: {len(imagem_base64)} caracteres")
            
            # 🔥 VALIDAR SE É UM BASE64 VÁLIDO
            if not imagem_base64 or len(imagem_base64) < 100:
                logger.error("❌ Base64 inválido ou muito curto")
                return JsonResponse({'error': 'Dados da imagem inválidos'}, status=400)
            
            # Extrair dados da imagem
            if ';base64,' in imagem_base64:
                formato, img_str = imagem_base64.split(';base64,', 1)
                extensao = formato.split('/')[-1] if '/' in formato else 'png'
                logger.info(f"📱 Formato detectado: {extensao}")
                
                if extensao in ['jpeg', 'jpg']:
                    extensao = 'jpg'
                elif extensao not in ['png', 'gif', 'webp']:
                    extensao = 'png'
            else:
                img_str = imagem_base64
                extensao = 'png'
                logger.warning("⚠️ Base64 sem cabeçalho, usando PNG como fallback")
            
            # 🔥 DECODIFICAR COM TRATAMENTO DE ERRO
            try:
                image_data = base64.b64decode(img_str)
                logger.info(f"📱 Dados decodificados: {len(image_data)} bytes")
            except Exception as e:
                logger.error(f"❌ Erro ao decodificar Base64: {e}")
                return JsonResponse({'error': 'Erro ao decodificar imagem'}, status=400)
            
            # Validar tamanho (5MB)
            if len(image_data) > 5 * 1024 * 1024:
                return JsonResponse({'error': 'Imagem muito grande (máx 5MB)'}, status=400)
            
            # Criar nome único
            filename = f"produtos/{produto.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extensao}"
            logger.info(f"📁 Salvando como: {filename}")
            
            # Salvar
            try:
                produto.imagem.save(filename, ContentFile(image_data), save=True)
                logger.info(f"✅ Imagem salva com sucesso: {produto.imagem.url}")
            except Exception as e:
                logger.error(f"❌ Erro ao salvar imagem: {e}")
                return JsonResponse({'error': f'Erro ao salvar: {str(e)}'}, status=500)
            
            return JsonResponse({
                'success': True,
                'message': 'Imagem atualizada com sucesso!',
                'url': produto.imagem.url if produto.imagem else None
            })
        
        logger.warning("⚠️ Nenhuma imagem fornecida")
        return JsonResponse({'error': 'Nenhuma imagem fornecida'}, status=400)
        
    except Exception as e:
        logger.error(f"❌ Erro no upload de imagem: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)