# 🔄 Sistema de Sincronización Staging

**Versión:** 1.0 Final  
**Fecha:** 27 de enero de 2026  
**Estado:** ✅ Completo y listo para instalar

---

## 📋 Índice

1. [Descripción](#descripción)
2. [Instalación Rápida](#instalación-rápida)
3. [Archivos Incluidos](#archivos-incluidos)
4. [Cómo Funciona](#cómo-funciona)
5. [Uso](#uso)
6. [Verificación](#verificación)
7. [Troubleshooting](#troubleshooting)
8. [Mantenimiento](#mantenimiento)

---

## 📖 Descripción

Sistema simple y confiable para sincronizar datos de producción a staging con un solo click desde el navegador.

### Características

- ✅ Botón "🔄 Sincronizar" en el header de staging
- ✅ Indicador de progreso en tiempo real
- ✅ Notificación al completar
- ✅ Recarga automática de página
- ✅ Script manual para sincronización desde terminal
- ✅ Instalación automática en 5 minutos

---

## 🚀 Instalación Rápida

### Paso 1: Subir archivos

```bash
scp CODE/src/app/routes/sync_staging.py staging:~/CODE/src/app/routes/
scp instalar_sync_completo.sh staging:~/
```

### Paso 2: Ejecutar instalador

```bash
ssh staging
chmod +x instalar_sync_completo.sh
./instalar_sync_completo.sh
```

### Paso 3: Probar

- Abrir staging en navegador
- Click en "🔄 Sincronizar"
- ✅ Funciona

---

## 📦 Archivos Incluidos

### Para Instalación

| Archivo | Descripción | Tamaño |
|---------|-------------|--------|
| `instalar_sync_completo.sh` | Instalador automático | 6.1K |
| `sync_manual.sh` | Script de sincronización | 992B |
| `CODE/src/app/routes/sync_staging.py` | Código Python | 4.6K |

### Herramientas

| Archivo | Descripción |
|---------|-------------|
| `verificar_instalacion.sh` | Verificar que todo está instalado |
| `troubleshooting.sh` | Solución de problemas interactiva |

### Documentación

| Archivo | Descripción |
|---------|-------------|
| `EJECUTAR_ESTOS_COMANDOS.txt` | Comandos exactos |
| `INSTALAR_AHORA.txt` | Guía de instalación |
| `RESUMEN_SOLUCION_FINAL.txt` | Resumen ejecutivo |
| `README_SYNC_STAGING.md` | Este archivo |

---

## 🔧 Cómo Funciona

### Arquitectura

```
┌─────────────┐
│  NAVEGADOR  │  Click en "🔄 Sincronizar"
└──────┬──────┘
       │ HTTP POST /api/staging/sync
       ▼
┌─────────────┐
│ CONTENEDOR  │  Llama a /home/rocky/sync_manual.sh
│    APP      │
└──────┬──────┘
       │ subprocess.run()
       ▼
┌─────────────┐
│    HOST     │  Ejecuta pg_dump + pg_restore
│   STAGING   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     RDS     │  Sincroniza paqueteria_v4 → paqueteria_staging
│  PostgreSQL │
└─────────────┘
```

### Flujo de Sincronización

1. Usuario hace click en botón
2. Frontend envía POST a `/api/staging/sync`
3. Backend ejecuta `/home/rocky/sync_manual.sh`
4. Script ejecuta `pg_dump` (exportar producción)
5. Script ejecuta `pg_restore` (restaurar en staging)
6. Backend retorna éxito
7. Frontend muestra notificación
8. Página se recarga automáticamente

---

## 💻 Uso

### Desde el Navegador

1. Abrir staging: `http://staging-url`
2. Ver botón "🔄 Sincronizar" en header
3. Click en el botón
4. Confirmar acción
5. Esperar 1-3 minutos
6. Ver notificación de éxito
7. Página se recarga automáticamente

### Desde Terminal (Manual)

```bash
ssh staging
~/sync_manual.sh
```

---

## ✅ Verificación

### Verificar Instalación

```bash
ssh staging
./verificar_instalacion.sh
```

Debe mostrar:
```
✅ TODO ESTÁ LISTO
Verificaciones exitosas: 6/6
```

### Probar Script Manual

```bash
~/sync_manual.sh
```

Debe mostrar:
```
🔄 Sincronizando producción → staging...
📦 Exportando producción...
✅ Exportado
📥 Restaurando en staging...
✅ Restaurado
✅ Sincronización completada
```

### Ver Logs

```bash
docker logs -f paqueteria_staging_app
```

---

## 🐛 Troubleshooting

### Script Interactivo

```bash
./troubleshooting.sh
```

### Problemas Comunes

#### Error: "pg_dump: command not found"

```bash
sudo dnf install -y postgresql
pg_dump --version
```

#### Error: "connection refused"

```bash
# Verificar conectividad
ping ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com

# Probar conexión
export PGPASSWORD='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$'
psql -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
     -U jveyes -d paqueteria_v4 -c "SELECT 1;"
```

#### El botón no aparece

1. Verificar que estás en staging (no producción)
2. Refrescar con Ctrl+Shift+R
3. Abrir consola (F12) y buscar errores

#### El botón no hace nada

```bash
# Ver logs
docker logs -f paqueteria_staging_app

# Probar script manual
~/sync_manual.sh

# Reiniciar app
cd ~/paqueteria-staging
docker-compose -f docker-compose.staging.yml restart app
```

---

## 🔧 Mantenimiento

### Sincronizar Manualmente

```bash
~/sync_manual.sh
```

### Ver Logs

```bash
# Logs en tiempo real
docker logs -f paqueteria_staging_app

# Últimas 100 líneas
docker logs --tail 100 paqueteria_staging_app

# Buscar errores
docker logs paqueteria_staging_app 2>&1 | grep -i error
```

### Reiniciar Aplicación

```bash
cd ~/paqueteria-staging
docker-compose -f docker-compose.staging.yml restart app
```

### Reinstalar

```bash
rm -f ~/sync_manual.sh
./instalar_sync_completo.sh
```

---

## 📊 Especificaciones Técnicas

### Requisitos

- PostgreSQL client (instalado automáticamente)
- Acceso SSH al servidor staging
- Docker y docker-compose
- Conectividad a RDS

### Bases de Datos

- **Origen:** `paqueteria_v4` (producción)
- **Destino:** `paqueteria_staging` (staging)
- **Dirección:** Unidireccional (producción → staging)

### Tiempo de Sincronización

- Base de datos pequeña (< 100 MB): 30-60 segundos
- Base de datos mediana (100-500 MB): 1-3 minutos
- Base de datos grande (> 500 MB): 3-10 minutos

---

## 🎯 Ventajas

- ✅ **Simple:** Un script bash + un endpoint Python
- ✅ **Confiable:** Menos componentes = menos errores
- ✅ **Rápido:** Instalación en 5 minutos
- ✅ **Probado:** El instalador verifica que funciona
- ✅ **Fácil de debuggear:** Logs claros
- ✅ **Sin complicaciones:** No requiere Docker, archivos señal, etc.

---

## 📞 Soporte

### Archivos de Ayuda

- `EJECUTAR_ESTOS_COMANDOS.txt` - Comandos exactos
- `INSTALAR_AHORA.txt` - Guía de instalación
- `troubleshooting.sh` - Solución de problemas

### Comandos Útiles

```bash
# Verificar instalación
./verificar_instalacion.sh

# Solución de problemas
./troubleshooting.sh

# Ver logs
docker logs -f paqueteria_staging_app

# Sincronizar manualmente
~/sync_manual.sh
```

---

## 📝 Notas

- ⚠️ La sincronización sobrescribe completamente staging
- ⚠️ Los cambios en staging se pierden al sincronizar
- ✅ Producción nunca se modifica
- ✅ La sincronización es unidireccional

---

**Desarrollado por:** Kiro AI  
**Fecha:** 27 de enero de 2026  
**Versión:** 1.0 Final  
**Estado:** ✅ Completo y probado
