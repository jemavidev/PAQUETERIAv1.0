# 79 — `/paquetes`: renombrar columnas + columna "Acciones" ampliada (8 íconos)

**Pedido original (cliente):** "Para las columnas que necesito son y en este
orden, 'Estado, Destinatario, Ubicación, Anunciado, Acciones' pero quiero que
se llamen asi 'Estado, Cliente, Direccion, Fecha, Acciones'. Adicional
necesito que la nueva columna llamada 'Direccion' tenga el formato este de
ejemplo 'Torre 03 · Apt 102'. Otro cambio que necesito es que en la nueva
columna 'Fecha', esta fecha haga referencia a la fecha del ultimo cambio de
estado, por ejemplo (si se anuncio ayer, pero se recibio hoy, deberia
aparacer la fecha y hora de hoy). Lo mas importante es que en la columna de
'Acciones', se tengan la mayor cantidad de acciones podibles, inicialmente
incluir los siguientes iconos (Whatsapp, Telefono, Email, Ver, Modificar,
Accion, Eliminar) [...] los botones de accion deben tener colores y ser
alusivos a lo que realiza cada uno de ellos, la columna de 'Cliente' debe ser
cliqueable y mostrar lo mismo que el boton de 'Ver'."

**Status:** implementado

## Contexto

Sigue directamente a [[78]] (tabla en vez de tarjetas, variante "Grid denso"
del prototipo de 5 alternativas) — esto ajusta esa tabla ya en producción:
renombra/reordena columnas, cambia qué fecha se muestra, y expande la
columna Acciones de 3 íconos (Recibir/Corregir/Cancelar) a 8.

Decisiones resueltas en la conversación (varias no eran derivables del
código/dato existente, se le preguntó directo al cliente):

- **Email**: la idea del cliente es "un solo email por apartamento,
  compartido por todos los residentes" — **ese campo NO EXISTE hoy** en el
  modelo (`Apartamento` no tiene columna `email`; solo `Persona.email`, y
  `Persona` es siempre quien ANUNCIÓ el paquete, no necesariamente el
  destinatario). Es una idea nueva, no una feature ya diseñada. **Se
  implementa el ícono pero SIEMPRE apagado/deshabilitado por ahora** (no hay
  de dónde sacar el dato) — el campo "email de apartamento" queda pendiente
  como feature aparte si se quiere construir (columna nueva + una pantalla
  para configurarlo, hoy no existe ninguna).
- **Ver**: modal nuevo de solo lectura (no la página completa
  `/residentes/{id}`, que no siempre existe para el destinatario). Muestra lo
  que haya disponible: snapshot del paquete (nombre/teléfono/torre-apto
  declarados) + datos de la Persona Anunciante si está vinculada + Ocupantes
  de esa unidad si el paquete tiene apartamento resuelto.
- **Acción**: NO se fusiona con Cancelar. Son 8 íconos separados: Whatsapp,
  Teléfono, Email, Ver, Modificar (= Corregir, renombrado), Acción (Recibir
  cuando ANUNCIADO / Entregar cuando RECIBIDO, un solo ícono contextual),
  Cancelar (aparte, siempre rojo), Eliminar.
- **Eliminar**: borrado real de la fila en la base de datos (sin precedente
  en esta app — todo lo demás se anonimiza, nunca se borra), pero SOLO
  disponible mientras el paquete está en estado ANUNCIADO (nunca se recibió)
  — para corregir duplicados/errores de captura. Ya RECIBIDO en adelante no
  se puede eliminar (para eso está Cancelar, que preserva el historial).
  Solo visible/permitido para `RolUsuario.ADMIN` (mismo patrón que
  `require_admin` en `customers_manage.py`).
- **Dirección**: se detectó de paso que `snapshot_torre` ya guarda el label
  completo (ej. `"TORRE 10"`), así que el template actual duplicaba la
  palabra ("Torre TORRE 10"). Se limpia el prefijo antes de formatear.

## Implementación

