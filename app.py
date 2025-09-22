from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from app.extensions import db
from app.models.user import Usuario
import os


migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id: str):
    try:
        return db.session.get(Usuario, int(user_id))
    except Exception:
        return None


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, static_folder="app/static", template_folder="app/templates")

    # Config
    if test_config:
        app.config.from_object("config.Config")
        app.config.update(test_config)
    else:
        app.config.from_object("config.Config")

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.public import bp as public_bp
    from app.routes.cliente import bp as cliente_bp
    from app.routes.restaurante import bp as restaurante_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cliente_bp)
    app.register_blueprint(restaurante_bp)

    # CLI commands
    from app.cli import register_cli

    register_cli(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
