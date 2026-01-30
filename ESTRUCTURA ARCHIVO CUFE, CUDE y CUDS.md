# Estructura de Extracción para Facturación Electrónica (DIAN)

Este documento define los bloques de datos y campos identificados en las Facturas Electrónicas de Venta y Documentos Equivalentes POS para su posterior procesamiento y almacenamiento en base de datos.

---

## 1. Bloque: Identificación del Documento (Header)
*Campos clave para la tabla principal de facturas.*

| Campo | Descripción | Tipo de Dato | Observaciones |
| :--- | :--- | :--- | :--- |
| `tipo_documento` | Factura o POS | String | Determina la lógica de validación |
| `identificador_unico` | CUFE, CUDE o CUDS | String (Hex) | **Primary Key** sugerida |
| `numero_factura` | Prefijo + Número | String | Ej: FEGM-2748 |
| `fecha_emision` | ISO 8601 | Datetime | Incluye fecha y hora |
| `fecha_vencimiento`| Fecha límite | Date | Puede ser nulo en POS/Contado |
| `tipo_operacion` | Código DIAN | String | Generalmente "10 Estándar" |

---

## 2. Bloque: Emisor (Vendedor)
*Información para la tabla de Proveedores/Terceros.*

* **Razón Social / Nombre Comercial**
* **NIT** (Incluir dígito de verificación si existe)
* **Régimen Fiscal** (Ej: R-99-PN)
* **Responsabilidad Tributaria** (Ej: 01-IVA)
* **Ubicación:** Dirección, Ciudad, Departamento.
* **Contacto:** Teléfono, Correo electrónico.

---

## 3. Bloque: Adquiriente (Comprador)
*Datos del cliente (en este caso, Papyrus SAS).*

* **Nombre / Razón Social**
* **NIT / Identificación**
* **Dirección / Ciudad**

---

## 4. Bloque: Condiciones Comerciales
*Metadatos de la transacción.*

* **Forma de Pago:** Contado / Crédito.
* **Medio de Pago:** Efectivo, Tarjeta (Débito/Crédito), Instrumento no definido.
* **Moneda:** ISO Code (COP).
* **Orden de Pedido:** Número y fecha asociada.

---

## 5. Bloque: Detalle de Ítems (Líneas de Factura)
*Estructura para tabla relacional `factura_detalles`.*

| Campo | Descripción | Tipo de Dato |
| :--- | :--- | :--- |
| `linea_id` | Orden del producto | Integer |
| `codigo_producto` | Referencia o EAN | String |
| `descripcion` | Nombre del producto | Text |
| `cantidad` | Unidades | Decimal |
| `unidad_medida` | Código (Ej: NIU) | String |
| `precio_unitario` | Valor base | Decimal |
| `iva_porcentaje` | % de impuesto | Decimal |
| `iva_valor` | Monto del impuesto | Decimal |
| `descuento_valor` | Rebaja por ítem | Decimal |
| `total_item` | Cantidad * Precio | Decimal |

---

## 6. Bloque: Totales Financieros
*Campos para auditoría y cierre de valores.*

* **Subtotal:** Suma de bases gravables.
* **Total Bruto:** Subtotal antes de descuentos.
* **Impuestos:**
    * `total_iva`: Sumatoria de IVA.
    * `total_inc`: Consumo (si aplica).
    * `total_bolsas`: Impuesto al plástico.
* **Total Neto:** Valor total pagado (Total Factura).

---

## 7. Bloque: Información Técnica (Validación)
*Datos para trazabilidad y legalidad.*

* **Proveedor Tecnológico:** Software que generó el PDF.
* **Resolución DIAN:** Número, prefijo, rango autorizado y fechas de vigencia.
* **Código QR:** URL o contenido del QR para validación directa.
