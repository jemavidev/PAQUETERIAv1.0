# 03 — Aviso y autorización manual en la ficha de `/residentes`

**What to build:** de punta a punta — el staff abre la ficha de un cliente/Apartamento en
`/residentes` y, si existen Paquetes huérfanos cuyo teléfono coincide con algún Ocupante de esa
unidad, ve un aviso tipo warning listándolos (código de acceso, destinatario, fecha) con un botón
"Asociar" por Paquete. Con un clic, el staff autoriza la asociación retroactiva de ese Paquete
puntual; puede ignorar cualquiera sin asociarlo. Una ficha sin huérfanos pendientes no muestra nada
de más. Esta es la vía de autorización para el caso de autoservicio (ticket 02 cubre el disparo
automático cuando es el staff quien vincula el teléfono).

**Blocked by:** 01 — Detección y corrección de Paquetes huérfanos (dominio).

**Status:** ready-for-agent

- [ ] Al renderizar la ficha de cliente/Apartamento en `/residentes`, por cada Ocupante activo de
      esa unidad (o la Persona sola, si la ficha es de un cliente sin Apartamento) se consulta el
      seam de detección del ticket 01 con su Teléfono.
- [ ] Si hay resultados, se muestra un aviso con la lista de Paquetes huérfanos: código de acceso,
      nombre del destinatario, fecha de anuncio, y un botón "Asociar" individual por Paquete.
- [ ] Sin resultados, la ficha no muestra el aviso ni ningún elemento relacionado — cero ruido
      visual quando no hay nada pendiente.
- [ ] Nueva ruta `POST` en `/residentes` (staff, gated por `current_staff`, sin `require_admin` —
      mismo criterio que el resto de acciones operativas de ese módulo) que recibe el `paquete_id`,
      resuelve el Apartamento actual de la Persona de la ficha, y llama a `corregir_apartamento`
      (seam del ticket 01) con el `Usuario` de la sesión como actor.
- [ ] Tras autorizar, la ruta redirige de vuelta a la misma ficha y el Paquete ya no aparece en el
      aviso (fue corregido).
- [ ] Si el Paquete señalado ya no está `Anunciado` cuando el staff hace clic en "Asociar" (carrera:
      alguien lo recibió mientras tanto), la acción falla de forma controlada — sin error 500, con
      un mensaje claro, sin romper el resto de la ficha.
- [ ] Tests nuevos en `tests/web/test_customers_manage.py`: ficha con huérfanos muestra el aviso con
      los datos correctos; ficha sin huérfanos no lo muestra; el `POST` corrige el Paquete y
      redirige; el caso de carrera (Paquete ya no `Anunciado`) no rompe la página.
- [ ] Suite completa del proyecto sigue en verde.
