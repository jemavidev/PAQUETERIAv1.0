Status: ready-for-agent
Feature: respaldos-y-restauracion
Branch: PaqueteXv.2
Fuente de verdad: sesión de `grilling` con Jesús (2026-09-25), resumida con sus 16 decisiones en
`notas-grilling.md` de esta misma carpeta · CONTEXT.md (glosario; su línea de D/R queda reemplazada, ver Further Notes)

---

## Problem Statement

PaqueteX v2 va a pasar a producción (elclub.papyrus.com.co) y después a otros conjuntos (balcones.papyrus.com.co, ...),
pero hoy no tiene respaldos: solo existen unos `pg_dump` manuales sueltos en el disco del servidor de test, sacados a
mano antes de operaciones riesgosas. Si se pierde el servidor, si un deploy daña datos o si alguien borra algo por
error, no hay forma confiable de volver atrás, y nadie se enteraría si un respaldo dejara de hacerse. Tampoco hay una
forma de llevarse los datos para montar el mismo sistema fuera de AWS, ni de bajar las fotos de los paquetes (que hoy
solo existen en S3).

## Solution

Cada instalación de PaqueteX (una por dominio) se respalda sola todos los días a las 3:00 a. m. hora de Colombia, y
además antes de cada deploy y cuando un administrador lo pide. Cada respaldo es una carpeta autocontenida con la base
de datos completa, una copia exacta del código que estaba desplegado, un manifiesto (qué es, de qué versión, con qué
conteos y huellas) y una plantilla del `.env` con los secretos ofuscados. Los respaldos suben a un bucket de S3
dedicado en la cuenta de Jesús (una carpeta por dominio, llave de solo subida por servidor), con conservación
automática por tipo, y las últimas 3 quedan también en el disco del servidor.

Si algo falla llega un correo inmediato; los lunes llega un resumen aunque todo esté bien; los domingos se prueba
automáticamente que el último respaldo sí se restaura. Una pantalla "Respaldos" en `/administracion` deja descargar
cualquier respaldo como `.zip`, pedir un respaldo al momento, traer las fotos de S3 al servidor de forma incremental
para descargarlas ("solo las nuevas" o "todas"), y ver el comando exacto para restaurar. Restaurar se hace solo por
SSH, con un script que se niega a hacer algo peligroso: verifica integridad, que el respaldo sea del mismo sistema,
que la versión sea compatible, saca una copia de lo actual, pide escribir el dominio para confirmar, y deja el sistema
encendido y verificado.

## User Stories

**Respaldo diario**

1. Como administrador del sistema, quiero que la base de datos se respalde sola todos los días a las 3:00 a. m. hora
   de Colombia, para no depender de acordarme de hacerlo.
2. Como administrador, quiero que el respaldo diario corra aunque nadie haya entrado al sistema ese día, para que la
   protección no dependa del uso.
3. Como administrador, quiero que el respaldo contenga la base de datos completa en el formato nativo de Postgres,
   para restaurarla con las herramientas estándar en cualquier lugar.
4. Como administrador, quiero que cada respaldo incluya una copia exacta del código que estaba desplegado ese día
   (compose, Caddyfile, Dockerfile, requirements, código, migraciones y scripts), para restaurar "el mismo sistema" sin
   depender de que ese commit siga existiendo en GitHub.
5. Como administrador, quiero que cada respaldo incluya un manifiesto con fecha y hora, dominio y conjunto, commit
   desplegado y versión de la base de datos (migración Alembic), para saber exactamente qué tengo en las manos.
6. Como administrador, quiero que el manifiesto guarde los conteos de las tablas principales (paquetes, personas,
   usuarios, etc.), para poder comprobar después que una restauración recuperó todo.
7. Como administrador, quiero que el manifiesto guarde tamaños y huellas (checksums) de cada archivo, para detectar
   una copia corrupta o una descarga incompleta.
8. Como administrador, quiero que cada respaldo incluya una plantilla del `.env` con TODAS las variables del sistema,
   agrupadas y con un comentario de para qué sirve cada una, para saber qué configurar al restaurar.
