/**
 * ========================================
 * OPTIMIZACIÓN DE SELECCIÓN DE IMÁGENES
 * ========================================
 * Mejoras de rendimiento y UX para escritorio
 * Fecha: 2025-11-17
 */

(function() {
    'use strict';
    
    // Configuración optimizada
    const CONFIG = {
        MAX_IMAGES: 3,
        MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
        ALLOWED_TYPES: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
        DESKTOP_BREAKPOINT: 769
    };
    
    // Detección mejorada de dispositivo
    function isDesktopDevice() {
        const hasFinePonter = window.matchMedia('(pointer: fine)').matches;
        const isWideScreen = window.innerWidth >= CONFIG.DESKTOP_BREAKPOINT;
        const userAgent = navigator.userAgent.toLowerCase();
        const isMobileUA = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);
        
        return hasFinePonter && isWideScreen && !isMobileUA;
    }
    
    // Optimizar texto del botón según el dispositivo
    function updateButtonText() {
        const button = document.getElementById('selectImagesBtn');
        const textElement = button?.querySelector('.desktop-text');
        
        if (textElement && isDesktopDevice()) {
            textElement.textContent = 'Seleccionar archivos de imagen';
        }
    }
    
    // Optimizar configuración del input file
    function optimizeFileInput() {
        const input = document.getElementById('packageImages');
        if (!input) return;
        
        if (isDesktopDevice()) {
            // En escritorio: solo galería, sin cámara
            input.removeAttribute('capture');
            input.setAttribute('accept', CONFIG.ALLOWED_TYPES.join(','));
            console.log('📁 Configurado para escritorio: solo galería');
        } else {
            // En móvil: permitir tomar foto con cámara
            input.setAttribute('capture', 'environment');
            input.setAttribute('accept', 'image/*');
            console.log('📱 Configurado para móvil: cámara + galería');
        }
    }
    
    // Validación rápida de archivos
    function validateFiles(files) {
        const errors = [];
        
        if (files.length > CONFIG.MAX_IMAGES) {
            errors.push(`Máximo ${CONFIG.MAX_IMAGES} imágenes permitidas`);
        }
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            if (!CONFIG.ALLOWED_TYPES.includes(file.type)) {
                errors.push(`Formato no válido: ${file.name}`);
            }
            
            if (file.size > CONFIG.MAX_FILE_SIZE) {
                errors.push(`Archivo muy grande: ${file.name} (máx. 5MB)`);
            }
        }
        
        return errors;
    }
    
    // Mostrar feedback visual inmediato
    function showButtonFeedback(button, type = 'loading') {
        if (!button) return;
        
        button.classList.add(type);
        
        // Remover feedback después de un tiempo
        setTimeout(() => {
            button.classList.remove(type);
        }, type === 'loading' ? 2000 : 1000);
    }
    
    // Inicialización cuando el DOM esté listo
    function initialize() {
        // Actualizar texto del botón
        updateButtonText();
        
        // Optimizar input file
        optimizeFileInput();
        
        // Agregar listener optimizado para cambio de ventana
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                updateButtonText();
                optimizeFileInput();
            }, 250);
        });
        
        // Mejorar el listener del botón si existe
        const button = document.getElementById('selectImagesBtn');
        if (button) {
            // Agregar feedback visual inmediato
            button.addEventListener('click', (e) => {
                // Reconfigurar input antes de cada click para asegurar configuración correcta
                optimizeFileInput();
                
                if (isDesktopDevice()) {
                    showButtonFeedback(button, 'loading');
                }
            });
            
            // Mejorar accesibilidad
            button.setAttribute('role', 'button');
            button.setAttribute('aria-label', 'Seleccionar imágenes para el paquete');
            
            // Soporte para teclado
            button.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    button.click();
                }
            });
        }
        
        console.log('🖼️ Optimización de selección de imágenes inicializada');
        console.log(`📱 Dispositivo detectado: ${isDesktopDevice() ? 'Escritorio' : 'Móvil/Tablet'}`);
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    // Exponer funciones útiles globalmente
    window.ImageUploadOptimizer = {
        isDesktopDevice,
        validateFiles,
        CONFIG
    };
    
})();