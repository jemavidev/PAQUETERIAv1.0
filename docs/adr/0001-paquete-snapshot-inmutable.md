---
status: accepted
---

# El Paquete congela su contexto de entrega como snapshot inmutable

Al **anunciar**, el Paquete copia `{anunciado_por (teléfono), nombre_destinatario, teléfono_destinatario (si hay), apartamento}` a **columnas propias denormalizadas** en vez de referenciar el Apartamento (u otras entidades mutables) por FK. Elegido porque un FK seguiría a la Persona cuando ésta se muda y **reescribiría los paquetes viejos**; el objetivo del dominio es que "los datos permanecen de principio a fin en cada paquete".

## Considered Options

- **FK al Apartamento vivo (normalizado, DRY).** Rechazado: mudar a una Persona cambiaría la dirección mostrada en todos sus paquetes históricos — la historia se reescribe sola. Es exactamente el defecto del modelo viejo (`customer_id` único + `display_name` huérfano).
- **Snapshot como JSON congelado.** Descartado frente a columnas discretas: el snapshot de apartamento debe ser **consultable** desde `/search`.

## Consequences

- El Anunciante sí puede referenciarse por FK a Persona (su Teléfono es estable, no muta), pero el **snapshot es la fuente de verdad** para mostrar e historizar el paquete.
- Hay duplicación deliberada de datos de apartamento entre `apartamentos` y las columnas-foto del Paquete. Es el costo aceptado de la inmutabilidad.

## Excepciones conocidas — acotadas y auditadas, no un FK vivo

Esta ADR protege contra que un FK a una entidad mutable reescriba paquetes viejos SOLO porque la
Persona cambió después — no contra que el staff corrija, de forma explícita, un dato del snapshot
que quedó incompleto o con un error de tipeo. Dos funciones de `paquete_lifecycle.py` implementan
esta excepción, cada una con su propio guard de estado acotado y el mismo rastro de auditoría
(`corrected_at`/`corrected_by_usuario_id`):

1. **`corregir_destinatario`** — corrige `recipient_name`/`recipient_phone` (ej. error de tipeo del
   cliente al anunciar). Guard: `ESTADOS_CORREGIBLES` (`ANUNCIADO`/`RECIBIDO`/`ENTREGADO` — ampliado
   2026-08-16, pedido explícito del cliente: el typo no siempre se nota mientras el paquete sigue
   `ANUNCIADO`). `CANCELADO` queda afuera — no tiene sentido de negocio corregir el destinatario de
   un paquete que nunca se entregó.
2. **`corregir_apartamento`** — corrige el snapshot de Apartamento cuando un Paquete se anunció
   antes de que su Teléfono estuviera vinculado a una unidad, y ese Teléfono se vincula después
   (`.scratch/asociacion-retroactiva-apartamento`). Guard: `ANUNCIADO` únicamente (sin cambios).
   Comparte las mismas columnas de auditoría que `corregir_destinatario` — el esquema no distingue
   cuál de las dos correcciones ocurrió.
