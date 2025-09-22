from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import Usuario, Restaurante, CategoriaPrato, Prato
from app.models.enums import TipoUsuario


def login(client, email, senha):
    return client.post('/auth/login', data={'email': email, 'senha': senha}, follow_redirects=True)


def test_block_add_when_indisponivel(app, client):
    with app.app_context():
        c = Usuario(nome_completo='C', email='c@c', telefone='1', senha_hash=generate_password_hash('x'), tipo=TipoUsuario.CLIENTE.value)
        db.session.add(c); db.session.commit()
        o = Usuario(nome_completo='O', email='o@o', telefone='1', senha_hash=generate_password_hash('x'), tipo=TipoUsuario.RESTAURANTE_OWNER.value)
        db.session.add(o); db.session.commit()
        r = Restaurante(owner_id=o.id, nome='R', endereco='e', telefone='t', tipo_culinaria='x')
        db.session.add(r); db.session.commit()
        cat = CategoriaPrato(nome_categoria='Cat')
        db.session.add(cat); db.session.commit()
        p = Prato(restaurante_id=r.id, categoria_id=cat.id, nome='P', descricao='d', preco=10, estoque=0, disponivel=True)
        db.session.add(p); db.session.commit()

    login(client, 'c@c', 'x')
    resp = client.post('/carrinho/add', json={'prato_id': p.id, 'quantidade': 1})
    assert resp.status_code == 400


def test_owner_cannot_edit_other_restaurant(app, client):
    with app.app_context():
        o1 = Usuario(nome_completo='O1', email='o1@o', telefone='1', senha_hash=generate_password_hash('x'), tipo=TipoUsuario.RESTAURANTE_OWNER.value)
        o2 = Usuario(nome_completo='O2', email='o2@o', telefone='1', senha_hash=generate_password_hash('x'), tipo=TipoUsuario.RESTAURANTE_OWNER.value)
        db.session.add_all([o1, o2]); db.session.commit()
        r1 = Restaurante(owner_id=o1.id, nome='R1', endereco='e', telefone='t', tipo_culinaria='x')
        db.session.add(r1); db.session.commit()

    login(client, 'o2@o', 'x')
    resp = client.get(f'/restaurante/pratos/{r1.id}/edit')
    assert resp.status_code in (302, 403)

