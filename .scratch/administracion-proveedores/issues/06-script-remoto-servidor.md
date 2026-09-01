# 06 — Aprovisionar el script remoto + `authorized_keys` restringido en el servidor

**What to build:** la mitad de la Fase 2 que vive FUERA de este repo — el script en
el servidor de `test.papyrus.com.co` que el mecanismo del ticket 04 invoca por SSH, y
la restricción de la llave que lo hace seguro. Es trabajo de infraestructura/ops, no
un PR de código Python — puede avanzar en paralelo al ticket 05, ya que ambos solo
dependen del contrato definido en el ticket 04.

Ver `.scratch/administracion-proveedores/spec.md` (Implementation Decisions "Script
remoto en el servidor"; Further Notes sobre por qué este script no se despliega vía
git).

**Blocked by:** 04 (necesita el contrato/protocolo exacto del payload)

**Status:** ready-for-agent

- [ ] Script en el servidor (ej. `update_provider_env.sh` o equivalente) que lee
      pares `KEY=VALOR` de stdin en el formato exacto que define el ticket 04.
- [ ] Rechaza cualquier `KEY` fuera del allowlist explícito de variables de
      proveedor (la misma lista derivada del catálogo de código) — sale con error sin
      tocar `.env` si encuentra una clave no permitida.
- [ ] Actualiza (o agrega) solo esas líneas específicas en `.env`, sin tocar el resto
      del archivo (comentarios, otras variables).
- [ ] Corre `docker compose --env-file .env up -d` (sin `--build`, ya que ningún
      código cambia) para que el contenedor recargue las variables nuevas.
- [ ] Entrada nueva en `authorized_keys` del servidor con `command="..."` forzado a
      ejecutar SOLO este script — la llave no debe poder abrir una shell libre ni
      ejecutar ningún otro comando.
- [ ] Prueba manual documentada: una clave dentro del allowlist se aplica y el
      contenedor recarga; una clave fuera del allowlist se rechaza sin tocar `.env`;
      un intento de usar la llave para otra cosa (`ssh -t`, otro comando) falla.
- [ ] El script y la configuración de `authorized_keys` quedan documentados en algún
      lugar versionado del repo (ej. `docs/`) aunque no se desplieguen desde ahí
      automáticamente — para que no quede como conocimiento tribal (ver Further Notes
      del spec).