9. Como administrador, quiero que en la plantilla lo que no es secreto aparezca con su valor completo, para no tener
   que reconstruirlo a mano.
10. Como administrador, quiero que los secretos aparezcan ofuscados como `ABC****XYZ` (3 primeros + 3 últimos), para
    reconocer cuál llave era sin exponerla.
11. Como administrador, quiero que un secreto de menos de 12 caracteres aparezca solo como `****`, para que ofuscarlo
    no revele media contraseña.
12. Como administrador, quiero que la plantilla se genere del `.env` real en cada respaldo, para que nunca quede
    desactualizada cuando se agregue una variable nueva.
13. Como administrador, quiero que el `.env` real nunca viaje en un respaldo, para que las copias no contengan
    credenciales.
14. Como administrador, quiero que un respaldo que falle a mitad de camino no deje una copia incompleta que parezca
    buena, para no confiar en algo roto.
15. Como administrador, quiero que dos respaldos nunca corran a la vez sobre el mismo servidor (por ejemplo el diario
    y un "Respaldar ahora"), para no mezclar archivos.

**Dónde se guardan y cuánto tiempo**

16. Como administrador, quiero que los respaldos se suban a un bucket de S3 dedicado solo a respaldos, en mi propia
    cuenta de AWS, para que perder el servidor no signifique perder los respaldos.
17. Como administrador, quiero que el servidor solo pueda SUBIR respaldos (no leerlos, borrarlos ni sobrescribirlos),
    para que alguien que entre al servidor no pueda destruirlos.
18. Como administrador, quiero que el bucket sea privado y con el cifrado por defecto de S3, para que las copias no
    queden expuestas en internet.
19. Como administrador, quiero que las últimas 3 copias también queden en el disco del servidor, para restaurar rápido
    algo puntual sin descargar nada.
20. Como administrador, quiero que las copias diarias se conserven 30 días, para cubrir errores que se notan pronto.
21. Como administrador, quiero que la copia del día 1 de cada mes se conserve 12 meses, para cubrir errores que se
    descubren tarde.
22. Como administrador, quiero que la copia del 1 de enero se conserve sin fecha de borrado, como registro histórico
    de cada año.
23. Como administrador, quiero que el borrado de copias viejas lo haga S3 solo, por reglas por carpeta, para que el
    servidor no necesite permiso de borrar.
24. Como administrador de varios conjuntos, quiero un solo bucket con una carpeta por dominio (test, elclub,
    balcones...), para tener todo en un lugar sin mezclar conjuntos.
25. Como administrador de varios conjuntos, quiero que la llave de cada servidor solo alcance la carpeta de su
    dominio, para que un servidor comprometido no toque los respaldos de otro conjunto.
26. Como administrador, quiero que test.papyrus.com.co también se respalde, para probar todo esto antes de
    producción.

**Respaldos puntuales**

27. Como administrador, quiero que se saque un respaldo automático justo antes de cada deploy, antes de que corran
    las migraciones, para poder volver al minuto anterior si un deploy daña datos.
28. Como administrador, quiero que si ese respaldo previo falla, el deploy no continúe, para no aplicar cambios sin red
    de seguridad.
29. Como administrador, quiero un botón "Respaldar ahora", para sacar una copia antes de cualquier operación manual
    riesgosa.
30. Como administrador, quiero que los respaldos puntuales vayan a su propia carpeta y se conserven 30 días, para no
    mezclarlos con la rotación de los diarios.
31. Como administrador, quiero que cada respaldo diga en su manifiesto por qué se hizo (diario, antes de deploy, a
    pedido de quién, antes de restaurar), para entender el historial.

**Avisos**

32. Como administrador, quiero un correo inmediato si un respaldo falla, diciendo qué paso falló (volcado, subida a
    S3, espacio en disco...), para actuar ese mismo día.
