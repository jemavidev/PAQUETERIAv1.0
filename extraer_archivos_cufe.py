#!/usr/bin/env python3
"""
Extraer archivos ZIP de CUFE y mover XML/PDF a carpeta principal
"""
import os
import zipfile
import shutil
from pathlib import Path

# Rutas
base_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML")
zip_dir_2025 = base_dir / "ZIP" / "2025"
zip_dir_2026 = base_dir / "ZIP" / "2026"
output_dir = base_dir  # Carpeta principal donde van los XML y PDF

# Crear directorio temporal para extracción
temp_dir = base_dir / "temp_extract"
temp_dir.mkdir(exist_ok=True)

print("=" * 80)
print("EXTRACCIÓN DE ARCHIVOS CUFE")
print("=" * 80)

# Contadores
total_zips = 0
total_xml = 0
total_pdf = 0
errores = 0

# Función para procesar un directorio de ZIPs
def procesar_directorio_zip(zip_directory, year):
    global total_zips, total_xml, total_pdf, errores
    
    if not zip_directory.exists():
        print(f"⚠️ Directorio no existe: {zip_directory}")
        return
    
    zip_files = list(zip_directory.glob("*.zip"))
    print(f"\n📁 Procesando {len(zip_files)} archivos ZIP de {year}...")
    
    for i, zip_path in enumerate(zip_files, 1):
        try:
            # Extraer CUFE del nombre del archivo (sin .zip)
            cufe = zip_path.stem
            
            # Verificar si ya existen los archivos
            xml_dest = output_dir / f"{cufe}.xml"
            pdf_dest = output_dir / f"{cufe}.pdf"
            
            if xml_dest.exists() and pdf_dest.exists():
                print(f"   [{i}/{len(zip_files)}] ⏭️  {cufe[:20]}... (ya existe)")
                continue
            
            # Extraer ZIP a directorio temporal
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            total_zips += 1
            
            # Buscar archivos XML y PDF en el directorio temporal
            xml_files = list(temp_dir.glob("**/*.xml"))
            pdf_files = list(temp_dir.glob("**/*.pdf"))
            
            # Mover XML
            if xml_files:
                for xml_file in xml_files:
                    if not xml_dest.exists():
                        shutil.move(str(xml_file), str(xml_dest))
                        total_xml += 1
            
            # Mover PDF
            if pdf_files:
                for pdf_file in pdf_files:
                    if not pdf_dest.exists():
                        shutil.move(str(pdf_file), str(pdf_dest))
                        total_pdf += 1
            
            # Limpiar directorio temporal
            for item in temp_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            
            print(f"   [{i}/{len(zip_files)}] ✅ {cufe[:20]}... (XML: {len(xml_files)}, PDF: {len(pdf_files)})")
            
        except Exception as e:
            errores += 1
            print(f"   [{i}/{len(zip_files)}] ❌ Error en {zip_path.name}: {e}")

# Procesar ambos directorios
procesar_directorio_zip(zip_dir_2025, "2025")
procesar_directorio_zip(zip_dir_2026, "2026")

# Limpiar directorio temporal
if temp_dir.exists():
    shutil.rmtree(temp_dir)

# Resumen final
print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"✅ ZIPs procesados: {total_zips}")
print(f"📄 Archivos XML extraídos: {total_xml}")
print(f"📑 Archivos PDF extraídos: {total_pdf}")
print(f"❌ Errores: {errores}")

# Contar archivos finales en la carpeta principal
xml_finales = len(list(output_dir.glob("*.xml")))
pdf_finales = len(list(output_dir.glob("*.pdf")))

print(f"\n📊 Total en carpeta principal:")
print(f"   XML: {xml_finales} archivos")
print(f"   PDF: {pdf_finales} archivos")

print("\n✅ Proceso completado!")
