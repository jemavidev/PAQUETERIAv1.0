Status: ready-for-agent
Feature: importador-v1-espejo
Branch: PaqueteXv.2
Fuente de verdad: sesión de `grilling` del 2026-09-23 (14 preguntas, enfocada al importador) ·
CONTEXT.md (glosario) · ADR-0001 (snapshot inmutable), ADR-0003/0007 (identidad), ADR-0004
(rebuild aislado) · antecedente: `.scratch/migracion-datos-legacy/estructura-migracion.md`
(import único ejecutado el 2026-08-20, datos luego borrados) · `.scratch/migracion-por-anio`
(interacción con "Migrar año")

---

## Problem Statement

La producción v1 (`paquetex.papyrus.com.co`, servidor `ssh paquetex`, base Postgres administrada
`paqueteria_v4`) sigue operando a diario: ~300 paquetes al mes, 609 residentes, 5 personas del
staff activas. La v2 (`test.papyrus.com.co`) ya está construida, pero sus datos son de prueba:
desde la v2 no se puede consultar ningún paquete, residente, foto ni cobro real.

El cliente quiere que la v2 muestre los datos reales de la v1 mientras la v1 sigue siendo el
sistema donde se trabaja, y poder dejar de usar la v1 el día que decida, sin perder historia y
sin un corte traumático. Una importación única (como la del 2026-08-20) no alcanza: la v1 cambia
cada día y ese import quedó viejo en horas.

## Solution

Un **importador espejo** que se corre repetidamente y copia en un solo sentido, de la v1 a la v2:

- Lee la base de la v1 con un rol de Postgres **de solo lectura** y vuelca su contenido al modelo
  de la v2: Persona, Paquete con su snapshot, Cobro, PaqueteFoto y Usuario. Las preferencias de
  notificación no se importan (decisión 2026-09-24).
- **La v1 manda.** Mientras dure la transición, el staff opera solo en la v1. Cada pasada vuelve
  a escribir lo importado con lo que diga la v1, crea lo nuevo y borra lo que desapareció. Lo que
  se creó directamente en la v2 no se toca.
- Corre en el contenedor de la v2 con cron cada 15 minutos y también se puede correr a mano.
  Cada pasada deja un reporte.
- Tiene un modo **simular**, que calcula todo sin escribir, y un modo **final**, que se usa en el
  corte: falla ante cualquier choque sin resolver.
- El día del corte: la v1 pasa a solo lectura, se corre la pasada final, se quita el cron y se
  apunta el dominio. Después de eso el importador no vuelve a correr.

Antes de la primera pasada se limpia el staging de todo lo que sea de residentes y paquetes. Se
conservan la configuración, el censo de apartamentos y los contactos externos.

## User Stories

### Operación del espejo

1. Como admin, quiero que la v2 muestre los paquetes, residentes, fotos y cobros reales de la v1,
   para consultar la operación real desde la versión nueva antes de apagar la vieja.
2. Como admin, quiero que el espejo se actualice solo cada 15 minutos, para que la v2 esté casi al
   día sin tener que acordarme de correrlo.
3. Como admin, quiero poder correr el importador a mano cuando quiera, para forzar una
   actualización inmediata, por ejemplo antes de revisar algo puntual o el día del corte.
4. Como admin, quiero que correr el importador dos veces seguidas sobre la misma v1 no cambie nada
   la segunda vez, para confiar en que repetirlo nunca duplica ni corrompe.
5. Como admin, quiero que cada pasada deje un reporte con lo creado, actualizado, borrado,
   saltado, los choques y los errores por entidad, más las fotos copiadas, para saber qué pasó sin
   revisar la base a mano.
6. Como admin, quiero un modo simular que haga todo el cálculo y el reporte sin escribir nada en la
   v2 ni en S3, para validar la primera ejecución contra la base real antes de activar el cron.
7. Como admin, quiero que lo que la v1 cambia se refleje en la v2 aunque la v1 no haya actualizado
   su `updated_at`, para no depender de una fecha que la v1 no siempre mantiene. Cada pasada lee
   todo y compara, algo viable con el volumen actual.
8. Como admin, quiero que si alguien toca un registro importado en la v2 (entregarlo, renombrar a
   una Persona), la siguiente pasada lo devuelva a lo que diga la v1, porque durante la transición
   la v1 es la única fuente de verdad.
