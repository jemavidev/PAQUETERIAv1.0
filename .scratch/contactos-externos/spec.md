Status: ready-for-agent
Feature: contactos-externos
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación, módulo 2 de 5) ·
`docs/contacts.csv` (export real de Google Contacts, 690 filas) · tabla `customers` de producción
v1.0 (`paquetex.papyrus.com.co`, RDS `paqueteria_v4`, 574 filas) · CONTEXT.md (glosario)

---

## Problem Statement

El cliente tiene información de clientes/residentes dispersa en dos lugares que nunca se cruzaron:
un archivo de exportación de Google Contacts (690 contactos personales/del negocio, sin ningún dato
de apartamento ni WhatsApp) y la tabla `customers` de la versión de producción v1.0 (574 clientes
reales, casi todos solo con nombre y teléfono). No hay forma hoy de saber, mirando ambas fuentes,
cuáles son la misma persona, ni de tener un solo lugar consultable con lo que se sabe de cada
contacto. El cliente además planea seguir sumando fuentes nuevas con el tiempo, así que la solución
no puede ser un cruce manual de una sola vez.

## Solution

Un script de importación fusiona ambas fuentes en un solo conjunto de **contactos externos** —
independiente de `Persona`/`Ocupante`, sin tocarlos ni crearlos — usando el teléfono como llave de
fusión: dos filas de cualquier fuente que compartan cualquier teléfono se convierten en un solo
contacto. Se incluye la unión completa de ambas fuentes (no solo las que coinciden entre sí), salvo
las filas sin ningún nombre o sin ningún teléfono válido, que se descartan por no tener con qué
identificarlas. Cuando el nombre difiere entre fuentes para el mismo contacto, gana el de Google
Contacts; si no está en esa fuente, se usa el de producción.

El resultado queda en una tabla nueva y completamente aparte, consultable desde una página simple
de búsqueda y paginación bajo `/administracion` — sin decidir todavía qué hacer con estos contactos
(promoverlos a `Persona`, descartar algunos, etc.), eso se resuelve en un momento posterior.

El diseño soporta más de un teléfono por contacto, y está pensado para que la próxima fuente que se
sume se cruce contra este mismo conjunto ya consolidado (sumando teléfonos o fuentes a un contacto
existente) en vez de rehacer la fusión desde cero cada vez.

## User Stories

1. Como desarrollador, quiero un script de importación que lea `docs/contacts.csv` y un export de la
   tabla `customers` de producción, para fusionarlos en un solo conjunto de contactos externos.
2. Como sistema, quiero fusionar en un solo contacto dos filas (de la misma fuente o de fuentes
   distintas) que compartan cualquier teléfono, para no duplicar a la misma persona.
3. Como sistema, quiero normalizar cada teléfono con `normalizar_telefono` (la misma regla que ya
   usa toda `Persona` en el sistema), para no reinventar ni divergir de la regla existente — un
   teléfono colombiano de 10 dígitos sin `+` se asume Colombia, igual que en el resto del sistema.
4. Como sistema, cuando el nombre difiere entre fuentes para el mismo contacto fusionado, quiero
   que gane el de Google Contacts, y el de producción solo cuando el contacto no aparezca en Google
   Contacts.
5. Como sistema, quiero descartar cualquier fila sin ningún nombre, o sin ningún teléfono que logre
   normalizarse, porque no hay con qué identificar ni fusionar ese contacto.
6. Como sistema, quiero incluir la unión completa de ambas fuentes (no solo los contactos que
   coinciden entre sí), para maximizar la cantidad de contactos capturados — aunque eso implique
   traer contactos personales del cliente que no son residentes.
