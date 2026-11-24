"""Routes for card (tarjeta) CRUD operations."""

import os
import uuid

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from PIL import Image
from werkzeug.utils import secure_filename

from models import db
from models.contenedor import Contenedor
from models.tarjeta import Compatibilidad, Tarjeta

tarjetas_bp = Blueprint('tarjetas', __name__)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _allowed_file(filename: str) -> bool:
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower()
        in current_app.config['ALLOWED_EXTENSIONS']
    )


def _save_photo(file) -> str | None:
    """Save an uploaded photo, resize it, and return the filename."""
    if file and file.filename and _allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f'{uuid.uuid4().hex}.{ext}'
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        img = Image.open(file)
        img.thumbnail(current_app.config['THUMBNAIL_SIZE'])
        img.save(filepath, quality=85, optimize=True)
        return filename
    return None


def _delete_photo(filename: str | None) -> None:
    """Remove a photo file from the uploads folder."""
    if filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)


# ------------------------------------------------------------------
# Views
# ------------------------------------------------------------------

@tarjetas_bp.route('/tarjetas')
def listar():
    """List all cards with optional search and filters."""
    query = request.args.get('q', '').strip()
    contenedor_id = request.args.get('contenedor', '')
    stock_filter = request.args.get('stock', '')

    stmt = Tarjeta.query

    # Full-text-ish search across key fields
    if query:
        like = f'%{query}%'
        stmt = stmt.filter(
            db.or_(
                Tarjeta.numero_tarjeta.ilike(like),
                Tarjeta.modelo_pantalla.ilike(like),
                Tarjeta.compatibilidades.any(
                    Compatibilidad.pantalla_compatible.ilike(like),
                ),
            )
        )

    if contenedor_id:
        stmt = stmt.filter(Tarjeta.contenedor_id == int(contenedor_id))

    if stock_filter == 'disponible':
        stmt = stmt.filter(Tarjeta.stock > 0)
    elif stock_filter == 'agotado':
        stmt = stmt.filter(Tarjeta.stock == 0)

    tarjetas = stmt.order_by(Tarjeta.updated_at.desc()).all()
    contenedores = Contenedor.query.order_by(Contenedor.nombre).all()

    return render_template(
        'index.html',
        tarjetas=tarjetas,
        contenedores=contenedores,
        query=query,
        contenedor_id=contenedor_id,
        stock_filter=stock_filter,
        total=len(tarjetas),
    )


@tarjetas_bp.route('/tarjetas/nueva', methods=['GET', 'POST'])
def crear():
    """Create a new card."""
    contenedores = Contenedor.query.order_by(Contenedor.nombre).all()

    if request.method == 'POST':
        numero = request.form.get('numero_tarjeta', '').strip()
        modelo = request.form.get('modelo_pantalla', '').strip()
        precio = request.form.get('precio', 0, type=float)
        stock = request.form.get('stock', 0, type=int)
        contenedor_id = request.form.get('contenedor_id', type=int)
        compat_raw = request.form.get('compatibilidades', '').strip()

        # --- Validation ---
        if not numero:
            flash('El número de tarjeta es obligatorio.', 'error')
            return render_template('tarjeta_form.html', contenedores=contenedores)

        if not modelo:
            flash('El modelo de pantalla es obligatorio.', 'error')
            return render_template('tarjeta_form.html', contenedores=contenedores)

        if Tarjeta.query.filter_by(numero_tarjeta=numero).first():
            flash(f'Ya existe una tarjeta con el número "{numero}".', 'error')
            return render_template('tarjeta_form.html', contenedores=contenedores)

        # --- Photo ---
        foto_filename = None
        if 'foto' in request.files:
            foto_filename = _save_photo(request.files['foto'])

        # --- Create ---
        tarjeta = Tarjeta(
            numero_tarjeta=numero,
            modelo_pantalla=modelo,
            precio=precio,
            stock=stock,
            contenedor_id=contenedor_id or None,
            foto_path=foto_filename,
        )

        if compat_raw:
            for pantalla in compat_raw.split(','):
                pantalla = pantalla.strip()
                if pantalla:
                    tarjeta.compatibilidades.append(
                        Compatibilidad(pantalla_compatible=pantalla),
                    )

        db.session.add(tarjeta)
        db.session.commit()

        flash(f'Tarjeta "{numero}" registrada exitosamente.', 'success')
        return redirect(url_for('tarjetas.listar'))

    return render_template('tarjeta_form.html', contenedores=contenedores)


