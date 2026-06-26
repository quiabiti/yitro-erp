from django.urls import path
from . import views

app_name = 'servicos'

urlpatterns = [
    # 🏢 CENTRAL YITRO (Requer login - Dashboard principal)
    path('', views.central_yitro, name='central'),  # 🔥 ROTA PRINCIPAL
    
    # 📊 DASHBOARD ADMINISTRATIVO (Requer login)
    path('dashboard/', views.dashboard_servicos, name='dashboard'),
    
    # Itens (unificado)
    path('itens/', views.lista_itens, name='lista_itens'),
    path('itens/criar/', views.criar_item, name='criar_item'),
    path('itens/<int:item_id>/', views.detalhe_item, name='detalhe_item'),
    path('itens/editar/<int:item_id>/', views.editar_item, name='editar_item'),
    
    # Compatibilidade (redireciona para itens)
    path('servicos/', views.lista_servicos, name='lista_servicos'),
    path('servicos/criar/', views.criar_item, name='criar_servico'),
    path('servicos/<int:servico_id>/', views.detalhe_servico, name='detalhe_servico'),
    path('servicos/editar/<int:servico_id>/', views.editar_item, name='editar_servico'),
    
    # Contratos
    path('contratos/', views.lista_contratos, name='lista_contratos'),
    path('contratos/criar/', views.criar_contrato, name='criar_contrato'),
    path('contratos/<int:contrato_id>/', views.detalhe_contrato, name='detalhe_contrato'),
    
    # Ordens de Serviço
    path('ordens/', views.lista_ordens, name='lista_ordens'),
    path('ordens/dashboard/', views.dashboard_ordens, name='dashboard_ordens'),
    path('ordens/criar/', views.criar_ordem, name='criar_ordem'),
    path('ordens/<int:ordem_id>/', views.detalhe_ordem, name='detalhe_ordem'),
    path('ordens/<int:ordem_id>/lancar-horas/', views.lancar_horas, name='lancar_horas'),
    
    # Faturamento
    path('faturamento/', views.lista_faturamentos, name='lista_faturamentos'),
    
    # 🛒 CARRINHO
    path('carrinho/', views.carrinho, name='carrinho'),
    path('carrinho/adicionar/', views.carrinho_adicionar, name='carrinho_adicionar'),
    path('carrinho/remover/', views.carrinho_remover, name='carrinho_remover'),
    path('carrinho/limpar/', views.carrinho_limpar, name='carrinho_limpar'),
    
    # ✅ CHECKOUT
    path('checkout/', views.checkout, name='checkout'),
    
    # ✅ GERAR PDF DO PEDIDO
    path('api/gerar-pdf-pedido/', views.gerar_pdf_pedido, name='gerar_pdf_pedido'),
    
    # APIs
    path('api/item/<int:item_id>/', views.api_item_data, name='api_item_data'),
    path('api/item/criar/', views.api_criar_item, name='api_criar_item'),
    path('api/item/<int:item_id>/editar/', views.api_editar_item, name='api_editar_item'),
    path('api/item/<int:item_id>/excluir/', views.api_excluir_item, name='api_excluir_item'),
    path('api/movimento-stock/', views.api_movimento_stock, name='api_movimento_stock'),
    
    # APIs compatibilidade
    path('api/<int:servico_id>/', views.api_servico_data, name='api_servico_data'),
    path('api/contrato/<int:contrato_id>/', views.api_contrato_data, name='api_contrato_data'),
    path('api/ordem/<int:ordem_id>/', views.api_ordem_data, name='api_ordem_data'),
    path('api/lancar-horas/', views.api_lancar_horas, name='api_lancar_horas'),
    
    # 🔥 PAINEL ADMIN PERSONALIZADO
    path('painel-admin/', views.painel_admin, name='painel_admin'),
    
    # 🔥 RELATÓRIOS
    path('relatorios/', views.relatorios, name='relatorios'),
    
    # 🔥 CONFIGURAÇÕES
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    
    # 🔥 SALVAR CONFIGURAÇÕES (API)
    path('configuracoes/salvar/', views.salvar_configuracoes, name='salvar_configuracoes'),
    
    # 🔥 CARREGAR CONFIGURAÇÕES (API)
    path('api/configuracoes/', views.api_configuracoes, name='api_configuracoes'),
]