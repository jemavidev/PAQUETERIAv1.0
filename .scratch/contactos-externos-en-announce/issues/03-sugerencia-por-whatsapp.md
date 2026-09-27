# 03 — Sugerencia por usuario de WhatsApp

**What to build:** la misma experiencia del ticket 02 cuando el valor tecleado en el campo único de `/announce` es un **usuario de WhatsApp** válido: si no existe en paquetes pero coincide con un Contacto externo, el Staff ve el mensaje y la tarjetita con el nombre, la elige, y Anunciar o Recibir registra a la Persona con ese nombre y ese usuario de WhatsApp (ADR-0007: una Persona puede tener solo WhatsApp, sin Teléfono).

**Spec:** `.scratch/contactos-externos-en-announce/spec.md` (historias 2, 3, 4, 5 y 28 —para WhatsApp—).

**Blocked by:** 02 — Sugerencia por Teléfono: elegir el nombre de un Contacto externo y anunciar o recibir a su nombre.

**Status:** abierto -- revisado 2026-09-26: sin implementar: `sugerir_nombre_de_contacto_externo` devuelve None para `whatsapp` ("llega con el ticket 03")

- [ ] Un usuario de WhatsApp que **no existe en paquetes** y coincide de forma exacta con **cualquiera de los usuarios de WhatsApp** de un Contacto externo produce la misma sugerencia que el Teléfono: mismo mensaje, misma tarjetita solo con el nombre, mismo desplegable "Nueva persona" plegado.
- [ ] La coincidencia ignora el formato de entrada: con o sin `@` inicial y en cualquier combinación de mayúsculas y minúsculas (la forma canónica es sin `@` y en minúscula).
- [ ] La tarjeta seleccionada lleva el **usuario de WhatsApp** (no un Teléfono) y el nombre como datos ocultos; Anunciar registra la Persona con ese usuario de WhatsApp y el nombre en MAYÚSCULAS, y crea el Paquete en `Anunciado`; Recibir además abre el modal de recepción.
- [ ] Mismas reglas de "cuándo no": no se sugiere si existe una Persona con ese usuario de WhatsApp (activa, De baja o Bloqueada); sin coincidencia externa el fragmento es idéntico al de hoy; un valor de 1 o 2 letras no dispara nada.
- [ ] Un Contacto externo encontrado por su Teléfono y otro encontrado por su WhatsApp son independientes: cada valor tecleado consulta solo su propia llave.
- [ ] Solo se expone el nombre, y el Contacto externo queda intacto tras usar la sugerencia.
- [ ] Pruebas web (rutas HTTP de `/announce`) para cada punto, incluyendo formatos de entrada distintos y un contacto con varios teléfonos y varios usuarios de WhatsApp; las pruebas del ticket 02 y las existentes siguen pasando.
