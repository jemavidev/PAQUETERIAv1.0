#!/usr/bin/env python3
"""
Script automático para cargar PDFs (sin interacción)
Uso: python3 cargar_pdfs_auto.py <usuario> <contraseña>
"""
import os
import sys
import requests
import time

# Configuración
PDF_DIR = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML"
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v2/invoices/facturas/upload"

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 cargar_pdfs_auto.py <usuario> <contraseña>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print("="*60)
    print("CARGA MASIVA DE PDFs - TAB FACTURAS")
    print("="*60)
    
    # Crear sesión
    session = requests.Session()
    
    # Login
    print("\n🔄 Autenticando...")
    try:
        response = session.post(
            f"{BASE_URL}/auth/login",
            data={'username': username, 'password': password},
            allow_redirects=True,
            timeout=10
        )
        
        # Verificar autenticación
        test = session.get(f"{BASE_URL}/invoices/facturas", timeout=5)
        if 'login' in test.url.lower():
            print("❌ Error: Credenciales incorrectas")
            sys.exit(1)
        
        print("✅ Autenticado correctamente")
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        sys.exit(1)
    
    # Obtener PDFs
    pdf_files = sorted([f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')])
    
    if not pdf_files:
        print("❌ No se encontraron archivos PDF")
        sys.exit(1)
    
    print(f"\n📄 Encontrados {len(pdf_files)} archivos PDF")
    print("="*60)
    
    # Contadores
    exitosos = 0
    fallidos = 0
    errores = []
    
    # Procesar cada PDF
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        
        print(f"\n[{i}/{len(pdf_files)}] {pdf_file}")
        
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': (pdf_file, f, 'application/pdf')}
                response = session.post(API_URL, files=files, timeout=35)
                
                if response.status_code == 200:
                    data = response.json()
                    cufe = data.get('cufe', 'N/A')[:20]
                    proveedor = data.get('proveedor_nombre', 'N/A')
                    
                    print(f"   ✅ OK - CUFE: {cufe}... - {proveedor}")
                    exitosos += 1
                else:
                    try:
                        error = response.json().get('detail', f'HTTP {response.status_code}')
                    except:
                        error = f'HTTP {response.status_code}'
                    
                    print(f"   ❌ Error: {error}")
                    errores.append(f"{pdf_file}: {error}")
                    fallidos += 1
                    
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout")
            errores.append(f"{pdf_file}: Timeout")
            fallidos += 1
            
        except Exception as e:
            print(f"   ❌ {str(e)}")
            errores.append(f"{pdf_file}: {str(e)}")
            fallidos += 1
        
        # Pausa
        if i < len(pdf_files):
            time.sleep(0.3)
    
    # Resumen
    print("\n" + "="*60)
    print("\n📊 RESUMEN")
    print(f"   Total: {len(pdf_files)}")
    print(f"   ✅ Exitosos: {exitosos}")
    print(f"   ❌ Fallidos: {fallidos}")
    
    if len(pdf_files) > 0:
        tasa = (exitosos / len(pdf_files)) * 100
        print(f"   📈 Tasa de éxito: {tasa:.1f}%")
    
    if errores and len(errores) <= 10:
        print(f"\n⚠️  Errores:")
        for error in errores:
            print(f"   - {error}")
    elif errores:
        print(f"\n⚠️  {len(errores)} errores (ver log completo)")
    
    print("\n✅ Completado")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por usuario")
        sys.exit(0)
