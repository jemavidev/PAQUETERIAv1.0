# 109 — Código de acceso (columna Cliente) también con fondo redondeado y color

**Pedido original (cliente):**
"no entiendo y que hiciste con lo que te pedi en la vista /paquetes,
especificamente la columna Clientes, necesito que este codigo se vea asi
como acabas de hacer con los otros, bordes redondeados y con un fondo en
ese background, me colaboras?"

**Status:** implementado

## Contexto

[[107]] solo cubrió la parte de "cliqueable → `/consultar?q=`" del código
de acceso en la columna Cliente -- no tocó su estilo visual (seguía sin
fondo, decisión explícita de [[81]]/issue 15 del 2026-08-15: "el chip de
fondo ámbar sólido quedaba demasiado intenso"). El cliente ahora pide
explícitamente el tratamiento de fondo+borde redondeado que se le dio al
chip de duración en [[108]] -- MISMO patrón (fondo suave `bg-{color}-100`
+ borde, no el fondo sólido que se había retirado antes), no una
repetición de aquel error.

## Implementación

- `_resultados.html`: el diccionario de colores por estado (antes
  duplicado como `duracion_colores`, local al bloque del modal) se sube a
  `estado_colores`, declarado UNA vez cerca del inicio del archivo (junto
  a `filtros_vigentes`) -- se usa ahora en DOS lugares del mismo archivo
  (el chip de duración del modal Y el código de acceso de la tabla),
  ambos leen el mismo `p.estado.value`, cero riesgo de que se
  desincronicen entre sí.
- El `<a>` del código de acceso (columna Cliente) gana
  `{{ estado_colores.get(p.estado.value, ...) }} border rounded-full
  px-2.5 py-1` -- mismo tratamiento "fondo suave" del design system que
  ya usan `badge()` y el chip de duración, conservando `font-mono
  font-extrabold` (lo que lo distingue como código, no como badge de
  estado).

## Verificación

- `tests/web/test_packages.py`: test nuevo confirma que el `<a>` del
  código de acceso lleva la clase de color correspondiente al Estado del
  paquete.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