9. Como admin, quiero que lo creado directamente en la v2 durante la transición (paquetes o
   Personas nuevas) nunca se modifique ni se borre por el importador, para poder probar en la v2
   sin que el espejo me pise.
10. Como admin, quiero que la v1 se lea con un rol de Postgres de solo lectura dedicado, para que
    un error del importador nunca pueda escribir en producción.
11. Como sistema, quiero que el importador nunca dispare avisos (SMS, email) al crear o actualizar
    paquetes, para que importar no le escriba a ningún residente.

### Borrados

12. Como admin, quiero que lo que desaparece de la v1 (anuncios vencidos que borra su limpieza de
    15 días, clientes o paquetes borrados por un admin) se borre también en la v2, junto con sus
    fotos y su cobro, para que la v2 sea un espejo exacto.
13. Como sistema, quiero borrar solo registros que vinieron de la v1, nunca los creados en la v2.
14. Como sistema, quiero que una Persona que desaparece de la v1 pero tiene paquetes creados en la
    v2 no se borre, sino que solo pierda su vínculo con la v1, para no dejar huérfanos datos nativos.
15. Como admin, quiero que si en una pasada desaparece más del 5 % de lo importado de alguna
    entidad, el importador aborte sin borrar nada y lo reporte como alerta, para que una lectura
    vacía o fallida de la v1 nunca vacíe la v2.

### Residentes (Persona)

16. Como admin, quiero que cada `customers` de la v1 sea una Persona de la v2 con el mismo teléfono
    (ya viene en formato `+57…`), el nombre de `full_name` y el email si lo tiene.
17. Como sistema, quiero que los clientes de la v1 sin paquetes también se importen como Persona,
    para tener el directorio completo.
18. Como sistema, quiero que si ya existe en la v2 una Persona nativa con el mismo teléfono que un
    cliente de la v1, el importador la adopte (la enlace a su origen en la v1 y le escriba los datos
    de la v1) en lugar de fallar o duplicarla.
19. Como sistema, quiero que las Personas importadas lleguen sin apartamento actual, porque la v1
    nunca guardó torre ni apartamento. Se completa con el tiempo mediante los flujos que ya existen.
20. Como sistema, quiero que las Personas importadas lleguen sin términos aceptados, para que cada
    residente los acepte en su primer ingreso a la v2.
21. ~~Preferencias de la v1 → filas Canal × Evento~~ **Reemplazada (decisión 2026-09-24, opción C):**
    las preferencias de notificación de la v1 no se importan. Toda Persona importada queda con el
    default de la v2 (SMS solo en Anunciado), y lo que el residente configure en la v2 el importador
    nunca lo pisa. Motivo: los 7 clientes con preferencias en la v1 tenían SMS prendido en
    Recibido/Entregado, que en la v2 solo puede activar un ADMIN.

### Paquetes

22. Como residente, quiero consultar mi paquete en la v2 con el mismo código de 4 caracteres que me
    llegó por SMS desde la v1, así que el `tracking_number` de la v1 pasa a ser el `access_code`.
23. Como sistema, quiero que el `access_code` de un paquete importado se fije solo al crearlo y que
    el importador nunca lo vuelva a escribir, para no deshacer el sufijo de año de "Migrar año".
24. Como sistema, quiero que si un código de la v1 choca con el de un paquete creado en la v2, se
    le cambie el código al de la v2 (es de prueba) y se anote en el reporte, para que el paquete de
    la v1 conserve el código que el residente conoce. En modo final, ese choque hace fallar la pasada.
25. Como sistema, quiero que el cliente de la v1 sea el Anunciante del paquete y que `display_name`
    sea el `recipient_name`, o el nombre del cliente si `display_name` está vacío.
26. Como sistema, quiero que el snapshot de un paquete importado quede sin conjunto, torre ni
    apartamento, y que nunca se reescriba aunque la Persona declare su apartamento después
    (ADR-0001).
27. Como sistema, quiero que estado, tipo y condición se copien tal cual, porque la v1 ya usa el
    vocabulario de la v2 (`RECIBIDO`/`ENTREGADO`/`CANCELADO`, `NORMAL`/`EXTRA_DIMENSIONADO`,
    `BUENO`/`REGULAR`/`ABIERTO`).
