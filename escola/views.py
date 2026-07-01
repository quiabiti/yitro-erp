# escola/views.py - VERSÃO CORRIGIDA COMPLETA

import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from core.decorators import (
    yitro_admin_required, 
    super_admin_required, 
    escola_required, 
    yitro_view_required,
    admin_required
)
from .configuracao.models import Instituicao, UsuarioInstituicao
from django.contrib.auth import get_user_model

# 🔥 IMPORTAR MODELOS PEDAGÓGICOS
from .pedagogico.models import Classe, Disciplina, Turma, AnoLectivo

# 🔥 TENTAR IMPORTAR MODELOS DE SECRETARIA (se existirem)
try:
    from .secretaria.models import Aluno, Professor, Matricula
except ImportError:
    Aluno = None
    Professor = None
    Matricula = None
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Modelos de secretaria não encontrados")

logger = logging.getLogger(__name__)
User = get_user_model()


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


# ============================================
# 🔥 FUNÇÃO PARA GARANTIR TENANT EM DADOS
# ============================================

def get_tenant_id_para_salvar(request, item=None):
    """Retorna o tenant_id para salvar no registro."""
    if item and hasattr(item, 'tenant_id') and item.tenant_id:
        return item.tenant_id
    
    tenant = get_tenant_escola(request)
    if tenant:
        return tenant.id
    
    return None


# ============================================
# VIEW PRINCIPAL - SPA (CORRIGIDA COM JSON)
# ============================================

@login_required
def index(request):
    """Página inicial da Escola - Carrega o SPA com dados JSON"""
    user = request.user
    
    tenant_slug = request.GET.get('tenant')
    
    is_super_admin = user.is_superuser
    is_admin_escola = user.is_superuser
    
    tenant_nome = None
    tenant_nome_fantasia = None
    carregar_dashboard = False
    esta_na_escola = False
    turmas = []
    escola = None
    
    if tenant_slug:
        try:
            escola = Instituicao.objects.get(slug=tenant_slug)
            tenant_nome = escola.nome
            tenant_nome_fantasia = escola.nome_fantasia
            carregar_dashboard = True
            esta_na_escola = True
            request.session['tenant_id'] = escola.id
            
            # 🔥 Buscar turmas da escola
            try:
                turmas = Turma.objects.filter(
                    tenant_id=escola.id,
                    ativo=True
                ).order_by('nome')
                logger.info(f"✅ {turmas.count()} turmas encontradas para {escola.nome}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao buscar turmas: {e}")
                turmas = []
                
        except Instituicao.DoesNotExist:
            logger.warning(f"❌ Escola não encontrada: {tenant_slug}")
            pass
    
    # 🔥 Converter turmas para JSON
    turmas_list = []
    for t in turmas:
        turmas_list.append({
            'id': t.id,
            'nome': t.nome,
            'ano': getattr(t, 'ano', None),
            'descricao': getattr(t, 'descricao', ''),
        })
    turmas_json = json.dumps(turmas_list, cls=DjangoJSONEncoder)
    
    # 🔥 Converter escola para JSON
    escola_dict = {}
    if escola:
        escola_dict = {
            'id': escola.id,
            'nome': escola.nome,
            'slug': escola.slug,
            'nome_fantasia': escola.nome_fantasia,
            'cor_primaria': getattr(escola, 'cor_primaria', '#00d4ff'),
            'cor_secundaria': getattr(escola, 'cor_secundaria', '#7b2ffc'),
            'logo': getattr(escola, 'logo', None) and escola.logo.url if hasattr(escola, 'logo') else None,
        }
    escola_json = json.dumps(escola_dict, cls=DjangoJSONEncoder)
    
    context = {
        'is_super_admin': is_super_admin,
        'is_admin_escola': is_admin_escola,
        'is_admin': is_super_admin,
        'show_escolas': is_super_admin,
        'tenant_slug': tenant_slug,
        'tenant_nome': tenant_nome,
        'tenant_nome_fantasia': tenant_nome_fantasia,
        'carregar_dashboard': carregar_dashboard,
        'esta_na_escola': esta_na_escola,
        'turmas': turmas,
        'turmas_json': turmas_json,  # 🔥 Dados das turmas em JSON
        'escola_json': escola_json,  # 🔥 Dados da escola em JSON
        'escola': escola,
    }
    
    return render(request, 'base_escola.html', context)


# ============================================
# ENTRAR NA ESCOLA PELO SLUG
# ============================================

