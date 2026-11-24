"""Routes for card (tarjeta) CRUD, search, advanced filters, and stock operations."""

import os
import uuid

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import selectinload

from models import db
from models.contenedor import Contenedor
from models.tarjeta import Compatibilidad, Tarjeta

tarjetas_bp = Blueprint('tarjetas', __name__)

SORT_OPTIONS = {
    'reciente': 'Más recientes',
    'numero_asc': 'Número (A–Z)',
    'precio_asc': 'Precio (menor a mayor)',
    'precio_desc': 'Precio (mayor a menor)',
    'stock_asc': 'Stock (menor a mayor)',
    'stock_desc': 'Stock (mayor a menor)',
}


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
    """Validate, orient, resize, and save an uploaded photo."""
    if not file or not file.filename:
        return None
    if not _allowed_file(file.filename):
        raise ValueError('Formato de imagen no compatible. Use JPG, PNG, GIF o WebP.')

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    try:
        img = Image.open(file)
        img = ImageOps.exif_transpose(img)
        if ext in {'jpg', 'jpeg'} and img.mode in {'RGBA', 'P', 'LA'}:
            background = Image.new('RGB', img.size, (255, 255, 255))
            rgba = img.convert('RGBA')
            background.paste(rgba, mask=rgba.split()[3])
            img = background
        elif ext in {'jpg', 'jpeg'} and img.mode != 'RGB':
            img = img.convert('RGB')

        img.thumbnail(current_app.config['THUMBNAIL_SIZE'], Image.Resampling.LANCZOS)
        save_kwargs = {'optimize': True}
        if ext in {'jpg', 'jpeg', 'webp'}:
            save_kwargs['quality'] = 85
        img.save(filepath, **save_kwargs)
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        if os.path.exists(filepath):
            os.remove(filepath)
        raise ValueError('No se pudo leer la imagen seleccionada. Verifique que el archivo no esté dañado.') from exc

    return filename


def _delete_photo(filename: str | None) -> None:
    """Remove a photo file from the uploads folder."""
    if filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)


def _parse_float(raw: str | None) -> float | None:
    if raw is None or raw.strip() == '':
        return None
    try:
        val = float(raw.strip().replace(',', ''))
        return val if val >= 0 else None
    except ValueError:
        return None


def _parse_int(raw: str | None) -> int | None:
    if raw is None or raw.strip() == '':
        return None
    try:
        return int(raw.strip())
    except ValueError:
        return None


def _parse_compatibilidades(raw: str) -> list[str]:
    """Split comma-separated screen models and deduplicate preserving order."""
    seen: set[str] = set()
    items: list[str] = []
    for entry in raw.replace('\n', ',').split(','):
        cleaned = ' '.join(entry.strip().split())
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            items.append(cleaned)
    return items


def _stock_state(stock: int) -> tuple[str, str]:
    threshold = current_app.config['LOW_STOCK_THRESHOLD']
    if stock <= 0:
        return ('agotado', 'Agotado')
    if stock <= threshold:
        return ('bajo', 'Bajo stock')
    return ('disponible', 'Disponible')


def _extract_form_data(form) -> dict:
    return {
        'numero_tarjeta': form.get('numero_tarjeta', '').strip(),
        'modelo_pantalla': form.get('modelo_pantalla', '').strip(),
        'precio': form.get('precio', '').strip(),
        'stock': form.get('stock', '').strip(),
        'contenedor_id': form.get('contenedor_id', '').strip(),
        'compatibilidades': form.get('compatibilidades', '').strip(),
    }


# ------------------------------------------------------------------
# Views
# ------------------------------------------------------------------

