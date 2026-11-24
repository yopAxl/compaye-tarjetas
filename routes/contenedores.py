"""Routes for container (contenedor) CRUD operations."""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from models import db
from models.contenedor import Contenedor

contenedores_bp = Blueprint('contenedores', __name__)


@contenedores_bp.route('/')
def listar():
    """List all containers with their card counts."""
    contenedores = Contenedor.query.order_by(Contenedor.nombre).all()
    return render_template('contenedores.html', contenedores=contenedores)


@contenedores_bp.route('/crear', methods=['POST'])
def crear():
    """Create a new container."""
    nombre = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if not nombre:
        flash('El nombre del contenedor es obligatorio.', 'error')
        return redirect(url_for('contenedores.listar'))

    if Contenedor.query.filter_by(nombre=nombre).first():
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
    contenedor = Contenedor.query.get_or_404(id)
    nombre = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if not nombre:
        flash('El nombre del contenedor es obligatorio.', 'error')
        return redirect(url_for('contenedores.listar'))

    dup = Contenedor.query.filter(
        Contenedor.nombre == nombre, Contenedor.id != id,
    ).first()
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
    contenedor = Contenedor.query.get_or_404(id)

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
