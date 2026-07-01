from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve
from django.shortcuts import redirect


# 🔥 VIEW PARA A PÁGINA INICIAL (INDEX)
def index_view(request):
    """Página inicial - redireciona para o dashboard apropriado"""
    if request.user.is_authenticated:
        # Verifica se o usuário tem uma escola associada
        try:
            from escola.configuracao.models import UsuarioInstituicao
            usuario_escola = UsuarioInstituicao.objects.filter(usuario=request.user, ativo=True).first()
            if usuario_escola:
                return redirect('escola:index')
        except:
            pass
        
        # Verifica se é admin
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/admin/')
        
        # Fallback
        return redirect('/escola/')
    
    # Usuário não autenticado - redireciona para login
    return redirect('/auth/login/')


urlpatterns = [
    # 🔥 PÁGINA INICIAL
    path('', index_view, name='index'),  # <-- ESSA É A URL 'index'!
    
    path('admin/', admin.site.urls),
    path('auth/', include('autenticacao.urls')),
    
    # 🔥 REDIRECIONAMENTOS PARA COMPATIBILIDADE
    # Redireciona /usuarios/ para /auth/
    path('usuarios/', RedirectView.as_view(url='/auth/', permanent=False)),
    path('usuarios/login/', RedirectView.as_view(url='/auth/login/', permanent=False)),
    path('usuarios/logout/', RedirectView.as_view(url='/auth/logout/', permanent=False)),
    path('usuarios/registro/', RedirectView.as_view(url='/auth/registro/', permanent=False)),
    path('usuarios/perfil/', RedirectView.as_view(url='/auth/perfil/', permanent=False)),
    
    # 🔥 APLICATIVOS
    path('servicos/', include('servicos.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('clientes/', include('clientes.urls')),
    path('escola/', include('escola.urls')),
]

# 🔥 SERVE ARQUIVOS DE MÍDIA
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # 🔥 Para produção (Render.com)
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': False
        }),
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': False
        }),
    ]