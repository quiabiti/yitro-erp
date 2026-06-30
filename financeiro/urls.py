from django.urls import path, include
from . import views
from clientes.views import ClienteListView  # 🔥 IMPORTAR DO APP CLIENTES

app_name = 'financeiro'

urlpatterns = [
    # Faturas
    path('faturas/', views.FaturaListView.as_view(), name='faturas_lista'),
    path('faturas/nova/', views.FaturaCreateView.as_view(), name='faturas_criar'),
    path('faturas/<int:pk>/editar/', views.FaturaUpdateView.as_view(), name='faturas_editar'),
    path('faturas/<int:pk>/excluir/', views.FaturaDeleteView.as_view(), name='faturas_excluir'),
    path('faturas/<int:pk>/detalhes/', views.FaturaDetailView.as_view(), name='faturas_detalhes'),
    path('lista/', views.FaturaListView.as_view(), name='lista_faturas'),
    
    # 🔥 CLIENTES - Redirecionar para o app clientes
    path('clientes/', include('clientes.urls')),
    
    # 🔥 URL para compatibilidade (usa a view importada)
    path('clientes/lista/', ClienteListView.as_view(), name='clientes_lista'),
    
    # ============================================================
    # 🔥 UPLOAD DE IMAGEM - ADICIONAR ESTA LINHA
    # ============================================================
    path('api/produto/<int:produto_id>/upload-imagem/', views.upload_produto_imagem, name='upload_produto_imagem'),
    
    # APIs
    path('api/faturas/', views.FaturaAPIListCreateView.as_view(), name='faturas_api_list'),
    path('api/faturas/<int:pk>/editar/', views.FaturaAPIUpdateView.as_view(), name='faturas_api_editar'),
    path('api/faturas/<int:pk>/excluir/', views.FaturaAPIDeleteView.as_view(), name='faturas_api_excluir'),
    path('api/faturas/<int:pk>/', views.FaturaDetailView.as_view(), name='faturas_api_detail'),
]