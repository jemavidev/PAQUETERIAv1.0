# 🔄 GUÍA RÁPIDA: Sincronizar Datos de Producción a Staging

## 🎯 Objetivo

Traer los datos actuales de producción (PAQUETEX) a staging para poder probar cambios con datos reales.

## ⚡ Opción 1: Desde la Interfaz Web (Recomendado)

### Paso 1: Acceder a Staging
```
https://staging.jemavi.co
```

### Paso 2: Iniciar Sesión como Admin
- Usuario: Tu usuario admin
- Contraseña: Tu contraseña

### Paso 3: Abrir el Modal de Sincronización
En cualquier página de admin, busca el botón:
```
🔄 Sincronizar BD
```

O ejecuta en la consola del navegador:
```javascript
openSyncDatabaseModal()
```

### Paso 4: Confirmar y Ejecutar
1. Lee las advertencias
2. Haz clic en "Iniciar Sincronización"
3. Observa los logs en tiempo real
4. Espera a que complete (5-10 minutos aprox)
5. Recarga la página

## 🖥️ Opción 2: Desde la Terminal (Avanzado)

### Configuración Inicial (Solo Primera Vez)

#### 1. Crear archivo `.env.staging`
```bash
cd PAQUETERIAv1.0/CODE
cp .env.staging.example .env.staging
```

#### 2. Editar `.env.staging` con credenciales de staging
```bash
nano .env.staging
```

Configurar:
```bash
# Base de datos de STAGING (diferente a producción)
DATABASE_URL=postgresql://usuario_staging:password@staging-rds.amazonaws.com:5432/staging
```

**IMPORTANTE:** Asegúrate de que el endpoint de RDS es DIFERENTE al de producción.

### Ejecución

#### Opción A: Modo Interactivo (Recomendado)
```bash
cd PAQUETERIAv1.0/scripts/database
./sync_rds_prod_to_staging.sh
```

Te mostrará un resumen y pedirá confirmación.

#### Opción B: Modo Automático
```bash
./sync_rds_prod_to_staging.sh --auto
```

Ejecuta sin pedir confirmación.

#### Opción C: Modo Dry-Run (Prueba)
```bash
./sync_rds_prod_to_staging.sh --dry-run
```

Simula la ejecución sin hacer cambios reales.

## 📋 Verificación

### Antes de Ejecutar
```bash
# Verificar que los endpoints son diferentes
echo "Producción:"
grep DATABASE_URL CODE/.env

echo "Staging:"
grep DATABASE_URL CODE/.env.staging

# Deben ser URLs DIFERENTES
```

### Después de Ejecutar
```bash
# Verificar conteo de paquetes
psql -h STAGING_HOST -U STAGING_USER -d staging -c "SELECT COUNT(*) FROM packages;"

# Verificar conteo de usuarios
psql -h STAGING_HOST -U STAGING_USER -d staging -c "SELECT COUNT(*) FROM users;"
```

## ⏱️ Tiempo Estimado

- Base de datos pequeña (< 1000 paquetes): 2-3 minutos
- Base de datos mediana (1000-10000 paquetes): 5-10 minutos
- Base de datos grande (> 10000 paquetes): 10-20 minutos

## 🔒 Seguridad

### ✅ Lo que SÍ hace:
- Lee datos de producción (backup)
- Elimina datos de staging
- Restaura datos en staging

### ❌ Lo que NO hace:
- NO modifica producción
- NO elimina datos de producción
- NO escribe en producción

**Producción está 100% segura.**

## 🚨 Solución de Problemas

### Error: "Script no encontrado"
```bash
# Verificar que el script existe
ls -la PAQUETERIAv1.0/scripts/database/sync_rds_prod_to_staging.sh

# Hacerlo ejecutable
chmod +x PAQUETERIAv1.0/scripts/database/sync_rds_prod_to_staging.sh
```

### Error: "DATABASE_URL no encontrado"
```bash
# Verificar que existe .env.staging
ls -la PAQUETERIAv1.0/CODE/.env.staging

# Si no existe, crearlo
cp PAQUETERIAv1.0/CODE/.env.staging.example PAQUETERIAv1.0/CODE/.env.staging
nano PAQUETERIAv1.0/CODE/.env.staging
```

### Error: "No se puede conectar a RDS"
```bash
# Verificar conectividad
psql -h PROD_HOST -U PROD_USER -d PROD_DB -c "SELECT 1;"

# Verificar credenciales en .env
cat CODE/.env | grep DATABASE_URL
```

### Error: "Timeout"
```bash
# La BD es muy grande, aumentar timeout
# Editar el script y cambiar:
# timeout=1800  # 30 minutos
# a
# timeout=3600  # 60 minutos
```

## 📊 Logs

Los logs se guardan en:
```
/tmp/db_sync_rds_YYYYMMDD_HHMMSS/
```

Puedes revisarlos después:
```bash
ls -la /tmp/db_sync_rds_*/
cat /tmp/db_sync_rds_*/staging_backup_before_sync.sql
```

## 🔄 Frecuencia Recomendada

- **Desarrollo activo**: 1 vez por semana
- **Antes de deploy importante**: Siempre
- **Testing de features nuevas**: Según necesidad

## 📞 Ayuda

Si tienes problemas:

1. Ejecuta con `--dry-run` primero
2. Revisa los logs en `/tmp/db_sync_rds_*/`
3. Verifica que los endpoints de RDS son diferentes
4. Verifica las credenciales en `.env` y `.env.staging`

## ✅ Checklist Rápido

Antes de ejecutar:
- [ ] Tengo acceso a staging
- [ ] Soy usuario ADMIN
- [ ] Archivo `.env.staging` configurado
- [ ] Endpoints de RDS son DIFERENTES
- [ ] Tengo 10-20 minutos disponibles
- [ ] Nadie más está usando staging

## 🎉 Resultado Esperado

Después de la sincronización:
- Staging tendrá los mismos datos que producción
- Podrás probar cambios con datos reales
- Producción no se habrá modificado en absoluto
- Las contraseñas en staging estarán sanitizadas (por seguridad)

## 📝 Notas Importantes

1. **Las contraseñas se sanitizan**: Los usuarios en staging no podrán iniciar sesión con sus contraseñas de producción (por seguridad)

2. **Staging se sobrescribe**: Todos los datos actuales de staging se perderán

3. **Producción es solo lectura**: El script solo lee de producción, nunca escribe

4. **Backups automáticos**: Se crea un backup de staging antes de sobrescribir

## 🚀 Próximos Pasos

Después de sincronizar:
1. Recarga la página de staging
2. Verifica que los datos están actualizados
3. Prueba tus cambios con datos reales
4. Cuando estés listo, haz deploy a producción

---

**¿Listo para sincronizar?** 

Opción más fácil: Abre https://staging.jemavi.co y busca el botón "🔄 Sincronizar BD"
