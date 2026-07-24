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
