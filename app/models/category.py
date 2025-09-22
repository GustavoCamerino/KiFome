from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.extensions import db


class CategoriaPrato(db.Model):
    __tablename__ = "categorias_pratos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome_categoria: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

