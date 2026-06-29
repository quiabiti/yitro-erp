# escola/pedagogico/views.py - VERSÃO CORRIGIDA COM SUPORTE A ManyToMany

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import AnoLectivo, Trimestre, NivelEnsino, Classe, Disciplina, Turma
from .forms import (
    AnoLectivoForm, TrimestreForm, NivelEnsinoForm,
    ClasseForm, DisciplinaForm, TurmaForm
)
from escola.configuracao.models import Instituicao
import logging

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
                pass
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
                pass
            except Exception as e:
                logger.error(f"❌ Erro ao buscar tenant: {e}")
    
    return tenant


# ============================================
# UTILITÁRIOS
# ============================================

def get_categoria_model(categoria):
    """Retorna o modelo correspondente à categoria"""
    models_map = {
        'ano_lectivo': AnoLectivo,
        'trimestre': Trimestre,
        'nivel_ensino': NivelEnsino,
        'classe': Classe,
        'disciplina': Disciplina,
        'turma': Turma,
    }
    return models_map.get(categoria)


def get_form_class(categoria):
    """Retorna o formulário correspondente à categoria"""
    forms_map = {
        'ano_lectivo': AnoLectivoForm,
        'trimestre': TrimestreForm,
        'nivel_ensino': NivelEnsinoForm,
        'classe': ClasseForm,
        'disciplina': DisciplinaForm,
        'turma': TurmaForm,
    }
    return forms_map.get(categoria)


# ============================================
# VIEW PRINCIPAL - GESTÃO PEDAGÓGICA
# ============================================

@login_required
def api_pedagogico_dashboard(request):
    """Dashboard do módulo pedagógico - Gestão do Ano Lectivo"""
    logger.info("=" * 50)
    logger.info("🚀 api_pedagogico_dashboard CHAMADA!")
    logger.info(f"👤 Usuário: {request.user.username}")
    logger.info(f"🔐 Autenticado: {request.user.is_authenticated}")
    
    tenant = get_tenant_escola(request)
    logger.info(f"🏫 Tenant: {tenant}")
    logger.info("=" * 50)
    
    context = {
        'titulo': 'Gestão Pedagógica',
        'icone': 'bi-calendar3',
        'modulo': 'Pedagógico',
    }
    return render(request, 'escola/partials/pedagogico/gestao_pedagogica.html', context)


@login_required
def pedagogico_dashboard(request):
    """Página principal do módulo pedagógico"""
    return render(request, 'escola/partials/pedagogico/gestao_pedagogica.html')


# ============================================
# STATS (DASHBOARD) - COM ISOLAMENTO
# ============================================

@login_required
def api_stats(request):
    """Retorna estatísticas para o dashboard - filtrando pela escola"""
    try:
        tenant = get_tenant_escola(request)
        tenant_id = tenant.id if tenant else None
        
        logger.info(f"📊 api_stats - Tenant ID: {tenant_id}")
        
        if tenant_id:
            data = {
                'ano_lectivo': AnoLectivo.objects.filter(tenant_id=tenant_id, ativo=True).count(),
                'trimestre': Trimestre.objects.filter(tenant_id=tenant_id, ativo=True).count(),
                'nivel_ensino': NivelEnsino.objects.filter(tenant_id=tenant_id, ativo=True).count(),
                'classe': Classe.objects.filter(tenant_id=tenant_id, ativo=True).count(),
                'disciplina': Disciplina.objects.filter(tenant_id=tenant_id, ativo=True).count(),
                'turma': Turma.objects.filter(tenant_id=tenant_id, ativo=True).count(),
            }
        else:
            data = {
                'ano_lectivo': AnoLectivo.objects.filter(ativo=True).count(),
                'trimestre': Trimestre.objects.filter(ativo=True).count(),
                'nivel_ensino': NivelEnsino.objects.filter(ativo=True).count(),
                'classe': Classe.objects.filter(ativo=True).count(),
                'disciplina': Disciplina.objects.filter(ativo=True).count(),
                'turma': Turma.objects.filter(ativo=True).count(),
            }
        
        logger.info(f"📊 Dados retornados: {data}")
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"❌ Erro em api_stats: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# VIEWS PARA LISTAR - COM ISOLAMENTO
# ============================================

