# Sincronización de Base de Datos: Producción → Staging

## Descripción

Scripts para sincronizar la base de datos de producción (PAQUETEX) con staging, permitiendo visualizar datos reales en el entorno de pruebas.

## Scripts Disponibles

### 1. `sync_production_to_staging.sh` (Sincronización Completa)

**Propósito:** Restauración completa de la BD de staging con datos de producción.

**Proceso:**
1. Hace dump completo de BD producción
2. Sanitiza datos sensibles (contraseñas, tokens)
3. Crea backup de BD staging actual
4. Elimina completamente BD staging
5. Restaura dump en staging
6. Verifica sincronización

**Uso:**
```bash
# Modo interactivo (recomendado)
./sync_production_to_staging.sh

# Modo automático (sin confirmación)
./sync_production_to_staging.sh --auto

# Simular sin ejecutar
./sync_production_to_staging.sh --dry-run
```

**Características:**
- ✅ Restauración completa de BD
- ✅ Sanitización de contraseñas y tokens
- ✅ Backup automático de staging
- ✅ Verificación de integridad
- ⚠️ Las contraseñas son sanitizadas (usuarios no podrán iniciar sesión)

## Requisitos

### Software Necesario
- PostgreSQL client (`pg_dump`, `psql`)
- SSH client
- Acceso SSH a servidores de producción y staging

### Instalación de Dependencias
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client openssh-client

# macOS
brew install postgresql
```

### Permisos Requeridos
- Acceso SSH a servidor de producción (papyrus)
- Acceso SSH a servidor de staging
- Permisos de lectura en BD producción
- Permisos de escritura en BD staging

## Configuración

Los scripts obtienen automáticamente las credenciales desde los archivos `.env` de cada servidor:

**Producción:**
- Servidor: `papyrus`
- Usuario SSH: `ubuntu`
- BD: `paquetex`
- Ruta .env: `/home/ubuntu/paqueteria/.env`

**Staging:**
- Servidor: `staging`
- Usuario SSH: `ubuntu`
- BD: `staging`
- Ruta .env: `/home/ubuntu/paqueteria-staging/.env`

## Flujo de Trabajo Recomendado

### Caso 1: Visualizar Cambios CSS/HTML con Datos Reales

```bash
# 1. Sincronizar BD
cd PAQUETERIAv1.0/scripts/database
./sync_production_to_staging.sh

# 2. Desplegar código a staging
cd ../..
./deploy.sh --env staging --deploy

# 3. Verificar en navegador
# https://staging.jemavi.co
```

### Caso 2: Sincronización Periódica

```bash
# Ejecutar cada vez que necesites datos actualizados
./sync_production_to_staging.sh --auto
```

## Datos Sanitizados

Por seguridad, los siguientes datos son sanitizados automáticamente:

- ✅ `password_hash` → Valor genérico
- ✅ `api_token` → 'SANITIZED_TOKEN'
- ✅ `api_key` → 'SANITIZED_API_KEY'
- ✅ `session_token` → 'SANITIZED_SESSION'
- ✅ `reset_token` → 'SANITIZED_RESET_TOKEN'

**Implicaciones:**
- Los usuarios NO podrán iniciar sesión con sus contraseñas originales
- Las sesiones activas serán invalidadas
- Los tokens de API no funcionarán

## Restaurar Contraseñas en Staging

Si necesitas que usuarios específicos puedan iniciar sesión en staging:

```bash
# Conectar a staging
ssh ubuntu@staging

# Acceder a la BD
PGPASSWORD='tu_password' psql -U postgres -d staging

# Cambiar contraseña de un usuario
UPDATE users SET password_hash = '$2b$12$NUEVO_HASH' WHERE username = 'usuario';
```

O usar el script de cambio de contraseña:
```bash
cd /home/ubuntu/paqueteria-staging/CODE/src
python cambiar_password_simple.py
```

## Verificación Post-Sincronización

### Verificar Conteo de Registros
```bash
# En producción
ssh ubuntu@papyrus
PGPASSWORD='password' psql -U postgres -d paquetex -c "SELECT COUNT(*) FROM packages;"

# En staging
ssh ubuntu@staging
PGPASSWORD='password' psql -U postgres -d staging -c "SELECT COUNT(*) FROM packages;"
```

### Verificar Última Actualización
```bash
# En staging
PGPASSWORD='password' psql -U postgres -d staging -c "SELECT MAX(updated_at) FROM packages;"
```

## Troubleshooting

### Error: "No se puede conectar al servidor"
```bash
# Verificar acceso SSH
ssh ubuntu@papyrus echo "OK"
ssh ubuntu@staging echo "OK"

# Verificar configuración SSH en ~/.ssh/config
```

### Error: "Password authentication failed"
```bash
# Verificar que las contraseñas estén en los .env
ssh ubuntu@papyrus "grep POSTGRES_PASSWORD /home/ubuntu/paqueteria/.env"
ssh ubuntu@staging "grep POSTGRES_PASSWORD /home/ubuntu/paqueteria-staging/.env"
```

### Error: "pg_dump: command not found"
```bash
# Instalar PostgreSQL client
sudo apt-get update
sudo apt-get install postgresql-client
```

### Sincronización muy lenta
```bash
# Usar compresión para transferencias grandes
# El script ya usa --clean --if-exists para optimizar

# Verificar espacio en disco
df -h /tmp
```

## Seguridad

### Buenas Prácticas
- ✅ Siempre sanitizar datos sensibles
- ✅ Crear backup antes de restaurar
- ✅ Verificar sincronización después de restaurar
- ✅ No compartir dumps sin sanitizar
- ✅ Eliminar dumps temporales después de usar

### Archivos Temporales
Los dumps se guardan en:
```
/tmp/db_sync_TIMESTAMP/
├── production_dump.sql          # Dump original
└── production_dump_sanitized.sql # Dump sanitizado
```

Se eliminan automáticamente al finalizar el script.

## Frecuencia Recomendada

- **Desarrollo activo:** Cada 2-3 días
- **Cambios visuales:** Antes de cada deploy importante
- **Mantenimiento:** Semanal o según necesidad

## Notas Importantes

⚠️ **ADVERTENCIA:** Este proceso elimina COMPLETAMENTE la BD de staging. Todos los datos actuales se perderán.

✅ **RECOMENDACIÓN:** Ejecutar en horarios de bajo tráfico para minimizar impacto en producción.

📊 **TAMAÑO:** El dump puede ser grande (varios MB o GB). Asegúrate de tener espacio suficiente.

⏱️ **DURACIÓN:** El proceso puede tardar de 2 a 10 minutos dependiendo del tamaño de la BD.

## Soporte

Si encuentras problemas:
1. Revisa los logs del script
2. Verifica conectividad SSH
3. Confirma credenciales de BD
4. Revisa espacio en disco
5. Consulta la sección de Troubleshooting

## Changelog

### v1.0.0 (2026-02-26)
- Sincronización completa de BD
- Sanitización automática de datos sensibles
- Backup automático de staging
- Verificación de integridad
- Modo dry-run para simulación
