Status: ready-for-agent
Feature: dinero-contra-entrega
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación, módulo 5 de 5) ·
CONTEXT.md (glosario) · `.scratch/cobro-bodegaje/spec.md` (módulo 1, comparte el mismo endpoint de
Entregar — ver Further Notes)

---

## Problem Statement

Algunos residentes dejan dinero en portería por adelantado para cubrir paquetes "pago contra
entrega" (donde un mensajero externo exige el pago para soltar el paquete) — a veces el monto
exacto, a veces de más, a veces de menos. Hoy nada de eso queda registrado: no hay forma de saber
cuánto dejó cada cliente, cuánto se le pagó a un mensajero en su nombre, ni cuánto le queda a favor
para el próximo paquete. El cliente necesita que cualquier miembro del staff pueda saber en
cualquier momento qué residentes tienen saldo a favor y cuánto, y que ese saldo se pueda usar tanto
para pagarle a un mensajero al recibir un paquete como para ajustarse (dar vueltas o cobrar el
faltante) cuando el residente viene a buscarlo.

## Solution

`Persona` gana un **saldo a favor** — no un campo fijo, sino la suma de un historial de movimientos
(depósitos y pagos) que cualquier miembro del staff puede registrar en cualquier momento. Ese saldo
es de quien lo deposita, pero se puede usar para pagar el contra entrega de **cualquier residente
del mismo apartamento** (no solo de quien lo dejó) — al momento de Recibir, si el mensajero exige
pago y el destinatario o algún compañero de apartamento ya tiene algún movimiento registrado, staff
elige de cuál de ellos se descuenta y registra el monto realmente pagado. El saldo puede quedar
negativo (una deuda) si lo pagado excede lo disponible — no se bloquea el pago al mensajero por
falta de fondos.

Si el paquete no tiene ningún historial de saldo asociado a su destinatario ni a sus compañeros de
apartamento, Recibir se comporta exactamente igual que hoy, sin ninguna mención de contra entrega.

Al momento de Entregar, si quedó un saldo negativo, se ofrece un campo opcional para registrar que
el residente pagó (todo o parte) en ese mismo momento — sin bloquear nunca la entrega: el paquete se
entrega igual aunque el residente no pague nada ahí, y la deuda queda pendiente de recuperar por
fuera del sistema. Cuando esa plata se recupera (el mismo día o después), se registra como un
movimiento nuevo, dejando el saldo en negativo (parcial), cero (exacto) o positivo (de más) — listo
para futuros paquetes contra entrega.

El residente ve su propio saldo e historial en su portal. Además, una página de búsqueda simple,
accesible a cualquier miembro del staff, muestra qué residentes tienen saldo distinto de cero.

## User Stories

1. Como miembro del staff, quiero poder registrar en cualquier momento que un residente dejó
   dinero en portería, sin que esto dependa de que haya un paquete de por medio todavía.
2. Como sistema, quiero calcular el saldo a favor de un residente como la suma de todos sus
   movimientos (depósitos menos pagos), en vez de guardar un número aparte que se pueda
   desincronizar.
3. Como miembro del staff, al Recibir un paquete, quiero que la opción de pagarle al mensajero desde
   el saldo aparezca SOLO si el destinatario o algún compañero de su apartamento actual ya tiene
   algún movimiento de saldo registrado — si nadie tiene historial, Recibir se comporta exactamente
   igual que hoy.
4. Como miembro del staff, cuando la opción aparece, quiero poder elegir de cuál residente del
   apartamento (entre los que ya tienen historial) se descuenta el pago, no solo del destinatario.
5. Como miembro del staff, quiero registrar el monto realmente pagado al mensajero, y que ese monto
   se descuente del saldo elegido en el mismo momento.
6. Como sistema, quiero permitir que el saldo quede en negativo si el pago al mensajero excede lo
   disponible — el pago no se bloquea nunca por falta de fondos.
7. Como miembro del staff, al Entregar un paquete cuyo saldo asociado quedó negativo, quiero ver ese
   saldo pendiente y tener la opción (no obligatoria) de registrar que el residente lo cubrió en ese
   momento, total o parcialmente.
8. Como sistema, NO quiero bloquear nunca la entrega de un paquete por un saldo negativo — el
   paquete se entrega igual, resuelva o no el residente la deuda en ese momento.
9. Como miembro del staff, si el residente no paga al momento de Entregar, quiero que la deuda quede
   registrada tal cual, para gestionar su cobro por fuera del sistema.
10. Como miembro del staff, cuando esa plata se recupera (en el momento o más adelante), quiero
    poder registrarlo como un movimiento nuevo, en cualquier momento, sin que dependa de ningún
    paquete puntual.
