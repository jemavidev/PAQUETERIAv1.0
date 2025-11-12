# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Servicio de Reportes
Versión: 1.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc, extract, case
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from uuid import UUID
import json

from app.models.report import (
    Report, ReportTemplate, DashboardMetric, ReportSchedule,
    ReportType, ReportStatus, ReportFormat
)
from app.models.package import Package, PackageStatus
from app.models.customer import Customer
from app.models.user import User
from app.models.message import Message
from app.models.notification import Notification
from app.utils.datetime_utils import get_colombia_now


class ReportService:
    """Servicio para generación y gestión de reportes"""

    def __init__(self, db: Session):
        self.db = db

    # === MÉTODOS PRINCIPALES DE GENERACIÓN ===

    def generate_report(self, report_type: ReportType, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Genera un reporte basado en el tipo especificado"""
        generators = {
            ReportType.PACKAGES_SUMMARY: self._generate_packages_summary,
            ReportType.CUSTOMERS_ANALYSIS: self._generate_customers_analysis,
            ReportType.REVENUE_REPORT: self._generate_revenue_report,
            ReportType.PERFORMANCE_METRICS: self._generate_performance_metrics,
            ReportType.SMS_ANALYTICS: self._generate_sms_analytics,
            ReportType.MESSAGES_REPORT: self._generate_messages_report,
        }

        generator = generators.get(report_type)
        if not generator:
            raise ValueError(f"Tipo de reporte no soportado: {report_type}")

        return generator(parameters or {})

    def get_dashboard_statistics(self, period_start: Optional[datetime] = None,
                               period_end: Optional[datetime] = None) -> Dict[str, Any]:
        """Obtiene estadísticas completas para el dashboard"""
        if not period_start:
            period_start = get_colombia_now() - timedelta(days=30)
        if not period_end:
            period_end = get_colombia_now()

        return {
            "packages_summary": self._generate_packages_summary({"date_from": period_start, "date_to": period_end}),
            "customers_analysis": self._generate_customers_analysis({"date_from": period_start, "date_to": period_end}),
            "revenue_report": self._generate_revenue_report({"date_from": period_start, "date_to": period_end}),
            "performance_metrics": self._generate_performance_metrics({"date_from": period_start, "date_to": period_end}),
            "sms_analytics": self._generate_sms_analytics({"date_from": period_start, "date_to": period_end}),
            "messages_report": self._generate_messages_report({"date_from": period_start, "date_to": period_end}),
            "period_start": period_start,
            "period_end": period_end,
            "generated_at": get_colombia_now()
        }

    # === GENERADORES DE REPORTES ESPECÍFICOS ===

    def _generate_packages_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Genera resumen de paquetes"""
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        # Consulta base
        query = self.db.query(Package)

        if date_from:
            query = query.filter(Package.created_at >= date_from)
        if date_to:
            query = query.filter(Package.created_at <= date_to)

        # Estadísticas generales
        total_packages = query.count()

        # Por estado
        status_counts = self.db.query(
            Package.status, func.count(Package.id)
        ).filter(
            and_(
                Package.created_at >= date_from if date_from else True,
                Package.created_at <= date_to if date_to else True
            )
        ).group_by(Package.status).all()

        status_summary = {status.value: count for status, count in status_counts}

        # Por tipo de paquete
        type_counts = self.db.query(
            Package.package_type, func.count(Package.id)
        ).filter(
            and_(
                Package.created_at >= date_from if date_from else True,
                Package.created_at <= date_to if date_to else True
            )
        ).group_by(Package.package_type).all()

        type_summary = {ptype.value if ptype else "sin_tipo": count for ptype, count in type_counts}

        # Tendencia por día (últimos 30 días)
        daily_trend = self._get_daily_package_trend(date_from, date_to)

        return {
            "total_packages": total_packages,
            "status_distribution": status_summary,
            "type_distribution": type_summary,
            "daily_trend": daily_trend,
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }

    def _generate_customers_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Genera análisis de clientes"""
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        # Estadísticas de clientes
        total_customers = self.db.query(func.count(Customer.id)).scalar()

        # Nuevos clientes en el período
        new_customers_query = self.db.query(func.count(Customer.id)).filter(
            and_(
                Customer.created_at >= date_from if date_from else True,
                Customer.created_at <= date_to if date_to else True
            )
        )
        new_customers = new_customers_query.scalar()

        # Clientes activos (con paquetes en los últimos 30 días)
        active_cutoff = get_colombia_now() - timedelta(days=30)
        active_customers = self.db.query(func.count(func.distinct(Package.customer_id))).filter(
            and_(
                Package.created_at >= active_cutoff,
                Package.customer_id.isnot(None)
            )
        ).scalar()

        # Top clientes por paquetes
        top_customers = self.db.query(
            Customer.full_name,
            Customer.phone,
            func.count(Package.id).label('package_count')
        ).join(Package, Customer.id == Package.customer_id
        ).group_by(Customer.id, Customer.full_name, Customer.phone
        ).order_by(desc('package_count')
        ).limit(10).all()

        return {
            "total_customers": total_customers,
            "new_customers": new_customers,
            "active_customers": active_customers,
            "top_customers": [
                {
                    "name": name,
                    "phone": phone,
                    "package_count": count
                } for name, phone, count in top_customers
            ],
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }

    def _generate_revenue_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte de ingresos"""
        # Nota: Este reporte requiere integración con sistema de tarifas
        # Por ahora retornamos estructura básica
        return {
            "total_revenue": 0,
            "revenue_by_type": {},
            "monthly_trend": [],
            "top_revenue_sources": [],
            "period": {
                "from": params.get("date_from").isoformat() if params.get("date_from") else None,
                "to": params.get("date_to").isoformat() if params.get("date_to") else None
            }
        }

    def _generate_performance_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Genera métricas de rendimiento"""
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        # Tiempos de procesamiento de paquetes
        processing_times = self.db.query(
            func.avg(
                func.extract('epoch', Package.received_at) - func.extract('epoch', Package.announced_at)
            ).label('avg_processing_hours')
        ).filter(
            and_(
                Package.announced_at.isnot(None),
                Package.received_at.isnot(None),
                Package.announced_at >= date_from if date_from else True,
                Package.announced_at <= date_to if date_to else True
            )
        ).scalar()

        avg_processing_hours = processing_times * 24 if processing_times else 0

        # Tasa de éxito de entregas
        delivered_count = self.db.query(func.count(Package.id)).filter(
            Package.status == PackageStatus.ENTREGADO
        ).scalar()

        total_received = self.db.query(func.count(Package.id)).filter(
            Package.status.in_([PackageStatus.RECIBIDO, PackageStatus.ENTREGADO])
        ).scalar()

        delivery_rate = (delivered_count / total_received * 100) if total_received > 0 else 0

        return {
            "avg_processing_hours": round(avg_processing_hours, 2),
            "delivery_rate": round(delivery_rate, 2),
            "total_processed": total_received,
            "total_delivered": delivered_count,
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }

    def _generate_sms_analytics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Genera análisis de SMS"""
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        # Estadísticas de SMS
        total_sms = self.db.query(func.count(Notification.id)).filter(
            and_(
                Notification.created_at >= date_from if date_from else True,
                Notification.created_at <= date_to if date_to else True
            )
        ).scalar()

        # Por estado
        status_counts = self.db.query(
            Notification.status, func.count(Notification.id)
        ).filter(
            and_(
                Notification.created_at >= date_from if date_from else True,
                Notification.created_at <= date_to if date_to else True
            )
        ).group_by(Notification.status).all()

        status_summary = {status.value: count for status, count in status_counts}

        # Costo total
        total_cost = self.db.query(func.sum(Notification.cost_cents)).filter(
            and_(
                Notification.created_at >= date_from if date_from else True,
                Notification.created_at <= date_to if date_to else True
            )
        ).scalar() or 0

        # Tasa de entrega
        delivered = status_summary.get('delivered', 0)
        delivery_rate = (delivered / total_sms * 100) if total_sms > 0 else 0

        return {
            "total_sms": total_sms,
            "status_distribution": status_summary,
            "total_cost_cents": total_cost,
            "total_cost_cop": total_cost / 100,
            "delivery_rate": round(delivery_rate, 2),
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }

    def _generate_messages_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte de mensajes"""
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        # Estadísticas de mensajes
        total_messages = self.db.query(func.count(Message.id)).filter(
            and_(
                Message.created_at >= date_from if date_from else True,
                Message.created_at <= date_to if date_to else True
            )
        ).scalar()

        # Por estado
        status_counts = self.db.query(
            Message.status, func.count(Message.id)
        ).filter(
            and_(
                Message.created_at >= date_from if date_from else True,
                Message.created_at <= date_to if date_to else True
            )
        ).group_by(Message.status).all()

        status_summary = {status.value: count for status, count in status_counts}

        # Por prioridad
        priority_counts = self.db.query(
            Message.priority, func.count(Message.id)
        ).filter(
            and_(
                Message.created_at >= date_from if date_from else True,
                Message.created_at <= date_to if date_to else True
            )
        ).group_by(Message.priority).all()

        priority_summary = {priority.value: count for priority, count in priority_counts}

        return {
            "total_messages": total_messages,
            "status_distribution": status_summary,
            "priority_distribution": priority_summary,
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }

    # === MÉTODOS AUXILIARES ===

    def _get_daily_package_trend(self, date_from: Optional[datetime] = None,
                                date_to: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Obtiene tendencia diaria de paquetes"""
        if not date_from:
            date_from = get_colombia_now() - timedelta(days=30)
        if not date_to:
            date_to = get_colombia_now()

        # Consulta de paquetes por día
        daily_stats = self.db.query(
            func.date(Package.created_at).label('date'),
            func.count(Package.id).label('count')
        ).filter(
            and_(
                Package.created_at >= date_from,
                Package.created_at <= date_to
            )
        ).group_by(func.date(Package.created_at)
        ).order_by(func.date(Package.created_at)).all()

        return [
            {
                "date": str(date),
                "count": count
            } for date, count in daily_stats
        ]

    # === MÉTODOS DE GESTIÓN DE REPORTES ===

    def create_report(self, title: str, report_type: ReportType,
                     parameters: Optional[Dict[str, Any]] = None,
                     created_by_id: Optional[UUID] = None) -> Report:
        """Crea un nuevo reporte"""
        report = Report(
            title=title,
            report_type=report_type,
            parameters=parameters or {},
            created_by_id=created_by_id
        )

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    def get_report(self, report_id: UUID) -> Optional[Report]:
        """Obtiene un reporte por ID"""
        return self.db.query(Report).filter(Report.id == report_id).first()

    def update_report_status(self, report_id: UUID, status: ReportStatus,
                           data: Optional[Dict[str, Any]] = None,
                           summary: Optional[Dict[str, Any]] = None) -> Report:
        """Actualiza el estado de un reporte"""
        report = self.get_report(report_id)
        if not report:
            raise ValueError(f"Reporte no encontrado: {report_id}")

        report.status = status
        if data:
            report.data = data
        if summary:
            report.summary = summary

        if status == ReportStatus.COMPLETED:
            report.completed_at = get_colombia_now()
            if report.created_at:
                processing_time = (report.completed_at - report.created_at).total_seconds()
                report.processing_time = processing_time

        self.db.commit()
        self.db.refresh(report)

        return report

    def get_reports_list(self, skip: int = 0, limit: int = 50,
                        filters: Optional[Dict[str, Any]] = None) -> Tuple[List[Report], int]:
        """Obtiene lista paginada de reportes"""
        query = self.db.query(Report)

        # Aplicar filtros
        if filters:
            if filters.get("report_type"):
                query = query.filter(Report.report_type == filters["report_type"])
            if filters.get("status"):
                query = query.filter(Report.status == filters["status"])
            if filters.get("created_by_id"):
                query = query.filter(Report.created_by_id == filters["created_by_id"])

        total = query.count()
        reports = query.order_by(desc(Report.created_at)).offset(skip).limit(limit).all()

        return reports, total

    # === MÉTODOS DE MÉTRICAS DE DASHBOARD ===

    def update_dashboard_metrics(self, period_start: datetime, period_end: datetime) -> List[DashboardMetric]:
        """Actualiza las métricas del dashboard"""
        stats = self.get_dashboard_statistics(period_start, period_end)

        metrics = []

        # Crear métricas para cada estadística
        metric_definitions = [
            ("total_packages", stats["packages_summary"]["total_packages"], "unidades", "packages", "total"),
            ("total_customers", stats["customers_analysis"]["total_customers"], "unidades", "customers", "total"),
            ("active_customers", stats["customers_analysis"]["active_customers"], "unidades", "customers", "active"),
            ("delivery_rate", stats["performance_metrics"]["delivery_rate"], "%", "performance", "delivery"),
            ("total_sms", stats["sms_analytics"]["total_sms"], "unidades", "sms", "total"),
            ("sms_delivery_rate", stats["sms_analytics"]["delivery_rate"], "%", "sms", "delivery"),
            ("total_messages", stats["messages_report"]["total_messages"], "unidades", "messages", "total"),
        ]

        for metric_name, value, unit, category, subcategory in metric_definitions:
            metric = DashboardMetric(
                metric_name=metric_name,
                metric_value=float(value),
                metric_unit=unit,
                category=category,
                subcategory=subcategory,
                period_start=period_start,
                period_end=period_end,
                data_source="ReportService.generate_dashboard_statistics"
            )
            self.db.add(metric)
            metrics.append(metric)

        self.db.commit()

        return metrics

    def get_dashboard_metrics(self, category: Optional[str] = None,
                            subcategory: Optional[str] = None,
                            period_start: Optional[datetime] = None,
                            period_end: Optional[datetime] = None) -> List[DashboardMetric]:
        """Obtiene métricas del dashboard"""
        query = self.db.query(DashboardMetric)

        if category:
            query = query.filter(DashboardMetric.category == category)
        if subcategory:
            query = query.filter(DashboardMetric.subcategory == subcategory)
        if period_start:
            query = query.filter(DashboardMetric.period_start >= period_start)
        if period_end:
            query = query.filter(DashboardMetric.period_end <= period_end)

        return query.order_by(desc(DashboardMetric.calculated_at)).all()