# 102 — La advertencia de nombre se apaga tras corregir, sin importar a quién

**Pedido original (cliente):**
"Estoy tratando de corregir para este codigo de acceso '9EXE', quiero
cambiar a 'PRINCIPAL TEXTO NUEVO' por cualquiera, pero sigue apareciendo
el mismo icono para cambiar, no se porque esta pasando, veo que el nombre
de la persona despues si se cambia, pero el icono sigue apareciendo, dime
que puede ser?" -- diagnosticado: `_nombre_no_coincide` comparaba el
`recipient_name` contra el nombre REGISTRADO del Anunciante, no contra "¿ya
se corrigió?" -- corregir a alguien que no fuera exactamente el Anunciante
dejaba la advertencia prendida aunque la corrección sí se hubiera
aplicado (confirmado en la base de datos para 9EXE: `corrected_at` sí
quedó registrado). Presentadas 2 opciones (A: se apaga con cualquier
corrección explícita; B: se queda prendida mientras el destinatario no
coincida con quien llamó, aunque se haya corregido). El cliente eligió
"Opción A: en caso que necesite re-corregir, usaré el ícono 'Modificar'."

**Status:** implementado

## Implementación

- `packages.py`, `_nombre_no_coincide`: ahora retorna `False` de una vez
  si `paquete.corrected_at is not None` -- "Corregir destinatario" (por
  cualquiera de sus 3 entradas: advertencia, "Modificar" de Acciones, o el
  botón del modal "Ver") apaga la advertencia para siempre, sin importar
  si el nombre elegido coincide con el Anunciante. "Modificar" en Acciones
  sigue disponible sin condición para volver a corregir después.
- Caso borde documentado en el propio código (no reportado, no se
  resuelve acá): `corrected_at` es compartido con `corregir_apartamento`
  (ADR-0001, "el esquema no distingue cuál de las dos correcciones
  ocurrió") -- un paquete sin Apartamento Y con nombre desajustado que se
  corrige SOLO de Apartamento también apaga la advertencia de nombre como
  efecto colateral.

## Verificación

- `tests/web/test_packages.py`: nuevo test corrige a una persona DISTINTA
  del Anunciante (no la que coincidiría bajo la regla vieja) y confirma
  que la advertencia igual se apaga -- 119 tests, todos pasan.
- Confirmado directamente sobre el paquete real que reportó el cliente
  (código de acceso `9EXE`, `recipient_name` ya en "NICOLAS RUEDA",
  Anunciante registrado como "ALEJANDRO RUEDA"): el ícono de advertencia
  ya no aparece.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
