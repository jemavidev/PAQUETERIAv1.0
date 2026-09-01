# Spec — `/administracion/proveedores`: gestionar proveedores de notificación desde formularios

**Fuente:** conversación 2026-09-01 (grilling), motivada por la investigación en vivo
de [[287]]/[[288]] (`.scratch/pendientes-cliente`) — diagnosticar y corregir el envío
de SMS terminó exponiendo que TODA la configuración de proveedores (AWS SNS, LIWA,
Twilio, SMTP) vive hoy en el `.env` del servidor: cambiar cuál proveedor está
habilitado, en qué orden, o rotar una credencial, exige editar el archivo a mano por
SSH y reiniciar el contenedor — nada de esto pasa por el repo ni por una pantalla,
así que el cliente no tiene forma propia de gestionarlo.

Sigue directamente a un "Out of Scope" explícito de `.scratch/sms-failover-twilio-sns/
spec.md`: *"Orden de precedencia configurable por el operador ... — LIWA → Twilio → SNS
es una constante fija en este slice."* Este spec cierra exactamente ese pendiente, y lo
extiende a los demás proveedores (SMTP) y al mecanismo de aplicar credenciales sin SSH manual.

## Problem Statement

El cliente (Jesús, quien opera el sistema día a día en nombre de Papyrus) no tiene
ninguna forma de ver ni cambiar qué proveedores de SMS/Email están activos, en qué
orden se prueban, o sus credenciales, sin pedirle a un desarrollador que edite el
`.env` del servidor por SSH y reinicie el contenedor. Esto ya causó fricción real: la
sesión de diagnóstico de [[287]]/[[288]] tomó decenas de minutos de ida y vuelta por
SSH solo para CONFIRMAR qué estaba configurado, sin que el cliente pudiera verlo ni
tocarlo él mismo. A futuro, cada vez que un proveedor cambie sus credenciales, se
quiera probar uno nuevo, o haya que apagar temporalmente uno que está fallando (como
LIWA/Twilio hoy mismo, ver [[288]]), la única vía sigue siendo pedir intervención
manual de desarrollo.

## Solution

Una pantalla nueva, `/administracion/proveedores` (solo rol ADMIN), separada de
`/administracion/notificaciones` (esa edita el TEXTO de los mensajes; esta edita la
plomería de cómo se envían). Por cada canal que ya tiene al menos un proveedor real
implementado en código (hoy: SMS con AWS SNS/LIWA/Twilio, Email con SMTP), la pantalla
muestra sus proveedores con:

- Un **toggle de habilitado/deshabilitado** por proveedor.
- Un **orden de precedencia** (solo relevante para canales con más de un proveedor —
  hoy solo SMS) que gobierna el mismo mecanismo de failover que `FailoverSmsSender`
  ya implementa.
- Un **formulario de credenciales** por proveedor (los campos que ese proveedor
  necesita) que nunca muestra el valor real de un secreto ya guardado — solo un
  placeholder tipo "•••• (configurado)"; dejar el campo vacío al guardar significa
  "no cambiar esa credencial".

Dos partes con mecanismos de aplicación MUY distintos:

- **Habilitado/orden** vive en una tabla nueva de base de datos — cambiarlo es
  **instantáneo**, la próxima notificación ya arma la cadena de failover con el orden
  nuevo, sin restart.
- **Credenciales** siguen viviendo SOLO en el `.env` del servidor (nunca en la base de
  datos, ni cifradas) — guardar un campo de credencial dispara una llamada SSH desde
  la propia app hacia el servidor, con una llave restringida por `authorized_keys`
  (`command=...`) a UNA sola operación: escribir en `.env` solamente las variables de
  un **allowlist explícito** (nunca `KEY=VALOR` libre), y correr `docker compose up -d`
  para que el contenedor las recargue. Esto tarda ~1 minuto (como un mini-deploy); si
  falla, se muestra el error tal cual y la credencial anterior sigue activa — nunca un
  "guardado" optimista que resulte falso.

La cadena real de proveedores que arma `construir_sender()` en cada envío exige **las
dos condiciones a la vez**: habilitado en la base de datos Y con credenciales
completas en `.env` (mismo chequeo `.configurado()`/`.sns_habilitado()` de hoy) — un
proveedor habilitado sin credenciales simplemente no entra a la cadena, sin error.

