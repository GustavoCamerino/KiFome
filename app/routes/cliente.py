from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, abort, flash
from flask_login import login_required, current_user
from sqlalchemy import select
from app.extensions import db
from app.models.user import Usuario
from app.models.address import EnderecoCliente
from app.models.dish import Prato
from app.models.order import Pedido
from app.services.pedidos import calcular_totais, validar_disponibilidade, criar_pedido


bp = Blueprint("cliente", __name__)


def require_cliente():
    if not current_user.is_authenticated or current_user.tipo != "CLIENTE":
        abort(403)


@bp.get("/cliente/dashboard")
@login_required
def cliente_dashboard():
    require_cliente()
    pedidos = db.session.execute(select(Pedido).where(Pedido.cliente_id == current_user.id).order_by(Pedido.id.desc())).scalars().all()
    return render_template("cliente_dashboard.html", pedidos=pedidos)


@bp.get("/cliente/enderecos")
@login_required
def enderecos_list():
    require_cliente()
    enderecos = db.session.execute(select(EnderecoCliente).where(EnderecoCliente.cliente_id == current_user.id)).scalars().all()
    return render_template("cliente_enderecos.html", enderecos=enderecos)


@bp.post("/cliente/enderecos")
@login_required
def enderecos_add():
    require_cliente()
    f = request.form
    e = EnderecoCliente(
        cliente_id=current_user.id,
        apelido=f.get("apelido") or None,
        logradouro=f.get("logradouro"),
        numero=f.get("numero"),
        bairro=f.get("bairro"),
        cidade=f.get("cidade"),
        uf=f.get("uf"),
        cep=f.get("cep"),
        complemento=f.get("complemento") or None,
    )
    db.session.add(e)
    db.session.commit()
    flash("Endereço salvo.", "success")
    return redirect(url_for("cliente.enderecos_list"))


@bp.post("/cliente/enderecos/<int:endereco_id>/delete")
@login_required
def enderecos_delete(endereco_id: int):
    require_cliente()
    e = db.session.get(EnderecoCliente, endereco_id)
    if not e or e.cliente_id != current_user.id:
        abort(404)
    db.session.delete(e)
    db.session.commit()
    flash("Endereço removido.", "info")
    return redirect(url_for("cliente.enderecos_list"))


def _cart() -> list[dict]:
    return session.setdefault("cart", [])


def _save_cart(items):
    session["cart"] = items
    session.modified = True


@bp.post("/carrinho/add")
@login_required
def carrinho_add():
    require_cliente()
    data = request.get_json(silent=True) or request.form
    prato_id = int(data.get("prato_id"))
    quantidade = int(data.get("quantidade", 1))
    observacoes = data.get("observacoes")
    prato = db.session.get(Prato, prato_id)
    if not prato:
        return jsonify({"error": "Prato não encontrado"}), 404
    try:
        validar_disponibilidade(prato, quantidade)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    items = _cart()
    # merge if already on cart
    for it in items:
        if it["prato_id"] == prato_id:
            new_qtd = it["quantidade"] + quantidade
            if prato.estoque < new_qtd:
                return jsonify({"error": "Estoque insuficiente"}), 400
            it["quantidade"] = new_qtd
            it["observacoes"] = observacoes or it.get("observacoes")
            _save_cart(items)
            break
    else:
        items.append({
            "prato_id": prato_id,
            "nome": prato.nome,
            "preco": float(prato.preco),
            "quantidade": quantidade,
            "observacoes": observacoes,
            "restaurante_id": prato.restaurante_id,
        })
        _save_cart(items)
    subtotal, taxa, total = calcular_totais(items)
    return jsonify({"ok": True, "subtotal": float(subtotal), "taxa": float(taxa), "total": float(total), "items": items})


@bp.post("/carrinho/update")
@login_required
def carrinho_update():
    require_cliente()
    data = request.get_json(silent=True) or {}
    prato_id = int(data.get("prato_id"))
    quantidade = max(0, int(data.get("quantidade", 1)))
    items = _cart()
    for it in items:
        if it["prato_id"] == prato_id:
            if quantidade == 0:
                items.remove(it)
                break
            prato = db.session.get(Prato, prato_id)
            try:
                validar_disponibilidade(prato, quantidade)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
            it["quantidade"] = quantidade
            break
    _save_cart(items)
    subtotal, taxa, total = calcular_totais(items)
    return jsonify({"ok": True, "subtotal": float(subtotal), "taxa": float(taxa), "total": float(total), "items": items})


@bp.post("/carrinho/remove")
@login_required
def carrinho_remove():
    require_cliente()
    data = request.get_json(silent=True) or {}
    prato_id = int(data.get("prato_id"))
    items = [it for it in _cart() if it["prato_id"] != prato_id]
    _save_cart(items)
    subtotal, taxa, total = calcular_totais(items)
    return jsonify({"ok": True, "subtotal": float(subtotal), "taxa": float(taxa), "total": float(total), "items": items})


@bp.get("/carrinho")
@login_required
def carrinho_view():
    require_cliente()
    items = _cart()
    subtotal, taxa, total = calcular_totais(items)
    return render_template("carrinho.html", items=items, subtotal=subtotal, taxa=taxa, total=total)


@bp.get("/checkout")
@login_required
def checkout():
    require_cliente()
    items = _cart()
    if not items:
        flash("Seu carrinho está vazio.", "warning")
        return redirect(url_for("public.home"))
    rest_id = items[0]["restaurante_id"]
    if any(it["restaurante_id"] != rest_id for it in items):
        flash("O carrinho aceita itens de um único restaurante por vez.", "error")
        return redirect(url_for("cliente.carrinho_view"))
    enderecos = db.session.execute(select(EnderecoCliente).where(EnderecoCliente.cliente_id == current_user.id)).scalars().all()
    subtotal, taxa, total = calcular_totais(items)
    return render_template("checkout.html", enderecos=enderecos, subtotal=subtotal, taxa=taxa, total=total)


@bp.post("/checkout/confirmar")
@login_required
def checkout_confirmar():
    require_cliente()
    items = _cart()
    if not items:
        abort(400)
    endereco_id = int(request.form.get("endereco_id"))
    rest_id = items[0]["restaurante_id"]
    pedido = criar_pedido(
        cliente_id=current_user.id,
        restaurante_id=rest_id,
        endereco_id=endereco_id,
        forma_pagamento="Simulado",
        items=items,
    )
    db.session.commit()
    session.pop("cart", None)
    flash("Pedido confirmado!", "success")
    return redirect(url_for("cliente.pedidos_detalhe", pedido_id=pedido.id))


@bp.get("/cliente/pedidos")
@login_required
def pedidos_list():
    require_cliente()
    pedidos = db.session.execute(select(Pedido).where(Pedido.cliente_id == current_user.id).order_by(Pedido.id.desc())).scalars().all()
    return render_template("cliente_pedidos.html", pedidos=pedidos)


@bp.get("/cliente/pedidos/<int:pedido_id>")
@login_required
def pedidos_detalhe(pedido_id: int):
    require_cliente()
    ped = db.session.get(Pedido, pedido_id)
    if not ped or ped.cliente_id != current_user.id:
        abort(404)
    return render_template("pedido_detalhe.html", pedido=ped)

