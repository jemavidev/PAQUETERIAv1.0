# 122 — "+ Nuevo residente" de Recibir permite mover (punto 1 de 3)

**Pedido original (cliente):**
Sobre el mensaje "Este teléfono ya es Ocupante activo -- debe darse de
baja antes de asociarse de nuevo.": "Vamos con la opcion 1" (de las dos
presentadas -- conectar el mecanismo de "mover" que ya tenía Corregir
destinatario, sin portar toda la vista previa en vivo).

**Status:** implementado

## Implementación

- `packages.py`, `receive_action`: nuevo campo `mover_de_otra_unidad:
  str = Form(None)`; `_resolver_desde_candidato` ahora se llama con
  `permitir_mover=True` (antes quedaba en `False` por defecto -- "mover"
  nunca se ofrecía dentro de Recibir). Mismo mecanismo exacto que ya usa
  Corregir destinatario, nada nuevo, solo conectado acá también.
- `_recibir_paquete.html`: checkbox "Si el contacto ya es Ocupante (no
  principal) de otra unidad, moverlo acá" en el sub-form "+ Nuevo
  residente" -- versión mínima (siempre visible, mismo texto que
  `/residentes`), sin la vista previa en vivo que sí tiene Corregir
  destinatario (eso es el punto 2, aparte).

## Verificación

- `tests/web/test_packages.py`: reemplaza el test que afirmaba el
  comportamiento viejo ("Recibir no ofrece mover") por uno que confirma
  que SÍ mueve marcando la casilla; test nuevo confirma que sin marcarla
  sigue bloqueando, pero con el mensaje enriquecido ("Mover acá"), no el
  genérico de antes.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
