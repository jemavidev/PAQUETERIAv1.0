# 🛠️ Scripts del Proyecto

Esta carpeta contiene todos los scripts de utilidad del proyecto organizados por categorías.

## 📁 Estructura

### `/testing`
Scripts para ejecutar pruebas del sistema:
- `test_sistema_completo_final.py` - Pruebas automatizadas completas del sistema OTP y preferencias
- `test_*.py` - Scripts de pruebas específicas
- `test_*.sh` - Scripts bash para pruebas
- `run_all_tests.sh` - Ejecuta todas las pruebas

### `/debug`
Scripts para debugging y diagnóstico:
- `debug_*.py` - Scripts de debugging
- `diagnostico_*.py` - Scripts de diagnóstico
- `check_*.py` - Scripts de verificación
- `find_*.py` - Scripts de búsqueda
- `get_*.py` - Scripts para obtener información
- `solicitar_*.py` - Scripts para solicitar datos

### `/database`
Scripts relacionados con la base de datos:
- `create_*.py` - Scripts para crear tablas/datos
- `create_*.sql` - Scripts SQL de creación
- `fix_*.py` - Scripts para corregir datos
- `fix_*.sql` - Scripts SQL de corrección

### Raíz (`/scripts`)
Scripts generales de utilidad:
- `COMANDOS_RAPIDOS_OTP.sh` - Comandos rápidos para OTP
- `restart_server.sh` - Reiniciar servidor
- `verify_fix.sh` - Verificar correcciones
- `build-tailwind.sh` - Compilar Tailwind CSS

## 🚀 Scripts Principales

### Pruebas Completas del Sistema
```bash
python3 scripts/testing/test_sistema_completo_final.py
```
Ejecuta pruebas automatizadas de:
- Autenticación OTP
- Gestión de preferencias
- Bloqueo de notificaciones
- Acceso al portal

### Verificar Estado del Sistema
```bash
bash scripts/debug/check_preferencias_staging.sh
```
Verifica el estado de las preferencias en staging.

### Crear Tablas de Base de Datos
```bash
python3 scripts/database/create_customer_otps_table.py
```
Crea las tablas necesarias para el sistema OTP.

## 📝 Notas

- Los scripts de prueba requieren `httpx`: `pip install httpx`
- Los scripts de base de datos requieren acceso a la BD
- Los scripts bash requieren permisos de ejecución: `chmod +x script.sh`

## 🔒 Seguridad

- NO ejecutar scripts de producción en desarrollo
- Verificar variables de entorno antes de ejecutar
- Hacer backup antes de ejecutar scripts de base de datos

## 📅 Última Actualización

**Fecha:** 2025-12-09  
**Versión:** 1.0.0
