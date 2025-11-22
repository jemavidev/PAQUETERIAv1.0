# ========================================
# PERFIL: QUICK FIX
# ========================================
# Para deploys rápidos de hotfixes

# Deshabilitar operaciones lentas
BACKUP_AUTO_BEFORE_DEPLOY=false
DOCKER_REBUILD_ON_DEPLOY=false
DOCKER_PULL_BEFORE_DEPLOY=false
TESTS_ENABLED=false

# Acelerar health check
HEALTH_CHECK_TIMEOUT=15
HEALTH_CHECK_RETRIES=5

# Migraciones manuales
MIGRATIONS_AUTO=false

# Sin confirmaciones
REQUIRE_CONFIRMATION=false
