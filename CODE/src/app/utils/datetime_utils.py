# ========================================
# PAQUETES EL CLUB v1.0 - Utilidades de Fecha y Hora
# ========================================
# Archivo: CODE/LOCAL/src/app/utils/datetime_utils.py (siguiendo reglas de AGENTS.md)
# Versión: 1.0.0
# Fecha: 2025-01-24
# Autor: Equipo de Desarrollo
# ========================================

from datetime import datetime, timezone, timedelta
from typing import Optional

def get_colombia_now() -> datetime:
    """
    Obtener la fecha y hora actual en zona horaria de Colombia (UTC-5)

    Returns:
        datetime: Fecha y hora actual en zona horaria de Colombia
    """
    # Colombia está en UTC-5
    colombia_offset = timezone(timedelta(hours=-5))
    return datetime.now(colombia_offset)

def get_colombia_datetime(date_str: Optional[str] = None) -> datetime:
    """
    Convertir string de fecha a datetime en zona horaria de Colombia

    Args:
        date_str: String de fecha en formato ISO (opcional)

    Returns:
        datetime: Fecha y hora en zona horaria de Colombia
    """
    if date_str:
        # Parsear la fecha del string
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    else:
        dt = datetime.utcnow()

    # Convertir a zona horaria de Colombia
    colombia_offset = timezone(timedelta(hours=-5))
    return dt.astimezone(colombia_offset)

def format_colombia_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formatear datetime en zona horaria de Colombia

    Args:
        dt: Objeto datetime
        format_str: Formato de salida (por defecto: YYYY-MM-DD HH:MM:SS)

    Returns:
        str: Fecha formateada
    """
    if dt.tzinfo is None:
        # Si no tiene zona horaria, asumir UTC y convertir a Colombia
        dt = dt.replace(tzinfo=timezone.utc)

    colombia_offset = timezone(timedelta(hours=-5))
    colombia_dt = dt.astimezone(colombia_offset)

    return colombia_dt.strftime(format_str)

def get_colombia_date() -> str:
    """
    Obtener la fecha actual en Colombia en formato YYYY-MM-DD

    Returns:
        str: Fecha en formato YYYY-MM-DD
    """
    return get_colombia_now().strftime("%Y-%m-%d")

def get_colombia_time() -> str:
    """
    Obtener la hora actual en Colombia en formato HH:MM:SS

    Returns:
        str: Hora en formato HH:MM:SS
    """
    return get_colombia_now().strftime("%H:%M:%S")

def get_colombia_timestamp() -> float:
    """
    Obtener timestamp Unix actual en zona horaria de Colombia

    Returns:
        float: Timestamp Unix
    """
    return get_colombia_now().timestamp()

def is_business_hour() -> bool:
    """
    Verificar si la hora actual está dentro del horario laboral colombiano
    (Lunes a Viernes, 8:00 AM - 6:00 PM)

    Returns:
        bool: True si está en horario laboral
    """
    now = get_colombia_now()
    weekday = now.weekday()  # 0 = Lunes, 6 = Domingo
    hour = now.hour

    # Lunes a Viernes (0-4), entre 8:00 y 18:00
    return weekday < 5 and 8 <= hour < 18

def get_business_days_from_now(days: int) -> datetime:
    """
    Calcular fecha sumando días hábiles desde ahora

    Args:
        days: Número de días hábiles a sumar

    Returns:
        datetime: Fecha resultante
    """
    current = get_colombia_now()
    added_days = 0
    while added_days < days:
        current = current + timedelta(days=1)
        if current.weekday() < 5:  # Lunes a Viernes
            added_days += 1
    return current