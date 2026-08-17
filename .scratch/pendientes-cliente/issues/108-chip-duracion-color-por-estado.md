# 108 — Chip de duración toma el color del Estado (mismo rol, fondo redondeado)

**Pedido original (cliente):**
"ahora puedes colocar ese mismo con border similar como has echo en otra
informacion como la de la hora dentro del modal o el estado que estan en
un fondo redondeado y de color, que me sugieres" -- se presentaron 2
opciones (A: mismo color que el badge de Estado de al lado; B: color por
umbral de urgencia). El cliente eligió **Opción A**.

**Status:** implementado

## Contexto

Evolución directa de [[107]] (mismo día): el chip de duración ("3 días y
2 horas") quedó en gris plano (`bg-slate-100`/`border-slate-200`) al
implementarse -- el cliente pidió emparejarlo visualmente con el badge de
Estado que tiene al lado (`{{ badge(p.estado) }}`), que sí usa fondo
suave de color por rol (ámbar/azul/verde/rojo según `ANUNCIADO`/
`RECIBIDO`/`ENTREGADO`/`CANCELADO`).

## Implementación

- `_resultados.html`, chip de duración: se agrega un diccionario local
  `duracion_colores` con la MISMA paleta que usa `_badge.html` (mismos 4
  valores de `clases` -- ámbar/azul/verde/rojo), indexado por
  `p.estado.value`. Se mantiene local a `_resultados.html` en vez de
  importar/refactorizar `_badge.html` -- ese macro se usa en varios
  lugares de la app, y este es un ajuste puntual de esta sola vista;
  mismo criterio que ya usa `_timeline.html` (su propio dict `roles`,
  independiente del de `_badge.html`, sin compartir entre componentes).
  El chip siempre queda sincronizado con el badge de Estado de al lado
  porque ambos leen el mismo `p.estado.value` -- no hay riesgo de que se
  desincronicen.

## Verificación

- `tests/web/test_packages.py`: test nuevo que confirma el chip de
  duración lleva la clase de color correspondiente al Estado actual del
  paquete (ej. `bg-blue-100` en RECIBIDO, igual que el badge).
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
