# 🎨 CAMBIOS PARA APLICAR LOOK & FEEL DEL TAB CUFE AL TAB FACTURAS

## ✅ CAMBIOS YA APLICADOS

1. **Migración a layout compartido** - El archivo ahora extiende `invoices_v2/layout.html`
2. **Bloque search_bar** - Implementado con el mismo estilo que CUFE
3. **Botón de carga** - Cambiado icono de "+" a icono de "upload" (nube)

---

## 🔧 CAMBIOS PENDIENTES POR APLICAR

### 1. TABLA - HEADER (Línea ~75)

**CAMBIAR:**
```html
<th scope="col" class="px-6 py-3 text-left">
    <input type="checkbox" id="select-all"...>
</th>
<th scope="col" class="px-6 py-3 text-left text-xs...">CUFE</th>
```

**POR:**
```html
<th scope="col" class="px-6 py-3 text-left w-12">
    <input type="checkbox" id="select-all"...>
</th>
<th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">CUFE</th>
```

**Y CAMBIAR:**
```html
<th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-40 md:w-48">
    <button id="delete-selected-btn"...>
```

**POR:**
```html
<th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-40 md:w-48">
    <span id="actions-header">Acciones</span>
    <button id="delete-selected-btn" 
            onclick="deleteSelectedInvoices()" 
            class="hidden px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 transition-colors ml-2"
            title="Eliminar seleccionadas">
        🗑️ Eliminar (<span id="selected-count">0</span>)
    </button>
```

---

### 2. FUNCIÓN renderInvoiceRow() - COMPLETA REESCRITURA

**REEMPLAZAR LA FUNCIÓN COMPLETA (línea ~600 aprox) POR:**

