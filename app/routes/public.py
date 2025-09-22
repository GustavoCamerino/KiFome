from flask import Blueprint, render_template, request, abort
from sqlalchemy import select
from app.extensions import db
from app.models.restaurant import Restaurante
from app.models.dish import Prato
from app.models.category import CategoriaPrato
from app.models.review import AvaliacaoRestaurante
from app.services.horarios import aberto_agora


bp = Blueprint("public", __name__)


@bp.get("/")
def home():
    q = request.args.get("q", "").strip()
    tipo = request.args.get("tipo", "").strip()
    aberto = request.args.get("aberto", "0") == "1"

    stmt = select(Restaurante)
    if q:
        stmt = stmt.where(Restaurante.nome.ilike(f"%{q}%"))
    if tipo:
        stmt = stmt.where(Restaurante.tipo_culinaria.ilike(f"%{tipo}%"))
    restaurantes = db.session.execute(stmt).scalars().all()
    if aberto:
        restaurantes = [r for r in restaurantes if aberto_agora(r.id)]
    return render_template("home.html", restaurantes=restaurantes, q=q, tipo=tipo, aberto=aberto)


@bp.get("/restaurantes/<int:restaurante_id>")
def restaurante_detalhe(restaurante_id: int):
    rest = db.session.get(Restaurante, restaurante_id)
    if not rest:
        abort(404)
    categorias = db.session.execute(select(CategoriaPrato)).scalars().all()
    pratos = db.session.execute(select(Prato).where(Prato.restaurante_id == restaurante_id, Prato.disponivel == True)).scalars().all()
    avals = db.session.execute(select(AvaliacaoRestaurante).where(AvaliacaoRestaurante.restaurante_id == restaurante_id)).scalars().all()
    return render_template("restaurante_detalhe.html", restaurante=rest, categorias=categorias, pratos=pratos, avaliacoes=avals)

