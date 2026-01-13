# 🚀 Cómo Desplegar los Cambios a Staging

## Problema Actual
Los cambios de permisos están en tu código local, pero el servidor de staging sigue ejecutando el código antiguo con las restricciones.

## ✅ Solución - 3 Pasos Simples

### Paso 1: Commit y Push de los Cambios
```bash
cd CODE

# Ver qué archivos cambiaron
git status

# Agregar los archivos modificados
git add src/app/routes/products.py
git add src/templates/products/list.html
git add src/main.py

# Hacer commit
git commit -m "feat: permitir acceso a productos para todos los usuarios autenticados"

# Push a GitHub
git push origin main
```

### Paso 2: Desplegar a Staging
```bash
# Desde el directorio raíz del proyecto
./deploy.sh --env staging --deploy
```

O si prefieres el modo interactivo:
```bash
./deploy.sh

# Luego selecciona:
# 1. Entorno: staging
# 2. Opción: [1] Deploy Completo
```

### Paso 3: Verificar
1. Espera a que termine el deploy (puede tomar 1-2 minutos)
2. Ve a https://staging.jemavi.co/products
3. Recarga la página (Ctrl+F5 o Cmd+Shift+R)
4. ¡Debería funcionar sin errores de permisos!

---

## 🔧 Alternativa: Deploy Manual por SSH

Si el script de deploy no funciona, puedes hacerlo manualmente:

```bash
# Conectar al servidor
ssh staging

# Ir al directorio del proyecto
cd /ruta/del/proyecto

# Pull de los cambios
git pull origin main

# Reiniciar los contenedores
docker-compose restart

# Salir
exit
```

---

## 📋 Verificación Post-Deploy

Después del deploy, verifica que:

1. ✅ La página de productos carga sin errores
2. ✅ Puedes ver la tabla de productos
3. ✅ El botón "Sincronizar" funciona
4. ✅ No aparece el mensaje de permisos

---

## ⚠️ Notas Importantes

- El deploy puede tomar 1-2 minutos
- Los contenedores se reiniciarán automáticamente
- Si hay usuarios conectados, pueden perder su sesión temporalmente
- Asegúrate de hacer el commit y push ANTES de desplegar

---

## 🆘 Si Algo Sale Mal

Si después del deploy sigue sin funcionar:

1. **Verificar que el código se actualizó:**
   ```bash
   ssh staging
   cd /ruta/del/proyecto
   git log -1  # Ver el último commit
   ```

2. **Verificar logs del contenedor:**
   ```bash
   docker-compose logs -f --tail=50
   ```

3. **Reiniciar manualmente:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **Limpiar caché del navegador:**
   - Ctrl+Shift+Delete (Chrome/Firefox)
   - Seleccionar "Caché" y "Cookies"
   - Limpiar
