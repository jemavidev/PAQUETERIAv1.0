# 🚀 Quick Start: Staging Database

## ⚡ Comandos Rápidos

### 1️⃣ Crear DB Staging (AWS Console - MÁS FÁCIL)

```sql
CREATE DATABASE paqueteria_staging OWNER jveyes;
```

### 2️⃣ O desde Servidor con Acceso a RDS

```bash
./scripts/database/create_staging_database_docker.sh
```

### 3️⃣ Sincronizar Datos

```bash
./scripts/database/sync_prod_to_staging_initial.sh
```

### 4️⃣ Iniciar Staging

```bash
docker-compose -f docker-compose.staging.yml up -d
```

### 5️⃣ Ver Logs

```bash
docker-compose -f docker-compose.staging.yml logs -f app
```

### 6️⃣ Verificar

```bash
curl http://localhost:8001/health
```

---

## 📊 Estado Actual

✅ **Archivos listos:**
- `.env.staging` → `paqueteria_staging`
- `docker-compose.staging.yml` → Puerto 8001
- Scripts de DB → Ejecutables

✅ **Producción intacta:**
- `.env` → `paqueteria_v4`
- Puerto 8000 → Producción

⏳ **Pendiente:**
- Crear DB `paqueteria_staging` en AWS RDS
- Ejecutar sincronización inicial

---

## 🔗 Documentación Completa

- `VERIFICACION_STAGING_COMPLETADA.md` - Resumen completo
- `INSTRUCCIONES_CREAR_DB_STAGING.md` - Instrucciones detalladas
- `ESTRATEGIA_BASES_DATOS_STAGING.md` - Estrategia completa

---

## 🆘 Troubleshooting

**Error: No se puede conectar a RDS**
→ Ejecutar desde servidor con acceso a RDS, no desde local

**Error: Base de datos ya existe**
→ El script preguntará si deseas eliminarla y recrearla

**Error: Puerto 8001 en uso**
→ Detener staging: `docker-compose -f docker-compose.staging.yml down`

---

**Última actualización:** 27 de enero de 2026
