# 100 — Modal "Ver" de /paquetes: Torre/Apto enlaza a la tab "Residentes del apartamento"

**Pedido original (cliente):**
"tengo varios cambios basicos con los que necesito que me ayudes, para
iniciar en la vista /paquetes, especificamente el modal de clientes, al
lado de la opcion de notificaciones para un residente (telefono/whatsapp)
esta la torre y el apartamento, lo que necesito es que esta torre y
apartamento le pueda hacer click y me lleve a la vista de /residentes en
el tab de "Residentes del apartamento""

**Status:** implementado

## Implementación

- `packages/_resultados.html`, modal "Ver" (`modal-ver-<id>`): el texto
  Torre/Apto (`p.direccion_corta`) que hoy vive junto al teléfono/WhatsApp
  pasa a ser un link cuando `p.persona_destino_id` está resuelto (mismo
  guard que ya usa el título del modal para el nombre, conversación
  2026-08-21) -- `/residentes/<persona_destino_id>?tab=residentes`,
  reusando el querystring `?tab=` ya soportado por la ruta
  (`customers_manage.py`, conversación 2026-08-17) para abrir directo en
  "Residentes del apartamento".
- Sin persona resuelta (`persona_destino_id` es `None`), Torre/Apto se
  queda como texto plano -- no hay ficha a la que enlazar.
- Sin atributo `title` en el link (a diferencia de otros íconos del modal):
  el texto visible ya es autodescriptivo, y el primer intento con `title`
  duplicaba "Torre X · Apt Y" en el HTML y rompía un test existente
  (`test_modal_ver_telefono_y_direccion_comparten_linea_con_separador`)
  que asume esa cadena aparece una sola vez por modal.

## Verificación

- `tests/web/test_packages.py`: dos tests nuevos --
  `test_modal_ver_torre_apto_enlaza_a_tab_residentes` (persona resuelta:
  el link existe y apunta a `?tab=residentes`) y
  `test_modal_ver_torre_apto_sin_persona_resuelta_queda_como_texto`
  (sin persona resuelta: sigue como texto plano, sin link). Suite completa
  de `test_packages.py`: 178 tests, todos pasan.
- Verificado contra el ambiente local (`paquetex_dev_up.sh`,
  localhost:8010) con curl autenticado: el link se renderiza en
  `/paquetes` para paquetes con apartamento y persona resueltos, y al
  seguirlo (`/residentes/<id>?tab=residentes`) la página responde con
  `activar('residentes')` -- abre directo en "Residentes del apartamento".
- Pendiente: deploy a test.papyrus.com.co.
