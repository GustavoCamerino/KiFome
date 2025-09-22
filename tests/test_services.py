import pytest
from decimal import Decimal
from app.services.pedidos import calcular_totais, debitar_estoque
from app.models.dish import Prato
from app.extensions import db
from app.models.restaurant import Restaurante
from app.models.user import Usuario
from app.models.enums import TipoUsuario


def test_calcular_totais():
    items = [
        {"preco": 10.00, "quantidade": 2},
        {"preco": 5.50, "quantidade": 1},
    ]
    subtotal, taxa, total = calcular_totais(items)
    assert subtotal == Decimal("25.50")
    assert taxa == Decimal("0.77")
    assert total == Decimal("26.27")


def test_estoque_nao_negativo(app):
    with app.app_context():
        u = Usuario(nome_completo="o", email="o@o", telefone="1", senha_hash="x", tipo=TipoUsuario.RESTAURANTE_OWNER.value)
        db.session.add(u); db.session.commit()
        r = Restaurante(owner_id=u.id, nome="R", endereco="e", telefone="t", tipo_culinaria="x")
        db.session.add(r); db.session.commit()
        p = Prato(restaurante_id=r.id, categoria_id=1, nome="X", descricao="D", preco=10, estoque=1, disponivel=True)
        db.session.add(p); db.session.commit()
        with pytest.raises(ValueError):
            debitar_estoque([{"prato_id": p.id, "quantidade": 2, "preco": 10}])

