Status: implementado, verificado en vivo en local (`localhost:8010`, migración aplicada); pendiente desplegar y correr `alembic upgrade head` en `test.papyrus.com.co`/producción
Feature: contactos-externos-import-export
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación) · módulo previo
`.scratch/contactos-externos` (esquema `ContactoExterno`/`ContactoExternoTelefono`, motor de
fusión original) · CONTEXT.md (glosario)

---

## Problem Statement

Un admin no técnico no tiene forma de cargar contactos externos nuevos por su cuenta. Hoy la única
vía de importación es un script de línea de comandos que solo el desarrollador puede correr (SSH +
`DATABASE_URL`), pensado para una carga histórica única (Google Contacts + producción v1.0) — no
está pensado para que alguien sin ese acceso lo use de forma recurrente. Tampoco existe ninguna
forma de sacar el listado de `/administracion/contactos-externos` a un archivo.

Además, el motor de fusión actual solo reconoce el teléfono como llave de identidad. Dos filas que
sean evidentemente la misma persona pero compartan únicamente un usuario de WhatsApp (sin ningún
teléfono en común) hoy terminan como dos contactos separados, perdiendo información en vez de
consolidarla — justo lo contrario del objetivo del módulo.

## Solution

La vista `/administracion/contactos-externos` suma un botón para importar (sube un CSV con
plantilla fija: Nombre, Teléfonos, WhatsApp) y uno para exportar (descarga el listado completo en
ese mismo formato). El import se aplica directo, sin vista previa, reutilizando y extendiendo el
motor de fusión ya existente: el usuario de WhatsApp pasa a contar como una segunda llave de
identidad además del teléfono, de modo que dos filas que compartan CUALQUIERA de las dos se
fusionan en el mismo contacto.

Al enriquecer un contacto ya existente, el NOMBRE del archivo más reciente gana sobre el ya
guardado (único campo de un solo valor que se sobreescribe), mientras que teléfonos y usuarios de
WhatsApp se acumulan por igual entre sí y nunca se eliminan solo porque un archivo puntual no los
traiga — son listas que se arman combinando fuentes con el tiempo, no un valor único que compite
consigo mismo, y ahora ambas son llave de fusión, así que perder un valor viejo arriesga que una
fila futura con ese mismo dato ya no se reconozca. El resumen del import (creados, enriquecidos,
conflictos y filas descartadas) se muestra al admin apenas termina de procesar.

## User Stories

1. Como admin, quiero subir un archivo CSV con contactos externos desde la propia vista web, para
   no depender de que un desarrollador corra el script por SSH cada vez que tengo datos nuevos.
2. Como admin, quiero que el import use una plantilla de columnas FIJA, para saber exactamente qué
   formato preparar sin adivinar.
3. Como admin, quiero poder descargar esa plantilla vacía desde la propia vista, para no tener que
   adivinar los nombres exactos de columna.
4. Como sistema, si el archivo subido no calza exactamente con las columnas de la plantilla (de más
   o de menos), quiero rechazarlo con un mensaje claro y NO escribir nada en la base, para que un
   error de formato nunca produzca datos corruptos o parciales.
5. Como admin, quiero declarar la fuente de cada archivo UNA SOLA VEZ en el formulario de subida (no
   columna por fila del CSV), para no tener que repetir el mismo texto en cada línea.
6. Como admin, quiero elegir la fuente entre las que ya se usaron antes (con opción de escribir una
   nueva), para no terminar con tags casi-duplicados por errores de tipeo entre imports.
7. Como sistema, quiero que la columna `Teléfonos` de la plantilla acepte varios números separados
   por `;`, sin tope de cantidad, para reflejar que un contacto puede tener más de un teléfono.
8. Como sistema, quiero que la columna `WhatsApp` de la plantilla acepte varios usuarios separados
   por `;`, sin tope de cantidad, con la misma regla que `Teléfonos`.
9. Como sistema, quiero que el import se aplique directo al subir el archivo (sin un paso de vista
   previa a confirmar), porque reimportar el mismo archivo ya es una operación segura (no
   duplica nada) y el resumen posterior ya informa si algo salió distinto de lo esperado.
