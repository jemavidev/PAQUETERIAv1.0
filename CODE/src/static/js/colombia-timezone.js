/**
 * Colombia Timezone Utilities
 * Utilidades para manejo de zona horaria de Colombia
 * PAQUETES EL CLUB v4.0
 */

// Configuración de zona horaria de Colombia
const COLOMBIA_TIMEZONE = 'America/Bogota';

/**
 * Obtiene la fecha actual en zona horaria de Colombia
 * @returns {Date} Fecha actual en Colombia
 */
function getColombiaTime() {
    return new Date().toLocaleString("en-US", {timeZone: COLOMBIA_TIMEZONE});
}

/**
 * Formatea una fecha para mostrar en zona horaria de Colombia
 * @param {Date|string} date - Fecha a formatear
 * @returns {string} Fecha formateada en zona horaria de Colombia
 */
function formatColombiaTime(date) {
    if (!date) return '';
    
    const colombiaDate = new Date(date).toLocaleString("es-CO", {
        timeZone: COLOMBIA_TIMEZONE,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    return colombiaDate;
}

/**
 * Obtiene el offset de Colombia respecto a UTC
 * @returns {number} Offset en minutos
 */
function getColombiaOffset() {
    const now = new Date();
    const utc = new Date(now.getTime() + (now.getTimezoneOffset() * 60000));
    const colombia = new Date(utc.toLocaleString("en-US", {timeZone: COLOMBIA_TIMEZONE}));
    return (colombia.getTime() - utc.getTime()) / 60000;
}

/**
 * Convierte una fecha UTC a zona horaria de Colombia
 * @param {Date|string} utcDate - Fecha UTC
 * @returns {Date} Fecha en zona horaria de Colombia
 */
function utcToColombia(utcDate) {
    if (!utcDate) return null;
    
    const date = new Date(utcDate);
    const offset = getColombiaOffset();
    return new Date(date.getTime() + (offset * 60000));
}

/**
 * Convierte una fecha de Colombia a UTC
 * @param {Date|string} colombiaDate - Fecha en Colombia
 * @returns {Date} Fecha UTC
 */
function colombiaToUtc(colombiaDate) {
    if (!colombiaDate) return null;
    
    const date = new Date(colombiaDate);
    const offset = getColombiaOffset();
    return new Date(date.getTime() - (offset * 60000));
}

/**
 * Obtiene la fecha actual en formato ISO para Colombia
 * @returns {string} Fecha ISO en zona horaria de Colombia
 */
function getColombiaISOString() {
    const now = new Date();
    const colombiaTime = new Date(now.toLocaleString("en-US", {timeZone: COLOMBIA_TIMEZONE}));
    return colombiaTime.toISOString();
}

// Exportar funciones para uso global
window.ColombiaTimezone = {
    getColombiaTime,
    formatColombiaTime,
    getColombiaOffset,
    utcToColombia,
    colombiaToUtc,
    getColombiaISOString,
    TIMEZONE: COLOMBIA_TIMEZONE
};

// Log de inicialización
console.log('🇨🇴 Colombia Timezone utilities loaded');
console.log('🕐 Current Colombia time:', getColombiaTime());
console.log('⏰ Colombia offset (minutes):', getColombiaOffset());
