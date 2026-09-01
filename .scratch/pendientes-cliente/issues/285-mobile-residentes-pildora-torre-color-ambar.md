# 285 — Seguimiento a [[282]]: píldora Torre/Apto pasa de índigo a ámbar

**Pedido original (cliente):** "como puedes hacer para diferenciar los
colores de las pildoras de la vista /residentes especificamente en la
version mobil, especificamente entre 'Principal y Torre/Apartamento',
los 2 tienen tonos azules"

**Status:** implementado

## Alcance

`customers_manage/_resultados.html`, mobile only: la píldora de
Torre/Apto ([[277]]/[[281]]) pasó de gris a `indigo` en [[282]] a
pedido del cliente -- pero índigo y azul (color de "Principal") son
colores vecinos, se confunden en un badge de 11px. Se cambia a `amber`
(`bg-amber-50 text-amber-700 border-amber-200`) -- cálido, claramente
distinto tanto del azul de "Principal" como del verde de "Auto", sin
volver al gris neutro que el cliente ya había pedido cambiar en [[282]].

## Verificación

Verificado en vivo (dev local, iframe same-origin, mismo método de
[[277]]-[[283]]) -- confirmado visualmente (zoom, fila con las 3
píldoras juntas: JESUS VILLALOBOS) que Auto (verde), Principal (azul)
y Torre/Apto (ámbar) se distinguen a simple vista. 0px de overflow.
Suite completa (`pytest tests/web/test_customers_manage.py`): 154
passed, sin regresiones. Desktop sin cambios (la píldora sigue sin
aparecer ahí).
