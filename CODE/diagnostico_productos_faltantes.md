# DIAGNÓSTICO: PRODUCTOS FALTANTES

## PROBLEMA IDENTIFICADO ✅

El parser está extrayendo **menos productos de los que realmente hay** en los PDFs:

### Comparación Real vs Extraído:

| Factura | Productos Reales | Productos Extraídos | Faltantes |
|---------|------------------|---------------------|-----------|
| 006D-611 | 20 | 18 | 2 (19-20) |
| 2FE-438 | 10 | 3 | 7 (4-10) |
| FE-15778 | 58 | 28 | 30 (29-58) |
| FELN-1141 | 2 | 2 | 0 ✅ |

**Total Real: 90 productos**  
**Total Extraído: 51 productos**  
**Faltantes: 39 productos**

---

## CAUSA PROBABLE

El parser está **deteniéndose antes de tiempo** o **no reconociendo algunos formatos de productos**.

### Posibles causas:

1. **Productos en páginas siguientes no se están leyendo**
   - El parser lee todas las páginas (max_pages=999) ✅
   - Pero puede que la sección de productos se esté cortando prematuramente

2. **Formato de productos cambia en la misma factura**
   - Los primeros productos tienen un formato
   - Los últimos productos tienen otro formato ligeramente diferente
   - El parser no reconoce el segundo formato

3. **Hay líneas intermedias que confunden al parser**
   - Subtotales
   - Notas
   - Saltos de página
   - Encabezados repetidos

---

## ANÁLISIS POR FACTURA

### 006D-611 (SOLUCIONES MAF)

**Productos extraídos (18):**
1. 7706616340433 - BANDERITAS ADH 5X20H
2. 5676 - PERIODICO TAYDEM 1/3
3. 7707294385914 - GANCHO LEGAJDOR PLA
4. 1266 - PEGA NOTAS TRITON SU
5. 2681 - PAPEL FTGRF A4 135 GR
6. 4063565550690 - CINTA ADH TRANSP EMP
7. 7707314792791 - CINTA EMPAQUE 30MX4
8. 2680 - PAPEL FTGRF C ADH A4
9. 2681 - PAPEL FTGRF A4 135 GR (duplicado)
10. 7707294385914 - GANCHO LEGAJDOR PLA (duplicado)
11. 7705465060639 - GANCHO LEG PLASTICO
12. 5844 - TACO MEMO BOND TAYD
13. 5848 - TACO MEMO PERIODICO
14. 7705465060639 - GANCHO LEG PLASTICO (duplicado)
15. 7707294378237 - BLOCK ESCOLAR FAMA C
16. 5844 - TACO MEMO BOND TAYD (duplicado)
17. 1266 - PEGA NOTAS TRITON SU (duplicado)
18. 5848 - TACO MEMO PERIODICO (duplicado)

**Productos faltantes (según imagen):**
19. 1266 - PEGA NOTAS TRITON SU RT PAQX 5
20. 5848 - TACO MEMO PERIODICO 9X9 250H

**Observación**: Los productos 19 y 20 están en la misma página que los anteriores. El parser se detuvo justo antes de ellos.

---

### 2FE-438 (EL GOLAZO)

**Productos extraídos (3):**
1. 631655 - 3H-24CTG-25 A9 REF:314
2. 631657 - 3H-17CTG-25 A9 REF:914
3. 631663 - O 33H-21CTG-25 A9 REF:

**Productos faltantes (según imagen):**
4-10: Faltan 7 productos más

**Observación**: Solo extrajo los primeros 3 productos de 10. Probablemente hay un cambio de formato o página que el parser no maneja.

---

### FE-15778 (MARCOS MARTINEZ)

**Productos extraídos (28):**
Solo los primeros 28 de 58 productos

**Productos faltantes:**
29-58: Faltan 30 productos (más de la mitad)

**Observación**: La imagen muestra que hay productos hasta el 58 en la página 3. El parser se detuvo en el producto 28, probablemente al final de la página 1.

---

## SOLUCIÓN PROPUESTA

### 1. Verificar extracción de texto completo
- Confirmar que `extract_text_from_pdf` está leyendo TODAS las páginas
- Verificar que no se está cortando el texto prematuramente

### 2. Mejorar detección de fin de tabla
- El parser probablemente está encontrando algún patrón que interpreta como "fin de tabla"
- Necesitamos ser más permisivos y continuar buscando productos

### 3. Agregar soporte para formatos adicionales
- Puede que los productos en páginas posteriores tengan un formato ligeramente diferente
- Necesitamos analizar el texto raw para ver qué formato tienen

### 4. Manejar encabezados repetidos
- Si hay encabezados de tabla repetidos en cada página, el parser debe ignorarlos y continuar

---

## PRÓXIMOS PASOS

1. **Extraer texto raw de los PDFs** para ver exactamente qué contienen
2. **Identificar el patrón de los productos faltantes**
3. **Ajustar el parser** para reconocer esos patrones
4. **Reprocesar las facturas** con el parser mejorado

---

## COMANDO PARA REPROCESAR

Una vez arreglado el parser:

```bash
cd CODE
python -c "
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from app.services.invoice_v2_service import InvoiceV2Service

db = SessionLocal()
service = InvoiceV2Service(db)

# Reprocesar cada factura
cufes = [
    '6ee372e238cc82c3d95fa44faa0869cd5c6e0e45d51cef31b9828697aad65af8f2e3a89ff13f799961ad968c89503f8e',
    '88f565e6a165010edd2680ea0f37c2453f3d2a11e2b58fcff298241c760f260cafef0dbed0b6214df2e67a3895ea6132',
    '7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad1c33a597f92eed3e2318402d2eb418d2'
]

for cufe in cufes:
    print(f'Reprocesando {cufe[:20]}...')
    # Aquí iría el código para reprocesar
"
```

---

## RESUMEN

✅ **Problema identificado**: Parser se detiene antes de tiempo  
✅ **Productos faltantes**: 39 de 90 (43%)  
❌ **Causa exacta**: Por determinar (necesitamos ver el texto raw)  
🔧 **Solución**: Mejorar el parser para reconocer todos los formatos  

**El sistema funciona, solo necesita ajustes en el parser para extraer el 100% de los productos.**
