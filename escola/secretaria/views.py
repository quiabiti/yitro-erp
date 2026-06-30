# escola/secretaria/views.py - VERSÃO COMPLETA

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.template.loader import get_template
from django.utils import timezone
from datetime import date, datetime
import json
import logging

from .models import Aluno, Matricula, HistoricoAluno
from escola.pedagogico.models import Classe, Turma, AnoLectivo
from escola.configuracao.models import Instituicao

logger = logging.getLogger(__name__)


# ============================================
# 🔥 FUNÇÃO PARA BUSCAR O TENANT (ESCOLA)
# ============================================

def get_tenant_escola(request):
    """Retorna a escola (tenant) da requisição"""
    tenant = getattr(request, 'tenant', None)
    
    if not tenant and hasattr(request, 'session'):
        tenant_id = request.session.get('tenant_id')
        if tenant_id:
            try:
                tenant = Instituicao.objects.get(id=tenant_id, ativo=True)
                request.tenant = tenant
                logger.info(f"✅ Tenant encontrado na sessão: {tenant.nome} (ID: {tenant.id})")
            except Instituicao.DoesNotExist:
                logger.warning(f"❌ Tenant não encontrado para ID: {tenant_id}")
            except Exception as e:
                logger.error(f"❌ Erro ao buscar tenant: {e}")
    
    if not tenant:
        tenant_slug = request.GET.get('tenant')
        if tenant_slug:
            try:
                tenant = Instituicao.objects.get(slug=tenant_slug, ativo=True)
                request.tenant = tenant
                logger.info(f"✅ Tenant encontrado pelo slug: {tenant.nome} (ID: {tenant.id})")
            except Instituicao.DoesNotExist:
                logger.warning(f"❌ Tenant não encontrado para slug: {tenant_slug}")
            except Exception as e:
                logger.error(f"❌ Erro ao buscar tenant: {e}")
    
    return tenant


def get_tenant_id(request):
    """Retorna o ID do tenant"""
    tenant = get_tenant_escola(request)
    return tenant.id if tenant else None


# ============================================
# 🔥 VIEWS PRINCIPAIS (PÁGINAS)
# ============================================

@login_required
def secretaria_matriculas(request):
    """Matrícula e Confirmação - Secretaria Geral"""
    tenant_id = get_tenant_id(request)
    
    # Buscar classes para o filtro
    if tenant_id:
        classes = Classe.objects.filter(tenant_id=tenant_id, ativo=True).order_by('nome')
    else:
        classes = Classe.objects.filter(ativo=True).order_by('nome')
    
    # 🔥 BUSCAR MATRÍCULAS PARA EXIBIR INICIALMENTE
    if tenant_id:
        matriculas = Matricula.objects.filter(
            tenant_id=tenant_id, 
            ativo=True
        ).select_related(
            'aluno', 'classe', 'turma', 'ano_lectivo'
        ).order_by('-data_matricula')[:50]
        
        total_alunos = Aluno.objects.filter(tenant_id=tenant_id, ativo=True).count()
        pendentes = Matricula.objects.filter(tenant_id=tenant_id, status='pendente', ativo=True).count()
        confirmadas = Matricula.objects.filter(tenant_id=tenant_id, status='confirmada', ativo=True).count()
        concluidas = Matricula.objects.filter(tenant_id=tenant_id, status='concluida', ativo=True).count()
        trancadas = Matricula.objects.filter(tenant_id=tenant_id, status='trancada', ativo=True).count()
        canceladas = Matricula.objects.filter(tenant_id=tenant_id, status='cancelada', ativo=True).count()
    else:
        matriculas = Matricula.objects.filter(ativo=True).select_related(
            'aluno', 'classe', 'turma', 'ano_lectivo'
        ).order_by('-data_matricula')[:50]
        
        total_alunos = Aluno.objects.filter(ativo=True).count()
        pendentes = Matricula.objects.filter(status='pendente', ativo=True).count()
        confirmadas = Matricula.objects.filter(status='confirmada', ativo=True).count()
        concluidas = Matricula.objects.filter(status='concluida', ativo=True).count()
        trancadas = Matricula.objects.filter(status='trancada', ativo=True).count()
        canceladas = Matricula.objects.filter(status='cancelada', ativo=True).count()
    
    context = {
        'titulo': 'Matrícula e Confirmação',
        'icone': 'bi-file-earmark-text',
        'modulo': 'Secretaria Geral',
        'classes': classes,
        # DADOS PARA OS CARDS
        'total_alunos': total_alunos,
        'total_pendentes': pendentes,
        'total_confirmadas': confirmadas,
        'total_concluidas': concluidas,
        'total_trancadas': trancadas,
        'total_canceladas': canceladas,
        # DADOS PARA A LISTA
        'matriculas': matriculas,
        'total_matriculas': len(matriculas),
    }
    return render(request, 'escola/partials/secretaria/matriculas.html', context)

