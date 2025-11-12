# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Monitor de Estados
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Sistema de monitoreo para detectar inconsistencias de estado.
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.package_status_service import PackageStatusService
from app.services.nomenclature_service import NomenclatureService
from app.database import get_db


# Configurar logger específico para monitoreo de estados
status_logger = logging.getLogger("status_monitor")
status_logger.setLevel(logging.INFO)

# Handler para archivo de logs de estado
status_handler = logging.FileHandler("logs/status_inconsistencies.log")
status_handler.setLevel(logging.INFO)

# Formato de logs
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
status_handler.setFormatter(formatter)
status_logger.addHandler(status_handler)


class StatusMonitor:
    """
    Monitor para detectar y registrar inconsistencias de estado.
    """
    
    def __init__(self):
        self.inconsistencies_count = 0
        self.last_check = None
    
    def log_status_inconsistency(
        self, 
        tracking_code: str, 
        expected_status: str, 
        actual_status: str, 
        endpoint: str = None,
        additional_info: Dict[str, Any] = None
    ):
        """
        Registrar una inconsistencia de estado.
        
        Args:
            tracking_code: Código de seguimiento
            expected_status: Estado esperado
            actual_status: Estado actual
            endpoint: Endpoint donde se detectó
            additional_info: Información adicional
        """
        self.inconsistencies_count += 1
        
        log_data = {
            "type": "status_inconsistency",
            "tracking_code": tracking_code,
            "expected_status": expected_status,
            "actual_status": actual_status,
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat(),
            "additional_info": additional_info or {}
        }
        
        status_logger.warning(f"Status inconsistency detected: {json.dumps(log_data)}")
    
    def log_nomenclature_issue(
        self,
        identifier: str,
        issue_type: str,
        description: str,
        endpoint: str = None
    ):
        """
        Registrar un problema de nomenclatura.
        
        Args:
            identifier: Identificador problemático
            issue_type: Tipo de problema
            description: Descripción del problema
            endpoint: Endpoint donde se detectó
        """
        log_data = {
            "type": "nomenclature_issue",
            "identifier": identifier,
            "issue_type": issue_type,
            "description": description,
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat()
        }
        
        status_logger.warning(f"Nomenclature issue detected: {json.dumps(log_data)}")
    
    def check_system_consistency(self, db: Session) -> Dict[str, Any]:
        """
        Verificar la consistencia del sistema completo.
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Reporte de consistencia
        """
        self.last_check = datetime.now()
        
        # Obtener reporte de nomenclatura
        nomenclature_report = NomenclatureService.get_nomenclature_report(db)
        
        # Verificar duplicados de tracking_code
        duplicates = nomenclature_report["duplicate_tracking_codes"]
        if duplicates:
            for duplicate in duplicates:
                self.log_nomenclature_issue(
                    identifier=duplicate,
                    issue_type="duplicate_tracking_code",
                    description=f"Tracking code {duplicate} exists in both packages and announcements"
                )
        
        # Generar reporte
        report = {
            "check_timestamp": self.last_check.isoformat(),
            "inconsistencies_found": self.inconsistencies_count,
            "nomenclature_report": nomenclature_report,
            "system_health": "healthy" if self.inconsistencies_count == 0 else "issues_detected"
        }
        
        status_logger.info(f"System consistency check completed: {json.dumps(report)}")
        
        return report
    
    def get_inconsistency_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Obtener estadísticas de inconsistencias de las últimas horas.
        
        Args:
            hours: Número de horas a revisar
            
        Returns:
            Estadísticas de inconsistencias
        """
        # Leer logs de las últimas horas
        since = datetime.now() - timedelta(hours=hours)
        
        inconsistencies = []
        nomenclature_issues = []
        
        try:
            with open("logs/status_inconsistencies.log", "r") as f:
                for line in f:
                    if "status_inconsistency" in line or "nomenclature_issue" in line:
                        try:
                            # Extraer JSON del log
                            json_start = line.find('{"type":')
                            if json_start != -1:
                                json_data = json.loads(line[json_start:])
                                log_time = datetime.fromisoformat(json_data["timestamp"])
                                
                                if log_time >= since:
                                    if json_data["type"] == "status_inconsistency":
                                        inconsistencies.append(json_data)
                                    elif json_data["type"] == "nomenclature_issue":
                                        nomenclature_issues.append(json_data)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
        except FileNotFoundError:
            pass
        
        return {
            "period_hours": hours,
            "since": since.isoformat(),
            "status_inconsistencies": {
                "count": len(inconsistencies),
                "details": inconsistencies
            },
            "nomenclature_issues": {
                "count": len(nomenclature_issues),
                "details": nomenclature_issues
            },
            "total_issues": len(inconsistencies) + len(nomenclature_issues)
        }
    
    def validate_endpoint_response(
        self,
        endpoint: str,
        tracking_code: str,
        response_data: Dict[str, Any],
        db: Session
    ) -> bool:
        """
        Validar que la respuesta de un endpoint sea consistente.
        
        Args:
            endpoint: Nombre del endpoint
            tracking_code: Código de seguimiento
            response_data: Datos de respuesta
            db: Sesión de base de datos
            
        Returns:
            True si es consistente, False si hay problemas
        """
        try:
            # Obtener estado correcto usando el servicio centralizado
            effective_status = PackageStatusService.get_effective_status(db, tracking_code)
            expected_status = effective_status["status"]
            
            # Verificar estado en respuesta
            actual_status = response_data.get("current_status")
            
            if actual_status != expected_status:
                self.log_status_inconsistency(
                    tracking_code=tracking_code,
                    expected_status=expected_status,
                    actual_status=actual_status,
                    endpoint=endpoint,
                    additional_info={
                        "allows_inquiries_expected": effective_status["allows_inquiries"],
                        "allows_inquiries_actual": response_data.get("inquiry_info", {}).get("allows_inquiries")
                    }
                )
                return False
            
            # Verificar permisos de consulta
            expected_allows = effective_status["allows_inquiries"]
            actual_allows = response_data.get("inquiry_info", {}).get("allows_inquiries", False)
            
            if expected_allows != actual_allows:
                self.log_status_inconsistency(
                    tracking_code=tracking_code,
                    expected_status=f"allows_inquiries={expected_allows}",
                    actual_status=f"allows_inquiries={actual_allows}",
                    endpoint=endpoint
                )
                return False
            
            return True
            
        except Exception as e:
            status_logger.error(f"Error validating endpoint response: {e}")
            return False


# Instancia global del monitor
status_monitor = StatusMonitor()


def setup_status_monitoring():
    """
    Configurar el sistema de monitoreo de estados.
    """
    import os
    
    # Crear directorio de logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    status_logger.info("Status monitoring system initialized")


def get_status_monitor() -> StatusMonitor:
    """
    Obtener la instancia del monitor de estados.
    
    Returns:
        Instancia del StatusMonitor
    """
    return status_monitor


# Decorator para monitoreo automático
def monitor_status_consistency(func):
    """
    Decorador para monitorear automáticamente la consistencia de estados.
    """
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        
        # Intentar extraer información para validación
        try:
            if isinstance(result, dict) and result.get("success"):
                # Buscar tracking_code en el resultado
                tracking_code = None
                if "announcement" in result and result["announcement"]:
                    tracking_code = result["announcement"].get("tracking_code")
                
                if tracking_code:
                    # Obtener db de kwargs
                    db = kwargs.get("db")
                    if db:
                        # Validar consistencia
                        endpoint_name = func.__name__
                        status_monitor.validate_endpoint_response(
                            endpoint=endpoint_name,
                            tracking_code=tracking_code,
                            response_data=result,
                            db=db
                        )
        except Exception as e:
            status_logger.error(f"Error in status monitoring decorator: {e}")
        
        return result
    
    return wrapper
