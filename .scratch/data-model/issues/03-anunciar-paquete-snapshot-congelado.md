# 03 — Anunciar Paquete con snapshot congelado

**Spec:** `.scratch/data-model/spec.md` · **ADR:** 0001 (Paquete snapshot inmutable)

**What to build:** Anunciar un paquete. Al anunciar, el sistema **congela una foto inmutable** del contexto de entrega y distingue **Anunciante** (quien avisa) de **Destinatario** (a nombre de quién llega). Un Destinatario sin teléfono queda como un **nombre bajo el teléfono del Anunciante**, nunca como una Persona sin llave. El Paquete nace en estado `ANUNCIADO`.

**Blocked by:** 02 — Apartamento + membresía actual.

**Status:** ready-for-agent

- [ ] Migración (descendiente) añade `usuarios` (esqueleto: rol enum `ADMIN`/`OPERADOR`, **sin** columnas de credencial — esas son de la rebanada de auth) y `paquetes`.
- [ ] `paquetes` incluye: FK al Anunciante (Persona) **+** `announced_by_phone` congelado; `recipient_name` + `recipient_phone` (nullable) congelados; **snapshot de apartamento como columnas de texto copiadas** (`snapshot_conjunto`/`snapshot_torre`/`snapshot_apartamento`), no FK; enum `estado` (`ANUNCIADO`/`RECIBIDO`/`ENTREGADO`/`CANCELADO`); `guide_number` nullable; `tracking_number`/`access_code` únicos; timestamps de transición y FK-actor nullable por transición hacia `usuarios`. *(ADR-0001)*
- [ ] `announce(anunciante_telefono, anunciante_nombre, destinatario, apartamento?)`: crea/reutiliza la Persona anunciante; resuelve el Destinatario (Persona registrada por teléfono | **nombre sin teléfono** bajo el tel del Anunciante); **congela el snapshot**; deja el Paquete en `ANUNCIADO`.
- [ ] Tests: anunciar para sí mismo; a nombre de una Persona registrada (Destinatario ≠ Anunciante); **nombre sin teléfono** (`recipient_name` bajo el tel del Anunciante, `recipient_phone` nulo, sin crear Persona sin llave); el snapshot refleja el apartamento resuelto **en el instante del anuncio**.

> Nota: la **lógica de la máquina de estados** (transiciones permitidas y quién puede cada una) queda fuera de este ticket — aquí solo se define el enum `estado` y las columnas. Ver Out of Scope del spec.
