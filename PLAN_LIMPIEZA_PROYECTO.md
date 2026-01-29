# 🧹 PLAN DE LIMPIEZA DEL PROYECTO MAINV2.1

## 📋 ESTRUCTURA PROPUESTA

```
PAQUETEX v1.0/
├── CODE/                           # Código de la aplicación
├── DOCS/                           # Documentación organizada
│   ├── 00-inicio/                 # Documentos de inicio rápido
│   ├── 01-arquitectura/           # Arquitectura y diseño
│   ├── 02-configuracion/          # Configuración de entornos
│   ├── 03-despliegue/             # Guías de despliegue
│   ├── 04-base-datos/             # Documentación de BD
│   ├── 05-features/               # Documentación de features
│   ├── 06-fixes/                  # Documentación de fixes
│   └── 07-analisis/               # Análisis técnicos
├── scripts/                        # Scripts de utilidad
│   ├── database/                  # Scripts de BD
│   ├── deployment/                # Scripts de deploy
│   ├── staging/                   # Scripts de staging
│   └── maintenance/               # Scripts de mantenimiento
├── .deploy/                        # Sistema de deploy
├── .github/                        # GitHub workflows
├── docker-compose*.yml            # Archivos de Docker
├── deploy.sh                      # Script principal de deploy
└── README.md                      # README principal
```

## 🗂️ CATEGORIZACIÓN DE ARCHIVOS

### 📁 00-inicio/ (Documentos de inicio rápido)
- EMPEZAR_AQUI.txt
- LEEME_PRIMERO.txt
- QUICK_START_STAGING.md
- CUFE_QUICK_START.md
- README.md (principal)

### 📁 01-arquitectura/
- ARQUITECTURA_BASE_DATOS.md
- ANALISIS_COMPLETO_MAINV2.1.md
- ESTRUCTURA_PROYECTO.md
- DIAGRAMA_FLUJO_SINCRONIZACION.md

### 📁 02-configuracion/
- RESUMEN_FINAL_CONFIGURACION.md
- ANALISIS_ENV_CONFIGURACION.md
- ANALISIS_ESTRUCTURA_PROD_VS_STAGING.md
- DIFERENCIAS_STAGING_VS_MAIN.md
- ESTRATEGIA_BASES_DATOS_STAGING.md

### 📁 03-despliegue/
- DEPLOY_STAGING_CHECKLIST.md
- CHECKLIST_DESPLIEGUE.md
- DESPLIEGUE_STAGING_COMPLETADO.md
- VERIFICACION_DEPLOY_STAGING.md
- GUIA_DESARROLLO_LOCALHOST.md
- DESPLIEGUE_INDICADOR_COMPLETADO.md

### 📁 04-base-datos/
- ANALISIS_CONEXIONES_DB_COMPLETO.md
- ANALISIS_STAGING_ACTUAL.md
- GUIA_CREACION_DB_STAGING.md
- INSTRUCCIONES_CREAR_DB_STAGING.md
- MIGRACION_EJECUTADA_*.md

### 📁 05-features/
- IMPLEMENTACION_TAB_CUFE.md
- BOTON_ELIMINAR_CUFE_AGREGADO.md
- BOTON_SINCRONIZACION_STAGING.md
- INDICADOR_ENTORNO_IMPLEMENTADO.md
- NOTIFICACIONES_CSS_IMPLEMENTADAS.md
- MEJORAS_TABLA_FACTURAS.md

### 📁 06-fixes/
- FIX_*.md
- SOLUCION_*.md
- CONTEXTO_FIX_*.md
- COLUMNA_CALIDAD_REMOVIDA.md
- FACTURAS_*.md
- LIMPIEZA_*.md

### 📁 07-analisis/
- ANALISIS_*.md (todos los análisis técnicos)
- RESUMEN_*.md (resúmenes de implementaciones)

### 📁 scripts/database/
- *.py (scripts de BD)
- *.sql (scripts SQL)
- *.sh (scripts de BD)

### 📁 scripts/deployment/
- deploy.sh
- *.sh (scripts de deploy)

### 📁 scripts/staging/
- sync_*.py
- sync_*.sh
- diagnostico_*.sh
- verificar_*.sh

### 📁 scripts/maintenance/
- limpiar_*.py
- corregir_*.py
- reprocesar_*.py

### 🗑️ ARCHIVOS A ELIMINAR (Temporales/Duplicados)
- COMANDOS_*.txt
- EJECUTAR_*.txt
- INSTALAR_*.txt
- LEEME_FIX_*.txt
- COPIAR_Y_PEGAR.sh
- APLICAR_SOLUCION_SIMPLE.txt
- Archivos de prueba temporales
- Backups antiguos

## 🎯 ACCIONES A REALIZAR

1. ✅ Crear estructura de carpetas
2. ✅ Mover archivos de documentación
3. ✅ Mover scripts
4. ✅ Eliminar archivos temporales
5. ✅ Actualizar README principal
6. ✅ Crear índices en cada carpeta
7. ✅ Commit de limpieza
