# servicos/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Item, ContratoServico, OrdemServico, LancamentoHoras, FaturamentoRecorrente

User = get_user_model()

class ItemForm(forms.ModelForm):
    """Formulário para criar/editar itens"""
    
    class Meta:
        model = Item
        fields = [
            'codigo', 'nome', 'descricao', 'tipo', 'status',
            'imagem',  # 🔥 ADICIONADO
            'preco_venda', 'preco_custo', 'recorrencia', 'duracao_padrao',
            'horas_estimadas', 'preco_hora', 'nivel_prioridade',
            'requer_visita', 'requer_equipamento', 'tempo_medio_execucao',
            'requer_ativacao', 'numero_usuarios_incluidos', 'permite_upgrade',
            'peso', 'dimensoes', 'codigo_barras', 'unidade_medida'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'imagem': forms.FileInput(attrs={'accept': 'image/*'}),  # 🔥 ADICIONADO
            'duracao_padrao': forms.NumberInput(attrs={'min': 1}),
            'horas_estimadas': forms.NumberInput(attrs={'step': '0.5', 'min': 0}),
            'preco_venda': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'preco_custo': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'preco_hora': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'peso': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'tempo_medio_execucao': forms.TextInput(attrs={'placeholder': 'HH:MM:SS'}),
        }
    
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if Item.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Já existe um item com este código.')
        return codigo
    
    def clean_preco_venda(self):
        preco = self.cleaned_data.get('preco_venda')
        if preco <= 0:
            raise forms.ValidationError('O preço de venda deve ser maior que zero.')
        return preco


class ContratoServicoForm(forms.ModelForm):
    """Formulário para criar/editar contratos"""
    
    cliente = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label='Cliente'
    )
    servico = forms.ModelChoiceField(
        queryset=Item.objects.filter(status='ativo'),
        label='Serviço'
    )
    
    class Meta:
        model = ContratoServico
        fields = [
            'cliente', 'servico', 'data_inicio', 'data_fim',
            'preco_acordado', 'desconto', 'valor_total',
            'renovacao_automatica', 'horas_contratadas'
        ]
        widgets = {
            'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'data_fim': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'preco_acordado': forms.NumberInput(attrs={'step': '0.01'}),
            'desconto': forms.NumberInput(attrs={'step': '0.01', 'min': 0, 'max': 100}),
            'valor_total': forms.NumberInput(attrs={'step': '0.01'}),
            'horas_contratadas': forms.NumberInput(attrs={'step': '0.5', 'min': 0}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        if data_inicio and data_fim and data_fim <= data_inicio:
            raise forms.ValidationError('A data de fim deve ser posterior à data de início.')
        
        return cleaned_data


class OrdemServicoForm(forms.ModelForm):
    """Formulário para criar/editar ordens de serviço"""
    
    class Meta:
        model = OrdemServico
        fields = [
            'contrato', 'cliente', 'titulo', 'descricao',
            'prioridade', 'prazo', 'horas_estimadas', 'responsavel'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'prazo': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'horas_estimadas': forms.NumberInput(attrs={'step': '0.5', 'min': 0}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contrato'].queryset = ContratoServico.objects.filter(status='ativo')
        self.fields['cliente'].queryset = User.objects.filter(is_active=True)
        self.fields['responsavel'].queryset = User.objects.filter(is_active=True)


class LancamentoHorasForm(forms.ModelForm):
    """Formulário para lançamento de horas"""
    
    class Meta:
        model = LancamentoHoras
        fields = ['ordem', 'funcionario', 'data', 'horas', 'descricao']
        widgets = {
            'data': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'horas': forms.NumberInput(attrs={'step': '0.5', 'min': 0.5, 'max': 24}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        horas = cleaned_data.get('horas')
        ordem = cleaned_data.get('ordem')
        
        if horas and ordem and ordem.contrato.horas_restantes:
            if horas > ordem.contrato.horas_restantes:
                raise forms.ValidationError(
                    f'Horas insuficientes no contrato. Disponível: {ordem.contrato.horas_restantes}h'
                )
        
        return cleaned_data


class FaturamentoRecorrenteForm(forms.ModelForm):
    """Formulário para faturamento recorrente"""
    
    class Meta:
        model = FaturamentoRecorrente
        fields = [
            'contrato', 'cliente', 'servico', 'frequencia',
            'valor', 'dia_cobranca', 'status', 'proxima_cobranca'
        ]
        widgets = {
            'proxima_cobranca': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valor': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'dia_cobranca': forms.NumberInput(attrs={'min': 1, 'max': 31}),
        }