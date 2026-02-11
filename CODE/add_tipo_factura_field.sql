-- Migración: Agregar campo tipo_factura a invoices_v2
-- Fecha: 2026-02-11
-- Descripción: Permite clasificar facturas como reventa, consumo, servicio u otro

-- 1. Agregar columna tipo_factura
ALTER TABLE invoices_v2 
ADD COLUMN IF NOT EXISTS tipo_factura VARCHAR(20) DEFAULT 'reventa' NOT NULL;

-- 2. Crear índice para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_invoices_tipo_factura 
ON invoices_v2(tipo_factura);

-- 3. Actualizar facturas existentes (opcional - todas quedan como 'reventa' por defecto)
-- Si quieres marcar algunas facturas específicas como consumo, puedes hacerlo aquí:
-- UPDATE invoices_v2 SET tipo_factura = 'consumo' WHERE proveedor_nombre LIKE '%SERVICIOS%';

-- 4. Verificar que se aplicó correctamente
SELECT 
    tipo_factura,
    COUNT(*) as total_facturas
FROM invoices_v2
GROUP BY tipo_factura
ORDER BY total_facturas DESC;

-- Resultado esperado:
-- tipo_factura | total_facturas
-- -------------+---------------
-- reventa      | XXX (todas las facturas existentes)
