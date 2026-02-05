# Plan: Delete Feature for CUFE View

## Overview
Add a delete button to each row in the CUFE tab that allows users to delete invoices. The deletion will:
1. Remove the database record (invoice + products via cascade)
2. Delete both S3 files (supplier PDF and DIAN PDF)
3. Show confirmation dialog before deletion
4. Provide visual feedback

## Backend Status
✅ **Already implemented!** The backend endpoint exists:
- **Endpoint**: `DELETE /api/v2/invoices/facturas/{cufe}`
- **Service method**: `InvoiceV2Service.delete_invoice(cufe)`
- **S3 cleanup**: Automatically deletes both files:
  - `archivo_proveedor_s3_key` (supplier invoice PDF)
  - `archivo_dian_s3_key` (DIAN document PDF)
- **Database**: Cascade delete removes products automatically

## Frontend Changes Needed

### 1. Add Delete Button to Table Row
**File**: `CODE/src/templates/invoices_v2/cufe.html`

Add a delete button (trash icon) to the actions column in `renderCufeRow()` function:

```javascript
// In the actions column, add:
<button onclick="confirmDeleteInvoice('${invoice.cufe}', '${proveedor}')" 
        class="text-red-600 hover:text-red-800 transition-colors" 
        title="Eliminar factura">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
    </svg>
</button>
```

### 2. Add Confirmation Modal
Add a confirmation modal to prevent accidental deletions:

```html
<!-- Delete Confirmation Modal -->
<div id="delete-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex items-center gap-3 mb-4">
            <div class="bg-red-100 p-3 rounded-full">
                <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
            </div>
            <div>
                <h3 class="text-lg font-bold text-gray-900">Confirmar Eliminación</h3>
                <p class="text-sm text-gray-500">Esta acción no se puede deshacer</p>
            </div>
        </div>
        
        <div class="mb-6">
            <p class="text-sm text-gray-700 mb-2">¿Estás seguro de eliminar esta factura?</p>
            <div class="bg-gray-50 p-3 rounded-lg border border-gray-200">
                <p class="text-xs text-gray-600 mb-1">CUFE:</p>
                <p id="delete-cufe-display" class="text-sm font-mono text-gray-900 break-all"></p>
                <p class="text-xs text-gray-600 mt-2 mb-1">Proveedor:</p>
                <p id="delete-proveedor-display" class="text-sm text-gray-900"></p>
            </div>
        </div>
        
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
            <div class="flex gap-2">
                <svg class="w-5 h-5 text-yellow-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
                <div class="text-xs text-yellow-800">
                    <p class="font-medium mb-1">Se eliminarán:</p>
                    <ul class="list-disc list-inside space-y-1">
                        <li>Registro de la factura en la base de datos</li>
                        <li>Todos los productos asociados</li>
                        <li>Archivo PDF del proveedor (S3)</li>
                        <li>Archivo PDF DIAN (S3)</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="flex justify-end gap-3">
            <button onclick="closeDeleteModal()" 
                    class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                Cancelar
            </button>
            <button id="confirm-delete-btn" 
                    onclick="deleteInvoice()" 
                    class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
                Eliminar Factura
            </button>
        </div>
    </div>
</div>
```

### 3. Add JavaScript Functions

```javascript
// Variable global para almacenar el CUFE a eliminar
let cufeToDelete = null;

function confirmDeleteInvoice(cufe, proveedor) {
    cufeToDelete = cufe;
    document.getElementById('delete-cufe-display').textContent = cufe;
    document.getElementById('delete-proveedor-display').textContent = proveedor || 'No especificado';
    document.getElementById('delete-modal').classList.remove('hidden');
}

function closeDeleteModal() {
    cufeToDelete = null;
    document.getElementById('delete-modal').classList.add('hidden');
}

async function deleteInvoice() {
    if (!cufeToDelete) return;
    
    const confirmBtn = document.getElementById('confirm-delete-btn');
    const originalText = confirmBtn.innerHTML;
    
    // Deshabilitar botón y mostrar loading
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = `
        <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Eliminando...
    `;
    
    try {
        const response = await fetch(`/api/v2/invoices/facturas/${cufeToDelete}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            showToast('Factura eliminada correctamente (BD + S3)', 'success');
            closeDeleteModal();
            loadCufeRecords(); // Recargar la tabla
        } else {
            const error = await response.json();
            showToast(error.detail || 'Error al eliminar la factura', 'error');
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = originalText;
        }
    } catch (error) {
        console.error('Error eliminando factura:', error);
        showToast('Error de conexión al eliminar la factura', 'error');
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = originalText;
    }
}

// Cerrar modal con ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !document.getElementById('delete-modal').classList.contains('hidden')) {
        closeDeleteModal();
    }
});
```

## Visual Design

### Delete Button Position
The delete button will be added to the **actions column** (rightmost column) alongside:
- Upload DIAN button (orange, only if not validated)
- View in DIAN portal button (purple, only if not validated)
- Download PDF DIAN button (red, only if has DIAN file)
- **NEW: Delete button (red trash icon, always visible)**

### Button Style
- **Icon**: Trash can icon
- **Color**: Red (`text-red-600 hover:text-red-800`)
- **Position**: Last button in the actions column
- **Tooltip**: "Eliminar factura"

### Confirmation Modal
- **Style**: Warning modal with red accent
- **Content**: 
  - Shows CUFE and provider name
  - Lists what will be deleted (DB record, products, S3 files)
  - Warning message about irreversibility
- **Actions**: Cancel (gray) and Delete (red)

## Security Considerations

1. ✅ **Backend validation**: Endpoint checks if invoice exists
2. ✅ **S3 cleanup**: Service handles S3 deletion with error handling
3. ✅ **Cascade delete**: Products are automatically deleted via DB cascade
4. ✅ **Confirmation**: User must confirm before deletion
5. ✅ **Visual feedback**: Toast notifications for success/error

## Testing Checklist

After implementation, test:
- [ ] Delete button appears in all rows
- [ ] Confirmation modal opens with correct CUFE and provider
- [ ] Cancel button closes modal without deleting
- [ ] Delete button removes invoice from database
- [ ] S3 files are deleted (check S3 bucket)
- [ ] Products are deleted (cascade)
- [ ] Table refreshes after deletion
- [ ] Toast notifications appear
- [ ] Error handling works (try deleting non-existent CUFE)

## Files to Modify

1. **CODE/src/templates/invoices_v2/cufe.html**
   - Add delete button to `renderCufeRow()` function
   - Add delete confirmation modal HTML
   - Add JavaScript functions for delete functionality

## Estimated Changes

- **Lines to add**: ~150 lines (modal HTML + JavaScript)
- **Lines to modify**: ~5 lines (add button to actions column)
- **Backend changes**: None (already implemented)

## Approval Required

Please review this plan and let me know if you approve. Once approved, I'll implement:
1. Delete button in the actions column
2. Confirmation modal with warning
3. JavaScript functions for delete flow
4. Visual feedback (loading states, toasts)
