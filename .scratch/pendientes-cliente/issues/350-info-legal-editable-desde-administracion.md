# 350 — Info legal/cambiante (NIT, dirección, razón social, etc.) editable desde `/administracion` y reflejada en páginas públicas

**Pedido original (Jesús, en el grilling de las páginas legales/informativas):**
"Ten presente que a futuro estaremos enfocándonos en que esa información
cambiable pueda ser actualizada en un formulario del aplicativo y que se
refleje en las páginas públicas (ejemplo: tarifas, conjunto, NIT, dirección,
en general todo lo que podría cambiar, este podría ser en la vista de
`/administracion/conjunto`)."

**Status:** desplegado a test.papyrus.com.co (2026-09-19), pendiente que el
cliente lo confirme visualmente — `ConfiguracionEmpresa` (razón social, NIT,
dirección, contacto) + horarios de atención en `ConfiguracionConjunto`,
editables desde `/administracion/conjunto`, reflejados en vivo en
`/ayuda`, `/terminos`, `/privacidad`, `/cookies`.

## Contexto

Hoy los datos de la empresa (razón social, email, teléfono, dirección) están
*hardcodeados* de forma idéntica en 4 plantillas distintas
(`CODE/src/app/web/templates/{ayuda,terms,privacy,cookies}/form.html`) —
sin fuente única de verdad. Las tarifas de cobro sí tienen fuente de verdad
real (`/administracion/tarifas-cobro`, tabla de tarifas vigentes) pero las
páginas legales actuales las citan como texto fijo, desincronizado.

## Alcance futuro (a definir cuando se retome)

- Un formulario en `/administracion/conjunto` (o donde se decida) para
  editar razón social, NIT, representante legal, dirección, teléfono, email
  de contacto — cualquier dato que hoy vive hardcodeado en las 4 plantillas
  legales.
- Las páginas públicas (`/ayuda`, `/terminos`, `/privacidad`, `/cookies`)
  leen esos valores en vez de tenerlos fijos en el HTML.
- Las tarifas mostradas en contenido público (si se decide mostrarlas) se
  resuelven en vivo desde `obtener_tarifas_vigentes` (mismo dominio que ya
  usa `/administracion/tarifas-cobro`), nunca como texto fijo.

## Por qué queda pendiente ahora

El trabajo actual (grilling en curso, 2026-09-18) se acotó explícitamente a
**contenido**, no a features nuevas de administración — evita mezclar una
decisión de producto de más peso (qué campos son editables, quién los edita,
versionado de cambios a un documento legal) con la tarea de corregir el
contenido desactualizado. Cuando se retome, probablemente amerite pasar por
`codebase-design` (dónde vive el modelo de "datos de la empresa") y/o
`/to-tickets` si se desglosa en varios cambios.