@login_required
def api_listar(request, categoria):
    """Lista todos os itens de uma categoria - filtrando pela escola"""
    try:
        Model = get_categoria_model(categoria)
        if not Model:
            return JsonResponse({'success': False, 'error': 'Categoria inválida'})
        
        tenant = get_tenant_escola(request)
        tenant_id = tenant.id if tenant else None
        
        logger.info(f"📋 api_listar - Categoria: {categoria}, Tenant ID: {tenant_id}")
        
        # 🔥 Filtrar por tenant_id
        if tenant_id:
            items = Model.objects.filter(tenant_id=tenant_id, ativo=True).order_by('-id')
            logger.info(f"📋 {categoria} - Encontrados (com tenant): {items.count()}")
        else:
            items = Model.objects.filter(ativo=True).order_by('-id')
            logger.info(f"📋 {categoria} - Encontrados (todos): {items.count()}")
        
        # Formatar dados para o frontend
        data = []
        for item in items:
            item_data = {
                'id': item.id,
                'nome': str(item),
                'ativo': item.ativo,
            }
            
            # Adicionar campos específicos
            if hasattr(item, 'ano'):
                item_data['ano'] = item.ano
            if hasattr(item, 'numero'):
                item_data['numero'] = item.numero
            if hasattr(item, 'codigo'):
                item_data['codigo'] = item.codigo
            if hasattr(item, 'carga_horaria'):
                item_data['carga_horaria'] = item.carga_horaria
            if hasattr(item, 'capacidade'):
                item_data['capacidade'] = item.capacidade
            if hasattr(item, 'ordem'):
                item_data['ordem'] = item.ordem
            if hasattr(item, 'descricao'):
                item_data['descricao'] = item.descricao
            if hasattr(item, 'tenant_id'):
                item_data['tenant_id'] = item.tenant_id
            
            # 🔥 PARA DISCIPLINA - ADICIONAR CLASSES ASSOCIADAS
            if categoria == 'disciplina' and hasattr(item, 'classes'):
                classes = item.classes.all()
                item_data['classes_ids'] = list(classes.values_list('id', flat=True))
                item_data['classes_nomes'] = list(classes.values_list('nome', flat=True))
                item_data['classes_display'] = ", ".join(classes.values_list('nome', flat=True))
            
            # Relações
            if hasattr(item, 'ano_lectivo') and item.ano_lectivo:
                try:
                    item_data['ano_lectivo_id'] = item.ano_lectivo.id
                    item_data['ano_lectivo_nome'] = str(item.ano_lectivo)
                except:
                    pass
                    
            if hasattr(item, 'classe') and item.classe:
                try:
                    item_data['classe_id'] = item.classe.id
                    item_data['classe_nome'] = str(item.classe)
                except:
                    pass
                    
            if hasattr(item, 'nivel_ensino') and item.nivel_ensino:
                try:
                    item_data['nivel_ensino_id'] = item.nivel_ensino.id
                    item_data['nivel_ensino_nome'] = str(item.nivel_ensino)
                except:
                    pass
            
            data.append(item_data)
        
        logger.info(f"📋 {categoria} - Dados retornados: {len(data)}")
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"❌ Erro em api_listar ({categoria}): {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# VIEWS PARA FORMULÁRIOS (CRIAR/EDITAR)
# ============================================

