# Instrucciones para Push a GitHub

## ✅ Estado Actual

- ✅ Repositorio Git inicializado
- ✅ Commit inicial realizado (333 archivos)
- ✅ Rama principal: `main`
- ⏳ Pendiente: Agregar remoto y hacer push

## 🚀 Opción 1: Usar el Script Automático

Si ya creaste el repositorio "PAQUETERIAv1.0" en GitHub:

```bash
./push-to-github.sh TU_USUARIO_GITHUB
```

Ejemplo:
```bash
./push-to-github.sh johndoe
```

## 🚀 Opción 2: Comandos Manuales

### Paso 1: Crear el repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `PAQUETERIAv1.0`
3. Descripción: "Sistema de gestión de paquetería - Versión 1.0"
4. Elige si será público o privado
5. **NO** inicialices con README, .gitignore o licencia (ya los tenemos)
6. Click en "Create repository"

### Paso 2: Agregar remoto y hacer push

Reemplaza `TU_USUARIO_GITHUB` con tu nombre de usuario real:

```bash
# Agregar remoto
git remote add origin https://github.com/TU_USUARIO_GITHUB/PAQUETERIAv1.0.git

# Verificar remoto
git remote -v

# Hacer push
git push -u origin main
```

### Si usas SSH en lugar de HTTPS:

```bash
git remote add origin git@github.com:TU_USUARIO_GITHUB/PAQUETERIAv1.0.git
git push -u origin main
```

## 🔐 Autenticación

Si GitHub te pide autenticación:

### Para HTTPS:
- Usa un Personal Access Token (PAT) como contraseña
- Crea uno en: https://github.com/settings/tokens
- Permisos necesarios: `repo` (acceso completo a repositorios)

### Para SSH:
- Asegúrate de tener tu clave SSH configurada en GitHub
- Verifica con: `ssh -T git@github.com`

## ✅ Verificación

Después del push, verifica en GitHub:
- ✅ Todos los archivos están presentes
- ✅ El README se renderiza correctamente
- ✅ La documentación es accesible
- ✅ No hay archivos `.env` o sensibles

## 📝 Comandos Útiles

```bash
# Ver estado del repositorio
git status

# Ver commits
git log --oneline

# Ver remotos configurados
git remote -v

# Cambiar URL del remoto (si es necesario)
git remote set-url origin NUEVA_URL

# Verificar conexión con GitHub
git ls-remote origin
```

## 🆘 Solución de Problemas

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/TU_USUARIO/PAQUETERIAv1.0.git
```

### Error: "repository not found"
- Verifica que el repositorio existe en GitHub
- Verifica que el nombre es exactamente "PAQUETERIAv1.0"
- Verifica que tienes permisos de escritura

### Error: "authentication failed"
- Verifica tus credenciales
- Si usas HTTPS, usa un Personal Access Token
- Si usas SSH, verifica tu clave SSH

---

**Nota**: Si necesitas ayuda, proporciona tu nombre de usuario de GitHub y puedo ejecutar los comandos por ti.

