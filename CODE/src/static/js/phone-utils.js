/**
 * PAQUETES EL CLUB v1.0 - Utilidades de Teléfono
 * Normalización y validación de números telefónicos
 * Formato: Internacional con Colombia (+57) por defecto
 * 
 * @version 1.0.0
 * @date 2025-11-14
 */

/**
 * Normaliza un número de teléfono a formato internacional
 * 
 * Comportamiento:
 * - Si empieza con +57 o +: mantiene el formato internacional
 * - Si NO tiene código de país: agrega +57 (Colombia por defecto)
 * - Elimina espacios, guiones, paréntesis
 * - Resultado: +[código][número] (ej: +573001234567)
 * 
 * @param {string} phone - Número de teléfono a normalizar
 * @returns {string} - Número normalizado en formato +[código][número]
 */
function normalizePhone(phone) {
    if (!phone) return '';
    
    // Convertir a string y limpiar
    let cleaned = String(phone).trim();
    
    // Eliminar espacios, guiones, paréntesis
    cleaned = cleaned.replace(/[\s\-()]/g, '');
    
    // Si ya tiene +, solo limpiar
    if (cleaned.startsWith('+')) {
        return cleaned;
    }
    
    // Si NO tiene +, agregar código de Colombia (+57)
    // Eliminar cualquier + que no esté al inicio
    cleaned = cleaned.replace(/\+/g, '');
    
    // Si empieza con 57 (posible código sin +), verificar longitud
    if (cleaned.startsWith('57') && cleaned.length >= 12) {
        // Probablemente ya tiene código de país sin +
        return '+' + cleaned;
    }
    
    // Agregar +57 por defecto (Colombia)
    return '+57' + cleaned;
}

/**
 * Valida si un número de teléfono es válido
 * 
 * Reglas:
 * - Debe tener entre 10 y 15 dígitos (sin contar el +)
 * - Números colombianos móviles: 3XXXXXXXXX (10 dígitos)
 * - Números colombianos fijos: 60XXXXXXXX (10 dígitos)
 * - Números internacionales: debe empezar con + y tener código válido
 * 
 * @param {string} phone - Número a validar
 * @returns {boolean} - true si es válido, false si no
 */
function validatePhone(phone) {
    if (!phone) return false;
    
    const normalized = normalizePhone(phone);
    
    // Debe empezar con +
    if (!normalized.startsWith('+')) return false;
    
    // Extraer solo dígitos (sin el +)
    const digits = normalized.substring(1);
    
    // Debe tener solo dígitos
    if (!/^\d+$/.test(digits)) return false;
    
    // Debe tener entre 10 y 15 dígitos
    if (digits.length < 10 || digits.length > 15) return false;
    
    // Validación específica para Colombia (+57)
    if (normalized.startsWith('+57')) {
        const colombianNumber = digits.substring(2); // Quitar "57"
        
        // Debe tener exactamente 10 dígitos después del +57
        if (colombianNumber.length !== 10) return false;
        
        // Móvil: debe empezar con 3
        // Fijo: debe empezar con 6
        const firstDigit = colombianNumber[0];
        if (firstDigit !== '3' && firstDigit !== '6') return false;
    }
    
    return true;
}

/**
 * Formatea un número de teléfono para visualización
 * Devuelve el formato normalizado sin espacios: +573001234567
 * 
 * @param {string} phone - Número a formatear
 * @returns {string} - Número formateado
 */
function formatPhoneDisplay(phone) {
    if (!phone) return '';
    return normalizePhone(phone);
}

/**
 * Formatea un número de teléfono para enlaces tel: y WhatsApp
 * Devuelve el número sin + para compatibilidad: 573001234567
 * 
 * @param {string} phone - Número a formatear
 * @returns {string} - Número sin + para enlaces
 */
function formatPhoneLink(phone) {
    if (!phone) return '';
    const normalized = normalizePhone(phone);
    // Quitar el + para enlaces
    return normalized.replace('+', '');
}

/**
 * Formatea automáticamente un input de teléfono mientras el usuario escribe
 * Aplica normalización y validación en tiempo real
 * 
 * @param {Event} event - Evento de input del campo de teléfono
 * @returns {string} - Valor normalizado
 */
function formatPhoneInput(event) {
    const input = event.target;
    const cursorPosition = input.selectionStart;
    const oldValue = input.value;
    const oldLength = oldValue.length;
    
    // Permitir escribir mientras se escribe
    let value = input.value;
    
    // Solo permitir +, números y temporalmente espacios/guiones para UX
    value = value.replace(/[^\d+\s\-()]/g, '');
    
    // Actualizar el valor limpio
    input.value = value;
    
    // Restaurar posición del cursor ajustada
    const newLength = value.length;
    const newPosition = cursorPosition + (newLength - oldLength);
    input.setSelectionRange(newPosition, newPosition);
    
    return value;
}

/**
 * Valida y normaliza un campo de teléfono al perder el foco (onblur)
 * Convierte el valor a formato normalizado final
 * 
 * @param {Event} event - Evento blur del campo
 * @returns {boolean} - true si es válido, false si no
 */
function normalizePhoneOnBlur(event) {
    const input = event.target;
    const value = input.value.trim();
    
    if (!value) return true; // Permitir vacío si no es required
    
    // Normalizar
    const normalized = normalizePhone(value);
    input.value = normalized;
    
    // Validar
    const isValid = validatePhone(normalized);
    
    // Aplicar clases de validación
    if (isValid) {
        input.classList.remove('border-red-500');
        input.classList.add('border-green-500');
    } else {
        input.classList.remove('border-green-500');
        input.classList.add('border-red-500');
    }
    
    return isValid;
}

/**
 * Inicializa la validación automática de campos de teléfono
 * Busca todos los inputs type="tel" y agrega los event listeners
 */
function initPhoneValidation() {
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    
    phoneInputs.forEach(input => {
        // Formatear mientras escribe
        input.addEventListener('input', formatPhoneInput);
        
        // Normalizar al perder foco
        input.addEventListener('blur', normalizePhoneOnBlur);
        
        // Agregar placeholder por defecto si no tiene
        if (!input.placeholder) {
            input.placeholder = '+573001234567 o 3001234567';
        }
        
        // Agregar atributos de validación
        input.setAttribute('minlength', '10');
        input.setAttribute('maxlength', '20');
    });
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPhoneValidation);
} else {
    initPhoneValidation();
}

// Exportar funciones para uso global
window.normalizePhone = normalizePhone;
window.validatePhone = validatePhone;
window.formatPhoneDisplay = formatPhoneDisplay;
window.formatPhoneLink = formatPhoneLink;
window.formatPhoneInput = formatPhoneInput;
window.normalizePhoneOnBlur = normalizePhoneOnBlur;
window.initPhoneValidation = initPhoneValidation;

