# Spec — Auditoría de actor visible (Grupo 11, Ronda 2)

**Fuente:** `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 11.

## Qué cambia

Hoy `Paquete` ya guarda quién ejecutó cada transición (`announced_by_usuario_id`,
`received_by_usuario_id`, `delivered_by_usuario_id`, `cancelled_by_usuario_id`) —
el esquema no cambia. Lo único nuevo es **mostrarlo**:

- `/consultar` (público, vista del cliente): cada hito de la línea de tiempo
  gana quién lo hizo.
  - **Anunciado**: si `announced_by_usuario_id` es `NULL` (el cliente anunció
    él mismo vía `/anunciar`), se muestra el nombre de la `Persona`
    anunciante (`announced_by_persona_id`) con la etiqueta "cliente". Si no es
    `NULL` (el staff anunció vía `/announce`), se muestra el nombre del
    `Usuario` con la etiqueta "staff".
  - **Recibido / Entregado / Cancelado**: siempre son transiciones de staff —
    se muestra el nombre del `Usuario` correspondiente con la etiqueta
    "staff". Si por algún motivo el actor es `NULL` (no debería pasar en
    datos nuevos, pero hay que ser defensivo), simplemente no se muestra la
    línea de actor para ese hito.
- `/paquetes` (staff): cada tarjeta gana una línea compacta "Última acción
  por: `<nombre>`" — el actor de la transición **más avanzada** que ya
  ocurrió (Cancelado > Entregado > Recibido > Anunciado, en ese orden de
  prioridad de visualización, porque es mutuamente excluyente con Entregado).

## Por qué (contexto)

Esto **revierte** una decisión explícita de la Ronda 1 (Grupo 2, pregunta 1):
en su momento el usuario confirmó que `/consultar` debía seguir ocultando el
actor ("no se revierte, solo que se pueda auditar"). La nueva nota deja claro
que ahora sí lo quiere visible. Se implementa la reversión tal cual se pide,
sin volver a preguntar — es una instrucción explícita y sin ambigüedad.

## Diseño

Nueva función de dominio, `app/domain/actor_service.py`:

```python
def nombre_usuario(session: Session, usuario_id) -> str | None:
    """Resuelve el nombre de un Usuario (staff) por id, o None si no hay
    actor (usuario_id es None) o el Usuario no existe."""
```

No hace falta una función equivalente para Persona — el patrón
`db.get(Persona, ...)` ya se usa igual en `packages.py`
(`_nombre_no_coincide`), se reutiliza tal cual en `search.py`.

### `search.py` (`_timeline`)

Cada hito gana `actor` (string ya formada, p.ej. `"Ana Torres (staff)"` o
`"Jesús Villalobos (cliente)"`) o `None`.

### `packages.py` (`_listar`)

Cada `Paquete` de la página gana un atributo transitorio
`p.actor_ultima_accion` (string o `None`), mismo patrón que ya usa
`p.advertencia_nombre`.

## Fuera de alcance

- No se toca qué puede editar el staff ni las reglas de la máquina de
  estados — esto es 100% de lectura/presentación.
- No se agrega ninguna columna ni migración.