Todo cambio (habilitar/deshabilitar, reordenar, o tocar una credencial) queda en un
historial de auditoría append-only — igual que `PlantillaNotificacionHistorial` ya
hace para plantillas — registrando SIEMPRE quién/cuándo/qué campo, pero **nunca el
valor de un secreto**, ni antes ni después.

Ni WhatsApp ni Llamadas aparecen en esta pantalla todavía — no tienen ningún proveedor
real implementado en código hoy (`_canal_configurado` para WhatsApp siempre devuelve
`False`); la lista de proveedores/campos por canal vive en un registro en código
(mismo patrón que ya usa `construir_sender()`), así que el día que exista un
`WhatsAppSender`/`LlamadaSender` real y se registre, su sección aparece sola en esta
pantalla, sin tocar la base de datos ni el HTML de nuevo.

**Entregable en dos fases** (ver Out of Scope de cada una implícito en la otra):

- **Fase 1**: tabla de habilitado/orden + refactor de la cadena de failover para
  leerla + auditoría + pantalla de solo toggles/reordenar + migración inicial que
  siembra el estado actual (AWS SNS → LIWA → Twilio, los tres habilitados) para que
  el día del deploy el comportamiento real NO cambie de sorpresa.
- **Fase 2**: el mecanismo SSH+allowlist+restart para editar credenciales reales desde
  la misma pantalla.

## User Stories

1. Como Jesús (admin), quiero ver en una sola pantalla qué proveedores de SMS/Email
   están habilitados hoy, sin tener que entrar por SSH a leer el `.env` del servidor.
2. Como Jesús, quiero ver el orden de precedencia actual de los proveedores de SMS
   (hoy AWS SNS → LIWA → Twilio), para entender cuál se prueba primero sin leer código.
3. Como Jesús, quiero poder deshabilitar un proveedor específico (ej. LIWA o Twilio,
   que hoy están fallando según [[288]]) sin borrar sus credenciales, para sacarlo
   temporalmente de la cadena y poder reactivarlo después sin volver a escribir nada.
4. Como Jesús, quiero que deshabilitar/reordenar un proveedor tenga efecto
   INMEDIATO (sin esperar un redeploy ni un restart), para poder reaccionar rápido
   ante un proveedor caído.
5. Como Jesús, quiero poder reordenar la precedencia de los proveedores de SMS (ej.
   volver a poner LIWA primero si algún día se resuelve su bloqueo de IP), sin pedirle
   a un desarrollador que edite una constante en código y despliegue.
6. Como Jesús, quiero poder actualizar la credencial de un proveedor (ej. rotar el
   Auth Token de Twilio) desde un formulario, sin entrar por SSH a editar el `.env`
   a mano.
7. Como Jesús, quiero que el formulario de credenciales NUNCA me muestre el valor real
   de una que ya guardé, para no volverme yo mismo un vector de fuga de esos secretos
   (captura de pantalla, `view-source`, etc.).
8. Como Jesús, quiero poder dejar en blanco los campos de una credencial que no quiero
   cambiar al guardar el resto del formulario, para no tener que reescribir todo cada
   vez que solo cambia un campo.
9. Como Jesús, quiero que guardar una credencial nueva confirme si de verdad se aplicó
   (éxito/error explícito), no un "guardado" que en el fondo no llegó al servidor.
10. Como Jesús, quiero que si aplicar una credencial nueva falla (servidor
    inalcanzable, `docker compose up -d` falla, etc.), la credencial ANTERIOR siga
    activa — nunca quedar con un proveedor a medio configurar sin saberlo.
11. Como Jesús, quiero, después de guardar una credencial nueva, poder usar el botón
    "Enviar prueba" que ya existe en `/administracion/notificaciones` para confirmar
    en vivo que de verdad funciona, sin necesitar un mecanismo de prueba aparte.
12. Como Jesús, quiero que esta pantalla quede reservada solo a rol ADMIN (igual que
    `/administracion/notificaciones`), para que un OPERADOR nunca pueda ver ni tocar
    credenciales de proveedores externos.
