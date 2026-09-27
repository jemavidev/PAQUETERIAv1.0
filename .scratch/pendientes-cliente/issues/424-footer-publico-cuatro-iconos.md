# 424 — Footer público: siempre los 4 íconos (Anunciar, Consultar, Ayuda, WhatsApp)

**Pedido original (Jesús, 2026-09-27):** "veo que para el footer de la vista publica /ayuda se tienen 4 iconos (Anunciar,
Consultar, Ayuda y Whatsapp) estos deben ser los iconos por default que deberia mostrar el aplicativo en todas las vistas
publicar cuando los usuarios no esten logueados o este el bloqueo activo por PIN para usuarios de staff." Confirmado: "usemos
la version de los 4 iconos".

**Status:** desplegado en test (`860699b`, 2026-09-27), pendiente confirmar en vivo

## Causa

El footer público ya era el mismo en todas las vistas, pero WhatsApp solo salía en `/ayuda`: el número configurado en
Administración → Conjunto (`ConfiguracionConjunto.numero_whatsapp`, issue 350) solo lo leía la ruta de `/ayuda`. El resto
caía a la variable de entorno `WHATSAPP_SOPORTE_NUMERO`, vacía donde no está configurada.

## Alcance

- El footer lee el número vigente (BD si hay; si no, la variable de entorno) en TODAS las vistas: los 4 íconos del
  footer público quedan fijos sin sesión y con el equipo bloqueado (`/bloqueo`). El WhatsApp de los footers de cliente y
  de escritorio usa el mismo número.
- Sin cambios: la capa de bloqueo sigue tapando toda la pantalla, y un residente con sesión propia conserva su footer de
  cliente.
