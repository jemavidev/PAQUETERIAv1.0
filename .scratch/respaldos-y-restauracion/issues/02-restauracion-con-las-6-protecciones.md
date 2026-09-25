# 02 — Restauración con las 6 protecciones

**What to build:** `restaurar.sh <carpeta-del-respaldo>`, por SSH, que restaura un respaldo sobre el mismo sistema y se
niega a hacer algo peligroso. El script es delgado (detiene/enciende contenedores y el cron del importador, pide la
confirmación); las protecciones y la restauración viven en el módulo de respaldos para poder probarlas.

**Blocked by:** 01

**Status:** done

- [x] (1) Verifica las huellas del manifiesto; si algo no coincide, no toca nada y dice qué archivo falla.
- [x] (2) Se niega si el dominio/conjunto del manifiesto no es el del servidor destino, salvo `--otro-destino`.
- [x] (3) Se niega si la BD del respaldo es más nueva que el código instalado y dice que se despliegue primero el
      `sistema.tar.gz` de ese respaldo; si es más vieja, restaura y aplica las migraciones pendientes.
- [x] (4) Antes de restaurar saca un respaldo de la BD actual con motivo "antes de restaurar".
- [x] (5) Pide escribir el dominio para confirmar; cualquier otra respuesta cancela sin tocar nada.
- [x] (6) Detiene la app y el importador, restaura, los vuelve a encender y verifica `/health`, informando claro si
      quedó bien.
- [x] Pruebas contra el Postgres efímero: ciclo real respaldar → restaurar con conteos iguales; cada protección se
      niega cuando corresponde; restaurar un respaldo viejo aplica migraciones.
- [x] Simulacro real en test.papyrus.com.co: respaldar, cambiar un dato, restaurar, ver el dato de vuelta.

## Comments

**2026-09-25 (implementado, PaqueteX `1b04fe0`):** simulacro real en test.papyrus.com.co: respaldo `2026-09-25_111616_a_pedido`,
marcador insertado (motivo de bloqueo "PRUEBA-RESTAURACION"), confirmación equivocada ("elclub.papyrus.com.co") →
NO se restauró y el sistema siguió respondiendo; confirmación correcta → "LISTO: restaurado y el sistema responde",
marcador 1 → 0, copia `..._antes_de_restaurar` creada, sitio 200. Ajuste encontrado en vivo: el contenedor de un solo
uso se tragaba la entrada del script (confirmación por tubería) → `</dev/null` en sus llamadas.
