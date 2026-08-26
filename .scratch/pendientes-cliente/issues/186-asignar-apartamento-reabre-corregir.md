# 186 — "Asignar apartamento" sin residente dejaba el paquete a medio asociar

**Pedido original:** reporte en vivo -- "agregue este paquete 'RAFA T 26NU' y trate de asociarlo
al apartamento 302 de la torre 2, donde la [está] Angelica... analiza que paso" → diagnosticado
con evidencia directa de la base de datos local (ver Diagnóstico) → confirmado el plan de fix:
"sí, lo que recomiendes."

**Status:** implementado

## Diagnóstico

Reconstruido con datos reales de la base local: el paquete se anunció con solo un teléfono (sin
unidad), y ~2 horas después se usó "Asignar apartamento" para ponerle Torre 2 / Apto 302 -- SIN
abrir la sección opcional "+ Nuevo residente" (colapsada por defecto). Resultado: la columna
Dirección del paquete mostraba "Torre 2 · Apt 302" (decorativo, viene del snapshot del propio
Paquete), pero **no existía ningún Ocupante real vinculado** -- el destinatario no aparecía como
residente de esa unidad en `/residentes`, no aparecía en "Agrupar por apartamento", y no tenía
ninguna relación con Angelica (la Principal real de esa unidad). Comportamiento documentado a
propósito en issue 149 ("asignar SOLO la unidad acá nunca registra un residente"), pero sin ningún
aviso ni guía de que ese segundo paso seguía pendiente -- el hueco real no es que sea posible
dejarlo así, es que nada lo señala.

## Cambio

- `packages.py` (`assign_apartment_action`): cuando `nuevo_ocupante_nombre` queda vacío (el staff
  no llenó "+ Nuevo residente"), el redirect de éxito cambia de `/paquetes` a
  `/paquetes?corregir=<id>` -- mismo query param que ya usa `packages_list` para reabrir
  "Corregir destinatario" (`corregir_paquete_id`). Con la unidad YA resuelta en el snapshot,
  `candidatos_correccion` encuentra a los Ocupantes reales de esa unidad (Angelica, en el caso
  real) y los muestra como tarjetas de un clic -- el staff completa la asociación real sin tener
  que saber que hacía falta un segundo paso, ni volver a buscar el paquete en la lista.
  Cuando SÍ se llenó "+ Nuevo residente", la asociación ya quedó completa en el mismo envío --
  sigue redirigiendo a la lista sola, sin cambios.
- No se reescribió la base de datos local para "RAFA T 26NU" -- es dato de prueba que sirvió para
  encontrar el bug; con el fix, reproducir el mismo flujo hoy ya reabre Corregir y ofrece a
  Angelica como candidata.

## Verificación

- 2 tests nuevos: `test_asignar_apartamento_sin_nuevo_residente_redirige_a_corregir` (confirma el
  nuevo `Location`, sigue el redirect y confirma que el modal Corregir queda abierto con la
  candidata real ofrecida) y `test_asignar_apartamento_con_nuevo_residente_no_redirige_a_corregir`
  (guard: con "+ Nuevo residente" lleno, sigue yendo a `/paquetes` sin cambios).
- Suite completa.
- Pendiente: verificar en test.papyrus.com.co tras deploy.
