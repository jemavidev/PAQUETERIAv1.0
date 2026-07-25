# 02 — Buscar por teléfono (listado de paquetes)

**Spec:** `.scratch/search-web/spec.md` · **Glosario:** Teléfono, Anunciante, Destinatario

**What to build:** Cuando el término de `/search` **no** coincide con ningún número de seguimiento, se interpreta como **teléfono**: se **normaliza** (misma regla canónica del dominio) y se listan los Paquetes de esa persona — los que **anunció** o los que **llegan a su nombre** — cada uno con su estado, enlazando a su timeline.

**Blocked by:** 01 — Buscar por número de seguimiento + timeline (misma ruta/formulario; reutiliza el render del resultado individual).

**Status:** ready-for-agent

- [ ] Si el término no coincide con un `tracking_number`, se **normaliza como teléfono** y se buscan los Paquetes cuyo **`announced_by_phone`** o **`recipient_phone`** coincidan con la forma canónica.
- [ ] Resultado: **lista** de los Paquetes de esa persona, cada uno con su **estado** (y acceso a su timeline individual, del ticket 01).
- [ ] **Distintos formatos** del mismo teléfono (con/sin indicativo, espacios, guiones) encuentran **los mismos** resultados (normalización consistente con el dominio).
- [ ] Ningún teléfono coincide → "sin resultados", **200**, sin error.
- [ ] Tests HTTP: sembrar paquetes (uno anunciado por X, otro a nombre de X vía `Destinatario.persona_registrada`) y buscar por el teléfono de X en **varios formatos** → aparecen ambos con su estado; teléfono sin paquetes → "sin resultados".
