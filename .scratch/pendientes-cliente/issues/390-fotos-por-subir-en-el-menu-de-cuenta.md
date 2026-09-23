# 390 — "Fotos por subir": dentro del menú de cuenta, debajo de "Lector"

**Pedido original (Jesús):** "Necesito que esto que acabas de agregar "📷 0 fotos por subir" lo coloque mejor en la
sección del header "account-menu", justo debajo de donde está ubicado el botón del "Lector"".

**Status:** implementado, pendiente confirmar en vivo (localhost)

## Contexto

El aviso de la cola de fotos del [[389]] quedó suelto en `.site-actions`, al lado del menú de cuenta. Además se veía
con "0": la clase `inline-flex` le ganaba al atributo `hidden` (mismo problema ya documentado en el proyecto), así que
nunca se ocultaba.

## Decisiones

- El aviso pasa a ser un ítem del menú de cuenta (`bloque_staff`, `base.html`), justo debajo de "Lector", con el mismo
  estilo de ítem y la cantidad a la derecha (como "Activado"/"Desactivado" del Lector).
- Oculto de verdad mientras no haya fotos pendientes: regla CSS `[hidden] { display:none }` propia del ítem.

## Ronda 2

**Pedido (Jesús):** "Solo deja que diga el número así: "Fotos por subir 2", remueve la palabra "fotos" que está después
del número de fotos pendientes." -- la cantidad a la derecha pasa de "2 fotos" / "1 foto" a solo "2" / "1".

## Verificación

- `tests/browser/test_fotos_cola.py`: con 0 fotos el ítem no se ve y está justo después de "Lector"; con una foto en
  cola aparece en el menú con "1 foto" y se oculta al subirse. Captura a 390 px revisada: "Fotos por subir" debajo de
  "Lector", cantidad en ámbar.
