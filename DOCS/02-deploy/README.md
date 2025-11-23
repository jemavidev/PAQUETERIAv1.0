# 📂 Documentación de Deploy

Documentación completa sobre el despliegue y configuración del sistema PAQUETEX v1.0.

## 📄 Archivos

- **README_DEPLOY.md** - Guía principal de deploy
- **GUIA_DESPLIEGUE_AUTOMATIZADO.md** - Guía de despliegue automatizado
- **CONFIGURACION_SERVIDOR.md** - Configuración del servidor
- **CORRECCION_DOCKER_COMPOSE.md** - Correcciones de Docker Compose
- **DIAGRAMA_FLUJO_DESPLIEGUE.md** - Diagrama de flujo del despliegue
- **INDICE_DESPLIEGUE.md** - Índice de documentación de deploy

## 🚀 Guía Rápida

### Deploy en Localhost
```bash
./deploy.sh --env localhost --deploy
```

### Deploy en Producción (Papyrus)
```bash
./deploy.sh --env papyrus --deploy
```

### Ver Estado
```bash
./deploy.sh --env papyrus --status
```

## 📖 Más Información

- [Volver a DOCS](../)
- [Proyecto](../01-proyecto/)
- [Sistema de Deploy Principal](../../deploy.sh)
