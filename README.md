# Yitro ERP - Sistema de Faturação AGT

Este projeto implementa a base do sistema ERP 'Yitro', focado em faturação certificada pela AGT (Angola), utilizando Python com Django e PostgreSQL. A arquitetura é modular, com um frontend moderno de "One-Page Application" e design Glassmorphism.

## 1. Pré-requisitos

Certifique-se de ter o Python 3.x e o pip instalados no seu sistema. É altamente recomendável usar um ambiente virtual.

## 2. Instalação das Dependências

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd yitro_erp
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate   # Windows
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## 3. Configuração do Ambiente

Crie um ficheiro `.env` na raiz do projeto (`yitro_erp/`) com as seguintes variáveis de ambiente:

```dotenv
SECRET_KEY='sua_chave_secreta_aqui' # Gerar uma chave segura para produção
DEBUG=True # Mudar para False em produção
ALLOWED_HOSTS='*' # Ex: .yitro.com, localhost, 127.0.0.1
DATABASE_URL='postgres://user:password@host:port/dbname' # Ex: postgres://yitro_user:yitro_pass@localhost:5432/yitro_db
```

**Nota sobre `SECRET_KEY`:** Em produção, esta chave deve ser um valor longo e aleatório, gerado de forma segura.

## 4. Configuração da Base de Dados (PostgreSQL)

O projeto está configurado para usar PostgreSQL em produção. Certifique-se de que o PostgreSQL está instalado e a correr. Crie uma base de dados e um utilizador para o projeto.

Exemplo de comandos para PostgreSQL (no terminal do PostgreSQL):

```sql
CREATE DATABASE yitro_db;
CREATE USER yitro_user WITH PASSWORD 'yitro_pass';
ALTER ROLE yitro_user SET client_encoding TO 'utf8';
ALTER ROLE yitro_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE yitro_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE yitro_db TO yitro_user;
```

Atualize a variável `DATABASE_URL` no seu ficheiro `.env` com as credenciais corretas.

## 5. Execução das Migrações

Após configurar o `.env` e a base de dados, execute as migrações para criar as tabelas no banco de dados:

```bash
python manage.py makemigrations autenticacao financeiro servicos clientes
python manage.py migrate
```

## 6. Criação do Superuser Inicial

Para aceder à área administrativa do Django, crie um superutilizador:

```bash
python manage.py createsuperuser
```

Siga as instruções no terminal para definir o nome de utilizador, email e palavra-passe.

## 7. Recolha de Ficheiros Estáticos

Para que os ficheiros estáticos (CSS, JS, imagens) sejam servidos corretamente em produção, execute:

```bash
python manage.py collectstatic
```

## 8. Executar o Servidor de Desenvolvimento

Para iniciar o servidor de desenvolvimento local:

```bash
python manage.py runserver
```

O sistema estará acessível em `http://127.0.0.1:8000/`.

## 9. Estrutura do Projeto

```
yitro_erp/
├── core/                 # Configurações do projeto Django
│   ├── settings.py       # Configurações otimizadas com variáveis de ambiente
│   └── urls.py           # URLs globais
├── autenticacao/         # Gestão de utilizadores (modelo customizado)
│   └── models.py
├── financeiro/           # Módulo AGT (Faturação)
│   ├── models.py         # Modelo Fatura e ItemFatura
│   ├── services.py       # Lógica de Hash AGT e sequenciação
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── servicos/             # Gestão de infraestrutura/marketing
│   ├── models.py         # Modelo Servico
│   ├── views.py          # Dashboard de serviços
│   └── urls.py
├── clientes/             # CRM (Gestão de Clientes)
│   └── models.py
├── templates/            # Templates HTML
│   └── base.html         # Template base com vídeo de fundo e Glassmorphism
│   └── servicos/dashboard.html
│   └── financeiro/lista_faturas.html
│   └── financeiro/form_fatura.html
├── static/               # Ficheiros estáticos (CSS, JS, Imagens)
│   ├── css/style.css
│   ├── img/logo.png      # Logótipo Yitro
│   └── video/            # Vídeo de fundo (se local)
├── media/                # Ficheiros de media (uploads)
├── .env.example          # Exemplo de ficheiro de variáveis de ambiente
├── manage.py             # Utilitário de linha de comando do Django
└── requirements.txt      # Dependências do projeto
```

## 10. Assinatura Digital AGT

A função `gerar_hash_agt` em `financeiro/services.py` é responsável por gerar o hash de controlo digitalmente assinado, essencial para a conformidade com as normas da AGT. Para o ambiente de produção, será necessário configurar uma chave privada segura para a assinatura digital das faturas. Esta chave deve ser gerada e armazenada de forma segura, e o caminho para ela ou a própria chave (se for pequena e encriptada) deve ser passado para a função de serviço.

---

**Desenvolvido por Manus AI**
