# 🧪 Prueba de Despliegue - Guía Paso a Paso

## 🎯 Objetivo
Probar el flujo completo de despliegue automatizado desde localhost a AWS.

---

## ✅ Pre-requisitos Verificados

- ✅ Servidor AWS: `paquetex.papyrus.com.co` (activo)
- ✅ SSH configurado: Alias `papyrus` funciona
- ✅ Proyecto en servidor: `/home/ubuntu/paqueteria`
- ✅ Git configurado: `https://github.com/jemavidev/PAQUETERIAv1.0.git`
- ✅ Contenedores corriendo: 7 contenedores healthy
- ✅ Script configurado: `deploy-to-aws.sh` listo

---

## 🚀 Prueba 1: Despliegue de Documentación (Seguro)

Esta prueba desplegará solo los archivos de documentación nuevos sin tocar el código de producción.

### Paso 1: Verificar Estado Local
```bash
# Ver archivos nuevos
git status

# Deberías ver:
# - CONFIGURACION_SERVIDOR.md (nuevo)
# - PRUEBA_DESPLIEGUE.md (nuevo)
# - deploy-to-aws.sh (modificado)
# - README.md (modificado)
# - Otros archivos de documentación
```

### Paso 2: Ejecutar Despliegue
```bash
# Desplegar con el script automatizado
./deploy-to-aws.sh "docs: agregar documentación de despliegue automatizado"
```

### Paso 3: Observar el Proceso
El script mostrará:
```
========================================
🚀 DESPLIEGUE AUTOMATIZADO A AWS
========================================

ℹ️  Verificando configuración...
✅ Configuración verificada

▶️  Verificando estado del repositorio local...
ℹ️  Cambios detectados:
 ?? CONFIGURACION_SERVIDOR.md
 ?? PRUEBA_DESPLIEGUE.md
 M  deploy-to-aws.sh
 M  README.md

▶️  Preparando commit...
ℹ️  Haciendo commit...
✅ Commit realizado: docs: agregar documentación de despliegue automatizado

ℹ️  Subiendo cambios a GitHub...
✅ Cambios subidos a GitHub correctamente

▶️  Desplegando en servidor AWS...
ℹ️  Conectando a: papyrus
✅ Conexión SSH verificada

ℹ️  Ejecutando actualización en AWS...
─────────────────────────────────────────
[Logs del servidor...]
✅ Pull completado exitosamente
─────────────────────────────────────────

▶️  Verificando despliegue...
✅ Health check exitoso

========================================
✅ DESPLIEGUE COMPLETADO
========================================
```

### Paso 4: Verificar en el Servidor
```bash
# Verificar que los archivos llegaron
ssh papyrus "cd /home/ubuntu/paqueteria && ls -la *.md | tail -5"

# Verificar último commit
ssh papyrus "cd /home/ubuntu/paqueteria && git log -1 --oneline"

# Verificar que la aplicación sigue funcionando
curl http://paquetex.papyrus.com.co/health
```

---

## 🧪 Prueba 2: Cambio Menor en Código (Con Hot Reload)

Esta prueba modificará un archivo Python para probar el hot reload.

### Paso 1: Hacer un Cambio Pequeño
```bash
# Agregar un comentario en un archivo
echo "# Test de despliegue automatizado - $(date)" >> CODE/src/app/config.py
```

### Paso 2: Desplegar
```bash
./deploy-to-aws.sh "test: probar hot reload con cambio menor"
```

### Paso 3: Verificar Hot Reload
```bash
# Ver logs del servidor para confirmar reload
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose logs --tail=20 app | grep -i reload"

# Deberías ver algo como:
# INFO: Detected file change in 'config.py'
# INFO: Reloading...
```

### Paso 4: Verificar Aplicación
```bash
# Health check
curl http://paquetex.papyrus.com.co/health

# Ver versión
ssh papyrus "cd /home/ubuntu/paqueteria && git log -1 --oneline"
```

---

## 📊 Resultados Esperados

### Prueba 1: Documentación
- ✅ Commit creado localmente
- ✅ Push a GitHub exitoso
- ✅ Pull en servidor exitoso
- ✅ Archivos nuevos en servidor
- ✅ Health check OK
- ⏱️ Tiempo: ~30 segundos
- 🚫 Downtime: NO

