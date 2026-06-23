# clientes/forms.py

from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
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
            'nome': 'Nome',
            'nif': 'NIF',
            'endereco': 'Endereço',
            'telefone': 'Telefone',
            'email': 'Email',
            'ativo': 'Ativo',
        }