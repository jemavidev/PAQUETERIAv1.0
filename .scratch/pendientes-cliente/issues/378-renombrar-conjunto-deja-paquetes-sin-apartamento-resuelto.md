# 378 — Renombrar el Conjunto dejaba a los paquetes existentes "sin apartamento resuelto"

**Reporte original (Jesús), tras [[377]]:** "para este paquete '7JY7' sigue mostrando este mensaje 'Este paquete no
tiene apartamento resuelto en su snapshot.'"

**Status:** implementado, pendiente confirmar en vivo

## Diagnóstico

7JY7 SÍ tiene apartamento (snapshot `EL CLUB` · `TORRE 4` · `806`, ANUNCIADO, dato demo `+57399…`), y esa unidad
existe en el catálogo -- pero como `EL CLUB APARTAMENTOS`. El Conjunto se renombró en `/administracion/conjunto`:
`renombrar_conjunto` (`configuracion_conjunto_service.py`) actualiza `Apartamento.conjunto`, pero NO
`Paquete.snapshot_conjunto`. Toda búsqueda por la terna del snapshot (`buscar_apartamento_por_terna`: candidatos de
Corregir/Recibir, "Nuevo residente", hermanos, promoción a Principal, ~10 lugares) deja de encontrar la unidad en los
paquetes anteriores al renombre. En la BD dev: 1569 paquetes con `EL CLUB`, 11 con el nombre nuevo. El fix del [[377]]
no lo cubría porque el paquete SÍ tiene los 3 campos del snapshot.

## Decisiones

1. `renombrar_conjunto` propaga el nombre nuevo también a `Paquete.snapshot_conjunto` (todos los estados). Renombrar
   el Conjunto es re-etiquetar el MISMO lugar, no una Persona que se muda -- no es lo que ADR-0001 protege; se
   documenta como excepción 4 en el ADR.
2. Migración de datos: si el catálogo tiene un único Conjunto, los paquetes con otro `snapshot_conjunto` (no nulo)
   pasan a ese nombre. Con más de un Conjunto no toca nada.
3. Refuerzo del [[377]]: en Recibir, un snapshot cuya unidad no se encuentra en el catálogo cuenta como "sin
   apartamento" -- se recibe igual, nunca se bloquea con ese mensaje.

## Verificación

- `tests/data_model/test_configuracion_conjunto_service.py`: el renombre propaga a los paquetes (y la terna vuelve a
  encontrar su unidad); no toca paquetes sin apartamento; la migración realinea un paquete desfasado.
- `tests/web/test_recibir_sin_apartamento.py`: tras renombrar, "Nuevo residente" registra al Ocupante en la unidad del
  paquete; un snapshot con un Conjunto que el catálogo no tiene se recibe igual (también se ajustó el bloqueo del
  issue 189, que miraba solo los 3 campos del snapshot). Las 4 nuevas fallaban antes del cambio.
- Regresión: `test_packages`, `test_admin_conjunto`, `test_announce_new`, `test_migration_graph` (377) en verde.
- BD dev: `alembic upgrade head` aplicó `0057`; 1580 paquetes con apartamento ahora en `EL CLUB APARTAMENTOS`
  (antes 1569 en `EL CLUB`), 7JY7 incluido. ADR-0001: excepción 4 documentada.
- Al desplegar, la migración corre sola (si producción también tuvo un renombre, lo corrige igual).
