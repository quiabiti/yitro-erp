# core/urls.py - VERSÃO COMPLETA

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve
from . import views  # Importar views do core

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('autenticacao.urls')),
    path('', RedirectView.as_view(url='/servicos/'), name='home'),
    path('servicos/', include('servicos.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('clientes/', include('clientes.urls')),
    path('escola/', include('escola.urls')),
    
    # 🔥 URLs do core (se existirem)
    path('core/', views.core_dashboard, name='core_dashboard'),
    path('itens/', views.lista_itens, name='lista_itens'),
    path('item/<int:item_id>/', views.detalhe_item, name='detalhe_item'),
    path('api/item/<int:item_id>/', views.api_item_data, name='api_item_data'),
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
    ]
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': False
        }),
    ]