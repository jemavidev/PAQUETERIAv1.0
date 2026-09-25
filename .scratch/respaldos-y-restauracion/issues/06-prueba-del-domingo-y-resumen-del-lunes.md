# 06 — Prueba del domingo y resumen del lunes

**What to build:** cada domingo de madrugada se restaura automáticamente el último respaldo diario en un Postgres
temporal y aparte (nunca la base real), se compara versión Alembic y conteos con el manifiesto y se destruye el
temporal. Cada lunes llega un resumen por correo aunque todo esté bien: respaldos de la semana, último tamaño, subida a
S3, resultado de la prueba del domingo y espacio en disco. Si la prueba falla, correo inmediato.

**Blocked by:** 02, 05

**Status:** done

- [x] La prueba nunca usa la base real ni sus credenciales, y el temporal se borra aunque falle.
- [x] "OK" significa: restauración sin errores + versión igual al manifiesto + conteos iguales.
- [x] Resumen del lunes con los datos del spec, incluido "N paquetes y M personas recuperados" de la prueba.
- [x] Correo inmediato si la prueba falla.
- [x] Pruebas: prueba OK y fallida (respaldo corrupto o conteos distintos), contenido del resumen.
- [x] Verificado en vivo en test: una prueba real del domingo y un resumen real del lunes (o disparados a mano).

## Comments

**2026-09-25 (PaqueteX `b558516`):** cron domingo `0 9 * * 0` y lunes `0 12 * * 1` (UTC). Disparados a mano en test:
prueba "OK: restauración completa y cuadra con el manifiesto", el Postgres desechable se borró solo; resumen enviado
(dice 0 de 7 porque cubre los 7 días ANTERIORES y los respaldos empezaron ese día -- correcto).
