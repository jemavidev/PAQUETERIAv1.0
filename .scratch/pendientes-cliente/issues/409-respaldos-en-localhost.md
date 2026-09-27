# 409 — La pantalla "Respaldos" no funciona en localhost

**Pedido original (Jesús, revisión 2026-09-26 en http://localhost:8010/administracion/respaldos):** "Respaldar ahora:
FALLÓ -- No se pudo iniciar: [Errno 13] Permission denied: '/respaldos'"; "Descargar .zip: no aparece nada";
"La copia de fotos FALLÓ ... Permission denied: '/respaldos'"; "Se descargan solo 2 archivos vacíos";
"Restaurar este respaldo (por SSH): no lo veo".

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Causa

El servidor local (`scripts/paquetex_dev_up.sh`) no define `RESPALDO_DIR` & cía.: cae al default del contenedor
(`/respaldos`, en la raíz del sistema), que en la PC no existe ni se puede crear. En test.papyrus.com.co sí funciona
(simulacro del 2026-09-25). Sin respaldos en la lista, no hay filas que descargar ni comando de restauración que mostrar;
las fotos locales viven en disco (no en S3), así que "copiar de S3" tampoco aplica tal cual.

## Qué se hace

- `paquetex_dev_up.sh`: carpetas locales de respaldos y de copia de fotos, y el checkout del monorepo con la subcarpeta
  `CODE` (la copia del código en local es la de `CODE/`, como en el repo de deploy).
- Fotos en local: copiar desde la carpeta local de fotos en vez de S3.
- Un error de configuración (carpeta inexistente) se explica en la pantalla, no como `Errno 13`.

## Verificación (localhost, 2026-09-26)

Con un admin temporal (borrado después): "Respaldar ahora" → terminó bien (4,1 MB, `.zip` con los 4 archivos, la copia
del código es solo `CODE/`), comando de restauración visible, copia de fotos 6.388 desde la carpeta local, "solo las
nuevas" 7 (justo las 7 registradas que antes figuraban "sin copiar") y "todas" 6.388. Pruebas nuevas: origen de fotos
local y subcarpeta del checkout. En local el comando de restauración se muestra pero `restaurar.sh` es para el servidor
(usa docker compose).

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar en vivo (localhost)". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
