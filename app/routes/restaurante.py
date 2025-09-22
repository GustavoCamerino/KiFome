from datetime import time
from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import select, func
from app.extensions import db
from app.models.restaurant import Restaurante, HorarioFuncionamentoRestaurante
from app.models.category import CategoriaPrato
from app.models.dish import Prato
from app.models.order import Pedido
from app.models.enums import StatusPedido
from app.services.pedidos import avancar_status


bp = Blueprint("restaurante", __name__)


def require_owner():
    if not current_user.is_authenticated or current_user.tipo != "RESTAURANTE_OWNER":
        abort(403)


def _get_meu_restaurante():
    return db.session.execute(select(Restaurante).where(Restaurante.owner_id == current_user.id)).scalar()


@bp.get("/restaurante/dashboard")
@login_required
def owner_dashboard():
    require_owner()
    rest = _get_meu_restaurante()
    vendas = 0
    taxa = 0
    ticket = 0
    if rest:
        pedidos = db.session.execute(select(Pedido).where(Pedido.restaurante_id == rest.id)).scalars().all()
        if pedidos:
            vendas = sum(float(p.valor_total) for p in pedidos)
            taxa = sum(float(p.taxa_empresa) for p in pedidos)
            ticket = vendas / len(pedidos)
    return render_template("owner_dashboard.html", restaurante=rest, vendas=vendas, taxa=taxa, ticket=ticket)


@bp.get("/restaurante/meu")
@login_required
def owner_meu_restaurante():
    require_owner()
    rest = _get_meu_restaurante()
    return render_template("owner_meu_restaurante.html", restaurante=rest)


@bp.post("/restaurante/meu")
@login_required
def owner_meu_restaurante_post():
    require_owner()
    f = request.form
    rest = _get_meu_restaurante()
    if not rest:
        rest = Restaurante(owner_id=current_user.id)
        db.session.add(rest)
    rest.nome = f.get("nome")
    rest.endereco = f.get("endereco")
    rest.telefone = f.get("telefone")
    rest.tipo_culinaria = f.get("tipo_culinaria")
    db.session.commit()
    flash("Dados do restaurante salvos.", "success")
    return redirect(url_for("restaurante.owner_meu_restaurante"))


@bp.get("/restaurante/horarios")
@login_required
def owner_horarios():
    require_owner()
    rest = _get_meu_restaurante()
    if not rest:
        flash("Cadastre seu restaurante primeiro.", "warning")
        return redirect(url_for("restaurante.owner_meu_restaurante"))
    horarios = db.session.execute(select(HorarioFuncionamentoRestaurante).where(HorarioFuncionamentoRestaurante.restaurante_id == rest.id)).scalars().all()
    return render_template("owner_horarios.html", horarios=horarios)


@bp.post("/restaurante/horarios")
@login_required
def owner_horarios_post():
    require_owner()
    rest = _get_meu_restaurante()
    if not rest:
        abort(400)
    dia = request.form.get("dia_semana")
    abertura = request.form.get("horario_abertura")
    fechamento = request.form.get("horario_fechamento")
    h = db.session.execute(
        select(HorarioFuncionamentoRestaurante).where(
            HorarioFuncionamentoRestaurante.restaurante_id == rest.id,
            HorarioFuncionamentoRestaurante.dia_semana == dia,
        )
    ).scalar()
    if not h:
        h = HorarioFuncionamentoRestaurante(restaurante_id=rest.id, dia_semana=dia)
        db.session.add(h)
    h.horario_abertura = time.fromisoformat(abertura)
    h.horario_fechamento = time.fromisoformat(fechamento)
    db.session.commit()
    flash("Horário salvo.", "success")
    return redirect(url_for("restaurante.owner_horarios"))


@bp.get("/restaurante/categorias")
@login_required
def owner_categorias():
    require_owner()
    cats = db.session.execute(select(CategoriaPrato).order_by(CategoriaPrato.nome_categoria)).scalars().all()
    return render_template("owner_categorias.html", categorias=cats)


@bp.post("/restaurante/categorias")
@login_required
def owner_categorias_post():
    require_owner()
    nome = request.form.get("nome_categoria")
    if nome:
        db.session.add(CategoriaPrato(nome_categoria=nome))
        db.session.commit()
        flash("Categoria salva.", "success")
    return redirect(url_for("restaurante.owner_categorias"))


