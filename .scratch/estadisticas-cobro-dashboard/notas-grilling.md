# Rediseño de `/administracion/estadisticas-cobro` como dashboard de tarjetas

Notas del `grilling` (2026-09-20). Se van completando decisión a decisión; sirven
de insumo para `/to-spec` y para no perder lo acordado si la conversación se
compacta. NO es la spec.

## Pedido original (Jesús, textual)

> para la vista /administracion/estadisticas-cobro necesito que rediseñes la
> forma en que se ve todo, la idea principal es tener una parte superior con
> formas de filtrar como aparece actualmente y en una parte inferior una serie
> de tarjetas e información resumida, la idea es que no se tengan listas, solo
> información consolidada, por ejemplo te menciono algunas "Ingresos Hoy,
> Ingresos Semana, Ingresos Mes, Promedio recaudado por Paquete, Pagos
> Pendientes, Recaudado por bodegaje, Total Paquetes, Procesados Hoy, Procesados
> Semana, Procesados Mes, Totales para (ANUNCIADOS, RECIBIDOS, ENTREGADOS y
> CANCELADOS), Total Clientes, Clientes con más paquetes, Total Cliente,
> paquetes pendientes, sms enviados (día, semana, mes), Costo Promedio SMS con
> AWS en COP, tiempos promedios (anunciados por día/semana/mes, recibidos
> día/semana/mes, bodegaje día/semana/mes, tasa de entrega, tasa de
> cancelación)", estos entre muchas otras que me podría sugerir

## Hechos verificados (no son decisiones)

- Se calculan con datos que YA existen: ingresos (`cobros`), promedio por
  paquete, servicio vs bodegaje, anulaciones/exenciones, volumen por estado
  (`paquetes` + timestamps), tasas, tiempos anuncio→recepción y permanencia,
  clientes (`personas`), cliente con más paquetes, por-cobrar en bodega
  (`calcular_cobro` sobre RECIBIDO), deuda contra entrega
  (`movimientos_saldo_contra_entrega`).
- NO existe registro de mensajes enviados: no hay tabla; `NotificationSender.
  enviar(destino, mensaje) -> None` no devuelve proveedor/id/costo. SMS por
  cadena AWS SNS -> LIWA -> Twilio (failover) y OTP por una ruta paralela
  (`OtpSender`). "SMS enviados" y "costo SMS" exigen infraestructura nueva
  (tabla + migración + gancho en el envío) y una tarifa por SMS en COP.
- Las 3 listas actuales (Por cliente/apartamento, Por usuario, Serie diaria)
  desaparecen con este rediseño (consecuencia directa de "no listas").
- Contexto previo de la vista: issues 361 (sin "Últimos 7/30 días"), 363 (sin
  select de Usuario), 364 (sin Desde/Hasta, atajos Hoy/Ayer/Semana/Mes/3
  meses/Semestre/Año, sin filtro = todos los datos).

## Decisiones (una por una)

**D1 — Periodos: DOS ZONAS (decidido).** Zona «Panorama» arriba con los tríos
Hoy / Semana / Mes FIJOS (miden siempre el día, la semana y el mes en curso;
ignoran el filtro). Debajo, zona «Periodo seleccionado»: totales, estados,
clientes, tasas y tiempos SÍ responden a las píldoras (Hoy…Último año, Tipo,
Cobrado/Anulado); sin píldora activa = todos los datos.

**D2 — Costo por SMS (decidido, respuesta libre de Jesús):** "En esta vista
/administracion/proveedores agrega un campo de formulario que permita ingresar
el costo promedio de cada mensaje de texto y se realicen los cálculos de lo que
son los mensajes de texto, recuerda solo para aws". => campo «costo promedio por
SMS (COP)» en la pestaña/sección de AWS SNS de `/administracion/proveedores`
(solo AWS; no en LIWA/Twilio); el dashboard calcula sobre eso.
  - Hecho: los campos de esa pantalla son variables del `.env` del servidor
    aplicadas por SSH (`app/infra/deploy_ssh.py`) y un cambio de credencial
    REINICIA el contenedor. Un precio no es secreto => recomendación: guardarlo
    en la BD (no en `.env`): cambiarlo no reinicia nada y funciona en local.
    (Detalle técnico a confirmar en la spec, no una decisión de negocio.)
  - Secuenciación (dashboard primero vs junto con el registro de envíos): se
    resuelve en `/to-tickets`, no aquí.