13. Como Jesús, quiero un historial de auditoría de estos cambios (quién, cuándo, qué
    campo, y para habilitado/orden el valor completo del cambio), para poder responder
    "¿quién tocó esto y cuándo" el día que algo deje de funcionar.
14. Como Jesús, quiero que ese historial NUNCA guarde el valor de un secreto (ni antes
    ni después del cambio), para que el propio historial de auditoría no se vuelva un
    lugar más donde credenciales quedan expuestas.
15. Como desarrollador, quiero que la llave SSH que la app usa para aplicar cambios de
    `.env` esté restringida por `authorized_keys` (`command=...`) a UNA operación
    puntual (escribir SOLO variables de un allowlist + `docker compose up -d`), para
    que ni siquiera una app comprometida pueda usarla para obtener una shell libre o
    tocar variables ajenas a proveedores (`DATABASE_URL`, `SECRET_KEY`, etc.).
16. Como desarrollador, quiero que el allowlist de variables aceptadas por ese
    comando SSH sea la misma lista de campos que declara el registro de proveedores en
    código, para que agregar un campo nuevo a un proveedor sea un solo cambio, no dos
    lugares que se puedan desincronizar.
17. Como desarrollador, quiero que la cadena real de proveedores en cada envío exija
    habilitado (BD) Y configurado (`.env`) a la vez, para que "prender" un proveedor en
    la pantalla sin haberle puesto credenciales todavía no rompa nada — simplemente no
    entra a la cadena, igual que hoy con una variable faltante.
18. Como desarrollador, quiero que `construir_sender()` (el corazón del failover, ya
    probado en [[sms-failover-twilio-sns]]) no cambie de forma en absoluto — solo
    cambia CÓMO `_sender_base()`/`get_otp_sender()` arman la lista de candidatos que le
    pasan, leyendo la BD en vez de una constante fija.
19. Como desarrollador, quiero que agregar un proveedor nuevo en el futuro (ej. un
    proveedor de llamadas) signifique escribir su clase `Sender` + una entrada en el
    registro de proveedores en código — no una migración de base de datos ni cambios
    en el HTML de la pantalla.
20. Como Jesús, quiero que WhatsApp y Llamadas simplemente NO aparezcan en esta
    pantalla mientras no tengan un proveedor real (evitar una sección "próximamente"
    que no hace nada), para no ver opciones muertas.
21. Como desarrollador, quiero que la migración inicial de la Fase 1 siembre la base de
    datos con el estado de precedencia que ya está en producción hoy (AWS SNS → LIWA →
    Twilio, los tres habilitados), para que desplegar esta feature no cambie ningún
    comportamiento real el día que sale a producción.
22. Como Jesús, quiero poder ver esta pantalla y sus toggles YA funcionando (Fase 1)
    aunque todavía no pueda editar credenciales desde ahí (Fase 2 pendiente), para
    empezar a ganar valor (apagar un proveedor caído sin deploy) sin esperar la pieza
    más delicada de construir.
23. Como desarrollador/tester, quiero que el mecanismo SSH de la Fase 2 tenga tests que
    nunca toquen un servidor real (mock de la llamada SSH/subproceso), para que la
    suite automatizada no dependa de infraestructura externa ni cueste tiempo/dinero.
24. Como desarrollador/tester, quiero tests del service de dominio nuevo
    (`proveedor_config_service.py`) que verifiquen habilitar/deshabilitar/reordenar
    contra una sesión de base de datos de test, sin pasar por HTTP, igual que ya
    existen para `notificacion_service.py`.

## Implementation Decisions

- **Módulo de dominio nuevo:** `app/domain/proveedor_config_service.py` — funciones
  puras sobre la tabla nueva (listar config por canal, guardar habilitado/orden,
  registrar en el historial), mismo estilo/altitud que `notificacion_service.py`. No
  conoce SSH ni `.env` — eso es responsabilidad de la Fase 2.

- **Registro de proveedores en código:** un diccionario/lista chica (ubicación
  sugerida: junto a `sms_failover.py`, o un módulo nuevo `proveedores_catalogo.py`)
  que declara, por canal, la lista ordenada de proveedores disponibles y, por cada
  uno, sus campos de configuración (nombre de variable de entorno, tipo, si es
  secreto). Esta es la ÚNICA fuente de verdad de "qué proveedores/campos existen" —
  tanto la pantalla (qué formulario mostrar) como el allowlist del comando SSH (Fase
  2) se derivan de este registro, nunca duplicados a mano en dos lugares.

