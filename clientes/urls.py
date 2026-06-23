# clientes/urls.py

from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Lista de clientes
    path('', views.ClienteListView.as_view(), name='lista'),
    
    # Criar cliente
    path('criar/', views.ClienteCreateView.as_view(), name='criar'),
    
    # Editar cliente
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='editar'),
    
    # Excluir cliente
    path('<int:pk>/excluir/', views.ClienteDeleteView.as_view(), name='excluir'),
    
    # Detalhes do cliente
    path('<int:pk>/detalhes/', views.ClienteDetailView.as_view(), name='detalhes'),
    
    # API para AJAX
    path('api/', views.ClienteAPIListCreateView.as_view(), name='api_list'),
    path('api/<int:pk>/', views.ClienteAPIDetailView.as_view(), name='api_detail'),
    path('api/<int:pk>/editar/', views.ClienteAPIUpdateView.as_view(), name='api_editar'),
    path('api/<int:pk>/excluir/', views.ClienteAPIDeleteView.as_view(), name='api_excluir'),
]