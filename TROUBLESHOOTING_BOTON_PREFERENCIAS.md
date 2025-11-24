# 🔧 Troubleshooting: Botón de Preferencias

## ✅ Estado Actual

- ✅ Botón morado visible en cada fila
- ✅ Modal HTML agregado
- ✅ JavaScript agregado
- ✅ Sin errores de sintaxis

---

## 🧪 Cómo Probar

### **1. Abrir la Consola del Navegador**

1. Ve a `http://localhost:8000/customers/manage`
2. Presiona `F12` para abrir DevTools
3. Ve a la pestaña "Console"

### **2. Hacer Clic en el Botón Morado**

1. Busca un cliente en la tabla
2. Haz clic en el botón morado (🔔)
3. Observa la consola

### **3. Verificar Logs**

Deberías ver en la consola:
```
openPreferencesModal llamado {customerId: "...", customerName: "..."}
Usando instancia global
```

O alguno de estos mensajes:
```
Usando Alpine.$data
Usando __x.$data
```

---

## ❌ Problemas Comunes

### **Problema 1: "Error: No se pudo abrir el modal"**

**Causa:** Alpine.js no está inicializado o la instancia no está disponible.

**Solución:**
1. Recarga la página completamente (`Ctrl+F5`)
2. Verifica que no haya errores de JavaScript en la consola
3. Verifica que Alpine.js esté cargado:
   ```javascript
   // En la consola del navegador:
   typeof Alpine
   // Debería retornar: "object"
   ```

### **Problema 2: Modal no se abre pero no hay error**

**Causa:** La propiedad `showPreferencesModal` no está cambiando.

**Solución:**
1. Abre la consola
2. Ejecuta:
   ```javascript
   const app = window.customerAppInstance;
   console.log(app);
   console.log(app.showPreferencesModal);
   ```
3. Si `app` es `undefined`, recarga la página

### **Problema 3: Error 404 en la API**

**Causa:** Las rutas de la API no están registradas.

**Solución:**
1. Verifica que las migraciones se ejecutaron:
   ```bash
   cd CODE
   alembic upgrade head
   ```
2. Verifica que el servidor esté corriendo:
   ```bash
   docker-compose ps
   ```
3. Verifica que las rutas estén registradas en `main.py`

### **Problema 4: Error "customer_id is required"**

**Causa:** El UUID del cliente no se está pasando correctamente.

**Solución:**
1. Verifica en la consola qué se está enviando:
   ```javascript
   // Debería mostrar el UUID del cliente
   ```
2. Si el `customerId` es `undefined`, verifica que el atributo `data-customer-id` esté en la fila de la tabla

---

## 🔍 Debug Manual

### **Paso 1: Verificar que el botón llama a la función**

En la consola del navegador:
```javascript
// Llamar manualmente la función
openPreferencesModal('test-id', 'Test Customer');
```

Si el modal se abre, el problema está en el onclick del botón.

### **Paso 2: Verificar la instancia de Alpine**

```javascript
// Obtener la instancia
const app = window.customerAppInstance;
console.log(app);

// Verificar que tiene el método
console.log(typeof app.openPreferencesModal);
// Debería ser: "function"

// Llamar directamente
app.openPreferencesModal('test-id', 'Test Customer');
```

### **Paso 3: Verificar que el modal existe**

```javascript
// Buscar el modal en el DOM
const modal = document.querySelector('[x-show="showPreferencesModal"]');
console.log(modal);
// Debería mostrar el elemento div del modal
```

### **Paso 4: Forzar apertura del modal**

```javascript
// Cambiar manualmente la propiedad
const app = window.customerAppInstance;
app.showPreferencesModal = true;
```

Si el modal aparece, el problema está en el método `openPreferencesModal`.

---

## 🛠️ Soluciones Rápidas

### **Solución 1: Recarga Completa**

```bash
# Limpiar caché del navegador
Ctrl + Shift + Delete (Chrome/Firefox)

# O forzar recarga
Ctrl + F5
```

### **Solución 2: Reiniciar Servidor**

```bash
docker-compose restart
```

### **Solución 3: Verificar Migraciones**

```bash
cd CODE
alembic current
alembic upgrade head
```

### **Solución 4: Verificar Logs del Servidor**

```bash
docker-compose logs -f app | grep -i "preferences"
```

---

## 📋 Checklist de Verificación

- [ ] El botón morado es visible
- [ ] Al hacer clic, aparece log en consola
- [ ] No hay errores en la consola del navegador
- [ ] Alpine.js está cargado (`typeof Alpine === "object"`)
- [ ] La instancia está disponible (`window.customerAppInstance !== undefined`)
- [ ] El modal existe en el DOM
- [ ] Las migraciones se ejecutaron
- [ ] El servidor está corriendo
- [ ] Las rutas de API están registradas

---

## 🆘 Si Nada Funciona

### **Opción 1: Verificar el Código**

1. Abre `CODE/src/templates/customers/manage.html`
2. Busca `showPreferencesModal:` (línea ~1757)
3. Verifica que esté dentro del `return {}` de `customerManagement()`
4. Busca `async openPreferencesModal(` (línea ~1776)
5. Verifica que esté dentro del `return {}` de `customerManagement()`

### **Opción 2: Comparar con el Código Original**

Abre `CODIGO_BOTON_PREFERENCIAS.html` y compara con el código actual.

### **Opción 3: Logs Detallados**

Agrega más logs al método:

```javascript
async openPreferencesModal(customerId, customerName) {
    console.log('=== INICIO openPreferencesModal ===');
    console.log('customerId:', customerId);
    console.log('customerName:', customerName);
    
    this.showPreferencesModal = true;
    console.log('showPreferencesModal cambiado a:', this.showPreferencesModal);
    
    // ... resto del código
}
```

---

## 📞 Información para Soporte

Si necesitas ayuda, proporciona:

1. **Logs de la consola del navegador** (captura de pantalla)
2. **Versión del navegador** (Chrome, Firefox, etc.)
3. **Logs del servidor** (`docker-compose logs app`)
4. **Resultado de:**
   ```javascript
   typeof Alpine
   typeof window.customerAppInstance
   ```

---

**Fecha:** 2025-01-24  
**Versión:** PAQUETEX v3.1  
**Estado:** 🔧 Troubleshooting
