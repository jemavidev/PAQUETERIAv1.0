# 05 — Respaldo diario automático y correo si falla

**What to build:** el respaldo corre solo todos los días a las 3:00 a. m. hora de Colombia en el servidor, con una
envoltura de cron (candado + registro rotado) como la del importador v1. Si cualquier paso falla (volcado, código,
plantilla, subida a S3, espacio en disco) llega un correo inmediato diciendo qué falló, a los destinatarios de
`RESPALDO_CORREO_AVISOS`. También avisa si el disco pasa del 80 %.

**Blocked by:** 03, 04

**Status:** done

- [x] Cron instalado en test a las 3:00 a. m. hora de Colombia; una línea por corrida en el registro del servidor.
- [x] Correo inmediato ante falla, con el paso y el error, a `jveyes@gmail.com` e `info@papyrus.com.co` (variable por
      servidor, lista separada por coma).
- [x] Aviso por correo si el disco supera el 80 %.
- [x] Pruebas con el `EmailSender` falso: correo de falla por paso, sin correo cuando todo sale bien, aviso de disco.
- [x] Verificado en vivo: una corrida nocturna real aparece en S3 y en el registro; una falla provocada genera el
      correo.

## Comments

**2026-09-25 (PaqueteX `b558516`):** cron instalado en test con `scripts/respaldos/instalar_cron.sh` (bloque idempotente
junto al del importador): diario `0 8 * * *` UTC = 3:00 a. m. Colombia. Corrida manual del diario subida a
`diario/`. Falla provocada (bucket inexistente) → paso «subida a S3», historial con `ok: false`, envío SMTP aceptado sin
error hacia `jveyes@gmail.com` e `info@papyrus.com.co` -- la llegada al buzón la confirma Jesús (el Gmail conectado a la
sesión es otro). Aviso de disco > 80 % cubierto por prueba (el disco de test está al 23 %).