@login_required
def entrar_escola(request, slug):
    """Redireciona para o ambiente da escola"""
    escola = get_object_or_404(Instituicao, slug=slug)
    
    user = request.user
    if not user.is_superuser:
        if not UsuarioInstituicao.objects.filter(usuario=user, instituicao=escola).exists():
            messages.error(request, 'Você não tem acesso a esta escola.')
            return redirect('escola:lista_escolas')
    
    request.session['tenant_id'] = escola.id
    return redirect(f'/escola/ambiente/?tenant={escola.slug}')


# ============================================
# VIEWS PARA GESTÃO DE ESCOLAS (YITRO)
# ============================================

@login_required
@yitro_admin_required
def api_escolas_listar(request):
    """Lista de escolas - apenas Yitro admins"""
    todas_escolas = Instituicao.objects.all().order_by('nome')
    escolas_ativas = Instituicao.objects.filter(ativo=True)
    escolas_inativas = Instituicao.objects.filter(ativo=False)
    
    context = {
        'escolas': escolas_ativas,
        'total': todas_escolas.count(),
        'escolas_ativas': escolas_ativas.count(),
        'escolas_inativas': escolas_inativas.count(),
        'total_usuarios': User.objects.count(),
        'view_only': request.GET.get('view_only', False),
    }
    return render(request, 'escola/partials/escolas_lista.html', context)


@login_required
@yitro_admin_required
def api_escola_nova(request):
    """Formulário para nova escola - HTML parcial"""
    return render(request, 'escola/partials/escola_form.html', {'escola': None, 'edit': False})


@login_required
@yitro_admin_required
def api_escola_editar(request, escola_id):
    """Formulário para editar escola - HTML parcial"""
    escola = get_object_or_404(Instituicao, id=escola_id)
    return render(request, 'escola/partials/escola_form.html', {'escola': escola, 'edit': True})


@login_required
@super_admin_required
@csrf_exempt
@require_http_methods(["POST"])
def api_escola_salvar(request):
    """Salvar escola via AJAX - apenas Super Admin"""
    try:
        nome = request.POST.get('nome')
        nome_fantasia = request.POST.get('nome_fantasia', '')
        cnpj = request.POST.get('cnpj')
        slug = request.POST.get('slug', '')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        whatsapp = request.POST.get('whatsapp', '')
        
        endereco = request.POST.get('endereco')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cep = request.POST.get('cep')
        
        cor_primaria = request.POST.get('cor_primaria', '#00d4ff')
        cor_secundaria = request.POST.get('cor_secundaria', '#7b2ffc')
        logo = request.FILES.get('logo')
        
        regime_tributario = request.POST.get('regime_tributario', 'SN')
        aliquota_iss = request.POST.get('aliquota_iss', 2.0)
        
        plano = request.POST.get('plano', 'BASIC')
        ativo = request.POST.get('ativo', 'on') == 'on'
        
        escola_id = request.POST.get('escola_id')
        
        errors = {}
        if not nome:
            errors['nome'] = 'Nome é obrigatório'
        if not cnpj:
            errors['cnpj'] = 'NIF é obrigatório'
        if not email:
            errors['email'] = 'E-mail é obrigatório'
        if not telefone:
            errors['telefone'] = 'Telefone é obrigatório'
        if not endereco:
            errors['endereco'] = 'Endereço é obrigatório'
        if not cidade:
            errors['cidade'] = 'Cidade é obrigatória'
        if not estado:
            errors['estado'] = 'Província é obrigatória'
        
        if not slug:
            slug = nome.lower().replace(' ', '-').replace('ç', 'c').replace('ã', 'a').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')[:50]
        
        if escola_id:
            if Instituicao.objects.filter(cnpj=cnpj).exclude(id=escola_id).exists():
                errors['cnpj'] = 'Já existe uma escola com este NIF'
        else:
            if Instituicao.objects.filter(cnpj=cnpj).exists():
                errors['cnpj'] = 'Já existe uma escola com este NIF'
        
        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        
        if escola_id:
            escola = get_object_or_404(Instituicao, id=escola_id)
            escola.nome = nome
            escola.nome_fantasia = nome_fantasia
            escola.cnpj = cnpj
            escola.slug = slug
            escola.email = email
            escola.telefone = telefone
            escola.whatsapp = whatsapp
            escola.endereco = endereco
            escola.cidade = cidade
            escola.estado = estado
            escola.cep = cep
            escola.cor_primaria = cor_primaria
            escola.cor_secundaria = cor_secundaria
            escola.regime_tributario = regime_tributario
            escola.aliquota_iss = aliquota_iss
            escola.plano = plano
            escola.ativo = ativo
            if logo:
                escola.logo = logo
            escola.save()
            mensagem = f'Escola {escola.nome} atualizada com sucesso!'
        else:
            escola = Instituicao.objects.create(
                nome=nome,
                nome_fantasia=nome_fantasia,
                cnpj=cnpj,
                slug=slug,
                email=email,
                telefone=telefone,
                whatsapp=whatsapp,
                endereco=endereco,
                cidade=cidade,
                estado=estado,
                cep=cep,
                cor_primaria=cor_primaria,
                cor_secundaria=cor_secundaria,
                regime_tributario=regime_tributario,
                aliquota_iss=aliquota_iss,
                plano=plano,
                ativo=ativo,
                logo=logo
            )
            mensagem = f'Escola {escola.nome} criada com sucesso!'
        
        return JsonResponse({
            'success': True,
            'message': mensagem,
            'escola_id': escola.id,
            'escola_slug': escola.slug,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        })