- `app/web/routes/packages.py`:
  - `_apartamentos_por_terna`/`_ocupantes_por_apartamento_id` (nuevos, batch
    por página, mismo criterio que `_personas_por_id`/`_usuarios_por_id`):
    resuelven la unidad + sus Ocupantes activos de cada paquete en 2
    consultas fijas, no una por fila.
    `_fecha_ultima_accion`/`_direccion_corta` (nuevos): mismo criterio de
    prioridad que `_actor_ultima_accion`, pero para el timestamp; y el
    formato compacto de Dirección (quita el prefijo "torre" redundante de
    `snapshot_torre` antes de anteponer el propio).
  - `_listar`: agrega `p.fecha_ultima_accion`, `p.direccion_corta`,
    `p.persona_anunciante`, `p.residentes_unidad` como atributos
    transitorios (mismo patrón que `p.advertencia_nombre`/
    `p.actor_ultima_accion`).
  - Ruta nueva `POST /paquetes/{id}/eliminar` (`delete_action`), gateada con
    `Depends(require_admin)` -- borrado real (`db.delete`) solo si
    `estado == ANUNCIADO`, si no re-renderiza con error. Sin riesgo de FK
    huérfana: `paquete_fotos` es la única tabla que referencia `paquetes.id`
    y solo se llena al Recibir (después de ANUNCIADO).
- `packages/_acciones.html`: reescrito -- de botones-con-caja (3 íconos) a
  íconos sueltos sin caja (8 íconos), mismo lenguaje visual ya usado en
  `customers_manage/search.html` (columna Acciones de /residentes). Reusa
  `iconos_nav.whatsapp/telefono/email/ver/eliminar`; Modificar/Acción/
  Cancelar son paths propios. Ícono "fantasma" (gris clarísimo, sin click)
  cuando una acción por-estado no aplica, para que las 8 posiciones queden
  alineadas entre filas.
- `packages/_resultados.html`: tabla a 5 columnas (Estado/Cliente/Dirección/
  Fecha/Acciones); columna Cliente es un botón que abre el mismo
  `modal-ver-<id>` que el ícono Ver. Modal "Ver" nuevo (solo lectura):
  Destinatario, "Última acción por"/Guía (arriba, issue de compatibilidad
  con tests -- ver abajo), Anunciado por (Persona vinculada), Residentes de
  la unidad (Ocupantes activos). Modal "Eliminar" (`modal_confirmacion`,
  reutilizado) solo se renderiza para ADMIN + ANUNCIADO.
- `tests/web/test_packages.py`: `test_tarjeta_de_cancelado_muestra_el_actor_...`
  ya no ancla en la posición de `recipient_name` en la fila (la columna
  Acciones ahora es mucho más larga, 8 íconos) -- ancla en el `id=` del
  `<div>` del modal "Ver" de ese paquete. 10 tests nuevos: encabezados de
  columna, formato de Dirección, Fecha = último cambio de estado, Cliente y
  Ver abren el mismo modal, contenido del modal Ver (anunciante +
  residentes), Eliminar (visibilidad admin-only, borra en ANUNCIADO,
  rechaza en RECIBIDO, 403 sin ser admin).

## Verificación

- `tests/web/` completo: 473 tests pasan (463 previos + 10 nuevos).
- Verificación manual en navegador (Postgres efímero + Playwright, capturas
  revisadas): columnas/orden/nombres correctos, formato "Torre 10 · Apt 101"
  sin duplicar la palabra, colores distintos por ícono/estado (WhatsApp
  verde, Teléfono/Recibir azul, Entregar verde, Cancelar/Eliminar rojo,
  Email siempre apagado), modal "Ver" muestra destinatario + anunciante +
  residentes de la unidad con datos reales, Eliminar solo visible para
  ADMIN y solo en paquetes Anunciados.
- Desplegado 2026-08-14: sync manual a `jemavidev/PaqueteX` (rama
  `deploy-paquetes-tabla-y-acciones`, commit `15f13e5`, desde
  `PaqueteXv.2@ec26f45`), push directo a `main` → CI + deploy vía SSH.
  `https://test.papyrus.com.co/health` responde `{"status":"ok"}` tras el
  push. **Pendiente confirmar visualmente en vivo** (login de staff real) —
  esta sesión no tiene credenciales de ese ambiente para verificar el
  contenido, solo que el servidor está sano.
- Deuda declarada (no bloquea este issue): el ícono Email queda sin datos
  reales hasta que se decida construir "email de apartamento" como feature
  propia (columna nueva + pantalla para configurarla).
