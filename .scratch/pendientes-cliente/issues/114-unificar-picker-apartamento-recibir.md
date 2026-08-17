# 114 — Unificar el picker de Apartamento (número→Torre) entre "Asignar apartamento" y "Recibir"

**Pedido original (cliente):**
"para el sistema de asignacion de apartamento donde solo colocamos el
numero de aparttamento y despues seleccionamos la torre, que tan viable
es que utulices ese metodo como standar para las veces en los flujos que
esto sea necesario" -- se presentó un análisis de los 4 patrones distintos
que existen hoy en la app (Asignar apartamento, Recibir, `/residentes/{id}`,
`/announce`) y una recomendación: unificar Recibir ya (mismo caso de uso,
bajo riesgo), dejar `/residentes/{id}` para discutir (puede que el staff
no siempre tenga el número de memoria ahí) y no tocar `/announce` (campo
único con otro propósito). El cliente confirmó "si" para arrancar con
Recibir. Aclarado antes de tocar código: el paso de Recibir NO muestra el
resumen de residentes/Libre (eso solo lo tenía "Asignar apartamento") --
el cliente eligió que alcance con elegir la Torre y seguir, ya que el
botón real de confirmar sigue siendo "Confirmar recibo" más abajo en el
mismo form.

**Status:** implementado

## Implementación

- **Nuevo** `components/_picker_apartamento.html`, macro
  `picker_apartamento(id_prefix, catalogo_torres, nombre_torre='torre',
  nombre_apartamento='apartamento', con_resumen=False,
  residentes_por_unidad=none)` -- input de Apartamento (número, 3-4
  dígitos) + contenedor de Torres candidatas + campos ocultos
  `torre`/`apartamento`. `con_resumen=True` agrega el bloque de resumen
  (Torre · Apto + Libre/residentes) que antes solo tenía "Asignar
  apartamento"; `con_resumen=False` (Recibir) se queda en una
  confirmación liviana de una línea tras elegir Torre.
- El JS (filtrar Torres por número tecleado, pintar tarjetas de un clic,
  resolver resumen O confirmación liviana según qué contenedores existan
  en el DOM) se movió a `recursos_recibir()` -- delegado sobre
  `document`, UNA sola vez por página, en vez de un `<script>` inline
  repetido por cada paquete (bug de eficiencia real que se corrigió de
  paso: con N paquetes en pantalla había N copias casi idénticas de este
  script).
- `_resultados.html` ("Asignar apartamento") y `_recibir_paquete.html`
  ("Recibir", paso de declarar unidad) ahora llaman al mismo macro --
  Recibir reemplaza su cascada `<select>` Torre→Apartamento por el flujo
  número→Torre, sin resumen.

## Verificación

- `tests/web/test_packages.py`: cubre que "Asignar apartamento" sigue
  funcionando igual (resumen incluido) y que Recibir ahora acepta
  declarar la unidad vía los mismos campos `torre`/`apartamento` que ya
  esperaba el endpoint (sin cambios en `packages.py`, solo en cómo se
  arman esos dos campos en el HTML).
- Playwright contra el servidor local real: escribir un número de
  apartamento dentro de "Recibir" muestra las Torres candidatas, elegir
  una llena los campos y el paquete recibido guarda el apartamento
  correcto -- sin pantalla de resumen extra.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
