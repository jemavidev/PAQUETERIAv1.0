# Spec — Doble escaneo de guía al entregar (Grupo 14, Ronda 2)

**Fuente:** `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 14.

## Qué cambia

El modal "Entregar" (`packages/list.html`) gana el mismo disparador de
escaneo ZXing que ya existe en "Recibir" — **solo cuando el paquete tiene
`guide_number` guardado** (si nunca se capturó guía al recibir, no hay
nada contra qué comparar y la sección de escaneo directamente no se
renderiza, en vez de mostrar un botón que no puede comparar nada).

Es una confirmación **100% client-side**: el valor esperado
(`guide_number`) ya viaja en el HTML como `data-guia-esperada` en el input
(el servidor ya lo conocía al renderizar la lista, no hace falta un
round-trip nuevo). El mismo callback de ZXing que ya rellena el input
ahora también compara el texto leído contra ese atributo y muestra
✅/⚠️ — **nunca** agrega un campo al `POST /paquetes/{id}/entregar`, que
sigue exactamente igual que antes (cero cambios de backend).

## Por qué

Instrucción explícita del usuario: reducir errores humanos al entregar,
sin agregar fricción — "por ahora... opcional y no bloqueante".

## Decisión de diseño (AgentX)

Se consideró hacer la comparación en el servidor (con un campo nuevo en el
POST), pero es innecesario: el dato a comparar (`guide_number`) ya está en
la página en el momento de abrir el modal, así que comparar en el
navegador da feedback INSTANTÁNEO (sin esperar un round-trip) y evita
tocar `paquete_lifecycle.deliver` o el endpoint HTTP por completo — el
riesgo de esta pieza queda acotado a una plantilla y un bloque de JS ya
existente, cero superficie de dominio nueva.

## Fuera de alcance

- No se persiste si el staff escaneó o no, ni si coincidió — es una ayuda
  visual momentánea, no un dato de auditoría.