```javascript
function renderInvoiceRow(invoice) {
    const isTempCufe = invoice.cufe.startsWith('TEMP_');
    
    // Estado con círculo de color (estilo CUFE)
    const estadoBadge = {
        'pendiente_dian': '<span class="inline-block w-3 h-3 rounded-full bg-yellow-500" title="Pendiente DIAN"></span>',
        'completo': '<span class="inline-block w-3 h-3 rounded-full bg-green-500" title="Completo"></span>',
        'error': '<span class="inline-block w-3 h-3 rounded-full bg-red-500" title="Error"></span>',
        'sin_dian': '<span class="inline-block w-3 h-3 rounded-full bg-gray-500" title="Sin DIAN"></span>',
        'sin_cufe': '<span class="inline-block w-3 h-3 rounded-full bg-orange-500" title="Sin CUFE"></span>',
    };
    
    // Proveedor en MAYÚSCULAS (estilo CUFE)
    const proveedorRaw = invoice.proveedor_nombre || '-';
    const proveedor = proveedorRaw !== '-' 
        ? `<span class="uppercase whitespace-nowrap overflow-hidden text-ellipsis block max-w-xs" title="${proveedorRaw}">${proveedorRaw}</span>`
        : '<span class="text-gray-400 italic text-xs">-</span>';
    
    // Número en una sola línea
    const numero = invoice.numero_factura 
        ? `<span class="whitespace-nowrap">${invoice.numero_factura}</span>` 
        : '<span class="text-gray-400 italic text-xs">-</span>';
    
    const fecha = invoice.fecha_emision ? formatDate(invoice.fecha_emision) : '<span class="text-gray-400 italic text-xs">-</span>';
    const total = invoice.total_factura ? formatCurrency(invoice.total_factura) : '<span class="text-gray-400 italic text-xs">-</span>';
    
    // Determinar si tiene archivos
    const hasArchivoProveedor = invoice.archivo_proveedor_s3_key || invoice.archivo_proveedor_url;
    
    return `
        <tr class="hover:bg-gray-50 transition-colors ${isTempCufe ? 'bg-orange-50' : ''}">
            <td class="px-6 py-4">
                <input type="checkbox" 
                       class="invoice-checkbox rounded border-gray-300 text-papyrus-blue focus:ring-papyrus-blue cursor-pointer" 
                       value="${invoice.cufe}"
                       onchange="updateSelectedCount()">
            </td>
            <td class="px-3 py-4">
                <button onclick="copyCufe('${invoice.cufe}')" 
                        class="font-mono text-xs text-gray-700 hover:text-papyrus-blue transition-colors flex items-center gap-1.5 group ${isTempCufe ? 'text-orange-600 font-bold' : ''}" 
                        title="${invoice.cufe}">
                    <span class="tracking-tight">${isTempCufe ? 'TEMPORAL' : invoice.cufe.substring(0, 12) + '...'}</span>
                    <svg class="w-3.5 h-3.5 text-gray-400 group-hover:text-papyrus-blue opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    </svg>
                </button>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">${proveedor}</td>
            <td class="px-6 py-4 text-sm text-gray-900 hidden md:table-cell">${numero}</td>
            <td class="px-6 py-4 text-sm text-gray-500 hidden lg:table-cell">${fecha}</td>
            <td class="px-6 py-4 text-sm font-medium text-gray-900">${total}</td>
            <td class="px-6 py-4 text-sm text-center">${estadoBadge[invoice.estado] || invoice.estado}</td>
            <td class="px-6 py-4 text-sm text-right">
                <div class="flex items-center justify-end gap-3">
                    ${isTempCufe ? `
                        <button onclick="showAssociateCufeModal('${invoice.cufe}')" 
                                class="text-orange-600 hover:text-orange-800 transition-colors" 
                                title="Asociar CUFE real">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                            </svg>
                        </button>
                    ` : ''}
                    ${!isTempCufe ? `
                        <a href="https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey=${invoice.cufe}" 
                           target="_blank" 
                           class="text-purple-600 hover:text-purple-800 transition-colors" 
                           title="Ver en portal DIAN">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                            </svg>
                        </a>
                    ` : ''}
                    ${hasArchivoProveedor ? `
                        <button onclick="downloadInvoice('${invoice.cufe}')" 
                                class="text-green-600 hover:text-green-800 transition-colors" 
                                title="Descargar PDF proveedor">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                            </svg>
                        </button>
                    ` : ''}
                    <button onclick="deleteInvoice('${invoice.cufe}')" 
                            class="text-red-600 hover:text-red-800 transition-colors" 
                            title="Eliminar factura">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                </div>
            </td>
        </tr>
    `;
}
```

---

### 3. MODAL DE CARGA - REEMPLAZAR COMPLETO

**BUSCAR:** `<!-- Modal de carga múltiple -->`

**REEMPLAZAR TODO EL MODAL POR:**

