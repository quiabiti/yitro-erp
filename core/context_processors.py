# core/context_processors.py
from servicos.models import ConfiguracaoSistema
from decimal import Decimal

def configuracao_sistema(request):
    """Context processor para disponibilizar configurações em todos os templates"""
    try:
        config = ConfiguracaoSistema.objects.first()
        if not config:
            config = ConfiguracaoSistema.objects.create()
        
        return {
            'config_sistema': config,
            'site_name': config.nome_sistema if config else 'Yitro ERP',
            'moeda_padrao': config.moeda_padrao if config else 'Kz',
            'idioma_padrao': config.idioma_padrao if config else 'pt-pt',
        }
    except:
        return {
            'config_sistema': None,
            'site_name': 'Yitro ERP',
            'moeda_padrao': 'Kz',
            'idioma_padrao': 'pt-pt',
        }

def configuracao_moeda(request):
    """Context processor para formatação de moeda"""
    try:
        config = ConfiguracaoSistema.objects.first()
        moeda = config.moeda_padrao if config else 'Kz'
        
        def formatar_moeda(valor):
            """Formata um valor com a moeda do sistema"""
            if valor is None:
                return f'{moeda} 0,00'
            try:
                valor = float(valor)
                return f'{moeda} {valor:,.2f}'.replace(',', ' ').replace('.', ',')
            except:
                return f'{moeda} 0,00'
        
        return {
            'moeda_padrao': moeda,
            'formatar_moeda': formatar_moeda,
        }
    except:
        return {
            'moeda_padrao': 'Kz',
            'formatar_moeda': lambda v: f'Kz {float(v or 0):,.2f}'.replace(',', ' ').replace('.', ',') if v else 'Kz 0,00',
        }

def departamentos_context(request):
    """
    Context processor para disponibilizar informações de departamentos
    """
    context = {
        'departamentos_usuario': [],
        'departamento_ativo': None,
        'is_superadmin': False,
    }
    
    if request.user.is_authenticated:
        if request.user.is_superuser:
            context['is_superadmin'] = True
            # Para superusuário, mostrar todos os departamentos
            from core.models import Departamento
            context['departamentos_usuario'] = Departamento.objects.filter(ativo=True)
        else:
            context['departamentos_usuario'] = request.user.get_departamentos()
            context['departamento_ativo'] = request.session.get('departamento_ativo')
    
    return context

def tenant_context(request):
    """
    Context processor para disponibilizar informações da instituição/ESCOLA
    """
    context = {
        'tenant': None,
        'tenant_id': None,
        'tenant_nome': None,
        'tenant_nome_fantasia': None,
        'tenant_logo': None,
        'tenant_logo_url': None,
        'tenant_cor_primaria': '#6C63FF',
        'tenant_cor_secundaria': '#FF6584',
        'tenant_plano': 'BASIC',
        'tenant_slug': None,
        'is_multi_tenant': False,
    }
    
    if hasattr(request, 'tenant') and request.tenant:
        tenant = request.tenant
        context['tenant'] = tenant
        context['tenant_id'] = tenant.id
        context['tenant_nome'] = tenant.nome
        context['tenant_nome_fantasia'] = tenant.nome_fantasia or tenant.nome
        context['tenant_slug'] = tenant.slug
        context['tenant_plano'] = tenant.plano
        context['tenant_cor_primaria'] = tenant.cor_primaria
        context['tenant_cor_secundaria'] = tenant.cor_secundaria
        context['is_multi_tenant'] = True
        
        if tenant.logo:
            context['tenant_logo'] = tenant.logo
            context['tenant_logo_url'] = tenant.logo.url
    
    return context

def combined_config(request):
    """
    Context processor COMBINADO com todas as configurações
    """
    context = {}
    
    # Configurações do Sistema
    try:
        config = ConfiguracaoSistema.objects.first()
        if config:
            context['sistema_nome'] = config.nome_sistema
            context['sistema_moeda'] = config.moeda_padrao
            context['sistema_idioma'] = config.idioma_padrao
    except:
        context['sistema_nome'] = 'Yitro ERP'
        context['sistema_moeda'] = 'Kz'
        context['sistema_idioma'] = 'pt-pt'
    
    # Configurações do Tenant (Escola)
    if hasattr(request, 'tenant') and request.tenant:
        tenant = request.tenant
        context['escola_nome'] = tenant.nome_fantasia or tenant.nome
        context['escola_logo'] = tenant.logo.url if tenant.logo else None
        context['escola_cor_primaria'] = tenant.cor_primaria
        context['escola_cor_secundaria'] = tenant.cor_secundaria
        context['escola_plano'] = tenant.plano
        
        # Prioridade: escola > sistema
        context['cor_primaria'] = tenant.cor_primaria
        context['cor_secundaria'] = tenant.cor_secundaria
        context['nome_sistema'] = f"{tenant.nome_fantasia or tenant.nome}"
    else:
        context['cor_primaria'] = '#6C63FF'
        context['cor_secundaria'] = '#FF6584'
    
    # Função para formatar moeda
    def formatar_moeda(valor):
        moeda = context.get('sistema_moeda', 'Kz')
        if valor is None:
            return f'{moeda} 0,00'
        try:
            valor = float(valor)
            return f'{moeda} {valor:,.2f}'.replace(',', ' ').replace('.', ',')
        except:
            return f'{moeda} 0,00'
    
    context['formatar_moeda'] = formatar_moeda
    
    return context