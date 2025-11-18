#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el estado del token SMS y su cache
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.sms_service import SMSService
from app.utils.datetime_utils import get_colombia_now


async def main():
    """Verificar estado del token SMS"""
    
    print("=" * 70)
    print("VERIFICACIÓN DEL TOKEN SMS - PAQUETEX EL CLUB")
    print("=" * 70)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Inicializar servicio SMS
        sms_service = SMSService()
        
        # Obtener configuración
        print("\n🔧 Verificando configuración...")
        config = sms_service.get_sms_config(db)
        print(f"   ✓ Proveedor: {config.provider}")
        print(f"   ✓ Cuenta: {config.account_id}")
        print(f"   ✓ API Key: {config.api_key[:20]}...")
        
        # Verificar estado del cache
        print(f"\n📋 Estado del Cache del Token:")
        now = get_colombia_now()
        
        if hasattr(sms_service, '_cached_token') and sms_service._cached_token:
            print(f"   ✅ Token en cache: SÍ")
            print(f"   🔑 Token: {sms_service._cached_token[:50]}...")
            
            if hasattr(sms_service, '_token_expires_at') and sms_service._token_expires_at:
                expires_at = sms_service._token_expires_at
                time_left = expires_at - now
                
                print(f"   ⏰ Expira en: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   ⏳ Tiempo restante: {time_left}")
                
                if time_left.total_seconds() > 0:
                    print(f"   ✅ Estado: VÁLIDO")
                else:
                    print(f"   ❌ Estado: EXPIRADO")
            else:
                print(f"   ⚠️  Fecha de expiración: NO DEFINIDA")
        else:
            print(f"   ❌ Token en cache: NO")
        
        # Probar obtención de token
        print(f"\n🔄 Probando obtención de token...")
        try:
            token = await sms_service.get_valid_token(config)
            print(f"   ✅ Token obtenido exitosamente")
            print(f"   🔑 Token: {token[:50]}...")
            
            # Verificar nuevo estado del cache
            if hasattr(sms_service, '_token_expires_at') and sms_service._token_expires_at:
                expires_at = sms_service._token_expires_at
                time_left = expires_at - get_colombia_now()
                print(f"   ⏰ Nuevo token expira en: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   ⏳ Tiempo de vida: {time_left}")
            
        except Exception as e:
            print(f"   ❌ Error obteniendo token: {str(e)}")
        
        # Mostrar estadísticas
        print(f"\n📊 Estadísticas SMS (últimos 7 días):")
        try:
            stats = sms_service.get_sms_stats(db, days=7)
            print(f"   📤 Total enviados: {stats['total_sent']}")
            print(f"   ✅ Total entregados: {stats['total_delivered']}")
            print(f"   ❌ Total fallidos: {stats['total_failed']}")
            print(f"   💰 Costo total: ${stats['total_cost_cents'] / 100:.2f} COP")
            print(f"   📈 Tasa de entrega: {stats['delivery_rate']:.1f}%")
            print(f"   💵 Costo promedio: ${stats['average_cost_per_sms'] / 100:.2f} COP")
        except Exception as e:
            print(f"   ⚠️  Error obteniendo estadísticas: {str(e)}")
        
        print(f"\n" + "=" * 70)
        print("VERIFICACIÓN COMPLETADA")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())