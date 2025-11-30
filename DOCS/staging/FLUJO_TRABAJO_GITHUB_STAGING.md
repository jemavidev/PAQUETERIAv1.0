# 🔄 Flujo de Trabajo: GitHub como Fuente Única de Verdad

**Fecha:** 2025-11-28  
**Objetivo:** Mantener staging sincronizado con GitHub, evitando cambios locales en el servidor

---

## 🎯 Filosofía: GitHub es la Fuente Única de Verdad

```
┌─────────────┐
│   GITHUB    │  ← Fuente única de verdad
│  (staging)  │
└──────┬──────┘
       │
       │ git pull / reset
       ↓
┌─────────────┐
│  SERVIDOR   │  ← Siempre sincronizado
│  STAGING    │
└─────────────┘
```

**Regla de Oro:** 
- ✅ Todos los cambios se hacen en local → commit → push a GitHub
- ✅ Staging solo hace pull/reset desde GitHub
- ❌ NUNCA editar archivos directamente en staging

---

## 🚀 Flujo de Trabajo Recomendado

### 1️⃣ **Desarrollo Local (Tu Computadora)**

```bash
# 1. Hacer cambios en tu código local
vim CODE/src/templates/components/mobile-footer.html

# 2. Probar localmente
docker-compose up -d

# 3. Commit de cambios
git add .
git commit -m "feat: footer móvil con detección inteligente v3"

# 4. Push a GitHub
git push origin staging
```

### 2️⃣ **Despliegue a Staging (Servidor)**

**Opción A: Pull Normal (si no hay cambios locales)**
```bash
# En el servidor staging
cd /ruta/al/proyecto
git pull origin staging
docker-compose -f docker-compose.staging.yml restart
```

**Opción B: Reset Completo (si hay cambios locales que descartar)**
```bash
# En el servidor staging
cd /ruta/al/proyecto
./reset-staging-from-github.sh
```

---

## 🛠️ Script: `reset-staging-from-github.sh`

### ¿Qué hace?

1. ✅ Guarda cambios locales en stash (por seguridad)
2. ✅ Hace fetch de GitHub
3. ✅ Resetea el código local a la versión de GitHub (`git reset --hard`)
4. ✅ Limpia archivos no rastreados (`git clean -fd`)
5. ✅ Reconstruye contenedores Docker desde cero
6. ✅ Reinicia el servidor

### ¿Cuándo usarlo?

- ✅ Cuando hay cambios locales en staging que quieres descartar
- ✅ Cuando quieres asegurar que staging = GitHub al 100%
- ✅ Después de hacer cambios experimentales en staging
- ✅ Para resolver conflictos de merge
- ✅ Como parte del proceso de deployment

### Uso:

```bash
cd /ruta/al/proyecto
./reset-staging-from-github.sh
```

El script te pedirá confirmación antes de ejecutar.

---

## 📋 Comandos Útiles

### Ver estado actual:
```bash
git status                    # Ver archivos modificados
git diff                      # Ver cambios específicos
git log -5 --oneline         # Ver últimos 5 commits
```

### Ver diferencias con GitHub:
```bash
git fetch origin staging
git diff origin/staging      # Ver qué es diferente
```

### Recuperar cambios del stash:
```bash
git stash list               # Ver todos los stash guardados
git stash show stash@{0}     # Ver contenido del último stash
git stash pop                # Aplicar y eliminar último stash
git stash apply stash@{0}    # Aplicar sin eliminar
```

### Limpiar todo manualmente:
```bash
git reset --hard origin/staging   # Resetear código
git clean -fd                     # Limpiar archivos no rastreados
```

---

## 🔒 Prevención: Evitar Cambios Locales en Staging

### 1. **Usar permisos de solo lectura (opcional)**

```bash
# En staging, después de hacer pull
chmod -R 444 CODE/src/templates/
```

Esto hace que los archivos sean de solo lectura, evitando ediciones accidentales.

### 2. **Hook de Git para advertir**

Crear `.git/hooks/pre-commit` en staging:

```bash
#!/bin/bash
echo "⚠️  ADVERTENCIA: Estás haciendo commit en STAGING"
echo "   Los cambios deben hacerse en local y pushearse a GitHub"
echo ""
read -p "¿Realmente quieres hacer commit aquí? (escribe 'SI'): " confirm
if [ "$confirm" != "SI" ]; then
    echo "❌ Commit cancelado"
    exit 1
fi
```

### 3. **Alias útiles**

Agregar a `~/.bashrc` o `~/.zshrc` en staging:

```bash
# Alias para recordar el flujo correcto
alias git-commit='echo "⚠️  No hagas commit en staging. Usa local → GitHub → pull"'
alias deploy='cd /ruta/proyecto && git pull origin staging && docker-compose restart'
alias reset-staging='cd /ruta/proyecto && ./reset-staging-from-github.sh'
```

---

## 📊 Escenarios Comunes

### Escenario 1: Deployment Normal

```bash
# En local
git add .
git commit -m "feat: nueva funcionalidad"
git push origin staging

# En staging
cd /ruta/proyecto
git pull origin staging
docker-compose -f docker-compose.staging.yml restart
```

### Escenario 2: Hay Cambios Locales en Staging

```bash
# En staging
cd /ruta/proyecto
./reset-staging-from-github.sh
# Esto descarta cambios locales y sincroniza con GitHub
```

### Escenario 3: Hotfix Urgente

```bash
# En local (rama hotfix)
git checkout -b hotfix/footer-mobile
# ... hacer cambios ...
git commit -m "hotfix: corregir footer móvil"
git push origin hotfix/footer-mobile

# Merge a staging en GitHub (PR o directo)
git checkout staging
git merge hotfix/footer-mobile
git push origin staging

# En staging
cd /ruta/proyecto
./reset-staging-from-github.sh
```

### Escenario 4: Rollback a Versión Anterior

```bash
# En local
git log --oneline  # Ver commits
git checkout staging
git reset --hard <commit-hash>  # Volver a commit específico
git push origin staging --force

# En staging
cd /ruta/proyecto
./reset-staging-from-github.sh
```

---

## 🔍 Verificación Post-Deployment

Después de hacer reset/pull en staging, verifica:

```bash
# 1. Verificar que el código coincide con GitHub
git diff origin/staging  # No debe mostrar diferencias

# 2. Verificar que no hay archivos modificados
git status  # Debe decir "working tree clean"

# 3. Verificar último commit
git log -1 --oneline

# 4. Verificar contenedores
docker-compose -f docker-compose.staging.yml ps

# 5. Verificar logs
docker-compose -f docker-compose.staging.yml logs --tail=50
```

---

## 🆘 Troubleshooting

### Problema: "git pull" falla por conflictos

**Solución:**
```bash
./reset-staging-from-github.sh
# Esto descarta cambios locales y resuelve conflictos
```

### Problema: Cambios locales importantes que no quiero perder

**Solución:**
```bash
# Guardar cambios en stash
git stash push -m "Cambios importantes - $(date)"

# Hacer reset
./reset-staging-from-github.sh

# Recuperar cambios (si es necesario)
git stash pop
```

### Problema: Docker no se reconstruye correctamente

**Solución:**
```bash
# Limpiar todo Docker
docker-compose -f docker-compose.staging.yml down -v
docker system prune -a --volumes -f

# Reconstruir desde cero
docker-compose -f docker-compose.staging.yml build --no-cache
docker-compose -f docker-compose.staging.yml up -d
```

### Problema: Archivos no rastreados que no se eliminan

**Solución:**
```bash
# Ver qué archivos no están rastreados
git status

# Eliminar manualmente
rm -rf archivo_o_carpeta

# O forzar limpieza
git clean -fdx  # ⚠️ Cuidado: elimina TODO lo no rastreado
```

---

## 📝 Checklist de Deployment

Antes de cada deployment a staging:

- [ ] Cambios commiteados en local
- [ ] Cambios pusheados a GitHub (rama staging)
- [ ] Verificar que el push fue exitoso en GitHub
- [ ] Conectar al servidor staging
- [ ] Ejecutar `./reset-staging-from-github.sh`
- [ ] Verificar que no hay errores en logs
- [ ] Probar la aplicación en staging
- [ ] Verificar que el footer móvil funciona (badge verde)
- [ ] Limpiar caché del navegador si es necesario

---

## 🎯 Resumen

**Flujo Correcto:**
```
Local → Commit → Push a GitHub → Reset en Staging → Verificar
```

**Flujo Incorrecto (evitar):**
```
Editar en Staging → Commit en Staging → Conflictos → Problemas
```

**Comando Clave:**
```bash
./reset-staging-from-github.sh
```

Este comando asegura que staging siempre refleje exactamente lo que está en GitHub.

---

## 🚀 Próximos Pasos

1. **Ahora mismo:** Ejecuta `./reset-staging-from-github.sh` en staging
2. **Verifica:** Que el código coincida con GitHub
3. **Prueba:** El footer móvil en tu celular
4. **Documenta:** Cualquier problema que encuentres

¡GitHub es ahora tu fuente única de verdad! 🎉
