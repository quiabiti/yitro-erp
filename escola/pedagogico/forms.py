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
    """Formulário para Classe - Atualizado com NivelEnsino e is_exame"""
    class Meta:
        model = Classe
        fields = ['nome', 'nivel_ensino', 'ano_lectivo', 'is_exame', 'descricao', 'ativo']  # 🔥 ADICIONADO is_exame
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
            'is_exame': forms.CheckboxInput(attrs={  # 🔥 NOVO
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
            'is_exame': 'Classe de Exame',  # 🔥 NOVO
            'descricao': 'Descrição',
            'ativo': 'Ativo'
        }


class DisciplinaForm(forms.ModelForm):
    """Formulário para Disciplina - Atualizado com tipo e is_chave"""
    class Meta:
        model = Disciplina
        fields = ['nome', 'codigo', 'carga_horaria', 'classe', 'tipo', 'is_chave', 'descricao', 'ativo']  # 🔥 ADICIONADO tipo e is_chave
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'metal-form-control',
                'placeholder': 'Ex: Matemática'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'metal-form-control',
                'placeholder': 'Ex: MAT-001'
            }),
            'carga_horaria': forms.NumberInput(attrs={
                'class': 'metal-form-control',
                'placeholder': '60',
                'min': 1
            }),
            'classe': forms.Select(attrs={
                'class': 'metal-form-select'
            }),
            'tipo': forms.Select(attrs={  # 🔥 NOVO
                'class': 'metal-form-select'
            }),
            'is_chave': forms.CheckboxInput(attrs={  # 🔥 NOVO
                'class': 'form-check-input'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'metal-form-control',
                'rows': 3,
                'placeholder': 'Descrição da disciplina'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome': 'Nome da Disciplina',
            'codigo': 'Código',
            'carga_horaria': 'Carga Horária (horas)',
            'classe': 'Classe',
            'tipo': 'Tipo de Disciplina',  # 🔥 NOVO
            'is_chave': 'Disciplina Chave',  # 🔥 NOVO
            'descricao': 'Descrição',
            'ativo': 'Ativo'
        }


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