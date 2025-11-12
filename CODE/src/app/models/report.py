# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Modelos de Reportes
Versión: 1.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Float, Enum, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
from src.app.utils.datetime_utils import get_colombia_now
import enum
import uuid


class ReportType(str, enum.Enum):
    """Tipos de reportes disponibles"""
    PACKAGES_SUMMARY = "packages_summary"
    CUSTOMERS_ANALYSIS = "customers_analysis"
    REVENUE_REPORT = "revenue_report"
    PERFORMANCE_METRICS = "performance_metrics"
    SMS_ANALYTICS = "sms_analytics"
    MESSAGES_REPORT = "messages_report"
    CUSTOM_REPORT = "custom_report"


class ReportStatus(str, enum.Enum):
    """Estados de generación de reportes"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportFormat(str, enum.Enum):
    """Formatos de exportación disponibles"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"


class Report(Base):
    """Modelo principal de reportes generados"""
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    format = Column(Enum(ReportFormat), default=ReportFormat.PDF)

    # Parámetros del reporte
    parameters = Column(JSON, nullable=True)  # Filtros, fechas, etc.

    # Resultados
    data = Column(JSON, nullable=True)  # Datos del reporte
    summary = Column(JSON, nullable=True)  # Resumen estadístico

    # Archivos generados
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # En bytes

    # Metadata
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=get_colombia_now)
    completed_at = Column(DateTime, nullable=True)
    processing_time = Column(Float, nullable=True)  # En segundos

    # Relaciones
    created_by = relationship("User", back_populates="reports")

    def __repr__(self):
        return f"<Report {self.title} - {self.report_type.value}>"


class ReportTemplate(Base):
    """Plantillas predefinidas de reportes"""
    __tablename__ = "report_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)

    # Configuración de la plantilla
    default_parameters = Column(JSON, nullable=True)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Metadata
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=get_colombia_now)
    updated_at = Column(DateTime, default=get_colombia_now, onupdate=get_colombia_now)

    # Relaciones
    created_by = relationship("User", back_populates="report_templates")

    def __repr__(self):
        return f"<ReportTemplate {self.name} - {self.report_type.value}>"


class DashboardMetric(Base):
    """Métricas calculadas para dashboards"""
    __tablename__ = "dashboard_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(100), nullable=False, unique=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)  # %, COP, unidades, etc.

    # Categorización
    category = Column(String(50), nullable=False)  # packages, customers, revenue, etc.
    subcategory = Column(String(50), nullable=True)

    # Periodo
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Metadata
    calculated_at = Column(DateTime, default=get_colombia_now)
    data_source = Column(String(100), nullable=True)  # Tabla o query que generó la métrica

    def __repr__(self):
        return f"<DashboardMetric {self.metric_name}: {self.metric_value} {self.metric_unit}>"


class ReportSchedule(Base):
    """Programación automática de reportes"""
    __tablename__ = "report_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Configuración del reporte
    report_type = Column(Enum(ReportType), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("report_templates.id"), nullable=True)
    parameters = Column(JSON, nullable=True)

    # Programación
    schedule_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    schedule_config = Column(JSON, nullable=True)  # Configuración específica (día de la semana, etc.)
    next_run = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # Destinatarios
    recipients = Column(JSON, nullable=True)  # Lista de emails para envío automático

    # Metadata
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=get_colombia_now)
    last_run = Column(DateTime, nullable=True)

    # Relaciones
    template = relationship("ReportTemplate", backref="schedules")
    created_by = relationship("User", back_populates="report_schedules")

    def __repr__(self):
        return f"<ReportSchedule {self.name} - {self.schedule_type}>"