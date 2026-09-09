# 04 — Flujo de aceptación de términos

**What to build:** una nueva dependencia que envuelve `current_customer` (usada por las rutas
normales del portal) redirige a la pantalla de aceptar términos mientras `bloqueado_en` siga
seteado; esa pantalla expone el texto real de `/terminos` con una confirmación explícita, y al
aceptar registra `terminos_aceptados_en` y limpia el estado de bloqueo por completo.

**Blocked by:** 01 — Núcleo: bloquear / autorizar desbloqueo. (Se combina con 02 para el recorrido
completo de un residente real, pero no depende técnicamente de él — sus tests pueden simular una
sesión de cliente ya autenticada directamente.)

**Status:** ready-for-agent

- [ ] Un residente con `desbloqueo_autorizado_en` seteado que accede a `/mis-paquetes` es redirigido
      a la pantalla de aceptar términos
- [ ] Puede acceder normalmente a esa pantalla puntual mientras sigue bloqueado
- [ ] Al aceptar, se registra `terminos_aceptados_en` y se limpian `bloqueado_en`/
      `desbloqueo_autorizado_en`/`motivo_bloqueo_id`
- [ ] Tras aceptar, vuelve a acceder con normalidad al resto de su portal
