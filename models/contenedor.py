from models import db


class Contenedor(db.Model):
    """Physical container where cards are stored (box, shelf, drawer, etc.)."""

    __tablename__ = 'contenedores'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f'<Contenedor {self.nombre}>'
