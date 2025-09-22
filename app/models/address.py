from sqlalchemy import BigInteger, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class EnderecoCliente(db.Model):
    __tablename__ = "enderecos_cliente"
    __table_args__ = (
        UniqueConstraint("cliente_id", "apelido", name="uq_cliente_apelido"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    apelido: Mapped[str | None] = mapped_column(Text, nullable=True)
    logradouro: Mapped[str] = mapped_column(Text, nullable=False)
    numero: Mapped[str] = mapped_column(Text, nullable=False)
    bairro: Mapped[str] = mapped_column(Text, nullable=False)
    cidade: Mapped[str] = mapped_column(Text, nullable=False)
    uf: Mapped[str] = mapped_column(Text, nullable=False)
    cep: Mapped[str] = mapped_column(Text, nullable=False)
    complemento: Mapped[str | None] = mapped_column(Text, nullable=True)

    cliente = relationship("Usuario", back_populates="enderecos")

