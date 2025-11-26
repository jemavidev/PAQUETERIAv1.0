#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para intentar obtener el saldo de LIWA desde el panel web
"""

import asyncio
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

LIWA_ACCOUNT = os.getenv('LIWA_ACCOUNT')
LIWA_PASSWORD = os.getenv('LIWA_PASSWORD')

async def get_balance_from_web():
    """Intenta obtener el saldo desde el panel web de LIWA"""
    
    print("=" * 80)
    print("OBTENCIÓN DE SALDO DESDE PANEL WEB DE LIWA")
    print("=" * 80)
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            # Intentar acceder al dashboard
            print("\n🔐 Intentando acceder al panel de LIWA...")
            
            # Primero, obtener la página de login
            login_page = await client.get("https://liwa.co/login")
            print(f"   Status página login: {login_page.status_code}")
            
            if login_page.status_code != 200:
                print("   ❌ No se pudo acceder a la página de login")
                return None
            
            # Buscar el formulario de login
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # Intentar login (esto puede variar según la implementación de LIWA)
            print("\n🔑 Intentando iniciar sesión...")
            
            login_data = {
                "account": LIWA_ACCOUNT,
                "password": LIWA_PASSWORD,
                "username": LIWA_ACCOUNT,
                "email": LIWA_ACCOUNT,
            }
            
            # Probar diferentes URLs de login
            login_urls = [
                "https://liwa.co/login",
                "https://liwa.co/auth/login",
                "https://liwa.co/api/login",
                "https://www.liwa.co/login",
            ]
            
            for url in login_urls:
                try:
                    response = await client.post(url, data=login_data)
                    print(f"   Probando {url}: {response.status_code}")
                    
                    if response.status_code in [200, 302]:
                        # Intentar acceder al dashboard
                        dashboard = await client.get("https://liwa.co/dashboard")
                        
                        if dashboard.status_code == 200:
                            soup = BeautifulSoup(dashboard.text, 'html.parser')
                            
                            # Buscar el saldo en el HTML
                            # Patrones comunes: "saldo", "balance", "créditos", "credits"
                            text = soup.get_text()
                            
                            # Buscar patrones de saldo
                            import re
                            patterns = [
                                r'saldo[:\s]+([0-9,\.]+)',
                                r'balance[:\s]+([0-9,\.]+)',
                                r'créditos[:\s]+([0-9,\.]+)',
                                r'credits[:\s]+([0-9,\.]+)',
                            ]
                            
                            for pattern in patterns:
                                match = re.search(pattern, text, re.IGNORECASE)
                                if match:
                                    balance = match.group(1)
                                    print(f"\n✅ Saldo encontrado: {balance}")
                                    return balance
                            
                            # Si no encontramos el saldo, guardar el HTML para inspección
                            with open("liwa_dashboard.html", "w", encoding="utf-8") as f:
                                f.write(dashboard.text)
                            print("\n⚠️  No se pudo extraer el saldo automáticamente")
                            print("   Dashboard guardado en: liwa_dashboard.html")
                            return None
                
                except Exception as e:
                    continue
            
            print("\n❌ No se pudo iniciar sesión en el panel web")
            return None
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("\n⚠️  NOTA IMPORTANTE:")
    print("   El panel web de LIWA puede tener protección CSRF, captcha o")
    print("   autenticación de dos factores que impida el acceso automático.")
    print()
    
    balance = await get_balance_from_web()
    
    print("\n" + "=" * 80)
    
    if balance:
        print(f"✅ SALDO ACTUAL: {balance} créditos")
    else:
        print("❌ NO SE PUDO OBTENER EL SALDO AUTOMÁTICAMENTE")
        print()
        print("💡 SOLUCIÓN MANUAL:")
        print("   1. Abre tu navegador")
        print("   2. Ve a: https://liwa.co/dashboard")
        print("   3. Inicia sesión con:")
        print(f"      • Cuenta: {LIWA_ACCOUNT}")
        print(f"      • Contraseña: (tu contraseña)")
        print("   4. Busca el saldo en el panel principal")
        print()
        print("📞 O CONTACTA A LIWA:")
        print("   • Email: contacto@cellvoz.com.co")
        print("   • Solicita el saldo actual de tu cuenta")
    
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
