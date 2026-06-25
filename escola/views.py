from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# ============================================
# VIEW PRINCIPAL - SPA
# ============================================

def index(request):
    """Página inicial da Escola - Carrega o SPA"""
    return render(request, 'base_escola.html')


# ============================================
# VIEWS DA API
# ============================================

def api_dashboard(request):
    """Dashboard - HTML parcial"""
    context = {
        'total_alunos': 0,
        'total_turmas': 0,
        'total_professores': 0,
        'total_disciplinas': 0,
    }
    return render(request, 'escola/partials/dashboard.html', context)


# ============================================
# ALUNOS
# ============================================

def api_alunos(request):
    """Lista de Alunos - HTML parcial"""
    alunos = []
    context = {
        'alunos': alunos,
        'total': len(alunos),
    }
    return render(request, 'escola/partials/alunos_lista.html', context)


def api_alunos_novo(request):
    """Formulário para novo Aluno - HTML parcial"""
    return render(request, 'escola/partials/aluno_form.html', {'aluno': None, 'edit': False})


def api_alunos_editar(request, aluno_id):
    """Formulário para editar Aluno - HTML parcial"""
    context = {
        'aluno': None,
        'edit': True,
        'aluno_id': aluno_id,
    }
    return render(request, 'escola/partials/aluno_form.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def api_alunos_salvar(request):
    """Salvar Aluno via AJAX"""
    try:
        nome = request.POST.get('nome')
        
        if not nome:
            return JsonResponse({'success': False, 'errors': {'nome': 'Nome é obrigatório'}})
        
        return JsonResponse({
            'success': True,
            'message': 'Aluno salvo com sucesso!',
            'aluno_id': 1,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        })


@csrf_exempt
@require_http_methods(["DELETE"])
def api_alunos_deletar(request, aluno_id):
    """Deletar Aluno via AJAX"""
    try:
        return JsonResponse({
            'success': True,
            'message': 'Aluno deletado com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        })


# ============================================
# TURMAS
# ============================================

def api_turmas(request):
    """Lista de Turmas - HTML parcial"""
    turmas = []
    context = {
        'turmas': turmas,
        'total': len(turmas),
    }
    return render(request, 'escola/partials/turmas_lista.html', context)


def api_turmas_novo(request):
    """Formulário para nova Turma - HTML parcial"""
    return render(request, 'escola/partials/turma_form.html', {'turma': None, 'edit': False})


def api_turmas_editar(request, turma_id):
    """Formulário para editar Turma - HTML parcial"""
    context = {
        'turma': None,
        'edit': True,
        'turma_id': turma_id,
    }
    return render(request, 'escola/partials/turma_form.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def api_turmas_salvar(request):
    """Salvar Turma via AJAX"""
    try:
        nome = request.POST.get('nome')
        
        if not nome:
            return JsonResponse({'success': False, 'errors': {'nome': 'Nome é obrigatório'}})
        
        return JsonResponse({
            'success': True,
            'message': 'Turma salva com sucesso!',
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        })


@csrf_exempt
@require_http_methods(["DELETE"])
def api_turmas_deletar(request, turma_id):
    """Deletar Turma via AJAX"""
    try:
        return JsonResponse({
            'success': True,
            'message': 'Turma deletada com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        })


# ============================================
# MATRÍCULAS
# ============================================

def api_matriculas(request):
    """Lista de Matrículas - HTML parcial"""
    matriculas = []
    context = {
        'matriculas': matriculas,
        'total': len(matriculas),
    }
    return render(request, 'escola/partials/matriculas_lista.html', context)


def api_matriculas_nova(request):
    """Formulário para nova Matrícula - HTML parcial"""
    context = {
        'alunos': [],
        'turmas': [],
    }
    return render(request, 'escola/partials/matricula_form.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def api_matriculas_salvar(request):
    """Salvar Matrícula via AJAX"""
    try:
        return JsonResponse({
            'success': True,
            'message': 'Matrícula realizada com sucesso!',
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        })


@csrf_exempt
@require_http_methods(["DELETE"])
def api_matriculas_deletar(request, matricula_id):
    """Deletar Matrícula via AJAX"""
    try:
        return JsonResponse({
            'success': True,
            'message': 'Matrícula cancelada com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        })


# ============================================
# DISCIPLINAS
# ============================================

def api_disciplinas(request):
    """Lista de Disciplinas - HTML parcial"""
    disciplinas = []
    context = {
        'disciplinas': disciplinas,
        'total': len(disciplinas),
    }
    return render(request, 'escola/partials/disciplinas_lista.html', context)


def api_disciplinas_novo(request):
    """Formulário para nova Disciplina - HTML parcial"""
    return render(request, 'escola/partials/disciplina_form.html', {'edit': False})


@csrf_exempt
@require_http_methods(["POST"])
def api_disciplinas_salvar(request):
    """Salvar Disciplina via AJAX"""
    try:
        return JsonResponse({
            'success': True,
            'message': 'Disciplina salva com sucesso!',
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        })


# ============================================
# PROFESSORES
# ============================================

def api_professores(request):
    """Lista de Professores - HTML parcial"""
    professores = []
    context = {
        'professores': professores,
        'total': len(professores),
    }
    return render(request, 'escola/partials/professores_lista.html', context)


def api_professores_novo(request):
    """Formulário para novo Professor - HTML parcial"""
    return render(request, 'escola/partials/professor_form.html', {'edit': False})


@csrf_exempt
@require_http_methods(["POST"])
def api_professores_salvar(request):
    """Salvar Professor via AJAX"""
    try:
        return JsonResponse({
            'success': True,
            'message': 'Professor salvo com sucesso!',
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        })


# ============================================
# CONFIGURAÇÕES
# ============================================

def api_configuracoes(request):
    """Configurações - HTML parcial"""
    return render(request, 'escola/partials/configuracoes.html', {'escola': None})


@csrf_exempt
@require_http_methods(["POST"])
def api_configuracoes_salvar(request):
    """Salvar Configurações via AJAX"""
    try:
        return JsonResponse({
            'success': True,
            'message': 'Configurações salvas com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': {'error': str(e)}
        })
