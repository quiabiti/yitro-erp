from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse

@csrf_protect
def login_view(request):
    """View de login personalizada"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Configurar sessão
            if not remember_me:
                request.session.set_expiry(0)  # Expira ao fechar o browser
            
            messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
            
            # Redirecionar
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return render(request, 'autenticacao/login.html', {
                'username': username
            })
    
    return render(request, 'autenticacao/login.html')

def logout_view(request):
    """View de logout"""
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('autenticacao:login')

@login_required
def perfil(request):
    """Perfil do usuário"""
    return render(request, 'autenticacao/perfil.html')

def csrf_failure(request, reason=""):
    """View personalizada para erro CSRF"""
    return render(request, 'autenticacao/csrf_error.html', {
        'reason': reason,
        'message': 'O token de segurança não foi válido. Por favor, recarregue a página.'
    }, status=403)