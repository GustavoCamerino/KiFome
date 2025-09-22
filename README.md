KiFome — Plataforma de Delivery (Flask + PostgreSQL)

Visão geral
- Web app completo com Flask 3.x, SQLAlchemy 2.x, Alembic, PostgreSQL e HTML/CSS/JS (vanilla).
- Duas áreas no mesmo app: Cliente e Restaurante (owner).
- Pagamento simulado (dummy): apenas muda status e registra forma “Simulado”.

Requisitos
- Python 3.11+
- PostgreSQL 13+

Stack e pacotes
- Flask, Flask-Login, Flask-Migrate (Alembic), SQLAlchemy, psycopg2-binary, python-dotenv

Configuração
1) Clone o projeto e crie o ambiente virtual
   - `python -m venv .venv`
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

2) Instale as dependências
   - `pip install -r requirements.txt`

3) Configure variáveis de ambiente
   - Copie `.env.example` para `.env` e ajuste `DATABASE_URL` e `SECRET_KEY`.
   - Exemplo: `DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/kifome`

4) Crie o banco no Postgres
   - `createdb kifome` (ou via GUI/CLI de sua preferência)

5) Migrações Alembic
   - `alembic upgrade head` (usa `alembic.ini` com `DATABASE_URL`)
   - Alternativa (com Flask-Migrate): `flask db upgrade`

6) (Opcional) Dados de seed
   - `flask seed` cria 1 owner + restaurante + horários, 4 categorias e ~8 pratos, 1 cliente + endereço.

7) Executar
   - `flask run`
   - App em `http://127.0.0.1:5000`

Estrutura de pastas
- `app.py` create_app(), registro de blueprints e CLI.
- `config.py` carrega `.env` (DATABASE_URL, SECRET_KEY).
- `app/` models, services, routes, templates, static.
- `migrations/` Alembic com migração inicial.
- `tests/` testes mínimos (serviços e rotas).

Modelagem (principal)
- Usuários (clientes e owners), Endereços, Restaurantes, Horários, Categorias, Pratos (com estoque e disponibilidade), Avaliações, Pedidos e Itens.
- Tipos e constraints: BIGSERIAL, NUMERIC(10,2), timestamptz, CHECKs e índices conforme enunciado.

Blueprints
- Público: `/`, `/restaurantes/<id>`
- Auth: `/auth/register`, `/auth/login`, `/auth/logout`
- Cliente: dashboard, endereços, carrinho, checkout, pedidos
- Restaurante: dashboard, meu restaurante, horários, categorias, pratos, pedidos, relatórios

Regras de negócio
- Carrinho em sessão (um restaurante por pedido).
- Valida estoque e disponibilidade ao adicionar/atualizar.
- Totais: subtotal + taxa empresa (3%) = total.
- Checkout “Simulado” cria pedido, debita estoque e limpa carrinho.
- Fluxo de status: preparacao → transito → entregue; cancelamento só em preparacao.
- “Aberto agora” baseado na tabela de horários.

Testes
- `pytest`
- Cobre: cálculo de totais; estoque não negativo; rota bloqueia adicionar item indisponível; owner não edita restaurante alheio.

Usuários de seed
- Owner: `owner@kifome.test` / `owner123`
- Cliente: `cliente@kifome.test` / `cliente123`

Observações
- Este projeto usa Enums com `native_enum=False` para compatibilidade com SQLite em testes.
- Para produção Postgres, `alembic upgrade head` aplica os tipos nomeados.

"# kifome" 