7. Como desarrollador, quiero que un contacto pueda tener más de un teléfono asociado, para el caso
   de alguien que aparece con dos números (ej. una fila de Google Contacts con "Phone 1" y "Phone
   2").
8. Como desarrollador, quiero que esta tabla nueva sea completamente independiente de
   `Persona`/`Ocupante` — no se crea, modifica ni referencia ninguna fila de esas tablas — para que
   este módulo no tenga ningún efecto sobre el resto del sistema mientras se decide qué hacer con
   los contactos.
9. Como admin, quiero una página bajo `/administracion` con un buscador (por nombre o teléfono) y
   paginación simple, para poder consultar estos contactos desde el navegador.
10. Como admin, en esa página quiero ver solo los campos que el contacto realmente tenga (teléfono,
    nombre, usuario de WhatsApp), sin celdas vacías forzadas — hoy ninguna fuente trae WhatsApp, así
    que esa columna queda vacía para todos por ahora.
11. Como sistema, cuando se importe una fuente nueva en el futuro, quiero cruzarla contra los
    contactos ya consolidados (por teléfono) en vez de repetir la fusión completa desde cero,
    sumando teléfonos o marcas de fuente nuevas a un contacto ya existente cuando corresponda.
12. Como sistema, al enriquecer un contacto ya existente con una fuente nueva, NO quiero
    sobreescribir su nombre ya registrado — solo sumar teléfonos/fuentes nuevas — para no perder un
    nombre bueno por una fuente de peor calidad que llegue después.
13. Como desarrollador, si una fuente nueva conecta (por teléfono compartido) dos contactos que ya
    existían como filas separadas en la tabla, quiero que el importador lo señale en vez de
    fusionarlos automáticamente, porque fusionar dos contactos ya persistidos es una operación más
    delicada que crear uno nuevo, y merece revisión humana.
14. Como admin, quiero que cada contacto guarde de qué fuente(s) vino (aunque no se muestre en la
    búsqueda simple), para poder priorizar más adelante cuáles tiene sentido revisar primero.
15. Como sistema, al volver a correr el mismo import con las mismas dos fuentes, NO quiero crear
    contactos duplicados — el cruce por teléfono ya existente debe detectarlo como "ya importado".
16. Como cliente, quiero que este módulo NO decida por sí solo promover ningún contacto a residente
    real (`Persona`/`Ocupante`) — eso lo defino yo más adelante, en otro momento.

## Implementation Decisions

- **Nueva entidad `ContactoExterno`** (`src/app/domain/contacto_externo.py` — nombre elegido para no
  chocar con el módulo ya existente `contacto.py`, que clasifica teléfono-vs-WhatsApp de un valor
  tecleado, algo distinto): `id`, `nombre`, `whatsapp_usuario` (nullable, ninguna fuente actual lo
  provee), `fuentes` (columna array de texto — tags como `"produccion_v1"`/`"google_contacts"`,
  sumando entradas nuevas en cada import sin duplicar), `created_at`/`updated_at`.
- **Nueva entidad `ContactoExternoTelefono`**: `id`, `contacto_externo_id` (FK), `telefono` (forma
  canónica de `normalizar_telefono`, único a nivel de tabla — un mismo teléfono nunca puede
  pertenecer a dos `ContactoExterno` distintos, esa unicidad es justamente la llave de fusión).
- **Nueva función pura `fusionar_fuentes(filas) -> list[ContactoExternoConsolidado]`** (en
  `contacto_externo_service.py`), donde cada fila de entrada es `(nombre, telefonos_normalizados,
  fuente)`. Agrupa filas por componentes conexas de teléfono compartido (dos filas con cualquier
  teléfono en común terminan en el mismo grupo, sin importar la fuente); por cada grupo resuelve
  nombre (gana Google Contacts; empate entre varias filas de la misma fuente lo resuelve el orden
  de aparición) y la unión de fuentes/teléfonos. No toca la base de datos — reusable tanto para la
  primera importación como para futuras.
- **Nueva función de persistencia `importar_contactos_externos(session, filas_nuevas) ->
  ResumenImportacion`**: aplica `fusionar_fuentes` sobre el lote nuevo, y por cada grupo resultante
  busca si alguno de sus teléfonos ya existe en `ContactoExternoTelefono`:
  - Ninguno existe → crea un `ContactoExterno` nuevo con sus teléfonos y fuente(s).
  - Coincide con exactamente un `ContactoExterno` existente → lo enriquece: agrega los teléfonos y
    fuente(s) que le falten, **nunca** sobreescribe `nombre` ya presente.
  - Coincide con más de un `ContactoExterno` existente y distinto entre sí (el lote nuevo conecta
    dos contactos que hoy son filas separadas) → NO se fusionan automáticamente; se reporta en el
    resumen de la importación para revisión manual (fuera de alcance decidir la fusión de contactos
    ya persistidos en esta versión).
  - Reejecutar el import con exactamente las mismas fuentes es un no-op (todo ya coincide con
    teléfonos existentes).
- **Script** `scripts/importar_contactos_externos.py`: recibe como argumentos la ruta a
  `docs/contacts.csv` y la ruta a un export ya generado de la tabla `customers` de producción
  (`phone`, `first_name`, `last_name` — el export en sí, vía `ssh paquetex` + `psql`, es un paso
  manual documentado en el script, no algo que el script haga por su cuenta). Parsea ambos a la
  forma común `(nombre, telefonos, fuente)` — descartando en el parseo cualquier teléfono que
  `normalizar_telefono` rechace (se ignora ese teléfono puntual, no toda la fila) y cualquier fila
  sin nombre ni teléfono válido — y llama a `importar_contactos_externos`.
- **Ruta nueva de admin** (`admin.py`, mismo patrón que otras vistas de solo lectura):
  `/administracion/contactos-externos` (GET), exclusiva de `require_admin` — buscador simple
  (nombre o teléfono, `ILIKE`) + paginación, mostrando solo los campos presentes por fila.

## Testing Decisions

Buen test acá = observar comportamiento externo (qué devuelve la función pura dado un input, qué
queda en las filas de `ContactoExterno`/`ContactoExternoTelefono` después, qué HTML se renderiza) —
nunca aserciones sobre el código interno.

- **Seam 1 — `fusionar_fuentes` (función pura)**: prior art de estilo,
  `tests/data_model/test_apartamento_seed.py` (importación/siembra de datos desde una fuente
  externa). Cubrir: dos filas de fuentes distintas con el mismo teléfono se fusionan en un contacto;
  gana el nombre de Google Contacts sobre producción cuando difieren; una fila sin nombre se
  descarta; una fila sin ningún teléfono válido se descarta; un contacto con dos teléfonos (Phone 1
  + Phone 2) queda con ambos asociados; un teléfono sin `+` de 10 dígitos colombiano se normaliza
  igual que en el resto del sistema; un teléfono no reconocible se ignora sin descartar el resto de
  la fila si tiene otro teléfono válido.
- **Seam 2 — `importar_contactos_externos` (persistencia incremental)**: nuevo archivo
  `tests/data_model/test_contacto_externo_service.py`. Cubrir: primera importación crea los
  `ContactoExterno` esperados; reimportar el mismo lote no duplica nada; un lote nuevo con un
  teléfono que ya existe enriquece ese contacto (nuevo teléfono/fuente) sin tocar su nombre ya
  guardado; un lote que conecta dos `ContactoExterno` ya existentes y distintos no los fusiona, y
  queda reportado en el resumen devuelto.
- **Seam 3 — `/administracion/contactos-externos`**: nuevo archivo
  `tests/web/test_admin_contactos_externos.py`, prior art directo de estilo:
  `tests/web/test_admin_conjunto.py`. Cubrir: acceso exclusivo de admin (un operador recibe 403);
  buscar por nombre encuentra el contacto esperado; buscar por teléfono (en cualquier formato de
  entrada) también lo encuentra; paginación no repite ni omite filas entre páginas; un contacto sin
  WhatsApp no muestra esa columna forzada a vacío de forma rara (se omite limpiamente).

## Out of Scope

- Cualquier cambio a `Persona`/`Ocupante` — este módulo no crea, promueve ni vincula ningún
  `ContactoExterno` a un residente real. Esa decisión queda para un módulo/momento posterior.
- Fusión automática de dos `ContactoExterno` ya persistidos y distintos, aunque una fuente nueva los
  conecte por teléfono compartido — se reporta para revisión manual, no se resuelve solo.
- Captura de usuario de WhatsApp — ninguna de las dos fuentes actuales lo provee; la columna queda
  lista para cuando una fuente futura sí lo traiga.
- Cualquier automatización del export de la tabla `customers` de producción (SSH, credenciales,
  scheduling) — es un paso manual documentado, no una integración automática.
- Filtros avanzados o exportar el listado de `/administracion/contactos-externos` a archivo — solo
  buscador + paginación en esta versión.

## Further Notes

- De los 690 contactos de `docs/contacts.csv`, 460 no coinciden por teléfono con ningún cliente de
  producción — son en su mayoría contactos personales/del negocio del cliente (34 tienen
  "Organization Name", sugiriendo proveedores/empresas). Se incluyen igual, por decisión explícita
  del cliente de maximizar la cantidad de contactos capturados sobre la precisión.
- El cliente planea seguir sumando fuentes nuevas con el tiempo (mencionó explícitamente una
  tercera fuente futura) — el diseño de importación incremental (Seam 2) es directamente para ese
  caso, no una especulación sin pedido.