- **Tabla de base de datos nueva** (Fase 1): un registro por `(canal, proveedor)` con
  al menos: habilitado (bool), orden (int, nullable — solo aplica a canales con más
  de un proveedor), `updated_at`, `updated_by` (FK a `usuarios`, nullable, mismo
  criterio que `PlantillaNotificacionHistorial.usuario_id`).

- **Tabla de auditoría nueva** (Fase 1), append-only, mismo patrón exacto que
  `PlantillaNotificacionHistorial` (solo INSERT, nunca UPDATE/DELETE): por cada
  cambio, guarda canal/proveedor, quién, cuándo, y:
  - Para habilitado/orden: el valor anterior y nuevo completos (no es secreto).
  - Para una credencial (Fase 2): SOLO el nombre del campo que cambió — nunca su
    valor, ni antes ni después.

- **Refactor de la cadena de failover existente** (Fase 1): `_sender_base()`
  (`app/web/notifications.py`) y `get_otp_sender()` (`app/web/otp.py`) dejan de
  recorrer una lista literal `[(sns_habilitado(), Sns...), (liwa...), ...]` fija en
  código, y en su lugar arman esa misma lista de candidatos `[(bool, sender), ...]`
  consultando `proveedor_config_service` para el orden y el habilitado, combinado con
  el `.configurado()`/`.sns_habilitado()` de cada proveedor (ambas condiciones
  necesarias, ver Solution). `construir_sender()` en sí (`sms_failover.py`) no
  cambia — sigue recibiendo exactamente la misma forma de entrada.

- **Migración de siembra inicial** (Fase 1): una migración de Alembic que inserta las
  filas iniciales replicando el estado actual en producción (AWS SNS orden 1
  habilitado, LIWA orden 2 habilitado, Twilio orden 3 habilitado; SMTP único
  proveedor de Email, habilitado) — el deploy de esta feature no debe cambiar ningún
  comportamiento observable el mismo día.

- **Pantalla `/administracion/proveedores`** (Fase 1: toggles/orden; Fase 2: además
  credenciales), protegida por `require_admin` (mismo patrón que
  `/administracion/notificaciones`). Un formulario por canal, agrupando sus
  proveedores; toggle de habilitado + input numérico (o control de arrastrar) para
  orden en canales con más de un proveedor.

- **Formulario de credenciales** (Fase 2): un campo de texto por variable del
  registro de proveedores, tipo `password`/enmascarado para los marcados como
  secretos. Al renderizar, cada campo secreto ya configurado muestra un placeholder
  fijo (ej. "•••• configurado") — NUNCA el valor real leído de ningún lado (la app ni
  siquiera necesita poder leer el `.env` del servidor para esto: basta con saber
  cuáles variables están seteadas, igual que hoy hacen `.configurado()`). Al
  enviar, solo los campos con contenido nuevo se incluyen en la llamada SSH; los
  vacíos se omiten (no se sobreescriben).

- **Mecanismo de aplicación de credenciales** (Fase 2): una función tipo
  `aplicar_credenciales_proveedor(cambios: dict[str, str]) -> None` en un módulo de
  infraestructura nuevo (ej. `app/infra/deploy_ssh.py` o similar — fuera de
  `app/domain`, ya que habla con un proceso externo, mismo criterio que
  `sns_sender.py`/`liwa_sender.py` viven en `domain` pero hablan HTTP/boto3 hacia
  afuera — aquí el límite es SSH). Valida cada clave de `cambios` contra el registro
  de proveedores (rechaza cualquier variable fuera del allowlist ANTES de intentar la
  conexión SSH — defensa en profundidad, no confiar solo en el `command=` del
  servidor). Se conecta por SSH con una llave dedicada (nueva variable de entorno,
  ej. `DEPLOY_SSH_KEY_PATH` o el contenido de la llave vía secreto), ejecuta el
  comando remoto (que en el servidor ya viene restringido por `authorized_keys`), y
  propaga cualquier fallo (timeout, comando rechazado, `docker compose up -d` con
  error) como excepción — la ruta HTTP lo traduce a un error visible, nunca a un
  "guardado" silencioso.

