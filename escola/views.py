from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.decorators import (
    yitro_admin_required, 
    super_admin_required, 
    escola_required, 
    yitro_view_required,
    admin_required
)
from .configuracao.models import Instituicao, UsuarioInstituicao
from django.contrib.auth import get_user_model

User = get_user_model()

# ============================================
# VIEW PRINCIPAL - SPA
# ============================================

@login_required
def index(request):
    """Página inicial da Escola - Carrega o SPA"""
    user = request.user
    
    tenant_slug = request.GET.get('tenant')
    
    # 🔥 SEPARAR: is_super_admin (Yitro) e is_admin_escola (dentro da escola)
    is_super_admin = user.is_superuser
    is_admin_escola = user.tem_acesso_departamento('administrativo')
    
    tenant_nome = None
    tenant_nome_fantasia = None
    carregar_dashboard = False
    esta_na_escola = False  # 🔥 NOVO: indica se está dentro de uma escola
    
    if tenant_slug:
        try:
            escola = Instituicao.objects.get(slug=tenant_slug)
            tenant_nome = escola.nome
            tenant_nome_fantasia = escola.nome_fantasia
            carregar_dashboard = True
            esta_na_escola = True  # 🔥 ESTÁ DENTRO DE UMA ESCOLA
        except Instituicao.DoesNotExist:
            pass
    
    context = {
        'is_super_admin': is_super_admin,      # 🔥 NOVO
        'is_admin_escola': is_admin_escola,    # 🔥 NOVO
        'is_admin': is_super_admin,            # Mantido para compatibilidade
        'show_escolas': is_super_admin,
        'tenant_slug': tenant_slug,
        'tenant_nome': tenant_nome,
        'tenant_nome_fantasia': tenant_nome_fantasia,
        'carregar_dashboard': carregar_dashboard,
        'esta_na_escola': esta_na_escola,      # 🔥 NOVO
    }
    
    return render(request, 'base_escola.html', context)

# ============================================
# ENTRAR NA ESCOLA PELO SLUG
# ============================================

@login_required
def entrar_escola(request, slug):
    """Redireciona para o dashboard da escola pelo slug"""
    escola = get_object_or_404(Instituicao, slug=slug)
    
    user = request.user
    if not user.is_superuser:
        if not UsuarioInstituicao.objects.filter(usuario=user, instituicao=escola).exists():
            messages.error(request, 'Você não tem acesso a esta escola.')
            return redirect('escola:index')
    
    return redirect(f'/escola/?tenant={escola.slug}')


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
# DASHBOARD - UNIFICADO
# ============================================

@login_required
def api_dashboard(request):
    """Dashboard - Unifica dashboard geral e dashboard da escola"""
    user = request.user
    
    is_admin = user.is_superuser or user.tem_acesso_departamento('administrativo')
    
    if is_admin:
        context = {
            'is_admin': True,
            'total_escolas': Instituicao.objects.count(),
            'total_usuarios': User.objects.count(),
            'escolas_ativas': Instituicao.objects.filter(ativo=True).count(),
            'escolas_inativas': Instituicao.objects.filter(ativo=False).count(),
            'ultimas_escolas': Instituicao.objects.all().order_by('-data_criacao')[:5],
        }
    else:
        try:
            usuario_instituicao = UsuarioInstituicao.objects.filter(usuario=user).first()
            if usuario_instituicao:
                escola = usuario_instituicao.instituicao
                context = {
                    'is_admin': False,
                    'escola': escola,
                    'escola_nome': escola.nome,
                    'total_alunos': 0,
                    'total_turmas': 0,
                    'total_professores': 0,
                    'total_disciplinas': 0,
                }
            else:
                context = {
                    'is_admin': False,
                    'escola': None,
                    'escola_nome': 'Nenhuma escola associada',
                    'total_alunos': 0,
                    'total_turmas': 0,
                    'total_professores': 0,
                    'total_disciplinas': 0,
                }
        except:
            context = {
                'is_admin': False,
                'escola': None,
                'escola_nome': 'Erro ao carregar escola',
                'total_alunos': 0,
                'total_turmas': 0,
                'total_professores': 0,
                'total_disciplinas': 0,
            }
    
    return render(request, 'escola/partials/dashboard.html', context)