@login_required
@super_admin_required
@csrf_exempt
@require_http_methods(["DELETE"])
def api_escola_deletar(request, escola_id):
    """Deletar escola via AJAX - apenas Super Admin"""
    try:
        escola = get_object_or_404(Instituicao, id=escola_id)
        nome = escola.nome
        escola.delete()
        return JsonResponse({
            'success': True,
            'message': f'Escola {nome} deletada com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        })


# ============================================
# 🔥 DASHBOARD
# ============================================

@login_required
def api_dashboard(request):
    """Dashboard - Exibe dados da escola atual"""
    user = request.user
    is_admin = user.is_superuser
    
    # 🔥 Buscar o tenant (escola)
    tenant = get_tenant_escola(request)
    tenant_id = tenant.id if tenant else None
    
    # 🔥 LOG PARA DIAGNÓSTICO
    logger.info("=" * 50)
    logger.info("📊 DASHBOARD - DIAGNÓSTICO")
    logger.info(f"👤 Usuário: {user.username}")
    logger.info(f"🏫 Tenant: {tenant}")
    logger.info(f"🆔 Tenant ID: {tenant_id}")
    logger.info("=" * 50)
    
    # 🔥 Buscar dados da escola
    escola = tenant
    
    # 🔥 Inicializar contadores
    total_alunos = 0
    total_turmas = 0
    total_professores = 0
    total_disciplinas = 0
    
    # 🔥 Se houver tenant, buscar dados
    if tenant_id:
        # 🔥 BUSCAR TURMAS
        try:
            total_turmas = Turma.objects.filter(tenant_id=tenant_id, ativo=True).count()
            logger.info(f"📊 Turmas (ativas): {total_turmas}")
        except Exception as e:
            logger.warning(f"Erro ao buscar turmas: {e}")
            total_turmas = 0
        
        # 🔥 BUSCAR DISCIPLINAS
        try:
            total_disciplinas = Disciplina.objects.filter(tenant_id=tenant_id, ativo=True).count()
            logger.info(f"📊 Disciplinas (ativas): {total_disciplinas}")
        except Exception as e:
            logger.warning(f"Erro ao buscar disciplinas: {e}")
            total_disciplinas = 0
        
        # 🔥 BUSCAR CLASSES (para debug)
        try:
            total_classes = Classe.objects.filter(tenant_id=tenant_id, ativo=True).count()
            logger.info(f"📊 Classes (ativas): {total_classes}")
        except:
            pass
        
        # 🔥 BUSCAR ALUNOS (se existir o modelo)
        if Aluno is not None:
            try:
                total_alunos = Aluno.objects.filter(tenant_id=tenant_id, ativo=True).count()
                logger.info(f"📊 Alunos: {total_alunos}")
            except Exception as e:
                logger.warning(f"Erro ao buscar alunos: {e}")
                total_alunos = 0
        else:
            logger.warning("⚠️ Modelo Aluno não encontrado")
            total_alunos = 0
        
        # 🔥 BUSCAR PROFESSORES (se existir o modelo)
        if Professor is not None:
            try:
                total_professores = Professor.objects.filter(tenant_id=tenant_id, ativo=True).count()
                logger.info(f"📊 Professores: {total_professores}")
            except Exception as e:
                logger.warning(f"Erro ao buscar professores: {e}")
                total_professores = 0
        else:
            logger.warning("⚠️ Modelo Professor não encontrado")
            total_professores = 0
    
    # 🔥 Se NÃO houver tenant, buscar todos os dados (fallback)
    else:
        logger.warning("⚠️ Nenhum tenant encontrado! Buscando todos os dados...")
        total_turmas = Turma.objects.filter(ativo=True).count()
        total_disciplinas = Disciplina.objects.filter(ativo=True).count()
        logger.info(f"📊 Todos os dados - Turmas: {total_turmas}, Disciplinas: {total_disciplinas}")
    
    # 🔥 LOG FINAL
    logger.info("=" * 50)
    logger.info("📊 DADOS FINAIS DO DASHBOARD:")
    logger.info(f"👨‍🎓 Alunos: {total_alunos}")
    logger.info(f"📚 Turmas: {total_turmas}")
    logger.info(f"👨‍🏫 Professores: {total_professores}")
    logger.info(f"📖 Disciplinas: {total_disciplinas}")
    logger.info("=" * 50)
    
    # 🔥 Construir contexto
    context = {
        'is_admin': is_admin,
        'escola': escola,
        'total_alunos': total_alunos,
        'total_turmas': total_turmas,
        'total_professores': total_professores,
        'total_disciplinas': total_disciplinas,
        'tenant_id': tenant_id,
        # Dados para admin Yitro
        'total_escolas': Instituicao.objects.count() if is_admin else 0,
        'total_usuarios': User.objects.count() if is_admin else 0,
        'escolas_ativas': Instituicao.objects.filter(ativo=True).count() if is_admin else 0,
        'escolas_inativas': Instituicao.objects.filter(ativo=False).count() if is_admin else 0,
        'ultimas_escolas': Instituicao.objects.all().order_by('-data_criacao')[:5] if is_admin else [],
    }
    
    return render(request, 'escola/partials/dashboard.html', context)


# ============================================
# 🔥 SECRETARIA GERAL (CORRIGIDAS COM DADOS)
# ============================================

@login_required
def secretaria_matriculas(request):
    """Matrícula e Confirmação - Secretaria Geral"""
    tenant = get_tenant_escola(request)
    context = {
        'titulo': 'Matrícula e Confirmação',
        'icone': 'bi-file-earmark-text',
        'modulo': 'Secretaria Geral',
        'tenant_nome': tenant.nome if tenant else None,
        'tenant_id': tenant.id if tenant else None,
    }
    return render(request, 'escola/partials/secretaria/matriculas.html', context)


@login_required
def secretaria_pagamentos(request):
    """Pagamentos - Secretaria Geral"""
    tenant = get_tenant_escola(request)
    context = {
        'titulo': 'Pagamentos',
        'icone': 'bi-wallet2',
        'modulo': 'Secretaria Geral',
        'tenant_nome': tenant.nome if tenant else None,
        'tenant_id': tenant.id if tenant else None,
    }
    return render(request, 'escola/partials/secretaria/pagamentos.html', context)


@login_required
def secretaria_alunos(request):
    """Lista de Alunos por Turma - Secretaria Geral COM DADOS"""
    try:
        tenant = get_tenant_escola(request)
        tenant_id = tenant.id if tenant else None
        
        # Buscar alunos se o modelo existir
        alunos = []
        turmas = []
        alunos_json = '[]'
        turmas_json = '[]'
        
        if tenant_id and Aluno is not None:
            alunos = Aluno.objects.filter(
                tenant_id=tenant_id,
                ativo=True
            ).select_related('turma').order_by('nome')[:100]
            
            turmas = Turma.objects.filter(
                tenant_id=tenant_id,
                ativo=True
            ).order_by('nome')
            
            # 🔥 Converter alunos para JSON
            alunos_list = []
            for a in alunos:
                alunos_list.append({
                    'id': a.id,
                    'nome': a.nome,
                    'matricula': a.matricula,
                    'turma': a.turma.nome if a.turma else '-',
                    'turma_id': a.turma.id if a.turma else None,
                    'data_nascimento': a.data_nascimento.strftime('%d/%m/%Y') if hasattr(a, 'data_nascimento') and a.data_nascimento else '-',
                    'status': getattr(a, 'status', 'ATIVO'),
                })
            alunos_json = json.dumps(alunos_list, cls=DjangoJSONEncoder)
            
            # 🔥 Converter turmas para JSON
            turmas_json = json.dumps([
                {'id': t.id, 'nome': t.nome} for t in turmas
            ], cls=DjangoJSONEncoder)
        
        context = {
            'titulo': 'Lista de Alunos por Turma',
            'icone': 'bi-people',
            'modulo': 'Secretaria Geral',
            'alunos': alunos,
            'turmas': turmas,
            'total_alunos': len(alunos),
            'tenant_id': tenant_id,
            'tenant_nome': tenant.nome if tenant else None,
            'tem_alunos': Aluno is not None,
            'alunos_json': alunos_json,  # 🔥 Dados dos alunos em JSON
            'turmas_json': turmas_json,  # 🔥 Dados das turmas em JSON
        }
        
        return render(request, 'escola/partials/secretaria/alunos.html', context)
        
    except Exception as e:
        logger.error(f"❌ Erro em secretaria_alunos: {e}")
        context = {
            'titulo': 'Lista de Alunos por Turma',
            'icone': 'bi-people',
            'modulo': 'Secretaria Geral',
            'erro': str(e),
            'alunos': [],
            'turmas': [],
            'total_alunos': 0,
            'alunos_json': '[]',
            'turmas_json': '[]',
            'tem_alunos': False,
        }
        return render(request, 'escola/partials/secretaria/alunos.html', context)


@login_required
def secretaria_documentos(request):
    """Solicitação de Documentos - Secretaria Geral"""
    tenant = get_tenant_escola(request)
    context = {
        'titulo': 'Solicitação de Documentos',
        'icone': 'bi-file-earmark',
        'modulo': 'Secretaria Geral',
        'tenant_nome': tenant.nome if tenant else None,
        'tenant_id': tenant.id if tenant else None,
    }
    return render(request, 'escola/partials/secretaria/documentos.html', context)


# ============================================
# 🔥 ÁREA ADMINISTRATIVA
# ============================================

@login_required
def admin_funcionarios(request):
    """Funcionários - Área Administrativa"""
    tenant = get_tenant_escola(request)
    context = {
        'titulo': 'Funcionários',
        'icone': 'bi-people',
        'modulo': 'Área Administrativa',
        'tenant_nome': tenant.nome if tenant else None,
        'tenant_id': tenant.id if tenant else None,
    }
    return render(request, 'escola/partials/admin/funcionarios.html', context)


@login_required
def admin_documentos(request):
    """Documentos - Área Administrativa"""
    tenant = get_tenant_escola(request)
    context = {
        'titulo': 'Documentos',
        'icone': 'bi-file-earmark',
        'modulo': 'Área Administrativa',
        'tenant_nome': tenant.nome if tenant else None,
        'tenant_id': tenant.id if tenant else None,
    }
    return render(request, 'escola/partials/admin/documentos.html', context)


@login_required
def admin_relatorios(request):
    """Relatórios - Área Administrativa"""
    tenant = get_tenant_escola(request)
    context = {
        'titulo': 'Relatórios',
        'icone': 'bi-file-earmark-text',
        'modulo': 'Área Administrativa',
        'tenant_nome': tenant.nome if tenant else None,
        'tenant_id': tenant.id if tenant else None,
    }
    return render(request, 'escola/partials/admin/relatorios.html', context)


@login_required
def admin_custos(request):
    """Gestão de Custos - Área Administrativa"""
    tenant = get_tenant_escola(request)
    context = {
        'titulo': 'Gestão de Custos',
        'icone': 'bi-coin',
        'modulo': 'Área Administrativa',
        'tenant_nome': tenant.nome if tenant else None,
        'tenant_id': tenant.id if tenant else None,
    }
    return render(request, 'escola/partials/admin/custos.html', context)


@login_required
def admin_folha_salarial(request):
    """Efetividade e Folha Salarial - Área Administrativa"""
    tenant = get_tenant_escola(request)
    context = {
        'titulo': 'Efetividade e Folha Salarial',
        'icone': 'bi-cash-stack',
        'modulo': 'Área Administrativa',
        'tenant_nome': tenant.nome if tenant else None,
        'tenant_id': tenant.id if tenant else None,
    }
    return render(request, 'escola/partials/admin/folha_salarial.html', context)


# escola/views.py

# escola/views.py

@login_required
def admin_usuarios(request):
    """Usuários - Área Administrativa (ISOLADO POR ESCOLA)"""
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group
    from .configuracao.models import UsuarioInstituicao
    
    User = get_user_model()
    
    tenant = get_tenant_escola(request)
    tenant_id = tenant.id if tenant else None
    user = request.user
    
    # 🔥 Super Admin vê todos os usuários (gestão global)
    if user.is_superuser and not tenant_id:
        usuarios = User.objects.all().order_by('username')
        total_usuarios = usuarios.count()
        total_ativos = usuarios.filter(is_active=True).count()
        total_inativos = usuarios.filter(is_active=False).count()
        total_admins = usuarios.filter(is_superuser=True).count()
        tenant_nome = "Todas as escolas (Super Admin)"
    else:
        # 🔥 Usuário normal vê APENAS os da sua escola
        if tenant_id:
            usuarios_ids = UsuarioInstituicao.objects.filter(
                instituicao_id=tenant_id,
                ativo=True
            ).values_list('usuario_id', flat=True).distinct()
            
            usuarios = User.objects.filter(id__in=usuarios_ids).order_by('username')
        else:
            usuarios = User.objects.none()
        
        total_usuarios = usuarios.count()
        total_ativos = usuarios.filter(is_active=True).count()
        total_inativos = usuarios.filter(is_active=False).count()
        total_admins = usuarios.filter(is_superuser=True).count()
        tenant_nome = tenant.nome if tenant else "Nenhuma escola"
    
    # 🔥 Grupos disponíveis para filtro
    grupos = Group.objects.all().values_list('name', flat=True)
    
    context = {
        'titulo': 'Usuários - Administrativo',
        'icone': 'bi-people',
        'modulo': 'Área Administrativa',
        'tenant_nome': tenant_nome,
        'tenant_id': tenant_id,
        'usuarios': usuarios,
        'total_usuarios': total_usuarios,
        'total_ativos': total_ativos,
        'total_inativos': total_inativos,
        'total_admins': total_admins,
        'grupos': grupos,
        'is_super_admin': user.is_superuser,
    }
    
    return render(request, 'escola/partials/admin/usuarios.html', context)


@login_required
def api_usuario_form(request, usuario_id=None):
    """Retorna o formulário para criar/editar usuário (ISOLADO POR ESCOLA)"""
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group
    from .configuracao.models import Instituicao, UsuarioInstituicao
    
    User = get_user_model()
    
    tenant = get_tenant_escola(request)
    tenant_id = tenant.id if tenant else None
    user = request.user
    
    usuario = None
    edit = False
    
    if usuario_id:
        usuario = get_object_or_404(User, id=usuario_id)
        edit = True
    
    # Buscar grupos disponíveis
    grupos = Group.objects.all().order_by('name')
    
    # 🔥 Buscar escolas para associar o usuário (ISOLADO POR ESCOLA)
    if user.is_superuser:
        # Super Admin vê todas as escolas
        instituicoes = Instituicao.objects.filter(ativo=True).order_by('nome')
    else:
        # 🔥 Usuário normal vê APENAS a escola onde está logado
        if tenant_id:
            instituicoes = Instituicao.objects.filter(id=tenant_id, ativo=True).order_by('nome')
        else:
            instituicoes = Instituicao.objects.none()
    
    # 🔥 Se estiver editando, verificar se o usuário pertence à escola atual
    if usuario and not user.is_superuser and tenant_id:
        # Verificar se o usuário tem associação com a escola atual
        tem_acesso = UsuarioInstituicao.objects.filter(
            usuario=usuario,
            instituicao_id=tenant_id,
            ativo=True
        ).exists()
        
        if not tem_acesso:
            # Se o usuário não pertence à escola, redirecionar ou mostrar erro
            return render(request, 'escola/partials/admin/erro.html', {
                'mensagem': 'Você não tem permissão para editar este usuário.'
            })
    
    context = {
        'usuario': usuario,
        'edit': edit,
        'tenant_id': tenant_id,
        'tenant_nome': tenant.nome if tenant else None,
        'grupos': grupos,
        'instituicoes': instituicoes,
        'is_super_admin': user.is_superuser,
        # 🔥 Para o template saber se deve mostrar o campo de escolas ou oculto
        'mostrar_escolas': user.is_superuser,
    }
    
    return render(request, 'escola/partials/admin/usuario_form.html', context)

    

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_usuario_salvar(request, usuario_id=None):
    """Salva usuário via AJAX"""
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group
    from .configuracao.models import Instituicao, UsuarioInstituicao
    
    User = get_user_model()
    
    try:
        tenant = get_tenant_escola(request)
        tenant_id = tenant.id if tenant else None
        
        # Dados do formulário
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        is_active = request.POST.get('is_active', 'on') == 'on'
        is_superuser = request.POST.get('is_superuser', '') == 'on'
        groups = request.POST.getlist('groups')
        instituicoes = request.POST.getlist('instituicoes')
        
        # Validar campos obrigatórios
        errors = {}
        
        if not username:
            errors['username'] = 'Nome de usuário é obrigatório'
        elif usuario_id is None and User.objects.filter(username=username).exists():
            errors['username'] = 'Este nome de usuário já está em uso'
        
        if not email:
            errors['email'] = 'E-mail é obrigatório'
        elif usuario_id is None and User.objects.filter(email=email).exists():
            errors['email'] = 'Este e-mail já está em uso'
        
        # Validar senha apenas se for criação ou se senha foi preenchida
        if usuario_id is None:
            if not password:
                errors['password'] = 'Senha é obrigatória'
            elif len(password) < 6:
                errors['password'] = 'Senha deve ter pelo menos 6 caracteres'
            elif password != password_confirm:
                errors['password_confirm'] = 'As senhas não coincidem'
        else:
            if password:
                if len(password) < 6:
                    errors['password'] = 'Senha deve ter pelo menos 6 caracteres'
                elif password != password_confirm:
                    errors['password_confirm'] = 'As senhas não coincidem'
        
        if not instituicoes:
            errors['instituicoes'] = 'Selecione pelo menos uma escola'
        
        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        
        # 🔥 Criar ou atualizar usuário
        if usuario_id:
            usuario = get_object_or_404(User, id=usuario_id)
            usuario.username = username
            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.is_active = is_active
            usuario.is_superuser = is_superuser
            
            if password:
                usuario.set_password(password)
            
            usuario.save()
            mensagem = f'Usuário {usuario.username} atualizado com sucesso!'
        else:
            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active,
                is_superuser=is_superuser
            )
            mensagem = f'Usuário {usuario.username} criado com sucesso!'
        
        # 🔥 Atualizar grupos
        usuario.groups.clear()
        for group_name in groups:
            try:
                group = Group.objects.get(name=group_name)
                usuario.groups.add(group)
            except Group.DoesNotExist:
                pass
        
        # 🔥 Atualizar instituições
        UsuarioInstituicao.objects.filter(usuario=usuario).delete()
        for inst_id in instituicoes:
            try:
                instituicao = Instituicao.objects.get(id=inst_id, ativo=True)
                UsuarioInstituicao.objects.create(
                    usuario=usuario,
                    instituicao=instituicao,
                    ativo=True
                )
            except Instituicao.DoesNotExist:
                pass
        
        return JsonResponse({
            'success': True,
            'message': mensagem,
            'usuario_id': usuario.id,
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar usuário: {e}")
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def api_usuario_deletar(request, usuario_id):
    """Deleta um usuário"""
    from django.contrib.auth import get_user_model
    from .configuracao.models import UsuarioInstituicao
    
    User = get_user_model()
    
    try:
        usuario = get_object_or_404(User, id=usuario_id)
        
        # Não permitir deletar o próprio usuário
        if usuario.id == request.user.id:
            return JsonResponse({
                'success': False,
                'errors': {'error': 'Você não pode deletar seu próprio usuário'}
            }, status=400)
        
        username = usuario.username
        
        # Remover associações com instituições
        UsuarioInstituicao.objects.filter(usuario=usuario).delete()
        
        # Deletar o usuário
        usuario.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Usuário {username} deletado com sucesso!'
        })
    except Exception as e:
        logger.error(f"❌ Erro ao deletar usuário: {e}")
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        }, status=500)

