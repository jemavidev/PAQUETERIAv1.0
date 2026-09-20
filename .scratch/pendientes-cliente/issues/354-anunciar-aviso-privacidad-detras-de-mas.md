# 354 — `/anunciar`: aviso de privacidad detrás de un link "más..."

**Pedido original (Jesús):** agregar un link de "más..." al final del
párrafo "Al marcar esta casilla, confirmo que he leído y acepto los términos
y condiciones del servicio de anuncios de paquetes." -- al hacer click se
muestra la segunda parte: "Tus datos se tratan según nuestra Política de
Tratamiento de Datos Personales, incluida la transferencia a servidores
fuera de Colombia de nuestro proveedor de infraestructura."

**Status:** implementado, pendiente confirmar visualmente

Seguimiento a [[351]] (que dejó ambas partes en un solo `<label>`).

## Decisiones

- **Mejora progresiva, no un `hidden` fijo en el HTML.** El aviso de
  privacidad es un aviso legal (Decreto 1377 de 2013, art. 4, ver [[351]]):
  si el JS falla o está deshabilitado, tiene que verse completo. El HTML
  llega con el aviso visible y el link "más..." oculto; un script al cargar
  invierte eso (oculta el aviso, muestra el link).
- **Dentro del mismo `<label>`**, no fuera: fuera de él volvería a ser
  `<label>` + otro elemento, justo lo que se pidió eliminar en [[351]]. El
  link es un `<a>` (no un `<button>`): un `<button>` es contenido
  "labelable" y HTML no lo permite anidado dentro de un `<label>` que
  apunta a otro control. Un click en un `<a>` anidado no tilda el
  checkbox (mismo mecanismo que ya usan los links de Términos y Privacidad).
- **Sin `class="block"` sobre el mismo elemento que lleva `hidden`:** las
  utilidades de display de Tailwind ganan por cascada al `[hidden]` (ya
  documentado en otras plantillas de este repo). El contenedor que se
  oculta es un `<span>` sin display propio; el salto de línea vive en un
  `<span class="block mt-1">` interno.
- Al hacer click el link desaparece (no vuelve a colapsar): lo pedido es
  solo "mostrar la segunda parte".