28. Como sistema, quiero que los anuncios activos de la v1 que todavía no son paquete se importen
    como paquetes `ANUNCIADO` con su código, para que el staff los pueda recibir en la v2 el día del
    corte.
29. Como sistema, quiero que las fechas (anuncio, recepción, entrega, cancelación) se lleven a UTC,
    porque la v1 mezcla columnas con y sin zona horaria.
30. Como sistema, quiero que el motivo de cancelación de la v1 (`"otro"`, tomado de
    `package_history`) se asigne al motivo equivalente del catálogo de la v2.
31. Como admin, quiero ver en el detalle y la línea de tiempo de un paquete importado quién lo
    recibió, entregó o canceló, igual que en uno nativo.

### Autoría (staff)

32. Como sistema, quiero que la autoría salga de `package_history.changed_by`, lo único que la v1
    registra, porque `created_by` y `updated_by` están vacíos.
33. Como sistema, quiero enlazar `rafael`, `maye`, `jveyes` y `jesus` a sus usuarios ya existentes
    en la v2 (`jesus` y `jveyes` son la misma persona: JESUS VILLALOBOS).
34. Como sistema, quiero que `MARIANELLA`, que no existe en la v2, se cree como usuario inactivo
    sin acceso, para que el historial conserve su nombre.
35. Como sistema, quiero que `operator_1`, que firmó todas las entregas y cancelaciones de la v1,
    se represente con un usuario técnico inactivo "Operador v1 (sin identificar)", usado en entregas,
    cancelaciones y cobros.
36. Como sistema, quiero que los usuarios importados o técnicos nunca puedan iniciar sesión y que
    no se copien contraseñas, porque los usuarios reales ya existen en la v2.

### Cobros

37. Como admin, quiero que cada paquete `ENTREGADO` de la v1 tenga un Cobro en la v2 con el monto
    que cobró la v1 (1.500 o 2.000), sin bodegaje, fechado en `delivered_at` y a nombre del Operador
    v1, para que las estadísticas de cobro muestren el historial desde noviembre de 2025.
38. Como sistema, quiero que los cobros importados sean copia fiel de la v1 y no se recalculen con
    las reglas de la v2 (exención de primera entrega, bloques de bodegaje).

### Fotos

39. Como admin, quiero ver en la v2 las fotos de recepción de los paquetes de la v1, que son la
    evidencia de la entrega.
40. Como sistema, quiero copiar cada foto de la v1 (bucket privado `elclub-paqueteria`) al bucket
    configurado de la v2, en `public-read` y con un nombre de destino que siempre sale igual para
    la misma foto, de modo que repetir la copia nunca duplique.
41. Como sistema, quiero que el bucket de destino sea el que tenga configurado la v2 (hoy el de
    staging, en el corte el de producción) sin cambiar código.
42. Como sistema, quiero que una foto que falla al copiarse quede en el reporte y se reintente en
    la siguiente pasada, sin frenar el resto.

### Limpieza previa y corte

43. Como admin, antes de la primera pasada quiero borrar del staging todo lo de residentes y
    paquetes: paquetes, fotos, cobros, movimientos de saldo, Personas, Ocupantes, OTP, preferencias
    de persona, registros de SMS y reseteos de contraseña de clientes, si existen. Se conservan
    usuarios, tarifas, motivos, plantillas, proveedores, la configuración del conjunto y de la
    empresa, los apartamentos (804) y los contactos externos (1.041). Antes se saca un dump.
44. Como admin, el día del corte quiero correr una pasada final que falle ante cualquier choque o
    error sin resolver, para saber que el espejo quedó completo antes de apuntar el dominio.
45. Como admin, quiero que después del corte el importador quede desactivado de forma explícita (se
    quita el cron), porque "la v1 gana siempre" pisaría operaciones reales hechas en la v2.

### Pantallas sin apartamento

46. Como staff, quiero que todas las pantallas de la v2 (listados y búsqueda de paquetes, detalle y
    línea de tiempo, recibir, entregar, `/consultar`, `/mis-datos`, gestión de clientes, estadísticas
    de cobro, exportaciones) funcionen con Personas sin apartamento actual y paquetes con snapshot
    sin apartamento, porque todos los datos importados llegan así.