10. Como sistema, quiero que una fila sea válida si tiene nombre y AL MENOS UN identificador (un
    teléfono normalizable, o un WhatsApp válido) — ya no exijo teléfono obligatoriamente, porque
    WhatsApp ahora es una llave de identidad igual de válida.
11. Como sistema, quiero descartar (sin crear ni tocar nada) cualquier fila sin nombre, o sin ningún
    identificador válido, igual que hoy — pero además quiero reportar cuántas y por qué, en vez de
    descartarlas en silencio.
12. Como sistema, quiero que el usuario de WhatsApp sea una SEGUNDA llave de fusión, igual que el
    teléfono: dos filas (de la misma fuente o de fuentes distintas) que compartan CUALQUIER
    teléfono O CUALQUIER usuario de WhatsApp terminan en el mismo contacto.
13. Como sistema, quiero normalizar cada usuario de WhatsApp con la misma regla canónica que ya usa
    `Persona` (sin espacios, sin `@` inicial, insensible a mayúsculas/minúsculas), para no
    reinventar ni divergir de la regla ya validada en producción.
14. Como desarrollador, quiero que un contacto pueda tener más de un usuario de WhatsApp asociado
    (igual que ya puede tener más de un teléfono), para no perder ninguno de los que se acumulen
    con el tiempo desde distintas fuentes.
15. Como sistema, al enriquecer un contacto ya existente con una fila nueva, quiero que el NOMBRE se
    actualice al valor de la fila más reciente, reemplazando el guardado — a diferencia del import
    histórico original, acá se trata de imports recurrentes hechos por el propio admin sobre sus
    propias fuentes, así que un nombre corregido en el archivo debe reflejarse. Es el ÚNICO campo
    de un solo valor que se sobreescribe así — ver la historia 17.
16. Como sistema, al enriquecer un contacto ya existente, quiero que los TELÉFONOS y los USUARIOS DE
    WHATSAPP se acumulen (unión) exactamente igual entre sí, sin eliminar nunca ninguno solo porque
    una fila puntual no lo traiga — ambos son ahora llaves de fusión (historia 12), así que
    necesitan conservar TODO valor visto alguna vez para poder seguir reconociendo filas futuras;
    perder uno por sobrescritura arriesga que una fila futura con ese valor viejo ya no se
    reconozca y cree un contacto duplicado en vez de fusionar.
17. Como sistema, quiero que la regla de "sobreescribir con el valor más reciente" (historia 15)
    aplique SOLO al nombre, nunca a teléfonos o WhatsApp — porque nombre es un dato de un solo
    valor que compite consigo mismo, mientras que teléfonos/WhatsApp son listas que se arman
    combinando fuentes con el tiempo (historia 16).
18. Como sistema, quiero seguir sumando las fuentes nuevas a la lista de fuentes del contacto sin
    quitar las anteriores, sin cambios respecto al comportamiento actual.
19. Como sistema, si una fila nueva conecta (por teléfono compartido, por WhatsApp compartido, o
    cruzado — teléfono con un contacto y WhatsApp con otro) dos `ContactoExterno` que ya existen
    como filas separadas y distintas, NO quiero fusionarlos automáticamente — quiero reportarlo
    para revisión manual, igual que ya pasa hoy con el conflicto de teléfono.
20. Como admin, quiero ver un resumen apenas termina el import: cuántos contactos se crearon,
    cuántos se enriquecieron, cuántos conflictos quedaron pendientes de revisión manual, y cuántas
    filas se descartaron (y por qué), para saber si el archivo se procesó como esperaba.
21. Como admin, quiero un botón para exportar el listado COMPLETO de contactos externos a un archivo
    CSV, sin importar si tengo un término de búsqueda activo en ese momento, para no exportar por
    error un subconjunto sin darme cuenta.
22. Como admin, quiero que el archivo exportado tenga EXACTAMENTE las mismas columnas que la
    plantilla de import (`Nombre`, `Teléfonos`, `WhatsApp`), para poder editarlo y volverlo a subir
    tal cual si necesito corregir datos en lote.
