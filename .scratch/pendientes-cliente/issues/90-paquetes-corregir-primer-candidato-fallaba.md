# 90 — `/paquetes` "Corregir destinatario": el primer candidato de la lista no se podía elegir

**Origen:** encontrado durante una prueba de humo pedida por el cliente ("realiza pruebas de lo
que se tiene en la vista de /paquetes... botones, enlaces, modales") — no fue un pedido puntual,
sino un bug real descubierto al ejercitar la vista de punta a punta con Playwright.

**Status:** implementado

## Bug

Las tarjetas de un clic de [[84]] (cada candidato ES el submit, `name="candidato_idx"`) fallaban
específicamente al hacer clic en el **primer** candidato de la lista: el POST llegaba con
`candidato_idx` vacío o ausente, el servidor respondía 400 y el destinatario no se corregía. Elegir
cualquier otro candidato (2do en adelante) funcionaba bien — eso ocultó el bug en pruebas manuales
previas, que probablemente no probaron sistemáticamente el primero.

## Causa raíz (dos bugs encadenados)

1. La sub-sección "Nuevo residente" tenía un `<input type="hidden" name="candidato_idx"
   value="nuevo">` suelto, siempre presente en el DOM (el atributo `hidden` del contenedor solo
   afecta visibilidad, no participación en el submit) — competía por el mismo `name` con los
   botones de candidato.
2. La causa real: el script global "anti doble-envío" (compartido por todos los modales de la
   página, vive en `_recibir_paquete.html`) hacía
   `f.querySelector('button[type=submit]')` — siempre agarra el PRIMER submit del form sin
   importar cuál se clickeó. Para forms de un solo botón da igual, pero este form tiene varios
   submits con el mismo `name`. Al clickear la primera tarjeta, el script la deshabilitaba antes
   de que el navegador terminara de armar los datos del envío — un control deshabilitado no se
   manda, así que `candidato_idx` llegaba vacío aunque la tarjeta clickeada fuera la correcta.

## Fix

- `packages/_resultados.html`: se quita el `<input type="hidden">` suelto; `name="candidato_idx"
  value="nuevo"` pasa directo al botón "Guardar nuevo residente".
- `components/_recibir_paquete.html`: el listener usa `e.submitter` (identifica el botón real que
  disparó el submit) en vez de "el primer submit del form", y difiere el `.disabled = true` un
  tick (`setTimeout(fn, 0)`) para no deshabilitar el submitter mientras el navegador todavía está
  armando el envío de ESE mismo evento.

## Verificación

- Reproducido y confirmado el bug en vivo con Playwright (Chromium headless) antes del fix:
  `POST DATA: candidato_idx=` (vacío) al clickear la primera tarjeta.
- Tras el fix, mismo escenario exacto: `candidato_idx=0` sí llega, la fila se actualiza
  correctamente.
- Recorrido completo de `/paquetes` con Playwright (no solo HTTP, interacción real de navegador):
  listado + paginación, modal Ver (Historial/Destinatario/Residentes), Corregir destinatario
  (candidatos + "nuevo residente"), Asignar apartamento (3 y 4 dígitos), Recibir, Entregar,
  Cancelar, íconos de Acciones (wa.me/tel/mailto), búsqueda — todo verificado funcionando.
- `tests/web/test_packages.py`: 95/95. Suite completa: 922/922.
- Pendiente: deploy a test.papyrus.com.co.
