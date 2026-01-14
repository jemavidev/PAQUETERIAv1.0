# ========================================
# PAQUETES EL CLUB - Servicio de Consulta CUFE DIAN
# ========================================
"""
Servicio para consultar y descargar facturas electrónicas
desde el portal de la DIAN usando el código CUFE.
"""

import logging
import re
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class CufeStatus(str, Enum):
    """Estados posibles de un CUFE en el proceso"""
    PENDING = "pending"           # Esperando procesamiento
    WAITING_CAPTCHA = "waiting_captcha"  # Esperando resolución de captcha
    DOWNLOADING = "downloading"   # Descargando PDF
    DOWNLOADED = "downloaded"     # PDF descargado exitosamente
    IMPORTING = "importing"       # Importando a la BD
    IMPORTED = "imported"         # Importado exitosamente
    ERROR = "error"               # Error en el proceso
    NOT_FOUND = "not_found"       # CUFE no encontrado en DIAN


@dataclass
class CufeTask:
    """Representa una tarea de importación de CUFE"""
    cufe: str
    status: CufeStatus = CufeStatus.PENDING
    error_message: Optional[str] = None
    pdf_content: Optional[bytes] = None
    invoice_id: Optional[int] = None
    invoice_number: Optional[str] = None
    supplier_name: Optional[str] = None
    total: Optional[int] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cufe": self.cufe,
            "cufe_short": self.cufe[:20] + "..." if len(self.cufe) > 20 else self.cufe,
            "status": self.status.value,
            "error_message": self.error_message,
            "invoice_id": self.invoice_id,
            "invoice_number": self.invoice_number,
            "supplier_name": self.supplier_name,
            "total": self.total,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DianCufeService:
    """
    Servicio para gestionar la importación de CUFEs desde la DIAN.
    
    El flujo es semi-automático:
    1. Usuario proporciona lista de CUFEs
    2. Sistema genera URLs de consulta
    3. Usuario resuelve captcha en ventana emergente
    4. Sistema descarga el PDF
    5. Sistema importa usando el extractor existente
    """
    
    DIAN_SEARCH_URL = "https://catalogo-vpfe.dian.gov.co/User/SearchDocument"
    DIAN_DOCUMENT_URL = "https://catalogo-vpfe.dian.gov.co/Document/FindDocument"
    
    def __init__(self):
        self.tasks: Dict[str, CufeTask] = {}
    
    @staticmethod
    def validate_cufe(cufe: str) -> Tuple[bool, str]:
        """
        Valida el formato de un CUFE.
        
        Un CUFE válido tiene 96 caracteres hexadecimales.
        Un CUDE (para documentos soporte) también tiene 96 caracteres.
        """
        # Limpiar espacios y caracteres especiales
        cufe_clean = re.sub(r'[^a-fA-F0-9]', '', cufe)
        
        if not cufe_clean:
            return False, "CUFE vacío"
        
        if len(cufe_clean) != 96:
            return False, f"CUFE debe tener 96 caracteres (tiene {len(cufe_clean)})"
        
        if not re.match(r'^[a-fA-F0-9]+$', cufe_clean):
            return False, "CUFE contiene caracteres inválidos"
        
        return True, cufe_clean.lower()
    
    @staticmethod
    def parse_cufe_list(text: str) -> List[Tuple[str, bool, str]]:
        """
        Parsea una lista de CUFEs desde texto.
        
        Acepta:
        - Un CUFE por línea
        - CUFEs separados por comas
        - CUFEs separados por espacios
        
        Returns:
            Lista de tuplas (cufe_original, is_valid, cufe_clean_or_error)
        """
        results = []
        
        # Dividir por líneas, comas o espacios múltiples
        potential_cufes = re.split(r'[\n,\s]+', text.strip())
        
        for cufe in potential_cufes:
            cufe = cufe.strip()
            if not cufe:
                continue
            
            is_valid, result = DianCufeService.validate_cufe(cufe)
            results.append((cufe, is_valid, result))
        
        return results
    
    def create_task(self, cufe: str) -> CufeTask:
        """Crea una nueva tarea de importación"""
        is_valid, result = self.validate_cufe(cufe)
        
        if not is_valid:
            task = CufeTask(
                cufe=cufe,
                status=CufeStatus.ERROR,
                error_message=result
            )
        else:
            task = CufeTask(cufe=result)
        
        self.tasks[task.cufe] = task
        return task
    
    def get_task(self, cufe: str) -> Optional[CufeTask]:
        """Obtiene una tarea por CUFE"""
        # Normalizar CUFE para búsqueda
        _, clean = self.validate_cufe(cufe)
        return self.tasks.get(clean) or self.tasks.get(cufe)
    
    def update_task_status(
        self, 
        cufe: str, 
        status: CufeStatus, 
        error_message: str = None,
        **kwargs
    ) -> Optional[CufeTask]:
        """Actualiza el estado de una tarea"""
        task = self.get_task(cufe)
        if task:
            task.status = status
            task.error_message = error_message
            task.updated_at = datetime.now()
            
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
        
        return task
    
    def get_all_tasks(self) -> List[CufeTask]:
        """Obtiene todas las tareas"""
        return list(self.tasks.values())
    
    def clear_tasks(self):
        """Limpia todas las tareas"""
        self.tasks.clear()
    
    def get_dian_search_url(self, cufe: str) -> str:
        """Genera la URL de búsqueda en la DIAN para un CUFE"""
        return f"{self.DIAN_SEARCH_URL}?DocumentKey={cufe}"
    
    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas de las tareas"""
        stats = {
            "total": len(self.tasks),
            "pending": 0,
            "waiting_captcha": 0,
            "downloading": 0,
            "downloaded": 0,
            "importing": 0,
            "imported": 0,
            "error": 0,
            "not_found": 0,
        }
        
        for task in self.tasks.values():
            stats[task.status.value] = stats.get(task.status.value, 0) + 1
        
        return stats


# Instancia global del servicio (para mantener estado entre requests)
_cufe_service_instance: Optional[DianCufeService] = None


def get_cufe_service() -> DianCufeService:
    """Obtiene la instancia global del servicio"""
    global _cufe_service_instance
    if _cufe_service_instance is None:
        _cufe_service_instance = DianCufeService()
    return _cufe_service_instance
