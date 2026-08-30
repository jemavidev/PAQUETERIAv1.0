# 233 — Revisión de código de la sección Residentes: bug de colisión, tests faltantes, refactors

**Pedido original (cliente):** "Para finalizar parcialmente con estas
sección de residentes quiero que analices todo el código que le
corresponde a esto en sus vistas, analiza y busca por bugs, reportados
pendientes y posibles nuevos." + confirmación de arreglar el bug de
colisión encontrado y aplicar los 2 refactors sugeridos por la revisión de
Standards.

**Status:** implementado

## Hallazgos (code-review de dos ejes, Standards + Spec, sobre el diff sin
commitear de toda la sesión en esta área)

1. **Bug real (Spec), angosto pero silencioso**: editar el Teléfono de un
   Ocupante a un valor que ya pertenece a una Persona HUÉRFANA (no es
   Ocupante activo de nadie) que además tiene su PROPIO WhatsApp histórico,
   re-liga al Ocupante a esa Persona -- si en el MISMO envío (el modal
   "Editar" unificado, issue 228) también se cambia el WhatsApp, ese
   WhatsApp histórico ajeno se sobreescribe en silencio, sin error. Mismo
   riesgo simétrico del lado WhatsApp→Teléfono.
2. **Standards**: `agregar_telefono_a_persona_de_ocupante`/`agregar_
   whatsapp_a_persona_de_ocupante` (issues 213/217/226) y las rutas
   `/editar`/`/notificaciones` (issues 226-229) sin ningún test directo --
   solo probadas a mano por curl.
3. **Standards**: `components/_badge.html::badge_ocupante()` existe
   (Principal/Confirmado/Pendiente) pero `/mis-datos` y `/residentes`
   siguen con `<span>` sueltos hand-rolled en vez de usarlo.
4. **Standards**: la clase larga de los chips (Confirmar/Rechazar/
   Promover/Editar/Notificaciones/etc.) se repite ~10 veces entre las dos
   vistas -- candidata a un macro `chip()`.

## Decisión del cliente

Arreglar el bug (1) ahora, y aplicar los dos refactors (3, 4). Tests (2) se
agregan de todas formas como parte del cierre.

## Implementación

**Bug (1):** `ocupante_service.py` -- guardas simétricas en la rama de canal
único de `editar_telefono_ocupante` y `editar_whatsapp_ocupante`: si la
Persona resuelta para el nuevo valor es huérfana (pasa el check de
`_persona_ya_es_ocupante_activo`) pero YA tiene su propio canal contrario
(WhatsApp del lado Teléfono, Teléfono del lado WhatsApp), levanta
`ValueError` en vez de re-ligar `persona_id` en silencio.

**Tests (2):** 8 tests de dominio nuevos en `test_ocupante_service.py`
(guardas de canal doble huérfano + cobertura completa de
`agregar_telefono_a_persona_de_ocupante`/`agregar_whatsapp_a_persona_de_
ocupante`, antes sin ningún test directo), 7 tests web nuevos en
`test_customer_verify.py` (`/editar` unificado y `/notificaciones` de
Ocupante), 2 tests web nuevos en `test_customers_manage.py` (rama AGREGAR
de `/telefono` y `/whatsapp` del lado staff).

**Refactor (3):** `badge_ocupante()` (`components/_badge.html`) ahora
acepta un `texto` opcional que sobreescribe el texto por default sin tocar
el color -- permite reusarlo tal cual en `/paquetes` (texto corto,
"Principal") y en `/mis-datos`/`/residentes` (texto largo con ⭐,
"⭐ Residente principal"). Reemplazados los `<span>` hand-rolled de
Principal/Confirmado/Pendiente en `customer/verify.html` y
`customers_manage/detail.html` (fila de gestión Y roster de solo lectura).

**Refactor (4):** nuevo macro `chip_accion(color)` en `_badge.html` --
devuelve solo la clase Tailwind (no el tag, para que `<button>`/`<summary>`
y sus atributos propios sigan a cargo del llamador). Reemplaza la cadena
larga repetida ~10 veces entre las dos vistas (Confirmar/Rechazar-Eliminar/
Promover/Editar/Notificaciones/✕ Teléfono/✕ WhatsApp/+ Teléfono/+
WhatsApp).

**Verificación:** 119 tests de dominio (`test_ocupante_service.py`) + 61
tests web cliente (`test_customer_verify.py`) + 130 tests web staff
(`test_customers_manage.py`) + 78 tests de preferencias/adicionales, todos
en verde. Confirmado en vivo por curl (login real de staff y de cliente vía
`otp_dev.sh`) que ambas vistas renderizan los badges/chips a través de los
macros nuevos, sin clases hand-rolled sobrantes.
