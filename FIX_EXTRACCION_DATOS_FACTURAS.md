# Fix: Extracción de Datos de Facturas de Proveedores

## Problema Identificado

Las facturas mostraban datos incorrectos o incompletos:
- ❌ Muchas facturas con "Sin proveedor" cuando SÍ tienen proveedor
- ❌ Fechas no se extraían correctamente
- ❌ Números de factura faltantes
- ❌ El problema estaba en el **backend** - método `extract_basic_info_from_pdf()`

## Análisis del Problema

El método original tenía limitaciones graves:

### 1. Extracción de Proveedor
**Antes:**
```python
# Solo buscaba "Razón Social" o "Nombre" cerca del NIT
razon_patterns = [
    r'Razón\s*Social[:\s]*([^\n]+)',
    r'Nombre[:\s]*([^\n]+)',
]
```

**Problema:** La mayoría de facturas no tienen el texto "Razón Social" explícito.

### 2. Extracción de Fecha
**Antes:**
```python
# Patrones muy limitados
date_patterns = [
    r'Fecha[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
    r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
    r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
]
```

**Problema:** No manejaba formatos como "11 de noviembre de 2025" ni validaba años razonables.

### 3. Extracción de Número de Factura
**Antes:**
```python
# Patrones básicos
invoice_patterns = [
    r'Factura\s*(?:No\.?|Nro\.?|#|N°)?\s*[:\s]*([A-Z0-9-]+)',
    r'(?:FV|FE|FA)[:\s-]*(\d+)',
    r'Número[:\s]*([A-Z0-9-]+)',
]
```

**Problema:** No capturaba formatos como "7GF-125" o "FE-30188".

## Solución Implementada

### 1. Extracción de Proveedor MEJORADA ✅

**Estrategia de 2 niveles:**

#### Nivel 1: Búsqueda por Patrones
```python
supplier_patterns = [
    r'(?:Razón\s*Social|Nombre\s*Comercial|Empresa)[:\s]*([^\n]+)',
    r'(?:Proveedor|Vendedor|Emisor)[:\s]*([^\n]+)',
]
```

#### Nivel 2: Búsqueda en Primeras Líneas
```python
# Si no se encuentra con patrones, buscar en las primeras 15 líneas
# El proveedor suele estar arriba, antes del NIT
for i, line in enumerate(lines[:15]):
    # Saltar líneas con palabras clave
    if any(keyword in line.upper() for keyword in ['FACTURA', 'FECHA', 'NIT', 'CUFE']):
        continue
    # Si tiene entre 5 y 100 caracteres y no es solo números
    if 5 < len(line) < 100 and not re.match(r'^[\d\s\-\.]+$', line):
        info['supplier_name'] = line.upper()
        break
```

#### Limpieza de Datos
```python
# Limpiar el nombre extraído
name = re.sub(r'\s+', ' ', name)  # Normalizar espacios
name = name.split('NIT')[0].strip()  # Quitar NIT si está junto
name = name.split('FECHA')[0].strip()  # Quitar FECHA si está junto
```

### 2. Extracción de Fecha MEJORADA ✅

**Más patrones y validación:**
```python
date_patterns = [
    r'Fecha\s*(?:de\s*)?(?:Emisión|Expedición)?[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
    r'Fecha[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
    r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
    r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
    r'Fecha[:\s]*(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',  # "11 de noviembre de 2025"
]

# Validar año razonable
if 2020 <= parsed_date.year <= 2030:
    info['invoice_date'] = parsed_date
```

### 3. Extracción de Número MEJORADA ✅

**Más patrones y validación:**
```python
invoice_patterns = [
    r'Factura\s*(?:No\.?|Nro\.?|#|N°|Número)?\s*[:\s]*([A-Z0-9-]+)',
    r'(?:FV|FE|FA|FC)[:\s-]*(\d+)',
    r'(?:^|\s)(?:No\.?|Nro\.?|#)\s*([A-Z0-9-]+)',
    r'Número\s*(?:de\s*)?Factura[:\s]*([A-Z0-9-]+)',
    r'Invoice\s*(?:No\.?|Number)?[:\s]*([A-Z0-9-]+)',
]

# Validar longitud
if 2 <= len(number) <= 50:
    info['invoice_number'] = number.upper()
```

