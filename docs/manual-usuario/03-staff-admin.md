# 3. Guía para el staff administrador

Esta guía es para vos si tenés rol de **Administrador**. Es un
complemento de la [Guía de Operador](02-staff-operador.md) — todo lo que
puede hacer un Operador, vos también podés hacerlo; acá está solo lo que
se suma encima de eso.

**Seguimos con el mismo caso de ejemplo** de la
[Guía de Operador](02-staff-operador.md): Torre 5 - Apto 302, con
**Angélica Ramírez** (Principal) y **Daniel Ramírez** (su hijo, vive con
ella); y **Carlos Pérez**, vecino de la Torre 2 - Apto 105, para los casos
de bloqueo. Sumamos a **Laura Gómez**, una Operadora nueva que se está
incorporando al equipo de portería.

## Cómo usar esta guía

Primero lo que extiende directamente acciones que ya conocés de la Guía de
Operador (mismo botón, más permiso), y después las 3 categorías del menú
**Administración**, en el mismo orden en que aparecen en pantalla:

| # | Bloque | De qué se trata |
|---|---|---|
| 1 | [Lo que solo vos podés hacer sobre Paquetes y Residentes](#1-acciones-exclusivas-de-admin-sobre-paquetes-y-residentes) | Eliminar paquete, Eliminar residente, Autorizar desbloqueo |
| 2 | [Administración → Cobros](#2-administración--cobros) | Tarifas de cobro, Estadísticas de cobro |
| 3 | [Administración → Datos](#3-administración--datos) | Conjunto, Contactos externos, Motivos de bloqueo, Motivos de anulación de cobro, Migrar año, Proveedores |
| 4 | [Administración → Perfiles](#4-administración--perfiles) | Usuarios (personal), Notificaciones |

El bloque 3 es el más largo — 6 pantallas distintas bajo la misma
categoría — pero cada una funciona sola; no hace falta leerlas en orden si
ya sabés cuál buscás.

## Todo lo que podés hacer, de un vistazo

| Querés... | Lo encontrás en... |
|---|---|
| Borrar de verdad un paquete que nunca se recibió | Botón Eliminar, en la fila del paquete |
| Borrar los datos de un residente (derecho al olvido) | Botón Eliminar, en su ficha |
| Habilitar a un residente bloqueado para que reintente el login | Botón Autorizar desbloqueo, en su ficha |
| Configurar las tarifas de cobro contra entrega y bodegaje | Administración → Cobros → Tarifas de cobro |
| Ver estadísticas de cobros, filtrables por fecha/tipo/usuario | Administración → Cobros → Estadísticas de cobro |
| Cambiar el nombre del conjunto residencial | Administración → Datos → Conjunto |
| Importar o exportar un padrón de contactos externos | Administración → Datos → Contactos externos |
| Administrar el catálogo de motivos de bloqueo | Administración → Datos → Motivos de bloqueo |
| Administrar el catálogo de motivos de anulación de cobro | Administración → Datos → Motivos de anulación de cobro |
| Migrar los códigos de acceso del año anterior | Administración → Datos → Migrar año |
| Configurar las credenciales de SMS, Email y WhatsApp | Administración → Datos → Proveedores |
| Crear y administrar cuentas de staff | Administración → Perfiles → Usuarios (personal) |
| Editar el texto de las notificaciones y el catálogo de motivos de cancelación | Administración → Perfiles → Notificaciones |

---

## 1. Acciones exclusivas de Admin sobre Paquetes y Residentes

Tres botones que un Operador ve en pantalla, pero que no le van a
funcionar — el sistema los bloquea internamente, no solo los esconde.

### Eliminar paquete

Botón **Eliminar**, en la bandeja de Paquetes — a diferencia de
**Cancelar** (que cualquier Operador puede hacer y deja rastro), esto es
un **borrado real**. Solo funciona mientras el paquete sigue en
**Anunciado** (nunca llegó a recibirse); en cualquier otro estado, el
sistema te pide que uses Cancelar en su lugar.

> **Ejemplo:** alguien anuncia un paquete escribiendo mal el número de
> teléfono, se da cuenta al toque y nunca llegó a recibirse. Como sigue
> Anunciado, **Eliminar** lo borra de verdad — no queda como un Cancelado
> más en el historial. Si en cambio ya alguien lo hubiera recibido por
> error, la única opción es Cancelar, aunque seas Admin.

### Eliminar residente

Botón **Eliminar**, en la ficha de un residente — borra sus datos
personales de verdad (derecho al olvido), para cuando alguien pide que se
eliminen sus datos por otro canal. Antes de dejarte eliminar, el sistema
exige que el **saldo contra entrega esté en $0** — si tiene saldo a favor
o en contra, primero hay que saldarlo.

> **Ejemplo:** Angélica pide que borren sus datos porque se muda
> definitivamente. Antes de que el botón **Eliminar** funcione, revisás su
> saldo contra entrega — si quedó con $3.000 a favor, hay que registrar
> esa devolución primero.

### Autorizar desbloqueo

Un paso **distinto** de "Liberar bloqueo" (que cualquier Operador ya
puede hacer, ver
[Baja, reactivación y bloqueos](02-staff-operador.md#10-baja-administrativa-reactivar-bloquear-liberar-bloqueo)
en la Guía de Operador): esto habilita que un residente bloqueado pueda
**reintentar** el login — no restaura el servicio de paquetes por sí solo.

> **Ejemplo:** Carlos Pérez quedó bloqueado por una sospecha que resultó
> ser un malentendido. Usás **Autorizar desbloqueo** para que pueda volver
> a pedir su código y entrar — si además el bloqueo debe levantarse del
> todo, hace falta además **Liberar bloqueo**, el mismo paso que ya tiene
> cualquier Operador.

---

## 2. Administración → Cobros

### Tarifas de cobro

Cuatro montos, los mismos que la bandeja de Paquetes usa para calcular
cada cobro automáticamente (ver
[Entregar un paquete](02-staff-operador.md#4-entregar-un-paquete) en la
Guía de Operador):

| Campo en pantalla | Qué tarifa es |
|---|---|
| "Servecio normal" *(así está escrito hoy en la pantalla — no es un error de esta guía)* | Cargo base de servicio, paquete normal. |
| "Servidio Extra-dimensionado" *(ídem)* | Cargo base de servicio, paquete extra-dimensionado (caja grande). |
| "Bodegaje normal" | Costo de bodegaje por día, paquete normal. |
| "Bodegaje Extra-dimensionado" | Costo de bodegaje por día, paquete extra-dimensionado. |

> **Ejemplo:** si subís "Bodegaje normal" de $2.000 a $2.500, cualquier
> paquete que se entregue **después** del cambio recalcula con la tarifa
> nueva — los cobros que ya estaban registrados no cambian con
> retroactividad.

### Estadísticas de cobro

Solo para consultar, no para editar nada. Arranca mostrando los
**últimos 30 días**. Podés filtrar (y combinar) por:
- Rango de fechas
- Tipo de paquete (normal / extra-dimensionado)
- Si el cobro fue cobrado o anulado
- Qué miembro del staff hizo la entrega

Trae tres tablas: por apartamento, por usuario de staff, y una serie
diaria.

> **Ejemplo:** querés saber cuánto cobró Laura Gómez (la Operadora nueva)
> en su primera semana, para revisar si está aplicando bien las
> exenciones. Filtrás por su nombre y el rango de fechas de esa semana —
> la tabla "por usuario" te da el total, y la serie diaria te muestra si
> hubo algún día raro.

---

## 3. Administración → Datos

### Conjunto

Lo más simple de todas: un solo campo, el nombre del conjunto
residencial, el mismo que aparece en las notificaciones y páginas
públicas.

> **Ejemplo:** el conjunto cambia de nombre comercial a "Conjunto Los
> Robles" — lo actualizás una sola vez acá y se propaga a todo lo que lo
> menciona.

### Contactos externos

Un padrón aparte del de residentes, para gente que no vive en el
conjunto pero de la que igual conviene tener datos (proveedores, por
ejemplo). Se administra con un archivo CSV:

- **Descargar plantilla** te da un CSV vacío con las columnas exactas que
  hacen falta.
- **Importar** te pide elegir o escribir una **fuente** — de dónde salió
  ese lote de contactos — para poder rastrear el origen después.
- Si dos filas del CSV comparten teléfono o WhatsApp, se combinan en un
  solo contacto — no quedan duplicadas.
- **Exportar** te trae el padrón completo actual, en el mismo formato.

> **Ejemplo:** conseguiste un CSV con los datos de los domiciliarios
> frecuentes del conjunto. Bajás la plantilla, acomodás tu archivo para
> que las columnas calcen, y al importar escribís la fuente "Domiciliarios
> 2026" — así, si en seis meses alguien pregunta de dónde salió ese
> contacto, queda registrado.

### Motivos de bloqueo

Un catálogo simple: crear y eliminar etiquetas. Alimenta el selector que
usa cualquier Operador al **Bloquear** a un residente.

> **Ejemplo:** agregás "Sospecha de uso indebido" al catálogo — a partir
> de ahí, cualquier Operador lo va a ver como opción la próxima vez que
> bloquee a alguien (como se hizo con Carlos Pérez más arriba).

### Motivos de anulación de cobro

Mismo patrón — crear y eliminar. Alimenta el selector obligatorio de
**Anular cobro**, dentro de **Entregar**.

> **Ejemplo:** el catálogo trae "Demora imputable a portería" — el mismo
> motivo que se usó en el ejemplo de Entregar de la Guía de Operador. Si
> lo borrás, esa opción deja de estar disponible para cobros nuevos (los
> que ya se anularon con ese texto no cambian).

### Migrar año

Una herramienta operativa, no de configuración: le agrega un sufijo de
año a los códigos de acceso de todo paquete que se haya **entregado o
cancelado el año calendario anterior** (los que siguen activos —
Anunciado o Recibido— nunca se tocan). La pantalla te muestra primero
cuántos paquetes son "elegibles", como vista previa, antes de que
confirmes. Correrla dos veces para el mismo año no hace nada la segunda
vez.

> **Ejemplo:** entrás en enero de 2027 y la pantalla te muestra
> "2026 — 340 paquetes elegibles". Confirmás: esos 340 códigos quedan con
> el sufijo del año agregado, y el contador baja a 0.

### Proveedores

Acá configurás **cómo se envían** las notificaciones (distinto de
"Perfiles → Notificaciones", que edita el texto). Una pestaña por canal:

| Canal | Proveedores disponibles | Estado |
|---|---|---|
| SMS | AWS SNS → LIWA → Twilio (ese orden, como respaldo si el primero falla) | Editable |
| Email | SMTP | Editable |
| WhatsApp | Meta (WhatsApp Business) | Editable, aunque todavía no envía mensajes reales — el terreno queda listo para cuando se conecte |
| Llamada | Issabel (PBX) | Visible pero bloqueada por ahora ("Próximamente") |

Por seguridad, un campo ya configurado nunca muestra el valor completo:
las contraseñas y tokens se muestran parcialmente tapados. Si dejás un
campo vacío al guardar, eso significa "no cambiar esa credencial" — nunca
borra lo que ya había.

> **Ejemplo:** AWS SNS (el proveedor principal de SMS) empieza a fallar
> por un problema de facturación. Mientras se resuelve, podés bajar su
> prioridad en el orden de la pestaña SMS para que LIWA pase a intentarse
> primero — sin tocar ninguna credencial, solo el orden.

---

## 4. Administración → Perfiles

### Usuarios / Personal

Alta y gestión de cuentas de staff (no de residentes):
- **Crear cuenta**: email, nombre, contraseña inicial, y rol (Operador o
  Admin).
- **Editar** nombre y rol de otra cuenta.
- **Resetear contraseña** de otra cuenta.
- **Activar / Desactivar** — desactivar nunca borra la cuenta, solo le
  quita el acceso.

**Importante:** para que el conjunto nunca se quede sin ningún
Administrador por accidente, hay dos cosas que un Admin no puede hacerse
a sí mismo: **degradarse** a Operador, ni **desactivarse**. Cualquiera de
las dos las tiene que hacer otro Admin.

> **Ejemplo:** das de alta a Laura Gómez como Operadora nueva — email,
> nombre, una contraseña provisional que ella va a cambiar en su primer
> ingreso, rol Operador. Meses después, si confirma que puede asumir más
> responsabilidad, volvés acá y le cambiás el rol a Admin.

### Notificaciones

Dos catálogos en la misma pantalla:

**Plantillas** — el texto de cada notificación, organizado por evento
(Anunciado, Recibido, Entregado, Cancelado) y canal (SMS, Email,
WhatsApp). El botón **Enviar prueba** manda un mensaje real a un destino
que escribas en el momento — no es una simulación, así que si el
proveedor falla de verdad, te lo dice tal cual, antes de que le llegue
algo raro a un residente real.

**Motivos de cancelación** — el mismo catálogo que alimenta el picker de
**Cancelar** en Paquetes, embebido en esta misma pantalla (crear, editar,
eliminar). A diferencia de los otros dos catálogos de motivos, este **no
te deja borrar el último que queda** — cancelar siempre exige un motivo,
así que la lista nunca puede quedar vacía.

> **Ejemplo:** cambiás el texto del SMS de "Recibido" para que mencione
> el horario de atención de portería. Antes de confiar en que llega bien,
> usás **Enviar prueba** con tu propio teléfono — si el mensaje llega con
> el texto nuevo, lo dejás así; si el proveedor devuelve un error, lo
> sabés ahí mismo, no cuando un residente se queje de que nunca le llegó
> nada.
