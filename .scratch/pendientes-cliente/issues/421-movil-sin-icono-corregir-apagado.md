# 421 — En móvil, sin apartamento, no se muestra el ícono apagado de Corregir

**Pedido original (Jesús, 2026-09-27):** "para la version movil en caso que que no exista un apartamento, no deberia poder verse el
icono de "Asigna un apartamento primero"". Mismo criterio que el issue 345 (en móvil lo que no se puede usar no se muestra).

**Status:** implementado (local), pendiente desplegar

## Alcance

- Modal "Ver" en móvil (< 640 px), paquete sin apartamento: el ícono de Corregir (apagado, 419) no se renderiza visible; queda el
  🏠 de Asignar apartamento. Escritorio sin cambios (gris con el aviso). En la tarjeta móvil nunca estuvo.
