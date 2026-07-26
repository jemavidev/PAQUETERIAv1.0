---
status: accepted
---

# Ocupante: residentes de un Apartamento sin Persona propia

Hoy el único caso de "nombre sin teléfono" es efímero y vive solo dentro del snapshot de un Paquete puntual (ADR-0003) — no hay forma de reconocer, de manera persistente, a un residente de un Apartamento que no tiene (o no quiere dar) su propio Teléfono. En la práctica, un apartamento suele tener varios residentes y no todos cargan celular propio; forzarlos a re-teclear su nombre en cada anuncio es fricción evitable.

Se decide introducir **Ocupante**: una entidad nueva, separada de Persona, ligada a un Apartamento, con Teléfono **opcional**. Cada Apartamento exige exactamente un Ocupante **principal**, con Teléfono **obligatorio** — ese Teléfono sigue siendo una Persona real en todo el sentido de ADR-0003 (login, OTP, identidad). Los demás Ocupantes del mismo Apartamento pueden o no tener Teléfono; si lo tienen, también son su propia Persona. El principal es intercambiable entre los Ocupantes-con-Teléfono (promover/degradar).

## Considered Options

- **Volver nullable el Teléfono de Persona.** Rechazado — es exactamente la opción que ADR-0003 ya descartó, y por la misma razón: reintroduce "personas sin llave" en *todo* el sistema (auth, notificaciones, unicidad), no solo en el padrón de un Apartamento. Ocupante en cambio es un concepto nuevo y **acotado** — solo describe membresía de un Apartamento — que no toca ninguna otra parte del sistema, donde Persona sigue siempre anclada a un Teléfono sin excepción.

## Consequences

- ADR-0003 no se reabre: Persona sigue exigiendo Teléfono siempre, sin excepciones.
- Un Ocupante sin Teléfono no puede loguearse ni anunciar por sí mismo — solo existe para que un Paquete se le anuncie a su nombre de forma reconocible y persistente.
- Cada Apartamento necesita lógica para garantizar que siempre haya exactamente un Ocupante principal (con Teléfono) — nunca cero, nunca más de uno.
