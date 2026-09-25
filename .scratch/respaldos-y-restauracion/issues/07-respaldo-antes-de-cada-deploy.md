# 07 — Respaldo antes de cada deploy

**What to build:** el workflow de GitHub Actions saca un respaldo con motivo "antes de deploy" (con el commit que
estaba corriendo) ANTES de actualizar el código y reiniciar la app — las migraciones corren al arrancar. Va a
`puntual/`. Si el respaldo falla, el deploy se detiene.

**Blocked by:** 04

**Status:** done

- [x] El paso corre antes del `git reset` y del reinicio/rebuild.
- [x] El respaldo queda en `puntual/` con el commit previo al deploy en su manifiesto.
- [x] Si el respaldo falla, el deploy no continúa y el job falla con un mensaje claro.
- [x] Verificado en vivo con un deploy real a test.

## Comments

**2026-09-25:** paso "Respaldo antes del deploy" en el workflow del repo de deploy, antes de `git reset`/reinicio; si
falla, `exit 1` y el deploy no sigue. Verificado en dos deploys reales (`c77c719`, `b558516`): respaldos
`..._antes_de_deploy` en el disco y en S3 `puntual/`.
