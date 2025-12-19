# 📋 Código Listo para Copiar y Pegar

## 1. Backend - Modificar Endpoint

**Archivo:** `CODE/src/app/routes/public.py`

**Buscar la línea ~1690 que dice:**
```python
@router.get("/api/customers/search-by-phone")
async def search_customer_by_phone_public(
```

**Reemplazar toda la función con esto:**

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
        
        # Normalizar teléfono
        normalized_phone = normalize_phone(phone)
        
        # Buscar cliente
        customer_service = CustomerService()
        customer = customer_service.get_customer_by_phone(db, normalized_phone)
        
        if not customer:
            return JSONResponse(
                status_code=404,
                content={"detail": "Cliente no encontrado"}
            )
        
        # 🆕 BUSCAR PAQUETES ANUNCIADOS
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
        
        logger.info(f"Cliente {customer.id} tiene {len(announced_codes)} paquetes anunciados")
        
        # Retornar datos del cliente + códigos de paquetes anunciados
        return {
            "id": str(customer.id),
            "full_name": customer.full_name,
            "display_name": customer.display_name,
            "phone": customer.phone,
            "email": customer.email,
            "is_vip": customer.is_vip,
            "total_packages_received": customer.total_packages_received,
            # 🆕 CÓDIGOS DE PAQUETES ANUNCIADOS
            "announced_codes": announced_codes,
            "total_announced": len(announced_codes),
            "has_announced_packages": len(announced_codes) > 0
        }
        
    except Exception as e:
        logger.error(f"Error buscando cliente por teléfono: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error al buscar cliente: {str(e)}"}
        )
```

---

## 2. Frontend - Agregar JavaScript

**Archivo:** `CODE/src/templates/announce/announce_quick.html`

**Buscar el final del archivo (antes de `</body>`) y agregar:**

```html
<script>
/**
 * Buscar cliente por teléfono y mostrar paquetes anunciados
 */
async function buscarClientePorTelefono(telefono) {
    try {
        // Limpiar alertas previas
        limpiarAlertasPaquetes();
        
        // Llamar al API
        const response = await fetch(`/api/customers/search-by-phone?phone=${telefono}`);
        
        if (response.status === 404) {
            // Cliente no encontrado - continuar proceso normal
            const nameInput = document.getElementById('customer-name');
            if (nameInput) {
                nameInput.value = '';
                nameInput.disabled = false;
            }
            return;
        }
        
        if (!response.ok) {
            console.error('Error al buscar cliente:', response.status);
            return;
        }
        
        const data = await response.json();
        
        // Mostrar nombre del cliente
        const nameInput = document.getElementById('customer-name');
        if (nameInput) {
            nameInput.value = data.display_name || data.full_name;
        }
        
        // Mostrar códigos de paquetes anunciados si existen
        if (data.has_announced_packages && data.announced_codes.length > 0) {
            mostrarCodigosConsulta(data.announced_codes);
        }
        
    } catch (error) {
        console.error('Error buscando cliente:', error);
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
        
        // Insertar después del campo de nombre
        const nameInput = document.getElementById('customer-name');
        if (nameInput && nameInput.parentElement) {
            nameInput.parentElement.insertAdjacentElement('afterend', alertContainer);
        }
    }
    
    // Construir HTML con enlaces
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
 * Limpiar alertas de paquetes
 */
function limpiarAlertasPaquetes() {
    const alertContainer = document.getElementById('announced-packages-alert');
    if (alertContainer) {
        alertContainer.remove();
    }
}

// Event listener para buscar cuando se ingresa el teléfono
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('customer-phone');
    
    if (phoneInput) {
        // Buscar al perder el foco
        phoneInput.addEventListener('blur', function() {
            const telefono = this.value.trim();
            if (telefono.length >= 10) {
                buscarClientePorTelefono(telefono);
            }
        });
        
        // También buscar al presionar Enter
        phoneInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const telefono = this.value.trim();
                if (telefono.length >= 10) {
                    buscarClientePorTelefono(telefono);
                }
            }
        });
    }
});
</script>
```

---

## 3. Probar

```bash
# Ejecutar script de prueba
python test_paquetes_anunciados.py 3001234567

# O probar manualmente en:
# https://staging.jemavi.co/announce-papyrus
```

---

## 4. Deploy

```bash
# Commit
git add .
git commit -m "feat: mostrar códigos de paquetes anunciados en announce-papyrus"

# Deploy a staging
./deploy.sh staging

# Después de probar, deploy a producción
./deploy.sh production
```

---

## ✅ Eso es todo!

Solo necesitas:
1. Copiar el código del backend
2. Copiar el código del frontend
3. Probar
4. Deploy

Simple y directo.