33. Como administrador, quiero un resumen por correo cada lunes aunque todo haya salido bien ("7 de 7 OK, último de
    X MB, subido a S3"), para darme cuenta si un lunes NO llega.
34. Como administrador, quiero que los avisos lleguen a varios correos (hoy `jveyes@gmail.com` e
    `info@papyrus.com.co`), configurables por servidor, para que cada conjunto avise a quien corresponda.
35. Como administrador, quiero un aviso por correo si el disco del servidor pasa del 80 %, para no quedarme sin
    espacio para respaldos ni fotos.
36. Como administrador, quiero una línea por corrida en un registro del servidor, para revisar el historial sin
    depender del correo.

**Prueba semanal de restauración**

37. Como administrador, quiero que cada domingo en la madrugada se restaure automáticamente el último respaldo en una
    base de datos temporal y aparte, para saber que los respaldos sí sirven.
38. Como administrador, quiero que esa prueba compruebe que la restauración termina sin errores, que la versión de la
    base de datos coincide con el manifiesto y que los conteos coinciden, para que "OK" signifique algo.
39. Como administrador, quiero que la base temporal se borre al terminar y nunca toque la base real, para que probar
    no ponga en riesgo el sistema.
40. Como administrador, quiero ver el resultado de la prueba en el resumen del lunes ("2.592 paquetes y 617 personas
    recuperados") y un correo inmediato si falla.

**Pantalla "Respaldos"**

41. Como administrador (rol ADMIN), quiero una pantalla "Respaldos" en `/administracion`, para gestionar todo esto sin
    SSH.
42. Como operador, no quiero ver ni poder abrir esa pantalla, porque contiene los datos de todo el conjunto.
43. Como administrador, quiero ver la lista de respaldos disponibles con fecha, tipo, tamaño y estado, para elegir.
44. Como administrador, quiero descargar el respaldo de la fecha que elija (o el más reciente) como un `.zip` con sus
    cuatro archivos, para llevármelo a donde quiera, incluso fuera de AWS.
45. Como administrador, quiero ver cuándo fue el último respaldo y si salió bien, para confirmar de un vistazo que el
    sistema está protegido.
46. Como administrador, quiero ver para cada respaldo el comando exacto de restauración, listo para copiar, para no
    tener que armarlo a mano en un momento de estrés.
47. Como administrador, quiero ver en la pantalla los pasos de restauración explicados, para seguirlos aunque no lo
    haya hecho antes.
48. Como administrador, quiero que "Respaldar ahora" me diga cuándo terminó y si salió bien, para no quedarme dudando.

**Fotos (a pedido, fuera del respaldo diario)**

49. Como administrador, quiero un botón que copie las fotos de S3 al disco del servidor, para poder descargarlas.
50. Como administrador, quiero que esa copia sea incremental (la primera vez todas, después solo las nuevas), para que
    no tarde ni ocupe más de lo necesario.
51. Como administrador, quiero que la copia corra en segundo plano mostrando el avance ("copiando 1.234 de 7.511"),
    para poder cerrar la pantalla mientras tanto.
52. Como administrador, quiero descargar "solo las nuevas desde la última descarga" como `.zip` con la misma
    estructura de carpetas que en S3, para mantener al día mi copia local descomprimiendo encima.
53. Como administrador, quiero también "descargar todas", para la primera vez o si perdí mi copia local.
54. Como administrador, quiero ver la fecha de la última descarga y cuántas fotos nuevas (y cuánto pesan) hay desde
    entonces, para decidir si vale la pena bajarlas.
55. Como administrador, quiero que la "última descarga" se registre por sistema (no por usuario), con la opción
    "todas" siempre disponible, para que nada se pierda si descargan dos administradores.
56. Como administrador, quiero que la descarga de fotos no se corte ni agote la memoria del servidor aunque sean
    varios GB, para que funcione en un servidor pequeño.

**Restauración (solo por SSH)**

57. Como administrador, quiero restaurar con un solo script (`restaurar.sh <carpeta-del-respaldo>`), para no depender
    de recordar pasos.
58. Como administrador, quiero que el script verifique las huellas del manifiesto antes de tocar nada, para no
    restaurar una copia corrupta.
59. Como administrador, quiero que el script se niegue si el respaldo es de otro dominio o conjunto, salvo que lo pida
    explícitamente con `--otro-destino`, para no pisar un conjunto con los datos de otro.
60. Como administrador, quiero que el script se niegue si la base de datos del respaldo es más nueva que el código
    instalado, diciéndome que despliegue primero el `sistema.tar.gz` de ese respaldo, para no dejar el sistema
    inconsistente.
61. Como administrador, quiero que si la base del respaldo es más vieja, el script la restaure y aplique las
    migraciones pendientes, para quedar en la versión actual.
62. Como administrador, quiero que el script saque automáticamente una copia de la base actual antes de restaurar
    (`antes_de_restaurar_<fecha>`), para poder deshacer si elegí la fecha equivocada.
63. Como administrador, quiero que el script me pida escribir el dominio para confirmar (no un simple "sí"), para no
    restaurar por un Enter distraído.
64. Como administrador, quiero que el script detenga la app y el importador antes de restaurar y los vuelva a encender
    después, para que nadie escriba datos a mitad de la restauración.
65. Como administrador, quiero que el script verifique `/health` al terminar y me diga claramente si quedó bien, para
    saber que el sistema volvió.
66. Como administrador que monta el sistema en un servidor nuevo (dentro o fuera de AWS), quiero poder restaurar con el
    mismo script a partir del `.zip` descargado, después de poner yo el `.env`, para no tener dos procedimientos.

**Puesta en marcha en AWS**

67. Como administrador, quiero que el bucket, sus reglas de conservación, las llaves por servidor y el permiso de
    lectura de fotos queden definidos como archivos en el repo (sin secretos), para poder recrearlos o revisarlos.
68. Como administrador, quiero que las llaves nuevas se instalen directo en el `.env` del servidor sin mostrarse ni
    guardarse en el repo, para que no queden expuestas (los repos son públicos).

## Implementation Decisions

- **Un módulo profundo de respaldos en el dominio**, con una interfaz pequeña que oculta `pg_dump`/`pg_restore`, el
  armado de la carpeta, el manifiesto, la plantilla del `.env`, la subida y la rotación. Operaciones: crear un respaldo
  (con su motivo: diario / antes de deploy / a pedido / antes de restaurar), listar respaldos, verificar un respaldo
  (huellas + manifiesto), restaurar (con las protecciones) y probar la restauración contra una base temporal.
- **Puertos, al estilo de `FotoStorage` / `EmailSender` / el copiador del importador v1:** un destino de respaldos (S3
  real; falso en memoria en pruebas), un origen de fotos para la sincronización (S3 real; falso en pruebas) y el
  `EmailSender` existente para los avisos.
- **Un único comando (CLI) dentro del contenedor de la app** expone esas operaciones — mismo patrón que el importador
  v1 (`python -m ...` ejecutado con `docker compose exec`). Lo usan: el cron del servidor (diario, prueba del domingo,
  resumen del lunes, aviso de disco), el paso previo al deploy y la pantalla web. No hay tres implementaciones.
- **Cron en el host con envoltura + candado (`flock`) + log rotado**, igual que el del importador v1. El candado evita
  dos respaldos simultáneos (el diario y un "Respaldar ahora").
- **La imagen de la app gana el cliente de Postgres 16** (`pg_dump`/`pg_restore`, misma versión mayor que el servidor
  de BD) y el contenedor gana montajes de SOLO LECTURA del checkout (para `sistema.tar.gz` y el commit) y del `.env`
  (para la plantilla), más una carpeta de lectura/escritura en el host para los respaldos locales y otra para la copia
  local de las fotos. Cambia el `Dockerfile` y el `docker-compose.yml` del repo de deploy → ese deploy reconstruye la
  imagen.
- **Formato de la carpeta de respaldo:** `base_datos.dump` (`pg_dump -Fc`), `sistema.tar.gz`, `manifiesto.txt`,
  `env.plantilla`. Se arma en una carpeta temporal y se "publica" solo al terminar completa (renombre atómico); una
  corrida fallida no deja una carpeta con apariencia de buena.
- **Ofuscación de secretos:** una lista explícita de nombres de variables secretas (llaves, contraseñas, tokens,
  `SECRET_KEY`...) más una heurística de respaldo por nombre (`KEY`, `SECRET`, `PASSWORD`, `TOKEN`); ante la duda, se
  trata como secreto. Secretos ≥ 12 caracteres → `ABC****XYZ`; más cortos → `****`.
- **S3:** bucket `paquetex-respaldos` en la cuenta `172460160630`, privado, cifrado por defecto, prefijo por dominio
  con subcarpetas `diario/`, `mensual/`, `anual/`, `puntual/`. La mensual y la anual son la misma copia del día 1 / 1
  de enero subida también a su carpeta. Reglas de ciclo de vida: `diario/` y `puntual/` 30 días, `mensual/` 365 días,
  `anual/` sin expiración. Llave por servidor: solo `PutObject` bajo su prefijo, sin lectura, listado ni borrado; no
  sobrescribir se garantiza con nombres únicos por fecha y hora.
- **Retención local:** las últimas 3 carpetas en el disco del servidor; la rotación local sí borra (es del servidor).
- **Respaldo previo al deploy:** paso nuevo en el workflow de GitHub Actions, por SSH, ANTES de `git reset --hard` y
  del reinicio (las migraciones corren al arrancar la app). Si falla, el deploy se detiene. Respaldo con motivo
  "antes de deploy" y el commit que estaba corriendo.
- **"Respaldar ahora" y la copia de fotos desde la web:** la ruta lanza la operación en segundo plano, fuera del ciclo
  de la petición, y la pantalla consulta su estado (en curso / avance / terminado / falló). El estado de la operación
  y el registro de "última descarga de fotos" se guardan en la base de datos (una tabla pequeña de estado de
  respaldos/fotos), no en memoria, para sobrevivir a reinicios.
- **Descargas (`.zip` del respaldo, fotos nuevas/todas):** se transmiten por partes (streaming), sin armar el `.zip`
  completo en memoria ni en un archivo temporal gigante.
- **Fotos "nuevas desde la última descarga":** se determinan por la fecha de creación de las fotos registradas en el
  sistema contra la marca de la última descarga; la estructura de carpetas es la misma de las claves de S3. La llave de
  fotos del servidor gana `ListBucket` y `GetObject` SOLO sobre el bucket (y prefijo) de fotos.
- **Restauración:** `restaurar.sh` es delgado (detener/encender contenedores y el cron del importador, pedir la
  confirmación escrita); las 6 protecciones y la restauración en sí viven en el módulo de respaldos. Orden: verificar
  huellas → mismo sistema (salvo `--otro-destino`) → versión compatible (BD más nueva que el código: se niega; más
  vieja: restaura y luego `alembic upgrade head`) → respaldo "antes de restaurar" de la BD actual → confirmación
  escribiendo el dominio → detener app + importador → restaurar → encender → verificar `/health`.
- **Prueba del domingo:** levanta un Postgres temporal aparte (contenedor desechable, misma versión mayor), restaura el
  último respaldo diario, compara versión Alembic y conteos con el manifiesto, destruye el temporal; nunca usa la base
  real ni sus credenciales.
- **Avisos:** correo inmediato ante cualquier falla (qué paso, con el error), resumen los lunes (respaldos de la
  semana, último tamaño, subida a S3, resultado de la prueba del domingo, espacio en disco), aviso de disco > 80 %.
  Destinatarios en `RESPALDO_CORREO_AVISOS` (lista separada por coma), por servidor.
- **Pantalla "Respaldos":** solo ADMIN (`require_admin`); entra al menú de cuenta dentro de "Datos".
- **Glosario:** se reemplaza en CONTEXT.md la línea de D/R ("`pg_dump` horario → S3 cifrado/versionado, RPO ~1 h") por
  la decisión actual.

## Testing Decisions

- **Buena prueba = comportamiento observable**, no detalles internos: qué archivos produce un respaldo y qué dicen,
  qué se sube y a qué carpeta, qué se niega a hacer la restauración y por qué, qué correo sale, qué muestra y descarga
  la pantalla. Nunca asertar sobre llamadas internas ni sobre el texto exacto de los comandos del sistema.
- **Seam A — módulo de respaldos**, contra el Postgres efímero de las pruebas (`tests/_harness.py`) con un destino S3
  falso en memoria, un origen de fotos falso y el `EmailSender` falso existente. Cubre: los 4 archivos y su
  contenido; manifiesto (commit, versión, conteos, huellas); `env.plantilla` (valores no secretos completos, ofuscación
  3+3, `****` para cortos, nunca el `.env` real); carpetas diario/mensual/anual/puntual según fecha y motivo; retención
  local de 3; corrida fallida sin carpeta publicada; candado; ciclo real `pg_dump` → `pg_restore` con conteos iguales;
  cada una de las 6 protecciones negándose cuando corresponde; restaurar un respaldo viejo aplica migraciones; prueba
  semanal OK y fallida; correos de falla, resumen y disco; sincronización incremental de fotos y "solo las nuevas".
  Prior art: `test_importador_v1_fotos.py` (servicio + copiador falso en memoria contra el Postgres efímero) y las
  pruebas de migraciones que usan el harness.
- **Seam B — pantalla "Respaldos" por HTTP** (TestClient, como `test_admin_motivos_cancelacion.py` y el resto de
  `/administracion`): solo ADMIN (operador 403, sin sesión → login), lista, descarga `.zip` (cabeceras y contenido),
  "Respaldar ahora" (lanza y reporta estado), botón de fotos (lanza, avance, descargas "nuevas"/"todas"), comando de
  restauración mostrado.
- **Sin prueba automática, verificado en vivo en test.papyrus.com.co** (criterio de aceptación del ticket que lo
  toque): el cron del host, el paso en GitHub Actions, las reglas del bucket y los permisos de las llaves (incluido
  que la llave del servidor NO pueda leer ni borrar), y un simulacro completo de restauración con `restaurar.sh`.

## Out of Scope

- Cifrado propio de las copias (Jesús decidió no cifrar; queda el cifrado por defecto de S3 y el bucket privado).
- Botón "Restaurar" en la web: restaurar es solo por SSH.
- Fotos dentro del respaldo diario: van aparte, a pedido.
- Un tercer destino fuera de AWS (Google Drive, Backblaze, ...): posible a futuro, no pedido.
- Respaldos cada hora / RPO de 1 hora (lo que decía el brief original).
- Configurar el `.env` o los secretos de un servidor restaurado: lo hace Jesús a mano.
- Producción (elclub.papyrus.com.co) y otros conjuntos: se implementa y prueba primero en test; replicarlo en cada
  servidor nuevo es parte de montar ese servidor.

## Further Notes

- Hechos del servidor de test (2026-09-25): Lightsail 2 vCPU / 1 GB sin swap / 38 GB (20 %); BD 22 MB; ~330
  paquetes/mes; fotos ~1,5–2,5 GB estimadas en S3 (`paquetex-staging-fotos`, cuenta `172460160630`, llave de solo
  subida); SMTP configurado. Con 1 GB de RAM, el `pg_restore` de la prueba del domingo y las descargas por streaming
  deben cuidar memoria.
- El deploy de test a veces solo reinicia la app (bind-mount del código) y solo reconstruye la imagen si cambian
  `requirements.txt`, `Dockerfile` o `docker-compose.yml`: el ticket que agregue el cliente de Postgres y los montajes
  va a disparar un rebuild.
- Los repos (`PAQUETERIAv1.0`, `PaqueteX`) son PÚBLICOS: nada de respaldos, llaves ni valores del `.env` en git.
- Lo acordado en detalle y el porqué de cada decisión: `notas-grilling.md`.
