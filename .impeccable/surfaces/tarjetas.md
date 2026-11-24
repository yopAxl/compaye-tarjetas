# Surface Brief — Inventario y Buscador de Tarjetas (`/tarjetas`)

- **Scope & Mode:** `Operate` (surface principal de consulta y gestión diaria al abrir la app).
- **Audience & Job:** Personal 50+ años en mostrador/almacén buscando una tarjeta por número, modelo, pantalla compatible, rango de precio o contenedor físico, ajustando stock rápidamente y alternando entre vista visual con foto y tabla escaneable.
- **Unresolved Decisions:** Ninguna; flujo y reglas de umbral confirmados por el usuario.

## Direction contract

- **THESIS:** Un catálogo de taller limpio y legible sobre papel hueso cálido que prioriza el buscador inmediato, la conmutación Tarjetas/Tabla y las alertas de stock con contraste real, rechazando paneles saturados con emojis informales o tipografías minúsculas.
- **OWN-WORLD:** Superficies blancas (`#FFFFFF`) nítidas con bordes definidos (`#8492A1` en inputs, `#D2D7DC` en contenedores) sobre fondo cálido (`#F5F3EF`), tinta azul-pizarra profunda (`#1C2833`), acento único azul acero (`#1B5E8A`) e iconografía SVG lineal uniforme (`stroke-width: 2`).
- **STORY:** El usuario abre la app, encuentra la tarjeta buscada combinando texto, contenedor, stock y rango de precio MXN, cambia a vista Tabla si necesita comparar varias rápido, y ajusta el stock `+/-` al instante sin perder su posición.
- **FIRST VIEWPORT:** Cabecera pegajosa limpia (`ComPaye Tarjetas` + 3 pestañas: `Tarjetas`, `Estadísticas`, `Contenedores`), barra de título con botón primario `+ Nueva Tarjeta`, panel de búsqueda con barra principal + filtros combinados (Contenedor, Stock, Precio mín/máx, Orden) + selector `Tarjetas | Tabla`, y la primera fila de resultados visibles sin desplazamiento excesivo.
- **FORM:** Extensión y pulido de superficie existente (modo Operate) manteniendo el mundo cálido de alto contraste aprobado; `seed: none (unavailable)` — el ejecutable offline de Impeccable no pudo correr en este entorno sin red.
- **FINISH:** unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.