@login_required
def secretaria_pagamentos(request):
    """Pagamentos - Secretaria Geral"""
    context = {
        'titulo': 'Pagamentos',
        'icone': 'bi-wallet2',
        'modulo': 'Secretaria Geral',
    }
    return render(request, 'escola/partials/secretaria/pagamentos.html', context)


@login_required
def secretaria_alunos(request):
    """Lista de Alunos por Turma - Secretaria Geral"""
    tenant_id = get_tenant_id(request)
    import json
    
    # 🔥 Buscar escola (tenant)
    escola = None
    if tenant_id:
        escola = Instituicao.objects.filter(id=tenant_id, ativo=True).first()
    
    # 🔥 Buscar turmas com contagem de alunos
    if tenant_id:
        turmas = Turma.objects.filter(tenant_id=tenant_id, ativo=True).select_related('classe', 'ano_lectivo').order_by('classe__nome', 'nome')
        total_alunos = Aluno.objects.filter(tenant_id=tenant_id, ativo=True).count()
        alunos = Aluno.objects.filter(tenant_id=tenant_id, ativo=True).prefetch_related('matriculas')
    else:
        turmas = Turma.objects.filter(ativo=True).select_related('classe', 'ano_lectivo').order_by('classe__nome', 'nome')
        total_alunos = Aluno.objects.filter(ativo=True).count()
        alunos = Aluno.objects.filter(ativo=True).prefetch_related('matriculas')
    
    # 🔥 Preparar dados das turmas com lista de alunos (COMPLETO)
    turmas_data = []
    for turma in turmas:
        alunos_turma = []
        for aluno in alunos:
            # Verificar se o aluno tem matrícula nesta turma
            matricula = aluno.matriculas.filter(turma=turma).first()
            
            if matricula:
                alunos_turma.append({
                    'id': aluno.id,
                    'nome_completo': aluno.nome_completo,
                    'bi': aluno.bi,
                    'genero': aluno.genero,
                    'idade': aluno.get_idade(),
                    'classe': turma.classe.nome if turma.classe else None,
                    'turma': turma.nome,
                    'sala': turma.sala if hasattr(turma, 'sala') and turma.sala else None,
                    'ano_lectivo': str(turma.ano_lectivo) if turma.ano_lectivo else None,
                    'status_matricula': matricula.status if matricula else None,
                    'status_matricula_display': matricula.get_status_display() if matricula else 'Sem Matrícula',
                })
        
        turmas_data.append({
            'id': turma.id,
            'nome': turma.nome,
            'classe_nome': turma.classe.nome if turma.classe else None,
            'sala': turma.sala if hasattr(turma, 'sala') and turma.sala else None,
            'ano_lectivo': str(turma.ano_lectivo) if turma.ano_lectivo else None,
            'total_alunos': len(alunos_turma),
            'alunos': alunos_turma,
        })
    
    # 🔥 Preparar dados da escola
    escola_data = {
        'nome': escola.nome if escola else 'Yitro - Gestão Escolar',
        'logo_url': escola.logo.url if escola and escola.logo else None,
        'endereco': escola.endereco if escola and hasattr(escola, 'endereco') else '',
        'telefone': escola.telefone if escola and hasattr(escola, 'telefone') else '',
        'email': escola.email if escola and hasattr(escola, 'email') else '',
        'provincia': escola.provincia if escola and hasattr(escola, 'provincia') else '',
        'municipio': escola.municipio if escola and hasattr(escola, 'municipio') else '',
    }
    
    # 🔥 CONVERTER PARA JSON - USANDO default=str PARA DATAS
    turmas_json = json.dumps(turmas_data, ensure_ascii=False, default=str)
    escola_json = json.dumps(escola_data, ensure_ascii=False, default=str)
    
    # 🔥 LOG PARA DEBUG
    print(f"📦 Turmas encontradas: {len(turmas_data)}")
    print(f"📦 Total de alunos: {total_alunos}")
    if turmas_data:
        print(f"📦 Primeira turma: {turmas_data[0]['nome']} - {turmas_data[0]['total_alunos']} alunos")
    
    context = {
        'titulo': 'Lista de Alunos por Turma',
        'icone': 'bi-people',
        'modulo': 'Secretaria Geral',
        'turmas': turmas_data,
        'total_alunos': total_alunos,
        'escola': escola_data,
        'turmas_json': turmas_json,
        'escola_json': escola_json,
    }
    
    return render(request, 'escola/partials/secretaria/alunos.html', context)  


