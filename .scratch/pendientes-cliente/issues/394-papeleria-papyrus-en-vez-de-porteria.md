# 394 — "La papelería Papyrus" / "el personal de Papyrus" en vez de "portería" / "portero"

**Pedido original (Jesús):** "en varias partes del sistema hablas de "El portero", la realidad es que no está enfocado a
porteros de un edificio, ... será personal de la papelería Papyrus los que están prestando el servicio, la idea es que
se identifiquen en el sistema pero no como porteros". Respuestas: el transportador deja el paquete en el punto Papyrus
("el punto Papyrus es correcto"); nombre del lugar: "... en la papelería Papyrus".

**Status:** implementado, pendiente confirmar en vivo (localhost)

## Decisiones

- Hacia el residente: el LUGAR es "la papelería Papyrus" y las PERSONAS son "el personal de Papyrus". Nunca
  "portería"/"portero". La plataforma sigue llamándose PAQUETEX. Internamente sin cambios: Staff (Admin/Operador).
- Se cambian los 11 textos visibles: mensajes de tope de `/anunciar` (2) y del OTP, nota de `/consultar` ofuscado,
  cuenta sin verificar, *Cómo funciona* (3), Términos, Privacidad, y el asunto por defecto del correo de "Recibido".
- Glosario (`CONTEXT.md`): término oficial hacia el cliente y "portería/portero" como término evitado.
- Datos de prueba: "Portero Juan"/"Portero Externo" renombrados.
- Plantillas de SMS/correo ya editadas por un admin en el servidor viven en su BD: se revisan a mano en
  `/administracion/notificaciones` (en la BD local no hay ninguna con "portería").

## Verificación

- `tests/web/test_textos_papeleria_papyrus.py` (8): ninguna página pública (`/como-funciona`, `/terminos`,
  `/privacidad`, `/anunciar`, `/otp`, `/consultar`) dice "portería"/"portero"; *Cómo funciona* nombra a la papelería y
  al personal de Papyrus; asunto del correo de Recibido. Ajustadas: `test_anunciar_limites_por_telefono.py` y los
  nombres de datos de prueba. 127 en verde con notificaciones y páginas legales.
- `CONTEXT.md`: término oficial hacia el residente + "portería"/"portero" como términos evitados.
- Quedan "Portero" como nombre de anunciante de ejemplo en 3 pruebas antiguas: no es texto del sistema.
