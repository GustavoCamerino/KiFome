from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Numeric, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db
from .enums import StatusPedido, enum_column


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("usuarios.id"), nullable=False)
    restaurante_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("restaurantes.id"), nullable=False)
    endereco_entrega_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("enderecos_cliente.id"), nullable=False)
    status: Mapped[StatusPedido] = mapped_column(enum_column(StatusPedido, "status_pedido"), nullable=False, server_default=StatusPedido.PREPARACAO.value)
    forma_pagamento: Mapped[str] = mapped_column(Text, nullable=False)
    valor_subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    taxa_empresa: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    valor_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=db.func.now())

    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")


class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"
    __table_args__ = (
        CheckConstraint("quantidade >= 1", name="ck_itens_qtde_pos"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False)
    prato_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("pratos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_unitario: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    pedido = relationship("Pedido", back_populates="itens")
    prato = relationship("Prato")

