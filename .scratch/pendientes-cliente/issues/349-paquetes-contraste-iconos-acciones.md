# 349 — `/paquetes`: contrastar los íconos de Acciones contra el nuevo fondo de fila

**Pedido original (cliente):**
"ahora contrasta los iconos de la columna accion" (a raíz de issue 348 --
el fondo de fila por Estado podía coincidir con el color de un ícono de
Acciones de la misma familia, ej. Teléfono azul sobre una fila RECIBIDO
también azul).

**Status:** implementado, pendiente confirmar visualmente

## Implementación

`packages/_acciones.html::_tam_accion` pasa a incluir `ring-2 ring-white`
además del tamaño (`clamp(...)`) -- ese único valor se inyecta como
parámetro `tam=` en cada llamado a `chip_icono()` (componente compartido,
`components/_badge.html`) Y se concatena en `_accion_off` (el apagado
armado a mano), así que un solo cambio propaga el aro blanco a los ~12
íconos de la columna (activos y apagados), sin tocar cada llamado uno por
uno.

El aro blanco despega el ícono del fondo de su fila sin importar si
coinciden en familia de color -- funciona igual sobre cualquiera de los 4
fondos de estado.

## Tests

`test_icono_telefono_en_acciones_cae_al_telefono_del_anunciante_sin_telefono_propio`
(test_packages.py) actualizado -- comparaba la clase exacta del ícono de
Teléfono, que ahora incluye `ring-2 ring-white`. Suite completa: 229
passed.

## Verificación

Pendiente confirmación visual del cliente.
