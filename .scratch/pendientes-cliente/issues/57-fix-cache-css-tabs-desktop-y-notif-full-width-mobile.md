# 57 — Fix: tabs/notificaciones "dañados" en desktop (cache de CSS) + distribuir Notificaciones a ancho completo en mobile

**Pedido original (cliente):** "Te pedi encarecidamente que dividieras lo
que es la vista del mobil con la vista del desktop, no se porque no
tomaste esta instruccion con relacion a los TABS, ahora las vistas del
desktop se dañaron [...] Veo que no solo eso de los TABS se afecto, tambien
dalaste las 'notificaciones' en el desktop. ANLIZA A FONDO LO QUE HICISTE Y
COMO LO HICISTE PARA QUE PROPONGAS CORREGIRLO. Por ultimo en tu
modificacion al tab de 'notificaciones' [...] seria posible que para la
vista de mobiles distribuyas el contenido en el ancho total del
dispositivo, esto ya que se encuentra todo el contenido ajustado y
apiñado a la izquierda."

**Status:** implementado

## Análisis — causa raíz real

**No fue un error de lógica CSS.** Se re-derivó a mano, regla por regla, el
comportamiento esperado de cada clase `lg:*` agregada en [[54]]/[[55]]/[[56]]
contra el HTML real, y la cascada mobile-first (`grid` → `lg:flex`,
`bg-slate-50 border` → `lg:bg-transparent lg:border-0`, `flex flex-wrap` →
`lg:grid lg:grid-cols-[...]`, etc.) es correcta.

**Primer intento de corrección (INCOMPLETO, corregido más abajo):** se
asumió que el problema era un `?v=` de cache-busting sin subir en
`base.html`, y se subió `?v=29` → `?v=30`. Desplegado, verificado con
`curl` directo (sin cache de navegador de por medio) contra
`test.papyrus.com.co/static/css/tailwind.css?v=30` -- **las reglas nuevas
seguían faltando**, con el mismo `etag`/`last-modified` (2026-08-05) que
`?v=29`. Eso descartó cache de navegador: ni Caddy ni el propio `curl` con
un query-string jamás usado antes cambiaban el resultado.

**Causa raíz real, encontrada entrando por SSH al servidor:** el
`Dockerfile` del repo de deploy (`jemavidev/PaqueteX`) es DISTINTO del
`Dockerfile` de este monorepo (`CODE/Dockerfile`) -- el de deploy NO
instala Node/npm ni corre `npm run build:css` en ningún paso; solo copia
`src/` tal cual viene del checkout de git:

```
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY alembic.ini .
COPY alembic/ alembic/
COPY src/ src/
```

Es decir: `src/app/web/static/css/tailwind.css` es un archivo COMMITEADO
en git que el deploy nunca recompila -- exactamente lo que el comentario
de `base.html` ya advertía ("hay que RECOMPILAR este archivo"), pero se
interpretó mal: no bastaba con subir el `?v=`, había que recompilar el
CSS EN LOCAL y comitear el archivo resultante, cosa que en los últimos 4
deploys (54, 55, 56, y el primer intento de 57) se hizo exactamente al
revés -- se recompiló en local para verificar las clases, y después se
revirtió (`git checkout --`) esa recompilación por creer, incorrectamente,
que el Dockerfile de deploy la iba a regenerar sola en cada build (así
trabaja el `CODE/Dockerfile` de este monorepo, pero NO el del repo de
deploy). Confirmado entrando al contenedor corriendo en
`test.papyrus.com.co`: `tailwind.css` con fecha 5 de agosto, sin ninguna
de las clases nuevas -- congelado desde el último commit (issue 48) que sí
comiteó el CSS recompilado.

Esto también explica por qué mobile SÍ se veía bien en 54/55/56: las
clases mobile-first (`grid`, `bg-slate-50`, `py-3`, `text-base`,
`flex-wrap`, etc.) ya existían en el CSS viejo por casualidad -- son
utilidades comunes usadas en otras partes de la app. Las que faltaban eran
específicamente las `lg:*` que revierten esos estilos en desktop
(`lg:bg-transparent`, `lg:border-0`, la columna de grid con valor
arbitrario), mucho menos probable que ya existieran de casualidad en
cualquier build viejo.

## Corrección

- CSS recompilado en local (`npm run build:css`, las dos rutas --
  `src/static/css/` y `src/app/web/static/css/`, ambas quedan idénticas
  como espera `tailwind.config.js`) y esta vez SÍ comiteado.
- `base.html`: `?v=30` → `?v=31` (insurance extra, ya que `?v=30` alcanzó a
  servir contenido viejo un rato antes de detectar el problema real).
- Regla a seguir de ahora en más: toda vez que se agregue/quite una clase
  de Tailwind en cualquier plantilla, **recompilar Tailwind en local Y
  comitear el `tailwind.css` resultante** (no solo subir el `?v=` --
  el deploy NO lo recompila solo) en el mismo commit.
- Pendiente de decidir con el cliente (fuera de alcance de este fix
  puntual): agregar el paso de build de Tailwind al `Dockerfile` del repo
  de deploy, para que esto deje de depender de que alguien se acuerde de
  recompilar y comitear a mano cada vez.

## Adicional — Notificaciones en mobile, distribuir a ancho completo

El layout de tarjetas de [[54]] usaba `flex flex-wrap` sin `justify-content`
para los 4 canales de cada evento -- por defecto quedaban pegados a la
izquierda (`justify-start`), con el resto del ancho vacío a la derecha.
Se agregó `justify-between` (solo mobile, `lg:justify-normal` lo neutraliza
en desktop) -- como el `<p>` del evento fuerza su propia línea completa
(`w-full`), `justify-between` solo afecta a la línea de los 4 canales, que
ahora quedan repartidos borde a borde en vez de amontonados.

## Verificación

- Recompilación local de Tailwind: confirmado que las 6+ reglas `lg:*` en
  cuestión (`lg:bg-transparent`, `lg:border-0`, `lg:flex`, `lg:grid`,
  `lg:justify-normal`, `justify-between`) se generan correctamente.
- Suite completa (`tests/data_model tests/web`): 633/633, sin regresiones.
- Pendiente: confirmar en `test.papyrus.com.co` que desktop volvió
  exactamente a como estaba antes de [[54]], que mobile sigue viéndose
  como en [[56]], y que los canales de Notificaciones ahora se reparten en
  todo el ancho en mobile. El cliente debería hacer un refresh forzado
  (Ctrl+Shift+R / Cmd+Shift+R) la primera vez, ya que su navegador de
  escritorio puede seguir teniendo cacheado el CSS viejo hasta que la URL
  con `?v=30` se lo fuerce.
