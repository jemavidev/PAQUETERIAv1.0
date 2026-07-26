# Paquetes: colores, filtros, paginación y enlace a anunciar completo

Fuente: `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 5.

## Problem Statement

`/paquetes` lista TODOS los paquetes sin filtro ni paginación — con muchos paquetes es una lista larga e inmanejable. Los colores de estado no siguen la convención que el staff espera. Y no hay forma directa de llegar al formulario completo de anunciar (`/announce`, Grupo 6) desde la pantalla principal de trabajo del staff.

## Solution

Colores de estado: Anunciado → naranja, Recibido → azul, Entregado → verde, Cancelado → rojo. Filtros por estado, código de acceso, guía, nombre del cliente, teléfono, torre y apartamento — combinables, vía querystring (`GET /paquetes?estado=...&q=...&torre=...`). Paginación de 20 por página, con controles arriba y abajo de la lista. Un enlace visible hacia `/announce` para el flujo completo de staff.

## User Stories

1. Como miembro del staff, quiero identificar el estado de un paquete por color de un vistazo, usando la convención que ya conozco (naranja/azul/verde/rojo).
2. Como miembro del staff, quiero filtrar la lista por estado, para enfocarme en lo que sigue pendiente.
3. Como miembro del staff, quiero buscar por código de acceso o guía, para encontrar un paquete específico que un residente menciona por teléfono.
4. Como miembro del staff, quiero buscar por nombre del cliente o teléfono, para ubicar los paquetes de una persona sin recorrer toda la lista.
5. Como miembro del staff, quiero filtrar por torre y apartamento, para revisar los paquetes de una unidad puntual.
6. Como miembro del staff, quiero combinar varios filtros a la vez (p.ej. estado + torre), para acotar más la búsqueda.
7. Como miembro del staff, quiero paginación arriba y abajo de la lista, para no perder el control al llegar al final de una lista larga.
8. Como miembro del staff, quiero un enlace directo a `/announce` desde `/paquetes`, para declarar unidades o anunciar con más datos sin salir del flujo de trabajo.

## Implementation Decisions

- **Colores** (`packages/list.html`, solo CSS): `.estado-anunciado` → naranja, `.estado-recibido` → azul, `.estado-entregado` → verde (sin cambio), `.estado-cancelado` → rojo. Mismo cambio de paleta en `search/form.html` (la vista de consulta del cliente usa las mismas clases) para mantener consistencia visual entre ambas vistas.
- **Filtros** (`GET /paquetes`, querystring): `estado`, `q` (busca por `access_code` O `guide_number` O `recipient_name` parcial O teléfono normalizado — el mismo campo cubre varios casos, como ya hace `/residentes`), `torre`, `apartamento`. Todos opcionales y combinables (AND entre los que vengan informados).
- **Paginación**: parámetro `pagina` (default 1), 20 resultados por página. Controles (Anterior / números / Siguiente) renderizados arriba y abajo de la lista — mismo componente reusado dos veces en la plantilla.
- **Enlace a `/announce`**: en el encabezado de `/paquetes`, junto al enlace "sesión" ya existente.
- **No se toca** la lógica de acciones (recibir/entregar/cancelar/corregir) ni la advertencia de nombre-no-coincide — siguen funcionando igual, ahora sobre una lista filtrada/paginada en vez de la lista completa.

## Testing Decisions

- Seam web (`tests/web/test_packages.py`, extender): cada filtro por separado (estado, código, guía, nombre, teléfono, torre, apartamento); combinación de dos filtros; paginación (más de 20 resultados, página 2 muestra los siguientes, controles visibles); colores correctos por estado (aserción sobre la clase CSS, no sobre el texto).
- Prior art: mismo patrón de query-string + filtros combinables que ya usa `/residentes` (`customers_manage.py`), aunque ahí es un solo campo `q`.

## Out of Scope

- Ordenar por columnas distintas a `announced_at` (fecha) — no se pidió.
- Exportar/descargar la lista filtrada.

## Further Notes

Esta rebanada es puramente aditiva sobre `/paquetes` — no depende de otro grupo pendiente (el enlace a `/announce` ya existe como ruta desde el Grupo 6).