- **Script remoto en el servidor** (Fase 2, infraestructura fuera del repo de la
  app — vive en la configuración del servidor/deploy, no en `PAQUETERIAv1.0` ni en
  `PaqueteX`): un script pequeño invocado por el `command=` forzado de
  `authorized_keys`, que lee pares `KEY=VALOR` de stdin, rechaza cualquier `KEY` fuera
  del allowlist, actualiza (o agrega) esas líneas en `.env` sin tocar el resto del
  archivo, y corre `docker compose --env-file .env up -d` (sin `--build`, ya que
  ningún código cambia). El allowlist en este script se mantiene sincronizado a mano
  con el registro de proveedores en código (no hay forma de compartir ese registro
  directamente con un script bash fuera del repo de Python) — ver Further Notes.

- **Variables involucradas hoy** (para el registro de proveedores inicial, deriva del
  `docker-compose.yml` actual):
  - AWS SNS: `AWS_SNS_SMS_ENABLED`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
    `AWS_REGION`.
  - LIWA: `LIWA_API_KEY`, `LIWA_ACCOUNT`, `LIWA_PASSWORD`, `LIWA_AUTH_URL`.
  - Twilio: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_MESSAGING_SERVICE_SID`.
  - SMTP: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`,
    `SMTP_USE_TLS`, `SMTP_USE_SSL`.
  - Explícitamente FUERA del allowlist: cualquier variable que no sea de un proveedor
    de notificación (`DATABASE_URL`, `SECRET_KEY`, `PG_PASSWORD`, `AWS_S3_*` —esas son
    del bucket de fotos, un proveedor distinto sin relación con notificaciones—,
    `WEB_ENV`, `PUBLIC_BASE_URL`, etc.).

## Testing Decisions

Un buen test acá ejercita comportamiento observable — nunca detalles internos de SSH
o de la tabla. Mismo criterio que ya usa el resto del dominio de notificaciones.

- `tests/data_model/test_proveedor_config_service.py` (nuevo) — habilitar/
  deshabilitar/reordenar contra una sesión de BD de test; verifica que el historial
  de auditoría queda una fila por cambio con el actor correcto; verifica que
  `usuario_id=None` es honesto cuando no hay actor (mismo criterio que
  `PlantillaNotificacionHistorial`).
- `tests/web/test_notifications.py`/equivalente de `otp.py` (extender): con la tabla
  sembrada en un orden distinto al de código, `_sender_base()`/`get_otp_sender()`
  arman la cadena en ESE orden — prueba que el refactor de verdad lee la BD y no dejó
  un fallback oculto a la constante vieja.
- `tests/data_model/test_sms_failover.py`: sin cambios — `construir_sender()` no
  cambió de forma, sus tests existentes siguen siendo la prueba de que el mecanismo
  de reintento en sí sigue intacto.
- `tests/web/test_admin_proveedores.py` (nuevo, Fase 1) — mismo patrón que
  `test_admin_notificaciones.py`: `_login_admin`/`_login_operador` (403 para
  operador), toggles de habilitado/orden vía POST, verifica que el HTML refleja el
  estado guardado.
- `tests/domain/test_deploy_ssh.py` o similar (nuevo, Fase 2) — `monkeypatch` sobre
  la librería SSH usada (ej. `paramiko`/`fabric`/`subprocess` según se elija en el
  ticket de implementación), verificando: (a) una `KEY` fuera del allowlist se
  rechaza ANTES de intentar conectar (nunca llega a la red); (b) un fallo de conexión
  o del comando remoto propaga una excepción clara; (c) el payload enviado por stdin
  tiene exactamente el formato `KEY=VALOR` esperado por el script remoto.
- `tests/web/test_admin_proveedores.py` (extender en Fase 2) — guardar un campo de
  credencial con la llamada SSH mockeada: éxito → confirma y queda en el historial
  (solo el nombre del campo); fallo → error visible, sin cambios en el historial ni
  en el estado "configurado" percibido.
