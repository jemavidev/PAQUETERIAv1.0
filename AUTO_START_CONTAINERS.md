# Auto-Start Containers on Reboot

## ✅ Configuración Aplicada

Todos los contenedores ahora tienen la política de restart `unless-stopped`, lo que significa que:

- ✅ Se reiniciarán automáticamente al reiniciar el sistema
- ✅ Se reiniciarán si se caen por error
- ❌ NO se reiniciarán si los detienes manualmente con `docker stop`

## Contenedores Configurados

| Contenedor | Puerto | Restart Policy |
|-----------|--------|----------------|
| `paquetex_dev_app` | 8000 | unless-stopped |
| `paqueteria_staging_app` | 8001 | unless-stopped |
| `paqueteria_staging_redis` | 6380 | unless-stopped |

## Verificar Configuración

```bash
# Ver política de restart de todos los contenedores
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{json .HostConfig.RestartPolicy}}"

# Ver solo los contenedores con restart configurado
docker inspect $(docker ps -aq) --format='{{.Name}}: {{.HostConfig.RestartPolicy.Name}}'
```

## Opciones de Restart Policy

- `no` - No reiniciar automáticamente (default)
- `always` - Siempre reiniciar, incluso si lo detienes manualmente
- `unless-stopped` - Reiniciar siempre excepto si lo detienes manualmente ✅ (recomendado)
- `on-failure` - Solo reiniciar si falla con código de error

## Comandos Útiles

### Iniciar todos los contenedores manualmente
```bash
./start_all_containers.sh
```

### Cambiar política de restart de un contenedor
```bash
# Cambiar a unless-stopped (recomendado)
docker update --restart=unless-stopped <container_name>

# Cambiar a always
docker update --restart=always <container_name>

# Desactivar auto-restart
docker update --restart=no <container_name>
```

### Ver logs de un contenedor
```bash
docker logs -f paquetex_dev_app
docker logs --tail 100 paqueteria_staging_app
```

### Detener un contenedor (no se reiniciará automáticamente)
```bash
docker stop paquetex_dev_app
```

### Iniciar un contenedor detenido
```bash
docker start paquetex_dev_app
```

## Alternativa: Systemd Service (Opcional)

Si quieres más control, puedes crear un servicio systemd:

```bash
sudo nano /etc/systemd/system/paquetex-containers.service
```

Contenido:
```ini
[Unit]
Description=Paquetex Docker Containers
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/stk/Documents/GIT/PAQUETEX v1.0
ExecStart=/home/stk/Documents/GIT/PAQUETEX v1.0/start_all_containers.sh
ExecStop=/usr/bin/docker stop paquetex_dev_app paqueteria_staging_app paqueteria_staging_redis

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable paquetex-containers.service
sudo systemctl start paquetex-containers.service
```

## Troubleshooting

### Los contenedores no inician al reiniciar

1. Verificar que Docker esté habilitado:
```bash
sudo systemctl status docker
sudo systemctl enable docker
```

2. Verificar política de restart:
```bash
docker inspect <container_name> --format='{{.HostConfig.RestartPolicy.Name}}'
```

3. Ver logs del sistema:
```bash
journalctl -u docker.service -n 50
```

### Un contenedor se cae constantemente

```bash
# Ver por qué se está cayendo
docker logs --tail 100 <container_name>

# Ver estadísticas de recursos
docker stats <container_name>

# Verificar health check
docker inspect <container_name> --format='{{json .State.Health}}'
```

## Estado Actual

```bash
# Verificar que todo esté funcionando
docker ps
curl http://localhost:8000/health  # Dev
curl http://localhost:8001/health  # Staging
```

## Notas

- Los contenedores con `unless-stopped` NO se reiniciarán si los detienes con `docker stop`
- Para que se reinicien incluso después de `docker stop`, usa `--restart=always`
- La configuración persiste entre reinicios del sistema
- Docker debe estar corriendo para que los contenedores se inicien
