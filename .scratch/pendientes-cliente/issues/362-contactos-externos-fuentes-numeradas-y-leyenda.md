# 362 — `/administracion/contactos-externos`: columna "Fuentes" numerada (`01 · 02 · 03`) + leyenda, solo desktop

**Pedido original (Jesús):** "en la columna de 'Fuentes', disenes una forma de
controlar las fuentes, esto para mejorar la forma en como se ven las fuentes
cuando sean muchas [...] actualmente [...] 'ACTUALIZACION, Paquetes, Whatsapp',
lo que necesito es que en esta columna permitas que se visualices de la
siguiente manera '01 · 02 · 03' y que en el (select name="fuente") aparezcan
asi las opciones (ACTUALIZACION - 03, Paquetes - 02 y Whatsapp - 04) [...]
sabiendo cual fue la primera, la segunda ... hasta la ultima. Dime si tiene
sentido [...] o como permitirias de forma facil saber a que fuente se hace
referencia, Ya que otra forma eficiente podria ser agregar arriba de la tabla
la equivalencia de cada uno de los nombres 'ACTUALIZACION = 03, Paquetes = 02,
Whatsapp = 01' o similar, que me recomiendas., recuerda que esto solo debe
funcionar para la vista desde el desktop [...] la vista para mobile es bastante
compacta y no es necesario ya que sera solo consulta."

**Status:** implementado; el cliente lo confirmó en local (2026-09-20) -- pendiente desplegar (requiere migración 0054) y verificar en test.papyrus.com.co

## Hechos hallados (2026-09-20, BD de dev)

- `ContactoExterno.fuentes` es un `ARRAY(String(40))` de nombres libres; no
  hay catálogo de fuentes ni número asociado.
- Dev tiene exactamente las 3 fuentes del ejemplo: ACTUALIZACION (1041
  contactos), Whatsapp (673), Paquetes (592). Todos los contactos tienen 2-3.
- El orden NO se puede deducir de los datos: `Whatsapp` y `ACTUALIZACION`
  comparten el mismo instante de primera aparición (2026-09-17
  12:43:43.9573); `Paquetes` 4 ms después.
- Los dos ejemplos del pedido no coinciden en Whatsapp: `04` en el select,
  `01` en la equivalencia.
- La columna hoy es `hidden sm:table-cell`; el select del import se puebla
  con `fuentes_existentes()` + "Otra (especificar)…".

## Propuesta (sujeta a las respuestas del cliente)

Números en la columna + leyenda sobre la tabla (ambas, solo desktop), tooltip
con el nombre en cada número, y `Nombre - NN` en el select. Los números se
asignan y guardan (catálogo pequeño, inmutables; una fuente nueva recibe el
siguiente).

## Decisiones confirmadas por el cliente (grilling, 2026-09-20)

1. **Numeración inicial:** 01 Whatsapp, 02 Paquetes, 03 ACTUALIZACION (el orden
   probablemente quedó así durante las pruebas de import; se toma tal cual).
2. **Autoincremental y permanente:** cada fuente NUEVA recibe el siguiente
   número (04, 05, ...), de modo que el número siempre dice cuál se agregó
   primero, cuál segundo, etc. El número no cambia nunca para una fuente ya
   existente.
3. **Presentación en desktop (desde 768px; debajo queda como hoy):** los números
   en la columna ("01 · 03", de menor a mayor, con el nombre completo como
   tooltip de cada número) **y** una leyenda sobre la tabla ("Fuentes: 01
   Whatsapp · 02 Paquetes · 03 ACTUALIZACION") con TODAS las fuentes
   registradas, no solo las de la página; si son muchas, se parte en varias
   líneas.
4. **Select del import:** opciones "Nombre - NN" ordenadas por número.
5. **"Otra (especificar)":** si el nombre ya existe con otra mayúscula o
   espacios (`whatsapp` vs `Whatsapp`), se reutiliza esa fuente en vez de crear
   una nueva.
6. **Sin datos, la numeración empieza en 01.**

## Implementación

- **Catálogo persistido** `fuentes_contactos_externos` (`numero` permanente +
  `nombre`, migración `0054`): el orden no se puede deducir de los datos, así
  que se guarda. `numero` no es autoincremental de la base sino máximo + 1
  bajo un bloqueo de tabla (`obtener_o_crear_fuente`): una carga revertida no
  deja huecos y dos imports simultáneos no chocan. Con la tabla vacía, la
  primera fuente es la 01.
- **Relleno de la migración:** respeta el orden confirmado (1 Whatsapp, 2
  Paquetes, 3 ACTUALIZACION, sin importar mayúsculas); cualquier otra fuente
  ya existente va después (por fecha de su primer contacto, luego nombre);
  las grafías que difieren solo en mayúsculas se juntan en una.
- **Import:** cada fuente usada por un contacto VÁLIDO se resuelve a su forma
  canónica (`whatsapp` reutiliza `Whatsapp`, y los contactos guardan la
  grafía del catálogo); un archivo cuyas filas se descartan todas no consume
  número. `contactos_externos.fuentes` sigue guardando nombres (sin FK).
- **Vista:** columna Fuentes con `01 · 02 · 03` (de menor a mayor, tooltip
  con el nombre) desde `md`; entre `sm` y `md` sigue el texto de antes;
  leyenda sobre la tabla (fuera del fragmento en vivo, con TODAS las fuentes);
  select del import "Nombre - NN" en orden de número.
- **Extra mínimo, no pedido:** el nombre de una fuente nueva se rechaza si
  pasa de 40 caracteres (antes fallaba en la base; el catálogo también lo
  limita a 40).
- Se retiró `fuentes_existentes` (y sus 2 tests): el catálogo la reemplaza.
- `tailwind.css` recompilado (ambas copias), `?v=` 96 -> 97.

## Verificación

- `tests/data_model/test_fuentes_contactos_externos.py` (25: servicio,
  import, numeración del listado y relleno/downgrade de la migración con los
  datos reales) y 12 tests nuevos en `tests/web/test_admin_contactos_externos.py`
  (54 en total en ese archivo); guard de paridad ORM-esquema y árbol de
  migraciones verdes.
- Migración aplicada a la BD de dev (`paquetex_dev`): catálogo 1 Whatsapp, 2
  Paquetes, 3 ACTUALIZACION. Medido en `localhost:8010` con Chromium contra
  los 1041 contactos: a 1280 y 768px leyenda visible + "01 · 02 · 03" + select
  "Nombre - NN"; a 700px sin leyenda y con nombres; a 375px sin leyenda ni
  columna. Sin overflow horizontal en ninguno.
- **Al desplegar:** correr `alembic upgrade head` (la migración es
  obligatoria: la vista lee el catálogo).
