# 342 — `/paquetes` modal "Ver": íconos "Modificar" y "Asignar apartamento" junto a Recibir/Entregar

**Pedidos originales (cliente), 2 mensajes seguidos (el 2do revisa al 1ro):**
1. "Necesito que en la vista de /paquetes para los iconos de 'Asignar
   apartamento' y 'Modificar' los incluyas en el modal del residente,
   especificamente al lado del codigo del paquete en este modal, recuerda
   conservar el mismo tamano de los iconos."
2. "o mas bien para esto ultimo que te pedi, puedes mejor ubicar los iconos
   al lado del boton de cambio de estado 'Recibir/Entregar'"

**Status:** implementado, pendiente confirmar visualmente

## Contexto

"Modificar" (columna Acciones, `packages/_acciones.html`) y "Asignar
apartamento" (🏠, columna Torre y Apartamento de la fila) solo vivían en la
tabla. El cliente pidió que también aparezcan dentro del modal "Ver" de
cada paquete, junto al botón "Recibir"/"Entregar" que ya vive ahí
(`packages/_resultados.html`, contenedor `<div class="flex items-center
gap-2">`).

Se interpretó "inclúyelas" como AGREGAR, no mover -- siguen existiendo
también en sus ubicaciones originales (columna Acciones / columna Torre y
Apartamento), el cliente no pidió quitarlos de ahí.

Hallazgo al implementar: el mecanismo `origen == "ver"` (decide si tras
corregir con éxito se reabre `/paquetes?ver=<id>` en vez del listado plano)
ya existía server-side (`correct_recipient_action`, `packages.py`) y en el
hidden input `corregir-origen-<id>`, pero estaba HUÉRFANO -- el único botón
que lo activaba (un "Corregir destinatario" distinto, dentro del propio
modal "Ver") se había retirado en issue 332. El nuevo botón "Modificar"
reactiva ese mecanismo ya construido, no fue necesario tocar el backend.

## Implementación

- `packages/_resultados.html`: 2 botones nuevos en el modal "Ver", antes
  del botón Recibir/Entregar, mismas condiciones de visibilidad que ese
  vecino ("terminales sin ícono" -- en ENTREGADO/CANCELADO no se renderiza
  nada):
  - "Modificar": mismo `chip_icono('slate', ...)` y mismo tamaño que la
    columna Acciones (pedido explícito: "conserva el mismo tamano de los
    iconos") -- el literal del tamaño (`clamp(1.625rem,7.8vw,2.15rem)`) se
    duplicó a propósito porque `_tam_accion` es privado a
    `_acciones.html` (Jinja no permite importar nombres con `_`). `origen`
    se pone en `'ver'` (no `''` como el de Acciones) para reabrir Ver tras
    corregir.
  - "Asignar apartamento": mismo emoji/tamaño (`text-lg`, sin chip) que la
    columna Torre y Apartamento -- solo si todavía no hay unidad asignada.
  - `chip_icono` se agrega al import de `components/_badge.html` en este
    archivo (antes solo lo usaba `_acciones.html`).
  - Comentario del hidden input `corregir-origen-<id>` actualizado --
    describía una 3ra entrada al modal Corregir que ya no existe
    (retirada en issue 332); ahora documenta la real (Acciones + este
    botón nuevo).

## Tests

- `test_packages.py::test_icono_asignar_apartamento_en_anunciado_y_recibido_sin_unidad`:
  el conteo de "🏠</button>" sube de 4 a 6 (2 paquetes × 3 ubicaciones ahora:
  fila desktop, píldora mobile, modal Ver -- antes 2).
- Suite completa `test_packages.py`: 230 passed.

## Verificación

Pendiente confirmación visual del cliente.