```html
<!-- Modal de carga múltiple con Drag & Drop -->
<div id="upload-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <!-- Header con gradiente -->
        <div class="bg-gradient-to-r from-papyrus-blue to-blue-600 px-6 py-4 rounded-t-2xl">
            <h3 class="text-xl font-bold text-white">Cargar Facturas de Proveedor</h3>
        </div>
        
        <form id="upload-form" enctype="multipart/form-data" class="p-6">
            <!-- Zona de Drag & Drop -->
            <div id="drop-zone" class="relative border-3 border-dashed border-gray-300 rounded-xl p-8 text-center transition-all duration-200 hover:border-papyrus-blue hover:bg-blue-50 cursor-pointer group">
                <input type="file" id="pdf-files" accept=".pdf" multiple required class="hidden">
                
                <!-- Icono y texto -->
                <div class="pointer-events-none">
                    <svg class="w-16 h-16 mx-auto text-gray-400 group-hover:text-papyrus-blue transition-colors mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                    </svg>
                    <p class="text-lg font-medium text-gray-700 mb-2">Arrastra archivos PDF aquí</p>
                    <p class="text-sm text-gray-500 mb-4">o haz clic para seleccionar</p>
                    <div class="inline-flex items-center px-4 py-2 bg-papyrus-blue text-white rounded-lg text-sm font-medium group-hover:bg-blue-700 transition-colors">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                        </svg>
                        Seleccionar archivos
                    </div>
                </div>
                
                <!-- Overlay cuando se arrastra -->
                <div id="drop-overlay" class="hidden absolute inset-0 bg-papyrus-blue bg-opacity-10 border-3 border-papyrus-blue rounded-xl flex items-center justify-center">
                    <div class="text-center">
                        <svg class="w-20 h-20 mx-auto text-papyrus-blue mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
                        </svg>
                        <p class="text-xl font-bold text-papyrus-blue">Suelta los archivos aquí</p>
                    </div>
                </div>
            </div>
            
            <!-- Lista de archivos seleccionados -->
            <div id="files-list" class="mt-4 hidden">
                <div class="flex items-center justify-between mb-3">
                    <p class="text-sm font-medium text-gray-700">
                        <span id="files-count-text">0</span> archivo(s) seleccionado(s)
                    </p>
                    <button type="button" onclick="clearSelectedFiles()" class="text-sm text-red-600 hover:text-red-800 font-medium">
                        Limpiar todo
                    </button>
                </div>
                <div id="files-container" class="space-y-2 max-h-48 overflow-y-auto border rounded-lg p-3 bg-gray-50">
                    <!-- Archivos se mostrarán aquí -->
                </div>
            </div>
            
            <!-- Progreso de carga -->
            <div id="upload-progress" class="mt-4 hidden">
                <div class="flex justify-between text-sm font-medium text-gray-700 mb-2">
                    <span>Procesando...</span>
                    <span id="progress-text">0 / 0</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div id="progress-bar" class="bg-gradient-to-r from-papyrus-blue to-blue-500 h-3 rounded-full transition-all duration-300 shadow-sm" style="width: 0%"></div>
                </div>
                <div id="upload-results" class="mt-3 space-y-1 max-h-40 overflow-y-auto">
                    <!-- Resultados se mostrarán aquí -->
                </div>
            </div>
            
            <!-- Botones -->
            <div class="flex justify-end gap-3 mt-6 pt-4 border-t">
                <button type="button" id="cancel-btn" onclick="closeUploadModal()"
                        class="px-5 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium text-gray-700">
                    Cancelar
                </button>
                <button type="submit" id="upload-btn" class="px-5 py-2.5 bg-papyrus-blue hover:bg-blue-700 text-white rounded-lg transition-all font-medium shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed">
                    <svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    Procesar <span id="file-count"></span>
                </button>
            </div>
        </form>
    </div>
</div>
```

---

### 4. JAVASCRIPT - AGREGAR FUNCIONES DRAG & DROP

**AGREGAR DESPUÉS DE `document.addEventListener('DOMContentLoaded', ...)`:**

