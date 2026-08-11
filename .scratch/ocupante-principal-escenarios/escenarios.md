# Escenarios: Ocupante / Principal / Apartamento — comportamiento verificado en código

Generado 2026-08-10, contra `PaqueteXv.2` @ `f616308`. Cada escenario describe **lo que
el código hace HOY** (verificado leyendo `ocupante_service.py`, `apartamento_service.py`,
`paquete_service.py` y las 5 rutas web que tocan esto — no es una suposición), con la
cita `archivo:línea` para que puedas confirmarlo vos mismo. La idea es que anotes, en
cada `¿Debería ser así?`, si el comportamiento actual es el que querés o si hay que
cambiarlo — dejalo en blanco si ya está bien.

No adiviné nada: donde el comportamiento me pareció sorprendente o inconsistente entre
vistas, lo marqué explícito en vez de asumir que es un bug o que es intencional.

---

## Piezas de estado (glosario rápido, para que el documento se lea solo)

- **Persona**: un residente. Siempre tiene Teléfono, WhatsApp, o ambos (nunca ninguno).
- **Apartamento**: unidad del catálogo **cerrado** — 804 unidades reales, sembradas UNA
  vez por migración (`0021_seed_catalogo_apartamentos`). `resolver_apartamento` **ya no
  crea** unidades nuevas — una Torre+Apartamento que no está en el catálogo es error de
  uso (typo), no un caso a tolerar (`apartamento_service.py:53-56`).
- **Ocupante**: un residente reconocido de un Apartamento. Puede o no tener Persona
  propia (Teléfono/WhatsApp). Estados:
  - `pending` / `confirmado` (`confirmado_en`) — un sello administrativo, no bloquea
    funcionalidad (un pending puede anunciar/recibir igual).
  - `es_principal` — a lo sumo UNO por Apartamento (entre los activos), y ese principal
    **siempre** tiene Persona propia (garantizado por índice único parcial en BD).
- **Regla nuclear** (`ocupante_service.py:22-34`, `530-579`): TODO Ocupante nuevo nace
  `pending` y `es_principal=False`, **incluido el primero de una unidad vacía** — la
  promoción a principal **ya no es automática al crear**. Ocurre recién al **confirmar**
  (`confirmar_ocupante`), y solo si en ese momento la unidad todavía no tiene ningún
  principal. Sí se exige que el primer Ocupante de una unidad vacía tenga Teléfono o
  WhatsApp al **crearse** (si no, ni siquiera podría llegar a confirmarse después).

---

## Hallazgos transversales (aplican a varias vistas — leé esto primero)

**H1 — WhatsApp como identidad de un Ocupante nuevo: solo desde `/announce`.**
Los formularios de "agregar Ocupante" en `/residentes` (tab Residentes),
`/mis-datos` y `/paquetes` → Corregir destinatario → Nuevo ocupante **solo tienen campo
Teléfono** (`customers_manage.py:565`, `customer_verify.py` form, `packages.py:386`) —
ni el HTML ni la ruta aceptan `whatsapp_usuario`, aunque `agregar_ocupante` (dominio) lo
soporta perfectamente. Las ÚNICAS dos vías donde un Ocupante nuevo puede nacer
identificado por WhatsApp son `/announce` camino Teléfono/WhatsApp directo y `/announce`
Torre+Apto → "Nueva persona" (campo `contacto`, clasificado igual que el principal).
→ **¿Debería ser así?**

**H2 — No existe forma de asociar/editar un WhatsApp a un Ocupante ya existente.**
`asociar_telefono_a_ocupante`/`editar_telefono_ocupante` son estrictamente de Teléfono
en TODO el código — no hay un equivalente de WhatsApp en ningún lado de
`ocupante_service.py`. Si un Ocupante nace sin contacto (o solo con WhatsApp vía
`/announce`), no hay UI para después asociarle/cambiarle el WhatsApp — solo Teléfono.
→ **¿Debería ser así?**

**H3 — "Volverse principal" pasa al CONFIRMAR, no al crear — salvo en un lugar.**
La tab "Dirección" de `/residentes` (`reasignar_apartamento`,
`ocupante_service.py:655-715`) agrega **y** confirma en el mismo acto — ahí sí se ve
"automático" para el staff (un solo clic, la persona queda principal de inmediato si la
unidad estaba vacía). En las otras 3 vías (`/announce` Torre+Apto nueva persona,
tab Residentes, `/mis-datos`), confirmar es un paso manual aparte.
→ **¿Debería ser así?**