### Prueba 2: Código con Hot Reload
- ✅ Commit creado localmente
- ✅ Push a GitHub exitoso
- ✅ Pull en servidor exitoso
- ✅ Hot reload detectado
- ✅ Aplicación recargada
- ✅ Health check OK
- ⏱️ Tiempo: ~30 segundos
- 🚫 Downtime: NO

---

## 🔍 Verificación Post-Prueba

### Checklist de Verificación
```bash
# 1. Verificar Git local
git log -3 --oneline

# 2. Verificar Git en servidor
ssh papyrus "cd /home/ubuntu/paqueteria && git log -3 --oneline"

# 3. Verificar contenedores
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose ps"

# 4. Verificar health check
curl http://paquetex.papyrus.com.co/health

# 5. Verificar logs (últimas 50 líneas)
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose logs --tail=50 app"
```

### Comandos de Diagnóstico
```bash
# Ver estado de Git en ambos lados
echo "=== LOCAL ===" && git status && echo "" && echo "=== SERVIDOR ===" && ssh papyrus "cd /home/ubuntu/paqueteria && git status"

# Comparar commits
echo "=== LOCAL ===" && git log -1 --oneline && echo "" && echo "=== SERVIDOR ===" && ssh papyrus "cd /home/ubuntu/paqueteria && git log -1 --oneline"

# Ver uso de recursos en servidor
ssh papyrus "free -h && echo '' && df -h | grep -E '(Filesystem|/$)' && echo '' && docker stats --no-stream"
```

---

## 🚨 Troubleshooting

### Problema: "No se pudo conectar al servidor AWS"
```bash
# Verificar conexión SSH
ssh papyrus "echo 'Conexión OK'"

# Si falla, verificar configuración SSH
cat ~/.ssh/config | grep -A 5 papyrus
```

### Problema: "Error al hacer push a GitHub"
```bash
# Verificar remoto
git remote -v

# Verificar credenciales
git config user.name
git config user.email

# Intentar push manual
git push origin main
```

### Problema: "Health check falló"
```bash
# Ver logs del contenedor
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose logs --tail=100 app"

# Verificar estado de contenedores
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose ps"

# Reiniciar si es necesario
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose restart app"

# Esperar 10 segundos y verificar
sleep 10 && curl http://paquetex.papyrus.com.co/health
```

### Problema: "Hot reload no funcionó"
```bash
# Verificar que el volumen está montado
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose config | grep -A 5 volumes"

# Ver logs de uvicorn
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose logs --tail=50 app | grep -i uvicorn"

# Reiniciar contenedor
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose restart app"
```

---

## 📝 Registro de Pruebas

### Prueba 1: Documentación
```
Fecha: _______________
Hora: _______________
Resultado: [ ] Exitoso  [ ] Fallido
Tiempo: _______________
Notas: _________________________________
```

### Prueba 2: Hot Reload
```
Fecha: _______________
Hora: _______________
Resultado: [ ] Exitoso  [ ] Fallido
Tiempo: _______________
Notas: _________________________________
```

---

## 🎓 Próximos Pasos

Una vez que las pruebas sean exitosas:

1. ✅ **Documentar tu configuración específica**
2. ✅ **Crear un backup del servidor**
3. ✅ **Configurar monitoreo con alertas**
4. ✅ **Implementar GitHub Actions (opcional)**
5. ✅ **Capacitar al equipo en el nuevo flujo**

---

## 📞 Comandos de Referencia Rápida

```bash
# DESPLIEGUE
./deploy-to-aws.sh "mensaje"

# VERIFICAR SERVIDOR
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose ps"

# VER LOGS
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose logs -f app"

# HEALTH CHECK
curl http://paquetex.papyrus.com.co/health

# REINICIAR
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose restart app"

# ROLLBACK (si algo sale mal)
ssh papyrus "cd /home/ubuntu/paqueteria && git log --oneline -5"
ssh papyrus "cd /home/ubuntu/paqueteria && git checkout <commit-anterior> && docker compose restart app"
```

---

## ✅ Checklist Final

Antes de considerar las pruebas completas:

- [ ] Prueba 1 (Documentación) exitosa
- [ ] Prueba 2 (Hot Reload) exitosa
- [ ] Health check responde correctamente
- [ ] Logs no muestran errores
- [ ] Contenedores en estado healthy
- [ ] Git sincronizado (local y servidor)
- [ ] Documentación actualizada
- [ ] Equipo capacitado en el nuevo flujo

---

**Fecha de creación:** 2025-11-16
**Servidor:** paquetex.papyrus.com.co
**Estado:** Listo para pruebas
