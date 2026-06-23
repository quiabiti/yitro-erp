import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
import base64
from datetime import datetime

def gerar_hash_agt(fatura_dados, chave_privada_pem):
    """
    Gera o Hash de controlo para a fatura conforme normas da AGT.
    O hash é baseado na data, número da fatura, total bruto e o hash da fatura anterior.
    """
    # Carregar chave privada
    private_key = serialization.load_pem_private_key(
        chave_privada_pem.encode(),
        password=None,
    )

    # String para assinar: Data;DataHora;NumeroFatura;TotalBruto;HashAnterior
    # Exemplo simplificado para a estrutura base
    string_para_assinar = f"{fatura_dados['data']};{fatura_dados['data_hora']};{fatura_dados['numero']};{fatura_dados['total_bruto']};{fatura_dados.get('hash_anterior', '')}"
    
    assinatura = private_key.sign(
        string_para_assinar.encode(),
        padding.PKCS1v15(),
        hashes.SHA1()
    )
    
    return base64.b64encode(assinatura).decode()

def gerar_proximo_numero_fatura(ano=None):
    from .models import Fatura
    if not ano:
        ano = datetime.now().year
    
    ultima_fatura = Fatura.objects.filter(numero__contains=f"/{ano}").order_by('-id').first()
    
    if not ultima_fatura:
        sequencia = 1
    else:
        # Extrair número da string FT 2024/1
        try:
            sequencia = int(ultima_fatura.numero.split('/')[-1]) + 1
        except:
            sequencia = 1
            
    return f"FT {ano}/{sequencia}"
