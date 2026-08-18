# 131 — `/announce`: quitar badges "Principal"/"Anunciante" de la lista de residentes

**Pedido original (cliente):**
Tras preguntarle qué se podía hacer en `/announce`, se le presentaron 3
posibilidades. Eligió la primera: "la primera" -- quitar los badges
"Principal"/"Anunciante" de la lista de residentes de una unidad, mismo
criterio ya aplicado a Recibir en [[125]].

**Status:** implementado

## Implementación

- `announce_new/_identificar_unidad.html`: se quitan los 2 `<span>` de
  badge ("Principal" azul, "Anunciante" verde) de cada `<button>` de
  residente -- queda solo `{{ r.nombre }}`. La lógica real (quién es
  Principal, quién llamó) NO se toca -- sigue determinando la
  preselección de la tarjeta Anunciar/Recibir más abajo en el mismo
  fragmento (`ns.preseleccionado`), solo deja de mostrarse como badge
  en la lista.

## Verificación

- `tests/web/test_announce_new.py`: 3 tests actualizados/renombrados --
  ya no esperan los badges; uno nuevo confirma la ausencia explícita
  (`test_identificar_telefono_con_coresidentes_no_muestra_badges_en_la_lista`).
  Cuidado real encontrado al escribir el test: "Principal" SIGUE
  apareciendo en la respuesta cuando quien llama es Principal -- pero
  como subtítulo de su propia tarjeta preseleccionada (`<p>...
  Principal</p>`, `_persona_resuelta.html`), un uso legítimo distinto
  del badge retirado (`<span>...Principal</span>`) -- el test distingue
  ambos por el tag de cierre en vez de asumir ausencia total de la
  palabra.
- 66 passed (`tests/web/test_announce_new.py`).
- Playwright contra el servidor local real (Torre 8 · Apto 403, 3
  residentes reales): tarjetas muestran solo el nombre, sin ningún
  badge.
- Suite completa: 1018 passed.
- Pendiente: deploy a test.papyrus.com.co.