## Implementation Decisions

### Módulos

- **Servicio de dominio de sincronización (módulo profundo, el único que se prueba a fondo).**
  Interfaz: `sincronizar_desde_v1(session, instantanea_v1, copiador_fotos, modo) → ReporteSincronizacion`.
  - `instantanea_v1` son filas planas en memoria (dataclasses): usuarios, clientes, paquetes,
    historial de paquetes, anuncios activos sin procesar y archivos de foto.
  - `modo` puede ser `normal`, `simular` o `final`.
  - `copiador_fotos` es un puerto con una operación "copiar el objeto de origen al destino
    determinístico y devolver la URL pública". Tiene una implementación S3 real y una falsa para
    pruebas.
  - Mismo patrón que `importar_contactos_externos(session, filas)`. Vive en el paquete de dominio
    aislado y no importa nada del mundo viejo (ADR-0004).
- **Lector de la v1.** Adaptador delgado: una conexión SQL de solo lectura a la base de la v1 que
  arma la `instantanea_v1`. Normaliza las fechas a UTC al leer. No contiene reglas de negocio.
- **Copiador S3.** Copia de `elclub-paqueteria`, con credenciales de lectura de la v1, al bucket
  de fotos configurado en la v2. Usa `public-read` y el prefijo propio de la v2. El destino se
  deriva de la key de la v1 (convención ya usada el 2026-08-20:
  `<prefijo-fotos-v2>legacy_<nombre-original>`). Si el destino ya existe, no se vuelve a copiar.
- **Script de línea de comandos.** Envoltura delgada: flags `--simular` y `--final`, lee
  credenciales del entorno, abre las dos sesiones, llama al servicio e imprime y guarda el reporte.
  Termina con un código distinto de cero si hay alerta del 5 % o, en modo final, cualquier choque o
  error.
- **Script de limpieza previa del staging.** Operación única y separada del importador, con la
  lista exacta de tablas que se borran y se conservan (historia 43).

### Esquema de la v2 (migración Alembic)

- Columna nullable `origen_v1_id` con índice único parcial (donde no es nula) en: `personas`
  (uuid del cliente de la v1), `paquetes` (id del paquete de la v1, o `anuncio:<id>` para los
  anuncios sin paquete), `paquete_fotos` (id de `file_uploads`) y `usuarios` (username de la v1,
  y el valor fijo `operator_1` para el usuario técnico).
- Los cobros no llevan la columna: se identifican por su paquete importado.
- `origen_v1_id` es permanente: se queda después del corte para rastreo. **No se muestra en
  ninguna pantalla.**
- Si un anuncio de la v1 pasa a ser paquete, el paquete `ANUNCIADO` importado se actualiza al
  `origen_v1_id` del paquete (se reconoce por el `package_id` del anuncio) y no se borra ni se
  vuelve a crear, para que no cambien su código ni su identidad.

### Reglas del servicio

- **Orden:** usuarios → Personas → paquetes (incluye anuncios) → cobros → fotos →
  borrados.
- **La v1 gana:** en cada registro con `origen_v1_id`, los campos importados se sobrescriben con
  lo que diga la v1. Excepción: `access_code`, que solo se fija al crear el paquete.
- **Choque de `access_code`:** si el código de la v1 ya lo tiene un paquete sin `origen_v1_id`,
  a ese paquete de la v2 se le asigna un código nuevo con el generador existente y se reporta. En
  modo final, la pasada falla.
- **Adopción de Persona:** si llega un teléfono de la v1 sin Persona con ese `origen_v1_id` pero
  hay una Persona nativa con ese teléfono, se le escribe `origen_v1_id` y se le aplican los datos
  de la v1.
- **Mapeo de autoría:** tabla fija dentro del servicio: `rafael`, `maye`, `jveyes` y `jesus` se
  resuelven por email a usuarios existentes (`jesus` → el mismo usuario que `jveyes`).
  `MARIANELLA` → usuario inactivo creado. `operator_1` → usuario técnico inactivo "Operador v1
  (sin identificar)". Un `changed_by` desconocido se reporta y queda sin autor (`NULL`), salvo en
  `cobrado_por`, que siempre usa el usuario técnico porque es obligatorio.
  - De `package_history`: el primer `RECIBIDO` da `received_by` y `received_at` si el paquete no
    los trae. `ENTREGADO` da `delivered_by`. `CANCELADO` da `cancelled_by` y el motivo.
  - `announced_by_usuario_id` queda sin autor: los anuncios de la v1 los hace el residente.
