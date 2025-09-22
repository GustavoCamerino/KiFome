from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Index, Numeric, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class Prato(db.Model):
    __tablename__ = "pratos"
    __table_args__ = (
        CheckConstraint("preco >= 0", name="ck_pratos_preco_pos"),
        CheckConstraint("estoque >= 0", name="ck_pratos_estoque_pos"),
        Index("ix_pratos_rest_cat_disp", "restaurante_id", "categoria_id", "disponivel"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    restaurante_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("restaurantes.id", ondelete="CASCADE"), nullable=False
    )
    categoria_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("categorias_pratos.id"), nullable=False)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    preco: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    disponivel: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=db.text("true"))
    estoque: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    restaurante = relationship("Restaurante", back_populates="pratos")
    categoria = relationship("CategoriaPrato")

