# 01 — Consultar: solo por access_code o guía, torre/apartamento + enlace

**Qué construir:** `/consultar` elimina la búsqueda por teléfono. Solo busca por `access_code` o `guide_number` exactos. El resultado muestra teléfono, torre/apartamento (con enlace a `/otp` para actualizar datos si falta el apartamento).

**Bloqueado por:** Ninguno — el Grupo 1 (access_code de 4 caracteres) ya está implementado.

**Estado:** ready-for-agent

- [ ] `search.py` elimina la rama de búsqueda por teléfono; `q` compara contra `access_code` O `guide_number` exactos.
- [ ] Mensaje "sin resultados" genérico (no distingue cuál campo falló).
- [ ] El resultado muestra teléfono del destinatario/anunciante.
- [ ] Si falta torre/apartamento, se muestra un enlace a `/otp` para que el cliente se verifique y complete sus datos.
- [ ] `tests/web/test_search.py` reescrito: sin tests de búsqueda por teléfono (comportamiento eliminado a propósito); casos de `access_code` y `guide_number`.
- [ ] Suite completa (`pytest`) pasa.
