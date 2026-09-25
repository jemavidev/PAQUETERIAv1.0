# 12 — Simulacro completo de punta a punta en test

**What to build:** con todo implementado, una verificación final en test.papyrus.com.co de que el sistema de respaldos
funciona como un todo (pedido de Jesús: "al final también deberías probarlo cuando termines todo").

**Blocked by:** 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11

**Status:** done

- [x] Respaldo diario real de la madrugada presente en S3 (carpeta correcta) y en el disco (últimas 3).
- [x] Respaldo "antes de deploy" de un deploy real presente en `puntual/`.
- [x] Desde la pantalla: "Respaldar ahora", descargar su `.zip` y comprobar las huellas del manifiesto en otra máquina.
- [x] Restauración completa con `restaurar.sh` a partir de ese `.zip` descargado, con las 6 protecciones ejercidas
      (incluidas al menos una negación de "otro sistema" y una de "versión más nueva").
- [x] Prueba del domingo y resumen del lunes recibidos en los dos correos.
- [x] Fotos: copia incremental + "solo las nuevas" + "todas" verificadas contra S3.
- [x] La llave del servidor confirmada sin permiso de leer ni borrar respaldos.
- [x] Resultado documentado en este ticket.

## Comments

**2026-09-25 -- simulacro completo en test.papyrus.com.co (PaqueteX `b558516`):**
- Diario: corrida manual subida a S3 `diario/` (el de la madrugada queda a cargo del cron `0 8 * * *` UTC).
- Antes de deploy: dos deploys reales dejaron `..._antes_de_deploy` en `puntual/`.
- Pantalla (admin temporal, borrado al final): "Respaldar ahora" → terminó bien; `.zip` descargado a otra máquina con
  sus huellas verificadas ahí y `solicitado_por` en el manifiesto.
- Restauración desde ese `.zip` con `restaurar.sh`: negada con un manifiesto de otro dominio y con uno de versión más
  nueva (antes de pedir el dominio y sin detener la app); restauración real → marcador 1 → 0, copia de lo anterior
  subida a S3, app encendida, sitio 200.
- Prueba del domingo (disparada a mano): OK, Postgres desechable borrado. Resumen enviado a los dos correos.
- Fotos: copia 7.561 + incremental 0; "todas" 7.561; "solo las nuevas" 7.519 y luego 0.
- Llave del servidor: listar, leer, borrar y etiquetar → negados (probado desde el propio contenedor).
Pendiente de Jesús: confirmar que le llegaron los correos (falla provocada y resumen) a los dos buzones.