@login_required
def secretaria_documentos(request):
    """Solicitação de Documentos - Secretaria Geral"""
    context = {
        'titulo': 'Solicitação de Documentos',
        'icone': 'bi-file-earmark',
        'modulo': 'Secretaria Geral',
    }
    return render(request, 'escola/partials/secretaria/documentos.html', context)


# ============================================
# 🔥 VIEW PARA FORMULÁRIO DE MATRÍCULA
# ============================================

@login_required
def api_matricula_form(request, matricula_id=None):
    """Retorna APENAS o formulário de matrícula"""
    tenant_id = get_tenant_id(request)
    
    aluno = None
    matricula = None
    edit = False
    proxima_classe_sugerida = None
    
    if matricula_id:
        matricula = get_object_or_404(Matricula, id=matricula_id, tenant_id=tenant_id)
        aluno = matricula.aluno
        edit = True
        
        if matricula.classe:
            proxima_classe = Classe.objects.filter(
                tenant_id=tenant_id,
                nivel_ensino=matricula.classe.nivel_ensino,
                ativo=True
            ).exclude(id=matricula.classe.id).order_by('nome').first()
            if proxima_classe:
                proxima_classe_sugerida = proxima_classe
    
    context = {
        'aluno': aluno,
        'matricula': matricula,
        'edit': edit,
        'tenant_id': tenant_id,
        'ano_lectivos': AnoLectivo.objects.filter(tenant_id=tenant_id, ativo=True).order_by('-ano'),
        'classes': Classe.objects.filter(tenant_id=tenant_id, ativo=True).select_related('nivel_ensino').order_by('nivel_ensino__ordem', 'nome'),
        'turmas': Turma.objects.filter(tenant_id=tenant_id, ativo=True).select_related('classe').order_by('classe__nome', 'nome'),
        'proxima_classe_sugerida': proxima_classe_sugerida,
    }
    
    return render(request, 'escola/partials/secretaria/matricula_form.html', context)


# ============================================
# 🔥 IMPRESSÃO - FICHA DE MATRÍCULA
# ============================================

@login_required
def impressao_matricula(request, matricula_id):
    """Gera a Ficha de Matrícula para impressão"""
    tenant_id = get_tenant_id(request)
    matricula = get_object_or_404(Matricula, id=matricula_id, tenant_id=tenant_id)
    
    # Buscar dados
    aluno = matricula.aluno
    ano_lectivo = matricula.ano_lectivo
    classe = matricula.classe
    turma = matricula.turma
    
    # Buscar escola
    escola = Instituicao.objects.filter(id=tenant_id).first()
    
    context = {
        'matricula': matricula,
        'aluno': aluno,
        'ano_lectivo': ano_lectivo,
        'classe': classe,
        'turma': turma,
        'escola': escola,
        'data_emissao': datetime.now().strftime('%d/%m/%Y'),
        'escola_nome': escola.nome if escola else 'Yitro - Gestão Escolar',
        'escola_logo': escola.logo.url if escola and escola.logo else None,
    }
    
    return render(request, 'escola/impressao/matricula.html', context)


# ============================================
# 🔥 API - ALUNOS
# ============================================

