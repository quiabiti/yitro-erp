# escola/secretaria/forms.py

from django import forms
from .models import Aluno, Matricula, HistoricoAluno
from escola.pedagogico.models import Classe, Turma, AnoLectivo


class AlunoForm(forms.ModelForm):
    """Formulário para Aluno"""
    
    class Meta:
        model = Aluno
        fields = [
            'nome_completo', 'data_nascimento', 'genero', 'naturalidade',
            'nacionalidade', 'bi', 'nif', 'data_emissao_bi', 'data_validade_bi',
            'email', 'telefone', 'endereco',
            'nome_pai', 'nome_mae', 'telefone_responsavel', 'email_responsavel',
            'observacoes', 'ativo'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'metal-form-control'}),
            'data_emissao_bi': forms.DateInput(attrs={'type': 'date', 'class': 'metal-form-control'}),
            'data_validade_bi': forms.DateInput(attrs={'type': 'date', 'class': 'metal-form-control'}),
            'nome_completo': forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Nome completo do aluno'}),
            'bi': forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Ex: 001-123456-AA'}),
            'nif': forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Ex: 5001234567'}),
            'naturalidade': forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Ex: Luanda'}),
            'nacionalidade': forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Angola'}),
            'telefone': forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Ex: 923456789'}),
            'email': forms.EmailInput(attrs={'class': 'metal-form-control', 'placeholder': 'aluno@email.com'}),
            'endereco': forms.Textarea(attrs={'class': 'metal-form-control', 'rows': 2, 'placeholder': 'Endereço completo'}),
            'nome_pai': forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Nome do pai'}),
            'nome_mae': forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Nome da mãe'}),
            'telefone_responsavel': forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Ex: 934567890'}),
            'email_responsavel': forms.EmailInput(attrs={'class': 'metal-form-control', 'placeholder': 'responsavel@email.com'}),
            'genero': forms.Select(attrs={'class': 'metal-form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'metal-form-control', 'rows': 2, 'placeholder': 'Observações sobre o aluno'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome_completo': 'Nome Completo',
            'data_nascimento': 'Data de Nascimento',
            'genero': 'Gênero',
            'naturalidade': 'Naturalidade',
            'nacionalidade': 'Nacionalidade',
            'bi': 'BI',
            'nif': 'NIF',
            'data_emissao_bi': 'Data de Emissão do BI',
            'data_validade_bi': 'Data de Validade do BI',
            'telefone': 'Telefone',
            'email': 'E-mail',
            'endereco': 'Endereço',
            'nome_pai': 'Nome do Pai',
            'nome_mae': 'Nome da Mãe',
            'telefone_responsavel': 'Telefone do Responsável',
            'email_responsavel': 'E-mail do Responsável',
            'observacoes': 'Observações',
            'ativo': 'Ativo',
        }


class MatriculaForm(forms.ModelForm):
    """Formulário para Matrícula"""
    
    class Meta:
        model = Matricula
        fields = [
            'aluno', 'ano_lectivo', 'classe', 'turma',
            'tipo', 'status', 'observacoes', 'ativo'
        ]
        widgets = {
            'aluno': forms.Select(attrs={'class': 'metal-form-control'}),
            'ano_lectivo': forms.Select(attrs={'class': 'metal-form-control'}),
            'classe': forms.Select(attrs={'class': 'metal-form-control'}),
            'turma': forms.Select(attrs={'class': 'metal-form-control'}),
            'tipo': forms.Select(attrs={'class': 'metal-form-control'}),
            'status': forms.Select(attrs={'class': 'metal-form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'metal-form-control', 'rows': 2, 'placeholder': 'Observações sobre a matrícula'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'aluno': 'Aluno',
            'ano_lectivo': 'Ano Lectivo',
            'classe': 'Classe',
            'turma': 'Turma',
            'tipo': 'Tipo de Matrícula',
            'status': 'Status',
            'observacoes': 'Observações',
            'ativo': 'Ativo',
        }


class MatriculaComAlunoForm(forms.Form):
    """Formulário combinado: Aluno + Matrícula"""
    
    # Dados do Aluno
    aluno_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    nome_completo = forms.CharField(
        label='Nome Completo',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Nome completo do aluno'})
    )
    data_nascimento = forms.DateField(
        label='Data de Nascimento',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'metal-form-control'})
    )
    genero = forms.ChoiceField(
        label='Gênero',
        choices=[('M', 'Masculino'), ('F', 'Feminino')],
        widget=forms.Select(attrs={'class': 'metal-form-control'})
    )
    bi = forms.CharField(
        label='BI',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Ex: 001-123456-AA'})
    )
    nif = forms.CharField(
        label='NIF',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Ex: 5001234567'})
    )
    naturalidade = forms.CharField(
        label='Naturalidade',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Ex: Luanda'})
    )
    nacionalidade = forms.CharField(
        label='Nacionalidade',
        max_length=50,
        initial='Angola',
        widget=forms.TextInput(attrs={'class': 'metal-form-control'})
    )
    telefone = forms.CharField(
        label='Telefone',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Ex: 923456789'})
    )
    email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'metal-form-control', 'placeholder': 'aluno@email.com'})
    )
    endereco = forms.CharField(
        label='Endereço',
        required=False,
        widget=forms.Textarea(attrs={'class': 'metal-form-control', 'rows': 2, 'placeholder': 'Endereço completo'})
    )
    nome_pai = forms.CharField(
        label='Nome do Pai',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Nome do pai'})
    )
    nome_mae = forms.CharField(
        label='Nome da Mãe',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Nome da mãe'})
    )
    telefone_responsavel = forms.CharField(
        label='Telefone do Responsável',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'metal-form-control', 'placeholder': 'Ex: 934567890'})
    )
    email_responsavel = forms.EmailField(
        label='E-mail do Responsável',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'metal-form-control', 'placeholder': 'responsavel@email.com'})
    )
    
    # Dados da Matrícula
    tipo = forms.ChoiceField(
        label='Tipo de Matrícula',
        choices=Matricula.TIPO_CHOICES,
        initial='nova',
        widget=forms.Select(attrs={'class': 'metal-form-control'})
    )
    ano_lectivo = forms.ModelChoiceField(
        label='Ano Lectivo',
        queryset=AnoLectivo.objects.none(),
        widget=forms.Select(attrs={'class': 'metal-form-control'})
    )
    classe = forms.ModelChoiceField(
        label='Classe',
        queryset=Classe.objects.none(),
        widget=forms.Select(attrs={'class': 'metal-form-control'})
    )
    turma = forms.ModelChoiceField(
        label='Turma',
        queryset=Turma.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'metal-form-control'})
    )
    status = forms.ChoiceField(
        label='Status',
        choices=Matricula.STATUS_CHOICES,
        initial='pendente',
        widget=forms.Select(attrs={'class': 'metal-form-control'})
    )
    observacoes = forms.CharField(
        label='Observações',
        required=False,
        widget=forms.Textarea(attrs={'class': 'metal-form-control', 'rows': 2, 'placeholder': 'Observações sobre a matrícula'})
    )
    
    def __init__(self, *args, **kwargs):
        tenant_id = kwargs.pop('tenant_id', None)
        super().__init__(*args, **kwargs)
        
        if tenant_id:
            self.fields['ano_lectivo'].queryset = AnoLectivo.objects.filter(tenant_id=tenant_id, ativo=True)
            self.fields['classe'].queryset = Classe.objects.filter(tenant_id=tenant_id, ativo=True)
            self.fields['turma'].queryset = Turma.objects.filter(tenant_id=tenant_id, ativo=True)