- **Cobro:** uno por paquete `ENTREGADO`. `monto_base` = `monto_total` = `total_amount` de la v1
  como entero. `bloques_bodegaje` = 0 y `monto_bodegaje` = 0. `cobrado_en` = `delivered_at`.
  `cobrado_por` = usuario técnico. Si en la v1 un paquete deja de estar entregado, su cobro
  importado se borra. Es un caso anómalo que se reporta.
  - El Cobro es append-only en la v2. El importador es la única excepción documentada, y solo
    sobre cobros de paquetes con `origen_v1_id`.
- **Sin avisos:** el servicio escribe directo en el modelo, sin pasar por el ciclo de vida que
  dispara notificaciones. Tampoco crea `RegistroSms` ni movimientos de saldo.
- **Borrado reflejado:** se calcula, por entidad, el conjunto de `origen_v1_id` presente en la v2
  que no está en la instantánea. Si supera el 5 % de lo importado de esa entidad, se aborta toda la
  pasada antes de escribir y se reporta como alerta. Si no, se borra en cascada: paquete → fotos
  (fila; el objeto S3 copiado se deja) → cobro. Una Persona con paquetes nativos solo se desvincula.
- **Transacción:** toda la escritura en la base de una pasada va en una sola transacción. La copia
  de fotos a S3 se hace antes del commit, pero como es idempotente, un rollback no deja estado
  inconsistente.
- **Descartes:** no se importan `customer_preferences` (decisión 2026-09-24), `notifications`, `messages`, `package_events` ni facturación y
  CUFE. Se descartan `posicion` (5 casos) y el `access_code` de 8 caracteres de la v1, que nunca se
  mostró.

### Infraestructura

- Rol `paquetex_importador` en la base de la v1: solo `CONNECT` y `SELECT` sobre las tablas
  leídas. Es el único cambio en producción y se hace a mano con el script de SQL que acompaña al
  ticket.
- Las credenciales de lectura de la v1 (base y S3) se pasan al contenedor de la v2 por el `.env`
  del servidor y se declaran de forma explícita en el `docker-compose.yml` del repo de despliegue,
  que no usa `env_file` genérico.
- Cron en el servidor v2 cada 15 minutos que ejecuta el script dentro del contenedor, con un lock
  para que no se solapen dos pasadas. El reporte se agrega a un log con rotación.
- El código se sincroniza al repo de despliegue `jemavidev/PaqueteX` siguiendo el procedimiento
  habitual (copiar archivos puntuales, no `subtree push`).

## Testing Decisions

- **Qué es una buena prueba aquí:** arma una `instantanea_v1` en memoria, corre
  `sincronizar_desde_v1` contra el Postgres real del arnés `tests/data_model`, y verifica el
  **estado observable** de la v2 (qué Personas, Paquetes, Cobros, Fotos y Usuarios existen y con
  qué valores) y el reporte. No verifica llamadas internas ni el orden de ejecución.
- **Casos que fijan el comportamiento:**
  - Primera pasada sobre una base vacía.
  - Segunda pasada idéntica: todo en cero (idempotencia).
  - La v1 cambia un estado: recibido → entregado crea el cobro.
  - La v2 editó un importado: se revierte.
  - Paquete nativo: intacto.
  - Adopción de una Persona nativa por teléfono.
  - Choque de `access_code` en modo normal y en modo final.
  - `access_code` con sufijo de año: no se revierte.
  - Anuncio que pasa a ser paquete: se conserva la identidad.
  - Borrado reflejado en cascada.
  - Persona con paquetes nativos: solo se desvincula.
  - Tope del 5 %: aborta sin borrar.
  - Mapeo de autoría, incluidos `jesus` = `jveyes` y `operator_1` → usuario técnico.
  - Cobro fiel sin recalcular.
  - Preferencias convertidas a filas por canal y evento.
  - Zona horaria normalizada.
  - Modo simular: la base y el copiador falso quedan sin cambios.
  - Foto que falla: se reporta y se reintenta.
  - Ningún aviso enviado: se usan los senders falsos existentes.
