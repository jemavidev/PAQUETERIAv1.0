#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear un anuncio de prueba y verificar el SMS
"""

import asyncio
import sys
from pathlib import Path
import httpx

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def main():
    """Crear anuncio de prueba via API"""
    
    print("=" * 70)
    print("CREAR ANUNCIO DE PRUEBA - PAQUETEX EL CLUB")
    print("=" * 70)
    
    try:
        # Datos del anuncio de prueba
        announcement_data = {
            "guide_number": "TEST789012",
            "customer_name": "JESUS VILLALOBOS",
            "customer_phone": "+573002596319"
        }
        
        print(f"\n📦 Creando anuncio de prueba:")
        print(f"   • Guía: {announcement_data['guide_number']}")
        print(f"   • Cliente: {announcement_data['customer_name']}")
        print(f"   • Teléfono: {announcement_data['customer_phone']}")
        
        # Enviar solicitud a la API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/api/announcements/",
                json=announcement_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\n📡 Respuesta de la API:")
            print(f"   • Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Anuncio creado exitosamente")
                print(f"   • ID: {data.get('id')}")
                print(f"   • Tracking Code: {data.get('tracking_code')}")
                print(f"   • Mensaje: {data.get('message')}")
            else:
                print(f"   ❌ Error creando anuncio")
                print(f"   • Respuesta: {response.text}")
        
        print(f"\n" + "=" * 70)
        print("PRUEBA COMPLETADA")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())