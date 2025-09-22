from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select
from app.extensions import db
from app.models.user import Usuario
from app.models.enums import TipoUsuario


bp = Blueprint("auth", __name__, template_folder="../templates/auth")


@bp.get("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("public.home"))
    return render_template("auth/register.html")


@bp.post("/register")
def register_post():
    data = request.form
    nome = data.get("nome")
    email = data.get("email")
    telefone = data.get("telefone")
    senha = data.get("senha")
    tipo = data.get("tipo")
    if tipo not in (TipoUsuario.CLIENTE.value, TipoUsuario.RESTAURANTE_OWNER.value):
        flash("Tipo inválido", "error")
        return redirect(url_for("auth.register"))
    if not nome or not email or not senha or not telefone:
        flash("Preencha todos os campos", "error")
        return redirect(url_for("auth.register"))
    exists = db.session.execute(select(Usuario).where(Usuario.email == email)).scalar()
    if exists:
        flash("E-mail já cadastrado", "error")
        return redirect(url_for("auth.register"))
    user = Usuario(
        nome_completo=nome,
        email=email,
        telefone=telefone,
        senha_hash=generate_password_hash(senha),
        tipo=tipo,
    )
    db.session.add(user)
    db.session.commit()
    flash("Cadastro realizado! Faça login.", "success")
    return redirect(url_for("auth.login"))


@bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.home"))
    return render_template("auth/login.html")


@bp.post("/login")
def login_post():
    email = request.form.get("email")
    senha = request.form.get("senha")
    user: Usuario | None = db.session.execute(select(Usuario).where(Usuario.email == email)).scalar()
    if not user or not check_password_hash(user.senha_hash, senha):
        flash("Credenciais inválidas", "error")
        return redirect(url_for("auth.login"))
    login_user(user)
    flash("Bem-vindo!", "success")
    return redirect(url_for("public.home"))


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sessão.", "info")
    return redirect(url_for("public.home"))

