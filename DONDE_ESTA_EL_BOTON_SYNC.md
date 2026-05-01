# 🔍 DÓNDE ESTÁ EL BOTÓN DE SINCRONIZACIÓN

## 📍 Ubicación del Botón

El botón de sincronización de base de datos aparece **SOLO en el entorno de STAGING** y **SOLO para usuarios ADMIN**.

### Dónde verlo:

1. **URL**: https://staging.jemavi.co
2. **Página**: Panel de Administración (`/admin`)
3. **Ubicación**: Esquina superior derecha, junto al botón "Actualizar"
4. **Apariencia**: Botón verde con icono de sincronización 🔄

```
┌─────────────────────────────────────────────────────────────┐
│  Panel de Administración                    [🔄 Sync] [↻]  │
│  Gestiona el sistema de paquetería                          │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Requisitos para Ver el Botón

Para que el botón aparezca, se deben cumplir TODAS estas condiciones:

1. ✅ **Entorno**: Debe ser STAGING (no producción)
2. ✅ **Usuario**: Debe ser ADMIN (no operador ni usuario)
3. ✅ **Página**: Debe estar en `/admin` (Panel de Administración)
4. ✅ **Variable de entorno**: `ENVIRONMENT=staging` en el `.env`

## 🔧 Cómo Verificar

### 1. Verificar que estás en staging:
```bash
# En el servidor de staging
cat /home/ubuntu/paqueteria-staging/CODE/.env | grep ENVIRONMENT
# Debe mostrar: ENVIRONMENT=staging
```

### 2. Verificar que eres ADMIN:
- Inicia sesión en https://staging.jemavi.co
- Ve a `/admin`
- Si ves la pestaña "Usuarios", eres ADMIN

### 3. Verificar en el navegador:
Abre la consola del navegador (F12) y ejecuta:
```javascript
// Verificar entorno
fetch('/api/config/environment')
  .then(r => r.json())
  .then(d => console.log('Entorno:', d.environment));

// Verificar si el botón existe
console.log('Botón existe:', !!document.getElementById('syncDbButton'));

// Mostrar el botón manualmente (para testing)
const btn = document.getElementById('syncDbButton');
if (btn) {
    btn.classList.remove('hidden');
    btn.classList.add('inline-flex');
    console.log('Botón mostrado');
}
```

## 🚨 Solución de Problemas

### Problema 1: No veo el botón en staging

**Causa**: La variable `ENVIRONMENT` no está configurada como `staging`

**Solución**:
```bash
# En el servidor de staging
cd /home/ubuntu/paqueteria-staging/CODE
nano .env

# Agregar o modificar:
ENVIRONMENT=staging

# Reiniciar servicios
cd ..
docker compose -f docker-compose.staging.yml restart
```

### Problema 2: El botón aparece pero está oculto

**Causa**: El JavaScript no detectó que es staging

**Solución temporal** (en consola del navegador):
```javascript
// Mostrar el botón manualmente
document.getElementById('syncDbButton').classList.remove('hidden');
document.getElementById('syncDbButton').classList.add('inline-flex');
```

**Solución permanente**:
Verificar que el endpoint `/api/config/environment` retorna `staging`:
```bash
curl https://staging.jemavi.co/api/config/environment
# Debe retornar: {"environment":"staging"}
```

### Problema 3: No soy ADMIN

**Causa**: Tu usuario no tiene rol de ADMIN

**Solución**:
Pide a otro administrador que te asigne el rol ADMIN, o ejecuta:
```bash
# En el servidor
cd /home/ubuntu/paqueteria-staging
docker compose -f docker-compose.staging.yml exec app python -c "
from app.database import SessionLocal
from app.models.user import User, UserRole
db = SessionLocal()
user = db.query(User).filter(User.username == 'TU_USUARIO').first()
if user:
    user.role = UserRole.ADMIN
    db.commit()
    print(f'Usuario {user.username} ahora es ADMIN')
else:
    print('Usuario no encontrado')
db.close()
"
```

## 🎯 Alternativa: Abrir el Modal Manualmente

Si el botón no aparece, puedes abrir el modal directamente desde la consola del navegador:

```javascript
// Abrir modal de sincronización
openSyncDatabaseModal();
```

O crear un bookmarklet:
```javascript
javascript:(function(){openSyncDatabaseModal();})();
```

## 📱 En Móvil

En dispositivos móviles, el botón muestra solo "Sync" en lugar de "Sincronizar BD" para ahorrar espacio.

## 🔄 Flujo Completo

1. Accede a https://staging.jemavi.co
2. Inicia sesión como ADMIN
3. Ve a `/admin` (Panel de Administración)
4. Busca el botón verde "🔄 Sincronizar BD" en la esquina superior derecha
5. Haz clic en el botón
6. Lee las advertencias
7. Confirma la sincronización
8. Observa los logs en tiempo real
9. Espera a que complete (5-10 minutos)
10. Recarga la página

## 📝 Archivos Modificados

Los siguientes archivos fueron modificados para agregar el botón:

1. **`CODE/src/templates/admin/admin_dashboard.html`**
   - Agregado botón en el header
   - Agregado modal de sincronización
   - Agregado script para detectar staging

2. **`CODE/src/app/routes/config.py`**
   - Agregado endpoint `/api/config/environment`

3. **`CODE/src/templates/components/sync-database-modal.html`**
   - Modal con interfaz de sincronización (ya existía)

4. **`CODE/src/app/routes/admin_sync.py`**
   - Endpoint de sincronización (ya existía)

## 🎨 Personalización

Si quieres cambiar la apariencia del botón, edita:
```html
<!-- En admin_dashboard.html -->
<button onclick="openSyncDatabaseModal()" id="syncDbButton" 
    class="... bg-green-600 hover:bg-green-700 ...">
    <!-- Cambiar bg-green-600 por otro color -->
</button>
```

## 📞 Soporte

Si después de seguir estos pasos aún no ves el botón:

1. Verifica que `ENVIRONMENT=staging` en el `.env`
2. Reinicia los servicios de staging
3. Limpia la caché del navegador (Ctrl+Shift+R)
4. Verifica que eres usuario ADMIN
5. Abre la consola del navegador y busca errores
6. Usa la alternativa de abrir el modal manualmente

---

**Resumen**: El botón aparece automáticamente en staging para usuarios ADMIN. Si no lo ves, verifica la variable `ENVIRONMENT` y tu rol de usuario.