**D3 — Conteo de SMS: REGISTRO REAL DE ENVÍOS (decidido).** Tabla nueva que anota
cada SMS con fecha, evento, paquete y el PROVEEDOR que finalmente lo entregó;
un gancho mínimo en el envío la llena. Las tarjetas cuentan SOLO los enviados
por AWS SNS × el costo configurado (D2). Exacto (respeta reintentos y
failover) pero cuenta desde el día que se active: el pasado no se recupera
(las tarjetas deberán decir "desde <fecha de activación>").

**D4 — OTP incluidos, DIFERENCIADOS (decidido).** El registro anota avisos de
paquetes Y códigos de acceso, cada uno con su tipo. Las tarjetas muestran el
total por AWS y el costo (así coincide con la factura de AWS) con desglose
«X avisos · Y códigos». Implica DOS ganchos: envío de avisos de estado
(`notificacion_service` / `web/notifications.py`) y envío de OTP (`web/otp.py`).

**D5 — «Pagos pendientes»: DOS TARJETAS SEPARADAS (decidido).**
  - «Por cobrar en bodega»: lo que se cobraría HOY por los paquetes RECIBIDO aún
    sin entregar (servicio + bodegaje acumulado, con la exención de primera
    entrega; misma aritmética que `calcular_cobro`).
  - «Deuda contra entrega»: suma de los saldos NEGATIVOS de dinero contra
    entrega.
  Ambas son una FOTO DE «AHORA» (stock): no dependen de las píldoras de fecha.
  Implicación de diseño: hay tarjetas de stock que no son ni «fijas
  Hoy/Semana/Mes» ni «periodo seleccionado» -> se resuelve en la pregunta de
  agrupación/secciones.

**D6 — «Procesados» = CERRADOS, con ENTREGADOS y CANCELADOS SEPARADOS
(decidido, respuesta libre: «Cerrados: pero sepáralos los entregados y los
cancelados»).** Procesado = paquete que llegó a un estado final (ENTREGADO o
CANCELADO) en el periodo, contado por la fecha en que se cerró (`delivered_at`
/ `cancelled_at`). Para Hoy / Semana / Mes se muestran las dos cifras por
separado (entregados y cancelados), no un único total. (Si van en tarjetas
distintas o en una tarjeta con dos cifras: detalle de diseño visual.)

**D7 — «Tiempos promedios»: AMBOS, en grupos separados (decidido).**
  - TIEMPOS (duración), cifras Hoy / Semana / Mes (fijas): anuncio→recepción
    (`received_at - announced_at`), permanencia en bodega (`delivered_at -
    received_at`, de los entregados) y bodegaje cobrado (horas de los cobros con
    bloques > 0, la métrica que ya existe).
  - RITMO, dentro del periodo seleccionado: promedio de anunciados, recibidos y
    entregados POR DÍA, POR SEMANA y POR MES (total del periodo ÷ días, ×7, ×30).
  - TASAS, periodo seleccionado: tasa de entrega y tasa de cancelación.
  (Cifras del preview a modo de ejemplo, no son datos.)

**D8 — Clientes: REGISTRADOS + ACTIVOS + TOP 1 (decidido), mostrando el NOMBRE
del cliente, no el teléfono** (agregado por Jesús: «sería mejor si es el nombre
del cliente en vez del número de teléfono»).
  - «Clientes registrados»: foto de ahora (personas sin eliminar ni de baja).
  - «Clientes activos»: distintos con >= 1 paquete en el periodo seleccionado.
  - «Cliente con más paquetes»: UNA tarjeta con el #1 del periodo: NOMBRE +
    apartamento + cuántos paquetes. No es un ranking.
  Detalle técnico para la spec: el nombre sale de `Persona.nombre` (o del
  `recipient_name` congelado del paquete si no hay Persona); el agrupamiento por
  teléfono sigue siendo la llave de «cliente».

**D9 — Extras: LOS CUATRO PAQUETES (decidido).**
  - Dinero (fugas y mezcla): % servicio vs bodegaje del recaudo; monto exonerado
    por anulaciones (+ cuántas y su tasa); exenciones por primera entrega
    (cuántas y cuánto se dejó de cobrar); cobro más alto del periodo.
  - Bodega (foto de ahora): paquetes en bodega; en gracia (<=48 h) vs con
    bodegaje corriendo; más de 7 días; abandonados (>30 días); paquete más
    antiguo; anuncios que nunca llegaron.
  - Operación y calidad: operador con más entregas del periodo; día y hora más
    activos; % entregado dentro de las 48 h de gracia; % extra-dimensionados;
    % recibidos abiertos / en mal estado (`package_condition`).
  - Clientes y SMS extra: clientes nuevos (primera entrega) y recurrentes del
    periodo; cliente con mayor gasto; clientes con deuda contra entrega; SMS
    fallidos; costo de SMS por paquete.

