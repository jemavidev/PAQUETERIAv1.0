# 294 — Usar TLS/Usar SSL pasan de dropdown a toggle real

**Pedido original (cliente):** "para Usar TLS y Usar SSL crea un toggle
para cada uno" — tras la corrección del issue 293 (AWS_SNS_SMS_ENABLED
oculto), quedaban solo estos dos campos booleanos visibles, todavía como
dropdown de 3 estados ("No cambiar"/true/false).

**Status:** implementado -- pendiente confirmar en vivo en test.papyrus.com.co

## Alcance acordado

- `SMTP_USE_TLS`/`SMTP_USE_SSL` pasan de `input_select` (3 estados) a
  `toggle` (el mismo componente que ya usa el `habilitado` de cada
  proveedor) -- 2 estados reales, sin "no cambiar".
- Un toggle real no puede representar "no cambiar" -- siempre manda su
  posición actual (o nada, si está apagado, como cualquier checkbox). Se
  compara esa posición contra el valor YA presente en `.env` (nunca contra
  lo que se cargó al abrir el formulario) -- mismo criterio que la
  sincronización de issue 293: solo cuenta como cambio si de verdad
  difiere, para no reiniciar el servidor en cada guardado que no tocó el
  switch. Sin configurar en `.env` equivale a "false" para esta
  comparación (mismo default que ya usa el switch para dibujarse apagado).
- Sin ícono ni ayuda "Actual: ..." para estos campos -- el macro `toggle`
  no tiene ese slot, y la posición del switch YA es la información (no hay
  ambigüedad que aclarar con texto aparte).
- Cada toggle en su propia fila (el macro `toggle` es `inline-flex`; sin un
  `<div>` envolvente, dos toggles seguidos quedaban uno junto al otro en
  vez de apilados).

## Implementación

`app/web/routes/admin_proveedores.py`: `_campo_cambio()` (nuevo helper,
unifica la decisión de "¿esto cambió?" para texto y booleano -- para
booleano compara la posición del switch contra `os.environ.get(...)`, con
"sin configurar" tratado como `"false"` en ambos lados, plantilla y ruta,
para no disparar el mecanismo SSH en el primer guardado de un campo nunca
antes tocado). `app/web/templates/admin/proveedores.html`: rama booleana
ahora usa `toggle()` en vez de `input_select()` (que se retiró del import,
sin más usos en el archivo), cada uno en su propio `<div>` para que queden
apilados en vez de en la misma fila (el macro `toggle` es `inline-flex`).
Docstring del módulo actualizado para dejar explícito que "vacío = no
cambiar" solo aplica a campos de texto, no a booleanos.

## Verificación

`tests/web/test_admin_proveedores.py`: 34 passed (incluye: los campos
booleanos renderizan `<input type="checkbox">`, no `<select>`; el switch
refleja el valor real configurado; encenderlo dispara el mecanismo SSH con
el payload correcto de un solo campo; guardar sin tocarlo no dispara nada;
apagarlo desde `true` dispara SSH con `"false"`). Code review (Standards +
Spec) sin hallazgos pendientes tras limpiar el import muerto de
`input_select`, borrar un comentario duplicado que quedó huérfano del
refactor, y anotar en el docstring del módulo la excepción booleana a
"vacío = no cambiar". Verificado visualmente en el navegador (Usar TLS/Usar
SSL cada uno en su fila, clic cambia el estado real del checkbox).
Desplegado a `test.papyrus.com.co` el 2026-09-03 (commit `f5de6d0`, repo de
deploy). Pendiente confirmar en vivo.
