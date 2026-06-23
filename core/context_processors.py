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