# 🚀 Infraestructura de Staging - PAQUETEX

## 📋 Descripción

Sistema completo para gestionar el ambiente de staging de PAQUETEX, incluyendo:
- Creación de base de datos staging
- Sincronización desde producción
- Gestión de migraciones
- Verificación de estado
- Limpieza y mantenimiento

## 🗄️ Bases de Datos

### Producción
- **Base de datos**: `paqueteria_v4`
- **Host**: AWS RDS (us-east-1)
- **Uso**: Solo lectura para sincronización

### Staging
- **Base de datos**: `paqueteria_staging`
- **Host**: Mismo servidor AWS RDS
- **Uso**: Ambiente de pruebas

## 📁 Estructura de Scripts

```
scripts/staging/
├── README.md                    # Este archivo
├── 01_create_staging_db.py      # Crear base de datos staging
├── 02_init_schema.py            # Inicializar esquema (tablas)
├── 03_sync_from_production.py   # Sincronizar datos desde producción
├── 04_verify_staging.py         # Verificar estado de staging
├── 05_cleanup_staging.py        # Limpiar datos de prueba
├── utils/
│   ├── db_connection.py         # Utilidades de conexión
│   └── sync_helpers.py          # Helpers de sincronización
└── docker/
    └── docker-compose.staging.yml  # Docker compose para staging
```

## 🚀 Guía de Uso Rápida

### 1. Crear Base de Datos Staging (Primera vez)

```bash
python scripts/staging/01_create_staging_db.py
```

### 2. Inicializar Esquema

```bash
python scripts/staging/02_init_schema.py
```

### 3. Sincronizar Datos desde Producción

```bash
python scripts/staging/03_sync_from_production.py
```

### 4. Verificar Estado

```bash
python scripts/staging/04_verify_staging.py
```

### 5. Limpiar Datos de Prueba

```bash
python scripts/staging/05_cleanup_staging.py
```

## 🐳 Uso con Docker

### Levantar Staging

```bash
cd scripts/staging/docker
docker-compose -f docker-compose.staging.yml up -d
```

### Ver Logs

```bash
docker-compose -f docker-compose.staging.yml logs -f app
```

### Detener Staging

```bash
docker-compose -f docker-compose.staging.yml down
```

## ⚙️ Variables de Entorno

Asegúrate de tener configurado `.env.staging` en la raíz del proyecto:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/paqueteria_staging
PROD_DATABASE_URL=postgresql://user:pass@host:5432/paqueteria_v4
ENVIRONMENT=staging
DEBUG=True
```

## 🔒 Seguridad

- ⚠️ **NUNCA** ejecutar scripts de sincronización en producción
- ✅ Los scripts verifican el ambiente antes de ejecutar
- ✅ Producción siempre es de solo lectura
- ✅ Staging puede ser sobrescrito sin afectar producción

## 📊 Flujo de Trabajo Recomendado

1. **Desarrollo Local** → Pruebas iniciales
2. **Staging** → Pruebas con datos reales (copia de producción)
3. **Producción** → Deploy final

## 🛠️ Mantenimiento

### Sincronización Regular

Se recomienda sincronizar staging con producción:
- Semanalmente para datos actualizados
- Antes de probar features importantes
- Después de cambios en el esquema

### Limpieza

Limpiar datos de prueba regularmente:
- Después de cada ciclo de testing
- Antes de sincronizar desde producción

## 📞 Soporte

Para problemas o dudas:
1. Revisar logs: `docker-compose logs`
2. Verificar estado: `04_verify_staging.py`
3. Consultar documentación del proyecto

## 🔄 Actualizaciones

Última actualización: 2026-01-29
Versión: 1.0.0
