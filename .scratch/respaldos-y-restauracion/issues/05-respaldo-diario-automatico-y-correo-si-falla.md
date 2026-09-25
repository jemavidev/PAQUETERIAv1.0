# 05 — Respaldo diario automático y correo si falla

**What to build:** el respaldo corre solo todos los días a las 3:00 a. m. hora de Colombia en el servidor, con una
envoltura de cron (candado + registro rotado) como la del importador v1. Si cualquier paso falla (volcado, código,
plantilla, subida a S3, espacio en disco) llega un correo inmediato diciendo qué falló, a los destinatarios de
`RESPALDO_CORREO_AVISOS`. También avisa si el disco pasa del 80 %.

**Blocked by:** 03, 04

**Status:** ready-for-agent

- [ ] Cron instalado en test a las 3:00 a. m. hora de Colombia; una línea por corrida en el registro del servidor.
- [ ] Correo inmediato ante falla, con el paso y el error, a `jveyes@gmail.com` e `info@papyrus.com.co` (variable por
      servidor, lista separada por coma).
- [ ] Aviso por correo si el disco supera el 80 %.
- [ ] Pruebas con el `EmailSender` falso: correo de falla por paso, sin correo cuando todo sale bien, aviso de disco.
- [ ] Verificado en vivo: una corrida nocturna real aparece en S3 y en el registro; una falla provocada genera el
      correo.
