# 303 — `/anunciar`, `/announce` y `/administracion/personal`: Post/Redirect/Get

**Pedido original (cliente):** "en la pagina de /anunciar al momento que un
paquete ya esta anunciado y se recarga la pagina, este genera un nuevo
codigo un nuevo pquete es anunciado, esto no deberia pasar... que me
sugieres para controlar esto" + "y cualquier otro caso similar que se
presente" (pedido explícito de extender el barrido/fix a toda la app).

**Status:** implementado

## Diagnóstico

Causa raíz: el POST de éxito renderizaba la confirmación como respuesta
DIRECTA del propio POST, en vez de redirigir. El navegador asocia esa
página con el último POST -- recargar (F5) reenvía el mismo formulario, y
el servidor procesa la creación otra vez. Patrón clásico de "resubmit form
on refresh", sin relación con nada específico de `/anunciar`.

Barrido de los 59 endpoints POST de la app (`grep RedirectResponse` por
archivo + verificación puntual): confirmados exactamente 3 con este
patrón, el resto ya redirige correctamente:

- `/anunciar` (`announce.py`) -- crea un `Paquete`, sin dedup natural
  (cada anuncio es legítimamente nuevo) -- el más grave de los 3.
- `/announce` (`announce_new.py`, staff) -- mismo patrón, mismo riesgo.
- `/administracion/personal` (`admin.py`, alta de staff) -- mismo patrón,
  pero el email es único en BD -- un reload no crea un duplicado
  silencioso, solo un error confuso "ya existe". Corregido igual por
  consistencia, menor severidad.

## Fix — Post/Redirect/Get en los 3

- **`/anunciar`**: nueva ruta `GET /anunciar/confirmacion?codigo=<access_
  code>` que busca el Paquete y renderiza `announce/confirmacion.html`
  (mismo template de siempre). El POST, tras crear el paquete, redirige
  (303) ahí en vez de renderizar directo. Código inválido/inexistente ->
  redirige de vuelta a `/anunciar`.
- **`/announce`**: `GET /announce` ahora acepta `anunciado` (access_code) y
  `recibir` (bool) opcionales -- si vienen, reconstruye el mismo contexto
  que antes armaba el POST (`paquete_creado`, y si `recibir=1` también
  `mostrar_recibir`/`tipos`/`condiciones`/`candidatos`/etc. para reabrir el
  modal de Recibir, ticket 06). El POST redirige (303) a `/announce?
  anunciado=<code>[&recibir=1]` en vez de renderizar directo.
- **`/administracion/personal`**: `GET` ahora acepta `creado` (id de
  Usuario) opcional para el toast de éxito. El POST redirige (303) a
  `/administracion/personal?creado=<id>`.

Recargar cualquiera de las 3 páginas de confirmación ahora solo repite el
GET -- nunca reenvía el formulario, nunca duplica nada.

## Verificación

- `tests/web/test_announce.py`, `tests/web/test_announce_new.py`,
  `tests/web/test_admin_staff.py`, `tests/data_model/test_announce_paquete.py`:
  **148 passed**, sin cambios necesarios en las aserciones -- `TestClient`
  sigue los redirects por defecto, así que `r.text`/`r.status_code` tras un
  `client.post(...)` siguen viendo la página final de siempre.