@bp.post("/restaurante/categorias/<int:cat_id>/delete")
@login_required
def owner_categorias_delete(cat_id: int):
    require_owner()
    cat = db.session.get(CategoriaPrato, cat_id)
    if not cat:
        abort(404)
    db.session.delete(cat)
    db.session.commit()
    flash("Categoria excluída.", "info")
    return redirect(url_for("restaurante.owner_categorias"))


@bp.get("/restaurante/pratos")
@login_required
def owner_pratos_list():
    require_owner()
    rest = _get_meu_restaurante()
    if not rest:
        flash("Cadastre seu restaurante primeiro.", "warning")
        return redirect(url_for("restaurante.owner_meu_restaurante"))
    pratos = db.session.execute(select(Prato).where(Prato.restaurante_id == rest.id)).scalars().all()
    return render_template("owner_pratos_list.html", pratos=pratos)


@bp.get("/restaurante/pratos/new")
@login_required
def owner_prato_new():
    require_owner()
    cats = db.session.execute(select(CategoriaPrato)).scalars().all()
    return render_template("owner_prato_form.html", prato=None, categorias=cats)


@bp.post("/restaurante/pratos/new")
@login_required
def owner_prato_new_post():
    require_owner()
    rest = _get_meu_restaurante()
    if not rest:
        abort(400)
    f = request.form
    prato = Prato(
        restaurante_id=rest.id,
        categoria_id=int(f.get("categoria_id")),
        nome=f.get("nome"),
        descricao=f.get("descricao"),
        preco=float(f.get("preco")),
        disponivel=(f.get("disponivel") == "on"),
        estoque=int(f.get("estoque")),
    )
    db.session.add(prato)
    db.session.commit()
    flash("Prato criado.", "success")
    return redirect(url_for("restaurante.owner_pratos_list"))


@bp.get("/restaurante/pratos/<int:prato_id>/edit")
@login_required
def owner_prato_edit(prato_id: int):
    require_owner()
    prato = db.session.get(Prato, prato_id)
    rest = _get_meu_restaurante()
    if not prato or not rest or prato.restaurante_id != rest.id:
        abort(403)
    cats = db.session.execute(select(CategoriaPrato)).scalars().all()
    return render_template("owner_prato_form.html", prato=prato, categorias=cats)


@bp.post("/restaurante/pratos/<int:prato_id>/edit")
@login_required
def owner_prato_edit_post(prato_id: int):
    require_owner()
    prato = db.session.get(Prato, prato_id)
    rest = _get_meu_restaurante()
    if not prato or not rest or prato.restaurante_id != rest.id:
        abort(403)
    f = request.form
    prato.categoria_id = int(f.get("categoria_id"))
    prato.nome = f.get("nome")
    prato.descricao = f.get("descricao")
    prato.preco = float(f.get("preco"))
    prato.disponivel = (f.get("disponivel") == "on")
    prato.estoque = int(f.get("estoque"))
    db.session.commit()
    flash("Prato atualizado.", "success")
    return redirect(url_for("restaurante.owner_pratos_list"))


@bp.get("/restaurante/pedidos")
@login_required
def owner_pedidos():
    require_owner()
    rest = _get_meu_restaurante()
    if not rest:
        abort(400)
    pedidos = db.session.execute(select(Pedido).where(Pedido.restaurante_id == rest.id).order_by(Pedido.id.desc())).scalars().all()
    return render_template("owner_pedidos.html", pedidos=pedidos)


@bp.post("/restaurante/pedidos/<int:pedido_id>/status")
@login_required
def owner_pedido_status(pedido_id: int):
    require_owner()
    rest = _get_meu_restaurante()
    ped = db.session.get(Pedido, pedido_id)
    if not ped or not rest or ped.restaurante_id != rest.id:
        abort(403)
    novo = request.form.get("status")
    try:
        avancar_status(ped, novo)
        db.session.commit()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"ok": True, "status": ped.status})


@bp.get("/restaurante/relatorios")
@login_required
def owner_relatorios():
    require_owner()
    rest = _get_meu_restaurante()
    if not rest:
        abort(400)
    # simples: pega tudo, poderia filtrar por período via query params
    pedidos = db.session.execute(select(Pedido).where(Pedido.restaurante_id == rest.id)).scalars().all()
    total_vendido = sum(float(p.valor_total) for p in pedidos)
    total_taxa = sum(float(p.taxa_empresa) for p in pedidos)
    ticket_medio = (total_vendido / len(pedidos)) if pedidos else 0
    return render_template("owner_relatorios.html", total_vendido=total_vendido, total_taxa=total_taxa, ticket_medio=ticket_medio)

