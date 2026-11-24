# 📋 Compaye Tarjetas

Sistema de inventario digital para tarjetas de pantallas — diseñado para funcionar **100% offline** en equipos de bajos recursos.

## ✨ Funcionalidades

- **CRUD completo** de tarjetas (crear, buscar, editar, eliminar)
- **Búsqueda** por número, modelo o pantalla compatible
- **Filtros** por contenedor y disponibilidad de stock
- **Fotos** de cada tarjeta (subida y redimensionado automático)
- **Gestión de stock** con botones rápidos +/-
- **Contenedores** para organizar ubicación física
- **Interfaz accesible** diseñada para usuarios de 50+ años

## 🛠️ Requisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/yopAxl/compaye-tarjetas.git
cd compaye-tarjetas

# 2. Crear entorno virtual
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python app.py
```

Abrir el navegador en: **http://localhost:5000**

## 📂 Estructura del Proyecto

```
compaye-tarjetas/
├── app.py                  # Punto de entrada
├── config.py               # Configuración
├── requirements.txt        # Dependencias
├── models/                 # Modelos de datos (SQLAlchemy)
│   ├── tarjeta.py
│   └── contenedor.py
├── routes/                 # Rutas / Endpoints
│   ├── tarjetas.py
│   └── contenedores.py
├── templates/              # Plantillas HTML
├── static/                 # CSS, JS, imágenes
├── uploads/                # Fotos subidas (generado automáticamente)
└── database/               # Base de datos SQLite (generado automáticamente)
```

## 💾 Respaldos

La base de datos es un archivo único en `database/compaye.db`. Para respaldarlo, simplemente copie ese archivo y la carpeta `uploads/`.

## 🌐 Uso en Red Local (LAN)

Para que otros equipos en la red accedan al sistema, cambiar en `app.py`:

```python
app.run(host='0.0.0.0', port=5000)
```

## 📄 Licencia

Uso interno — ComPaye © 2026
