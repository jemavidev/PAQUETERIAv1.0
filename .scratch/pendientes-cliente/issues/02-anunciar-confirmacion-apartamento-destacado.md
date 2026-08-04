# 02 — `/anunciar` confirmación: "Apartamento" con el mismo estilo destacado

**Pedido original (cliente):** "se ve perfecto, pero necesito que
'Apartamento' en esta misma vista se vea igual" (mismo tratamiento que
Nombre/Teléfono del ticket 01: mayúsculas + negrilla).

**Vista:** `announce/confirmacion.html` (recibo de éxito tras anunciar un
paquete desde `/anunciar`).

**Status:** verificado

## Qué se hizo

- `announce/confirmacion.html`: `destacado=true` también en la fila de
  Apartamento.
- Sincronizado el ejemplo de uso en el docstring de
  `components/_confirmacion.html` (mismo patrón que el ticket 01).

## Verificación

- [x] Render local confirma `class="font-bold uppercase ..."` en la fila de
      Apartamento cuando `snapshot_apartamento` está presente (test temporal
      con persona+apartamento seeded, borrado tras confirmar).
- [x] 8/8 `test_announce.py`, 436/436 suite completa.
- [x] Desplegado a `test.papyrus.com.co` (commit `f660227`) y confirmado en
      vivo: `POST /anunciar` para +573000000001 (CAMILA RESTREPO, con
      apartamento ya asociado) → las 3 filas (Nombre, Teléfono, Apartamento)
      renderizan `font-bold uppercase`.
