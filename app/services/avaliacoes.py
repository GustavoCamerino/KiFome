from sqlalchemy import func, select
from app.extensions import db
from app.models.review import AvaliacaoRestaurante
from app.models.restaurant import Restaurante


def atualizar_nota_media(restaurante_id: int) -> None:
    stmt = (
        select(func.coalesce(func.avg(AvaliacaoRestaurante.nota), 0))
        .where(AvaliacaoRestaurante.restaurante_id == restaurante_id)
    )
    media = db.session.execute(stmt).scalar_one()
    rest = db.session.get(Restaurante, restaurante_id)
    if rest:
        rest.nota_media = round(float(media), 1)

