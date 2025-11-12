# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Esquemas de Reportes
Versión: 1.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from app.models.report import ReportType, ReportStatus, ReportFormat


# === ESQUEMAS BASE ===

class ReportBase(BaseModel):
    """Esquema base para reportes"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    report_type: ReportType
    format: ReportFormat = ReportFormat.PDF
    parameters: Optional[Dict[str, Any]] = None


class ReportTemplateBase(BaseModel):
    """Esquema base para plantillas de reportes"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    report_type: ReportType
    default_parameters: Optional[Dict[str, Any]] = None
    is_default: bool = False
    is_active: bool = True


class DashboardMetricBase(BaseModel):
    """Esquema base para métricas de dashboard"""
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: float
    metric_unit: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=50)
    subcategory: Optional[str] = None
    period_start: datetime
    period_end: datetime
    data_source: Optional[str] = None


class ReportScheduleBase(BaseModel):
    """Esquema base para programación de reportes"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    report_type: ReportType
    template_id: Optional[UUID] = None
    parameters: Optional[Dict[str, Any]] = None
    schedule_type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    schedule_config: Optional[Dict[str, Any]] = None
    next_run: datetime
    is_active: bool = True
    recipients: Optional[List[str]] = None


# === ESQUEMAS DE CREACIÓN ===

class ReportCreate(ReportBase):
    """Esquema para crear un reporte"""
    pass


class ReportTemplateCreate(ReportTemplateBase):
    """Esquema para crear una plantilla de reporte"""
    pass


class DashboardMetricCreate(DashboardMetricBase):
    """Esquema para crear una métrica de dashboard"""
    pass


class ReportScheduleCreate(ReportScheduleBase):
    """Esquema para crear una programación de reporte"""
    pass


# === ESQUEMAS DE ACTUALIZACIÓN ===

class ReportUpdate(BaseModel):
    """Esquema para actualizar un reporte"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ReportStatus] = None
    parameters: Optional[Dict[str, Any]] = None


class ReportTemplateUpdate(BaseModel):
    """Esquema para actualizar una plantilla de reporte"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    default_parameters: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class ReportScheduleUpdate(BaseModel):
    """Esquema para actualizar una programación de reporte"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    schedule_config: Optional[Dict[str, Any]] = None
    next_run: Optional[datetime] = None
    is_active: Optional[bool] = None
    recipients: Optional[List[str]] = None


# === ESQUEMAS DE RESPUESTA ===

class ReportResponse(ReportBase):
    """Esquema de respuesta para reportes"""
    id: UUID
    status: ReportStatus
    data: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    created_by_id: Optional[UUID] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None

    class Config:
        from_attributes = True


class ReportTemplateResponse(ReportTemplateBase):
    """Esquema de respuesta para plantillas de reportes"""
    id: UUID
    created_by_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DashboardMetricResponse(DashboardMetricBase):
    """Esquema de respuesta para métricas de dashboard"""
    id: UUID
    calculated_at: datetime

    class Config:
        from_attributes = True


class ReportScheduleResponse(ReportScheduleBase):
    """Esquema de respuesta para programaciones de reportes"""
    id: UUID
    created_by_id: Optional[UUID] = None
    created_at: datetime
    last_run: Optional[datetime] = None

    class Config:
        from_attributes = True


# === ESQUEMAS DE LISTADO ===

class ReportListResponse(BaseModel):
    """Esquema de respuesta para lista de reportes"""
    reports: List[ReportResponse]
    total: int
    skip: int = 0
    limit: int = 50


class ReportTemplateListResponse(BaseModel):
    """Esquema de respuesta para lista de plantillas"""
    templates: List[ReportTemplateResponse]
    total: int


class DashboardMetricsResponse(BaseModel):
    """Esquema de respuesta para métricas de dashboard"""
    metrics: List[DashboardMetricResponse]
    total: int
    period_start: datetime
    period_end: datetime


class ReportScheduleListResponse(BaseModel):
    """Esquema de respuesta para lista de programaciones"""
    schedules: List[ReportScheduleResponse]
    total: int


# === ESQUEMAS ESPECÍFICOS PARA REPORTES ===

class ReportGenerationRequest(BaseModel):
    """Esquema para solicitar generación de reporte"""
    report_type: ReportType
    format: ReportFormat = ReportFormat.PDF
    parameters: Optional[Dict[str, Any]] = None
    template_id: Optional[UUID] = None


class ReportGenerationResponse(BaseModel):
    """Esquema de respuesta para generación de reporte"""
    report_id: UUID
    status: ReportStatus
    estimated_time: Optional[int] = None  # En segundos
    message: str


class ReportDownloadResponse(BaseModel):
    """Esquema de respuesta para descarga de reporte"""
    report_id: UUID
    file_url: str
    file_name: str
    file_size: int
    content_type: str


# === ESQUEMAS DE ESTADÍSTICAS ===

class ReportStatistics(BaseModel):
    """Estadísticas generales de reportes"""
    total_reports: int
    reports_by_type: Dict[str, int]
    reports_by_status: Dict[str, int]
    reports_by_format: Dict[str, int]
    average_processing_time: float
    total_file_size: int


class DashboardStatistics(BaseModel):
    """Estadísticas del dashboard"""
    packages_summary: Dict[str, Any]
    customers_analysis: Dict[str, Any]
    revenue_report: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    sms_analytics: Dict[str, Any]
    messages_report: Dict[str, Any]
    period_start: datetime
    period_end: datetime
    generated_at: datetime


# === ESQUEMAS DE FILTROS ===

class ReportFilter(BaseModel):
    """Filtros para consultas de reportes"""
    report_type: Optional[ReportType] = None
    status: Optional[ReportStatus] = None
    format: Optional[ReportFormat] = None
    created_by_id: Optional[UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None


class DashboardFilter(BaseModel):
    """Filtros para métricas de dashboard"""
    category: Optional[str] = None
    subcategory: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None