from enum import Enum
from sqlalchemy import Enum as SAEnum


class TipoUsuario(str, Enum):
    CLIENTE = "CLIENTE"
    RESTAURANTE_OWNER = "RESTAURANTE_OWNER"


class DiaSemana(str, Enum):
    Segunda = "Segunda"
    Terca = "Terça"
    Quarta = "Quarta"
    Quinta = "Quinta"
    Sexta = "Sexta"
    Sabado = "Sábado"
    Domingo = "Domingo"


class StatusPedido(str, Enum):
    PREPARACAO = "preparacao"
    TRANSITO = "transito"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


def enum_column(enum_cls, name: str):
    # Use native_enum=False for cross-db tests (SQLite) and named type for Postgres
    return SAEnum(enum_cls, name=name, native_enum=False, validate_strings=True)