**H4 — `promover_a_principal` no exige que el Ocupante esté confirmado.**
Leyendo `ocupante_service.py:582-616`: solo exige `persona_id` no nulo y que no esté
dado de baja — no chequea `confirmado_en`. En teoría, un Ocupante `pending` podría
promoverse a principal directo por el botón "Promover", saltándose "Confirmar" por
completo (ese Ocupante quedaría `es_principal=True` pero `confirmado_en=None`).
→ **¿Debería ser así, o promover debería exigir estar confirmado primero?**

**H5 — Quién termina siendo principal depende de quién se CONFIRME primero, no de quién
se registró primero.**
Si una unidad tiene varios Ocupantes `pending` y ninguno confirmado todavía, el primero
en confirmarse (por cualquier vía: staff en tab Residentes, el propio autoservicio si
alguna vez llega a poder, etc.) se lleva la promoción — sin importar el orden en que se
crearon. Dos flujos que compiten por la misma unidad vacía pueden dar un resultado
distinto según cuál llegue primero a "Confirmar".
→ **¿Es el comportamiento esperado?**

**H6 — Un Ocupante puede quedar creado en la base aunque el staff vea un error.**
`get_db` (`db.py:30-39`) hace `commit()` al final de CUALQUIER request que no lance una
excepción — un `return` con una respuesta de error (400, etc.) cuenta como éxito para
esto. En `/announce` Torre+Apto → nueva persona (`announce_new.py:397-404`) y en
`/paquetes` → Corregir destinatario → nuevo ocupante (`packages.py:420-452`): si
`agregar_ocupante` tiene éxito pero el paso SIGUIENTE falla (no hay Anunciante
resolvible; o el paquete cambió de estado entre cargar la página y enviar el form), la
ruta devuelve un error **sin lanzar excepción** → el Ocupante nuevo queda persistido de
todos modos, aunque la acción visible (anunciar / corregir) haya fallado.
→ **¿Es aceptable, o debería revertirse la creación del Ocupante si el paso siguiente falla?**

---

## Vista 1 — `/announce` (staff), camino Teléfono/WhatsApp directo

Variables: ¿la Persona identificada por el tel/whatsapp tecleado ya existe? Si existe,
¿es Ocupante activo de algo? Si lo es, ¿vive sola o con más gente?

### 1.1 — No existe la Persona todavía
**Hoy:** se crea una Persona nueva (solo con el dato tecleado + nombre que el staff
escriba). Destinatario = Anunciante = ella misma (`Destinatario.yo_mismo()`). **Sin
apartamento** — este camino nunca toca Ocupante/Apartamento para nada
(`paquete_service.py:248-251`). — `announce_new.py:421-440`
**¿Debería ser así?**

### 1.2 — Existe, pero nunca fue Ocupante de ninguna unidad
**Hoy:** tarjeta directa "Ya registrado", Anunciante=Destinatario=ella misma, sin
apartamento (su `apartamento_actual_id` es `None`). — `announce_new.py:193-217`
**¿Debería ser así?**

### 1.3 — Existe, es Ocupante activo, pero vive SOLA (única activa de su unidad)
**Hoy:** igual que 1.2 pero CON apartamento en el snapshot (su propia unidad). El atajo
directo sigue aplicando — no se le pide elegir nada. — `announce_new.py:163-176, 200-213`
**¿Debería ser así?**

### 1.4 — Existe, es Ocupante activo de una unidad con MÁS de un residente activo
**Hoy:** NO aparece la tarjeta directa. En su lugar, la MISMA pantalla de unidad del
camino Torre+Apto, con esta persona marcada "Anunciante" en la lista. El staff debe
elegir a quién se anuncia:

**1.4.a — Elige un residente EXISTENTE de la lista** (puede ser ella misma u otro
Ocupante activo, confirmado o pending) → Destinatario = ese Ocupante. El Anunciante
**siempre** es quien tecleó el teléfono/whatsapp — nunca se resuelve por
`anunciante_para_ocupante` en este caso. — `announce_new.py:305-338`
**¿Debería ser así?**