@tarjetas_bp.route('/tarjetas')
def listar():
    """List cards with search, combined V2 filters, sorting, and view toggle."""
    query = request.args.get('q', '').strip()
    contenedor_param = request.args.get('contenedor', '').strip()
    stock_filter = request.args.get('stock', '').strip()
    precio_min_raw = request.args.get('precio_min', '').strip()
    precio_max_raw = request.args.get('precio_max', '').strip()
    orden = request.args.get('orden', 'reciente').strip()
    vista = request.args.get('vista', 'tarjetas').strip()
    page = max(1, request.args.get('pagina', 1, type=int) or 1)

    if vista not in {'tarjetas', 'tabla'}:
        vista = 'tarjetas'
    if orden not in SORT_OPTIONS:
        orden = 'reciente'

    threshold = current_app.config['LOW_STOCK_THRESHOLD']
    precio_min = _parse_float(precio_min_raw)
    precio_max = _parse_float(precio_max_raw)

    if precio_min is not None and precio_max is not None and precio_min > precio_max:
        precio_min, precio_max = precio_max, precio_min
        precio_min_raw = f'{precio_min:g}'
        precio_max_raw = f'{precio_max:g}'

    stmt = db.select(Tarjeta).options(
        selectinload(Tarjeta.contenedor),
        selectinload(Tarjeta.compatibilidades),
    )

    if query:
        like = f'%{query}%'
        stmt = stmt.filter(
            db.or_(
                Tarjeta.numero_tarjeta.ilike(like),
                Tarjeta.modelo_pantalla.ilike(like),
                Tarjeta.compatibilidades.any(
                    Compatibilidad.pantalla_compatible.ilike(like),
                ),
                Tarjeta.contenedor.has(
                    Contenedor.nombre.ilike(like),
                ),
            )
        )

    if contenedor_param == 'sin_asignar':
        stmt = stmt.filter(Tarjeta.contenedor_id.is_(None))
    elif contenedor_param:
        cid = _parse_int(contenedor_param)
        if cid is not None:
            stmt = stmt.filter(Tarjeta.contenedor_id == cid)
        else:
            contenedor_param = ''

    if stock_filter == 'con_existencia':
        stmt = stmt.filter(Tarjeta.stock > 0)
    elif stock_filter == 'disponible':
        stmt = stmt.filter(Tarjeta.stock > threshold)
    elif stock_filter == 'bajo':
        stmt = stmt.filter(Tarjeta.stock > 0, Tarjeta.stock <= threshold)
    elif stock_filter == 'agotado':
        stmt = stmt.filter(Tarjeta.stock == 0)
    else:
        stock_filter = ''

    if precio_min is not None:
        stmt = stmt.filter(Tarjeta.precio >= precio_min)
    if precio_max is not None:
        stmt = stmt.filter(Tarjeta.precio <= precio_max)

    order_map = {
        'reciente': (Tarjeta.updated_at.desc(), Tarjeta.id.desc()),
        'numero_asc': (Tarjeta.numero_tarjeta.asc(),),
        'precio_asc': (Tarjeta.precio.asc(), Tarjeta.numero_tarjeta.asc()),
        'precio_desc': (Tarjeta.precio.desc(), Tarjeta.numero_tarjeta.asc()),
        'stock_asc': (Tarjeta.stock.asc(), Tarjeta.numero_tarjeta.asc()),
        'stock_desc': (Tarjeta.stock.desc(), Tarjeta.numero_tarjeta.asc()),
    }
    stmt = stmt.order_by(*order_map[orden])

    pagination = db.paginate(
        stmt,
        page=page,
        per_page=current_app.config['CARDS_PER_PAGE'],
        error_out=False,
    )
    tarjetas = pagination.items
    contenedores = db.session.scalars(
        db.select(Contenedor).order_by(Contenedor.nombre.asc())
    ).all()

    has_advanced_filters = any([
        precio_min is not None,
        precio_max is not None,
        orden != 'reciente',
    ])
    has_any_filter = any([
        bool(query),
        bool(contenedor_param),
        bool(stock_filter),
        precio_min is not None,
        precio_max is not None,
    ])

    return render_template(
        'index.html',
        tarjetas=tarjetas,
        pagination=pagination,
        contenedores=contenedores,
        query=query,
        contenedor_id=contenedor_param,
        stock_filter=stock_filter,
        precio_min=precio_min_raw if precio_min is not None else '',
        precio_max=precio_max_raw if precio_max is not None else '',
        orden=orden,
        sort_options=SORT_OPTIONS,
        vista=vista,
        total=pagination.total,
        has_advanced_filters=has_advanced_filters,
        has_any_filter=has_any_filter,
    )


