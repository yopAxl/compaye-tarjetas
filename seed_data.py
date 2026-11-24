# -*- coding: utf-8 -*-
"""Script para cargar datos de prueba en la base de datos de Compaye Tarjetas.

Ejecutar dentro del entorno virtual:
    python seed_data.py

El script crea algunos contenedores y tarjetas de ejemplo. Las rutas de foto son
marcadores de posición; puedes reemplazarlas con imágenes reales.
"""
import os
from datetime import datetime

from app import create_app
from models import db
from models.tarjeta import Tarjeta, Compatibilidad
from models.contenedor import Contenedor

app = create_app()

with app.app_context():
    # --- Contenedores -------------------------------------------------------
    cont1 = Contenedor(nombre="Caja A", descripcion="Caja de madera en la oficina")
    cont2 = Contenedor(nombre="Estante B", descripcion="Estante metálico del almacén")
    db.session.add_all([cont1, cont2])
    db.session.commit()

    # --- Tarjetas de prueba -------------------------------------------------
    tarjetas = [
        {
            "numero_tarjeta": "TARJ-001",
            "modelo_pantalla": "Samsung QLED 55" ,
            "precio": 12500.00,
            "foto_path": "uploads/TARJ-001.jpg",
            "stock": 5,
            "contenedor": cont1,
            "compatibilidades": ["Samsung 55", "Samsung 65"]
        },
        {
            "numero_tarjeta": "TARJ-002",
            "modelo_pantalla": "LG OLED 48",
            "precio": 9800.50,
            "foto_path": "uploads/TARJ-002.jpg",
            "stock": 3,
            "contenedor": cont2,
            "compatibilidades": ["LG 48", "LG 55"]
        },
        {
            "numero_tarjeta": "TARJ-003",
            "modelo_pantalla": "Sony Bravia 65",
            "precio": 15800.75,
            "foto_path": "uploads/TARJ-003.jpg",
            "stock": 2,
            "contenedor": cont1,
            "compatibilidades": ["Sony 65", "Sony 75"]
        },
        {
            "numero_tarjeta": "TARJ-004",
            "modelo_pantalla": "Panasonic 32",
            "precio": 4500.00,
            "foto_path": "uploads/TARJ-004.jpg",
            "stock": 10,
            "contenedor": cont2,
            "compatibilidades": ["Panasonic 32"]
        },
    ]

    for t in tarjetas:
        tarjeta = Tarjeta(
            numero_tarjeta=t["numero_tarjeta"],
            modelo_pantalla=t["modelo_pantalla"],
            precio=t["precio"],
            foto_path=t["foto_path"],
            stock=t["stock"],
            contenedor=t["contenedor"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(tarjeta)
        db.session.flush()  # obtener id antes de crear compatibilidades
        for comp in t["compatibilidades"]:
            db.session.add(Compatibilidad(tarjeta_id=tarjeta.id, pantalla_compatible=comp))
    db.session.commit()
    print("Datos de prueba insertados exitosamente.")
