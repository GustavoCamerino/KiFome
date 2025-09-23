# KiFome — Plataforma de Delivery (Django + MySQL)

KiFome é uma plataforma web de delivery com cadastro de clientes e restaurantes, vitrine de pratos, carrinho com checkout simulado e acompanhamento de pedidos.

- Backend: Django (Python)
- Banco: MySQL (via Django ORM). Para facilitar o start local, há fallback para SQLite se variáveis de ambiente do MySQL não forem definidas.
- Frontend: HTML, CSS e JavaScript simples

## Rodando localmente

1) Crie e ative um virtualenv (opcional, mas recomendado)

- Windows (PowerShell):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instale dependências
```
pip install -r requirements.txt
```

3) Configure o banco de dados

Defina variáveis de ambiente para MySQL (recomendado):
- `MYSQL_NAME` (ex: `kifome`)
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_HOST` (ex: `localhost`)
- `MYSQL_PORT` (ex: `3306`)

Se essas variáveis não forem definidas, o projeto usa SQLite automaticamente para facilitar o start local.

4) Aplique migrações
```
python manage.py migrate
```

5) Crie um superusuário (opcional, para acessar o admin)
```
python manage.py createsuperuser
```

6) Rode o servidor de desenvolvimento
```
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

## Banco de Dados (MySQL): comandos completos

Você pode usar os scripts prontos em `scripts/` ou executar os comandos abaixo manualmente.

- Criar banco e usuário (no cliente MySQL):
```
-- conecte como root/admin (ex: mysql -u root -p)
CREATE DATABASE IF NOT EXISTS kifome CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'kifome_user'@'localhost' IDENTIFIED BY 'SUA_SENHA_AQUI';
GRANT ALL PRIVILEGES ON kifome.* TO 'kifome_user'@'localhost';
FLUSH PRIVILEGES;
```

- Variáveis de ambiente (escolha seu shell):
  - PowerShell (Windows):
```
$env:MYSQL_NAME="kifome"
$env:MYSQL_USER="kifome_user"
$env:MYSQL_PASSWORD="SUA_SENHA_AQUI"
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
```
  - CMD (Windows):
```
set MYSQL_NAME=kifome
set MYSQL_USER=kifome_user
set MYSQL_PASSWORD=SUA_SENHA_AQUI
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
```
  - Bash (Linux/macOS):
```
export MYSQL_NAME=kifome
export MYSQL_USER=kifome_user
export MYSQL_PASSWORD=SUA_SENHA_AQUI
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
```

- Aplicar migrações e iniciar:
```
python manage.py migrate
python manage.py createsuperuser  # opcional
python manage.py runserver
```

- Testar conexão via Django (opcional; requer `mysql` no PATH):
```
python manage.py dbshell
```

### Scripts prontos
- SQL de criação de BD/usuário: `scripts/mysql_init.sql`
  - Uso: `mysql -u root -p < scripts/mysql_init.sql`
- Variáveis (PowerShell): `scripts/env_mysql.ps1`
  - Uso: `.\scripts\env_mysql.ps1`
- Variáveis (Bash): `scripts/env_mysql.sh`
  - Uso: `source scripts/env_mysql.sh`

## Estrutura de apps
- `clientes` — cadastro/login de clientes, perfis e histórico
- `restaurantes` — cadastro/login de restaurantes, gestão de pratos e horários
- `pedidos` — carrinho, criação de pedidos, checkout simulado e acompanhamento de status
- `avaliacoes` — avaliações de restaurantes (nota 0–5 e feedback)

## Funcionalidades principais
- Listagem de restaurantes e página de restaurante com menu por categorias
- Cadastro/login de clientes e restaurantes
- Carrinho (sessão) e checkout simulado (sem gateway real)
- Acompanhamento do pedido com fluxo dummy: preparação → trânsito → entregue
- Admin do Django habilitado para gerenciar dados

## Observações
- Não há entregadores. O sistema apenas registra a venda e calcula comissão de 3% por pedido concluído (propriedade em `Pedido`).
- Sem dados fake; a estrutura inicial está pronta para uso.
- Código simples, organizado e documentado no necessário.

## Notas de desenvolvimento
- Arquivos estáticos em `static/` e templates em `templates/`.
- Ajuste `DEBUG`, `ALLOWED_HOSTS` e banco de dados via variáveis de ambiente conforme necessário.
