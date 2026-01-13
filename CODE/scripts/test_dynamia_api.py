#!/usr/bin/env python3
"""
Script para probar la conexión con la API de DynamiaERP
"""
import requests
import json
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DynamiaAPIClient:
    """Cliente para interactuar con la API de DynamiaERP"""
    
    def __init__(self, base_url: str = "https://api.dynamiaerp.co"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.account_id: Optional[int] = None
        
    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Autenticar con la API y obtener token
        
        Args:
            username: Usuario de DynamiaERP
            password: Contraseña
            
        Returns:
            Respuesta con token y datos de autenticación
        """
        url = f"{self.base_url}/api/seguridad/gettoken"
        payload = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get('token')
            
            print("✓ Autenticación exitosa")
            print(f"  Token: {self.token[:50]}..." if self.token else "  No token recibido")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error en autenticación: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Respuesta: {e.response.text}")
            raise
    
    def get_headers(self) -> Dict[str, str]:
        """Obtener headers con autenticación"""
        if not self.token:
            raise ValueError("No hay token. Debe autenticarse primero.")
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_account_context(self) -> Dict[str, Any]:
        """Obtener contexto de la cuenta"""
        url = f"{self.base_url}/api/v2/public/accounts/context"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            data = response.json()
            if 'accountId' in data:
                self.account_id = data['accountId']
            
            print("✓ Contexto de cuenta obtenido")
            print(f"  Account ID: {self.account_id}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo contexto: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Respuesta: {e.response.text}")
            raise
    
    def get_empresa_info(self) -> Dict[str, Any]:
        """Obtener información de la empresa"""
        url = f"{self.base_url}/api/empresa"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            data = response.json()
            print("✓ Información de empresa obtenida")
            print(f"  Nombre: {data.get('nombre', 'N/A')}")
            print(f"  NIT: {data.get('identificacion', 'N/A')}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo empresa: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Respuesta: {e.response.text}")
            raise
    
    def get_sucursales(self) -> list:
        """Obtener lista de sucursales"""
        url = f"{self.base_url}/api/empresa/sucursales"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            data = response.json()
            print(f"✓ Sucursales obtenidas: {len(data)} encontradas")
            
            for sucursal in data:
                print(f"  - {sucursal.get('nombre', 'N/A')} (ID: {sucursal.get('id', 'N/A')})")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo sucursales: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Respuesta: {e.response.text}")
            raise
    
    def get_clientes(self, limit: int = 10) -> list:
        """Obtener lista de clientes"""
        url = f"{self.base_url}/api/ventas/clientes"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            
            data = response.json()
            print(f"✓ Clientes obtenidos: {len(data)} encontrados")
            
            for cliente in data[:5]:  # Mostrar solo los primeros 5
                nombre = cliente.get('razonSocial') or f"{cliente.get('nombres', '')} {cliente.get('apellidos', '')}".strip()
                print(f"  - {nombre} (ID: {cliente.get('id', 'N/A')}, NIT: {cliente.get('identificacion', 'N/A')})")
            
            if len(data) > 5:
                print(f"  ... y {len(data) - 5} más")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo clientes: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Respuesta: {e.response.text}")
            raise
    
    def get_tipos_venta(self) -> list:
        """Obtener tipos de venta disponibles"""
        url = f"{self.base_url}/api/connect/ventas/tipos/documentos"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            data = response.json()
            print(f"✓ Tipos de venta obtenidos: {len(data)} encontrados")
            
            for tipo in data:
                print(f"  - {tipo.get('nombre', 'N/A')} (ID: {tipo.get('id', 'N/A')})")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo tipos de venta: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Respuesta: {e.response.text}")
            raise
    
    def get_face_status(self) -> Dict[str, Any]:
        """Obtener estado del emisor de facturación electrónica"""
        url = f"{self.base_url}/api/ventas/facturaElectronica/status"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            data = response.json()
            print("✓ Estado de facturación electrónica obtenido")
            print(f"  Estado: {data.get('estado', 'N/A')}")
            print(f"  Activo: {data.get('activo', 'N/A')}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo estado FACE: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Respuesta: {e.response.text}")
            raise
    
    def get_inventario_items(self, limit: int = 10) -> list:
        """Obtener items de inventario"""
        url = f"{self.base_url}/api/inventario/items"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            
            data = response.json()
            print(f"✓ Items de inventario obtenidos: {len(data)} encontrados")
            
            for item in data[:5]:  # Mostrar solo los primeros 5
                print(f"  - {item.get('nombre', 'N/A')} (ID: {item.get('id', 'N/A')}, Código: {item.get('codigo', 'N/A')})")
            
            if len(data) > 5:
                print(f"  ... y {len(data) - 5} más")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo inventario: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Respuesta: {e.response.text}")
            raise


def main():
    """Función principal para probar la API"""
    print("=" * 80)
    print("PRUEBA DE CONEXIÓN CON API DE DYNAMIAERP")
    print("=" * 80)
    print()
    
    # Obtener credenciales de variables de entorno
    username = os.getenv('DYNAMIA_USERNAME')
    password = os.getenv('DYNAMIA_PASSWORD')
    base_url = os.getenv('DYNAMIA_API_URL', 'https://api.dynamiaerp.co')
    
    if not username or not password:
        print("⚠ ADVERTENCIA: No se encontraron credenciales en variables de entorno")
        print("  Configure DYNAMIA_USERNAME y DYNAMIA_PASSWORD en el archivo .env")
        print()
        print("Ejemplo de .env:")
        print("  DYNAMIA_USERNAME=tu_usuario")
        print("  DYNAMIA_PASSWORD=tu_contraseña")
        print("  DYNAMIA_API_URL=https://api.dynamiaerp.co")
        print()
        
        # Solicitar credenciales manualmente
        username = input("Usuario de DynamiaERP: ").strip()
        password = input("Contraseña: ").strip()
        
        if not username or not password:
            print("✗ Credenciales no proporcionadas. Abortando.")
            return
    
    print(f"Base URL: {base_url}")
    print(f"Usuario: {username}")
    print()
    
    # Crear cliente
    client = DynamiaAPIClient(base_url)
    
    try:
        # 1. Autenticación
        print("1. Autenticando...")
        client.authenticate(username, password)
        print()
        
        # 2. Obtener contexto de cuenta
        print("2. Obteniendo contexto de cuenta...")
        client.get_account_context()
        print()
        
        # 3. Información de empresa
        print("3. Obteniendo información de empresa...")
        client.get_empresa_info()
        print()
        
        # 4. Sucursales
        print("4. Obteniendo sucursales...")
        client.get_sucursales()
        print()
        
        # 5. Tipos de venta
        print("5. Obteniendo tipos de venta...")
        client.get_tipos_venta()
        print()
        
        # 6. Clientes
        print("6. Obteniendo clientes...")
        client.get_clientes(limit=10)
        print()
        
        # 7. Items de inventario
        print("7. Obteniendo items de inventario...")
        client.get_inventario_items(limit=10)
        print()
        
        # 8. Estado de facturación electrónica
        print("8. Obteniendo estado de facturación electrónica...")
        client.get_face_status()
        print()
        
        print("=" * 80)
        print("✓ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 80)
        
    except Exception as e:
        print()
        print("=" * 80)
        print("✗ ERROR EN LAS PRUEBAS")
        print("=" * 80)
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
