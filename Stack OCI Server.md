# Consolidación de Stacks Docker en OCI

## 1. Arquitectura de Instancia
Se recomienda la creación de **una única instancia** con los recursos totales (**4 OCPUs / 24 GB RAM**).
* **Razón:** Maximiza el aprovechamiento de recursos, simplifica el mantenimiento del SO y evita la fragmentación de memoria.
* **Runtime:** Docker Engine + Docker Compose (Linux Nativo).

## 2. Estructura de Directorios Multi-Proyecto
```
/opt/
├── traefik/                  # Proxy inverso + SSL
├── portainer/                # Gestión de contenedores
├── projects/
│   ├── proyecto1/
│   │   ├── docker-compose.yml
│   │   └── data/
│   ├── proyecto2/
│   └── proyecto3/
├── shared/
│   ├── postgres/             # PostgreSQL compartido
│   ├── mysql/                # MySQL compartido
│   └── redis/                # Cache compartido
└── backup-manager/           # Sistema de backup/restore
    ├── scripts/
    ├── config/
    └── logs/
```

## 3. Gestión de Red y Dominios con Traefik

### 3.1 Configuración de Traefik
```yaml
# /opt/traefik/docker-compose.yml
services:
  traefik:
    image: traefik:v3.0
    restart: unless-stopped
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--providers.docker.network=proxy-network"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik_letsencrypt:/letsencrypt
    networks:
      - proxy-network
    labels:
      - "traefik.enable=true"
      # Dashboard
      - "traefik.http.routers.dashboard.rule=Host(`traefik.${DOMAIN}`)"
      - "traefik.http.routers.dashboard.service=api@internal"
      - "traefik.http.routers.dashboard.tls.certresolver=letsencrypt"
      - "traefik.http.routers.dashboard.middlewares=auth"
      - "traefik.http.middlewares.auth.basicauth.users=${TRAEFIK_AUTH}"

volumes:
  traefik_letsencrypt:

networks:
  proxy-network:
    external: true
```

### 3.2 Ejemplo de Servicio con Traefik
```yaml
# En cualquier proyecto
services:
  mi-app:
    image: mi-app:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.mi-app.rule=Host(`app.tudominio.com`)"
      - "traefik.http.routers.mi-app.tls.certresolver=letsencrypt"
      - "traefik.http.services.mi-app.loadbalancer.server.port=3000"
    networks:
      - proxy-network
```

### 3.3 Configuración DNS
* **Registro Wildcard:** `*.tudominio.com` → IP de la instancia
* **Certificados SSL:** Automáticos via Let's Encrypt (TLS Challenge)

```bash
# Crear red compartida
docker network create --driver bridge proxy-network
```

## 4. Bases de Datos Compartidas

### 4.1 PostgreSQL
```yaml
# /opt/shared/postgres/docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${POSTGRES_ROOT_PASSWORD}
    volumes:
      - /opt/shared/postgres/data:/var/lib/postgresql/data
    networks:
      - proxy-network
    deploy:
      resources:
        reservations:
          memory: 2G
        limits:
          memory: 6G

networks:
  proxy-network:
    external: true
```

Crear bases de datos por proyecto:
```bash
docker exec -it postgres psql -U admin -c "CREATE DATABASE proyecto1;"
docker exec -it postgres psql -U admin -c "CREATE USER proyecto1_user WITH PASSWORD 'password';"
docker exec -it postgres psql -U admin -c "GRANT ALL PRIVILEGES ON DATABASE proyecto1 TO proyecto1_user;"
```

### 4.2 MySQL
```yaml
# /opt/shared/mysql/docker-compose.yml
services:
  mysql:
    image: mysql:8.0
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    volumes:
      - /opt/shared/mysql/data:/var/lib/mysql
    networks:
      - proxy-network
    deploy:
      resources:
        reservations:
          memory: 2G
        limits:
          memory: 6G

networks:
  proxy-network:
    external: true
```

Crear bases de datos por proyecto:
```bash
docker exec -it mysql mysql -uroot -p -e "CREATE DATABASE proyecto1;"
docker exec -it mysql mysql -uroot -p -e "CREATE USER 'proyecto1_user'@'%' IDENTIFIED BY 'password';"
docker exec -it mysql mysql -uroot -p -e "GRANT ALL PRIVILEGES ON proyecto1.* TO 'proyecto1_user'@'%';"
```

### 4.3 Redis (Cache compartido)
```yaml
# /opt/shared/redis/docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - /opt/shared/redis/data:/data
    networks:
      - proxy-network
    deploy:
      resources:
        reservations:
          memory: 512M
        limits:
          memory: 2G

networks:
  proxy-network:
    external: true
```

## 5. Sincronización con AWS S3

### 5.1 Estrategia de Costos S3
| Operación | Costo | Estrategia |
|-----------|-------|------------|
| Data IN (upload) | GRATIS | Sin restricción |
| Data OUT (download) | $0.09/GB | Solo en restore |
| PUT requests | $0.005/1000 | Sync incremental |
| GET requests | $0.0004/1000 | Mínimo uso |
| Storage Standard | $0.023/GB/mes | Lifecycle rules |
| Storage IA | $0.0125/GB/mes | Backups >30 días |

### 5.2 Configuración de Rclone
```bash
# Instalación
curl https://rclone.org/install.sh | sudo bash

# Configurar remote
rclone config
# Nombre: s3backup
# Tipo: s3
# Provider: AWS
# Access Key ID: tu-key
# Secret Access Key: tu-secret
# Region: us-east-1 (o tu región)
```

### 5.3 Estructura del Bucket S3
```
s3://oci-projects-backup/
├── databases/
│   ├── postgres/
│   │   └── YYYY-MM-DD_HH-MM.sql
│   └── mysql/
│       └── YYYY-MM-DD_HH-MM.sql
├── projects/
│   ├── proyecto1/
│   │   └── data/
│   └── proyecto2/
│       └── data/
└── shared/
    └── redis/
```

### 5.4 Política IAM Mínima
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::oci-projects-backup",
        "arn:aws:s3:::oci-projects-backup/*"
      ]
    }
  ]
}
```

### 5.5 Lifecycle Rules para S3 (Ahorro de costos)
```json
{
  "Rules": [
    {
      "ID": "MoveToIA",
      "Status": "Enabled",
      "Filter": { "Prefix": "databases/" },
      "Transitions": [
        { "Days": 30, "StorageClass": "STANDARD_IA" }
      ],
      "Expiration": { "Days": 90 }
    }
  ]
}
```

## 6. Sistema de Backup/Restore Automatizado

### 6.1 Estructura
```
/opt/backup-manager/
├── scripts/
│   ├── backup.sh           # Backup manual/programado
│   ├── restore.sh          # Restauración desde S3
│   ├── sync-files.sh       # Sync de archivos
│   └── cleanup.sh          # Limpieza de backups antiguos
├── config/
│   └── backup.conf         # Configuración
└── logs/
    └── backup.log
```

### 6.2 Configuración
```bash
# /opt/backup-manager/config/backup.conf
S3_BUCKET="s3://oci-projects-backup"
RCLONE_REMOTE="s3backup"

# Rutas locales
POSTGRES_DATA="/opt/shared/postgres/data"
MYSQL_DATA="/opt/shared/mysql/data"
PROJECTS_DIR="/opt/projects"

# Retención
DB_RETENTION_DAYS=30
FILES_SYNC_INTERVAL=5  # minutos

# Contenedores
POSTGRES_CONTAINER="postgres"
MYSQL_CONTAINER="mysql"
```

### 6.3 Script de Backup
```bash
#!/bin/bash
# /opt/backup-manager/scripts/backup.sh

source /opt/backup-manager/config/backup.conf
TIMESTAMP=$(date +%Y-%m-%d_%H-%M)
LOG="/opt/backup-manager/logs/backup.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG; }

backup_postgres() {
    log "Iniciando backup PostgreSQL..."
    docker exec $POSTGRES_CONTAINER pg_dumpall -U admin > /tmp/postgres_$TIMESTAMP.sql
    rclone copy /tmp/postgres_$TIMESTAMP.sql $RCLONE_REMOTE:oci-projects-backup/databases/postgres/
    rm /tmp/postgres_$TIMESTAMP.sql
    log "Backup PostgreSQL completado: postgres_$TIMESTAMP.sql"
}

backup_mysql() {
    log "Iniciando backup MySQL..."
    docker exec $MYSQL_CONTAINER mysqldump -uroot -p$MYSQL_ROOT_PASSWORD --all-databases > /tmp/mysql_$TIMESTAMP.sql
    rclone copy /tmp/mysql_$TIMESTAMP.sql $RCLONE_REMOTE:oci-projects-backup/databases/mysql/
    rm /tmp/mysql_$TIMESTAMP.sql
    log "Backup MySQL completado: mysql_$TIMESTAMP.sql"
}

backup_files() {
    PROJECT=$1
    log "Sincronizando archivos de $PROJECT..."
    rclone sync $PROJECTS_DIR/$PROJECT/data $RCLONE_REMOTE:oci-projects-backup/projects/$PROJECT/data \
        --transfers 4 \
        --checkers 8 \
        --contimeout 60s \
        --timeout 300s \
        --retries 3 \
        --low-level-retries 10
    log "Sync completado para $PROJECT"
}

# Uso
case "$1" in
    db)
        case "$2" in
            postgres) backup_postgres ;;
            mysql) backup_mysql ;;
            all) backup_postgres; backup_mysql ;;
            *) echo "Uso: $0 db [postgres|mysql|all]" ;;
        esac
        ;;
    files)
        if [ -z "$2" ]; then
            # Sync todos los proyectos
            for dir in $PROJECTS_DIR/*/; do
                PROJECT=$(basename $dir)
                backup_files $PROJECT
            done
        else
            backup_files $2
        fi
        ;;
    all)
        backup_postgres
        backup_mysql
        for dir in $PROJECTS_DIR/*/; do
            PROJECT=$(basename $dir)
            backup_files $PROJECT
        done
        ;;
    *)
        echo "Uso: $0 [db|files|all] [opciones]"
        echo "  db postgres    - Backup PostgreSQL"
        echo "  db mysql       - Backup MySQL"
        echo "  db all         - Backup todas las BD"
        echo "  files          - Sync todos los proyectos"
        echo "  files proyecto - Sync proyecto específico"
        echo "  all            - Backup completo"
        ;;
esac
```

### 6.4 Script de Restore
```bash
#!/bin/bash
# /opt/backup-manager/scripts/restore.sh

source /opt/backup-manager/config/backup.conf
LOG="/opt/backup-manager/logs/backup.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG; }

list_backups() {
    TYPE=$1
    echo "Backups disponibles ($TYPE):"
    rclone ls $RCLONE_REMOTE:oci-projects-backup/databases/$TYPE/ | tail -20
}

restore_postgres() {
    BACKUP_FILE=$1
    if [ -z "$BACKUP_FILE" ]; then
        list_backups postgres
        echo ""
        read -p "Nombre del archivo a restaurar: " BACKUP_FILE
    fi
    
    log "Restaurando PostgreSQL desde $BACKUP_FILE..."
    rclone copy $RCLONE_REMOTE:oci-projects-backup/databases/postgres/$BACKUP_FILE /tmp/
    docker exec -i $POSTGRES_CONTAINER psql -U admin < /tmp/$BACKUP_FILE
    rm /tmp/$BACKUP_FILE
    log "Restore PostgreSQL completado"
    echo "✓ PostgreSQL restaurado desde $BACKUP_FILE"
}

restore_mysql() {
    BACKUP_FILE=$1
    if [ -z "$BACKUP_FILE" ]; then
        list_backups mysql
        echo ""
        read -p "Nombre del archivo a restaurar: " BACKUP_FILE
    fi
    
    log "Restaurando MySQL desde $BACKUP_FILE..."
    rclone copy $RCLONE_REMOTE:oci-projects-backup/databases/mysql/$BACKUP_FILE /tmp/
    docker exec -i $MYSQL_CONTAINER mysql -uroot -p$MYSQL_ROOT_PASSWORD < /tmp/$BACKUP_FILE
    rm /tmp/$BACKUP_FILE
    log "Restore MySQL completado"
    echo "✓ MySQL restaurado desde $BACKUP_FILE"
}

restore_files() {
    PROJECT=$1
    if [ -z "$PROJECT" ]; then
        echo "Proyectos disponibles en backup:"
        rclone lsd $RCLONE_REMOTE:oci-projects-backup/projects/
        echo ""
        read -p "Nombre del proyecto a restaurar: " PROJECT
    fi
    
    log "Restaurando archivos de $PROJECT..."
    rclone sync $RCLONE_REMOTE:oci-projects-backup/projects/$PROJECT/data $PROJECTS_DIR/$PROJECT/data \
        --transfers 4 \
        --checkers 8
    log "Restore de archivos completado para $PROJECT"
    echo "✓ Archivos restaurados para $PROJECT"
}

# Uso
case "$1" in
    db)
        case "$2" in
            postgres) restore_postgres $3 ;;
            mysql) restore_mysql $3 ;;
            *) echo "Uso: $0 db [postgres|mysql] [archivo]" ;;
        esac
        ;;
    files)
        restore_files $2
        ;;
    list)
        case "$2" in
            postgres) list_backups postgres ;;
            mysql) list_backups mysql ;;
            files) rclone lsd $RCLONE_REMOTE:oci-projects-backup/projects/ ;;
            *) echo "Uso: $0 list [postgres|mysql|files]" ;;
        esac
        ;;
    *)
        echo "Uso: $0 [db|files|list] [opciones]"
        echo "  db postgres [archivo]  - Restaurar PostgreSQL"
        echo "  db mysql [archivo]     - Restaurar MySQL"
        echo "  files [proyecto]       - Restaurar archivos"
        echo "  list postgres          - Listar backups PostgreSQL"
        echo "  list mysql             - Listar backups MySQL"
        echo "  list files             - Listar proyectos en backup"
        ;;
esac
```

### 6.5 Script de Limpieza
```bash
#!/bin/bash
# /opt/backup-manager/scripts/cleanup.sh

source /opt/backup-manager/config/backup.conf
LOG="/opt/backup-manager/logs/backup.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG; }

# Limpiar backups de BD mayores a 30 días
log "Limpiando backups antiguos..."

rclone delete $RCLONE_REMOTE:oci-projects-backup/databases/postgres/ --min-age ${DB_RETENTION_DAYS}d
rclone delete $RCLONE_REMOTE:oci-projects-backup/databases/mysql/ --min-age ${DB_RETENTION_DAYS}d

log "Limpieza completada"
```

### 6.6 Cron Jobs
```bash
# /etc/cron.d/backup-manager

# Sync de archivos cada 5 minutos
*/5 * * * * root /opt/backup-manager/scripts/backup.sh files >> /opt/backup-manager/logs/cron.log 2>&1

# Backup de BD cada hora
0 * * * * root /opt/backup-manager/scripts/backup.sh db all >> /opt/backup-manager/logs/cron.log 2>&1

# Limpieza diaria a las 3am
0 3 * * * root /opt/backup-manager/scripts/cleanup.sh >> /opt/backup-manager/logs/cron.log 2>&1
```

### 6.7 Casos donde usar inotify (sync inmediato)
Para archivos críticos que no pueden esperar 5 minutos:
- **Archivos de configuración** que cambian raramente pero son críticos
- **Certificados SSL** personalizados
- **Secrets/credentials** (aunque mejor usar Vault)

```bash
# Solo si es necesario para un proyecto específico
inotifywait -m -r /opt/projects/critico/config -e modify,create,delete |
while read path action file; do
    rclone copy "$path$file" $RCLONE_REMOTE:oci-projects-backup/projects/critico/config/
done
```

## 7. Límites de Recursos por Contenedor

### 7.1 Estrategia de Recursos
- **Reservación mínima:** 2GB RAM garantizados
- **Límite máximo:** Flexible según disponibilidad (6GB default)
- **CPU:** Sin límite duro, permite burst

```yaml
# Template para servicios
deploy:
  resources:
    reservations:
      memory: 2G        # Mínimo garantizado
    limits:
      memory: 6G        # Máximo permitido
      # Sin límite de CPU = puede usar lo disponible
```

### 7.2 Distribución Sugerida (24GB RAM)
| Servicio | Reservado | Límite |
|----------|-----------|--------|
| Traefik | 256M | 512M |
| Portainer | 256M | 512M |
| PostgreSQL | 2G | 6G |
| MySQL | 2G | 6G |
| Redis | 512M | 2G |
| Proyecto 1 | 2G | 6G |
| Proyecto 2 | 2G | 6G |
| Proyecto 3 | 2G | 6G |
| **Sistema/Swap** | ~4G | - |

## 8. Configuración del Docker Daemon
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "default-address-pools": [
    {"base": "172.20.0.0/16", "size": 24}
  ]
}
```

## 9. Recomendaciones de Seguridad y Estabilidad

* **Orquestación:** Usar **Portainer CE** para monitoreo gráfico de contenedores.
* **Resiliencia:** Configurar `restart: unless-stopped` en todos los servicios.
* **Estabilidad:** Crear un **archivo Swap de 8GB** para prevenir fallos por picos de memoria (OOM).
* **Arquitectura:** Validar que las imágenes de Docker sean compatibles con **ARM64**.
* **Seguridad:** Instalar **Fail2ban** para protección contra ataques de fuerza bruta.
* **Monitoreo:** Usar **Uptime Kuma** para health checks (ligero y efectivo).

### Crear Swap de 8GB
```bash
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 10. Comandos Rápidos

```bash
# Backup manual
/opt/backup-manager/scripts/backup.sh all

# Restaurar BD
/opt/backup-manager/scripts/restore.sh db postgres
/opt/backup-manager/scripts/restore.sh db mysql

# Restaurar archivos de proyecto
/opt/backup-manager/scripts/restore.sh files proyecto1

# Ver backups disponibles
/opt/backup-manager/scripts/restore.sh list postgres
/opt/backup-manager/scripts/restore.sh list mysql
/opt/backup-manager/scripts/restore.sh list files

# Ver logs
tail -f /opt/backup-manager/logs/backup.log
```

## 11. Herramientas Adicionales Recomendadas

| Herramienta | Propósito | RAM Aprox |
|-------------|-----------|-----------|
| Portainer CE | Gestión de contenedores | 256M |
| Uptime Kuma | Health checks | 100M |
| Watchtower | Auto-update de imágenes | 50M |
