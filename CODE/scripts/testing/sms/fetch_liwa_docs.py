#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para obtener la documentación de LIWA
"""

import httpx
import asyncio
from bs4 import BeautifulSoup

async def fetch_documentation():
    """Obtener documentación de LIWA"""
    
    urls_to_try = [
        "https://apidoc.liwa.co/",
        "https://api.liwa.co/docs",
        "https://liwa.co/docs",
        "https://liwa.co/api-docs",
    ]
    
    print("=" * 80)
    print("OBTENIENDO DOCUMENTACIÓN DE LIWA")
    print("=" * 80)
    
    for url in urls_to_try:
        print(f"\n🔍 Intentando: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ Acceso exitoso")
                    
                    # Intentar parsear HTML
                    content_type = response.headers.get('content-type', '')
                    
                    if 'html' in content_type:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Buscar título
                        title = soup.find('title')
                        if title:
                            print(f"   📄 Título: {title.text.strip()}")
                        
                        # Buscar encabezados principales
                        headers = soup.find_all(['h1', 'h2', 'h3'])
                        if headers:
                            print(f"\n   📋 Secciones encontradas:")
                            for h in headers[:10]:  # Primeros 10
                                print(f"      • {h.text.strip()}")
                        
                        # Buscar endpoints en el contenido
                        text = soup.get_text()
                        if '/v2/' in text or 'endpoint' in text.lower():
                            print(f"\n   ✅ Contiene información de API")
                        
                        # Guardar contenido
                        filename = f"liwa_docs_{url.replace('https://', '').replace('/', '_')}.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"\n   💾 Guardado en: {filename}")
                        
                        return True
                    
                    elif 'json' in content_type:
                        print(f"   📄 Respuesta JSON:")
                        import json
                        data = response.json()
                        print(json.dumps(data, indent=2)[:500])
                        return True
                    
                    else:
                        print(f"   📄 Tipo de contenido: {content_type}")
                        print(f"   Primeros 500 caracteres:")
                        print(response.text[:500])
                        return True
                
                else:
                    print(f"   ❌ No accesible")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("❌ No se pudo acceder a la documentación")
    print("\n💡 Alternativas:")
    print("   • Contactar soporte: soporte@liwa.co")
    print("   • Revisar panel web: https://liwa.co/dashboard")
    print("   • Solicitar documentación oficial")
    print("=" * 80)
    
    return False

if __name__ == "__main__":
    asyncio.run(fetch_documentation())
