# 07 — Respaldo antes de cada deploy

**What to build:** el workflow de GitHub Actions saca un respaldo con motivo "antes de deploy" (con el commit que
estaba corriendo) ANTES de actualizar el código y reiniciar la app — las migraciones corren al arrancar. Va a
`puntual/`. Si el respaldo falla, el deploy se detiene.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] El paso corre antes del `git reset` y del reinicio/rebuild.
- [ ] El respaldo queda en `puntual/` con el commit previo al deploy en su manifiesto.
- [ ] Si el respaldo falla, el deploy no continúa y el job falla con un mensaje claro.
- [ ] Verificado en vivo con un deploy real a test.
