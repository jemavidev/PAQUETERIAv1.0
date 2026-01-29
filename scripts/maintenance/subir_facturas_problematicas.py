#!/usr/bin/env python3
"""
Script para subir las facturas problemáticas al servidor staging
permitiendo múltiples archivos con el mismo CUFE
"""

import sys
import os
import hashlib
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.models.invoice import SupplierInvoice, SupplierInvoiceStatus
from app.services.s3_storage_service import S3StorageService
from datetime import datetime


def calcular_hash(filepath):
    """Calcula el hash SHA256 del archivo"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def subir_factura_manual(pdf_path: str, descripcion: str = None):
    """
    Sube una factura manualmente al sistema, permitiendo duplicados de CUFE
    """
    if not os.path.exists(pdf_path):
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return None
    
    filename = os.path.basename(pdf_path)
    file_hash = calcular_hash(pdf_path)
    
    print(f"\n{'='*80}")
    print(f"📤 Subiendo: {filename}")
    if descripcion:
        print(f"   Descripción: {descripcion}")
    print(f"   Hash: {file_hash}")
    print(f"{'='*80}")
    
    db = SessionLocal()
    
    try:
        # Verificar si ya existe por hash
        existing = db.query(SupplierInvoice).filter(
            SupplierInvoice.original_file_hash == file_hash
        ).first()
        
        if existing:
            print(f"⚠️  Este archivo ya existe en la base de datos:")
            print(f"   ID: {existing.id}")
            print(f"   Nombre: {existing.original_filename}")
            print(f"   Status: {existing.status.value}")
            print(f"   CUFE: {existing.cufe or 'NO EXTRAÍDO'}")
            
            respuesta = input("\n¿Deseas continuar de todas formas? (s/n): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada")
                return None
        
        # Extraer CUFE del contenido
        print("\n🔍 Extrayendo información del PDF...")
        
        try:
            import PyPDF2
            from PyPDF2 import PdfReader
            import re
            
            cufe = None
            texto_completo = ""
            
            with open(pdf_path, 'rb') as file:
                pdf = PdfReader(file)
                for page in pdf.pages:
                    try:
                        texto = page.extract_text()
                        texto_completo += texto + "\n"
                    except:
                        pass
            
            # Buscar CUFE
            pattern = r'([a-f0-9]{96})'
            matches = re.findall(pattern, texto_completo, re.IGNORECASE)
            if matches:
                cufe = matches[0].lower()
                print(f"   ✅ CUFE encontrado: {cufe[:20]}...{cufe[-20:]}")
            else:
                print(f"   ⚠️  No se encontró CUFE en el contenido")
            
            # Buscar NIT
            nit = None
            nit_match = re.search(r'NIT[:\s]*([0-9\-]+)', texto_completo, re.IGNORECASE)
            if nit_match:
                nit = re.sub(r'[^\d]', '', nit_match.group(1))[:10]
                print(f"   ✅ NIT encontrado: {nit}")
            
            # Buscar proveedor
            proveedor = None
            proveedor_patterns = [
                r'Razón\s+Social[:\s]*([^\n]+)',
                r'Nombre[:\s]*([^\n]+)',
            ]
            for pattern in proveedor_patterns:
                match = re.search(pattern, texto_completo, re.IGNORECASE)
                if match:
                    proveedor = match.group(1).strip()[:255]
                    if len(proveedor) > 3:
                        print(f"   ✅ Proveedor: {proveedor}")
                        break
            
            # Buscar número de factura
            numero = None
            numero_patterns = [
                r'Factura\s+(?:No\.?|Número)[:\s]*([A-Z0-9\-]+)',
                r'No\.\s+([A-Z0-9\-]+)',
            ]
            for pattern in numero_patterns:
                match = re.search(pattern, texto_completo, re.IGNORECASE)
                if match:
                    numero = match.group(1).strip()[:50]
                    print(f"   ✅ Número: {numero}")
                    break
            
        except Exception as e:
            print(f"   ⚠️  Error extrayendo información: {e}")
            cufe = None
            nit = None
            proveedor = None
            numero = None
        
        # Verificar si el CUFE ya existe
        if cufe:
            existing_cufe = db.query(SupplierInvoice).filter(
                SupplierInvoice.cufe == cufe
            ).all()
            
            if existing_cufe:
                print(f"\n⚠️  ADVERTENCIA: Ya existen {len(existing_cufe)} archivo(s) con este CUFE:")
                for ex in existing_cufe:
                    print(f"   - ID {ex.id}: {ex.original_filename} ({ex.status.value})")
                print(f"\n   Esto es NORMAL si tienes:")
                print(f"   1. La factura del proveedor")
                print(f"   2. El archivo CUFE de la DIAN")
                
                respuesta = input("\n¿Deseas continuar y crear un registro adicional? (s/n): ")
                if respuesta.lower() != 's':
                    print("❌ Operación cancelada")
                    return None
        
        # Subir a S3
        print(f"\n☁️  Subiendo archivo a S3...")
        s3 = S3StorageService()
        
        if s3.is_enabled():
            with open(pdf_path, 'rb') as f:
                content = f.read()
            
            s3_path = s3.upload_pdf(content, file_hash, prefix="supplier-invoices")
            if s3_path:
                print(f"   ✅ Archivo subido a S3: {s3_path}")
            else:
                print(f"   ⚠️  No se pudo subir a S3, continuando...")
                s3_path = None
        else:
            print(f"   ⚠️  S3 no está habilitado")
            s3_path = None
        
        # Crear registro en la base de datos
        print(f"\n💾 Creando registro en la base de datos...")
        
        status = SupplierInvoiceStatus.CUFE_EXTRACTED if cufe else SupplierInvoiceStatus.NO_CUFE
        
        supplier_invoice = SupplierInvoice(
            original_filename=filename,
            original_file_hash=file_hash,
            original_file_path=s3_path,
            supplier_name=proveedor,
            supplier_nit=nit,
            invoice_number=numero,
            cufe=cufe,
            cufe_source='content' if cufe else None,
            status=status,
            notes=descripcion,
            uploaded_at=datetime.now(),
        )
        
        db.add(supplier_invoice)
        db.commit()
        db.refresh(supplier_invoice)
        
        print(f"\n✅ Factura subida exitosamente!")
        print(f"   ID: {supplier_invoice.id}")
        print(f"   Status: {supplier_invoice.status.value}")
        print(f"   CUFE: {supplier_invoice.cufe or 'NO EXTRAÍDO'}")
        
        return supplier_invoice
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return None
    finally:
        db.close()


def main():
    print("\n" + "="*80)
    print("SUBIR FACTURAS PROBLEMÁTICAS AL SISTEMA")
    print("="*80)
    
    facturas = [
        {
            'path': 'f669005ad5338a8701edd82c08a9afa1499788b9fa606d5c0d68ba872e80a6877a3988a17522e186ebc269c3aaaf2f6c.pdf',
            'descripcion': 'Factura original del proveedor PAPELERIA FUTURO CARTAGENA - PF-91385'
        },
        {
            'path': 'ad09002788230002692476616.pdf',
            'descripcion': 'Archivo CUFE descargado de la DIAN - PF-91385'
        }
    ]
    
    resultados = []
    
    for factura in facturas:
        resultado = subir_factura_manual(factura['path'], factura['descripcion'])
        resultados.append({
            'path': factura['path'],
            'success': resultado is not None,
            'id': resultado.id if resultado else None
        })
        
        if resultado:
            print(f"\n✅ {factura['path']} subida correctamente (ID: {resultado.id})")
        else:
            print(f"\n❌ {factura['path']} NO se pudo subir")
    
    print("\n" + "="*80)
    print("RESUMEN")
    print("="*80)
    
    exitosas = sum(1 for r in resultados if r['success'])
    print(f"✅ Facturas subidas: {exitosas}/{len(facturas)}")
    
    for r in resultados:
        status = "✅" if r['success'] else "❌"
        id_str = f"(ID: {r['id']})" if r['id'] else ""
        print(f"{status} {r['path']} {id_str}")


if __name__ == "__main__":
    main()
