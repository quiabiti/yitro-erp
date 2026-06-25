import os
import sys
import django

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models import Departamento

DEPARTAMENTOS = [
    {
        'nome': 'Comercial',
        'slug': 'comercial',
        'descricao': 'Gestão de vendas, produtos e clientes. Vitrine de produtos tecnológicos.',
        'icone': 'fa-store',
        'ordem': 1
    },
    {
        'nome': 'Financeiro',
        'slug': 'financeiro',
        'descricao': 'Gestão financeira, faturação, contabilidade e conformidade AGT.',
        'icone': 'fa-coins',
        'ordem': 2
    },
    {
        'nome': 'Escola',
        'slug': 'escola',
        'descricao': 'Gestão pedagógica completa: alunos, professores, turmas e secretaria.',
        'icone': 'fa-school',
        'ordem': 3
    },
    {
        'nome': 'Serviços',
        'slug': 'servicos',
        'descricao': 'Suporte técnico, manutenção e consultoria.',
        'icone': 'fa-tools',
        'ordem': 4
    },
    {
        'nome': 'Administrativo',
        'slug': 'administrativo',
        'descricao': 'Gestão administrativa geral, recursos humanos e documentos.',
        'icone': 'fa-building',
        'ordem': 5
    },
]

def init_departamentos():
    print("="*50)
    print("🚀 Inicializando Departamentos da Yitro")
    print("="*50)
    
    for dep_data in DEPARTAMENTOS:
        dep, created = Departamento.objects.get_or_create(
            slug=dep_data['slug'],
            defaults=dep_data
        )
        if created:
            print(f"✅ Criado: {dep.nome}")
        else:
            print(f"ℹ️ Já existe: {dep.nome}")
    
    print("="*50)
    print(f"✅ Total: {Departamento.objects.count()} departamentos")
    print("="*50)

if __name__ == '__main__':
    init_departamentos()
