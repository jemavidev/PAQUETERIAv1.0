# S3 Cleanup Guide - Orphaned DIAN Files

## Problem

After deleting invoices from the CUFE view, the files still remain in AWS S3 at `invoices/dian/`. This happens because:

1. The invoices were deleted from the database
2. The S3 deletion might have failed silently
3. Or the files were uploaded before the delete functionality was properly implemented

## Current Situation

- **Database**: Empty (all invoices deleted)
- **S3 Bucket**: `elclub-paqueteria`
- **S3 Path**: `invoices/dian/`
- **Files**: 19 PDF files (orphaned - no database records)

## Solutions

I've created two scripts to help you clean up:

### Option 1: Delete Only Orphaned Files (Recommended)

This script is **SAFE** - it only deletes files that don't have a corresponding database record.

**Script**: `cleanup_orphaned_s3_files.py`

**What it does**:
1. Lists all files in `invoices/dian/` on S3
2. Gets all CUFEs from the database
3. Identifies files that don't have a database record (orphaned)
4. Shows you which files will be deleted
5. Asks for confirmation
6. Deletes only the orphaned files

**How to run**:
```bash
# Make sure you're in the project root
cd /path/to/PAQUETEX

# Set AWS credentials (if not already in .env)
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_S3_BUCKET_NAME="elclub-paqueteria"
export AWS_REGION="us-east-1"

# Run the script
CODE/.venv/bin/python3 cleanup_orphaned_s3_files.py
```

**Example output**:
```
🧹 LIMPIEZA DE ARCHIVOS DIAN HUÉRFANOS EN S3
================================================================================

📦 Bucket: elclub-paqueteria
📁 Prefix: invoices/dian/

🔍 Listando archivos DIAN en S3...
   Encontrados: 19 archivos en S3

🔍 Obteniendo CUFEs de la base de datos...
   Encontrados: 0 registros en BD

🔍 Identificando archivos huérfanos...
   Archivos huérfanos: 19

📋 ARCHIVOS HUÉRFANOS ENCONTRADOS:
   1. CUFE: 03391745b16d6324...
   2. CUFE: 11923ccd02f0b975...
   ...

⚠️  ADVERTENCIA: Se eliminarán 19 archivos de S3
   Estos archivos no tienen registro en la base de datos

¿Deseas continuar? (si/no): si

🗑️  ELIMINANDO ARCHIVOS HUÉRFANOS...
[1/19] 03391745b16d6324... ✅ Eliminado
[2/19] 11923ccd02f0b975... ✅ Eliminado
...

📊 RESUMEN DE LA LIMPIEZA
   Total archivos en S3:     19
   Archivos huérfanos:       19
   ✅ Eliminados:            19
   ❌ Fallidos:              0
```

### Option 2: Delete ALL DIAN Files (Nuclear Option)

This script is **DANGEROUS** - it deletes ALL files in `invoices/dian/` regardless of database records.

**Script**: `delete_all_dian_s3_files.py`

**What it does**:
1. Lists all files in `invoices/dian/`
2. Shows you what will be deleted
3. Requires you to type "ELIMINAR TODO" to confirm
4. Deletes ALL files in batches of 1000

**When to use**:
- When you want to start completely fresh
- When you're sure you don't need any DIAN files
- When you've already backed up important files

**How to run**:
```bash
# Make sure you're in the project root
cd /path/to/PAQUETEX

# Set AWS credentials (if not already in .env)
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_S3_BUCKET_NAME="elclub-paqueteria"
export AWS_REGION="us-east-1"

# Run the script
CODE/.venv/bin/python3 delete_all_dian_s3_files.py
```

**Example output**:
```
🗑️  ELIMINAR TODOS LOS ARCHIVOS DIAN DE S3
================================================================================

📦 Bucket: elclub-paqueteria
📁 Prefix: invoices/dian/

🔍 Listando archivos DIAN en S3...
   Encontrados: 19 archivos

📋 ARCHIVOS A ELIMINAR (primeros 10):
   1. 03391745b16d6324... (invoices/dian/03391745b16d6324d08bb833cbc3f4e531e7c97ee726fc2a962b0c043143d19de8101eb991a1236376eda6a9e0664a13.pdf)
   ...

⚠️  ADVERTENCIA CRÍTICA:
   Se eliminarán TODOS los 19 archivos DIAN de S3
   Esta acción NO se puede deshacer
   Los archivos se perderán permanentemente

¿Estás ABSOLUTAMENTE SEGURO? Escribe 'ELIMINAR TODO' para confirmar: ELIMINAR TODO

🗑️  ELIMINANDO ARCHIVOS...
   Lote 1: 19 archivos eliminados

📊 RESUMEN DE LA ELIMINACIÓN
   Total archivos:    19
   ✅ Eliminados:     19
   ❌ Fallidos:       0
```

## Recommendation

Since your database is empty (you deleted all invoices), I recommend using **Option 2** (delete all) because:

1. All 19 files are orphaned (no database records)
2. It's faster (batch deletion)
3. You're starting fresh anyway

However, if you want to be extra safe, use **Option 1** first to verify which files are orphaned.

## Why Did This Happen?

The delete functionality in the code is correct:

```python
# CODE/src/app/services/invoice_v2_service.py
def delete_invoice(self, cufe: str) -> bool:
    invoice = self.get_invoice_by_cufe(cufe)
    if not invoice:
        return False
    
    # Delete S3 files
    if invoice.archivo_proveedor_s3_key and self.s3_service:
        self.s3_service.delete_file(invoice.archivo_proveedor_s3_key)
    
    if invoice.archivo_dian_s3_key and self.s3_service:
        self.s3_service.delete_file(invoice.archivo_dian_s3_key)
    
    # Delete from database
    self.db.delete(invoice)
    self.db.commit()
```

Possible reasons for orphaned files:
1. **S3 credentials issue**: The S3 service might not have been properly configured when you deleted
2. **Silent failures**: The delete_file() calls are wrapped in try-except that only logs warnings
3. **Database inconsistency**: The `archivo_dian_s3_key` field might have been NULL or incorrect
4. **Timing**: Files were uploaded but the database records were deleted before S3 cleanup

## Prevention

To prevent this in the future, the code should:
1. ✅ Already implemented: Try to delete S3 files before database deletion
2. ✅ Already implemented: Log warnings if S3 deletion fails
3. ⚠️ Could improve: Make S3 deletion mandatory (fail the whole operation if S3 fails)
4. ⚠️ Could improve: Add a cleanup job that runs periodically to find orphaned files

## After Cleanup

After running either script, verify the cleanup:

```bash
# Check S3 bucket
aws s3 ls s3://elclub-paqueteria/invoices/dian/ --recursive

# Should show: (empty) or no output
```

Or check in the AWS Console:
- Go to S3 → elclub-paqueteria → invoices → dian/
- Should be empty

## Need Help?

If you encounter any issues:
1. Check AWS credentials are correct
2. Check you have delete permissions on the S3 bucket
3. Check the bucket name is correct: `elclub-paqueteria`
4. Check the region is correct: `us-east-1`
