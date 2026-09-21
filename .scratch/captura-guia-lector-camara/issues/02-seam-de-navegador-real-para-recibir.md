# 02 — Prueba en navegador real para el modal Recibir (el seam de navegador)

**What to build:** hoy lo que solo existe en un navegador (el Enter que envía el formulario, el foco, el ciclo de vida de la cámara) se verifica a mano, y así pasó desapercibido que un Enter del lector recibe el paquete. Dar al proyecto **un** punto de prueba de navegador real: Chromium con Playwright contra la aplicación levantada sobre el mismo Postgres efímero que usa la suite web, con teclado real (eventos de confianza, no despachados a mano, porque el envío implícito con Enter solo ocurre con esos) y la BD como fuente de verdad de qué se envió de verdad. Corre aparte de la suite por defecto.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historia 63; sección Testing Decisions, seam 2).

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Existe un marcador `browser` registrado en la configuración de pytest, y el comando `pytest -m browser` corre estas pruebas. El `pytest` sin marcador **no** las recoge (la suite por defecto no cambia, ni en tiempo ni en dependencias).
- [ ] Si Playwright o Chromium no están instalados, las pruebas se saltan con un mensaje que dice qué falta, en vez de fallar.
- [ ] Un fixture levanta la aplicación sobre el Postgres efímero migrado de la suite web (mismo aislamiento entre pruebas: tablas truncadas al terminar cada una), en un puerto libre, y lo cierra sin dejar procesos ni puertos abiertos. **No** toca el servidor ni la base de desarrollo (`localhost:8010`).
- [ ] Hay ayudantes reutilizables para: iniciar sesión como Operador, dejar un Paquete `Anunciado`, abrir el modal Recibir de ese paquete y consultar el estado del Paquete en la BD.
- [ ] Prueba que ya pasa hoy: teclear en minúsculas en el campo Guía la deja en mayúsculas.
- [ ] Prueba que ya pasa hoy: llenar la Guía y pulsar "Recibir" deja el Paquete `Recibido` con esa guía guardada (verificado en la BD), demostrando que el seam distingue un envío real de uno que no ocurrió.
- [ ] Cómo correrlas queda escrito en el propio archivo de configuración del seam (comando, requisitos, qué hacer si falta Chromium).
