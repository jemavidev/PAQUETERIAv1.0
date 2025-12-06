# Organización de Archivos del Proyecto

Última actualización: 2024-12-06

## Estructura de Directorios

### `/DOCS/` - Documentación
Toda la documentación del proyecto organizada por categorías:

- **`01-proyecto/`** - Documentación general del proyecto
- **`02-deploy/`** - Documentación de despliegue y comandos
  - `COMANDOS_STAGING.txt` - Comandos útiles para staging
- **`03-sms/`** - Documentación de SMS y notificaciones
  - `FIX_SMS_CARACTERES_INVALIDOS.md`
- **`04-fixes/`** - Documentación de fixes y correcciones
  - `FIX_TRACKING_REDIRECT.md` - Fix de tracking público
  - `RESUMEN_FIX_TRACKING.md` - Resumen del fix
  - `FIX_REDIRECT_PORTAL.md` - Fix de redirecciones
  - `README.md` - Índice de todos los fixes
- **`05-legal/`** - Documentación legal (términos, privacidad, etc.)
- **`06-testing/`** - Documentación de testing
- **`07-analisis/`** - Análisis y diagnósticos
- **`guias/`** - Guías de uso y procedimientos
  - `INSTRUCCIONES_RAPIDAS.md` - Guía rápida de procedimientos

### `/CODE/scripts/` - Scripts del Proyecto
Scripts organizados por función:

- **`deployment/`** - Scripts de despliegue
  - `EJECUTAR_EN_STAGING.sh` - Script de despliegue a staging
- **`testing/`** - Scripts de testing y verificación
  - `verificar_fix_tracking.sh` - Verificar fix de tracking
  - `debug_routes.py` - Debug de rutas
  - `README.md` - Documentación de scripts de testing
- **`maintenance/`** - Scripts de mantenimiento
- **`optimization/`** - Scripts de optimización

### `/CODE/tests/` - Tests Unitarios
Tests automatizados del proyecto:

- `test_public_routes_fix.py` - Tests del fix de rutas públicas
- `e2e/` - Tests end-to-end
- `run_tests.sh` - Script para ejecutar todos los tests

### Raíz del Proyecto
Solo archivos esenciales:

- `README.md` - Documentación principal
- `deploy.sh` - Script principal de despliegue
- `docker-compose.*.yml` - Configuraciones de Docker
- `.env` - Variables de entorno
- `COMMIT_SUMMARY.md` - Resumen de commits recientes

## Convenciones

### Documentación (`.md`)
- **Fixes**: `DOCS/04-fixes/`
- **Guías**: `DOCS/guias/`
- **Deploy**: `DOCS/02-deploy/`
- **SMS**: `DOCS/03-sms/`

### Scripts (`.sh`, `.py`)
- **Deployment**: `CODE/scripts/deployment/`
- **Testing**: `CODE/scripts/testing/`
- **Maintenance**: `CODE/scripts/maintenance/`

### Tests
- **Unit tests**: `CODE/tests/`
- **E2E tests**: `CODE/tests/e2e/`

## Reglas de Organización

1. **No dejar archivos sueltos en la raíz** - Solo archivos esenciales del proyecto
2. **Documentar en DOCS/** - Toda documentación va en subdirectorios organizados
3. **Scripts en CODE/scripts/** - Organizados por función
4. **Tests en CODE/tests/** - Tests automatizados
5. **Cada directorio debe tener README.md** - Explicando su contenido

## Archivos Recientes Organizados (2024-12-06)

### Fix de Tracking Público
- ✅ `FIX_TRACKING_REDIRECT.md` → `DOCS/04-fixes/`
- ✅ `RESUMEN_FIX_TRACKING.md` → `DOCS/04-fixes/`
- ✅ `verificar_fix_tracking.sh` → `CODE/scripts/testing/`
- ✅ `test_public_routes_fix.py` → `CODE/tests/`
- ✅ `debug_routes.py` → `CODE/scripts/testing/`

### Otros
- ✅ `INSTRUCCIONES_RAPIDAS.md` → `DOCS/guias/`
- ✅ `FIX_SMS_CARACTERES_INVALIDOS.md` → `DOCS/03-sms/`
- ✅ `FIX_REDIRECT_PORTAL.md` → `DOCS/04-fixes/`
- ✅ `COMANDOS_STAGING.txt` → `DOCS/02-deploy/`
- ✅ `EJECUTAR_EN_STAGING.sh` → `CODE/scripts/deployment/`
