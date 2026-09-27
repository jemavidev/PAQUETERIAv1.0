# 03 — El staff ve la Posición al buscar y entregar

**What to build:** en /paquetes, cada Paquete `Recibido` con Posición muestra la etiqueta "📍 NN" (tarjeta móvil y fila de escritorio); los demás estados y los sin Posición no muestran nada. El modal Entregar muestra la Posición en grande arriba, o "Sin ubicación" si es NULL. El residente nunca la ve. Spec: `../spec.md`.

**Blocked by:** 01 — Recibir captura la Posición.

**Status:** done

- [x] Etiqueta "📍 NN" solo para `Recibido` con Posición, en móvil y escritorio.
- [x] Modal Entregar: Posición destacada o "Sin ubicación".
- [x] La Posición no aparece en /mis-paquetes, /consultar público, la línea de tiempo ni las notificaciones.
- [x] La Posición se conserva tras `Entregado` (no se muestra en el listado).
