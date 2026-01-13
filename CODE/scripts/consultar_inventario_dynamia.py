#!/usr/bin/env python3
"""
Script para consultar el inventario de DynamiaERP
"""
import requests
import json
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DynamiaInventarioClient:
    """Cliente para consultar inventario de DynamiaERP"""
    
    def __init__(self, token: str, base_url: str = "https://api.dynamiaerp.co"):
        self.base_url = base_url
        self.token = token
        
    def get_headers(self) -> Dict[str, str]:
        """Obtener headers con autenticación"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los items del inventario
        
        Returns:
            Lista de items del inventario
        """
        url = f"{self.base_url}/api/inventario/items"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            data = response.json()
            
            # La API retorna un diccionario con la clave 'data'
            if isinstance(data, dict) and 'data' in data:
                items = data['data']
            else:
                items = data if isinstance(data, list) else []
            
            print(f"✓ Total de items encontrados: {len(items)}")
            
            return items
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo items: {e}")
            return []
    
    def get_ultimos_items(self) -> List[Dict[str, Any]]:
        """
        Obtener últimos items creados
        
        Returns:
            Lista de últimos items
        """
        url = f"{self.base_url}/api/inventario/items/ultimos"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            items = response.json()
            print(f"✓ Últimos items: {len(items)}")
            
            return items
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo últimos items: {e}")
            return []
    
    def get_tipos_items(self) -> List[Dict[str, Any]]:
        """
        Obtener tipos de items disponibles
        
        Returns:
            Lista de tipos de items
        """
        url = f"{self.base_url}/api/inventario/items/tipos"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            tipos = response.json()
            print(f"✓ Tipos de items: {len(tipos)}")
            
            return tipos
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo tipos: {e}")
            return []
    
    def get_marcas(self) -> List[Dict[str, Any]]:
        """
        Obtener marcas disponibles
        
        Returns:
            Lista de marcas
        """
        url = f"{self.base_url}/api/inventario/marcas"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            marcas = response.json()
            print(f"✓ Marcas: {len(marcas)}")
            
            return marcas
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo marcas: {e}")
            return []
    
    def get_lineas(self) -> List[Dict[str, Any]]:
        """
        Obtener líneas de productos
        
        Returns:
            Lista de líneas
        """
        url = f"{self.base_url}/api/inventario/lineas"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            lineas = response.json()
            print(f"✓ Líneas de productos: {len(lineas)}")
            
            return lineas
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo líneas: {e}")
            return []
    
    def get_bodegas(self) -> List[Dict[str, Any]]:
        """
        Obtener bodegas disponibles
        
        Returns:
            Lista de bodegas
        """
        url = f"{self.base_url}/api/inventario/bodegas"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            bodegas = response.json()
            print(f"✓ Bodegas: {len(bodegas)}")
            
            return bodegas
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error obteniendo bodegas: {e}")
            return []
    
    def get_existencias(self, bodega_id: int = None, item_id: int = None) -> List[Dict[str, Any]]:
        """
        Consultar existencias de inventario
        
        Args:
            bodega_id: ID de la bodega (opcional)
            item_id: ID del item (opcional)
            
        Returns:
            Lista de existencias
        """
        url = f"{self.base_url}/api/inventario/items/existencias"
        params = {}
        
        if bodega_id:
            params['bodegaId'] = bodega_id
        if item_id:
            params['itemId'] = item_id
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            
            existencias = response.json()
            print(f"✓ Existencias consultadas: {len(existencias)}")
            
            return existencias
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error consultando existencias: {e}")
            return []
    
    def buscar_item_por_nombre(self, nombre: str, items: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Buscar items por nombre
        
        Args:
            nombre: Nombre o parte del nombre a buscar
            items: Lista de items (si no se proporciona, se consultan todos)
            
        Returns:
            Lista de items que coinciden con el nombre
        """
        if items is None:
            items = self.get_all_items()
        
        nombre_lower = nombre.lower()
        resultados = [
            item for item in items 
            if nombre_lower in item.get('nombre', '').lower()
        ]
        
        print(f"✓ Items encontrados con '{nombre}': {len(resultados)}")
        return resultados
    
    def buscar_item_por_codigo(self, codigo: str, items: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Buscar item por código
        
        Args:
            codigo: Código del item
            items: Lista de items (si no se proporciona, se consultan todos)
            
        Returns:
            Item encontrado o None
        """
        if items is None:
            items = self.get_all_items()
        
        for item in items:
            if item.get('codigo') == codigo:
                print(f"✓ Item encontrado: {item.get('nombre')}")
                return item
        
        print(f"✗ No se encontró item con código: {codigo}")
        return None
    
    def mostrar_item(self, item: Dict[str, Any]):
        """Mostrar información detallada de un item"""
        print(f"\n{'=' * 80}")
        print(f"ITEM: {item.get('nombre', 'Sin nombre')}")
        print(f"{'=' * 80}")
        print(f"ID: {item.get('id')}")
        print(f"Código: {item.get('codigo', 'N/A')}")
        
        precio = item.get('precio', 0)
        if precio:
            print(f"Precio: ${precio:,.2f}")
        
        tipo = item.get('tipo')
        if tipo and isinstance(tipo, dict):
            print(f"Tipo: {tipo.get('nombre', 'N/A')}")
        
        marca = item.get('marca')
        if marca and isinstance(marca, dict):
            print(f"Marca: {marca.get('nombre', 'N/A')}")
        
        linea = item.get('linea')
        if linea and isinstance(linea, dict):
            print(f"Línea: {linea.get('nombre', 'N/A')}")
        
        print(f"Estado: {item.get('estado', 'N/A')}")
        
        desc = item.get('descripcion', '')
        if desc:
            print(f"Descripción: {desc}")
        
        print(f"{'=' * 80}\n")


def main():
    """Función principal"""
    print("=" * 80)
    print("CONSULTA DE INVENTARIO - DYNAMIAERP")
    print("=" * 80)
    print()
    
    # Obtener token de variables de entorno
    token = os.getenv('DYNAMIA_TOKEN')
    
    if not token:
        print("✗ Error: No se encontró DYNAMIA_TOKEN en variables de entorno")
        print("  Configure DYNAMIA_TOKEN en el archivo .env")
        return 1
    
    # Crear cliente
    client = DynamiaInventarioClient(token)
    
    # Menú interactivo
    while True:
        print("\n" + "=" * 80)
        print("OPCIONES:")
        print("=" * 80)
        print("1. Listar todos los items")
        print("2. Últimos items creados")
        print("3. Tipos de items")
        print("4. Marcas")
        print("5. Líneas de productos")
        print("6. Bodegas")
        print("7. Consultar existencias")
        print("8. Buscar item por nombre")
        print("9. Buscar item por código")
        print("10. Guardar inventario completo en JSON")
        print("0. Salir")
        print()
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            print("\n" + "-" * 80)
            items = client.get_all_items()
            print(f"\nMostrando primeros 20 items:")
            for i, item in enumerate(items[:20], 1):
                print(f"{i}. {item.get('nombre')} (ID: {item.get('id')}, Código: {item.get('codigo', 'N/A')})")
            if len(items) > 20:
                print(f"... y {len(items) - 20} items más")
        
        elif opcion == "2":
            print("\n" + "-" * 80)
            items = client.get_ultimos_items()
            for item in items:
                print(f"  - {item.get('nombre')} (ID: {item.get('id')})")
        
        elif opcion == "3":
            print("\n" + "-" * 80)
            tipos = client.get_tipos_items()
            for tipo in tipos:
                print(f"  - ID: {tipo.get('id')} - {tipo.get('nombre')}")
        
        elif opcion == "4":
            print("\n" + "-" * 80)
            marcas = client.get_marcas()
            for marca in marcas[:20]:
                print(f"  - ID: {marca.get('id')} - {marca.get('nombre')}")
            if len(marcas) > 20:
                print(f"... y {len(marcas) - 20} marcas más")
        
        elif opcion == "5":
            print("\n" + "-" * 80)
            lineas = client.get_lineas()
            for linea in lineas[:20]:
                print(f"  - ID: {linea.get('id')} - {linea.get('nombre')}")
            if len(lineas) > 20:
                print(f"... y {len(lineas) - 20} líneas más")
        
        elif opcion == "6":
            print("\n" + "-" * 80)
            bodegas = client.get_bodegas()
            for bodega in bodegas:
                print(f"  - ID: {bodega.get('id')} - {bodega.get('nombre')}")
                sucursal = bodega.get('sucursal')
                if sucursal and isinstance(sucursal, dict):
                    print(f"    Sucursal: {sucursal.get('nombre', 'N/A')}")
        
        elif opcion == "7":
            print("\n" + "-" * 80)
            bodega_id = input("ID de bodega (Enter para todas): ").strip()
            item_id = input("ID de item (Enter para todos): ").strip()
            
            bodega_id = int(bodega_id) if bodega_id else None
            item_id = int(item_id) if item_id else None
            
            existencias = client.get_existencias(bodega_id, item_id)
            for existencia in existencias[:20]:
                print(f"  - {existencia}")
        
        elif opcion == "8":
            print("\n" + "-" * 80)
            nombre = input("Nombre a buscar: ").strip()
            if nombre:
                resultados = client.buscar_item_por_nombre(nombre)
                for item in resultados[:10]:
                    client.mostrar_item(item)
                if len(resultados) > 10:
                    print(f"... y {len(resultados) - 10} items más")
        
        elif opcion == "9":
            print("\n" + "-" * 80)
            codigo = input("Código a buscar: ").strip()
            if codigo:
                item = client.buscar_item_por_codigo(codigo)
                if item:
                    client.mostrar_item(item)
        
        elif opcion == "10":
            print("\n" + "-" * 80)
            items = client.get_all_items()
            filename = "inventario_dynamia.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            print(f"✓ Inventario guardado en: {filename}")
        
        elif opcion == "0":
            print("\n¡Hasta luego!")
            break
        
        else:
            print("\n✗ Opción inválida")


if __name__ == "__main__":
    exit(main())
