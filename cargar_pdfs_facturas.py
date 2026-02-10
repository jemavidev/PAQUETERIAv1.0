#!/usr/bin/env python3
"""
Script para cargar todos los PDFs de CUFE-XML en el tab de Facturas
"""
import os
import sys
import requests
from pathlib import Path
import time

# Configuración
PDF_DIR = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML"
API_URL = "http://localhost:8000/api/v2/invoices/facturas/upload"
LOGIN_URL = "http://localhost:8000/auth/login"

# Sesión para mantener cookies
session = requests.Session()

def login():
    """Intenta hacer login en el sistema"""
    print("\n🔐 Autenticación requerida")
    
    # Intentar con credenciales por defecto o solicitar
    username = input("Usuario: ").strip()
    password = input("Contraseña: ").strip()
    
    try:
        response = session.post(
            LOGIN_URL,
            data={'username': username, 'password': password},
            timeout=10
        )
        
        if response.status_code == 200 or 'redirect' in response.text.lower():
            print("✅ Login exitoso")
            return True
        else:
            print(f"❌ Login fallido: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False


def cargar_pdfs():
    """Carga todos los PDFs en el sistema"""
    
    # Obtener lista de PDFs
    pdf_files = sorted([f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')])
    
    if not pdf_files:
        print("❌ No se encontraron archivos PDF")
        return
    
    print(f"📄 Encontrados {len(pdf_files)} archivos PDF")
    print(f"📁 Directorio: {PDF_DIR}")
    print(f"🌐 API: {API_URL}")
    print("\n" + "="*60)
    
    # Contadores
    exitosos = 0
    fallidos = 0
    errores = []
    
    # Procesar cada PDF
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        
        print(f"\n[{i}/{len(pdf_files)}] Procesando: {pdf_file}")
        
        try:
            # Abrir archivo
            with open(pdf_path, 'rb') as f:
                files = {'file': (pdf_file, f, 'application/pdf')}
                
                # Hacer request con sesión autenticada
                response = session.post(API_URL, files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    cufe = data.get('cufe', 'N/A')[:20]
                    proveedor = data.get('proveedor_nombre', 'N/A')
                    print(f"   ✅ Cargado exitosamente")
                    print(f"   📋 CUFE: {cufe}...")
                    print(f"   🏢 Proveedor: {proveedor}")
                    exitosos += 1
                else:
                    error_msg = response.json().get('detail', 'Error desconocido')
                    print(f"   ❌ Error: {error_msg}")
                    errores.append(f"{pdf_file}: {error_msg}")
                    fallidos += 1
                    
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout - El archivo tardó demasiado")
            errores.append(f"{pdf_file}: Timeout")
            fallidos += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            errores.append(f"{pdf_file}: {str(e)}")
            fallidos += 1
        
        # Pequeña pausa para no saturar el servidor
        if i < len(pdf_files):
            time.sleep(0.5)
    
    # Resumen final
    print("\n" + "="*60)
    print("\n📊 RESUMEN DE CARGA")
    print(f"   Total archivos: {len(pdf_files)}")
    print(f"   ✅ Exitosos: {exitosos}")
    print(f"   ❌ Fallidos: {fallidos}")
    print(f"   📈 Tasa de éxito: {(exitosos/len(pdf_files)*100):.1f}%")
    
    if errores:
        print(f"\n⚠️  ERRORES ENCONTRADOS ({len(errores)}):")
        for error in errores[:10]:  # Mostrar solo los primeros 10
            print(f"   - {error}")
        if len(errores) > 10:
            print(f"   ... y {len(errores) - 10} errores más")
    
    print("\n✅ Proceso completado")

if __name__ == "__main__":
    print("="*60)
    print("CARGA MASIVA DE PDFs - TAB FACTURAS")
    print("="*60)
    
    # Verificar que el directorio existe
    if not os.path.exists(PDF_DIR):
        print(f"❌ Error: El directorio no existe: {PDF_DIR}")
        sys.exit(1)
    
    # Verificar que el servidor está corriendo
    try:
        response = session.get("http://localhost:8000/", timeout=5)
        if response.status_code in [200, 302, 307]:
            print("✅ Servidor conectado")
        else:
            print("⚠️  Advertencia: El servidor respondió con código", response.status_code)
    except:
        print("❌ Error: No se puede conectar al servidor en http://localhost:8000")
        print("   Asegúrate de que el servidor esté corriendo")
        sys.exit(1)
    
    # Intentar login
    if not login():
        print("❌ No se pudo autenticar. Abortando.")
        sys.exit(1)
    
    # Confirmar antes de proceder
    print(f"\n⚠️  Se cargarán 183 archivos PDF")
    respuesta = input("¿Deseas continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        sys.exit(0)
    
    # Ejecutar carga
    cargar_pdfs()
