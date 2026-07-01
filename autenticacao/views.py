from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.conf import settings


def get_departamento_redirect(user):
    """
    Retorna a URL de redirecionamento baseada no departamento do usuário
    """
    # Superusuário vai para a Central Yitro
    if user.is_superuser:
        return 'servicos:central'
    
    # 🔥 PRIORIDADE MÁXIMA: Verificar se o usuário tem acesso a uma ESCOLA
    try:
        from escola.configuracao.models import UsuarioInstituicao
        
        usuario_escola = UsuarioInstituicao.objects.filter(usuario=user, ativo=True).first()
        
        if usuario_escola:
            # 🔥 CORRETO: Usar 'escola:index' que é o nome da view que carrega o SPA
            return 'escola:index'
    except ImportError:
        pass  # Módulo escola não está disponível
    
    # Verificar se o usuário tem departamento principal (funcionário Yitro)
    if hasattr(user, 'departamento_principal') and user.departamento_principal:
        departamento_slug = user.departamento_principal.slug
        
        # Se for do departamento Escola
        if departamento_slug == 'escola':
            return 'escola:index'
        
        # Se for do departamento Financeiro
        if departamento_slug == 'financeiro':
            return 'financeiro:lista_faturas'
        
        # Se for do departamento Comercial
        if departamento_slug == 'comercial':
            return 'servicos:central'
    
    # Verificar permissões de departamento
    if hasattr(user, 'tem_acesso_departamento') and user.tem_acesso_departamento('escola'):
        return 'escola:index'
    
    # Verificar se o usuário tem acesso ao admin
    if user.is_staff:
        return '/admin/'
    
    # Por padrão, ir para a Central Yitro ou escola
    # 🔥 FALLBACK SEGURO: Usar uma URL que com certeza existe
    try:
        # Tenta redirecionar para escola
        return 'escola:index'
    except:
        # Se não existir, vai para a raiz
        return '/'


@csrf_protect
def login_view(request):
    """View de login com redirecionamento inteligente"""
    if request.user.is_authenticated:
        return redirect(get_departamento_redirect(request.user))
    
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
            
            # 🔥 Redirecionamento inteligente baseado no departamento
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and next_url != 'home':
                return redirect(next_url)
            
            # Redirecionar baseado no departamento
            try:
                redirect_url = get_departamento_redirect(user)
                return redirect(redirect_url)
            except Exception as e:
                # 🔥 FALLBACK: Se houver erro no redirecionamento, vai para a raiz
                print(f"⚠️ Erro no redirecionamento: {e}")
                return redirect('/')
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