### 4. Extracción de NIT MEJORADA ✅

**Patrón adicional sin prefijo:**
```python
nit_patterns = [
    r'NIT[:\s]*(\d{3}\.?\d{3}\.?\d{3}[-\s]?\d)',
    r'N\.?I\.?T\.?[:\s]*(\d{9,12}[-\s]?\d?)',
    r'(?:^|\s)(\d{9,10})(?:\s|$)',  # NIT sin prefijo "NIT:"
]

# Validar longitud
if 9 <= len(nit) <= 12:
    info['supplier_nit'] = nit[:10]
```

### 5. Extracción de Total AGREGADA ✅

**Nueva funcionalidad:**
```python
total_patterns = [
    r'Total\s*(?:a\s*Pagar|Factura)?[:\s]*\$?\s*([\d,\.]+)',
    r'Valor\s*Total[:\s]*\$?\s*([\d,\.]+)',
    r'Total[:\s]*\$?\s*([\d,\.]+)',
]

# Validar rango razonable
if 100 <= total <= 999999999:
    info['total_amount'] = total
```

### 6. Logging Mejorado ✅

```python
logger.info(f"Información extraída: Proveedor={info['supplier_name']}, Fecha={info['invoice_date']}, Número={info['invoice_number']}")
```

## Script de Reprocesamiento

Se creó `reprocesar_facturas_supplier.py` para:
1. Leer todas las facturas existentes
2. Buscar sus PDFs
3. Re-extraer la información con el nuevo método
4. Actualizar solo los campos que cambiaron
5. Mostrar reporte detallado

### Uso:
```bash
cd CODE
python ../reprocesar_facturas_supplier.py
```

## Resultados Esperados

### Antes:
```
Proveedor: Sin proveedor
Fecha: N/A
Número: N/A
```

### Después:
```
Proveedor: COMERCIALIZADORA EL GOLAZO SAS
Fecha: 30/08/2025
Número: 7GF-125
```

## Casos de Prueba

### Factura 1: COMERCIALIZADORA EL GOLAZO SAS
- ✅ Proveedor extraído de primeras líneas
- ✅ Fecha parseada correctamente
- ✅ Número "7GF-125" capturado
- ✅ CUFE extraído

### Factura 2: ALOMOBILE CTG
- ✅ Proveedor extraído
- ✅ Fecha parseada
- ✅ Número "30631" capturado
- ⚠️ Sin CUFE (correcto)

### Factura 3: COMERCIALIZADORA RACOPI S.A.S.
- ✅ Proveedor extraído
- ✅ Fecha "2025-11-11" parseada
- ✅ Número "FE-30188" capturado
- ✅ CUFE extraído

## Archivos Modificados

1. `CODE/src/app/services/supplier_invoice_service.py`
   - Método `extract_basic_info_from_pdf()` completamente reescrito
   - Extracción más robusta y precisa
   - Mejor manejo de casos edge
   - Validaciones de datos
   - Logging mejorado

2. `reprocesar_facturas_supplier.py` (NUEVO)
   - Script para reprocesar facturas existentes
   - Actualiza datos sin perder información
   - Reporte detallado de cambios

## Próximos Pasos

1. ✅ Desplegar cambios al servidor
2. ✅ Ejecutar script de reprocesamiento
3. ✅ Verificar que las facturas muestren datos correctos
4. ✅ Probar con nuevas facturas subidas

## Comandos de Deploy

```bash
# 1. Desplegar código
./deploy.sh papyrus

# 2. Conectar al servidor y ejecutar reprocesamiento
ssh usuario@servidor
cd /ruta/proyecto
docker exec -it papyrus_web python /app/reprocesar_facturas_supplier.py

# 3. Verificar resultados en /invoices
```

## Notas Importantes

- El script NO elimina datos existentes, solo actualiza
- Si un campo ya tiene valor y no se encuentra nuevo, se mantiene el original
- Los PDFs deben estar en `/app/src/uploads/supplier-invoices/` o `/app/src/uploads/invoices/`
- El script es seguro de ejecutar múltiples veces