**1.4.b — Crea un residente NUEVO en esa misma unidad** (nombre + contacto opcional,
que SÍ puede ser WhatsApp) → se agrega un Ocupante `pending` nuevo; como la unidad ya
tiene gente, un Ocupante nuevo SIN contacto es válido acá. Destinatario = ese nuevo
Ocupante, Anunciante = quien tecleó el tel/whatsapp igual. — `announce_new.py:357-365`
**¿Debería ser así?**

---

## Vista 1 (cont.) — `/announce`, camino Torre+Apartamento

Variables: ¿el código calza con el catálogo? Estado de la unidad (vacía / con gente sin
principal confirmado / con principal confirmado). ¿Elige existente o "Nueva persona"?
Si nueva persona, ¿trae contacto y de qué tipo?

### 2.1 — Código a medio teclear o inválido (no calza con ninguna unidad real)
**Hoy:** no aparece nada (`HTMLResponse("")`). — `announce_new.py:219-222`
**¿Debería ser así?**

### 2.2 — Unidad VACÍA + "Nueva persona" SIN contacto
**Hoy:** error explícito, nada se crea: "El primer Ocupante de un Apartamento debe
tener Teléfono o WhatsApp...". — `ocupante_service.py:419-424`
**¿Debería ser así?**

### 2.3 — Unidad VACÍA + "Nueva persona" CON teléfono
**Hoy:** se crea el Ocupante (`pending`, NO principal todavía — eso pasa recién al
confirmar) y se anuncia a su nombre. El Anunciante se resuelve como ella misma (tiene
Persona propia). — `announce_new.py:340-355`
**¿Debería ser así?**

### 2.4 — Unidad VACÍA + "Nueva persona" CON WhatsApp
**Hoy:** igual que 2.3, por WhatsApp.
**¿Debería ser así?**

### 2.5 — Unidad VACÍA + "Nueva persona" con contacto que no clasifica
(ni teléfono de 10 dígitos empezando en 3, ni ≥3 letras para WhatsApp)
**Hoy:** error explícito, nada se crea: "Ese contacto no parece un Teléfono ni un
usuario de WhatsApp válido...". — `announce_new.py:386-395`
**¿Debería ser así?**

### 2.6 — Unidad CON gente pero SIN principal confirmado + "Nueva persona" SIN contacto
**Hoy:** el Ocupante SÍ se crea (`pending`, sin contacto — válido porque la unidad ya
tiene gente). Pero al intentar anunciar, `anunciante_para_ocupante` no encuentra
Persona propia ni Principal confirmado → error: "Este residente no tiene Teléfono ni
WhatsApp propio, y la unidad todavía no tiene un Principal confirmado -- no se puede
anunciar todavía." **El Ocupante queda creado igual** (ver H6) aunque el paquete NUNCA
se anuncia. — `announce_new.py:340-346`
**¿Debería ser así?**

### 2.7 — Unidad CON gente pero SIN principal confirmado + elige un EXISTENTE sin Persona propia
**Hoy:** mismo error que 2.6 — no se puede anunciar.
**¿Debería ser así?**

### 2.8 — Unidad CON gente pero SIN principal confirmado + elige un EXISTENTE que SÍ tiene Persona propia
(aunque nadie de la unidad esté formalmente "confirmado")
**Hoy:** SÍ se puede anunciar — `anunciante_para_ocupante` encuentra su propia Persona
sin necesitar que sea principal ni que esté confirmado. — `ocupante_service.py:179-200`
**¿Debería ser así?**

### 2.9 — Unidad CON principal confirmado + elige un EXISTENTE sin Persona propia
**Hoy:** se anuncia a su nombre, el Anunciante cae al Principal de la unidad.
**¿Debería ser así?**

### 2.10 — Unidad CON principal confirmado + "Nueva persona" SIN contacto
**Hoy:** se crea el Ocupante nuevo (`pending`, sin contacto) y SÍ se puede anunciar de
una — el Anunciante cae al Principal.
**¿Debería ser así?**

### 2.11 — Unidad CON principal confirmado + "Nueva persona" CON contacto
**Hoy:** se crea con Persona propia, Anunciante = ella misma.
**¿Debería ser así?**

