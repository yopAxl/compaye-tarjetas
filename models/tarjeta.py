from datetime import datetime, timezone

from models import db


class Tarjeta(db.Model):
    """Represents a screen/display circuit board card in inventory."""

    __tablename__ = 'tarjetas'

    id = db.Column(db.Integer, primary_key=True)
    numero_tarjeta = db.Column(
        db.String(100), unique=True, nullable=False, index=True,
    )
    modelo_pantalla = db.Column(db.String(200), nullable=False, index=True)
    precio = db.Column(db.Float, nullable=False, default=0.0)
    foto_path = db.Column(db.String(500), nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=0)
    contenedor_id = db.Column(
        db.Integer, db.ForeignKey('contenedores.id'), nullable=True,
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    contenedor = db.relationship(
        'Contenedor', backref=db.backref('tarjetas', lazy=True),
    )
    compatibilidades = db.relationship(
        'Compatibilidad',
        backref='tarjeta',
        lazy=True,
        cascade='all, delete-orphan',
    )

    def __repr__(self):
        return f'<Tarjeta {self.numero_tarjeta}>'


class Compatibilidad(db.Model):
    """A screen model that a card is compatible with."""

    __tablename__ = 'compatibilidades'

    id = db.Column(db.Integer, primary_key=True)
    tarjeta_id = db.Column(
        db.Integer, db.ForeignKey('tarjetas.id'), nullable=False,
    )
    pantalla_compatible = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Compatibilidad {self.pantalla_compatible}>'
