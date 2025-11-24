# 🎯 Implementación: Botón de Preferencias en Gestión de Clientes

## 📋 Objetivo

Agregar un botón "Preferencias" en `/customers/manage` que permita a los administradores:
1. Ver las preferencias de notificaciones de un cliente
2. Modificar las preferencias si es necesario
3. Generar/copiar el link de preferencias para enviar al cliente

---

## 🔧 Cambios a Realizar

### **1. Agregar Botón de Preferencias en la Tabla**

En `CODE/src/templates/customers/manage.html`, buscar la sección de botones de acciones (alrededor de la línea 253) y agregar:

```html
<!-- ANTES (botones existentes) -->
<button onclick="openViewModalFromRow(this)" ...>Ver</button>
<button onclick="openEditModalFromRow(this)" ...>Editar</button>
<button onclick="deleteCustomer('{{ customer.id }}')" ...>Eliminar</button>

<!-- AGREGAR NUEVO BOTÓN -->
<button onclick="openPreferencesModal('{{ customer.id }}', '{{ customer.full_name }}')"
        title="Gestionar Preferencias"
        class="inline-flex items-center justify-center w-9 h-9 border border-transparent text-xs font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 transition-colors duration-200">
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
    </svg>
</button>
```

### **2. Agregar Modal de Preferencias**

Agregar al final del archivo, antes del cierre de `</div>` principal:

```html
<!-- Modal de Preferencias de Cliente -->
<div x-show="showPreferencesModal" 
     x-cloak
     x-transition
     class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
     @click.away="closePreferencesModal()"
     @click.self="closePreferencesModal()"
     @keydown.escape.window="closePreferencesModal()"
     style="display: none;">
    <div class="relative top-20 mx-auto p-5 w-11/12 md:w-3/4 lg:w-1/2 max-w-2xl" @click.stop>
        <div class="bg-white rounded-xl shadow-lg border border-gray-100">
            <!-- Header -->
            <div class="border-b border-gray-100 px-6 py-4 flex items-center justify-between">
                <div>
                    <h3 class="text-xl font-light text-gray-900">Preferencias de Notificaciones</h3>
                    <p class="text-sm text-gray-500 mt-1" x-text="preferencesCustomerName"></p>
                </div>
                <button @click="closePreferencesModal()" class="text-gray-400 hover:text-gray-600 transition-colors">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>

            <!-- Loading State -->
            <div x-show="preferencesLoading" class="px-6 py-12 text-center">
                <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                <p class="mt-4 text-gray-600">Cargando preferencias...</p>
            </div>

            <!-- Content -->
            <div x-show="!preferencesLoading" class="px-6 py-6">
                
                <!-- Link de Preferencias -->
                <div class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div class="flex items-start">
                        <svg class="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <div class="ml-3 flex-1">
                            <p class="text-sm font-medium text-blue-800">Link de Preferencias del Cliente</p>
                            <div class="mt-2 flex items-center space-x-2">
                                <input type="text" 
                                       x-model="preferencesUrl" 
                                       readonly
                                       class="flex-1 px-3 py-2 text-sm border border-blue-300 rounded-lg bg-white">
                                <button @click="copyPreferencesUrl()" 
                                        class="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors">
                                    <span x-show="!urlCopied">Copiar</span>
                                    <span x-show="urlCopied">✓ Copiado</span>
                                </button>
                            </div>
                            <p class="mt-2 text-xs text-blue-700">Envía este link al cliente para que gestione sus preferencias</p>
                        </div>
                    </div>
                </div>

                <!-- Preferencias -->
                <div class="space-y-4">
                    <h4 class="text-sm font-medium text-gray-900">Preferencias Actuales</h4>

                    <!-- Tipo de Notificaciones -->
                    <div class="space-y-3">
                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                                <p class="text-sm font-medium text-gray-900">📱 SMS</p>
                                <p class="text-xs text-gray-500">Notificaciones por SMS</p>
                            </div>
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" x-model="preferences.sms_notifications_enabled" class="sr-only peer">
                                <div class="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-purple-600 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                            </label>
                        </div>

                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                                <p class="text-sm font-medium text-gray-900">📧 Email</p>
                                <p class="text-xs text-gray-500">Notificaciones por Email</p>
                            </div>
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" x-model="preferences.email_notifications_enabled" class="sr-only peer">
                                <div class="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-purple-600 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                            </label>
                        </div>
                    </div>

                    <!-- Eventos -->
                    <div class="space-y-3 mt-4">
                        <h5 class="text-xs font-medium text-gray-700 uppercase">Eventos de Paquetes</h5>
                        
                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                                <p class="text-sm font-medium text-gray-900">📦 Paquete Anunciado</p>
                            </div>
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" x-model="preferences.notify_package_announced" class="sr-only peer">
                                <div class="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-purple-600 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                            </label>
                        </div>

                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                                <p class="text-sm font-medium text-gray-900">✅ Paquete Recibido</p>
                            </div>
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" x-model="preferences.notify_package_received" class="sr-only peer">
                                <div class="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-purple-600 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                            </label>
                        </div>

                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                                <p class="text-sm font-medium text-gray-900">🎉 Paquete Entregado</p>
                            </div>
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" x-model="preferences.notify_package_delivered" class="sr-only peer">
                                <div class="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-purple-600 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                            </label>
                        </div>

                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                                <p class="text-sm font-medium text-gray-900">💰 Recordatorios de Pago</p>
                            </div>
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" x-model="preferences.notify_payment_due" class="sr-only peer">
                                <div class="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-purple-600 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                            </label>
                        </div>

                        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                                <p class="text-sm font-medium text-gray-900">🎁 Marketing</p>
                            </div>
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" x-model="preferences.marketing_enabled" class="sr-only peer">
                                <div class="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-purple-600 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="border-t border-gray-200 px-6 py-4 flex justify-end space-x-3">
                <button @click="closePreferencesModal()" 
                        class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
                    Cancelar
                </button>
                <button @click="savePreferences()" 
                        :disabled="preferencesSaving"
                        class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50">
                    <span x-show="!preferencesSaving">Guardar Cambios</span>
                    <span x-show="preferencesSaving">Guardando...</span>
                </button>
            </div>
        </div>
    </div>
</div>
```

