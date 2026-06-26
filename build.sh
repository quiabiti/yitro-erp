#!/bin/bash
echo "🚀 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Executando migrações..."
# Primeiro, criar migrações para todas as apps personalizadas
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

# Depois, executar todas as migrações
python manage.py migrate --noinput

# Verificar se as tabelas existem antes de criar superusuário
echo "🚀 Verificando se a tabela autenticacao_usuario existe..."
if python manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='autenticacao_usuario'\"); print(cursor.fetchone())" | grep -q "autenticacao_usuario"; then
    echo "✅ Tabela autenticacao_usuario encontrada. Criando superusuário..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')
    print('✅ Superusuário admin criado com sucesso!')
else:
    print('ℹ️ Superusuário admin já existe.')
"
else
    echo "⚠️ Tabela autenticacao_usuario não encontrada. Pulando criação de superusuário."
fi

echo "🚀 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Build concluído!"