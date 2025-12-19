// ========================================
// INTEGRACIÓN FRONTEND: Mostrar Paquetes Anunciados
// ========================================
// 
// Este código debe agregarse en:
// CODE/src/templates/announce/announce_quick.html
// O en el archivo JavaScript correspondiente
// ========================================

/**
 * Buscar cliente por teléfono y mostrar paquetes anunciados
 */
async function buscarClientePorTelefono(telefono) {
    try {
        // Mostrar indicador de carga
        mostrarCargando(true);
        
        // Limpiar alertas previas
        limpiarAlertasPaquetes();
        
        // Llamar al API
        const response = await fetch(`/api/customers/search-by-phone?phone=${telefono}`);
        
        if (response.status === 404) {
            // Cliente no encontrado - continuar con proceso normal
            manejarClienteNuevo(telefono);
            return;
        }
        
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Mostrar información del cliente
        mostrarInformacionCliente(data);
        
        // 🆕 VERIFICAR Y MOSTRAR CÓDIGOS DE PAQUETES ANUNCIADOS
        if (data.has_announced_packages && data.announced_codes.length > 0) {
            mostrarCodigosConsulta(data.announced_codes);
        }
        
    } catch (error) {
        console.error('Error buscando cliente:', error);
        mostrarError('Error al buscar cliente. Intente nuevamente.');
    } finally {
        mostrarCargando(false);
    }
}

/**
 * Mostrar información básica del cliente
 */
function mostrarInformacionCliente(cliente) {
    // Rellenar el campo de nombre
    const nombreInput = document.getElementById('customer-name');
    if (nombreInput) {
        nombreInput.value = cliente.display_name || cliente.full_name;
    }
    
    // Mostrar badge VIP si aplica
    if (cliente.is_vip) {
        mostrarBadgeVIP();
    }
    
    // Mostrar estadísticas
    const statsDiv = document.getElementById('customer-stats');
    if (statsDiv) {
        statsDiv.innerHTML = `
            <div class="text-sm text-gray-600">
                <span class="font-medium">${cliente.total_packages_received}</span> paquetes recibidos
            </div>
        `;
    }
}

/**
 * 🆕 Mostrar códigos de consulta de paquetes anunciados como enlaces
 */
function mostrarCodigosConsulta(codes) {
    // Crear contenedor de alerta si no existe
    let alertContainer = document.getElementById('announced-packages-alert');
    
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'announced-packages-alert';
        
        // Insertar después del campo de nombre del cliente
        const nameInput = document.getElementById('customer-name');
        if (nameInput && nameInput.parentElement) {
            nameInput.parentElement.insertAdjacentElement('afterend', alertContainer);
        }
    }
    
    // Construir HTML con enlaces a la vista de búsqueda
    const codigosHTML = codes.map(code => {
        const searchUrl = `https://staging.jemavi.co/search?auto_search=${code.tracking_code}`;
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
                        <span class="sr-only">Cerrar</span>
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Scroll suave hacia la alerta
    alertContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Limpiar alertas de paquetes anunciados
 */
function limpiarAlertasPaquetes() {
    const alertContainer = document.getElementById('announced-packages-alert');
    if (alertContainer) {
        alertContainer.remove();
    }
}

/**
 * Manejar cliente nuevo (continuar con proceso normal)
 */
function manejarClienteNuevo(telefono) {
    console.log('Cliente nuevo:', telefono);
    
    // Limpiar el campo de nombre para que el usuario lo ingrese
    const nombreInput = document.getElementById('customer-name');
    if (nombreInput) {
        nombreInput.value = '';
        nombreInput.focus();
        nombreInput.disabled = false; // Habilitar edición
    }
    
    // Remover alerta de paquetes si existe
    limpiarAlertasPaquetes();
}

/**
 * Mostrar/ocultar indicador de carga
 */
function mostrarCargando(mostrar) {
    const loader = document.getElementById('loading-indicator');
    if (loader) {
        loader.style.display = mostrar ? 'block' : 'none';
    }
}

/**
 * Mostrar mensaje de error
 */
function mostrarError(mensaje) {
    // Implementar según tu sistema de alertas
    console.error(mensaje);
    alert(mensaje);
}

/**
 * Mostrar badge VIP
 */
function mostrarBadgeVIP() {
    const nombreInput = document.getElementById('customer-name');
    if (nombreInput && nombreInput.parentElement) {
        const badge = document.createElement('span');
        badge.className = 'ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800';
        badge.innerHTML = '⭐ VIP';
        nombreInput.parentElement.appendChild(badge);
    }
}

// ========================================
// EVENT LISTENERS
// ========================================

// Buscar cliente cuando se ingresa el teléfono
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('customer-phone');
    
    if (phoneInput) {
        // Buscar al perder el foco (blur)
        phoneInput.addEventListener('blur', function() {
            const telefono = this.value.trim();
            if (telefono.length >= 10) {
                buscarClientePorTelefono(telefono);
            }
        });
        
        // O buscar al presionar Enter
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
