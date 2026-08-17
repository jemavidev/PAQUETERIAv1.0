# 100 — "+ Nuevo residente" se oculta sin apartamento propio + ajustes de texto

**Pedido original (cliente):**
1. "que tan logico seria el no poder modificar o Corregir destinatario si
   este no tiene asignado un apartamento confirmado o asignado?" —
   respondido: bloquear TODO "Corregir destinatario" sería demasiado
   amplio (Corregir por candidato no necesita apartamento y ya funciona
   bien sin uno); lo lógico es ocultar solo "+ Nuevo residente" cuando no
   hay apartamento propio, ya que ESA sub-acción sí lo necesita. El
   cliente confirmó: "yes".
2. "cambia este mensaje 'Es el Residente Principal de TORRE 7 · Apto 101
   -- para mudarlo, primero hay que promover a otro residente como
   principal ahí (lo degrada automáticamente). Ir a Clientes' por
   'Residente Principal de TORRE 7 · Apto 101 -- Degradarlo <link a vista
   /residentes en el tab de (data-tab="residentes")>'".
3. "cambia este texto 'Ya existe como ALEJANDRO RUEDA -- se usará ese
   nombre. Para registrar este número con otro nombre, primero hay que
   desvincularlo de donde esté.' por 'Ya existe como ALEJANDRO RUEDA.'"

**Status:** implementado

## Implementación

- `packages/_resultados.html`, "+ Nuevo residente": la opción ahora se
  arma en 3 estados según `p.direccion_corta` (tiene apartamento) y el
  estado del paquete:
  - **Con apartamento**: botón "Nuevo residente" de siempre.
  - **Sin apartamento, ANUNCIADO** (existe "Asignar apartamento", issue
    85-88): botón que hace swap directo a ese modal
    (`data-open="modal-asignar-apto-<id>"` + `data-close="modal-correct-
    <id>"`) -- "Sin apartamento asignado -- asignar apartamento primero".
  - **Sin apartamento, RECIBIDO/ENTREGADO** (no existe "Asignar
    apartamento" fuera de ANUNCIADO): solo texto explicativo, sin link a
    ningún lado.
- Aviso de Principal (issue 98) simplificado: "Residente Principal de
  `<Torre/Apto>` -- Degradarlo" (antes explicaba la razón completa en
  texto). El link "Degradarlo" ahora entra directo a la tab "Residentes"
  vía `?tab=residentes`, no a "Datos" -- nuevo query param en `GET
  /residentes/{id}` (`customers_manage.py`), validado contra las 4 tabs
  reales, cae al default `datos` si viene algo desconocido.
- Vista previa "Ya existe como X" (issue 97) simplificada a solo eso,
  sin la explicación de "se usará ese nombre... desvincularlo primero" --
  el enforcement real sigue en `agregar_ocupante` sin cambios, solo se
  acortó el texto.

## Verificación

- `tests/web/test_packages.py`: 3 tests nuevos para los 3 estados de "+
  Nuevo residente" según apartamento/estado.
- `tests/web/test_customers_manage.py`: 2 tests nuevos para `?tab=`
  (tab válida abre ahí, tab desconocida cae al default).
- Playwright contra el servidor local real: confirmado el texto exacto
  del aviso de Principal ("Residente Principal de TORRE 5 · Apto 801 --
  Degradarlo"), el `href` con `?tab=residentes`, que el panel
  "Residentes" carga con `display: block` al seguir ese link, y el texto
  acortado de "Ya existe como X.".
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
