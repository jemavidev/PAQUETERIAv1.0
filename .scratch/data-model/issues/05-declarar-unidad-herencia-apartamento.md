# 05 — Declarar unidad + herencia de apartamento

**Spec:** `.scratch/data-model/spec.md` · **Glosario:** Herencia de apartamento, Declaración de unidad

**What to build:** El staff **declara una unidad a propósito** (varios teléfonos de un mismo Apartamento) y todos **heredan** ese Apartamento de una vez. Un "a nombre de" **casual** al anunciar **no** agrupa a nadie. Cualquier herencia errónea es **corregible** mudando/desvinculando.

**Blocked by:** 03 — Anunciar Paquete con snapshot congelado.

**Status:** done · 66 tests verdes

- [x] `declare_unit(apartamento, [telefonos])` asigna ese Apartamento como **actual** a **todos los teléfonos declarados a la vez** (la herencia). Get-or-create del Apartamento si hace falta.
- [x] Un `announce` con un Destinatario "a nombre de" **casual** NO modifica el `apartamento_actual` de nadie más allá del contexto del propio paquete (**no agrupa**).
- [x] La herencia es **corregible**: tras declarar la unidad, `move_resident` sobre un teléfono lo saca del grupo **sin afectar a los demás**.
- [x] Tests: declarar unidad agrupa (todos comparten apartamento actual); announce casual no agrupa; corrección vía `move_resident`.

> El "grupo misma unidad" **no es una entidad persistente** — es el conjunto de Personas que comparten Apartamento actual (ver `CONTEXT.md`). No se crea tabla de grupo.
