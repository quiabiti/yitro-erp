from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.db import OperationalError
import pytz
from servicos.models import ConfiguracaoSistema
from escola.configuracao.models import Instituicao, UsuarioInstituicao

class ConfiguracaoMiddleware:
    """Middleware para aplicar configurações do sistema em tempo real"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config = None
        try:
            config = ConfiguracaoSistema.objects.first()
        except OperationalError:
            pass
        except Exception:
            pass
        
        if config:
            if config.modo_manutencao and not request.user.is_superuser:
                return render(request, 'servicos/manutencao.html', {
                    'site_name': config.nome_sistema
                }, status=503)
            
            if config.fuso_horario:
                try:
                    timezone.activate(pytz.timezone(config.fuso_horario))
                except:
                    pass
        
        response = self.get_response(request)
        
        # 🔥 VERIFICAR SE O RESPONSE PERMITE ATRIBUIÇÃO
        if config and hasattr(response, '__setitem__'):
            try:
                response['X-Sistema'] = config.nome_sistema
            except (TypeError, AttributeError):
                # Se não puder atribuir, ignora
                pass
        
        return response


class MultiTenancyMiddleware:
    """Middleware para identificar a instituição/ESCOLA"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pular para URLs públicas
        if self._is_public_path(request.path):
            request.tenant = None
            return self.get_response(request)
        
        # Identificar tenant
        tenant_slug = request.GET.get('tenant')
        if tenant_slug:
            try:
                tenant = Instituicao.objects.get(slug=tenant_slug, ativo=True)
                request.tenant = tenant
            except Instituicao.DoesNotExist:
                request.tenant = None
        else:
            request.tenant = None
        
        response = self.get_response(request)
        return response
    
    def _is_public_path(self, path):
        """Verifica se o caminho é público"""
        public_paths = [
            '/admin/',
            '/auth/',
            '/login/',
            '/logout/',
            '/media/',
            '/static/',
            '/escola/',
            '/financeiro/',
            '/servicos/',
            '/clientes/',
        ]
        
        for public_path in public_paths:
            if path.startswith(public_path):
                return True
        return False


class ContadorTentativasLoginMiddleware:
    """Middleware para contar tentativas de login"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/auth/login/' and request.method == 'POST':
            max_tentativas = 5
            try:
                config = ConfiguracaoSistema.objects.first()
                if config:
                    max_tentativas = config.tentativas_login
            except OperationalError:
                pass
            except Exception:
                pass
            
            if not request.session.get('login_attempts'):
                request.session['login_attempts'] = 0
            
            if request.session['login_attempts'] >= max_tentativas:
                return render(request, 'servicos/bloqueado.html', {
                    'tempo_bloqueio': 15,
                    'max_tentativas': max_tentativas
                }, status=403)
        
        return self.get_response(request)
