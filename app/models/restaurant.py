from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Numeric, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db
from .enums import DiaSemana, enum_column


class Restaurante(db.Model):
    __tablename__ = "restaurantes"
    __table_args__ = (
        Index("ix_restaurantes_nome", "nome"),
        Index("ix_restaurantes_tipo", "tipo_culinaria"),
        CheckConstraint("nota_media >= 0 AND nota_media <= 5", name="ck_restaurantes_nota"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    telefone: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_culinaria: Mapped[str] = mapped_column(Text, nullable=False)
    nota_media: Mapped[float] = mapped_column(Numeric(2, 1), nullable=False, server_default="0")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=db.func.now())

    owner = relationship("Usuario", back_populates="restaurantes")
    horarios = relationship(
        "HorarioFuncionamentoRestaurante",
        back_populates="restaurante",
        cascade="all, delete-orphan",
    )
    pratos = relationship("Prato", back_populates="restaurante", cascade="all, delete-orphan")


class HorarioFuncionamentoRestaurante(db.Model):
    __tablename__ = "horarios_funcionamento_restaurantes"
    __table_args__ = (
        UniqueConstraint("restaurante_id", "dia_semana", name="uq_restaurante_dia"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    restaurante_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("restaurantes.id", ondelete="CASCADE"), nullable=False
    )
    dia_semana: Mapped[DiaSemana] = mapped_column(enum_column(DiaSemana, "dia_semana"), nullable=False)
    horario_abertura: Mapped[datetime] = mapped_column(Time, nullable=False)
    horario_fechamento: Mapped[datetime] = mapped_column(Time, nullable=False)

    restaurante = relationship("Restaurante", back_populates="horarios")

