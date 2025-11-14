# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Migración de Números de Teléfono
Script para normalizar todos los números de teléfono a formato internacional

Convierte todos los teléfonos a formato: +[código país][número]
Por defecto agrega +57 (Colombia) a números sin código de país

Uso:
    # Modo dry-run (solo muestra cambios sin aplicarlos)
    python -m scripts.migrate_phone_numbers --dry-run
    
    # Aplicar cambios reales
    python -m scripts.migrate_phone_numbers
    
    # Aplicar solo a un cliente específico
    python -m scripts.migrate_phone_numbers --customer-id <uuid>

@version 1.0.0
@date 2025-11-14
@author Equipo de Desarrollo
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import logging
from datetime import datetime
from typing import List, Dict, Tuple
from uuid import UUID

# Configurar entorno para evitar validaciones de AWS
os.environ.setdefault('ENVIRONMENT', 'development')
os.environ.setdefault('AWS_ACCESS_KEY_ID', 'dummy')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'dummy')
os.environ.setdefault('AWS_S3_BUCKET', 'dummy')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from app.database import get_db, engine
from app.models.customer import Customer
from app.utils.phone_utils import normalize_phone, validate_phone

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'phone_migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PhoneMigration:
    """Clase para manejar la migración de números de teléfono"""
    
    def __init__(self, session: Session, dry_run: bool = False):
        self.session = session
        self.dry_run = dry_run
        self.stats = {
            'total': 0,
            'normalized': 0,
            'already_normalized': 0,
            'invalid': 0,
            'skipped': 0,
            'errors': 0
        }
        self.changes: List[Dict] = []
        self.errors: List[Dict] = []
    
    def is_already_normalized(self, phone: str) -> bool:
        """Verifica si un teléfono ya está normalizado"""
        if not phone:
            return False
        
        # Un teléfono normalizado debe:
        # 1. Empezar con +
        # 2. Tener solo dígitos después del +
        # 3. Tener entre 11 y 16 caracteres totales (+XX XXXXXXXXXX)
        
        if not phone.startswith('+'):
            return False
        
        digits = phone[1:]
        if not digits.isdigit():
            return False
        
        if len(digits) < 10 or len(digits) > 15:
            return False
        
        return True
    
    def migrate_customer_phone(self, customer: Customer) -> Tuple[bool, str]:
        """
        Migra el teléfono de un cliente
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            original_phone = customer.phone
            
            if not original_phone:
                self.stats['skipped'] += 1
                return False, "Sin teléfono"
            
            # Verificar si ya está normalizado
            if self.is_already_normalized(original_phone):
                self.stats['already_normalized'] += 1
                logger.debug(f"Cliente {customer.id} - Teléfono ya normalizado: {original_phone}")
                return False, f"Ya normalizado: {original_phone}"
            
            # Normalizar
            normalized_phone = normalize_phone(original_phone)
            
            if not normalized_phone:
                self.stats['invalid'] += 1
                error_msg = f"No se pudo normalizar: {original_phone}"
                logger.warning(f"Cliente {customer.id} - {error_msg}")
                self.errors.append({
                    'customer_id': str(customer.id),
                    'customer_name': customer.full_name,
                    'original_phone': original_phone,
                    'error': 'No se pudo normalizar'
                })
                return False, error_msg
            
            # Validar el teléfono normalizado
            if not validate_phone(normalized_phone):
                self.stats['invalid'] += 1
                error_msg = f"Teléfono inválido después de normalizar: {original_phone} → {normalized_phone}"
                logger.warning(f"Cliente {customer.id} - {error_msg}")
                self.errors.append({
                    'customer_id': str(customer.id),
                    'customer_name': customer.full_name,
                    'original_phone': original_phone,
                    'normalized_phone': normalized_phone,
                    'error': 'Inválido después de normalizar'
                })
                return False, error_msg
            
            # Si no hay cambio, no hacer nada
            if original_phone == normalized_phone:
                self.stats['already_normalized'] += 1
                logger.debug(f"Cliente {customer.id} - Sin cambios: {original_phone}")
                return False, f"Sin cambios: {original_phone}"
            
            # Registrar el cambio
            change = {
                'customer_id': str(customer.id),
                'customer_name': customer.full_name,
                'original_phone': original_phone,
                'normalized_phone': normalized_phone
            }
            self.changes.append(change)
            
            # Aplicar el cambio (si no es dry-run)
            if not self.dry_run:
                customer.phone = normalized_phone
                self.session.flush()
            
            self.stats['normalized'] += 1
            logger.info(f"✅ Cliente {customer.id} ({customer.full_name}): {original_phone} → {normalized_phone}")
            return True, f"{original_phone} → {normalized_phone}"
            
        except Exception as e:
            self.stats['errors'] += 1
            error_msg = f"Error al procesar: {str(e)}"
            logger.error(f"❌ Cliente {customer.id} - {error_msg}", exc_info=True)
            self.errors.append({
                'customer_id': str(customer.id),
                'customer_name': customer.full_name if customer else 'Desconocido',
                'original_phone': original_phone if 'original_phone' in locals() else 'N/A',
                'error': str(e)
            })
            return False, error_msg
    
    def migrate_all_customers(self, customer_id: str = None):
        """Migra todos los clientes o uno específico"""
        try:
            logger.info("=" * 80)
            logger.info("INICIANDO MIGRACIÓN DE NÚMEROS DE TELÉFONO")
            logger.info("=" * 80)
            logger.info(f"Modo: {'DRY-RUN (no se aplicarán cambios)' if self.dry_run else 'PRODUCCIÓN (se aplicarán cambios)'}")
            logger.info("")
            
            # Obtener clientes
            if customer_id:
                logger.info(f"Migrando cliente específico: {customer_id}")
                customers = self.session.query(Customer).filter(Customer.id == UUID(customer_id)).all()
            else:
                logger.info("Migrando todos los clientes...")
                customers = self.session.query(Customer).all()
            
            self.stats['total'] = len(customers)
            logger.info(f"Total de clientes a procesar: {self.stats['total']}")
            logger.info("")
            
            # Procesar cada cliente
            for i, customer in enumerate(customers, 1):
                logger.debug(f"Procesando {i}/{self.stats['total']}: {customer.full_name} ({customer.id})")
                self.migrate_customer_phone(customer)
            
            # Commit si no es dry-run
            if not self.dry_run and self.stats['normalized'] > 0:
                self.session.commit()
                logger.info("")
                logger.info("✅ Cambios guardados en la base de datos")
            elif self.dry_run:
                self.session.rollback()
                logger.info("")
                logger.info("ℹ️  Modo DRY-RUN: No se guardaron cambios")
            
            # Mostrar resumen
            self.print_summary()
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Error crítico durante la migración: {str(e)}", exc_info=True)
            raise
    
    def print_summary(self):
        """Imprime el resumen de la migración"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("RESUMEN DE LA MIGRACIÓN")
        logger.info("=" * 80)
        logger.info(f"Total de clientes procesados:    {self.stats['total']}")
        logger.info(f"Teléfonos normalizados:          {self.stats['normalized']}")
        logger.info(f"Ya estaban normalizados:         {self.stats['already_normalized']}")
        logger.info(f"Teléfonos inválidos:             {self.stats['invalid']}")
        logger.info(f"Sin teléfono (omitidos):         {self.stats['skipped']}")
        logger.info(f"Errores:                         {self.stats['errors']}")
        logger.info("=" * 80)
        
        # Mostrar cambios detallados
        if self.changes:
            logger.info("")
            logger.info("CAMBIOS APLICADOS:")
            logger.info("-" * 80)
            for change in self.changes:
                logger.info(f"  • {change['customer_name']} ({change['customer_id'][:8]}...)")
                logger.info(f"    {change['original_phone']} → {change['normalized_phone']}")
        
        # Mostrar errores detallados
        if self.errors:
            logger.info("")
            logger.info("ERRORES ENCONTRADOS:")
            logger.info("-" * 80)
            for error in self.errors:
                logger.info(f"  • {error['customer_name']} ({error['customer_id'][:8]}...)")
                logger.info(f"    Teléfono: {error['original_phone']}")
                logger.info(f"    Error: {error['error']}")
        
        logger.info("")
        
        if self.dry_run:
            logger.info("⚠️  RECORDATORIO: Esto fue un DRY-RUN. Para aplicar los cambios, ejecuta sin --dry-run")
        elif self.stats['normalized'] > 0:
            logger.info("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        else:
            logger.info("ℹ️  No se requirieron cambios")
        
        logger.info("=" * 80)


def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(
        description='Migrar números de teléfono a formato internacional',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Modo dry-run (solo muestra cambios sin aplicarlos)
  python -m scripts.migrate_phone_numbers --dry-run
  
  # Aplicar cambios reales
  python -m scripts.migrate_phone_numbers
  
  # Migrar un cliente específico
  python -m scripts.migrate_phone_numbers --customer-id <uuid>
  
  # Dry-run de un cliente específico
  python -m scripts.migrate_phone_numbers --dry-run --customer-id <uuid>
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Ejecutar en modo prueba (no aplica cambios)'
    )
    
    parser.add_argument(
        '--customer-id',
        type=str,
        help='ID del cliente específico a migrar (opcional)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostrar información detallada (modo debug)'
    )
    
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Confirmar automáticamente sin solicitar confirmación interactiva'
    )
    
    args = parser.parse_args()
    
    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Confirmar antes de ejecutar en modo producción
    if not args.dry_run:
        logger.warning("")
        logger.warning("⚠️  ADVERTENCIA: Estás a punto de modificar la base de datos en MODO PRODUCCIÓN")
        logger.warning("⚠️  Se cambiarán PERMANENTEMENTE los números de teléfono")
        logger.warning("")
        
        if not args.yes:
            response = input("¿Estás seguro de que deseas continuar? (escribe 'SI' para confirmar): ")
            
            if response.strip().upper() != 'SI':
                logger.info("❌ Migración cancelada por el usuario")
                return 1
        
        logger.info("")
        logger.info("✅ Confirmación recibida. Iniciando migración...")
        logger.info("")
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # Crear instancia de migración
        migration = PhoneMigration(session=db, dry_run=args.dry_run)
        
        # Ejecutar migración
        migration.migrate_all_customers(customer_id=args.customer_id)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("")
        logger.warning("⚠️  Migración interrumpida por el usuario")
        db.rollback()
        return 130
        
    except Exception as e:
        logger.error(f"❌ Error fatal: {str(e)}", exc_info=True)
        db.rollback()
        return 1
        
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())

