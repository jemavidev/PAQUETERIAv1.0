#!/usr/bin/env python3
"""
Script para verificar paquetes anunciados de un cliente
Uso: python test_paquetes_anunciados.py [telefono]
"""

import sys
import asyncio
import httpx

BASE_URL = "https://staging.jemavi.co"

async def verificar_paquetes_anunciados(telefono: str):
    """Verificar si un cliente tiene paquetes anunciados"""
    
    print(f"\n🔍 Buscando cliente con teléfono: {telefono}")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Buscar cliente por teléfono
            response = await client.get(
                f"{BASE_URL}/api/customers/search-by-phone",
                params={"phone": telefono}
            )
            
            if response.status_code == 404:
                print("❌ Cliente no encontrado")
                return
            
            if response.status_code != 200:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                return
            
            data = response.json()
            
            # 2. Mostrar información del cliente
            print(f"\n✅ Cliente encontrado:")
            print(f"   ID: {data['id']}")
            print(f"   Nombre: {data['full_name']}")
            print(f"   Teléfono: {data['phone']}")
            print(f"   Email: {data.get('email', 'No registrado')}")
            print(f"   VIP: {'Sí' if data.get('is_vip') else 'No'}")
            print(f"   Total paquetes recibidos: {data.get('total_packages_received', 0)}")
            
            # 3. Verificar si tiene paquetes anunciados
            if 'announced_codes' in data:
                print(f"\n📦 Paquetes Anunciados (Pendientes):")
                print(f"   Total: {data.get('total_announced', 0)}")
                
                if data['announced_codes']:
                    print(f"\n   Códigos de consulta:")
                    for code in data['announced_codes']:
                        tracking_code = code['tracking_code']
                        search_url = f"https://staging.jemavi.co/search?auto_search={tracking_code}"
                        print(f"   • {tracking_code} → {search_url}")
                else:
                    print("   ✅ No tiene paquetes pendientes")
            else:
                print("\n⚠️  El endpoint actual no devuelve códigos de paquetes anunciados")
                print("   Necesitas modificar el endpoint según la guía")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

async def consultar_directamente_bd(telefono: str):
    """
    Consulta directa a la base de datos (requiere acceso)
    Este es un ejemplo de cómo hacerlo si tienes acceso a la BD
    """
    print(f"\n🗄️  Consulta Directa a Base de Datos")
    print("=" * 60)
    print("Para consultar directamente en la BD, ejecuta:")
    print(f"""
    SELECT 
        a.id,
        a.guide_number,
        a.tracking_code,
        a.customer_name,
        a.announced_at,
        a.is_processed,
        a.is_active
    FROM package_announcements_new a
    WHERE a.customer_phone = '{telefono}'
      AND a.is_processed = FALSE
      AND a.is_active = TRUE
    ORDER BY a.announced_at DESC;
    """)

def main():
    if len(sys.argv) < 2:
        print("Uso: python test_paquetes_anunciados.py [telefono]")
        print("Ejemplo: python test_paquetes_anunciados.py 3001234567")
        sys.exit(1)
    
    telefono = sys.argv[1]
    
    # Ejecutar verificación
    asyncio.run(verificar_paquetes_anunciados(telefono))
    
    # Mostrar consulta SQL de ejemplo
    asyncio.run(consultar_directamente_bd(telefono))

if __name__ == "__main__":
    main()
