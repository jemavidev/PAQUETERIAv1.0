# 📦 Implementación Simple: Mostrar Paquetes Anunciados

## 🎯 Flujo Simplificado

1. **Usuario ingresa teléfono** en `/announce-papyrus`
2. **Sistema busca cliente:**
   - ✅ **Cliente existe:** Muestra nombre + códigos de consulta de paquetes anunciados (como enlaces)
   - ❌ **Cliente NO existe:** Continúa con proceso normal (pide nombre)
3. **Códigos mostrados como enlaces:** Clic abre `/search?auto_search=CODIGO`

## 📋 Ejemplo Visual

### Cliente con Paquetes Anunciados:
```
┌─────────────────────────────────────────────────────┐
│ Teléfono: 3001234567                                │
│ Nombre: JUAN PEREZ                                  │
│                                                      │
│ ┌─────────────────────────────────────────────────┐ │
│ │ ℹ️ Este cliente tiene 2 paquete(s) anunciado(s) │ │
│ │                                                  │ │
│ │ Códigos de consulta (clic para ver detalles):   │ │
│ │ • 5SX8 🔗                                        │ │
│ │ • A1B2 🔗                                        │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│ [Anunciar Paquete]                                  │
└─────────────────────────────────────────────────────┘
```

### Cliente sin Paquetes Anunciados:
```
┌─────────────────────────────────────────────────────┐
│ Teléfono: 3009876543                                │
│ Nombre: MARIA LOPEZ                                 │
│                                                      │
│ [Anunciar Paquete]                                  │
└─────────────────────────────────────────────────────┘
```

### Cliente Nuevo:
```
┌─────────────────────────────────────────────────────┐
│ Teléfono: 3005555555                                │
│ Nombre: [Campo vacío - usuario debe ingresar]      │
│                                                      │
│ [Anunciar Paquete]                                  │
└─────────────────────────────────────────────────────┘
```

## 🔧 Implementación

### 1. Backend (CODE/src/app/routes/public.py)

Reemplazar el endpoint en la línea ~1690:

```python
@router.get("/api/customers/search-by-phone")
async def search_customer_by_phone_public(
    phone: str,
    db: Session = Depends(get_db)
):
    """Buscar cliente por teléfono - Incluye códigos de paquetes anunciados"""
    try:
        from app.utils.phone_utils import normalize_phone
        from app.services.customer_service import CustomerService
        
        normalized_phone = normalize_phone(phone)
        customer_service = CustomerService()
        customer = customer_service.get_customer_by_phone(db, normalized_phone)
        
        if not customer:
            return JSONResponse(
                status_code=404,
                content={"detail": "Cliente no encontrado"}
            )
        
        # Buscar paquetes anunciados
        announced_packages = db.query(PackageAnnouncementNew).filter(
            PackageAnnouncementNew.customer_id == customer.id,
            PackageAnnouncementNew.is_processed == False,
            PackageAnnouncementNew.is_active == True
        ).order_by(PackageAnnouncementNew.announced_at.desc()).all()
        
        # Solo devolver tracking_codes
        announced_codes = [
            {"tracking_code": pkg.tracking_code}
            for pkg in announced_packages
        ]
        
        return {
            "id": str(customer.id),
            "full_name": customer.full_name,
            "display_name": customer.display_name,
            "phone": customer.phone,
            "email": customer.email,
            "is_vip": customer.is_vip,
            "total_packages_received": customer.total_packages_received,
            "announced_codes": announced_codes,
            "total_announced": len(announced_codes),
            "has_announced_packages": len(announced_codes) > 0
        }
        
    except Exception as e:
        logger.error(f"Error buscando cliente: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error: {str(e)}"}
        )
```

### 2. Frontend (CODE/src/templates/announce/announce_quick.html)

Agregar este JavaScript al final del archivo, antes de `</body>`:

