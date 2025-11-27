/**
 * PAQUETES EL CLUB v2.0 - Manejo de Redirección de Autenticación (Refactorizado)
 * Archivo: CODE/src/static/js/auth-redirect-v2.js
 * Versión: 2.0.0
 * Fecha: 2025-01-27
 * Autor: Equipo de Desarrollo
 * 
 * RESPONSABILIDADES:
 * - SOLO interceptar respuestas 401 de fetch/XMLHttpRequest
 * - Mostrar notificación al usuario
 * - Redirigir a página de login
 * 
 * NO HACE:
 * - Verificar autenticación al cargar página (eso es del backend)
 * - Mantener lista de rutas públicas (eso es del backend)
 * - Decidir si verificar o no según la ruta (eso es del backend)
 */

class AuthRedirectHandler {
    constructor() {
        this.loginUrl = '/auth/login';
        this.setupInterceptors();
        console.log('🔐 AuthRedirectHandler v2.0 inicializado (solo intercepta 401)');
    }

    /**
     * Configurar interceptores para fetch y XMLHttpRequest
     */
    setupInterceptors() {
        this.interceptFetch();
        this.interceptXHR();
    }

    /**
     * Interceptor para fetch API
     */
    interceptFetch() {
        const originalFetch = window.fetch;
        const self = this;
        
        window.fetch = async function(...args) {
            try {
                const response = await originalFetch(...args);
                
                // Solo manejar respuestas 401
                if (response.status === 401) {
                    // Clonar response para poder leerla
                    const clonedResponse = response.clone();
                    
                    try {
                        const data = await clonedResponse.json();
                        
                        // Verificar si requiere autenticación
                        if (data.requires_auth || data.redirect_url) {
                            self.handleUnauthorized(data);
                        }
                    } catch (jsonError) {
                        // Si no es JSON, asumir que requiere autenticación
                        console.warn('Respuesta 401 sin JSON válido, redirigiendo a login');
                        self.handleUnauthorized({});
                    }
                }
                
                return response;
            } catch (error) {
                console.error('Error en fetch:', error);
                throw error;
            }
        };
    }

    /**
     * Interceptor para XMLHttpRequest
     */
    interceptXHR() {
        const self = this;
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this._url = url;
            return originalOpen.apply(this, [method, url, ...args]);
        };
        
        XMLHttpRequest.prototype.send = function(data) {
            this.addEventListener('readystatechange', function() {
                if (this.readyState === 4 && this.status === 401) {
                    try {
                        const responseData = JSON.parse(this.responseText);
                        
                        if (responseData.requires_auth || responseData.redirect_url) {
                            self.handleUnauthorized(responseData);
                        }
                    } catch (jsonError) {
                        // Si no es JSON, asumir que requiere autenticación
                        console.warn('Respuesta 401 XHR sin JSON válido, redirigiendo a login');
                        self.handleUnauthorized({});
                    }
                }
            });
            
            return originalSend.call(this, data);
        };
    }

    /**
     * Manejar respuesta 401
     */
    handleUnauthorized(data) {
        const redirectUrl = data.redirect_url || this.loginUrl;
        const originalUrl = data.original_url || window.location.href;
        
        console.log('🔒 Sesión expirada, redirigiendo a login');
        
        // Mostrar notificación
        this.showAuthNotification();
        
        // Redirigir después de un breve delay
        setTimeout(() => {
            this.redirectToLogin(redirectUrl, originalUrl);
        }, 1500);
    }

    /**
     * Mostrar notificación de autenticación requerida
     */
    showAuthNotification() {
        // Verificar si ya existe una notificación
        if (document.querySelector('.auth-notification')) {
            return;
        }
        
        // Crear notificación
        const notification = document.createElement('div');
        notification.className = 'auth-notification';
        notification.innerHTML = `
            <div class="auth-notification-content">
                <div class="auth-notification-icon">🔒</div>
                <div class="auth-notification-text">
                    <strong>Sesión expirada</strong>
                    <p>Tu sesión ha expirado. Serás redirigido al login...</p>
                </div>
            </div>
        `;
        
        // Estilos inline para la notificación
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 10000;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;
        
        // Agregar estilos CSS si no existen
        if (!document.getElementById('auth-notification-styles-v2')) {
            const styles = document.createElement('style');
            styles.id = 'auth-notification-styles-v2';
            styles.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                .auth-notification-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                .auth-notification-icon {
                    font-size: 24px;
                }
                .auth-notification-text strong {
                    display: block;
                    color: #92400e;
                    margin-bottom: 4px;
                }
                .auth-notification-text p {
                    margin: 0;
                    color: #78350f;
                    font-size: 14px;
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(notification);
        
        // Remover después de 3 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    /**
     * Redirigir al login
     */
    redirectToLogin(loginUrl = this.loginUrl, originalUrl = null) {
        let redirectUrl = loginUrl;
        
        // Agregar URL original como parámetro
        if (originalUrl && originalUrl !== window.location.href) {
            const separator = loginUrl.includes('?') ? '&' : '?';
            redirectUrl += `${separator}redirect=${encodeURIComponent(originalUrl)}`;
        }
        
        console.log('Redirigiendo a:', redirectUrl);
        window.location.href = redirectUrl;
    }
}

// Inicializar SOLO el interceptor (sin verificación de autenticación)
document.addEventListener('DOMContentLoaded', () => {
    window.authRedirectHandler = new AuthRedirectHandler();
});

// Exportar para uso global
window.AuthRedirectHandler = AuthRedirectHandler;
