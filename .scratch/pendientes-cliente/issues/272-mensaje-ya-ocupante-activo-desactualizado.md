# 272 — `mensaje_ya_ocupante_activo`: ya no cita "Mover acá" (desactualizado)

**Pedido original (cliente):** "Ajusta estos mensajes 'Ya es Ocupante
PRINCIPAL de TORRE 2 Apto 302 -- marcá "Mover acá" para reubicarlo
(se degrada automáticamente a otro Residente de esa unidad, o queda
vacía si está solo).' y similares para que estén acordes con lo que se
ha cambiado."

**Status:** implementado

## Verificación

Se encontraron y actualizaron 6 asserts en tests (`test_ocupante_
service.py` x2, `test_announce_new.py`, `test_customers_manage.py` x2,
`test_packages.py` x2) que verificaban literal "Mover acá". Suite
completa de los 4 archivos afectados: 537 passed. Verificado en vivo
(`POST /residentes/.../apartamento` sobre LAIS, que ya es Ocupante
Principal con otro Residente activo): el mensaje nuevo aparece
completo, sin mutar nada (bloqueado con 400 como corresponde).

## Diagnóstico

`ocupante_service.mensaje_ya_ocupante_activo` (ambas ramas, principal y
no-principal) cita literalmente `marcá "Mover acá"` -- ya
desactualizado antes de hoy (ningún checkbox real dice exactamente
eso), y esta función es COMPARTIDA por 4 flujos distintos, cada uno
con su propio checkbox de texto diferente:

- `customers_manage.py:785` (tab Dirección) -- ahora dice "Mudar
  residente de apartamento" (issue 269/271, además ahora es un toggle).
- `customers_manage.py:917` (tab Residentes, "Agregar Residente") --
  dice "Mudar residente acá" / "Mudar residente a TORRE X · Apto Y"
  (dinámico).
- `packages.py:1482` (/paquetes, "Corregir destinatario"/"+ Nuevo
  residente") -- mismo patrón dinámico "Mudar residente a X".
- `announce_new.py:446` (/announce) -- a revisar, mismo patrón
  esperado.

Arreglar solo para calzar con UNO de los 4 (ej. citar literal "Mudar
residente de apartamento") dejaría los otros 3 igual de desalineados
-- y volvería a pasar la próxima vez que cualquiera de los 4 textos
cambie por separado.

## Alcance

Se saca la cita literal de un texto de botón específico -- el mensaje
describe la ACCIÓN ("activa la opción de mudarlo") en vez de citar
palabra por palabra un label que varía según la vista. Root cause, no
symptom: esto no vuelve a desalinearse aunque cualquiera de los 4
checkboxes cambie su texto en el futuro.