**D10 — Zonas: TRES, en este orden; tríos en UNA tarjeta (decidido).**
  1. PANORAMA (fijo, ignora los filtros de fecha): tarjetas con Hoy | Semana |
     Mes en columnas: Ingresos, Entregados, Cancelados, SMS AWS (con costo) y
     Tiempos (anuncio→recepción, permanencia en bodega, bodegaje cobrado).
  2. AHORA (foto del momento): pendientes (anunciados+recibidos), en bodega
     (en gracia <=48 h / con bodegaje / >7 días / abandonados >30 días / paquete
     más antiguo), por cobrar en bodega, deuda contra entrega, clientes
     registrados, anuncios que nunca llegaron.
  3. PERIODO SELECCIONADO (responde a las píldoras): recaudo (total, promedio
     por paquete, bodegaje, % servicio vs bodegaje, exonerado por anulaciones,
     exenciones 1.ª entrega, cobro más alto), paquetes (total, anunciados,
     recibidos, entregados, cancelados), ritmo (/día /semana /mes), tasas,
     clientes (activos, nuevos, recurrentes, #1 por NOMBRE, mayor gasto, con
     deuda), operación (operador top, día pico, hora pico, % dentro de gracia,
     % extra-dimensionados, % abiertos/mal estado), SMS del periodo (fallidos,
     costo por paquete, avisos vs códigos).
  (Layout ASCII acordado en la pregunta 10; se materializa en el prototipo.)

**D11 — Filtros: tarjetas ATENUADAS CON «NO APLICA» (decidido).** El encabezado
de la zona «Periodo seleccionado» muestra los filtros activos (ej. «Este mes ·
Extra-dimensionado»). Cada filtro acota las tarjetas donde tiene sentido (Tipo:
las que tienen `package_type`, o sea recibidos/entregados y su recaudo;
Cobrado/Anulado: solo tarjetas de cobro); las que un filtro activo no puede
acotar se ven atenuadas con una nota corta («no depende de Tipo»). La
disposición no cambia.
  - Implícito en D1/D10 (a confirmar en el resumen final): PANORAMA y AHORA
    ignoran TODOS los filtros (fecha, Tipo, Cobrado/Anulado) — son siempre el
    total del conjunto; solo «Periodo seleccionado» responde a la barra.

**D12 — Tasas: SOBRE CERRADOS (decidido).** Tasa de entrega = entregados ÷
(entregados + cancelados); tasa de cancelación = cancelados ÷ (entregados +
cancelados), contados por la fecha en que se cerraron, en el periodo
seleccionado. Suman 100 %; los paquetes en curso no las distorsionan (ya salen
en «Pendientes»). Ej.: 97 % entrega · 3 % cancelación.

**D13 — Zona horaria: HORA DE COLOMBIA EN TODO (decidido).** Hoy, Ayer, Esta
semana (desde el lunes), Este mes, los rangos de meses/año, el ritmo por día y
la hora pico se miden en hora de Colombia (UTC-5 fijo, `ZONA_HORARIA_APP` de
`web/templating.py`), 00:00–23:59 locales. Corrige el desfase de las 7 p.m.
del día UTC. Consecuencias para la spec:
  - Los límites de día de las estadísticas se corren 5 h respecto de la pantalla
    actual (los números por día cambian un poco).
  - El servidor calcula «hoy» en hora local: el parámetro `hoy` que hoy manda el
    navegador (issue 364) deja de hacer falta. El agrupamiento por día del
    servicio (`func.date(cobrado_en)`, hoy en UTC) debe pasar a hora local.

**D14 — Comparativos: SÍ, SOLO EN PANORAMA (decidido).** En los tríos fijos
(Ingresos, Entregados, Cancelados, SMS): Hoy vs ayer, Semana vs semana anterior,
Mes vs mes anterior, comparando el MISMO TRAMO (hoy hasta la hora actual vs
ayer hasta esa misma hora; semana a la fecha vs la anterior al mismo día y
hora; mes a la fecha vs el anterior al mismo día y hora) para no mostrar ▼
falsos a media mañana. Color según convenga (más ingresos = bueno, más
cancelados = malo). NO hay comparativos en «Periodo seleccionado».

