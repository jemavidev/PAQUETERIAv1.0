#!/usr/bin/env python3
"""
Script para verificar los CUFEs en la base de datos
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE/src'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.invoice_v2 import InvoiceV2

def check_cufes():
    """Verifica los CUFEs problemáticos en la BD"""
    
    cufes = [
        "fd7892b8723009bb46c2f065caa325144d76ee5e3eada87cf2dce405dc23b0b4e5938e060c94fa4c3f846220c56dc4e1",
        "dce84f5f446f8c609791c431e785b550a2d63cd81fa2ccd4f429ac8c3a7ba442b7137b4727dbcfb151862e7ad9f5b1ce",
        "b95d05e6ff51cbaf53e1510b1d213af6a0ec838d1e4420e708b99e9c723c984926586ce3a64de8d5a621b2eeea9ec051",
        "5602488e173b5caa1c07c03d621c590fe6449ddb0c344f875f1dc4e82433b9bed4b2c22f0be10c5c092beba63ef70b8e",
        "89d9a6f4dbef0dfb72f3ae4d6e53cd90613384dbf38b47805437e06ca807484bacf272069d4e0223de55a99a8f6354c9",
    ]
    
    db = SessionLocal()
    
    try:
        print(f"\n{'='*80}")
        print(f"🔍 VERIFICANDO CUFEs EN LA BASE DE DATOS")
        print(f"{'='*80}\n")
        
        for cufe in cufes:
            cufe_corto = cufe[:16]
            factura = db.query(InvoiceV2).filter_by(cufe=cufe).first()
            
            if factura:
                print(f"✅ {cufe_corto}...")
                print(f"   Total DIAN: ${factura.dian_total_neto or 0:,.2f}")
                print(f"   Archivo DIAN S3: {factura.archivo_dian_s3_key or 'No tiene'}")
                print(f"   Estado DIAN: {factura.dian_validado}")
                print()
            else:
                print(f"❌ {cufe_corto}... - NO ENCONTRADO EN BD")
                print()
        
        print(f"{'='*80}\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_cufes()
