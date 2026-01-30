# 🔧 Solución: Health Check Timeout

## 🎯 Problema
El contenedor no pasa el health check y se queda en timeout.

## ✅ Causa
La migración de base de datos no se ha aplicado, causando que la aplicación falle al iniciar.

## 🚀 Solución Rápida

### Opción 1: Script Automático (Recomendado)
```bash
bash deploy_invoices_v2.sh
```

Este script:
1. Verifica sintaxis
2. Construye la imagen
3. Inicia servicios
4. Aplica migración automáticamente
5. Reinicia la app
6. Verifica que todo funcione

### Opción 2: Manual (Paso a Paso)

#### 1. Detener servicios actuales
```bash
docker-compose -f docker-compose.staging.yml down
```

#### 2. Construir imagen
```bash
docker-compose -f docker-compose.staging.yml build app
```

#### 3. Iniciar servicios
```bash
docker-compose -f docker-compose.staging.yml up -d
```

#### 4. Esperar a que la base de datos esté lista
```bash
sleep 10
```

#### 5. Aplicar migración
```bash
docker-compose -f docker-compose.staging.yml exec app alembic upgrade head
```

#### 6. Reiniciar app
```bash
docker-compose -f docker-compose.staging.yml restart app
```

#### 7. Verificar logs
```bash
docker-compose -f docker-compose.staging.yml logs -f app
```

## 🔍 Verificación

### Ver estado de servicios
```bash
docker-compose -f docker-compose.staging.yml ps
```

### Ver logs en tiempo real
```bash
docker-compose -f docker-compose.staging.yml logs -f app
```

### Verificar health check
```bash
curl http://localhost:8000/health
```

Debería responder:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "version": "...",
  "environment": "staging"
}
```

### Verificar que la ruta de facturas funciona
```bash
curl -I http://localhost:8000/invoices/facturas
```

Debería responder con `200 OK` o `302 Found` (redirect a login).

## 🐛 Si Sigue Fallando

### 1. Ver logs detallados
```bash
docker-compose -f docker-compose.staging.yml logs --tail=100 app
```

### 2. Entrar al contenedor
```bash
docker-compose -f docker-compose.staging.yml exec app bash
```

### 3. Verificar migración manualmente
```bash
docker-compose -f docker-compose.staging.yml exec app alembic current
```

Debería mostrar:
```
20260130_invoice_v2 (head)
```

### 4. Ver todas las migraciones disponibles
```bash
docker-compose -f docker-compose.staging.yml exec app alembic history
```

### 5. Aplicar migración específica
```bash
docker-compose -f docker-compose.staging.yml exec app alembic upgrade 20260130_invoice_v2
```

## 📊 Verificar Base de Datos

### Conectarse a PostgreSQL
```bash
docker-compose -f docker-compose.staging.yml exec db psql -U postgres -d paquetex_staging
```

### Verificar que las tablas existen
```sql
\dt invoices_v2
\dt invoice_products_v2
```

Debería mostrar:
```
 Schema |        Name         | Type  |  Owner   
--------+---------------------+-------+----------
 public | invoices_v2         | table | postgres
 public | invoice_products_v2 | table | postgres
```

### Ver estructura de la tabla
```sql
\d invoices_v2
```

## 🔧 Aumentar Timeout del Health Check

Si el servidor tarda mucho en iniciar, puedes aumentar el timeout en `docker-compose.staging.yml`:

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 10s
      retries: 10  # Aumentar de 5 a 10
      start_period: 60s  # Aumentar de 40s a 60s
```

## ✅ Checklist de Solución

- [ ] Detener servicios
- [ ] Construir imagen
- [ ] Iniciar servicios
- [ ] Esperar a que DB esté lista
- [ ] Aplicar migración
- [ ] Reiniciar app
- [ ] Verificar logs
- [ ] Verificar health check
- [ ] Acceder a /invoices/facturas

## 🎉 Resultado Esperado

Después de seguir estos pasos, deberías poder:

1. Ver el servicio corriendo:
```bash
docker-compose -f docker-compose.staging.yml ps
```
```
NAME                    STATUS
paqueteria_staging_app  Up (healthy)
paqueteria_staging_db   Up (healthy)
```

2. Acceder a la aplicación:
```
http://localhost:8000/invoices/facturas
```

3. Ver el enlace "Facturas" en el header entre "Consulta" y "DynamiaERP"

## 📝 Notas

- La migración solo necesita aplicarse UNA VEZ
- Después de aplicar la migración, los reinicios normales funcionarán
- Si borras el volumen de la base de datos, necesitarás aplicar la migración nuevamente
- El health check timeout es normal la primera vez que se aplica la migración

## 🆘 Soporte

Si después de seguir todos estos pasos sigue fallando, ejecuta:

```bash
# Recopilar información de diagnóstico
echo "=== Estado de servicios ===" > diagnostico.txt
docker-compose -f docker-compose.staging.yml ps >> diagnostico.txt
echo "" >> diagnostico.txt
echo "=== Logs de app ===" >> diagnostico.txt
docker-compose -f docker-compose.staging.yml logs --tail=100 app >> diagnostico.txt
echo "" >> diagnostico.txt
echo "=== Migraciones ===" >> diagnostico.txt
docker-compose -f docker-compose.staging.yml exec -T app alembic current >> diagnostico.txt
echo "" >> diagnostico.txt
echo "=== Health check ===" >> diagnostico.txt
curl -v http://localhost:8000/health >> diagnostico.txt 2>&1

cat diagnostico.txt
```

Esto generará un archivo con toda la información de diagnóstico.
