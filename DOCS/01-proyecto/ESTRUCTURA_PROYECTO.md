# 📁 Estructura del Proyecto PAQUETEX

## 🎯 Estructura Reorganizada

```
PAQUETERIA v1.0/
│
├── 📂 CODE/                          # Código fuente principal
│   ├── 📂 src/                       # Código de la aplicación
│   ├── 📂 scripts/                   # Scripts organizados
│   │   ├── 📂 maintenance/           # Scripts de mantenimiento
│   │   ├── 📂 optimization/          # Scripts de optimización
│   │   ├── 📂 testing/               # Scripts de testing
│   │   │   ├── 📂 sms/              # Tests de SMS
│   │   │   └── 📂 liwa/             # Tests de Liwa API
│   │   └── 📂 deployment/            # Scripts de deployment antiguos
│   ├── 📂 alembic/                   # Migraciones de BD
│   ├── 📂 nginx/                     # Configuración Nginx
│   ├── 📂 monitoring/                # Monitoreo
│   ├── Dockerfile                    # Docker principal
│   ├── requirements.txt              # Dependencias Python
│   └── alembic.ini                   # Config de Alembic
│
├── 📂 DOCS/                          # Documentación
│   ├── ORGANIZACION_PROYECTO.md      # Organización del proyecto
│   ├── README_DEPLOY.md              # Documentación de deploy
│   └── ESTRUCTURA_PROYECTO.md        # Este archivo
│
├── 📂 .deploy/                       # Sistema de deploy
│   ├── 📂 config/                    # Configuraciones de entornos
│   ├── 📂 lib/                       # Librerías del sistema
│   ├── 📂 docs/                      # Documentación del deploy
│   ├── 📂 hooks/                     # Hooks de deploy
│   └── 📂 templates/                 # Templates
│
├── 📂 scripts/                       # Scripts del proyecto raíz
│
├── 📄 deploy.sh                      # Script principal de deploy
├── 📄 docker-compose.*.yml           # Configuraciones Docker
├── 📄 README.md                      # README principal
└── 📄 .env                           # Variables de entorno

```

## 📋 Archivos Reorganizados

### ✅ Movidos a `CODE/scripts/maintenance/`
- `cleanup_database.py` - Limpieza de base de datos
- `clear_cache.py` - Limpieza de caché
- `performance_monitor.py` - Monitor de rendimiento
- `fix_deliver_function.py` - Corrección de función de entrega
- `check_announcements.py` - Verificación de anuncios

### ✅ Movidos a `CODE/scripts/optimization/`
- `optimize_database.sql` - Optimización de BD
- `optimize_customers_query.sql` - Optimización de consultas
- `optimize_deliver.js` - Optimización de entregas

### ✅ Movidos a `CODE/scripts/testing/`
- Scripts de testing de SMS → `testing/sms/`
- Scripts de testing de Liwa → `testing/liwa/`
- Scripts de pruebas generales

### ✅ Movidos a `DOCS/`
- `ORGANIZACION_PROYECTO.md`
- `README_DEPLOY.md`

## 🎯 Archivos Esenciales (No Movidos)

### Raíz del Proyecto
- `deploy.sh` - Script principal de deploy
- `docker-compose.*.yml` - Configuraciones Docker
- `README.md` - Documentación principal
- `.env` - Variables de entorno
- `.gitignore` - Configuración Git

### CODE/
- `Dockerfile` - Imagen Docker
- `requirements.txt` - Dependencias
- `alembic.ini` - Configuración de migraciones
- `.env` - Variables de entorno del código
- `env.example` - Ejemplo de variables

## 📝 Notas Importantes

1. **No se rompió el proyecto**: Todos los archivos esenciales permanecen en su lugar
2. **Mejor organización**: Scripts agrupados por función
3. **Fácil navegación**: Estructura clara y documentada
4. **Deployment intacto**: Sistema de deploy funcional

## 🚀 Próximos Pasos

1. Actualizar referencias a scripts movidos (si las hay)
2. Revisar y limpiar scripts antiguos de deployment
3. Documentar cada categoría de scripts
4. Considerar eliminar scripts obsoletos

## 📞 Contacto

Para dudas sobre la estructura, consultar con el equipo de desarrollo.
