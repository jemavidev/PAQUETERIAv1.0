// ========================================
// PAQUETES EL CLUB v4.0 - Configuración JavaScript
// ========================================
// Archivo: CODE/LOCAL/src/static/js/config.js
// Versión: 1.0.0
// Fecha: 2025-01-24
// Autor: Equipo de Desarrollo
// ========================================

/**
 * Configuración global de la aplicación
 */
window.PAQUETES_CONFIG = {
    // Configuración de la aplicación
    app: {
        name: 'PAQUETES EL CLUB',
        version: '4.0.0',
        environment: 'development'
    },
    
    // Configuración de API
    api: {
        baseUrl: '/api',
        timeout: 30000,
        retryAttempts: 3
    },
    
    // Configuración de alertas
    alerts: {
        defaultDuration: 5000,
        maxAlerts: 5,
        position: 'top-right'
    },
    
    // Configuración de validación
    validation: {
        debounceDelay: 300,
        showErrorsOnBlur: true,
        showErrorsOnSubmit: true
    },
    
    // Configuración de formularios
    forms: {
        autoFocus: true,
        preventDoubleSubmit: true,
        showLoadingStates: true
    },
    
    // Configuración de notificaciones
    notifications: {
        enabled: true,
        checkInterval: 30000,
        maxUnread: 99
    }
};

/**
 * Utilidades de configuración
 */
window.ConfigUtils = {
    /**
     * Obtener valor de configuración
     */
    get: function(path, defaultValue = null) {
        const keys = path.split('.');
        let value = window.PAQUETES_CONFIG;
        
        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return defaultValue;
            }
        }
        
        return value;
    },
    
    /**
     * Establecer valor de configuración
     */
    set: function(path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        let target = window.PAQUETES_CONFIG;
        
        for (const key of keys) {
            if (!target[key] || typeof target[key] !== 'object') {
                target[key] = {};
            }
            target = target[key];
        }
        
        target[lastKey] = value;
    },
    
    /**
     * Verificar si una característica está habilitada
     */
    isEnabled: function(feature) {
        return this.get(feature, false);
    }
};

// Log de inicialización
console.log('🔧 Configuración PAQUETES EL CLUB v4.0 cargada correctamente');