@tarjetas_bp.route('/tarjetas/<int:id>')
def detalle(id):
    """Show card details."""
    tarjeta = Tarjeta.query.get_or_404(id)
    return render_template('tarjeta_detail.html', tarjeta=tarjeta)


@tarjetas_bp.route('/tarjetas/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    """Edit an existing card."""
    tarjeta = Tarjeta.query.get_or_404(id)
    contenedores = Contenedor.query.order_by(Contenedor.nombre).all()

    if request.method == 'POST':
        numero = request.form.get('numero_tarjeta', '').strip()
        modelo = request.form.get('modelo_pantalla', '').strip()
        precio = request.form.get('precio', 0, type=float)
        stock = request.form.get('stock', 0, type=int)
        contenedor_id = request.form.get('contenedor_id', type=int)
        compat_raw = request.form.get('compatibilidades', '').strip()

        if not numero:
            flash('El número de tarjeta es obligatorio.', 'error')
            return render_template(
                'tarjeta_form.html', tarjeta=tarjeta, contenedores=contenedores,
            )

        if not modelo:
            flash('El modelo de pantalla es obligatorio.', 'error')
            return render_template(
                'tarjeta_form.html', tarjeta=tarjeta, contenedores=contenedores,
            )

        dup = Tarjeta.query.filter(
            Tarjeta.numero_tarjeta == numero, Tarjeta.id != id,
        ).first()
        if dup:
            flash(f'Ya existe otra tarjeta con el número "{numero}".', 'error')
            return render_template(
                'tarjeta_form.html', tarjeta=tarjeta, contenedores=contenedores,
            )

        # Photo update
        if 'foto' in request.files and request.files['foto'].filename:
            _delete_photo(tarjeta.foto_path)
            tarjeta.foto_path = _save_photo(request.files['foto'])

        if request.form.get('remove_foto') == '1':
            _delete_photo(tarjeta.foto_path)
            tarjeta.foto_path = None

        tarjeta.numero_tarjeta = numero
        tarjeta.modelo_pantalla = modelo
        tarjeta.precio = precio
        tarjeta.stock = stock
        tarjeta.contenedor_id = contenedor_id or None

        # Rebuild compatibilities
        Compatibilidad.query.filter_by(tarjeta_id=id).delete()
        if compat_raw:
            for pantalla in compat_raw.split(','):
                pantalla = pantalla.strip()
                if pantalla:
                    tarjeta.compatibilidades.append(
                        Compatibilidad(pantalla_compatible=pantalla),
                    )

        db.session.commit()
        flash(f'Tarjeta "{numero}" actualizada exitosamente.', 'success')
        return redirect(url_for('tarjetas.detalle', id=id))

    return render_template(
        'tarjeta_form.html', tarjeta=tarjeta, contenedores=contenedores,
    )


@tarjetas_bp.route('/tarjetas/<int:id>/eliminar', methods=['POST'])
def eliminar(id):
    """Delete a card and its photo."""
    tarjeta = Tarjeta.query.get_or_404(id)
    _delete_photo(tarjeta.foto_path)
    numero = tarjeta.numero_tarjeta
    db.session.delete(tarjeta)
    db.session.commit()
    flash(f'Tarjeta "{numero}" eliminada.', 'success')
    return redirect(url_for('tarjetas.listar'))


@tarjetas_bp.route('/tarjetas/<int:id>/stock', methods=['POST'])
def actualizar_stock(id):
    """Quick stock increment / decrement."""
    tarjeta = Tarjeta.query.get_or_404(id)
    action = request.form.get('action')

    if action == 'increment':
        tarjeta.stock += 1
    elif action == 'decrement' and tarjeta.stock > 0:
        tarjeta.stock -= 1

    db.session.commit()
    return redirect(request.referrer or url_for('tarjetas.listar'))


@tarjetas_bp.route('/uploads/tarjetas/<filename>')
def uploaded_file(filename):
    """Serve uploaded card photos."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
