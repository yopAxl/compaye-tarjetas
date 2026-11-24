"""Routes for inventory statistics dashboard (V3)."""

from flask import Blueprint, current_app, redirect, render_template, url_for
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from models import db
from models.contenedor import Contenedor
from models.tarjeta import Tarjeta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def dashboard_alias():
    """Redirect legacy /dashboard URL to /estadisticas."""
    return redirect(url_for('dashboard.resumen'))


@dashboard_bp.route('/estadisticas')
def resumen():
    """Render inventory statistics, stock alerts, and container breakdown."""
    threshold = current_app.config['LOW_STOCK_THRESHOLD']

    # Overall inventory aggregates
    totals = db.session.query(
        func.count(Tarjeta.id),
        func.coalesce(func.sum(Tarjeta.stock), 0),
        func.coalesce(func.sum(Tarjeta.precio * Tarjeta.stock), 0.0),
    ).one()

    total_modelos = int(totals[0] or 0)
    total_piezas = int(totals[1] or 0)
    valor_total = float(totals[2] or 0.0)

    conteo_agotado = db.session.scalar(
        db.select(func.count(Tarjeta.id)).filter(Tarjeta.stock == 0)
    ) or 0
    conteo_bajo = db.session.scalar(
        db.select(func.count(Tarjeta.id)).filter(
            Tarjeta.stock > 0,
            Tarjeta.stock <= threshold,
        )
    ) or 0
    conteo_disponible = db.session.scalar(
        db.select(func.count(Tarjeta.id)).filter(Tarjeta.stock > threshold)
    ) or 0
    total_alertas = conteo_agotado + conteo_bajo

    # Priority stock alerts (exhausted first, then low stock)
    alertas_tarjetas = db.session.scalars(
        db.select(Tarjeta)
        .options(selectinload(Tarjeta.contenedor))
        .filter(Tarjeta.stock <= threshold)
        .order_by(Tarjeta.stock.asc(), Tarjeta.updated_at.desc())
        .limit(15)
    ).all()

    # Distribution by container
    contenedores_rows = (
        db.session.query(
            Contenedor,
            func.count(Tarjeta.id).label('modelos'),
            func.coalesce(func.sum(Tarjeta.stock), 0).label('piezas'),
            func.coalesce(func.sum(Tarjeta.precio * Tarjeta.stock), 0.0).label('valor'),
        )
        .outerjoin(Tarjeta, Tarjeta.contenedor_id == Contenedor.id)
        .group_by(Contenedor.id)
        .order_by(func.coalesce(func.sum(Tarjeta.stock), 0).desc(), Contenedor.nombre.asc())
        .all()
    )

    distribucion = []
    for contenedor, modelos, piezas, valor in contenedores_rows:
        piezas_int = int(piezas or 0)
        pct = round((piezas_int / total_piezas) * 100) if total_piezas > 0 else 0
        distribucion.append({
            'id': contenedor.id,
            'nombre': contenedor.nombre,
            'descripcion': contenedor.descripcion,
            'modelos': int(modelos or 0),
            'piezas': piezas_int,
            'valor': float(valor or 0.0),
            'pct': pct,
            'filter_param': str(contenedor.id),
        })

    # Include unassigned cards if any exist
    sin_asignar = db.session.query(
        func.count(Tarjeta.id),
        func.coalesce(func.sum(Tarjeta.stock), 0),
        func.coalesce(func.sum(Tarjeta.precio * Tarjeta.stock), 0.0),
    ).filter(Tarjeta.contenedor_id.is_(None)).one()

    sin_modelos = int(sin_asignar[0] or 0)
    if sin_modelos > 0:
        sin_piezas = int(sin_asignar[1] or 0)
        pct = round((sin_piezas / total_piezas) * 100) if total_piezas > 0 else 0
        distribucion.append({
            'id': None,
            'nombre': 'Sin contenedor asignado',
            'descripcion': 'Tarjetas pendientes de ubicar',
            'modelos': sin_modelos,
            'piezas': sin_piezas,
            'valor': float(sin_asignar[2] or 0.0),
            'pct': pct,
            'filter_param': 'sin_asignar',
        })

    # Recent updates
    recientes = db.session.scalars(
        db.select(Tarjeta)
        .options(selectinload(Tarjeta.contenedor))
        .order_by(Tarjeta.updated_at.desc(), Tarjeta.id.desc())
        .limit(6)
    ).all()

    return render_template(
        'dashboard.html',
        total_modelos=total_modelos,
        total_piezas=total_piezas,
        valor_total=valor_total,
        conteo_disponible=conteo_disponible,
        conteo_bajo=conteo_bajo,
        conteo_agotado=conteo_agotado,
        total_alertas=total_alertas,
        total_contenedores=len(contenedores_rows),
        alertas_tarjetas=alertas_tarjetas,
        distribucion=distribucion,
        recientes=recientes,
    )
