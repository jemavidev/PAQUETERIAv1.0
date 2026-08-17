# 111 — Modal "Cancelar": motivos en lista, botón "Cancelar", sin "Volver", "Otro" revela input

**Pedido original (cliente):**
"Necesito modificar el modal de Cancelar, lo que necesito es que las
opciones que se tienen se muestren en forma de lista. Cambia el
contenido del boton de confirmar de 'Confirmar cancelación' a
'Cancelar'. Remueve el boton de 'Volver'. Si se presiona el boton de
'Otro' se deberia mostrar un input para escribir una posible causa que
no este representada en la lista anterior."

**Status:** implementado

## Contexto

El modal de Cancelar usa el macro compartido `modal_confirmacion`
(`components/_modales.html`) -- el MISMO que usan "Eliminar paquete"
(`/paquetes`) y "Eliminar cliente" (`/residentes`). "Remueve el botón
Volver" y "cambia el texto del botón" no podían aplicarse tocando el
macro a secas -- hubiera apagado "Volver" y renombrado el botón en esos
otros 2 modales, que nadie pidió tocar.

## Implementación

- `_modales.html`, `modal_confirmacion`: nuevo parámetro
  `mostrar_volver=True` (default preserva el comportamiento exacto de
  Eliminar paquete/Eliminar cliente, sin tocarlos). El botón "Volver"
  ahora es condicional a ese parámetro. Sigue existiendo una salida sin
  confirmar aunque no haya "Volver": clic en el fondo oscuro
  (`data-close` en el overlay) sigue cerrando el modal, mismo mecanismo
  de siempre.
- `_resultados.html`, modal Cancelar: `texto_confirmar` pasa de
  "Confirmar cancelación" a "Cancelar", `mostrar_volver=False`.
  `grupo_chips('motivo', ...)` (chips en fila, pensado para <5 opciones
  mostradas como pastillas envueltas) se reemplaza por una lista vertical
  propia -- mismo mecanismo de radio real oculto + `peer-checked` que ya
  usa `grupo_chips`, pero apilada en filas de ancho completo en vez de
  envueltas. Al marcar "Otro" aparece un `<input>` de texto libre
  (`motivo_otro`, JS vainilla mínimo, mismo criterio ADR-0004 que ya usa
  el resto de esta vista) -- se oculta y limpia si se vuelve a elegir
  cualquier otro motivo.
- `packages.py`, `cancel_action`: nuevo campo `motivo_otro: str =
  Form(None)`. Si `motivo == "OTRO"` y `motivo_otro` trae texto, ESE texto
  (no el literal "OTRO") es lo que se guarda en `cancel_reason` -- la
  causa real queda en la auditoría, no un placeholder genérico. Si se
  marca "Otro" sin escribir nada, sigue cancelando con "OTRO" como motivo
  (no bloquea la cancelación por dejarlo vacío, mismo criterio permisivo
  que el resto del formulario, que tampoco fuerza `required` en el picker
  de motivo -- la validación real vive en el dominio, `cancel()` sigue
  exigiendo motivo no vacío).

## Verificación

- `tests/web/test_packages.py`: tests nuevos -- lista de motivos renderiza
  como filas (no como fila de chips envueltos), botón dice "Cancelar",
  "Volver" ausente del modal de Cancelar (presente sin cambios en
  Eliminar paquete), input `motivo_otro` oculto por defecto, cancelar con
  motivo="OTRO" + `motivo_otro` guarda el texto libre en `cancel_reason`,
  cancelar con motivo="OTRO" sin texto libre guarda "OTRO" (fallback).
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
