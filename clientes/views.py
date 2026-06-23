# clientes/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
import json
import logging

from .models import Cliente
from .forms import ClienteForm

logger = logging.getLogger(__name__)


# ============================================
# CLIENTES - LIST VIEW
# ============================================
class ClienteListView(LoginRequiredMixin, ListView):
    """Lista de clientes"""
    model = Cliente
    template_name = 'clientes/lista.html'
    context_object_name = 'clientes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Busca
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(nif__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        return queryset.order_by('nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        context['titulo'] = 'Clientes'
        context['total_clientes'] = queryset.count()
        context['clientes_ativos'] = queryset.filter(ativo=True).count()
        context['clientes_inativos'] = queryset.filter(ativo=False).count()
        context['search_query'] = self.request.GET.get('q', '')
        
        return context


# ============================================
# CLIENTES - CREATE VIEW
# ============================================
class ClienteCreateView(LoginRequiredMixin, CreateView):
    """Criar cliente via modal"""
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/lista.html'
    success_url = reverse_lazy('clientes:lista')
    
    def form_valid(self, form):
        # Verifica se NIF já existe
        nif = form.cleaned_data.get('nif')
        if Cliente.objects.filter(nif=nif).exists():
            messages.error(self.request, f'Já existe um cliente com o NIF "{nif}".')
            return self.form_invalid(form)
        
        messages.success(self.request, '✅ Cliente criado com sucesso!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Novo Cliente'
        context['is_update'] = False
        return context


# ============================================
# CLIENTES - UPDATE VIEW
# ============================================
class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    """Editar cliente via modal"""
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/lista.html'
    success_url = reverse_lazy('clientes:lista')
    
    def form_valid(self, form):
        # Verifica se NIF já existe (excluindo o próprio)
        nif = form.cleaned_data.get('nif')
        if Cliente.objects.filter(nif=nif).exclude(pk=self.object.pk).exists():
            messages.error(self.request, f'Já existe um cliente com o NIF "{nif}".')
            return self.form_invalid(form)
        
        messages.success(self.request, '✅ Cliente atualizado com sucesso!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Cliente'
        context['is_update'] = True
        return context


# ============================================
# CLIENTES - DELETE VIEW
# ============================================
class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    """Excluir cliente via modal"""
    model = Cliente
    template_name = 'clientes/lista.html'
    success_url = reverse_lazy('clientes:lista')
    
    def delete(self, request, *args, **kwargs):
        cliente = self.get_object()
        nome = cliente.nome
        cliente.delete()
        messages.success(request, f'✅ Cliente "{nome}" excluído com sucesso!')
        return redirect('clientes:lista')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Excluir Cliente'
        return context


# ============================================
# CLIENTES - DETAIL VIEW
# ============================================
class ClienteDetailView(LoginRequiredMixin, DetailView):
    """Detalhes do cliente via modal"""
    model = Cliente
    template_name = 'clientes/lista.html'
    context_object_name = 'cliente'
    
    def get(self, request, *args, **kwargs):
        """Suporte para JSON (requisições AJAX)"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            self.object = self.get_object()
            data = {
                'id': self.object.id,
                'nome': self.object.nome,
                'nif': self.object.nif,
                'endereco': self.object.endereco,
                'telefone': self.object.telefone,
                'email': self.object.email,
                'ativo': self.object.ativo,
                'data_criacao': self.object.data_criacao.strftime('%d/%m/%Y %H:%M') if self.object.data_criacao else '-',
                'data_atualizacao': self.object.data_atualizacao.strftime('%d/%m/%Y %H:%M') if self.object.data_atualizacao else '-',
            }
            return JsonResponse({'status': 'success', 'cliente': data})
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detalhes do Cliente'
        return context


# ============================================
# API VIEWS PARA CLIENTES
# ============================================

class ClienteAPIListCreateView(LoginRequiredMixin, View):
    """API para listar e criar clientes via AJAX"""
    
    def get(self, request):
        """Listar clientes em JSON"""
        clientes = Cliente.objects.all().order_by('nome')
        
        # Busca
        search_query = request.GET.get('q', '').strip()
        if search_query:
            clientes = clientes.filter(
                Q(nome__icontains=search_query) |
                Q(nif__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        data = []
        for cliente in clientes:
            data.append({
                'id': cliente.id,
                'nome': cliente.nome,
                'nif': cliente.nif,
                'telefone': cliente.telefone,
                'email': cliente.email,
                'endereco': cliente.endereco,
                'ativo': cliente.ativo,
                'data_criacao': cliente.data_criacao.strftime('%d/%m/%Y') if cliente.data_criacao else '-',
            })
        
        return JsonResponse({'status': 'success', 'clientes': data})
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Criar novo cliente via AJAX"""
        try:
            data = json.loads(request.body)
            
            # Validar campos obrigatórios
            nome = data.get('nome', '').strip()
            nif = data.get('nif', '').strip()
            
            if not nome:
                return JsonResponse({'error': 'O nome é obrigatório.'}, status=400)
            if not nif:
                return JsonResponse({'error': 'O NIF é obrigatório.'}, status=400)
            
            # Verificar duplicidade de NIF
            if Cliente.objects.filter(nif=nif).exists():
                return JsonResponse({'error': f'Já existe um cliente com o NIF "{nif}".'}, status=400)
            
            # Criar cliente
            cliente = Cliente(
                nome=nome,
                nif=nif,
                endereco=data.get('endereco', ''),
                telefone=data.get('telefone', ''),
                email=data.get('email', ''),
                ativo=data.get('ativo', True)
            )
            
            cliente.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '✅ Cliente criado com sucesso!',
                'cliente': {
                    'id': cliente.id,
                    'nome': cliente.nome,
                    'nif': cliente.nif,
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dados inválidos.'}, status=400)
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


class ClienteAPIUpdateView(LoginRequiredMixin, View):
    """API para atualizar cliente via AJAX"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        try:
            data = json.loads(request.body)
            
            # Buscar cliente
            cliente = get_object_or_404(Cliente, id=pk)
            
            # Validar campos obrigatórios
            nome = data.get('nome', '').strip()
            nif = data.get('nif', '').strip()
            
            if not nome:
                return JsonResponse({'error': 'O nome é obrigatório.'}, status=400)
            if not nif:
                return JsonResponse({'error': 'O NIF é obrigatório.'}, status=400)
            
            # Verificar duplicidade de NIF (excluindo o próprio)
            if Cliente.objects.filter(nif=nif).exclude(pk=cliente.pk).exists():
                return JsonResponse({'error': f'Já existe um cliente com o NIF "{nif}".'}, status=400)
            
            # Atualizar cliente
            cliente.nome = nome
            cliente.nif = nif
            cliente.endereco = data.get('endereco', '')
            cliente.telefone = data.get('telefone', '')
            cliente.email = data.get('email', '')
            cliente.ativo = data.get('ativo', True)
            cliente.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '✅ Cliente atualizado com sucesso!',
                'cliente': {
                    'id': cliente.id,
                    'nome': cliente.nome,
                    'nif': cliente.nif,
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dados inválidos.'}, status=400)
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


class ClienteAPIDeleteView(LoginRequiredMixin, View):
    """API para excluir cliente via AJAX"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def delete(self, request, pk):
        try:
            cliente = get_object_or_404(Cliente, id=pk)
            nome = cliente.nome
            cliente.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'✅ Cliente "{nome}" excluído com sucesso!'
            })
            
        except Exception as e:
            logger.error(f"Erro ao excluir cliente: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


class ClienteAPIDetailView(LoginRequiredMixin, View):
    """API para obter detalhes de um cliente"""
    
    def get(self, request, pk):
        try:
            cliente = get_object_or_404(Cliente, id=pk)
            
            data = {
                'id': cliente.id,
                'nome': cliente.nome,
                'nif': cliente.nif,
                'endereco': cliente.endereco,
                'telefone': cliente.telefone,
                'email': cliente.email,
                'ativo': cliente.ativo,
                'data_criacao': cliente.data_criacao.strftime('%d/%m/%Y %H:%M') if cliente.data_criacao else '-',
                'data_atualizacao': cliente.data_atualizacao.strftime('%d/%m/%Y %H:%M') if cliente.data_atualizacao else '-',
            }
            
            return JsonResponse({'status': 'success', 'cliente': data})
            
        except Exception as e:
            logger.error(f"Erro ao buscar cliente: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)