# 01 — Extraer el formulario de "persona nueva" de `/announce` a un componente reutilizable (prefactor)

**What to build:** hoy el formulario que aparece cuando el Teléfono o usuario de WhatsApp tecleado en el campo único de `/announce` no existe en paquetes ("No encontramos a nadie con ese dato — regístralo": campo Nombre + Anunciar + Recibir, con la identidad tecleada como dato oculto) está incrustado dentro del fragmento de resolución en vivo. Extraerlo a un componente reutilizable, que reciba el tipo de identidad (Teléfono o usuario de WhatsApp) y el valor tecleado, **sin cambiar nada de lo que ve o hace el Staff**. Es preparación: el ticket 02 necesita el mismo formulario dentro del desplegable "Nueva persona" de la sugerencia, y así no se duplica el marcado.

**Spec:** `.scratch/contactos-externos-en-announce/spec.md` (historias 15, 18 y 19; no agrega comportamiento nuevo).

**Blocked by:** None — can start immediately.

**Status:** done

- [x] El fragmento "sin coincidencia" se ve y se comporta igual que antes, tanto por Teléfono como por usuario de WhatsApp: mismo texto, campo Nombre obligatorio y que escribe en mayúsculas, **sin autofocus**, la identidad tecleada como campo oculto (`telefono` o `whatsapp_usuario`, nunca ambos) y los botones Anunciar y Recibir presentes y cableados.
- [x] Un solo lugar define ese formulario; el fragmento de resolución en vivo lo usa a través del componente.
- [x] El componente se puede incluir desde otro fragmento (por ejemplo, dentro de un desplegable) sin depender del contexto del fragmento actual: recibe todo lo que necesita como parámetros.
- [x] Las pruebas web existentes de `/announce` (resolución en vivo y registro por Teléfono/WhatsApp directo) pasan **sin modificarse**.
- [x] No hay cambios de esquema, de rutas ni de comportamiento visible.

## Verificación

- El HTML del fragmento "sin coincidencia" (Teléfono y WhatsApp) es **idéntico
  byte a byte** al de antes del refactor: se capturó del servidor de dev antes
  de tocar nada y se comparó después (2072 y 2082 bytes).
- 4 tests nuevos fijan el contrato del componente aislado, sin el contexto de
  ningún fragmento: por Teléfono, por WhatsApp, el `intro` opcional y el
  escape del valor tecleado. Se vieron fallar primero (componente inexistente).
- Las pruebas existentes de `/announce` pasan sin modificarse (137 en los dos
  archivos web de `/announce`); suite completa: 1840 pasan.
- Decisión menor: el texto "No encontramos a nadie con ese dato — regístralo:"
  se pasa como parámetro opcional `intro`, no vive dentro del componente --
  así el ticket 02 puede incluir el formulario dentro de "Nueva persona" sin
  ese aviso. Cualquier otro valor de `tipo` cae a WhatsApp, como antes.
- Sin cambios de esquema, de rutas ni de CSS compilado. El repo no tiene
  verificador de tipos configurado.
