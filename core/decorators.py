# core/decorators.py
from servicos.models import ConfiguracaoSistema

def limitar_tentativas_login(max_tentativas=5):
    """Decorator para limitar tentativas de login"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            config = ConfiguracaoSistema.objects.first()
            limite = config.tentativas_login if config else 5
            # Lógica para contar tentativas
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator