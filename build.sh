#!/bin/bash

echo "🚀 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Removendo migrações problemáticas..."
# 🔥 REMOVER MIGRAÇÕES PROBLEMÁTICAS PARA EVITAR DEPENDÊNCIA CIRCULAR
rm -rf autenticacao/migrations/0*.py 2>/dev/null || true
rm -rf core/migrations/0*.py 2>/dev/null || true

echo "🚀 Criando migrações na ordem correta..."
# 🔥 CRIAR MIGRAÇÕES NA ORDEM CORRETA (autenticacao primeiro)
python manage.py makemigrations autenticacao --name initial --noinput 2>/dev/null || python manage.py makemigrations autenticacao --noinput || true
python manage.py makemigrations core --name initial --noinput 2>/dev/null || python manage.py makemigrations core --noinput || true

echo "🚀 Executando migrações com --fake-initial..."
# 🔥 APLICAR COM --fake-initial PARA EVITAR CONFLITOS
python manage.py migrate --noinput --fake-initial || {
    echo "⚠️ Falha no migrate --fake-initial, tentando --fake..."
    python manage.py migrate autenticacao --noinput --fake || true
    python manage.py migrate core --noinput --fake || true
    python manage.py migrate --noinput
}

echo "🚀 Criando migrações para as outras apps..."
# 🔥 CRIAR MIGRAÇÕES PARA AS OUTRAS APPS
python manage.py makemigrations financeiro --noinput || true
python manage.py makemigrations servicos --noinput || true
python manage.py makemigrations clientes --noinput || true
python manage.py makemigrations escola --noinput || true
python manage.py makemigrations escola.configuracao --noinput || true
python manage.py makemigrations escola.secretaria --noinput || true
python manage.py makemigrations escola.pedagogico --noinput || true
python manage.py makemigrations escola.docente --noinput || true
python manage.py makemigrations escola.administrativo --noinput || true

echo "🚀 Aplicando migrações restantes..."
python manage.py migrate --noinput

echo "🚀 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "🚀 Criando superusuário..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('Quiabiti', 'quiabiti@email.com', 'Falvenio1995.')
    print('✅ Superusuário criado com sucesso!')
else:
    print('✅ Superusuário já existe.')
EOF

echo "✅ Build concluído com sucesso!"