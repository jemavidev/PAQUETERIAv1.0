# 115 — Modal "Recibir": limpieza de textos, cámara para fotos, botón "Recibir"

**Pedido original (cliente), 6 puntos en un mismo mensaje (el último llegó
en dos partes):**
"Remueve esto del modal de recibir 'Este destinatario todavía no tiene
apartamento — podés declararlo acá (opcional).'. Incluye la etiqueta de
'Apartamento' en el mismo input que dice 'Ej. 302'. Incluye 'Guía del
transportador (opcional)' en el input de la guia, deberia decir 'Guía'.
Remueve este texto 'Fotos (opcional, hasta 3 ángulos)', y permite que se
pueda usar la camara de dispositivos mobiles para capturar las imagenes,
recuerda que son maximo 3 imagenes. Cambia el Nombre de[l boton
'Confirmar recibo' a 'Recibir']."

**Status:** implementado

## Implementación

- `_recibir_paquete.html`: se quita el párrafo "Este destinatario
  todavía no tiene apartamento...". Botón final `"Confirmar recibo"` →
  `"Recibir"`. El input de Guía pierde su `<label>` separado --
  `placeholder="Guía"` en el input mismo, con `aria-label="Guía del
  transportador"` para lectores de pantalla (el texto completo no
  desaparece, solo deja de ocupar una línea propia).
- `_picker_apartamento.html`: el `<label>Apartamento</label>` separado se
  quita -- el input pasa a `placeholder="Apartamento (ej. 302)"` +
  `aria-label="Apartamento"`. Este componente es compartido con "Asignar
  apartamento" (issue 114) -- el cambio aplica en los dos lugares por
  igual, no solo en Recibir, ya que es la misma simplificación visual en
  ambos (más compacto, sin perder claridad).
- `_carga_fotos.html`: `etiqueta` default pasa de `'Fotos (opcional,
  hasta 3 ángulos)'` a `none` (sin texto) -- único consumidor real es
  Recibir, cambiar el default no afecta a nadie más. El `<input
  type="file">` gana `capture="environment"` -- en mobile, permite
  disparar la cámara del dispositivo directo desde el mismo control,
  sin dejar de poder elegir fotos ya existentes de la galería. El tope
  de 3 fotos no cambia (`fijarArchivos` ya recortaba a `MAX` antes de
  esto).

## Verificación

- `tests/web/test_packages.py`: tests actualizados/nuevos para el texto
  quitado, el placeholder nuevo del picker, el placeholder "Guía", la
  etiqueta de fotos ausente, `capture="environment"` presente, y el
  botón "Recibir" (ya no "Confirmar recibo").
- Playwright contra el servidor local real: captura del modal Recibir
  confirmando visualmente los 6 puntos.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
