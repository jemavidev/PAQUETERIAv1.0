# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Tareas Programadas
Versión: 1.0.0
Fecha: 2026-01-09
Autor: Equipo de Desarrollo

Tareas que se ejecutan automáticamente en intervalos definidos.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.database import SessionLocal
from app.config import settings

logger = logging.getLogger(__name__)

# Configuración de tareas
CLEANUP_ANNOUNCEMENTS_DAYS = 15  # Días para considerar un anuncio como antiguo
CLEANUP_INTERVAL_HOURS = 24  # Ejecutar cada 24 horas


class ScheduledTasksService:
    """
    Servicio para ejecutar tareas programadas en background.
    """
    
    _instance: Optional['ScheduledTasksService'] = None
    _running: bool = False
    _task: Optional[asyncio.Task] = None
    
    @classmethod
    def get_instance(cls) -> 'ScheduledTasksService':
        """Obtener instancia singleton"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def cleanup_old_announcements(self):
        """
        Eliminar anuncios pendientes con más de X días.
        Solo elimina anuncios que NO han sido procesados (is_processed = False).
        """
        db = SessionLocal()
        try:
            from sqlalchemy import text
            
            cutoff_date = datetime.now() - timedelta(days=CLEANUP_ANNOUNCEMENTS_DAYS)
            
            logger.info(f"🧹 [SCHEDULED] Iniciando limpieza de anuncios > {CLEANUP_ANNOUNCEMENTS_DAYS} días")
            logger.info(f"📅 Fecha límite: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Contar anuncios a eliminar
            count_query = text("""
                SELECT COUNT(*) FROM package_announcements_new 
                WHERE is_processed = false AND announced_at < :cutoff_date
            """)
            result = db.execute(count_query, {"cutoff_date": cutoff_date})
            count = result.scalar()
            
            if count == 0:
                logger.info("✅ [SCHEDULED] No hay anuncios antiguos para eliminar")
                return {"deleted": 0}
            
            logger.info(f"🗑️ [SCHEDULED] Eliminando {count} anuncios antiguos...")
            
            # Eliminar anuncios antiguos
            delete_query = text("""
                DELETE FROM package_announcements_new 
                WHERE is_processed = false AND announced_at < :cutoff_date
            """)
            result = db.execute(delete_query, {"cutoff_date": cutoff_date})
            db.commit()
            
            deleted = result.rowcount
            logger.info(f"✅ [SCHEDULED] Limpieza completada: {deleted} anuncios eliminados")
            
            return {"deleted": deleted}
            
        except Exception as e:
            logger.error(f"❌ [SCHEDULED] Error en limpieza de anuncios: {str(e)}")
            db.rollback()
            return {"deleted": 0, "error": str(e)}
        finally:
            db.close()
    
    async def _run_scheduled_tasks(self):
        """Loop principal de tareas programadas"""
        logger.info("🚀 [SCHEDULED] Iniciando servicio de tareas programadas")
        
        # Esperar 60 segundos antes de la primera ejecución
        # para dar tiempo a que la app se inicialice completamente
        await asyncio.sleep(60)
        
        while self._running:
            try:
                # Ejecutar limpieza de anuncios
                await self.cleanup_old_announcements()
                
                # Esperar hasta la próxima ejecución
                logger.info(f"⏰ [SCHEDULED] Próxima ejecución en {CLEANUP_INTERVAL_HOURS} horas")
                await asyncio.sleep(CLEANUP_INTERVAL_HOURS * 3600)
                
            except asyncio.CancelledError:
                logger.info("🛑 [SCHEDULED] Tareas programadas canceladas")
                break
            except Exception as e:
                logger.error(f"❌ [SCHEDULED] Error en loop de tareas: {str(e)}")
                # Esperar 1 hora antes de reintentar en caso de error
                await asyncio.sleep(3600)
    
    def start(self):
        """Iniciar el servicio de tareas programadas"""
        if self._running:
            logger.warning("⚠️ [SCHEDULED] El servicio ya está corriendo")
            return
        
        self._running = True
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._task = asyncio.create_task(self._run_scheduled_tasks())
            else:
                logger.warning("⚠️ [SCHEDULED] No hay event loop corriendo, no se pueden iniciar tareas")
        except Exception as e:
            logger.error(f"❌ [SCHEDULED] Error iniciando tareas: {str(e)}")
            self._running = False
    
    def stop(self):
        """Detener el servicio de tareas programadas"""
        logger.info("🛑 [SCHEDULED] Deteniendo servicio de tareas programadas")
        self._running = False
        
        if self._task:
            self._task.cancel()
            self._task = None


# Función helper para iniciar desde main.py
def start_scheduled_tasks():
    """Iniciar tareas programadas (llamar desde startup de FastAPI)"""
    service = ScheduledTasksService.get_instance()
    service.start()


def stop_scheduled_tasks():
    """Detener tareas programadas (llamar desde shutdown de FastAPI)"""
    service = ScheduledTasksService.get_instance()
    service.stop()
