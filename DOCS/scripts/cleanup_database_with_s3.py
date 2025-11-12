#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Script de Limpieza Completa (Base de Datos + AWS S3)
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script realiza limpieza completa del sistema:
- Elimina archivos de AWS S3
- Vacía las tablas de la base de datos
- Resetea secuencias
- Verifica limpieza completa

IMPORTANTE: Este script elimina TODOS los datos y archivos.
Solo usar en desarrollo, NUNCA en producción.
"""

import os
import sys
import logging
import boto3
from datetime import datetime
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Tuple

# Agregar el directorio src al path para importar los modelos
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent  # Ir a la raíz del proyecto
src_dir = project_root / "CODE" / "LOCAL" / "src"
sys.path.insert(0, str(src_dir))

# Cambiar al directorio del proyecto para que las importaciones funcionen
os.chdir(project_root)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Usar DATABASE_URL directamente desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://paqueteria_user:paqueteria_pass@localhost:5432/paqueteria_local")

# Importar modelos directamente
sys.path.insert(0, str(src_dir / "app" / "models"))

# Importar solo los modelos que necesitamos
try:
    from package import Package
    from package_history import PackageHistory
    from announcement_new import PackageAnnouncementNew
    from message import Message
    from file_upload import FileUpload
    from customer import Customer
except ImportError as e:
    print(f"❌ Error importando modelos: {e}")
    print("💡 Verificando estructura de modelos...")
    import os
    models_dir = src_dir / "app" / "models"
    print(f"📁 Directorio models: {models_dir}")
    if models_dir.exists():
        print(f"📋 Archivos en models: {os.listdir(models_dir)}")
    else:
        print("❌ Directorio models no encontrado")
    sys.exit(1)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/database_s3_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class S3CleanupService:
    """Servicio para limpieza de archivos en AWS S3"""
    
    def __init__(self):
        """Inicializar cliente S3"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.bucket_name = os.getenv('AWS_S3_BUCKET', 'paquetes-el-club')
            logger.info(f"✅ Cliente S3 inicializado - Bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("❌ Credenciales AWS no encontradas")
            raise
        except Exception as e:
            logger.error(f"❌ Error inicializando S3: {e}")
            raise
    
    def get_all_s3_keys(self, session) -> List[str]:
        """Obtener todas las claves S3 de la base de datos"""
        try:
            # Obtener todas las claves S3 de file_uploads
            s3_keys = session.query(FileUpload.s3_key).filter(
                FileUpload.s3_key.isnot(None)
            ).all()
            
            # Extraer solo las claves (no tuplas)
            keys = [key[0] for key in s3_keys if key[0]]
            
            logger.info(f"📊 Encontradas {len(keys)} claves S3 en la base de datos")
            return keys
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo claves S3: {e}")
            return []
    
    def delete_s3_files(self, s3_keys: List[str]) -> Tuple[int, int]:
        """Eliminar archivos de S3"""
        if not s3_keys:
            logger.info("✅ No hay archivos S3 para eliminar")
            return 0, 0
        
        deleted_count = 0
        error_count = 0
        
        logger.info(f"🗑️ Eliminando {len(s3_keys)} archivos de S3...")
        
        for i, s3_key in enumerate(s3_keys, 1):
            try:
                # Verificar si el archivo existe
                self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
                
                # Eliminar archivo
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
                deleted_count += 1
                
                if i % 10 == 0 or i == len(s3_keys):
                    logger.info(f"🗑️ Progreso S3: {i}/{len(s3_keys)} archivos procesados")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    logger.warning(f"⚠️ Archivo no encontrado en S3: {s3_key}")
                else:
                    logger.error(f"❌ Error eliminando {s3_key}: {e}")
                    error_count += 1
            except Exception as e:
                logger.error(f"❌ Error inesperado eliminando {s3_key}: {e}")
                error_count += 1
        
        logger.info(f"✅ S3: {deleted_count} archivos eliminados, {error_count} errores")
        return deleted_count, error_count
    
    def verify_s3_cleanup(self, s3_keys: List[str]) -> bool:
        """Verificar que todos los archivos fueron eliminados de S3"""
        if not s3_keys:
            return True
        
        remaining_files = []
        
        for s3_key in s3_keys:
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
                remaining_files.append(s3_key)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    # Archivo no encontrado = eliminado correctamente
                    continue
                else:
                    remaining_files.append(s3_key)
            except Exception as e:
                logger.error(f"❌ Error verificando {s3_key}: {e}")
                remaining_files.append(s3_key)
        
        if remaining_files:
            logger.warning(f"⚠️ {len(remaining_files)} archivos aún existen en S3")
            for file_key in remaining_files[:5]:  # Mostrar solo los primeros 5
                logger.warning(f"   - {file_key}")
            if len(remaining_files) > 5:
                logger.warning(f"   ... y {len(remaining_files) - 5} más")
            return False
        else:
            logger.info("✅ Verificación S3: Todos los archivos fueron eliminados")
            return True

class DatabaseCleanup:
    """Clase para manejar la limpieza de la base de datos"""
    
    def __init__(self):
        """Inicializar conexión a la base de datos"""
        try:
            self.database_url = DATABASE_URL
            self.engine = create_engine(self.database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info("✅ Conexión a base de datos establecida correctamente")
        except Exception as e:
            logger.error(f"❌ Error al conectar con la base de datos: {e}")
            sys.exit(1)
    
    def get_table_counts(self):
        """Obtener conteo de registros en cada tabla"""
        counts = {}
        with self.engine.connect() as conn:
            tables = [
                'packages', 'package_history', 'package_announcements_new',
                'messages', 'file_uploads', 'customers'
            ]
            
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    counts[table] = count
                    logger.info(f"📊 {table}: {count} registros")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo obtener conteo de {table}: {e}")
                    counts[table] = 0
        
        return counts
    
    def cleanup_tables(self):
        """Limpiar todas las tablas en el orden correcto"""
        session = self.SessionLocal()
        
        try:
            logger.info("🧹 Iniciando limpieza de base de datos...")
            
            # Orden de eliminación (respetando foreign keys):
            cleanup_order = [
                ('file_uploads', FileUpload),
                ('messages', Message),
                ('package_history', PackageHistory),
                ('package_announcements_new', PackageAnnouncementNew),
                ('packages', Package),
                ('customers', Customer)
            ]
            
            total_deleted = 0
            
            for table_name, model_class in cleanup_order:
                try:
                    # Contar registros antes de eliminar
                    count_before = session.query(model_class).count()
                    
                    if count_before > 0:
                        # Eliminar todos los registros
                        deleted_count = session.query(model_class).delete()
                        session.commit()
                        
                        total_deleted += deleted_count
                        logger.info(f"🗑️ {table_name}: {deleted_count} registros eliminados")
                    else:
                        logger.info(f"✅ {table_name}: Ya está vacía")
                        
                except Exception as e:
                    logger.error(f"❌ Error al limpiar {table_name}: {e}")
                    session.rollback()
                    raise
            
            logger.info(f"🎉 Limpieza DB completada. Total de registros eliminados: {total_deleted}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante la limpieza de DB: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def reset_sequences(self):
        """Resetear secuencias de auto-incremento"""
        try:
            with self.engine.connect() as conn:
                # Resetear secuencias para tablas con ID auto-incremento
                sequences_to_reset = [
                    'packages_id_seq',
                    'messages_id_seq',
                    'file_uploads_id_seq'
                ]
                
                for sequence in sequences_to_reset:
                    try:
                        conn.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1"))
                        logger.info(f"🔄 Secuencia {sequence} reseteada")
                    except Exception as e:
                        logger.warning(f"⚠️ No se pudo resetear {sequence}: {e}")
                
                conn.commit()
                logger.info("✅ Secuencias reseteadas correctamente")
                
        except Exception as e:
            logger.error(f"❌ Error al resetear secuencias: {e}")
    
    def verify_cleanup(self):
        """Verificar que la limpieza fue exitosa"""
        logger.info("🔍 Verificando limpieza de base de datos...")
        counts = self.get_table_counts()
        
        all_empty = True
        for table, count in counts.items():
            if count > 0:
                logger.warning(f"⚠️ {table} aún tiene {count} registros")
                all_empty = False
            else:
                logger.info(f"✅ {table} está vacía")
        
        if all_empty:
            logger.info("🎉 Verificación DB exitosa: Todas las tablas están vacías")
        else:
            logger.warning("⚠️ Algunas tablas no se limpiaron completamente")
        
        return all_empty

class CompleteCleanupService:
    """Servicio principal de limpieza completa"""
    
    def __init__(self):
        """Inicializar servicios"""
        self.db_cleanup = DatabaseCleanup()
        self.s3_cleanup = S3CleanupService()
    
    def get_cleanup_summary(self):
        """Obtener resumen de lo que se va a limpiar"""
        session = self.db_cleanup.SessionLocal()
        
        try:
            # Conteo de base de datos
            db_counts = self.db_cleanup.get_table_counts()
            total_db_records = sum(db_counts.values())
            
            # Conteo de archivos S3
            s3_keys = self.s3_cleanup.get_all_s3_keys(session)
            total_s3_files = len(s3_keys)
            
            return {
                'database': {
                    'counts': db_counts,
                    'total_records': total_db_records
                },
                's3': {
                    'total_files': total_s3_files,
                    'keys': s3_keys
                }
            }
        finally:
            session.close()
    
    def execute_complete_cleanup(self):
        """Ejecutar limpieza completa"""
        session = self.db_cleanup.SessionLocal()
        
        try:
            # 1. Obtener claves S3 antes de limpiar la DB
            logger.info("📋 Obteniendo claves S3 de la base de datos...")
            s3_keys = self.s3_cleanup.get_all_s3_keys(session)
            
            # 2. Eliminar archivos de S3
            if s3_keys:
                logger.info("🗑️ Eliminando archivos de AWS S3...")
                deleted_files, error_files = self.s3_cleanup.delete_s3_files(s3_keys)
            else:
                deleted_files, error_files = 0, 0
                logger.info("✅ No hay archivos S3 para eliminar")
            
            # 3. Limpiar base de datos
            logger.info("🗑️ Limpiando base de datos...")
            db_success = self.db_cleanup.cleanup_tables()
            
            if not db_success:
                logger.error("❌ Error en limpieza de base de datos")
                return False
            
            # 4. Resetear secuencias
            logger.info("🔄 Reseteando secuencias...")
            self.db_cleanup.reset_sequences()
            
            # 5. Verificar limpieza
            logger.info("🔍 Verificando limpieza...")
            db_clean = self.db_cleanup.verify_cleanup()
            s3_clean = self.s3_cleanup.verify_s3_cleanup(s3_keys)
            
            # 6. Resumen final
            logger.info("="*60)
            logger.info("📊 RESUMEN DE LIMPIEZA COMPLETA")
            logger.info("="*60)
            logger.info(f"🗑️ Archivos S3 eliminados: {deleted_files}")
            if error_files > 0:
                logger.warning(f"⚠️ Errores S3: {error_files}")
            logger.info(f"🗑️ Registros DB eliminados: {sum(self.db_cleanup.get_table_counts().values())}")
            logger.info(f"✅ Base de datos limpia: {'Sí' if db_clean else 'No'}")
            logger.info(f"✅ S3 limpio: {'Sí' if s3_clean else 'No'}")
            logger.info("="*60)
            
            return db_clean and s3_clean
            
        finally:
            session.close()

def confirm_cleanup():
    """Solicitar confirmación del usuario"""
    print("\n" + "="*70)
    print("⚠️  ADVERTENCIA: LIMPIEZA COMPLETA DEL SISTEMA  ⚠️")
    print("="*70)
    print("Este script eliminará:")
    print("• TODOS los archivos de AWS S3")
    print("• TODOS los datos de las siguientes tablas:")
    print("  - packages")
    print("  - package_history") 
    print("  - package_announcements_new")
    print("  - messages")
    print("  - file_uploads")
    print("  - customers")
    print("\nEsta acción NO SE PUEDE DESHACER.")
    print("="*70)
    
    while True:
        response = input("\n¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ").strip()
        if response == 'SI':
            return True
        elif response.lower() in ['no', 'n', 'cancel', 'cancelar']:
            print("❌ Operación cancelada por el usuario")
            return False
        else:
            print("❌ Respuesta inválida. Escribe 'SI' para confirmar o 'no' para cancelar")

def main():
    """Función principal"""
    print("🚀 PAQUETES EL CLUB v4.0 - Limpieza Completa (DB + S3)")
    print("="*70)
    
    # Verificar que estamos en el directorio correcto
    if not (Path.cwd() / "CODE" / "LOCAL").exists():
        print("❌ Error: Ejecutar este script desde la raíz del proyecto")
        sys.exit(1)
    
    # Crear directorio de logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    # Verificar variables de entorno AWS
    required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_S3_BUCKET']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variables de entorno AWS faltantes: {', '.join(missing_vars)}")
        print("💡 Configura las variables en CODE/LOCAL/.env")
        sys.exit(1)
    
    # Inicializar servicio de limpieza
    try:
        cleanup_service = CompleteCleanupService()
    except Exception as e:
        print(f"❌ Error inicializando servicios: {e}")
        sys.exit(1)
    
    # Mostrar resumen de limpieza
    print("\n📊 Resumen de limpieza:")
    summary = cleanup_service.get_cleanup_summary()
    
    print(f"📊 Base de datos: {summary['database']['total_records']} registros")
    print(f"📊 AWS S3: {summary['s3']['total_files']} archivos")
    
    total_items = summary['database']['total_records'] + summary['s3']['total_files']
    if total_items == 0:
        print("✅ El sistema ya está vacío")
        return
    
    print(f"\nTotal de elementos a eliminar: {total_items}")
    
    # Solicitar confirmación
    if not confirm_cleanup():
        return
    
    # Ejecutar limpieza completa
    print("\n🧹 Iniciando limpieza completa...")
    success = cleanup_service.execute_complete_cleanup()
    
    if success:
        print("\n✅ Limpieza completa exitosa")
        print("📝 Revisa el archivo logs/database_s3_cleanup.log para más detalles")
    else:
        print("\n❌ Error durante la limpieza")
        print("📝 Revisa el archivo logs/database_s3_cleanup.log para más detalles")
        sys.exit(1)

if __name__ == "__main__":
    main()
