# Spec — Corregir vía selección de Ocupantes conocidos (Grupo 16, Ronda 2)

**Fuente:** `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 16.

## Qué cambia

El modal "Corregir" (`/paquetes/{id}/corregir`) deja de ser texto libre por
defecto. Nuevo servicio de lectura `paquete_correccion_service.
candidatos_correccion(session, paquete)`:

- Si el paquete tiene un snapshot de Apartamento resuelto
  (`snapshot_conjunto`/`torre`/`apartamento`), candidatos = los Ocupantes de
  ese Apartamento (`ocupante_service.listar_ocupantes`) + el Anunciante
  mismo, únicos por `(nombre, teléfono)`.
- Sin Apartamento resuelto, candidatos = solo el Anunciante (que casi
  siempre resuelve, porque `announced_by_persona_id` es obligatorio) —
  la lista prácticamente nunca queda vacía en la práctica.
- La UI (`packages/list.html`) muestra un `<select>` cuando hay candidatos,
  o los dos campos de texto libre de siempre cuando no hay ninguno.
- La ruta (`packages.py::correct_recipient_action`) **recalcula los
  candidatos server-side** y valida el índice elegido contra ESA lista —
  nunca confía en lo que mandó el cliente. Así la restricción "SOLO
  selección" es real, no una simple ayuda visual.

## Por qué

El staff no debe inventar el nombre correcto de un destinatario — ese dato
ya lo validó el propio cliente (vía `/mis-datos` o `/announce`). El staff
solo reconoce cuál de los nombres ya conocidos es el correcto (p.ej. "Jesu
Villalobos" anunciado → "Jesus Villalobos" ya registrado).

## Decisión de diseño (AgentX)

Nuevo `apartamento_service.buscar_apartamento_por_terna` — versión de solo
lectura de `get_or_create_apartamento`, para no crear un Apartamento por
accidente al resolver candidatos de un snapshot que podría no tener match
real (dato legado o de prueba).

## Fuera de alcance

- No cambia nada de cómo se resuelve el destinatario al anunciar (Grupo 1,
  Ronda 1) — esto es solo la corrección posterior por el staff.
- El doble-escaneo de guía (Grupo 14) y las fotos múltiples + S3 (Grupo 15)
  son grupos aparte, aunque compartían la misma nota de origen.
