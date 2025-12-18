# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio de Administración
Versión: 1.0.0 (Optimizado con Cache)
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract, case
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
# from uuid import UUID  # User model uses Integer, not UUID
import logging

from app.models.user import User, UserRole
from app.models.package import Package, PackageStatus
from app.models.customer import Customer
from app.models.message import Message
from app.models.notification import Notification
from app.models.report import Report, ReportStatus
from app.utils.datetime_utils import get_colombia_now
from app.cache_manager import cache_manager

logger = logging.getLogger(__name__)


class AdminService:
    """Servicio para funcionalidades administrativas del sistema (Optimizado con Cache)"""

    def __init__(self, db: Session):
        self.db = db

    # === DASHBOARD ADMINISTRATIVO ===

    def get_admin_dashboard_stats(self, period_days: int = 30, include_analytics: bool = True) -> Dict[str, Any]:
        """Obtiene estadísticas completas para el dashboard administrativo (Optimizado con Cache)"""
        # Intentar obtener del cache
        cache_key = f"admin_dashboard_stats_{period_days}_{include_analytics}"
        cached_stats = cache_manager.get(f"paqueteria:cache:{cache_key}")
        if cached_stats:
            logger.debug(f"Cache HIT: admin dashboard stats (period={period_days}, analytics={include_analytics})")
            return cached_stats
        
        logger.debug(f"Cache MISS: admin dashboard stats (period={period_days}, analytics={include_analytics})")
        
        period_end = get_colombia_now()
        period_start = period_end - timedelta(days=period_days)

        stats = {
            "system_overview": self._get_system_overview(),
            "user_management": self._get_user_management_stats(),
            "business_metrics": self._get_business_metrics(period_start, period_end),
            "system_health": self._get_system_health_stats(),
            "recent_activity": self._get_recent_activity(),
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "days": period_days
            }
        }
        
        # Agregar analytics avanzados si se solicitan
        if include_analytics:
            stats["financial_metrics"] = self._get_financial_metrics(period_start, period_end)
            stats["package_analytics"] = self._get_package_analytics()
            stats["customer_analytics"] = self._get_customer_analytics(period_start, period_end)
            stats["notification_analytics"] = self._get_notification_analytics(period_start, period_end)
            stats["performance_metrics"] = self._get_performance_metrics()
            stats["file_analytics"] = self._get_file_analytics()
        
        # Cachear por 5 minutos (300 segundos)
        cache_manager.set(f"paqueteria:cache:{cache_key}", stats, ttl=300)
        
        return stats

    def _get_system_overview(self) -> Dict[str, Any]:
        """Vista general del sistema"""
        # Total de reportes (opcional - puede no existir la tabla)
        total_reports = 0
        try:
            total_reports = self.db.query(func.count(Report.id)).scalar()
        except Exception:
            self.db.rollback()  # Resetear transacción
        
        return {
            "total_users": self.db.query(func.count(User.id)).scalar(),
            "active_users": self.db.query(func.count(User.id)).filter(User.is_active == True).scalar(),
            "total_packages": self.db.query(func.count(Package.id)).scalar(),
            "total_customers": self.db.query(func.count(Customer.id)).scalar(),
            "total_messages": self.db.query(func.count(Message.id)).scalar(),
            "total_notifications": self.db.query(func.count(Notification.id)).scalar(),
            "total_reports": total_reports
        }

    def _get_user_management_stats(self) -> Dict[str, Any]:
        """Estadísticas de gestión de usuarios"""
        # Usuarios por rol
        role_counts = self.db.query(
            User.role, func.count(User.id)
        ).group_by(User.role).all()

        roles_summary = {role.value: count for role, count in role_counts}

        # Usuarios activos vs inactivos
        active_inactive = self.db.query(
            User.is_active, func.count(User.id)
        ).group_by(User.is_active).all()

        status_summary = {("active" if active else "inactive"): count for active, count in active_inactive}

        # Usuarios recientes (últimos 30 días)
        recent_cutoff = get_colombia_now() - timedelta(days=30)
        recent_users = self.db.query(func.count(User.id)).filter(
            User.created_at >= recent_cutoff
        ).scalar()

        return {
            "users_by_role": roles_summary,
            "users_by_status": status_summary,
            "recent_users": recent_users,
            "total_admins": roles_summary.get("ADMIN", 0),
            "total_operators": roles_summary.get("operator", 0),
            "total_clients": roles_summary.get("user", 0)
        }

    def _get_business_metrics(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Métricas de negocio para el período"""
        # Paquetes por estado
        package_status = self.db.query(
            Package.status, func.count(Package.id)
        ).filter(
            and_(
                Package.created_at >= period_start,
                Package.created_at <= period_end
            )
        ).group_by(Package.status).all()

        packages_by_status = {status.value: count for status, count in package_status}

        # Clientes nuevos
        new_customers = self.db.query(func.count(Customer.id)).filter(
            and_(
                Customer.created_at >= period_start,
                Customer.created_at <= period_end
            )
        ).scalar()

        # Mensajes por estado
        message_status = self.db.query(
            Message.status, func.count(Message.id)
        ).filter(
            and_(
                Message.created_at >= period_start,
                Message.created_at <= period_end
            )
        ).group_by(Message.status).all()

        messages_by_status = {status.value: count for status, count in message_status}

        # SMS enviados y costos
        sms_stats = self.db.query(
            func.count(Notification.id),
            func.sum(Notification.cost_cents)
        ).filter(
            and_(
                Notification.created_at >= period_start,
                Notification.created_at <= period_end
            )
        ).first()

        total_sms = sms_stats[0] or 0
        total_sms_cost = (sms_stats[1] or 0) / 100  # Convertir de centavos a pesos

        # Reportes generados (opcional - puede no existir la tabla)
        reports_generated = 0
        try:
            reports_generated = self.db.query(func.count(Report.id)).filter(
                and_(
                    Report.created_at >= period_start,
                    Report.created_at <= period_end
                )
            ).scalar()
        except Exception:
            self.db.rollback()  # Resetear transacción

        return {
            "packages_by_status": packages_by_status,
            "new_customers": new_customers,
            "messages_by_status": messages_by_status,
            "total_sms_sent": total_sms,
            "total_sms_cost_cop": total_sms_cost,
            "reports_generated": reports_generated
        }

    def _get_system_health_stats(self) -> Dict[str, Any]:
        """Estadísticas de salud del sistema"""
        # Reportes fallidos (opcional - puede no existir la tabla)
        failed_reports = 0
        try:
            failed_reports = self.db.query(func.count(Report.id)).filter(
                Report.status == ReportStatus.FAILED
            ).scalar()
        except Exception:
            self.db.rollback()  # Resetear transacción

        # Usuarios inactivos
        inactive_users = self.db.query(func.count(User.id)).filter(
            User.is_active == False
        ).scalar()

        # Paquetes sin procesar (anunciados pero no recibidos)
        unprocessed_packages = self.db.query(func.count(Package.id)).filter(
            Package.status == PackageStatus.ANUNCIADO
        ).scalar()

        # Mensajes pendientes
        from app.models.message import MessageStatus
        pending_messages = self.db.query(func.count(Message.id)).filter(
            Message.status == MessageStatus.ABIERTO
        ).scalar()

        return {
            "failed_reports": failed_reports,
            "inactive_users": inactive_users,
            "unprocessed_packages": unprocessed_packages,
            "pending_messages": pending_messages,
            "system_status": "healthy" if failed_reports == 0 else "warning"
        }

    def _get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Actividad reciente del sistema"""
        activities = []

        # Usuarios recientes
        recent_users = self.db.query(User).order_by(desc(User.created_at)).limit(3).all()
        for user in recent_users:
            activities.append({
                "type": "user_created",
                "description": f"Nuevo usuario: {user.full_name}",
                "timestamp": user.created_at.isoformat(),
                "user": user.username
            })

        # Paquetes recientes
        recent_packages = self.db.query(Package).order_by(desc(Package.created_at)).limit(3).all()
        for package in recent_packages:
            activities.append({
                "type": "package_created",
                "description": f"Paquete creado: {package.tracking_number}",
                "timestamp": package.created_at.isoformat(),
                "user": "system"
            })

        # Reportes recientes (opcional - puede no existir la tabla)
        try:
            recent_reports = self.db.query(Report).order_by(desc(Report.created_at)).limit(2).all()
            for report in recent_reports:
                activities.append({
                    "type": "report_generated",
                    "description": f"Reporte generado: {report.title}",
                    "timestamp": report.created_at.isoformat(),
                    "user": report.created_by.username if report.created_by else "system"
                })
        except Exception:
            self.db.rollback()  # Resetear transacción

        # Ordenar por timestamp y limitar
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]

    # === ANALYTICS AVANZADOS ===

    def _get_financial_metrics(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Métricas financieras del período"""
        from app.models.package import PackageType
        from decimal import Decimal
        
        # Paquetes entregados (ingresos confirmados)
        delivered_packages = self.db.query(Package).filter(
            and_(
                Package.status == PackageStatus.ENTREGADO,
                Package.delivered_at >= period_start,
                Package.delivered_at <= period_end
            )
        ).all()
        
        # Calcular ingresos totales
        total_revenue = sum((p.base_fee + p.storage_fee) for p in delivered_packages)
        
        # Valor promedio por paquete
        average_package_value = total_revenue / len(delivered_packages) if delivered_packages else Decimal(0)
        
        # Ingresos por tipo de paquete
        revenue_by_type = {}
        for pkg_type in PackageType:
            type_packages = [p for p in delivered_packages if p.package_type == pkg_type]
            revenue_by_type[pkg_type.value] = sum((p.base_fee + p.storage_fee) for p in type_packages)
        
        # Total de tarifas de almacenamiento y entrega
        total_storage_fees = sum(p.storage_fee for p in delivered_packages)
        total_delivery_fees = sum(p.base_fee for p in delivered_packages)
        
        # Paquetes con pagos pendientes (RECIBIDO pero no ENTREGADO)
        pending_packages = self.db.query(Package).filter(
            Package.status == PackageStatus.RECIBIDO
        ).all()
        pending_payments = sum((p.base_fee + p.storage_fee) for p in pending_packages)
        
        # Agregar ventas por período (día/semana/mes)
        sales_by_period = self.get_sales_by_period()
        
        return {
            "total_revenue": float(total_revenue),
            "average_package_value": float(average_package_value),
            "revenue_by_type": {k: float(v) for k, v in revenue_by_type.items()},
            "total_storage_fees": float(total_storage_fees),
            "total_delivery_fees": float(total_delivery_fees),
            "pending_payments": float(pending_payments),
            "delivered_packages_count": len(delivered_packages),
            "pending_packages_count": len(pending_packages),
            "sales_by_period": sales_by_period
        }

    def _get_package_analytics(self) -> Dict[str, Any]:
        """Análisis detallado de paquetes"""
        from app.models.package import PackageType, PackageCondition
        
        # Paquetes por tipo
        packages_by_type = {}
        for pkg_type in PackageType:
            count = self.db.query(func.count(Package.id)).filter(
                Package.package_type == pkg_type
            ).scalar()
            packages_by_type[pkg_type.value] = count
        
        # Paquetes por condición
        packages_by_condition = {}
        for condition in PackageCondition:
            count = self.db.query(func.count(Package.id)).filter(
                Package.package_condition == condition
            ).scalar()
            packages_by_condition[condition.value] = count
        
        # Días promedio de almacenamiento (para paquetes entregados)
        delivered_packages = self.db.query(Package).filter(
            and_(
                Package.status == PackageStatus.ENTREGADO,
                Package.received_at.isnot(None),
                Package.delivered_at.isnot(None)
            )
        ).all()
        
        if delivered_packages:
            total_days = sum(
                (p.delivered_at - p.received_at).days 
                for p in delivered_packages
            )
            average_storage_days = total_days / len(delivered_packages)
        else:
            average_storage_days = 0
        
        # Paquetes con almacenamiento extra (más de 3 días)
        packages_with_overtime = len([p for p in delivered_packages if (p.delivered_at - p.received_at).days > 3])
        
        # Posiciones ocupadas vs disponibles
        occupied_positions = self.db.query(func.count(Package.id)).filter(
            and_(
                Package.posicion.isnot(None),
                Package.status == PackageStatus.RECIBIDO
            )
        ).scalar()
        
        available_positions = 100 - occupied_positions  # BAROTI: 00-99
        
        # Tasas de entrega y cancelación
        total_received = self.db.query(func.count(Package.id)).filter(
            Package.status.in_([PackageStatus.RECIBIDO, PackageStatus.ENTREGADO])
        ).scalar()
        
        total_delivered = self.db.query(func.count(Package.id)).filter(
            Package.status == PackageStatus.ENTREGADO
        ).scalar()
        
        total_cancelled = self.db.query(func.count(Package.id)).filter(
            Package.status == PackageStatus.CANCELADO
        ).scalar()
        
        delivery_rate = (total_delivered / total_received * 100) if total_received > 0 else 0
        cancellation_rate = (total_cancelled / (total_received + total_cancelled) * 100) if (total_received + total_cancelled) > 0 else 0
        
        return {
            "packages_by_type": packages_by_type,
            "packages_by_condition": packages_by_condition,
            "average_storage_days": round(average_storage_days, 2),
            "packages_with_overtime": packages_with_overtime,
            "occupied_positions": occupied_positions,
            "available_positions": available_positions,
            "delivery_rate": round(delivery_rate, 2),
            "cancellation_rate": round(cancellation_rate, 2)
        }

    def _get_customer_analytics(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Análisis de clientes"""
        
        # Clientes VIP
        vip_customers = self.db.query(func.count(Customer.id)).filter(
            Customer.is_vip == True
        ).scalar()
        
        # Top 10 clientes por cantidad de paquetes
        top_customers_by_packages = self.db.query(
            Customer.full_name,
            func.count(Package.id).label('package_count')
        ).join(Package).group_by(Customer.id, Customer.full_name).order_by(
            desc('package_count')
        ).limit(10).all()
        
        # Top 10 clientes por gasto
        top_customers_by_spending = self.db.query(
            Customer.full_name,
            Customer.total_spent
        ).filter(
            Customer.total_spent > 0
        ).order_by(desc(Customer.total_spent)).limit(10).all()
        
        # Clientes con paquetes pendientes
        customers_with_pending = self.db.query(func.count(func.distinct(Package.customer_id))).filter(
            Package.status == PackageStatus.RECIBIDO
        ).scalar()
        
        # Clientes por ciudad (top 5)
        customers_by_city = self.db.query(
            Customer.address_city,
            func.count(Customer.id).label('count')
        ).filter(
            Customer.address_city.isnot(None)
        ).group_by(Customer.address_city).order_by(desc('count')).limit(5).all()
        
        # Clientes nuevos vs recurrentes en el período
        new_customers_period = self.db.query(func.count(Customer.id)).filter(
            and_(
                Customer.created_at >= period_start,
                Customer.created_at <= period_end
            )
        ).scalar()
        
        returning_customers = self.db.query(func.count(func.distinct(Package.customer_id))).filter(
            and_(
                Package.created_at >= period_start,
                Package.created_at <= period_end
            )
        ).scalar() - new_customers_period
        
        return {
            "vip_customers": vip_customers,
            "top_customers_by_packages": [
                {"name": name, "package_count": count} 
                for name, count in top_customers_by_packages
            ],
            "top_customers_by_spending": [
                {"name": name, "total_spent_cop": float(spent / 100)} 
                for name, spent in top_customers_by_spending
            ],
            "customers_with_pending_packages": customers_with_pending,
            "customers_by_city": [
                {"city": city, "count": count} 
                for city, count in customers_by_city
            ],
            "new_customers_period": new_customers_period,
            "returning_customers": max(0, returning_customers)
        }

    def _get_notification_analytics(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Análisis de notificaciones"""
        from app.models.notification import NotificationEvent
        
        # SMS por tipo de evento
        sms_by_event = {}
        for event in NotificationEvent:
            count = self.db.query(func.count(Notification.id)).filter(
                and_(
                    Notification.event_type == event,
                    Notification.created_at >= period_start,
                    Notification.created_at <= period_end
                )
            ).scalar()
            if count > 0:
                sms_by_event[event.value] = count
        
        # Tasa de éxito de SMS (simulado - en producción vendría del provider)
        total_sms = self.db.query(func.count(Notification.id)).filter(
            and_(
                Notification.created_at >= period_start,
                Notification.created_at <= period_end
            )
        ).scalar()
        
        sms_success_rate = 98.5  # Simulado - en producción calcular basado en respuestas del provider
        
        # Costo promedio por notificación
        total_cost = self.db.query(func.sum(Notification.cost_cents)).filter(
            and_(
                Notification.created_at >= period_start,
                Notification.created_at <= period_end
            )
        ).scalar() or 0
        
        cost_per_notification = (total_cost / total_sms / 100) if total_sms > 0 else 0
        
        # Uso diario y mensual de SMS
        from app.config import settings
        sms_daily_limit = settings.sms_daily_limit
        sms_monthly_limit = settings.sms_monthly_limit
        
        today = get_colombia_now().date()
        sms_today = self.db.query(func.count(Notification.id)).filter(
            func.date(Notification.created_at) == today
        ).scalar()
        
        return {
            "sms_by_event": sms_by_event,
            "total_sms_sent": total_sms,
            "sms_success_rate": sms_success_rate,
            "cost_per_notification_cop": round(cost_per_notification, 2),
            "sms_daily_usage": {
                "sent": sms_today,
                "limit": sms_daily_limit,
                "percentage": round((sms_today / sms_daily_limit * 100), 2) if sms_daily_limit > 0 else 0
            },
            "sms_monthly_usage": {
                "sent": total_sms,
                "limit": sms_monthly_limit,
                "percentage": round((total_sms / sms_monthly_limit * 100), 2) if sms_monthly_limit > 0 else 0
            }
        }

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Métricas de rendimiento operacional"""
        
        # Tiempo promedio de procesamiento (ANUNCIADO → RECIBIDO)
        processed_packages = self.db.query(Package).filter(
            and_(
                Package.announced_at.isnot(None),
                Package.received_at.isnot(None)
            )
        ).all()
        
        if processed_packages:
            total_processing_time = sum(
                (p.received_at - p.announced_at).total_seconds() / 3600  # en horas
                for p in processed_packages
            )
            average_processing_time = total_processing_time / len(processed_packages)
        else:
            average_processing_time = 0
        
        # Tiempo promedio de entrega (RECIBIDO → ENTREGADO)
        delivered_packages = self.db.query(Package).filter(
            and_(
                Package.received_at.isnot(None),
                Package.delivered_at.isnot(None)
            )
        ).all()
        
        if delivered_packages:
            total_delivery_time = sum(
                (p.delivered_at - p.received_at).total_seconds() / 3600  # en horas
                for p in delivered_packages
            )
            average_delivery_time = total_delivery_time / len(delivered_packages)
        else:
            average_delivery_time = 0
        
        # Paquetes procesados y entregados hoy
        today = get_colombia_now().date()
        packages_processed_today = self.db.query(func.count(Package.id)).filter(
            func.date(Package.received_at) == today
        ).scalar()
        
        packages_delivered_today = self.db.query(func.count(Package.id)).filter(
            func.date(Package.delivered_at) == today
        ).scalar()
        
        return {
            "average_processing_time_hours": round(average_processing_time, 2),
            "average_delivery_time_hours": round(average_delivery_time, 2),
            "packages_processed_today": packages_processed_today,
            "packages_delivered_today": packages_delivered_today
        }

    def _get_file_analytics(self) -> Dict[str, Any]:
        """Análisis de archivos y almacenamiento"""
        from app.models.file_upload import FileUpload, FileType
        
        # Total de archivos
        total_files = self.db.query(func.count(FileUpload.id)).scalar()
        
        # Archivos por tipo
        files_by_type = {}
        for file_type in FileType:
            count = self.db.query(func.count(FileUpload.id)).filter(
                FileUpload.file_type == file_type
            ).scalar()
            if count > 0:
                files_by_type[file_type.value] = count
        
        # Promedio de archivos por paquete
        packages_with_files = self.db.query(func.count(func.distinct(FileUpload.package_id))).filter(
            FileUpload.package_id.isnot(None)
        ).scalar()
        
        average_files_per_package = (total_files / packages_with_files) if packages_with_files > 0 else 0
        
        return {
            "total_files_uploaded": total_files,
            "files_by_type": files_by_type,
            "average_files_per_package": round(average_files_per_package, 2),
            "packages_with_files": packages_with_files
        }

    # === GESTIÓN DE USUARIOS ===

    def get_users_list(self, skip: int = 0, limit: int = 50,
                      filters: Optional[Dict[str, Any]] = None) -> Tuple[List[User], int]:
        """Obtiene lista paginada de usuarios con filtros"""
        query = self.db.query(User)

        # Aplicar filtros
        if filters:
            if filters.get("role"):
                query = query.filter(User.role == filters["role"])
            if filters.get("is_active") is not None:
                query = query.filter(User.is_active == filters["is_active"])
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        User.username.ilike(search_term),
                        User.email.ilike(search_term),
                        User.full_name.ilike(search_term)
                    )
                )

        total = query.count()
        users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()

        return users, total

    def create_user(self, user_data: Dict[str, Any], created_by_user_id: Optional[int] = None) -> User:
        """Crea un nuevo usuario administrativo"""
        from app.utils.auth import get_password_hash

        hashed_password = get_password_hash(user_data["password"])

        user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            phone=user_data.get("phone"),
            role=UserRole(user_data["role"]),
            password_hash=hashed_password,
            is_active=user_data.get("is_active", True)
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Log de auditoría
        logger.info(
            f"USER_CREATED: user_id={user.id}, username={user.username}, "
            f"role={user.role.value}, created_by={created_by_user_id}"
        )

        return user

    def update_user(self, user_id: int, user_data: Dict[str, Any], updated_by_user_id: Optional[int] = None) -> User:
        """Actualiza un usuario existente"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Usuario no encontrado: {user_id}")

        # Guardar valores anteriores para el log
        old_values = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active
        }

        # Actualizar campos permitidos
        changed_fields = []
        for field in ["username", "email", "full_name", "phone", "role", "is_active"]:
            if field in user_data:
                old_value = getattr(user, field)
                if field == "role":
                    new_value = UserRole(user_data[field])
                    user.role = new_value
                    if old_value.value != new_value.value:
                        changed_fields.append(f"{field}:{old_value.value}->{new_value.value}")
                else:
                    new_value = user_data[field]
                    setattr(user, field, new_value)
                    if old_value != new_value:
                        changed_fields.append(f"{field}:{old_value}->{new_value}")

        user.updated_at = get_colombia_now()
        self.db.commit()
        self.db.refresh(user)

        # Log de auditoría
        if changed_fields:
            logger.info(
                f"USER_UPDATED: user_id={user.id}, username={user.username}, "
                f"changes={','.join(changed_fields)}, updated_by={updated_by_user_id}"
            )

        return user

    def toggle_user_status(self, user_id: int, changed_by_user_id: Optional[int] = None) -> User:
        """Activa/desactiva un usuario"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Usuario no encontrado: {user_id}")

        old_status = user.is_active

        # No permitir desactivar al último admin
        if user.role.value == "ADMIN" and user.is_active:
            admin_count = self.db.query(func.count(User.id)).filter(
                and_(User.role == UserRole.ADMIN, User.is_active == True)
            ).scalar()
            if admin_count <= 1:
                raise ValueError("No se puede desactivar al último administrador activo")

        user.is_active = not user.is_active
        user.updated_at = get_colombia_now()
        self.db.commit()
        self.db.refresh(user)

        # Log de auditoría
        logger.info(
            f"USER_STATUS_TOGGLED: user_id={user.id}, username={user.username}, "
            f"status={old_status}->{user.is_active}, changed_by={changed_by_user_id}"
        )

        return user

    def reset_user_password(self, user_id: int, new_password: str, reset_by_user_id: Optional[int] = None) -> User:
        """Resetea la contraseña de un usuario"""
        from app.utils.auth import get_password_hash

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Usuario no encontrado: {user_id}")

        user.password_hash = get_password_hash(new_password)
        user.updated_at = get_colombia_now()
        self.db.commit()
        self.db.refresh(user)

        # Log de auditoría (sin incluir la contraseña)
        logger.info(
            f"USER_PASSWORD_RESET: user_id={user.id}, username={user.username}, "
            f"reset_by={reset_by_user_id}"
        )

        return user

    def delete_user(self, user_id: int, deleted_by_user_id: Optional[int] = None) -> bool:
        """Elimina un usuario (con validaciones de seguridad)"""
        # Obtener información del usuario sin cargar relaciones problemáticas
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Usuario no encontrado: {user_id}")

        # Guardar información para el log antes de eliminar
        username = user.username
        role = user.role.value

        # No permitir eliminar al último admin
        if user.role.value == "ADMIN":
            admin_count = self.db.query(func.count(User.id)).filter(
                User.role == UserRole.ADMIN
            ).scalar()
            if admin_count <= 1:
                raise ValueError("No se puede eliminar al último administrador")

        # Limpiar todas las referencias del usuario en otras tablas antes de eliminar
        from sqlalchemy import text
        try:
            # Limpiar referencias en messages
            self.db.execute(
                text("UPDATE messages SET sender_id = NULL WHERE sender_id = :user_id"),
                {"user_id": user_id}
            )
            self.db.execute(
                text("UPDATE messages SET recipient_id = NULL WHERE recipient_id = :user_id"),
                {"user_id": user_id}
            )
            self.db.execute(
                text("UPDATE messages SET answered_by = NULL WHERE answered_by = :user_id"),
                {"user_id": user_id}
            )
            
            # Limpiar referencias en packages
            self.db.execute(
                text("UPDATE packages SET created_by = NULL WHERE created_by = :user_id"),
                {"user_id": user_id}
            )
            self.db.execute(
                text("UPDATE packages SET updated_by = NULL WHERE updated_by = :user_id"),
                {"user_id": user_id}
            )
            
            # Limpiar referencias en customers
            self.db.execute(
                text("UPDATE customers SET created_by_id = NULL WHERE created_by_id = :user_id"),
                {"user_id": user_id}
            )
            self.db.execute(
                text("UPDATE customers SET updated_by_id = NULL WHERE updated_by_id = :user_id"),
                {"user_id": user_id}
            )
            
            # Limpiar referencias en package_events
            self.db.execute(
                text("UPDATE package_events SET operator_id = NULL WHERE operator_id = :user_id"),
                {"user_id": user_id}
            )
            
            # user_preferences se elimina automáticamente con CASCADE
            # Ahora eliminar el usuario
            self.db.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar usuario {user_id}: {e}", exc_info=True)
            raise ValueError(f"Error al eliminar usuario: {str(e)}")

        # Log de auditoría
        logger.info(
            f"USER_DELETED: user_id={user_id}, username={username}, "
            f"role={role}, deleted_by={deleted_by_user_id}"
        )

        return True

    # === CONFIGURACIONES DEL SISTEMA ===

    def get_system_config(self) -> Dict[str, Any]:
        """Obtiene configuraciones del sistema"""
        # Por ahora retornamos configuración básica
        # En el futuro esto podría venir de una tabla de configuraciones
        return {
            "app_name": "PAQUETES EL CLUB",
            "app_version": "1.0.0",
            "environment": "development",
            "database_url": "[CONFIGURADO]",
            "smtp_config": {
                "host": "[CONFIGURADO]",
                "port": 587,
                "enabled": True
            },
            "sms_config": {
                "provider": "Liwa.co",
                "enabled": True
            },
            "file_upload": {
                "max_size": "5MB",
                "allowed_extensions": ["jpg", "jpeg", "png", "gif", "webp"]
            }
        }

    def update_system_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza configuraciones del sistema"""
        # Por ahora solo validamos y retornamos
        # En el futuro esto actualizaría una tabla de configuraciones
        allowed_keys = ["app_name", "maintenance_mode", "debug_mode"]

        updated_config = {}
        for key, value in config_data.items():
            if key in allowed_keys:
                updated_config[key] = value

        return updated_config

    # === AUDITORÍA Y LOGS ===

    def get_audit_logs(self, skip: int = 0, limit: int = 50,
                      filters: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], int]:
        """Obtiene logs de auditoría del sistema"""
        # Por ahora simulamos logs básicos
        # En el futuro esto vendría de una tabla de auditoría dedicada

        # Simular algunos logs de ejemplo
        logs = [
            {
                "id": "log-1",
                "timestamp": (get_colombia_now() - timedelta(hours=1)).isoformat(),
                "action": "user_login",
                "user": "ADMIN",
                "details": "Inicio de sesión exitoso",
                "ip_address": "192.168.1.100"
            },
            {
                "id": "log-2",
                "timestamp": (get_colombia_now() - timedelta(hours=2)).isoformat(),
                "action": "report_generated",
                "user": "ADMIN",
                "details": "Reporte de paquetes generado",
                "ip_address": "192.168.1.100"
            },
            {
                "id": "log-3",
                "timestamp": (get_colombia_now() - timedelta(hours=3)).isoformat(),
                "action": "user_created",
                "user": "ADMIN",
                "details": "Usuario 'operator1' creado",
                "ip_address": "192.168.1.100"
            }
        ]

        # Aplicar filtros básicos
        if filters:
            if filters.get("action"):
                logs = [log for log in logs if log["action"] == filters["action"]]
            if filters.get("user"):
                logs = [log for log in logs if log["user"] == filters["user"]]

        total = len(logs)
        paginated_logs = logs[skip:skip + limit]

        return paginated_logs, total

    # === UTILIDADES ADMINISTRATIVAS ===

    def cleanup_old_data(self, days_old: int = 90) -> Dict[str, int]:
        """Limpia datos antiguos del sistema"""
        cutoff_date = get_colombia_now() - timedelta(days=days_old)

        # Contar elementos a eliminar (sin eliminar realmente por seguridad)
        old_reports = self.db.query(func.count(Report.id)).filter(
            and_(
                Report.created_at < cutoff_date,
                Report.status.in_(["completed", "failed"])
            )
        ).scalar()

        old_notifications = self.db.query(func.count(Notification.id)).filter(
            Notification.created_at < cutoff_date
        ).scalar()

        return {
            "old_reports_to_delete": old_reports,
            "old_notifications_to_delete": old_notifications,
            "cleanup_date": cutoff_date.isoformat(),
            "message": "Use with caution - cleanup not executed"
        }

    def get_system_info(self) -> Dict[str, Any]:
        """Información del sistema para diagnóstico"""
        return {
            "app_version": "1.0.0",
            "python_version": "3.11",
            "database_type": "PostgreSQL",
            "cache_type": "Redis",
            "environment": "development",
            "uptime": "Simulado",  # En producción calcular uptime real
            "last_backup": "2025-09-20T10:00:00Z",
            "disk_usage": "45%",
            "memory_usage": "60%"
        }


    def get_sales_by_period(self) -> Dict[str, Any]:
        """Obtiene ventas por día, semana y mes"""
        from decimal import Decimal
        
        now = get_colombia_now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Ventas de hoy
        today_packages = self.db.query(Package).filter(
            and_(
                Package.status == PackageStatus.ENTREGADO,
                Package.delivered_at >= today_start
            )
        ).all()
        
        revenue_today = sum((p.base_fee + p.storage_fee) for p in today_packages)
        packages_today = len(today_packages)
        
        # Ventas de la semana
        week_packages = self.db.query(Package).filter(
            and_(
                Package.status == PackageStatus.ENTREGADO,
                Package.delivered_at >= week_start
            )
        ).all()
        
        revenue_week = sum((p.base_fee + p.storage_fee) for p in week_packages)
        packages_week = len(week_packages)
        
        # Ventas del mes
        month_packages = self.db.query(Package).filter(
            and_(
                Package.status == PackageStatus.ENTREGADO,
                Package.delivered_at >= month_start
            )
        ).all()
        
        revenue_month = sum((p.base_fee + p.storage_fee) for p in month_packages)
        packages_month = len(month_packages)
        
        return {
            "today": {
                "revenue": float(revenue_today),
                "packages": packages_today,
                "average": float(revenue_today / packages_today) if packages_today > 0 else 0
            },
            "week": {
                "revenue": float(revenue_week),
                "packages": packages_week,
                "average": float(revenue_week / packages_week) if packages_week > 0 else 0
            },
            "month": {
                "revenue": float(revenue_month),
                "packages": packages_month,
                "average": float(revenue_month / packages_month) if packages_month > 0 else 0
            }
        }
