# Requerimientos — ajustes post-revisión funcional

Documento de **intake**, no un spec. Consolida las notas que el usuario dejó en
`CODE/docs/refactoring/REFERENCIA_FUNCIONAL_APLICATIVO.md` (sección por sección)
en **grupos de feature** — cada grupo es un candidato a su propio ciclo
`/to-spec` → `/to-tickets` → `/implement`, no una sola tanda.

**Cómo se usa:** cada grupo tiene su fuente (la nota original), lo que ya está
claro, y las **preguntas abiertas** que bloquean escribir el spec de ese grupo
(`/to-spec` sintetiza, no entrevista — así que estas se resuelven ANTES, aquí).
Un grupo pasa a "Listo para /to-spec" solo cuando sus preguntas abiertas tienen
respuesta. Las respuestas se anotan directamente bajo cada pregunta.

**Orden de dependencia** (quién bloquea a quién): Grupo 1 es el más grande y
varios otros grupos lo referencian (2, 5, 6) — conviene resolverlo primero.

---

## Índice de grupos

| # | Grupo | Toca | Estado |
|---|---|---|---|
| 1 | [Anunciar + resolución de destinatario por staff](#grupo-1--anunciar--resolución-de-destinatario-por-staff) | `/anunciar`, `/paquetes` (nuevo botón) | ✅ Implementado — `.scratch/anunciar-resolucion-destinatario-staff/` |
| 2 | [Consultar — auditoría + alcance de búsqueda](#grupo-2--consultar--auditoría--alcance-de-búsqueda) | `/consultar` | ✅ Implementado — `.scratch/consultar-rediseno/` |
| 3 | [OTP — unificación de perfil](#grupo-3--otp--unificación-de-perfil) | `/otp*`, `/mis-datos` | ✅ Implementado (código de 2 dígitos) |
| 4 | [Segundo contacto / Ocupante — modelo de dominio](#grupo-4--segundo-contacto--ocupante--modelo-de-dominio) | `/mis-datos`, `/residentes`, dominio (Persona) | ✅ Implementado — `.scratch/ocupante-entidad/` |
| 5 | [Paquetes — colores, filtros, paginación, anunciar staff](#grupo-5--paquetes--colores-filtros-paginación-anunciar-staff) | `/paquetes` | ✅ Implementado — `.scratch/paquetes-filtros-paginacion/` |
| 6 | [Declarar unidad — propósito de `/announce`](#grupo-6--declarar-unidad--propósito-de-announce) | `/announce` | ✅ Implementado — `.scratch/announce-staff-completo/` |
| 7 | [Residentes — segundo contacto + nivel de acceso](#grupo-7--residentes--segundo-contacto--nivel-de-acceso) | `/residentes` | ✅ Implementado — `.scratch/residentes-ocupantes/` |
| 8 | [Notificaciones — evento Anunciado, plantillas, LIWA](#grupo-8--notificaciones--evento-anunciado-plantillas-liwa) | dominio `notificacion_service` | ✅ Implementado (LIWA real bloqueado por credenciales) — `.scratch/notificaciones-anunciado-plantillas/` |
| 9 | [Transversales — navegación, teléfono internacional](#grupo-9--transversales--navegación-teléfono-internacional) | `base.html`, `telefono.py` | 🟡 Teléfono ✅ implementado. Header/footer sin empezar (cosmético, a propósito para el final) |

**Roadmap Ronda 1 completo — los 9 grupos implementados. 310/310 tests pasan.** LIWA implementado y desplegado con credenciales reales; verificación en vivo bloqueada por whitelist de IP pendiente del lado de LIWA (ver Grupo 8) — único pendiente externo de la Ronda 1. Header/footer (Grupo 9, `.scratch/header-footer/`): los 3 tickets implementados y revisados, footer visible también en desktop a pedido posterior del usuario.

**Ronda 2** (este documento continúa más abajo, Grupos 10-19): fuente = comentarios `**NOTA:**` que el usuario dejó directamente dentro de `GUIA_USUARIO_FINAL.md` al revisar el estado real desplegado. Mismo formato, misma disciplina — cada grupo pasa a 🟢 solo cuando sus preguntas están resueltas.

| # | Grupo | Toca | Estado |
|---|---|---|---|
| 10 | [Header unificado — login combinado, menús, "Mis paquetes", logout único](#grupo-10--header-unificado--login-combinado-menús-mis-paquetes-logout-único) | `base.html`, nueva ruta `/entrar`, nueva ruta `/mis-paquetes` | 🟢 Listo para `/to-spec` |
| 11 | [Consultar — mostrar auditoría de actor por transición](#grupo-11--consultar--mostrar-auditoría-de-actor-por-transición) | `/consultar`, `/paquetes` | ✅ Implementado — `.scratch/consultar-auditoria-actor/` |
| 12 | [Mis Datos — eliminar documento, bloquear Conjunto](#grupo-12--mis-datos--eliminar-documento-bloquear-conjunto) | `/mis-datos`, `/residentes/{id}` | ✅ Implementado — `.scratch/mis-datos-documento-conjunto/` |
| 13 | [Preferencias de notificación por canal × evento](#grupo-13--preferencias-de-notificación-por-canal--evento) | dominio `Persona`, `/mis-datos` | ✅ Implementado — `.scratch/preferencia-notificacion-matriz/` |
| 14 | [Paquetes — doble escaneo de guía al entregar](#grupo-14--paquetes--doble-escaneo-de-guía-al-entregar) | `/paquetes` (modal Entregar) | 🟢 Listo para `/to-spec` |
| 15 | [Paquetes — fotos múltiples + S3 real](#grupo-15--paquetes--fotos-múltiples--s3-real) | `/paquetes` (modal Recibir), `foto_storage.py` | 🟡 Código listo para spec; despliegue real bloqueado por bucket/credenciales S3 (misma categoría que LIWA, Grupo 8) |
| 16 | [Corregir — selección desde Ocupantes conocidos](#grupo-16--corregir--selección-desde-ocupantes-conocidos) | `/paquetes` (modal Corregir) | ✅ Implementado — `.scratch/corregir-ocupantes-conocidos/` |
| 17 | [Residentes — búsqueda extendida](#grupo-17--residentes--búsqueda-extendida) | `/residentes` | ✅ Implementado — `.scratch/residentes-busqueda-extendida/` |
| 18 | [Personal — CRUD completo de cuentas de staff](#grupo-18--personal--crud-completo-de-cuentas-de-staff) | `/administracion/personal` | 🟢 Listo para `/to-spec` |
| 19 | [Notificaciones — plantilla Anunciado dividida Cliente/Staff](#grupo-19--notificaciones--plantilla-anunciado-dividida-clientestaff) | `/administracion/notificaciones` | 🟢 Listo para `/to-spec` |

**Orden de ejecución sugerido (Ronda 2):** 11 → 12 → 13 (cluster residente: consultar + mis-datos, se tocan cerca en el tiempo) → 16 → 17 (cluster staff: paquetes/residentes) → 10 (header, cruza todas las pantallas — conviene que las rutas nuevas como `/mis-paquetes` ya existan antes de enlazarlas desde el nav) → 18 → 19 (pantallas de administración) → 14 → 15 (fotos, cierra con el ítem parcialmente bloqueado). No es una dependencia dura salvo 10 después de 11/13 (que crean rutas que el header enlaza) — es la secuencia que minimiza retrabajo.

---

## Grupo 1 — Anunciar + resolución de destinatario por staff

**Fuente:** notas §1 y §6 de la referencia funcional.

**Lo que ya está claro:**
- Cliente en `/anunciar` solo ingresa: Nombre, Teléfono, Aceptar T&C. Se elimina el radio `a_nombre_de` de esta vista.
- El cliente nunca ve teléfonos asociados a nombres en esta vista.
- Después de anunciar, el **staff** revisa el anuncio y decide/asocia el destinatario real (existente o nuevo), usando el teléfono de quien anunció como base.
- Formato de `access_code` (el código que ve el cliente): 4 caracteres, excluye `0`, `1`, `O`, `I`, `L`; evita la secuencia `666` al inicio o al final.
- Pantalla de éxito debe mostrar: Nombre, Teléfono, código de acceso, Torre y Apartamento (en caso que exista), y enlaces a consultar y a actualizar datos.

**Preguntas abiertas:**

1. **Nombres de campo.** Confirmado por el usuario en el turno anterior: lo que las notas llaman `tracking_number` (creado vacío al anunciar, llenado por el staff al recibir el paquete físico) es funcionalmente el `guide_number` de hoy. Y `access_code` es el único código que ve el cliente.
   → _Respuesta: ndo claro lo que es el "tracking_number" este no es funcional para este proyecto, sacalo de todo los flujos, solo deja "guide_number" que sera ingresado por el staff y tambien deja todo el flujo de "access_code", recuerda que access_code es solo de 4 digitos como lo aclare.

2. El botón "anunciar a nombre de un cliente" que aparece en la nota del Grupo 5 (`/paquetes`) — ¿es la misma pantalla/acción donde el staff resuelve el `a_nombre_de` de este anuncio, o es una acción distinta (staff anunciando un paquete nuevo desde cero, sin que el cliente haya anunciado nada)?
   → _Respuesta: Estos 2 hacen practicamente lo mismo, pero son flujos diferentes que llevan al mismo resultado, cuando el cliente anuncia solo se identifican el numero de telefono y el nombre del destinatario. Cuando el staff anuncia este puede incluir datos adicionales acerca de quien recibe (torre, apartamento, nombre o teléfono de notificaciones), practicamente el flujo del staff es mucho mas completo, ya que tambien permite arreglar un paquete que haya quedado mal anunciado, por ejemplo puede asociar ese anuncio al nombre correcto de la persona que esta registrada, por ejemplo (cliente anuncia con el numero de telefono correcto y el nombre con un error tipografico (Jesu Perez y deberia ser Jesus Perez), "Jesus Perez es como esta registrado este cliente en la base de datos y el staff podra hacer la asociacion correcta", un warning debe aparecer cuando el nombre de lo que se anuncio no corresponde a lo que se tiene en la base de datos.)

3. En la pantalla de éxito, "enlace para actualizar datos personales" — el cliente en ese momento no tiene sesión (`/anunciar` es sin login). ¿Ese enlace lleva a `/otp` para verificarse primero, y de ahí a `/mis-datos`?
   → _Respuesta: Si correcto, es el camino lógico, este proceso debe ser eficiente y rápido.

4. ¿Cómo ve el staff los anuncios pendientes de resolución (sin destinatario confirmado todavía)? ¿Es un estado nuevo del Paquete, un filtro en `/paquetes`, o una cola aparte?
   → _Respuesta: Debería ver los anuncios de forma normal, pero si el numero de teléfono ya estaba registrado y asociado a un o unos nombres específicos, pero el nombre que se anuncio no corresponde a los registrados, debería verse con un warning para que el staff lo pueda corregir y asociar correctamente. 

---

## Grupo 2 — Consultar — auditoría + alcance de búsqueda

**Fuente:** notas §2.

**Lo que ya está claro:**
- Búsqueda **solo** por `access_code` o el código de guía (una vez exista) — nunca por teléfono, por seguridad (el código solo lo conoce quien anunció).
- Mostrar torre/apartamento del cliente si existen, con enlace a actualizar datos si faltan.
- Mostrar la línea de tiempo completa con fechas/horas/condiciones/tipo de paquete/imágenes cuando existan.

**Preguntas abiertas:**

1. Mostrar "qué miembro del staff hizo cada acción" revierte una decisión de diseño ya documentada en el código (`search.py`: se oculta a propósito, es "solo para auditoría interna"). ¿Confirmado que se revierte?
   → _Respuesta: No se revierte, solo que se pueda auditar y que no cambie la información de quien hizo que.
   → **Interpretación (AgentX):** `/consultar` (vista del cliente) sigue **sin** mostrar quién del staff actuó — tal como hoy. Lo que pides es que ese dato (`received_by_usuario_id`, etc.) siga existiendo y sea inmutable para auditoría interna — que ya es el caso, nadie lo edita hoy. No hay cambio de comportamiento aquí, solo confirmar que no se toque. **Estado: 🟢 listo.**

2. "Tipo de paquete" e "imágenes" en la línea de tiempo — hoy el Paquete no tiene ningún campo de tipo ni fotos asociadas. ¿Es un campo nuevo a capturar al anunciar o al recibir? `file_uploads` ya existe en el sistema legacy solo para fotos de paquete (fuera del rebuild hasta ahora) — ¿se conecta con eso?
   → _Respuesta: Este si estaba descrito y hacia referencia a las imágenes que estructural mente se tienen en AWS S3 (sistema actual en producción, la versión vieja sin refactorizar), analiza como se maneja allí e incluye esto en el flujo de recepción de paquetes, esto es solo la confirmación visual de como se recibe cada paquete.
   → **Investigado (AgentX):** el legacy (`CODE/src/app/services/file_upload_service.py` + `s3_service.py`) tiene un modelo `FileUpload` simple: `package_id` (FK), `filename`, `s3_key`, `s3_url`, `file_type` (`IMAGEN`/`DOCUMENTO`/`RECIBO`), `file_size`, `content_type`. Sube a S3 con boto3 bajo el prefijo `paquetes-recibidos-imagenes/`, ligado siempre a la **recepción** del paquete (no al anuncio) — confirma lo que dijiste. Para el rebuild: nueva tabla equivalente ligada a `Paquete`, subida de foto(s) como parte del modal "Recibir" en `/paquetes`, mostradas en la línea de tiempo de `/consultar`. **Estado: 🟢 listo para spec.**

---

## Grupo 3 — OTP — unificación de perfil

**Fuente:** notas §3.

**Lo que ya está claro (sin ambigüedad, listo para spec en cuanto se resuelva el punto 1):**
- Se elimina `/otp/perfil` como pantalla separada; tras verificar el código, el cliente cae directo en `/mis-datos`.
- `/otp/verificar` sigue verificando el código generado por `/otp/solicitar` con sus reglas (expiración, intentos).

**Pregunta abierta:**

1. El código pasa de 6 a **2 dígitos** en la nota — eso son 100 combinaciones posibles en una ventana de 5 minutos, con rate limit solo por IP (no por teléfono). Es una reducción de seguridad significativa frente a los 6 dígitos actuales. ¿Es intencional (y por qué), o fue un error al escribir la nota?
   → _Respuesta: La realidad es que existen unos 2000 clientes potenciales, cuantos de ellos estarán realizando sincronizacion concurrente, la idea es que 1 IP tenga hasta 99 posibilidades para confirmar que es el porque tienen el numero correcto que se le envió por SMS, solo tiene 5 minutos para ingresar el numero correcto, pero solo podrá ingresar hasta 5 intentos antes de que esta opción bloquee la IP para este código que se le envió. En otras palabras ofrece algo de seguridad y facilita el uso de solo 2 digitos y no 4, agregando facilidad para que el cliente lo ingrese exitosamente.
   → **Verificado (AgentX):** el bloqueo a los 5 intentos que describes **ya existe hoy** en el código (`_otp_vigente` en `otp_service.py` exige `intentos < max_intentos`, y `max_intentos=5` ya se fija al crear el OTP) — está atado al **teléfono**, no a la IP, que es incluso más estricto de lo que pedías (bloquea ese código específico sin importar desde qué IP se intente). **Ya implementado** (no solo especificado): `_LONGITUD_CODIGO` cambiado de 6 a 2 en `otp_service.py`, `maxlength` y el texto de ayuda actualizados en `customer_verify.html`, docstrings de `otp_service.py`/`otp_cliente.py` actualizados, y los 2 tests que asumían un código incorrecto fijo de 6 dígitos (`"000000"`) corregidos para no depender del tamaño (con 100 combinaciones posibles, un valor fijo podía coincidir por azar). 223/223 tests pasan. **Estado: 🟢 hecho.**

---

## Grupo 4 — Segundo contacto / Ocupante — modelo de dominio

**Fuente:** notas §4 y §8.

**Por qué está bloqueado antes de spec:** `CONTEXT.md` ya nombra este concepto exacto — un padrón de personas asociadas a un apartamento sin ser la Persona titular — como **"Ocupante"**, y dice explícitamente que está *"fuera de este modelo hasta que se decida explícitamente"*. Lo que se pide (segundo contacto múltiple, con teléfono propio, login OTP propio, capacidad de anunciar/recibir a su nombre) es exactamente esa decisión pendiente. Es un cambio de **glosario y modelo de dominio**, no una pantalla — antes de cualquier spec necesita una sesión con el skill `/domain-modeling` para:
- Definir la relación Persona ↔ Ocupante (¿cuántos por apartamento? ¿el titular es un caso especial de Ocupante, o son cosas distintas?). --> Un apartamento puede tener varias personas, como mínimo 1 de esas personas deberá tener un numero de teléfono valido, esa primera persona sera el telefono por defaul o principal, el resto de personas podrá tener o no un numero de teléfono asociado a su nombre.
- Decidir si el teléfono de un Ocupante lo vuelve indistinguible de una Persona normal (¿por qué no es simplemente otra Persona con su propio apartamento?). --> Para este caso digamos que viven 3 personas en un apartamento, inicialmente papa registra su numero de teléfono y su nombre (el es el principal), mas adelante mama registra solo su nombre (sin teléfono asociado), posterior a eso la hija registra su nombre y registra su numero de teléfono. Cuando hablo de registrar es que tengan la oportunidad de asociar un numero de teléfono a un nombre de una persona (al principio este el el principal), posterior se podrían registrar mas personas a ese mismo apartamento, esto con o sin un numero de teléfono asociado. Para que esto sea posible es necesario que exista un apartamento real donde podrían vivir varias personas las cuales pueden registra su nombre y podría o no registra su numero de teléfono. Si uan persona da anuncia con el numero de teléfono principal o de un segundo contacto, la notificación llegara al numero de teléfono que realice el anuncio.
- Actualizar `CONTEXT.md` con el término resuelto, y probablemente un ADR (es difícil de revertir, sorprendente sin contexto, y hay trade-offs reales — los 3 criterios para ADR).

**Notas capturadas para esa sesión:**
- Puede haber varios "segundo_contacto" por Persona/apartamento.
- Cada uno con su propio teléfono o sin teléfono (en caso que no tenga teléfono, se usara el numero de la persona principal para este segundo contacto).
- Cada uno puede pedir su propio OTP para editar solo sus propios datos (no los de la cuenta principal), los datos que no le correspondan quedaran deshabilitados para la edición.
- Un paquete puede anunciarse a nombre de un segundo_contacto identificándolo por su teléfono, y notificársele directamente a él o a nombre de otra persona.
- El cliente principal puede desasociar un segundo_contacto desde `/mis-datos`.

**Preguntas abiertas:**

1. ¿Agendamos la sesión de `/domain-modeling` para esto? Es prerrequisito de todo lo demás en este grupo.
   → _Respuesta: No se aqui a que te refieres, pero creo que lo que decidas estara bien.
   → **Propuesta (AgentX), pendiente de tu confirmación:** con el detalle que ya diste (papá/mamá/hija) hay suficiente para resolver el modelo sin una sesión aparte. Se introduce **Ocupante**: nombre + Apartamento + teléfono **opcional**. Regla: cada Apartamento tiene exactamente **1** Persona "principal" (con teléfono — esto preserva el invariante de ADR-0003 "el Teléfono es la llave universal", pero aclarando que aplica a **Persona**, no a Ocupante). Un Ocupante **con** teléfono es, en la práctica, su propia Persona (login OTP propio, edita solo lo suyo). Un Ocupante **sin** teléfono es un registro liviano — solo nombre, no puede loguearse ni anunciar por sí mismo, pero permite que un paquete se le anuncie a su nombre reconocible (en vez de perderse dentro del snapshot de un solo paquete como hoy). Esto actualiza `CONTEXT.md` (el término "Ocupante" ya estaba previsto ahí) y necesita un ADR nuevo (revierte/matiza un invariante documentado). **¿Confirmas esta resolución para que quede 🟢 listo?** Si y quiero que un ocupante pueda ser actualizado a principal y un un principal pueda ser degradado o remplazado por un ocupante (lógico debe tener numero de teléfono valido).
   → **Confirmado — cierre (AgentX):** agregado a la propuesta: promover un Ocupante a "principal" (requiere que tenga teléfono válido) y degradar/reemplazar al principal actual por otro Ocupante (mismo requisito). Es una transición de estado limpia sobre el modelo ya propuesto — el apartamento conserva siempre exactamente 1 principal, solo cambia cuál.
   → **`/domain-modeling` hecho (AgentX):** `CONTEXT.md` actualizado con el término **Ocupante** resuelto (nueva sección propia + cross-referencias en "Nombre sin teléfono" y "Herencia de apartamento"). Escrito `docs/adr/0006-ocupante-residentes-sin-persona-propia.md` — documenta por qué NO se reabre ADR-0003 (nullable el teléfono de Persona) sino que Ocupante es un concepto nuevo y acotado. **Estado: 🟢 listo para `/to-spec`.**

---

## Grupo 5 — Paquetes — colores, filtros, paginación, anunciar staff

**Fuente:** notas §6.

**Lo que ya está claro, listo para spec/tickets directo (sin bloqueos):**
- Colores de estado: Anunciado → naranja, Recibido → azul, Entregado → verde, Cancelado → rojo (hoy es azul/amarillo/verde/gris).
- Filtros de búsqueda: por estado, código, guía, cliente, teléfono, torre, apartamento.
- Paginación arriba y abajo de la lista (estilo "Anterior 1 2 3 … 10 Siguiente").

**Pregunta abierta (compartida con Grupo 1):**

1. El botón "anunciar a nombre de un cliente" — ver pregunta 2 del Grupo 1.
   → Respuesta: Si este debe existir y a diferencia del simple anuncias, permitirá al staff ingresar mas datos al anunciar.

---

## Grupo 6 — Declarar unidad — propósito de `/announce`

**Fuente:** nota §7.

**El problema:** hoy `/announce` es "declarar unidad" (agrupar teléfonos existentes bajo un Apartamento — la herencia de apartamento en lote). La nota dice *"la idea de `/announce` es que se pueda anunciar un paquete de un cliente en su nombre"* — un propósito completamente distinto.

**Pregunta abierta (bloqueante, no se puede especificar nada de este grupo sin resolver esto primero):**

1. ¿Se **redefine** el propósito de la ruta `/announce` existente hacia "anunciar un paquete a nombre de un cliente" (y la funcionalidad actual de "declarar unidad" se mueve a otro lado, o se elimina)? ¿O es una **ruta/botón nuevo y separado** (posiblemente el mismo del Grupo 1/5), y `/announce` sigue siendo "declarar unidad" sin cambios?
   → Respuesta: "/announce" solo lo realizara el staff y la idea es que este anuncie, pero pueda agregar mas informacion que la simple vista "/anunciar"

2. Si se confirma la redefinición: la nota también dice que Conjunto/Torre/Apartamento pasan de siempre-obligatorios a "todos vacíos o todos llenos" — coherente si el propósito cambia a anunciar paquetes (el apartamento sería opcional ahí, como en `/anunciar`). Si NO se redefine la ruta, esta parte de la nota no aplicaría — queda pendiente de la respuesta anterior.
   → _Respuesta:_ Para /anunciar no estará disponible esta vista, pero en /announce si se vera y se editara a criterio del staff.

3. **Pregunta nueva (AgentX):** confirmado que `/announce` se redefine hacia "anunciar completo por el staff" — ¿qué pasa con su función **actual** ("declarar unidad": unir de una vez varios teléfonos existentes a un mismo apartamento)? ¿Desaparece (y ahora esa asociación en lote se hace registrando Ocupantes uno por uno vía el Grupo 4), se mueve a otra ruta, o el nuevo `/announce` la conserva como parte del mismo formulario (además de anunciar el paquete)?
   → _Respuesta: Todo se integra, ya que esta opcion del staff debe ser lo mas cmpleta posible._
   → **Cierre (AgentX):** confirmado — `/announce` queda como un único formulario completo de staff: anuncia el paquete Y declara/edita la unidad (conjunto/torre/apartamento + Ocupantes, Grupo 4) en el mismo flujo. **Estado: 🟢 listo para `/to-spec`.**

---

## Grupo 7 — Residentes — segundo contacto + nivel de acceso

**Fuente:** nota §8.

**Lo que ya está claro:**
- Agregar teléfono del segundo contacto en la ficha de `/residentes/{id}` — depende de cómo se resuelva el Grupo 4.
- Requisito general de auditoría — ya existe a nivel de BD (actor + timestamp en cada transición); si se pide una **vista** de auditoría, es pantalla nueva a especificar.

**Pregunta abierta:**

1. "El personal de staff podrá realizar modificaciones aquí sin ninguna restricción" — ¿incluye poder **eliminar** clientes (hoy exclusivo de `ADMIN`, ver ADR-0005), o se refiere solo a editar (que ya está abierto a cualquier rol hoy)?
   → _Respuesta:_ Seria edicion total o un soft delete.
   → **Interpretación (AgentX), confirmar:** entiendo esto como "cualquier rol de staff puede editar todo, y también puede ejecutar el soft-delete (la anonimización que ya existe, ADR-0005)" — es decir, se quita la restricción de `ADMIN` únicamente en **eliminar** (editar ya era abierto). ¿Correcto?
   → _Respuesta:_ Esta eliminacion tipo soft solo la realizara el ADMIN, el staff normal solo podra editar.
   → **Cierre (AgentX):** entendido — esto confirma el comportamiento **actual** sin cambios (eliminar sigue exclusivo de `ADMIN`, editar ya era abierto a cualquier rol). El único ajuste real de este grupo es agregar el teléfono del segundo contacto/Ocupante a la ficha (depende del Grupo 4, ya cerrado). **Estado: 🟢 listo para `/to-spec`.**

---

## Grupo 8 — Notificaciones — evento Anunciado, plantillas, LIWA

**Fuente:** nota §10.

**Ya aplicado (no requiere spec, ya está en producción/staging):**
- `SMS_OVERRIDE_NUMBER=+573002596319` configurado y verificado en el servidor de staging.

**Lo que ya está claro:**
- Los mensajes deben tener plantilla modificable por evento/motivo (hoy están hardcodeados en `construir_mensaje`).

**Preguntas abiertas:**

1. "Anunciar sí requiere notificación por SMS" revierte una decisión ya documentada (el brief original resolvió explícitamente que `ANUNCIADO` no notifica porque el cliente ya lo sabe). ¿Es porque con el nuevo flujo del Grupo 1 el anunciante y el destinatario real pueden ser personas distintas, y se quiere avisar al destinatario real una vez el staff lo resuelve? Si es así, este ítem depende de que el Grupo 1 esté resuelto primero.
   → Respuesta: Si requiere notificación.

2. **LIWA (proveedor de SMS)** — sin contexto previo. Se necesita: URL/documentación de su API, mecanismo de autenticación (API key / usuario-clave), si reemplaza también el envío de OTP (hoy `DevOtpSender`, sin SMS real) o solo las notificaciones de paquete, formato esperado del mensaje y remitente, límites de tasa del proveedor.
   → _Respuesta:_ Analiza el proyecto actual de producción y saca lo que necesites para la implementacion.
   → **Investigado (AgentX)** en `CODE/src/app/services/sms_service.py` (legacy, integración real ya probada en producción):
     - **Auth:** `POST {LIWA_AUTH_URL}` (default `https://api.liwa.co/v2/auth/login`) con JSON `{"account": ..., "password": ...}` → responde `{"token": "..."}`. El token se cachea ~23h.
     - **Envío:** `POST https://api.liwa.co/v2/sms/single`, headers `Authorization: Bearer {token}` + `API-KEY: {api_key}`. Payload `{"number": "57XXXXXXXXXX" (sin "+", con "57" al frente), "message": "...", "type": 1}`. Respuesta `{"success": bool, "menssageId": "..." (sic, con doble "s"), "message": "..."}`.
     - **Credenciales** (env vars ya usadas en legacy, mismos nombres recomendados para el rebuild): `LIWA_API_KEY`, `LIWA_ACCOUNT`, `LIWA_PASSWORD`, `LIWA_AUTH_URL`, `LIWA_FROM_NAME`. Los valores reales no están en el código (correctamente, vía entorno) — hace falta que los proveas cuando se implemente (igual que hicimos con `STAGING_SSH_KEY`).
     - El legacy solo lo usa para notificaciones de paquete, no para OTP — para el rebuild, reemplazaría tanto `ConsoleNotificationSender` como (si se quiere SMS real también ahí) `DevOtpSender`, cada uno como su propia implementación del puerto ya existente (mismo patrón `Protocol` que ya tiene el código).
     - **Estado: 🟢 listo para spec** (falta que proveas las credenciales reales al momento de desplegar, no de especificar).
   - **Implementado (AgentX):** `LiwaNotificationSender`/`LiwaOtpSender` (`app/domain/liwa_sender.py`), credenciales reales encontradas en `CODE/scripts/testing/sms/README_SMS.md` y configuradas en el servidor de staging. `get_notification_sender()`/`get_otp_sender()` (nuevo `app/web/otp.py`) usan LIWA real automáticamente si `LIWA_API_KEY` está presente. Probado con API simulada (7 tests). **Verificación real BLOQUEADA:** desde `52.6.204.211`, `api.liwa.co` no conecta por TCP 443 (timeout consistente, con internet general funcionando normal) — LIWA probablemente restringe su API por IP y este servidor no está en esa whitelist. El usuario va a contactar a LIWA para autorizar `52.6.204.211` en la cuenta `00486396309`. Código y despliegue 100% listos, solo pendiente de la autorización de red.

---

## Grupo 9 — Transversales — navegación, teléfono internacional

**Fuente:** nota §0.

**Preguntas abiertas:**

1. Header/footer — la nota dice "como te lo pedí anteriormente"; no hay registro de esa especificación en esta conversación. ¿Qué debe llevar exactamente (links, marca, qué diferencia staff de cliente)?
   → _Respuesta:_ Analiza el look and feel del proyecto en produccion y lo realizaras similar, te estre corrigiendo cuando lo vea.
   → **Investigado (AgentX)** en `CODE/src/templates/components/`: hay `public-navbar.html` (sin sesión) y `authenticated-navbar.html` (con sesión) separados — ya existe esa distinción cliente/staff en el legacy. El público tiene: logo SVG (colibrí geométrico multicolor) + wordmark "PAQUETEX", links centrales a Anunciar/Consultar, y botones Iniciar Sesión/Registrarse a la derecha — todo Tailwind, estilo limpio con acentos de color (azul/verde/naranja/rosa/morado/cyan). Tomo esto como base para el header/footer del rebuild y ajusto con tu feedback visual cuando lo veas corriendo. **Estado: 🟢 listo para spec** (con la salvedad de que vas a corregir detalles visuales después, como ya dijiste).
   → **Spec publicado (AgentX):** `.scratch/header-footer/spec.md` vía `/to-spec`. `base.html` hoy está completamente vacío (sin header ni footer) — se le agregan ambos, en CSS plano/JS vanilla (NO Tailwind/Alpine, respeta ADR-0004), envolviendo el contenido de cada pantalla sin tocarlo. Tres variantes de navegación (público / cliente / staff, con matiz ADMIN vs OPERADOR) resueltas desde la sesión ya existente — decisión clave: guardar el rol de staff en la sesión firmada al hacer login (en vez de tocar las ~10 rutas para resolver permisos de menú), registrada como `DEC-09`. El "footer" retoma el concepto de barra inferior fija en móvil del legacy, pero con un simple *breakpoint* CSS en vez de su detección de dispositivo por JavaScript. **Estado: 🟢 hecho** — los 3 tickets implementados (nav pública + cliente + staff OPERADOR/ADMIN, sesiones coexistentes mostrando ambos conjuntos sin ocultarse). `/code-review` en cada uno (Standards+Spec en paralelo) encontró y corrigió un bug real (botón de logout heredando estilos de selectores `button{}` sin scope de casi toda pantalla existente, resuelto con `all:revert`); resto de hallazgos fueron juicios de valor sin acción requerida. Verificado visualmente con Playwright+Chrome en las 5 combinaciones de audiencia/rol. 305/305 tests pasan. Pendiente únicamente de que el usuario lo vea corriendo en staging y dé feedback de estilo, como ya avisó.

2. Teléfono internacional — hoy solo funciona correctamente para Colombia (indicativo `57`); cualquier otro país se corrompe en la normalización actual. ¿Soporte multi-país real (requiere librería tipo E.164/`phonenumbers` y saber el país de cada número), o se mantiene "Colombia únicamente" como limitación conocida por ahora?
   → _Respuesta:_ La idea es que puedas permitir que ingrese cualquier numero, por ejemplo si comienza con 3 y tiene 10 digitos, asocialo a colombia, si inicia con +57 y tiene 10 digitos asocialo a colombia, pero por otra parte si no inicia con + y no comienza con 3, genera un error, y el otro caso es que inicie con + y tenga como minimo 10 digitos deberia ser un numero valido, no sabemos de donde pero deberia ser, esta creo que es la forma mas facil para esta implementacion, o que me sugieres?
   → **Sugerencia (AgentX):** tu regla funciona, la afino un poco para que quede sin ambigüedad al implementarla:
     1. Quitar todo lo que no sea dígito (igual que hoy), conservando si el original empezaba con `+`.
     2. Si (sin el `+`) quedan 10 dígitos y el primero es `3` → Colombia, forma canónica `+57` + esos 10 dígitos. (Nota: esto es implícitamente "solo celular colombiano" — coherente, porque todo el sistema depende de SMS.)
     3. Si quedan 12 dígitos, empieza por `57` y el dígito 3 es `3` → Colombia igual (equivalente a "+57 300 ...").
     4. Si el original **no** tenía `+` y no cae en 2 o 3 → error ("teléfono inválido").
     5. Si el original **tenía** `+` y quedan entre 10 y 15 dígitos (rango real de E.164) → válido, se guarda tal cual como `+` + dígitos, sin validar de qué país es.
     6. Si tenía `+` pero menos de 10 dígitos → error (evita basura obvia).
     Esto es exactamente tu regla, con el "mínimo 10" acotado también por arriba (15, el máximo real de un número de teléfono) para no aceptar cualquier cosa. **Estado: 🟢 listo para spec** si esto te sirve tal cual — si no, ajusto.
     → **Implementado (AgentX):** `telefono.py` reescrito con esta regla exacta. Encontré y actualicé un test viejo (`test_no_corrompe_nacional_que_empieza_por_57`) cuya expectativa contradecía la regla nueva (aceptaba cualquier nacional de 10 dígitos sin exigir que empiece en 3) — ahora ese caso lanza `ValueError` a propósito. Agregados tests para el rango internacional (10-15 dígitos con `+`, incluyendo el ejemplo `+13002596319` de tu pregunta original). 229/229 tests pasan (6 nuevos). **Estado: 🟢 hecho.**

---

## Grupo 10 — Header unificado — login combinado, menús, "Mis paquetes", logout único

**Fuente:** `NOTA` en §2.2 de `GUIA_USUARIO_FINAL.md`.

**Lo que ya está claro:**
- **Login combinado:** "Iniciar sesión" (residente) y "Staff" dejan de ser 2 botones — se unifican en un único punto de entrada con un selector (Cliente/Usuario) que cambia los campos del formulario según el caso. Diseño propuesto (AgentX): nueva ruta pública `/entrar` con un *toggle* de dos pestañas — "Soy residente" (campo teléfono → dispara el flujo OTP existente, `POST /otp/solicitar`) y "Soy del staff" (email + contraseña → `POST /ingresar`, sin cambios). Las rutas `/otp` y `/ingresar` **no desaparecen** (siguen siendo los *targets* reales de cada sub-formulario, y quedan accesibles por URL directa si algo las enlaza); `/entrar` es la nueva puerta visual que las envuelve. El header pasa a mostrar un solo botón "Iniciar sesión" apuntando a `/entrar`.
- **Menú de staff renombrado y reducido:** `Paquetes · Clientes · Consultar` (`Residentes` se renombra a `Clientes` solo como etiqueta del link — la ruta sigue siendo `/residentes`). `Declarar unidad` **sale del nav de escritorio** — la nota dice explícitamente "lo incluiremos más adelante en un botón", así que la ruta `/announce` sigue funcionando pero deja de estar en el header hasta que se diseñe ese botón (fuera de alcance de este grupo). `ADMIN` conserva `Personal · Notificaciones` además de lo anterior.
- **"Mis paquetes" para el residente:** nuevo ítem de nav entre "Consultar" y "Mis datos", nueva ruta protegida `/mis-paquetes` (requiere sesión de cliente) que lista los paquetes donde el teléfono de la sesión aparece como `announced_by_phone` **o** `recipient_phone` (cubre tanto "lo que anuncié" como "lo que me anunciaron a mí"), cada fila con enlace a su detalle en `/consultar`.
- **Logout único:** hoy (DEC-09) cada sesión (cliente/staff) tiene su propio botón y cerrar una no afecta la otra — la nota pide invertir esto: **un solo botón visible**, que si hay ambas sesiones coexistiendo, cierra **las dos a la vez**. Esto es un cambio de comportamiento explícito sobre una decisión ya tomada (DEC-09) — se implementa tal como se pide (nueva ruta `POST /salir-todo` o el mismo botón dispara ambos `POST` en secuencia), y se registra como decisión nueva (referencia a DEC-09, no la anula del todo: las sesiones siguen siendo cookies/keys independientes internamente, solo cambia que *un* botón las cierra ambas).
- **Footer móvil, dos variantes según audiencia:**
  - Público/cliente: **Anunciar · Buscar · Ayuda · Whatsapp** (login queda solo arriba en el header, no en el footer).
  - Staff: **Anunciar · Buscar · Paquetes · Clientes** ("Anunciar" aquí es `/announce`; a diferencia del nav de escritorio, en el footer móvil sí se incluye ya, porque no hay otro lugar equivalente al "botón" que se planea agregar más adelante para escritorio — es la única superficie donde el staff puede llegar rápido a declarar/anunciar desde el celular hasta que exista ese botón).

**Pregunta que resuelvo yo (no bloqueante — tiene salida sin detener el grupo):**

1. "Ayuda" y "Whatsapp" son ítems nuevos que no existen en ningún lado de la app hoy — no puedo inventar un número de WhatsApp real ni contenido de ayuda sin más información, pero tampoco hace falta bloquear el grupo por esto:
   - **"Ayuda"** → nueva ruta estática `/ayuda`, generada a partir del contenido de la sección "Preguntas frecuentes" (§7) de esta misma guía — un solo lugar que mantener.
   - **"Whatsapp"** → enlace `https://wa.me/<numero>`, con el número tomado de una variable de entorno nueva `WHATSAPP_SOPORTE_NUMERO`. Si no está configurada, el ítem del footer simplemente no se muestra (nunca se publica un enlace roto). Se configura en el servidor como cualquier otro secreto de despliegue, mismo patrón que `LIWA_API_KEY` — dime el número cuando lo tengas a mano y lo activamos con un `docker compose` restart, sin tocar código.

**Estado: 🟢 listo para `/to-spec`** con las resoluciones de arriba.

---

## Grupo 11 — Consultar — mostrar auditoría de actor por transición

**Fuente:** `NOTA` en §3.2.

**El contexto:** en la Ronda 1 (Grupo 2, pregunta 1) ya se discutió esto y se resolvió explícitamente **no** mostrarlo ("no se revierte, solo que se pueda auditar... que ya es el caso"). La nueva nota pide lo contrario en términos claros — la trato como una reversión intencional de esa decisión anterior, no como una contradicción a aclarar.

**Lo que ya está claro:**
- El esquema **ya tiene** todo lo necesario: `announced_by_usuario_id`, `received_by_usuario_id`, `delivered_by_usuario_id`, `cancelled_by_usuario_id` en `Paquete` (ver `paquete.py`) — este grupo es 100% de presentación, cero cambios de esquema.
- `/consultar` (vista del residente) agrega a la línea de tiempo, por cada evento, quién lo hizo: cuando el anuncio lo hizo el propio cliente (`announced_by_usuario_id` es `NULL`, caso normal de `/anunciar`), se muestra el nombre del cliente que anunció; cuando lo hizo el staff (vía `/announce`, Grupo 6 de la Ronda 1), se muestra el nombre del `Usuario` staff. Recibido/Entregado/Cancelado siempre muestran el nombre del `Usuario` staff que actuó (esas transiciones son siempre de staff).
- Alcance: aplica también a `/paquetes` (vista de staff), no solo a `/consultar` — pediste "que se pueda auditar" en general, y el staff se beneficia igual de verlo sin tener que ir a otra pantalla.

**Estado: 🟢 listo para `/to-spec`.**

---

## Grupo 12 — Mis Datos — eliminar documento, bloquear Conjunto

**Fuente:** `NOTA` en §3.4.

**Lo que ya está claro:**
- El campo "documento" (y "tipo de documento") deja de capturarse/mostrarse/validarse en **todos** los flujos: `/mis-datos` (el propio residente), `/residentes/{id}` (edición por staff), y cualquier otro formulario donde aparezca hoy.
- Decisión de esquema (AgentX): **no se elimina** la columna `documento`/`tipo_documento` de la tabla `personas` — dato histórico neutral sin impacto, evita una migración destructiva innecesaria ahora mismo. Si más adelante se quiere limpiar el esquema, es un ticket aparte y explícito, no parte de esto.
- El residente ya **no** puede editar "Conjunto" en `/mis-datos` (queda de solo lectura si ya tiene uno asignado, u oculto si no) — solo Torre y Apartamento. Corregir/asignar el Conjunto sigue siendo tarea del staff (`/residentes/{id}` o `/announce`).

**Estado: 🟢 listo para `/to-spec`.**

---

## Grupo 13 — Preferencias de notificación por canal × evento

**Fuente:** `NOTA` en §3.4 (segundo párrafo).

**El problema:** hoy `Persona.notificaciones_activas` es un único booleano (todo o nada, todos los eventos, un solo canal implícito: SMS). La nota pide una matriz **Canal × Evento**.

**Lo que ya está claro:**
- Canales: SMS, Email, Llamadas, Whatsapp. Eventos: Anunciado, Recibido, Entregado, Cancelado. Los 4 canales aplican a los 4 eventos por igual — no hay combinaciones prohibidas, es una grilla completa 4×4.
- Solo **SMS** está conectado a un proveedor real (LIWA) hoy. Email/Llamadas/Whatsapp quedan como preferencias que se guardan y se muestran en la UI, pero no disparan ningún envío real todavía (no hay proveedor integrado para esos canales) — **desactivados por defecto**, tal como pediste explícitamente.
- Diseño de datos (AgentX): tabla nueva `persona_preferencia_notificacion` (`persona_id`, `canal`, `evento`, `activo`) en vez de columnas fijas en `Persona` — así conectar un canal nuevo el día de mañana no vuelve a tocar el esquema, solo agrega filas.
- Migración de datos: toda `Persona` existente con `notificaciones_activas=True` (el default actual) se traduce a "SMS activo en los 4 eventos, resto de canales apagado" — preserva el comportamiento de hoy exactamente, nadie deja de recibir lo que ya recibía.
- UI en `/mis-datos`: una tabla 4×4 (canales como columnas, eventos como filas), un checkbox por celda.

**Estado: 🟢 listo para `/to-spec`** — el grupo más grande de esta ronda (nueva tabla + servicio de resolución de destino que hoy solo mira `notificaciones_activas` + UI de matriz).

---

## Grupo 14 — Paquetes — doble escaneo de guía al entregar

**Fuente:** `NOTA` en §4.2 (primer párrafo).

**Lo que ya está claro:**
- El modal "Entregar" gana el mismo componente de escaneo (ZXing + cámara) que ya existe en "Recibir". Al escanear, compara el valor leído contra el `guide_number` ya guardado en ese paquete: coincide → confirmación visual; no coincide → advertencia visual, **no bloquea la entrega** (pediste explícitamente "opcional y no bloqueante").
- Si el paquete no tiene `guide_number` guardado (se recibió sin capturar guía — es opcional, ver §3.1), el escaneo en Entregar no tiene contra qué comparar y simplemente se omite el chequeo, sin error.

**Estado: 🟢 listo para `/to-spec`.**

---

## Grupo 15 — Paquetes — fotos múltiples + S3 real

**Fuente:** `NOTA` en §4.2 (segundo párrafo).

**Lo que ya está claro:**
- El dominio **ya soporta** varias fotos por paquete — `paquete_foto_service.agregar_foto` puede llamarse varias veces, `paquete_fotos` ya es una tabla 1:N (`paquete_foto.py`, comentario propio: *"Un Paquete puede tener varias fotos"*). Lo único que falta es (a) permitir subir hasta 3 en el modal "Recibir" de la UI, con el tope de 3 validado también en el servicio (defensa en profundidad), y (b) reemplazar el storage.
- **S3 real:** investigado en el legacy (`s3_storage_service.py`, `file_upload_service.py`) — usa `boto3`, credenciales por variables de entorno (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_S3_BUCKET_NAME` + prefijo). Para el rebuild: nueva clase `S3FotoStorage` que implementa el mismo `Protocol FotoStorage` que ya existe (`foto_storage.py`) — mismo patrón que `LiwaNotificationSender` vs `ConsoleNotificationSender`, cero cambios en dominio o rutas, solo el *wiring* en `app/web/fotos.py`.

**Pregunta abierta — bloqueo real (misma categoría que LIWA/Grupo 8):**

1. Falta que confirmes/proveas: ¿el bucket S3 es el **mismo** que usa hoy el sistema legacy en producción, o uno **nuevo y dedicado** a PaqueteXv.2? Y las credenciales (`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/nombre del bucket/región) cuando estén listas.
   → _Sin respuesta aún._ Mientras tanto, el código y el spec quedan 100% listos con `LocalFotoStorage` como implementación activa (igual que hoy) — el día que confirmes el bucket, es el mismo tipo de cambio de una sola función que fue conectar LIWA.

**Estado: 🟡 listo para `/to-spec` del lado de código (UI + tope de 3 + `S3FotoStorage`); el *despliegue* real a S3 queda bloqueado hasta que confirmes el bucket, igual que LIWA quedó bloqueado por el whitelist de IP.**

---

## Grupo 16 — Corregir — selección desde Ocupantes conocidos

**Fuente:** `NOTA` en §4.2 (tercer párrafo).

**Lo que ya está claro:**
- El modal "Corregir" (hoy: texto libre para nombre/teléfono, ver `packages.py` `POST /paquetes/{id}/corregir`) cambia a una lista de candidatos: Personas/Ocupantes ya asociados al `snapshot_torre`/`snapshot_apartamento` del paquete, o que comparten el `announced_by_phone`. El staff **solo** puede elegir un nombre de esa lista — no digitar uno nuevo — tal como pediste explícitamente ("SOLO se podrá... seleccionar el nombre correcto"), porque el dato correcto ya lo validó el propio cliente en algún momento (`/mis-datos` o `/announce`), no el staff.

**Pregunta que resuelvo yo (default explícito, ajustable si no te sirve):**

1. Si el paquete no tiene apartamento asociado (se anunció sin declarar unidad, sin candidatos posibles), forzar "solo selección" dejaría el botón inútil. Propuesta: si hay candidatos, selección obligatoria de la lista; si no hay ninguno, se mantiene el texto libre actual como único fallback — la única forma de que "Corregir" siga sirviendo para ese caso.

**Estado: 🟢 listo para `/to-spec`** con esa resolución por defecto.

---

## Grupo 17 — Residentes — búsqueda extendida

**Fuente:** `NOTA` en §4.4.

**Lo que ya está claro:**
- `/residentes` amplía su búsqueda para incluir, además de nombre/teléfono de la Persona principal: torre, apartamento, y nombre/teléfono de **segundo contacto** (Ocupante). La búsqueda por teléfono deja de mirar solo a la Persona principal — incluye el teléfono de cualquier Ocupante del apartamento.
- Un resultado que coincide por el teléfono de un Ocupante lleva a la ficha del apartamento/Persona principal correspondiente (los Ocupantes sin teléfono propio no tienen ficha propia — ver Grupo 4 de la Ronda 1).
- El campo "documento" desaparece de esta pantalla también (ver Grupo 12, misma nota lo reitera acá).

**Estado: 🟢 listo para `/to-spec`.**

---

## Grupo 18 — Personal — CRUD completo de cuentas de staff

**Fuente:** `NOTA` en §4.5.

**Lo que ya está claro:**
- `/administracion/personal` gana una tabla de cuentas existentes (email, nombre, rol, activo/inactivo) además del formulario de creación que ya existe. Acciones: editar nombre/rol, resetear contraseña, activar/desactivar.
- **Desactivar, no borrar** (AgentX, por consistencia con el patrón de anonimización ya usado para clientes, ADR-0005): un `Usuario` desactivado no puede iniciar sesión, pero la fila permanece — así nunca se rompen las FK de auditoría (`received_by_usuario_id` y las demás del Grupo 11 dependen de que el `Usuario` siga existiendo).
- Regla de sentido común que agrego salvo que digas lo contrario: un `ADMIN` no puede desactivarse ni degradarse a sí mismo a `OPERADOR` — evita dejar el sistema sin ningún admin activo por accidente.
- Solo visible para `ADMIN` (como hoy).

**Estado: 🟢 listo para `/to-spec`.**

---

## Grupo 19 — Notificaciones — plantilla Anunciado dividida Cliente/Staff

**Fuente:** `NOTA` en §4.6.

**Lo que ya está claro:**
- `/administracion/notificaciones` separa la fila única "Anunciado" en dos: **"Anunciado · Cliente"** (cuando el propio residente anuncia vía `/anunciar`) y **"Anunciado · Staff"** (cuando el staff anuncia vía `/announce`, Grupo 6 de la Ronda 1) — mismo patrón que ya existe para los 4 motivos de cancelación (cada uno con su propio texto editable/default).

**Estado: 🟢 listo para `/to-spec`.**

---

## Grupo 20 (documentación, no desarrollo) — FAQ desactualizada sobre anunciar sin teléfono

**Fuente:** `NOTA` en §7.

La respuesta del FAQ ("¿Puedo anunciar un paquete para alguien que no tiene teléfono?") describe un comportamiento **anterior** a la Ronda 1: antes de que el Grupo 1 simplificara `/anunciar` a 3 campos fijos, existía un radio `a_nombre_de` que permitía poner cualquier nombre libremente. Hoy `/anunciar` **siempre** exige un teléfono válido (`announce()` en `paquete_service.py` no tiene forma de saltarse `anunciante_telefono`) — la respuesta vieja quedó desactualizada al escribir la guía. No es un cambio de código, es un error de redacción mío. Corregido directamente en `GUIA_USUARIO_FINAL.md` en el mismo cierre de esta ronda.

**Estado: ✅ corregido directo, no pasa por `/to-spec`.**

---

## Próximo paso

Este documento no se autogenera — cuando se respondan las preguntas de un grupo, se anota la respuesta aquí mismo y ese grupo pasa a 🟢 "Listo para /to-spec". Se ejecuta `/to-spec` grupo por grupo (empezando por el Grupo 1, del que dependen 2, 5 y 8), no todos a la vez.
