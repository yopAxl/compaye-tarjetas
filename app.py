"""
ComPaye Tarjetas — Gestor de Inventario de Tarjetas de Pantallas.

Ejecutar en modo desarrollo:
    python app.py

Ejecutar en modo produccion local (Windows):
    python -m waitress --host=127.0.0.1 --port=5000 app:app
"""

import os

from flask import Flask, redirect, render_template, url_for

from config import Config
from models import db


def format_mxn(value) -> str:
    """Format a numeric amount as MXN currency (e.g. $1,250.00)."""
    try:
        amount = float(value or 0.0)
    except (TypeError, ValueError):
        amount = 0.0
    return f'${amount:,.2f}'


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure runtime directories exist
    os.makedirs(app.config['DATABASE_DIR'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Jinja template filters & globals
    app.jinja_env.filters['mxn'] = format_mxn

    @app.context_processor
    def inject_inventory_globals():
        return {
            'low_stock_threshold': app.config['LOW_STOCK_THRESHOLD'],
        }

    # Register blueprints (lazy imports to avoid circular deps)
    from routes.tarjetas import tarjetas_bp
    from routes.contenedores import contenedores_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(tarjetas_bp)
    app.register_blueprint(contenedores_bp, url_prefix='/contenedores')
    app.register_blueprint(dashboard_bp)

    # Create all tables on first run
    with app.app_context():
        from models.tarjeta import Tarjeta, Compatibilidad  # noqa: F401
        from models.contenedor import Contenedor              # noqa: F401
        db.create_all()

    # Root URL -> redirect to card listing / search
    @app.route('/')
    def index():
        return redirect(url_for('tarjetas.listar'))

    # Friendly error pages
    @app.errorhandler(404)
    def not_found(_error):
        return render_template('error.html', code=404, title='Página no encontrada',
                               message='La dirección solicitada no existe o la tarjeta fue eliminada.'), 404

    @app.errorhandler(413)
    def file_too_large(_error):
        return render_template('error.html', code=413, title='Archivo demasiado grande',
                               message='La imagen supera el límite permitido de 16 MB. Intente con una foto más ligera.'), 413

    @app.errorhandler(500)
    def internal_error(_error):
        return render_template('error.html', code=500, title='Error interno',
                               message='Ocurrió un problema inesperado al procesar su solicitud.'), 500

    return app


# ------------------------------------------------------------------
# Entry point for `python app.py`
# ------------------------------------------------------------------
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