```javascript
<script>
/**
 * Buscar cliente por teléfono
 */
async function buscarClientePorTelefono(telefono) {
    try {
        limpiarAlertasPaquetes();
        
        const response = await fetch(`/api/customers/search-by-phone?phone=${telefono}`);
        
        if (response.status === 404) {
            // Cliente nuevo - continuar proceso normal
            document.getElementById('customer-name').value = '';
            document.getElementById('customer-name').disabled = false;
            return;
        }
        
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Mostrar nombre del cliente
        const nameInput = document.getElementById('customer-name');
        if (nameInput) {
            nameInput.value = data.display_name || data.full_name;
        }
        
        // Mostrar códigos de paquetes anunciados
        if (data.has_announced_packages && data.announced_codes.length > 0) {
            mostrarCodigosConsulta(data.announced_codes);
        }
        
    } catch (error) {
        console.error('Error:', error);
    }
}

/**
 * Mostrar códigos de consulta como enlaces
 */
function mostrarCodigosConsulta(codes) {
    let alertContainer = document.getElementById('announced-packages-alert');
    
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'announced-packages-alert';
        
        const nameInput = document.getElementById('customer-name');
        if (nameInput && nameInput.parentElement) {
            nameInput.parentElement.insertAdjacentElement('afterend', alertContainer);
        }
    }
    
    const codigosHTML = codes.map(code => {
        const searchUrl = `/search?auto_search=${code.tracking_code}`;
        return `
            <li class="py-1">
                <a href="${searchUrl}" 
                   target="_blank"
                   class="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium hover:underline">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                    ${code.tracking_code}
                </a>
            </li>
        `;
    }).join('');
    
    alertContainer.innerHTML = `
        <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4 rounded-r-lg shadow-sm">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="ml-3 flex-1">
                    <h3 class="text-sm font-medium text-blue-800">
                        ℹ️ Este cliente tiene ${codes.length} paquete(s) anunciado(s)
                    </h3>
                    <div class="mt-2">
                        <p class="text-sm text-blue-700 mb-2">
                            Códigos de consulta (clic para ver detalles):
                        </p>
                        <ul class="text-sm space-y-1">
                            ${codigosHTML}
                        </ul>
                    </div>
                </div>
                <div class="ml-3 flex-shrink-0">
                    <button 
                        onclick="limpiarAlertasPaquetes()"
                        class="inline-flex text-blue-400 hover:text-blue-600 focus:outline-none"
                    >
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Limpiar alertas
 */
function limpiarAlertasPaquetes() {
    const alertContainer = document.getElementById('announced-packages-alert');
    if (alertContainer) {
        alertContainer.remove();
    }
}

// Event listener para el campo de teléfono
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('customer-phone');
    
    if (phoneInput) {
        phoneInput.addEventListener('blur', function() {
            const telefono = this.value.trim();
            if (telefono.length >= 10) {
                buscarClientePorTelefono(telefono);
            }
        });
    }
});
</script>
```

## 🧪 Pruebas

### Prueba 1: Cliente con Paquetes Anunciados
```bash
# 1. Crear un paquete anunciado para un cliente
# 2. Ir a: https://staging.jemavi.co/announce-papyrus
# 3. Ingresar el teléfono del cliente
# 4. Verificar que aparecen los códigos como enlaces
# 5. Hacer clic en un código
# 6. Verificar que abre /search?auto_search=CODIGO
```

### Prueba 2: Cliente sin Paquetes Anunciados
```bash
# 1. Ir a: https://staging.jemavi.co/announce-papyrus
# 2. Ingresar teléfono de cliente sin paquetes anunciados
# 3. Verificar que solo muestra el nombre
# 4. NO debe aparecer ninguna alerta
```

### Prueba 3: Cliente Nuevo
```bash
# 1. Ir a: https://staging.jemavi.co/announce-papyrus
# 2. Ingresar teléfono que no existe
# 3. Verificar que el campo de nombre queda vacío
# 4. Usuario debe poder ingresar el nombre manualmente
```

## 📊 Consulta SQL para Verificar

```sql
-- Ver clientes con paquetes anunciados
SELECT 
    c.full_name,
    c.phone,
    a.tracking_code,
    a.guide_number,
    a.announced_at
FROM customers c
INNER JOIN package_announcements_new a ON c.id = a.customer_id
WHERE a.is_processed = FALSE 
  AND a.is_active = TRUE
ORDER BY c.full_name, a.announced_at DESC;
```

## 🚀 Deploy

```bash
# 1. Hacer los cambios en el código
# 2. Commit
git add .
git commit -m "feat: mostrar códigos de paquetes anunciados en announce-papyrus"

# 3. Deploy a staging
./deploy.sh staging

# 4. Probar en staging
# 5. Deploy a producción
./deploy.sh production
```

## ✅ Checklist

- [ ] Modificar endpoint `/api/customers/search-by-phone`
- [ ] Agregar JavaScript en `announce_quick.html`
- [ ] Probar con cliente que tiene paquetes anunciados
- [ ] Verificar que los enlaces funcionan correctamente
- [ ] Probar con cliente sin paquetes anunciados
- [ ] Probar con cliente nuevo
- [ ] Verificar estilos en móvil
- [ ] Deploy a staging
- [ ] Pruebas en staging
- [ ] Deploy a producción

## 🎨 Personalización

Si quieres cambiar la URL base de los enlaces, modifica esta línea:

```javascript
const searchUrl = `/search?auto_search=${code.tracking_code}`;

// Para producción:
const searchUrl = `https://jemavi.co/search?auto_search=${code.tracking_code}`;

// Para staging:
const searchUrl = `https://staging.jemavi.co/search?auto_search=${code.tracking_code}`;
```

## 📝 Notas

- Los enlaces se abren en nueva pestaña (`target="_blank"`)
- Solo se muestran códigos de paquetes con `is_processed = FALSE`
- Los códigos son enlaces clicables que llevan a la vista de búsqueda
- Si el cliente no tiene paquetes anunciados, no se muestra ninguna alerta
- Si el cliente no existe, continúa el flujo normal de anuncio
