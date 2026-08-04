# 01 — Alcance ampliado: `/mis-paquetes` muestra los paquetes de todo el Apartamento

**What to build:** de punta a punta — un Ocupante que abre `/mis-paquetes` ve los Paquetes de
TODOS los Ocupantes activos de su mismo Apartamento (no solo los propios), incluyendo los suyos.
Las pestañas por estado (Anunciados/Recibidos/Entregados/Cancelados) y sus conteos reflejan ese
conjunto ampliado. Una sesión sin Apartamento asignado sigue viendo exactamente lo mismo que hoy
(solo sus propios Paquetes) — el cambio de alcance no le afecta en nada observable.

**Blocked by:** None — can start immediately.

**Verificado en vivo** (commit `2fa910c` en `jemavidev/PaqueteX`, deploy success, health OK,
`test.papyrus.com.co`). Ticket 02 (avatar de color) desbloqueado.

**Status:** ready-for-agent

- [ ] `ocupante_service.telefonos_activos_del_apartamento_de(session, persona)` existe: sin
      Apartamento devuelve `[persona.telefono]` (comportamiento actual); con Apartamento, devuelve
      los Teléfonos de los Ocupantes ACTIVOS de esa unidad (reutiliza `listar_ocupantes`, no
      reinventa la consulta).
- [ ] Ocupantes SIN Teléfono no aportan nada a la lista (no pueden haber anunciado/recibido bajo
      su propia identidad) — no rompe, simplemente no suman ningún teléfono.
- [ ] Ocupantes dados de baja (`desvinculado_en` no nulo) NO aparecen en la lista — `listar_ocupantes`
      ya los excluye por defecto, se confirma que se sigue usando así.
- [ ] La ruta `/mis-paquetes` cambia su filtro de "mi teléfono" a "cualquiera de los teléfonos del
      seam anterior" (`announced_by_phone` OR `recipient_phone` sobre la lista completa).
- [ ] Los conteos por pestaña se calculan sobre el conjunto ampliado (ya es automático una vez el
      filtro cambia, se verifica con un test explícito).
- [ ] Dos Ocupantes del mismo Apartamento, cada uno logueado en su propia sesión, ven AMBOS el
      mismo conjunto combinado de Paquetes (los de los dos).
- [ ] Una sesión sin Apartamento asignado sigue viendo solo sus propios Paquetes — test de
      regresión explícito sobre el comportamiento actual.
- [ ] Un Ocupante dado de baja de la unidad no contamina la vista de los Ocupantes activos
      restantes (sus Paquetes viejos no aparecen para los demás).
- [ ] Tests nuevos en `tests/data_model/` (función de dominio, mismo arnés que
      `test_ocupante_service.py`) y `tests/web/test_mis_paquetes.py` (alcance ampliado vía la
      ruta real).
- [ ] Suite completa del proyecto sigue en verde.