### 2.12 — El `ocupante_id` elegido ya no existe (carrera: se borró/cambió entre el GET y el POST)
**Hoy:** error "Ese residente ya no existe -- vuelve a buscar la unidad." —
`announce_new.py:360-362`
**¿Debería ser así?**

### 2.13 — Interacción entre los dos caminos: quién queda como Anunciante
Si se llegó a la pantalla de unidad DESDE Teléfono/WhatsApp con co-residentes (1.4), el
Anunciante queda fijo en esa persona pase lo que pase después. Si se llegó DIRECTO por
Torre+Apto, el Anunciante siempre se resuelve por `anunciante_para_ocupante` (nunca se
sabe con certeza quién llama por este camino). — docstring `announce_new.py:35-47`
**¿Debería ser así?**

---

## Vista 2 — `/residentes/{id}/apartamento` (staff, tab "Dirección") — `reasignar_apartamento`

Asocia/cambia/desvincula la Torre+Apartamento de una Persona **ya existente** (la que se
está viendo en esa ficha).

### 3.1 — Asignar vacío (desvincular) — era Ocupante NO-principal
**Hoy:** se da de baja sin problema. — `ocupante_service.py:700-706`
**¿Debería ser así?**

### 3.2 — Asignar vacío — era PRINCIPAL y único Ocupante activo de su unidad
**Hoy:** se da de baja sin problema, la unidad queda vacía.
**¿Debería ser así?**

### 3.3 — Asignar vacío — era PRINCIPAL pero quedan otros Ocupantes activos
**Hoy:** error: "El principal no puede darse de baja mientras existan otros Ocupantes
activos -- promové a alguno primero...". Nada cambia. — `ocupante_service.py:486-501`
**¿Debería ser así?**

### 3.4 — Asignar vacío — no tenía Ocupante activo pero sí `apartamento_actual_id` (dato huérfano)
**Hoy:** se limpia directo, sin pasar por `dar_de_baja_ocupante`. — `ocupante_service.py:703-705`
**¿Debería ser así?**

### 3.5 — Envía solo Torre o solo Apartamento (no los dos, no ninguno)
**Hoy:** error "Completa Torre y Apartamento, o deja los dos vacíos." — `customers_manage.py:518-522`
**¿Debería ser así?**

### 3.6 — Torre+Apartamento no existen en el catálogo
**Hoy:** error de `resolver_apartamento` ("La unidad ... no existe en el catálogo...").
**¿Debería ser así?**

### 3.7 — Asigna la MISMA unidad donde ya es Ocupante activo (reenvío sin cambios)
**Hoy:** no-op — devuelve el mismo Ocupante tal cual, sin tocar su estado de
principal/confirmado. — `ocupante_service.py:708-709`
**¿Debería ser así?**

### 3.8 — Ya es Ocupante activo de OTRA unidad distinta a la que se le quiere asignar
**Hoy:** error "ya es Ocupante activo -- debe darse de baja antes de asociarse de
nuevo." No se mueve. — `ocupante_service.py:442-444`
**¿Debería ser así?**

### 3.9 — No es Ocupante de nada + unidad destino VACÍA
**Hoy:** se crea Y se confirma en el MISMO acto → queda **PRINCIPAL de inmediato**, sin
paso manual (toda Persona ya tiene tel o whatsapp por invariante, así que nunca falla
acá). — `ocupante_service.py:711-715`
**¿Debería ser así?**

### 3.10 — No es Ocupante de nada + unidad destino con gente pero SIN NADIE principal confirmado
**Hoy:** se crea y confirma en el mismo acto — y como sigue sin haber principal, **esta
Persona se lleva la promoción**, aunque hubiera otros Ocupantes `pending` de antes en
esa unidad (ver H5).
**¿Debería ser así?**

### 3.11 — No es Ocupante de nada + unidad destino YA tiene principal confirmado
**Hoy:** se crea y confirma en el mismo acto, pero NO se vuelve principal (ya hay uno) —
queda Ocupante confirmado no-principal.
**¿Debería ser así?**

### 3.12 — Unidad destino ya tiene el máximo de Ocupantes activos (5)
**Hoy:** error de `agregar_ocupante`.
**¿Debería ser así?**

---

## Vista 3 — `/residentes/{id}`, tab "Residentes" (staff)

