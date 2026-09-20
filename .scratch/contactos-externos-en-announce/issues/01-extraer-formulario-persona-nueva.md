# 01 — Extraer el formulario de "persona nueva" de `/announce` a un componente reutilizable (prefactor)

**What to build:** hoy el formulario que aparece cuando el Teléfono o usuario de WhatsApp tecleado en el campo único de `/announce` no existe en paquetes ("No encontramos a nadie con ese dato — regístralo": campo Nombre + Anunciar + Recibir, con la identidad tecleada como dato oculto) está incrustado dentro del fragmento de resolución en vivo. Extraerlo a un componente reutilizable, que reciba el tipo de identidad (Teléfono o usuario de WhatsApp) y el valor tecleado, **sin cambiar nada de lo que ve o hace el Staff**. Es preparación: el ticket 02 necesita el mismo formulario dentro del desplegable "Nueva persona" de la sugerencia, y así no se duplica el marcado.

**Spec:** `.scratch/contactos-externos-en-announce/spec.md` (historias 15, 18 y 19; no agrega comportamiento nuevo).

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] El fragmento "sin coincidencia" se ve y se comporta igual que antes, tanto por Teléfono como por usuario de WhatsApp: mismo texto, campo Nombre obligatorio y que escribe en mayúsculas, **sin autofocus**, la identidad tecleada como campo oculto (`telefono` o `whatsapp_usuario`, nunca ambos) y los botones Anunciar y Recibir presentes y cableados.
- [ ] Un solo lugar define ese formulario; el fragmento de resolución en vivo lo usa a través del componente.
- [ ] El componente se puede incluir desde otro fragmento (por ejemplo, dentro de un desplegable) sin depender del contexto del fragmento actual: recibe todo lo que necesita como parámetros.
- [ ] Las pruebas web existentes de `/announce` (resolución en vivo y registro por Teléfono/WhatsApp directo) pasan **sin modificarse**.
- [ ] No hay cambios de esquema, de rutas ni de comportamiento visible.
