# 80 — `/paquetes`: refinamientos del modal "Ver" + nuevo "Asignar apartamento"

**Pedido original (cliente):** batch de ajustes en vivo sobre el modal "Ver"
y la columna Dirección, tras ver [[79]] desplegado:
1. "necesito que en caso que se tenga email, telefono o usuario de whatsapp
   se muestren en este modal, ademas necesto que sea clickeables, accionando
   su destino (whatsapp, llamada o enviar mail)" — Destinatario/Anunciado
   por: ocultar filas vacías, las que sí tienen dato quedan clicables
   (`tel:`/`wa.me`/`mailto:`).
2. "en la seccion 'Residentes de la unidad' tambien necesito que solo sean
   un icono" + "solo un icono de whatsapp en este modal por los usuario que
   tengan usuario estaria bien" — ícono de teléfono/WhatsApp solo-ícono (sin
   texto), WhatsApp solo si hay `whatsapp_usuario` explícito (sin caer a
   teléfono ahí).
3. "en caso que no tenga nada, simplemente debes remover lo que aparezca en
   esa linea" — sin íconos ni "—" para un residente sin teléfono ni
   WhatsApp, solo el nombre.
4. "en la parte superior donde dice TORRE y APARTAMENTO en este modal esten
   en mayusculas y en negrilla" — la línea badge+dirección del modal.
5. "en la seccion 'Anunciado por' remueve las etiqueta de los nombres...y
   deja solo los iconos" — quita los chips "Nombre"/"Teléfono"/etc, deja
   ícono + valor.
6. "en la columna de 'Dirección' combierte todo a mayusculas" — columna de
   la TABLA (no el modal), incluyendo "Sin apartamento".
7. "en caso que no tenga un apartamento asignado solo coloca un icono que al
   presionarlo nos lleve a poder asignar un apartamento a este cliente" —
   feature nueva: ícono + modal "Asignar apartamento", solo para paquetes
   ANUNCIADO sin unidad (confirmado explícitamente por el cliente: el
   snapshot queda congelado después de Recibido, mismo criterio que
   Corregir destinatario).
8. "vamos a eliminar el icono de 'Ver' en la columna 'Acciones'" — quedaba
   redundante con la columna Cliente (que ya abre el mismo modal, punto
   explícito desde [[79]]); columna Cliente queda como único disparador.
9. "necesito que en la columna de Acciones todos los iconos siempre tengan
   colores... me refiero a los iconos de los estados Anunciado, recibido,
   entregado y cancelado" — el ícono "Acción" (check) y "Cancelar" (X) ya
   NO se apagan a gris en los estados terminales: Acción toma el color del
   badge propio de la fila (verde en Entregado, rojo en Cancelado);
   Cancelar queda rojo siempre. Ninguno de los dos es clicable fuera de su
   estado válido -- solo cambia el color, no la función.
10. "en el modal del cliente... necesito que se tenga un icono relacionado
    con el cambio de estado del paquete, en caso que este anunciado, debe
    aparecer el icono de recibir, y asi sucesivamente para cada estado...
    entregado y cancelado no tienen otro que les siga, este icono debe
    estar en la parte superior derecha y debe ser visible" — ícono circular
    grande (Recibir/Entregar según estado) en la esquina superior derecha
    del modal "Ver", junto al botón de cerrar; nada en Entregado/Cancelado
    (terminales). Clic cierra "Ver" y abre el modal real de la acción en el
    mismo gesto (traspaso limpio, no dos modales superpuestos).

**Status:** implementado

## Contexto

Sigue a [[79]] -- pulido del modal "Ver" tras verlo en vivo, más una
feature nueva chica (asignar apartamento) que salió de esa misma revisión.

## Implementación

