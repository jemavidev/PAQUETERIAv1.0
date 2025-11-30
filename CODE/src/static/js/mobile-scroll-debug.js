/**
 * PAQUETES EL CLUB v4.0 - Mobile Scroll Debug
 * Versión: 4.0.1
 * Autor: Sistema PAQUETES EL CLUB
 * Fecha: 2024-11-27
 * 
 * Script para detectar y reportar problemas de scroll en dispositivos móviles
 * Solo se activa en modo debug o cuando se detectan problemas
 */

(function() {
    'use strict';
    
    // Configuración
    const DEBUG_MODE = false; // Cambiar a true para activar logs detallados
    const AUTO_FIX = false; // DESHABILITADO: Estaba causando problemas de rendimiento
    const ENABLE_MONITOR = false; // DESHABILITADO: MutationObserver bloqueaba el navegador
    
    /**
     * Detecta si estamos en un dispositivo móvil
     */
    function isMobileDevice() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               window.innerWidth <= 768;
    }
    
    /**
     * Detecta si estamos en iOS Safari
     */
    function isIOSSafari() {
        const ua = navigator.userAgent;
        const iOS = /iPad|iPhone|iPod/.test(ua);
        const webkit = /WebKit/.test(ua);
        const notChrome = !/CriOS/.test(ua);
        return iOS && webkit && notChrome;
    }
    
    /**
     * Verifica si un elemento tiene problemas de scroll
     */
    function checkScrollIssues(element) {
        const issues = [];
        const computed = window.getComputedStyle(element);
        
        // Verificar overflow
        if (computed.overflow === 'hidden' || computed.overflowY === 'hidden') {
            issues.push({
                type: 'overflow-hidden',
                element: element,
                message: 'Elemento tiene overflow:hidden que puede bloquear scroll'
            });
        }
        
        // Verificar altura fija
        if (computed.height !== 'auto' && computed.height.includes('vh')) {
            issues.push({
                type: 'fixed-height-vh',
                element: element,
                message: 'Elemento usa altura en vh que puede causar problemas en iOS'
            });
        }
        
        // Verificar si el contenido excede el contenedor
        if (element.scrollHeight > element.clientHeight && computed.overflowY === 'visible') {
            issues.push({
                type: 'content-overflow',
                element: element,
                message: 'Contenido excede el contenedor pero overflow es visible'
            });
        }
        
        return issues;
    }
    
    /**
     * Aplica correcciones automáticas
     */
    function applyAutoFixes() {
        if (!AUTO_FIX) return;
        
        // Fix 1: Asegurar que body permita scroll
        document.body.style.overflowY = 'auto';
        document.body.style.webkitOverflowScrolling = 'touch';
        document.body.style.minHeight = '100%';
        document.body.style.height = 'auto';
        
        // Fix 2: Asegurar que html permita scroll
        document.documentElement.style.overflowY = 'auto';
        document.documentElement.style.height = '100%';
        
        // Fix 3: iOS Safari viewport fix
        if (isIOSSafari()) {
            document.documentElement.style.height = '-webkit-fill-available';
            document.body.style.minHeight = '-webkit-fill-available';
        }
        
        // Fix 4: Asegurar que main permita scroll
        const main = document.querySelector('main');
        if (main) {
            main.style.flex = '1 1 auto';
            main.style.overflowY = 'auto';
            main.style.webkitOverflowScrolling = 'touch';
            main.style.minHeight = '0';
            main.style.height = 'auto';
        }
        
        // Fix 5: Corregir contenedores problemáticos
        const containers = document.querySelectorAll('.container, .max-w-7xl, .mx-auto');
        containers.forEach(container => {
            if (container.style.height && container.style.height !== 'auto') {
                container.style.height = 'auto';
            }
            if (container.style.overflow === 'hidden') {
                container.style.overflow = 'visible';
            }
        });
        
        if (DEBUG_MODE) {
            console.log('✅ Correcciones automáticas de scroll aplicadas');
        }
    }
    
    /**
     * Analiza toda la página en busca de problemas
     */
    function analyzePage() {
        const allIssues = [];
        
        // Elementos críticos a verificar
        const criticalElements = [
            document.documentElement,
            document.body,
            document.querySelector('main'),
            ...document.querySelectorAll('.container, .max-w-7xl, .content-wrapper')
        ].filter(el => el !== null);
        
        criticalElements.forEach(element => {
            const issues = checkScrollIssues(element);
            if (issues.length > 0) {
                allIssues.push(...issues);
            }
        });
        
        return allIssues;
    }
    
    /**
     * Reporta problemas encontrados
     */
    function reportIssues(issues) {
        if (issues.length === 0) {
            if (DEBUG_MODE) {
                console.log('✅ No se encontraron problemas de scroll');
            }
            return;
        }
        
        console.warn(`⚠️ Se encontraron ${issues.length} problemas de scroll:`);
        issues.forEach((issue, index) => {
            console.warn(`${index + 1}. ${issue.type}: ${issue.message}`, issue.element);
        });
    }
    
    /**
     * Monitorea cambios en el DOM que puedan afectar el scroll
     * DESHABILITADO: Causaba problemas de rendimiento
     */
    function setupScrollMonitor() {
        if (!ENABLE_MONITOR) {
            if (DEBUG_MODE) {
                console.log('⏸️ Monitor de scroll deshabilitado (mejora de rendimiento)');
            }
            return;
        }
        
        const observer = new MutationObserver((mutations) => {
            // Verificar si algún cambio afecta el scroll
            let needsCheck = false;
            
            mutations.forEach(mutation => {
                if (mutation.type === 'attributes' && 
                    (mutation.attributeName === 'style' || 
                     mutation.attributeName === 'class')) {
                    needsCheck = true;
                }
            });
            
            if (needsCheck && AUTO_FIX) {
                applyAutoFixes();
            }
        });
        
        observer.observe(document.body, {
            attributes: true,
            childList: true,
            subtree: true,
            attributeFilter: ['style', 'class']
        });
        
        if (DEBUG_MODE) {
            console.log('👁️ Monitor de scroll activado');
        }
    }
    
    /**
     * Agrega información de debug al DOM
     */
    function addDebugInfo() {
        if (!DEBUG_MODE) return;
        
        const debugInfo = document.createElement('div');
        debugInfo.id = 'scroll-debug-info';
        debugInfo.style.cssText = `
            position: fixed;
            bottom: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            z-index: 9999;
            max-width: 300px;
        `;
        
        const updateDebugInfo = () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight;
            const clientHeight = document.documentElement.clientHeight;
            const scrollPercent = (scrollTop / (scrollHeight - clientHeight) * 100).toFixed(1);
            
            debugInfo.innerHTML = `
                <strong>Scroll Debug</strong><br>
                Dispositivo: ${isMobileDevice() ? 'Móvil' : 'Desktop'}<br>
                iOS Safari: ${isIOSSafari() ? 'Sí' : 'No'}<br>
                Scroll: ${scrollTop}px / ${scrollHeight}px (${scrollPercent}%)<br>
                Viewport: ${clientHeight}px<br>
                Body Height: ${document.body.scrollHeight}px
            `;
        };
        
        document.body.appendChild(debugInfo);
        window.addEventListener('scroll', updateDebugInfo);
        updateDebugInfo();
    }
    
    /**
     * Inicialización
     */
    function init() {
        // DESHABILITADO TEMPORALMENTE para debugging
        // Este script estaba causando problemas de rendimiento
        if (DEBUG_MODE) {
            console.log('⏸️ mobile-scroll-debug.js deshabilitado temporalmente');
        }
        return;
        
        /* CÓDIGO ORIGINAL COMENTADO
        // Solo ejecutar en dispositivos móviles o en modo debug
        if (!isMobileDevice() && !DEBUG_MODE) {
            return;
        }
        
        if (DEBUG_MODE) {
            console.log('🔍 Iniciando análisis de scroll móvil...');
        }
        
        // Esperar a que el DOM esté completamente cargado
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        // Aplicar correcciones automáticas
        applyAutoFixes();
        
        // Analizar página
        const issues = analyzePage();
        reportIssues(issues);
        
        // Configurar monitor
        setupScrollMonitor();
        
        // Agregar info de debug si está habilitado
        addDebugInfo();
        
        // Verificar después de que todas las imágenes se carguen
        window.addEventListener('load', () => {
            setTimeout(() => {
                applyAutoFixes();
                const postLoadIssues = analyzePage();
                if (postLoadIssues.length > 0 && DEBUG_MODE) {
                    console.warn('⚠️ Problemas detectados después de cargar:', postLoadIssues);
                }
            }, 500);
        });
        
        if (DEBUG_MODE) {
            console.log('✅ Análisis de scroll móvil completado');
        }
        */
    }
    
    // Exponer funciones globalmente para debugging manual
    window.scrollDebug = {
        analyze: analyzePage,
        fix: applyAutoFixes,
        report: reportIssues,
        isMobile: isMobileDevice,
        isIOS: isIOSSafari
    };
    
    // Iniciar
    init();
})();
