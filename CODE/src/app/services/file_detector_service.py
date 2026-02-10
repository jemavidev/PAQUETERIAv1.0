"""
Servicio para detectar tipo de archivo (XML o PDF)
"""
import logging
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


class FileDetectorService:
    """
    Detecta el tipo de archivo basándose en extensión y contenido
    """
    
    @staticmethod
    def detect_file_type(file_path: str) -> Literal['XML', 'PDF', 'UNKNOWN']:
        """
        Detecta si un archivo es XML o PDF
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            'XML', 'PDF' o 'UNKNOWN'
        """
        try:
            path = Path(file_path)
            
            # Verificar que el archivo existe
            if not path.exists():
                logger.warning(f"Archivo no encontrado: {file_path}")
                return 'UNKNOWN'
            
            # ESTRATEGIA 1: Por extensión
            extension = path.suffix.lower()
            
            if extension == '.xml':
                logger.info(f"✅ Archivo detectado como XML (por extensión): {path.name}")
                return 'XML'
            elif extension == '.pdf':
                logger.info(f"✅ Archivo detectado como PDF (por extensión): {path.name}")
                return 'PDF'
            
            # ESTRATEGIA 2: Por magic bytes (primeros bytes del archivo)
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(8)
                    
                    # PDF magic bytes: %PDF
                    if header.startswith(b'%PDF'):
                        logger.info(f"✅ Archivo detectado como PDF (por magic bytes): {path.name}")
                        return 'PDF'
                    
                    # XML magic bytes: <?xml o <
                    if header.startswith(b'<?xml') or header.startswith(b'<'):
                        logger.info(f"✅ Archivo detectado como XML (por magic bytes): {path.name}")
                        return 'XML'
            
            except Exception as e:
                logger.warning(f"Error leyendo magic bytes: {e}")
            
            # No se pudo detectar
            logger.warning(f"⚠️ No se pudo detectar el tipo de archivo: {path.name}")
            return 'UNKNOWN'
            
        except Exception as e:
            logger.error(f"❌ Error detectando tipo de archivo: {e}")
            return 'UNKNOWN'
    
    @staticmethod
    def get_file_icon(file_type: str) -> str:
        """
        Retorna el icono SVG apropiado para el tipo de archivo
        
        Args:
            file_type: 'XML', 'PDF' o 'UNKNOWN'
            
        Returns:
            Nombre del icono
        """
        icons = {
            'XML': 'code',      # Icono de código
            'PDF': 'document',  # Icono de documento
            'UNKNOWN': 'question'
        }
        return icons.get(file_type, 'question')
    
    @staticmethod
    def get_file_badge_class(file_type: str) -> str:
        """
        Retorna las clases CSS para el badge del tipo de archivo
        
        Args:
            file_type: 'XML', 'PDF' o 'UNKNOWN'
            
        Returns:
            Clases CSS de Tailwind
        """
        classes = {
            'XML': 'bg-green-100 text-green-800 border-green-200',
            'PDF': 'bg-blue-100 text-blue-800 border-blue-200',
            'UNKNOWN': 'bg-gray-100 text-gray-800 border-gray-200'
        }
        return classes.get(file_type, classes['UNKNOWN'])
