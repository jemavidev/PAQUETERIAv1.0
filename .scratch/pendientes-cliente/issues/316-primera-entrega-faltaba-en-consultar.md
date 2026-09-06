# 316 — Bandera "primera entrega" faltaba en el modal Entregar de /consultar

**Pedido original (cliente):** "veo que si intento entregar un paquete desde
'modal-entregar-consultar' no me aparece el mensaje indicando que es un usuario nuevo, analiza y
dime se hace falta en algun otro lugar."

**Status:** implementado, desplegado a test.papyrus.com.co (2026-09-05, commit `bcac30d`) --
pendiente que el cliente lo confirme visualmente (extensión de Chrome no disponible en esta
sesión).

## Diagnóstico

El modal "Entregar" (issue 314) vive DUPLICADO en 2 templates -- `packages/_resultados.html`
(`/paquetes`) y `search/form.html` (`/consultar`, `modal-entregar-consultar`), ambos postean al
mismo endpoint `/paquetes/{id}/entregar`. La bandera de issue 314 solo se agregó en la primera --
`search.py` nunca corre `packages.py::_listar()` (resuelve un solo `Paquete` directo por query,
sin el batch de enriquecimiento), así que `paquete.primera_entrega_a_telefono` nunca existía ahí.
Búsqueda exhaustiva confirmó que estos 2 son los ÚNICOS lugares que postean a `/paquetes/{id}/
entregar` en todo el código -- no hay un tercer lugar faltante.

## Implementación

Nueva `es_primera_entrega_a_telefono(session, recipient_phone)` en `paquete_service.py` --
versión de UN SOLO teléfono (vs. el batch de `_listar` en packages.py) para callers que resuelven
un paquete a la vez. `search.py` la llama, gateada igual que el propio modal (sesión de staff +
RECIBIDO), y expone `paquete.primera_entrega_a_telefono` como atributo transitorio (mismo nombre
que usa `packages.py`).

El markup de la bandera se extrajo a un macro compartido (`bandera_primera_entrega()` en
`components/_badge.html`) para que los 2 templates nunca vuelvan a divergir -- este mismo drift
(agregarlo en un lugar, olvidar el duplicado) es justo lo que reportó el cliente.

## Bug encontrado y corregido en el camino

`es_primera_entrega_a_telefono` tenía la lógica INVERTIDA en el primer intento -- devolvía
`True` cuando SÍ había una entrega previa (el nombre de la función decía lo contrario). Se
detectó verificando en vivo contra datos reales del servidor (`F4UP`, sin entregas previas, NO
mostraba la bandera; `JTV8`, con 3 entregas previas, SÍ la mostraba -- exactamente al revés).
Corregido negando el resultado del `.exists()`. 3 tests nuevos en `test_search.py` bloquean esta
regresión a futuro. 427 tests en verde
(`test_packages.py`/`test_layout.py`/`test_customers_manage.py`/`test_search.py`).
