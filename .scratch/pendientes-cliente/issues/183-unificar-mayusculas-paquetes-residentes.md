# 183 — Unificar tratamiento de mayúsculas entre `/paquetes` y `/residentes`

**Pedido original:** "realiza ahora la unificacion de las vistas /paquetes y /residentes para
que por ejemplo las mayusculas sean en los mismos puntos o solo unifica a una de las 2"

**Status:** implementado

## Diagnóstico

Auditoría a fondo de todos los puntos donde aparecen mayúsculas en ambas vistas (columnas de
tabla, encabezados, badges, nombres):

- **Nombres (`Persona.nombre`, `Paquete.recipient_name`, `Ocupante.nombre`, etc.)**: YA
  unificados de forma no obvia -- TODOS pasan por la misma función `texto.normalizar_nombre()`
  (mayúsculas + espacios colapsados) en el servidor, sin importar por cuál vista/formulario
  entren. Sin gap.
- **Encabezados de tabla** (`<thead>`): ambas vistas usan la misma clase `uppercase
  tracking-wide` sobre el texto Sentence-case del template -- mismo mecanismo, mismo resultado
  visual.
- **Badges** (`badge()`/`badge_ocupante()`, componente compartido `_badge.html`): mismo
  componente, casing idéntico por construcción.
- **Única diferencia real encontrada**: la columna Torre/Apartamento-equivalente. `/paquetes`
  fuerza mayúsculas por CSS (`class="... uppercase"`) sobre `direccion_corta` (que en Python es
  Title Case: `f"Torre {torre} · Apt {apto}"`, `packages.py:_direccion_corta`). `/residentes` NO
  tenía esa clase -- pero `etiqueta_torre_apto` ya devuelve el texto en mayúscula LITERAL en el
  propio Python (`f"T {torre:02d} - APT {apto}"`), así que hoy se ve igual de todos modos por una
  vía distinta (mayúscula-en-el-dato vs. mayúscula-por-CSS). Inconsistencia real de mecanismo,
  sin efecto visual actual, pero no a prueba de futuro (si el formato de `etiqueta_torre_apto`
  cambiara a Title Case algún día, quedaría mostrando minúsculas sin que nadie lo not).

## Cambio

- `customers_manage/_resultados.html`: agregada la clase `uppercase` a la celda Torre y
  Apartamento, mismo criterio explícito que ya usa `packages/_resultados.html` en su columna
  Dirección -- las dos vistas fuerzan mayúsculas por CSS en ese punto, ninguna confía en que el
  dato ya venga así. Efecto secundario esperado (no un bug): el fallback "No Asignado" ahora se
  ve "NO ASIGNADO" en pantalla, a juego con el resto de la columna -- el texto en el HTML fuente
  no cambia (`text-transform` es puramente visual), así que el test existente que verifica el
  string literal sigue pasando sin tocarlo.

## Verificación

- Suite completa.
- Los 24 tests relacionados con torre/apartamento/asignado en `test_customers_manage.py` pasan
  sin cambios (la clase CSS no altera el HTML fuente, solo el render visual).
- Pendiente: verificar en test.papyrus.com.co tras deploy.