@tarjetas_bp.route('/tarjetas/nueva', methods=['GET', 'POST'])
def crear():
    """Create a new card."""
    contenedores = db.session.scalars(
        db.select(Contenedor).order_by(Contenedor.nombre.asc())
    ).all()

    if request.method == 'POST':
        form_data = _extract_form_data(request.form)
        numero = form_data['numero_tarjeta']
        modelo = form_data['modelo_pantalla']
        precio = _parse_float(form_data['precio'])
        stock = _parse_int(form_data['stock'])
        contenedor_id = _parse_int(form_data['contenedor_id'])
        compat_list = _parse_compatibilidades(form_data['compatibilidades'])

        # --- Validation ---
        error_msg = None
        if not numero:
            error_msg = 'El número de tarjeta es obligatorio.'
        elif not modelo:
            error_msg = 'El modelo de pantalla es obligatorio.'
        elif precio is None and form_data['precio'] != '':
            error_msg = 'El precio debe ser un número positivo o cero.'
        elif stock is None and form_data['stock'] != '':
            error_msg = 'El stock debe ser un número entero mayor o igual a cero.'
        elif stock is not None and stock < 0:
            error_msg = 'El stock no puede ser negativo.'
        elif db.session.scalar(db.select(Tarjeta).filter_by(numero_tarjeta=numero)):
            error_msg = f'Ya existe una tarjeta registrada con el número "{numero}".'

        if error_msg:
            flash(error_msg, 'error')
            return render_template(
                'tarjeta_form.html',
                contenedores=contenedores,
                form_data=form_data,
            )

        # --- Photo ---
        foto_filename = None
        if 'foto' in request.files and request.files['foto'].filename:
            try:
                foto_filename = _save_photo(request.files['foto'])
            except ValueError as exc:
                flash(str(exc), 'error')
                return render_template(
                    'tarjeta_form.html',
                    contenedores=contenedores,
                    form_data=form_data,
                )

        # --- Create ---
        tarjeta = Tarjeta(
            numero_tarjeta=numero,
            modelo_pantalla=modelo,
            precio=precio if precio is not None else 0.0,
            stock=stock if stock is not None else 0,
            contenedor_id=contenedor_id,
            foto_path=foto_filename,
        )

        for pantalla in compat_list:
            tarjeta.compatibilidades.append(
                Compatibilidad(pantalla_compatible=pantalla),
            )

        db.session.add(tarjeta)
        db.session.commit()

        flash(f'Tarjeta "{numero}" registrada exitosamente.', 'success')
        return redirect(url_for('tarjetas.listar'))

    return render_template('tarjeta_form.html', contenedores=contenedores, form_data=None)


@tarjetas_bp.route('/tarjetas/<int:id>')
def detalle(id):
    """Show card details."""
    tarjeta = db.session.scalar(
        db.select(Tarjeta)
        .options(
            selectinload(Tarjeta.contenedor),
            selectinload(Tarjeta.compatibilidades),
        )
        .filter_by(id=id)
    )
    if tarjeta is None:
        from flask import abort
        abort(404)
    return render_template('tarjeta_detail.html', tarjeta=tarjeta)


