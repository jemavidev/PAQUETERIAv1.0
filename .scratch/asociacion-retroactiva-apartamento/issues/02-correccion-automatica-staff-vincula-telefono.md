# 02 — Corrección automática cuando el staff vincula un teléfono (`/residentes` + `/announce`)

**What to build:** de punta a punta — cuando el staff vincula un Teléfono a un Apartamento (agregar
un Ocupante, asociarle/editarle el teléfono en `/residentes`, o declarar una unidad en lote desde
`/announce`), cualquier Paquete huérfano preexistente de ese teléfono queda corregido en el mismo
paso, sin aviso ni confirmación aparte — el staff ya está presente y decidiendo. El autoservicio en
`/mis-datos` sigue exactamente igual que hoy: no dispara ninguna corrección automática.

**Blocked by:** 01 — Detección y corrección de Paquetes huérfanos (dominio).

**Status:** ready-for-agent

- [ ] `ocupante_service.agregar_ocupante`, `asociar_telefono_a_ocupante` y
      `editar_telefono_ocupante` aceptan un parámetro nuevo `staff_actor: Usuario | None = None`
      (mismo patrón que el `staff_actor` que ya existe en `paquete_service.announce`).
- [ ] Con `staff_actor` presente: después de vincular `apartamento_actual_id`, la función consulta
      los Paquetes huérfanos de ese teléfono (seam del ticket 01) y los corrige a todos, en la misma
      transacción que la vinculación.
- [ ] Sin `staff_actor` (valor por defecto): el comportamiento es idéntico al actual — ningún
      Paquete huérfano se toca.
- [ ] Las rutas de `/residentes` en `customers_manage.py` que llaman a esas 3 funciones pasan el
      `Usuario` de la sesión de staff (`current_staff`) como `staff_actor`.
- [ ] `announce_new.py` (declarar unidad en lote) pasa el mismo `staff_actor` en cada llamada, una
      por cada Teléfono del grupo que se está declarando.
- [ ] `customer_verify.py` (autoservicio, `/mis-datos`) NO pasa `staff_actor` — test de regresión
      explícito que confirma que un residente autoregistrándose (o vinculando a otro Ocupante desde
      su propia cuenta) no dispara ninguna corrección automática, aunque tenga Paquetes huérfanos.
- [ ] Si el teléfono vinculado no tiene ningún Paquete huérfano, el flujo normal de vincular
      (staff o autoservicio) no cambia en nada observable — sin aviso, sin paso de más.
- [ ] Tests nuevos en `tests/data_model/test_ocupante_service.py` (con/sin `staff_actor`, con/sin
      huérfanos) y de punta a punta en `tests/web/test_customers_manage.py` /
      `tests/web/test_announce_new.py` (vía la ruta real, no llamando al dominio directo).
- [ ] Suite completa del proyecto sigue en verde.