@login_required
def api_form_criar(request, categoria):
    """Retorna o formulário para criar um novo item"""
    try:
        Form = get_form_class(categoria)
        if not Form:
            return JsonResponse({'success': False, 'error': 'Categoria inválida'})
        
        tenant = get_tenant_escola(request)
        tenant_id = tenant.id if tenant else None
        
        form = Form()
        context = {
            'form': form,
            'categoria': categoria,
            'item': None,
            'edit': False,
            'tenant_id': tenant_id,
        }
        
        # 🔥 PARA DISCIPLINA - PASSAR CLASSES DISPONÍVEIS
        if categoria == 'disciplina':
            if tenant_id:
                context['classes_disponiveis'] = Classe.objects.filter(
                    tenant_id=tenant_id, ativo=True
                ).select_related('nivel_ensino').order_by('nivel_ensino__ordem', 'nome')
            else:
                context['classes_disponiveis'] = Classe.objects.filter(
                    ativo=True
                ).select_related('nivel_ensino').order_by('nivel_ensino__ordem', 'nome')
            context['classes_selecionadas'] = []
        
        # Adicionar querysets para selects (filtrados por tenant)
        if categoria in ['trimestre', 'classe', 'turma']:
            if tenant_id:
                context['ano_lectivos'] = AnoLectivo.objects.filter(tenant_id=tenant_id, ativo=True)
            else:
                context['ano_lectivos'] = AnoLectivo.objects.filter(ativo=True)
        
        if categoria in ['classe', 'disciplina', 'turma']:
            if tenant_id:
                context['niveis_ensino'] = NivelEnsino.objects.filter(tenant_id=tenant_id, ativo=True)
            else:
                context['niveis_ensino'] = NivelEnsino.objects.filter(ativo=True)
        
        if categoria in ['turma']:
            if tenant_id:
                context['classes'] = Classe.objects.filter(tenant_id=tenant_id, ativo=True)
            else:
                context['classes'] = Classe.objects.filter(ativo=True)
        
        return render(request, f'escola/partials/pedagogico/{categoria}_form.html', context)
    except Exception as e:
        logger.error(f"❌ Erro em api_form_criar ({categoria}): {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_form_editar(request, categoria, item_id):
    """Retorna o formulário para editar um item existente"""
    try:
        Model = get_categoria_model(categoria)
        Form = get_form_class(categoria)
        
        if not Model or not Form:
            return JsonResponse({'success': False, 'error': 'Categoria inválida'})
        
        tenant = get_tenant_escola(request)
        tenant_id = tenant.id if tenant else None
        
        item = get_object_or_404(Model, id=item_id)
        
        # 🔥 Verificar se o item pertence à escola
        if tenant_id and hasattr(item, 'tenant_id') and item.tenant_id != tenant_id:
            return JsonResponse({'success': False, 'error': 'Este item não pertence à sua escola'})
        
        form = Form(instance=item)
        context = {
            'form': form,
            'categoria': categoria,
            'item': item,
            'edit': True,
            'tenant_id': tenant_id,
        }
        
        # 🔥 PARA DISCIPLINA - PASSAR CLASSES DISPONÍVEIS E SELECIONADAS
        if categoria == 'disciplina':
            if tenant_id:
                context['classes_disponiveis'] = Classe.objects.filter(
                    tenant_id=tenant_id, ativo=True
                ).select_related('nivel_ensino').order_by('nivel_ensino__ordem', 'nome')
            else:
                context['classes_disponiveis'] = Classe.objects.filter(
                    ativo=True
                ).select_related('nivel_ensino').order_by('nivel_ensino__ordem', 'nome')
            context['classes_selecionadas'] = list(item.classes.values_list('id', flat=True))
        
        if categoria in ['trimestre', 'classe', 'turma']:
            if tenant_id:
                context['ano_lectivos'] = AnoLectivo.objects.filter(tenant_id=tenant_id, ativo=True)
            else:
                context['ano_lectivos'] = AnoLectivo.objects.filter(ativo=True)
        
        if categoria in ['classe', 'disciplina', 'turma']:
            if tenant_id:
                context['niveis_ensino'] = NivelEnsino.objects.filter(tenant_id=tenant_id, ativo=True)
            else:
                context['niveis_ensino'] = NivelEnsino.objects.filter(ativo=True)
        
        if categoria in ['turma']:
            if tenant_id:
                context['classes'] = Classe.objects.filter(tenant_id=tenant_id, ativo=True)
            else:
                context['classes'] = Classe.objects.filter(ativo=True)
        
        return render(request, f'escola/partials/pedagogico/{categoria}_form.html', context)
    except Exception as e:
        logger.error(f"❌ Erro em api_form_editar ({categoria}, {item_id}): {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# VIEWS PARA SALVAR (CRIAR/ATUALIZAR)
# ============================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_salvar(request, categoria, item_id=None):
    """Salva um item (cria ou atualiza)"""
    try:
        Model = get_categoria_model(categoria)
        Form = get_form_class(categoria)
        
        if not Model or not Form:
            return JsonResponse({'success': False, 'error': 'Categoria inválida'})
        
        tenant = get_tenant_escola(request)
        tenant_id = tenant.id if tenant else None
        
        if item_id:
            instance = get_object_or_404(Model, id=item_id)
            # 🔥 Verificar se o item pertence à escola
            if tenant_id and hasattr(instance, 'tenant_id') and instance.tenant_id != tenant_id:
                return JsonResponse({'success': False, 'error': 'Este item não pertence à sua escola'})
            form = Form(request.POST, instance=instance)
        else:
            form = Form(request.POST)
        
        if form.is_valid():
            item = form.save(commit=False)
            
            # 🔥 ADICIONAR TENANT_ID
            if tenant_id and not item_id and hasattr(item, 'tenant_id'):
                item.tenant_id = tenant_id
            
            item.save()
            
            # 🔥 SALVAR RELACIONAMENTOS MANYTOMANY (classes)
            if hasattr(form, 'save_m2m'):
                form.save_m2m()
            
            # 🔥 PARA DISCIPLINA - LOG DAS CLASSES ASSOCIADAS
            if categoria == 'disciplina' and hasattr(item, 'classes'):
                classes_ids = request.POST.getlist('classes')
                logger.info(f"📋 Disciplina {item.id} - Classes associadas: {classes_ids}")
            
            return JsonResponse({
                'success': True,
                'message': f'{categoria.replace("_", " ").title()} salvo com sucesso!',
                'id': item.id
            })
        else:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0]
            logger.error(f"❌ Erros no formulário: {errors}")
            return JsonResponse({'success': False, 'errors': errors})
    except Exception as e:
        logger.error(f"❌ Erro em api_salvar ({categoria}, {item_id}): {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# VIEWS PARA DELETAR
# ============================================

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def api_deletar(request, categoria, item_id):
    """Deleta um item"""
    try:
        Model = get_categoria_model(categoria)
        if not Model:
            return JsonResponse({'success': False, 'error': 'Categoria inválida'})
        
        tenant = get_tenant_escola(request)
        tenant_id = tenant.id if tenant else None
        
        item = get_object_or_404(Model, id=item_id)
        
        # 🔥 Verificar se o item pertence à escola
        if tenant_id and hasattr(item, 'tenant_id') and item.tenant_id != tenant_id:
            return JsonResponse({'success': False, 'error': 'Este item não pertence à sua escola'})
        
        nome = str(item)
        item.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{nome} deletado com sucesso!'
        })
    except Exception as e:
        logger.error(f"❌ Erro em api_deletar ({categoria}, {item_id}): {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})