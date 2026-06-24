# core/middleware.py
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.db import OperationalError
import pytz
from servicos.models import ConfiguracaoSistema

class ConfiguracaoMiddleware:
    """Middleware para aplicar configurações do sistema em tempo real"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 🔥 Tenta buscar configurações, mas não quebra se a tabela não existir
        config = None
        try:
            config = ConfiguracaoSistema.objects.first()
        except OperationalError:
            # Tabela ainda não existe - ignorar
            pass
        except Exception:
            pass
        
        if config:
            # 1. Modo de Manutenção
            if config.modo_manutencao and not request.user.is_superuser:
                return render(request, 'servicos/manutencao.html', {
                    'site_name': config.nome_sistema
                }, status=503)
            
            # 2. Fuso Horário
            if config.fuso_horario:
                try:
                    timezone.activate(pytz.timezone(config.fuso_horario))
                except:
                    pass
        
        response = self.get_response(request)
        
        # 3. Adicionar cabeçalhos de segurança
        if config:
            response['X-Sistema'] = config.nome_sistema
        
        return response


class ContadorTentativasLoginMiddleware:
    """Middleware para contar tentativas de login"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar se é uma tentativa de login
        if request.path == '/auth/login/' and request.method == 'POST':
            # 🔥 Tenta buscar configurações, mas não quebra se a tabela não existir
            max_tentativas = 5
            try:
                config = ConfiguracaoSistema.objects.first()
                if config:
                    max_tentativas = config.tentativas_login
            except OperationalError:
                pass
            except Exception:
                pass
            
            # Contar tentativas na sessão
            if not request.session.get('login_attempts'):
                request.session['login_attempts'] = 0
            
            # Verificar se excedeu
            if request.session['login_attempts'] >= max_tentativas:
                return render(request, 'servicos/bloqueado.html', {
                    'tempo_bloqueio': 15,
                    'max_tentativas': max_tentativas
                }, status=403)
        
        return self.get_response(request)