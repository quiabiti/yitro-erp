#!/bin/bash
echo "🚀 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Executando migrações..."
# Criar migrações para TODAS as apps
python manage.py makemigrations core --noinput || true
python manage.py makemigrations autenticacao --noinput || true
python manage.py makemigrations financeiro --noinput || true
python manage.py makemigrations servicos --noinput || true
python manage.py makemigrations clientes --noinput || true
python manage.py makemigrations escola --noinput || true
python manage.py makemigrations escola.configuracao --noinput || true
python manage.py makemigrations escola.secretaria --noinput || true
python manage.py makemigrations escola.pedagogico --noinput || true
python manage.py makemigrations escola.docente --noinput || true
python manage.py makemigrations escola.administrativo --noinput || true

# Executar todas as migrações
python manage.py migrate --noinput

echo "🚀 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Build concluído!"