### **3. Agregar JavaScript**

Agregar al final del script de Alpine.js (buscar `function customerManagement()`):

```javascript
// Agregar estas propiedades al return de customerManagement()
showPreferencesModal: false,
preferencesLoading: false,
preferencesSaving: false,
preferencesCustomerId: null,
preferencesCustomerName: '',
preferencesUrl: '',
preferencesToken: '',
urlCopied: false,
preferences: {
    sms_notifications_enabled: true,
    email_notifications_enabled: true,
    notify_package_received: true,
    notify_package_delivered: true,
    notify_package_announced: true,
    notify_payment_due: true,
    marketing_enabled: false
},

// Agregar estos métodos
async openPreferencesModal(customerId, customerName) {
    this.showPreferencesModal = true;
    this.preferencesCustomerId = customerId;
    this.preferencesCustomerName = customerName;
    this.preferencesLoading = true;
    this.urlCopied = false;
    
    try {
        // Crear o obtener preferencias
        const createResponse = await fetch(`/api/customer/preferences/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ customer_id: customerId })
        });
        
        if (!createResponse.ok) {
            throw new Error('Error al crear preferencias');
        }
        
        const createData = await createResponse.json();
        this.preferencesToken = createData.token;
        this.preferencesUrl = window.location.origin + createData.preferences_url;
        
        // Cargar preferencias actuales
        const getResponse = await fetch(`/api/customer/preferences?token=${createData.token}`);
        
        if (!getResponse.ok) {
            throw new Error('Error al cargar preferencias');
        }
        
        const getData = await getResponse.json();
        this.preferences = getData.preferences;
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar preferencias: ' + error.message);
        this.closePreferencesModal();
    } finally {
        this.preferencesLoading = false;
    }
},

