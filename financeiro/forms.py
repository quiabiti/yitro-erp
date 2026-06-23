# financeiro/forms.py

from django import forms
from django.utils import timezone
from .models import Fatura, Produto, ItemFatura
from clientes.models import Cliente  # 🔥 IMPORTAR DO APP CLIENTES


class FaturaForm(forms.ModelForm):
    """Formulário para criação/edição de faturas"""
    
    class Meta:
        model = Fatura
        fields = ['cliente', 'data_emissao', 'data_vencimento', 'status', 'observacoes']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'metal-form-select'}),
            'data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'metal-form-control'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'metal-form-control'}),
            'status': forms.Select(attrs={'class': 'metal-form-select'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'metal-form-control'}),
        }
        labels = {
            'cliente': 'Cliente',
            'data_emissao': 'Data de Emissão',
            'data_vencimento': 'Data de Vencimento',
            'status': 'Status',
            'observacoes': 'Observações',
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar clientes por empresa
        if self.empresa:
            self.fields['cliente'].queryset = Cliente.objects.filter(empresa=self.empresa, ativo=True)
        elif self.request and self.request.user.is_superuser:
            self.fields['cliente'].queryset = Cliente.objects.filter(ativo=True)


class ClienteForm(forms.ModelForm):
    """Formulário para criação/edição de clientes"""
    
    class Meta:
        model = Cliente
        fields = ['nome', 'nif', 'endereco', 'telefone', 'email', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'metal-form-control'}),
            'nif': forms.TextInput(attrs={'class': 'metal-form-control'}),
            'endereco': forms.Textarea(attrs={'rows': 3, 'class': 'metal-form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'metal-form-control'}),
            'email': forms.EmailInput(attrs={'class': 'metal-form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'metal-form-check-input'}),
        }
        labels = {
            'nome': 'Nome do Cliente',
            'nif': 'NIF',
            'endereco': 'Endereço',
            'telefone': 'Telefone',
            'email': 'Email',
            'ativo': 'Ativo',
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)


class ProdutoForm(forms.ModelForm):
    """Formulário para criação/edição de produtos"""
    
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'codigo', 'preco', 'iva', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'metal-form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'metal-form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'metal-form-control'}),
            'preco': forms.NumberInput(attrs={'class': 'metal-form-control', 'step': '0.01'}),
            'iva': forms.NumberInput(attrs={'class': 'metal-form-control', 'step': '0.01'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'metal-form-check-input'}),
        }
        labels = {
            'nome': 'Nome do Produto/Serviço',
            'descricao': 'Descrição',
            'codigo': 'Código',
            'preco': 'Preço Unitário (Kz)',
            'iva': 'IVA (%)',
            'ativo': 'Ativo',
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar produtos por empresa
        if self.empresa:
            self.fields['produto'].queryset = Produto.objects.filter(empresa=self.empresa, ativo=True)


class ItemFaturaForm(forms.ModelForm):
    """Formulário para itens da fatura"""
    
    class Meta:
        model = ItemFatura
        fields = ['produto', 'descricao', 'quantidade', 'preco_unitario']
        widgets = {
            'produto': forms.Select(attrs={'class': 'metal-form-select'}),
            'descricao': forms.TextInput(attrs={'class': 'metal-form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'metal-form-control', 'step': '0.01', 'min': '0.01'}),
            'preco_unitario': forms.NumberInput(attrs={'class': 'metal-form-control', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'produto': 'Produto/Serviço',
            'descricao': 'Descrição',
            'quantidade': 'Quantidade',
            'preco_unitario': 'Preço Unitário (Kz)',
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.empresa = kwargs.pop('empresa', None)
        self.fatura = kwargs.pop('fatura', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar produtos por empresa
        if self.empresa:
            self.fields['produto'].queryset = Produto.objects.filter(empresa=self.empresa, ativo=True)
        elif self.request and self.request.user.is_superuser:
            self.fields['produto'].queryset = Produto.objects.filter(ativo=True)