```javascript
// Configurar Drag & Drop
function setupDragAndDrop() {
    const dropZone = document.getElementById('drop-zone');
    const dropOverlay = document.getElementById('drop-overlay');
    const fileInput = document.getElementById('pdf-files');
    
    // Click en la zona para abrir selector
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Prevenir comportamiento por defecto
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Highlight cuando se arrastra sobre la zona
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropOverlay.classList.remove('hidden');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropOverlay.classList.add('hidden');
        }, false);
    });
    
    // Manejar drop
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        // Asignar archivos al input
        fileInput.files = files;
        
        // Disparar evento change
        const event = new Event('change', { bubbles: true });
        fileInput.dispatchEvent(event);
    }, false);
}

function openUploadModal() {
    document.getElementById('upload-modal').classList.remove('hidden');
    setupDragAndDrop();
}

function clearSelectedFiles() {
    const fileInput = document.getElementById('pdf-files');
    fileInput.value = '';
    displaySelectedFiles([]);
}

function displaySelectedFiles(files) {
    const filesList = document.getElementById('files-list');
    const filesContainer = document.getElementById('files-container');
    const fileCount = document.getElementById('file-count');
    const filesCountText = document.getElementById('files-count-text');
    
    if (files.length > 0) {
        filesList.classList.remove('hidden');
        filesContainer.innerHTML = '';
        
        Array.from(files).forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 hover:border-papyrus-blue transition-colors group';
            fileItem.innerHTML = `
                <div class="flex items-center flex-1 min-w-0">
                    <div class="flex-shrink-0 w-10 h-10 bg-red-50 rounded-lg flex items-center justify-center mr-3">
                        <svg class="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"></path>
                        </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-900 truncate">${file.name}</p>
                        <p class="text-xs text-gray-500">${(file.size / 1024).toFixed(1)} KB</p>
                    </div>
                </div>
                <button type="button" onclick="removeFile(${index})" class="ml-3 text-gray-400 hover:text-red-600 transition-colors opacity-0 group-hover:opacity-100">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            `;
            filesContainer.appendChild(fileItem);
        });
        
        fileCount.textContent = `(${files.length})`;
        filesCountText.textContent = files.length;
        
        // Habilitar botón de procesar
        document.getElementById('upload-btn').disabled = false;
    } else {
        filesList.classList.add('hidden');
        fileCount.textContent = '';
        filesCountText.textContent = '0';
        document.getElementById('upload-btn').disabled = true;
    }
}

function removeFile(index) {
    const fileInput = document.getElementById('pdf-files');
    const dt = new DataTransfer();
    const files = Array.from(fileInput.files);
    
    files.forEach((file, i) => {
        if (i !== index) {
            dt.items.add(file);
        }
    });
    
    fileInput.files = dt.files;
    displaySelectedFiles(fileInput.files);
}
```

---

### 5. ACTUALIZAR EVENT LISTENER DE ARCHIVOS

**BUSCAR:**
```javascript
document.getElementById('pdf-files').addEventListener('change', (e) => {
    const files = e.target.files;
    const filesList = document.getElementById('files-list');
    ...
});
```

**REEMPLAZAR POR:**
```javascript
document.getElementById('pdf-files').addEventListener('change', (e) => {
    const files = e.target.files;
    displaySelectedFiles(files);
});
```

---

### 6. AGREGAR ESTILOS CSS AL FINAL

**AGREGAR ANTES DE `{% endblock %}`:**

```html
<style>
    /* Estilos personalizados para el drag and drop */
    #drop-zone {
        border-width: 3px;
    }
    
    #drop-zone:hover {
        border-color: #2563eb;
        background-color: #eff6ff;
    }
    
    .border-3 {
        border-width: 3px;
    }
</style>
```

---

### 7. CAMBIAR FUNCIÓN closeUploadModal()

**BUSCAR:**
```javascript
function closeUploadModal() {
    document.getElementById('upload-modal').classList.add('hidden');
    document.getElementById('pdf-files').value = '';
    document.getElementById('files-list').classList.add('hidden');
    ...
}
```

**REEMPLAZAR POR:**
```javascript
function closeUploadModal() {
    document.getElementById('upload-modal').classList.add('hidden');
    document.getElementById('pdf-files').value = '';
    document.getElementById('files-list').classList.add('hidden');
    document.getElementById('upload-progress').classList.add('hidden');
    document.getElementById('upload-btn').disabled = false;
    document.getElementById('cancel-btn').textContent = 'Cancelar';
    document.getElementById('file-count').textContent = '';
    document.getElementById('files-count-text').textContent = '0';
    document.getElementById('files-container').innerHTML = '';
}
```

---

## 🎯 RESULTADO ESPERADO

Después de aplicar todos estos cambios, el TAB FACTURAS tendrá:

✅ Mismo layout que TAB CUFE (usando `layout.html`)
✅ Modal premium con Drag & Drop
✅ CUFE con hover effect elegante
✅ Estados con círculos de color
✅ Proveedor en MAYÚSCULAS
✅ Enlace a portal DIAN
✅ Gradientes en headers
✅ Transiciones suaves
✅ Look & feel consistente con TAB CUFE

---

## 📝 NOTAS

- Los cambios son compatibles con la funcionalidad existente
- No se pierde ninguna característica actual
- Solo se mejora el diseño visual
- El código JavaScript sigue siendo funcional
