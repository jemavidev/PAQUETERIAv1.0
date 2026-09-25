# 12 — Simulacro completo de punta a punta en test

**What to build:** con todo implementado, una verificación final en test.papyrus.com.co de que el sistema de respaldos
funciona como un todo (pedido de Jesús: "al final también deberías probarlo cuando termines todo").

**Blocked by:** 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11

**Status:** ready-for-agent

- [ ] Respaldo diario real de la madrugada presente en S3 (carpeta correcta) y en el disco (últimas 3).
- [ ] Respaldo "antes de deploy" de un deploy real presente en `puntual/`.
- [ ] Desde la pantalla: "Respaldar ahora", descargar su `.zip` y comprobar las huellas del manifiesto en otra máquina.
- [ ] Restauración completa con `restaurar.sh` a partir de ese `.zip` descargado, con las 6 protecciones ejercidas
      (incluidas al menos una negación de "otro sistema" y una de "versión más nueva").
- [ ] Prueba del domingo y resumen del lunes recibidos en los dos correos.
- [ ] Fotos: copia incremental + "solo las nuevas" + "todas" verificadas contra S3.
- [ ] La llave del servidor confirmada sin permiso de leer ni borrar respaldos.
- [ ] Resultado documentado en este ticket.
