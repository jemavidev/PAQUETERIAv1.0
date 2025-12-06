# Scripts de Testing

Scripts de prueba y verificación del sistema.

## Scripts de Verificación

### verificar_fix_tracking.sh
Script para verificar que el fix de tracking público funciona correctamente.
- Prueba endpoints de tracking sin autenticación
- Verifica que no haya redirecciones a login
- Uso: `./verificar_fix_tracking.sh`

### debug_routes.py
Script para depurar y verificar configuración de rutas públicas y protegidas.
- Lista todas las rutas configuradas
- Verifica configuración de middleware
- Uso: `python debug_routes.py`

## Scripts de Testing SMS

Ver subdirectorio `sms/` para scripts relacionados con pruebas de SMS.

## Scripts de Testing LIWA

Ver subdirectorio `liwa/` para scripts relacionados con pruebas de integración LIWA.

## Nota

Los tests unitarios y de integración están en `CODE/tests/`.
Este directorio contiene scripts de verificación y debugging.
