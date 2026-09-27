# 72 — `/paquetes`: quitar la línea "nombre · anunciar · sesión" del header

**Pedido original (cliente):** remover el `<span class="text-sm
text-slate-500">` del header de `/paquetes` cuyo contenido es
`{{ staff.nombre }} · anunciar · sesión`.

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Contexto

`packages/list.html:22` — la línea es redundante con el menú de cuenta
(`base.html`, avatar + dropdown) que ya trae Anunciar y Mi sesión (issues
[[59]] / [[62]]), así que no se reemplaza por nada.

## Implementación

- Se removió el `<span>` completo; el header de `/paquetes` queda solo con
  el `<h1>Paquetes</h1>`.

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- Preview renderizado (headless Chrome) del header: sin la línea de
  usuario.
- `tests/web/test_packages.py` (52) y `tests/web/test_layout.py` (26)
  pasan sin cambios.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
