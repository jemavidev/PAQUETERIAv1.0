/**
 * PAQUETES EL CLUB v4.0 - Gestión Dinámica de Tarifas
 * Carga tarifas desde .env y las aplica dinámicamente en el frontend
 */

// Variable global para almacenar las tarifas
window.packageRates = null;

/**
 * Cargar tarifas dinámicas desde el backend
 */
async function loadDynamicRates() {
    console.log('🔄 Cargando tarifas dinámicas desde .env...');
    
    try {
        const response = await fetch('/api/packages/rates/dynamic');
        const data = await response.json();
        
        if (data.success && data.rates) {
            window.packageRates = data.rates;
            console.log('✅ Tarifas cargadas exitosamente desde .env:', window.packageRates);
            console.log(`   💰 Normal: $${window.packageRates.normal} COP`);
            console.log(`   💰 Extra Dimensionado: $${window.packageRates.extra_dimensioned} COP`);
            console.log(`   📦 Almacenamiento/día: $${window.packageRates.storage_per_day} COP`);
            return window.packageRates;
        } else {
            console.error('❌ Error al cargar tarifas:', data);
            return null;
        }
    } catch (error) {
        console.error('❌ Error al obtener tarifas dinámicas:', error);
        return null;
    }
}

/**
 * Obtener tarifa según tipo de paquete
 */
function getRateByPackageType(packageType) {
    // Intentar obtener tarifas de window.appConfig primero (cargado desde el template)
    if (window.appConfig && window.appConfig.rates) {
        if (packageType === 'normal') {
            return window.appConfig.rates.normal || 1500;
        } else if (packageType === 'extra_dimensioned') {
            return window.appConfig.rates.extra_dimensioned || 2000;
        }
        return window.appConfig.rates.normal || 1500;
    }
    
    // Si window.packageRates está disponible (cargado dinámicamente)
    if (window.packageRates) {
        if (packageType === 'normal') {
            return window.packageRates.normal;
        } else if (packageType === 'extra_dimensioned') {
            return window.packageRates.extra_dimensioned;
        }
        return window.packageRates.normal; // Default
    }
    
    // Valores por defecto que coinciden con .env (último recurso)
    console.warn('⚠️ Tarifas no cargadas, usando valores por defecto del .env');
    return packageType === 'normal' ? 1500 : 2000;
}

/**
 * Actualizar visualización de tarifa en el modal de recepción
 */
async function updatePackageTypeFeeDisplay() {
    const packageTypeSelect = document.getElementById('packageType');
    if (!packageTypeSelect) return;
    
    // Cargar tarifas si no están disponibles
    if (!window.packageRates) {
        await loadDynamicRates();
    }
    
    const selectedType = packageTypeSelect.value;
    if (!selectedType) return;
    
    const baseFee = getRateByPackageType(selectedType);
    const feeDescription = selectedType === 'normal' ? 'Normal (30x30x30cm)' : 'Extra Dimensionado';
    
    console.log(`🔍 Tipo seleccionado: ${selectedType} | Tarifa: $${baseFee} COP`);
    
    // Buscar o crear elemento para mostrar tarifa
    let feeDisplay = document.getElementById('packageTypeFeeDisplay');
    if (!feeDisplay) {
        // Crear elemento si no existe
        feeDisplay = document.createElement('div');
        feeDisplay.id = 'packageTypeFeeDisplay';
        feeDisplay.className = 'mt-3 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl shadow-sm';
        
        // Insertar después del select de tipo de paquete
        const parentDiv = packageTypeSelect.parentNode;
        if (parentDiv.nextSibling) {
            parentDiv.parentNode.insertBefore(feeDisplay, parentDiv.nextSibling);
        } else {
            parentDiv.parentNode.appendChild(feeDisplay);
        }
    }
    
    if (baseFee > 0) {
        feeDisplay.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center">
                    <svg class="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <div>
                        <span class="text-sm font-semibold text-blue-900">Tarifa Base de Entrega</span>
                        <div class="text-xs text-blue-600">${feeDescription}</div>
                    </div>
                </div>
                <div class="text-2xl font-bold text-blue-900">
                    $${baseFee.toLocaleString()}
                </div>
            </div>
            <div class="flex items-start text-xs text-blue-700 bg-blue-100 rounded-lg p-2">
                <svg class="w-4 h-4 mr-1 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                </svg>
                <div>
                    <div>✓ Tarifa configurada dinámicamente desde .env</div>
                    <div class="mt-1">* Se agregarán $${window.packageRates?.storage_per_day || 1000}/día de almacenamiento si aplica</div>
                </div>
            </div>
        `;
        feeDisplay.style.display = 'block';
    } else {
        feeDisplay.style.display = 'none';
    }
}

/**
 * Inicializar listener para cambios en el tipo de paquete
 */
function initializePackageTypeListener() {
    const packageTypeSelect = document.getElementById('packageType');
    if (packageTypeSelect) {
        packageTypeSelect.addEventListener('change', updatePackageTypeFeeDisplay);
        console.log('✅ Listener de tipo de paquete inicializado');
    }
}

// Cargar tarifas al cargar la página
document.addEventListener('DOMContentLoaded', async () => {
    await loadDynamicRates();
});
