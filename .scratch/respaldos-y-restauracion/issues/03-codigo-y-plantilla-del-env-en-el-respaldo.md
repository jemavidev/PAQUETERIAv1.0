# 03 — Código y plantilla del `.env` en el respaldo

**What to build:** cada respaldo suma `sistema.tar.gz` (copia exacta del código desplegado: compose, Caddyfile,
Dockerfile, requirements, código, migraciones y scripts) y `env.plantilla` (todas las variables del `.env` real,
agrupadas y con un comentario cada una; lo no secreto con su valor completo; los secretos ofuscados). Ambos entran en
las huellas del manifiesto, que además lista los nombres de las variables requeridas.

**Blocked by:** 01

**Status:** done

- [x] `sistema.tar.gz` corresponde exactamente al commit del manifiesto y nunca incluye el `.env` ni secretos.
- [x] `env.plantilla` tiene todas las variables del `.env` real, agrupadas por tema y con su comentario.
- [x] Secretos de 12 caracteres o más como `ABC****XYZ`; más cortos como `****`; ante la duda (nombre con KEY, SECRET,
      PASSWORD, TOKEN...) se trata como secreto.
- [x] Una variable nueva en el `.env` aparece sola en la siguiente plantilla.
- [x] Pruebas: contenido del `.tar.gz`, ofuscación por longitud, heurística de secretos, ausencia del `.env` real.

## Comments

**2026-09-25 (implementado, PaqueteX `1b04fe0`):** respaldo real en test con los 4 archivos: `sistema.tar.gz` (1,3 MB, 479
entradas, ningún `.env` -- en el checkout del servidor hay 5 copias viejas del `.env` que NO entran), `env.plantilla`
(secretos ofuscados, ej. `SECRET_KEY=307****0f3`) y 47 variables requeridas en el manifiesto. Imagen con `git` 2.47.