Precondición general de "Agregar Residente": la Persona cuya ficha se ve debe YA tener
`apartamento_actual_id` — si no, error "Este cliente no tiene apartamento asignado."
(`customers_manage.py:573-579`). Por eso, en este flujo, la unidad de destino **nunca
está vacía** (siempre hay al menos la Persona que se está viendo).

### 4.1 — Agregar Ocupante CON teléfono
**Hoy:** se agrega `pending` con Persona propia (reutiliza la Persona si ese teléfono
ya existía sin ser Ocupante activo en otro lado). — `customers_manage.py:580-583`
**¿Debería ser así?**

### 4.2 — Agregar Ocupante SIN teléfono
**Hoy:** se agrega `pending` sin Persona propia (solo nombre) — válido porque la unidad
nunca está vacía acá.
**¿Debería ser así?**

### 4.3 — El teléfono dado ya es Ocupante activo (de esta unidad o de otra)
**Hoy:** error "ya es Ocupante activo...".
**¿Debería ser así?**

### 4.4 — Ya hay 5 Ocupantes activos en la unidad
**Hoy:** error de máximo.
**¿Debería ser así?**

### 4.5 — Se quiere registrar a alguien cuya única identidad es WhatsApp
**Hoy:** NO se puede desde acá — el formulario solo tiene campo Teléfono (ver H1).
**¿Debería ser así?**

### 4.6 — Confirmar: es el primero de su unidad (sin principal) y SÍ tiene Persona propia
**Hoy:** se confirma Y se promueve a principal en el mismo acto. — `ocupante_service.py:560-575`
**¿Debería ser así?**

### 4.7 — Confirmar: es el primero de su unidad (sin principal) pero NO tiene Persona propia
**Hoy:** error, no se puede confirmar ("debe tener Teléfono o WhatsApp").
**¿Debería ser así?**

### 4.8 — Confirmar: la unidad YA tiene un principal confirmado
**Hoy:** se confirma, no se vuelve principal (tenga o no Persona propia).
**¿Debería ser así?**

### 4.9 — Confirmar: ya estaba confirmado
**Hoy:** error "Este Ocupante ya está confirmado."
**¿Debería ser así?**

### 4.10 — Promover a principal: el Ocupante NO tiene Persona propia
**Hoy:** error, no puede promoverse. — `ocupante_service.py:591-595`
**¿Debería ser así?**

### 4.11 — Promover a principal: el Ocupante está dado de baja
**Hoy:** error.
**¿Debería ser así?**

### 4.12 — Promover a principal: caso válido (tiene Persona propia, activo)
**Hoy:** se promueve, el principal ANTERIOR (si había) se degrada en la misma
transacción. **No se exige que esté confirmado** (ver H4).
**¿Debería ser así?**

### 4.13 — Dar de baja: no-principal
**Hoy:** se da de baja sin problema.
**¿Debería ser así?**

### 4.14 — Dar de baja: principal, único activo
**Hoy:** se da de baja sin problema.
**¿Debería ser así?**

### 4.15 — Dar de baja: principal, con otros activos
**Hoy:** error, debe promover a otro primero.
**¿Debería ser así?**

### 4.16 — Asociar teléfono a un Ocupante sin contacto propio
**Hoy:** funciona (reutiliza o crea Persona).
**¿Debería ser así?**

### 4.17 — Asociar teléfono: ese número ya es Ocupante activo en otro lado
**Hoy:** error.
**¿Debería ser así?**

### 4.18 — Editar teléfono de un Ocupante que YA tenía uno (no-principal)
**Hoy:** funciona, re-liga a la Persona del nuevo número, sin tocar la Persona
anterior.
**¿Debería ser así?**

### 4.19 — Editar/desvincular el teléfono del PRINCIPAL desde acá
**Hoy:** error explícito — el teléfono del principal se edita desde "Datos
personales", no acá; y no puede desvincularse directamente (siempre debe tener
contacto). — `ocupante_service.py:304-307, 336-339`
**¿Debería ser así?**

### 4.20 — Desvincular teléfono de un no-principal
**Hoy:** funciona, el Ocupante queda solo con nombre.
**¿Debería ser así?**

---

## Vista 4 — `/mis-datos` (autoservicio del cliente)

Torre/Apartamento son de **solo lectura** para el cliente — la asignación es exclusiva
de staff desde `/residentes/{id}` (tab Dirección). Acá el cliente solo puede gestionar
OTROS Ocupantes de SU PROPIA unidad, y solo si es el principal confirmado.

