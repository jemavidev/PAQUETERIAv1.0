# 263 — `/residentes` tab Residentes: Ocupante sin contacto no se puede gestionar + duplicados por nombre

**Pedido original (cliente):** reportó en vivo (recreado en
`http://localhost:8010/residentes/c75f7cdd-...`) que aparecían dos
"LAIS HERNANDEZ" y dos "RAFAEL TORRES" en la misma unidad. Al
preguntarle cómo debería comportarse el caso de nombre duplicado,
señaló el problema real: *"este usuario nuevo debería quedar para
rechazar o confirmar, pero simplemente no tiene ninguna opción para
gestionarlos, no sé qué se deba hacer"* -- confirmado después: *"Veo
que las características para gestionarlo solo aparecen después de
agregar teléfono/whatsapp"*.

**Status:** implementado

## Diagnóstico

Dos problemas relacionados:

1. **Causa raíz de los duplicados**: `agregar_ocupante` no valida
   nombre duplicado cuando el nuevo Ocupante no trae Teléfono ni
   WhatsApp -- el form "Agregar Residente" (nombre solo) deja crear un
   segundo "LAIS HERNANDEZ" sin ningún aviso, aunque ya exista uno
   ACTIVO en la misma unidad. Reproducido con una llamada directa a
   `agregar_ocupante` (sin bloquear, creó una fila más).

2. **Problema más amplio (el que realmente le duele al cliente)**: en
   `customers_manage/detail.html`, TODO el bloque de acciones
   (✅ Confirmar, ❌ Rechazar/Eliminar, ⭐ Promover, ✏️ Editar, 🔔
   Notificaciones) y sus modales viven detrás de `{% if o.persona_id
   %}` -- un Ocupante SIN contacto propio (`persona_id is None`, sea
   duplicado o un caso legítimo como un hijo menor sin celular) no
   tiene NINGUNA forma de confirmarse o rechazarse desde esta vista,
   solo el form "Teléfono o WhatsApp / Agregar". El dominio SÍ soporta
   ambas operaciones sin `persona_id` (`confirmar_ocupante` solo exige
   contacto si es el primer Ocupante de una unidad vacía;
   `dar_de_baja_ocupante` no exige contacto en ningún caso) -- es
   puramente un hueco de la vista, no del dominio.

## Alcance de la implementación (versión final, tras feedback del cliente)

El cliente refinó el alcance en vivo después del primer diagnóstico:
*"solo debe aparecer las opciones para confirmar o rechazar, seguido a
esto si es confirmado, debería poder habilitar los botones 'Edición,
notificación y Eliminar', no se incluye Promover ya que no se tiene
forma de notificarlo (solamente a la cuenta del principal), tan pronto
se tenga teléfono/whatsapp será posible la opción de promover, por
ahora el input que hace referencia al placeholder 'Teléfono o WhatsApp'
no debería estar allí, este ya está integrado al botón de editar. La
idea de todo esto es que se hable un mismo idioma siempre."*

1. `agregar_ocupante`: rechaza con `ValueError` si `nombre` (normalizado
   igual que `normalizar_nombre`) coincide con el de un Ocupante YA
   ACTIVO de la misma unidad -- SOLO quando el nuevo Ocupante no trae
   Teléfono ni WhatsApp (con contacto, dos personas reales pueden
   compartir nombre legítimamente, el contacto ya distingue identidad).
2. `customers_manage/detail.html` -- por estado del Ocupante SIN
   principal:
   - **Pendiente, sin contacto**: SOLO ✅ Confirmar y ❌ Rechazar. Nada
     de Editar/Notificaciones/Promover.
   - **Confirmado, sin contacto**: se suma ✏️ Editar (el modal ahora
     también sirve para agregar el PRIMER contacto -- Notificaciones y
     Promover se quedan ocultos, no hay canal para notificar ni para
     promover sin Teléfono/WhatsApp propio).
   - **Con contacto** (pending o confirmado): sin cambios respecto a
     antes -- todo el set completo de botones.
   - El form suelto "Teléfono o WhatsApp / Agregar" se RETIRA de la
     vista -- su función se integra al modal Editar.
3. `customers_manage.py::customers_manage_ocupante_editar`: ya no exige
   `ocupante.persona_id` de entrada. Si es `None`, Teléfono/WhatsApp acá
   agregan el PRIMER contacto (`asociar_telefono_a_ocupante`/`asociar_
   whatsapp_a_ocupante`, mismas funciones que ya usaba el form
   retirado). Nombre se sigue editando directo sobre `Ocupante.nombre`
   (columna propia) aunque no haya contacto; Email sin Persona a la que
   aplicarse se descarta en silencio. La ruta `/contacto` (y `/telefono`,
   `/whatsapp`, etc.) se queda intacta para quien la use directo -- mismo
   criterio que el resto de rutas "viejas" de esta tab, solo se retiró
   su render en la plantilla de staff (el equivalente de `/mis-datos`,
   `customer_verify.py`, no se tocó -- el pedido fue puntual sobre
   `/residentes`).

## Verificación

- Tests nuevos: `test_agregar_ocupante_sin_contacto_rechaza_nombre_duplicado_de_activo`,
  `test_agregar_ocupante_con_contacto_no_rechaza_nombre_duplicado`
  (`test_ocupante_service.py`); `test_staff_agregar_residente_sin_contacto_rechaza_nombre_duplicado`,
  `test_ficha_ocupante_pendiente_sin_contacto_solo_confirmar_y_rechazar`,
  `test_ficha_ocupante_confirmado_sin_contacto_habilita_editar`,
  `test_staff_confirma_ocupante_sin_contacto`, `test_staff_rechaza_ocupante_sin_contacto`,
  `test_staff_edita_ocupante_sin_contacto_propio_agrega_el_primero`,
  `test_staff_edita_ocupante_sin_contacto_solo_nombre_no_crea_persona`,
  `test_staff_edita_ocupante_sin_contacto_telefono_y_whatsapp_juntos`
  (`test_customers_manage.py`). Suite completa: 1255 passed.
- Verificado en vivo sobre el caso REAL que recreó el cliente
  (`/residentes/c75f7cdd-...`, TORRE 10 apto 302): las dos entradas
  duplicadas sin contacto (LAIS HERNANDEZ y RAFAEL TORRES) mostraban
  exactamente el set de botones esperado por estado (RAFAEL, que el
  cliente ya había confirmado mientras se implementaba, mostraba ✏️
  Editar + ❌ Eliminar, sin 🔔 ni ⭐; LAIS, todavía pending, mostraba
  SOLO ✅/❌) -- se rechazaron ambas vía el ❌ ahora funcional (POST real
  a `/baja`, 303 los dos), dejando la unidad de vuelta a sus 2
  residentes reales. Confirmado también que intentar recrear
  "RAFAEL TORRES" sin contacto ahora rechaza con "Ya existe un
  Residente activo llamado 'RAFAEL TORRES' en esta unidad."
