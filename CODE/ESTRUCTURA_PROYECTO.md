# 📂 Estructura del Proyecto - PAQUETES EL CLUB

**Última actualización:** 2025-12-09  
**Versión:** 1.0.0

---

## 🎯 Resumen

Este documento describe la estructura completa del proyecto después de la reorganización.

---

## 📁 Estructura Principal

```
CODE/
├── 📂 src/                     # Código fuente de la aplicación
├── 📂 alembic/                 # Migraciones de base de datos
├── 📂 tests/                   # Tests unitarios e integración
├── 📂 scripts/                 # Scripts de utilidad (ver detalle abajo)
├── 📂 docs/                    # Documentación (ver detalle abajo)
├── 📂 nginx/                   # Configuración Nginx
├── 📂 monitoring/              # Scripts de monitoreo
├── 📂 node_modules/            # Dependencias Node.js
├── 📂 LOCAL/                   # Archivos locales (no en git)
│
├── 📄 .env                     # Variables de entorno (no en git)
├── 📄 .gitignore              # Archivos ignorados por git
├── 📄 alembic.ini             # Configuración Alembic
├── 📄 build-tailwind.sh       # Script para compilar Tailwind
├── 📄 Dockerfile              # Dockerfile principal
├── 📄 Dockerfile.lightsail    # Dockerfile para AWS Lightsail
├── 📄 env.example             # Ejemplo de variables de entorno
├── 📄 package.json            # Dependencias Node.js
├── 📄 package-lock.json       # Lock de dependencias Node.js
├── 📄 README.md               # Documentación principal del proyecto
├── 📄 requirements.txt        # Dependencias Python
├── 📄 tailwind.config.js      # Configuración Tailwind CSS
└── 📄 uvicorn_config.py       # Configuración Uvicorn
```

---

## 📂 Detalle: `/src` - Código Fuente

```
src/
├── app/
│   ├── models/              # Modelos SQLAlchemy (BD)
│   │   ├── customer.py
│   │   ├── customer_otp.py
│   │   ├── customer_preferences.py
│   │   ├── package.py
│   │   ├── notification.py
│   │   └── ...
│   │
│   ├── routes/              # Endpoints de la API
│   │   ├── customer_preferences_otp.py
│   │   ├── customer_portal.py
│   │   ├── packages.py
│   │   └── ...
│   │
│   ├── services/            # Lógica de negocio
│   │   ├── sms_service.py
│   │   ├── email_service.py
│   │   ├── customer_portal_service.py
│   │   └── ...
│   │
│   ├── schemas/             # Esquemas Pydantic
│   │   ├── customer_portal.py
│   │   ├── notification.py
│   │   └── ...
│   │
│   └── utils/               # Utilidades
│       ├── phone_utils.py
│       ├── datetime_utils.py
│       └── ...
│
├── templates/               # Templates HTML (Jinja2)
│   ├── customer_portal/
│   ├── customers/
│   ├── announce/
│   └── ...
│
├── static/                  # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
│
└── main.py                  # Punto de entrada de la aplicación
```

---

## 📂 Detalle: `/scripts` - Scripts de Utilidad

```
scripts/
├── 📂 testing/              # Scripts de pruebas
│   ├── test_sistema_completo_final.py  ⭐ Principal
│   ├── test_otp_*.py
│   ├── test_portal.py
│   └── run_all_tests.sh
│
├── 📂 debug/                # Scripts de debugging
│   ├── debug_*.py
│   ├── diagnostico_*.py
│   ├── check_*.py
│   ├── find_*.py
│   └── get_*.py
│
├── 📂 database/             # Scripts de base de datos
│   ├── create_*.py
│   ├── create_*.sql
│   ├── fix_*.py
│   └── fix_*.sql
│
├── 📂 deployment/           # Scripts de despliegue
├── 📂 maintenance/          # Scripts de mantenimiento
├── 📂 optimization/         # Scripts de optimización
│
├── 📄 README.md             # Documentación de scripts
├── 📄 COMANDOS_RAPIDOS_OTP.sh
├── 📄 restart_server.sh
└── 📄 verify_fix.sh
```

---

## 📂 Detalle: `/docs` - Documentación

```
docs/
├── 📂 analisis/             # Análisis de problemas
│   ├── ANALISIS_FUNCIONALIDAD_OTP.md
│   ├── ANALISIS_IMPACTO_CAMBIOS.md
│   ├── DIAGNOSTICO_OTP_STAGING.md
│   └── ...
│
├── 📂 implementacion/       # Documentación de implementaciones
│   ├── IMPLEMENTACION_OTP_MULTICANAL.md
│   ├── IMPLEMENTACION_OTP_PREFERENCIAS.md
│   ├── MEJORAS_PORTAL_CLIENTES.md
│   ├── ACTUALIZACION_PORTAL_COMPLETO.md
│   └── ...
│
├── 📂 soluciones/           # Soluciones a problemas
│   ├── SOLUCION_FINAL_OTP.md
│   ├── SOLUCION_PREFERENCIAS_NOTIFICACIONES.md
│   ├── CORRECCION_SISTEMA_OTP_FINAL.md
│   └── ...
│
├── 📂 pruebas/              # Reportes de pruebas
│   ├── VERIFICACION_CODIGO_COMPLETA.md        ⭐ Principal
│   ├── RESUMEN_PRUEBAS_SISTEMA.md             ⭐ Principal
│   ├── INSTRUCCIONES_PRUEBAS.md               ⭐ Principal
│   ├── RESUMEN_FINAL_VERIFICACION.txt         ⭐ Principal
│   ├── CHECKLIST_DESPLIEGUE.md
│   └── ...
│
├── 📂 referencias/          # Material de referencia
│   ├── PORTAL_CLIENTES_README.md
│   ├── INVENTARIO_VISTAS_OTP_PORTAL.md
│   ├── liwa_dashboard.html
│   ├── liwa_openapi.json
│   └── ...
│
└── 📄 README.md             # Índice de documentación
```

