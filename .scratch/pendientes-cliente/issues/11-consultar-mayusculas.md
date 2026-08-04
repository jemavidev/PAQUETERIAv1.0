# 11 — `/consultar`: todo el contenido en mayúsculas

**Pedido original (cliente):** "se ve bastante bien, realiza el cambio
para esta vista" — confirmando el preview de mayúsculas mostrado antes
(inyección de CSS solo visual, sin desplegar) sobre `/consultar`.

**Vista:** `search/form.html` (`/consultar` completa — formulario,
resultado, y estado "sin resultados").

**Status:** verificado

## Historia (2 rondas, alcance corregido a mitad de camino)

**Ronda 1** (commit `6705654`): `uppercase` aplicado al `<div>` contenedor
de TODA la vista (formulario + resultado + "sin resultados"). Reveló un
bug aparte: el botón "Consultar" no quedaba en mayúsculas por el reset de
Tailwind (`button,select{text-transform:none}` en el preflight, un valor
declarado directo en el elemento gana sobre la herencia) — corregido en
`b7412c0` con `[&_button]:uppercase`.

**Ronda 2** (commit `47ccb71`, mismo turno, aclaración del cliente
mid-tarea): el alcance de la ronda 1 estaba mal — el pedido real era
**solo la sección de la línea de tiempo**, no toda la vista. Se revirtió
el `uppercase` del contenedor general (título/subtítulo del formulario,
nombre, teléfono, badge de estado, pill de días, botón, vuelven a case
normal) y se aplicó `uppercase` únicamente al `<div>` que envuelve
`timeline_paquete()`. El fix del botón (`[&_button]:uppercase`) ya no
hacía falta (no hay `<button>` dentro del timeline) y se quitó.

## Qué quedó (estado final)

- `uppercase` SOLO en el wrapper de la línea de tiempo
  (`<div class="mt-5 uppercase">`).
- Formulario, nombre, teléfono, badge, pill de días, "sin apartamento",
  y fotos: case normal.
- Puramente visual (`text-transform`), no cambia el dato guardado ni lo
  que se envía al buscar.

## Verificación

- [x] Captura de pantalla (mobile + desktop) confirma el alcance final:
      título/subtítulo/botón/nombre/teléfono/badge/pill en case normal,
      SOLO Anunciado/Recibido (con Fecha/Actor/Tipo/Condición/Guía) en
      mayúsculas.
- [x] 13/13 `test_search.py` + 436/436 suite completa (en cada una de las
      2 rondas).
- [x] Desplegado a `test.papyrus.com.co` (commit final `47ccb71`) y
      confirmado en vivo con `NSFC`. Deploy automático en las 3 rondas de
      este ticket.