23. Como sistema, quiero que reimportar exactamente el mismo archivo sea un no-op real (no cree
    contactos duplicados ni cambie nada), igual que ya garantiza el import histórico.
24. Como cliente, quiero que este módulo siga sin decidir por sí solo promover ningún
    `ContactoExterno` a residente real (`Persona`/`Ocupante`) — sin cambios respecto al alcance ya
    definido en el módulo original.
25. Como admin, quiero que el import y el export sigan exclusivos de mi rol (mismo control de acceso
    que ya tiene toda la vista `/administracion/contactos-externos`), sin un permiso nuevo separado.

## Implementation Decisions

- **Normalización de WhatsApp promovida a módulo compartido**: hoy `_normalizar_whatsapp_usuario` /
  `_validar_whatsapp_usuario` (con la regla de Meta: 3-35 caracteres, letras latinas, números,
  puntos o guion bajo) viven privadas dentro del servicio de `Persona`, usadas solo ahí. Se extraen
  a un módulo nuevo, mismo patrón que ya existe para teléfono (que vive separado en su propio
  módulo con una única función pública `normalizar_telefono`), y el servicio de `Persona` pasa a
  importar desde ahí en vez de mantener su propia copia privada — sin cambio de comportamiento para
  `Persona`. El motor de fusión de contactos externos importa la misma función en vez de duplicar
  la regla.
- **Nueva entidad `ContactoExternoWhatsapp`**: mismo patrón que `ContactoExternoTelefono` (FK al
  contacto, `whatsapp_usuario` en su forma canónica, único a nivel de tabla — esa unicidad es la
  llave de fusión, igual que ya pasa con teléfono). El campo `whatsapp_usuario` que hoy vive
  directo en `ContactoExterno` se retira de ahí (pasa a ser un dato derivado de sus filas
  relacionadas, igual que ya pasa con teléfono) — requiere una migración de esquema nueva.
- **`fusionar_fuentes` (función pura) generalizada a dos tipos de llave**: el algoritmo de
  unión-búsqueda ya usado para teléfono se extiende para agrupar también por WhatsApp normalizado
  — dos filas que compartan CUALQUIER teléfono O CUALQUIER WhatsApp terminan en el mismo grupo. La
  regla de fila válida pasa de "nombre + al menos un teléfono normalizable" a "nombre + al menos un
  identificador (teléfono O whatsapp) normalizable/válido". El resultado consolidado por grupo
  ahora trae también el conjunto de WhatsApps del grupo, no solo teléfonos.
- **`importar_contactos_externos` cruza contra ambas tablas**: al buscar si una fila nueva ya
  corresponde a un contacto existente, se consulta tanto por teléfono como por WhatsApp. Ningún
  identificador coincide → crea. Coincide con exactamente un contacto existente (por cualquiera de
  las dos llaves) → enriquece: el NOMBRE se actualiza al valor de la fila más reciente (único campo
  de un solo valor que se sobreescribe); los TELÉFONOS y los WHATSAPP se acumulan por igual entre
  sí, sumando los que traiga la fila nueva sin eliminar nunca los que el contacto ya tenía.
  Coincide con más de un contacto existente y distinto (por cualquier combinación
  de las dos llaves, incluyendo el caso cruzado) → se reporta como conflicto, mismo mecanismo ya
  existente, sin fusión automática. El resumen (`ResumenImportacion`) suma un campo nuevo con las
  filas descartadas y el motivo de cada una.
- **Parseo de la plantilla en un solo lugar** (corrección tras revisión -- la redacción original de
  este punto prometía algo que no tiene sentido construir): el script CLI (`scripts/importar_
  contactos_externos.py`) parsea DOS formatos de fuente que no son la plantilla nueva -- el export
  de Google Contacts (columnas "First Name"/"Phone 1 - Value"/etc.) y el export de `customers` de
  producción v1.0 (columnas `first_name`/`phone`/etc.) -- cada uno con su propio parser ya existente
  y sin relación con las columnas `Nombre`/`Teléfonos`/`WhatsApp` de la plantilla nueva. Forzar una
  función "compartida" entre formatos que no comparten columnas sería una abstracción artificial
  (fingir una forma común que no existe), así que el script queda intacto -- sigue produciendo el
  mismo resultado de siempre para sus dos fuentes de un solo uso. Lo que sí queda en un solo lugar
  es el parseo de la plantilla EN SÍ (`fila_plantilla_a_fila_fuente`, un único punto reusado por
  cualquier caller futuro del formato de plantilla, aunque hoy solo lo llame el endpoint web) — y la
  regla de "qué fila es válida" (nombre + al menos un identificador) vive en un solo lugar real
  (`fusionar_fuentes`/`filas_descartadas`, vía el helper compartido `_identificadores_normalizados`),
  independiente de qué parser produjo la fila.