11. Como sistema, quiero que el saldo resultante de una recuperación pueda terminar en negativo
    (recuperación parcial), en cero (exacto), o positivo (de más) — cualquiera de los tres es un
    resultado válido.
12. Como residente, quiero poder ver mi propio saldo a favor y el historial de a qué paquete se
    aplicó cada movimiento, desde mi portal, para saber en todo momento cuánto tengo disponible.
13. Como miembro del staff (cualquier rol), quiero una página de búsqueda simple que me muestre qué
    residentes tienen saldo distinto de cero, para saber en cualquier momento quién pagó cuánto.
14. Como sistema, quiero que un residente sin ningún movimiento propio ni de sus compañeros de
    apartamento no tenga ninguna mención de saldo en ningún lado — el saldo es cero e invisible por
    defecto, no un "$0" mostrado activamente.
15. Como sistema, NO quiero permitir editar o borrar un movimiento ya registrado — un error se
    corrige con un movimiento nuevo que lo compense, nunca reescribiendo el historial (mismo
    criterio de auditoría que el resto de los módulos de dinero de esta conversación).
16. Como miembro del staff (cualquier rol), quiero poder registrar depósitos, pagos y recuperaciones
    sin que esto sea exclusivo de admin — es una acción operativa del día a día.
17. Como sistema, si un residente se muda de apartamento, quiero que la elegibilidad para compartir
    saldo en Recibir se calcule según su apartamento ACTUAL en ese momento (no el apartamento que
    tenía cuando se hizo un depósito viejo) — el saldo sigue siendo de la persona, pero con quién se
    puede compartir cambia si se muda.
18. Como cliente, quiero que este módulo NO cree ningún campo nuevo en `Paquete` para marcar "es
    contra entrega" — la única condición que activa todo el flujo es la existencia de historial de
    saldo, nada más.

## Implementation Decisions

- **Nueva entidad `MovimientoSaldoContraEntrega`** (`src/app/domain/`): `id`, `persona_id` (FK, de
  quién es el saldo afectado), `monto` (entero con signo — positivo suma al saldo: depósito, pago
  del residente, recuperación; negativo resta: pago a mensajero, vuelta entregada), `paquete_id`
  (FK nullable — el paquete asociado, si aplica), `registrado_por_usuario_id`, `created_at`. Sin
  `updated_at` — append-only, ningún movimiento se edita ni se borra una vez creado (mismo criterio
  de inmutabilidad que `Cobro` del módulo 1 y el motivo de bloqueo del módulo 4).
- **Nueva función `registrar_movimiento_saldo(session, persona_id, monto, staff, paquete_id=None) ->
  MovimientoSaldoContraEntrega`** (en `saldo_contra_entrega_service.py`) — único punto que crea un
  movimiento, reusado igual para depósito, pago a mensajero, ajuste en Entregar, y recuperación
  posterior. No valida signo del saldo resultante (permite negativo).
- **Nueva función `saldo_de_persona(session, persona_id) -> int`** — suma de `monto` sobre todos los
  movimientos de esa Persona. Sin campo desnormalizado en `Persona`.
- **Nueva función `personas_con_historial_en_apartamento(session, apartamento_id) ->
  list[Persona]`** — Ocupantes con Persona propia del apartamento dado que tienen al menos un
  movimiento registrado (para poblar el selector "de quién se descuenta" en Recibir). Usa el
  `apartamento_actual_id` VIGENTE de cada Persona, no ningún snapshot congelado de un paquete.
- **Extensión del flujo de Recibir** (`_recibir_paquete.html` + el endpoint que ya existe): antes de
  mostrar el paso de tipo/condición, resuelve el destinatario del paquete (por `recipient_phone`,
  igual que ya hace `es_primera_entrega_a_telefono`) y su apartamento actual; si él o algún
  compañero tiene historial (`personas_con_historial_en_apartamento`), muestra el selector +campo de
  monto pagado al mensajero, opcional. Al confirmar, en la misma transacción que `receive()`, llama
  a `registrar_movimiento_saldo` con `monto` negativo.
- **Extensión del endpoint único de Entregar** (`packages.py`, el mismo que ya extiende el módulo 1
  para el cobro — ver Further Notes): si el destinatario tiene saldo negativo, el modal muestra el
  monto pendiente y un campo opcional "¿pagó ahora?"; si se completa, se llama a
  `registrar_movimiento_saldo` con `monto` positivo en la misma transacción; si se deja vacío, la
  entrega procede igual, sin ningún bloqueo.
