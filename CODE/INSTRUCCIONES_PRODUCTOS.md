# 📦 Instrucciones para Activar la Vista de Productos

## Problema Actual
El mensaje "Error al sincronizar productos. Verifica que tengas permisos de administrador" aparece porque tu usuario NO tiene permisos de ADMINISTRADOR en la base de datos.

## Solución (Elige UNA opción)

### ✅ OPCIÓN 1: Dar Permisos de Admin (RECOMENDADO)

1. **Listar usuarios disponibles:**
```bash
cd CODE
python dar_permisos_admin.py listar
```

2. **Dar permisos de admin a tu usuario:**
```bash
python dar_permisos_admin.py TU_USUARIO
```

Ejemplo:
```bash
python dar_permisos_admin.py jveyes
```

3. **Cerrar sesión y volver a iniciar sesión** en la aplicación web

4. **Ahora podrás sincronizar productos** desde el botón "Sincronizar" en la vista

---

### ✅ OPCIÓN 2: Sincronizar Productos Manualmente (Sin cambiar permisos)

Si no quieres dar permisos de admin, puedes sincronizar los productos una vez manualmente:

```bash
cd CODE
python sync_products_initial.py
```

Esto sincronizará los productos desde DynamiaERP y los guardará en la base de datos. Después podrás verlos en la vista (aunque no podrás sincronizar de nuevo sin permisos de admin).

---

### ✅ OPCIÓN 3: Dar Permisos Directamente en la Base de Datos

Si tienes acceso a la base de datos PostgreSQL:

```sql
-- Ver usuarios actuales
SELECT id, username, full_name, email, role FROM users;

-- Dar permisos de admin a un usuario específico
UPDATE users SET role = 'ADMIN' WHERE username = 'TU_USUARIO';
```

---

## Verificación

Después de dar permisos de admin:

1. ✅ Cierra sesión en la aplicación web
2. ✅ Vuelve a iniciar sesión
3. ✅ Ve a la vista de Productos (tab "DynamiaERP")
4. ✅ Haz clic en el botón "Sincronizar"
5. ✅ Espera a que se complete la sincronización (puede tomar varios minutos)
6. ✅ Los productos aparecerán en la tabla

---

## Roles del Sistema

- **ADMIN**: Puede sincronizar productos, gestionar usuarios, ver todo
- **OPERADOR**: Puede gestionar paquetes, ver clientes
- **USUARIO**: Solo puede ver sus propios datos

---

## Notas Importantes

- La sincronización puede tomar varios minutos dependiendo de la cantidad de productos en DynamiaERP
- Solo los usuarios con rol ADMIN pueden sincronizar productos
- Los productos se sincronizan desde la API de DynamiaERP
- La configuración de columnas es personalizable por usuario

---

## ¿Necesitas Ayuda?

Si tienes problemas:

1. Verifica que las credenciales de DynamiaERP estén configuradas en el archivo `.env`
2. Verifica que el usuario tenga rol ADMIN
3. Revisa los logs del servidor para ver errores específicos
