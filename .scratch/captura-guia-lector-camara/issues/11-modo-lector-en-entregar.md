# 11 — Modo lector en Entregar: foco en "Confirmar guía"

**What to build:** con el modo lector encendido (ticket 10), al abrir el modal Entregar de un paquete **que tiene guía**, el foco va directo al campo "Confirmar guía" (sin teclado en pantalla y con su contenido seleccionado), para verificar el paquete leyendo su etiqueta sin tocar nada. Es el mismo mecanismo de Recibir aplicado al segundo lugar donde se captura la guía. El ✅ o ⚠️ que compara contra la guía registrada sigue funcionando y sigue sin bloquear la entrega.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 31 a 33).

**Blocked by:** 10 — Modo lector: interruptor por equipo y foco al abrir Recibir.

**Status:** ready-for-agent

- [ ] Con el modo lector encendido, abrir Entregar de un paquete con guía deja el foco en "Confirmar guía", sin teclado en pantalla y con su contenido seleccionado; tocar el campo pide el teclado normal.
- [ ] Un paquete sin guía no muestra el campo "Confirmar guía" y abrir Entregar no enfoca ningún otro campo por esta vía.
- [ ] Con el modo apagado, abrir Entregar no mueve el foco (comportamiento de hoy).
- [ ] Escribir o leer una guía en "Confirmar guía" sigue mostrando ✅ si coincide con la registrada y ⚠️ si es distinta, sin bloquear la entrega (comportamiento de hoy, sin cambios).
- [ ] Vale en el modal Entregar de /paquetes y en el de /consultar; prueba en navegador real con el modo lector encendido y apagado en cada uno.
- [ ] Abrir Entregar no altera el resto de su flujo (cobro, anulación, saldo): las pruebas existentes de Entregar pasan sin modificarse.
