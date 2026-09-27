# 01 — Tablero de punta a punta: 3 zonas + tarjeta de Ingresos

**What to build:** `/administracion/estadisticas-cobro` deja de ser listas y pasa a ser el tablero de
tarjetas de la spec (`.scratch/estadisticas-cobro-dashboard/spec.md`, variante C del prototipo en la
rama `prototipo/estadisticas-cobro-dashboard`): la barra de filtros de siempre arriba, y debajo tres
zonas apiladas con su carril vertical de color — Panorama (azul), Ahora (ámbar) y Periodo seleccionado
(verde) —, cada una con su etiqueta de zona y sin encabezados de sección. Este ticket es el tracer
bullet: fija toda la arquitectura (servicio de dominio con reloj inyectable, hora de Colombia, ruta
delgada, actualización en vivo, retiro de las listas, CSS recompilado) con solo **una tarjeta real por
zona fija** — el resto de las tarjetas de Panorama y Ahora quedan para tickets posteriores, y toda la
zona Periodo (salvo su encabezado y el mecanismo de actualización en vivo) también.

Las tres tarjetas que sí quedan completas en este ticket:

- **Panorama → Ingresos**: Hoy | Semana | Mes en una sola tarjeta, sin variación ni minigráfico todavía
  (eso es el ticket 08).
- **Periodo seleccionado → Total de ingresos**: responde a los tres filtros (atajo de fecha, Tipo,
  Cobrado/Anulado); sin ningún atajo activo, todos los datos existentes.
- La zona Ahora queda con su carril y su etiqueta, sin tarjetas todavía (ticket 09).

**Blocked by:** None — can start immediately.

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: 1a4d74b)

- [ ] La pantalla ya no tiene los campos "Desde"/"Hasta" ni el `<select>` de Usuario, ni las tres listas
      paginadas (por cliente/apartamento, por usuario, serie diaria); solo Admin puede verla (sin sesión
      redirige a login; un Operador recibe 403).
- [ ] Se ve el carril vertical azul de Panorama, el ámbar de Ahora (vacío) y el verde de Periodo
      seleccionado, en ese orden, sin encabezados de texto por sección.
- [ ] "Ingresos" (Panorama) muestra Hoy, Esta semana y Este mes, calculados en hora de Colombia
      (UTC-5 fijo): la tarjeta no cambia al tocar ningún filtro de la barra.
- [ ] Un nuevo servicio de dominio expone la consulta del tablero y recibe el instante "ahora" como
      parámetro (no lee el reloj del sistema por su cuenta) — hay una prueba de dominio, contra Postgres
      real, que fija ese instante justo antes y justo después de la medianoche local y de las 19:00 UTC,
      y confirma que "Hoy" cae del lado correcto en ambos casos.
- [ ] "Total de ingresos" (Periodo seleccionado) sin ningún atajo de fecha activo sale con TODOS los
      cobros existentes; al activar un atajo se acota a ese rango (probado con "Este mes" y con "Último
      año"); al activar Tipo o Cobrado/Anulado, la cifra se acota también.
- [ ] Encima de "Total de ingresos" se ven los chips de los filtros activos (ej. "Este mes" · "Anulado"),
      o "Todos los datos" cuando ninguno está activo.
- [ ] Cambiar cualquier filtro actualiza solo la zona Periodo seleccionado sin recargar la página
      (mismo mecanismo de petición en segundo plano que ya usaba la pantalla).
- [ ] Un valor de filtro desconocido o inválido en la URL se ignora en silencio (sigue dando 200, nunca
      400).
- [ ] Con la base de datos vacía (sin paquetes ni cobros) el tablero carga sin error y muestra $0 en
      ambas tarjetas de Ingresos.
- [ ] El CSS de Tailwind se recompiló y se commiteó con las clases nuevas del tablero (el deploy no lo
      recompila).
- [ ] Las pruebas de la ruta web para esta pantalla usan únicamente este servicio nuevo (aunque el
      servicio de estadísticas anterior siga existiendo y en uso mientras tanto — su retiro es el
      ticket 17).
