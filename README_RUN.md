# Cómo ejecutar el proyecto Compaye Tarjetas (Windows)

## Requisitos previos
- **Python 3.12+** instalado y añadido al `PATH`.
- **PowerShell** (se asume que está disponible en Windows).
- **Entorno virtual** (usaremos el que ya está creado en el repositorio).
- **Microsoft Edge** instalado (se usa para generar capturas de pantalla con el script `capture_review.py`).

## Paso a paso

1. **Abrir PowerShell en la carpeta del proyecto**
   ```powershell
   cd "C:\Users\AxelE\OneDrive\Escritorio\repositorios\compaye-tarjetas"
   ```

2. **Activar el entorno virtual**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   Si la política de ejecución impide activar scripts, permite la ejecución temporalmente:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\Activate.ps1
   ```

3. **Instalar dependencias**
   ```powershell
   pip install -r requirements.txt
   ```
   Esto instalará Flask, SQLAlchemy y demás paquetes necesarios.

4. **Inicializar la base de datos (SQLite)**
   - La primera vez que se ejecute la aplicación Flask, se creará automáticamente el archivo `instance/compaye.db` si no existe.
   - Si el proyecto usa Flask‑Migrate, puedes ejecutar:
     ```powershell
     set FLASK_APP=app.py
     flask db upgrade
     ```
   - En nuestro caso, basta con iniciar la app; la base se genera al arrancar.

5. **Ejecutar el servidor de desarrollo**
   ```powershell
   set FLASK_APP=app.py
   flask run
   # o alternativamente
   python -m flask run
   ```
   El servidor escuchará en `http://127.0.0.1:5000/`. Abre el navegador y verifica que la aplicación carga.

6. **Opcional: Ejecutar pruebas**
   ```powershell
   python -m unittest discover -s tests -v
   ```
   Todas las pruebas deben pasar sin errores.

7. **Opcional: Generar capturas de pantalla con Impeccable**
   El script `capture_review.py` usa Microsoft Edge en modo headless.
   ```powershell
   python capture_review.py
   ```
   Las imágenes se guardarán en `.impeccable\review\`.

## Notas adicionales
- **Entorno de desarrollo**: Si deseas recargar automáticamente al guardar cambios, establece la variable de entorno `FLASK_ENV=development` antes de ejecutar `flask run`.
- **Persistencia de datos**: El archivo SQLite queda en la carpeta `instance`. Puedes respaldarlo copiándolo a otro lugar.
- **Ejecutar sin internet**: Todas las operaciones anteriores funcionan completamente offline después de haber instalado las dependencias una vez.

---
*Este documento se añadió como `README_RUN.md` en el repositorio para que cualquier colaborador pueda seguir los pasos rápidamente.*