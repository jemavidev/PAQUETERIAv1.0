/**
 * PAQUETES EL CLUB v4.0 - Sistema de Validación de Formularios
 * Versión: 1.0.0
 * Fecha: 2025-01-24
 * Autor: Equipo de Desarrollo
 */

class FormValidator {
    constructor(formId, options = {}) {
        this.form = document.getElementById(formId);
        this.options = {
            showErrors: true,
            showSuccess: true,
            validateOnSubmit: true,
            validateOnChange: false,
            ...options
        };
        this.errors = {};
        
        if (this.form) {
            this.init();
        }
    }
    
    init() {
        if (this.options.validateOnSubmit) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
        
        if (this.options.validateOnChange) {
            const inputs = this.form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
            });
        }
    }
    
    handleSubmit(e) {
        e.preventDefault();
        
        // Limpiar errores anteriores
        this.clearErrors();
        
        // Validar todos los campos
        const isValid = this.validateForm();
        
        if (isValid) {
            if (this.options.showSuccess) {
                showSuccessMessage('Formulario enviado correctamente');
            }
            
            // Ejecutar callback de éxito si existe
            if (this.options.onSuccess) {
                this.options.onSuccess(this.getFormData());
            }
        } else {
            if (this.options.showErrors) {
                this.showValidationErrors();
            }
            
            // Ejecutar callback de error si existe
            if (this.options.onError) {
                this.options.onError(this.errors);
            }
        }
        
        return isValid;
    }
    
    validateForm() {
        this.errors = {};
        const inputs = this.form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            this.validateField(input);
        });
        
        return Object.keys(this.errors).length === 0;
    }
    
    validateField(input) {
        const fieldName = input.name || input.id;
        const value = input.value.trim();
        const rules = this.getFieldRules(input);
        
        // Limpiar errores anteriores del campo
        delete this.errors[fieldName];
        
        // Aplicar reglas de validación
        for (const rule of rules) {
            const error = this.applyRule(value, rule, input);
            if (error) {
                if (!this.errors[fieldName]) {
                    this.errors[fieldName] = [];
                }
                this.errors[fieldName].push(error);
            }
        }
        
        return this.errors[fieldName] || [];
    }
    
    getFieldRules(input) {
        const rules = [];
        
        // Reglas basadas en atributos HTML
        if (input.hasAttribute('required')) {
            rules.push({ type: 'required', message: 'Este campo es requerido' });
        }
        
        if (input.type === 'email') {
            rules.push({ type: 'email', message: 'El email no es válido' });
        }
        
        if (input.type === 'tel') {
            rules.push({ type: 'phone', message: 'El teléfono no es válido' });
        }
        
        if (input.hasAttribute('minlength')) {
            const minLength = parseInt(input.getAttribute('minlength'));
            rules.push({ 
                type: 'minlength', 
                value: minLength, 
                message: `Debe tener al menos ${minLength} caracteres` 
            });
        }
        
        if (input.hasAttribute('maxlength')) {
            const maxLength = parseInt(input.getAttribute('maxlength'));
            rules.push({ 
                type: 'maxlength', 
                value: maxLength, 
                message: `No puede tener más de ${maxLength} caracteres` 
            });
        }
        
        if (input.hasAttribute('pattern')) {
            const pattern = input.getAttribute('pattern');
            rules.push({ 
                type: 'pattern', 
                value: pattern, 
                message: 'El formato no es válido' 
            });
        }
        
        // Reglas personalizadas desde data attributes
        if (input.dataset.validationRules) {
            try {
                const customRules = JSON.parse(input.dataset.validationRules);
                rules.push(...customRules);
            } catch (e) {
                console.warn('Error parsing validation rules:', e);
            }
        }
        
        return rules;
    }
    
    applyRule(value, rule, input) {
        switch (rule.type) {
            case 'required':
                return value === '' ? rule.message : null;
                
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return value && !emailRegex.test(value) ? rule.message : null;
                
            case 'phone':
                const phoneRegex = /^[\+]?[0-9\s\-\(\)]{7,}$/;
                return value && !phoneRegex.test(value) ? rule.message : null;
                
            case 'minlength':
                return value && value.length < rule.value ? rule.message : null;
                
            case 'maxlength':
                return value && value.length > rule.value ? rule.message : null;
                
            case 'pattern':
                const regex = new RegExp(rule.value);
                return value && !regex.test(value) ? rule.message : null;
                
            case 'custom':
                if (rule.validator && typeof rule.validator === 'function') {
                    return rule.validator(value, input) ? rule.message : null;
                }
                return null;
                
            default:
                return null;
        }
    }
    
    showValidationErrors() {
        if (Object.keys(this.errors).length > 0) {
            showValidationErrors(this.errors);
        }
    }
    
    clearErrors() {
        this.errors = {};
    }
    
    getFormData() {
        const formData = new FormData(this.form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }
    
    setFieldError(fieldName, message) {
        if (!this.errors[fieldName]) {
            this.errors[fieldName] = [];
        }
        this.errors[fieldName].push(message);
    }
    
    clearFieldError(fieldName) {
        delete this.errors[fieldName];
    }
}

// Funciones de conveniencia para validación rápida
function validateForm(formId, options = {}) {
    const validator = new FormValidator(formId, options);
    return validator.validateForm();
}

function validateField(fieldId, rules = []) {
    const field = document.getElementById(fieldId);
    if (!field) return [];
    
    const validator = new FormValidator(field.closest('form').id);
    validator.errors = {};
    
    // Aplicar reglas personalizadas
    rules.forEach(rule => {
        const error = validator.applyRule(field.value.trim(), rule, field);
        if (error) {
            if (!validator.errors[fieldId]) {
                validator.errors[fieldId] = [];
            }
            validator.errors[fieldId].push(error);
        }
    });
    
    return validator.errors[fieldId] || [];
}

// Validadores personalizados comunes
const CustomValidators = {
    // Validar que dos campos coincidan (ej: contraseña y confirmación)
    matchFields: (field1, field2, message = 'Los campos no coinciden') => {
        const value1 = document.getElementById(field1)?.value;
        const value2 = document.getElementById(field2)?.value;
        return value1 !== value2 ? message : null;
    },
    
    // Validar formato de número de guía
    trackingNumber: (value) => {
        const trackingRegex = /^[A-Z0-9]{6,20}$/;
        return value && !trackingRegex.test(value) ? 'El número de guía no es válido' : null;
    },
    
    // Validar formato de teléfono colombiano
    colombianPhone: (value) => {
        const phoneRegex = /^(\+57|57)?[0-9]{10}$/;
        return value && !phoneRegex.test(value.replace(/\s/g, '')) ? 'El teléfono colombiano no es válido' : null;
    },
    
    // Validar formato de cédula colombiana
    colombianId: (value) => {
        const idRegex = /^[0-9]{6,12}$/;
        return value && !idRegex.test(value) ? 'La cédula no es válida' : null;
    }
};

// Auto-inicialización de formularios con data-validation="true"
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-validation="true"]');
    forms.forEach(form => {
        new FormValidator(form.id, {
            validateOnSubmit: true,
            validateOnChange: form.dataset.validateOnChange === 'true',
            showErrors: true,
            showSuccess: true
        });
    });
});

// Exportar para uso global
window.FormValidator = FormValidator;
window.validateForm = validateForm;
window.validateField = validateField;
window.CustomValidators = CustomValidators;