### 5.1 — Cliente logueado NO es Ocupante de ninguna unidad
**Hoy:** no ve el bloque de gestión de Ocupantes en absoluto; tampoco puede pedir
Torre+Apartamento él mismo (solo lectura, exclusivo de staff). — `customer_verify.py:5-10`
**¿Debería ser así?**

### 5.2 — Cliente es Ocupante pero NO principal (es un "Hijo"/secundario)
**Hoy:** mismo trato que 5.1 — no ve el bloque de gestión. — `customer_verify.py:320-322`
**¿Debería ser así?**

### 5.3 — Cliente ES principal confirmado de su unidad
**Hoy:** ve y puede hacer todo lo de la Vista 3 (4.1-4.20) sobre los OTROS Ocupantes de
su unidad, actuando él mismo como `actor` (una Persona) en vez de un `Usuario` staff.
Mismo gap de WhatsApp que 4.5 (formulario solo con Teléfono).
**¿Debería ser así?**

### 5.4 — Cliente intenta gestionar un `ocupante_id` que NO pertenece a su propia unidad
(URL manipulada a mano)
**Hoy:** 403. — `customer_verify.py:190-192`, `_ocupante_gestionable_por`
**¿Debería ser así?**

---

## Vista 5 — `/paquetes` → "Corregir destinatario" → "Nuevo ocupante" (staff)

Acotado al Apartamento YA resuelto en el **snapshot** del paquete — no elige unidad, ya
viene dada por el paquete que se está corrigiendo.

### 6.1 — El paquete no tiene Apartamento en su snapshot
**Hoy:** no se puede usar "nuevo ocupante" — error genérico ("Escribí el nombre del
nuevo ocupante.", el mismo mensaje cubre tanto "sin apartamento" como "sin nombre", no
distingue cuál de las dos causas fue). — `packages.py:408-418`
**¿Debería ser así, o convendría un mensaje distinto para cada causa?**

### 6.2 — Unidad del snapshot VACÍA + sin teléfono
**Hoy:** error de `agregar_ocupante` ("primer Ocupante... debe tener Teléfono o
WhatsApp") — pero como este formulario **solo tiene campo Teléfono** (ver H1), en la
práctica esta exigencia JAMÁS se puede satisfacer con WhatsApp desde acá.
**¿Debería ser así?**

### 6.3 — Unidad del snapshot VACÍA + CON teléfono
**Hoy:** se crea el Ocupante `pending` (sin promoción automática — queda pending hasta
que alguien lo confirme por otra vía) y se corrige el destinatario a su nombre.
**¿Debería ser así?**

### 6.4 — Unidad con gente (con o sin principal) + SIN teléfono
**Hoy:** se crea `pending` sin contacto, y la corrección SÍ funciona igual — a
diferencia de `/announce`, acá no depende de resolver un Anunciante, solo cambia a
quién va el paquete. — `packages.py:427, 446-447`
**¿Debería ser así?**

### 6.5 — Unidad con gente + CON teléfono
**Hoy:** Ocupante `pending` con Persona propia, corrección funciona.
**¿Debería ser así?**

### 6.6 — El teléfono dado ya es Ocupante activo en otro lado
**Hoy:** error.
**¿Debería ser así?**

### 6.7 — Ya hay 5 Ocupantes activos en esa unidad
**Hoy:** error de máximo.
**¿Debería ser así?**

### 6.8 — `agregar_ocupante` tiene éxito, pero `corregir_destinatario` falla después
(el paquete cambió de estado entre cargar la página y enviar el formulario)
**Hoy:** el Ocupante nuevo queda creado en la base igual (ver H6) — el staff ve el
error de "el estado cambió", pero el registro ya existe.
**¿Debería ser así?**

---

## Cómo seguir

Dejá tus notas en cada `¿Debería ser así?` (o en los 6 hallazgos transversales de
arriba, que son los que probablemente más te interesa revisar primero). Cuando termines
de anotar, decime y armamos los cambios — si es poco, los aplico directo; si toca
rediseñar algo de fondo (por ejemplo H3/H5, o agregar WhatsApp donde falta), lo pasamos
por `grilling` antes de tocar código.
