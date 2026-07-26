# 02 — Nuevo modo de Destinatario + simplificar `/anunciar` (cliente)

**Qué construir:** El residente anuncia un paquete con solo 3 campos (Nombre, Teléfono, Aceptar T&C), sin elegir "a nombre de quién". El sistema registra/reutiliza la Persona del anunciante y crea el Paquete con el nombre tal cual lo escribió, usando su mismo teléfono como contacto por defecto. La pantalla de éxito muestra Nombre, Teléfono, código de acceso, Torre/Apartamento (si existen), y enlaces a Consultar y a Actualizar mis datos (vía `/otp`).

**Bloqueado por:** 01 (necesita el `access_code` y la ausencia de `tracking_number` ya resueltos para la pantalla de éxito).

**Estado:** ready-for-agent

- [ ] Nuevo modo en `Destinatario` (`paquete_service.py`) que resuelve `recipient_name` al nombre declarado por el cliente y `recipient_phone` al teléfono del anunciante — sin tocar el comportamiento de `yo_mismo`/`persona_registrada`/`solo_nombre` existentes (los tests de otras rebanadas que los usan como fixture no deben cambiar).
- [ ] `GET/POST /anunciar`: el formulario y la ruta solo aceptan `nombre`, `telefono`, `acepta_tyc` — se elimina `a_nombre_de`, `destinatario_telefono`, `destinatario_nombre`.
- [ ] Pantalla de éxito (`announce/confirmacion.html`) muestra: nombre, teléfono, código de acceso, torre y apartamento (si `snapshot_apartamento` existe), enlace "Consultar mi paquete" (`/consultar`) y enlace "Actualizar mis datos" (`/otp`).
- [ ] `tests/web/test_announce.py` actualizado: sin casos de `a_nombre_de`, con el caso feliz de 3 campos y la pantalla de éxito nueva.
- [ ] `tests/data_model/test_announce_paquete.py` con casos para el nuevo modo de `Destinatario`.
- [ ] Suite completa (`pytest`) pasa.
