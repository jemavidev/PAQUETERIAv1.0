# 46 — `/mis-paquetes`: el código de acceso redirige a `/consultar?q=` en vez de copiar

**Pedido original (cliente):** "En la vista (/mis-paquetes) especificamente para el codigo de
acceso de los paquetes en la clase (codigo-texto), quiero que al hacer click en este en vez de
copiar ese codigo, el usuario sea redirigido a la vista (/consultar?q=<CODIGO DE ACCESO>) para ver
la informacion".

**Status:** implementado — verificado con tests (10/10 en `test_mis_paquetes.py`, suite completa
553/559, mismas 6 fallas preexistentes de `test_layout.py` sin relación). Falta desplegar y
verificar en vivo.

## Verificación previa

`GET /consultar?q=<access_code>` (`search.py`) ya busca exacto por `access_code` (o
`guide_number`) y devuelve el resultado completo en la misma respuesta — no requiere un segundo
clic ni pre-llena un formulario, el redirect solicitado muestra el detalle directo. Las clases
`copiar-codigo`/`codigo-texto` solo existen en `customer/paquetes.html`, en ningún otro template —
el cambio no afecta nada más.

## Implementación

Reemplazar el `<button class="copiar-codigo" data-copiar="...">` (copia al portapapeles vía JS) por
un `<a href="/consultar?q={{ p.access_code }}">` real — navegación nativa, sin JS, accesible por
teclado y con clic-derecho/clic-medio funcionando como cualquier enlace. Se retira el bloque JS de
copiar al portapapeles (huérfano tras el cambio, sin otro uso en el repo). El ícono de portapapeles
se reemplaza por uno de flecha/enlace, para no dejar una pista visual que ya no aplica (ajuste
menor no pedido explícitamente, pero el ícono viejo quedaría engañoso).

## Comments
