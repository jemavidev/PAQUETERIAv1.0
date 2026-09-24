# 398 — "Staff Papyrus" en vez de "Operador v1 (sin identificar)"

**Pedido original (Jesús):** "Remplaza esto "Operador v1 (sin identificar)" por esto "Staff Papyrus"".

**Status:** implementado (pendiente de desplegar y de la siguiente pasada del cron)

## Contexto

El importador espejo v1 → v2 (`.scratch/importador-v1-espejo`) crea un Usuario técnico inactivo para
`operator_1`, el usuario genérico que firmó TODAS las entregas y cancelaciones de la v1. Su nombre se ve en
la línea de tiempo (`/consultar`, `/mis-paquetes`, detalle en `/paquetes`), en `/administracion/personal` y
en estadísticas de cobro ("Operador con más entregas"). Hacia el residente, el glosario dice "el personal
de Papyrus" (issue 394), así que "Staff Papyrus" encaja mejor que el nombre técnico.

## Qué se hace

- El nombre del Usuario técnico pasa a "Staff Papyrus" (`OPERADOR_V1_NOMBRE`).
- El Usuario técnico que ya existe en test se renombra solo en la siguiente pasada del importador (el
  importador mantiene el nombre de ese usuario técnico; no toca a los usuarios reales enlazados).
