# 🧹 Solución: Archivos Duplicados en el Servidor

## 🔍 Problema Identificado

En el servidor hay archivos `.sh` duplicados en la raíz del proyecto que deberían estar solo en `DOCS/scripts/deployment/`.

### Estado Actual en el Servidor
```bash
ubuntu@paquetex:~/paqueteria$ git status
On branch main
Your branch is up to date with 'origin/main'.

Untracked files:
  deploy-aws.sh
  deploy.sh
  dev-up.sh
  pull-only.sh
  pull-update.sh
  rollback.sh
  setup-env.sh
  setup-production.sh
  update.sh
```

---

## 📋 Análisis

### Archivos Duplicados (deben eliminarse de la raíz)
Estos archivos existen en `DOCS/scripts/deployment/` y NO deben estar en la raíz:

1. ❌ `deploy-aws.sh` → Está en `DOCS/scripts/deployment/deploy-aws.sh`
2. ❌ `deploy.sh` → Está en `DOCS/scripts/deployment/deploy.sh`
3. ❌ `dev-up.sh` → Está en `DOCS/scripts/deployment/dev-up.sh`
4. ❌ `pull-only.sh` → Está en `DOCS/scripts/deployment/pull-only.sh`
5. ❌ `pull-update.sh` → Está en `DOCS/scripts/deployment/pull-update.sh`
6. ❌ `rollback.sh` → Está en `DOCS/scripts/deployment/rollback.sh`
7. ❌ `setup-env.sh` → Está en `DOCS/scripts/deployment/setup-env.sh`
8. ❌ `setup-production.sh` → Está en `DOCS/scripts/deployment/setup-production.sh`
9. ❌ `update.sh` → Está en `DOCS/scripts/deployment/update.sh`

### Archivos Correctos (deben permanecer en la raíz)
Estos archivos SÍ deben estar en la raíz del proyecto:

1. ✅ `deploy-lightsail.sh` - Script de despliegue Lightsail
2. ✅ `deploy-to-aws.sh` - Script de despliegue automatizado
3. ✅ `monitor.sh` - Script de monitoreo
4. ✅ `start.sh` - Script de inicio
5. ✅ `test-scripts.sh` - Script de pruebas

---

## ✅ Solución

### Opción 1: Limpieza Automática (Recomendada)

He creado un script que limpia automáticamente los archivos duplicados:

```bash
# En el servidor
ssh papyrus "cd /home/ubuntu/paqueteria && bash limpiar-servidor.sh"
```

El script:
1. Identifica archivos duplicados
2. Muestra qué se va a eliminar
3. Pide confirmación
4. Elimina los archivos duplicados
5. Muestra el estado final

### Opción 2: Limpieza Manual

```bash
# Conectar al servidor
ssh papyrus

# Ir al directorio del proyecto
cd /home/ubuntu/paqueteria

# Eliminar archivos duplicados uno por uno
rm deploy-aws.sh
rm deploy.sh
rm dev-up.sh
rm pull-only.sh
rm pull-update.sh
rm rollback.sh
rm setup-env.sh
rm setup-production.sh
rm update.sh

# Verificar estado
git status
```

### Opción 3: Limpieza con un Solo Comando

```bash
ssh papyrus "cd /home/ubuntu/paqueteria && rm deploy-aws.sh deploy.sh dev-up.sh pull-only.sh pull-update.sh rollback.sh setup-env.sh setup-production.sh update.sh && git status"
```

---

## 🎯 Resultado Esperado

Después de la limpieza, `git status` debería mostrar:

