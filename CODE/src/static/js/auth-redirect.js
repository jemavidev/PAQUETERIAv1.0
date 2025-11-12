/**
 * PAQUETES EL CLUB v4.0 - Manejo de Redirección de Autenticación
 * Archivo: CODE/LOCAL/src/static/js/auth-redirect.js
 * Versión: 1.0.0
 * Fecha: 2025-01-24
 * Autor: Equipo de Desarrollo
 */

/**
 * Manejo automático de redirección de autenticación para llamadas AJAX
 */
class AuthRedirectHandler {
    constructor() {
        this.loginUrl = '/auth/login';
        this.setupInterceptors();
    }

    /**
     * Configurar interceptores para fetch y XMLHttpRequest
     */
    setupInterceptors() {
        // Interceptor para fetch
        this.interceptFetch();
        
        // Interceptor para XMLHttpRequest (para compatibilidad)
        this.interceptXHR();
    }

    /**
     * Interceptor para fetch API
     */
    interceptFetch() {
        const originalFetch = window.fetch;
        
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch(...args);
                
                // Verificar si la respuesta es 401
                if (response.status === 401) {
                    await this.handleUnauthorized(response, args[0]);
                    return response;
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
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this._url = url;
            return originalOpen.apply(this, [method, url, ...args]);
        };
        
        XMLHttpRequest.prototype.send = function(data) {
            this.addEventListener('readystatechange', () => {
                if (this.readyState === 4 && this.status === 401) {
                    this.handleUnauthorizedResponse();
                }
            });
            
            return originalSend.call(this, data);
        };
    }

    /**
     * Manejar respuesta 401 de fetch
     */
    async handleUnauthorized(response, requestInfo) {
        try {
            const data = await response.json();
            
            // Verificar si la respuesta indica que se requiere autenticación
            if (data.requires_auth || data.redirect_url) {
                const redirectUrl = data.redirect_url || this.loginUrl;
                const originalUrl = data.original_url || window.location.href;
                
                // Mostrar notificación al usuario
                this.showAuthNotification();
                
                // Redirigir después de un breve delay
                setTimeout(() => {
                    this.redirectToLogin(redirectUrl, originalUrl);
                }, 1500);
            }
        } catch (error) {
            console.error('Error al procesar respuesta 401:', error);
            // Redirigir de todas formas si hay error
            this.redirectToLogin();
        }
    }

    /**
     * Manejar respuesta 401 de XMLHttpRequest
     */
    handleUnauthorizedResponse() {
        try {
            const responseText = this.responseText;
            const data = JSON.parse(responseText);
            
            if (data.requires_auth || data.redirect_url) {
                const redirectUrl = data.redirect_url || '/auth/login';
                const originalUrl = data.original_url || window.location.href;
                
                // Mostrar notificación
                if (window.authRedirectHandler) {
                    window.authRedirectHandler.showAuthNotification();
                }
                
                // Redirigir
                setTimeout(() => {
                    if (window.authRedirectHandler) {
                        window.authRedirectHandler.redirectToLogin(redirectUrl, originalUrl);
                    }
                }, 1500);
            }
        } catch (error) {
            console.error('Error al procesar respuesta 401 de XHR:', error);
            // Redirigir de todas formas
            setTimeout(() => {
                if (window.authRedirectHandler) {
                    window.authRedirectHandler.redirectToLogin();
                }
            }, 1000);
        }
    }

    /**
     * Mostrar notificación de autenticación requerida
     */
    showAuthNotification() {
        // Crear notificación toast
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
        
        // Estilos para la notificación
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
        if (!document.getElementById('auth-notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'auth-notification-styles';
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
        
        // Remover la notificación después de 3 segundos
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
        
        // Agregar la URL original como parámetro de redirección
        if (originalUrl && originalUrl !== window.location.href) {
            const separator = loginUrl.includes('?') ? '&' : '?';
            redirectUrl += `${separator}redirect=${encodeURIComponent(originalUrl)}`;
        }
        
        console.log('Redirigiendo al login:', redirectUrl);
        window.location.href = redirectUrl;
    }

    /**
     * Verificar si el usuario está autenticado
     */
    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/me', {
                method: 'GET',
                credentials: 'include'
            });
            
            if (response.status === 401) {
                this.redirectToLogin();
                return false;
            }
            
            return response.ok;
        } catch (error) {
            console.error('Error al verificar estado de autenticación:', error);
            return false;
        }
    }
}

// Inicializar el manejador de redirección de autenticación
document.addEventListener('DOMContentLoaded', () => {
    window.authRedirectHandler = new AuthRedirectHandler();
    
    // Verificar estado de autenticación al cargar la página SOLO en rutas protegidas
    const protectedPaths = ['/profile', '/settings', '/admin', '/dashboard', '/messages', '/packages', '/receive'];
    const publicPaths = ['/announce', '/search', '/auth/login', '/auth/register', '/help', '/cookies', '/policies', '/', '/error-demo'];
    const currentPath = window.location.pathname;

    // No verificar autenticación en rutas públicas
    const isPublic = publicPaths.some(path => currentPath === path || currentPath.startsWith(path + '/'));
    const isProtected = protectedPaths.some(path => currentPath.startsWith(path));

    if (isProtected && !isPublic) {
        window.authRedirectHandler.checkAuthStatus();
    }
});

// Exportar para uso global
window.AuthRedirectHandler = AuthRedirectHandler;
