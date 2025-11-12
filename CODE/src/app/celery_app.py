# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Configuración de Celery
Versión: 1.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from celery import Celery
from .config import settings

# Crear aplicación Celery
celery_app = Celery(
    "paqueteria_v4",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"]
)

# Configuración de Celery
celery_app.conf.update(
    # Configuración básica
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Bogota",
    enable_utc=True,

    # Configuración de tareas
    task_routes={
        "app.tasks.generate_report": {"queue": "reports"},
        "app.tasks.send_bulk_sms": {"queue": "sms"},
        "app.tasks.process_file_upload": {"queue": "files"},
        "app.tasks.cleanup_old_data": {"queue": "maintenance"},
    },

    # Configuración de colas
    task_default_queue="default",
    task_queues={
        "reports": {"exchange": "reports", "routing_key": "reports"},
        "sms": {"exchange": "sms", "routing_key": "sms"},
        "files": {"exchange": "files", "routing_key": "files"},
        "maintenance": {"exchange": "maintenance", "routing_key": "maintenance"},
    },

    # Configuración de resultados
    result_expires=3600,  # 1 hora
    task_ignore_result=False,

    # Configuración de workers
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,

    # Configuración de logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",

    # Configuración de beat (tareas programadas)
    beat_schedule={
        "cleanup-old-reports": {
            "task": "app.tasks.cleanup_old_reports",
            "schedule": 86400.0,  # Cada 24 horas
        },
        "cleanup-temp-files": {
            "task": "app.tasks.cleanup_temp_files",
            "schedule": 3600.0,  # Cada hora
        },
        "update-dashboard-metrics": {
            "task": "app.tasks.update_dashboard_metrics",
            "schedule": 300.0,  # Cada 5 minutos
        },
    },
)

# Configuración específica para desarrollo/producción
if settings.environment == "development":
    celery_app.conf.update(
        worker_log_level="INFO",
        task_always_eager=False,  # Ejecutar tareas de forma asíncrona
    )
else:
    celery_app.conf.update(
        worker_log_level="WARNING",
        task_always_eager=False,
    )

# Función para crear tareas programadas dinámicamente
def setup_periodic_tasks(sender, **kwargs):
    """Configurar tareas programadas dinámicamente"""
    try:
        from .tasks import send_daily_reminders
        # Tarea de ejemplo: enviar recordatorios diarios
        sender.add_periodic_task(
            86400.0,  # Cada 24 horas
            send_daily_reminders.s(),
            name="send-daily-reminders"
        )
    except ImportError:
        # Si la tarea no existe, simplemente no agregarla
        pass

# Conectar la función de configuración
from celery.signals import celeryd_init
celeryd_init.connect(setup_periodic_tasks)

if __name__ == "__main__":
    celery_app.start()