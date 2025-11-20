#!/usr/bin/env python3
"""Script para optimizar la función confirmDeliverAction"""

# Leer el archivo
with open('src/templates/packages/packages.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar la función
old_function_start = "function confirmDeliverAction() {"
new_function = """async function confirmDeliverAction() {
    console.log('🔄 confirmDeliverAction called');
    
    // Validate required fields
    const paymentAmount = parseFloat(document.getElementById('paymentAmount').value);

    if (!paymentAmount || paymentAmount <= 0) {
        showErrorToast('Error', 'Debe ingresar un monto de pago válido', 3000);
        return;
    }

    // Validar que el monto sea razonable
    const calculatedAmount = parseFloat(document.getElementById('suggestedAmountText').textContent.replace('Valor calculado: $', ''));
    if (paymentAmount > calculatedAmount * 2) {
        if (!confirm(`El monto ingresado ($${paymentAmount.toFixed(2)}) es mayor al calculado ($${calculatedAmount.toFixed(2)}). ¿Continuar?`)) {
            return;
        }
    }

    // Deshabilitar botón inmediatamente
    const confirmButton = document.getElementById('confirmAction');
    if (confirmButton) {
        confirmButton.disabled = true;
        confirmButton.innerHTML = '<svg class="animate-spin h-5 w-5 mx-auto" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';
    }

    const cleanPackageId = currentPackageId.toString().replace('announcement_', '');
    const packageData = packagesByState.received.find(p => p.id.toString() === cleanPackageId) || currentPackage;
    const customerId = packageData?.customer_id || null;
    
    const deliverData = {
        payment_method: 'efectivo',
        payment_amount: paymentAmount,
        customer_id: customerId,
        operator_id: 1,
        customer_signature: null
    };

    console.log('📤 Entregando paquete:', cleanPackageId);
    
    try {
        const response = await fetch(`/api/packages/${cleanPackageId}/deliver`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(deliverData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al entregar');
        }
        
        const data = await response.json();
        console.log('✅ Entregado exitosamente');
        
        // Cerrar modal inmediatamente
        closeModal();
        
        // Mostrar toast de éxito
        const packageData = data.package || data;
        const hasEmail = packageData.customer && packageData.customer.email;
        const message = hasEmail ? 'Paquete entregado. Email disponible' : 'Paquete entregado correctamente';
        showSuccessToast('✅ Entregado', message, 3000);
        
        if (hasEmail) {
            window.deliveredPackageForEmail = packageData;
        }
        
        // Recargar inmediatamente SIN delay
        reloadPackages();
    } catch (error) {
        console.error('❌ Error:', error);
        showErrorToast('Error', error.message, 4000);
        
        // Rehabilitar botón en caso de error
        if (confirmButton) {
            confirmButton.disabled = false;
            confirmButton.innerHTML = 'Confirmar Entrega';
        }
    }
}"""

# Encontrar el inicio de la función
start_idx = content.find(old_function_start)
if start_idx == -1:
    print("❌ No se encontró la función confirmDeliverAction")
    exit(1)

# Encontrar el final de la función (siguiente función)
end_marker = "\nfunction confirmDeleteAction()"
end_idx = content.find(end_marker, start_idx)
if end_idx == -1:
    print("❌ No se encontró el final de la función")
    exit(1)

# Reemplazar
new_content = content[:start_idx] + new_function + content[end_idx:]

# Guardar
with open('src/templates/packages/packages.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Función confirmDeliverAction optimizada correctamente")
