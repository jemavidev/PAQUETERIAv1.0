// ========================================
// OVERRIDE COMPLETO DE VALIDACIÓN NATIVA - ARCHIVO JS
// PAQUETES EL CLUB v4.0
// ========================================

(function() {
    'use strict';
    
    // DEBUG MODE - Cambiar a false para producción
    const DEBUG_VALIDATION = false;
    
    if (DEBUG_VALIDATION) console.log('🚨 Inicializando OVERRIDE completo de validación nativa...');
    
    // Referencias a los elementos del DOM
    let container, title, message, fieldName, closeBtn;
    
    // Función para inicializar referencias del DOM
    function inicializarReferencias() {
        container = document.getElementById('validation-override-container');
        title = document.getElementById('validation-override-title');
        message = document.getElementById('validation-override-message');
        fieldName = document.getElementById('field-name-override');
        closeBtn = document.getElementById('validation-override-close-btn');
        
        if (!container) {
            if (DEBUG_VALIDATION) console.error('❌ No se encontró el contenedor de validación');
            return false;
        }
        
        if (DEBUG_VALIDATION) console.log('✅ Referencias del DOM inicializadas correctamente');
        return true;
    }
    
    // Función para mostrar error de validación
    function mostrarErrorValidacion(campo, mensaje, tipoValidacion) {
        if (DEBUG_VALIDATION) console.log('📝 Mostrando error de validación:', { campo, mensaje, tipoValidacion });
        
        if (!inicializarReferencias()) {
            console.error('❌ No se pueden mostrar errores sin las referencias del DOM');
            return;
        }
        
        // Obtener el nombre del campo
        const nombreCampo = obtenerNombreCampo(campo);
        
        // Actualizar contenido
        title.textContent = 'Error de Validación';
        message.textContent = mensaje;
        fieldName.textContent = nombreCampo;
        
        // Mostrar el contenedor con animación
        container.style.display = 'block';
        container.style.opacity = '0';
        container.style.transform = 'scale(0.95)';
        
        // Animar la aparición
        setTimeout(() => {
            container.style.transition = 'all 0.3s ease-out';
            container.style.opacity = '1';
            container.style.transform = 'scale(1)';
        }, 10);
        
        // Auto-cerrar después de 8 segundos
        setTimeout(() => {
            cerrarError();
        }, 8000);
    }
    
    // Función para obtener el nombre del campo
    function obtenerNombreCampo(campo) {
        // Buscar label asociado
        const label = document.querySelector(`label[for="${campo.id}"]`);
        if (label) {
            return label.textContent.replace('*', '').trim();
        }
        
        // Buscar placeholder
        if (campo.placeholder) {
            return campo.placeholder;
        }
        
        // Usar el nombre del campo
        return campo.name || campo.id || 'Campo';
    }
    
    // Función para cerrar error
    function cerrarError() {
        if (!container) return;
        
        container.style.transition = 'all 0.2s ease-in';
        container.style.opacity = '0';
        container.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
            container.style.display = 'none';
        }, 200);
    }
    
    // Función para obtener mensaje de validación personalizado
    function obtenerMensajeValidacion(campo) {
        const validacion = campo.validity;
        
        if (validacion.valueMissing) {
            return 'Este campo es obligatorio. Por favor, complételo.';
        }
        
        if (validacion.tooShort) {
            const minLength = campo.getAttribute('minlength') || campo.minLength;
            return `El campo debe tener al menos ${minLength} caracteres.`;
        }
        
        if (validacion.tooLong) {
            const maxLength = campo.getAttribute('maxlength') || campo.maxLength;
            return `El campo no puede tener más de ${maxLength} caracteres.`;
        }
        
        if (validacion.typeMismatch) {
            if (campo.type === 'email') {
                return 'Por favor, ingrese un email válido.';
            }
            if (campo.type === 'url') {
                return 'Por favor, ingrese una URL válida.';
            }
            return 'El formato del campo no es válido.';
        }
        
        if (validacion.patternMismatch) {
            return 'El formato del campo no coincide con el patrón requerido.';
        }
        
        if (validacion.rangeUnderflow) {
            const min = campo.getAttribute('min') || campo.min;
            return `El valor debe ser mayor o igual a ${min}.`;
        }
        
        if (validacion.rangeOverflow) {
            const max = campo.getAttribute('max') || campo.max;
            return `El valor debe ser menor o igual a ${max}.`;
        }
        
        if (validacion.stepMismatch) {
            return 'El valor no es válido para este campo.';
        }
        
        if (validacion.badInput) {
            return 'El valor ingresado no es válido.';
        }
        
        if (validacion.customError) {
            return campo.validationMessage || 'Error de validación personalizado.';
        }
        
        return 'Por favor, complete este campo correctamente.';
    }
    
    // DESHABILITAR COMPLETAMENTE LA VALIDACIÓN NATIVA
    function deshabilitarValidacionNativa() {
        if (DEBUG_VALIDATION) console.log('🔧 Deshabilitando validación nativa del navegador...');
        
        // Interceptar TODOS los eventos de formulario
        document.addEventListener('submit', function(event) {
            if (DEBUG_VALIDATION) console.log('📤 Evento submit interceptado:', event);
            event.preventDefault(); // Prevenir envío nativo
            event.stopPropagation(); // Detener propagación
            
            const formulario = event.target;
            if (DEBUG_VALIDATION) console.log('📋 Formulario interceptado:', formulario);
            
            // Validar manualmente
            validarFormularioManual(formulario);
        }, true);
        
        // Interceptar TODOS los eventos de click en botones submit
        document.addEventListener('click', function(event) {
            if (event.target.type === 'submit' || event.target.tagName === 'BUTTON') {
                if (DEBUG_VALIDATION) console.log('🖱️ Click en botón interceptado:', event.target);
                event.preventDefault();
                event.stopPropagation();
                
                const formulario = event.target.closest('form');
                if (formulario) {
                    validarFormularioManual(formulario);
                }
            }
        }, true);
        
        // Interceptar eventos de teclado (Enter)
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && event.target.tagName === 'INPUT') {
                if (DEBUG_VALIDATION) console.log('⌨️ Enter en input interceptado:', event.target);
                event.preventDefault();
                event.stopPropagation();
                
                const formulario = event.target.closest('form');
                if (formulario) {
                    validarFormularioManual(formulario);
                }
            }
        }, true);
    }
    
    // VALIDACIÓN MANUAL COMPLETA
    function validarFormularioManual(formulario) {
        if (DEBUG_VALIDATION) console.log('🔍 Validando formulario manualmente:', formulario);
        
        // Obtener todos los campos del formulario
        const campos = formulario.querySelectorAll('input, select, textarea');
        let esValido = true;
        let primerCampoInvalido = null;
        
        // Validar cada campo
        campos.forEach(campo => {
            if (campo.hasAttribute('required') && !campo.value.trim()) {
                if (DEBUG_VALIDATION) console.log('❌ Campo requerido vacío:', campo);
                esValido = false;
                if (!primerCampoInvalido) {
                    primerCampoInvalido = campo;
                }
            } else if (campo.hasAttribute('minlength')) {
                const minLength = parseInt(campo.getAttribute('minlength'));
                if (campo.value.length < minLength) {
                    if (DEBUG_VALIDATION) console.log('❌ Campo con longitud mínima:', campo);
                    esValido = false;
                    if (!primerCampoInvalido) {
                        primerCampoInvalido = campo;
                    }
                }
            } else if (campo.type === 'email' && campo.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(campo.value)) {
                    if (DEBUG_VALIDATION) console.log('❌ Email inválido:', campo);
                    esValido = false;
                    if (!primerCampoInvalido) {
                        primerCampoInvalido = campo;
                    }
                }
            } else if (campo.hasAttribute('pattern') && campo.value) {
                const pattern = new RegExp(campo.getAttribute('pattern'));
                if (!pattern.test(campo.value)) {
                    if (DEBUG_VALIDATION) console.log('❌ Patrón inválido:', campo);
                    esValido = false;
                    if (!primerCampoInvalido) {
                        primerCampoInvalido = campo;
                    }
                }
            }
        });
        
        if (esValido) {
            if (DEBUG_VALIDATION) console.log('✅ Formulario válido, enviando...');
            // Aquí puedes enviar el formulario
            alert('✅ Formulario válido! Datos enviados correctamente.');
        } else {
            if (DEBUG_VALIDATION) console.log('❌ Formulario inválido, mostrando error...');
            const mensaje = obtenerMensajeValidacion(primerCampoInvalido);
            mostrarErrorValidacion(primerCampoInvalido, mensaje, 'validacion');
            primerCampoInvalido.focus();
        }
    }
    
    // Función para configurar event listeners
    function configurarEventListeners() {
        // Event listener para el botón de cerrar
        if (closeBtn) {
            closeBtn.addEventListener('click', cerrarError);
        }
        
        // Interceptar cambios en campos para ocultar errores
        document.addEventListener('input', function(event) {
            if (event.target.tagName === 'INPUT') {
                const campo = event.target;
                if (campo.validity && campo.validity.valid) {
                    // Ocultar error si el campo ahora es válido
                    cerrarError();
                }
            }
        });
    }
    
    // Función global para mostrar errores de validación personalizados
    window.mostrarErrorValidacionOverride = function(campo, mensaje) {
        mostrarErrorValidacion(campo, mensaje, 'personalizado');
    };
    
    // Función global para validar un formulario específico
    window.validarFormularioOverride = function(formularioId) {
        const formulario = document.getElementById(formularioId);
        if (formulario) {
            validarFormularioManual(formulario);
        }
    };
    
    // Función de prueba
    window.probarOverrideValidacion = function() {
        if (DEBUG_VALIDATION) console.log('🧪 Probando override de validación...');
        const campo = document.querySelector('input[required]');
        if (campo) {
            campo.value = '';
            campo.focus();
            mostrarErrorValidacion(campo, 'Este campo es obligatorio. Por favor, complételo.', 'prueba');
        }
    };
    
    // Inicializar cuando el DOM esté listo
    function inicializar() {
        if (DEBUG_VALIDATION) console.log('🚀 Inicializando override de validación...');
        
        // Esperar un poco para que el DOM esté completamente cargado
        setTimeout(() => {
            if (inicializarReferencias()) {
                configurarEventListeners();
                deshabilitarValidacionNativa();
                if (DEBUG_VALIDATION) console.log('✅ Override de validación inicializado correctamente');
            } else {
                if (DEBUG_VALIDATION) console.error('❌ No se pudo inicializar el override de validación');
            }
        }, 100);
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }
    
    if (DEBUG_VALIDATION) console.log('🎯 Override de validación nativa cargado');
})();