@login_required
def api_alunos_listar(request):
    """Lista todos os alunos - filtrando pela escola"""
    try:
        tenant_id = get_tenant_id(request)
        
        busca = request.GET.get('busca', '')
        classe_id = request.GET.get('classe', '')
        turma_id = request.GET.get('turma', '')
        status = request.GET.get('status', '')
        
        if tenant_id:
            alunos = Aluno.objects.filter(tenant_id=tenant_id)
        else:
            alunos = Aluno.objects.all()
        
        if busca:
            alunos = alunos.filter(
                Q(nome_completo__icontains=busca) |
                Q(bi__icontains=busca) |
                Q(telefone__icontains=busca)
            )
        
        # 🔥 CORREÇÃO: Buscar por turma considerando TODAS as matrículas
        if turma_id:
            alunos = alunos.filter(
                Q(matriculas__turma_id=turma_id)  # 🔥 REMOVER O filtro ativo=True
            ).distinct()
        
        if classe_id:
            alunos = alunos.filter(
                Q(matriculas__classe_id=classe_id)  # 🔥 REMOVER O filtro ativo=True
            ).distinct()
        
        if status:
            alunos = alunos.filter(matriculas__status=status).distinct()
        
        alunos = alunos.order_by('nome_completo').select_related('usuario')
        data = [aluno.to_dict() for aluno in alunos]
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"❌ Erro em api_alunos_listar: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def api_alunos_buscar(request):
    """Busca aluno por BI, Nome ou ID (para matrícula)"""
    try:
        tenant_id = get_tenant_id(request)
        termo = request.GET.get('termo', '')
        
        if not termo:
            return JsonResponse({'success': True, 'data': []})
        
        if tenant_id:
            alunos = Aluno.objects.filter(tenant_id=tenant_id)
        else:
            alunos = Aluno.objects.all()
        
        # 🔥 TENTAR BUSCAR POR ID PRIMEIRO (se for número)
        if termo.isdigit():
            # Busca por ID exato
            alunos = alunos.filter(id=int(termo))
            print(f"🔍 Buscando por ID: {termo}, encontrados: {alunos.count()}")
        else:
            # Busca por BI exato ou nome contém
            alunos = alunos.filter(
                Q(bi__iexact=termo) |
                Q(nome_completo__icontains=termo)
            )
            print(f"🔍 Buscando por texto: {termo}, encontrados: {alunos.count()}")
        
        alunos = alunos.order_by('nome_completo')[:10].select_related('usuario')
        
        data = []
        for aluno in alunos:
            aluno_data = aluno.to_dict()
            matricula = aluno.get_matricula_atual()
            if matricula:
                aluno_data['matricula_atual'] = matricula.to_dict()
            data.append(aluno_data)
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"❌ Erro em api_alunos_buscar: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def api_alunos_stats(request):
    """Retorna estatísticas de alunos"""
    try:
        tenant_id = get_tenant_id(request)
        
        if tenant_id:
            total = Aluno.objects.filter(tenant_id=tenant_id, ativo=True).count()
            por_classe = Matricula.objects.filter(
                tenant_id=tenant_id, ativo=True, status__in=['pendente', 'confirmada']
            ).values('classe__nome').annotate(total=Count('id'))
            por_turma = Matricula.objects.filter(
                tenant_id=tenant_id, ativo=True, status__in=['pendente', 'confirmada']
            ).values('turma__nome').annotate(total=Count('id'))
            por_status = Matricula.objects.filter(
                tenant_id=tenant_id, ativo=True
            ).values('status').annotate(total=Count('id'))
        else:
            total = Aluno.objects.filter(ativo=True).count()
            por_classe = Matricula.objects.filter(ativo=True, status__in=['pendente', 'confirmada']).values('classe__nome').annotate(total=Count('id'))
            por_turma = Matricula.objects.filter(ativo=True, status__in=['pendente', 'confirmada']).values('turma__nome').annotate(total=Count('id'))
            por_status = Matricula.objects.filter(ativo=True).values('status').annotate(total=Count('id'))
        
        return JsonResponse({
            'success': True,
            'data': {
                'total': total,
                'por_classe': list(por_classe),
                'por_turma': list(por_turma),
                'por_status': list(por_status),
            }
        })
    except Exception as e:
        logger.error(f"❌ Erro em api_alunos_stats: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# 🔥 API - TURMAS
# ============================================

@login_required
def api_turmas_listar(request):
    """Lista todas as turmas com contagem de alunos"""
    try:
        tenant_id = get_tenant_id(request)
        
        if tenant_id:
            turmas = Turma.objects.filter(tenant_id=tenant_id, ativo=True)
        else:
            turmas = Turma.objects.filter(ativo=True)
        
        # Ordenar por classe e nome da turma
        turmas = turmas.select_related('classe', 'ano_lectivo').order_by('classe__nome', 'nome')
        
        data = []
        for turma in turmas:
            # Contar alunos ativos na turma
            total_alunos = Matricula.objects.filter(
                turma=turma,
                ativo=True,
                status__in=['pendente', 'confirmada']
            ).count()
            
            data.append({
                'id': turma.id,
                'nome': turma.nome,
                'classe_nome': turma.classe.nome if turma.classe else None,
                'classe_id': turma.classe.id if turma.classe else None,
                'ano_lectivo': str(turma.ano_lectivo) if turma.ano_lectivo else None,
                'ano_lectivo_id': turma.ano_lectivo.id if turma.ano_lectivo else None,
                'total_alunos': total_alunos,
                'capacidade': turma.capacidade if hasattr(turma, 'capacidade') else None,
                'ativo': turma.ativo,
            })
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"❌ Erro em api_turmas_listar: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})




# ============================================
# 🔥 API - MATRÍCULAS
# ============================================

@login_required
def api_matriculas_listar(request):
    """Lista todas as matrículas - filtrando pela escola"""
    try:
        tenant_id = get_tenant_id(request)
        
        status = request.GET.get('status', '')
        classe_id = request.GET.get('classe', '')
        turma_id = request.GET.get('turma', '')
        ano_lectivo_id = request.GET.get('ano_lectivo', '')
        busca = request.GET.get('busca', '')
        
        if tenant_id:
            matriculas = Matricula.objects.filter(tenant_id=tenant_id)
        else:
            matriculas = Matricula.objects.all()
        
        if status:
            matriculas = matriculas.filter(status=status)
        if classe_id:
            matriculas = matriculas.filter(classe_id=classe_id)
        if turma_id:
            matriculas = matriculas.filter(turma_id=turma_id)
        if ano_lectivo_id:
            matriculas = matriculas.filter(ano_lectivo_id=ano_lectivo_id)
        if busca:
            matriculas = matriculas.filter(
                Q(aluno__nome_completo__icontains=busca) |
                Q(aluno__bi__icontains=busca)
            )
        
        matriculas = matriculas.select_related(
            'aluno', 'classe', 'turma', 'ano_lectivo', 'matricula_anterior'
        ).order_by('-data_matricula')
        
        data = [matricula.to_dict() for matricula in matriculas]
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"❌ Erro em api_matriculas_listar: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# 🔥 API - SALVAR MATRÍCULA
# ============================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_matricula_salvar(request, matricula_id=None):
    """Salva matrícula (cria aluno + matrícula ou apenas matrícula)"""
    try:
        tenant_id = get_tenant_id(request)
        
        # 🔥 LOG PARA DEBUG
        print(f"🔍 Salvando matrícula - Tenant ID: {tenant_id}")
        print(f"🔍 Dados recebidos: {request.POST}")
        
        # Dados do Aluno
        aluno_id = request.POST.get('aluno_id')
        bi = request.POST.get('bi', '').strip()
        nome_completo = request.POST.get('nome_completo', '').strip()
        genero = request.POST.get('genero', 'M')
        naturalidade = request.POST.get('naturalidade', '')
        nacionalidade = request.POST.get('nacionalidade', 'Angola')
        nif = request.POST.get('nif', '')
        telefone = request.POST.get('telefone', '')
        email = request.POST.get('email', '')
        endereco = request.POST.get('endereco', '')
        nome_pai = request.POST.get('nome_pai', '')
        nome_mae = request.POST.get('nome_mae', '')
        telefone_responsavel = request.POST.get('telefone_responsavel', '')
        email_responsavel = request.POST.get('email_responsavel', '')
        
        # CONVERTER DATA DE NASCIMENTO
        data_nascimento_raw = request.POST.get('data_nascimento')
        data_nascimento = None
        if data_nascimento_raw:
            try:
                data_nascimento = datetime.strptime(data_nascimento_raw, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'errors': {'data_nascimento': 'Data de nascimento inválida. Use o formato YYYY-MM-DD.'}
                })
        
        # Dados da Matrícula
        tipo = request.POST.get('tipo', 'nova')
        ano_lectivo_id = request.POST.get('ano_lectivo')
        classe_id = request.POST.get('classe')
        turma_id = request.POST.get('turma')
        observacoes = request.POST.get('observacoes', '')
        status = request.POST.get('status', 'pendente')
        
        # Validar campos obrigatórios
        if not bi:
            return JsonResponse({'success': False, 'errors': {'bi': 'BI é obrigatório'}})
        if not nome_completo:
            return JsonResponse({'success': False, 'errors': {'nome_completo': 'Nome é obrigatório'}})
        if not data_nascimento:
            return JsonResponse({'success': False, 'errors': {'data_nascimento': 'Data de nascimento é obrigatória'}})
        if not ano_lectivo_id:
            return JsonResponse({'success': False, 'errors': {'ano_lectivo': 'Ano lectivo é obrigatório'}})
        if not classe_id:
            return JsonResponse({'success': False, 'errors': {'classe': 'Classe é obrigatória'}})
        
        # ============================================
        # 🔥 BUSCAR OU CRIAR ALUNO - CORRIGIDO
        # ============================================
        aluno = None
        
        # 1. Se tem aluno_id, busca por ID
        if aluno_id and aluno_id != '':
            try:
                aluno = Aluno.objects.get(id=aluno_id, tenant_id=tenant_id)
                print(f"✅ Aluno encontrado por ID: {aluno.nome_completo} (ID: {aluno.id})")
            except Aluno.DoesNotExist:
                print(f"⚠️ Aluno não encontrado por ID: {aluno_id}")
                aluno = None
        
        # 2. Se não encontrou por ID, tenta por BI
        if not aluno and bi:
            aluno = Aluno.objects.filter(bi=bi, tenant_id=tenant_id).first()
            if aluno:
                print(f"✅ Aluno encontrado por BI: {aluno.nome_completo} (ID: {aluno.id})")
            else:
                print(f"⚠️ Nenhum aluno encontrado com BI: {bi}")
        
        # 3. Se encontrou aluno, ATUALIZA os dados
        if aluno:
            print(f"📝 Atualizando dados do aluno: {aluno.nome_completo}")
            aluno.nome_completo = nome_completo
            aluno.bi = bi
            aluno.data_nascimento = data_nascimento
            aluno.genero = genero
            aluno.naturalidade = naturalidade
            aluno.nacionalidade = nacionalidade
            aluno.nif = nif
            aluno.telefone = telefone
            aluno.email = email
            aluno.endereco = endereco
            aluno.nome_pai = nome_pai
            aluno.nome_mae = nome_mae
            aluno.telefone_responsavel = telefone_responsavel
            aluno.email_responsavel = email_responsavel
            aluno.save()
            print(f"✅ Aluno atualizado: {aluno.nome_completo}")
        else:
            # 4. Cria novo aluno
            print(f"📝 Criando novo aluno: {nome_completo}")
            aluno = Aluno.objects.create(
                tenant_id=tenant_id,
                nome_completo=nome_completo,
                bi=bi,
                data_nascimento=data_nascimento,
                genero=genero,
                naturalidade=naturalidade,
                nacionalidade=nacionalidade,
                nif=nif,
                telefone=telefone,
                email=email,
                endereco=endereco,
                nome_pai=nome_pai,
                nome_mae=nome_mae,
                telefone_responsavel=telefone_responsavel,
                email_responsavel=email_responsavel,
                ativo=True
            )
            print(f"✅ Novo aluno criado: {aluno.nome_completo} (ID: {aluno.id})")
        
        # Buscar ano lectivo, classe e turma
        ano_lectivo = get_object_or_404(AnoLectivo, id=ano_lectivo_id, tenant_id=tenant_id)
        classe = get_object_or_404(Classe, id=classe_id, tenant_id=tenant_id)
        turma = None
        if turma_id:
            turma = get_object_or_404(Turma, id=turma_id, tenant_id=tenant_id)
        
        # ============================================
        # 🔥 VERIFICAR MATRÍCULA EXISTENTE - CORRIGIDO
        # ============================================
        # Só verifica se NÃO é edição
        if not matricula_id:
            # 🔥 BUSCA APENAS MATRÍCULAS ATIVAS E NÃO CANCELADAS
            matricula_existente = Matricula.objects.filter(
                aluno=aluno,
                ano_lectivo=ano_lectivo,
                tenant_id=tenant_id,
                ativo=True
            ).exclude(
                status__in=['cancelada', 'concluida']  # 🔥 EXCLUI CANCELADAS E CONCLUÍDAS
            ).first()
            
            if matricula_existente:
                print(f"⚠️ Matrícula existente encontrada: ID {matricula_existente.id} - Status: {matricula_existente.status}")
                return JsonResponse({
                    'success': False,
                    'errors': {'ano_lectivo': f'{aluno.nome_completo} já possui uma matrícula ATIVA em {ano_lectivo.ano}'}
                })
            else:
                print(f"✅ Nenhuma matrícula ativa encontrada para {aluno.nome_completo} em {ano_lectivo.ano}")
        
        # ============================================
        # 🔥 EDITAR OU CRIAR MATRÍCULA
        # ============================================
        if matricula_id:
            print(f"📝 Editando matrícula ID: {matricula_id}")
            matricula = get_object_or_404(Matricula, id=matricula_id, tenant_id=tenant_id)
            matricula.aluno = aluno
            matricula.ano_lectivo = ano_lectivo
            matricula.classe = classe
            matricula.turma = turma
            matricula.tipo = tipo
            matricula.status = status
            matricula.observacoes = observacoes
            matricula.save()
            
            historico = HistoricoAluno.objects.filter(matricula=matricula).first()
            if historico:
                historico.ano_lectivo = ano_lectivo
                historico.classe = classe
                historico.turma = turma
                historico.status = status
                historico.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Matrícula de {aluno.nome_completo} atualizada com sucesso!',
                'id': matricula.id,
                'data': {'aluno': aluno.to_dict(), 'matricula': matricula.to_dict()}
            })
        
        # ============================================
        # 🔥 CRIAR NOVA MATRÍCULA
        # ============================================
        print(f"📝 Criando nova matrícula para {aluno.nome_completo}")
        
        matricula = Matricula.objects.create(
            tenant_id=tenant_id,
            aluno=aluno,
            ano_lectivo=ano_lectivo,
            classe=classe,
            turma=turma,
            tipo=tipo,
            status=status,
            observacoes=observacoes,
            ativo=True
        )
        
        print(f"✅ Matrícula criada: ID {matricula.id}")
        
        # Criar histórico
        HistoricoAluno.objects.create(
            tenant_id=tenant_id,
            aluno=aluno,
            matricula=matricula,
            ano_lectivo=ano_lectivo,
            classe=classe,
            turma=turma,
            status=status,
            aprovado=False,
            observacoes=f"Matrícula {tipo} criada em {date.today().strftime('%d/%m/%Y')}"
        )
        
        print(f"✅ Histórico criado para matrícula {matricula.id}")
        
        return JsonResponse({
            'success': True,
            'message': f'Matrícula de {aluno.nome_completo} criada com sucesso!',
            'id': matricula.id,
            'data': {'aluno': aluno.to_dict(), 'matricula': matricula.to_dict()}
        })
    except Exception as e:
        logger.error(f"❌ Erro em api_matricula_salvar: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)})

# ============================================
# 🔥 API - CONFIRMAR MATRÍCULA
# ============================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_matricula_confirmar(request, matricula_id):
    """Confirma uma matrícula"""
    try:
        tenant_id = get_tenant_id(request)
        matricula = get_object_or_404(Matricula, id=matricula_id, tenant_id=tenant_id)
        
        matricula.confirmar()
        
        historico = HistoricoAluno.objects.filter(matricula=matricula).first()
        if historico:
            historico.status = 'confirmada'
            historico.save()
        
        logger.info(f"✅ Matrícula confirmada: {matricula.aluno.nome_completo} (ID: {matricula.id})")
        
        return JsonResponse({
            'success': True,
            'message': f'Matrícula de {matricula.aluno.nome_completo} confirmada com sucesso!',
            'data': matricula.to_dict()
        })
    except Exception as e:
        logger.error(f"❌ Erro em api_matricula_confirmar: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# 🔥 API - CANCELAR MATRÍCULA
# ============================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_matricula_cancelar(request, matricula_id):
    """Cancela uma matrícula"""
    try:
        tenant_id = get_tenant_id(request)
        matricula = get_object_or_404(Matricula, id=matricula_id, tenant_id=tenant_id)
        
        # Verificar se já está cancelada
        if matricula.status == 'cancelada':
            return JsonResponse({
                'success': False,
                'error': 'Esta matrícula já está cancelada.'
            })
        
        matricula.cancelar()
        
        historico = HistoricoAluno.objects.filter(matricula=matricula).first()
        if historico:
            historico.status = 'cancelada'
            historico.save()
        
        logger.info(f"✅ Matrícula cancelada: {matricula.aluno.nome_completo} (ID: {matricula.id})")
        
        return JsonResponse({
            'success': True,
            'message': f'Matrícula de {matricula.aluno.nome_completo} cancelada com sucesso!',
            'data': matricula.to_dict()
        })
    except Exception as e:
        logger.error(f"❌ Erro em api_matricula_cancelar: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# 🔥 API - TRANSCAR MATRÍCULA
# ============================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_matricula_trancar(request, matricula_id):
    """Tranca uma matrícula"""
    try:
        tenant_id = get_tenant_id(request)
        matricula = get_object_or_404(Matricula, id=matricula_id, tenant_id=tenant_id)
        
        # Verificar se já está trancada
        if matricula.status == 'trancada':
            return JsonResponse({
                'success': False,
                'error': 'Esta matrícula já está trancada.'
            })
        
        matricula.trancar()
        
        historico = HistoricoAluno.objects.filter(matricula=matricula).first()
        if historico:
            historico.status = 'trancada'
            historico.save()
        
        logger.info(f"✅ Matrícula trancada: {matricula.aluno.nome_completo} (ID: {matricula.id})")
        
        return JsonResponse({
            'success': True,
            'message': f'Matrícula de {matricula.aluno.nome_completo} trancada com sucesso!',
            'data': matricula.to_dict()
        })
    except Exception as e:
        logger.error(f"❌ Erro em api_matricula_trancar: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# 🔥 API - DELETAR MATRÍCULA
# ============================================

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def api_matricula_deletar(request, matricula_id):
    """Deleta uma matrícula"""
    try:
        tenant_id = get_tenant_id(request)
        matricula = get_object_or_404(Matricula, id=matricula_id, tenant_id=tenant_id)
        
        HistoricoAluno.objects.filter(matricula=matricula).delete()
        nome_aluno = matricula.aluno.nome_completo
        matricula.delete()
        
        logger.info(f"✅ Matrícula deletada: {matricula_id} - {nome_aluno}")
        
        return JsonResponse({
            'success': True,
            'message': f'Matrícula de {nome_aluno} deletada com sucesso!'
        })
    except Exception as e:
        logger.error(f"❌ Erro em api_matricula_deletar: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# 🔥 API - HISTÓRICO
# ============================================

@login_required
def api_historico_aluno(request, aluno_id):
    """Retorna o histórico escolar de um aluno"""
    try:
        tenant_id = get_tenant_id(request)
        aluno = get_object_or_404(Aluno, id=aluno_id, tenant_id=tenant_id)
        
        historico = HistoricoAluno.objects.filter(
            aluno=aluno, tenant_id=tenant_id
        ).select_related('ano_lectivo', 'classe', 'turma').order_by('-ano_lectivo')
        
        data = [h.to_dict() for h in historico]
        
        return JsonResponse({
            'success': True,
            'data': {
                'aluno': aluno.to_dict(),
                'historico': data
            }
        })
    except Exception as e:
        logger.error(f"❌ Erro em api_historico_aluno: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# 🔥 API - STATS MATRÍCULAS
# ============================================

@login_required
def api_matriculas_stats(request):
    """Retorna estatísticas de matrículas para os cards"""
    try:
        tenant_id = get_tenant_id(request)
        
        if tenant_id:
            total = Aluno.objects.filter(tenant_id=tenant_id, ativo=True).count()
            por_status = Matricula.objects.filter(
                tenant_id=tenant_id, ativo=True
            ).values('status').annotate(total=Count('id'))
        else:
            total = Aluno.objects.filter(ativo=True).count()
            por_status = Matricula.objects.filter(ativo=True).values('status').annotate(total=Count('id'))
        
        return JsonResponse({
            'success': True,
            'data': {
                'total': total,
                'por_status': list(por_status),
            }
        })
    except Exception as e:
        logger.error(f"❌ Erro em api_matriculas_stats: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})