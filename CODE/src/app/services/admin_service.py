# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Servicio de Administración
Versión: 1.0.0
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

logger = logging.getLogger(__name__)


class AdminService:
    """Servicio para funcionalidades administrativas del sistema"""

    def __init__(self, db: Session):
        self.db = db

    # === DASHBOARD ADMINISTRATIVO ===

    def get_admin_dashboard_stats(self, period_days: int = 30) -> Dict[str, Any]:
        """Obtiene estadísticas completas para el dashboard administrativo"""
        period_end = get_colombia_now()
        period_start = period_end - timedelta(days=period_days)

        return {
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

    def _get_system_overview(self) -> Dict[str, Any]:
        """Vista general del sistema"""
        return {
            "total_users": self.db.query(func.count(User.id)).scalar(),
            "active_users": self.db.query(func.count(User.id)).filter(User.is_active == True).scalar(),
            "total_packages": self.db.query(func.count(Package.id)).scalar(),
            "total_customers": self.db.query(func.count(Customer.id)).scalar(),
            "total_messages": self.db.query(func.count(Message.id)).scalar(),
            "total_notifications": self.db.query(func.count(Notification.id)).scalar(),
            "total_reports": self.db.query(func.count(Report.id)).scalar()
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

        # Reportes generados
        reports_generated = self.db.query(func.count(Report.id)).filter(
            and_(
                Report.created_at >= period_start,
                Report.created_at <= period_end
            )
        ).scalar()

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
        # Reportes fallidos
        failed_reports = self.db.query(func.count(Report.id)).filter(
            Report.status == ReportStatus.FAILED
        ).scalar()

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

        # Reportes recientes
        recent_reports = self.db.query(Report).order_by(desc(Report.created_at)).limit(2).all()
        for report in recent_reports:
            activities.append({
                "type": "report_generated",
                "description": f"Reporte generado: {report.title}",
                "timestamp": report.created_at.isoformat(),
                "user": report.created_by.username if report.created_by else "system"
            })

        # Ordenar por timestamp y limitar
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]

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
            "app_version": "4.0.0",
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
            "app_version": "4.0.0",
            "python_version": "3.11",
            "database_type": "PostgreSQL",
            "cache_type": "Redis",
            "environment": "development",
            "uptime": "Simulado",  # En producción calcular uptime real
            "last_backup": "2025-09-20T10:00:00Z",
            "disk_usage": "45%",
            "memory_usage": "60%"
        }