**D15 — Costo de SMS: RECALCULAR CON EL PRECIO ACTUAL (decidido; Jesús eligió la
opción simple, no la recomendada).** Costo de cualquier periodo = cantidad de
SMS AWS × el «costo promedio por SMS» configurado HOY. No se guarda un precio
por mensaje; al cambiar el precio, todos los periodos se recalculan. Consecuencia
buena: el registro de envíos no necesita columna de costo y no hay «SMS sin
costo» — en cuanto se configura el precio, todo el historial del registro se
valora.


**D16 — Variante visual: C, «Mosaico con carriles de color» (decidido, 2026-09-20).**
Veredicto de Jesús tras ver las tres variantes: «la opción C se ve bastante bien».
Elecciones implícitas que se asumen (confirmar en la spec): los tres tiempos del
Panorama van en UNA tarjeta con tres filas (como en C) y la matriz «qué filtro
aplica a qué tarjeta» queda como en el prototipo.
Anatomía de C que la spec debe respetar:
  - Sin encabezados de sección: cada zona lleva un CARRIL VERTICAL de color a la
    izquierda (Panorama azul `#1e40af`, Ahora ámbar `#d97706`, Periodo verde
    `#059669`).
  - Cuadrícula de 12 columnas. En menos de ~900 px las tarjetas pasan a 2 por
    fila (600–899 px) y a 1 por fila en celular; los carriles se adaptan.
  - Tarjeta: borde superior en el color de la zona; etiqueta pequeña arriba
    (la categoría, o «foto» / «dinero» en Ahora); título; cifra grande; detalle
    pequeño; nota «no depende de …» cuando está atenuada.
  - PANORAMA: Ingresos (6 col), Entregados (3), Cancelados (3), SMS AWS (6, con
    su costo estimado debajo) y Tiempos promedio (6, una tarjeta con tres filas:
    anuncio→recepción, permanencia, bodegaje cobrado × Hoy/Semana/Mes). Cada trío
    con etiqueta ▲▼ de variación (verde/rojo según convenga) y, en Ingresos /
    Entregados / Cancelados / SMS, un minigráfico de los últimos 7 días.
  - AHORA: tarjetas de 2 columnas (6 por fila) con punto de semáforo (gris, verde,
    ámbar, rojo) y etiqueta «foto»; las dos de dinero (Por cobrar en bodega, Deuda
    contra entrega) de 3 columnas con punto azul y etiqueta «dinero».
  - PERIODO: un solo mosaico de tarjetas de 3 columnas (4 por fila) con la
    categoría (Recaudo, Paquetes, Ritmo y tasas, Clientes, Operación y calidad, SMS
    del periodo) como etiqueta de cada tarjeta; encima, los chips de los filtros
    activos (ej. «Este mes» · «Anulado»). Tarjeta atenuada = opacidad ~40 %, escala
    de grises y la nota «no depende de Tipo / de Cobrado/Anulado».
  - Formato de cifras como el resto de la app (comas de miles, `$` pegado).
Abierto para la spec: el MINIGRÁFICO de 7 días no estaba en D1–D15 (lo trae C). Si
se incluye, hay que definir su fuente (serie diaria de 7 días en hora de Colombia
para ingresos, entregados, cancelados y SMS) y su costo de consulta.
El prototipo NO se lleva tal cual: sus cifras son inventadas y los filtros se
simulan en el navegador; en la versión real cada cambio de filtro recalcula en el
servidor (fetch en vivo, como hoy).
Referencia: el prototipo COMPLETO (A, B, C, datos de ejemplo y selector) vive en la
rama desechable `prototipo/estadisticas-cobro-dashboard` — fuente primaria, no se
mergea a `main`.

## Supuestos tomados (a confirmar en el resumen final)

1. PANORAMA y AHORA ignoran TODOS los filtros; solo «Periodo seleccionado»
   responde a la barra (fecha, Tipo, Cobrado/Anulado).
2. Las 3 listas actuales desaparecen: «Por cliente/apartamento» -> tarjeta
   «Cliente con más paquetes» (nombre); «Por usuario» -> «Operador con más
   entregas»; «Serie diaria» -> ritmo y día/hora pico.
3. La barra de filtros no cambia: 7 atajos de fecha (Hoy, Ayer, Esta semana, Este
   mes, 3 últimos meses, Semestre, Último año) + Tipo + Cobrado/Anulado; sin
   atajo activo = todos los datos.
4. SMS: 1 SMS = 1 mensaje sin importar los segmentos (el costo promedio ya lo
   absorbe). Las tarjetas cuentan solo los ENVIADOS por AWS SNS. El registro
   guarda: momento, tipo (aviso de paquete / código OTP), evento, paquete (en
   avisos), proveedor que lo entregó y resultado (enviado/fallido); NO guarda el
   texto del mensaje ni el teléfono completo.