```bash
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

---

## 📊 Estructura Correcta del Proyecto

```
PAQUETERIA v1.0/
├── deploy-lightsail.sh          ✅ Raíz (correcto)
├── deploy-to-aws.sh             ✅ Raíz (correcto)
├── monitor.sh                   ✅ Raíz (correcto)
├── start.sh                     ✅ Raíz (correcto)
├── test-scripts.sh              ✅ Raíz (correcto)
├── limpiar-servidor.sh          ✅ Raíz (nuevo)
│
├── DOCS/
│   └── scripts/
│       └── deployment/
│           ├── deploy-aws.sh    ✅ Aquí (correcto)
│           ├── deploy.sh        ✅ Aquí (correcto)
│           ├── dev-up.sh        ✅ Aquí (correcto)
│           ├── pull-only.sh     ✅ Aquí (correcto)
│           ├── pull-update.sh   ✅ Aquí (correcto)
│           ├── rollback.sh      ✅ Aquí (correcto)
│           ├── setup-env.sh     ✅ Aquí (correcto)
│           ├── setup-production.sh ✅ Aquí (correcto)
│           └── update.sh        ✅ Aquí (correcto)
```

---

## 🔍 Verificación Post-Limpieza

### 1. Verificar que no hay archivos sin rastrear
```bash
ssh papyrus "cd /home/ubuntu/paqueteria && git status"
```

**Resultado esperado:**
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

### 2. Verificar archivos en la raíz
```bash
ssh papyrus "cd /home/ubuntu/paqueteria && ls -la *.sh"
```

**Resultado esperado:**
```
-rwxrwxr-x 1 ubuntu ubuntu 7252 deploy-lightsail.sh
-rwxrwxr-x 1 ubuntu ubuntu 6911 deploy-to-aws.sh
-rwxrwxr-x 1 ubuntu ubuntu 6705 monitor.sh
-rwxrwxr-x 1 ubuntu ubuntu 5709 start.sh
-rwxrwxr-x 1 ubuntu ubuntu 3084 test-scripts.sh
```

### 3. Verificar archivos en DOCS/scripts/deployment/
```bash
ssh papyrus "cd /home/ubuntu/paqueteria && ls -la DOCS/scripts/deployment/*.sh"
```

**Resultado esperado:**
```
-rwxrwxr-x 1 ubuntu ubuntu  290 deploy-aws.sh
-rwxrwxr-x 1 ubuntu ubuntu 1340 deploy.sh
-rwxrwxr-x 1 ubuntu ubuntu 1070 dev-up.sh
-rwxrwxr-x 1 ubuntu ubuntu 3183 pull-only.sh
-rwxrwxr-x 1 ubuntu ubuntu 8719 pull-update.sh
-rwxrwxr-x 1 ubuntu ubuntu  910 rollback.sh
-rwxrwxr-x 1 ubuntu ubuntu 2890 setup-env.sh
-rwxrwxr-x 1 ubuntu ubuntu 9114 setup-production.sh
-rwxrwxr-x 1 ubuntu ubuntu  486 update.sh
```

---

## 🚨 Importante

### ¿Por qué ocurrió esto?

Los archivos duplicados probablemente se crearon cuando:
1. Se copiaron scripts manualmente al servidor
2. Se ejecutaron scripts que crearon copias en la raíz
3. Se hicieron pruebas de despliegue

### ¿Cómo evitarlo en el futuro?

1. **Usar solo el flujo de Git:**
   ```bash
   # Hacer cambios en localhost
   git add .
   git commit -m "mensaje"
   git push origin main
   
   # Actualizar en servidor
   ssh papyrus "cd /home/ubuntu/paqueteria && git pull origin main"
   ```

2. **No copiar archivos manualmente al servidor**

3. **Usar el script de despliegue automatizado:**
   ```bash
   ./deploy-to-aws.sh "mensaje"
   ```

---

## 📝 Comandos de Referencia Rápida

```bash
# Limpieza automática (recomendada)
ssh papyrus "cd /home/ubuntu/paqueteria && bash limpiar-servidor.sh"

# Limpieza manual (un solo comando)
ssh papyrus "cd /home/ubuntu/paqueteria && rm deploy-aws.sh deploy.sh dev-up.sh pull-only.sh pull-update.sh rollback.sh setup-env.sh setup-production.sh update.sh"

# Verificar estado
ssh papyrus "cd /home/ubuntu/paqueteria && git status"

# Ver archivos en raíz
ssh papyrus "cd /home/ubuntu/paqueteria && ls -la *.sh"
```

---

## ✅ Checklist de Limpieza

- [ ] Ejecutar script de limpieza o eliminar archivos manualmente
- [ ] Verificar que `git status` muestra "working tree clean"
- [ ] Verificar que solo hay 5 archivos .sh en la raíz
- [ ] Verificar que los scripts en DOCS/scripts/deployment/ están intactos
- [ ] Probar que el despliegue automatizado funciona
- [ ] Documentar el proceso para el equipo

---

**Fecha:** 2025-11-16
**Problema:** Archivos duplicados en servidor
**Solución:** Script de limpieza automática
**Estado:** Listo para ejecutar
