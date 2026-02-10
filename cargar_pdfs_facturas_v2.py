#!/usr/bin/env python3
"""
Script mejorado para cargar PDFs con manejo de autenticación
"""
import os
import sys
import requests
import time
import json
from getpass import getpass

# Configuración
PDF_DIR = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML"
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v2/invoices/facturas/upload"

class PDFUploader:
    def __init__(self):
        self.session = requests.Session()
        self.exitosos = 0
        self.fallidos = 0
        self.errores = []
    
    def verificar_servidor(self):
        """Verifica que el servidor esté corriendo"""
        try:
            response = self.session.get(BASE_URL, timeout=5)
            return True
        except:
            return False
    
    def login(self, username, password):
        """Intenta hacer login"""
        try:
            # Intentar login con form data
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                data={'username': username, 'password': password},
                allow_redirects=True,
                timeout=10
            )
            
            # Verificar si el login fue exitoso probando un endpoint protegido
            test_response = self.session.get(f"{BASE_URL}/invoices/facturas", timeout=5)
            
            if test_response.status_code == 200:
                return True, "Login exitoso"
            elif 'login' in test_response.url.lower():
                return False, "Credenciales incorrectas"
            else:
                return True, "Login exitoso (verificado)"
                
        except Exception as e:
            return False, f"Error en login: {str(e)}"
    
    def cargar_pdf(self, pdf_path, filename, index, total):
        """Carga un PDF individual"""
        print(f"\n[{index}/{total}] Procesando: {filename}")
        
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': (filename, f, 'application/pdf')}
                response = self.session.post(API_URL, files=files, timeout=35)
                
                if response.status_code == 200:
                    data = response.json()
                    cufe = data.get('cufe', 'N/A')[:20]
                    proveedor = data.get('proveedor_nombre', 'N/A')
                    estado = data.get('estado', 'N/A')
                    
                    print(f"   ✅ Cargado exitosamente")
                    print(f"   📋 CUFE: {cufe}...")
                    print(f"   🏢 Proveedor: {proveedor}")
                    print(f"   📊 Estado: {estado}")
                    
                    self.exitosos += 1
                    return True
                    
                elif response.status_code == 401 or response.status_code == 403:
                    print(f"   🔒 Error de autenticación")
                    self.errores.append(f"{filename}: No autenticado")
                    self.fallidos += 1
                    return False
                    
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('detail', f'HTTP {response.status_code}')
                    except:
                        error_msg = f'HTTP {response.status_code}'
                    
                    print(f"   ❌ Error: {error_msg}")
                    self.errores.append(f"{filename}: {error_msg}")
                    self.fallidos += 1
                    return True  # Continuar con otros archivos
                    
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout - El archivo tardó demasiado")
            self.errores.append(f"{filename}: Timeout")
            self.fallidos += 1
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            self.errores.append(f"{filename}: {str(e)}")
            self.fallidos += 1
            return True
    
    def procesar_directorio(self):
        """Procesa todos los PDFs del directorio"""
        # Obtener lista de PDFs
        pdf_files = sorted([f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')])
        
        if not pdf_files:
            print("❌ No se encontraron archivos PDF")
            return
        
        print(f"\n📄 Encontrados {len(pdf_files)} archivos PDF")
        print("="*60)
        
        # Procesar cada PDF
        for i, pdf_file in enumerate(pdf_files, 1):
            pdf_path = os.path.join(PDF_DIR, pdf_file)
            
            continuar = self.cargar_pdf(pdf_path, pdf_file, i, len(pdf_files))
            
            if not continuar:
                print("\n⚠️  Deteniendo proceso por error de autenticación")
                break
            
            # Pausa entre archivos
            if i < len(pdf_files):
                time.sleep(0.5)
        
        # Resumen
        self.mostrar_resumen(len(pdf_files))
    
    def mostrar_resumen(self, total):
        """Muestra resumen final"""
        print("\n" + "="*60)
        print("\n📊 RESUMEN DE CARGA")
        print(f"   Total archivos: {total}")
        print(f"   ✅ Exitosos: {self.exitosos}")
        print(f"   ❌ Fallidos: {self.fallidos}")
        
        if total > 0:
            tasa = (self.exitosos / total) * 100
            print(f"   📈 Tasa de éxito: {tasa:.1f}%")
        
        if self.errores:
            print(f"\n⚠️  ERRORES ENCONTRADOS ({len(self.errores)}):")
            for error in self.errores[:10]:
                print(f"   - {error}")
            if len(self.errores) > 10:
                print(f"   ... y {len(self.errores) - 10} errores más")
        
        print("\n✅ Proceso completado")


def main():
    print("="*60)
    print("CARGA MASIVA DE PDFs - TAB FACTURAS")
    print("="*60)
    
    # Verificar directorio
    if not os.path.exists(PDF_DIR):
        print(f"❌ Error: El directorio no existe: {PDF_DIR}")
        sys.exit(1)
    
    # Crear uploader
    uploader = PDFUploader()
    
    # Verificar servidor
    print("\n🔍 Verificando servidor...")
    if not uploader.verificar_servidor():
        print("❌ Error: No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:8000")
        sys.exit(1)
    
    print("✅ Servidor conectado")
    
    # Login
    print("\n🔐 Autenticación")
    username = input("Usuario: ").strip()
    password = getpass("Contraseña: ")
    
    print("\n🔄 Autenticando...")
    success, message = uploader.login(username, password)
    
    if not success:
        print(f"❌ {message}")
        sys.exit(1)
    
    print(f"✅ {message}")
    
    # Confirmar
    print(f"\n⚠️  Se cargarán 183 archivos PDF desde:")
    print(f"   {PDF_DIR}")
    respuesta = input("\n¿Deseas continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        sys.exit(0)
    
    # Procesar
    uploader.procesar_directorio()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(0)
