# autenticacao/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import Usuario
import logging

logger = logging.getLogger(__name__)

# Obter o modelo de usuário customizado
User = get_user_model()


@csrf_protect
def login_view(request):
    """Página de login personalizada"""
    
    # Se usuário já estiver logado, redirecionar para o dashboard
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me', False)
        
        # Validações básicas
        if not username or not password:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return render(request, 'autenticacao/login.html', {
                'username': username
            })
        
        try:
            # Autenticar usuário
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Login bem-sucedido
                login(request, user)
                
                # Configurar sessão
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 semanas
                else:
                    request.session.set_expiry(0)  # Sessão de navegador
                
                # Registrar login
                logger.info(f"Usuário {user.username} fez login com sucesso.")
                
                # Redirecionar para a página de destino
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                # Login falhou
                messages.error(request, 'Usuário ou senha incorretos.')
                logger.warning(f"Tentativa de login falhou para usuário: {username}")
                
                return render(request, 'autenticacao/login.html', {
                    'username': username
                })
                
        except Exception as e:
            logger.error(f"Erro durante login: {str(e)}")
            messages.error(request, 'Ocorreu um erro ao tentar fazer login. Tente novamente.')
            return render(request, 'autenticacao/login.html', {
                'username': username
            })
    
    # GET request
    return render(request, 'autenticacao/login.html')


@login_required
def logout_view(request):
    """Logout do usuário"""
    username = request.user.username
    logout(request)
    messages.success(request, f'Usuário {username} desconectado com sucesso!')
    logger.info(f"Usuário {username} fez logout.")
    return redirect('login')


@csrf_protect
def register_view(request):
    """Registro de novos usuários"""
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        # Validações
        errors = []
        
        if not username:
            errors.append('O nome de usuário é obrigatório.')
        elif len(username) < 3:
            errors.append('O nome de usuário deve ter pelo menos 3 caracteres.')
        elif not username.isalnum():
            errors.append('O nome de usuário deve conter apenas letras e números.')
        elif User.objects.filter(username=username).exists():
            errors.append('Este nome de usuário já está em uso.')
        
        if not email:
            errors.append('O email é obrigatório.')
        elif User.objects.filter(email=email).exists():
            errors.append('Este email já está cadastrado.')
        
        if not password:
            errors.append('A senha é obrigatória.')
        elif len(password) < 8:
            errors.append('A senha deve ter pelo menos 8 caracteres.')
        elif not any(c.isupper() for c in password):
            errors.append('A senha deve conter pelo menos uma letra maiúscula.')
        elif not any(c.islower() for c in password):
            errors.append('A senha deve conter pelo menos uma letra minúscula.')
        elif not any(c.isdigit() for c in password):
            errors.append('A senha deve conter pelo menos um número.')
        
        if password != password_confirm:
            errors.append('As senhas não coincidem.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'autenticacao/register.html', {
                'username': username,
                'email': email
            })
        
        try:
            # Criar usuário usando o modelo customizado
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Se você tiver campos adicionais no modelo Usuario, configure-os aqui
            # Exemplo:
            # user.is_active = True
            # user.save()
            
            messages.success(request, f'Usuário {username} criado com sucesso!')
            logger.info(f"Novo usuário registrado: {username}")
            
            # Autenticar e logar automaticamente
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                return redirect('login')
                
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            messages.error(request, 'Erro ao criar usuário. Tente novamente.')
            return render(request, 'autenticacao/register.html', {
                'username': username,
                'email': email
            })
    
    return render(request, 'autenticacao/register.html')