- **Nueva ruta para depósito/recuperación standalone** (`customers_manage.py`, mismo patrón que
  bloquear/dar de baja): `POST /residentes/{persona_id}/saldo-contra-entrega/movimiento` — acepta
  monto (positivo o negativo) y `paquete_id` opcional. `current_staff`, cualquier rol.
- **Nueva ruta de listado** (`customers_manage.py` o un router propio, bajo `/residentes` — NO bajo
  `/administracion`, para que quede accesible a cualquier `current_staff` y no solo a admin, a
  diferencia de las páginas de solo-admin de los módulos 1-3): buscador + listado de Personas con
  `saldo_de_persona != 0`.
- **Portal del residente** (`customer_paquetes.py`/`customer_verify.py`, rutas ya gateadas por
  `current_customer`): muestra el saldo propio (`saldo_de_persona`) y el historial de movimientos
  propios, incluyendo a qué paquete se aplicó cada uno.
- **Sin cambios en `Paquete`** — ningún campo nuevo de "es contra entrega"; toda la lógica depende
  de si existe historial de saldo, no de una marca en el paquete.

## Testing Decisions

Buen test acá = observar comportamiento externo (qué devuelve la función/ruta, qué queda en
`MovimientoSaldoContraEntrega` después, qué HTML se renderiza) — nunca aserciones sobre el código
interno.

- **Seam 1 — `registrar_movimiento_saldo`/`saldo_de_persona`** (nuevo
  `tests/data_model/test_saldo_contra_entrega_service.py`): un depósito suma al saldo; un pago
  (monto negativo) resta y puede dejarlo en negativo; la suma de varios movimientos da el saldo
  esperado; no existe ninguna función/ruta que edite o borre un movimiento ya creado.
- **Seam 2 — `personas_con_historial_en_apartamento`**: devuelve al destinatario y a sus compañeros
  de apartamento ACTUAL que tienen movimientos; NO incluye a alguien de otro apartamento aunque
  tenga saldo; si el residente se mudó, usa su apartamento nuevo, no uno viejo.
- **Seam 3 — Recibir con saldo** (extensión de `tests/web/test_packages.py`, prior art:
  `test_modal_entregar_incluye_escaneo_si_el_paquete_tiene_guia`/
  `test_modal_entregar_sin_escaneo_si_el_paquete_no_tiene_guia`, mismo patrón de "aparece
  condicionalmente"): el selector de pago aparece solo si hay historial; Recibir sin historial se
  comporta idéntico a hoy (sin ninguna mención de saldo); confirmar un pago crea el movimiento
  negativo y transiciona el paquete en la misma operación.
- **Seam 4 — Entregar con ajuste** (extensión de los mismos tests de Entregar del módulo 1): un
  saldo negativo muestra el campo de ajuste; completarlo crea el movimiento positivo; dejarlo vacío
  entrega igual sin crear ningún movimiento ni bloquear nada.
- **Seam 5 — rutas de staff** (`tests/web/test_customers_manage.py`): depósito/recuperación
  standalone disponible para cualquier rol de staff; el listado de saldos distintos de cero
  devuelve exactamente lo esperado y no incluye a residentes en cero.
- **Seam 6 — portal del residente** (`tests/web/test_customer_paquetes.py` o equivalente): el
  residente ve su propio saldo e historial; NO ve el de otro residente.

## Out of Scope

- Cualquier marca de "es contra entrega" en `Paquete` — la condición es siempre la existencia de
  historial de saldo, no un campo del paquete.
- Captura del medio de pago del depósito/recuperación (efectivo, transferencia, etc.).
- Cualquier automatización o integración con un proveedor de pago real — todo es registro manual
  de dinero que ya se entregó en efectivo/otro medio fuera del sistema.
- Corrección o edición de un movimiento ya registrado — un error se compensa con un movimiento
  nuevo.
- Notificaciones (WhatsApp/SMS) que mencionen el saldo o los movimientos — el residente lo consulta
  en su propio portal cuando quiera, no se le empuja información nueva por este canal.
- Límite o validación de que el saldo no pueda quedar negativo — está permitido explícitamente.

## Further Notes

- **Este módulo y el módulo 1 (`.scratch/cobro-bodegaje/spec.md`) extienden el mismo endpoint de
  Entregar** — uno agrega el cobro obligatorio por bodegaje/tipo de paquete, este agrega el ajuste
  opcional de saldo contra entrega. Son piezas independientes entre sí (ningún dato de una afecta a
  la otra), pero quien implemente el segundo de los dos debe revisar el formulario/endpoint ya
  extendido por el primero para no pisar sus cambios.
- El saldo pertenece a la Persona que lo deposita, pero es utilizable por cualquier residente de su
  mismo apartamento — decisión explícita del cliente, más simple que atar cada depósito a un
  paquete específico por adelantado.