- **Endpoint de import nuevo** (mismo patrón de acceso que el resto de `/administracion`, exclusivo
  de rol admin): recibe el archivo subido y el valor de fuente del formulario (elegido de las
  fuentes ya usadas, o un valor nuevo escrito a mano), valida que las columnas del archivo calcen
  exacto con la plantilla antes de procesar nada (si no calzan, rechaza con un mensaje claro sin
  tocar la base), parsea con la función compartida y llama al motor de fusión. Re-renderiza la
  misma vista con el resumen del resultado en el contexto — mismo patrón ya usado por la
  confirmación de migración de año (misma plantilla, flags de contexto extra tras el POST).
- **Endpoint de descarga de plantilla**: entrega un CSV vacío con únicamente el encabezado esperado
  (`Nombre`, `Teléfonos`, `WhatsApp`), mismo control de acceso que el resto de la vista.
- **Endpoint de export nuevo**: trae el listado completo de contactos externos (sin paginar, sin
  respetar ningún término de búsqueda), arma un CSV en memoria con las mismas columnas exactas de
  la plantilla de import, y lo devuelve como descarga de archivo.
- **Fuente del formulario de import**: el `<select>` se puebla con los valores de fuente ya
  presentes en la tabla (sin duplicados), más una opción para escribir un valor nuevo a mano.
- **UI en la propia plantilla de la vista** (no en el componente de búsqueda genérico compartido con
  otras vistas de admin, que no tiene lugar reservado para acciones adicionales y no debe acoplarse
  a esta vista puntual): botones de Importar / Exportar / Descargar plantilla, un formulario de
  subida con el selector de fuente, y el resumen post-import mostrado con el componente de aviso
  breve ya existente para el titular (creados/enriquecidos) más un bloque propio, persistente (no
  autodesaparece), para el detalle de conflictos y filas descartadas cuando los haya.

## Testing Decisions

Buen test acá = observar comportamiento externo (qué devuelve la función pura dado un input, qué
queda en las filas de las tablas después, qué HTML/CSV se genera) — nunca aserciones sobre el
código interno. Mismo criterio ya documentado en el módulo original.

- **Normalización de WhatsApp (módulo nuevo, función pura)**: cubrir los mismos casos que ya prueba
  hoy la normalización de `Persona` (con/sin `@` inicial, mayúsculas/minúsculas equivalentes,
  formato inválido) — movidos/reutilizados desde ahí, sin reinventar casos.
- **`fusionar_fuentes` generalizado (función pura)**: extiende los tests de fusión ya existentes.
  Cubrir: dos filas que comparten SOLO WhatsApp (sin teléfono en común) se fusionan en un contacto;
  una fila con WhatsApp válido pero sin ningún teléfono ya NO se descarta; una fila sin nombre, sin
  teléfono Y sin WhatsApp sigue descartándose; un contacto con dos WhatsApps distintos (de dos
  filas del mismo grupo) queda con ambos asociados; un WhatsApp con `@` inicial o mayúsculas
  distintas normaliza igual que uno sin esas diferencias.
- **`importar_contactos_externos` extendido (persistencia incremental)**: extiende los tests ya
  existentes de este seam. Cubrir: un lote nuevo enriquece un contacto existente por coincidencia
  de WhatsApp aunque el teléfono sea distinto o no venga; el nombre del contacto se actualiza al de
  la fila más reciente; un lote nuevo con un WhatsApp que el contacto no tenía se lo suma sin
  tocar los que ya tenía; un teléfono o WhatsApp que el
  contacto ya tenía nunca desaparece aunque un lote nuevo no lo traiga; un lote que conecta, por
  cualquier combinación de las dos llaves, dos contactos ya existentes y distintos, se reporta como
  conflicto y no se fusiona; una fila descartada (sin nombre o sin ningún identificador) queda
  contada en el resumen con su motivo.
