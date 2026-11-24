"""Routes for container (contenedor) CRUD operations."""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import func

from models import db
from models.contenedor import Contenedor
from models.tarjeta import Tarjeta

contenedores_bp = Blueprint('contenedores', __name__)


@contenedores_bp.route('/')
def listar():
    """List all containers with card counts and total stock pieces."""
    rows = (
        db.session.query(
            Contenedor,
            func.count(Tarjeta.id).label('modelos_count'),
            func.coalesce(func.sum(Tarjeta.stock), 0).label('piezas_count'),
        )
        .outerjoin(Tarjeta, Tarjeta.contenedor_id == Contenedor.id)
        .group_by(Contenedor.id)
        .order_by(Contenedor.nombre.asc())
        .all()
    )

    contenedores_info = [
        {
            'contenedor': row[0],
            'modelos_count': int(row[1] or 0),
            'piezas_count': int(row[2] or 0),
        }
        for row in rows
    ]
    sin_asignar_count = db.session.scalar(
        db.select(func.count(Tarjeta.id)).filter(Tarjeta.contenedor_id.is_(None))
    ) or 0

    return render_template(
        'contenedores.html',
        contenedores_info=contenedores_info,
        sin_asignar_count=sin_asignar_count,
    )


@contenedores_bp.route('/crear', methods=['POST'])
def crear():
    """Create a new container."""
    nombre = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if not nombre:
        flash('El nombre del contenedor es obligatorio.', 'error')
        return redirect(url_for('contenedores.listar'))

    if db.session.scalar(db.select(Contenedor).filter_by(nombre=nombre)):
        flash(f'Ya existe un contenedor llamado "{nombre}".', 'error')
        return redirect(url_for('contenedores.listar'))

    contenedor = Contenedor(nombre=nombre, descripcion=descripcion)
    db.session.add(contenedor)
    db.session.commit()

    flash(f'Contenedor "{nombre}" creado exitosamente.', 'success')
    return redirect(url_for('contenedores.listar'))


@contenedores_bp.route('/<int:id>/editar', methods=['POST'])
def editar(id):
    """Update an existing container."""
    contenedor = db.get_or_404(Contenedor, id)
    nombre = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if not nombre:
        flash('El nombre del contenedor es obligatorio.', 'error')
        return redirect(url_for('contenedores.listar'))

    dup = db.session.scalar(
        db.select(Contenedor).filter(
            Contenedor.nombre == nombre, Contenedor.id != id,
        )
    )
    if dup:
        flash(f'Ya existe otro contenedor llamado "{nombre}".', 'error')
        return redirect(url_for('contenedores.listar'))

    contenedor.nombre = nombre
    contenedor.descripcion = descripcion
    db.session.commit()

    flash(f'Contenedor "{nombre}" actualizado.', 'success')
    return redirect(url_for('contenedores.listar'))


@contenedores_bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar(id):
    """Delete a container (only if it has no cards assigned)."""
    contenedor = db.get_or_404(Contenedor, id)

    if contenedor.tarjetas:
        flash(
            f'No se puede eliminar "{contenedor.nombre}" porque tiene '
            f'{len(contenedor.tarjetas)} tarjeta(s) asignada(s). '
            f'Reasigne las tarjetas primero.',
            'error',
        )
        return redirect(url_for('contenedores.listar'))

    nombre = contenedor.nombre
    db.session.delete(contenedor)
    db.session.commit()

    flash(f'Contenedor "{nombre}" eliminado.', 'success')
    return redirect(url_for('contenedores.listar'))
