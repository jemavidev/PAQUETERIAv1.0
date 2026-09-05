# 306 — Botón flotante + glow en los modales de confirmación (vistas de staff)

**Pedido original (cliente):** el botón de confirmación del modal "Recibir" queda al final del
contenido -- hay que hacer scroll/swipe hasta el fondo para llegar a él. Pide: (1) que el botón sea
flotante, siempre visible mientras se interactúa con el modal; (2) que al llegar al final del scroll,
ese botón flotante NO tape la última línea de información; (3) sin fondo blanco detrás del botón;
(4) un glow alrededor para distinguir que está flotando -- probamos rojo primero, pero coincidiendo
que el rojo ya es Cancelar/Eliminar en esta app, se define **violeta** (único tono libre, no choca con
ningún Estado ni ícono existente). Aprobado en "Recibir", el cliente pidió replicarlo a **todos los
modales del aplicativo**; acotado con el cliente a **solo vistas de staff** (`/paquetes`,
`/residentes`, `/administracion`) -- pantallas de cliente (`customer/verify.html`, `/mis-datos`) y
`/consultar` (pública) quedan FUERA de este alcance a propósito.

**Status:** implementado en todos los modales de staff salvo un caso pendiente de decisión (ver
abajo) -- pendiente verificar visualmente en vivo (extensión de Chrome no disponible en esta sesión).
415 tests relacionados en verde (`test_packages.py`, `test_customers_manage.py`,
`test_admin_staff.py`, `test_admin_notificaciones.py`) -- solo confirman que el HTML se sigue
generando bien, no el comportamiento visual del `sticky`/glow.

## Enfoque técnico

`position: sticky; bottom: 0` sobre el botón (sin fondo propio, glow violeta
`shadow-[0_0_18px_rgba(139,92,246,0.65)]` en vez de `shadow-sm`), nunca `fixed`/`absolute`: sigue
siendo un elemento de flujo real, así que el navegador le reserva su espacio -- resuelve "siempre
visible" y "no tapa la última línea" a la vez, sin padding-bottom calculado a mano. `-mx-5 -mb-5`
cancela el `p-5` del contenedor con scroll para que la barra llegue a los bordes reales del modal.

Dos mecanismos distintos según el macro:
- **`modal_confirmacion()`** (`components/_modales.html`): parámetro nuevo `boton_flotante=False`
  (opt-in) -- con `True` la fila de botones ("Regresar" + confirmar) queda sticky y el botón de
  confirmar suma el glow. `False` por defecto para no afectar callers fuera de alcance
  (`customer/verify.html`).
- **`boton()`** (`components/_botones.html`, usado fuera de modales también -- login, `/anunciar`,
  `/administracion/proveedores`): parámetro nuevo `flotante=False` (opt-in) -- solo cambia la sombra
  del botón; el posicionamiento sticky lo arma el caller envolviéndolo en su propio `<div>`, igual
  que un `<button>` sin macro.
- Botones sueltos (sin macro): se envuelve cada uno a mano, mismo patrón que "Recibir".

## Aplicado en

- **`/paquetes`** (`packages/_resultados.html`): Recibir, Asignar apartamento, Corregir destinatario
  (los 2 "Guardar" -- nuevo residente y texto libre; las TARJETAS de candidatos, que son selección
  de un clic, no botón de confirmar, se dejaron igual a propósito), Entregar, Eliminar paquete,
  Cancelar paquete.
- **`/residentes`** (`customers_manage/detail.html`, `customers_manage/_resultados.html`): Editar
  ocupante (Guardar -- "Quitar teléfono"/"Quitar WhatsApp" son enlaces de texto secundarios, se
  dejaron igual), Dar de baja, Convertir en principal, Eliminar residente.
- **`/administracion/personal`** (`admin/staff.html`): Editar usuario, Resetear contraseña, Nuevo
  usuario.
- **`/administracion/notificaciones`** (`admin/notificaciones.html`): Agregar motivo, Editar motivo,
  Borrar motivo.

## Seguimiento -- "Regresar" decorativo + ambigüedad de "Cancelar"

Retroalimentación en vivo tras ver el resultado: el botón "Regresar" (cierra el modal sin hacer
nada) es decorativo en TODOS los modales de confirmación -- tocar el fondo oscuro afuera del modal
ya cumple la misma función. Se retira parejo (`mostrar_volver=False`) en los 10 modales que lo
tenían, incluidas las 4 vistas de cliente (`customer/verify.html`) -- a diferencia del tratamiento
sticky/glow, esto se pidió "a todos" sin acotar a staff, y remover un control redundante (no una
capacidad) es de bajo riesgo igual en cliente.

Al quedar sin "Regresar", "Cancelar paquete" (`/paquetes`) pasó a tener un solo botón, y ese botón
decía literalmente "Cancelar" -- ambiguo entre "cerrar este diálogo" y "confirmar la cancelación
del paquete" (dato encontrado en el propio código: el 2026-08-17 el cliente ya había pedido
explícitamente ese texto, y en su momento se descartó "Confirmar cancelación" por el mismo botón).
Revisé el resto de la app -- es el ÚNICO botón de confirmación que reutiliza una palabra que también
significa "abortar". Autorizado por el cliente: pasa a **"Confirmar"** (una sola palabra, sin la
ambigüedad -- el título "Cancelar paquete" y el mensaje "Esta acción es irreversible" ya comunican
qué hace).

Tests actualizados: `test_modal_eliminar_no_tiene_boton_regresar` (antes afirmaba lo contrario) y
`test_modal_cancelar_boton_dice_confirmar_y_no_tiene_regresar` (antes esperaba "Cancelar"). 462 + 15
tests relacionados en verde.

## Pendiente de decisión -- NO tocado todavía

El modal de plantillas de notificación (`admin/notificaciones.html`, `modal('notif-' ~ fila_id, ...)`)
tiene una estructura distinta al resto: por cada canal (SMS/Email/WhatsApp) hay DOS botones
independientes -- "Guardar" (plantilla) y "Enviar prueba" -- cada uno en su propio `<form>`, uno
debajo del otro. Poner los DOS sticky a la vez los haría competir por el mismo `bottom: 0` y
solaparse. Falta decidir con el cliente: ¿solo "Guardar" flota?, ¿se unifican los dos en una sola
barra al fondo?, ¿se deja este modal sin el tratamiento por ser un caso distinto (edición de texto
largo, no una confirmación puntual)?
