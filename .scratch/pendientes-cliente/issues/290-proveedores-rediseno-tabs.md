# 290 — Rediseño de `/administracion/proveedores` a tabs (unificar con /residentes)

**Pedido original (cliente):** "de ahora en adelante enfocate en que
estaremos trabajando en localhost solamente, te pedire explisitamente que
despliegues a test.papyrus.com.co, por ahora no. Por otro lado necesito que
mejores y el como se ve toda esta vista de /administracion/proveedores, la
idea es que se unifique lo mas que se pueda a las otras vistas, podria ser
similar a la vista de /residentes, donde se manjena una serie de tabs que
despliega la informacion necesaria cuando esta es seleccionada, en lo
posible si crees que es necesario en algunos de estos flujos tambien
implementa modales (solo si lo crees necesario), por ultimo ten presente
que si tienes algo desactivado, deberia no verse lo que se puede hacer con
este por ahora, seria una limpieza visual a lo que no utilizaremos.
Recuerda siempre en lo que te estoy pidiendo, manejar los tamans y
proporciones de las otras vistas."

**Status:** implementado -- pendiente confirmar en vivo en test.papyrus.com.co

## Alcance acordado

- **Deploy**: confirmado -- desde ahora, trabajo solo contra `localhost`
  (`scripts/paquetex_dev_up.sh`), sin sincronizar/desplegar a
  `test.papyrus.com.co` salvo pedido explícito (ya era la convención
  vigente, memoria `deploy-solo-cuando-se-pide` -- el cliente la reafirma).
- **Rediseño visual de `/administracion/proveedores`** (construida en
  issues 03/05/289): de 4 tarjetas apiladas verticalmente a un layout de
  tabs -- mismo patrón que `customers_manage/detail.html` (`/residentes`):
  `.tab-btn`/`.tab-panel`, JS plano, `?tab=` sincronizado, ancho de página
  unificado (`max-w-lg lg:max-w-2xl`, no el `max-w-md` que forzaba
  `formulario_flujo`).
- **Modales**: evaluados, no aplicados -- ningún flujo de esta pantalla
  (todos formularios de una sola tarjeta, sin pasos ni confirmación
  destructiva) justificaba uno; ninguna tab de `/residentes` usa modal
  para su contenido principal tampoco, solo para sub-acciones puntuales que
  acá no existen.
- **Llamadas/PXB, tres iteraciones en vivo hasta la versión final**:
  1. Primer intento: campos visibles con `disabled` + badge "Próximamente"
     (igual a como quedó descrito en issue 289).
  2. El cliente pidió limpieza visual ("lo que este desactivado, seria
     mejor que no lo muestre o lo escondas") -- se probó ocultar solo los
     campos (estado vacío, `components/_estado_vacio.html`) y luego,
     tras otra corrección, ocultar la tab entera (`_filas_proveedores` la
     excluía de `canales`).
  3. El cliente revirtió: "veo que ocultaste el pbx y no lo sacaste de
     nuevo, la idea es que la seccion este presente, pero desactivada o
     sin poder visualizar los campos del formulario" -- mostrado dos
     mockups, eligió "campos visibles pero deshabilitados (grises, sin
     poder tocarlos)". **Esta es la versión final**, igual a la del punto 1:
     tab siempre presente, toggle/campos/botón "Guardar" con `disabled` en
     HTML, badge "Próximamente", `_estado_vacio.html` ya no se usa.
- **Ocultar campos de un proveedor editable mientras su toggle esté
  apagado** (pedido separado del cliente, mismo alcance de trabajo: "I was
  thinking in hiding just the toggles that are disable[d] (hide the forms
  when toggle is disabled)"): aplica a AWS SNS/LIWA/Twilio/SMTP/Meta (los
  `disponible=True`) -- JS plano (`.campos-proveedor` + `data-campos-de`)
  sincroniza mostrar/ocultar con el estado del checkbox, en vivo y al
  cargar. Llamadas/`PXB` queda afuera de este mecanismo a propósito (sus
  campos siempre visibles, ver punto anterior).

## Implementación

`app/web/templates/admin/proveedores.html` (reescrito) +
`app/web/routes/admin_proveedores.py` (`_tab_inicial`, `_filas_proveedores`
extendido con `disponible`/`todos_deshabilitados`).

## Verificación

Suite completa: 1316 passed. `tests/web/test_admin_proveedores.py`: 22
passed. Verificado manualmente en el navegador contra `localhost:8010`
(tabs, `?tab=` persiste tras F5, Llamadas bloqueada, ocultar/mostrar campos
al togglear LIWA en vivo). Pendiente confirmar en vivo contra
`test.papyrus.com.co`.
