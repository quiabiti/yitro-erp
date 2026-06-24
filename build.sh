#!/bin/bash
echo "🚀 Instalando dependências..."
pip install -r requirements.txt

echo "🚀 Executando migrações..."
python manage.py migrate --noinput

echo "🚀 Criando superusuário..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')
"

echo "🚀 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "🚀 Verificando vídeo..."
ls -la static/videos/ || echo "Vídeo não encontrado!"
ls -la staticfiles/videos/ || echo "Vídeo não copiado!"

echo "✅ Build concluído!"