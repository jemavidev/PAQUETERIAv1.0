# 68 — `/residentes`: batch de correcciones sobre el rediseño del issue 67

**Pedido original (cliente):** batch de 14 correcciones sobre lo entregado en
[[67]] (ver conversación completa). Resumen punto por punto:

1. Ficha (desktop): quitar la línea de subtítulo bajo el título ("+57... ·
   CONJUNTO... · Torre... · Apto...", clase `text-sm text-slate-500 ml-10`).
2. Explicar qué hace `segundo_contacto` (no era claro para el cliente).
3. Quitar el texto de ayuda bajo `whatsapp_usuario-help`.
4. Recepción automática: convertir en una etiqueta/badge visible en todo
   momento (lista y ficha), sin tener que entrar a validar.
5. Picker de Torre/Apartamento: reemplazar el `<select>` por 3 pasos de
   botones interactivos -- Torre (10) → Piso (primer dígito del número de
   apartamento) → Apartamento (número completo) -- con selección actual
   resaltada visualmente.
6. Tab Notificaciones: casillas desalineadas / contenido no justificado.
7. Propuesta (aceptada): separar Torre/Apartamento en su propia tab
   "Dirección".
8. Agregar el botón de eliminar cliente (Zona de peligro) también en la
   columna "Acciones" de la lista principal.
9. Mover los íconos de WhatsApp/llamada de la columna "Teléfono de
   contacto" a la columna "Acciones".
10. Renombrar la tab "Apartamento y Residentes" a solo "Residentes".
11. Distinguir visualmente Residente principal vs. secundario, visible en
    todo momento (lista y ficha), sin consultar nada adicional.
12. (aclaración) "botón eliminar" = la Zona de peligro existente.
13. Usuario de WhatsApp: anteponer `@` automáticamente, sin duplicarlo si
    ya viene con `@` (ej. pegado desde otro lado).
14. Barra de búsqueda de `/residentes`: alinear look and feel con
    producción (`paquetex.papyrus.com.co`).

**Status:** implementado

## Decisiones de implementación

- **Principal/secundario** (punto 11): solo aplica a Personas que además
  son Ocupante activo de su Apartamento (`ocupante_activo_de_persona`) --
  una Persona con apartamento asignado pero SIN pasar por "declarar
  unidad"/agregar residente no tiene Ocupante, así que no se le muestra
  ningún badge de principal/secundario (no aplica, no es un estado
  indefinido).
- **`whatsapp_usuario` + `@`**: se seguirá guardando SIN el `@` (la validación
  y el link `wa.me/<usuario>` no cambian) -- el `@` es puramente de
  presentación: se limpia cualquier `@` inicial al guardar (nunca puede
  quedar duplicado) y se antepone uno solo al mostrar el campo.
- **Barra de búsqueda** (punto 14): `/customers/manage` de producción está
  detrás de login de staff, no se pudo inspeccionar directo. Se usó
  `/search` (pública, mismo dominio) como referencia -- confirma el mismo
  patrón "ícono + subrayado" que ya usa `input_texto` en este proyecto.
  Pendiente de confirmar con una captura si `/customers/manage` se ve
  distinto.
- **Picker Torre/Piso/Apartamento**: 100% client-side (JS puro, sin
  petición nueva al servidor) sobre el mismo `catalogo_torres` que ya se
  pasaba al `<select>` -- los inputs reales siguen siendo
  `name="torre"`/`name="apartamento"` (ocultos), así que la ruta
  `/residentes/{id}/apartamento` no cambió.

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- **Verificación visual en navegador real** (Playwright, no solo tests):
  levantado el server local (`uvicorn`) contra un Postgres efímero con datos
  de prueba variados (cliente con apartamento + WhatsApp + auto-recepción +
  principal, cliente sin apartamento, residente secundario, admin/operador).
  Confirmado sin bugs: picker de Torre→Piso→Apartamento funciona de punta a
  punta (10 torres, pisos derivados, apartamentos filtrados, selección
  resaltada, precarga de la unidad actual, guardado real vía POST y
  re-render con la nueva selección), notificaciones alineadas en columnas,
  badges de header visibles en las 4 tabs, `@` antepuesto sin texto de
  ayuda, botón eliminar por fila en la lista (solo ADMIN), tabs en grid 2x2
  en mobile. Sin errores de consola en ningún paso.
- Suite completa (`tests/data_model tests/web`): 672/672, sin regresiones.
  22 tests nuevos (badges de Principal/Secundario y Recepción automática en
  lista y ficha, 4 tabs, `@` en `whatsapp_usuario` sin duplicarse, botón
  eliminar condicionado a rol, `ocupantes_activos_de_personas` batch,
  `url_whatsapp`/`url_llamada`).
- Tailwind recompilado y comiteado (clases nuevas: `grid-cols-5`, etc.) —
  `?v=34` → `?v=35`.
- Pendiente: confirmar con el cliente en vivo, en particular si la barra de
  búsqueda coincide con lo que ve en `/customers/manage` de producción (no
  se pudo inspeccionar esa página directamente, está detrás de login).
