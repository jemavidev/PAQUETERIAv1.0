# 432 — Enlaces de WhatsApp de escritorio abren la app instalada de WhatsApp Web

**Pedido original (Jesús):** probó "Solicitar autorización por WhatsApp" (`/announce`) en escritorio: "funciona de
maravillas, como debería funcionar, aplica esto al resto de mensajes de WhatsApp para el escritorio".

**Status:** implementado (local, sin desplegar)

## Contexto

Chrome solo manda un enlace a la app instalada (navigation capturing) cuando el clic abre un contexto nuevo
(`target="_blank"`); un clic que navega en la misma pestaña no se captura
(`.scratch/whatsapp-deep-link/investigacion-oficial.md`). El botón de `/announce` era el único enlace de escritorio con
`target="_blank" rel="noopener"`.

## Decisiones

- Todo enlace de WhatsApp de escritorio (`web.whatsapp.com/send?phone=`) lleva `target="_blank" rel="noopener"`:
  Acciones de `/paquetes`, lista/tabla y vista agrupada de `/residentes`, footer de escritorio.
- Límite: cuando la persona tiene usuario de WhatsApp (no número), el enlace es `wa.me/<usuario>` también en
  escritorio -- `web.whatsapp.com/send` solo acepta números, y `wa.me` no está en el alcance de la app instalada, así
  que no puede abrirla. Es el caso de los enlaces del modal Ver (solo aparecen con usuario de WhatsApp): quedan igual.
- Los enlaces de celular (`wa.me`) no cambian.

## Verificación

- `tests/web/test_whatsapp_escritorio_nueva_pestana.py`: todo `<a href="https://web.whatsapp.com/...">` de `/paquetes`,
  `/residentes` (lista y vista agrupada) y el footer de escritorio lleva `target="_blank" rel="noopener"` (3 fallaban
  antes); los `wa.me` de celular no cambian. Pruebas de WhatsApp/footer/Acciones existentes: 51 en verde.
