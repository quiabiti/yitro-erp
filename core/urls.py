# core/urls.py - VERSÃO CORRIGIDA COM CLIENTES

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from servicos.views import dashboard_servicos

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home / Dashboard (Página inicial - pública)
    path('', dashboard_servicos, name='home'),
    
    # Autenticação (login, logout, registrar) - Em /auth/
    path('auth/', include('autenticacao.urls')),
    # Isso vai criar: /auth/login/, /auth/logout/, /auth/registrar/
    
    # Apps do sistema
    path('financeiro/', include('financeiro.urls')),
    path('servicos/', include('servicos.urls')),
    path('clientes/', include('clientes.urls')),  # 🔥 ADICIONADO - APP CLIENTES
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)