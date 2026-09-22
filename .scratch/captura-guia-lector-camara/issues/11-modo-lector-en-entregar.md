# 11 — Modo lector en Entregar: foco en "Confirmar guía"

**What to build:** con el modo lector encendido (ticket 10), al abrir el modal Entregar de un paquete **que tiene guía**, el foco va directo al campo "Confirmar guía" (sin teclado en pantalla y con su contenido seleccionado), para verificar el paquete leyendo su etiqueta sin tocar nada. Es el mismo mecanismo de Recibir aplicado al segundo lugar donde se captura la guía. El ✅ o ⚠️ que compara contra la guía registrada sigue funcionando y sigue sin bloquear la entrega.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 31 a 33).

**Blocked by:** 10 — Modo lector: interruptor por equipo y foco al abrir Recibir.

**Status:** done

- [x] Con el modo lector encendido, abrir Entregar de un paquete con guía deja el foco en "Confirmar guía", sin teclado en pantalla y con su contenido seleccionado; tocar el campo pide el teclado normal.
- [x] Un paquete sin guía no muestra el campo "Confirmar guía" y abrir Entregar no enfoca ningún otro campo por esta vía.
- [x] Con el modo apagado, abrir Entregar no mueve el foco (comportamiento de hoy).
- [x] Escribir o leer una guía en "Confirmar guía" sigue mostrando ✅ si coincide con la registrada y ⚠️ si es distinta, sin bloquear la entrega (comportamiento de hoy, sin cambios).
- [x] Vale en el modal Entregar de /paquetes y en el de /consultar; prueba en navegador real con el modo lector encendido y apagado en cada uno.
- [x] Abrir Entregar no altera el resto de su flujo (cobro, anulación, saldo): las pruebas existentes de Entregar pasan sin modificarse.

## Verificación

- Vistas fallar primero en navegador real (`tests/browser/test_modo_lector_entregar.py`): 3 de las 6 pruebas
  fallaban (el foco en "Confirmar guía" en /paquetes y en /consultar, y la comparación tecleando en el campo
  enfocado). Las otras tres fijan lo que no debe cambiar: paquete sin guía, modo apagado, y que un toque devuelve el
  teclado normal (esta se reforzó para partir de `inputmode="none"`, así no pasa en vacío). Ahora pasan las 6 y las
  60 del seam completo.
- Con el modo encendido, abrir Entregar de un paquete con guía deja el foco en "Confirmar guía" con
  `inputmode="none"` (sin teclado en pantalla) y el contenido seleccionado; un toque devuelve `inputmode="text"`.
  Igual en el modal Entregar de /paquetes y en el de /consultar.
- Paquete sin guía: el modal no trae el campo "Confirmar guía" y abrirlo no enfoca ningún otro campo (comprobado: el
  elemento enfocado no es un campo de texto dentro del diálogo). Modo apagado: el foco no se mueve y el campo sigue
  con `inputmode="text"`.
- La comparación no cambia: una lectura entra en el campo enfocado, muestra "Coincide con la guía registrada" si es
  la misma y "Guía distinta a la registrada" si no; el botón de entregar del formulario sigue habilitado (nunca
  bloquea, como hoy).
- Reutiliza todo lo del ticket 10 (interruptor, `inputmode`, selección, toque): solo se amplió el selector del campo
  a enfocar (la Guía de Recibir y el campo con la guía esperada de Entregar) y el chequeo de modales que llegan ya
  abiertos. Los ayudantes del menú de cuenta pasaron a `_ayudantes.py` para no duplicarlos.
- Regresión: `test_captura_guia`, `test_packages`, `test_search`, `test_announce_new`,
  `test_announce_sugerencia_contacto_externo`, `test_layout` (453 pruebas web) y el seam completo, en verde.