- `app/web/routes/packages.py`:
  - `url_llamada`/`url_whatsapp` (de `persona_service`, ya usadas en
    `/residentes`) pasadas al contexto de `_render_lista` -- mismo patrón
    que `customers_manage.py` (contexto explícito, no global de Jinja).
  - `residentes_unidad` ahora guarda la `Persona` completa (no solo
    `telefono` suelto) para poder usar esos helpers en la plantilla.
  - Ruta nueva `POST /paquetes/{id}/asignar-apartamento`
    (`assign_apartment_action`): reusa `corregir_apartamento` (ya existía,
    excepción acotada a ADR-0001, pensada exactamente para este caso de
    "paquete huérfano") -- antes solo alcanzable como paso opcional dentro
    de Recibir; ahora también como acción independiente. Mismo guard
    server-side (`TransicionInvalida` si ya no está ANUNCIADO).
- `packages/_resultados.html`: modal "Ver" reestructurado (campos vacíos se
  ocultan en vez de mostrar "—"; enlaces `tel:`/`wa.me`/`mailto:` reales;
  chips de etiqueta quitados en "Anunciado por"; residentes solo-ícono).
  Columna Dirección con `uppercase`; ícono "Asignar apartamento"
  (`iconos_nav.casa`) reemplaza el texto "Sin apartamento" SOLO para
  ANUNCIADO. Modal nuevo "Asignar apartamento" con el mismo picker cascada
  Torre→Apartamento que ya usaba Recibir (mismo `catalogo_torres`).
- `components/_recibir_paquete.html` (`recursos_recibir()`): segundo
  listener `change` delegado para `data-torre-asignar`/`data-apto-asignar`
  (prefijo propio para no chocar con `data-torre-recibir` del paso opcional
  de Recibir -- ambos pueden coexistir para el mismo paquete).
- `packages/_acciones.html`: botón "Ver" quitado del todo (la columna
  Cliente sigue abriendo `modal-ver-<id>` sin cambios). Íconos Acción/
  Cancelar: el `else` gris (`text-slate-200`) de los estados terminales se
  reemplaza por el color de estado correspondiente (`text-emerald-600` en
  Entregado, `text-red-600` en Cancelado para Acción; `text-red-600` fijo
  para Cancelar) -- siguen sin `data-open` (no clicables), solo cambia el
  color. Modificar se deja intacto (su color activo ya es neutro/slate).
- `packages/_resultados.html`: cabecera del modal "Ver" ahora `justify-
  between` -- badge+dirección a la izquierda, ícono circular de "siguiente
  estado" a la derecha (Recibir azul en ANUNCIADO, Entregar verde en
  RECIBIDO, nada en terminales). El botón trae AMBOS `data-open`/`data-
  close` a la vez.
- `components/_recibir_paquete.html` (`recursos_recibir()`): el listener
  delegado de `[data-open]` ahora también revisa si ESE MISMO elemento trae
  `data-close` y, de ser así, cierra ese modal además de abrir el nuevo --
  antes solo un atributo por elemento tenía efecto (el de `data-open`
  ganaba y el `data-close` se ignoraba en silencio). Cambio genérico y
  retrocompatible: solo actúa cuando ambos atributos están en el MISMO
  elemento, algo que ningún botón existente hacía hasta este ícono.
- `tests/web/test_packages.py`: 5 tests nuevos (ícono solo en ANUNCIADO sin
  unidad, asignación exitosa, rechazo si ya no está ANUNCIADO, rechazo sin
  datos, rechazo con terna inexistente); `test_columna_cliente_y_boton_ver_...`
  renombrado a `test_columna_cliente_abre_el_modal_ver` (ahora 1 solo
  disparador, no 2).

## Verificación

- `tests/web/` completo: 481 tests pasan (476 previos + 5 nuevos; corrida
  final tras TODOS los puntos de este issue, incluido el quitar "Ver" y el
  coloreado de estado de Acción/Cancelar).
- Verificación manual en navegador (Postgres efímero + Playwright): modal
  "Ver" con datos reales (campos ocultos/clicables correctos), columna
  Dirección en mayúsculas, ícono "Asignar apartamento" abre el modal y la
  cascada Torre→Apartamento funciona, íconos Acción/Cancelar en color real
  (verde/rojo) para filas Entregado/Cancelado en vez de gris.
- Pendiente: confirmar en test.papyrus.com.co tras el próximo deploy (no
  desplegado todavía).
