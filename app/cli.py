from flask import current_app
from flask.cli import with_appcontext
import click
from werkzeug.security import generate_password_hash
from sqlalchemy import select
from app.extensions import db
from app.models import Usuario, Restaurante, HorarioFuncionamentoRestaurante, CategoriaPrato, Prato, EnderecoCliente
from app.models.enums import TipoUsuario


def register_cli(app):
    @app.cli.command("seed")
    @with_appcontext
    def seed():
        click.echo("Seeding base data...")
        # categorias
        categorias = ["Entradas", "Massas", "Sobremesas", "Bebidas"]
        for c in categorias:
            if not db.session.execute(select(CategoriaPrato).where(CategoriaPrato.nome_categoria == c)).scalar():
                db.session.add(CategoriaPrato(nome_categoria=c))
        db.session.commit()

        # owner
        owner = db.session.execute(select(Usuario).where(Usuario.email == "owner@kifome.test")).scalar()
        if not owner:
            owner = Usuario(
                nome_completo="Dono Exemplo",
                email="owner@kifome.test",
                telefone="11999999999",
                senha_hash=generate_password_hash("owner123"),
                tipo=TipoUsuario.RESTAURANTE_OWNER.value,
            )
            db.session.add(owner)
            db.session.commit()

        # restaurante
        rest = db.session.execute(select(Restaurante).where(Restaurante.owner_id == owner.id)).scalar()
        if not rest:
            rest = Restaurante(
                owner_id=owner.id,
                nome="KiFome Trattoria",
                endereco="Rua das Flores, 100",
                telefone="1133334444",
                tipo_culinaria="Italiana",
            )
            db.session.add(rest)
            db.session.commit()

        # horários (segunda a domingo 11:00-22:00)
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        for d in dias:
            if not db.session.execute(select(HorarioFuncionamentoRestaurante).where(HorarioFuncionamentoRestaurante.restaurante_id == rest.id, HorarioFuncionamentoRestaurante.dia_semana == d)).scalar():
                db.session.add(HorarioFuncionamentoRestaurante(restaurante_id=rest.id, dia_semana=d, horario_abertura="11:00:00", horario_fechamento="22:00:00"))
        db.session.commit()

        # cliente
        cliente = db.session.execute(select(Usuario).where(Usuario.email == "cliente@kifome.test")).scalar()
        if not cliente:
            cliente = Usuario(
                nome_completo="Cliente Exemplo",
                email="cliente@kifome.test",
                telefone="1188887777",
                senha_hash=generate_password_hash("cliente123"),
                tipo=TipoUsuario.CLIENTE.value,
            )
            db.session.add(cliente)
            db.session.commit()
            db.session.add(EnderecoCliente(
                cliente_id=cliente.id,
                apelido="Casa",
                logradouro="Av. Brasil",
                numero="200",
                bairro="Centro",
                cidade="São Paulo",
                uf="SP",
                cep="01000-000",
            ))
            db.session.commit()

        # pratos
        cat_map = {c.nome_categoria: c for c in db.session.execute(select(CategoriaPrato)).scalars().all()}
        pratos = [
            ("Entradas", "Bruschetta", "Pão italiano com tomate e manjericão", 18.00, 20),
            ("Massas", "Spaghetti Carbonara", "Clássico com pancetta e parmesão", 42.00, 15),
            ("Massas", "Fetuccine Alfredo", "Molho cremoso de queijo", 39.90, 10),
            ("Sobremesas", "Tiramisù", "Tradicional italiano", 24.00, 12),
            ("Bebidas", "Refrigerante", "Lata 350ml", 7.00, 50),
            ("Bebidas", "Água", "Sem gás 500ml", 5.50, 50),
            ("Entradas", "Caprese", "Mussarela de búfala, tomate, manjericão", 22.00, 10),
            ("Sobremesas", "Panna Cotta", "Com calda de frutas vermelhas", 21.00, 8),
        ]
        for cat, nome, desc, preco, est in pratos:
            exists = db.session.execute(select(Prato).where(Prato.restaurante_id == rest.id, Prato.nome == nome)).scalar()
            if not exists:
                db.session.add(Prato(restaurante_id=rest.id, categoria_id=cat_map[cat].id, nome=nome, descricao=desc, preco=preco, estoque=est, disponivel=True))
        db.session.commit()
        click.echo("Seed concluído.")

