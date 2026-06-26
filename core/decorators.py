from django.shortcuts import render, redirect
from django.contrib import messages
from functools import wraps
from django.http import HttpResponseForbidden

def departamento_required(departamento_slug, nivel_minimo='VIEW', redirect_url='home'):
    """
    Decorator para restringir acesso a um departamento específico.
    
    Args:
        departamento_slug: Slug do departamento
        nivel_minimo: Nível mínimo de acesso (VIEW, EDIT, MANAGE, ADMIN)
        redirect_url: URL para redirecionar em caso de negação
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Faça login para acessar esta área.')
                return redirect('login')
            
            # Superusuário tem acesso a tudo
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar acesso ao departamento
            if not request.user.tem_acesso_departamento(departamento_slug):
                messages.error(request, f'Você não tem acesso ao departamento {departamento_slug}.')
                return redirect(redirect_url)
            
            # Verificar nível mínimo (se necessário)
            if nivel_minimo != 'VIEW':
                nivel_atual = request.user.get_nivel_acesso_departamento(departamento_slug)
                niveis = ['VIEW', 'EDIT', 'MANAGE', 'ADMIN']
                if niveis.index(nivel_atual) < niveis.index(nivel_minimo):
                    messages.error(request, 'Você não tem permissão suficiente.')
                    return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# ============================================
# DECORATORS PARA DEPARTAMENTOS
# ============================================

def escola_required(nivel_minimo='VIEW'):
    """Decorator específico para o departamento escola"""
    return departamento_required('escola', nivel_minimo)

def financeiro_required(nivel_minimo='VIEW'):
    """Decorator específico para o departamento financeiro"""
    return departamento_required('financeiro', nivel_minimo)

def comercial_required(nivel_minimo='VIEW'):
    """Decorator específico para o departamento comercial"""
    return departamento_required('comercial', nivel_minimo)

def servicos_required(nivel_minimo='VIEW'):
    """Decorator específico para o departamento de serviços"""
    return departamento_required('servicos', nivel_minimo)

def administrativo_required(nivel_minimo='VIEW'):
    """Decorator específico para o departamento administrativo"""
    return departamento_required('administrativo', nivel_minimo)

# ============================================
# DECORATORS PARA YITRO (ADMINISTRAÇÃO)
# ============================================

def yitro_admin_required(view_func):
    """
    Decorator para acesso administrativo da Yitro.
    Apenas Super Admin ou usuários com acesso ao departamento Administrativo.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Faça login para acessar esta área.')
            return redirect('login')
        
        # Superusuário tem acesso
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verificar se tem acesso ao departamento administrativo
        if request.user.tem_acesso_departamento('administrativo'):
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso restrito a administradores da Yitro.')
        return redirect('servicos:central')
    return wrapper

def yitro_view_required(view_func):
    """
    Decorator para visualização de dados da Yitro.
    Qualquer funcionário Yitro pode visualizar, mas não editar.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Faça login para acessar esta área.')
            return redirect('login')
        
        # Superusuário tem acesso
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verificar se o usuário tem algum departamento Yitro
        departamentos_yitro = ['administrativo', 'financeiro', 'comercial', 'servicos']
        for dep in departamentos_yitro:
            if request.user.tem_acesso_departamento(dep):
                return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Você não tem permissão para visualizar esta área.')
        return redirect('servicos:central')
    return wrapper

# ============================================
# DECORATOR PARA SUPER ADMIN
# ============================================

def super_admin_required(view_func):
    """
    Decorator para acesso apenas de Super Admin.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Faça login para acessar esta área.')
            return redirect('login')
        
        if not request.user.is_superuser:
            messages.error(request, 'Acesso restrito a Super Administradores.')
            return redirect('servicos:central')
        
        return view_func(request, *args, **kwargs)
    return wrapper

# ============================================
# DECORATORS ADICIONAIS
# ============================================

def admin_required(view_func):
    """
    Decorator específico para acesso administrativo (apenas superusuários)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Faça login para acessar esta área.')
            return redirect('login')
        
        if not request.user.is_superuser:
            messages.error(request, 'Acesso restrito a administradores.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper