# 🔧 Scripts - PAQUETEX v4.0

Scripts utilitarios para gestión del proyecto.

## 📁 Estructura

```
scripts/
├── deploy/                      # Scripts de deploy
│   ├── deploy-lightsail.sh      # Deploy específico para Lightsail
│   └── actualizar-produccion.sh # Actualización en producción
├── sync/                        # Scripts de sincronización
│   ├── sincronizar-static.sh    # Sincronizar archivos estáticos
│   ├── sincronizar-templates.sh # Sincronizar templates
│   └── verificar-templates.sh   # Verificar templates
└── utils/                       # Utilidades generales
```

## 🚀 Scripts de Deploy

### deploy-lightsail.sh
Deploy optimizado para AWS Lightsail (1GB RAM, 20GB Disco).

```bash
./scripts/deploy/deploy-lightsail.sh
```

**Características:**
- Optimizado para recursos limitados
- Limpieza automática de recursos
- Verificación de requisitos
- Health checks completos

**Nota:** Usar el nuevo sistema unificado: `./deploy.sh --env papyrus --deploy`

### actualizar-produccion.sh
Script para actualizar templates en producción.

```bash
./scripts/deploy/actualizar-produccion.sh
```

**Funciones:**
- Pull desde GitHub
- Verificación de templates
- Reinicio de contenedores
- Verificación de endpoints

## 🔄 Scripts de Sincronización

### sincronizar-static.sh
Sincroniza archivos estáticos entre directorios.

```bash
./scripts/sync/sincronizar-static.sh
```

**Sincroniza:**
- `/CODE/static` → `/CODE/src/static`
- CSS, JS, imágenes
- Mantiene estructura de directorios

### sincronizar-templates.sh
Sincroniza templates HTML.

```bash
./scripts/sync/sincronizar-templates.sh
```

**Sincroniza:**
- Templates entre directorios
- Verifica integridad
- Backup automático

### verificar-templates.sh
Verifica que los templates existan y sean válidos.

```bash
./scripts/sync/verificar-templates.sh
```

**Verifica:**
- Existencia de archivos
- Sintaxis HTML básica
- Referencias rotas

## 📝 Uso

### Permisos de Ejecución

```bash
# Dar permisos a todos los scripts
chmod +x scripts/deploy/*.sh
chmod +x scripts/sync/*.sh
```

### Ejecutar Scripts

```bash
# Desde la raíz del proyecto
./scripts/deploy/deploy-lightsail.sh
./scripts/sync/sincronizar-static.sh
```

## ⚠️ Notas Importantes

### Sistema de Deploy Nuevo

La mayoría de estos scripts han sido reemplazados por el nuevo sistema unificado de deploy:

```bash
# En lugar de scripts individuales, usar:
./deploy.sh --env <entorno> --deploy
```

Ver documentación: [README_DEPLOY.md](../README_DEPLOY.md)

### Scripts Mantenidos

Estos scripts se mantienen para casos específicos:
- `sincronizar-static.sh` - Sincronización manual de estáticos
- `sincronizar-templates.sh` - Sincronización manual de templates
- `verificar-templates.sh` - Verificación de templates

### Scripts Archivados

Scripts antiguos de deploy se mantienen en `DOCS/archived/` por referencia histórica.

## 🔧 Desarrollo

### Crear Nuevo Script

1. Crear archivo en la carpeta apropiada
2. Agregar shebang: `#!/bin/bash`
3. Documentar uso en comentarios
4. Dar permisos: `chmod +x script.sh`
5. Actualizar este README

### Mejores Prácticas

```bash
#!/bin/bash
# ========================================
# NOMBRE DEL SCRIPT
# ========================================
# Descripción breve
# Uso: ./script.sh [opciones]
# ========================================

set -e  # Salir si hay error

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Funciones
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Script principal
log_success "Script iniciado"
```

## 📚 Documentación

- [README principal](../README.md)
- [Sistema de deploy](../README_DEPLOY.md)
- [Documentación completa](../DOCS/INDEX.md)

---

**Última actualización:** 2024-11-22
