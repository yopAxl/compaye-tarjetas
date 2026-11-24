# Surface Brief — Dashboard de Estadísticas (`/estadisticas`)

- **Scope & Mode:** `Operate` (tablero de lectura rápida y acciones de reposición para dueño y encargados).
- **Audience & Job:** Jefe/encargado (50+ años) revisando de un vistazo cuántas tarjetas y piezas hay, el valor total del inventario en MXN, qué tarjetas requieren resurtido urgente (agotadas o ≤ 2 piezas) y cómo se reparten entre contenedores físicos.
- **Unresolved Decisions:** Ninguna; umbral de bajo stock (`≤ 2`) y moneda (`MXN $`) confirmados por el usuario.

## Direction contract

- **THESIS:** Un tablero operativo sobrio, sin gráficas decorativas ni colores estridentes, que convierte los números del almacén en decisiones inmediatas: valor total, alertas accionables de reposición y ocupación por contenedor con enlace directo al inventario filtrado.
- **OWN-WORLD:** Comparte el mismo sistema cálido de ComPaye Tarjetas (`#F5F3EF` fondo, `#FFFFFF` tarjetas de métricas con borde `#D2D7DC`, acento `#1B5E8A`, números tabulares amplios y barras de proporción CSS puras de alto contraste, cero dependencias JS externas).
- **STORY:** Al entrar a Estadísticas, el usuario ve al instante las 4 métricas clave (Modelos registrados, Piezas en stock, Valor total MXN, Alertas de stock), revisa debajo la lista accionable de tarjetas agotadas/bajo stock y la tabla/barras de contenedores para hacer clic directo en cualquier contenedor o tarjeta.
- **FIRST VIEWPORT:** Cabecera de página (`Estadísticas del Inventario` + botón rápido hacia `Ver todas las tarjetas`), franja de 4 tarjetas KPI con cifras tabulares de gran escala y etiquetas claras, seguida de las dos columnas operativas: Alertas de stock (0–2 piezas) y Distribución por contenedor.
- **FORM:** Nueva superficie Operate dentro del sistema visual establecido de ComPaye Tarjetas; `seed: none (unavailable)` — el ejecutable offline de Impeccable no pudo correr en este entorno sin red.
- **FINISH:** unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.
