# 82 — `/paquetes`: chip de código atenuado + botón de estado al doble + historial completo en el modal "Ver"

**Pedido original (cliente), 3 rondas seguidas sobre [[81]]:**
1. "LA LETRA SE VE PERFECTA Y EL TAMAÑO TAMBIEN, PERO EL COLOR NARANJA ES MUY
   INTENSO, PUEDES ATENUARLO UN POCO MAS" — el chip de código de acceso
   (`bg-amber-400`) se sentía demasiado intenso.
2. "QUE POSIBILIDAD EXISTE en que puedas atenuar este color naranja un poco
   mas" — un segundo pedido de atenuación tras el primer ajuste
   (`bg-amber-300`).
3. "Se ve mucho mejor sin ese amber, lo que necesito ahora es que en el
   modal de clientes de esta vista el boton para cambio de estado Anunciado
   --> Recibido y Recibido --> Entregado lo hagas el doble de tamano." —
   confirma el tono final (`bg-amber-200`) y pide además doblar el tamaño
   del botón de acción de estado en el modal "Ver".
4. "Lo que necesito ahora es modificar nuevamente el modal de clientes,
   necesito que aparezcan todos los estados que ha tenido el paquete, ya
   aparece anunciado, pero ahora necesito que se reflejen cada uno de los
   estados del mismo en esta vista" — el modal "Ver" solo mostraba un
   resumen de la ÚLTIMA acción ("Última acción por: X"); ahora debe mostrar
   el HISTORIAL completo (todos los hitos ocurridos, no solo el actual).

**Status:** implementado

## Implementación

- `packages/_resultados.html`:
  - Chip de código de acceso: `bg-amber-400` → `bg-amber-300` → `bg-amber-200`
    (2 rondas de atenuación en el mismo día, en la columna Cliente y en el
    modal "Ver").
  - Botón de siguiente estado (Recibir/Entregar) en el modal "Ver": de
    36px/20px (botón/ícono) a 72px/40px, el doble exacto, misma proporción.
  - Nueva sección "Historial" dentro del modal "Ver", reemplaza el párrafo
    resumen "Última acción por: X / Guía Y" (redundante una vez que el
    historial completo muestra el actor y la guía por hito). Reutiliza la
    infraestructura YA aprobada y en producción en `customer/paquetes.html`
    (`timeline_paquete`/`paso_timeline` de `components/_timeline.html` +
    `timelines_de_paquetes` de `paquete_timeline_service.py`, batch-resuelto
    para evitar N+1) -- mismo patrón, sin la galería de fotos (esta vista de
    staff no carga `p.fotos`, fuera de alcance de este pedido).
- `packages/_resultados.html` (import) + `routes/packages.py`: import de
  `timelines_de_paquetes`, batch-call en `_listar()`, `p.timeline` asignado
  por paquete en el mismo loop que ya arma `p.direccion_corta` etc.
- `icons.py`: ícono nuevo `reloj` (heroicon "clock") para el encabezado de
  la sección "Historial".
- `tests/web/test_packages.py`: el test
  `test_tarjeta_de_cancelado_muestra_el_actor_de_la_cancelacion_no_el_de_recepcion`
  (issue 79) verificaba que el modal mostrara SOLO el actor de la última
  acción -- ya no aplica (el historial completo muestra todos los actores a
  propósito). Renombrado a
  `test_historial_del_modal_atribuye_cada_actor_a_su_propio_hito`: ahora
  verifica que cada actor quede atribuido a SU PROPIO hito (Recibió/Canceló
  no se mezclan entre sí), no que uno esté ausente.

## Verificación

- `tests/web/test_packages.py`: 86 tests pasan.
- Verificación manual en navegador (ambiente local): modal "Ver" probado
  con un paquete Entregado (3 hitos: Anunciado→Recibido→Entregado, cada uno
  con Fecha/Actor/Tipo/Condición), uno Cancelado (Motivo visible en su
  propio hito) y uno solo Anunciado (1 hito, badge "• Actual", sin línea
  conectora). Colores por rol, badges y atribución de actor por hito
  correctos en los 3 casos.
- Pendiente: `tests/` completo + deploy a test.papyrus.com.co.
