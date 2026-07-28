# Spec — Quitar "documento", bloquear Conjunto (Grupo 12, Ronda 2)

**Fuente:** `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 12.

## Qué cambia

1. `documento`/`tipo_documento` dejan de aceptarse en **todos** los
   formularios: `/mis-datos` (cliente) y `/residentes/{id}` (staff). Las
   columnas de `Persona` **no se eliminan** (dato histórico neutral, evita
   una migración destructiva innecesaria) — solo dejan de escribirse.
   `update_datos_personales` pierde esos dos parámetros por completo.
2. El cliente ya **no** puede fijar ni cambiar el Conjunto en `/mis-datos`:
   - El servidor **nunca lee** un campo `conjunto` del formulario — el valor
     se deriva siempre del `apartamento_actual` ya asignado (o `None` si no
     tiene ninguno).
   - Si no tiene Conjunto asignado, el formulario no muestra Torre/Apartamento
     en absoluto (no tiene sentido declarar una unidad sin saber en cuál
     Conjunto) — se muestra un mensaje pidiendo que el staff lo asigne primero.
   - Si ya tiene Conjunto (asignado antes por staff, vía `/announce`), el
     campo se muestra de solo lectura (`disabled`, sin `name`) y el cliente
     puede actualizar libremente Torre y Apartamento dentro de ese Conjunto.

## Por qué

Instrucción explícita del usuario. Antes de este cambio, un cliente nuevo
podía autoservirse un Conjunto/Torre/Apartamento completos desde cero en
`/mis-datos` — ahora esa asignación inicial pasa a ser exclusivamente tarea
del staff (`/announce`, Grupo 6 de la Ronda 1); el cliente solo ajusta su
posición (Torre/Apto) dentro de la unidad que el staff ya le asignó.

## Fuera de alcance

- `/residentes/{id}` (staff) no gana ni pierde control sobre Conjunto — ya
  no lo editaba antes (esa pantalla nunca tuvo campos de apartamento), y
  sigue sin tenerlos. Nada cambia ahí salvo quitar documento.
- No se toca la matriz de canales de notificación (Grupo 13, aparte).
