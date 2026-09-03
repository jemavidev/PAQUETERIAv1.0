# 292 — `docker-compose.yml` no montaba las variables de Meta/PXB al contenedor

**Pedido original (cliente):** "como podemos verificar que al cambiar
datos en el sistema las cosas funcionen o no, y los archivos en el
servidor se editen como se requiere" — verificando de punta a punta el
guardado de una credencial de WhatsApp/Meta contra el servidor real.

**Status:** verificado -- desplegado y confirmado en vivo contra
test.papyrus.com.co (2026-09-03).

## Investigación

1. Confirmado que el allowlist real desplegado (`variables_permitidas()`
   dentro del contenedor) ya incluye las 10 variables nuevas de issue 289
   (`META_*`/`PXB_*`) -- el catálogo se desplegó bien.
2. Aplicado `META_APP_ID=TEST-VERIFICACION-289` vía el mecanismo real
   (`aplicar_credenciales_proveedor`, el mismo que usa el formulario) --
   `.env` del servidor quedó correctamente actualizado.
3. **Pero** `os.environ.get("META_APP_ID")` DENTRO del contenedor seguía
   devolviendo `None` después del reinicio -- la variable nunca llegó al
   proceso de la app.
4. Causa raíz: `docker-compose.yml` (repo de deploy, `jemavidev/PaqueteX`)
   NO usa un `env_file: .env` genérico -- lista cada variable de entorno
   una por una (`LIWA_API_KEY: ${LIWA_API_KEY}`, `AWS_REGION: ${AWS_REGION}`,
   etc.) bajo `services.app.environment`. Las 10 variables de Meta/PXB
   (issue 289) nunca se agregaron a esa lista -- aunque el `.env` en disco
   tenga el valor correcto, Docker Compose no las pasa al contenedor.
5. Efecto práctico: el formulario de WhatsApp muestra "Configuración
   guardada", el `.env` real queda correcto, la auditoría se registra --
   todo parece funcionar -- pero la credencial es INVISIBLE para cualquier
   código que la lea (`os.environ.get(...)`) hasta que se agregue al
   `docker-compose.yml`. No afecta nada hoy (no existe `Sender` real de
   WhatsApp/PBX todavía) pero sí es una brecha real para cuando se
   construya ese módulo.
6. Limpieza: la línea de prueba `META_APP_ID=...` se removió a mano del
   `.env` del servidor (el mecanismo SSH no tiene forma de "desconfigurar"
   una variable, solo de escribirla).

## Fix

Agregar las 10 variables (`META_APP_ID`, `META_PHONE_NUMBER_ID`,
`META_ACCESS_TOKEN`, `META_BUSINESS_ACCOUNT_ID`,
`META_WEBHOOK_VERIFY_TOKEN`, `PXB_HOST`, `PXB_PUERTO`, `PXB_USUARIO`,
`PXB_SECRETO`, `PXB_EXTENSION_ORIGEN`) al `environment:` de `docker-
compose.yml` en el repo de deploy, mismo patrón que las demás.

## Verificación

Desplegado a `test.papyrus.com.co` (commit `729ac0e`, repo de deploy).
Reaplicado `META_APP_ID` de prueba tras el deploy -- esta vez
`os.environ.get("META_APP_ID")` DENTRO del contenedor sí devolvió el valor
real, contenedor recreado limpio, sitio sano (200 en `/entrar`). Línea de
prueba removida del `.env` real al terminar.
