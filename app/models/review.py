from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class AvaliacaoRestaurante(db.Model):
    __tablename__ = "avaliacoes_restaurantes"
    __table_args__ = (
        CheckConstraint("nota >= 0 AND nota <= 5", name="ck_avaliacao_nota_range"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    restaurante_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("restaurantes.id", ondelete="CASCADE"), nullable=False)
    cliente_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    nota: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=db.func.now())

    restaurante = relationship("Restaurante")

