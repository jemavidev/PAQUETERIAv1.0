# 03 — Código y plantilla del `.env` en el respaldo

**What to build:** cada respaldo suma `sistema.tar.gz` (copia exacta del código desplegado: compose, Caddyfile,
Dockerfile, requirements, código, migraciones y scripts) y `env.plantilla` (todas las variables del `.env` real,
agrupadas y con un comentario cada una; lo no secreto con su valor completo; los secretos ofuscados). Ambos entran en
las huellas del manifiesto, que además lista los nombres de las variables requeridas.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] `sistema.tar.gz` corresponde exactamente al commit del manifiesto y nunca incluye el `.env` ni secretos.
- [ ] `env.plantilla` tiene todas las variables del `.env` real, agrupadas por tema y con su comentario.
- [ ] Secretos de 12 caracteres o más como `ABC****XYZ`; más cortos como `****`; ante la duda (nombre con KEY, SECRET,
      PASSWORD, TOKEN...) se trata como secreto.
- [ ] Una variable nueva en el `.env` aparece sola en la siguiente plantilla.
- [ ] Pruebas: contenido del `.tar.gz`, ofuscación por longitud, heurística de secretos, ausencia del `.env` real.