---

## 🎯 Archivos Principales por Tarea

### 🚀 Para Iniciar el Proyecto
1. `README.md` - Documentación principal
2. `env.example` - Configurar variables de entorno
3. `requirements.txt` - Instalar dependencias
4. `alembic/` - Ejecutar migraciones

### 🧪 Para Ejecutar Pruebas
1. `scripts/testing/test_sistema_completo_final.py` - Pruebas completas
2. `docs/pruebas/INSTRUCCIONES_PRUEBAS.md` - Guía de pruebas
3. `docs/pruebas/RESUMEN_PRUEBAS_SISTEMA.md` - Resumen de pruebas

### 📖 Para Entender el Sistema
1. `docs/pruebas/VERIFICACION_CODIGO_COMPLETA.md` - Verificación técnica
2. `docs/implementacion/IMPLEMENTACION_OTP_PREFERENCIAS.md` - Implementación OTP
3. `docs/referencias/PORTAL_CLIENTES_README.md` - Portal de clientes

### 🐛 Para Debugging
1. `scripts/debug/` - Scripts de debugging
2. `docs/analisis/` - Análisis de problemas
3. `docs/soluciones/` - Soluciones implementadas

### 🚢 Para Despliegue
1. `docs/pruebas/CHECKLIST_DESPLIEGUE.md` - Checklist
2. `Dockerfile` - Configuración Docker
3. `scripts/deployment/` - Scripts de despliegue

---

## 📝 Convenciones

### Nombres de Archivos
- **Documentación:** `MAYUSCULAS_CON_GUIONES.md`
- **Scripts Python:** `snake_case.py`
- **Scripts Bash:** `kebab-case.sh`
- **Código fuente:** `snake_case.py`

### Organización
- **Código de producción:** `/src`
- **Scripts de utilidad:** `/scripts`
- **Documentación:** `/docs`
- **Tests:** `/tests`
- **Configuración:** Raíz del proyecto

---

## 🔍 Búsqueda Rápida

### ¿Dónde está...?

| Busco... | Ubicación |
|----------|-----------|
| Código del sistema OTP | `src/app/routes/customer_preferences_otp.py` |
| Servicio de SMS | `src/app/services/sms_service.py` |
| Servicio de Email | `src/app/services/email_service.py` |
| Modelo de preferencias | `src/app/models/customer_preferences.py` |
| Script de pruebas completo | `scripts/testing/test_sistema_completo_final.py` |
| Verificación del sistema | `docs/pruebas/VERIFICACION_CODIGO_COMPLETA.md` |
| Instrucciones de pruebas | `docs/pruebas/INSTRUCCIONES_PRUEBAS.md` |
| Documentación de implementación | `docs/implementacion/` |
| Scripts de debugging | `scripts/debug/` |
| Templates del portal | `src/templates/customer_portal/` |

---

## ✅ Checklist de Archivos Esenciales

### Configuración
- [x] `.env` (crear desde `env.example`)
- [x] `requirements.txt`
- [x] `package.json`
- [x] `alembic.ini`
- [x] `tailwind.config.js`

### Código Principal
- [x] `src/main.py`
- [x] `src/app/routes/`
- [x] `src/app/services/`
- [x] `src/app/models/`

### Documentación
- [x] `README.md`
- [x] `docs/README.md`
- [x] `docs/pruebas/VERIFICACION_CODIGO_COMPLETA.md`
- [x] `docs/pruebas/INSTRUCCIONES_PRUEBAS.md`

### Scripts
- [x] `scripts/README.md`
- [x] `scripts/testing/test_sistema_completo_final.py`
- [x] `build-tailwind.sh`

---

## 📅 Historial de Cambios

### 2025-12-09 - Reorganización Completa
- ✅ Movidos archivos de documentación a `/docs`
- ✅ Movidos scripts de prueba a `/scripts/testing`
- ✅ Movidos scripts de debug a `/scripts/debug`
- ✅ Movidos scripts de BD a `/scripts/database`
- ✅ Creados READMEs en cada carpeta
- ✅ Actualizado README principal
- ✅ Creado este documento de estructura

---

**Mantenido por:** Equipo de Desarrollo PAQUETES EL CLUB  
**Versión:** 1.0.0
