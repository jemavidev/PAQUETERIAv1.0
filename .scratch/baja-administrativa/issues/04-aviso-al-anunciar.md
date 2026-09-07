# 04 — Aviso discreto al anunciar para alguien de baja

**What to build:** cuando el staff identifica, en el flujo de `/announce`, a un residente que está
en baja administrativa, ve un aviso discreto ("Sin notificar — de baja") junto a su nombre — mismo
lugar y mismo estilo visual que el pill "Auto" que ya existe para `autoriza_recepcion_automatica`.
El aviso es puramente informativo: no bloquea anunciar ni recibir un paquete a nombre de esa
persona.

**Blocked by:** 01 (necesita que exista la columna `baja_administrativa_en`).

**Status:** ready-for-agent

- [ ] Pill/aviso "Sin notificar — de baja" en los componentes de `/announce` que ya muestran el pill
      "Auto" (identificación de unidad/contacto) cuando la Persona identificada tiene
      `baja_administrativa_en` seteado.
- [ ] El aviso es solo informativo — anunciar y recibir un paquete a nombre de esa persona sigue
      funcionando con normalidad, sin ningún bloqueo ni confirmación extra.
- [ ] Una persona que NO está de baja no muestra este aviso (sin cambio de comportamiento/apariencia
      para el caso activo).
- [ ] Tests (`tests/web/test_announce_new.py`, prior art: los tests de hoy que cubren el pill
      "Auto"): el aviso aparece al identificar a alguien de baja; no aparece para un residente
      activo.