closePreferencesModal() {
    this.showPreferencesModal = false;
    this.preferencesCustomerId = null;
    this.preferencesCustomerName = '';
    this.preferencesUrl = '';
    this.preferencesToken = '';
    this.urlCopied = false;
},

async savePreferences() {
    this.preferencesSaving = true;
    
    try {
        const response = await fetch(`/api/customer/preferences?token=${this.preferencesToken}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(this.preferences)
        });
        
        if (!response.ok) {
            throw new Error('Error al guardar preferencias');
        }
        
        alert('✅ Preferencias guardadas correctamente');
        this.closePreferencesModal();
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al guardar preferencias: ' + error.message);
    } finally {
        this.preferencesSaving = false;
    }
},

copyPreferencesUrl() {
    navigator.clipboard.writeText(this.preferencesUrl).then(() => {
        this.urlCopied = true;
        setTimeout(() => {
            this.urlCopied = false;
        }, 2000);
    }).catch(err => {
        console.error('Error al copiar:', err);
        alert('Error al copiar el link');
    });
}
```

### **4. Agregar Función Global**

Agregar fuera del componente Alpine.js:

```javascript
// Función global para abrir modal de preferencias
function openPreferencesModal(customerId, customerName) {
    // Obtener instancia de Alpine
    const alpineData = Alpine.$data(document.querySelector('[x-data="customerManagement()"]'));
    if (alpineData && alpineData.openPreferencesModal) {
        alpineData.openPreferencesModal(customerId, customerName);
    }
}
```

---

## 🎯 Resultado Final

### **Funcionalidades:**

1. ✅ **Botón "Preferencias"** en cada fila de cliente (color morado)
2. ✅ **Modal con preferencias** del cliente
3. ✅ **Link único** para que el cliente gestione sus preferencias
4. ✅ **Botón "Copiar"** para copiar el link fácilmente
5. ✅ **Toggles** para modificar preferencias desde el admin
6. ✅ **Guardar cambios** directamente desde el modal

### **Flujo de Uso:**

```
1. Admin va a /customers/manage
   ↓
2. Hace clic en botón "Preferencias" (morado) de un cliente
   ↓
3. Se abre modal con:
   - Link único del cliente (para copiar y enviar)
   - Preferencias actuales (toggles)
   ↓
4. Admin puede:
   - Copiar link para enviar al cliente
   - Modificar preferencias directamente
   - Guardar cambios
   ↓
5. Cliente recibe link y gestiona sus preferencias
```

---

## 📝 Ventajas de esta Implementación

1. **Centralizado**: Todo desde la vista de gestión de clientes
2. **Rápido**: Un clic para ver/modificar preferencias
3. **Flexible**: Admin puede modificar O enviar link al cliente
4. **Visual**: Botón morado distintivo
5. **Intuitivo**: Modal claro y fácil de usar

---

## 🚀 Alternativas Consideradas

### **Opción A: Botón en Acciones** (Implementada)
- ✅ Rápido acceso
- ✅ Visible en la tabla
- ⚠️ Agrega un botón más

### **Opción B: Menú Desplegable**
- ✅ Menos botones visibles
- ⚠️ Requiere más clics
- ⚠️ Menos descubrible

### **Opción C: Tab en Modal de Edición**
- ✅ Integrado con edición
- ⚠️ Mezcla funcionalidades
- ⚠️ Modal más complejo

**Recomendación:** Opción A (botón directo) es la mejor para acceso rápido.

---

**Fecha:** 2025-01-24  
**Versión:** PAQUETEX v3.1  
**Estado:** 📝 Listo para implementar