# ============================================
# 🔥 ÁREA FINANCEIRA
# ============================================

@login_required
def financeiro_relatorio(request):
    """Relatório Financeiro - Área Financeira"""
    tenant = get_tenant_escola(request)
    context = {
        'titulo': 'Relatório Financeiro',
        'icone': 'bi-file-earmark-text',
        'modulo': 'Área Financeira',
        'tenant_nome': tenant.nome if tenant else None,
        'tenant_id': tenant.id if tenant else None,
    }
    return render(request, 'escola/partials/financeiro/relatorio.html', context)


@login_required
def financeiro_tributario(request):
    """Relatório Tributário - Área Financeira"""
    tenant = get_tenant_escola(request)
    context = {
        'titulo': 'Relatório Tributário',
        'icone': 'bi-receipt',
        'modulo': 'Área Financeira',
        'tenant_nome': tenant.nome if tenant else None,
        'tenant_id': tenant.id if tenant else None,
    }
    return render(request, 'escola/partials/financeiro/tributario.html', context)


# ============================================
# 🔥 API PARA ALUNOS (AJAX)
# ============================================

@login_required
def api_alunos_listar(request):
    """API para listar alunos da escola atual (JSON)"""
    try:
        tenant = get_tenant_escola(request)
        tenant_id = tenant.id if tenant else None
        
        if not tenant_id:
            return JsonResponse({
                'success': False,
                'error': 'Nenhuma escola selecionada'
            }, status=400)
        
        if Aluno is None:
            return JsonResponse({
                'success': False,
                'error': 'Modelo Aluno não encontrado'
            }, status=404)
        
        alunos = Aluno.objects.filter(
            tenant_id=tenant_id,
            ativo=True
        ).select_related('turma').order_by('nome')
        
        dados_alunos = []
        for aluno in alunos:
            dados_alunos.append({
                'id': aluno.id,
                'nome': aluno.nome,
                'matricula': aluno.matricula,
                'turma': aluno.turma.nome if aluno.turma else '-',
                'turma_id': aluno.turma.id if aluno.turma else None,
                'data_nascimento': aluno.data_nascimento.strftime('%d/%m/%Y') if hasattr(aluno, 'data_nascimento') and aluno.data_nascimento else '-',
                'status': getattr(aluno, 'status', 'ATIVO'),
                'status_display': dict(getattr(aluno, 'STATUS_CHOICES', [('ATIVO', 'Ativo')])).get(getattr(aluno, 'status', 'ATIVO'), 'Ativo'),
            })
        
        return JsonResponse({
            'success': True,
            'data': dados_alunos,
            'total': len(dados_alunos),
            'tenant_id': tenant_id,
            'tenant_nome': tenant.nome
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar alunos: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_alunos_por_turma(request, turma_id):
    """API para listar alunos por turma (JSON)"""
    try:
        tenant = get_tenant_escola(request)
        tenant_id = tenant.id if tenant else None
        
        if not tenant_id:
            return JsonResponse({
                'success': False,
                'error': 'Nenhuma escola selecionada'
            }, status=400)
        
        if Aluno is None:
            return JsonResponse({
                'success': False,
                'error': 'Modelo Aluno não encontrado'
            }, status=404)
        
        alunos = Aluno.objects.filter(
            tenant_id=tenant_id,
            turma_id=turma_id,
            ativo=True
        ).order_by('nome')
        
        dados_alunos = []
        for aluno in alunos:
            dados_alunos.append({
                'id': aluno.id,
                'nome': aluno.nome,
                'matricula': aluno.matricula,
                'data_nascimento': aluno.data_nascimento.strftime('%d/%m/%Y') if hasattr(aluno, 'data_nascimento') and aluno.data_nascimento else '-',
                'status': getattr(aluno, 'status', 'ATIVO'),
            })
        
        return JsonResponse({
            'success': True,
            'data': dados_alunos,
            'total': len(dados_alunos),
            'turma_id': turma_id
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar alunos por turma: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_turmas_listar(request):
    """API para listar turmas da escola (JSON)"""
    try:
        tenant = get_tenant_escola(request)
        tenant_id = tenant.id if tenant else None
        
        if not tenant_id:
            return JsonResponse({
                'success': False,
                'error': 'Nenhuma escola selecionada'
            }, status=400)
        
        turmas = Turma.objects.filter(
            tenant_id=tenant_id,
            ativo=True
        ).order_by('nome')
        
        dados_turmas = []
        for turma in turmas:
            total_alunos = 0
            if Aluno is not None:
                total_alunos = Aluno.objects.filter(
                    turma=turma,
                    ativo=True
                ).count()
            
            dados_turmas.append({
                'id': turma.id,
                'nome': turma.nome,
                'ano': getattr(turma, 'ano', None),
                'total_alunos': total_alunos,
                'descricao': getattr(turma, 'descricao', ''),
            })
        
        return JsonResponse({
            'success': True,
            'data': dados_turmas,
            'total': len(dados_turmas)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar turmas: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)