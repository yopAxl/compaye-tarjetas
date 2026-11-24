"""
ComPaye Tarjetas — Gestor de Inventario de Tarjetas de Pantallas.

Ejecutar en modo desarrollo:
    python app.py

Ejecutar en modo produccion local (Windows):
    python -m waitress --host=127.0.0.1 --port=5000 app:app
"""

import os

from flask import Flask, redirect, url_for

from config import Config
from models import db


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure runtime directories exist
    os.makedirs(app.config['DATABASE_DIR'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints (lazy imports to avoid circular deps)
    from routes.tarjetas import tarjetas_bp
    from routes.contenedores import contenedores_bp

    app.register_blueprint(tarjetas_bp)
    app.register_blueprint(contenedores_bp, url_prefix='/contenedores')

    # Create all tables on first run
    with app.app_context():
        from models.tarjeta import Tarjeta, Compatibilidad  # noqa: F401
        from models.contenedor import Contenedor              # noqa: F401
        db.create_all()

    # Root URL → redirect to card listing
    @app.route('/')
    def index():
        return redirect(url_for('tarjetas.listar'))

    return app


# ------------------------------------------------------------------
# Entry point for `python app.py`
# ------------------------------------------------------------------
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
