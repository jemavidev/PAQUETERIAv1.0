# 05 — Sesión de un Ocupante-con-teléfono (no principal) en `/mis-datos`

**What to build:** cuando alguien se loguea vía OTP y su teléfono corresponde a un Ocupante ACTIVO no-principal de algún Apartamento, `/mis-datos` se renderiza en modo "Ocupante" (misma ruta, distinta vista según el rol resuelto): edita solo sus propios datos personales (nombre, email — preferencias se definen en el ticket 06); ve de solo lectura el resto del roster activo de su Apartamento (nombre Y teléfono de todos, incluido el principal — visibilidad completa dentro del mismo apartamento, sin restricción); NO ve ni edita Torre/Apartamento/Conjunto (eso es del principal); NO ve la sección de gestión de Ocupantes del ticket 03 (crear/asociar/desvincular/dar de baja de OTROS es exclusivo del principal); SÍ puede autodarse de baja de ese Apartamento (usa `dar_de_baja_ocupante` del ticket 02 sobre su propio Ocupante).

**Blocked by:** 03, 02

**Status:** done

- [x] Un Ocupante-con-teléfono no-principal, al entrar a `/mis-datos`, ve sus propios datos personales editables.
- [x] Ve el resto del roster activo de su Apartamento (nombre + teléfono de cada uno, incluido el principal) de solo lectura.
- [x] No puede modificar los datos de nadie más que los suyos propios.
- [x] No ve el bloque de gestión de Ocupantes (crear/asociar teléfono/desvincular/dar de baja de otros) — eso queda exclusivo del principal.
- [x] Puede autodarse de baja de ese Apartamento por su cuenta.
- [x] La vista del principal (ticket 03) sigue funcionando sin regresión.
- [x] Tests cubren: renderizado correcto según rol (principal vs Ocupante), edición restringida a lo propio, auto-baja exitosa.

## Implementación

**Corrección importante encontrada al empezar**: `agregar_ocupante`/`asociar_telefono_a_ocupante` nunca sincronizaban `Persona.apartamento_actual_id` — un Ocupante no-principal recién asociado no tenía NINGÚN apartamento resuelto para su propia Persona, lo que además de romper la vista de solo lectura de este ticket, habría roto el snapshot de `announce()` si esa Persona anunciaba un paquete. Corregido en `ocupante_service.py`: `agregar_ocupante`, `asociar_telefono_a_ocupante` ahora fijan `apartamento_actual_id`; `desvincular_telefono_ocupante` y `dar_de_baja_ocupante` lo limpian. 4 tests nuevos de dominio.

- `customer_verify.py`: `_contexto_base` ahora resuelve el roster para CUALQUIER Ocupante activo (no solo principal) + `personas_telefono` (teléfonos del roster, para la vista "ve todo"). El POST ignora por completo Torre/Apartamento/Conjunto si la Persona es Ocupante no-principal (se descubrió que solo poner los valores en `None` no bastaba -- `conjunto_v` seguía resolviendo no-`None` vía `apartamento_actual_id` ya sincronizado, disparando el rechazo "Completa Torre y Apartamento" — el bloque entero de Apartamento ahora se salta para este rol). Nueva ruta `POST /mis-datos/ocupantes/salir` (autoservicio, opera sobre el Ocupante del que llama, no un id elegido).
- `customer/verify.html`: Torre/Apartamento se muestran deshabilitados para un Ocupante no-principal; tarjeta nueva "Quiénes más viven acá" (roster completo, solo lectura) + botón "Salir de este apartamento".
- Corregido también un bug latente en el helper de tests `_login_cliente` (siempre resolvía al teléfono default sin importar cuál se pasara) — necesario para poder loguearse como un Ocupante distinto del principal en los tests.
- Suite completa: 495 passed.
