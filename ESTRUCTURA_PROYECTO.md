# 📁 Estructura del Proyecto - PAQUETEX v4.0

**Fecha:** 2024-11-30  
**Versión:** 4.0  
**Organización:** Archivos reorganizados para mejor mantenibilidad

---

## 📂 Estructura de Carpetas

```
PAQUETERIA v1.0/
├── CODE/                           # Código fuente de la aplicación
│   ├── src/                        # Código Python y templates
│   ├── alembic/                    # Migraciones de base de datos
│   ├── package.json                # Configuración npm (Tailwind)
│   ├── tailwind.config.js          # Configuración Tailwind CSS
│   └── Dockerfile                  # Imagen Docker
│
├── DOCS/                           # Documentación organizada
│   ├── deployment/                 # Documentos de deployment
│   ├── fixes/                      # Documentación de fixes
│   ├── features/                   # Documentación de features
│   ├── testing/                    # Documentación de pruebas
│   ├── staging/                    # Documentación de staging
│   └── instructions/               # Instrucciones y guías
│
├── scripts/                        # Scripts organizados
│   ├── deployment/                 # Scripts de deployment
│   ├── fixes/                      # Scripts de fixes
│   ├── testing/                    # Scripts de pruebas
│   └── diagnostics/                # Scripts de diagnóstico
│
├── .deploy/                        # Sistema de deployment
├── .github/                        # GitHub workflows
├── docker-compose.*.yml            # Configuraciones Docker
├── deploy.sh                       # Script principal de deployment
└── README.md                       # Documentación principal
```

---

## 📋 DOCS/ - Documentación

### deployment/
Documentos relacionados con deployments:
- `DEPLOYMENT_COMPLETADO_2024-11-30.md`
- `DEPLOYMENT_FINAL_COMPLETADO.md`

### fixes/
Documentación de problemas resueltos:
- `FIX_ALTO_CPU_FOOTERS.md` - Fix de CPU alto en footers
- `FIX_BROWSER_FREEZE_2024-11-29.md` - Fix de freeze del navegador
- `FIX_FAVICON_404.md` - Fix de favicon 404
- `RESUMEN_FIX_CPU_2024-11-30.md` - Resumen fix CPU
- `SOLUCION_DEVTOOLS_MOVIL.md` - Solución DevTools móvil
- `SOLUCION_ERROR_502.md` - Solución error 502
- `SOLUCION_SCROLL_MOBILE_RESUMEN.md` - Solución scroll móvil
- `SOLUCION_FINAL_CPU_TAILWIND.md` - Solución final CPU Tailwind

### features/
Documentación de features implementadas:
- `FOOTER_AUTENTICADO_ACTUALIZADO.md` - Footer autenticado
- `FOOTER_AUTENTICADO_IMPLEMENTADO.md` - Implementación footer
- `FOOTER_PAQUETES_DESTACADO.md` - Footer paquetes
- `ANALISIS_SCROLL_MOBILE.md` - Análisis scroll móvil
- `DETECCION_INTELIGENTE_MOBILE.md` - Detección móvil
- `REFACTOR_COMPLETADO_FINAL.md` - Refactor final
- `WHATSAPP_LINK_ACTUALIZADO.md` - Link WhatsApp

### testing/
Documentación de pruebas:
- `CHECKLIST_PRUEBAS.md` - Checklist general
- `CHECKLIST_RAPIDO_STAGING.md` - Checklist rápido
- `PLAN_PRUEBAS_STAGING_2024-11-29.md` - Plan de pruebas
- `PRUEBAS_SCROLL_MOBILE.md` - Pruebas scroll
- `PRUEBAS_STAGING_2024-11-29.md` - Pruebas staging
- `RESUMEN_PRUEBAS_STAGING.md` - Resumen pruebas
- `VERIFICACION_FINAL.md` - Verificación final

### staging/
Documentación específica de staging:
- `FLUJO_TRABAJO_GITHUB_STAGING.md` - Flujo de trabajo
- `LEEME_PRIMERO_STAGING.md` - Guía inicial
- `MERGE_COMPLETADO_2024-11-29.md` - Merge completado
- `NUEVO_SERVIDOR_STAGING.md` - Nuevo servidor
- `SETUP_STAGING_COMANDOS.md` - Comandos setup
- `STAGING_CONFIGURADO.md` - Configuración
- `REVERT_FOOTERS_COMPLETADO.md` - Revert footers

### instructions/
Instrucciones y guías:
- `INSTRUCCIONES_FINALES_DEPLOYMENT.md` - Deployment
- `INSTRUCCIONES_LIMPIAR_CACHE_MOBILE.md` - Limpiar caché
- `INSTRUCCIONES_RAPIDAS_SCROLL.md` - Scroll rápido
- `TAILWIND_LOCAL_INSTALACION.md` - Instalación Tailwind
- `VERIFICACION_RUTAS_DOCKER.md` - Rutas Docker
- `RESUMEN_TAILWIND_LOCAL_FINAL.md` - Resumen Tailwind

### Raíz de DOCS/
Documentos de fases del proyecto:
- `FASE1_COMPLETADA.md`
- `FASE2_COMPLETADA.md`
- `FASE3_COMPLETADA.md`
- `FASE4_COMPLETADA.md`
- `API_LIWA_REFERENCIA.md`

---