@tarjetas_bp.route('/tarjetas/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    """Edit an existing card."""
    tarjeta = db.get_or_404(Tarjeta, id)
    contenedores = db.session.scalars(
        db.select(Contenedor).order_by(Contenedor.nombre.asc())
    ).all()

    if request.method == 'POST':
        form_data = _extract_form_data(request.form)
        numero = form_data['numero_tarjeta']
        modelo = form_data['modelo_pantalla']
        precio = _parse_float(form_data['precio'])
        stock = _parse_int(form_data['stock'])
        contenedor_id = _parse_int(form_data['contenedor_id'])
        compat_list = _parse_compatibilidades(form_data['compatibilidades'])

        error_msg = None
        if not numero:
            error_msg = 'El número de tarjeta es obligatorio.'
        elif not modelo:
            error_msg = 'El modelo de pantalla es obligatorio.'
        elif precio is None and form_data['precio'] != '':
            error_msg = 'El precio debe ser un número positivo o cero.'
        elif stock is None and form_data['stock'] != '':
            error_msg = 'El stock debe ser un número entero mayor o igual a cero.'
        elif stock is not None and stock < 0:
            error_msg = 'El stock no puede ser negativo.'
        else:
            dup = db.session.scalar(
                db.select(Tarjeta).filter(
                    Tarjeta.numero_tarjeta == numero, Tarjeta.id != id,
                )
            )
            if dup:
                error_msg = f'Ya existe otra tarjeta con el número "{numero}".'

        if error_msg:
            flash(error_msg, 'error')
            return render_template(
                'tarjeta_form.html',
                tarjeta=tarjeta,
                contenedores=contenedores,
                form_data=form_data,
            )

        # Validate & save new photo BEFORE deleting old one
        new_photo = None
        if 'foto' in request.files and request.files['foto'].filename:
            try:
                new_photo = _save_photo(request.files['foto'])
            except ValueError as exc:
                flash(str(exc), 'error')
                return render_template(
                    'tarjeta_form.html',
                    tarjeta=tarjeta,
                    contenedores=contenedores,
                    form_data=form_data,
                )

        if new_photo:
            _delete_photo(tarjeta.foto_path)
            tarjeta.foto_path = new_photo
        elif request.form.get('remove_foto') == '1':
            _delete_photo(tarjeta.foto_path)
            tarjeta.foto_path = None

        tarjeta.numero_tarjeta = numero
        tarjeta.modelo_pantalla = modelo
        tarjeta.precio = precio if precio is not None else 0.0
        tarjeta.stock = stock if stock is not None else 0
        tarjeta.contenedor_id = contenedor_id

        # Rebuild compatibilities
        db.session.execute(
            db.delete(Compatibilidad).where(Compatibilidad.tarjeta_id == id)
        )
        for pantalla in compat_list:
            tarjeta.compatibilidades.append(
                Compatibilidad(pantalla_compatible=pantalla),
            )

        db.session.commit()
        flash(f'Tarjeta "{numero}" actualizada exitosamente.', 'success')
        return redirect(url_for('tarjetas.detalle', id=id))

    return render_template(
        'tarjeta_form.html',
        tarjeta=tarjeta,
        contenedores=contenedores,
        form_data=None,
    )


@tarjetas_bp.route('/tarjetas/<int:id>/eliminar', methods=['POST'])
def eliminar(id):
    """Delete a card and its photo."""
    tarjeta = db.get_or_404(Tarjeta, id)
    _delete_photo(tarjeta.foto_path)
    numero = tarjeta.numero_tarjeta
    db.session.delete(tarjeta)
    db.session.commit()
    flash(f'Tarjeta "{numero}" eliminada del inventario.', 'success')
    return redirect(url_for('tarjetas.listar'))


@tarjetas_bp.route('/tarjetas/<int:id>/stock', methods=['POST'])
def actualizar_stock(id):
    """Quick stock increment / decrement (supports AJAX JSON + form fallback)."""
    tarjeta = db.get_or_404(Tarjeta, id)
    action = request.form.get('action')

    if action == 'increment':
        tarjeta.stock += 1
    elif action == 'decrement' and tarjeta.stock > 0:
        tarjeta.stock -= 1

    db.session.commit()

    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('Accept', '')
    )
    if is_ajax:
        estado, estado_label = _stock_state(tarjeta.stock)
        return jsonify({
            'ok': True,
            'id': tarjeta.id,
            'stock': tarjeta.stock,
            'estado': estado,
            'estado_label': estado_label,
        })

    return redirect(request.referrer or url_for('tarjetas.listar'))


@tarjetas_bp.route('/uploads/tarjetas/<filename>')
def uploaded_file(filename):
    """Serve uploaded card photos."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
