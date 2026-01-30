# Especificación de Extracción de Datos - Facturación Electrónica DIAN

Este documento define la lógica de captura para los 5 campos prioritarios y campos secundarios, adaptada a la variabilidad de formatos (Factura Estándar, Tiquete POS, Factura de Papelería).

---

## 1. Bloque de Datos Prioritarios (Core Data)

| Campo | Identificador Técnico | Estrategia de Extracción (RegEx / Anchor) |
| :--- | :--- | :--- |
| **CUFE / CUDS** | `uuid_dian` | **RegEx:** `[0-9a-fA-F]{96}` (Cadena exacta de 96 caracteres hexadecimales). |
| **Proveedor** | `emisor_nombre` | **Anchor:** Texto inmediatamente superior a "NIT" en el primer bloque o después de "Vendedor:". |
| **Valor Total** | `total_factura` | **Anchor:** Valor numérico a la derecha de "TOTAL", "TOTAL FACTURA" o "VALOR A PAGAR". |
| **Fecha** | `fecha_emision` | **RegEx:** `\d{4}[-/]\d{2}[-/]\d{2}` o `\d{2}[-/]\d{2}[-/]\d{4}`. |
| **Nro. Factura** | `documento_numero` | **Anchor:** Texto tras "Número de factura:", "FEV No." o "GRM...". |

---

## 2. Bloque de Datos Secundarios (Enriquecimiento)
*Datos detectados en los archivos cargados que aportan valor a la base de datos.*

* **NIT Proveedor:** `(?i)NIT[:\s]+(\d{9,10}[-\d]?)`
* **Nombre Cliente:** Generalmente "DISTRIBUIDORA PAPYRUS SAS" o "PAPYRUS SOLUCIONES".
* **NIT Cliente:** `901210008` (Constante en tus archivos).
* **Impuesto (IVA):** Valor asociado a la etiqueta "IVA 19%" o "Total Impuestos".
* **Medio de Pago:** "Efectivo", "Tarjeta Débito", "Crédito".

---

## 3. Lógica de Captura por Tipo de Archivo

Para garantizar la mayor cantidad de datos, el extractor debe aplicar estas reglas de prioridad:

### A. Formato Tiquete (POS/Veneplast)
* **Número de Factura:** Buscar patrón que inicie con prefijo `GRM` o `GRMZ`.
* **CUDS:** Suele estar al final del documento, cerca del bloque de "Firma Digital" o "Certificado".
* **Total:** Buscar la línea que dice `TOTAL $XX.XXX,XX`.

### B. Formato Estándar (Nancy Diaz / Racopi)
* **Proveedor:** Ubicado en el encabezado (Top-Left o Top-Center).
* **Fecha:** Buscar etiquetas "Fecha de Generación" o "Fecha de Validación".
* **CUFE:** Generalmente debajo del título del documento o cerca del código QR.

---

## 4. Normalización de Datos (Post-Extracción)

Antes de insertar en la base de datos, aplicar:
1. **Limpieza de Moneda:** Eliminar `$`, puntos de miles y convertir comas decimales a puntos (`480.000,00` -> `480000.00`).
2. **Estandarización de Fecha:** Convertir todos los formatos encontrados a `ISO 8601` (`YYYY-MM-DD`).
3. **Trim de Identificadores:** Eliminar saltos de línea accidentales en el CUFE/CUDS de 96 caracteres.