## 🔧 scripts/ - Scripts

### deployment/
Scripts de deployment:
- `rebuild-staging.sh` - Rebuild staging
- `reset-staging-from-github.sh` - Reset desde GitHub

### fixes/
Scripts de fixes:
- `fix-browser-freeze.sh` - Fix freeze navegador
- `fix-footer-logs.sh` - Fix logs footer
- `fix-footer-mobile-ahora.sh` - Fix footer móvil
- `fix-mobile-cache-staging.sh` - Fix caché móvil
- `force-cache-clear.sh` - Limpiar caché forzado

### testing/
Scripts de pruebas:
- `pruebas-manuales-interactivas.sh` - Pruebas interactivas
- `test-staging-commits.sh` - Test commits staging
- `verificar-fix-movil.sh` - Verificar fix móvil
- `verificar-footer-autenticado.sh` - Verificar footer
- `verificar-footer-v2.sh` - Verificar footer v2
- `verificar-paquetes-destacado.sh` - Verificar paquetes

### diagnostics/
Scripts de diagnóstico:
- `diagnostico-502-staging.sh` - Diagnóstico 502
- `diagnostico-staging.sh` - Diagnóstico general

---

## 📄 Archivos en Raíz

### Archivos Principales:
- `README.md` - Documentación principal del proyecto
- `deploy.sh` - Script principal de deployment
- `.env` - Variables de entorno
- `.gitignore` - Archivos ignorados por git

### Docker Compose:
- `docker-compose.dev.yml` - Desarrollo local
- `docker-compose.staging.yml` - Staging
- `docker-compose.prod.yml` - Producción
- `docker-compose.lightsail.yml` - AWS Lightsail

### Archivos de Sistema:
- `.deploy-current` - Deployment actual
- `.deploy-history` - Historial de deployments
- `.cursorrules` - Reglas de Cursor
- `.cursorignore` - Ignorar en Cursor

---

## 🎯 Beneficios de la Organización

### Antes:
- ❌ 70 archivos en la raíz
- ❌ Difícil encontrar documentación
- ❌ Scripts mezclados
- ❌ Desorganizado

### Después:
- ✅ Archivos organizados por categoría
- ✅ Fácil encontrar documentación
- ✅ Scripts agrupados por función
- ✅ Estructura clara y mantenible

---

## 🔍 Cómo Encontrar Archivos

### Buscar documentación de un fix:
```bash
ls DOCS/fixes/
```

### Buscar scripts de deployment:
```bash
ls scripts/deployment/
```

### Buscar pruebas:
```bash
ls DOCS/testing/
ls scripts/testing/
```

### Buscar instrucciones:
```bash
ls DOCS/instructions/
```

---

## 📝 Convenciones

### Documentación (DOCS/):
- **deployment/** - Documentos de deployments realizados
- **fixes/** - Documentación de problemas y soluciones
- **features/** - Documentación de features implementadas
- **testing/** - Planes y resultados de pruebas
- **staging/** - Documentación específica de staging
- **instructions/** - Guías e instrucciones paso a paso

### Scripts (scripts/):
- **deployment/** - Scripts para hacer deployments
- **fixes/** - Scripts para aplicar fixes
- **testing/** - Scripts para ejecutar pruebas
- **diagnostics/** - Scripts para diagnosticar problemas

---

## 🚀 Comandos Útiles

### Ver estructura:
```bash
tree -L 2 -d
```

### Buscar documentación:
```bash
find DOCS -name "*.md" | grep -i "keyword"
```

### Buscar scripts:
```bash
find scripts -name "*.sh" | grep -i "keyword"
```

### Listar por categoría:
```bash
ls DOCS/fixes/        # Fixes
ls DOCS/features/     # Features
ls scripts/testing/   # Scripts de pruebas
```

---

## ✅ Archivos NO Movidos (Vitales)

Estos archivos permanecen en la raíz porque son esenciales:
- `README.md` - Documentación principal
- `deploy.sh` - Script principal de deployment
- `docker-compose.*.yml` - Configuraciones Docker
- `.env` - Variables de entorno
- `.gitignore` - Git ignore
- `.deploy-*` - Sistema de deployment

---

## 📊 Resumen de Cambios

| Categoría | Archivos Movidos | Destino |
|-----------|------------------|---------|
| Deployment | 2 docs | DOCS/deployment/ |
| Fixes | 11 docs | DOCS/fixes/ |
| Features | 9 docs | DOCS/features/ |
| Testing | 9 docs | DOCS/testing/ |
| Staging | 10 docs | DOCS/staging/ |
| Instructions | 6 docs | DOCS/instructions/ |
| Fases | 6 docs | DOCS/ |
| Scripts Deployment | 2 scripts | scripts/deployment/ |
| Scripts Fixes | 5 scripts | scripts/fixes/ |
| Scripts Testing | 6 scripts | scripts/testing/ |
| Scripts Diagnostics | 2 scripts | scripts/diagnostics/ |

**Total:** ~68 archivos organizados

---

## 🎉 Resultado

- ✅ Proyecto organizado y limpio
- ✅ Fácil navegación
- ✅ Documentación categorizada
- ✅ Scripts agrupados por función
- ✅ Mantenibilidad mejorada

---

**Autor:** Kiro AI Assistant  
**Fecha:** 2024-11-30  
**Estado:** ✅ COMPLETADO
