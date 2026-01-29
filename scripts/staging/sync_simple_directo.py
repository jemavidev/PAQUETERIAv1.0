#!/usr/bin/env python3
"""
Script simple para sincronizar producción → staging
Ejecutar directamente en el servidor staging
"""
import subprocess
import sys
import os
from datetime import datetime

# Credenciales
HOST = "ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
USER = "jveyes"
PASSWORD = "a?HC!2.*1#?[==:|289qAI=)#V4kDzl$"

def log(message):
    """Imprimir con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_command(cmd, env=None):
    """Ejecutar comando y retornar resultado"""
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos máximo
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout: El comando tardó más de 10 minutos"
    except Exception as e:
        return -1, "", str(e)

def main():
    log("🔄 Iniciando sincronización producción → staging")
    log("=" * 60)
    
    # Configurar PGPASSWORD
    env = os.environ.copy()
    env["PGPASSWORD"] = PASSWORD
    
    # Paso 1: Exportar producción
    log("📦 Paso 1/3: Exportando base de datos de producción...")
    dump_file = "/tmp/backup_staging.dump"
    
    dump_cmd = [
        "pg_dump",
        "-h", HOST,
        "-U", USER,
        "-d", "paqueteria_v4",
        "-F", "c",
        "-f", dump_file,
        "--no-owner",
        "--no-acl"
    ]
    
    code, stdout, stderr = run_command(dump_cmd, env)
    
    if code != 0:
        log(f"❌ Error en exportación: {stderr}")
        sys.exit(1)
    
    log("✅ Exportación completada")
    
    # Paso 2: Restaurar en staging
    log("📥 Paso 2/3: Restaurando en staging...")
    
    restore_cmd = [
        "pg_restore",
        "-h", HOST,
        "-U", USER,
        "-d", "paqueteria_staging",
        dump_file,
        "--clean",
        "--if-exists",
        "--no-owner",
        "--no-acl"
    ]
    
    code, stdout, stderr = run_command(restore_cmd, env)
    
    # pg_restore puede retornar 1 con warnings, es normal
    if code not in [0, 1]:
        log(f"❌ Error en restauración: {stderr}")
        sys.exit(1)
    
    log("✅ Restauración completada")
    
    # Paso 3: Limpiar
    log("🧹 Paso 3/3: Limpiando archivos temporales...")
    try:
        os.remove(dump_file)
        log("✅ Limpieza completada")
    except:
        log("⚠️  No se pudo eliminar archivo temporal (no es crítico)")
    
    log("=" * 60)
    log("✅ Sincronización completada exitosamente")
    log(f"📊 Timestamp: {datetime.now().isoformat()}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n⚠️  Sincronización cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        log(f"❌ Error inesperado: {e}")
        sys.exit(1)