- Prior art: `tests/data_model/test_notificacion_service.py` (patrón de service de
  dominio + historial), `tests/web/test_admin_notificaciones.py` (patrón de ruta
  admin con `require_admin` + historial), `tests/data_model/test_sms_failover.py` y
  `test_sns_sender.py`/`test_liwa_sender.py` (patrón de mockear el límite
  externo — acá el límite es SSH en vez de HTTP/boto3).

## Out of Scope

- **WhatsApp, Llamadas, o cualquier canal sin proveedor real hoy** — no aparecen en
  la pantalla hasta que exista un `Sender` real registrado en código (ver decisión de
  diseño explícita en Solution).
- **"Probar antes de guardar"** una credencial nueva sin aplicarla — se decidió
  reusar el botón "Enviar prueba" ya existente en `/administracion/notificaciones`
  DESPUÉS de guardar, en vez de construir un mecanismo de prueba en caliente aparte.
- **Selección de proveedor único sin failover** — el modelo sigue siendo la cadena
  configurable (habilitar varios + orden), nunca "elegir solo uno" excluyente.
- **Credenciales cifradas en base de datos** — decisión explícita de mantenerlas
  únicamente en `.env`, nunca duplicadas (cifradas o no) en la base de datos.
- **Disparar el cambio vía GitHub Actions/`workflow_dispatch`** — se descartó por el
  problema de que los inputs de un workflow quedan visibles en el log de la
  ejecución; el mecanismo elegido es SSH directo con una llave restringida.
- **Montar el socket de Docker dentro del contenedor de la app** — descartado por dar
  a la app una capacidad equivalente a root sobre el host; se prefirió una llave SSH
  acotada por `command=`.
- **Rate limiting o tope de costo por proveedor** (ej. alertar tras N usos de SNS) —
  no existe ese control hoy tampoco (ver mismo punto en
  `.scratch/sms-failover-twilio-sns/spec.md`); no se introduce aquí.
- **Reescribir o reemplazar el mecanismo de failover en sí** (`construir_sender()`,
  `FailoverSmsSender`) — esta feature solo cambia de dónde sale la lista de
  candidatos que ese mecanismo ya sabe procesar.
- **Gestión de qué IP/servidor recibe el SSH** — asume el único servidor de
  producción/staging actual (`test.papyrus.com.co`); no contempla múltiples entornos
  gestionables desde la misma pantalla.

## Further Notes

- **Motivación real, con evidencia concreta:** durante [[287]]/[[288]] (sesión del
  2026-09-01), confirmar y corregir la configuración de AWS SNS/LIWA/Twilio tomó
  decenas de comandos SSH manuales — incluyendo descubrir en vivo que LIWA está caído
  (timeout de conexión) y que Twilio responde 401 (credenciales inválidas/vencidas),
  sin ninguna forma de que el cliente lo hubiera visto por sí mismo ni de apagarlos
  temporalmente de la cadena sin pedir ayuda.
- **El script remoto del servidor vive fuera de este repo.** A diferencia del resto
  de esta feature (que vive en `PAQUETERIAv1.0`/`PaqueteXv.2` y se sincroniza al repo
  de deploy `jemavidev/PaqueteX`, ver `paquetex-v2-infra-topology` en memoria), el
  script bash + la configuración de `authorized_keys` con `command=` restringido se
  aprovisionan directamente en el servidor (Lightsail) — no hay un mecanismo hoy para
  desplegar eso vía git. Un ticket de la Fase 2 debe documentar ese script en algún
  lugar versionado igual (ej. `docs/` del repo, aunque no se "despliegue" desde ahí
  automáticamente) para que no quede como conocimiento tribal.
- **LIWA/Twilio caídos hoy (2026-09-01) son la motivación inmediata, no un blocker de
  este spec** — esta feature no los arregla, pero es la herramienta que permitiría
  deshabilitarlos de la cadena sin intervención manual la próxima vez que esto pase
  (ver issue [[288]] para el estado actual de esos dos proveedores).
- **Precedente de "orden de precedencia = constante fija"**: `.scratch/
  sms-failover-twilio-sns/spec.md` lo dejó fuera de alcance explícitamente citando "un
  slice futuro" — este spec es ese slice futuro.
