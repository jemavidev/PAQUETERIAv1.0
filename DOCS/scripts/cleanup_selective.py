#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Script de Limpieza Selectiva (Base de Datos + AWS S3)
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script permite limpieza selectiva del sistema:
- Elegir qué tablas limpiar
- Elegir si limpiar archivos S3
- Limpieza por fechas
- Limpieza por usuario específico

IMPORTANTE: Este script elimina datos y archivos.
Solo usar en desarrollo, NUNCA en producción.
"""

import os
import sys
import logging
import boto3
from datetime import datetime, timedelta
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Tuple, Optional

# Agregar el directorio src al path para importar los modelos
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent  # Ir a la raíz del proyecto
src_dir = project_root / "LOCAL" / "src"
sys.path.insert(0, str(src_dir))

# Cambiar al directorio del proyecto para que las importaciones funcionen
os.chdir(project_root)

from sqlalchemy import create_engine, text, and_
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL
from app.models import (
    Package, PackageHistory, PackageAnnouncementNew, 
    Message, FileUpload, Customer, User
)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/selective_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SelectiveCleanupService:
    """Servicio para limpieza selectiva del sistema"""
    
    def __init__(self):
        """Inicializar servicios"""
        try:
            self.database_url = DATABASE_URL
            self.engine = create_engine(self.database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Inicializar S3 si las credenciales están disponibles
            self.s3_client = None
            self.bucket_name = None
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_REGION', 'us-east-1')
                )
                self.bucket_name = os.getenv('AWS_S3_BUCKET', 'paquetes-el-club')
                logger.info(f"✅ Cliente S3 inicializado - Bucket: {self.bucket_name}")
            except Exception as e:
                logger.warning(f"⚠️ S3 no disponible: {e}")
            
            logger.info("✅ Servicios inicializados correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando servicios: {e}")
            sys.exit(1)
    
    def get_cleanup_options(self):
        """Mostrar opciones de limpieza disponibles"""
        print("\n" + "="*60)
        print("🧹 OPCIONES DE LIMPIEZA SELECTIVA")
        print("="*60)
        print("1. Limpieza completa (todas las tablas + S3)")
        print("2. Solo base de datos (todas las tablas)")
        print("3. Solo archivos S3")
        print("4. Tablas específicas")
        print("5. Limpieza por fechas")
        print("6. Limpieza por usuario")
        print("7. Solo archivos huérfanos de S3")
        print("8. Solo registros sin archivos S3")
        print("="*60)
    
    def get_table_selection(self):
        """Permitir selección de tablas específicas"""
        tables = {
            '1': ('packages', Package),
            '2': ('package_history', PackageHistory),
            '3': ('package_announcements_new', PackageAnnouncementNew),
            '4': ('messages', Message),
            '5': ('file_uploads', FileUpload),
            '6': ('customers', Customer)
        }
        
        print("\n📋 Selecciona las tablas a limpiar:")
        for key, (table_name, _) in tables.items():
            print(f"{key}. {table_name}")
        
        print("0. Todas las tablas")
        
        while True:
            selection = input("\nIngresa los números separados por comas (ej: 1,2,3): ").strip()
            
            if selection == "0":
                return list(tables.values())
            
            try:
                selected_indices = [idx.strip() for idx in selection.split(',')]
                selected_tables = []
                
                for idx in selected_indices:
                    if idx in tables:
                        selected_tables.append(tables[idx])
                    else:
                        print(f"❌ Opción inválida: {idx}")
                        break
                else:
                    return selected_tables
                    
            except Exception as e:
                print(f"❌ Error en la selección: {e}")
    
    def get_date_range(self):
        """Obtener rango de fechas para limpieza"""
        print("\n📅 Limpieza por fechas")
        print("Formato: YYYY-MM-DD")
        
        while True:
            start_date_str = input("Fecha de inicio (dejar vacío para sin límite): ").strip()
            if not start_date_str:
                start_date = None
                break
            
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                break
            except ValueError:
                print("❌ Formato de fecha inválido. Usa YYYY-MM-DD")
        
        while True:
            end_date_str = input("Fecha de fin (dejar vacío para sin límite): ").strip()
            if not end_date_str:
                end_date = None
                break
            
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                break
            except ValueError:
                print("❌ Formato de fecha inválido. Usa YYYY-MM-DD")
        
        return start_date, end_date
    
    def get_user_selection(self):
        """Obtener selección de usuario"""
        session = self.SessionLocal()
        
        try:
            users = session.query(User).all()
            
            if not users:
                print("❌ No hay usuarios en la base de datos")
                return None
            
            print("\n👥 Selecciona el usuario:")
            for i, user in enumerate(users, 1):
                print(f"{i}. {user.username} ({user.email}) - {user.role.value}")
            
            while True:
                try:
                    selection = int(input("Ingresa el número del usuario: ")) - 1
                    if 0 <= selection < len(users):
                        return users[selection]
                    else:
                        print("❌ Número inválido")
                except ValueError:
                    print("❌ Ingresa un número válido")
        finally:
            session.close()
    
    def cleanup_by_tables(self, selected_tables: List[Tuple], include_s3: bool = True):
        """Limpiar tablas específicas"""
        session = self.SessionLocal()
        
        try:
            # Obtener claves S3 antes de limpiar si se incluye S3
            s3_keys = []
            if include_s3 and self.s3_client:
                s3_keys = self.get_s3_keys_from_tables(session, selected_tables)
            
            # Limpiar tablas
            total_deleted = 0
            
            for table_name, model_class in selected_tables:
                try:
                    count_before = session.query(model_class).count()
                    
                    if count_before > 0:
                        deleted_count = session.query(model_class).delete()
                        session.commit()
                        total_deleted += deleted_count
                        logger.info(f"🗑️ {table_name}: {deleted_count} registros eliminados")
                    else:
                        logger.info(f"✅ {table_name}: Ya está vacía")
                        
                except Exception as e:
                    logger.error(f"❌ Error limpiando {table_name}: {e}")
                    session.rollback()
                    raise
            
            # Limpiar archivos S3 si se solicitó
            if include_s3 and s3_keys and self.s3_client:
                logger.info("🗑️ Eliminando archivos S3...")
                deleted_files, error_files = self.delete_s3_files(s3_keys)
                logger.info(f"✅ S3: {deleted_files} archivos eliminados, {error_files} errores")
            
            return total_deleted
            
        finally:
            session.close()
    
    def cleanup_by_dates(self, start_date: Optional[datetime], end_date: Optional[datetime], include_s3: bool = True):
        """Limpiar registros por rango de fechas"""
        session = self.SessionLocal()
        
        try:
            # Construir filtros de fecha
            date_filters = []
            if start_date:
                date_filters.append(Package.created_at >= start_date)
            if end_date:
                date_filters.append(Package.created_at <= end_date)
            
            if not date_filters:
                logger.warning("⚠️ No se especificaron filtros de fecha")
                return 0
            
            # Obtener paquetes en el rango de fechas
            packages_query = session.query(Package)
            if date_filters:
                packages_query = packages_query.filter(and_(*date_filters))
            
            packages = packages_query.all()
            package_ids = [p.id for p in packages]
            
            if not package_ids:
                logger.info("✅ No hay paquetes en el rango de fechas especificado")
                return 0
            
            logger.info(f"📊 Encontrados {len(package_ids)} paquetes en el rango de fechas")
            
            # Obtener claves S3 si se incluye
            s3_keys = []
            if include_s3 and self.s3_client:
                s3_keys = session.query(FileUpload.s3_key).filter(
                    FileUpload.package_id.in_(package_ids),
                    FileUpload.s3_key.isnot(None)
                ).all()
                s3_keys = [key[0] for key in s3_keys if key[0]]
            
            # Eliminar registros relacionados
            total_deleted = 0
            
            # Eliminar file_uploads
            deleted_files = session.query(FileUpload).filter(
                FileUpload.package_id.in_(package_ids)
            ).delete(synchronize_session=False)
            total_deleted += deleted_files
            logger.info(f"🗑️ file_uploads: {deleted_files} registros eliminados")
            
            # Eliminar messages
            deleted_messages = session.query(Message).filter(
                Message.package_id.in_(package_ids)
            ).delete(synchronize_session=False)
            total_deleted += deleted_messages
            logger.info(f"🗑️ messages: {deleted_messages} registros eliminados")
            
            # Eliminar package_history
            deleted_history = session.query(PackageHistory).filter(
                PackageHistory.package_id.in_(package_ids)
            ).delete(synchronize_session=False)
            total_deleted += deleted_history
            logger.info(f"🗑️ package_history: {deleted_history} registros eliminados")
            
            # Eliminar package_announcements_new
            deleted_announcements = session.query(PackageAnnouncementNew).filter(
                PackageAnnouncementNew.package_id.in_(package_ids)
            ).delete(synchronize_session=False)
            total_deleted += deleted_announcements
            logger.info(f"🗑️ package_announcements_new: {deleted_announcements} registros eliminados")
            
            # Eliminar packages
            deleted_packages = session.query(Package).filter(
                Package.id.in_(package_ids)
            ).delete(synchronize_session=False)
            total_deleted += deleted_packages
            logger.info(f"🗑️ packages: {deleted_packages} registros eliminados")
            
            session.commit()
            
            # Limpiar archivos S3 si se solicitó
            if include_s3 and s3_keys and self.s3_client:
                logger.info("🗑️ Eliminando archivos S3...")
                deleted_files, error_files = self.delete_s3_files(s3_keys)
                logger.info(f"✅ S3: {deleted_files} archivos eliminados, {error_files} errores")
            
            return total_deleted
            
        finally:
            session.close()
    
    def cleanup_by_user(self, user: User, include_s3: bool = True):
        """Limpiar registros de un usuario específico"""
        session = self.SessionLocal()
        
        try:
            # Obtener paquetes creados por el usuario
            packages = session.query(Package).filter(Package.created_by == user.id).all()
            package_ids = [p.id for p in packages]
            
            if not package_ids:
                logger.info(f"✅ No hay paquetes creados por {user.username}")
                return 0
            
            logger.info(f"📊 Encontrados {len(package_ids)} paquetes creados por {user.username}")
            
            # Obtener claves S3 si se incluye
            s3_keys = []
            if include_s3 and self.s3_client:
                s3_keys = session.query(FileUpload.s3_key).filter(
                    FileUpload.package_id.in_(package_ids),
                    FileUpload.s3_key.isnot(None)
                ).all()
                s3_keys = [key[0] for key in s3_keys if key[0]]
            
            # Eliminar registros relacionados (mismo proceso que por fechas)
            total_deleted = 0
            
            # Eliminar file_uploads
            deleted_files = session.query(FileUpload).filter(
                FileUpload.package_id.in_(package_ids)
            ).delete(synchronize_session=False)
            total_deleted += deleted_files
            logger.info(f"🗑️ file_uploads: {deleted_files} registros eliminados")
            
            # Eliminar messages
            deleted_messages = session.query(Message).filter(
                Message.package_id.in_(package_ids)
            ).delete(synchronize_session=False)
            total_deleted += deleted_messages
            logger.info(f"🗑️ messages: {deleted_messages} registros eliminados")
            
            # Eliminar package_history
            deleted_history = session.query(PackageHistory).filter(
                PackageHistory.package_id.in_(package_ids)
            ).delete(synchronize_session=False)
            total_deleted += deleted_history
            logger.info(f"🗑️ package_history: {deleted_history} registros eliminados")
            
            # Eliminar package_announcements_new
            deleted_announcements = session.query(PackageAnnouncementNew).filter(
                PackageAnnouncementNew.package_id.in_(package_ids)
            ).delete(synchronize_session=False)
            total_deleted += deleted_announcements
            logger.info(f"🗑️ package_announcements_new: {deleted_announcements} registros eliminados")
            
            # Eliminar packages
            deleted_packages = session.query(Package).filter(
                Package.id.in_(package_ids)
            ).delete(synchronize_session=False)
            total_deleted += deleted_packages
            logger.info(f"🗑️ packages: {deleted_packages} registros eliminados")
            
            session.commit()
            
            # Limpiar archivos S3 si se solicitó
            if include_s3 and s3_keys and self.s3_client:
                logger.info("🗑️ Eliminando archivos S3...")
                deleted_files, error_files = self.delete_s3_files(s3_keys)
                logger.info(f"✅ S3: {deleted_files} archivos eliminados, {error_files} errores")
            
            return total_deleted
            
        finally:
            session.close()
    
    def cleanup_orphaned_s3_files(self):
        """Limpiar archivos S3 huérfanos (sin referencia en DB)"""
        if not self.s3_client:
            logger.error("❌ Cliente S3 no disponible")
            return 0
        
        session = self.SessionLocal()
        
        try:
            # Obtener todas las claves S3 de la base de datos
            db_s3_keys = session.query(FileUpload.s3_key).filter(
                FileUpload.s3_key.isnot(None)
            ).all()
            db_s3_keys = set(key[0] for key in db_s3_keys if key[0])
            
            logger.info(f"📊 Claves S3 en base de datos: {len(db_s3_keys)}")
            
            # Listar archivos en S3
            s3_files = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=self.bucket_name):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        s3_files.append(obj['Key'])
            
            logger.info(f"📊 Archivos en S3: {len(s3_files)}")
            
            # Encontrar archivos huérfanos
            orphaned_files = [key for key in s3_files if key not in db_s3_keys]
            
            if not orphaned_files:
                logger.info("✅ No hay archivos huérfanos en S3")
                return 0
            
            logger.info(f"🗑️ Encontrados {len(orphaned_files)} archivos huérfanos en S3")
            
            # Eliminar archivos huérfanos
            deleted_count, error_count = self.delete_s3_files(orphaned_files)
            
            logger.info(f"✅ Archivos huérfanos eliminados: {deleted_count}, errores: {error_count}")
            return deleted_count
            
        finally:
            session.close()
    
    def cleanup_records_without_s3(self):
        """Limpiar registros de file_uploads sin archivos S3"""
        session = self.SessionLocal()
        
        try:
            # Obtener registros sin s3_key o con s3_key vacío
            records_without_s3 = session.query(FileUpload).filter(
                (FileUpload.s3_key.is_(None)) | (FileUpload.s3_key == '')
            ).all()
            
            if not records_without_s3:
                logger.info("✅ No hay registros sin archivos S3")
                return 0
            
            logger.info(f"🗑️ Encontrados {len(records_without_s3)} registros sin archivos S3")
            
            # Eliminar registros
            deleted_count = session.query(FileUpload).filter(
                (FileUpload.s3_key.is_(None)) | (FileUpload.s3_key == '')
            ).delete()
            
            session.commit()
            logger.info(f"✅ Registros sin S3 eliminados: {deleted_count}")
            return deleted_count
            
        finally:
            session.close()
    
    def get_s3_keys_from_tables(self, session, selected_tables: List[Tuple]) -> List[str]:
        """Obtener claves S3 de las tablas seleccionadas"""
        s3_keys = []
        
        for table_name, model_class in selected_tables:
            if model_class == FileUpload:
                # Para file_uploads, obtener directamente las claves
                keys = session.query(FileUpload.s3_key).filter(
                    FileUpload.s3_key.isnot(None)
                ).all()
                s3_keys.extend([key[0] for key in keys if key[0]])
            elif hasattr(model_class, 'id') and model_class != Customer:
                # Para otras tablas, obtener claves a través de file_uploads
                if hasattr(model_class, 'file_uploads'):
                    # Si tiene relación directa con file_uploads
                    records = session.query(model_class).all()
                    for record in records:
                        if hasattr(record, 'file_uploads'):
                            for file_upload in record.file_uploads:
                                if file_upload.s3_key:
                                    s3_keys.append(file_upload.s3_key)
                else:
                    # Buscar por package_id si es una tabla relacionada
                    if hasattr(model_class, 'package_id'):
                        records = session.query(model_class).all()
                        package_ids = [r.package_id for r in records if hasattr(r, 'package_id')]
                        if package_ids:
                            keys = session.query(FileUpload.s3_key).filter(
                                FileUpload.package_id.in_(package_ids),
                                FileUpload.s3_key.isnot(None)
                            ).all()
                            s3_keys.extend([key[0] for key in keys if key[0]])
        
        return list(set(s3_keys))  # Eliminar duplicados
    
    def delete_s3_files(self, s3_keys: List[str]) -> Tuple[int, int]:
        """Eliminar archivos de S3"""
        if not s3_keys or not self.s3_client:
            return 0, 0
        
        deleted_count = 0
        error_count = 0
        
        for i, s3_key in enumerate(s3_keys, 1):
            try:
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
        
        return deleted_count, error_count

def main():
    """Función principal"""
    print("🚀 PAQUETES EL CLUB v4.0 - Limpieza Selectiva")
    print("="*50)
    
    # Verificar que estamos en el directorio correcto
    if not (Path.cwd() / "CODE" / "LOCAL").exists():
        print("❌ Error: Ejecutar este script desde la raíz del proyecto")
        sys.exit(1)
    
    # Crear directorio de logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    # Inicializar servicio
    try:
        cleanup_service = SelectiveCleanupService()
    except Exception as e:
        print(f"❌ Error inicializando servicios: {e}")
        sys.exit(1)
    
    # Mostrar opciones
    cleanup_service.get_cleanup_options()
    
    while True:
        try:
            choice = input("\nSelecciona una opción (1-8): ").strip()
            
            if choice == "1":
                # Limpieza completa
                print("\n⚠️ ADVERTENCIA: Esto eliminará TODOS los datos y archivos")
                if input("¿Continuar? (escribe 'SI' para confirmar): ").strip() == 'SI':
                    selected_tables = [
                        ('file_uploads', FileUpload),
                        ('messages', Message),
                        ('package_history', PackageHistory),
                        ('package_announcements_new', PackageAnnouncementNew),
                        ('packages', Package),
                        ('customers', Customer)
                    ]
                    deleted = cleanup_service.cleanup_by_tables(selected_tables, include_s3=True)
                    print(f"\n✅ Limpieza completa: {deleted} registros eliminados")
                break
                
            elif choice == "2":
                # Solo base de datos
                selected_tables = cleanup_service.get_table_selection()
                deleted = cleanup_service.cleanup_by_tables(selected_tables, include_s3=False)
                print(f"\n✅ Limpieza DB: {deleted} registros eliminados")
                break
                
            elif choice == "3":
                # Solo S3
                if not cleanup_service.s3_client:
                    print("❌ Cliente S3 no disponible")
                    break
                session = cleanup_service.SessionLocal()
                s3_keys = cleanup_service.get_s3_keys_from_tables(session, [('file_uploads', FileUpload)])
                session.close()
                deleted, errors = cleanup_service.delete_s3_files(s3_keys)
                print(f"\n✅ Limpieza S3: {deleted} archivos eliminados, {errors} errores")
                break
                
            elif choice == "4":
                # Tablas específicas
                selected_tables = cleanup_service.get_table_selection()
                include_s3 = input("¿Incluir archivos S3? (s/n): ").strip().lower() == 's'
                deleted = cleanup_service.cleanup_by_tables(selected_tables, include_s3=include_s3)
                print(f"\n✅ Limpieza selectiva: {deleted} registros eliminados")
                break
                
            elif choice == "5":
                # Por fechas
                start_date, end_date = cleanup_service.get_date_range()
                include_s3 = input("¿Incluir archivos S3? (s/n): ").strip().lower() == 's'
                deleted = cleanup_service.cleanup_by_dates(start_date, end_date, include_s3=include_s3)
                print(f"\n✅ Limpieza por fechas: {deleted} registros eliminados")
                break
                
            elif choice == "6":
                # Por usuario
                user = cleanup_service.get_user_selection()
                if user:
                    include_s3 = input("¿Incluir archivos S3? (s/n): ").strip().lower() == 's'
                    deleted = cleanup_service.cleanup_by_user(user, include_s3=include_s3)
                    print(f"\n✅ Limpieza por usuario: {deleted} registros eliminados")
                break
                
            elif choice == "7":
                # Archivos huérfanos S3
                deleted = cleanup_service.cleanup_orphaned_s3_files()
                print(f"\n✅ Archivos huérfanos S3 eliminados: {deleted}")
                break
                
            elif choice == "8":
                # Registros sin S3
                deleted = cleanup_service.cleanup_records_without_s3()
                print(f"\n✅ Registros sin S3 eliminados: {deleted}")
                break
                
            else:
                print("❌ Opción inválida. Selecciona 1-8")
                
        except KeyboardInterrupt:
            print("\n❌ Operación cancelada por el usuario")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error en main: {e}")
    
    print("\n✅ Script completado")
    print("📝 Revisa el archivo logs/selective_cleanup.log para más detalles")

if __name__ == "__main__":
    main()
