# 02 — Restauración con las 6 protecciones

**What to build:** `restaurar.sh <carpeta-del-respaldo>`, por SSH, que restaura un respaldo sobre el mismo sistema y se
niega a hacer algo peligroso. El script es delgado (detiene/enciende contenedores y el cron del importador, pide la
confirmación); las protecciones y la restauración viven en el módulo de respaldos para poder probarlas.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] (1) Verifica las huellas del manifiesto; si algo no coincide, no toca nada y dice qué archivo falla.
- [ ] (2) Se niega si el dominio/conjunto del manifiesto no es el del servidor destino, salvo `--otro-destino`.
- [ ] (3) Se niega si la BD del respaldo es más nueva que el código instalado y dice que se despliegue primero el
      `sistema.tar.gz` de ese respaldo; si es más vieja, restaura y aplica las migraciones pendientes.
- [ ] (4) Antes de restaurar saca un respaldo de la BD actual con motivo "antes de restaurar".
- [ ] (5) Pide escribir el dominio para confirmar; cualquier otra respuesta cancela sin tocar nada.
- [ ] (6) Detiene la app y el importador, restaura, los vuelve a encender y verifica `/health`, informando claro si
      quedó bien.
- [ ] Pruebas contra el Postgres efímero: ciclo real respaldar → restaurar con conteos iguales; cada protección se
      niega cuando corresponde; restaurar un respaldo viejo aplica migraciones.
- [ ] Simulacro real en test.papyrus.com.co: respaldar, cambiar un dato, restaurar, ver el dato de vuelta.