5. El campo «costo promedio por SMS (COP)» vive en la sección de AWS SNS de
   `/administracion/proveedores`, se guarda en la BD (no en `.env`: sin reinicio),
   admite decimales, >= 0. Sin costo configurado: las cantidades se muestran y
   el costo dice «Configura el costo en Proveedores».
6. Las tarjetas de SMS cuentan desde la activación del registro; deben decir
   «desde <fecha>». El pasado no se recupera.
7. «Totales para ANUNCIADOS/RECIBIDOS/ENTREGADOS/CANCELADOS» = flujo del periodo
   seleccionado (por la fecha de cada evento) + en AHORA cuántos están hoy
   anunciados y recibidos.
8. Técnico: el CSS de Tailwind compilado se commitea y el deploy no lo recompila
   (memoria `paquetex-tailwind-build`): las clases nuevas del tablero exigen
   reconstruirlo. Los agregados (tasas, comparativos, límites de día en hora
   local) son lógica delicada: candidatos a `tdd`.

## Entregas sugeridas (lo afina `/to-tickets`)

A. Tablero con todo lo que YA tiene datos (zonas 1-3 sin SMS): nueva consulta de
   agregados en hora de Colombia, plantilla de tarjetas, filtros con «no
   aplica», comparativos de Panorama.
B. Registro de envíos de SMS (tabla + migración + ganchos en avisos y OTP) +
   campo de costo en `/administracion/proveedores` + tarjetas de SMS.

## Prototipo visual (2026-09-20) — CAPTURADO en una rama desechable

Skill `prototype`, sub-forma A: tres variantes sobre la MISMA ruta
(`?variant=a|b|c`), datos de ejemplo, solo lectura, solo localhost. Ganó **C**
(ver D16).

- Fuente primaria: rama local `prototipo/estadisticas-cobro-dashboard`, commit
  `89a58e7` (NO se mergea a `main`, sin push). Trae A, B y C, los datos de ejemplo,
  el selector flotante, el gancho de 4 líneas en `routes/admin.py` y una copia de
  estas notas.
- `main` / árbol de trabajo: el prototipo YA fue retirado (módulo, plantillas y
  gancho). La pantalla real no cambió.
- Para volver a verlo: `git worktree add ../MATT-prototipo
  prototipo/estadisticas-cobro-dashboard` y correr la app desde ahí; las variantes
  están en `CODE/src/app/web/templates/admin/prototipo_estadisticas/`
  (`variante_c.html` es la ganadora y la referencia visual para implementar).
- A — secciones apiladas (cuadrícula uniforme). B — héroes, tira de alertas y
  pestañas. C — mosaico de 12 columnas con carriles de color (elegida).

## Insumos para `/to-spec` (propuestos por Claude, no acordados)

Seams de prueba que propondré (`/to-spec` pide validarlos con Jesús):
  1. Dominio, Postgres real (patrón de `tests/data_model/
     test_cobro_service_integration.py`): la consulta de agregados del tablero —
     límites de día/semana/mes en hora de Colombia, comparativos «mismo tramo»,
     tasas sobre cerrados, «foto de ahora» (por cobrar con la aritmética de
     `calcular_cobro`, deuda contra entrega, bodega/abandonados) y filtros
     Tipo / Cobrado-Anulado con su matriz de «no aplica».
  2. Web (TestClient, patrón de `tests/web/test_admin_estadisticas_cobro.py`): la
     ruta `/administracion/estadisticas-cobro` — render de las 3 zonas, el
     fragmento en vivo, filtros y atenuado.
  3. SMS: dominio del registro de envíos (avisos y OTP, proveedor que entregó,
     éxito/fallo) y web de `/administracion/proveedores` para el campo de costo
     (solo AWS, en BD).
Candidatos a `tdd`: los agregados y los límites de periodo en hora local.
Entregas sugeridas: A = tablero con datos existentes (zonas 1–3 sin SMS);
B = registro de envíos + ganchos + campo de costo + tarjetas de SMS.

## Spec publicada (2026-09-20)

`spec.md` en esta carpeta (`Status: ready-for-agent`): 96 historias de usuario, decisiones de
implementación y de prueba. Seams validados con Jesús: (1) servicio del tablero en el dominio con reloj
inyectable contra Postgres real; (2) ruta web delgada; (3) entrega de SMS + campo de costo en
Proveedores. Siguiente paso: `/to-tickets .scratch/estadisticas-cobro-dashboard/spec.md` (lo invoca Jesús).