- **Prior art:** `test_importar_contactos_externos.py` (importador con filas de fuente),
  `test_migrar_codigos_del_anio.py` (interacción con el sufijo de año),
  `test_cobro_service_integration.py`, `test_paquete_foto.py` y `test_s3_foto_storage.py` (puerto
  de fotos con implementación falsa).
- **Pantallas sin apartamento:** pruebas en `tests/web` que siembran Personas y paquetes sin
  apartamento y recorren cada pantalla de la historia 46, esperando respuesta correcta y la
  presentación "Sin apartamento" donde aplique.
- **Sin pruebas automáticas** para el lector SQL de la v1, el copiador S3 real ni el script de
  línea de comandos: son adaptadores delgados. Se validan con la corrida `--simular` contra la base
  real y una copia chica de fotos antes de escalar, como el 2026-08-20.
- Antes de subir, correr `pytest` sin rutas, como hace CI, para detectar nombres de archivo de
  prueba repetidos.

## Out of Scope

- El procedimiento completo del corte: dominio final, servidor de producción de la v2, reemplazo
  de Liwa por SNS, aviso a los residentes y poner la v1 en solo lectura. Aquí solo se entregan el
  modo final y la desactivación del cron.
- Sincronización de la v2 hacia la v1 y operación simultánea en los dos sistemas.
- Etiqueta o filtro "v1/v2" en la interfaz.
- Una pantalla de asignación asistida de apartamento para Personas importadas.
- Historial de notificaciones, mensajes, facturación y CUFE de la v1.
- Borrar los objetos S3 copiados cuando se borra una foto, y borrar el bucket de la v1.
- Arreglar la v1: SMS de Liwa caído, error `'NoneType' object has no attribute 'role'` y el cron
  de limpieza que nunca corre.

## Further Notes

- **Volumen al 2026-09-23:** 609 clientes (todos con teléfono único `+57…`, 2 con email, ninguno
  con apartamento), 2.555 paquetes (2.537 entregados, 9 recibidos, 9 cancelados), 18 anuncios
  activos sin procesar, 7.475 fotos (509 MB), 7 preferencias, 3.857.500 COP cobrados desde el
  2025-11-25.
- La base de la v1 acepta conexiones desde internet (Lightsail en modo público), y se llega desde
  el servidor v2 sin túneles.
- La limpieza del staging se apoya en la definición de "limpieza selectiva" ya usada en el
  proyecto, ampliada aquí para conservar también los contactos externos y los apartamentos.
- Espacio de `access_code`: 31 símbolos a la cuarta, 923.521 combinaciones. Los choques con
  códigos de la v1 van a ser raros. Los códigos de la v1 pueden traer caracteres fuera del alfabeto
  de la v2 (`0`, `1`, `O`, `I`, `L`), y eso es válido: el alfabeto solo restringe la generación.
- Esta especificación reemplaza dos decisiones del import único del 2026-08-20: ahora sí se
  importan los cobros, y ahora sí se importan los anuncios pendientes recientes.
- **Corrección 2026-09-23 (durante el ticket 11):** en el grilling se dijo que el staging redirige
  todos los SMS a `SMS_OVERRIDE_NUMBER`. **No es así**: `test.papyrus.com.co` corre con
  `WEB_ENV=production` (lo fija el `Dockerfile`; el override se retiró el 2026-08-10), así que los
  SMS de la v2 llegan a destinatarios reales. El importador no envía avisos, pero con el espejo
  activo una prueba en la v2 sobre un paquete importado sí le escribiría a un residente real. Hay
  que decidirlo antes de activar el espejo: ver `puesta-en-marcha.md` §0.
- **Decisión 2026-09-24 (opción A):** mientras dure el espejo, `IMPORTADOR_V1_ESPEJO_ACTIVO=1`
  apaga los avisos de los paquetes importados de la v1 (`espejo_v1.py`, en
  `preparar_notificacion`). Los nativos, el OTP y las pruebas con clientes reales siguen igual. En el
  corte se quita la variable.
