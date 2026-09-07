# 01 — Núcleo: dar de baja / reactivar manual, visible en `/residentes`

**What to build:** el staff (cualquier rol) puede dar de baja administrativamente a un residente
desde su ficha en `/residentes` — sin tocar ningún dato personal — y reactivarlo manualmente
después. Mientras está de baja, queda visualmente marcado con un badge ámbar "De baja" tanto en su
ficha como en el listado/búsqueda de `/residentes` (a diferencia de "Eliminado", sigue apareciendo
en el listado por defecto). Al dar de baja a un Principal, se desvincula su Ocupante activo,
promoviendo un sucesor con contacto propio si existe (reusa el mecanismo ya construido para el
derecho al olvido).

Fuera de esta ficha (cubierto por los tickets 02/03/04, no bloquean a este): la reactivación
automática al recibir un paquete, la supresión de notificaciones, y el aviso al anunciar. Este
ticket entrega el mecanismo manual completo — dar de baja y reactivar son ya usables y verificables
de punta a punta sin esas tres piezas.

**Blocked by:** Ninguno — puede arrancar de inmediato.

**Status:** ready-for-agent

- [ ] Migración: nueva columna `Persona.baja_administrativa_en` (timestamp con zona horaria,
      nullable), declarada también en el modelo ORM (paridad esquema↔ORM).
- [ ] `persona_service.dar_de_baja_administrativa(session, persona)`: setea
      `baja_administrativa_en` a ahora; idempotente (si ya estaba de baja, no hace nada); no
      modifica ningún otro campo de `Persona`.
- [ ] `persona_service.reactivar_persona(session, persona)`: limpia `baja_administrativa_en`;
      idempotente (si no estaba de baja, no hace nada); no reconecta ningún Ocupante.
- [ ] `POST /residentes/{persona_id}/baja-administrativa`: llama a
      `desvincular_ocupante_activo_de_persona` (ya existente) y luego a
      `dar_de_baja_administrativa`; disponible para cualquier rol de staff (`current_staff`, NO
      `require_admin`).
- [ ] `POST /residentes/{persona_id}/reactivar`: llama a `reactivar_persona`; mismo acceso (cualquier
      rol de staff).
- [ ] Dar de baja a un residente que es Principal de su unidad promueve automáticamente al Ocupante
      activo más antiguo con contacto propio, si existe (mismo criterio que ya usa el staff para
      esto); si no hay candidato, la unidad simplemente queda sin Principal.
- [ ] Ficha del residente (`customers_manage/detail.html`): botón "Dar de baja" (visible cuando no
      está de baja ni eliminado) y botón "Reactivar" (visible cuando SÍ está de baja), mismo patrón
      visual/confirmación que "Eliminar residente".
- [ ] Ficha y listado/búsqueda de `/residentes` (`customers_manage/detail.html` y
      `customers_manage/_resultados.html`): badge ámbar "De baja" cuando `baja_administrativa_en`
      está seteado — visualmente distinto del badge rojo "Eliminado".
- [ ] Un residente de baja SIGUE apareciendo en el listado por defecto de `/residentes` (a
      diferencia de "Eliminado", que se excluye) — sin cambios en las consultas de listado por
      defecto más allá de lo que ya excluyen por `eliminado_en`.
- [ ] Tests HTTP (`test_customers_manage.py`, prior art: los tests de hoy sobre
      `/residentes/{id}/eliminar`): dar de baja desvincula el Ocupante y promueve sucesor si
      corresponde; no toca datos personales; cualquier rol de staff puede darla de baja y
      reactivarla; el badge aparece/desaparece correctamente; el residente de baja sigue en el
      listado por defecto.
