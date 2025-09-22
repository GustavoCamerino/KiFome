from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import BigInteger, CheckConstraint, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db
from .enums import TipoUsuario, enum_column


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome_completo: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    telefone: Mapped[str] = mapped_column(Text, nullable=False)
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[TipoUsuario] = mapped_column(enum_column(TipoUsuario, "tipo_usuario"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=db.func.now())

    enderecos = relationship("EnderecoCliente", back_populates="cliente", cascade="all, delete-orphan")
    restaurantes = relationship("Restaurante", back_populates="owner", cascade="all, delete-orphan")

    def get_id(self):
        return str(self.id)