- **Endpoint de import (nuevo, o extiende el archivo de test ya existente de esta vista)**: acceso
  exclusivo admin (un operador recibe 403); subir un CSV válido según la plantilla crea/enriquece
  según corresponda y el resumen mostrado refleja los números reales; un archivo con columnas que
  no calzan con la plantilla se rechaza con un mensaje claro y no crea ni modifica ningún contacto;
  reimportar exactamente el mismo archivo no duplica nada.
- **Endpoint de export (mismo archivo de test)**: exporta TODOS los contactos existentes sin
  importar si hay un término de búsqueda activo; las columnas del archivo exportado calzan
  exactamente con las que espera el import (mismo orden, mismos nombres); el archivo exportado se
  puede volver a subir como import sin ninguna edición y el resultado es un no-op (todos ya
  existen).
- **Endpoint de descarga de plantilla**: acceso exclusivo admin; el archivo trae únicamente el
  encabezado esperado, sin filas.
- **Script CLI**: queda intacto (ver corrección en Implementation Decisions) -- no hay comportamiento
  nuevo que probar ahí. Sí se verificó que sigue importando correctamente sin errores tras los
  cambios de esquema/servicio de los que depende (`ContactoExterno`/`importar_contactos_externos`).

## Out of Scope

- Vista previa antes de confirmar el import — se aplica directo (decisión explícita del cliente
  durante `/grilling`: reimportar ya es seguro, y el resumen posterior ya informa lo necesario).
- Mapeo flexible de columnas de un archivo con encabezados distintos — la plantilla es fija y
  estricta; cualquier archivo que no calce exacto se rechaza sin intentar adivinar columnas.
- Resolución automática de los conflictos reportados (dos contactos ya existentes que una fila
  nueva conecta) — se listan para revisión manual, igual que ya estaba fuera de alcance en el
  módulo original; no se agrega ninguna acción de fusión manual desde la UI en esta versión.
- Cualquier acción de borrado explícito de un teléfono o WhatsApp puntual desde la UI — el import
  nunca elimina datos, y esta versión tampoco agrega una vía manual de hacerlo.
- Exportar un subconjunto filtrado (respetando el buscador activo de la vista) — el export siempre
  trae el listado completo.
- Soporte de formatos distintos a CSV (Excel u otros) — no se agrega ninguna dependencia nueva al
  proyecto para esto.
- Automatización del export de la tabla `customers` de producción v1.0 — sigue siendo un paso
  manual fuera de esta feature, sin cambios respecto al módulo original.
- Cualquier cambio a `Persona`/`Ocupante` — este módulo sigue sin crear, promover ni vincular ningún
  `ContactoExterno` a un residente real.

## Further Notes

- Este spec extiende el módulo original `.scratch/contactos-externos` (import CLI de una sola vez +
  vista de consulta) con capacidad de self-service recurrente, y de paso corrige un hueco real del
  motor de fusión: hasta ahora el teléfono era la única llave de identidad, y el usuario de
  WhatsApp era un dato suelto sin ninguna lógica de deduplicación — nunca fue un problema porque
  ninguna fuente lo traía, pero la plantilla de import nueva sí lo trae, así que el hueco se vuelve
  real con esta misma feature.
- La normalización de WhatsApp no es nueva — ya existe, validada en producción, para `Persona`
  (issues 67/162 de `.scratch/pendientes-cliente`). Este spec la reutiliza en vez de inventar una
  regla paralela, promoviéndola a un módulo compartido siguiendo el mismo patrón que `telefono.py`
  ya estableció para el teléfono.
- El spec original ya anticipaba que el cliente seguiría sumando fuentes nuevas con el tiempo — este
  trabajo es la continuación directa de esa previsión, ahora sin requerir que el desarrollador
  intervenga en cada carga.
