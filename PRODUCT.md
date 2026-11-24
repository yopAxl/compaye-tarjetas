# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Personal de mostrador y almacén (50+ años):** Consultan rápido si hay una tarjeta en existencia, verifican compatibilidad con pantallas, consultan su precio en pesos mexicanos (MXN) y ven en qué contenedor físico está guardada para no buscar a mano entre cajas.
- **Dueño / Jefe del taller de electrónica:** Revisa el estado general del inventario, identifica tarjetas agotadas o con bajo stock para reabastecer, y valida el valor total y la distribución por contenedores.

## Product Purpose

Digitalizar el inventario físico de tarjetas de pantallas de un negocio de electrónica ("ComPaye Tarjetas") para eliminar la búsqueda manual agotadora en cajas y estantes, concentrando número de tarjeta, modelo de pantalla, pantallas compatibles, precio (MXN), fotografía, stock y ubicación física (contenedor) en un solo sistema local rápido y claro.

El éxito significa que cualquier trabajador de 50+ años pueda encontrar una tarjeta por número, modelo, compatibilidad, precio o contenedor en segundos, actualizar el stock con un clic sin perder su lugar en la pantalla, y revisar alertas del almacén sin depender de internet.

## Positioning

Inventario local offline-first diseñado específicamente para talleres de reparación de pantallas y electrónica: combina búsqueda por compatibilidad múltiple entre modelos de pantalla, ubicación física exacta por contenedor, fotografía local redimensionada y operación cómoda para vista madura en equipos de bajos recursos, con migración directa a red local o servidor PostgreSQL cuando el negocio lo decida.

## Operating Context

- **Entorno físico:** Mostrador y taller de electrónica con computadora de escritorio de bajos recursos (≤ 4 GB RAM) y conectividad intermitente o sin internet la mayor parte del tiempo.
- **Flujo diario:** Al abrir la aplicación se entra directo al **Buscador / Inventario de Tarjetas**. Desde la barra superior se accede a **Estadísticas** (dashboard resumen) y **Contenedores** (catálogo de ubicaciones físicas).
- **Respaldo y portabilidad:** Toda la información vive localmente en `database/compaye.db` y `uploads/tarjetas/`, lista para respaldarse copiando archivos o escalarse a red local (`0.0.0.0`) y servidor.

## Capabilities and Constraints

- **Stack establecido:** Python 3 + Flask + Flask-SQLAlchemy + SQLite + Pillow + Waitress + Jinja2 + HTML/CSS/JavaScript vanilla (cero dependencias de Node.js, CDN o internet en tiempo de ejecución).
- **Campos por tarjeta:** `numero_tarjeta` (único), `modelo_pantalla`, `compatibilidades` (lista uno-a-muchos), `precio` (MXN `$`), `foto_path` (local, redimensionada con orientación EXIF corregida), `stock` (entero ≥ 0), `contenedor_id` (opcional; permite tarjetas sin asignar).
- **Reglas de stock:** `0` = Agotado, `1–2` = Bajo stock, `≥ 3` = Disponible.
- **Búsqueda y vistas (V2):** Búsqueda por texto libre + filtros combinados por contenedor (incluyendo "Sin asignar"), estado de stock, rango de precio (mínimo/máximo) y ordenamiento; vista alternable entre Tarjetas con foto y Tabla compacta de inventario.
- **Estadísticas (V3):** Dashboard con totales del inventario, valor en MXN, alertas de tarjetas agotadas/bajo stock y distribución por contenedor.

## Brand Commitments

- **Nombre:** ComPaye Tarjetas.
- **Lenguaje visual confirmado:** Tonos claros y cálidos de alto contraste (fondo papel cálido y tarjetas blancas con acento azul sobrio), **sin colores chillantes/neón** y **sin tipografías diminutas**, con iconografía limpia y profesional.

## Evidence on Hand

- Repositorio local con MVP funcional en Flask/SQLite (`app.py`, `models/`, `routes/`, `templates/`, `static/`).
- Especificación técnica documentada en `propuesta-tecnica.md`.
- Sin datos productivos cargados aún en `database/compaye.db` (0 tarjetas, 0 contenedores al momento de registro; cualquier dato de prueba debe quedar claro como de demostración o eliminarse tras pruebas).

## Product Principles

1. **Velocidad de búsqueda ante todo:** Entrar directo al inventario con el buscador visible arriba y filtros claros que preservan la vista elegida.
2. **Cero pérdida de trabajo:** Los formularios conservan los datos capturados si ocurre un error de validación y los ajustes rápidos de stock (`+/-`) no hacen saltar la página ni recargan la vista innecesariamente.
3. **Claridad visual para vista madura:** Tipografía amplia (18 px base), números tabulares en precios/cantidades, contrastes WCAG AA/AAA reales y etiquetas persistentes en español claro.
4. **Autonomía offline y peso pluma:** Cero fuentes externas, CDNs, librerías JS de gráficas pesadas o pasos de compilación; todo funciona al instante en equipo modesto sin internet.

## Accessibility & Inclusion

- **Audiencia principal 50+ años:** Tipografía base ≥ 18 px (16 px mínimo absoluto en etiquetas secundarias), alto contraste (≥ 4.5:1 texto normal, ≥ 3:1 controles y bordes), controles táctiles/clicables de al menos 48 px de altura, estados de foco visibles (`:focus-visible`), soporte de navegación por teclado, lectura en zoom 200% y respeto a `prefers-reduced-motion`.
- **No depender solo del color:** Todo estado de stock (Disponible, Bajo stock, Agotado) combina texto explícito, icono o indicador claro y color con contraste verificado.
