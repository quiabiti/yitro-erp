# forms.py - VERSÃO COMPLETAMENTE CORRIGIDA

from django import forms
from .models import AnoLectivo, Trimestre, NivelEnsino, Classe, Disciplina, Turma


class AnoLectivoForm(forms.ModelForm):
    class Meta:
        model = AnoLectivo
        fields = ['ano', 'data_inicio', 'data_fim', 'descricao', 'ativo']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }


class TrimestreForm(forms.ModelForm):
    class Meta:
        model = Trimestre
        fields = ['ano_lectivo', 'numero', 'nome', 'data_inicio', 'data_fim', 'descricao', 'ativo']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }


class NivelEnsinoForm(forms.ModelForm):
    """Formulário para Nível de Ensino"""
    class Meta:
        model = NivelEnsino
        fields = ['nome', 'descricao', 'ordem', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'metal-form-control',
                'placeholder': 'Ex: Ensino Fundamental, Ensino Médio...'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'metal-form-control',
                'rows': 3,
                'placeholder': 'Descrição detalhada do nível de ensino'
            }),
            'ordem': forms.NumberInput(attrs={
                'class': 'metal-form-control',
                'min': 0,
                'placeholder': '0'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome': 'Nome do Nível',
            'descricao': 'Descrição',
            'ordem': 'Ordem de Exibição',
            'ativo': 'Ativo'
        }


class ClasseForm(forms.ModelForm):
    """Formulário para Classe"""
    class Meta:
        model = Classe
        fields = ['nome', 'nivel_ensino', 'ano_lectivo', 'is_exame', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'metal-form-control',
                'placeholder': 'Ex: 1º Ano A'
            }),
            'nivel_ensino': forms.Select(attrs={
                'class': 'metal-form-select'
            }),
            'ano_lectivo': forms.Select(attrs={
                'class': 'metal-form-select'
            }),
            'is_exame': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'metal-form-control',
                'rows': 3,
                'placeholder': 'Descrição da classe'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome': 'Nome da Classe',
            'nivel_ensino': 'Nível de Ensino',
            'ano_lectivo': 'Ano Lectivo',
            'is_exame': 'Classe de Exame',
            'descricao': 'Descrição',
            'ativo': 'Ativo'
        }


# 🔥 FORMULÁRIO DE DISCIPLINA CORRIGIDO
class DisciplinaForm(forms.ModelForm):
    """Formulário para Disciplina - Suporte a Múltiplas Classes (ManyToMany)"""
    
    class Meta:
        model = Disciplina
        # 🔥 USAR 'classes' (ManyToMany) em vez de 'classe' (ForeignKey)
        fields = ['nome', 'codigo', 'carga_horaria', 'classes', 'tipo', 'is_chave', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'metal-form-control',
                'placeholder': 'Ex: Matemática, Português, Ciências...'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'metal-form-control',
                'placeholder': 'Ex: MAT-001, PORT-001...'
            }),
            'carga_horaria': forms.NumberInput(attrs={
                'class': 'metal-form-control',
                'placeholder': '60',
                'min': 1,
                'max': 240
            }),
            # 🔥 SelectMultiple para múltiplas classes
            'classes': forms.SelectMultiple(attrs={
                'class': 'metal-form-control',
                'style': 'height: auto; min-height: 150px;'
            }),
            'tipo': forms.Select(attrs={
                'class': 'metal-form-select'
            }),
            'is_chave': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'metal-form-control',
                'rows': 3,
                'placeholder': 'Descreva os objetivos, conteúdo programático e competências da disciplina'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome': 'Nome da Disciplina',
            'codigo': 'Código',
            'carga_horaria': 'Carga Horária (horas)',
            'classes': 'Classes Associadas',
            'tipo': 'Tipo de Disciplina',
            'is_chave': 'Disciplina Chave',
            'descricao': 'Descrição',
            'ativo': 'Ativo'
        }
        help_texts = {
            'codigo': 'Código único para identificar a disciplina',
            'carga_horaria': 'Total de horas por trimestre/semestre',
            'tipo': 'Curricular: obrigatória | Extra: atividades complementares | Opcional: escolha do aluno',
            'is_chave': 'Disciplinas chave são fundamentais para o currículo básico',
            'ativo': 'Desative para ocultar esta disciplina do sistema',
            'classes': 'Selecione uma ou mais classes onde esta disciplina será ministrada'
        }
        error_messages = {
            'classes': {
                'required': 'Selecione pelo menos uma classe para associar à disciplina',
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🔥 Filtrar apenas classes ativas, ordenadas por nível e nome
        self.fields['classes'].queryset = Classe.objects.filter(
            ativo=True
        ).select_related('nivel_ensino').order_by(
            'nivel_ensino__ordem', 
            'nivel_ensino__nome',
            'nome'
        )
        # 🔥 Tornar o campo obrigatório
        self.fields['classes'].required = True
        
        # 🔥 Opções para o campo tipo com ícones
        TIPO_CHOICES = [
            ('curricular', '📚 Curricular'),
            ('extra_curricular', '🎯 Extra-Curricular'),
            ('opcional', '⭐ Opcional'),
        ]
        self.fields['tipo'].choices = TIPO_CHOICES


class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['nome', 'codigo', 'classe', 'ano_lectivo', 'capacidade', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'metal-form-control',
                'placeholder': 'Ex: Turma A'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'metal-form-control',
                'placeholder': 'Ex: TUR-A-001'
            }),
            'classe': forms.Select(attrs={
                'class': 'metal-form-select'
            }),
            'ano_lectivo': forms.Select(attrs={
                'class': 'metal-form-select'
            }),
            'capacidade': forms.NumberInput(attrs={
                'class': 'metal-form-control',
                'placeholder': '30',
                'min': 1
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'metal-form-control',
                'rows': 3,
                'placeholder': 'Descrição da turma'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome': 'Nome da Turma',
            'codigo': 'Código',
            'classe': 'Classe',
            'ano_lectivo': 'Ano Lectivo',
            'capacidade': 'Capacidade',
            'descricao': 'Descrição',
            'ativo': 'Ativo'
        }