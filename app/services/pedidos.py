from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.dish import Prato
from app.models.order import Pedido, ItemPedido
from app.models.enums import StatusPedido


TAXA = Decimal("0.03")


def _to_money(value: Decimal | float | int) -> Decimal:
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_totais(items: Sequence[dict]) -> tuple[Decimal, Decimal, Decimal]:
    subtotal = Decimal("0.00")
    for it in items:
        subtotal += _to_money(it["preco"]) * int(it["quantidade"])
    subtotal = _to_money(subtotal)
    taxa = _to_money(subtotal * TAXA)
    total = _to_money(subtotal + taxa)
    return subtotal, taxa, total


def validar_disponibilidade(prato: Prato, quantidade: int) -> None:
    if not prato.disponivel:
        raise ValueError("Prato indisponível")
    if prato.estoque < quantidade:
        raise ValueError("Estoque insuficiente")


def debitar_estoque(items: Sequence[dict]) -> None:
    for it in items:
        prato = db.session.get(Prato, int(it["prato_id"]))
        if not prato:
            raise ValueError("Prato inexistente")
        validar_disponibilidade(prato, int(it["quantidade"]))
        prato.estoque -= int(it["quantidade"])
        if prato.estoque < 0:
            raise ValueError("Estoque não pode ser negativo")


def criar_pedido(cliente_id: int, restaurante_id: int, endereco_id: int, forma_pagamento: str, items: Sequence[dict]) -> Pedido:
    subtotal, taxa, total = calcular_totais(items)
    pedido = Pedido(
        cliente_id=cliente_id,
        restaurante_id=restaurante_id,
        endereco_entrega_id=endereco_id,
        status=StatusPedido.PREPARACAO.value,
        forma_pagamento=forma_pagamento,
        valor_subtotal=subtotal,
        taxa_empresa=taxa,
        valor_total=total,
    )
    db.session.add(pedido)
    db.session.flush()  # id

    for it in items:
        item = ItemPedido(
            pedido_id=pedido.id,
            prato_id=int(it["prato_id"]),
            quantidade=int(it["quantidade"]),
            preco_unitario=_to_money(it["preco"]),
            observacoes=it.get("observacoes"),
        )
        db.session.add(item)

    debitar_estoque(items)
    return pedido


def avancar_status(pedido: Pedido, novo_status: str) -> None:
    atual = pedido.status
    if atual == StatusPedido.CANCELADO.value:
        raise ValueError("Pedido cancelado não pode mudar")
    cadeia = [StatusPedido.PREPARACAO.value, StatusPedido.TRANSITO.value, StatusPedido.ENTREGUE.value]
    if novo_status == StatusPedido.CANCELADO.value:
        if atual != StatusPedido.PREPARACAO.value:
            raise ValueError("Só é possível cancelar em preparação")
        pedido.status = StatusPedido.CANCELADO.value
        return
    try:
        if cadeia.index(novo_status) - cadeia.index(atual) != 1:
            raise ValueError("Transição de status inválida")
    except ValueError:
        raise ValueError("Status inválido")
    pedido.status = novo_status

