from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve  # ← ADICIONAR ESTA IMPORTAÇÃO

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('autenticacao.urls')),
    path('', RedirectView.as_view(url='/servicos/'), name='home'),
    path('servicos/', include('servicos.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('clientes/', include('clientes.urls')),
    path('escola/', include('escola.urls')),
]

# 🔥 SERVE ARQUIVOS DE MÍDIA EM PRODUÇÃO (igual ao outro sistema)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # 🔥 Para produção (Render.com), servimos manualmente
    # Isso é necessário porque com DEBUG=False o Django não serve arquivos de mídia
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': False
        }),
    ]
    
    # 🔥 Para arquivos estáticos em produção (já servidos pelo WhiteNoise)
    # Mas garantimos também
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': False
        }),
    ]